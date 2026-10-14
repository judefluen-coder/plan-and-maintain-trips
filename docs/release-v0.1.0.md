## Plan & Maintain Trips v0.1.0

First public preview of the Codex travel-planning skill (2026-10-14).

- Plan and maintain trips with a canonical `trip.json`, dated evidence, controlled booking statuses, protected anchors, and change checks.
- Create a lossless route atlas, offline phone route page, KML points, and ICS calendar from structured itinerary data.
- Propose same-day changes for delay, rain, or closure without silently moving fixed bookings; shortlist researched restaurants near the route.
- Use the bilingual README, the [redacted France historical case](https://github.com/judefluen-coder/plan-and-maintain-trips/tree/main/examples/france-2026), and the [fictional Lisbon → Cascais live example](https://judefluen-coder.github.io/plan-and-maintain-trips/) to inspect the outputs before installing.
- Run `python3 scripts/demo.py` after a public HTTPS clone to regenerate the fictional derived files offline; no GitHub CLI sign-in or third-party Python packages are required.
- Run the Python 3.11/3.13 CI checks and inspect the [full changelog](https://github.com/judefluen-coder/plan-and-maintain-trips/blob/main/CHANGELOG.md).

The Lisbon dataset contains fictional venues and does not show live ticket inventory. The France guide is a redacted historical editorial case, not a runnable dataset. Feishu and other document platforms are optional publishing integrations available through the user's connected tools. Source and documentation are available under the MIT license.
