# Changelog

This project uses `vMAJOR.MINOR.PATCH` tags. While the major version is `0`, minor releases may adjust the trip schema or output conventions; patch releases fix behavior without intentionally changing them.

## Unreleased

- No changes yet.

## v0.1.0 — 2026-10-10

First public preview release of the reusable Codex travel-planning skill.

- Canonical `trip.json` state, dated evidence, controlled booking statuses, protected anchors, exclusions, and revision guidance.
- Bilingual Chinese and English README, route atlas and day-card previews, and optional document-publishing workflow.
- SVG route atlas, offline phone route page, KML points, and ICS calendar; the SVG can now derive directly from structured `trip.json` items.
- Non-destructive same-day replan proposals and a reusable city restaurant catalog helper.
- Strict sample-state validation, behavioral tests, GitHub CI, and a full fictional Lisbon → Cascais output example.

The release does not provide live booking inventory, a hosted app, or bundled Feishu credentials. Navigation links and current travel facts still require connectivity and rechecking.
