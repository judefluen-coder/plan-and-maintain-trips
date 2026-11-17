#!/usr/bin/env python3
"""Render mobile SVG day cards and searchable Markdown from a structured trip."""

from __future__ import annotations

import argparse
import html
import json
import sys
import unicodedata
from pathlib import Path


COLORS = ("#a63f3d", "#14735d", "#965900", "#245f91", "#694888", "#116d73")
INK = "#183149"
MUTED = "#536776"
PAPER = "#faf8f3"
RULE = "#d8dedc"


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
    return lines or ["TBC"]


def label(x: int, y: int, value: object, *, size: int = 32, fill: str = INK, weight: int = 400, family: str = "Arial, PingFang SC, Microsoft YaHei, sans-serif") -> str:
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" font-weight="{weight}">{html.escape(str(value))}</text>'


def multiline(x: int, y: int, value: object, *, limit: int = 48, size: int = 30, line_height: int = 40, fill: str = INK, weight: int = 400, family: str = "Arial, PingFang SC, Microsoft YaHei, sans-serif") -> tuple[str, int]:
    lines = wrap(value, limit)
    rendered = "".join(label(x, y + index * line_height, line, size=size, fill=fill, weight=weight, family=family) for index, line in enumerate(lines))
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
           f'<rect width="1080" height="__HEIGHT__" fill="{PAPER}"/>',
           f'<rect width="1080" height="12" fill="{accent}"/>',
           label(62, 74, "TRAVEL FIELD GUIDE", size=22, fill=MUTED, weight=700),
           label(62, 203, f"{index + 1:02d}", size=120, fill=accent, weight=400, family="Georgia, Songti SC, serif"),
           f'<text x="1032" y="74" text-anchor="end" fill="{MUTED}" font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif" font-size="29" font-weight="700">{html.escape(str(day["date"]))}</text>']
    title_svg, title_height = multiline(256, 157, title, limit=29, size=52, line_height=62, weight=700, family="Georgia, Songti SC, serif")
    svg.append(title_svg)
    outcome_y = 157 + title_height + 8
    outcome_svg, outcome_height = multiline(256, outcome_y, outcome, limit=50, size=27, line_height=35, fill=MUTED)
    svg.append(outcome_svg)
    header_bottom = max(275, outcome_y + outcome_height + 22)
    svg.append(f'<line x1="48" y1="{header_bottom}" x2="1032" y2="{header_bottom}" stroke="{RULE}" stroke-width="2"/>')
    y = header_bottom + 28

    anchor = hard_anchor(data, day)
    anchor_text = f"{anchor[0].get('start', 'Time TBC')}  {anchor[0]['name']}" if anchor else "No fixed booking recorded for this day"
    anchor_lines = wrap(anchor_text, 43)
    anchor_height = 162 + (len(anchor_lines) - 1) * 43
    svg.append(f'<rect x="48" y="{y}" width="984" height="{anchor_height}" rx="16" fill="#ffffff" stroke="{RULE}" stroke-width="2"/>')
    svg.append(f'<rect x="48" y="{y}" width="9" height="{anchor_height}" rx="4" fill="{accent}"/>')
    svg.append(label(78, y + 40, "DO NOT MISS" if anchor else "NO FIXED ANCHOR", size=22, fill=accent, weight=700))
    for line_number, line in enumerate(anchor_lines):
        svg.append(label(78, y + 86 + line_number * 43, line, size=33, weight=700))
    if anchor:
        status = anchor[1].get("status", "not confirmed")
        svg.append(label(78, y + anchor_height - 27, f"Reservation: {status}; verify entry evidence and arrival buffer", size=21, fill=MUTED))
    y += anchor_height + 57

    svg.append(label(62, y, "FOLLOW IN ORDER", size=24, fill=MUTED, weight=700))
    y += 22
    svg.append(f'<line x1="48" y1="{y}" x2="1032" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
    y += 12
    for item_number, item in enumerate(items, start=1):
        name_lines = wrap(item.get("name", "Unnamed stop"), 35)
        row_height = 104 + len(name_lines) * 43
        svg.append(f'<circle cx="264" cy="{y + 51}" r="21" fill="{accent}"/>')
        svg.append(f'<text x="264" y="{y + 59}" text-anchor="middle" fill="#ffffff" font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif" font-size="23" font-weight="700">{item_number}</text>')
        svg.append(label(62, y + 52, item.get("start") or "TBC", size=31, weight=700))
        if item.get("end"):
            svg.append(label(62, y + 85, f"to {item['end']}", size=21, fill=MUTED))
        for line_number, line in enumerate(name_lines):
            svg.append(label(308, y + 51 + line_number * 43, line, size=33, weight=700))
        detail_y = y + 58 + len(name_lines) * 43
        if not item.get("start") or not item.get("end"):
            svg.append(label(308, detail_y, "Time not specified", size=22, fill=MUTED))
        if "lat" in item and "lon" in item:
            url = f"https://www.google.com/maps/search/?api=1&amp;query={item['lat']},{item['lon']}"
            svg.append(label(308, detail_y + 29, "OPEN MAP ↗", size=21, fill=accent, weight=700))
            svg.append(f'<a href="{url}" target="_blank"><rect x="294" y="{detail_y}" width="210" height="44" fill="transparent"/></a>')
        svg.append(f'<line x1="48" y1="{y + row_height}" x2="1032" y2="{y + row_height}" stroke="{RULE}" stroke-width="2"/>')
        y += row_height

    y += 53
    svg.append(label(62, y, "IF PLANS CHANGE", size=24, fill=MUTED, weight=700))
    y += 20
    first_cut = day.get("first_cut") or "Choose a flexible stop to cut"
    fallback = day.get("weather_fallback") or "Check weather and transport before leaving"
    for heading, value in (("FIRST CUT", first_cut), ("RAIN / DISRUPTION", fallback)):
        lines = wrap(value, 48)
        box_height = 86 + len(lines) * 39
        svg.append(f'<rect x="48" y="{y}" width="984" height="{box_height}" rx="16" fill="#f1f0ea"/>')
        svg.append(label(78, y + 38, heading, size=21, fill=accent, weight=700))
        for line_number, line in enumerate(lines):
            svg.append(label(78, y + 81 + line_number * 39, line, size=28, weight=600))
        y += box_height + 12

    y += 36
    svg.append(f'<line x1="48" y1="{y}" x2="1032" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
    svg.append(label(62, y + 48, "BEFORE LEAVING", size=23, fill=MUTED, weight=700))
    svg.append(label(62, y + 92, "Weather · transit · booking evidence · first navigation", size=25))
    svg.append(label(62, y + 133, "Hotel address / ticket QR: add only confirmed details", size=23, fill=MUTED))
    svg.append(label(62, y + 190, "FICTIONAL DEMO · schematic links are not live travel advice", size=20, fill=MUTED))
    height = y + 235
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
