---
title: Time to first fix, almanac and ephemeris, cold/warm/hot starts and assisted GNSS (u-blox AssistNow) — and how to get a fast, reliable fix on the launch pad
domain: 21-gnss
slug: ttff-agps-almanac-ephemeris
tags: [gnss, ttff, cold-start, warm-start, hot-start, aided-start, almanac, ephemeris, navigation-message, lnav, i-nav, glonass-strings, a-gnss, assistnow, live-orbits, predictive-orbits, assistnow-autonomous, mga, bbr, rtc, v-bckp, launch-pad, reacquisition]
prerequisites: [gnss-signals-and-codes.md, gnss-receiver-architecture-acquisition-tracking.md]
related: [gnss-receiver-integration-u-blox.md, gnss-on-rockets-dynamics-and-limits.md, gnss-timing-1pps.md]
level: intro
confidence: high
last_updated: 2026-10-02
---

# TTFF, almanac, ephemeris and assisted GNSS

## Questions this page answers
- Why does a GNSS receiver take ~30 s to get its first fix from cold?
- What is the difference between almanac and ephemeris, and how long are they valid?
- What do cold, warm, hot and aided start mean, and what does the receiver need for each?
- What is A-GNSS / u-blox AssistNow (Live Orbits, Predictive Orbits, Autonomous)?
- How do I make sure my rocket has a good fix before launch and gets it back quickly after landing?
- Why did my GPS cold-start after I reset it?

## TL;DR
- A fix needs (1) signals acquired and tracked, (2) the **time of transmission** (from the message's time-of-week), and (3) each satellite's **ephemeris** (precise orbit + clock, ≈ 2–4 h validity; GLONASS updates every 30 min) [1][2]. The **almanac** (coarse orbits for the whole constellation, valid for weeks) only speeds up the search.
- **The message is slow**: GPS LNAV needs subframes 1–3 (18 s of a 30-s frame) — **18–36 s, mean 29 s** after decoding starts (any-order collection), 33 s if the receiver insists on one frame; GLONASS strings 1–4 take 8 s every 30 s (mean 23 s); a multi-GNSS receiver that finishes on whichever system completes first averages ≈ 16 s (`tools/verify/gnss_ttff.py`). The full GPS almanac takes 12.5 min.
- **u-blox numbers**: ZED-F9P cold 25–30 s, hot 2 s [3]; MAX-M10S cold 23–28 s (multi-GNSS), 29–56 s single-GNSS, hot 1 s, AssistNow Live Orbits 1 s, Predictive Orbits 2–3 s (7-day-old data), Autonomous 3–4 s (2-day-old data) [4].
- **Hot start** requires the backup domain: V_BCKP keeps RTC + BBR (ephemeris, almanac, last position, configuration) [5][6]. **RESET_N or a hardware-reset command clears BBR → cold start** [5][6].
- **AssistNow** (u-blox A-GNSS): *Live Orbits* — host downloads ephemeris/almanac/time/iono over the internet (EPH valid 2–4 h, ≈ 2–4 kB per constellation); *Predictive Orbits* — predicted orbits valid 1–14 days; *Autonomous* — the receiver extrapolates broadcast ephemerides itself for 3–6 days, no internet [6].
- **Pad rule**: power the GNSS (with V_BCKP) under open sky for ≥ 15 min before launch (all ephemerides; almanac after 12.5 min), keep it powered through the countdown, never reset it; after landing it will reacquire in seconds.

## Intuition (no math)
Finding a satellite is like finding a radio station whose frequency you only roughly know, playing a song you know by heart, but very quietly. The almanac is a printed programme guide: it tells you roughly which stations are on air now and where to tune, so you don't scan the whole dial. Once tuned in, you still need the station to read out its exact position and clock (the ephemeris), and it reads that out very slowly — 50 bits per second for GPS, repeating every 30 s. So even a receiver that finds satellites instantly waits up to half a minute for the paperwork. Assisted GNSS hands the paperwork over through another channel (internet, or the receiver's own memory and predictions), so the first fix comes in a second or two.

## The math

### Level 1 — start types

| Start | Receiver knows | What it must still do | Typical TTFF (u-blox) |
|---|---|---|---|
| Cold | nothing (no time, position, almanac, ephemeris) | search all PRNs × full Doppler (incl. its own TCXO error), decode time and ephemeris | 23–30 s multi-GNSS [3][4] |
| Warm | almanac, approximate time (s) and position (≈ 100 km); no valid ephemeris | narrow search, decode ephemeris | ≈ cold minus search time (≈ 25 s) |
| Hot | valid ephemeris, RTC time, last position | narrow code search, coarse time | 1–2 s [3][4] |
| Aided (AssistNow) | ephemeris/predicted orbits + time from host or memory | short search | 1–4 s [4] |
| Reacquisition (signal lost briefly while tracking) | everything | local search around last code/Doppler | < 1–2 s ("reacquisition sensitivity" −160 dBm [3][4]) |

**Validity**: GPS ephemeris uses a 4-hour curve-fit interval (fit-interval flag), new sets uploaded every ~2 h [1]; u-blox describes ephemerides as valid "approximately 2–4 hours depending on the GNSS system" and almanacs "a few weeks" [6]; GLONASS transmits a new ephemeris set every 30 min [2].

### Level 2 — how long the ephemeris takes (message structures)
Let decoding begin at a uniformly random time within the 30-s frame.

**GPS LNAV / BeiDou D1**: subframes 1, 2, 3 (6 s each) carry clock + ephemeris; they occupy [0, 18) s of each 30-s frame [1][7]. If the receiver accepts subframes from consecutive frames with matching IODE/IODC, collection completes at the end of the last subframe type still missing: minimum 18 s, maximum 36 s, mean 29.3 s; insisting on a single frame gives mean 32.9 s, max 48 s (script). All GPS satellites transmit subframes in lock-step with GPS time, so this wait is **common to all satellites** — more GPS satellites do not shorten it.

**GLONASS**: strings 1–4 (2 s each, 8 s) at the start of each 30-s frame [2] → 8–38 s, mean 22.9 s.

**Galileo I/NAV (E1-B)**: ephemeris/clock word types are spread through the 30-s subframe (2-s pages); modelled approximately as four 2-s pages → mean ≈ 22 s, max 32 s (script; approximate model of the page order). Dual-band E1-B + E5b-I receivers get the words twice as fast because the two signals carry them in offset pages.

**Multi-GNSS**: frames of different systems are not aligned, so taking the first system to complete gives a mean ≈ 16 s (script) — part of why multi-GNSS cold TTFF (23–25 s) beats GPS-only (29–30 s) in u-blox's tables [3][4].

**Budget** (script, illustrative): cold ≈ 3 s search + 6 s bit/frame sync (TLM/HOW every 6 s) + 29 s ephemeris + 0.5 s solution ≈ 39 s GPS-only (u-blox's better 29–30 s reflects parallel searching and early use of partially decoded data); hot ≈ 1.3 s.

**Search width at a cold start**: satellite Doppler ±5 kHz plus oscillator uncertainty: a ±0.5 ppm TCXO adds ±0.79 kHz (25 bins of 500 Hz), ±2 ppm ±3.15 kHz (34 bins), a ±10 ppm crystal ±15.8 kHz (85 bins) (script) — why GNSS modules use TCXOs and why frequency aiding (`MGA-INI-FREQ`, clock-drift assistance) helps [6].

### Level 3 — assistance data and coarse-time navigation
**AssistNow services** (u-blox [6]):

| Feature | Data | Validity | Size | TTFF |
|---|---|---|---|---|
| Live Orbits (replaces "Online") | EPH, ALM, TIME, AUX (iono, health, UTC, time offsets) | 2–4 h | ≈ 2–4 kB per constellation | 1–2 s |
| Predictive Orbits (replaces "Offline") | ANO (predicted orbits, one message per satellite per day), ALM | 1–14 days | high | "well below 10 s" |
| Autonomous (on-receiver) | ANO generated from broadcast ephemerides | 3–6 days | none (BBR/flash/host) | good/fair |

Rules from the manual: send assistance **immediately at start-up**, time first (`UBX-MGA-INI-TIME_UTC`) with an honest accuracy (default 10 s) — "do not provide too optimistic value"; the receiver ignores assisted time if its own RTC time is better; don't send near-expiry ephemerides; AssistNow Autonomous excludes eccentric orbits (e > 0.05, e.g. Galileo E18) and its maximum orbit error is configurable (`CFG-ANA-ORBMAXERR`) [6]. Alternatives to a battery: dump the navigation database (`UBX-MGA-DBD`) to the host before power-off and restore it at start-up, or save-on-shutdown to an attached flash [6].

**Coarse-time navigation.** If the receiver knows time only to a second or so but has ephemeris (aided), it can solve for an extra unknown (the time error) using the satellites' range rates, without decoding the time-of-week — this is how sub-second "hot" fixes and snapshot positioning (u-blox CloudLocate) work [4].

## Design equations & rules of thumb

| Item | Value | Source |
|---|---|---|
| GPS ephemeris collection | 18–36 s (mean 29 s) after decoding starts | script, [1] |
| GLONASS ephemeris | 8–38 s (mean 23 s) | script, [2] |
| GPS almanac | 12.5 min (25 pages × 30 s) | [1] |
| GLONASS almanac | 2.5 min superframe | [2] |
| BeiDou D1 almanac | 12 min | [7] |
| Ephemeris validity | 2–4 h (GPS 4 h fit); GLONASS new set every 30 min | [1][2][6] |
| Almanac validity | weeks | [6] |
| Hot start needs | V_BCKP (RTC + BBR) | [5][6] |
| RESET_N | cold start | [5][6] |

## Worked examples
**1 — Launch-day timeline (Avionics-C, MAX-M10S, no AssistNow).** T − 30 min: power on in the open; cold start ≈ 25–30 s to first fix; ephemerides for most satellites within ≈ 1 min; full almanac by ≈ 13 min. Keep powered; check `NAV-SAT` that ≥ 20 satellites have ephemeris (`ephAvail` flags) and `NAV-PVT.gnssFixOK`. T − 0: lift-off with a hot receiver. If the vehicle sits on the pad for hours, nothing expires as long as it keeps tracking (ephemerides refresh continuously).

**2 — Battery swap on the pad.** If the flight battery is swapped and V_BCKP is not separately supplied, the M10S cold-starts (≈ 25–30 s) and, because it has no flash, reverts to defaults (9600 baud NMEA, Portable model) until the host reconfigures it ([integration page](gnss-receiver-integration-u-blox.md)). With a coin cell/supercap on V_BCKP: hot start in ≈ 1 s with configuration retained (BBR).

**3 — After landing.** The receiver was tracking until apogee, lost some satellites during descent, and now lies in grass at an angle. Ephemerides (≤ 4 h old) and RTC are valid → reacquisition/hot start ≈ 1–2 s once signals are visible; poor sky view limits it, not the data.

**4 — Ground station without internet at a remote launch site.** Use AssistNow Autonomous on the receivers (enable `CFG-ANA-USE_ANA`) and keep them powered the night before: next-day starts behave like aided starts (3–4 s) for up to 3–6 days [4][6].

## Practical notes
- **Configure, then save to BBR** (and Flash on the F9P) so a brown-out doesn't wipe the configuration; re-send configuration on every host boot anyway.
- **Don't let the flight software "fix" a slow fix by resetting the receiver** — a reset throws away ephemeris; poll `MON-VER`/`NAV-STATUS` and wait.
- **Measure TTFF** in your own installation with `UBX-CFG-RST` cold/warm/hot commands and log `NAV-STATUS.ttff`; compare with the datasheet to detect antenna/interference problems (a cold start much slower than 30 s under open sky is a red flag).
- **Night-before checks**: if the receivers sat unpowered for > 4 h, the first start is warm at best.

## Common mistakes & misconceptions
- **"Almanac gives position."** It only predicts which satellites are visible and their approximate Doppler; positioning needs ephemeris.
- **"More satellites → faster cold start."** The ephemeris wait is set by the message structure; it is common to all satellites of a system.
- **"Hot start works after any power-off."** Only with the backup domain (V_BCKP/RTC) or restored assistance data.
- **"A reset fixes a GNSS that won't fix."** It usually makes it slower; find the real cause (antenna, interference, configuration).

## How to simulate / verify
- `python3 tools/verify/gnss_ttff.py` — ephemeris-collection distributions (GPS LNAV policies, GLONASS, approximate Galileo), multi-GNSS benefit, TTFF budgets, almanac times, oscillator Doppler search widths. ALL PASS.
- Bench: u-center → UBX-CFG-RST (cold/warm/hot) and NAV-STATUS ttff, repeated 20× for statistics.

## Open questions / gaps
- The Galileo I/NAV page order was modelled approximately; the exact word-type schedule (OS SIS ICD §4.3) was not re-read.
- The BeiDou D1 almanac/superframe duration (12 min) is from the ICD structure summary; not separately verified.

## Sources
1. U.S. Space Force, *IS-GPS-200N*, 2022 — LNAV frame/subframe structure (300-bit subframes, TLM every 6 s, 25 pages), ephemeris fit interval (4 h). https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-200N.pdf (standard)
2. ESA Navipedia, "GLONASS Navigation Message" — strings, frames, superframe, immediate data in strings 1–4, new ephemeris every 30 min. https://gssc.esa.int/navipedia/index.php/GLONASS_Navigation_Message (encyclopedia, ESA)
3. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05 — TTFF cold 25–30 s, hot/aided 2 s, reacquisition −160 dBm. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
4. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — TTFF tables incl. AssistNow Online/Offline/Autonomous, CloudLocate. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
5. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — RESET_N cold start, V_BCKP/RTC/BBR, hardware backup mode. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
6. u-blox, *MAX-M10S Integration manual*, UBX-20053088 R05 — §3.12 AssistNow (Table 34 service overview, Live Orbits data and host rules, Predictive Orbits, Autonomous concept/limits), §3.12.4 preserving data (BBR+RTC, MGA-DBD, save-on-shutdown), memory permanence (RESET_N clears BBR). https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer)
7. China Satellite Navigation Office, *BDS-SIS-ICD-B1I-3.0*, 2019 — D1/D2 frame structures. http://www.beidou.gov.cn/xt/gfxz/201902/P020190227593621142475.pdf (standard)
8. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., 2017 — TTFF components, assisted GNSS, coarse-time navigation. (textbook; general reference)
