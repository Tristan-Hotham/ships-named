"""Step 9: README.md from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json"); S = R["source"]
rows = "\n".join(f"| {t['place']} | {t['nation']} | {t['ships']} | {int(t['first']) if t['first'] else ''} | {int(t['last']) if t['last'] else ''} |" for t in R["top"][:12])
md = f"""# HMS Your Town

Which British towns have had a Royal Navy warship named after them, how many times, and what happened to those ships: {S['matched']} ships named after {S['towns']} towns and cities, from Wikidata.

Dr Tristan Hotham · Independent researcher · 2026

- Interactive map: {PAGE}
- Paper: {{https://doi.org/10.5281/zenodo.24052719}}
- Blog post: {{https://blog.tristanhotham.com/2026/10/31/ships-named/}}
- Code and data: {REPO}

## Headline results

| Town | Nation | Ships | First | Latest |
|:-|:-|:-|:-|:-|
{rows}

- {R['five_plus']} towns have had five ships or more, {R['one_ship_towns']} just one; {R['coast']['within10_pct']:.0f}% lie within 10 km of the open sea.
- Town names were common in the later 1600s ({R['peak']['pct']:.0f}% of ships commissioned 1650 to 1699), rare in the 1800s, and common again after 1950.
- Lancaster has had {R['lancaster']['ships']} ships in the data; Barrow-in-Furness none.
- Only {S['fate_known_pct']:.0f}% of the ships have any recorded fate in Wikidata; {R['fates']['lost']} are recorded as lost.
- Where Wikidata records a ship's namesake, the US Navy has {R['intl']['usn_us_towns']} ships named after American towns and cities.

## Files

| Path | What |
|:-|:-|
| `index.html`, `js/`, `fonts/`, `data/points.json` | the interactive page (Inked World map style) |
| `data/rn_ships.csv` | each matched ship: town, how it was matched, year and its source, class, recorded fate, flags |
| `data/places.csv` | each town: ships, first and latest year, nation, distance to the sea, flags |
| `data/international.csv` | ships named after places, by navy |
| `data/results.json` | every number quoted anywhere |
| `code/` | numbered scripts, templates, `qa.js` |
| `release/` | paper, blog post and figures, Zenodo files |
| `reddit/` | collage, its script and the post |

## Method

Royal Navy ships labelled HMS in Wikidata are linked to a British town by their "named after" (P138) where it is a British town or city ({S['by_match']['wikidata']} ships), by an exact name match to a British town or city ({S['by_match']['name']}), or as "town Castle" ({S['by_match']['castle']}). Ships named after other things are excluded by their P138, by class (Hunt, Racecourse, River, Flower, Bird, Tree, Isles, Dance, and the classes named after counties) and by a list of names (people, battles, rivers, counties, foreign places), {S['excluded']} in all. {S['title_ships']} matched ships ({S['title_pct']:.0f}%) share their name with a noble title; they are counted but flagged, and without them {R['notitle']['ships']} ships and {R['notitle']['towns']} towns remain. Years are commissioning years or the class's median. Fates come from the ships' significant events.

Caveats: Wikidata is incomplete: only {S['rn_with_p138']} of the {S['rn_ships']:,} ships ({S['p138_pct']:.0f}%) record what they were named after, the matches are {S['matched_pct']:.0f}% of all the HMS ships, and {R['town_destroyers']['us_label']} of the {R['town_destroyers']['in_data']} Town-class destroyers of 1940 appear only under their American names, so are missed. A name match is inference; fates are mostly unrecorded; the international view covers only ships with a recorded namesake.

## Sources and licences

- Wikidata (CC0): ships and UK settlements. Natural Earth (public domain) for static maps and the coastline.
- Map: OpenStreetMap contributors (ODbL) via OpenFreeMap; the Inked World style (MIT) and its data.
- Code MIT; text, figures and derived data CC BY 4.0. See LICENSE.

## Rerun

```
cd code
python3 01_ships.py && python3 02_analysis.py && python3 05_build_site.py && python3 06_figures.py && python3 07_paper.py
python3 ../reddit/collage.py && python3 09_readme.py && python3 08_release.py
node qa.js
```
Raw inputs are listed in `code/common.py`.

## Citation

Hotham, T. (2026) HMS Your Town: British towns and the Royal Navy ships named after them. Zenodo. {{https://doi.org/10.5281/zenodo.24052719}}

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in md, bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(md)
print("README", len(md))
