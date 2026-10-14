# v0.2.0 — Day cards and contributor entry points

The fictional offline demo now generates mobile SVG day cards and a searchable Markdown counterpart from the same `trip.json` as the route atlas, phone page, KML, and calendar. The sample distinguishes a bookable target from a purchased ticket and keeps each day's first-cut advice tied to a scheduled item.

- `python3 scripts/demo.py` regenerates the full fictional field pack without network access or a Feishu account.
- CI checks the day-card output for drift; tests cover booking labels, unknown times, and first-cut consistency.
- `CONTRIBUTING.md`, privacy-aware issue forms, and a pull-request checklist make it easier to report and fix problems.
- A five-minute independent-user test and bilingual launch copy are prepared. Neither external testing nor posting is claimed.
- A 1280×640 social-preview image is included in `assets/`; it was uploaded through GitHub repository settings after the release was first published on 2026-10-14.

This release does not provide live venue hours, ticket inventory, or authenticated publishing credentials. The France guide remains a redacted historical case; the runnable Lisbon → Cascais dataset is fictional.
