"""Step 7: the paper. Fills code/paper_template.tex from data/results.json, adds tables and compiles with xelatex.
Output: release/paper/Hotham_News_Speed.pdf and .tex, beside the f_* figures. The DOI stays as a placeholder."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_HMS_Your_Town"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

P = pd.read_csv(f"{DATA}/places.csv")
R["nations"]["Northern_Ireland"] = R["nations"]["Northern Ireland"]
assert R["era"][4]["pct"] < 3 and R["era"][5]["pct"] < 3 and R["era"][3]["start"] == 1750
assert {t["place"] for t in R["top"] if t["ships"] == 8} == {"Glasgow"}
assert {t["place"] for t in R["top"] if t["ships"] == 7} == {"Chatham", "Falmouth", "London", "Maidstone", "Pembroke", "Scarborough", "York"}
assert {t["place"] for t in R["top"] if t["ships"] == 9} == {"Gloucester", "Newcastle upon Tyne"}
rows = "".join(f"{tex(r.place)} & {r.nation} & {int(r.ships)} & {'' if pd.isna(r.first) else int(r.first)} & {'' if pd.isna(r.last) else int(r.last)} & {'yes' if r.title else ''}\\\\\n" for r in P.itertuples())
TT = ("{\\footnotesize\\begin{longtable}{llrrrl}\\caption{Every British town or city with a Royal Navy ship of its name in the data, by number of ships. Title: the name is also a noble title.}\\\\"
      "\\toprule Town & Nation & Ships & First & Latest & Title\\\\\\midrule\\endfirsthead\\toprule Town & Nation & Ships & First & Latest & Title\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\usepackage{graphicx,booktabs,float,caption,array,xcolor}", "\\usepackage{graphicx,booktabs,float,caption,array,xcolor,longtable}")
t = t.replace("{{PAGE}}", "\\url{%s}" % PAGE).replace("{{REPO}}", "\\url{%s}" % REPO).replace("{{AI}}", AI)
t = t.replace("{{TABLE_TOP}}", TT)
t = re.sub(r"\{\{(?!DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), t)
assert "{{" not in t and "--" not in t and "\u2014" not in t and "\u2013" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
