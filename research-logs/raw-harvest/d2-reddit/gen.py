#!/usr/bin/env python3
"""Build gaps/D2-reddit.md from class_*.tsv (hand classification) + harvested metadata + hand-written sections."""
import json, glob, os, collections, datetime
D = os.path.dirname(os.path.abspath(__file__))
OUTF = "/Users/marcusquek/Documents/RF Physics/gaps/D2-reddit.md"

meta = {}
for f in glob.glob(D + "/data2/*.jsonl"):
    for l in open(f):
        try:
            p = json.loads(l); meta[p["id"]] = p
        except Exception:
            pass
if os.path.exists(D + "/rss_scores.jsonl"):
    for l in open(D + "/rss_scores.jsonl"):
        p = json.loads(l); meta.setdefault(p["id"], p)
rsssub = {}
if os.path.exists(D + "/rss_posts.jsonl"):
    for l in open(D + "/rss_posts.jsonl"):
        r = json.loads(l); rsssub[r["id"]] = r["sub"]

rows, seen = [], set()
for f in sorted(glob.glob(D + "/class_*.tsv")):
    for l in open(f):
        l = l.rstrip("\n")
        if not l.strip() or l.startswith("#"):
            continue
        parts = l.split("\t")
        while len(parts) < 6:
            parts.append("")
        pid, q, dom, st, page, note = parts[:6]
        if pid in seen:
            continue
        seen.add(pid)
        m = meta.get(pid, {})
        sub = m.get("subreddit") or rsssub.get(pid, "?")
        rows.append(dict(id=pid, q=q, dom=dom, st=st, page=page, note=note, sub=sub,
                         score=m.get("score", ""), com=m.get("num_comments", ""),
                         yr=datetime.datetime.utcfromtimestamp(int(m["created_utc"])).year if m.get("created_utc") else ""))

STN = {"C": "covered", "P": "partial", "M": "missing", "O": "out-of-scope"}
inscope = [r for r in rows if r["st"] in "CPM"]

def tab(counter_key):
    t = collections.defaultdict(collections.Counter)
    for r in inscope:
        t[r[counter_key]][r["st"]] += 1
    return t

def pct(a, b):
    return f"{100*a/b:.1f} %" if b else "–"

out = []
tot = collections.Counter(r["st"] for r in inscope)
n = len(inscope)
out.append(f"**{len(rows)} questions harvested and classified: {n} in scope — {tot['C']} covered ({pct(tot['C'],n)}) · "
           f"{tot['P']} partial ({pct(tot['P'],n)}) · {tot['M']} missing ({pct(tot['M'],n)}); plus "
           f"{len(rows)-n} career questions (out of scope for the physics KB, kept for §4).**\n")
out.append("| Subreddit | covered | partial | missing | in scope | career (O) |\n|---|---|---|---|---|---|")
bs = tab("sub")
oc = collections.Counter(r["sub"] for r in rows if r["st"] == "O")
for s in sorted(set(r["sub"] for r in rows), key=lambda s: -sum(bs[s].values())):
    c = bs[s]
    out.append(f"| r/{s} | {c['C']} | {c['P']} | {c['M']} | {sum(c.values())} | {oc.get(s,0)} |")
out.append("")
out.append("| Domain | covered | partial | missing | total | covered share |\n|---|---|---|---|---|---|")
bd = tab("dom")
def dkey(d):
    return (0, int(d)) if d.isdigit() else (1, d)
for d in sorted(bd, key=dkey):
    c = bd[d]; t = sum(c.values())
    out.append(f"| {d} | {c['C']} | {c['P']} | {c['M']} | {t} | {pct(c['C'],t)} |")
summary = "\n".join(out)

table = ["| # | question (paraphrased) | URL | subreddit | score | comments | domain | status | KB page | note |",
         "|---|---|---|---|---|---|---|---|---|---|"]
order = sorted(rows, key=lambda r: (r["sub"].lower(), -(r["score"] if isinstance(r["score"], int) else 0)))
for i, r in enumerate(order, 1):
    url = f"https://www.reddit.com/r/{r['sub']}/comments/{r['id']}/"
    q = r["q"].replace("|", "/")
    table.append(f"| {i} | {q} | {url} | {r['sub']} | {r['score']} | {r['com']} | {r['dom']} | {STN.get(r['st'], r['st'])} | {r['page'].replace('|','/')} | {r['note'].replace('|','/')} |")

head = open(D + "/sec_head.md").read() if os.path.exists(D + "/sec_head.md") else "# D2 — Reddit gap analysis (W4-D2)\n\nStatus: in progress.\n"
mid = open(D + "/sec_mid.md").read() if os.path.exists(D + "/sec_mid.md") else "## 2–4. (in progress)\n"
with open(OUTF, "w") as fh:
    fh.write(head.rstrip() + "\n\n## 1. Summary\n\n" + summary + "\n\n" + mid.rstrip() + "\n\n## 5. Full table\n\n"
             "Rows sorted by subreddit, then score. Score/comments are Arctic Shift archive values at harvest time "
             "(2026-09-29). Domain LRN = learning-path/roadmap question; CAR = career. Status is judged against the KB "
             "as of the re-check date in §0.\n\n" + "\n".join(table) + "\n")
print(len(rows), "rows;", dict(tot), "missing meta:", sum(1 for r in rows if r["score"] == ""))
