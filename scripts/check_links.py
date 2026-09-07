#!/usr/bin/env python3
"""Extract and optionally verify HTTP links in a Markdown travel guide."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


LINK_PATTERN = re.compile(r"https?://[^\s<>\])}\"']+")
PROTECTED_CODES = {401, 403, 429}


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def extract_links(text: str) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for match in LINK_PATTERN.findall(text):
        link = match.rstrip(".,;:!?")
        if link not in seen:
            seen.add(link)
            links.append(link)
    return links


def request(url: str, method: str, timeout: float) -> tuple[int | None, str | None]:
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "plan-and-maintain-trips-link-checker/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, str(exc)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, str(exc)


def check_link(url: str, timeout: float) -> dict[str, Any]:
    status, error = request(url, "HEAD", timeout)
    if status in {405, 501} or status is None:
        get_status, get_error = request(url, "GET", timeout)
        if get_status is not None or status is None:
            status, error = get_status, get_error
    if status is not None and 200 <= status < 400:
        state = "ok"
    elif status in PROTECTED_CODES:
        state = "protected"
    elif status is not None:
        state = "broken"
    else:
        state = "error"
    return {"url": url, "state": state, "status": status, "error": error}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Markdown path, or - for stdin")
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--extract-only", action="store_true")
    args = parser.parse_args()

    try:
        links = extract_links(read_text(args.path))
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.extract_only:
        if args.json_output:
            print(json.dumps(links, ensure_ascii=False, indent=2))
        else:
            for link in links:
                print(link)
        return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(lambda url: check_link(url, args.timeout), links))

    failed = any(result["state"] in {"broken", "error"} for result in results)
    if args.json_output:
        print(json.dumps({"ok": not failed, "results": results}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = result["status"] if result["status"] is not None else "network"
            print(f"{result['state'].upper():9} {status!s:>7} {result['url']}")
        print(f"{'PASS' if not failed else 'FAIL'}: checked {len(results)} unique links")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
