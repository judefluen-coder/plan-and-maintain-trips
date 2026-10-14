# Changelog

This project uses `vMAJOR.MINOR.PATCH` tags. While the major version is `0`, minor releases may adjust the trip schema or output conventions; patch releases fix behavior without intentionally changing them.

## Unreleased

No changes yet.

## v0.2.0 — 2026-10-14

- Render mobile SVG day cards and searchable Markdown directly from structured `trip.json` days; include them in the one-command demo and CI drift checks.
- Align the fictional sample's first-cut items with its actual timeline, and distinguish a bookable gallery slot from a purchased ticket.
- Add contributor guidance, privacy-aware issue forms, and a pull-request checklist.
- Prepare an independent-user trial script and an unposted launch kit with a social-preview PNG.

## v0.1.0 — 2026-10-14

First public preview release of the reusable Codex travel-planning skill.

- Canonical `trip.json` state, dated evidence, controlled booking statuses, protected anchors, exclusions, and revision guidance.
- Bilingual Chinese and English README, route atlas and day-card previews, and optional document-publishing workflow.
- SVG route atlas, offline phone route page, KML points, and ICS calendar; the SVG can now derive directly from structured `trip.json` items.
- Non-destructive same-day replan proposals and a reusable city restaurant catalog helper.
- Strict sample-state validation, behavioral tests, GitHub CI, and a full fictional Lisbon → Cascais output example.
- One-command offline demo that regenerates the fictional route, calendar, and day-of advice.
- Redacted France historical case study, clearly separated from the runnable fictional dataset.
- MIT license and public HTTPS installation without a GitHub CLI login.

The release does not provide live booking inventory, a hosted app, or bundled Feishu credentials. Navigation links and current travel facts still require connectivity and rechecking.
