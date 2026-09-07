#!/usr/bin/env python3
"""Render a high-resolution schematic route map from a compact JSON file."""

from __future__ import annotations

import argparse
import json
import math
import sys
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_COLORS = ["#B33A3A", "#167C5A", "#D38300", "#1666A8", "#7251A5", "#008D8D"]
MODE_DASH = {
    "walk": "",
    "transit": "14 12",
    "rail": "6 10",
    "drive": "18 9",
    "flight": "3 14",
}


def load_route(path: str) -> dict[str, Any]:
    try:
        with Path(path).open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid route JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("route JSON must be an object")
    days = data.get("days")
    if not isinstance(days, list) or not 1 <= len(days) <= 6:
        raise ValueError("days must contain between one and six day objects")
    for day_index, day in enumerate(days):
        if not isinstance(day, dict) or not isinstance(day.get("stops"), list) or not day["stops"]:
            raise ValueError(f"days[{day_index}].stops must be a non-empty list")
        for stop_index, stop in enumerate(day["stops"]):
            if not isinstance(stop, dict):
                raise ValueError(f"days[{day_index}].stops[{stop_index}] must be an object")
            for coordinate in ("lat", "lon"):
                if not isinstance(stop.get(coordinate), (int, float)):
                    raise ValueError(
                        f"days[{day_index}].stops[{stop_index}].{coordinate} must be numeric"
                    )
            if not isinstance(stop.get("name"), str) or not stop["name"].strip():
                raise ValueError(f"days[{day_index}].stops[{stop_index}].name is required")
    return data


def svg_text(x: float, y: float, value: str, size: int, *, weight: int = 400, fill: str = "#17355F", anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, PingFang SC, '
        f'Microsoft YaHei, sans-serif" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def render(data: dict[str, Any], width: int, height: int) -> str:
    days: list[dict[str, Any]] = data["days"]
    stops = [stop for day in days for stop in day["stops"]]
    min_lat = min(stop["lat"] for stop in stops)
    max_lat = max(stop["lat"] for stop in stops)
    min_lon = min(stop["lon"] for stop in stops)
    max_lon = max(stop["lon"] for stop in stops)
    lat_span = max(max_lat - min_lat, 0.01)
    lon_span = max(max_lon - min_lon, 0.01)

    margin_x = width * 0.055
    title_height = height * 0.105
    map_top = title_height
    map_height = height * 0.53
    map_bottom = map_top + map_height
    card_top = map_bottom + height * 0.025
    card_bottom = height * 0.965
    card_gap = width * 0.014
    columns = 3 if len(days) > 2 else len(days)
    rows = math.ceil(len(days) / columns)
    card_width = (width - 2 * margin_x - (columns - 1) * card_gap) / columns
    card_height = (card_bottom - card_top - (rows - 1) * card_gap) / rows

    plot_left = margin_x + width * 0.025
    plot_right = width - margin_x - width * 0.025
    plot_top = map_top + height * 0.04
    plot_bottom = map_bottom - height * 0.045

    def project(stop: dict[str, Any]) -> tuple[float, float]:
        x = plot_left + (stop["lon"] - min_lon) / lon_span * (plot_right - plot_left)
        y = plot_bottom - (stop["lat"] - min_lat) / lat_span * (plot_bottom - plot_top)
        return x, y

    output = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#F8F5EC"/>',
        f'<rect x="{margin_x:.1f}" y="{map_top:.1f}" width="{width - 2 * margin_x:.1f}" height="{map_height:.1f}" rx="28" fill="#FCFBF7" stroke="#9AB0C5" stroke-width="3"/>',
    ]

    output.append(svg_text(width / 2, height * 0.052, str(data.get("title", "Trip route map")), 64, weight=700, anchor="middle"))
    subtitle = str(data.get("subtitle", "Schematic overview — verify live navigation on the day"))
    output.append(svg_text(width / 2, height * 0.079, subtitle, 27, weight=500, fill="#3F5877", anchor="middle"))

    for step in range(1, 10):
        x = margin_x + step * (width - 2 * margin_x) / 10
        output.append(f'<line x1="{x:.1f}" y1="{map_top:.1f}" x2="{x:.1f}" y2="{map_bottom:.1f}" stroke="#E6E4DE" stroke-width="2"/>')
    for step in range(1, 7):
        y = map_top + step * map_height / 7
        output.append(f'<line x1="{margin_x:.1f}" y1="{y:.1f}" x2="{width - margin_x:.1f}" y2="{y:.1f}" stroke="#E6E4DE" stroke-width="2"/>')

    label_boxes: list[tuple[float, float, float, float]] = []

    def place_label(x: float, y: float, label_width: float) -> tuple[float, float]:
        label_height = 62.0
        candidates = [
            (x + 38, y - 48),
            (x + 38, y + 18),
            (x - label_width - 38, y - 48),
            (x - label_width - 38, y + 18),
            (x - label_width / 2, y - 92),
            (x - label_width / 2, y + 30),
        ]
        best: tuple[float, float] | None = None
        best_score: float | None = None
        for rank, (candidate_x, candidate_y) in enumerate(candidates):
            candidate_x = max(plot_left, min(candidate_x, plot_right - label_width))
            candidate_y = max(plot_top, min(candidate_y, plot_bottom - label_height))
            overlap = 0.0
            for used_x, used_y, used_width, used_height in label_boxes:
                overlap_width = max(
                    0.0,
                    min(candidate_x + label_width, used_x + used_width) - max(candidate_x, used_x),
                )
                overlap_height = max(
                    0.0,
                    min(candidate_y + label_height, used_y + used_height) - max(candidate_y, used_y),
                )
                overlap += overlap_width * overlap_height
            score = overlap * 1000 + rank
            if best_score is None or score < best_score:
                best = (candidate_x, candidate_y)
                best_score = score
        assert best is not None
        label_boxes.append((best[0], best[1], label_width, label_height))
        return best

    for day_index, day in enumerate(days):
        color = str(day.get("color") or DEFAULT_COLORS[day_index])
        points = [project(stop) for stop in day["stops"]]
        for stop_index in range(1, len(points)):
            start_x, start_y = points[stop_index - 1]
            end_x, end_y = points[stop_index]
            mode = str(day["stops"][stop_index].get("mode_from_previous", "walk"))
            dash = MODE_DASH.get(mode, MODE_DASH["transit"])
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            output.append(
                f'<path d="M {start_x:.1f} {start_y:.1f} L {end_x:.1f} {end_y:.1f}" '
                f'fill="none" stroke="#FFFFFF" stroke-width="18" stroke-linecap="round"/>'
            )
            output.append(
                f'<path d="M {start_x:.1f} {start_y:.1f} L {end_x:.1f} {end_y:.1f}" '
                f'fill="none" stroke="{escape(color)}" stroke-width="10" stroke-linecap="round"{dash_attr}/>'
            )

        for stop_index, (stop, point) in enumerate(zip(day["stops"], points), start=1):
            x, y = point
            label = stop["name"]
            label_width = min(max(240, len(label) * 25 + 70), 620)
            label_x, label_y = place_label(x, y, label_width)
            output.append(f'<rect x="{label_x:.1f}" y="{label_y:.1f}" width="{label_width:.1f}" height="62" rx="22" fill="#FFFFFF" stroke="#D8DEE4" stroke-width="2"/>')
            output.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="29" fill="{escape(color)}" stroke="#FFFFFF" stroke-width="6"/>')
            output.append(svg_text(x, y + 10, str(stop_index), 26, weight=700, fill="#FFFFFF", anchor="middle"))
            output.append(svg_text(label_x + 22, label_y + 41, label, 25, weight=600, fill="#243D5E"))

    for day_index, day in enumerate(days):
        row = day_index // columns
        column = day_index % columns
        x = margin_x + column * (card_width + card_gap)
        y = card_top + row * (card_height + card_gap)
        color = str(day.get("color") or DEFAULT_COLORS[day_index])
        output.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{card_width:.1f}" height="{card_height:.1f}" rx="26" fill="#FFFFFF" stroke="{escape(color)}" stroke-width="3"/>')
        output.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{card_width:.1f}" height="68" rx="26" fill="{escape(color)}"/>')
        output.append(f'<rect x="{x:.1f}" y="{y + 40:.1f}" width="{card_width:.1f}" height="28" fill="{escape(color)}"/>')
        heading = f"Day {day.get('day', day_index + 1)}"
        if day.get("date"):
            heading += f" · {day['date']}"
        if day.get("label"):
            heading += f" · {day['label']}"
        output.append(svg_text(x + 24, y + 47, heading, 27, weight=700, fill="#FFFFFF"))
        line_y = y + 112
        max_lines = max(1, int((card_height - 135) / 48))
        for stop_index, stop in enumerate(day["stops"], start=1):
            if stop_index > max_lines:
                break
            duration = f" · {stop['duration']}" if stop.get("duration") else ""
            output.append(f'<circle cx="{x + 32:.1f}" cy="{line_y - 7:.1f}" r="17" fill="{escape(color)}"/>')
            output.append(svg_text(x + 32, line_y, str(stop_index), 17, weight=700, fill="#FFFFFF", anchor="middle"))
            output.append(svg_text(x + 61, line_y, f"{stop['name']}{duration}", 23, weight=500, fill="#253E5D"))
            line_y += 48

    disclaimer = str(data.get("disclaimer", "Schematic map: use live navigation for turn-by-turn directions."))
    output.append(svg_text(width / 2, height * 0.988, disclaimer, 20, fill="#65778C", anchor="middle"))
    output.append("</svg>")
    return "\n".join(output) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="route JSON path")
    parser.add_argument("output", help="output SVG path")
    parser.add_argument("--width", type=int, default=2480)
    parser.add_argument("--height", type=int, default=3508)
    args = parser.parse_args()
    if args.width < 800 or args.height < 1000:
        parser.error("width must be at least 800 and height at least 1000")
    try:
        data = load_route(args.input)
        svg = render(data, args.width, args.height)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(svg, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {args.output} ({args.width}x{args.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
