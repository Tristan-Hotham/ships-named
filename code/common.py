"""Shared paths and helpers for the ships-named study ("HMS Your Town").

Raw inputs (read in place, never modified):
  NAVY  /home/claude/newdata/raw_new8/navy_ships.tsv  Wikidata (CC0): ships operated by the Royal Navy and the US Navy,
        one row per ship and significant event (P793): item, label, operator, class, launch, commission and
        decommission dates (P729/P730 where present), event label, named after (P138) item, sitelinks.
  NAMED /home/claude/newdata/raw_new8/ships_named.tsv  Wikidata (CC0): ships of any operator with P138 "named after" a
        place that has coordinates: ship, class, operator, flag, dates, events, the place, its coordinates, country and type.
  UK    /home/claude/newdata/raw_new8/uk_settlements.tsv  Wikidata (CC0): UK settlements with coordinates, population, type.
  GEO   /home/claude/newdata/raw/geo/  Natural Earth (public domain) for the static figures.
  FONTS /home/claude/ref/fonts; the Inked World lettering fonts in fonts/ttf
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("SN_RAW", "/home/claude/newdata/raw_new8")
GEO = os.environ.get("SN_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("SN_FONTS", "/home/claude/ref/fonts")
INKFONTS = os.path.join(ROOT, "fonts", "ttf")
DATA = os.path.join(ROOT, "data")
WORK = os.environ.get("SN_WORK", "/home/claude/work/new8/ships-named/work")
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "ships-named"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# fate groups, from the ship's significant events (P793) and dates, in order of precedence
FATES = [("lost", "Sunk, wrecked or destroyed", "#A3261B"), ("captured", "Captured or surrendered", "#7A3E8C"),
         ("broken", "Broken up or scrapped", "#6E604E"), ("sold", "Sold or transferred", "#D9A21E"),
         ("decomm", "Decommissioned, fate not recorded", "#9DB0A0"), ("service", "In service", "#3D6E9E"),
         ("unknown", "Fate not recorded", "#FFFDF6")]
FATE_NAME = {k: n for k, n, c in FATES}
FATE_COL = {k: c for k, n, c in FATES}
EV_FATE = {"sinking": "lost", "shipwrecking": "lost", "scuttling": "lost", "destruction": "lost", "torpedo attack": "lost",
           "ship abandonment": "lost", "explosion": "lost", "foundering": "lost", "capture": "captured", "capitulation": "captured",
           "ship breaking": "broken", "scrapping": "broken", "sale": "sold", "transfer": "sold", "ship disposal": "sold",
           "ship decommissioning": "decomm", "service retirement": "decomm", "striking": "decomm"}

def hav(a, b):
    """Great-circle distance in km between (lat, lon) pairs."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1, math.sqrt(h)))


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "word": return NUMWORD.get(int(v), f"{int(v):,}")
    raise ValueError(f)


NUMWORD = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
           11: "eleven", 12: "twelve"}
KEEP = {"DOI_URL", "BLOG_URL", "DOI"}


def fill(t, R):
    t = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP or m.group(1).startswith("IMG") else fmt(get(R, m.group(1)), m.group(3)), t)
    return t


def check_visible(t):
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, bad
