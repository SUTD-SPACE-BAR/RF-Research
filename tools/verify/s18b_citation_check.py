"""W5-S18b: check bibliographic data of references marked "cited from knowledge" against Crossref.

For every numbered reference line containing "cited from knowledge" (or "from memory") in the free
domains, query the Crossref REST API (api.crossref.org, the DOI registration agency's metadata),
and print the best match's year / volume / issue / pages next to the KB line, plus an automatic
comparison (volume, first page and year must appear in the KB line).

Run: python3 tools/verify/s18b_citation_check.py [domain-prefix ...]   (from any directory: paths are built from
__file__, W6-F5 2026-10-14; before that the script only worked from the repo root)
Output is also written to tools/verify/s18b_citation_check_output.txt.
Needs network access. Crossref is authoritative for journal bibliographic data, not for content.
"""
import glob, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repo root (tools/verify/ -> RF Physics/)

SKIP = ("16-",)          # 16 owned by W5-S11 on 2026-10-13 (02 and 03 freed later that day)
PAT = re.compile(r"cited from knowledge|from memory", re.I)
prefixes = sys.argv[1:] or None
out = []


def crossref(q):
    url = ("https://api.crossref.org/works?rows=3&select=title,volume,issue,page,issued,"
           "container-title,author,DOI&query.bibliographic=" + urllib.parse.quote(q[:300]))
    req = urllib.request.Request(url, headers={"User-Agent": "rf-kb-citation-check/1.0 (mailto:none)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]["items"]


for p in sorted(os.path.relpath(x, ROOT) for x in glob.glob(os.path.join(ROOT, "kb", "*", "*.md"))):
    dom = p.split("/")[1]
    if dom.startswith(SKIP):
        continue
    if prefixes and not any(dom.startswith(x) for x in prefixes):
        continue
    raw = open(os.path.join(ROOT, p), encoding="utf-8").read().split("\n")
    refs = []                      # (line number, joined reference text incl. wrapped lines)
    for i, l in enumerate(raw):
        if re.match(r"\s*\d+\.\s", l):
            j, txt = i + 1, l
            while j < len(raw) and raw[j].startswith("   ") and raw[j].strip() and not re.match(r"\s*\d+\.\s", raw[j]):
                txt += " " + raw[j].strip(); j += 1
            refs.append((i + 1, txt))
    for ln, line in refs:
        if not PAT.search(line):
            continue
        q = re.sub(r"[*_`\[\]()]", " ", line)
        q = re.sub(r"https?://\S+", " ", q)
        q = re.split(r"\(peer-reviewed|\(textbook|\(standard|\(app note", q)[0]
        try:
            items = crossref(q)
        except Exception as e:  # network or API failure
            out.append(f"{p}:{ln} ERROR {e}")
            continue
        out.append(f"\n{p}:{ln}\n  KB: {line.strip()[:260]}")
        for it in items[:1]:
            yr = it.get("issued", {}).get("date-parts", [[None]])[0][0]
            vol, iss, pg = it.get("volume", ""), it.get("issue", ""), it.get("page", "")
            title = (it.get("title") or [""])[0]
            jn = (it.get("container-title") or [""])[0]
            au = ", ".join(a.get("family", "") for a in it.get("author", [])[:3])
            first = pg.split("-")[0] if pg else ""
            match = all(str(x) in line for x in (yr, vol, first) if x)
            out.append(f"  CR: {au} ({yr}) '{title[:90]}' {jn} {vol}({iss}):{pg} doi:{it.get('DOI')}")
            out.append(f"  AUTO: {'consistent' if match else 'CHECK'}")
        time.sleep(0.3)

txt = "\n".join(out)
print(txt)
open(os.path.join(HERE, "s18b_citation_check_output.txt"), "w", encoding="utf-8").write(txt + "\n")
