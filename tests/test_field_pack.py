"""Behavioral checks for derived trip artifacts and disruption advice."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.export_field_pack import calendar, kml, load, page
from scripts.replan_day import propose
from scripts.suggest_food import candidates
from scripts.validate_trip import validate


EXAMPLE = Path(__file__).resolve().parents[1] / "assets" / "trip.example.json"


class FieldPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.days, cls.zone = load(EXAMPLE)

    def test_calendar_converts_local_time_and_protects_anchor(self):
        output = calendar(self.data, self.days, self.zone)
        self.assertIn("DTSTART:20300502T090000Z", output)
        self.assertIn("TRIGGER:-PT60M", output)
        self.assertEqual(output.count("BEGIN:VEVENT"), 9)

    def test_kml_contains_ordered_points(self):
        root = ET.fromstring(kml(self.data, self.days))
        namespace = {"k": "http://www.opengis.net/kml/2.2"}
        self.assertEqual(len(root.findall(".//k:Point", namespace)), 7)
        self.assertEqual(len(root.findall(".//k:LineString", namespace)), 3)

    def test_offline_page_embeds_all_days_without_remote_assets(self):
        output = page(self.data, self.days)
        self.assertIn('type="application/json"', output)
        self.assertIn("2030-05-05", output)
        self.assertNotIn("<script src=", output)
        self.assertNotIn("@import", output)

    def test_replan_warns_on_fixed_booking_without_mutation(self):
        original = copy.deepcopy(self.data)
        result = propose(self.data, "2030-05-02", 45, None, True)
        self.assertEqual(self.data, original)
        self.assertEqual(result["plan"][0]["start"], "10:00")
        self.assertTrue(any("fixed" in warning for warning in result["warnings"]))
        self.assertTrue(any(item["name"] == "Garden recovery break" for item in result["removed"]))

    def test_food_is_near_route_but_not_claimed_open(self):
        found, cautions = candidates(self.data, "2030-05-01", "lunch", 1.5)
        self.assertEqual(len(found), 1)
        self.assertLess(found[0]["distance_km"], 0.1)
        self.assertEqual(cautions, [])

    def test_structured_items_reject_bad_coordinate_and_time(self):
        bad = copy.deepcopy(self.data)
        bad["days"][0]["items"][1]["lat"] = 999
        bad["days"][0]["items"][1]["end"] = "09:00"
        findings, _ = validate(bad)
        self.assertTrue(any("coordinate" in error for error in findings.errors))
        self.assertTrue(any("end must follow" in error for error in findings.errors))

    def test_text_only_trip_stays_valid_but_cannot_export_empty_map(self):
        legacy = copy.deepcopy(self.data)
        for day in legacy["days"]:
            day["items"] = [item["name"] if isinstance(item, dict) else item for item in day["items"]]
        findings, _ = validate(legacy)
        self.assertEqual(findings.errors, [])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trip.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "geocoded"):
                load(path)


if __name__ == "__main__":
    unittest.main()
