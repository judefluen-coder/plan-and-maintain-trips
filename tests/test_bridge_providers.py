"""Provider command construction and structured-output parsing tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bridge"))
import providers  # noqa: E402


class ProviderTests(unittest.TestCase):
    def test_claude_disables_tools_and_parses_structured_output(self) -> None:
        day = {"date": "2030-05-01", "items": []}
        envelope = {"type": "result", "subtype": "success", "is_error": False, "structured_output": {"summary": "调整一天", "day_json": json.dumps(day), "warnings": []}}
        completed = type("Completed", (), {"returncode": 0, "stdout": json.dumps(envelope), "stderr": ""})()
        with patch.object(providers.subprocess, "run", return_value=completed) as run:
            result = providers.run_claude({"trip": {}, "days": [day]}, day["date"], "放松一点", "claude")
        command = run.call_args.args[0]
        self.assertEqual(result["day"], day)
        self.assertIn("--tools", command)
        self.assertEqual(command[command.index("--tools") + 1], "")
        self.assertIn("--strict-mcp-config", command)
        self.assertIn("--json-schema", command)
        self.assertIn("plan-and-maintain-trips", run.call_args.kwargs["input"])

    def test_rejects_incomplete_agent_output(self) -> None:
        with self.assertRaises(ValueError):
            providers.normalize_proposal({"summary": "ok", "warnings": [], "day_json": "not json"})


if __name__ == "__main__":
    unittest.main()
