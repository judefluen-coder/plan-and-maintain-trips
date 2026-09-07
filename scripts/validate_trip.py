#!/usr/bin/env python3
"""Validate the canonical JSON state used by plan-and-maintain-trips."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


BOOKING_STATUSES = {
    "bookable",
    "not_released",
    "date_not_in_system",
    "sold_out",
    "walk_in",
    "same_day",
    "booked",
    "needs_recheck",
    "unknown",
}
VOLATILE_STATUSES = {
    "bookable",
    "not_released",
    "date_not_in_system",
    "sold_out",
    "needs_recheck",
}
RIGIDITY_VALUES = {"hard", "soft", "optional"}
PLACEHOLDER_PATTERN = re.compile(r"(?:\bTBD\b|\bTODO\b|待定|待补|_{4,})", re.I)


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_date(value: Any, path: str, findings: Findings) -> date | None:
    if not isinstance(value, str):
        findings.error(f"{path} must be an ISO date string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        findings.error(f"{path} must use YYYY-MM-DD: {value!r}")
        return None


def parse_datetime(value: Any, path: str, findings: Findings) -> datetime | None:
    if not isinstance(value, str):
        findings.error(f"{path} must be an ISO datetime string")
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        findings.error(f"{path} must be an ISO datetime: {value!r}")
        return None


def require_list(data: dict[str, Any], key: str, findings: Findings) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        findings.error(f"{key} must be a list")
        return []
    return value


def require_unique_ids(items: list[Any], group: str, findings: Findings) -> set[str]:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            findings.error(f"{group}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            findings.error(f"{group}[{index}].id must be a non-empty string")
        elif item_id in seen:
            findings.error(f"duplicate {group} id: {item_id}")
        else:
            seen.add(item_id)
    return seen


def scan_placeholders(value: Any, path: str, findings: Findings) -> None:
    if isinstance(value, str) and PLACEHOLDER_PATTERN.search(value):
        findings.warn(f"unresolved placeholder at {path}: {value!r}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            scan_placeholders(item, f"{path}[{index}]", findings)
    elif isinstance(value, dict):
        for key, item in value.items():
            scan_placeholders(item, f"{path}.{key}", findings)


def validate(data: Any) -> tuple[Findings, dict[str, int]]:
    findings = Findings()
    counts = {"segments": 0, "anchors": 0, "bookings": 0, "days": 0}
    if not isinstance(data, dict):
        findings.error("top-level JSON value must be an object")
        return findings, counts

    if data.get("schema_version") != 1:
        findings.error("schema_version must be 1")

    trip = data.get("trip")
    if not isinstance(trip, dict):
        findings.error("trip must be an object")
        trip = {}

    start = parse_date(trip.get("start_date"), "trip.start_date", findings)
    end = parse_date(trip.get("end_date"), "trip.end_date", findings)
    if start and end and end < start:
        findings.error("trip.end_date must not precede trip.start_date")

    travelers = trip.get("travelers")
    if not isinstance(travelers, int) or isinstance(travelers, bool) or travelers < 1:
        findings.error("trip.travelers must be a positive integer")

    segments = require_list(data, "segments", findings)
    anchors = require_list(data, "anchors", findings)
    bookings = require_list(data, "bookings", findings)
    days = require_list(data, "days", findings)
    counts.update(
        segments=len(segments), anchors=len(anchors), bookings=len(bookings), days=len(days)
    )

    require_unique_ids(segments, "segments", findings)
    anchor_ids = require_unique_ids(anchors, "anchors", findings)
    booking_ids = require_unique_ids(bookings, "bookings", findings)

    segment_ranges: list[tuple[date, date, str]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            continue
        segment_start = parse_date(segment.get("start_date"), f"segments[{index}].start_date", findings)
        segment_end = parse_date(segment.get("end_date"), f"segments[{index}].end_date", findings)
        if not isinstance(segment.get("base"), str) or not segment["base"].strip():
            findings.error(f"segments[{index}].base must be a non-empty string")
        if segment_start and segment_end:
            if segment_end <= segment_start:
                findings.error(f"segments[{index}].end_date must be after start_date")
            else:
                actual_nights = (segment_end - segment_start).days
                if segment.get("nights") != actual_nights:
                    findings.error(
                        f"segments[{index}].nights is {segment.get('nights')!r}; expected {actual_nights}"
                    )
                segment_ranges.append((segment_start, segment_end, str(segment.get("id", index))))
            if start and segment_start < start:
                findings.error(f"segments[{index}] starts before the trip")
            if end and segment_end > end:
                findings.error(f"segments[{index}] ends after the trip end date")

    segment_ranges.sort()
    for previous, current in zip(segment_ranges, segment_ranges[1:]):
        if current[0] < previous[1]:
            findings.error(f"segments {previous[2]} and {current[2]} overlap")
        elif current[0] > previous[1]:
            findings.warn(f"gap between segments {previous[2]} and {current[2]}")

    for index, booking in enumerate(bookings):
        if not isinstance(booking, dict):
            continue
        status = booking.get("status")
        if status not in BOOKING_STATUSES:
            findings.error(
                f"bookings[{index}].status must be one of {sorted(BOOKING_STATUSES)}"
            )
        if status == "unknown":
            findings.warn(f"bookings[{index}] still has temporary status 'unknown'")
        if status in VOLATILE_STATUSES:
            if not isinstance(booking.get("source_url"), str) or not booking["source_url"].startswith(
                ("https://", "http://")
            ):
                findings.warn(f"bookings[{index}] needs an official source_url")
            checked_at = booking.get("checked_at")
            if checked_at is None:
                findings.warn(f"bookings[{index}] needs checked_at evidence")
            else:
                parse_datetime(checked_at, f"bookings[{index}].checked_at", findings)
        intended_date = booking.get("intended_date")
        if intended_date is not None:
            parsed = parse_date(intended_date, f"bookings[{index}].intended_date", findings)
            if parsed and start and end and not (start <= parsed <= end):
                findings.error(f"bookings[{index}].intended_date lies outside the trip")

    for index, anchor in enumerate(anchors):
        if not isinstance(anchor, dict):
            continue
        rigidity = anchor.get("rigidity")
        if rigidity not in RIGIDITY_VALUES:
            findings.error(f"anchors[{index}].rigidity must be hard, soft, or optional")
        parsed = parse_date(anchor.get("date"), f"anchors[{index}].date", findings)
        if parsed and start and end and not (start <= parsed <= end):
            findings.error(f"anchors[{index}].date lies outside the trip")
        booking_id = anchor.get("booking_id")
        if booking_id is not None and booking_id not in booking_ids:
            findings.error(f"anchors[{index}].booking_id references missing booking {booking_id!r}")

    day_dates: dict[date, int] = {}
    for index, day_item in enumerate(days):
        if not isinstance(day_item, dict):
            findings.error(f"days[{index}] must be an object")
            continue
        parsed = parse_date(day_item.get("date"), f"days[{index}].date", findings)
        if not parsed:
            continue
        if parsed in day_dates:
            findings.error(f"duplicate day date {parsed.isoformat()}")
        day_dates[parsed] = index
        if start and end and not (start <= parsed <= end):
            findings.error(f"days[{index}].date lies outside the trip")
        anchor_refs = day_item.get("anchor_ids", [])
        if not isinstance(anchor_refs, list):
            findings.error(f"days[{index}].anchor_ids must be a list")
        else:
            for anchor_id in anchor_refs:
                if anchor_id not in anchor_ids:
                    findings.error(f"days[{index}] references missing anchor {anchor_id!r}")

    if start and end:
        expected_dates = {start + timedelta(days=offset) for offset in range((end - start).days + 1)}
        for missing in sorted(expected_dates - set(day_dates)):
            findings.error(f"missing day entry for {missing.isoformat()}")

    scan_placeholders(data, "$", findings)
    return findings, counts


def load_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="trip JSON path, or - for stdin")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit JSON")
    args = parser.parse_args()

    try:
        data = load_json(args.path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}", file=sys.stderr)
        return 2

    findings, counts = validate(data)
    failed = bool(findings.errors or (args.strict and findings.warnings))

    if args.json_output:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "strict": args.strict,
                    "counts": counts,
                    "errors": findings.errors,
                    "warnings": findings.warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for message in findings.errors:
            print(f"ERROR: {message}")
        for message in findings.warnings:
            print(f"WARNING: {message}")
        status = "PASS" if not failed else "FAIL"
        print(
            f"{status}: {counts['days']} days, {counts['segments']} segments, "
            f"{counts['anchors']} anchors, {counts['bookings']} bookings; "
            f"{len(findings.errors)} errors, {len(findings.warnings)} warnings"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
