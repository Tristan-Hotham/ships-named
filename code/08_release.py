"""Step 8: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24052719, https://doi.org/10.5281/zenodo.24052719 and https://blog.tristanhotham.com/2026/10/31/ships-named/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
shutil.copy(f"{DATA}/results.json", os.path.join(ROOT, "results.json"))  # top-level copy
REL = os.path.join(ROOT, "release"); NAME = "Hotham_HMS_Your_Town"
R["nations"]["Northern_Ireland"] = R["nations"]["Northern Ireland"]
assert R["lancaster"]["ships"] == 4 and R["lancaster"]["years"][2] == 1944 and R["barrow"]["ships"] == 0 and R["era"][7]["pct"] > 20 and R["era"][4]["pct"] < 3
assert 140 <= R["intl"]["navies"][0]["towns"] <= 160 and 340 <= R["intl"]["navies"][0]["places"] <= 360

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
S = R["source"]
meta = {"title": "HMS Your Town: which British towns have had a warship named after them?",
        "slug": "ships-named",
        "excerpt": f"I matched every Royal Navy ship in Wikidata to the British towns they are named after: {S['matched']} ships for {S['towns']} towns. Gloucester and Newcastle have had nine each; Lancaster four; Barrow none.",
        "seo_description": f"{S['towns']} British towns and cities that gave their name to {S['matched']} Royal Navy warships, from 1650 to today, mapped from Wikidata.",
        "tags": ["maps", "history", "Royal Navy", "ships", "place names", "Wikidata", "data visualisation", "naval history"],
        "header_alt": "Title card reading 'HMS Your Town' on parchment beside a map of Great Britain and Northern Ireland with circles on the towns that gave their name to Royal Navy ships, sized by the number of ships."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
OWN = ["rn_ships.csv", "places.csv", "international.csv", "results.json", "points.json"]
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith(".pyc") or fn == "__pycache__" or fn.endswith(".png"):
            continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in OWN:
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("``", "\u201c").replace("''", "\u201d")
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab)
zmeta = {"title": "HMS Your Town: British Towns and the Royal Navy Ships Named after Them",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/ships-named/}}.</p><p>Sources: Wikidata (CC0); Natural Earth (public domain). Derived data and text CC BY 4.0, code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["naval history", "ship names", "Royal Navy", "toponymy", "Wikidata", "place names", "maps", "open data"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
