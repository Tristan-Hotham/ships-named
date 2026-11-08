"""Step 5: index.html from code/page_template.html, filled from data/results.json, with the full-screen snippet."""
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
R["nations"]["Northern_Ireland"] = R["nations"]["Northern Ireland"]
M = pd.read_csv(f"{DATA}/rn_ships.csv")
# facts stated in words on the page
lost = {l["label"] for l in R["lost"]}
assert {"HMS Gloucester", "HMS Sheffield", "HMS Coventry"} <= lost
assert R["peak"]["start"] == 1650 and R["era"][4]["pct"] < 5 and R["era"][5]["pct"] < 5 and R["era"][7]["pct"] > 15
for p in ("Chatham", "Falmouth", "Pembroke", "Scarborough"):
    assert next(t["ships"] for t in R["top"] if t["place"] == p) in (7, 8)
assert {t["place"] for t in R["top"] if t["ships"] == 9} == {"Gloucester", "Newcastle upon Tyne"}
assert R["lancaster"]["classes"] == ["1719 Establishment Group", "", "Castle-class corvette", "Type 23 frigate"]
assert R["intl"]["usn_top"].get("Raleigh") and R["intl"]["usn_top"].get("Newport News")
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI)
t = fill(t, R)
left = set(re.findall(r"\{\{([^}]+)\}\}", t))
assert left <= KEEP, left
check_visible(t)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
