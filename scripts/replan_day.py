#!/usr/bin/env python3
"""Propose a day-of schedule after a delay, closure, or rain; never edit trip.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def minute(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def clock(value: int) -> str:
    suffix = f" (+{value // 1440} day)" if value >= 1440 else ""
    value %= 1440
    return f"{value // 60:02d}:{value % 60:02d}{suffix}"


def propose(data: dict, target_date: str, delay: int, closed_id: str | None, rain: bool) -> dict:
    day = next((d for d in data.get("days", []) if d.get("date") == target_date), None)
    if day is None:
        raise ValueError(f"no day for {target_date}")
    items = day.get("items", [])
    if not items or any(not isinstance(i, dict) or not all(k in i for k in ("name", "start", "end")) for i in items):
        raise ValueError("day-of replanning needs structured, timed items for the selected day")
    anchors = {a.get("id"): a for a in data.get("anchors", []) if isinstance(a, dict)}
    bookings = {b.get("id"): b for b in data.get("bookings", []) if isinstance(b, dict)}
    anchor_by_name = {str(a.get("name", "")).casefold(): a for a in anchors.values()}
    plan, removed, warnings = [], [], []
    cursor = minute(items[0]["start"]) + delay
    for item in items:
        old_start, old_end = minute(item["start"]), minute(item["end"])
        if old_end <= old_start:
            raise ValueError(f"{item['name']}: end must follow start")
        anchor = anchors.get(item.get("anchor_id")) or anchor_by_name.get(str(item["name"]).casefold(), {})
        hard = item.get("rigidity") == "hard" or anchor.get("rigidity") == "hard"
        affected_by_closure = closed_id and closed_id in (item.get("id"), item.get("anchor_id"), item.get("booking_id"))
        affected_by_rain = rain and item.get("weather_sensitive") and not hard
        if affected_by_closure or affected_by_rain:
            reason = "closed" if affected_by_closure else "rain-sensitive"
            removed.append({"name": item["name"], "reason": reason, "hard": hard})
            if hard:
                warnings.append(f"{item['name']}: fixed booking may be unusable; contact operator and check refund or replacement")
            continue
        proposed_start = old_start if hard else max(old_start, cursor)
        proposed_end = proposed_start + old_end - old_start
        if proposed_end >= 1440:
            warnings.append(f"{item['name']}: proposed end spills into the next day; review or cut this stop")
        if hard and cursor > old_start:
            warnings.append(f"{item['name']}: delayed arrival conflicts with fixed {item['start']} start; manual decision required")
        next_hard = next((other for other in items if minute(other["start"]) >= old_end and (other.get("rigidity") == "hard" or (anchors.get(other.get("anchor_id")) or anchor_by_name.get(str(other.get("name", "")).casefold(), {})).get("rigidity") == "hard")), None)
        if not hard and next_hard and proposed_end > minute(next_hard["start"]):
            if item.get("rigidity") == "optional" or item.get("id") == day.get("first_cut_id"):
                removed.append({"name": item["name"], "reason": "protect next fixed appointment", "hard": False})
                continue
            warnings.append(f"{item['name']}: overlaps next fixed appointment {next_hard['name']}; shorten or remove manually")
        cursor = proposed_end
        booking = bookings.get(item.get("booking_id") or anchor.get("booking_id"), {})
        if booking and proposed_start != old_start:
            warnings.append(f"{item['name']}: booking status {booking.get('status', 'unknown')} must be reconfirmed before moving")
        plan.append({"id": item.get("id"), "name": item["name"], "start": clock(proposed_start), "end": clock(proposed_end), "original_start": item["start"], "hard": hard})
    return {"date": target_date, "proposal_only": True, "protected_anchor_ids": day.get("anchor_ids", []), "plan": plan, "removed": removed, "warnings": list(dict.fromkeys(warnings)), "weather_fallback": day.get("weather_fallback") if rain else None, "next_steps": ["Check operator notices and live transit", "Review affected meals, bookings, map and field card", "Accept changes into trip.json only after resolving warnings"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trip_json", type=Path)
    parser.add_argument("--date", required=True)
    parser.add_argument("--delay-minutes", type=int, default=0)
    parser.add_argument("--closed-id")
    parser.add_argument("--rain", action="store_true")
    args = parser.parse_args()
    if args.delay_minutes < 0:
        parser.error("--delay-minutes must be non-negative")
    try:
        data = json.loads(args.trip_json.read_text(encoding="utf-8"))
        result = propose(data, args.date, args.delay_minutes, args.closed_id, args.rain)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
