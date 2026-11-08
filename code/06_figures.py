"""Step 6: figures for the blog (release/blog/b_*), paper (release/paper/f_*), page (img/) and header.png."""
import pandas as pd
import matplotlib.patheffects as pe
from figstyle import *

R = jload(f"{DATA}/results.json")
P = pd.read_csv(f"{DATA}/places.csv")
M = pd.read_csv(f"{DATA}/rn_ships.csv")
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper"); IM = os.path.join(ROOT, "img")
for d in (BL, PA, IM): os.makedirs(d, exist_ok=True)
HALO = [pe.withStroke(linewidth=3.2, foreground=SEAC)]
HALOP = [pe.withStroke(linewidth=3.2, foreground=PAPER)]
ERAS = [("before 1800", "#6E604E"), ("1800s", "#D9A21E"), ("1900 to 1945", "#A3261B"), ("since 1946", "#3D6E9E")]
ERAC = dict(ERAS)


def save(fig, name, page=True, jpg=False):
    if jpg:
        fig.savefig(f"{WORK}/tmp.png", dpi=200, facecolor=fig.get_facecolor())
        Image.open(f"{WORK}/tmp.png").convert("RGB").save(os.path.join(PA, "f_" + name + ".jpg"), quality=85, optimize=True); os.remove(f"{WORK}/tmp.png")
    else:
        fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    if page: fig.savefig(os.path.join(IM, name + ".png"), dpi=116.67, facecolor=fig.get_facecolor())
    plt.close(fig)


def title(fig, t, sub=None, y=0.965, x=0.03):
    fig.text(x, y, t, fontproperties=DISP, fontsize=24, color=INK, va="top")
    if sub: fig.text(x, y - 0.5 / fig.get_figheight(), sub, fontproperties=FELLI, fontsize=15, color=MUT, va="top")


def credit(fig, t="Data: Wikidata (CC0), Natural Earth · maps.tristanhotham.com/ships-named", y=0.012):
    fig.text(0.97, y, t, fontsize=9, color=MUT, ha="right", va="bottom")


def size(n): return 26 + 46 * n


# label positions (lon, lat, ha): every label sits on the sea, beside its town
LABELS = {"Newcastle upon Tyne": (-0.2, 55.35, "left"), "Glasgow": (-6.9, 56.05, "right"), "Scarborough": (0.35, 54.45, "left"),
          "London": (1.75, 51.95, "left"), "Gloucester": (-5.0, 51.38, "right"), "York": (0.2, 54.1, "left"),
          "Falmouth": (-4.85, 49.9, "left"), "Pembroke": (-6.3, 51.75, "right"), "Chatham": (1.8, 51.5, "left"), "Maidstone": (1.6, 51.08, "left"),
          "Liverpool": (-3.65, 53.75, "right"), "Bristol": (-5.0, 51.12, "right"), "Southampton": (-0.9, 50.35, "left"), "Weymouth": (-2.4, 50.25, "right")}


def placemap(ax, label=True, fs=11):
    ukmap(ax)
    for era, c in ERAS + [("nan", "#FFFDF6")]:  # nan: no ship of the town has a year
        d = P[P.era.fillna("nan") == era]
        x, y = ukproj(d.lon, d.lat)
        ax.scatter(x, y, s=size(d.ships), c=c, edgecolors=INK, linewidths=0.7, alpha=0.88, zorder=6)
    if label:
        for pl, (lo, la, ha) in LABELS.items():
            r = P[P.place == pl].iloc[0]
            tx, ty = ukproj(lo, la); px, py = ukproj(r.lon, r.lat)
            ax.plot([px, tx], [py, ty], color=INK, lw=0.6, zorder=7)
            ax.text(tx + (0.05 if ha == "left" else -0.05), ty, f"{pl.replace(' upon Tyne', '')} {r.ships}", fontsize=fs, ha=ha, va="center", color=INK, path_effects=HALO, zorder=8)


# 1. the map
fig = plt.figure(figsize=(10, 12), facecolor=PAPER)
title(fig, "HMS Your Town", f"{R['source']['towns']} British towns and cities that gave their name to {R['source']['matched']} Royal Navy ships", y=0.975)
ax = fig.add_axes([0.02, 0.07, 0.96, 0.83]); placemap(ax)
lax = fig.add_axes([0, 0, 1, 1], zorder=10); lax.set_axis_off(); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
x = 0.04
lax.text(x, 0.045, "Latest ship:", fontsize=11, color=INK, va="center"); x += 0.15
for era, c in ERAS + [("year not known", "#FFFDF6")]:
    lax.scatter([x], [0.045], s=110, c=c, edgecolors=INK, linewidths=0.7); lax.text(x + 0.015, 0.045, era, fontsize=11, va="center"); x += 0.035 + 0.0105 * len(era)
for i, n in enumerate((1, 5, 9)):
    lax.scatter([0.06 + 0.11 * i], [0.018], s=size(n), facecolors="none", edgecolors=INK); lax.text(0.085 + 0.11 * i, 0.018, f"{n} ship{'s' if n > 1 else ''}", fontsize=10, va="center")
credit(fig, y=0.004)
save(fig, "map", jpg=True)

# 2. eras
E = pd.DataFrame(R["era"]); E = E[E.ships >= 20]
fig = plt.figure(figsize=(12, 6.2), facecolor=PAPER)
title(fig, "Town names rose, fell and rose again", "Share of Royal Navy ships in Wikidata that bore a British town's name, by the half century they were commissioned")
ax = fig.add_axes([0.08, 0.13, 0.88, 0.64]); ax.set_facecolor(PAPER); spines(ax)
ax.bar(E.start + 25, E.pct, width=42, color="#A3261B", edgecolor=INK, lw=0.6)
for r in E.itertuples():
    ax.text(r.start + 25, r.pct + 0.8, f"{r.town} of {r.ships:,}", ha="center", fontsize=9.5, color=MUT)
ax.set_xticks(E.start + 25); ax.set_xticklabels([f"{s} to {s + 49}" for s in E.start], fontsize=9.5); ax.set_ylabel("% of ships with a town's name")
ax.grid(axis="y", color=RULE, lw=0.7); ax.set_axisbelow(True); ax.set_ylim(0, max(E.pct) + 6)
credit(fig)
save(fig, "eras")

# 3. top towns
T = P.head(20).iloc[::-1]
fig = plt.figure(figsize=(12, 8), facecolor=PAPER)
title(fig, "The most-named towns", "Royal Navy ships named after each town, coloured by the era of each ship")
ax = fig.add_axes([0.22, 0.11, 0.74, 0.74]); ax.set_facecolor(PAPER); spines(ax)
for i, r in enumerate(T.itertuples()):
    ships = M[M.place == r.place].sort_values("year")
    for k, s in enumerate(ships.itertuples()):
        y = s.year
        era = "before 1800" if y < 1800 else "1800s" if y < 1900 else "1900 to 1945" if y <= 1945 else "since 1946" if y == y else None
        ax.barh(i, 1, left=k, color=ERAC.get(era, "#FFFDF6"), edgecolor=INK, lw=0.6)
ax.set_yticks(range(len(T))); ax.set_yticklabels([p.replace(" upon Tyne", "") for p in T.place], fontsize=11)
ax.set_xlabel("ships"); ax.set_xlim(0, 10)
for era, c in ERAS: ax.barh([-5], [0], color=c, label=era)
ax.barh([-5], [0], color="#FFFDF6", edgecolor=INK, label="year unknown"); ax.set_ylim(-0.6, len(T) - 0.4)
ax.legend(frameon=False, loc="lower right", fontsize=10.5)
credit(fig)
save(fig, "top")

# 4. fates
F = R["fates"]
fig = plt.figure(figsize=(12, 5.6), facecolor=PAPER)
title(fig, "What happened to them? Mostly, Wikidata does not say", f"Recorded fate of the {R['source']['matched']} town-named ships", y=0.95)
ax = fig.add_axes([0.03, 0.36, 0.94, 0.3]); ax.set_axis_off()
left = 0
for k, n, c in FATES:
    v = F[k]
    if not v: continue
    ax.barh(0, v, left=left, color=c, edgecolor=INK, lw=0.7)
    if v >= 10: ax.text(left + v / 2, 0, f"{v}", ha="center", va="center", fontsize=12, color="#FFFDF6" if k in ("lost", "broken", "captured", "service") else INK)
    left += v
ax.set_xlim(0, left); ax.set_ylim(-0.6, 0.6)
k_ = 0
for k, n, c in FATES:
    if not F[k]: continue
    x, y = 0.03 + 0.48 * (k_ % 2), 0.24 - 0.065 * (k_ // 2); k_ += 1
    fig.patches.append(plt.Rectangle((x, y - 0.018), 0.018, 0.036, facecolor=c, edgecolor=INK, lw=0.6, transform=fig.transFigure, figure=fig))
    fig.text(x + 0.026, y, f"{n}: {F[k]}", fontsize=11, va="center")
credit(fig, y=0.005)
save(fig, "fates")

# 5. international
I = pd.DataFrame(R["intl"]["navies"]).head(10).iloc[::-1]
fig = plt.figure(figsize=(12, 6.4), facecolor=PAPER)
title(fig, "Other navies name ships after towns too", "Ships whose Wikidata entry names a town or city they honour, by navy (all places in brackets)")
ax = fig.add_axes([0.28, 0.1, 0.68, 0.7]); ax.set_facecolor(PAPER); spines(ax)
ax.barh(range(len(I)), I.places, color="#E2D3AE", edgecolor=INK, lw=0.5)
ax.barh(range(len(I)), I.towns, color="#3D6E9E", edgecolor=INK, lw=0.5)
for i, r in enumerate(I.itertuples()):
    ax.text(r.places + 4, i, f"{r.towns} towns ({r.places} places)" + (f"; most: {r.top_town} ({r.top_n})" if r.top_n > 1 else ""), va="center", fontsize=9.5, color=INK)
ax.set_yticks(range(len(I))); ax.set_yticklabels(I.navy, fontsize=10.5); ax.set_xlim(0, max(I.places) * 1.75)
credit(fig)
save(fig, "intl")

# header
fig = plt.figure(figsize=(12, 6.3), facecolor=PAPER)
fig.text(0.04, 0.88, "HMS Your Town", fontproperties=DISP, fontsize=50, color=INK, va="top")
fig.text(0.04, 0.72, f"{R['source']['towns']} British towns, {R['source']['matched']} warships", fontproperties=FELLI, fontsize=24, color=MUT, va="top")
fig.text(0.04, 0.6, "Which towns gave their name to\na Royal Navy ship, how often,\nand what became of them", fontsize=15, color=INK, va="top", linespacing=1.5)
fig.text(0.04, 0.06, "Dr Tristan Hotham · maps.tristanhotham.com/ships-named", fontsize=11, color=MUT)
ax = fig.add_axes([0.5, 0.0, 0.5, 1.0]); placemap(ax, label=False)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=PAPER); plt.close(fig)
print("figures done")
