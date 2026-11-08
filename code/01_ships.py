"""Step 1: Royal Navy ships from Wikidata, with a year, a fate and, where possible, the UK town they are named after.

Matching (strict):
  * "wikidata": the ship's P138 (named after) is a UK place in ships_named.tsv.
  * "name": no P138, and the name after "HMS " is exactly the name of a UK town or city in uk_settlements.tsv (type town,
    market town, city, county town, seaside resort, new town, or 10,000 people or more), inside the UK. If several UK
    towns share the name, the most populous is used and the match is flagged ambiguous.
  * "castle": no P138, the name is "<town> Castle" (the Castle-class corvettes of 1943 to 1945 and older ships),
    matched to that town; flagged.
  Excluded: ships whose P138 is anything other than a UK place (a person, a battle, a foreign town); classes named after
  something other than towns (Hunt-class destroyers after fox hunts, Racecourse-class minesweepers after racecourses,
  River-class frigates and destroyers after rivers); and names in EXCLUDE below (people, battles, foreign places,
  rivers and counties that happen to share a name with a UK town).
  Names that are also titles of royal dukes or peers (York, Gloucester, Lancaster ...) are kept but flagged: some of
  the older ships honoured the duke or earl rather than the town.
Writes data/rn_ships.csv and WORK/ships.pkl."""
import pandas as pd, numpy as np
from common import *

cl = lambda s: s.str.replace(r'^"(.*)"@\w+$', r"\1", regex=True).str.replace(r"^<http://www.wikidata.org/entity/(.*)>$", r"\1", regex=True)


def load(f):
    d = pd.read_csv(f"{RAW}/{f}", sep="\t", dtype=str, keep_default_na=False, quoting=3)
    d.columns = [c.strip("?") for c in d.columns]
    for c in d.columns:
        d[c] = cl(d[c])
    return d


N = load("navy_ships.tsv")
SN = load("ships_named.tsv")
U = load("uk_settlements.tsv")
U["popn"] = pd.to_numeric(U["pop"], errors="coerce")
xy = U.coord.str.extract(r"Point\(([-0-9.eE]+) ([-0-9.eE]+)\)", flags=re.I)
U["lon"], U["lat"] = xy[0].astype(float), xy[1].astype(float)
TT = {"town", "market town", "city", "county town", "seaside resort", "big city", "new town (UK)", "town of the United Kingdom",
      "city of United Kingdom", "port city", "city status in the United Kingdom", "cathedral city", "largest city", "port settlement"}
inuk = U.lat.between(49.8, 61) & U.lon.between(-8.7, 2.0)
T = U[inuk & (U.typel.isin(TT) | (U.popn >= 10000))].copy()
T["popn"] = T.popn.fillna(0)
T = T.sort_values("popn", ascending=False)
nshare = T.groupby("pl").p.nunique()
TOWN = {r.pl: dict(qid=r.p, lat=r.lat, lon=r.lon, pop=r.popn, type=r.typel, ambiguous=bool(nshare[r.pl] > 1)) for r in T.drop_duplicates("pl").itertuples()}

EXCLUDE = {  # name: reason
    "Alexandria": "a city in Egypt", "Gibraltar": "Gibraltar", "Dunkirk": "the French port and its evacuation",
    "Halifax": "Halifax, Nova Scotia, or the Earl of Halifax", "Falkland": "the Falkland Islands or Viscount Falkland",
    "Kimberley": "Kimberley in South Africa or the Earl of Kimberley", "Nelson": "Admiral Nelson", "Wellington": "the Duke of Wellington",
    "Moira": "the Earl of Moira", "Keith": "Admiral Lord Keith", "Marlborough": "the Duke of Marlborough", "Berkeley": "Admiral Berkeley",
    "St George": "the saint", "Colne": "the river", "Blackwater": "the river", "Wye": "the river", "Usk": "the river", "Leven": "the river",
    "Somerset": "the county", "Antrim": "the county", "Clare": "the county or the Earl", "Lee": "the river", "Boston": "Boston, Massachusetts, in early ships",
    "Bentley": "a person", "Rotherham": "Captain Edward Rotherham, Collingwood's flag captain at Trafalgar", "Easton": "a person", "Oxley": "a person", "Alderney": "a Channel Island", "Blackwood": "a person", "Blackwall": "the London shipyard",
}
# short forms the Navy used for towns whose gazetteer name is longer (the short form names a smaller town elsewhere)
ALIAS = {"Newcastle": "Newcastle upon Tyne", "Yarmouth": "Great Yarmouth", "Berwick": "Berwick-upon-Tweed", "Londonderry": "Derry",
         "Shoreham": "Shoreham-by-Sea", "Milford": "Milford Haven", "Weston": "Weston-super-Mare"}
# ships checked one by one in review and found not to honour the town (or not the town matched), or duplicate items
DROP = {"Q11289816": "named after Admiral Lord Exmouth", "Q5632358": "Duncan class, named after admirals (Lord Exmouth)",
        "Q1466257": "flotilla leader named after Admiral Lord Exmouth", "Q5632355": "carries on the name of the Exmouth leader (Lord Exmouth)",
        "Q261121": "former East Indiaman Earl of Abergavenny", "Q5632712": "former East Indiaman named after Warren Hastings",
        "Q5477823": "flotilla leader named after the Marquess of Montrose", "Q60790842": "namesake uncertain",
        "Q111938649": "Newport: which Newport is uncertain", "Q113364979": "apparent duplicate of Q113331530 (no dates distinguish them)"}
# "<name> Castle" ships whose castle is not in the gazetteer town of that name: None = excluded, else the town it is in
CASTLE_FIX = {"Leeds": None,                       # Leeds Castle is in the village of Leeds, Kent, not the city
              "Caistor": "Caister-on-Sea",         # Caister Castle, Norfolk (the corvette spelt it Caistor)
              "Hadleigh": ("Hadleigh", "Q2346831")}  # Hadleigh Castle, Essex, not Hadleigh, Suffolk
TITLES = set("York Gloucester Lancaster Cumberland Monmouth Portland Newcastle Newcastle_upon_Tyne Bedford Buckingham Richmond Shrewsbury Warwick Arundel "
             "Salisbury Northampton Oxford Cambridge Chester Exeter Rochester Winchester Lincoln Nottingham Windsor Pembroke Sandwich Chichester "
             "Dartmouth Plymouth Portsmouth Southampton Worcester Bristol Coventry Ludlow Torrington Montrose Perth St_Albans Burford Orford Abergavenny Edinburgh Carlisle Sunderland Tavistock Winchelsea Chesterfield".split())
BADCLASS = re.compile(r"County-class|Kent-class|London-class heavy|Norfolk-class heavy|Monmouth-class armou?red|Devonshire-class armou?red|Hunt-class|Racecourse-class|River-class|Flower-class|Bird-class|Tree-class|Isles-class|Dance-class", re.I)

# places that ships_named records as P138 targets in the UK
SNUK = SN[SN.ncl == "United Kingdom"].copy()
pxy = SNUK.ncoord.str.extract(r"Point\(([-0-9.eE]+) ([-0-9.eE]+)\)", flags=re.I)
SNUK["lon"], SNUK["lat"] = pxy[0].astype(float), pxy[1].astype(float)
PLACE = {r.n: dict(name=r.nl, lat=r.lat, lon=r.lon, type=r.ntypel) for r in SNUK.drop_duplicates("n").itertuples()}
SNANY = set(SN.n)
NOTTOWN = re.compile(r"county(?! town)|river|island|protectorate|territor|constituent|palace|castle|lieutenancy|country", re.I)

rn = N[N.opl == "Royal Navy"].copy()
rn["cy"] = pd.to_numeric(rn.comm.str[:4], errors="coerce")
rn["dy"] = pd.to_numeric(rn.decomm.str[:4], errors="coerce")
g = rn.groupby("s").agg(label=("sl", "first"), cls=("clsl", "first"), comm=("cy", "min"), decomm=("dy", "max"),
                         events=("fatel", lambda x: sorted(set(v for v in x if v))), n=("n", lambda x: next((v for v in x if v), "")),
                         sitelinks=("sitelinks", "first")).reset_index()
g = g[g.label.str.match(r"^HMS ")].copy()
g["name"] = g.label.str[4:].str.replace(r"\s*\(.*\)$", "", regex=True).str.strip()

# year: commissioning year, else the median commissioning year of the ship's class (3 or more dated ships), else the
# year in the class name (the Establishments of 1706 to 1745)
cm = g[g.comm.notna() & (g.cls != "")].groupby("cls").comm.agg(["median", "size"])
cm = cm[cm["size"] >= 3]["median"]


def year(r):
    if pd.notna(r.comm): return int(r.comm), "commissioned"
    if r.cls in cm.index: return int(cm[r.cls]), "class"
    m = re.match(r"^(1[6-9]\d\d) ", r.cls or "")
    if m: return int(m.group(1)), "class"
    return None, ""


g[["year", "year_src"]] = g.apply(lambda r: pd.Series(year(r)), axis=1)
g.loc[g.cls == "Town-class destroyer", ["year", "year_src"]] = [1940, "commissioned"]  # transferred from the US Navy in 1940


def fate(r):
    fs = [EV_FATE[e] for e in r.events if e in EV_FATE]
    for k, _, _ in FATES:
        if k in fs: return k
    if pd.notna(r.decomm): return "decomm"
    if pd.notna(r.comm) and r.comm >= 1985: return "service"
    return "unknown"


g["fate"] = g.apply(fate, axis=1)
g["fate_event"] = g.events.map(lambda es: "; ".join(e for e in es if e in EV_FATE))


def match(r):
    if r.s in DROP:
        return "excluded", DROP[r.s], None, None, "", "", False
    if r.n and BADCLASS.search(r.cls or ""):
        return "excluded", "class named after other things", None, None, "", r.n, False
    if r.n:
        if r.n in PLACE:
            p = PLACE[r.n]
            if 49.8 <= p["lat"] <= 61 and -8.7 <= p["lon"] <= 2.0 and not NOTTOWN.search(p["type"] or ""):
                return "wikidata", p["name"], p["lat"], p["lon"], p["type"], r.n, False
            return "excluded", "named after a UK county, river, island, territory or building", None, None, p["type"], r.n, False
        return "excluded", ("named after " + ("a place outside the UK" if r.n in SNANY else "something other than a place")), None, None, "", r.n, False
    if BADCLASS.search(r.cls or ""):
        return "excluded", "class named after other things", None, None, "", "", False
    nm = r["name"]
    if nm.endswith(" Castle") and nm[:-7] in CASTLE_FIX:
        fx = CASTLE_FIX[nm[:-7]]
        if fx is None:
            return "excluded", "named after a castle outside the town of that name", None, None, "", "", False
        if isinstance(fx, tuple):
            q = U[U.p == fx[1]].iloc[0]
            return "castle", fx[0], q.lat, q.lon, q.typel, fx[1], False
        t = TOWN[fx]
        return "castle", fx, t["lat"], t["lon"], t["type"], t["qid"], False
    nm = ALIAS.get(nm, nm)
    if nm in EXCLUDE:
        return "excluded", "named after " + EXCLUDE[nm], None, None, "", "", False
    if nm in TOWN:
        t = TOWN[nm]
        return "name", nm, t["lat"], t["lon"], t["type"], t["qid"], t["ambiguous"]
    if nm.endswith(" Castle") and nm[:-7] in TOWN and nm[:-7] not in EXCLUDE:
        t = TOWN[nm[:-7]]
        return "castle", nm[:-7], t["lat"], t["lon"], t["type"], t["qid"], t["ambiguous"]
    return "", "", None, None, "", "", False


g[["match", "place", "lat", "lon", "ptype", "pqid", "ambiguous"]] = g.apply(lambda r: pd.Series(match(r)), axis=1)
g["title"] = g.place.str.replace(" ", "_").isin(TITLES) & g.match.isin(["name", "castle"])
g["events"] = g.events.map("; ".join)
g.to_pickle(f"{WORK}/ships.pkl")
out = g[g.match.isin(["wikidata", "name", "castle"])].drop(columns=["n"])
out.to_csv(f"{DATA}/rn_ships.csv", index=False)
print("RN HMS ships", len(g), "| matched", out.match.value_counts().to_dict(), "| excluded", int((g.match == "excluded").sum()))
print("places", out.place.nunique(), "| year src", g.year_src.value_counts().to_dict())
print("fates (matched)", out.fate.value_counts().to_dict())
print(out.place.value_counts().head(15).to_dict())
