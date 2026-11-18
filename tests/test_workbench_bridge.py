"""Safety and write-boundary tests for the local workbench bridge."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workbench_bridge", ROOT / "bridge" / "server.py")
bridge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.trip_path = Path(self.temp.name) / "trip.json"
        self.data = json.loads((ROOT / "assets" / "trip.example.json").read_text(encoding="utf-8"))
        self.data["trip"]["demo"] = False
        self.trip_path.write_text(json.dumps(self.data), encoding="utf-8")
        self.server = bridge.Bridge(("127.0.0.1", 0), self.trip_path, {"https://example.test"}, sys.executable)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, path: str, payload: dict | None = None, *, origin: str = "https://example.test", token: str | None = None) -> tuple[int, dict]:
        body = json.dumps(payload).encode() if payload is not None else None
        req = Request(self.url + path, data=body, headers={"Origin": origin, "X-Trip-Token": token or self.server.token, "Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try:
            with urlopen(req, timeout=3) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            with exc:
                return exc.code, json.load(exc)

    def test_rejects_other_origins(self) -> None:
        status, _ = self.request("/api/trip", origin="https://untrusted.test")
        self.assertEqual(status, 403)

    def test_hard_anchor_cannot_move(self) -> None:
        day = copy.deepcopy(self.data["days"][1])
        day["items"][0]["start"] = "11:00"
        self.assertTrue(any("硬预约" in error for error in bridge.check_proposed_day(self.data, day["date"], day)))

    def test_hard_anchor_cannot_be_softened(self) -> None:
        day = copy.deepcopy(self.data["days"][1])
        day["items"][0]["rigidity"] = "optional"
        self.assertTrue(any("硬预约" in error for error in bridge.check_proposed_day(self.data, day["date"], day)))

    def test_proposal_requires_confirmation_and_creates_backup(self) -> None:
        before = self.data["days"][1]
        after = copy.deepcopy(before)
        after["items"] = [item for item in after["items"] if item["id"] != "garden"]
        after["first_cut"] = "Neighborhood dinner"
        result = {"summary": "移除可选花园", "day": after, "warnings": []}
        with patch.object(bridge, "run_codex", return_value=result):
            status, proposed = self.request("/api/propose", {"date": before["date"], "request": "把这一天放松一点"})
        self.assertEqual(status, 200, proposed)
        self.assertEqual(self.data, json.loads(self.trip_path.read_text(encoding="utf-8")))
        status, applied = self.request("/api/apply", {"proposal_id": proposed["proposal_id"]})
        self.assertEqual(status, 200, applied)
        self.assertEqual(len(applied["trip"]["days"][1]["items"]), 2)
        self.assertTrue(self.trip_path.with_name("trip.json.bak").is_file())

    def test_stale_proposal_does_not_overwrite_external_edit(self) -> None:
        before = self.data["days"][1]
        result = {"summary": "保持原计划", "day": copy.deepcopy(before), "warnings": []}
        with patch.object(bridge, "run_codex", return_value=result):
            _, proposed = self.request("/api/propose", {"date": before["date"], "request": "检查一下当天强度"})
        self.data["trip"]["title"] = "Changed in Codex"
        self.trip_path.write_text(json.dumps(self.data), encoding="utf-8")
        status, _ = self.request("/api/apply", {"proposal_id": proposed["proposal_id"]})
        self.assertEqual(status, 409)
        self.assertEqual("Changed in Codex", json.loads(self.trip_path.read_text(encoding="utf-8"))["trip"]["title"])

    def test_claude_bridge_uses_same_validation_boundary(self) -> None:
        self.server.provider = "claude"
        self.server.cli_bin = sys.executable
        status, health = self.request("/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["provider"], "claude")
        self.assertTrue(health["provider_available"])
        day = copy.deepcopy(self.data["days"][1])
        day["items"][0]["start"] = "11:00"
        with patch.object(bridge, "run_claude", return_value={"summary": "移动预约", "day": day, "warnings": []}):
            status, rejected = self.request("/api/propose", {"date": day["date"], "request": "把当天安排晚一些"})
        self.assertEqual(status, 422)
        self.assertIn("硬预约", " ".join(rejected["details"]))
        self.assertEqual(self.data, json.loads(self.trip_path.read_text(encoding="utf-8")))

    def test_manual_bridge_reads_external_agent_changes_without_model(self) -> None:
        self.server.provider = "manual"
        self.server.cli_bin = None
        status, health = self.request("/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(health["provider_available"])
        self.assertFalse(health["can_propose"])
        self.assertEqual(health["trip_path"], str(self.trip_path.resolve()))
        status, before = self.request("/api/trip")
        self.assertEqual(status, 200)
        self.assertEqual(before["validation_errors"], [])
        self.data["trip"]["title"] = "Edited by another agent"
        self.trip_path.write_text(json.dumps(self.data), encoding="utf-8")
        status, after = self.request("/api/trip")
        self.assertEqual(status, 200)
        self.assertNotEqual(before["version"], after["version"])
        self.assertEqual(after["trip"]["trip"]["title"], "Edited by another agent")
        status, _ = self.request("/api/propose", {"date": self.data["days"][0]["date"], "request": "放松当天安排"})
        self.assertEqual(status, 409)


if __name__ == "__main__":
    unittest.main()
