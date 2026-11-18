const COLORS = ["#ba6650", "#308976", "#cc914a", "#6878a7", "#8a6e97", "#508c9f"];
const DEMO_LABELS = {
  Lisbon: "里斯本", Cascais: "卡斯凯什",
  "Recover from arrival and learn the historic center": "抵达后慢慢认识老城",
  "Focused art and architecture day": "艺术与建筑的一天",
  "Make a low-risk base transfer": "从里斯本从容转往海岸",
  "Explore the coast at an easy pace": "放慢脚步探索海岸",
  "Depart without schedule risk": "留足余裕，轻松离开",
  "Hotel bag drop": "酒店寄存行李", "Riverside orientation walk": "河畔散步，熟悉街区",
  "Market lunch": "市场午餐", "Gallery entry target": "画廊预约入场",
  "Garden recovery break": "花园休息", "Neighborhood dinner": "街区晚餐",
  "Hotel checkout": "酒店退房", "Transfer to the coast": "乘火车前往海岸",
  "Seafront walk": "海滨散步", "Paula Rego House of Stories": "保拉·雷戈故事馆",
  "Long lunch": "悠闲午餐", "Marechal Carmona Park": "卡尔莫纳公园", "Santa Marta Lighthouse Museum": "圣玛尔塔灯塔博物馆",
  "Breakfast near hotel": "酒店附近早餐", "Rainha Beach promenade": "王后海滩散步", "Cascais railway station": "卡斯凯什火车站",
  "Skip the park in rain; recheck museum opening before departure": "下雨则跳过公园；出发前复核博物馆开放情况",
  "Skip the garden and take an indoor café break": "跳过花园，改到室内咖啡馆休息",
  bookable: "可预约", walk_in: "现场前往", needs_recheck: "历史待复核"
};
const $ = (id) => document.getElementById(id);
const state = { data: null, source: "demo", selectedDate: null, selectedItem: null, map: null, mapReady: false, markers: [], bridge: null, candidate: null, providerLabel: null, canPropose: false, tripPath: null, version: null, syncError: null, externalUpdate: false, proposal: null, busy: false };
function label(value) { return state.data?.trip?.demo ? DEMO_LABELS[value] || value : value; }
function isHistoricalDemo() { return state.source === "demo" && state.data?.trip?.demo_kind === "historical"; }
function itemTime(item) { return item.start ? `${item.start}${item.end ? ` — ${item.end}` : ""}` : item.time_text || "时间待补"; }

function toast(message) {
  const node = $("toast");
  node.textContent = message;
  node.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { node.hidden = true; }, 4800);
}

function dateLabel(value) {
  const date = new Date(`${value}T12:00:00`);
  return new Intl.DateTimeFormat("zh-CN", { month: "long", day: "numeric" }).format(date);
}

function items(day) {
  return (day?.items || []).map((item, index) => typeof item === "string" ? { id: `legacy-${index}`, name: item } : item);
}

function dayColor(index) { return COLORS[index % COLORS.length]; }
function point(item) { return Number.isFinite(item.lat) && Number.isFinite(item.lon); }
function dayAt(data, date) { return data?.days?.find((day) => day.date === date); }
function activeData() {
  if (!state.proposal) return state.data;
  const copy = structuredClone(state.data);
  copy.days = copy.days.map((day) => day.date === state.proposal.date ? state.proposal.after : day);
  return copy;
}

function setStatus(message, action = "了解连接方式") {
  $("status-copy").textContent = message;
  $("status-action").firstChild.textContent = `${action} `;
}

function renderHeader() {
  const trip = state.data.trip || {};
  $("trip-title").textContent = trip.title || "未命名旅程";
  $("trip-meta").textContent = `${trip.start_date || "日期待补"} — ${trip.end_date || "日期待补"}  ·  ${state.data.days.length} 天  ·  ${trip.travelers || "?"} 人`;
  $("data-badge").textContent = state.source === "demo" ? (isHistoricalDemo() ? "历史案例回放" : "虚构示例") : state.source === "bridge" ? "本地真实行程" : "浏览器导入";
  const connected = state.source === "bridge";
  $("connect-button").classList.toggle("connected", connected);
  $("connection-label").textContent = connected ? `已连接 ${state.providerLabel || "本机代理"}` : "连接本机";
  if (state.proposal) setStatus("正在预览修改提案；地图与日程只是预览，尚未写入 trip.json。", "查看提案");
  else if (state.externalUpdate) setStatus("本机代理已修改行程，地图与日程已同步；请核对固定预约、票务和路线变化。", "查看行程");
  else if (connected) setStatus(state.canPropose ? `已连接 ${state.providerLabel || "本机代理"}。网页操作会先生成提案，只有确认后才修改本地 trip.json。` : "已连接本机行程文件。让装有 Skill 的代理保存 trip.json，工作台会自动刷新。", "连接说明");
  else if (state.source === "import") setStatus("当前行程只在浏览器标签页中。可复制修改要求交给已安装 Skill 的代理，完成后重新导入。", "使用说明");
  else setStatus(isHistoricalDemo() ? "这是已过去的巴黎攻略脱敏回放，不代表已出票或当前可订。Day 2 可体验模拟修改。" : "你正在浏览虚构示例。可导入代理生成的行程；Day 2 可体验模拟修改。", "了解使用方式");
  $("generate-button").hidden = connected && !state.canPropose;
  $("generator-note").textContent = connected ? (state.canPropose ? `当前由 ${state.providerLabel || "本机代理"} 生成真实提案。` : "复制要求给已安装 Skill 的本机代理；它保存同一份 trip.json 后，地图与日程会自动刷新。") : "其他代理：下载当前 JSON、复制要求交给已安装 Skill 的代理，完成后重新导入；浏览器不调用模型。";
}

function renderTabs(data) {
  const root = $("day-tabs");
  root.replaceChildren();
  const overview = document.createElement("button");
  overview.type = "button";
  overview.className = `day-tab overview-tab${state.selectedDate ? "" : " active"}`;
  overview.textContent = "全程";
  overview.setAttribute("role", "tab");
  overview.setAttribute("aria-selected", String(!state.selectedDate));
  overview.addEventListener("click", () => selectDay(null));
  root.append(overview);
  data.days.forEach((day, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `day-tab${state.selectedDate === day.date ? " active" : ""}`;
    button.style.setProperty("--day-color", dayColor(index));
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", String(state.selectedDate === day.date));
    const number = document.createElement("strong");
    number.textContent = String(index + 1).padStart(2, "0");
    const dot = document.createElement("i");
    dot.className = "day-dot";
    const small = document.createElement("small");
    small.textContent = dateLabel(day.date);
    button.append(number, dot, small);
    button.addEventListener("click", () => selectDay(day.date));
    root.append(button);
  });
}

function bookingFor(item, data) {
  if (!item.booking_id) return null;
  return data.bookings?.find((booking) => booking.id === item.booking_id) || null;
}

function safeExternalLink(url, labelText) {
  try {
    const parsed = new URL(url);
    if (!["https:", "http:"].includes(parsed.protocol)) return null;
    const link = document.createElement("a");
    link.href = parsed.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = `${labelText} ↗`;
    return link;
  } catch { return null; }
}

function renderOverview(data) {
  $("detail-kicker").textContent = "JOURNEY OVERVIEW / 全程";
  $("detail-title").textContent = "旅程总览";
  $("detail-subtitle").textContent = "点选一天，在地图与时间轴之间深入查看。";
  $("overview-panel").hidden = false;
  $("day-panel").hidden = true;
  $("stat-days").textContent = data.days.length;
  $("stat-stops").textContent = data.days.reduce((sum, day) => sum + items(day).filter(point).length, 0);
  $("stat-anchors").textContent = (data.anchors || []).filter((anchor) => anchor.rigidity === "hard").length;
  const root = $("overview-days");
  root.replaceChildren();
  data.days.forEach((day, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "overview-day";
    button.style.setProperty("--day-color", dayColor(index));
    const number = document.createElement("b"); number.textContent = String(index + 1).padStart(2, "0");
    const copy = document.createElement("div");
    const title = document.createElement("strong"); title.textContent = label(day.title || day.outcome || day.base || `Day ${index + 1}`);
    const sub = document.createElement("small"); sub.textContent = `${dateLabel(day.date)} · ${label(day.base || "地点待补")} · ${items(day).length} 项`;
    copy.append(title, sub);
    const arrow = document.createElement("span"); arrow.textContent = "↗";
    button.append(number, copy, arrow);
    button.addEventListener("click", () => selectDay(day.date));
    root.append(button);
  });
}

function renderDay(data, day) {
  const index = data.days.findIndex((candidate) => candidate.date === day.date);
  $("detail-kicker").textContent = `DAY ${String(index + 1).padStart(2, "0")} / ${dateLabel(day.date)}`;
  $("detail-title").textContent = label(day.title || day.outcome || `${day.base || "旅程"}的一天`);
  $("detail-subtitle").textContent = label(day.outcome || day.primary_outcome || "按时间顺序查看当天安排。");
  $("overview-panel").hidden = true;
  $("day-panel").hidden = false;
  $("day-base").textContent = label(day.base || "地点待补");
  $("day-count").textContent = `${items(day).length} 项安排`;
  const root = $("timeline");
  root.replaceChildren();
  const entries = items(day);
  entries.forEach((item) => {
    const row = document.createElement("li");
    row.style.setProperty("--day-color", dayColor(index));
    const button = document.createElement("button");
    button.type = "button";
    button.className = `stop-button${state.selectedItem === item.id ? " selected" : ""}`;
    const icon = document.createElement("span"); icon.className = "stop-icon"; icon.innerHTML = POI_ICONS[poiIconKey(item)];
    const time = document.createElement("span"); time.className = "stop-time"; time.textContent = itemTime(item);
    const title = document.createElement("strong"); title.textContent = label(item.name || "未命名项目");
    if (item.rigidity === "hard" || item.anchor_id && (data.anchors || []).some((anchor) => anchor.id === item.anchor_id && anchor.rigidity === "hard")) {
      const lock = document.createElement("span"); lock.className = "lock"; lock.textContent = "🔒 固定"; title.append(lock);
    }
    const note = document.createElement("small"); note.textContent = item.note || (point(item) ? "点击地图可查看位置" : "位置未核实 / 不显示地图点");
    button.append(icon, time, title, note);
    button.addEventListener("click", () => { state.selectedItem = item.id; render(); focusItem(item); });
    row.append(button); root.append(row);
  });
  const bookings = (data.bookings || []).filter((booking) => booking.intended_date === day.date);
  const bookingBox = $("booking-box"); bookingBox.replaceChildren();
  const caption = document.createElement("b"); caption.textContent = "预约与票务"; bookingBox.append(caption);
  const detail = document.createElement("span");
  detail.textContent = bookings.length ? bookings.map((booking) => `${label(booking.item || booking.id)} · ${label(booking.status || "待核实")}`).join("；") : "没有已记录的预约；这不代表所有地点都无需预约。";
  bookingBox.append(detail);
  $("fallback-box").hidden = !day.weather_fallback;
  $("fallback-box").textContent = day.weather_fallback ? `雨天或中断：${label(day.weather_fallback)}` : "";
  $("assistant-context").textContent = `${dateLabel(day.date)} · ${label(day.base || "旅程")}`;
}

function boardNode(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = value;
  return node;
}

function ticketEntries(data, day = null) {
  if (data.planning_checklist?.length) return day ? data.planning_checklist.filter((entry) => entry.date === day.date) : data.planning_checklist;
  const bookings = data.bookings || [];
  return (day ? bookings.filter((entry) => entry.intended_date === day.date) : bookings).map((entry) => ({
    name: entry.item || entry.id, date: entry.intended_date, action: entry.note || (entry.status === "walk_in" ? "现场前往；请核对营业情况。" : "请核对票面与官方入口。"),
    url: entry.source_url, status: entry.status
  }));
}

function ticketCard(entry) {
  const card = boardNode("article", "board-ticket");
  const top = boardNode("div", "ticket-top");
  top.append(boardNode("span", "ticket-date", entry.date ? dateLabel(entry.date) : entry.when || "待确认"));
  top.append(boardNode("span", "ticket-status", isHistoricalDemo() ? "历史待复核" : label(entry.status || "待核实")));
  card.append(top, boardNode("h4", "", label(entry.name || "未命名项目")), boardNode("p", "", label(entry.action || "请核对官方入口。")));
  const link = safeExternalLink(entry.url, "查看官方入口"); if (link) card.append(link);
  return card;
}

function renderBoardOverview(data) {
  $("board-title").textContent = "全程规划画布";
  $("board-subtitle").textContent = "先看五天的路线节奏，再看需要逐项核对的票务与交通。";
  $("board-context").textContent = `${data.days.length} 天 · ${ticketEntries(data).length} 项待办`;
  const root = $("board-content"); root.replaceChildren();
  const header = boardNode("div", "board-section-heading");
  header.append(boardNode("span", "", "01 / 每日路线"), boardNode("small", "", "点击日卡，同步进入地图与当天执行看板"));
  root.append(header);
  const strip = boardNode("div", "board-day-strip");
  data.days.forEach((day, index) => {
    const card = boardNode("button", "board-day-card"); card.type = "button";
    card.style.setProperty("--day-color", dayColor(index));
    const top = boardNode("div", "board-day-top");
    top.append(boardNode("b", "", `DAY ${String(index + 1).padStart(2, "0")}`), boardNode("span", "", dateLabel(day.date)));
    const title = boardNode("strong", "", label(day.title || day.outcome || day.base || `Day ${index + 1}`));
    const description = day.primary_outcome || day.outcome;
    const titleSource = day.title || day.outcome || day.base;
    const outcome = boardNode("p", "", description && label(description) !== label(titleSource) ? label(description) : "点击查看地图、时间轴与当天执行看板。");
    const foot = boardNode("div", "board-day-foot");
    foot.append(boardNode("span", "", `${items(day).length} 项安排 · ${day.pace === "high" ? "偏高强度" : day.pace === "low" ? "轻松" : "中等节奏"}`), boardNode("span", "", "↗"));
    card.append(top, title, outcome, foot);
    card.addEventListener("click", () => { selectDay(day.date); $("workspace").scrollIntoView({ behavior: "smooth", block: "start" }); });
    strip.append(card);
  });
  root.append(strip);
  const entries = ticketEntries(data);
  if (!entries.length) return;
  const bookingHead = boardNode("div", "board-section-heading booking-heading");
  bookingHead.append(boardNode("span", "", "02 / 订票与复核节点"), boardNode("small", "", isHistoricalDemo() ? "历史计划，不代表已经出票或现在可订" : "以下状态以行程数据为准"));
  const grid = boardNode("div", "board-ticket-grid"); entries.forEach((entry) => grid.append(ticketCard(entry)));
  root.append(bookingHead, grid);
}

function renderBoardDay(data, day) {
  const index = data.days.indexOf(day);
  $("board-title").textContent = `Day ${index + 1} · ${label(day.title || day.base || "当天路线")}`;
  $("board-subtitle").textContent = label(day.primary_outcome || day.outcome || "按地图与时间轴执行当天计划。 ");
  $("board-context").textContent = `${dateLabel(day.date)} · ${label(day.base || "地点待补")}`;
  const root = $("board-content"); root.replaceChildren();
  const flowHead = boardNode("div", "board-section-heading");
  flowHead.append(boardNode("span", "", "01 / 路线节奏"), boardNode("small", "", "点击节点，地图定位到对应地标"));
  const flow = boardNode("div", "board-route-flow");
  items(day).forEach((item, stopIndex) => {
    const card = boardNode("button", `board-flow-stop${state.selectedItem === item.id ? " active" : ""}`); card.type = "button";
    const glyph = boardNode("span", "board-flow-glyph"); glyph.innerHTML = POI_ICONS[poiIconKey(item)];
    const meta = boardNode("span", "board-flow-meta", `${String(stopIndex + 1).padStart(2, "0")}  ·  ${itemTime(item)}`);
    const title = boardNode("strong", "", label(item.name || "未命名项目"));
    card.append(glyph, meta, title);
    if (item.rigidity === "hard") card.append(boardNode("small", "board-flow-hard", "固定安排"));
    card.addEventListener("click", () => { state.selectedItem = item.id; render(); focusItem(item); if (point(item)) $("map-frame").scrollIntoView({ behavior: "smooth", block: "center" }); });
    flow.append(card);
  });
  root.append(flowHead, flow);
  const anchors = (data.anchors || []).filter((anchor) => day.anchor_ids?.includes(anchor.id));
  const decision = boardNode("div", "board-decision-strip");
  [["必须保护", anchors.length ? anchors.map((anchor) => label(anchor.name || anchor.title || anchor.id)).join(" · ") : label(day.primary_outcome || "当天主线")], ["先删什么", label(day.first_cut || "尚未指定")], ["雨天 / 中断", label(day.weather_fallback || "尚未指定")]].forEach(([title, copy], i) => {
    const item = boardNode("div", `board-decision decision-${i + 1}`);
    item.append(boardNode("span", "", title), boardNode("strong", "", copy)); decision.append(item);
  });
  root.append(decision);
  const grid = boardNode("div", "board-action-grid");
  const guide = day.guide || {};
  [["01", "出发前确认", "before", "◌"], ["02", "交通与动线", "transport", "↗"], ["03", "吃饭与休息", "food", "◕"], ["04", "临场取舍", "decision", "↪"]].forEach(([number, title, key, glyph]) => {
    const card = boardNode("article", `board-action action-${key}`);
    const badge = boardNode("div", "board-action-badge"); badge.append(boardNode("span", "", number), boardNode("b", "", glyph));
    card.append(badge, boardNode("h3", "", title), boardNode("p", "", guide[key] ? label(guide[key]) : "这项执行信息尚未记录。"));
    grid.append(card);
  });
  root.append(grid);
  const tickets = ticketEntries(data, day);
  if (tickets.length) {
    const ticketHead = boardNode("div", "board-section-heading booking-heading");
    ticketHead.append(boardNode("span", "", "02 / 当天票券与预约"), boardNode("small", "", isHistoricalDemo() ? "所有链接需按新的出行日期重新核对" : "以真实确认邮件或二维码为准"));
    const ticketGrid = boardNode("div", "board-ticket-grid"); tickets.forEach((entry) => ticketGrid.append(ticketCard(entry)));
    root.append(ticketHead, ticketGrid);
  }
  if (guide.links?.length) {
    const sources = boardNode("div", "board-source-dock"); sources.append(boardNode("span", "", "原攻略相关入口"));
    guide.links.forEach((entry) => { const link = safeExternalLink(entry.url, entry.label); if (link) sources.append(link); });
    root.append(sources);
  }
}

function renderBoard(data, day) { if (day) renderBoardDay(data, day); else renderBoardOverview(data); }

function renderLegend(data) {
  const root = $("map-legend"); root.replaceChildren();
  data.days.forEach((day, index) => {
    const label = document.createElement("span");
    const dot = document.createElement("i"); dot.style.background = dayColor(index);
    label.append(dot, document.createTextNode(`Day ${index + 1}`)); root.append(label);
  });
}

function renderMapEmpty(data) {
  const day = state.selectedDate ? dayAt(data, state.selectedDate) : null;
  const empty = day && !items(day).some(point);
  $("map-empty").hidden = !empty;
  $("map-frame").classList.toggle("has-empty", Boolean(empty));
  if (!empty) return;
  const index = data.days.indexOf(day) + 1;
  $("map-empty-kicker").textContent = `DAY ${String(index).padStart(2, "0")} / ${label(day.base || "地点待补")}`;
  $("map-empty-title").textContent = label(day.title || day.outcome || "这一天的地图点待补充");
  const root = $("map-empty-items"); root.replaceChildren();
  items(day).forEach((item) => {
    const chip = document.createElement("span");
    chip.innerHTML = POI_ICONS[poiIconKey(item)];
    chip.append(document.createTextNode(label(item.name || "未命名项目")));
    root.append(chip);
  });
}

function renderMap(data) {
  if (!state.mapReady) return;
  state.markers.forEach((marker) => marker.remove()); state.markers = [];
  const lines = [];
  const bounds = new maplibregl.LngLatBounds();
  data.days.forEach((day, index) => {
    if (state.selectedDate && day.date !== state.selectedDate) return;
    const dayItems = items(day);
    const points = dayItems.filter(point);
    if (!state.selectedDate) {
      points.forEach((item) => bounds.extend([item.lon, item.lat]));
      const representative = points[0];
      if (representative) {
        const element = document.createElement("button");
        element.type = "button";
        element.className = "map-day-pin";
        element.style.setProperty("--day-color", dayColor(index));
        element.innerHTML = `<span>DAY</span><strong>${String(index + 1).padStart(2, "0")}</strong>`;
        const name = document.createElement("span"); name.className = "map-day-label"; name.textContent = label(day.title || day.outcome || day.base);
        element.append(name);
        element.title = `${dateLabel(day.date)} · ${name.textContent}`;
        element.setAttribute("aria-label", `进入 Day ${index + 1}：${name.textContent}`);
        element.addEventListener("click", () => selectDay(day.date));
        state.markers.push(new maplibregl.Marker({ element, anchor: "center" }).setLngLat([representative.lon, representative.lat]).addTo(state.map));
      }
      if (points.length > 1) lines.push({ type: "Feature", properties: { color: dayColor(index) }, geometry: { type: "LineString", coordinates: points.map((item) => [item.lon, item.lat]) } });
      return;
    }
    const centerLon = points.length ? (Math.min(...points.map((item) => item.lon)) + Math.max(...points.map((item) => item.lon))) / 2 : 0;
    points.forEach((item) => {
      bounds.extend([item.lon, item.lat]);
      const element = document.createElement("button");
      element.type = "button";
      element.className = `map-pin${state.selectedDate === day.date && state.selectedItem === item.id ? " selected" : ""}${item.lon > centerLon ? " label-left" : ""}`;
      element.style.setProperty("--day-color", dayColor(index));
      const emblem = document.createElement("span"); emblem.className = "map-pin-emblem"; emblem.innerHTML = POI_ICONS[poiIconKey(item)];
      const number = document.createElement("span"); number.className = "map-pin-number"; number.textContent = String(dayItems.indexOf(item) + 1).padStart(2, "0");
      const name = document.createElement("span"); name.className = "map-pin-label"; name.textContent = label(item.name);
      element.append(emblem, number, name);
      element.title = `${dateLabel(day.date)} · ${label(item.name)}`;
      element.setAttribute("aria-label", element.title);
      element.addEventListener("click", () => { state.selectedDate = day.date; state.selectedItem = item.id; render(); focusItem(item); });
      state.markers.push(new maplibregl.Marker({ element, anchor: "bottom", offset: [0, -7] }).setLngLat([item.lon, item.lat]).addTo(state.map));
    });
    if (points.length > 1) lines.push({ type: "Feature", properties: { color: dayColor(index) }, geometry: { type: "LineString", coordinates: points.map((item) => [item.lon, item.lat]) } });
  });
  state.map.getSource("route-lines").setData({ type: "FeatureCollection", features: lines });
  if (!bounds.isEmpty()) {
    if (bounds.getNorth() === bounds.getSouth() && bounds.getEast() === bounds.getWest()) state.map.flyTo({ center: bounds.getCenter(), zoom: 13, duration: 650 });
    else state.map.fitBounds(bounds, { padding: { top: 80, right: 80, bottom: 90, left: 80 }, maxZoom: 14, duration: 650 });
  } else if (state.selectedDate) {
    const selectedDay = dayAt(data, state.selectedDate);
    const knownBasePoint = data.days.filter((day) => day.base === selectedDay.base).flatMap(items).find(point);
    if (knownBasePoint) state.map.flyTo({ center: [knownBasePoint.lon, knownBasePoint.lat], zoom: 12, duration: 650 });
  }
}

function focusItem(item) {
  if (state.mapReady && point(item)) state.map.flyTo({ center: [item.lon, item.lat], zoom: 14.5, duration: 600 });
}

function render() {
  if (!state.data) return;
  const data = activeData();
  renderHeader(); renderTabs(data); renderLegend(data);
  const day = state.selectedDate ? dayAt(data, state.selectedDate) : null;
  if (day) {
    renderDay(data, day);
    $("map-title").textContent = `Day ${data.days.indexOf(day) + 1} · ${label(day.base || "当日地图")}`;
    $("map-location-kicker").textContent = `DAY ${String(data.days.indexOf(day) + 1).padStart(2, "0")} · ${dateLabel(day.date)}`;
    $("map-location-title").textContent = label(day.title || day.outcome || day.base || "当天路线");
    $("map-location-note").textContent = state.proposal?.date === day.date ? "修改提案预览 · 尚未应用" : `${items(day).filter(point).length} 个已定位站点`;
  } else {
    renderOverview(data);
    $("map-title").textContent = "全程概览";
    $("map-location-kicker").textContent = "ALL DAYS / 全程";
    $("map-location-title").textContent = "整段旅程，一眼看清";
    $("map-location-note").textContent = state.proposal ? "含尚未应用的修改预览" : "点 Day 圆章或右侧列表，展开当天路线。";
    $("assistant-context").textContent = "全程旅程";
  }
  renderMapEmpty(data);
  renderMap(data);
  renderBoard(data, day);
}

function selectDay(date) {
  state.selectedDate = date; state.selectedItem = null;
  render();
}

function initMap() {
  if (!window.maplibregl) { $("map-fallback").hidden = false; return; }
  try {
    state.map = new maplibregl.Map({ container: "map", style: "https://tiles.openfreemap.org/styles/liberty", center: [-9.2, 38.7], zoom: 10, attributionControl: true });
    state.map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    state.map.on("load", () => {
      state.map.addSource("route-lines", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      state.map.addLayer({ id: "route-lines", type: "line", source: "route-lines", paint: { "line-color": ["get", "color"], "line-width": 4, "line-opacity": .85, "line-dasharray": [1, 1] } });
      state.mapReady = true; renderMap(activeData());
    });
    state.map.on("error", () => { if (!state.mapReady) $("map-fallback").hidden = false; });
  } catch { $("map-fallback").hidden = false; }
}

function openDrawer() {
  $("assistant-drawer").classList.add("open"); $("assistant-drawer").setAttribute("aria-hidden", "false");
  $("drawer-backdrop").hidden = false; $("assistant-fab").setAttribute("aria-expanded", "true");
  $("drawer-close").focus();
}
function closeDrawer() {
  $("assistant-drawer").classList.remove("open"); $("assistant-drawer").setAttribute("aria-hidden", "true");
  $("drawer-backdrop").hidden = true; $("assistant-fab").setAttribute("aria-expanded", "false");
  $("assistant-fab").focus();
}

function demoProposal(day) {
  if (isHistoricalDemo()) {
    const after = structuredClone(day);
    after.items = items(day).filter((item) => item.id !== "rodin");
    after.items.unshift({ id: "rest-morning", name: "上午放慢节奏 · 咖啡与休息", start: "10:00", end: "10:45", rigidity: "optional", note: "示意调整；未指定地点，不绘制地图点" });
    after.title = "左岸艺术 · 轻松版";
    after.primary_outcome = "保留13:00奥赛，上午缩减一馆";
    after.first_cut = "特罗卡德罗看铁塔闪灯";
    if (after.guide) {
      after.guide.before = "上午改为10:00—10:45休息；仍须12:40到奥赛安检，保护13:00时段。";
      after.guide.transport = "休息后前往荣军院，再步行到奥赛；这只是路线模拟，交通与管制未重新核验。";
      after.guide.decision = "迟到时可再删荣军院，不能压缩奥赛到场缓冲；下雨或疲劳取消铁塔夜景。";
    }
    return { summary: "示意：删去罗丹美术馆，上午留休息；荣军院与13:00奥赛保持原时段。", day: after, warnings: ["这是历史案例的本地模拟，不代表真实改票或重新核验了开放情况。"] };
  }
  const after = structuredClone(day);
  after.items = items(day).filter((item) => !["garden", "free-afternoon"].includes(item.id));
  after.items.splice(1, 0, { id: "free-afternoon", name: "自由午后 · 咖啡与休息", start: "12:30", end: "15:00", rigidity: "optional", note: "可随体力调整；尚未指定地点，不在地图上虚构点位。" });
  after.outcome = "保留已预约的画廊，午后留出充足休息时间";
  after.first_cut = "自由午后 · 咖啡与休息";
  return { summary: "保留 10:00 的画廊入场；去掉固定花园行程，午后改为可自行决定的休息时段。", day: after, warnings: ["这是虚构示例的模拟提案，没有查询真实营业时间或票务。"] };
}

function diffRows(before, after) {
  const oldItems = items(before), newItems = items(after);
  const oldById = new Map(oldItems.map((item) => [item.id, item]));
  const newById = new Map(newItems.map((item) => [item.id, item]));
  const rows = [];
  oldItems.forEach((item) => {
    if (!newById.has(item.id)) rows.push({ type: "removed", text: `${item.start || "—"} · ${label(item.name)}` });
    else if (JSON.stringify(item) !== JSON.stringify(newById.get(item.id))) rows.push({ type: "removed", text: `${item.start || "—"} · ${label(item.name)}（原安排）` });
    else if (item.rigidity === "hard") rows.push({ type: "kept", text: `${item.start || "—"} · ${label(item.name)}（固定预约保留）` });
  });
  newItems.forEach((item) => {
    if (!oldById.has(item.id) || JSON.stringify(item) !== JSON.stringify(oldById.get(item.id))) rows.push({ type: "added", text: `${item.start || "—"} · ${label(item.name)}` });
  });
  return rows.length ? rows : [{ type: "kept", text: "站点未变化；请核对说明和风险提示。" }];
}

function showProposal(result, before, proposalId = null) {
  state.proposal = { date: before.date, after: result.day, before, id: proposalId, summary: result.summary, warnings: result.warnings || [] };
  $("proposal-panel").hidden = false;
  $("proposal-title").textContent = `${dateLabel(before.date)} 的调整`;
  $("proposal-summary").textContent = result.summary;
  const diff = $("proposal-diff"); diff.replaceChildren();
  diffRows(before, result.day).forEach((row) => {
    const node = document.createElement("div"); node.className = `diff-row ${row.type}`;
    const mark = document.createElement("span"); mark.textContent = row.type === "added" ? "+" : row.type === "removed" ? "−" : "=";
    const copy = document.createElement("span"); copy.textContent = row.text;
    node.append(mark, copy); diff.append(node);
  });
  $("proposal-warnings").hidden = !state.proposal.warnings.length;
  $("proposal-warnings").textContent = state.proposal.warnings.join("；");
  $("apply-button").textContent = state.source === "bridge" ? "确认并写入本地行程 →" : "应用到当前示例 →";
  render();
  $("proposal-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function api(path, method = "GET", body = undefined) {
  const bridge = state.bridge || state.candidate;
  if (!bridge) throw new Error("缺少本机连接信息；请先启动 bridge/server.py 并使用它给出的链接。 ");
  const response = await fetch(`http://127.0.0.1:${bridge.port}/api/${path}`, { method, headers: { "Content-Type": "application/json", "X-Trip-Token": bridge.token }, body: body ? JSON.stringify(body) : undefined, cache: "no-store" });
  const value = await response.json();
  if (!response.ok) throw new Error(value.details?.length ? `${value.error}：${value.details.join("；")}` : value.error || `HTTP ${response.status}`);
  return value;
}

async function connect() {
  if (!state.candidate && !state.bridge) { toast("先运行本机桥接，再使用它打印的专属链接打开此页面。"); return; }
  $("connect-confirm").disabled = true;
  try {
    const health = await api("health");
    if (!health.provider_available && !health.codex_available) throw new Error(`本机未找到 ${health.provider_label || "所选代理 CLI"}，请先安装或配置 --cli-bin`);
    const result = await api("trip");
    if (!result.trip?.trip || !Array.isArray(result.trip.days)) throw new Error("本机行程格式不完整");
    if (result.validation_errors?.length) throw new Error(`本机行程未通过校验：${result.validation_errors[0]}`);
    state.bridge = state.candidate || state.bridge;
    state.providerLabel = health.provider_label || "本机代理";
    state.canPropose = health.can_propose ?? Boolean(health.codex_available);
    state.tripPath = health.trip_path || null;
    state.version = result.version;
    state.syncError = null;
    state.externalUpdate = false;
    state.data = result.trip; state.source = "bridge"; state.selectedDate = null; state.proposal = null;
    $("connect-dialog").close(); render(); toast(state.canPropose ? `已连接 ${state.providerLabel}。修改前仍会要求你确认。` : "已连接本机行程。代理保存文件后，工作台会自动刷新。");
  } catch (error) { toast(`连接失败：${error.message}`); }
  finally { $("connect-confirm").disabled = false; }
}

async function generate() {
  if (state.busy) return;
  if (!state.selectedDate) { toast("请先选择要调整的某一天。"); return; }
  const request = $("change-request").value.trim();
  if (request.length < 3) { toast("请用至少 3 个字描述想调整的地方。"); return; }
  state.busy = true; $("generate-button").disabled = true; $("proposal-loading").querySelector("strong").textContent = `${state.providerLabel || "代理"} 正在整理修改提案…`; $("proposal-loading").hidden = false; $("proposal-panel").hidden = true;
  try {
    const before = dayAt(state.data, state.selectedDate);
    if (state.source === "bridge" && state.canPropose) {
      const result = await api("propose", "POST", { date: state.selectedDate, request });
      showProposal(result.proposal, result.before, result.proposal_id);
    } else if (state.source === "demo" && state.selectedDate === state.data.days[1]?.date) {
      await new Promise((resolve) => setTimeout(resolve, 650));
      showProposal(demoProposal(before), before);
    } else {
      throw new Error("当前没有连接本机代理。可使用下方 JSON 交接，或启动本机桥接；示例只提供 Day 2 模拟修改。");
    }
  } catch (error) { toast(error.message); }
  finally { state.busy = false; $("generate-button").disabled = false; $("proposal-loading").hidden = true; }
}

async function copyHandoff() {
  if (!state.selectedDate) { toast("请先选择要调整的某一天。"); return; }
  const request = $("change-request").value.trim();
  if (request.length < 3) { toast("请先写下至少 3 个字的修改要求。"); return; }
  const shared = state.source === "bridge" && !state.canPropose && state.tripPath;
  const target = shared ? `请直接修改本机文件 ${state.tripPath}。` : "请修改我提供的 trip.json。";
  const finish = shared ? "保存并校验同一份文件后告诉我；工作台会自动刷新。" : "完成后请给我可下载的完整 trip.json，我会重新导入工作台。";
  const message = `请使用已安装的 plan-and-maintain-trips Skill。${target}只调整 ${state.selectedDate}，要求：${request}\n请保护所有硬预约、固定时间、地点和预订编号；核实会变化的开放与票务信息；更新受影响的清单和说明。不要改 Skill 目录里的示例。${finish}未确认的事实请标注待核实，不要伪造。`;
  try {
    await navigator.clipboard.writeText(message);
    toast(shared ? "已复制要求。交给你的本机 AI 代理；保存同一文件后工作台会自动刷新。" : "已复制要求。请先下载当前行程 JSON，连同要求交给你的 AI 代理；完成后重新导入。");
  } catch { toast("复制失败，请检查浏览器的剪贴板权限。"); }
}

async function applyProposal() {
  if (!state.proposal || state.busy) return;
  state.busy = true; $("apply-button").disabled = true;
  try {
    if (state.source === "bridge") {
      const result = await api("apply", "POST", { proposal_id: state.proposal.id });
      state.data = result.trip;
      state.version = result.version;
      state.externalUpdate = false;
      toast("已写入本地 trip.json；原文件另有 .bak 备份。");
    } else {
      state.data.days = state.data.days.map((day) => day.date === state.proposal.date ? state.proposal.after : day);
      toast("已应用到当前浏览器示例；刷新会恢复原状，可下载 JSON 保存。");
    }
    state.proposal = null; $("proposal-panel").hidden = true; render(); closeDrawer();
  } catch (error) { toast(`未应用：${error.message}`); }
  finally { state.busy = false; $("apply-button").disabled = false; }
}

function downloadTrip() {
  const blob = new Blob([`${JSON.stringify(state.data, null, 2)}\n`], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a"); link.href = url; link.download = `${state.data.trip?.id || "trip"}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function syncTrip() {
  if (state.source !== "bridge" || state.busy || state.proposal || document.visibilityState === "hidden") return;
  try {
    const result = await api("trip");
    if (result.validation_errors?.length) throw new Error(`文件未通过校验：${result.validation_errors[0]}`);
    if (result.version !== state.version) {
      state.data = result.trip;
      state.version = result.version;
      state.externalUpdate = true;
      if (!dayAt(state.data, state.selectedDate)) state.selectedDate = null;
      state.selectedItem = null;
      render();
      toast("本机行程已更新，地图和日程已同步。");
    }
    state.syncError = null;
  } catch (error) {
    if (error.message !== state.syncError) toast(`暂未同步：${error.message}`);
    state.syncError = error.message;
  }
}

function wireEvents() {
  $("connect-button").addEventListener("click", () => $("connect-dialog").showModal());
  $("status-action").addEventListener("click", () => state.proposal ? openDrawer() : $("connect-dialog").showModal());
  $("connect-confirm").addEventListener("click", connect);
  $("import-button").addEventListener("click", () => $("trip-file").click());
  $("trip-file").addEventListener("change", async (event) => {
    const file = event.target.files?.[0]; if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      if (!data.trip || !Array.isArray(data.days) || !data.days.length) throw new Error("文件缺少 trip 或 days");
      state.data = data; state.source = "import"; state.bridge = null; state.candidate = null; state.providerLabel = null; state.canPropose = false; state.tripPath = null; state.version = null; state.syncError = null; state.externalUpdate = false; sessionStorage.removeItem("trip-bridge"); state.selectedDate = null; state.proposal = null;
      render(); toast("已在浏览器中打开行程；没有上传到服务器。");
    } catch (error) { toast(`导入失败：${error.message}`); }
    event.target.value = "";
  });
  $("map-overview").addEventListener("click", () => selectDay(null));
  $("export-button").addEventListener("click", downloadTrip);
  $("assistant-fab").addEventListener("click", openDrawer);
  $("adjust-button").addEventListener("click", openDrawer);
  $("drawer-close").addEventListener("click", closeDrawer);
  $("drawer-backdrop").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && $("assistant-drawer").classList.contains("open")) closeDrawer(); });
  $("relax-suggestion").addEventListener("click", () => { $("change-request").value = "把这一天放松一点，但保留所有已预约项目和固定时间。"; });
  $("rain-suggestion").addEventListener("click", () => { $("change-request").value = "准备雨天替代方案，保留已预约项目和固定时间。"; });
  $("generate-button").addEventListener("click", generate);
  $("handoff-download").addEventListener("click", downloadTrip);
  $("handoff-button").addEventListener("click", copyHandoff);
  $("discard-button").addEventListener("click", () => { state.proposal = null; $("proposal-panel").hidden = true; render(); toast("已放弃提案，原行程没有变化。"); });
  $("apply-button").addEventListener("click", applyProposal);
}

async function boot() {
  wireEvents();
  setInterval(syncTrip, 5000);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") syncTrip(); });
  const hash = new URLSearchParams(location.hash.replace(/^#/, ""));
  const port = Number(hash.get("port")); const token = hash.get("token");
  if (Number.isInteger(port) && port >= 1024 && port <= 65535 && token && token.length >= 32) {
    state.candidate = { port, token };
    sessionStorage.setItem("trip-bridge", JSON.stringify(state.candidate));
    history.replaceState(null, "", location.pathname + location.search);
    setStatus("检测到本机工作台链接。点击「连接本机」并允许浏览器连接本机服务。", "连接本机");
  } else {
    try { state.candidate = JSON.parse(sessionStorage.getItem("trip-bridge") || "null"); }
    catch { sessionStorage.removeItem("trip-bridge"); }
  }
  try {
    const demoFile = new URLSearchParams(location.search).get("demo") === "lisbon" ? "trip.example.json" : "paris.demo.json";
    const response = await fetch(`../assets/${demoFile}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.data = await response.json();
    render(); initMap();
    if (state.candidate) setStatus("检测到本机工作台链接。点击「连接本机」并允许浏览器连接本机服务。", "连接本机");
  } catch (error) {
    $("trip-title").textContent = "暂时无法打开示例";
    setStatus(`示例数据加载失败：${error.message}。可尝试导入自己的 trip.json。`);
  }
}

boot();
