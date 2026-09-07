# Deliverables and publishing

## Platform-neutral package

Complete local artifacts before publishing:

- `trip.json`: canonical state;
- `guide.md`: full human-readable guide;
- `booking-checklist.md` or an equivalent section;
- `route-map.svg` plus PNG when a renderer exists;
- `audit.md`: final quality report.

Keep one authoritative guide. Do not leave several unlabeled competing versions.

## Guide order

Use this order unless the user requests another:

1. route map or trip-at-a-glance;
2. immediate booking checklist;
3. confirmed decisions and unresolved fields;
4. daily itinerary;
5. route-linked restaurants;
6. lodging and transport decisions;
7. budget and pace;
8. day-of field cards;
9. weather and disruption fallbacks;
10. final audit and source check date.

## Day-of field card

Keep each card mobile-first and screenshot-friendly:

- date, base, and primary outcome;
- anchor and arrival deadline;
- ordered timeline;
- ticket wallet;
- one-tap location links;
- previous-night or morning checks;
- late/rain/closure branch;
- one sentence stating what to protect.

Use explicit blanks for unknown flight, terminal, hotel, booking number, insurance, or emergency contact. Fill them only from user-provided confirmations.

When a visual execution pack is requested, create one SVG or high-resolution PNG per day and preserve a searchable text version. Inspect each image at phone width for clipped text, illegible type, excessive blank space, and stale itinerary details.

## Route map

Use geographic coordinates when available, but describe the map as schematic unless it uses a verified navigation engine. Prefer one map per base or compact region and no more than six day colors per map.

Always preserve a vector source. Inspect labels, route order, legends, dates, and hotel inclusion before exporting a high-resolution image.

## Publisher adapter order

Detect capabilities and honor the user's requested destination:

1. requested connected publisher, when available and authorized;
2. Markdown plus images;
3. DOCX or PDF when document tools are available;
4. structured response plus downloadable local files.

Feishu/Lark is optional. If requested and available, use the installed Lark document workflow, request user authorization only when needed, write with user identity, insert images, and read the result back. If the CLI or account is unavailable, finish the local guide and offer an importable Markdown/DOCX fallback.

Apply the same adapter principle to Notion, Google Docs, or other platforms. Never install software or create external accounts without explicit permission.

## Publish verification

After any external write:

- read back the title and changed section;
- verify images or resource tokens exist;
- confirm critical dates, anchors, and statuses;
- check that no obsolete version remains active;
- return the direct document link and any unresolved fill-in fields.

A publishing failure must not destroy or invalidate the local package.
