<p align="center">
  <a href="assets/readme-hero.en.svg">
    <img src="assets/readme-hero.en.png" alt="Plan & Maintain Trips — from scattered ideas to an executable trip" width="100%">
  </a>
</p>

<h1 align="center">Plan & Maintain Trips</h1>

<p align="center">远行策划</p>

<p align="center">
  <a href="./README.md">简体中文</a> · <strong>English</strong>
</p>

<p align="center">
  <strong>Turn a trip from scattered ideas into one project you can book, execute, revise, and audit.</strong>
</p>

<p align="center">
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-163A63?style=flat-square">
  <img alt="Any destination" src="https://img.shields.io/badge/Destination-Anywhere-16856B?style=flat-square">
  <img alt="Visual field cards" src="https://img.shields.io/badge/Output-Visual%20field%20cards-D88700?style=flat-square">
  <img alt="Multi-document publishing" src="https://img.shields.io/badge/Publish-Multi--document-7354A5?style=flat-square">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-4C657A?style=flat-square"></a>
</p>

> This is not another attraction list. Every schedule, reservation, restaurant, route map, and day-of field card is derived from one canonical trip state. Change one decision, and every affected deliverable stays in sync.

## See what it ships

### 1. One map for the whole trip

Each day gets its own color and numbered stops. Walking, transit, pace, fixed reservations, and the first item to cut are visible without digging through a long document.

<p align="center">
  <a href="assets/readme-route-sample.en.svg">
    <img src="assets/readme-route-sample.en.png" alt="Six-day route atlas with numbered stops, day cards, distances, and booking anchors" width="100%">
  </a>
</p>

<p align="center"><sub>Click the image for the lossless SVG. The README uses a 2400×1600 PNG for reliable GitHub rendering.</sub></p>

### 2. A field card for every day

The full guide is for planning. On the road, you need one card that answers what happens next. Each card keeps only the essentials: protected reservations, arrival time, sequence, tickets, route, lunch, pace, and what to drop when you are late or the weather changes.

<p align="center">
  <a href="assets/readme-day-card.en.svg">
    <img src="assets/readme-day-card.en.png" alt="Day-of travel field card with timeline, ticket wallet, route, pace, and fallback decisions" width="100%">
  </a>
</p>

The image above is a layout concept. [Open the Day 02 PNG actually generated from the example `trip.json`](examples/lisbon-coast/day-02.png), its [lossless SVG](examples/lisbon-coast/day-02.svg), and its [searchable text equivalent](examples/lisbon-coast/field-cards.md) to see what the data really supports. The generated card uses a phone-friendly travel-journal layout.

Each field card can:

- ship as a separate high-resolution PNG that is easy to save to a phone;
- retain a lossless SVG source for editing, printing, or embedding in a guide;
- keep a searchable text version for addresses and accessibility;
- expose missing hotel, flight, or ticket details instead of inventing them.

### 3. One plan, multiple publishing targets

Feishu is an optional publisher, not a prerequisite. The Skill completes a platform-independent local delivery package first, then publishes through whichever connected tools the user actually has.

<p align="center">
  <a href="assets/readme-publishing.en.svg">
    <img src="assets/readme-publishing.en.png" alt="One canonical trip project publishing to Feishu Lark, Markdown, Notion, Google Docs, DOCX, and PDF" width="100%">
  </a>
</p>

Supported outputs:

- **Always available:** Markdown, `trip.json`, route maps in SVG/PNG, and daily field cards;
- **Feishu / Lark:** publish to Docx or Wiki, insert images, and read back for verification when the capability is installed and authorized;
- **Notion / Google Docs:** publish when the corresponding connector is available and authorized;
- **DOCX / PDF:** create an editable or print-ready archive when document tools are available;
- **No platform connected:** still deliver the complete core guide without blocking on a CLI, account, or connector.

## Explore the live trip workbench

[Open the workbench online](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/) without installing anything. It opens a redacted [five-day Paris historical case](examples/france-2026/README.md): select a day on the overview map, then explore its landmark map, timeline, and linked field-guide board. The board makes ticket checks, transport, food, protected appointments, and weather tradeoffs visible. Day 2 includes a **browser-only simulated** revision proposal.

<p align="center">
  <a href="assets/workbench-overview.jpg"><img src="assets/workbench-overview.jpg" alt="Actual workbench screenshot: five-day Paris overview map and day selection" width="100%"></a>
</p>

<p align="center">
  <a href="assets/workbench-day-map.jpg"><img src="assets/workbench-day-map.jpg" alt="Actual workbench screenshot: Day 4 landmark map linked to its timeline" width="49%"></a>
  <a href="assets/workbench-day-board.jpg"><img src="assets/workbench-day-board.jpg" alt="Actual workbench screenshot: Day 4 route, tickets, transport, food, and contingency board" width="49%"></a>
</p>

<p align="center"><sub>These are screenshots of the working interface, which is currently in Chinese. The Paris itinerary is an archived 2026 case: markers are not entrance-level navigation, and ticket labels are not current availability.</sub></p>

### From the demo to your own trip

1. **Explore first:** open the [Paris workbench](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/), choose a Day tab or map badge, and inspect the field-guide board. The earlier [fictional Lisbon demo](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/?demo=lisbon) remains available.
2. **Create your trip:** install the Skill and tell Codex your dates, destinations, preferences, and existing bookings. Have it create your own `trip.json` **outside the Skill directory**. The static website does not yet generate a whole trip from scratch with hosted AI.
3. **Connect the visual workbench:** make sure the Codex CLI is installed and signed in, then run the command below locally. The bridge prints and opens an online workbench link with a temporary pairing secret; click “未连接 Codex” (“Not connected to Codex”) on the page to connect. Do not share the pairing link. If your browser asks to connect to a local service, approve only the page you trust.

   ```bash
   python3 bridge/server.py --trip /absolute/path/to/your/trip.json
   ```

4. **Review before applying:** select one day and describe a change in natural language. Inspect the map, timeline, warnings, and diff; only your confirmation writes back to `trip.json`, with a `.bak` backup. The current bridge revises one day at a time. Model requests use your locally signed-in Codex CLI and your own quota; GitHub Pages supplies neither model compute nor trip storage. See the [workbench setup and safety guide](web/README.md).

For a complete human-readable guide, see the [Paris + French Riviera case](examples/france-2026/README.md), with maps, ticket checklist, transport, food, and hotel-selection logic. For reproducible offline exports, use the fictional [Lisbon → Cascais dataset](examples/lisbon-coast/README.md) and its [live offline-route preview](https://judefluen-coder.github.io/plan-and-maintain-trips/). These examples serve different purposes.

See the [changelog](CHANGELOG.md) for version history.

Found a bug or have a concrete workflow improvement? Read [Contributing](CONTRIBUTING.md) and use the repository's issue forms with redacted reproduction details.

For a first trial, follow the [five-minute new-user test](docs/try-it.md). A [maintainer launch kit](docs/launch-kit.md) is prepared but has not been posted on anyone's behalf.

## Capabilities and deliverables

The visuals above show the finished artifacts. This table shows what the Skill does throughout the planning process.

| Stage | What it does | What you receive |
|---|---|---|
| Intake | Consolidates dates, lodging, transport, budget, preferences, exclusions, and immovable plans | Trip overview + canonical `trip.json` state |
| Official research | Verifies hours, closure days, reservation rules, release windows, and official entry points | Booking checklist with status, evidence, next action, and fallback |
| Route scheduling | Balances geography, visit duration, security queues, transfers, recovery, and physical load | Executable day-by-day schedule with concrete times |
| Restaurant fit | Selects food around the actual route, booking gaps, opening hours, and queue risk | Primary and backup restaurants with route-specific reasoning |
| Maps and field execution | Encodes days with colors and numbered stops, then extracts the decisions that matter on site | High-resolution route atlas + daily field cards |
| Offline and reminders | Exports a phone route page, map points, and calendar events from geocoded timed items | Single-file offline HTML + KML + ICS |
| Live replan and food | Proposes changes for delays, closures, or rain; ranks researched restaurants along the route | Non-destructive proposal + nearby food shortlist |
| Controlled revisions | Traces each date, hotel, or attraction change into bookings, routes, restaurants, and maps | Change log + synchronized deliverables |
| Final delivery | Audits dates, nights, hard anchors, links, budget, and cross-format consistency before publishing | Markdown / Feishu / Notion / Google Docs / DOCX / PDF |

## Why choose Plan & Maintain Trips

The hard part of trip planning is not listing places. It is keeping the guide usable after reservations, route changes, and disruptions. This Skill focuses on that work:

🧭 **One source of truth** — dates, lodging, transport, reservations, and exclusions live in one canonical state.

🎫 **Precise booking states** — clearly distinguishes not released, date not in the system, sold out, walk-in, and booked.

📍 **Routing beyond distance** — accounts for opening times, security, queues, slopes, luggage, meals, recovery, and the next fixed reservation.

🔁 **Impact analysis for every revision** — checks affected dates, tickets, hotels, transport, restaurants, maps, budgets, and field cards.

🌧️ **Day-of decisions built in** — states what must be protected, what to cut first, and what to do during rain or closures.

📦 **Portable delivery** — produces local files you can keep and use offline first, then publishes to Feishu or other document platforms when authorized tools are available.

## How it works

```mermaid
flowchart LR
    A[Requirements and bookings] --> B[Dates, cities, and hard anchors]
    B --> C[Official sources and booking states]
    C --> D[Executable itinerary]
    D --> E[Route atlas]
    D --> F[Daily field cards]
    D --> G[Full guide]
    E --> H[Consistency audit]
    F --> H
    G --> H
    H --> I[Feishu / Markdown / Notion / Docs / DOCX / PDF]
```

## Start in 30 seconds

The public repository needs no GitHub sign-in. Install with Git and Python 3.11+, then run the fully offline demo:

```bash
git clone https://github.com/judefluen-coder/plan-and-maintain-trips.git "$HOME/.codex/skills/plan-and-maintain-trips"
cd "$HOME/.codex/skills/plan-and-maintain-trips"
python3 scripts/demo.py
```

The command validates [one fictional trip state](assets/trip.example.json), generates a route SVG, daily field-card SVGs and searchable text, an offline route page, KML, ICS, a delay-and-rain replan proposal, and a nearby food shortlist in a temporary directory, then prints the file paths. It does not use the network, buy or reserve anything, or generate live research, a full written guide, or a Feishu document. Those require running the Skill in Codex and checking destination-specific sources.

Start a new Codex task or reload skills, then try:

```text
Use $plan-and-maintain-trips to plan a trip to Japan from October 1 to October 10.
We arrive in Tokyo, depart from Osaka, travel as two people, and prefer a moderate pace.
Give us a booking checklist, detailed routes, route-linked restaurants, daily field cards,
and a final guide.
```

It also maintains an existing plan through changes:

```text
Use $plan-and-maintain-trips to update the current itinerary. Keep the Kyoto hotel unchanged,
and do not move the booked Shinkansen. Move Nara one day later, then synchronize the restaurants,
booking checklist, route atlas, and daily field cards.
```

<details>
<summary><strong>Booking status dictionary</strong></summary>

- `bookable`: the target date is available to book now.
- `not_released`: the official operator has confirmed that sales have not opened yet.
- `date_not_in_system`: the target date is not visible and there is not enough evidence to infer the release rule.
- `sold_out`: the official source explicitly shows the target date or performance as sold out.
- `walk_in`: normal entry without advance booking.
- `same_day`: booking is only available or most appropriate on the day.
- `booked`: the user has a confirmation number, ticket, or QR code.
- `needs_recheck`: the conclusion is temporary and has a defined recheck time.

`unknown` may exist briefly during research, but must be resolved before final delivery.

</details>

<details>
<summary><strong>Built-in validation and mapping tools</strong></summary>

The scripts use only the Python standard library:

```bash
# Check dates, hotel nights, hard anchors, booking evidence, and unresolved placeholders
python3 scripts/validate_trip.py trip.json --strict

# Render a lossless 2480×3508 SVG route map from the same trip.json
python3 scripts/render_route_map.py trip.json route-map.svg --from-trip

# Check booking and reservation links in a guide
python3 scripts/check_links.py guide.md

# Derive an offline route page, map points, and calendar from trip.json
python3 scripts/export_field_pack.py trip.json output/

# Derive one SVG field card per day plus searchable Markdown
python3 scripts/render_field_cards.py trip.json output/

# Propose a same-day change without modifying the canonical state
python3 scripts/replan_day.py trip.json --date 2030-05-02 --delay-minutes 45 --rain

# Rank researched lunch candidates near the day's route
python3 scripts/suggest_food.py trip.json --date 2030-05-01 --meal lunch

# Optionally load a reusable city food catalog
python3 scripts/suggest_food.py trip.json --date 2030-05-01 --meal lunch --catalog city-restaurants.json
```

Example of a successful state validation:

```text
PASS: 5 days, 2 segments, 2 anchors, 2 bookings; 0 errors, 0 warnings
```

</details>

<details>
<summary><strong>Repository structure</strong></summary>

```text
plan-and-maintain-trips/
├── README.md / README.en.md
├── LICENSE
├── CHANGELOG.md
├── SKILL.md
├── .github/workflows/        # CI and example preview deployment
├── agents/openai.yaml
├── examples/lisbon-coast/    # browser-openable complete output example
├── examples/france-2026/     # redacted historical case; not a runnable dataset
├── assets/
│   ├── trip.example.json
│   ├── route.example.json
│   ├── restaurants.example.json
│   ├── guide-template.md
│   ├── readme-*.{png,svg}       # Chinese visuals
│   ├── readme-*.en.{png,svg}    # English visuals
│   └── workbench-*.jpg         # screenshots of the live workbench
├── web/                         # GitHub Pages interactive workbench
├── bridge/                      # optional local Codex bridge
├── references/
│   ├── state-model.md
│   ├── research-and-evidence.md
│   ├── scheduling-and-change-control.md
│   ├── deliverables-and-publishing.md
│   └── quality-gates.md
├── scripts/
    ├── validate_trip.py
    ├── render_route_map.py
    ├── render_field_cards.py
    ├── export_field_pack.py
    ├── replan_day.py
    ├── suggest_food.py
    ├── demo.py
    └── check_links.py
└── tests/                    # behavioral tests
```

</details>

## Guardrails

- Never purchase, book, send messages, install software, or publish documents without authorization.
- Never label an unavailable future date as sold out without evidence, or silently move a user-defined hard anchor.
- Never compare an aggregator teaser price with a tax-inclusive price under different room or cancellation terms.
- Treat route maps as planning tools; check live navigation, weather, and operator notices on the day.
- The offline HTML shows trip details and schematic lines; navigation links need connectivity. KML lines express visit order, and restaurant distance is straight-line distance.
- Never store passports, payment details, account credentials, tokens, or authorization codes in the project or Skill.

---

<p align="center">
  <strong>Plan beautifully. Book deliberately. Travel calmly.</strong><br>
  <sub>漂亮地规划，克制地预约，从容地出发。</sub>
</p>
