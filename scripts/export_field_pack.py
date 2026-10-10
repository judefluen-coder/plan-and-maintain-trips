#!/usr/bin/env python3
"""Export an offline route page, KML, and calendar from one trip.json."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


COLORS = ("#be4b49", "#248569", "#d58a13", "#3971b8", "#7958a6", "#138f93")
KML_NS = "http://www.opengis.net/kml/2.2"


def load(path: Path) -> tuple[dict, list[dict], ZoneInfo]:
    data = json.loads(path.read_text(encoding="utf-8"))
    trip = data.get("trip", {})
    try:
        zone = ZoneInfo(trip["timezone"])
    except (KeyError, ZoneInfoNotFoundError) as exc:
        raise ValueError("trip.timezone must be a valid IANA time zone") from exc
    days = data.get("days", [])
    if not isinstance(days, list) or not days:
        raise ValueError("days must be a non-empty list")
    for day in days:
        datetime.fromisoformat(day["date"])
        if not isinstance(day.get("items"), list):
            raise ValueError(f"{day['date']}: items must be a list")
        for item in day["items"]:
            if not isinstance(item, dict):
                continue  # Legacy text items remain valid, but cannot become map/calendar events.
            if not item.get("name"):
                raise ValueError(f"{day['date']}: a structured item needs name")
            if ("lat" in item) != ("lon" in item):
                raise ValueError(f"{day['date']} {item['name']}: lat and lon must appear together")
            if "lat" in item:
                lat, lon = item["lat"], item["lon"]
                if not all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v) for v in (lat, lon)) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError(f"{day['date']} {item['name']}: invalid coordinates")
            if "start" in item or "end" in item:
                if not isinstance(item.get("start"), str) or not isinstance(item.get("end"), str):
                    raise ValueError(f"{day['date']} {item['name']}: timed items need start and end")
                start = datetime.fromisoformat(f"{day['date']}T{item['start']}")
                end = datetime.fromisoformat(f"{day['date']}T{item['end']}")
                if end <= start:
                    raise ValueError(f"{day['date']} {item['name']}: end must follow start")
    structured = [item for day in days for item in day["items"] if isinstance(item, dict)]
    if not any("lat" in item for item in structured) or not any("start" in item for item in structured):
        raise ValueError("export needs at least one geocoded and one timed structured item; text-only days remain valid for planning")
    return data, days, zone


def esc_ics(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def fold_ics(line: str) -> str:
    parts, current = [], ""
    for char in line:
        if len((current + char).encode("utf-8")) > 73:
            parts.append(current)
            current = " " + char
        else:
            current += char
    parts.append(current)
    return "\r\n".join(parts)


def calendar(data: dict, days: list[dict], zone: ZoneInfo) -> str:
    trip = data["trip"]
    bookings = {b.get("id"): b for b in data.get("bookings", []) if isinstance(b, dict)}
    anchors = {a.get("id"): a for a in data.get("anchors", []) if isinstance(a, dict)}
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//plan-and-maintain-trips//field-pack//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{esc_ics(trip.get('title', 'Trip'))}"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for day in days:
        for index, item in enumerate(day["items"]):
            if not isinstance(item, dict) or "start" not in item:
                continue
            start = datetime.fromisoformat(f"{day['date']}T{item['start']}").replace(tzinfo=zone).astimezone(timezone.utc)
            end = datetime.fromisoformat(f"{day['date']}T{item['end']}").replace(tzinfo=zone).astimezone(timezone.utc)
            anchor = anchors.get(item.get("anchor_id"), {})
            booking = bookings.get(item.get("booking_id") or anchor.get("booking_id"), {})
            item_id = re.sub(r"[^a-zA-Z0-9_-]", "-", str(item.get("id") or index))
            trip_id = re.sub(r"[^a-zA-Z0-9_-]", "-", str(trip.get("id") or "trip"))
            description = [f"Day: {day.get('title') or day.get('base', '')}"]
            if booking:
                description.append(f"Booking status: {booking.get('status', 'unknown')}")
                if booking.get("source_url"):
                    description.append(f"Official link: {booking['source_url']}")
            if item.get("note"):
                description.append(str(item["note"]))
            lines += ["BEGIN:VEVENT", f"UID:{trip_id}-{day['date']}-{item_id}@plan-and-maintain-trips.local", f"DTSTAMP:{stamp}", f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}", f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}", f"SUMMARY:{esc_ics(item['name'])}", f"DESCRIPTION:{esc_ics(chr(10).join(description))}"]
            if item.get("address"):
                lines.append(f"LOCATION:{esc_ics(item['address'])}")
            if anchor.get("rigidity") == "hard" or item.get("rigidity") == "hard":
                lines += ["BEGIN:VALARM", "TRIGGER:-PT60M", "ACTION:DISPLAY", f"DESCRIPTION:{esc_ics(item['name'])}", "END:VALARM"]
            lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold_ics(line) for line in lines) + "\r\n"


def kml(data: dict, days: list[dict]) -> str:
    ET.register_namespace("", KML_NS)
    q = lambda name: f"{{{KML_NS}}}{name}"
    root = ET.Element(q("kml"))
    document = ET.SubElement(root, q("Document"))
    ET.SubElement(document, q("name")).text = data["trip"].get("title", "Trip")
    for day_index, day in enumerate(days):
        folder = ET.SubElement(document, q("Folder"))
        ET.SubElement(folder, q("name")).text = f"{day['date']} · {day.get('title') or day.get('base', '')}"
        points = []
        for item in day["items"]:
            if not isinstance(item, dict) or "lat" not in item:
                continue
            point = (item["lon"], item["lat"])
            points.append(point)
            placemark = ET.SubElement(folder, q("Placemark"))
            ET.SubElement(placemark, q("name")).text = item["name"]
            ET.SubElement(placemark, q("description")).text = f"{item.get('start', '')}–{item.get('end', '')} · {item.get('mode_from_previous', 'walk')}"
            ET.SubElement(ET.SubElement(placemark, q("Point")), q("coordinates")).text = f"{point[0]},{point[1]},0"
        if len(points) > 1:
            line = ET.SubElement(folder, q("Placemark"))
            ET.SubElement(line, q("name")).text = f"Day {day_index + 1} · order only, not navigable streets"
            ET.SubElement(ET.SubElement(line, q("LineString")), q("coordinates")).text = " ".join(f"{lon},{lat},0" for lon, lat in points)
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def page(data: dict, days: list[dict]) -> str:
    title = html.escape(str(data["trip"].get("title", "Trip")))
    payload = json.dumps({"days": days, "bookings": data.get("bookings", [])}, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 离线路线</title>
<style>
:root{{--ink:#173253;--muted:#597088;--paper:#f7f3eb;--card:#fff;--line:#dce3e7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"PingFang SC",sans-serif}}header{{padding:22px 18px 12px;max-width:980px;margin:auto}}h1{{font-size:clamp(24px,5vw,38px);margin:0}}header p,.note{{color:var(--muted);margin:5px 0}}main{{max-width:980px;margin:auto;padding:0 14px 40px}}.tabs{{display:flex;gap:7px;overflow:auto;padding:10px 0 14px}}button{{font:inherit;cursor:pointer}}.tabs button{{border:1px solid var(--line);border-radius:999px;background:white;padding:8px 13px;white-space:nowrap}}.tabs button[aria-selected=true]{{background:var(--ink);color:white}}.layout{{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(280px,1fr);gap:14px}}.panel{{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden}}.map-wrap{{height:550px;touch-action:none;overflow:hidden;background:linear-gradient(90deg,#edf2ed 1px,transparent 1px),linear-gradient(#edf2ed 1px,transparent 1px),#fbfcf9;background-size:40px 40px}}svg{{width:100%;height:100%}}.info{{padding:16px}}.stops{{list-style:none;padding:0;margin:0}}.stops li{{border-top:1px solid var(--line);padding:12px 0}}.stops a{{color:#166d89;margin-right:12px}}.time{{font-variant-numeric:tabular-nums;color:var(--muted);font-size:14px}}.badge{{display:inline-block;border-radius:99px;padding:1px 7px;background:#e9f2f1;color:#235e61;font-size:12px}}.map-caption{{padding:9px 14px;color:var(--muted);font-size:13px}}@media(max-width:700px){{.layout{{grid-template-columns:1fr}}.map-wrap{{height:360px}}}}
.map-wrap{{touch-action:pan-y}}@media(max-width:700px){{.map-wrap{{height:300px}}}}</style></head><body><header><h1>{title}</h1><p>离线路线册 · 地点、顺序和时间来自同一份 trip.json</p></header><main><nav class="tabs" id="tabs" aria-label="选择日期"></nav><section class="layout"><div class="panel"><div class="map-wrap"><svg id="map" viewBox="0 0 800 600" role="img" aria-label="当日地点示意图"></svg></div><div class="map-caption">示意连线仅表示游览顺序，不代表可通行道路。地点和计划离线可看；点击导航需要网络。</div></div><div class="panel info"><h2 id="daytitle"></h2><p class="note" id="outcome"></p><ol class="stops" id="stops"></ol><p class="note" id="fallback"></p></div></section></main>
<script type="application/json" id="trip-data">{payload}</script><script>
const data=JSON.parse(document.getElementById('trip-data').textContent),tabs=document.getElementById('tabs'),svg=document.getElementById('map'),list=document.getElementById('stops');
const NS='http://www.w3.org/2000/svg',colors={json.dumps(COLORS)};
function node(name,attrs={{}}){{let e=document.createElementNS(NS,name);for(let [k,v] of Object.entries(attrs))e.setAttribute(k,v);return e}}
function show(index){{
  const day=data.days[index],color=colors[index%colors.length];
  const points=day.items.filter(x=>typeof x==='object'&&Number.isFinite(x.lat)&&Number.isFinite(x.lon));
  tabs.querySelectorAll('button').forEach((b,i)=>b.setAttribute('aria-selected',i===index));
  document.getElementById('daytitle').textContent=day.date+' · '+(day.title||day.base||'');
  document.getElementById('outcome').textContent=day.outcome||day.primary_outcome||'';
  document.getElementById('fallback').textContent=day.weather_fallback?'雨天/中断：'+day.weather_fallback:'';
  list.replaceChildren();svg.replaceChildren();
  if(points.length){{
    const lats=points.map(p=>p.lat),lons=points.map(p=>p.lon);
    const minLat=Math.min(...lats),maxLat=Math.max(...lats),minLon=Math.min(...lons),maxLon=Math.max(...lons);
    const latSpan=maxLat-minLat,lonSpan=maxLon-minLon;
    const coords=points.map(p=>[lonSpan?80+(p.lon-minLon)/lonSpan*640:400,latSpan?520-(p.lat-minLat)/latSpan*440:300]);
    if(coords.length>1)svg.append(node('polyline',{{points:coords.map(p=>p.join(',')).join(' '),fill:'none',stroke:color,'stroke-width':5,'stroke-linecap':'round','stroke-linejoin':'round'}}));
    points.forEach((p,i)=>{{
      const [x,y]=coords[i],g=node('g',{{tabindex:0,role:'link','aria-label':p.name}});
      const c=node('circle',{{cx:x,cy:y,r:18,fill:color,stroke:'white','stroke-width':3}});
      const t=node('text',{{x,y:y+5,'text-anchor':'middle',fill:'white','font-size':15,'font-weight':'bold'}});
      const label=node('text',{{x,y:y-31,'text-anchor':'middle',fill:'#173253','font-size':24,'font-weight':600,'paint-order':'stroke',stroke:'white','stroke-width':7}});
      t.textContent=i+1;label.textContent=p.name;g.append(c,t,label);
      g.addEventListener('click',()=>open('https://www.google.com/maps/search/?api=1&query='+p.lat+','+p.lon,'_blank'));
      svg.append(g);
    }});
  }}else{{
    const message=node('text',{{x:400,y:300,'text-anchor':'middle',fill:'#597088','font-size':24}});
    message.textContent='这一天还没有已核实的地点坐标';svg.append(message);
  }}
  day.items.forEach(item=>{{
    const p=typeof item==='string'?{{name:item}}:item,li=document.createElement('li'),strong=document.createElement('strong');
    strong.textContent=p.name;li.append(strong);
    if(p.start){{const time=document.createElement('div');time.className='time';time.textContent=p.start+'–'+p.end+(p.mode_from_previous?' · '+p.mode_from_previous:'');li.append(time)}}
    if(Number.isFinite(p.lat)&&Number.isFinite(p.lon)){{const a=document.createElement('a');a.href='https://www.google.com/maps/search/?api=1&query='+p.lat+','+p.lon;a.target='_blank';a.rel='noopener';a.textContent='导航';li.append(a)}}
    if(p.address){{const span=document.createElement('span');span.className='time';span.textContent=p.address;li.append(span)}}
    list.append(li);
  }});
}}
data.days.forEach((d,i)=>{{let b=document.createElement('button');b.textContent=d.date+' · '+(d.title||d.base||'Day '+(i+1));b.addEventListener('click',()=>show(i));tabs.append(b)}});show(0);
</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trip_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    try:
        data, days, zone = load(args.trip_json)
        artifacts = {
            "route-offline.html": page(data, days),
            "trip.kml": kml(data, days),
            "trip.ics": calendar(data, days, zone),
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in artifacts.items():
            (args.output_dir / name).write_text(content, encoding="utf-8", newline="" if name.endswith(".ics") else None)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote route-offline.html, trip.kml, trip.ics to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
