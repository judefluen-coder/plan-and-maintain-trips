#!/usr/bin/env python3
"""Loopback-only bridge between the static workbench and a user's Codex CLI."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Path(__file__).with_name("proposal.schema.json")
sys.path.insert(0, str(ROOT / "scripts"))
from validate_trip import validate  # noqa: E402


def fingerprint(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def find_day(data: dict, date: str) -> dict:
    return next((day for day in data.get("days", []) if day.get("date") == date), None)


def check_proposed_day(data: dict, date: str, proposed: dict) -> list[str]:
    errors = []
    original = find_day(data, date)
    if not original:
        return ["所选日期不在旅程中"]
    if not isinstance(proposed, dict) or proposed.get("date") != date:
        return ["提案日期与所选日期不一致"]
    if not isinstance(proposed.get("items"), list):
        return ["提案缺少行程项目"]
    old_items = {item.get("id"): item for item in original.get("items", []) if isinstance(item, dict)}
    new_items = {item.get("id"): item for item in proposed["items"] if isinstance(item, dict)}
    hard_ids = {anchor.get("id") for anchor in data.get("anchors", []) if anchor.get("date") == date and anchor.get("rigidity") == "hard"}
    anchor_refs = proposed.get("anchor_ids", [])
    if not isinstance(anchor_refs, list) or not hard_ids.issubset(set(anchor_refs)):
        errors.append("硬预约引用不得从当天移除")
    for item_id, item in old_items.items():
        if item.get("rigidity") != "hard" and item.get("anchor_id") not in hard_ids:
            continue
        replacement = new_items.get(item_id)
        if replacement is None:
            errors.append(f"硬预约项目 {item_id} 不得删除")
            continue
        if item != replacement:
            errors.append(f"硬预约项目 {item_id} 不得变更")
    candidate = copy.deepcopy(data)
    candidate["days"] = [proposed if day.get("date") == date else day for day in data["days"]]
    findings, _ = validate(candidate)
    errors.extend(findings.errors)
    return errors


def run_codex(data: dict, date: str, request: str, codex_bin: str) -> dict:
    prompt = (
        "Use the installed $plan-and-maintain-trips skill to propose a scoped travel-day revision. "
        "Return only JSON conforming to the supplied schema. Do not edit any files. "
        "day_json must be a JSON-encoded string of a complete day object for only the selected date, preserving its date, "
        "all hard appointments, their times, locations, anchor IDs and booking IDs. "
        "Do not invent verified hours, ticket status or coordinates; retain uncertainty in warnings. "
        "Keep the existing trip schema and structured item IDs where an item is unchanged. "
        "Write the summary and warnings in the same language as the user request.\n\n"
        f"Selected date: {date}\nUser request: {request}\n\nCanonical trip JSON:\n"
        + json.dumps(data, ensure_ascii=False)
    )
    with tempfile.TemporaryDirectory(prefix="trip-workbench-") as temp:
        output = Path(temp) / "proposal.json"
        command = [codex_bin, "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "-C", str(ROOT), "--output-schema", str(SCHEMA), "--output-last-message", str(output), "-"]
        result = subprocess.run(command, input=prompt, text=True, capture_output=True, timeout=240, check=False)
        if result.returncode or not output.exists():
            detail = (result.stderr or result.stdout).strip()[-800:]
            raise RuntimeError(f"Codex 未能生成提案：{detail or '未知错误'}")
        result = json.loads(output.read_text(encoding="utf-8"))
        return {"summary": result["summary"], "day": json.loads(result["day_json"]), "warnings": result["warnings"]}


class Bridge(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], trip_path: Path, origins: set[str], codex_bin: str):
        super().__init__(address, Handler)
        self.trip_path = trip_path.resolve()
        self.origins = origins
        self.codex_bin = codex_bin
        self.token = secrets.token_urlsafe(32)
        self.proposals: dict[str, dict] = {}
        self.lock = threading.Lock()

    def read_trip(self) -> dict:
        return json.loads(self.trip_path.read_text(encoding="utf-8"))


class Handler(BaseHTTPRequestHandler):
    server: Bridge

    def cors_origin(self) -> str | None:
        origin = self.headers.get("Origin", "")
        return origin if origin in self.server.origins else None

    def respond(self, status: int, value: dict) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        origin = self.cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        return self.cors_origin() is not None and secrets.compare_digest(self.headers.get("X-Trip-Token", ""), self.server.token)

    def do_OPTIONS(self) -> None:
        if not self.cors_origin():
            self.respond(403, {"error": "来源未获授权"})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Trip-Token")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self) -> None:
        if not self.authorized():
            self.respond(403, {"error": "请从工作台完成本机配对"})
            return
        path = urlparse(self.path).path
        if path == "/api/health":
            self.respond(200, {"ok": True, "codex_available": bool(shutil.which(self.server.codex_bin))})
        elif path == "/api/trip":
            try:
                data = self.server.read_trip()
                self.respond(200, {"trip": data, "version": fingerprint(data)})
            except (OSError, ValueError) as exc:
                self.respond(500, {"error": f"无法读取旅程：{exc}"})
        else:
            self.respond(404, {"error": "未知接口"})

    def do_POST(self) -> None:
        if not self.authorized():
            self.respond(403, {"error": "请从工作台完成本机配对"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.respond(400, {"error": "Content-Length 无效"})
            return
        if length < 0 or length > 16000:
            self.respond(413, {"error": "请求过大"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (ValueError, TypeError):
            self.respond(400, {"error": "请求不是有效 JSON"})
            return
        if not isinstance(payload, dict):
            self.respond(400, {"error": "请求必须是 JSON 对象"})
            return
        path = urlparse(self.path).path
        if path == "/api/propose":
            self.propose(payload)
        elif path == "/api/apply":
            self.apply(payload)
        else:
            self.respond(404, {"error": "未知接口"})

    def propose(self, payload: dict) -> None:
        date, request = payload.get("date"), payload.get("request")
        if not isinstance(date, str) or not isinstance(request, str) or not 3 <= len(request.strip()) <= 700:
            self.respond(400, {"error": "请选择日期，并输入 3–700 字的修改要求"})
            return
        if not shutil.which(self.server.codex_bin):
            self.respond(503, {"error": "本机未找到 Codex CLI"})
            return
        try:
            data = self.server.read_trip()
            if not find_day(data, date):
                self.respond(400, {"error": "所选日期不在旅程中"})
                return
            result = run_codex(data, date, request.strip(), self.server.codex_bin)
            errors = check_proposed_day(data, date, result.get("day"))
            if errors:
                self.respond(422, {"error": "提案未通过安全校验", "details": errors[:8]})
                return
            proposal_id = secrets.token_urlsafe(18)
            with self.server.lock:
                self.server.proposals = {proposal_id: {"version": fingerprint(data), "date": date, "result": result}}
            self.respond(200, {"proposal_id": proposal_id, "proposal": result, "before": find_day(data, date)})
        except subprocess.TimeoutExpired:
            self.respond(504, {"error": "Codex 生成超时，请缩小修改范围后重试"})
        except (OSError, ValueError, RuntimeError) as exc:
            self.respond(500, {"error": str(exc)})

    def apply(self, payload: dict) -> None:
        proposal_id = payload.get("proposal_id")
        with self.server.lock:
            proposal = self.server.proposals.get(proposal_id)
            if not proposal:
                self.respond(404, {"error": "提案已失效，请重新生成"})
                return
            try:
                data = self.server.read_trip()
                if data.get("trip", {}).get("demo"):
                    self.respond(403, {"error": "仓库示例不可写，请使用自己的 trip.json"})
                    return
                if fingerprint(data) != proposal["version"]:
                    self.respond(409, {"error": "旅程已在别处修改，请刷新后重新生成提案"})
                    return
                date = proposal["date"]
                day = proposal["result"]["day"]
                errors = check_proposed_day(data, date, day)
                if errors:
                    self.respond(422, {"error": "提案未通过安全校验", "details": errors[:8]})
                    return
                data["days"] = [day if old.get("date") == date else old for old in data["days"]]
                backup = self.server.trip_path.with_name(self.server.trip_path.name + ".bak")
                shutil.copy2(self.server.trip_path, backup)
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.server.trip_path.parent, prefix=".trip-", suffix=".json", delete=False) as handle:
                    temp_path = Path(handle.name)
                    json.dump(data, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                try:
                    os.replace(temp_path, self.server.trip_path)
                finally:
                    temp_path.unlink(missing_ok=True)
                self.server.proposals.clear()
                self.respond(200, {"trip": data, "version": fingerprint(data)})
            except (OSError, ValueError) as exc:
                self.respond(500, {"error": f"写入失败：{exc}"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trip", required=True, type=Path, help="要操作的本地 trip.json")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--web-url", default="https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/")
    parser.add_argument("--allow-origin", action="append", default=["https://judefluen-coder.github.io", "http://127.0.0.1:8765", "http://localhost:8765"])
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    if not args.trip.is_file():
        parser.error("--trip 必须指向现有的 trip.json")
    if not 1024 <= args.port <= 65535:
        parser.error("--port 应在 1024–65535 之间")
    server = Bridge(("127.0.0.1", args.port), args.trip, set(args.allow_origin), args.codex_bin)
    url = f"{args.web_url}#port={args.port}&token={server.token}"
    print("本机桥接已启动。只访问你信任的工作台页面；关闭此进程即断开连接。", flush=True)
    print(url, flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
