# Lisbon → Cascais · example guide

> Fictional output example for testing the skill. The sample gallery, restaurant, and `example.com` links are not real travel recommendations. Verify every venue, schedule, fare, and booking before using this pattern for a real trip.

Trip: 2030-05-01 through 2030-05-05 · 2 travelers · Lisbon 2 nights, Cascais 2 nights · Europe/Lisbon.

Open the [offline route page](route-offline.html), [vector route atlas](route.svg), [calendar](trip.ics), and [KML points](trip.kml).

## Booking checklist

| Item | Target | State in sample | Next action |
|---|---|---|---|
| Gallery entry | May 2, 10:00, 2 travelers | `bookable` in fictional sample | Replace example link with a real official page, recheck, then reserve |
| Market lunch | May 1 | `walk_in` in fictional sample | Verify real venue and current service hours |

`bookable` here demonstrates the state model; it is not a live availability claim. No booking is recorded as purchased.

## Day by day

| Date | Base | Planned sequence | First cut |
|---|---|---|---|
| May 1 | Lisbon | 10:00 bag drop → 11:00 riverside walk → 12:15 market lunch | Sunset viewpoint |
| May 2 | Lisbon | 10:00 fixed gallery entry → 12:30 garden break → 19:00 neighborhood dinner | Garden in rain or delay |
| May 3 | Cascais | 09:00 checkout → 11:00 coast train → 12:15 seafront walk | Lighthouse extension |
| May 4 | Cascais | Coastal museum → long lunch → beach or indoor branch | Clifftop extension |
| May 5 | Cascais | Breakfast → short promenade if time permits → onward transfer | Promenade |

The May 4–5 items are intentionally untimed text entries. They appear in the guide and offline page but do not become calendar events or map points; a real plan would add verified times and coordinates before export.

## Food, lodging, and budget

- The reusable food catalog contains an example Lisbon café near the May 1 lunch point. The food helper reports straight-line distance; opening hours, availability, and real walking time remain unverified.
- Lisbon and Cascais overnight bases reconcile to four nights. Hotel names and prices are intentionally unfilled.
- No fare or total budget is invented. Replace the sample with dated, tax-inclusive prices before a real booking decision.

## Day-of field cards

| Day | Protect | Morning check | If disrupted |
|---|---|---|---|
| May 1 | Easy arrival | Hotel bag-drop details | Shorten walk |
| May 2 | 10:00 gallery entry | Ticket confirmation and venue notice | Skip garden; do not move fixed entry without operator confirmation |
| May 3 | Base transfer | Train service and checkout | Skip seafront walk |
| May 4 | Easy coastal day | Weather and museum opening | Use the indoor branch |
| May 5 | Onward transfer | Departure time and luggage | Skip promenade |

## Audit

- Five calendar dates are covered once; segments total four nights.
- The hard May 2 gallery anchor matches its structured item time.
- The SVG atlas, offline page, KML, and ICS are generated from `assets/trip.example.json`.
- The fictional names, example links, unverified hours, hotel, and budget are visible unresolved fields, not real-world claims.
