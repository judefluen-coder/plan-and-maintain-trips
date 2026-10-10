# Alternatives and positioning

Checked on 2026-10-10. This comparison uses the projects' public READMEs and this repository's code. We have **not** run every project against the same trip prompt. “Not highlighted” does not mean a feature is absent. Stars and prices are intentionally excluded.

| Project | Form | What its public documentation emphasizes | Trade-off to consider |
|---|---|---|---|
| [Plan & Maintain Trips](../README.en.md) | Codex / Agent Skill | Dated evidence, precise booking states, protected anchors and revision control; SVG, offline HTML, KML, ICS, and optional document publishing | Needs an agent to research live facts; is not a collaborative app; some exports need timed and geocoded input |
| [trip-planner-skill](https://github.com/skywain/trip-planner-skill) | Agent Skill | Hour-by-hour itineraries, flight comparisons, KML, ICS, eight page themes, and several replan modes | Strong emphasis on designed web roadbooks, with a more complex query and rendering workflow |
| [Jianhao Travel Planner](https://github.com/awangwang123/jianhao-travel-planner) | Chinese Agent Skill | Live research, single-file offline roadbooks, real photos, hand-drawn guides, and reusable city food cards | Suits content-rich Chinese roadbooks; its public materials emphasize editorial and visual delivery |
| [travel-plan-viz](https://github.com/zexuanw958-svg/travel-plan-viz) | Agent Skill | Mobile-first single-file HTML, interactive maps, timelines, reminders, and field/coordinate validation | Good for a lightweight web guide; its README says map tiles and photos may need connectivity |
| [marco-polo.skill](https://github.com/megumi-ben/marco-polo.skill) | Agent Skill | Amap places, entrances and routes; Xiaohongshu experience research; map, food, and city handbooks | Strong for domestic China itineraries; the full workflow needs other skills, credentials, and sign-in |
| [TREK](https://github.com/liketrek/TREK) | Self-hosted travel app | Collaboration, interactive maps, reservations, budgets, offline PWA, and MCP | Suits ongoing shared trip management; requires deployment and operates at a different product layer |

## Positioning

This project keeps a changing travel plan in `trip.json`, records sources and recheck dates for volatile facts, and derives consistent itineraries and execution materials. It can publish through available tools such as Feishu, but does not bundle those accounts or services.

The route SVG, offline page, KML, and ICS can come from the same timed, geocoded trip state. See the [Lisbon → Cascais output package](../examples/lisbon-coast/README.md). Live navigation, inventory, restaurant hours, and service status still require a fresh check.

A useful next benchmark would give each project the same multi-city dates, fixed booking, weather disruption, and sold-out ticket, then compare source quality, time-zone accuracy, revision consistency, mobile readability, and run cost.
