#!/usr/bin/env python3
"""Merge harvested posts, keep question-like on-topic posts, rank by score per subreddit.
Usage: select.py [per_sub_cap]  -> writes candidates.tsv"""
import json, glob, os, re, sys, collections
D = os.path.dirname(os.path.abspath(__file__))

posts = {}
for f in glob.glob(D + "/data2/*.jsonl"):
    for line in open(f):
        try:
            p = json.loads(line)
        except Exception:
            continue
        posts[p["id"]] = p
# RSS search results (no score); scores filled from ids lookup file if present
rss_scores = {}
if os.path.exists(D + "/rss_scores.jsonl"):
    for line in open(D + "/rss_scores.jsonl"):
        p = json.loads(line); rss_scores[p["id"]] = p
if os.path.exists(D + "/rss_posts.jsonl"):
    for line in open(D + "/rss_posts.jsonl"):
        r = json.loads(line)
        if r["id"] in posts:
            posts[r["id"]].setdefault("queries", []).append(r["query"]); continue
        s = rss_scores.get(r["id"], {})
        posts[r["id"]] = {"id": r["id"], "title": r["title"], "subreddit": r["sub"],
                          "score": s.get("score", -1), "num_comments": s.get("num_comments", -1),
                          "link_flair_text": s.get("link_flair_text"), "queries": [r["query"]],
                          "created_utc": s.get("created_utc", 0)}

QWORDS = r"^(how|why|what|whats|what's|which|is|are|can|could|should|does|do|did|will|would|where|when|who|help|need|any|anyone|anybody|looking for|advice|recommend|best|question|eli5|confused|trying to|new to|beginner|noob|newbie|struggling|seeking|i need|i want to|i'm trying|im trying|am i|has anyone|have you|thoughts on|opinions on|explain|understanding|difference between|getting started|where to start|tips)"
QFLAIR = {"QUESTION", "Question", "Troubleshooting", "DIY Projects/questions", "question", "Help", "help"}

def is_question(p):
    t = p["title"].strip().lower()
    if "?" in t:
        return True
    if re.match(QWORDS, t):
        return True
    if (p.get("link_flair_text") or "") in QFLAIR:
        return True
    return False

OFF = re.compile(r"(resume|internship|salary|job offer|interview at|hiring|\bmeme\b|\bfor sale\b|\bwtb\b|\bwts\b|giveaway|callsign|vanity|license exam|exam pool|study guide|technician exam|general exam|extra exam|hamcram|test session|\bve\b session|net control|\bnet\b tonight|contest|field day|pota|sota|qsl|dxcc|award|club meeting|swap ?meet|hamfest)", re.I)

if __name__ == "__main__":
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    by = collections.defaultdict(list)
    for p in posts.values():
        if not is_question(p):
            continue
        by[p["subreddit"]].append(p)
    rows = []
    for sub, L in by.items():
        L.sort(key=lambda p: -(p.get("score") or 0))
        for p in L[:cap]:
            rows.append(p)
    with open(D + "/candidates.tsv", "w") as fh:
        for p in rows:
            fh.write("\t".join([p["id"], p["subreddit"], str(p.get("score")), str(p.get("num_comments")),
                                (p.get("link_flair_text") or ""), ",".join(p.get("queries", [])),
                                "OFF?" if OFF.search(p["title"]) else "",
                                p["title"].replace("\t", " ").replace("\n", " ")]) + "\n")
    tot = collections.Counter(p["subreddit"] for p in posts.values())
    q = {s: len(L) for s, L in by.items()}
    for s in sorted(tot):
        print(f"{s:22s} posts {tot[s]:6d}  questions {q.get(s,0):6d}")
    print("candidates", len(rows))
