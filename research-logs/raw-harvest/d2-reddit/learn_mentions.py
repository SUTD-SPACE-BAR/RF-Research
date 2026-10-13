#!/usr/bin/env python3
"""Count book/course/channel/tool mentions in comments of learning-path threads (counts only; no text stored)."""
import json, re, sys, time, urllib.request, urllib.parse, collections, os
D = os.path.dirname(os.path.abspath(__file__))
ids = [l.split("\t")[0] for f in ["class_rf.tsv", "class_rf2.tsv", "class_sdr.tsv", "class_ae.tsv", "class_more.tsv"]
       if os.path.exists(D + "/" + f) for l in open(D + "/" + f) if "\tLRN\t" in l or "\tCAR\t" in l]
ids += sys.argv[1:]
PAT = {
 "Pozar, Microwave Engineering": r"pozar",
 "Bowick, RF Circuit Design": r"bowick",
 "Hayward et al., Experimental Methods in RF Design (EMRFD)": r"emrfd|experimental methods",
 "ARRL Handbook": r"arrl handbook|arrl radio handbook|the arrl hand",
 "ARRL Antenna Book": r"arrl antenna|antenna book",
 "Balanis, Antenna Theory": r"balanis",
 "Kraus, Antennas": r"\bkraus\b",
 "Stutzman & Thiele": r"stutzman",
 "Lee, Planar Microwave Engineering": r"planar microwave|thomas lee|tom lee",
 "Lee, Design of CMOS RF ICs": r"cmos radio|design of cmos r",
 "Razavi, RF Microelectronics": r"razavi",
 "Ludwig & Bretchko, RF Circuit Design": r"ludwig|bretchko",
 "Gonzalez, Microwave Transistor Amplifiers": r"gonzalez",
 "Collin": r"\bcollin\b",
 "Steer, Microwave and RF Design (free)": r"\bsteer\b",
 "Hagen, Radio-Frequency Electronics": r"\bhagen\b",
 "Hayward, Introduction to RF Design": r"introduction to radio frequency design|intro to rf design",
 "Horowitz & Hill, Art of Electronics": r"art of electronics|horowitz",
 "Skolnik (radar)": r"skolnik",
 "Richards, Principles of Modern Radar / Fundamentals of Radar SP": r"richards|principles of modern radar",
 "Mahafza (radar MATLAB)": r"mahafza",
 "Lyons, Understanding DSP": r"\blyons\b|understanding digital signal",
 "PySDR (Lichtman)": r"pysdr",
 "Orfanidis EWA (free)": r"orfanidis",
 "Rick Hartley (PCB)": r"hartley",
 "Eric Bogatin (SI)": r"bogatin",
 "Henry Ott (EMC)": r"\bott\b|henry ott",
 "Cripps (PA)": r"cripps",
 "Egan (PLL)": r"\began\b",
 "Dean Banerjee (PLL)": r"banerjee",
 "Kurokawa / Microwave Journal": r"microwave journal",
 "W2AEW (YouTube)": r"w2aew",
 "The Signal Path (YouTube)": r"signal path|shahram",
 "Marshall Bruner RF (YouTube)": r"marshall ?bruner",
 "Rohde & Schwarz / Keysight app notes & videos": r"rohde|keysight|agilent app",
 "Analog Devices (Wiki/University/RF basics)": r"analog devices|adi university|analog\.com",
 "Michael Ossmann / Great Scott Gadgets SDR course": r"ossmann|great scott",
 "MIT OCW 6.013 / 6.776 etc.": r"ocw|mit open",
 "Coursera / edX": r"coursera|edx",
 "ham radio licence": r"ham licen|amateur radio licen|get (your|a) (ham|license|licence)|technician licen",
 "NanoVNA": r"nanovna",
 "tinySA": r"tinysa",
 "RTL-SDR": r"rtl-?sdr",
 "HackRF": r"hackrf",
 "Pluto SDR": r"pluto",
 "QUCS/QucsStudio": r"qucs",
 "LTspice/ngspice": r"ltspice|ngspice",
 "openEMS": r"openems",
 "Sonnet": r"sonnet",
 "ADS/AWR/HFSS (commercial)": r"\bads\b|\bawr\b|hfss|cst",
 "4nec2/MMANA/NEC": r"4nec2|mmana|\bnec\b",
 "scikit-rf": r"scikit-rf|skrf",
}
cnt = collections.Counter(); threads = collections.Counter(); ncom = 0; nthr = 0
for pid in dict.fromkeys(ids):
    url = "https://arctic-shift.photon-reddit.com/api/comments/search?" + urllib.parse.urlencode(
        {"link_id": pid, "limit": 100, "fields": "body,score"})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rf-kb-research/0.1"}), timeout=90) as r:
            d = json.load(r).get("data") or []
    except Exception as e:
        print("err", pid, e); time.sleep(5); continue
    nthr += 1; ncom += len(d)
    seen = set()
    for c in d:
        b = (c.get("body") or "").lower()
        for k, p in PAT.items():
            if re.search(p, b):
                cnt[k] += 1; seen.add(k)
    for k in seen:
        threads[k] += 1
    time.sleep(1.2)
print(f"threads {nthr}, comments {ncom}")
for k, v in threads.most_common():
    print(f"{threads[k]:3d} threads  {cnt[k]:3d} comments  {k}")
