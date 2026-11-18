"""Read-only proposal generation through supported local agent CLIs."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Path(__file__).with_name("proposal.schema.json")
PROVIDER_LABELS = {"codex": "Codex CLI", "claude": "Claude Code CLI", "manual": "本机共享行程"}
DEFAULT_BINS = {"codex": "codex", "claude": "claude"}


def proposal_prompt(data: dict, date: str, request: str, *, invoke_skill: bool) -> str:
    skill = "Use the installed $plan-and-maintain-trips skill. " if invoke_skill else (
        "Follow the bundled plan-and-maintain-trips skill guidance below. "
    )
    guidance = "" if invoke_skill else f"\n\nSkill guidance:\n{(ROOT / 'SKILL.md').read_text(encoding='utf-8')}"
    return (
        skill + "Propose a scoped travel-day revision. Return only JSON conforming to the supplied schema. "
        "Do not edit any files. day_json must be a JSON-encoded string of a complete day object for only the selected date, "
        "preserving its date, all hard appointments, their times, locations, anchor IDs and booking IDs. "
        "Do not invent verified hours, ticket status or coordinates; retain uncertainty in warnings. "
        "Keep the existing trip schema and structured item IDs where an item is unchanged. "
        "Write the summary and warnings in the same language as the user request.\n\n"
        f"Selected date: {date}\nUser request: {request}\n\nCanonical trip JSON:\n"
        + json.dumps(data, ensure_ascii=False)
        + guidance
    )


def normalize_proposal(value: dict) -> dict:
    if not isinstance(value, dict) or not isinstance(value.get("summary"), str) or not isinstance(value.get("warnings"), list):
        raise ValueError("代理没有返回完整的提案结构")
    if not all(isinstance(warning, str) for warning in value["warnings"]):
        raise ValueError("提案警告格式无效")
    day_json = value.get("day_json")
    if not isinstance(day_json, str):
        raise ValueError("代理没有返回当天行程 JSON")
    return {"summary": value["summary"], "day": json.loads(day_json), "warnings": value["warnings"]}


def run_codex(data: dict, date: str, request: str, cli_bin: str) -> dict:
    prompt = proposal_prompt(data, date, request, invoke_skill=True)
    with tempfile.TemporaryDirectory(prefix="trip-workbench-") as temp:
        output = Path(temp) / "proposal.json"
        command = [cli_bin, "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "-C", str(ROOT), "--output-schema", str(SCHEMA), "--output-last-message", str(output), "-"]
        result = subprocess.run(command, input=prompt, text=True, capture_output=True, timeout=240, check=False)
        if result.returncode or not output.exists():
            detail = (result.stderr or result.stdout).strip()[-800:]
            raise RuntimeError(f"Codex 未能生成提案：{detail or '未知错误'}")
        return normalize_proposal(json.loads(output.read_text(encoding="utf-8")))


def run_claude(data: dict, date: str, request: str, cli_bin: str) -> dict:
    prompt = proposal_prompt(data, date, request, invoke_skill=False)
    schema = SCHEMA.read_text(encoding="utf-8")
    command = [cli_bin, "--setting-sources", "", "--strict-mcp-config", "--tools", "", "--disallowedTools", "mcp__*", "--no-session-persistence", "--output-format", "json", "--json-schema", schema, "-p", "Read the instructions and trip JSON from stdin; return the requested proposal."]
    result = subprocess.run(command, cwd=ROOT, input=prompt, text=True, capture_output=True, timeout=240, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()[-800:]
        raise RuntimeError(f"Claude Code 未能生成提案：{detail or '未知错误'}")
    envelope = json.loads(result.stdout)
    if envelope.get("is_error") or envelope.get("subtype") not in (None, "success"):
        raise RuntimeError("Claude Code 未能完成提案")
    value = envelope.get("structured_output")
    if value is None:
        value = json.loads(envelope.get("result", "{}"))
    return normalize_proposal(value)
