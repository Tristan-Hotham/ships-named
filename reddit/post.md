# Reddit post

**Title:** [OC] HMS Your Town: 135 British towns have given their name to a Royal Navy warship, 394 ships in all. Gloucester and Newcastle lead with 9 each

**Image:** ships_named_collage.png

**Body:**

I matched every Royal Navy "HMS" ship in Wikidata (6,006 ships) to the British towns and cities they are named after, strictly: an exact match to a real town, leaving out ships named after people, battles, rivers, counties, fox hunts or foreign places. Only 261 ships (4%) say in Wikidata what they were named after, so most matches are inferred from the name, and the 394 are 7% of all the HMS ships in the data.

- 28 towns have had five ships or more; 50 just one.
- 63% of the towns are within 10 km of the sea.
- The fashion came and went: about a third of ships commissioned 1650 to 1699 bore a town's name, under 3% in the 1800s, over a fifth from 1950 to 1999.
- Lancaster has had 4 in the data; Barrow-in-Furness, which built so many of them, none.
- Only 24% have any recorded fate in Wikidata, so "what happened to them" is mostly a gap.

Interactive map (tap a town for its ships): https://maps.tristanhotham.com/ships-named/

**Source comment:**

Data: Wikidata (CC0), Royal Navy ships with class, dates, events and "named after"; UK towns and cities with population and type. Some names are also noble titles (York, Gloucester, and the Type 23 frigates named after dukedoms): 42% of the matches, counted but flagged on the map; without them it is 227 ships and 93 towns. The 1940 Town-class destroyers from the US are in Wikidata only under their American names, so they are missed. Tools: Python (pandas, matplotlib), MapLibre. Paper, data and code: https://github.com/Tristan-Hotham/ships-named
