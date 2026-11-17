// Original landmark-inspired pictograms and generic travel symbols; no official venue logos.
const POI_ICONS = Object.freeze({
  louvre: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M4 36h40M7 33 24 8l17 25H7Z M24 8v25M12 26h24M16 20h16M11 33l13-19 13 19"/></svg>',
  tuileries: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 40V23M15 40h18M24 29l-10-7M24 25l10-8M24 22l-5-9M24 22l6-11"/><path d="M10 21c-2-5 1-10 7-10 1-5 5-7 9-5 5-3 11 1 11 6 5 1 7 7 4 11-2 4-7 5-11 3-5 3-10 2-13-1-4 1-6-1-7-4Z"/></svg>',
  orsay: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 38h38M8 38V19l16-8 16 8v19M8 22h32M14 38V28h20v10"/><circle cx="24" cy="19" r="7"/><path d="M24 15v4l3 2"/></svg>',
  chapelle: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M8 40h32M12 40V20L24 7l12 13v20M24 7V3M17 40V24l7-7 7 7v16M24 17v23M17 29h14M20 11l4-5 4 5"/></svg>',
  notredame: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 40h38M8 40V11h10v9h12v-9h10v29M8 17h10M30 17h10M18 40V29a6 6 0 0 1 12 0v11M21 20a3 3 0 1 0 6 0 3 3 0 0 0-6 0ZM12 9V5M36 9V5"/></svg>',
  arc: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M6 41h36M9 38V15h30v23M9 20h30M17 38V29a7 7 0 0 1 14 0v9M14 15V9h20v6M22 9V6h4v3M13 25h3M32 25h3"/></svg>',
  sacrecoeur: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 40h38M9 40V25h30v15M15 25v-8h18v8M19 17a5 5 0 0 1 10 0M24 12V5M19 8h10M14 40v-9h7v9M27 40v-9h7v9M7 25V14h6v11M35 25V14h6v11"/></svg>',
  invalides: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 40h38M8 40V25h32v15M13 25h22M16 25c0-8 3-13 8-13s8 5 8 13M24 12V6M20 8h8M14 31v9M21 31v9M28 31v9M35 31v9"/></svg>',
  eiffel: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M8 42h32M13 42 24 6l11 36M19 24h10M15 34h18M17 42a7 7 0 0 1 14 0M21 15h6M24 6V3"/></svg>',
  versailles: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M4 41h40M7 41V22h34v19M11 22v-8h26v8M16 14V9h16v5M21 9V5h6v4M21 41V29h6v12M11 28h6v7h-6zM31 28h6v7h-6zM7 37h34"/></svg>',
  museum: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 18 24 8l19 10M7 20h34M9 39h30M6 43h36M12 21v17M20 21v17M28 21v17M36 21v17"/></svg>',
  garden: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 41V23M16 41h16M24 31l-9-8M24 26l9-9"/><path d="M10 24c-3-4-1-10 4-11 1-5 6-8 10-6 5-3 11 0 12 5 6 1 8 8 4 12-3 4-8 5-12 2-6 3-11 2-14-1-2 1-3 0-4-1Z"/></svg>',
  food: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M8 27h32M12 27c0-10 5-16 12-16s12 6 12 16M6 33h36M13 39h22M24 11V7"/></svg>',
  rail: '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="10" y="8" width="28" height="28" rx="5"/><path d="M17 17h14M16 25h4M28 25h4M15 36l-5 6M33 36l5 6M14 31h20"/></svg>',
  walk: '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="26" cy="9" r="4"/><path d="m23 16-7 8 8 3 5-7M23 16l7 6 7 1M24 27l-8 13M24 27l9 12M7 42h34"/></svg>',
  landmark: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M6 40h36M10 40V21l14-13 14 13v19M17 40V27h14v13M21 19h6"/></svg>'
});

function poiIconKey(item) {
  if (item.icon && POI_ICONS[item.icon]) return item.icon;
  const name = item.name || "";
  const named = [
    [/louvre|卢浮宫/i, "louvre"], [/tuileries|杜乐丽/i, "tuileries"],
    [/orsay|奥赛/i, "orsay"], [/sainte.chapelle|圣礼拜堂/i, "chapelle"],
    [/notre.dame|巴黎圣母院/i, "notredame"],
    [/凯旋门|arc de triomphe/i, "arc"], [/圣心堂|sacr[eé].c[oœ]ur/i, "sacrecoeur"],
    [/荣军院|invalides/i, "invalides"], [/铁塔|eiffel|trocad[eé]ro/i, "eiffel"],
    [/凡尔赛|versailles|trianon/i, "versailles"]
  ].find(([pattern]) => pattern.test(name));
  if (named) return named[1];
  if (item.meal || /lunch|dinner|breakfast|午餐|晚餐|早餐|餐厅/i.test(name)) return "food";
  if (item.mode_from_previous === "rail" || /train|火车|铁路/i.test(name)) return "rail";
  if (/garden|park|花园|公园/i.test(name)) return "garden";
  if (/gallery|museum|博物馆|美术馆|画廊/i.test(name)) return "museum";
  if (/walk|stroll|promenade|散步|漫步/i.test(name)) return "walk";
  return "landmark";
}
