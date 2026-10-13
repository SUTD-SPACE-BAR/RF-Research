#!/usr/bin/env python3
"""Look up score/num_comments for RSS-found posts via Arctic Shift /api/posts/ids (read-only)."""
import json, os, time, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
have = set()
if os.path.exists(D + "/rss_scores.jsonl"):
    have = {json.loads(l)["id"] for l in open(D + "/rss_scores.jsonl")}
ids = []
for l in open(D + "/rss_posts.jsonl"):
    i = json.loads(l)["id"]
    if i not in have and i not in ids:
        ids.append(i)
print("to look up", len(ids))
with open(D + "/rss_scores.jsonl", "a") as fh:
    for k in range(0, len(ids), 100):
        chunk = ids[k:k + 100]
        url = "https://arctic-shift.photon-reddit.com/api/posts/ids?" + urllib.parse.urlencode(
            {"ids": ",".join(chunk), "fields": "id,score,num_comments,link_flair_text,created_utc,subreddit,title"})
        for t in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rf-kb-research/0.1"}), timeout=120) as r:
                    d = json.load(r)
                for p in d.get("data") or []:
                    fh.write(json.dumps(p) + "\n")
                break
            except Exception as e:
                print("retry", e); time.sleep(10 * (t + 1))
        time.sleep(1.5)
print("done")
