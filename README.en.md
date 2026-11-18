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
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent-Skill-163A63?style=flat-square">
  <img alt="Any destination" src="https://img.shields.io/badge/Destination-Anywhere-16856B?style=flat-square">
  <img alt="Visual field cards" src="https://img.shields.io/badge/Output-Visual%20field%20cards-D88700?style=flat-square">
  <img alt="Multi-document publishing" src="https://img.shields.io/badge/Publish-Multi--document-7354A5?style=flat-square">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-4C657A?style=flat-square"></a>
</p>

> This is not another attraction list. Every schedule, reservation, restaurant, route map, and day-of field card is derived from one canonical trip state. Change one decision, and every affected deliverable stays in sync.

## See the real workbench first

> **Cross-agent status:** this skill follows the [Agent Skills format](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx). Agents that can install a Skill and read/write local files can create a `trip.json` for the same visual workbench. The local bridge supports Codex CLI and now has a Claude Code CLI adapter; protocol and safety tests pass, but a live Claude proposal could not complete because the current account returned insufficient balance. A model provider such as DeepSeek is not itself a skill-capable agent.

### Choose your path

| Your tool | Install | Workbench path |
| --- | --- | --- |
| Codex CLI / App | Use `npx skills` below or the existing manual method | Import/export JSON; Codex CLI can optionally use the automatic local bridge |
| Claude Code | Select Claude Code in `npx skills` | JSON handoff; optional CLI bridge requires working model authorization or balance |
| OpenCode | Select OpenCode in `npx skills` | Verified: create and revise a local `trip.json`, import it online, and auto-refresh after a save |
| Kimi Code CLI, Gemini CLI, Cursor, Qwen Code, GitHub Copilot CLI | Select the agent in `npx skills`; invoke the skill using that agent's syntax | Shared-file or JSON handoff is the intended path; these agents have not each been run end-to-end |
| WorkBuddy / CodeBuddy | Use the product's local Skill import for your specific version | Shared-file workbench if it can edit the same local file; otherwise JSON handoff. Direct model invocation is unverified |
| DeepSeek, Kimi or another model API/web chat | Choose a skill-capable agent that uses the model; the model itself cannot install a local Skill | File/script access is needed for the full workflow |

Verification scope: on 2026-11-18, OpenCode v2.3.2 loaded the Skill and created and revised an entirely fictional two-day trip in an isolated directory. The file passed strict validation, imported into the live workbench, and refreshed there after the agent saved another edit. No real traveler data was used; this does not guarantee future availability of the tested free model or other agents. Claude Code Skill installation was verified, but live model generation stopped at insufficient account balance. WorkBuddy/CodeBuddy ZIP import and the other agents' full runs remain unverified.

The [Vercel `skills` CLI](https://github.com/vercel-labs/skills/blob/main/README.md) requires Node.js 22.20+. In your own trip project, run:

```bash
npx skills add judefluen-coder/plan-and-maintain-trips --skill plan-and-maintain-trips
```

The repository root is the Skill, so `npx skills` may copy the whole repository. For products that import a local ZIP (such as WorkBuddy/CodeBuddy), download the [v0.3.0 slim Skill ZIP](https://github.com/judefluen-coder/plan-and-maintain-trips/releases/download/v0.3.0/plan-and-maintain-trips-skill.zip), or clone the repo and run `python3 scripts/package_skill.py /outside-the-repo/plan-and-maintain-trips.zip` to package it yourself. Ask your agent to use `plan-and-maintain-trips` and create a `trip.json` outside the Skill folder. Invocation syntax varies: Codex uses `$plan-and-maintain-trips`; Kimi Code CLI uses `/skill:plan-and-maintain-trips`.

**On the same computer, use the shared-file workbench:** run `python3 bridge/server.py --provider manual --trip /absolute/path/to/trip.json` from the installed Skill or repository root. Open the private link it prints. Select a day, write a change request, copy it to your skill-enabled agent, and have the agent edit that same `trip.json`. The workbench refreshes its map and schedule after a valid save. This mode does not call a model from the browser or require a programmable agent CLI.

**Across devices, use JSON handoff:** import the trip into the [workbench](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/). Use the “① 下载交接 JSON” (download handoff JSON) and “② 复制要求给 AI 代理” (copy request for AI agent) buttons, then re-import the agent's updated file. This path does not auto-sync or back up the old file.

Your chosen agent supplies its own model, authorization, and usage allowance. GitHub Pages supplies neither compute nor trip storage. Keep a copy and review hard bookings; shared-file sync does not approve the agent's edits for you. Only Codex CLI and Claude Code CLI have browser-triggered model adapters; other agents do not yet have verified one-click model invocation.

[Open the live workbench](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/) without installing anything. It starts with a redacted [five-day Paris historical case](examples/france-2026/README.md): choose a day on the overview map, then inspect its landmark map and timeline. Tickets, transport, food, and on-the-ground tradeoffs follow the selected day in the field-guide board. Day 2 includes a **browser-only simulated** revision proposal.

<p align="center">
  <a href="assets/workbench-overview-v2.jpg"><img src="assets/workbench-overview-v2.jpg" alt="Actual Plan &amp; Maintain Trips workbench: five-day Paris overview map and day selection" width="100%"></a>
</p>

<details>
<summary>Expand Day 4: landmark map, timeline, and complete field-guide board</summary>

<p align="center"><a href="assets/workbench-day-map-v2.jpg"><img src="assets/workbench-day-map-v2.jpg" alt="Actual Day 4 landmark map linked to its timeline" width="100%"></a></p>
<p align="center"><a href="assets/workbench-day-board-v2.jpg"><img src="assets/workbench-day-board-v2.jpg" alt="Actual Day 4 route, tickets, transport, food, and contingency board" width="100%"></a></p>
</details>

<p align="center"><sub>These are screenshots of the working interface, currently in Chinese—not concept art. The Paris trip is an archived 2026 case; map markers are not entrance-level navigation, and ticket labels are not current availability.</sub></p>

## What else it ships

### 1. One map for the whole trip

Each day gets its own color and numbered stops. Walking, transit, pace, fixed reservations, and the first item to cut are visible without digging through a long document.

See the [high-resolution Paris route map](examples/france-2026/paris-route-4k.png) or the [editable SVG layout concept](assets/readme-route-sample.en.svg). The former is a historical guide artifact; the latter is a visual concept, not the same dataset.

### 2. A field card for every day

The full guide is for planning. On the road, you need one card that answers what happens next. Each card keeps only the essentials: protected reservations, arrival time, sequence, tickets, route, lunch, pace, and what to drop when you are late or the weather changes.

[Open the Day 02 PNG actually generated from the example `trip.json`](examples/lisbon-coast/day-02.png), its [lossless SVG](examples/lisbon-coast/day-02.svg), and its [searchable text equivalent](examples/lisbon-coast/field-cards.md) to see what the data really supports. The data is a fictional English-language trip; a separate [layout concept](assets/readme-day-card.en.svg) remains available.

Each field card can:

- ship as a separate high-resolution PNG that is easy to save to a phone;
- retain a lossless SVG source for editing, printing, or embedding in a guide;
- keep a searchable text version for addresses and accessibility;
- expose missing hotel, flight, or ticket details instead of inventing them.

### 3. One plan, multiple publishing targets

Feishu is an optional publisher, not a prerequisite. The Skill completes a platform-independent local delivery package first, then publishes through whichever connected tools the user actually has.

[View the multi-document publishing diagram](assets/readme-publishing.en.svg).

Supported outputs:

- **Always available:** Markdown, `trip.json`, route maps in SVG/PNG, and daily field cards;
- **Feishu / Lark:** publish to Docx or Wiki, insert images, and read back for verification when the capability is installed and authorized;
- **Notion / Google Docs:** publish when the corresponding connector is available and authorized;
- **DOCX / PDF:** create an editable or print-ready archive when document tools are available;
- **No platform connected:** still deliver the complete core guide without blocking on a CLI, account, or connector.

## From the demo to your own trip

1. **Explore first:** open the [Paris workbench](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/), choose a Day tab or map badge, and inspect the field-guide board. The earlier [fictional Lisbon demo](https://judefluen-coder.github.io/plan-and-maintain-trips/workbench/?demo=lisbon) remains available.
2. **Create your trip:** install the Skill and tell your agent your dates, destinations, preferences, and existing bookings. Have it create your own `trip.json` **outside the Skill directory**. The static website does not yet generate a whole trip from scratch with hosted AI.
3. **Connect the visual workbench:** any agent can use JSON import. If you use Codex CLI or Claude Code CLI and want browser-triggered proposals, make sure its model authorization or balance works, then run the command below locally. The bridge prints and opens an online workbench link with a temporary pairing secret; click “连接本机” (“Connect locally”) on the page. Do not share the pairing link. If your browser asks to connect to a local service, approve only the page you trust.

   ```bash
   python3 bridge/server.py --trip /absolute/path/to/your/trip.json
   ```

   Claude Code: `python3 bridge/server.py --provider claude --trip /absolute/path/to/your/trip.json`. Its bridge request includes the bundled Skill guidance and disables built-in and MCP tools; your CLI account pays for the model request.

4. **Review before applying:** select one day and describe a change in natural language. Inspect the map, timeline, warnings, and diff; only your confirmation writes back to `trip.json`, with a `.bak` backup. The current bridge revises one day at a time. Model requests use your selected local CLI and your own quota; GitHub Pages supplies neither model compute nor trip storage. See the [workbench setup and safety guide](web/README.md).

For a complete human-readable guide, see the [Paris + French Riviera case](examples/france-2026/README.md), with maps, ticket checklist, transport, food, and hotel-selection logic. For reproducible offline exports, use the fictional [Lisbon → Cascais dataset](examples/lisbon-coast/README.md) and its [live offline-route preview](https://judefluen-coder.github.io/plan-and-maintain-trips/). These examples serve different purposes.

See the [changelog](CHANGELOG.md) for version history.

Found a bug or have a concrete workflow improvement? Read [Contributing](CONTRIBUTING.md) and use the repository's issue forms with redacted reproduction details.

For a first trial, follow the [five-minute new-user test](docs/try-it.md). A [maintainer launch kit](docs/launch-kit.md) is prepared but has not been posted on anyone's behalf.

## Capabilities and deliverables

The real workbench screenshots above show the map and field-guide board. This table shows what the whole project does throughout planning.

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
├── bridge/                      # optional local Codex / Claude bridge
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
