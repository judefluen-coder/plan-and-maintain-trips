# Lisbon → Cascais: complete output example

This is a **fictional demonstration**, not a bookable itinerary. Names such as “Reserved gallery entry” and “Example Riverside Café” are placeholders; `example.com` links are not ticket or restaurant services.

Open [the offline phone route page](route-offline.html) in a browser, or inspect the [lossless route atlas](route.svg). The route page embeds its data and code, so its day tabs work without internet. Its external navigation buttons still need a connection. You can also import [the calendar](trip.ics) or [the KML points](trip.kml).

The [guide](guide.md) shows how the booking checklist, five-day itinerary, food choice, field cards, and audit fit together. All machine-generated files above come from the single [example trip state](../../assets/trip.example.json); the guide is a human-readable demonstration of the same data.

Regenerate locally from the repository root:

```bash
python3 scripts/validate_trip.py assets/trip.example.json --strict
python3 scripts/render_route_map.py assets/trip.example.json examples/lisbon-coast/route.svg --from-trip
python3 scripts/export_field_pack.py assets/trip.example.json examples/lisbon-coast/
```
