# Research and evidence policy

## Source hierarchy

Use the narrowest authoritative source that supports the claim:

1. official venue, operator, government, airline, railway, hotel, or restaurant;
2. official ticketing partner or destination authority;
3. reputable secondary source when the primary source is inaccessible;
4. aggregator only for discovery or clearly labeled price comparison.

Do not treat search snippets as sufficient when the target page is accessible. Do not quote more than necessary.

## Facts that require current research

Browse for opening hours, closure days, renovations, reservation rules, release windows, live availability, exhibitions, performances, prices, taxes, hotel inventory, transit schedules, strikes, road rules, weather, entry rules, and local regulations.

Recheck per volatility:

- inventory and prices: at decision time and immediately before payment;
- sale windows: whenever the official date range advances;
- venue hours and transit plans: at planning, seven days before, and 72 hours before;
- weather and outdoor safety: seven days, 72 hours, and morning-of;
- event security and strikes: 72 hours and morning-of.

## Availability classification

Use evidence, not inference:

- A calendar ending before the target date means `date_not_in_system` unless an official sale schedule proves `not_released`.
- A disabled or absent time is not `sold_out` without an explicit official signal.
- An anti-bot or CAPTCHA page means the inventory is unverified; do not bypass it without user involvement.
- A pass covering admission does not imply a timed slot exists.
- A ticket in a cart is not `booked`; require confirmation or a QR code.

## Price discipline

Label every price basis:

- per person, room, vehicle, or party;
- one night, sample night, or continuous stay;
- before or after taxes/fees;
- refundable or nonrefundable;
- breakfast and baggage inclusion;
- source currency and planning exchange-rate assumption.

Never combine unrelated nightly teaser prices into a fake continuous-stay quote. Compare hotels using the same dates, occupancy, bed, taxes, meal plan, and cancellation terms.

## Evidence record

For each consequential claim record:

- what is claimed;
- direct URL;
- source type;
- checked timestamp with timezone;
- date or booking the claim applies to;
- whether it is observed or inferred;
- when it must be checked again.

If a claim cannot be verified, label the uncertainty and provide a low-risk fallback.

## Research stop rule

Stop once the plan has enough verified information to make the next decision. Do not research dozens of restaurants or hotels before the user has selected a neighborhood, budget, or food preference.
