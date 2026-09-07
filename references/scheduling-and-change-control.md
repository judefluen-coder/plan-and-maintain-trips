# Scheduling and change control

## Build the route from constraints

Schedule in this order:

1. arrival, departure, and overnight bases;
2. hard bookings and fixed dates;
3. venue closure days and timed-entry windows;
4. transfers and security buffers;
5. geographically coherent clusters;
6. meals and recovery blocks;
7. optional viewpoints, shopping, parks, and nightlife.

Use door-to-door time, not map distance alone. Include stairs, hills, station depth, luggage, security, queues, and the cost of returning to the hotel.

## Pace rules

Estimate both walking and standing. A museum-heavy day can be strenuous at low outdoor mileage.

Default guardrails unless the user requests a high pace:

- no more than two major museums or one major excursion per day;
- at least 30 minutes between unrelated timed entries;
- 45–60 minutes before performances and major transport;
- a seated meal or formal rest block on long days;
- a first-cut item that can be removed without breaking the route;
- no speculative attraction on a flight or long-transfer day.

Alternate high-load days with medium or low-load days when possible.

## Lodging logic

Prefer one hotel per base when day trips are practical. Recommend changing hotels only when it materially reduces transfers, avoids an unsafe/fragile commute, or enables a valuable early/late experience.

Compare lodging on:

- continuous-stay total and worst single-night price;
- room and bed size;
- cancellation and payment terms;
- air conditioning, elevator, accessibility, luggage storage, and noise;
- transit to hard anchors and day-trip stations;
- late arrival and early departure practicality;
- nearby breakfast and dinner options.

Do not add hotel points to a route map unless the user asks.

## Change impact matrix

When a decision changes, inspect every affected layer:

| Change | Recheck |
|---|---|
| Move a venue | closure day, ticket, pass, route, meal, map, field card |
| Change a base | hotel nights, transfers, day trips, luggage, budget, map |
| Add a show | dinner, dress/rest time, arrival buffer, late transit |
| Change flight | hotel checkout, airport, transfer day, first/last activity |
| Remove a site | pass economics, route gap, meal timing, map numbering |
| Change pace | dwell times, recovery blocks, first cuts, taxis, hotel location |

Update the canonical state first. Then regenerate or patch every dependent artifact. Explicitly state which hard anchors remained unchanged.

## Conflict handling

If two requirements cannot coexist, show the conflict with concrete timing or cost evidence. Protect confirmed bookings and user-declared invariants. Offer the smallest viable change rather than silently rewriting the whole trip.
