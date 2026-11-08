"""Reddit collage (r/dataisbeautiful): British towns with a Royal Navy ship of their name, light paper, labels on the sea.
Run from the study root: python3 reddit/collage.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import pandas as pd
import matplotlib.patheffects as pe
from figstyle import *

R = jload(f"{DATA}/results.json")
P = pd.read_csv(f"{DATA}/places.csv")
HALO = [pe.withStroke(linewidth=4, foreground=SEAC)]
ERAS = [("before 1800", "#6E604E"), ("1800s", "#D9A21E"), ("1900 to 1945", "#A3261B"), ("since 1946", "#3D6E9E")]
LABELS = {"Newcastle upon Tyne": (0.0, 55.6, "left"), "Glasgow": (-7.2, 56.2, "right"), "Scarborough": (0.5, 54.6, "left"),
          "London": (1.9, 52.1, "left"), "Gloucester": (-5.2, 51.2, "right"), "York": (0.4, 54.05, "left"),
          "Falmouth": (-4.85, 49.9, "left"), "Pembroke": (-6.0, 51.55, "right"), "Chatham": (1.9, 51.55, "left"), "Maidstone": (1.75, 51.05, "left"),
          "Liverpool": (-3.7, 53.62, "right"), "Bristol": (-5.2, 50.98, "right"), "Southampton": (-0.9, 50.3, "left"), "Weymouth": (-2.5, 50.2, "right"),
          "Lancaster": (-4.1, 53.98, "right"), "Edinburgh": (-1.2, 56.45, "left")}
fig = plt.figure(figsize=(24, 18), facecolor=PAPER)
fig.text(0.03, 0.975, "HMS Your Town", fontproperties=DISP, fontsize=66, color=INK, va="top")
fig.text(0.03, 0.915, f"{R['source']['towns']} British towns and cities that gave their name to {R['source']['matched']} Royal Navy warships, 1650 to today",
         fontproperties=FELLI, fontsize=28, color=MUT, va="top")
ax = fig.add_axes([0.01, 0.07, 0.56, 0.82]); ukmap(ax)
for era, c in ERAS + [("nan", "#FFFDF6")]:  # nan: no ship of the town has a year
    d = P[P.era.fillna("nan") == era]; x, y = ukproj(d.lon, d.lat)
    ax.scatter(x, y, s=60 + 110 * d.ships, c=c, edgecolors=INK, linewidths=1, alpha=0.9, zorder=6)
for pl, (lo, la, ha) in LABELS.items():
    r = P[P.place == pl].iloc[0]
    tx, ty = ukproj(lo, la); px, py = ukproj(r.lon, r.lat)
    ax.plot([px, tx], [py, ty], color=INK, lw=0.9, zorder=7)
    ax.text(tx + (0.06 if ha == "left" else -0.06), ty, f"{pl.replace(' upon Tyne', '')} {r.ships}", fontsize=19, ha=ha, va="center", color=INK, path_effects=HALO, zorder=8)
# right column on paper
E = pd.DataFrame(R["era"]); E = E[E.ships >= 20]
bx = fig.add_axes([0.62, 0.56, 0.35, 0.235]); bx.set_facecolor(PAPER)
for s_ in ("top", "right"): bx.spines[s_].set_visible(False)
bx.bar(E.start + 25, E.pct, width=42, color="#A3261B", edgecolor=INK, lw=0.8)
bx.set_xticks(E.start + 25); bx.set_xticklabels([f"{s}s" if s % 100 else f"{s}s" for s in E.start], fontsize=13, rotation=0)
bx.tick_params(labelsize=13); bx.set_ylabel("% of ships", fontsize=14)
fig.text(0.62, 0.865, "A fashion that came and went", fontproperties=DISPB, fontsize=27, color=INK, va="bottom")
fig.text(0.62, 0.845, "Share of Royal Navy ships named after a British town,\nby the half century they were commissioned", fontsize=14.5, color=MUT, va="top")
facts = [(f"{R['top'][0]['ships']} ships each", "Gloucester and Newcastle, the most-named towns"),
         (f"{R['lancaster']['ships']} for Lancaster, 0 for Barrow", f"HMS Lancaster in {R['lancaster']['years'][0]}, {R['lancaster']['years'][1]} and {R['lancaster']['years'][3]}, and Lancaster Castle in {R['lancaster']['years'][2]}"),
         (f"{R['coast']['within10_pct']:.0f}% on the coast", "of the towns lie within 10 km of the open sea"),
         (f"{R['source']['fate_known_pct']:.0f}% with a known fate", f"Wikidata rarely records what became of them; {R['fates']['lost']} are recorded as lost")]
y = 0.47
for big, small in facts:
    fig.text(0.62, y, big, fontproperties=DISPB, fontsize=27, color="#A3261B", va="top")
    fig.text(0.62, y - 0.035, small, fontsize=14.5, color=INK, va="top", wrap=True)
    y -= 0.09
lax = fig.add_axes([0, 0, 1, 1], zorder=10); lax.set_axis_off(); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
x = 0.03
lax.text(x, 0.045, "Latest ship named after the town:", fontsize=17, va="center", fontweight="bold"); x += 0.215
for era, c in ERAS + [("year not known", "#FFFDF6")]:
    lax.scatter([x], [0.045], s=260, c=c, edgecolors=INK); lax.text(x + 0.012, 0.045, era, fontsize=17, va="center"); x += 0.026 + 0.0082 * len(era)
lax.text(x + 0.01, 0.045, "Size: ships (1 to 9)", fontsize=17, va="center")
fig.text(0.97, 0.012, "Data: Wikidata (CC0): Royal Navy ships matched strictly to UK towns by name or 'named after'; Natural Earth · Dr Tristan Hotham · maps.tristanhotham.com/ships-named",
         fontsize=13, color=MUT, ha="right", va="bottom")
out = os.path.join(ROOT, "reddit", "ships_named_collage.png")
fig.savefig(out, dpi=110, facecolor=PAPER); print(out, Image.open(out).size)
