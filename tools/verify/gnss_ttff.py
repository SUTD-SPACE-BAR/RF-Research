#!/usr/bin/env python3
"""
gnss_ttff.py — verification for kb/21-gnss/ttff-agps-almanac-ephemeris.md

 1. Time to collect a complete broadcast ephemeris after data decoding starts at a random
    moment, from the message structures in the ICDs:
      GPS LNAV:   50 b/s, 6-s subframes, 30-s frame; ephemeris+clock = subframes 1-3.
      BeiDou D1:  50 b/s, 6-s subframes, 30-s frame; ephemeris+clock = subframes 1-3.
      GLONASS:    2-s strings, 30-s frame; immediate data = strings 1-4 (8 s).
      Galileo I/NAV (E1-B): ephemeris/clock words spread over the 30-s subframe (modelled as
                  needing 4 specific 2-s pages at fixed slots in a 30-s cycle; approximate).
    Two receiver policies: (a) all subframes from the same frame, (b) any order with matching IODE.
 2. Cold/warm/hot TTFF budget: acquisition search + bit/frame sync + ephemeris wait.
 3. Almanac collection: GPS 25 pages x 30 s = 12.5 min; GLONASS 2.5 min; BeiDou D1 12 min.
 4. Oscillator uncertainty -> Doppler search width at a cold start (TCXO +-0.5..2.5 ppm).
Run: python3 tools/verify/gnss_ttff.py
"""
import numpy as np

rng = np.random.default_rng(7)
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def collect_time(start, slots, dur, period, same_frame=False):
    """earliest time (from start) at which all 'slots' (start offsets within the period, each of
    length dur) have been received completely at least once after 'start'."""
    done = []
    for s in slots:
        k = np.ceil((start - s) / period)          # first complete occurrence starting at/after start
        t0 = s + k * period
        done.append(t0 + dur)
    if not same_frame:
        return max(done) - start
    # same frame: need a frame whose slots all start after 'start'
    k = np.ceil((start - min(slots)) / period)
    return (min(slots) + k * period + max(slots) - min(slots) + dur) - start


N = 20000
starts = rng.uniform(0, 30, N)
gps_any = np.array([collect_time(s, [0, 6, 12], 6, 30) for s in starts])
gps_same = np.array([collect_time(s, [0, 6, 12], 6, 30, same_frame=True) for s in starts])
glo = np.array([collect_time(s, [0], 8, 30) for s in starts])
# Galileo I/NAV E1-B: assume ephemeris word types 1-4 in four 2-s pages at slots 20,22,24,26 s (approx.)
gal = np.array([collect_time(s, [20, 22, 24, 26], 2, 30) for s in starts])
print("1) ephemeris collection time after data decoding starts (s): mean / 95th percentile / max")
for name, x in [("GPS LNAV (any order, IODE match)", gps_any), ("GPS LNAV (same frame)", gps_same),
                ("GLONASS strings 1-4", glo), ("Galileo I/NAV (approx. model)", gal)]:
    print(f"  {name:34s} {x.mean():5.1f} / {np.percentile(x,95):5.1f} / {x.max():5.1f}")
check("GPS: 18 s minimum, <= 36 s worst case", gps_any.min() >= 17.9 and gps_any.max() <= 36.01)
check("GLONASS: 8 s minimum, <= 38 s worst case", glo.min() >= 7.9 and glo.max() <= 38.01)
# all GPS satellites transmit subframes in lock-step (frames aligned to GPS time), so waiting is
# common to all satellites; a multi-GNSS receiver can finish on whichever system completes first
first_any = np.minimum.reduce([gps_any, glo, gal])
print(f"  multi-GNSS (first system to complete): mean {first_any.mean():.1f} s")
check("multi-GNSS shortens the mean ephemeris wait", first_any.mean() < gps_any.mean() - 5)

print("\n2) TTFF budgets (typical, illustrative)")
budget = {
    "cold (no almanac/time/position)": {"search all PRNs, wide Doppler": 3.0, "bit+frame sync (TLM/HOW)": 6.0,
                                         "ephemeris wait (mean)": gps_any.mean(), "first nav solution": 0.5},
    "warm (almanac, time +-s, pos +-100 km)": {"narrowed search": 1.0, "bit+frame sync": 6.0,
                                                 "ephemeris wait (mean)": gps_any.mean(), "nav": 0.5},
    "hot (valid ephemeris, RTC time, position)": {"narrow code search": 0.5, "coarse-time / TOW": 0.5, "nav": 0.3},
}
for k, v in budget.items():
    print(f"  {k:42s} total ~ {sum(v.values()):5.1f} s   ({', '.join(f'{a} {b:.1f}' for a, b in v.items())})")
check("modelled cold TTFF ~ 30-40 s (u-blox single-GPS spec 29-30 s)", 25 < sum(budget['cold (no almanac/time/position)'].values()) < 42)

print("\n3) almanac collection")
print(f"  GPS LNAV: 25 pages x 30 s frame = {25*30/60:.1f} min; GLONASS superframe 5 x 30 s = {150/60:.1f} min;"
      f" BeiDou D1 superframe 24 pages x 30 s = {24*30/60:.0f} min")
check("GPS almanac takes 12.5 min", 25 * 30 / 60 == 12.5)

print("\n4) cold-start Doppler uncertainty")
for ppm in [0.5, 2.0, 2.5, 10.0]:
    df = ppm * 1e-6 * 1575.42e6
    bins = int(np.ceil(2 * (df + 5000) / 500)) + 1
    print(f"  TCXO +-{ppm:4.1f} ppm -> +-{df/1e3:5.2f} kHz oscillator + +-5 kHz satellite -> {bins} bins of 500 Hz")
check("a +-2 ppm TCXO adds +-3.2 kHz, comparable with satellite Doppler", abs(2e-6 * 1575.42e6 - 3151) < 1)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
