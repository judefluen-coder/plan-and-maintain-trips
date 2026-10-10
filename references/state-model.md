# Canonical trip state

Use one JSON document as the source of truth. Outputs may summarize it but must not override it silently.

## Top-level structure

```json
{
  "schema_version": 1,
  "trip": {},
  "preferences": {},
  "segments": [],
  "transports": [],
  "anchors": [],
  "bookings": [],
  "days": [],
  "exclusions": [],
  "decisions": [],
  "evidence": []
}
```

## Required trip fields

- `trip.id`: stable slug for project artifacts.
- `trip.title`: user-facing name.
- `trip.start_date`, `trip.end_date`: inclusive ISO dates.
- `trip.travelers`: positive integer.
- `trip.home_currency`: ISO currency code used for the budget summary.

Store arrival and departure details only when known. Use `null`, not invented values.

## Preferences

Record only planning-relevant preferences:

- `pace`: `low`, `medium`, or `high`;
- `interests`: ranked tags;
- `mobility`: walking, stairs, accessibility, heat, or luggage limits;
- `food`: cuisines, allergies, meal duration, and price target;
- `lodging`: bed, room size, nightly cap, neighborhood, cancellation, and facility needs;
- `transport`: rail, transit, driving, cycling, or taxi preferences.

Keep sensitive identity and payment data outside this file.

## Segments and nights

Each overnight base has:

```json
{
  "id": "base-a",
  "base": "City A",
  "start_date": "2030-05-01",
  "end_date": "2030-05-04",
  "nights": 3,
  "lodging_status": "shortlist"
}
```

Treat `end_date` as checkout day. `nights` must equal the date difference. Adjacent segments may share the transfer date.

## Anchors

Use anchors for anything that structures a day:

```json
{
  "id": "anchor-gallery",
  "title": "Reserved gallery visit",
  "date": "2030-05-02",
  "time": "10:30",
  "duration_minutes": 120,
  "rigidity": "hard",
  "booking_id": "booking-gallery"
}
```

- `hard`: do not move without explicit approval.
- `soft`: preserve if possible; explain any move.
- `optional`: first-cut candidate.

## Booking states

Use exactly one of:

- `bookable`: target inventory is visible and can be purchased now.
- `not_released`: an official sale window shows the target is not yet on sale.
- `date_not_in_system`: the system does not expose the date and no sale rule resolves why.
- `sold_out`: the official target inventory explicitly has no availability.
- `walk_in`: no advance reservation is required or offered.
- `same_day`: inventory is released only on or near the visit day.
- `booked`: the traveler has confirmation or a QR code.
- `needs_recheck`: a prior fact is too old or conditional for execution.
- `unknown`: temporary research state; forbidden in final delivery.

Each booking should include `source_url`, `checked_at`, `next_check_at`, `price`, `price_basis`, and `fallback` when applicable.

## Days

Cover every calendar date in the inclusive trip range exactly once. Arrival, transfer, rest, and departure days count.

Each day should include:

- `date`, `base`, and `title`;
- `primary_outcome`;
- ordered `items` with start/end or duration;
- `hard_anchor_ids`;
- `estimated_walk_km` and `pace`;
- `first_cut`;
- `weather_fallback`;
- `field_card_status`.

For exportable maps, calendars, food matching, and day-of replanning, use structured `items` instead of plain strings:

```json
{
  "id": "gallery",
  "name": "Reserved gallery entry",
  "start": "10:00",
  "end": "12:00",
  "lat": 38.7108,
  "lon": -9.1427,
  "anchor_id": "gallery-entry",
  "booking_id": "gallery-ticket",
  "rigidity": "hard",
  "mode_from_previous": "walk"
}
```

Use local wall-clock times in the trip's IANA `timezone`; the calendar exporter converts them to UTC. Coordinates are WGS84 decimal degrees for the actual entrance or meeting point, not the venue centroid when these differ. Add `address`, `note`, `meal` (`lunch` or `dinner`), or `weather_sensitive` only when known. Text items remain valid for older plans but cannot become calendar events or map points. Never fabricate coordinates or times to fill an export.

Optionally store researched food candidates in top-level `restaurants` with stable `id`, `name`, `base`, WGS84 `lat` and `lon`, `meals`, `price_level`, `reservation`, `source_url`, and `checked_at`. `closed_weekdays` uses lowercase English three-letter weekday names. These are candidates, not confirmed bookings; keep current opening hours and availability in the evidence or booking state. The food helper uses straight-line proximity only and never claims a walking time.

For reuse across trips, keep the same `restaurants` array in a separate city catalog JSON such as `assets/restaurants.example.json` and pass it with `--catalog`. A candidate with the same `id` in `trip.json` overrides the catalog entry. Do not carry old opening-hour or price claims into a new trip without rechecking their dates.

## Decisions and exclusions

Append decisions rather than rewriting history:

```json
{
  "id": "decision-004",
  "at": "2030-04-01T10:00:00+08:00",
  "decision": "Keep the museum on May 2",
  "protected": ["anchor-gallery"],
  "supersedes": "decision-002"
}
```

Store rejected places or routes in `exclusions` with a reason. Before final delivery, scan outputs to ensure excluded items are absent except in clearly labeled historical notes.

## Evidence

Use stable IDs so a claim can be refreshed without changing every reference:

```json
{
  "id": "evidence-gallery-hours",
  "claim": "Open on the planned date",
  "source_url": "https://example.com/official",
  "source_type": "official_venue",
  "checked_at": "2030-04-01T09:00:00Z",
  "applies_to": "2030-05-02",
  "next_check_at": "2030-04-25T09:00:00Z"
}
```

Do not store copied articles or long quotations. Store the claim, a short paraphrase, and the direct source URL.
