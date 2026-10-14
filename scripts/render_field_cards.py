#!/usr/bin/env python3
"""Render mobile SVG day cards and searchable Markdown from a structured trip."""

from __future__ import annotations

import argparse
import html
import json
import sys
import unicodedata
from pathlib import Path


COLORS = ("#b74742", "#188066", "#c87a13", "#286aa2", "#78599e", "#138c91")
INK = "#173253"
MUTED = "#597088"


def wrap(value: object, limit: int) -> list[str]:
    """Wrap mixed Latin/CJK labels without relying on installed fonts."""
    remaining = " ".join(str(value).split())
    lines = []
    while remaining:
        units = 0
        end = 0
        for char in remaining:
            width = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
            if units + width > limit:
                break
            units += width
            end += 1
        if end == len(remaining):
            lines.append(remaining)
            break
        boundary = remaining.rfind(" ", 0, end + 1)
        if boundary > end // 2:
            end = boundary
        lines.append(remaining[:end].strip())
        remaining = remaining[end:].strip()
    return lines or ["—"]


def label(x: int, y: int, value: object, *, size: int = 32, fill: str = INK, weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif" font-size="{size}" font-weight="{weight}">{html.escape(str(value))}</text>'


def multiline(x: int, y: int, value: object, *, limit: int = 48, size: int = 30, line_height: int = 40, fill: str = INK, weight: int = 400) -> tuple[str, int]:
    lines = wrap(value, limit)
    rendered = "".join(label(x, y + index * line_height, line, size=size, fill=fill, weight=weight) for index, line in enumerate(lines))
    return rendered, len(lines) * line_height


def day_items(day: dict) -> list[dict]:
    return [item if isinstance(item, dict) else {"name": str(item)} for item in day.get("items", [])]


def hard_anchor(data: dict, day: dict) -> tuple[dict, dict] | None:
    anchors = {anchor.get("id"): anchor for anchor in data.get("anchors", []) if isinstance(anchor, dict)}
    bookings = {booking.get("id"): booking for booking in data.get("bookings", []) if isinstance(booking, dict)}
    for item in day_items(day):
        anchor = anchors.get(item.get("anchor_id"), {})
        if item.get("rigidity") == "hard" or anchor.get("rigidity") == "hard":
            booking = bookings.get(item.get("booking_id") or anchor.get("booking_id"), {})
            return item, booking
    return None


def render_card(data: dict, day: dict, index: int) -> str:
    items = day_items(day)
    accent = COLORS[index % len(COLORS)]
    outcome = day.get("outcome") or day.get("primary_outcome") or "Outcome to confirm"
    title = day.get("title") or day.get("base") or "Trip day"
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="__HEIGHT__" viewBox="0 0 1080 __HEIGHT__" role="img" aria-label="Day {index + 1} field card">',
           '<rect width="1080" height="__HEIGHT__" fill="#f7f4ed"/>',
           f'<rect width="1080" height="312" fill="{INK}"/>',
           f'<rect x="62" y="54" width="110" height="48" rx="24" fill="{accent}"/>',
           label(84, 88, f"DAY {index + 1:02d}", size=27, fill="#ffffff", weight=700),
           label(62, 157, day["date"], size=39, fill="#ffffff", weight=700),
           label(62, 214, title, size=40, fill="#ffffff", weight=700)]
    outcome_svg, outcome_height = multiline(62, 266, outcome, limit=48, size=27, line_height=35, fill="#dbe6ed")
    svg.append(outcome_svg)
    y = max(355, 266 + outcome_height + 38)

    anchor = hard_anchor(data, day)
    svg.append(f'<rect x="48" y="{y}" width="984" height="124" rx="18" fill="#ffffff"/>')
    svg.append(f'<rect x="48" y="{y}" width="10" height="124" rx="5" fill="{accent}"/>')
    svg.append(label(78, y + 41, "PROTECT THIS", size=23, fill=MUTED, weight=700))
    if anchor:
        item, booking = anchor
        anchor_text = f"{item.get('start', 'Time TBC')}  {item['name']}"
        svg.append(label(78, y + 84, anchor_text, size=31, weight=700))
        status = booking.get("status", "not confirmed")
        svg.append(label(78, y + 112, f"Reservation: {status}; verify entry evidence and arrival buffer", size=19, fill=MUTED))
    else:
        svg.append(label(78, y + 88, "No fixed booking recorded for this day", size=29, weight=700))
    y += 168

    svg.append(label(62, y, "FOLLOW IN ORDER", size=26, fill=MUTED, weight=700))
    y += 38
    for item_number, item in enumerate(items, start=1):
        name_lines = wrap(item.get("name", "Unnamed stop"), 43)
        row_height = max(124, 72 + len(name_lines) * 39)
        svg.append(f'<rect x="48" y="{y}" width="984" height="{row_height}" rx="16" fill="#ffffff"/>')
        svg.append(f'<circle cx="91" cy="{y + 47}" r="24" fill="{accent}"/>')
        svg.append(f'<text x="91" y="{y + 56}" text-anchor="middle" fill="#ffffff" font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif" font-size="26" font-weight="700">{item_number}</text>')
        for line_number, line in enumerate(name_lines):
            svg.append(label(140, y + 46 + line_number * 39, line, size=31, weight=700))
        detail_y = y + 49 + len(name_lines) * 39
        time = f"{item['start']}–{item['end']}" if item.get("start") and item.get("end") else "Time not specified"
        svg.append(label(140, detail_y, time, size=24, fill=MUTED))
        if "lat" in item and "lon" in item:
            url = f"https://www.google.com/maps/search/?api=1&amp;query={item['lat']},{item['lon']}"
            svg.append(label(826, detail_y, "OPEN MAP ↗", size=22, fill=accent, weight=700))
            svg.append(f'<a href="{url}" target="_blank"><rect x="810" y="{detail_y - 30}" width="210" height="42" fill="transparent"/></a>')
        y += row_height + 14

    y += 32
    svg.append(label(62, y, "IF PLANS CHANGE", size=26, fill=MUTED, weight=700))
    y += 26
    first_cut = day.get("first_cut") or "Choose a flexible stop to cut"
    fallback = day.get("weather_fallback") or "Check weather and transport before leaving"
    for heading, value in (("FIRST CUT", first_cut), ("RAIN / DISRUPTION", fallback)):
        lines = wrap(value, 49)
        box_height = 84 + len(lines) * 39
        svg.append(f'<rect x="48" y="{y}" width="984" height="{box_height}" rx="16" fill="#ffffff"/>')
        svg.append(label(78, y + 38, heading, size=22, fill=MUTED, weight=700))
        for line_number, line in enumerate(lines):
            svg.append(label(78, y + 78 + line_number * 39, line, size=28))
        y += box_height + 14

    y += 48
    svg.append(label(62, y, "BEFORE LEAVING", size=25, fill=MUTED, weight=700))
    svg.append(label(62, y + 42, "Weather · transit · booking evidence · first navigation", size=27))
    svg.append(label(62, y + 83, "Hotel address / ticket QR: add only confirmed details", size=24, fill=MUTED))
    svg.append(label(62, y + 136, "FICTIONAL DEMO · schematic links are not live travel advice", size=21, fill=MUTED))
    height = max(1600, y + 190)
    svg.append("</svg>")
    return "\n".join(svg).replace("__HEIGHT__", str(height)) + "\n"


def render_markdown(data: dict) -> str:
    lines = ["# Day-of field cards", "", "Fictional demo. Verify live transport, venue rules, and booking evidence before real travel.", ""]
    for index, day in enumerate(data["days"], start=1):
        lines += [f"## Day {index} · {day['date']} · {day.get('title') or day.get('base') or 'Trip day'}", "", f"Outcome: {day.get('outcome') or day.get('primary_outcome') or 'To confirm'}", ""]
        anchor = hard_anchor(data, day)
        if anchor:
            item, booking = anchor
            lines += [f"Protect: {item.get('start', 'time to confirm')} {item['name']} (reservation: {booking.get('status', 'not confirmed')}; arrival buffer to verify).", ""]
        for item in day_items(day):
            time = f"{item['start']}–{item['end']} " if item.get("start") and item.get("end") else ""
            navigation = f" [Map](https://www.google.com/maps/search/?api=1&query={item['lat']},{item['lon']})" if "lat" in item and "lon" in item else ""
            lines.append(f"- {time}{item['name']}{navigation}")
        lines += ["", f"First cut: {day.get('first_cut') or 'To confirm'}", f"Rain/disruption: {day.get('weather_fallback') or 'Check current conditions'}", "", "Morning check: weather, transit, booking evidence, first navigation. Add unknown hotel/ticket details only after confirmation.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trip_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.trip_json.read_text(encoding="utf-8"))
        days = data.get("days", [])
        if not days or any(not isinstance(day, dict) or not day.get("date") for day in days):
            raise ValueError("days must contain dated day objects")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for index, day in enumerate(days):
            (args.output_dir / f"day-{index + 1:02d}.svg").write_text(render_card(data, day, index), encoding="utf-8")
        (args.output_dir / "field-cards.md").write_text(render_markdown(data), encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {len(days)} SVG day cards and field-cards.md to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
