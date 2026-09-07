# Quality gates

Run these gates before final delivery and after any major revision.

## State integrity

- Trip dates are valid and inclusive.
- Every date appears once in the day plan.
- Weekday labels match dates.
- Segment nights equal checkout minus check-in.
- Transfer dates reconcile adjacent bases.
- Hard anchors match the latest user decision.
- Excluded items are absent from active plans.
- Unknown or placeholder fields are prominently listed.

## Research integrity

- Consequential volatile claims use current sources.
- Official sources are preferred and linked directly.
- Every booking status follows the controlled vocabulary.
- `sold_out` is backed by an explicit official signal.
- Pass coverage and timed-entry requirements are separate.
- Prices state occupancy, dates, taxes/fees, and cancellation basis.
- Evidence records include checked and next-check times.

## Schedule integrity

- Arrival, departure, security, and queue buffers are realistic.
- Opening hours cover the planned visit window.
- Meals do not endanger hard anchors.
- Long days include rest or a lower-load follow-up day.
- Each day has a first-cut item and disruption branch.
- Walking, standing, stairs, hills, luggage, and late transit are considered.

## Artifact integrity

- Booking console, itinerary, budget, maps, and field cards share one version.
- Day-of cards match detailed daily times.
- Map day colors, route order, labels, and dates match the guide.
- Old airports, hotels, transport modes, sold-out shows, or superseded routes are absent.
- Links have been checked; protected/anti-bot pages are labeled for manual verification.
- Local source files remain available even when publishing externally.

## Publication integrity

- The user authorized the write.
- The requested identity/account was used.
- The changed section was read back.
- Images and attachments survived the update.
- The final response includes a direct link and unresolved fields.

Do not mark the project complete while a required artifact is missing or the published result has not been verified.
