# HMS Your Town

Which British towns have had a Royal Navy warship named after them, how many times, and what happened to those ships: 394 ships named after 135 towns and cities, from Wikidata.

Dr Tristan Hotham · Independent researcher · 2026

- Interactive map: https://maps.tristanhotham.com/ships-named/
- Paper: https://doi.org/10.5281/zenodo.24052719
- Blog post: https://blog.tristanhotham.com/2026/10/31/ships-named/
- Code and data: https://github.com/Tristan-Hotham/ships-named

## Headline results

| Town | Nation | Ships | First | Latest |
|:-|:-|:-|:-|:-|
| Gloucester | England | 9 | 1654 | 1985 |
| Newcastle upon Tyne | England | 9 | 1653 | 1978 |
| Glasgow | Scotland | 8 | 1741 | 1979 |
| Chatham | England | 7 | 1691 | 1990 |
| Falmouth | England | 7 | 1693 | 1961 |
| London | England | 7 | 1656 | 1987 |
| Maidstone | England | 7 | 1744 | 1937 |
| Pembroke | Wales | 7 | 1689 | 1944 |
| Scarborough | England | 7 | 1708 | 1957 |
| York | England | 7 | 1654 | 1985 |
| Berwick-upon-Tweed | England | 6 | 1689 | 1961 |
| Bristol | England | 6 | 1653 | 1973 |

- 28 towns have had five ships or more, 50 just one; 63% lie within 10 km of the open sea.
- Town names were common in the later 1600s (33% of ships commissioned 1650 to 1699), rare in the 1800s, and common again after 1950.
- Lancaster has had 4 ships in the data; Barrow-in-Furness none.
- Only 24% of the ships have any recorded fate in Wikidata; 11 are recorded as lost.
- Where Wikidata records a ship's namesake, the US Navy has 146 ships named after American towns and cities.

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

Royal Navy ships labelled HMS in Wikidata are linked to a British town by their "named after" (P138) where it is a British town or city (10 ships), by an exact name match to a British town or city (350), or as "town Castle" (34). Ships named after other things are excluded by their P138, by class (Hunt, Racecourse, River, Flower, Bird, Tree, Isles, Dance, and the classes named after counties) and by a list of names (people, battles, rivers, counties, foreign places), 675 in all. 167 matched ships (42%) share their name with a noble title; they are counted but flagged, and without them 227 ships and 93 towns remain. Years are commissioning years or the class's median. Fates come from the ships' significant events.

Caveats: Wikidata is incomplete: only 261 of the 6,006 ships (4%) record what they were named after, the matches are 7% of all the HMS ships, and 43 of the 45 Town-class destroyers of 1940 appear only under their American names, so are missed. A name match is inference; fates are mostly unrecorded; the international view covers only ships with a recorded namesake.

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

Hotham, T. (2026) HMS Your Town: British towns and the Royal Navy ships named after them. Zenodo. https://doi.org/10.5281/zenodo.24052719

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
