---
name: plan-and-maintain-trips
description: Plan, research, revise, audit, and publish executable trips for any destination. Use when Codex needs to design a single-city or multi-city itinerary, compare lodging or transport, manage fixed bookings and changing constraints, distinguish booking availability from unreleased inventory, create route maps and day-of field cards, recheck volatile travel facts, or publish a final travel guide to an available document platform.
---

# Plan and Maintain Trips

Treat a trip as a maintained project, not a one-shot list of attractions. Keep one canonical state, preserve user decisions, verify volatile facts from current sources, and derive every itinerary, checklist, map, and published document from that state.

## Start the project

Collect only the information that changes the plan materially:

- dates or trip length;
- destinations or open-ended region;
- travelers and mobility needs;
- arrival and departure constraints;
- total and nightly budgets;
- interests, pace, food needs, and lodging requirements;
- bookings already made;
- dates or activities that must not move;
- requested outputs and publishing platform.

If details are missing, state safe assumptions and begin a draft. Ask a concise question only when the answer would change cities, dates, cost class, accessibility, or an irreversible booking recommendation.

Create a project directory outside the skill. Copy `assets/trip.example.json` to `trip.json` and replace the example data. Treat `trip.json` as the source of truth. Read `references/state-model.md` before creating or materially changing it.

Never put traveler credentials, payment data, passport numbers, API tokens, or document authorization codes in the project or skill.

## Choose the operating mode

- **Plan:** build the city/base structure first, then schedule days.
- **Revise:** record the new decision, compute its impact, and update every affected artifact.
- **Booking:** turn planned items into a status-controlled booking console with official links.
- **Recheck:** refresh only volatile facts whose review time has arrived.
- **Day-of:** produce compact field cards from confirmed bookings and current conditions.
- **Publish:** render local artifacts first, then use an available optional publisher.

The user can move between modes naturally. Do not restart from scratch when a decision changes.

## Build the plan in order

### 1. Freeze the trip skeleton

Set entry and exit points, overnight bases, night counts, transfers, and hard anchors. Separate:

- hard anchors that require explicit approval to move;
- soft targets that may shift;
- optional items that are first to cut;
- exclusions that must not reappear.

Validate date arithmetic before researching individual attractions:

```bash
python3 scripts/validate_trip.py /path/to/trip.json
```

Read `references/scheduling-and-change-control.md` for routing, pace, lodging, and impact-analysis rules.

### 2. Research volatile facts

Browse whenever information may have changed: opening days, timed-entry rules, sale windows, inventory, prices, transit schedules, strikes, special events, weather, restaurant hours, hotel availability, and local regulations.

Prefer primary sources in this order:

1. venue, operator, government, airline, railway, hotel, or restaurant official page;
2. official tourism authority or ticketing partner;
3. a reputable secondary source only when the primary source is unavailable.

Record the claim, source URL, checked time, applicable date, and next recheck time in `trip.json` or an evidence file. Read `references/research-and-evidence.md` before assigning booking status.

Never equate a missing date with sold out. Use only these booking states:

- `bookable`
- `not_released`
- `date_not_in_system`
- `sold_out`
- `walk_in`
- `same_day`
- `booked`
- `needs_recheck`

Use `unknown` only during research and eliminate it before final delivery.

### 3. Schedule executable days

Place hard anchors first. Then group attractions by geography, opening hours, realistic dwell time, security queues, meals, transfers, rest, and weather exposure.

For every day include:

- one primary outcome;
- hard anchors and arrival buffers;
- realistic visit and movement durations;
- a meal strategy tied to the route;
- a recovery block on long days;
- an estimated walking/standing load;
- a first-cut item;
- a weather or disruption branch.

Do not optimize only for straight-line distance. A geographically close venue can still be infeasible because of opening times, security, hills, luggage, or a later reservation.

### 4. Produce the booking console

For each paid or reserved item show:

- current status;
- intended date, time, and traveler count;
- official purchase or reservation link;
- price basis and whether fees/taxes are included;
- sale-window explanation;
- refund or cancellation condition when material;
- failure fallback;
- next action and next recheck date.

Do not claim success until the user has a confirmation or QR code. Do not buy, reserve, message, install software, or publish externally without user authorization.

### 5. Produce day-of field cards

Create one mobile-first card for every calendar day, including arrival, transfer, and departure days. Each card must contain:

- today's anchor;
- follow-in-order timeline;
- ticket wallet;
- one-tap location links;
- morning or previous-night checks;
- late/rain/closure decision;
- one sentence stating what must be protected.

Leave explicit fill-in fields for unknown hotel, flight, terminal, booking number, insurance, or emergency-contact details. Never invent them.

### 6. Create route maps

Create one map per compact geographic segment, normally no more than six days. Use a different color per day, numbered stops, solid lines for walking, dashed lines for transit, and short day cards.

When latitude/longitude data is available, copy `assets/route.example.json`, replace its data, and run:

```bash
python3 scripts/render_route_map.py route.json route.svg
```

Inspect the SVG visually before delivery. Convert to a high-resolution PNG only if a renderer is available; preserve the SVG as the lossless source. Label a schematic map honestly and do not imply turn-by-turn accuracy.

## Maintain changes without drift

When the user changes one decision:

1. restate the new decision and protected anchors;
2. update the canonical state and decision log;
3. identify affected dates, bookings, passes, hotels, transport, meals, maps, budgets, and field cards;
4. update all affected outputs;
5. scan for stale statements from earlier versions;
6. report what changed and what did not.

Never reintroduce excluded items or silently move a hard anchor. Do not compare hotel teaser prices with full-stay, tax-included checkout prices.

## Deliver and publish

Always generate platform-neutral local artifacts first. Read `references/deliverables-and-publishing.md` before publishing.

Minimum final package:

- canonical trip state;
- booking console;
- detailed itinerary;
- route-linked food and lodging decisions;
- budget and pace summary;
- day-of field cards;
- route map source and high-resolution export when available;
- final audit.

Treat Feishu/Lark, Notion, Google Docs, DOCX, PDF, and other destinations as optional adapters. Detect capabilities before using them. If the requested publisher is unavailable, finish the local package and offer an importable Markdown or DOCX/PDF fallback. Never make a missing CLI or account block the core plan.

## Validate before handoff

Read `references/quality-gates.md` and run:

```bash
python3 scripts/validate_trip.py /path/to/trip.json --strict
python3 scripts/check_links.py /path/to/guide.md
```

Confirm that:

- every calendar date is covered exactly once;
- weekday labels match dates;
- lodging nights and transfer dates reconcile;
- fixed anchors have not moved;
- booking statuses are evidence-backed;
- volatile facts show their check date;
- the day-of cards match the detailed itinerary;
- maps, budgets, restaurants, and checklists share the same version;
- obsolete routes and claims are absent;
- published content was read back after writing.

If unresolved fields remain, list them prominently and explain exactly what input or later recheck will close them.

## Reference routing

- Read `references/state-model.md` when creating or editing project state.
- Read `references/research-and-evidence.md` for web research, prices, inventory, and citations.
- Read `references/scheduling-and-change-control.md` for routing, pacing, hotels, and revisions.
- Read `references/deliverables-and-publishing.md` for guides, maps, field cards, and publisher fallbacks.
- Read `references/quality-gates.md` before final delivery or a major recheck.
