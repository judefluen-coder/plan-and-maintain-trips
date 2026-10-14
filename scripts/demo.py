#!/usr/bin/env python3
"""Regenerate the fictional example's derived artifacts without network access."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "trip.example.json"


def run(script: str, *args: str) -> str:
    command = [sys.executable, str(ROOT / "scripts" / script), *args]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{script} failed:\n{result.stderr or result.stdout}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new or empty directory for generated files")
    args = parser.parse_args()
    output = args.output.expanduser().resolve() if args.output else Path(tempfile.mkdtemp(prefix="trip-skill-demo-"))
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error(f"output must be a new or empty directory: {output}")
    try:
        output.mkdir(parents=True, exist_ok=True)
        trip = output / "trip.json"
        shutil.copy2(SOURCE, trip)
        print(run("validate_trip.py", str(trip), "--strict").strip())
        run("render_route_map.py", str(trip), str(output / "route.svg"), "--from-trip")
        run("export_field_pack.py", str(trip), str(output))
        run("render_field_cards.py", str(trip), str(output))
        replanned = run("replan_day.py", str(trip), "--date", "2030-05-02", "--delay-minutes", "45", "--rain")
        food = run("suggest_food.py", str(trip), "--date", "2030-05-01", "--meal", "lunch")
        for name, content in (("replan-proposal.json", replanned), ("food-candidates.json", food)):
            json.loads(content)  # Fail if a helper stops returning machine-readable output.
            (output / name).write_text(content, encoding="utf-8")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("\nFictional offline demo; names and booking links are placeholders, not travel advice.")
    print(f"Open the route page: {output / 'route-offline.html'}")
    print(f"Route map: {output / 'route.svg'}")
    print(f"Day cards, calendar, map points, and change advice are in: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
