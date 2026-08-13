"""Render data/hunting_log.json into index.html: a single sortable,
filterable table of every class hunting log entry, with per-row done
tracking persisted to localStorage.

Run extract_data.py first to produce the JSON this reads.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_JSON = REPO_ROOT / "data" / "hunting_log.json"
OUT_HTML = REPO_ROOT / "index.html"

PAGE_TITLE = "FFXIV Hunt Log Tracker"
STORAGE_KEY = "ffxivHuntLogTrackerDone"
FILTERS_STORAGE_KEY = "ffxivHuntLogTrackerFilters"

CLASS_ORDER = [
    "Gladiator", "Marauder", "Lancer", "Pugilist", "Rogue",
    "Archer", "Conjurer", "Thaumaturge", "Arcanist",
]
GC_ORDER = ["Immortal Flames", "Maelstrom", "Order of the Twin Adder"]
class_idx = {c: i for i, c in enumerate(CLASS_ORDER + GC_ORDER)}

# Badge colors follow the game's own conventions (ffxiv.consolegameswiki.com/wiki/Class):
# role colors for classes (tank/healer/DPS), and each Grand Company's home-city
# color for the company itself and for zones in that city's home region.
CLASS_BADGE = {
    "Gladiator": "tank", "Marauder": "tank",
    "Conjurer": "healer",
    "Lancer": "dps", "Pugilist": "dps", "Rogue": "dps",
    "Archer": "dps", "Thaumaturge": "dps", "Arcanist": "dps",
    "Maelstrom": "maelstrom",
    "Order of the Twin Adder": "adder",
    "Immortal Flames": "flames",
}


def zone_badge(zone):
    if "Shroud" in zone:
        return "adder"
    if "Thanalan" in zone:
        return "flames"
    if "La Noscea" in zone:
        return "maelstrom"
    return "neutral"

rows = json.loads(IN_JSON.read_text())

zones_sorted = sorted(set(r["zone"] for r in rows))

rows.sort(key=lambda r: (
    zones_sorted.index(r["zone"]), class_idx.get(r["class"], 99),
    r["rank"], r["monster"],
))


total_entries = len(rows)
total_zones = len(zones_sorted)

# The table body is populated client-side from data/hunting_log.csv (see the
# fetch() in the inline <script> below) rather than baked into this HTML, so
# CSV_PATH is the only thing that needs to change if the data file moves.
CSV_PATH = "data/hunting_log.csv"

zone_filter_buttons = "\n".join(
    f'<button data-zone="{z}" data-badge="{zone_badge(z)}">{z}</button>' for z in zones_sorted
)

html = f'''<title>{PAGE_TITLE}</title>
<style>
:root {{
  --bg: #eef1ea;
  --surface: #ffffff;
  --surface-2: #e4e8de;
  --ink: #1e2a1e;
  --ink-soft: #52604d;
  --ink-faint: #7c8a76;
  --accent: #9a5f24;
  --accent-soft: #c98a4a;
  --line: #d3d9c9;
  --line-strong: #b9c2ac;
  --focus: #6f8c5a;
  --badge-tank: #3568c9;
  --badge-healer: #2f8f52;
  --badge-dps: #c9463a;
  --font-display: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, 'SF Mono', 'Cascadia Mono', Consolas, monospace;
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #12160f;
    --surface: #1a2016;
    --surface-2: #212a1c;
    --ink: #e7ece0;
    --ink-soft: #a9b6a1;
    --ink-faint: #77836f;
    --accent: #dd9a4e;
    --accent-soft: #b97836;
    --line: #2c3524;
    --line-strong: #3c4732;
    --focus: #9bc17f;
    --badge-tank: #7aa8f2;
    --badge-healer: #5fcf8a;
    --badge-dps: #f0796c;
  }}
}}

:root[data-theme="dark"] {{
  --bg: #12160f;
  --surface: #1a2016;
  --surface-2: #212a1c;
  --ink: #e7ece0;
  --ink-soft: #a9b6a1;
  --ink-faint: #77836f;
  --accent: #dd9a4e;
  --accent-soft: #b97836;
  --line: #2c3524;
  --line-strong: #3c4732;
  --focus: #9bc17f;
  --badge-tank: #7aa8f2;
  --badge-healer: #5fcf8a;
  --badge-dps: #f0796c;
}}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-body);
  line-height: 1.45;
  min-height: 100vh;
}}

.page {{
  max-width: 1040px;
  margin: 0 auto;
  padding: 0 1.5rem 4rem;
}}

header.masthead {{
  padding: 3rem 0 1.75rem;
  border-bottom: 1px solid var(--line-strong);
  margin-bottom: 1.75rem;
}}

.eyebrow {{
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 0.6rem;
}}

h1 {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: clamp(2.1rem, 4.5vw, 2.9rem);
  margin: 0 0 0.5rem;
  text-wrap: balance;
  letter-spacing: -0.01em;
}}

.subhead {{
  color: var(--ink-soft);
  font-size: 1.02rem;
  max-width: 62ch;
  margin: 0 0 0.25rem;
}}

.subhead .note {{
  display: block;
  margin-top: 0.5rem;
  font-size: 0.88rem;
  color: var(--ink-faint);
}}

.controls {{
  position: sticky;
  top: 0;
  z-index: 5;
  background: var(--bg);
  padding: 1rem 0;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.5rem;
}}

.search-row {{
  display: flex;
  gap: 0.6rem;
  margin-bottom: 0.85rem;
}}

#search {{
  flex: 1;
  font-family: var(--font-body);
  font-size: 0.95rem;
  padding: 0.6rem 0.85rem;
  border-radius: 7px;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--ink);
}}

#search:focus-visible, .filter-row button:focus-visible {{
  outline: 2px solid var(--focus);
  outline-offset: 2px;
}}

#search::placeholder {{ color: var(--ink-faint); }}

.filter-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}}

.filter-row button {{
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.03em;
  padding: 0.32rem 0.6rem;
  border-radius: 5px;
  border: 2px solid var(--line-strong);
  background: var(--surface);
  color: var(--ink-soft);
  cursor: pointer;
  white-space: nowrap;
}}

.filter-row button:hover {{ border-color: var(--accent-soft); color: var(--ink); }}

.filter-row button.active {{
  background: var(--accent);
  border-color: var(--accent);
  color: var(--surface);
}}

.filter-row button[data-badge] {{
  --badge-color: var(--ink-faint);
  border-color: color-mix(in srgb, var(--badge-color) 65%, var(--line-strong));
  color: var(--badge-color);
}}

.filter-row button[data-badge="tank"] {{ --badge-color: var(--badge-tank); }}
.filter-row button[data-badge="healer"] {{ --badge-color: var(--badge-healer); }}
.filter-row button[data-badge="dps"] {{ --badge-color: var(--badge-dps); }}
.filter-row button[data-badge="maelstrom"] {{ --badge-color: var(--badge-tank); }}
.filter-row button[data-badge="adder"] {{ --badge-color: var(--badge-healer); }}
.filter-row button[data-badge="flames"] {{ --badge-color: var(--accent); }}

.filter-row button[data-badge]:hover {{ border-color: var(--badge-color); color: var(--ink); }}

.filter-row button[data-badge].active {{
  background: var(--badge-color);
  border-color: var(--badge-color);
  color: var(--surface);
}}

.filters-toggle {{
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  letter-spacing: 0.03em;
  padding: 0.6rem 0.85rem;
  border-radius: 7px;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--ink-soft);
  cursor: pointer;
  white-space: nowrap;
}}

.filters-toggle:hover {{ border-color: var(--accent-soft); color: var(--ink); }}

.filters-count {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--accent);
}}

.filters-toggle .chevron {{
  display: inline-block;
  font-size: 1.1em;
  line-height: 1;
  transition: transform 0.12s ease;
}}

.filters-toggle[aria-expanded="true"] .chevron {{ transform: rotate(180deg); }}

.filters-body {{
  display: none;
}}

.filters-body.open {{
  display: block;
}}

.table-wrap {{
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}}

table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  min-width: 600px;
}}

thead th {{
  text-align: left;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ink-faint);
  padding: 0.55rem 0.8rem;
  border-bottom: 1px solid var(--line-strong);
  background: var(--surface-2);
}}

thead th.sortable {{ cursor: pointer; user-select: none; }}
thead th.sortable:hover {{ color: var(--ink); }}

.sort-arrow {{
  display: inline-block;
  width: 0.9em;
  color: var(--accent);
}}

tbody td {{
  padding: 0.5rem 0.8rem;
  border-bottom: 1px solid var(--line);
  vertical-align: baseline;
}}

tbody tr:last-child td {{ border-bottom: none; }}

tbody tr.hidden {{ display: none; }}

.col-zone {{ min-width: 9rem; }}

.col-rank {{
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  color: var(--ink-soft);
  width: 3.5rem;
}}

.col-monster {{ font-weight: 500; }}

.col-area {{ color: var(--ink-soft); }}

.col-done {{
  width: 2.4rem;
  text-align: center;
}}

.done-check {{
  width: 1.05rem;
  height: 1.05rem;
  accent-color: var(--accent);
  cursor: pointer;
  vertical-align: middle;
}}

tbody tr.done td {{
  color: var(--ink-faint);
}}

tbody tr.done .col-monster,
tbody tr.done .class-tag {{
  text-decoration: line-through;
  text-decoration-color: var(--ink-faint);
}}

tbody tr.done .badge {{ opacity: 0.55; }}

tbody tr.done.hide-done {{ display: none; }}

.sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}}

.progress-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
}}

.progress-text {{
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--ink-soft);
  white-space: nowrap;
}}

.progress-bar {{
  flex: 1;
  height: 5px;
  background: var(--surface-2);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--line);
}}

.progress-fill {{
  height: 100%;
  background: var(--accent);
  width: 0%;
}}

.hide-toggle {{
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--ink-soft);
  cursor: pointer;
  white-space: nowrap;
  user-select: none;
}}

.hide-toggle input {{
  accent-color: var(--accent);
  cursor: pointer;
}}

.badge {{
  display: inline-flex;
  align-items: center;
  padding: 0.22rem 0.5rem;
  border-radius: 5px;
  border: 2px solid;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.03em;
  white-space: nowrap;
  --badge-color: var(--ink-faint);
  color: var(--badge-color);
  border-color: color-mix(in srgb, var(--badge-color) 65%, var(--line-strong));
  background: var(--surface);
}}

.badge-tank {{ --badge-color: var(--badge-tank); }}
.badge-healer {{ --badge-color: var(--badge-healer); }}
.badge-dps {{ --badge-color: var(--badge-dps); }}
.badge-maelstrom {{ --badge-color: var(--badge-tank); }}
.badge-adder {{ --badge-color: var(--badge-healer); }}
.badge-flames {{ --badge-color: var(--accent); }}

.zone-badges {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}}

#empty-state {{
  display: none;
  padding: 2.5rem 0;
  text-align: center;
  color: var(--ink-faint);
  font-family: var(--font-display);
  font-size: 1.05rem;
}}

#empty-state.show {{ display: block; }}

footer {{
  margin-top: 3rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--line);
  color: var(--ink-faint);
  font-size: 0.8rem;
}}

@media (prefers-reduced-motion: no-preference) {{
  .filter-row button {{ transition: background 0.12s ease, color 0.12s ease, border-color 0.12s ease; }}
}}
</style>

<div class="page">
  <header class="masthead">
    <p class="eyebrow">Eorzea &middot; Field Reference</p>
    <h1>{PAGE_TITLE}</h1>
    <p class="subhead">Every class and Grand Company hunting log entry from A Realm Reborn,
      in one sortable table &mdash; {total_entries} entries across {total_zones} zones,
      9 classes, and 3 Grand Companies.
      <span class="note">Source: FFXIV Console Games Wiki, Hunting Log and per-class/
      per-company log pages. Where the wiki listed several possible zones for one
      target, each zone gets its own row; the specific sub-area is only shown when
      the source tied it to a single zone. Click a column header to sort.</span>
    </p>
  </header>

  <div class="controls">
    <div class="progress-row">
      <span class="progress-text" id="progress-text">0 / {total_entries} done</span>
      <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
      <label class="hide-toggle">
        <input type="checkbox" id="hide-done" autocomplete="off">
        Hide done
      </label>
    </div>
    <div class="search-row">
      <input id="search" type="text" placeholder="Filter by monster, area, class, or zone&hellip;" autocomplete="off">
      <button type="button" id="filters-toggle" class="filters-toggle" aria-expanded="false" aria-controls="filters-body">
        Filters<span class="filters-count" id="filters-count"></span>
        <span class="chevron">&#9660;</span>
      </button>
    </div>
    <div class="filters-body" id="filters-body">
      <div class="filter-row" id="class-filter">
        {"".join(f'<button data-class="{c}" data-badge="{CLASS_BADGE[c]}">{c}</button>' for c in sorted(CLASS_ORDER))}
      </div>
      <div class="filter-row" id="gc-filter">
        {"".join(f'<button data-class="{c}" data-badge="{CLASS_BADGE[c]}">{c}</button>' for c in sorted(GC_ORDER))}
      </div>
      <div class="filter-row" id="rank-filter">
        {"".join(f'<button data-rank="{n}">Rank {n}</button>' for n in range(1, 6))}
      </div>
      <div class="filter-row" id="zone-filter">
        {zone_filter_buttons}
      </div>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th class="col-done"><span class="sr-only">Done</span></th>
          <th class="col-zone sortable" data-sort="zone">Zone<span class="sort-arrow"></span></th>
          <th class="col-class sortable" data-sort="class">Class<span class="sort-arrow"></span></th>
          <th class="col-rank sortable" data-sort="rank">Rank<span class="sort-arrow"></span></th>
          <th class="col-monster sortable" data-sort="monster">Monster<span class="sort-arrow"></span></th>
          <th class="col-area sortable" data-sort="area">Area<span class="sort-arrow"></span></th>
        </tr>
      </thead>
      <tbody id="log-body"></tbody>
    </table>
  </div>

  <p id="empty-state">No entries match that filter.</p>

  <footer>Compiled from ffxiv.consolegameswiki.com/wiki/Hunting_Log and its nine
  linked class pages plus the three Grand Company pages.</footer>
</div>

<script>
(function () {{
  const STORAGE_KEY = '{STORAGE_KEY}';
  const FILTERS_STORAGE_KEY = '{FILTERS_STORAGE_KEY}';
  const search = document.getElementById('search');
  const classButtons = document.querySelectorAll('#class-filter button, #gc-filter button');
  const rankButtons = document.querySelectorAll('#rank-filter button');
  const zoneButtons = document.querySelectorAll('#zone-filter button');
  const filtersToggle = document.getElementById('filters-toggle');
  const filtersBody = document.getElementById('filters-body');
  const filtersCount = document.getElementById('filters-count');
  const tbody = document.getElementById('log-body');
  const emptyState = document.getElementById('empty-state');
  const hideDoneToggle = document.getElementById('hide-done');
  const progressText = document.getElementById('progress-text');
  const progressFill = document.getElementById('progress-fill');
  let allRows = [];
  let totalCount = 0;
  const activeClasses = new Set();
  const activeRanks = new Set();
  const activeZones = new Set();
  let hideDone = false;

  function loadDone() {{
    try {{
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}');
    }} catch (e) {{
      return {{}};
    }}
  }}

  function saveDone(done) {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(done));
  }}

  let doneMap = loadDone();

  function loadFilters() {{
    try {{
      return JSON.parse(localStorage.getItem(FILTERS_STORAGE_KEY) || '{{}}');
    }} catch (e) {{
      return {{}};
    }}
  }}

  function saveFilters() {{
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify({{
      hideDone: hideDone,
      search: search.value,
      classes: Array.from(activeClasses),
      ranks: Array.from(activeRanks),
      zones: Array.from(activeZones)
    }}));
  }}

  function escapeHtml(str) {{
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }}

  function parseCsv(text) {{
    const rows = [];
    let row = [];
    let field = '';
    let inQuotes = false;
    for (let i = 0; i < text.length; i++) {{
      const c = text[i];
      if (inQuotes) {{
        if (c === '"') {{
          if (text[i + 1] === '"') {{ field += '"'; i++; }}
          else {{ inQuotes = false; }}
        }} else {{
          field += c;
        }}
      }} else if (c === '"') {{
        inQuotes = true;
      }} else if (c === ',') {{
        row.push(field);
        field = '';
      }} else if (c === '\\n' || c === '\\r') {{
        if (c === '\\r' && text[i + 1] === '\\n') i++;
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
      }} else {{
        field += c;
      }}
    }}
    if (field !== '' || row.length) {{
      row.push(field);
      rows.push(row);
    }}
    return rows;
  }}

  function idPart(str) {{
    return str.toLowerCase().replace(/'/g, '').replace(/\\s+/g, '_');
  }}

  // Mirrors CLASS_BADGE / zone_badge in build_page.py.
  const CLASS_BADGE = {{
    'Gladiator': 'tank', 'Marauder': 'tank',
    'Conjurer': 'healer',
    'Lancer': 'dps', 'Pugilist': 'dps', 'Rogue': 'dps',
    'Archer': 'dps', 'Thaumaturge': 'dps', 'Arcanist': 'dps',
    'Maelstrom': 'maelstrom',
    'Order of the Twin Adder': 'adder',
    'Immortal Flames': 'flames'
  }};

  function classBadge(cls) {{
    return CLASS_BADGE[cls] || 'neutral';
  }}

  function zoneBadge(zone) {{
    if (zone.indexOf('Shroud') !== -1) return 'adder';
    if (zone.indexOf('Thanalan') !== -1) return 'flames';
    if (zone.indexOf('La Noscea') !== -1) return 'maelstrom';
    return 'neutral';
  }}

  function buildRows(records) {{
    // A monster valid in several zones for the same class+rank hunting log
    // entry was split into one CSV row per zone (see NOTES.md); only one
    // kill is actually required, so merge those rows back into a single
    // checkable entry listing every valid zone. Rows are only merged when
    // every candidate has an empty area, since that's the split's signature
    // (a real area means it's a distinct, independently-tracked entry).
    const groups = new Map();
    records.forEach(function (r, idx) {{
      const zone = r[0], cls = r[1], rank = r[2], monster = r[3], area = r[4] || '';
      const key = [cls, rank, monster].join('\\u0001');
      if (!groups.has(key)) groups.set(key, {{ cls: cls, rank: rank, monster: monster, entries: [] }});
      groups.get(key).entries.push({{ zone: zone, area: area, idx: idx }});
    }});

    const specs = [];
    groups.forEach(function (g) {{
      const entries = g.entries;
      const mergeable = entries.length > 1 && entries.every(function (e) {{ return e.area === ''; }});
      if (mergeable) {{
        specs.push({{
          idx: entries.reduce(function (m, e) {{ return Math.min(m, e.idx); }}, entries[0].idx),
          zone: entries.map(function (e) {{ return e.zone; }}).join(' / '),
          cls: g.cls, rank: g.rank, monster: g.monster, area: ''
        }});
      }} else {{
        entries.forEach(function (e) {{
          specs.push({{ idx: e.idx, zone: e.zone, cls: g.cls, rank: g.rank, monster: g.monster, area: e.area }});
        }});
      }}
    }});
    specs.sort(function (a, b) {{ return a.idx - b.idx; }});

    const usedIds = Object.create(null);
    return specs.map(function (s) {{
      const base = [idPart(s.cls), idPart(s.zone), s.rank, idPart(s.monster), idPart(s.area)].join('|');
      let id = base;
      let suffix = 2;
      while (usedIds[id]) {{
        id = base + '_' + suffix;
        suffix++;
      }}
      usedIds[id] = true;
      return {{ zone: s.zone, cls: s.cls, rank: s.rank, monster: s.monster, area: s.area, id: id }};
    }});
  }}

  function renderRows(rows) {{
    tbody.innerHTML = rows.map(function (r) {{
      const areaDisplay = r.area ? escapeHtml(r.area) : '\\u2014';
      const zoneBadges = r.zone.split(' / ').map(function (z) {{
        return '<span class="badge badge-' + zoneBadge(z) + '">' + escapeHtml(z) + '</span>';
      }}).join('');
      return '<tr data-zone="' + escapeHtml(r.zone) + '" data-class="' + escapeHtml(r.cls) +
        '" data-monster="' + escapeHtml(r.monster) + '" data-area="' + escapeHtml(r.area) +
        '" data-id="' + escapeHtml(r.id) + '" data-rank="' + escapeHtml(r.rank) + '">' +
        '<td class="col-done"><input type="checkbox" class="done-check" data-id="' + escapeHtml(r.id) +
        '" aria-label="Mark ' + escapeHtml(r.monster) + ' done"></td>' +
        '<td class="col-zone"><span class="zone-badges">' + zoneBadges + '</span></td>' +
        '<td class="col-class"><span class="badge badge-' + classBadge(r.cls) + ' class-tag">' + escapeHtml(r.cls) + '</span></td>' +
        '<td class="col-rank">' + escapeHtml(r.rank) + '</td>' +
        '<td class="col-monster">' + escapeHtml(r.monster) + '</td>' +
        '<td class="col-area">' + areaDisplay + '</td>' +
        '</tr>';
    }}).join('');
  }}

  function updateProgress() {{
    const doneCount = Object.keys(doneMap).filter(function (k) {{
      return doneMap[k];
    }}).length;
    progressText.textContent = doneCount + ' / ' + totalCount + ' done';
    progressFill.style.width = (totalCount ? (doneCount / totalCount * 100) : 0) + '%';
  }}

  function applyDoneState() {{
    allRows.forEach(function (row) {{
      const id = row.getAttribute('data-id');
      const isDone = !!doneMap[id];
      row.classList.toggle('done', isDone);
      row.classList.toggle('hide-done', isDone && hideDone);
      const box = row.querySelector('.done-check');
      if (box) box.checked = isDone;
    }});
    updateProgress();
  }}

  function applyFilter() {{
    const q = search.value.trim().toLowerCase();
    let anyVisible = false;
    allRows.forEach(function (row) {{
      const cls = row.getAttribute('data-class');
      const rank = row.getAttribute('data-rank');
      const zone = row.getAttribute('data-zone');
      const monster = row.getAttribute('data-monster').toLowerCase();
      const area = row.getAttribute('data-area').toLowerCase();
      const classOk = activeClasses.size === 0 || activeClasses.has(cls);
      const rankOk = activeRanks.size === 0 || activeRanks.has(rank);
      const zoneOk = activeZones.size === 0 || zone.split(' / ').some(function (z) {{ return activeZones.has(z); }});
      const textOk = !q || monster.includes(q) || area.includes(q) ||
        zone.toLowerCase().includes(q) || cls.toLowerCase().includes(q);
      const doneOk = !(hideDone && row.classList.contains('done'));
      const show = classOk && rankOk && zoneOk && textOk && doneOk;
      row.classList.toggle('hidden', !show);
      if (show) anyVisible = true;
    }});
    emptyState.classList.toggle('show', !anyVisible);
  }}

  function toggleButton(btn, attr, activeSet) {{
    const v = btn.getAttribute(attr);
    if (btn.classList.contains('active')) {{
      btn.classList.remove('active');
      activeSet.delete(v);
    }} else {{
      btn.classList.add('active');
      activeSet.add(v);
    }}
  }}

  function updateFiltersCount() {{
    const n = activeClasses.size + activeRanks.size + activeZones.size;
    filtersCount.textContent = n ? ' (' + n + ')' : '';
  }}

  function restoreFilters() {{
    const saved = loadFilters();

    hideDone = !!saved.hideDone;
    hideDoneToggle.checked = hideDone;

    search.value = saved.search || '';

    function restoreGroup(buttons, attr, values, activeSet) {{
      const wanted = new Set(values || []);
      buttons.forEach(function (btn) {{
        const v = btn.getAttribute(attr);
        if (wanted.has(v)) {{
          btn.classList.add('active');
          activeSet.add(v);
        }}
      }});
    }}

    restoreGroup(classButtons, 'data-class', saved.classes, activeClasses);
    restoreGroup(rankButtons, 'data-rank', saved.ranks, activeRanks);
    restoreGroup(zoneButtons, 'data-zone', saved.zones, activeZones);
    updateFiltersCount();

    if (activeClasses.size || activeRanks.size || activeZones.size) {{
      filtersBody.classList.add('open');
      filtersToggle.setAttribute('aria-expanded', 'true');
    }}
  }}

  function attachEvents() {{
    search.addEventListener('input', function () {{
      applyFilter();
      saveFilters();
    }});

    filtersToggle.addEventListener('click', function () {{
      const open = filtersBody.classList.toggle('open');
      filtersToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }});

    classButtons.forEach(function (btn) {{
      btn.addEventListener('click', function () {{
        toggleButton(btn, 'data-class', activeClasses);
        updateFiltersCount();
        applyFilter();
        saveFilters();
      }});
    }});

    rankButtons.forEach(function (btn) {{
      btn.addEventListener('click', function () {{
        toggleButton(btn, 'data-rank', activeRanks);
        updateFiltersCount();
        applyFilter();
        saveFilters();
      }});
    }});

    zoneButtons.forEach(function (btn) {{
      btn.addEventListener('click', function () {{
        toggleButton(btn, 'data-zone', activeZones);
        updateFiltersCount();
        applyFilter();
        saveFilters();
      }});
    }});

    document.querySelectorAll('.done-check').forEach(function (box) {{
      box.addEventListener('change', function () {{
        const id = box.getAttribute('data-id');
        // Re-read before writing so a stale in-memory doneMap (e.g. this
        // page left open in another tab) can't clobber done-state saved
        // elsewhere since this tab loaded.
        doneMap = loadDone();
        if (box.checked) {{
          doneMap[id] = true;
        }} else {{
          delete doneMap[id];
        }}
        saveDone(doneMap);
        applyDoneState();
        applyFilter();
      }});
    }});

    hideDoneToggle.addEventListener('change', function () {{
      hideDone = hideDoneToggle.checked;
      applyDoneState();
      applyFilter();
      saveFilters();
    }});

    // Sorting
    const sortHeaders = document.querySelectorAll('th.sortable');
    let currentSort = {{ key: null, dir: 'asc' }};

    function updateSortArrows() {{
      sortHeaders.forEach(function (th) {{
        const arrow = th.querySelector('.sort-arrow');
        if (th.getAttribute('data-sort') === currentSort.key) {{
          arrow.textContent = currentSort.dir === 'asc' ? '\\u25b2' : '\\u25bc';
        }} else {{
          arrow.textContent = '';
        }}
      }});
    }}

    sortHeaders.forEach(function (th) {{
      th.addEventListener('click', function () {{
        const key = th.getAttribute('data-sort');
        const dir = (currentSort.key === key && currentSort.dir === 'asc') ? 'desc' : 'asc';
        currentSort = {{ key: key, dir: dir }};
        const numeric = key === 'rank';
        const rowsArr = Array.from(tbody.querySelectorAll('tr'));
        rowsArr.sort(function (a, b) {{
          let av = a.getAttribute('data-' + key);
          let bv = b.getAttribute('data-' + key);
          if (numeric) {{
            av = Number(av);
            bv = Number(bv);
            return dir === 'asc' ? av - bv : bv - av;
          }}
          av = av.toLowerCase();
          bv = bv.toLowerCase();
          if (av < bv) return dir === 'asc' ? -1 : 1;
          if (av > bv) return dir === 'asc' ? 1 : -1;
          return 0;
        }});
        rowsArr.forEach(function (row) {{ tbody.appendChild(row); }});
        updateSortArrows();
      }});
    }});
  }}

  function init() {{
    fetch('{CSV_PATH}')
      .then(function (res) {{
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.text();
      }})
      .then(function (text) {{
        const allRecords = parseCsv(text).filter(function (r) {{ return r.length === 5; }});
        const records = allRecords.slice(1);
        renderRows(buildRows(records));
        allRows = document.querySelectorAll('tbody tr[data-id]');
        totalCount = allRows.length;
        restoreFilters();
        attachEvents();
        applyDoneState();
        applyFilter();
      }})
      .catch(function (err) {{
        emptyState.textContent = 'Failed to load hunting log data ({CSV_PATH}).';
        emptyState.classList.add('show');
        console.error(err);
      }});
  }}

  init();
}})();
</script>
'''

OUT_HTML.write_text(html)
print(f"wrote {OUT_HTML} ({len(html)} bytes)")
