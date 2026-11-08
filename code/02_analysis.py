"""Step 2: towns, eras, fates and the international view; data/results.json (every quoted number, with asserts),
data/places.csv, data/points.json (the map) and data/international.csv."""
import warnings; warnings.filterwarnings("ignore", category=DeprecationWarning)
import pandas as pd, numpy as np
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
from common import *

S = pd.read_pickle(f"{WORK}/ships.pkl")
M = S[S.match.isin(["wikidata", "name", "castle"])].copy()
ALL = S.copy()

# ---- nation (from local authority boundaries) and distance to the sea (Natural Earth 1:10m coastline via countries)
lad = jload(f"{GEO}/lad23_bgc.geojson")
geoms = [shape(f["geometry"]) for f in lad["features"]]
codes = [next(v for k, v in f["properties"].items() if k.upper().startswith("LAD") and k.upper().endswith("CD")) for f in lad["features"]]
tree = STRtree(geoms)
NAT = {"E": "England", "W": "Wales", "S": "Scotland", "N": "Northern Ireland"}
ne = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
gb = unary_union([shape(f["geometry"]) for f in ne["features"] if f["properties"].get("ADM0_A3") in ("GBR", "IRL")])
coast = gb.boundary


def nation(lon, lat):
    p = Point(lon, lat)
    for i in tree.query(p):
        if geoms[i].contains(p): return NAT[codes[i][0]]
    best = min(range(len(geoms)), key=lambda i: geoms[i].distance(p))
    return NAT[codes[best][0]]


from pyproj import Transformer
from shapely.ops import transform as _tf
_bng = Transformer.from_crs(4326, 27700, always_xy=True).transform
coast_bng = _tf(_bng, coast)


def coast_km(lon, lat):
    """Distance in km to the Natural Earth coastline of Great Britain and Ireland, on the British National Grid."""
    return coast_bng.distance(_tf(_bng, Point(lon, lat))) / 1000.0


# ---- places
rows = []
for pl, x in M.groupby("place"):
    x = x.sort_values("year")
    lat, lon = float(x.lat.iloc[0]), float(x.lon.iloc[0])
    fates = x.fate.value_counts().to_dict()
    yrs = x.year.dropna()
    rows.append(dict(place=pl, lat=round(lat, 4), lon=round(lon, 4), ships=len(x), first=int(yrs.min()) if len(yrs) else None,
                     last=int(yrs.max()) if len(yrs) else None, nation=nation(lon, lat), coast_km=round(coast_km(lon, lat), 1),
                     title=bool(x.title.any()), ambiguous=bool(x.ambiguous.any()), confirmed=int((x.match == "wikidata").sum()),
                     castle=int((x.match == "castle").sum()), lost=fates.get("lost", 0), known_fate=int((~x.fate.isin(["unknown"])).sum()),
                     recent=fates.get("service", 0), pqid=x.pqid.iloc[0],
                     names="; ".join(f"{r.label} ({int(r.year) if pd.notna(r.year) else 'year unknown'})" for r in x.itertuples())))
P = pd.DataFrame(rows).sort_values(["ships", "place"], ascending=[False, True])
P["era"] = pd.cut(P["last"], [0, 1799, 1899, 1945, 2100], labels=["before 1800", "1800s", "1900 to 1945", "since 1946"]).astype(str)
P.to_csv(f"{DATA}/places.csv", index=False)
M = M.merge(P[["place", "nation", "coast_km"]], on="place", how="left")
M.drop(columns=["n"]).to_csv(f"{DATA}/rn_ships.csv", index=False)

# ---- eras: share of all HMS ships (with a year) that bear a town name
ALL["bin"] = (ALL.year // 50 * 50)
M["bin"] = (M.year // 50 * 50)
era = []
for b in sorted(ALL.bin.dropna().unique()):
    a = int((ALL.bin == b).sum()); m = int((M.bin == b).sum())
    era.append(dict(start=int(b), ships=a, town=m, pct=100 * m / a if a else 0))
ERA = pd.DataFrame(era)

# ---- classes
CLS = M.groupby("cls").size().sort_values(ascending=False)

# ---- international (ships of any navy with P138 a place with coordinates)
cl = lambda s: s.str.replace(r'^"(.*)"@\w+$', r"\1", regex=True).str.replace(r"^<http://www.wikidata.org/entity/(.*)>$", r"\1", regex=True)
SN = pd.read_csv(f"{RAW}/ships_named.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
SN.columns = [c.strip("?") for c in SN.columns]
for c in SN.columns: SN[c] = cl(SN[c])
NAVY = re.compile(r"Navy|Marine|Naval|Kriegsmarine|Armada|Marina", re.I)
SN = SN[SN.opl.str.contains(NAVY)].drop_duplicates(["s", "n"])
TOWNT = re.compile(r"city|town|municipality|commune|village|borough|capital|prefecture|port|settlement", re.I)
SN["townish"] = SN.ntypel.str.contains(TOWNT)
xy = SN.ncoord.str.extract(r"Point\(([-0-9.eE]+) ([-0-9.eE]+)\)", flags=re.I)
SN["lon"], SN["lat"] = xy[0].astype(float), xy[1].astype(float)
nav = SN.drop_duplicates("s").groupby("opl").s.size().sort_values(ascending=False)
I = []
for op in nav.index[:14]:
    x = SN[SN.opl == op].drop_duplicates("s")
    t = x[x.townish & (x.nl != "")]
    vc = t.nl.value_counts()
    I.append(dict(navy=op, ships=len(x), towns=int(len(t)), places=int(x.n.nunique()),
                  top_town=vc.index[0] if len(vc) else "", top_n=int(vc.iloc[0]) if len(vc) else 0))
INT = pd.DataFrame(I)
INT.to_csv(f"{DATA}/international.csv", index=False)
usn = SN[(SN.opl == "United States Navy")].drop_duplicates("s")
usn_t = usn[usn.townish & (usn.ncl == "United States") & (usn.nl != "")]
intl_pts = SN[SN.townish & SN.lat.notna()].groupby(["nl", "ncl", "lat", "lon"]).agg(ships=("s", "nunique"), navies=("opl", lambda v: "; ".join(sorted(set(v))))).reset_index()

# ---- results
R = {}
R["source"] = dict(rn_ships=int(len(S)), rn_with_p138=int((S.n != "").sum()), towns=int(P.place.nunique()), matched=int(len(M)),
                   by_match={k: int(v) for k, v in M.match.value_counts().items()}, excluded=int((S.match == "excluded").sum()),
                   year_known=int(M.year.notna().sum()), year_comm=int((M.year_src == "commissioned").sum()), year_class=int((M.year_src == "class").sum()),
                   fate_known=int((M.fate != "unknown").sum()), fate_known_pct=100 * float((M.fate != "unknown").mean()),
                   title_ships=int(M.title.sum()), ambiguous_ships=int(M.ambiguous.sum()))
R["fates"] = {k: int((M.fate == k).sum()) for k, _, _ in FATES}
R["top"] = [dict(place=r.place, ships=int(r.ships), first=r.first, last=r.last, nation=r.nation) for r in P.head(15).itertuples()]
R["nations"] = {n: dict(towns=int((P.nation == n).sum()), ships=int(M[M.nation == n].shape[0])) for n in NAT.values()}
R["coast"] = dict(within10=int((P.coast_km <= 10).sum()), within10_pct=100 * float((P.coast_km <= 10).mean()),
                  ships_within10_pct=100 * float((M.coast_km <= 10).mean()))
R["era"] = ERA.to_dict(orient="records")
peak = ERA[ERA.ships >= 100].sort_values("pct", ascending=False).iloc[0]
R["peak"] = dict(start=int(peak.start), pct=float(peak.pct), ships=int(peak.ships), town=int(peak.town))
R["classes"] = {c: int(v) for c, v in CLS.head(12).items()}
R["castle_class"] = int((M.cls == "Castle-class corvette").sum())
R["type42"] = int((M.cls == "Type 42 guided missile destroyer").sum())
R["type26"] = int((M.cls == "Type 26 frigate").sum())
R["establishment"] = int(M.cls.str.contains("Establishment", na=False).sum())
lan = M[M.place == "Lancaster"].sort_values("year")
R["lancaster"] = dict(ships=int(len(lan)), names=lan.label.tolist(), years=[int(y) if pd.notna(y) else None for y in lan.year], classes=lan.cls.fillna("").tolist())
R["barrow"] = dict(ships=int((M.place == "Barrow-in-Furness").sum()), in_list=bool((S.name.str.contains("Barrow")).any()))
R["lost"] = [dict(label=r.label, year=int(r.year) if pd.notna(r.year) else None, event=r.fate_event) for r in M[M.fate == "lost"].sort_values("year").itertuples()]
R["intl"] = dict(navies=I, usn_ships=int(len(usn)), usn_us_towns=int(len(usn_t)), usn_top=usn_t.nl.value_counts().head(5).to_dict(),
                 ships=int(SN.s.nunique()), navy_n=int(len(nav)))
R["one_ship_towns"] = int((P.ships == 1).sum())
R["source"]["matched_pct"] = 100 * R["source"]["matched"] / R["source"]["rn_ships"]
R["source"]["p138_pct"] = 100 * R["source"]["rn_with_p138"] / R["source"]["rn_ships"]
R["source"]["title_pct"] = 100 * R["source"]["title_ships"] / R["source"]["matched"]
NT = M[~M.title]
R["notitle"] = dict(ships=int(len(NT)), towns=int(NT.place.nunique()))
# Town-class destroyers of 1940 (ex-US): in Wikidata under their US names only, so not matched
NV = pd.read_csv(f"{RAW}/navy_ships.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
NV.columns = [c.strip("?") for c in NV.columns]
td = NV[NV.opl.str.contains("Royal Navy") & NV.clsl.str.contains("Town-class destroyer")]
R["town_destroyers"] = dict(in_data=int(td.s.nunique()), us_label=int(td[td.sl.str.startswith('"USS')].s.nunique()))
R["five_plus"] = int((P.ships >= 5).sum())

# asserts for facts in words
assert R["lancaster"]["ships"] == 4 and R["barrow"]["ships"] == 0
assert R["source"]["fate_known_pct"] < 40
assert P.iloc[0].ships == 9 and set(P[P.ships == 9].place) == {"Gloucester", "Newcastle upon Tyne"}
assert R["coast"]["within10_pct"] > 50
jsave(R, f"{DATA}/results.json", indent=1)

# ---- points for the map
ships = [[r.label, int(r.year) if pd.notna(r.year) else 0, r.year_src, r.cls or "", r.fate, r.fate_event or "", r.match, r.s, 1 if r.title else 0]
         for r in M.sort_values("year").itertuples()]
pidx = {p: i for i, p in enumerate(P.place)}
for s, r in zip(ships, M.sort_values("year").itertuples()):
    s.append(pidx[r.place])
jsave(dict(places=[[r.lon, r.lat, r.place, int(r.ships), r.first or 0, r.last or 0, r.nation, 1 if r.title else 0, 1 if r.ambiguous else 0, r.era, r.pqid, int(r.lost), int(r.known_fate)] for r in P.itertuples()],
           ships=ships, fates=[[k, n, c] for k, n, c in FATES],
           intl=[[round(r.lon, 3), round(r.lat, 3), r.nl, r.ncl, int(r.ships), r.navies] for r in intl_pts.itertuples()]), f"{DATA}/points.json")
print(json.dumps({k: R[k] for k in ("source", "fates", "nations", "coast", "peak", "castle_class", "type42", "lancaster", "barrow", "one_ship_towns", "five_plus")}, indent=0, default=str)[:3000])
print(ERA.to_string()); print(INT.to_string()); print(R["intl"]["usn_top"], R["intl"]["usn_us_towns"])
print(P.head(15)[["place", "ships", "first", "last", "nation", "coast_km"]].to_string())
