"""Keep the workbench's Paris replay aligned with the archived itinerary."""

import json
import unittest
from pathlib import Path

from scripts.render_route_map import route_from_trip
from scripts.validate_trip import validate


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "assets" / "paris.demo.json"


class ParisDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DEMO.read_text(encoding="utf-8"))

    def test_five_historical_sightseeing_days_are_mappable(self):
        findings, _ = validate(self.data)
        self.assertEqual(findings.errors, [])
        self.assertEqual(findings.warnings, [])
        self.assertEqual([day["date"] for day in self.data["days"]], [f"2026-09-{day}" for day in range(25, 30)])
        route = route_from_trip(str(DEMO), None, None)
        self.assertEqual(len(route["days"]), 5)
        self.assertTrue(all(len(day["stops"]) >= 2 for day in route["days"]))

    def test_protected_dates_and_historical_ticket_boundary(self):
        anchors = {anchor["id"]: anchor for anchor in self.data["anchors"]}
        self.assertEqual((anchors["orsay-slot"]["date"], anchors["orsay-slot"]["time"]), ("2026-09-26", "13:00"))
        self.assertEqual(anchors["louvre-date"]["date"], "2026-09-27")
        self.assertEqual((anchors["versailles-slot"]["date"], anchors["versailles-slot"]["time"]), ("2026-09-29", "12:00"))
        self.assertTrue(all(booking["status"] == "needs_recheck" for booking in self.data["bookings"]))
        self.assertTrue(self.data["trip"]["demo_kind"] == "historical")

    def test_daily_briefings_and_booking_checklist_are_present(self):
        self.assertEqual(len(self.data["planning_checklist"]), 8)
        self.assertTrue(all(entry["url"].startswith("https://") for entry in self.data["planning_checklist"]))
        dates = {day["date"] for day in self.data["days"]}
        self.assertTrue(all(entry.get("date") in dates or entry.get("when") for entry in self.data["planning_checklist"]))
        for day in self.data["days"]:
            guide = day["guide"]
            self.assertTrue(all(guide.get(field) for field in ("before", "transport", "food", "decision", "links")))
            self.assertTrue(all(link["url"].startswith("https://") for link in guide["links"]))


if __name__ == "__main__":
    unittest.main()
