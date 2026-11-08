"""House style for the static figures, in the ink of the Inked World: parchment, iron-gall black, vermilion lettering,
hand-tinted colours; the Albers projection for the United States; Natural Earth outlines."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import numpy as np
from PIL import Image
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-Black.ttf" if w == 900 else f"{FD}/Fraunces-Bold.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
HAND = fm.FontProperties(fname=f"{INKFONTS}/MedievalSharp.ttf")
FELL = fm.FontProperties(fname=f"{INKFONTS}/IMFeENrm28P.ttf")
FELLI = fm.FontProperties(fname=f"{INKFONTS}/IMFeGPit28P.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
fm.fontManager.addfont(f"{INKFONTS}/IMFeENrm28P.ttf")
MONO = "IBM Plex Mono"
for f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",):
    if os.path.exists(f):
        fm.fontManager.addfont(f)
plt.rcParams.update({"font.family": [MONO, "Noto Sans CJK JP"], "font.size": 12, "axes.edgecolor": "#6E604E", "axes.labelcolor": "#2B2119",
                     "xtick.color": "#6E604E", "ytick.color": "#6E604E", "text.color": "#2B2119"})
PAPER, PAPER2, INK, MUT, RED, SEA, RULE = "#F6EED8", "#F3E5BF", "#2B2119", "#6E604E", "#A3261B", "#E3EAE6", "#E2D3AE"
LANDC = "#ECD9AC"
SEAC = "#DFE6E1"


def eqearth(lon, lat):
    """Equal Earth projection (Savric, Patterson and Jenny 2018), unit sphere."""
    lon = np.radians(np.asarray(lon, float)); lat = np.radians(np.asarray(lat, float))
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    M = np.sqrt(3) / 2
    th = np.arcsin(M * np.sin(lat))
    t2 = th * th; t6 = t2 ** 3
    x = 2 * np.sqrt(3) * lon * np.cos(th) / (3 * (9 * A4 * t6 * t2 + 7 * A3 * t6 + 3 * A2 * t2 + A1))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


def plate(lon, lat, lat0=0):
    return np.asarray(lon, float) * np.cos(np.radians(lat0)), np.asarray(lat, float)


NE = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
LAND = jload(f"{GEO}/ne_50m_land.geojson")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


NE10 = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
ISLES = [f for f in NE10["features"] if f["properties"].get("ADM0_A3") in ("GBR", "IRL", "IMN")]
EUROPE = [f for f in NE10["features"] if f["properties"].get("ADM0_A3") in ("FRA", "BEL", "NLD", "NOR", "DNK", "DEU")]
LAT0 = 54.5


def ukproj(lon, lat):
    return np.asarray(lon, float) * np.cos(np.radians(LAT0)), np.asarray(lat, float)


def ukmap(ax, ext=(-8.4, 2.0, 49.8, 59.5), fill=LANDC):
    ax.set_facecolor(SEAC)
    for feats, fc, lw in ((EUROPE, "#EFE3C4", 0.3), (ISLES, fill, 0.6)):
        polys = []
        for f in feats:
            for r in rings(f["geometry"]):
                if len(r) < 4: continue
                x, y = ukproj(r[:, 0], r[:, 1]); polys.append(MPoly(np.c_[x, y], closed=True))
        ax.add_collection(PatchCollection(polys, facecolor="none", edgecolor="#6C9FD6", lw=5, alpha=0.18, zorder=1))
        ax.add_collection(PatchCollection(polys, facecolor=fc, edgecolor=INK, lw=lw, zorder=2))
    x, y = ukproj(np.array(ext[:2]), np.array(ext[2:]))
    ax.set_xlim(*x); ax.set_ylim(*y); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_visible(False)


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
