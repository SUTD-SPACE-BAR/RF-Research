#!/usr/bin/env python3
"""Fetch SE API question lists into JSON files. Usage: fetch.py site tag sort page [name]"""
import sys, json, time, gzip, urllib.request, urllib.parse, os

FILTER = "!-(2.P7VfO_0q5wNbWMLG*.yT"
BASE = "https://api.stackexchange.com/2.3/questions"

def fetch(site, tag, sort, page, pagesize=100):
    q = {"order": "desc", "sort": sort, "site": site, "pagesize": pagesize,
         "page": page, "filter": FILTER}
    if tag:
        q["tagged"] = tag
    url = BASE + "?" + urllib.parse.urlencode(q, safe=";")
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw)

if __name__ == "__main__":
    jobs = [l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    for j in jobs:
        site, tag, sort, page = j[0], j[1], j[2], int(j[3])
        tag = "" if tag == "-" else tag
        fn = f"q_{site}_{(tag or 'ALL').replace(';','+')}_{sort}_p{page}.json"
        if os.path.exists(fn):
            continue
        try:
            d = fetch(site, tag, sort, page)
        except Exception as e:
            print("ERR", fn, e); time.sleep(2); continue
        json.dump(d, open(fn, "w"))
        print(fn, len(d.get("items", [])), "quota", d.get("quota_remaining"), "backoff", d.get("backoff"))
        time.sleep(max(1.0, d.get("backoff", 0) or 0))
