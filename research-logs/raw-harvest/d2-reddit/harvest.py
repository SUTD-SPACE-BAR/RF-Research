#!/usr/bin/env python3
"""Read-only harvester of Reddit post metadata from the Arctic Shift archive API.
Pages backwards in time (before=) per subreddit, or per keyword title search in yearly windows.
Writes JSONL per job; resumable (skips jobs whose .done marker exists)."""
import json, os, sys, time, urllib.request, urllib.parse, datetime

BASE = "https://arctic-shift.photon-reddit.com/api/posts/search"
UA = "rf-kb-research/0.1 (read-only gap analysis)"
FIELDS = "id,title,score,num_comments,created_utc,link_flair_text,subreddit"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/data2"
os.makedirs(OUT, exist_ok=True)
DELAY = 1.0

def get(params, tries=6):
    url = BASE + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            if d.get("error"):
                raise RuntimeError(d["error"])
            return d["data"] or []
        except Exception as e:
            wait = 5 * (i + 1)
            print(f"  retry {i} ({e}) wait {wait}s", flush=True)
            time.sleep(wait)
    print("  GIVING UP", url, flush=True)
    return None

def ts(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp())

def page_all(sub, after, before, fh, title=None, max_pages=10**6, flair=None):
    """Page from `before` backwards to `after`."""
    cur = ts(before)
    lo = ts(after)
    n = 0
    for _ in range(max_pages):
        p = {"subreddit": sub, "limit": 100, "before": cur, "after": lo, "fields": FIELDS, "sort": "desc"}
        if title:
            p["title"] = title
        if flair:
            p["link_flair_text"] = flair
        d = get(p)
        if d is None:
            return n, False
        if not d:
            break
        for post in d:
            fh.write(json.dumps(post) + "\n")
        n += len(d)
        newcur = min(int(x["created_utc"]) for x in d)
        if newcur >= cur:
            break
        cur = newcur
        time.sleep(DELAY)
        if len(d) < 100:
            break
    return n, True

def job_all(sub, after="2008-01-01", before="2026-09-30", flair=None):
    name = f"all_{sub}_{after}" + (f"_fl-{flair.replace('/','-').replace(' ','_')}" if flair else "")
    done = f"{OUT}/{name}.done"
    if os.path.exists(done):
        print("skip", name); return
    print("JOB", name, flush=True)
    # split into yearly windows so a crash only loses one window
    y0, y1 = int(after[:4]), int(before[:4])
    allok = True
    for y in range(y1, y0 - 1, -1):
        a = max(after, f"{y}-01-01"); b = min(before, f"{y+1}-01-01")
        wdone = f"{OUT}/{name}_{y}.done"
        if os.path.exists(wdone):
            continue
        with open(f"{OUT}/{name}_{y}.jsonl", "w") as fh:
            n, ok = page_all(sub, a, b, fh, flair=flair)
        print(f"  {sub} {y}: {n}", flush=True)
        if ok:
            open(wdone, "w").close()
        else:
            allok = False
    if allok:
        open(done, "w").close()

def job_title(sub, words, after="2012-01-01", before="2026-09-30", pages_per_year=4):
    for w in words:
        name = f"title_{sub}_{w.replace(' ', '_')}"
        done = f"{OUT}/{name}.done"
        if os.path.exists(done):
            print("skip", name); continue
        print("JOB", name, flush=True)
        tot = 0
        with open(f"{OUT}/{name}.jsonl", "w") as fh:
            for y in range(int(before[:4]), int(after[:4]) - 1, -1):
                a = max(after, f"{y}-01-01"); b = min(before, f"{y+1}-01-01")
                n, ok = page_all(sub, a, b, fh, title=w, max_pages=pages_per_year)
                tot += n
                time.sleep(DELAY)
        print(f"  {name}: {tot}", flush=True)
        open(done, "w").close()

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "dedicated":
        for sub in ["rfelectronics", "antennas", "sdr", "radar", "GNURadio", "LoRa", "HighPowerRocketry",
                    "HamRadio", "DSP"]:
            job_all(sub)
        for fl in ["QUESTION", "ANTENNA", "PROPAGATION"]:
            job_all("amateurradio", flair=fl)
        for fl in ["Troubleshooting", "DIY Projects/questions", "Antennas"]:
            job_all("RTLSDR", flair=fl)
        job_all("meshtastic", after="2024-01-01")
    elif which == "keywords":
        job_title("AskElectronics", ["antenna", "RF", "radio", "impedance", "coax", "SMA", "LoRa", "433",
                                     "oscillator", "crystal", "SWR", "dipole", "transmitter", "receiver",
                                     "SDR", "ground plane", "EMI", "shielding", "ferrite", "balun",
                                     "50 ohm", "VNA", "spectrum analyzer", "PLL", "mixer", "LNA", "GPS",
                                     "radar", "bandpass", "noise", "wifi", "bluetooth", "FM", "AM radio",
                                     "microstrip", "interference", "signal generator", "matching"])
        job_title("PrintedCircuitBoard", ["RF", "antenna", "impedance", "ground plane", "50 ohm", "coplanar",
                                          "LoRa", "ESP32", "stackup", "EMI", "via stitching", "microstrip",
                                          "u.fl", "SMA", "GPS", "wifi", "ground pour", "controlled impedance"],
                  after="2016-01-01")
        job_title("ElectricalEngineering", ["RF", "antenna", "radio", "impedance", "transmission line", "EMI",
                                            "radar", "analog", "microwave", "electromagnetics", "signal integrity",
                                            "noise", "oscillator"])
        job_title("ECE", ["RF", "antenna", "analog", "microwave", "electromagnetics", "radar", "communications",
                          "signal processing", "DSP", "wireless"])
        job_title("rocketry", ["telemetry", "GPS", "radio", "LoRa", "antenna", "tracker", "transmitter",
                               "ground station", "flight computer", "RF"])
        job_title("amateurradio", ["antenna", "SWR", "coax", "balun", "dipole", "propagation", "SDR", "noise",
                                   "Yagi", "vertical", "ground", "feedline", "tuner", "LoRa", "Meshtastic",
                                   "NanoVNA", "filter", "amplifier", "radiation", "ferrite", "EFHW", "loop"],
                  after="2012-01-01", before="2022-01-01", pages_per_year=3)
