#!/usr/bin/env python3
"""Rank stored restaurant candidates against a day's route and meal time."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path


def distance_km(a: dict, b: dict) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    part = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 12742 * math.asin(min(1, math.sqrt(part)))


def candidates(data: dict, target_date: str, meal: str, radius_km: float) -> tuple[list[dict], list[str]]:
    day = next((d for d in data.get("days", []) if d.get("date") == target_date), None)
    if day is None:
        raise ValueError(f"no day for {target_date}")
    items = [i for i in day.get("items", []) if isinstance(i, dict)]
    meal_item = next((i for i in items if i.get("meal") == meal and "lat" in i), None)
    if meal_item:
        target = meal_item
    else:
        hour = 12 if meal == "lunch" else 19
        timed = [i for i in items if "lat" in i and i.get("start") and abs(int(i["start"][:2]) - hour) <= 3]
        if not timed:
            raise ValueError("add a geocoded meal item or a timed nearby stop before suggesting food")
        target = min(timed, key=lambda i: abs(int(i["start"][:2]) - hour))
    weekday = date.fromisoformat(target_date).strftime("%a").lower()
    found, cautions = [], []
    excluded = {str(x.get("item", "")).lower() for x in data.get("exclusions", []) if isinstance(x, dict)}
    for restaurant in data.get("restaurants", []):
        if not isinstance(restaurant, dict) or not isinstance(restaurant.get("name"), str):
            continue
        if restaurant["name"].lower() in excluded or restaurant.get("base") not in (None, day.get("base")):
            continue
        if meal not in restaurant.get("meals", []):
            continue
        if "lat" not in restaurant or "lon" not in restaurant:
            cautions.append(f"{restaurant['name']}: missing coordinates")
            continue
        if weekday in restaurant.get("closed_weekdays", []):
            continue
        try:
            dist = distance_km(target, restaurant)
        except (TypeError, ValueError, KeyError):
            cautions.append(f"{restaurant['name']}: invalid coordinates")
            continue
        if dist > radius_km:
            continue
        distance_label = f"约 {round(dist * 1000):d} 米" if dist < 0.1 else f"约 {dist:.1f} 公里"
        found.append({"name": restaurant["name"], "distance_km": round(dist, 2), "price_level": restaurant.get("price_level"), "reservation": restaurant.get("reservation"), "source_url": restaurant.get("source_url"), "checked_at": restaurant.get("checked_at"), "reason": f"{distance_label}，靠近 {target['name']}"})
    found.sort(key=lambda r: r["distance_km"])
    return found, cautions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trip_json", type=Path)
    parser.add_argument("--date", required=True)
    parser.add_argument("--meal", choices=("lunch", "dinner"), required=True)
    parser.add_argument("--radius-km", type=float, default=1.5)
    parser.add_argument("--catalog", type=Path, help="optional reusable city restaurant JSON")
    args = parser.parse_args()
    if args.radius_km <= 0:
        parser.error("--radius-km must be positive")
    try:
        data = json.loads(args.trip_json.read_text(encoding="utf-8"))
        if args.catalog:
            catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
            if not isinstance(catalog.get("restaurants"), list):
                raise ValueError("catalog must contain a restaurants list")
            by_id = {r.get("id", r.get("name")): r for r in catalog["restaurants"] if isinstance(r, dict)}
            by_id.update({r.get("id", r.get("name")): r for r in data.get("restaurants", []) if isinstance(r, dict)})
            data["restaurants"] = list(by_id.values())
        found, cautions = candidates(data, args.date, args.meal, args.radius_km)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"date": args.date, "meal": args.meal, "candidates": found, "cautions": cautions, "note": "距离为直线距离；餐厅营业时间、空位和实际步行路线须在出发前复查。"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
