# FFXIV Hunt Log Tracker

A self-contained, single-file tracker for every class hunting log entry from
*FFXIV: A Realm Reborn* (all 9 base classes), as one sortable/filterable
table with columns Done | Zone | Class | Rank | Monster | Area.

Open `index.html` directly in a browser, or serve it via GitHub Pages (it's
at the repo root on `main`, so it's ready to go as-is). No build step and no
backend — everything, including progress tracking, runs client-side.

## Features

- Checkbox per row → progress persisted to `localStorage`, so it's
  remembered between visits.
- "Hide done" toggle, plus a progress bar/count.
- Free-text search across monster/area/zone/class.
- Filter buttons for class, rank (1–5), and zone.
- Click any column header to sort ascending/descending.
- Theme-aware (light/dark, follows system preference or manual override).

## Data provenance

Source: [ffxiv.consolegameswiki.com/wiki/Hunting_Log](https://ffxiv.consolegameswiki.com/wiki/Hunting_Log)
— that overview page only links out to 9 per-class sub-pages (Arcanist,
Archer, Conjurer, Gladiator, Lancer, Marauder, Pugilist, Rogue,
Thaumaturge), each fetched and parsed separately.

Known caveats baked into the data:
- For Archer, Conjurer, and Lancer, the source didn't reliably give a
  sub-area (only the zone), so many of those rows have an empty Area (shown
  as "—" in the table).
- Some monsters are valid in multiple zones on the source page (e.g.
  "Central Shroud / Southern Thanalan"). Those were split into one row per
  zone; when split, the Area is dropped for that row since it wasn't clear
  which zone it belonged to.
- Row IDs (used for the localStorage done-tracking) are built as
  `class|zone|rank|monster|area`, lowercased, spaces→underscores,
  apostrophes stripped, with a numeric suffix on collision.

## Repo layout

```
index.html            generated page — open this in a browser
data/hunting_log.csv   raw data (zone, class, rank, monster, area), fetched by
                        index.html at runtime to populate the table
data/hunting_log.json  intermediate data used to generate index.html and the CSV
scripts/
  extract_data.py      parses raw wiki text into data/hunting_log.json
  build_page.py         renders data/hunting_log.json into index.html
  export_csv.py         exports data/hunting_log.json into data/hunting_log.csv
```

`index.html` doesn't embed the table data — it fetches `data/hunting_log.csv`
client-side on load and renders the rows from that. So `data/hunting_log.csv`
must exist (and be current) before opening `index.html`, or the page loads
with an empty table and an error in place of the "no entries match" message.

## Regenerating the data

Requires Python 3, standard library only (no dependencies to install).

Run from the repo root, in order:

```bash
# 1. Parse raw wiki text into data/hunting_log.json
python3 scripts/extract_data.py

# 2. Export data/hunting_log.json into data/hunting_log.csv — index.html
#    fetches this at runtime, so it must exist before you open the page
python3 scripts/export_csv.py

# 3. Render data/hunting_log.json into index.html
python3 scripts/build_page.py
```

`extract_data.py` must run first — the other two scripts both read its
`data/hunting_log.json` output. `build_page.py` doesn't itself read the CSV,
so it will still run fine before `export_csv.py` — but run `export_csv.py`
first anyway, since `index.html` won't have anything to show until
`data/hunting_log.csv` exists.
