"""Export data/hunting_log.json to data/hunting_log.csv.

Run extract_data.py first to produce the JSON this reads.
"""
import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_JSON = REPO_ROOT / "data" / "hunting_log.json"
OUT_CSV = REPO_ROOT / "data" / "hunting_log.csv"

CLASS_ORDER = [
    "Gladiator", "Marauder", "Lancer", "Pugilist", "Rogue",
    "Archer", "Conjurer", "Thaumaturge", "Arcanist",
    "Maelstrom", "Order of the Twin Adder", "Immortal Flames",
]
class_idx = {c: i for i, c in enumerate(CLASS_ORDER)}

rows = json.loads(IN_JSON.read_text())
zones_sorted = sorted(set(r["zone"] for r in rows))
rows.sort(key=lambda r: (
    zones_sorted.index(r["zone"]), class_idx.get(r["class"], 99),
    r["rank"], r["monster"],
))

with open(OUT_CSV, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["zone", "class", "rank", "monster", "area"])
    for r in rows:
        w.writerow([r["zone"], r["class"], r["rank"], r["monster"], r["area"]])

print(f"wrote {OUT_CSV} ({len(rows)} rows)")
