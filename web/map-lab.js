const PLACES = [
  { id: "louvre", name: "卢浮宫", en: "LOUVRE", category: "艺术地标", note: "馆藏与建筑在同一地点相遇。这里用来比较景点卡片在密集城区中的辨识度。", symbol: "◇", kind: "museum", coordinates: [2.3376, 48.8606] },
  { id: "tuileries", name: "杜乐丽花园", en: "TUILERIES", category: "城市花园", note: "从室内展馆走到户外，适合观察地图上“停留点”与“途经点”的层级。", symbol: "✳", kind: "garden", coordinates: [2.3279, 48.8637] },
  { id: "orsay", name: "奥赛博物馆", en: "MUSÉE D’ORSAY", category: "艺术地标", note: "塞纳河左岸的艺术站点。地图上的跨河连线仅表示顺序，不是推荐道路。", symbol: "◈", kind: "museum", coordinates: [2.3266, 48.8600] },
  { id: "chapelle", name: "圣礼拜堂", en: "SAINTE-CHAPELLE", category: "建筑与历史", note: "位于西岱岛。用它来检验长地名在窄街区中的标注是否清晰。", symbol: "✧", kind: "heritage", coordinates: [2.3448, 48.8554] },
  { id: "notredame", name: "巴黎圣母院", en: "NOTRE-DAME", category: "建筑与历史", note: "地图示意只展示位置，不代表开放、预约或宗教活动安排。", symbol: "♢", kind: "heritage", coordinates: [2.3499, 48.8530] }
];
const STYLES = {
  atlas: { name: "旅行手帐", edition: "A / 旅行手帐", description: "让景点像收藏在旅行册中的一张张小卡片。地名、类别和顺序同时可见，适合全程图与首次浏览。", tradeoff: "信息丰富，但高密度街区需要在缩放时收起部分标签。", map: "positron", route: "#ad634a" },
  wayfinder: { name: "城市寻路", edition: "B / 城市寻路", description: "用清晰编号把地图变成当天的行动索引。标签更轻，留出更多底图细节，适合在路上快速扫读。", tradeoff: "更便于执行，但地点的文化氛围要靠侧栏或点击后的详情补足。", map: "liberty", route: "#187f72" },
  nocturne: { name: "夜色导览", edition: "C / 夜色导览", description: "把城市作为舞台：低亮度底图、柔和发光的地标，适合夜游、演出与带有情绪的旅程展示。", tradeoff: "氛围更强；白天强光和打印场景的易读性不如浅色方案。", map: "dark", route: "#dfb77a" },
  emblem: { name: "地标徽章", edition: "D / 地标徽章", description: "用专属建筑剪影建立地标识别，再以小尺寸名称标签补充。像一套有秩序的城市徽章。", tradeoff: "建筑识别很强，但第一次看到自绘图形的用户仍需要地名辅助。", map: "bright", route: "#9a554c" },
  postcard: { name: "城市邮票", edition: "E / 城市邮票", description: "每个景点像一枚可收藏的旅行邮票：插画、编号与地名并列，尤其适合分享卡片和导出图。", tradeoff: "视觉个性最强，但卡片占地图面积较大，密集区需要智能避让。", map: "positron", route: "#d48351" },
  iconic: { name: "图标寻宝", edition: "F / 图标寻宝", description: "地图默认只展示专属地标图形和序号；点击或聚焦后才展开名称，给城市底图更多呼吸空间。", tradeoff: "地图最清爽，适合手机；但首次浏览要依靠侧栏理解全部站点。", map: "liberty", route: "#337d7f" }
};
const state = { map: null, ready: false, markers: [], theme: "atlas", selected: "louvre" };
const $ = (id) => document.getElementById(id);

function routeFeature() {
  return { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: PLACES.map((place) => place.coordinates) } };
}

function makeMarker(place, index) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `poi-marker ${state.theme} ${place.kind}${state.selected === place.id ? " selected" : ""}`;
  button.setAttribute("aria-label", `${index + 1} · ${place.name} · ${place.category}`);
  const number = document.createElement("span"); number.className = "poi-number"; number.textContent = String(index + 1).padStart(2, "0");
  const emblem = document.createElement("span"); emblem.className = "poi-emblem"; emblem.innerHTML = POI_ICONS[place.id];
  const text = document.createElement("span"); text.className = "poi-copy";
  const name = document.createElement("strong"); name.textContent = place.name;
  const meta = document.createElement("small"); meta.textContent = state.theme === "nocturne" ? place.en : place.category;
  text.append(name, meta); button.append(number, emblem, text);
  button.addEventListener("click", () => selectPlace(place.id, true));
  return button;
}

function renderMarkers() {
  if (!state.ready) return;
  state.markers.forEach((marker) => marker.remove()); state.markers = [];
  PLACES.forEach((place, index) => {
    const element = makeMarker(place, index);
    state.markers.push(new maplibregl.Marker({ element, anchor: "bottom", offset: [0, -8] }).setLngLat(place.coordinates).addTo(state.map));
  });
}

function renderStops() {
  const list = $("stop-list"); list.replaceChildren();
  PLACES.forEach((place, index) => {
    const row = document.createElement("li");
    const button = document.createElement("button"); button.type = "button";
    button.className = `stop-item${state.selected === place.id ? " active" : ""}`;
    button.setAttribute("aria-current", String(state.selected === place.id));
    const number = document.createElement("span"); number.textContent = String(index + 1).padStart(2, "0");
    const text = document.createElement("span");
    const title = document.createElement("strong"); title.textContent = place.name;
    const category = document.createElement("small"); category.textContent = place.category;
    text.append(title, category);
    const arrow = document.createElement("i"); arrow.textContent = "↗";
    button.append(number, text, arrow); button.addEventListener("click", () => selectPlace(place.id, true));
    row.append(button); list.append(row);
  });
}

function selectPlace(id, move) {
  state.selected = id;
  const place = PLACES.find((candidate) => candidate.id === id);
  $("place-name").textContent = place.name;
  $("place-category").textContent = place.category;
  $("place-note").textContent = place.note;
  $("place-symbol").innerHTML = POI_ICONS[place.id];
  renderStops(); renderMarkers();
  if (move && state.ready) state.map.flyTo({ center: place.coordinates, zoom: Math.max(state.map.getZoom(), 13.5), duration: 550, essential: true });
}

function syncRoute() {
  if (!state.map) return;
  if (!state.map.getSource("sample-route")) state.map.addSource("sample-route", { type: "geojson", data: routeFeature() });
  if (!state.map.getLayer("sample-route-halo")) state.map.addLayer({ id: "sample-route-halo", type: "line", source: "sample-route", paint: { "line-color": "#fff9ec", "line-width": 9, "line-opacity": state.theme === "nocturne" ? .12 : .75 } });
  if (!state.map.getLayer("sample-route")) state.map.addLayer({ id: "sample-route", type: "line", source: "sample-route", paint: { "line-color": STYLES[state.theme].route, "line-width": 3.5, "line-opacity": .95, "line-dasharray": [1.4, 1.1] } });
}

function fitRoute() {
  if (!state.ready) return;
  const compact = state.map.getContainer().clientWidth < 600;
  state.map.easeTo({ center: [2.3383, 48.8585], zoom: compact ? 12.2 : 12.9, duration: 550, essential: true });
}

function selectStyle(theme) {
  state.theme = theme;
  document.body.dataset.theme = theme;
  document.querySelectorAll(".choice").forEach((button) => { const active = button.dataset.style === theme; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
  const style = STYLES[theme];
  $("map-edition").textContent = style.edition;
  $("style-index").textContent = `DESIGN ${String(Object.keys(STYLES).indexOf(theme) + 1).padStart(2, "0")} / 06`;
  $("style-name").textContent = style.name;
  $("style-description").textContent = style.description;
  $("style-tradeoff").textContent = style.tradeoff;
  renderMarkers();
  if (state.ready) { state.map.setStyle(`https://tiles.openfreemap.org/styles/${style.map}`); fitRoute(); }
}

function initMap() {
  if (!window.maplibregl) { $("map-fallback").hidden = false; return; }
  try {
    state.map = new maplibregl.Map({ container: "map", style: "https://tiles.openfreemap.org/styles/positron", center: [2.338, 48.8587], zoom: 13.1, attributionControl: true });
    state.map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    state.map.on("style.load", syncRoute);
    state.map.on("load", () => { state.ready = true; renderMarkers(); syncRoute(); fitRoute(); });
    state.map.on("error", () => { if (!state.ready) $("map-fallback").hidden = false; });
  } catch { $("map-fallback").hidden = false; }
}

document.querySelectorAll(".choice").forEach((button) => button.addEventListener("click", () => selectStyle(button.dataset.style)));
document.querySelectorAll(".preview-emblem b, .preview-iconic b").forEach((node) => { node.innerHTML = POI_ICONS.louvre; });
$("fit-route").addEventListener("click", fitRoute);
selectPlace(state.selected, false); initMap();
