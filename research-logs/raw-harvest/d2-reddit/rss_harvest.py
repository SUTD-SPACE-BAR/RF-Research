#!/usr/bin/env python3
"""Read-only: Reddit subreddit search RSS (sort=top, t=all), respecting x-ratelimit headers.
Output: rss/<sub>__<q>.xml and rss_posts.jsonl (id,title,link,published,sub,query). Resumable."""
import os, re, json, time, urllib.request, urllib.parse, html

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) rf-kb-research/0.1 (read-only gap analysis)"
D = os.path.dirname(os.path.abspath(__file__))
OUT = D + "/rss"
os.makedirs(OUT, exist_ok=True)

Q = {
 'rocketry': ['telemetry', 'GPS', 'LoRa', 'radio', 'antenna', 'tracker'],
 'HighPowerRocketry': ['telemetry', 'GPS', 'tracker'],
 'meshtastic': ['range', 'antenna', 'settings', 'best antenna'],
 'PrintedCircuitBoard': ['RF', 'antenna', 'impedance', 'ground plane', 'LoRa', 'stitching', 'coplanar', '50 ohm'],
 'ECE': ['RF', 'antenna', 'analog', 'electromagnetics', 'microwave'],
 'ElectricalEngineering': ['RF', 'antenna', 'RF engineer', 'impedance', 'radar', 'EMI', 'analog design'],
 'amateurradio': ['antenna', 'SWR', 'coax', 'balun', 'propagation', 'SDR', 'dipole', 'noise', 'NanoVNA', 'Meshtastic', 'vertical', 'EFHW', 'ground', 'Yagi', 'tuner', 'feedline', 'learn'],
 'RTLSDR': ['antenna', 'beginner', 'gain', 'sample rate', 'LNA', 'noise'],
 'rfelectronics': ['learn', 'book', 'career', 'beginner'],
 'AskElectronics': ['antenna', 'RF', 'radio', 'impedance matching', 'coax', 'oscillator', 'crystal', 'SWR', 'transmitter', 'receiver', 'SDR', 'EMI', 'ferrite', 'balun', 'ground plane', 'LNA', 'GPS', 'radar', '433MHz', 'LoRa', 'spectrum analyzer', 'VNA', 'bandpass', 'PLL', 'FM transmitter', 'wifi antenna', 'shielding', 'interference', 'noise'],
}

def fetch(url):
    for i in range(8):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
                rem = float(r.headers.get("x-ratelimit-remaining", "1") or 1)
                reset = float(r.headers.get("x-ratelimit-reset", "60") or 60)
                return body, rem, reset
        except urllib.error.HTTPError as e:
            reset = float(e.headers.get("x-ratelimit-reset", "60") or 60)
            print(f"  HTTP {e.code}; waiting {reset+5:.0f}s", flush=True)
            time.sleep(reset + 5)
        except Exception as e:
            print("  err", e, flush=True); time.sleep(30)
    return None, 0, 60

def parse(body):
    out = []
    for e in body.split("<entry>")[1:]:
        t = re.search(r"<title>(.*?)</title>", e, re.S)
        l = re.search(r'<link href="(.*?)"', e)
        i = re.search(r"<id>(t3_[a-z0-9]+)</id>", e)
        p = re.search(r"<published>(.*?)</published>", e)
        if t and l and i:
            out.append({"id": i.group(1)[3:], "title": html.unescape(t.group(1)), "link": l.group(1),
                        "published": p.group(1) if p else ""})
    return out

if __name__ == "__main__":
    with open(D + "/rss_posts.jsonl", "a") as fh:
        for sub, qs in Q.items():
            for q in qs:
                fn = f"{OUT}/{sub}__{q.replace(' ', '_')}.xml"
                if os.path.exists(fn):
                    continue
                url = (f"https://www.reddit.com/r/{sub}/search.rss?" +
                       urllib.parse.urlencode({"q": q, "restrict_sr": "on", "sort": "top", "t": "all", "limit": 100}))
                body, rem, reset = fetch(url)
                if body is None:
                    print("FAILED", sub, q, flush=True); continue
                open(fn, "w").write(body)
                ents = parse(body)
                for x in ents:
                    x["sub"] = sub; x["query"] = q
                    fh.write(json.dumps(x) + "\n")
                fh.flush()
                print(f"{sub} / {q}: {len(ents)} (remaining {rem}, reset {reset})", flush=True)
                time.sleep((reset + 3) if rem < 1 else 3)
