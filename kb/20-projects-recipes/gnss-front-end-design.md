---
title: Recipe — GNSS front end on a rocket with onboard LoRa transmitters (ZED-F9P / MAX-M10S, active antenna chain, SAW/LNA budget, desense and harmonic coexistence)
domain: 20-projects-recipes
slug: gnss-front-end-design
tags: [recipe, gnss, zed-f9p, max-m10s, active-antenna, saw, lna, blocking, desense, coexistence, harmonics, l2, e6, wideband-noise, isolation, e22-400t33d, e220-900t30d, ubx, mon-rf, pre-registration]
prerequisites:
  - ../08-antennas/gnss-antennas.md
  - ../21-gnss/gnss-interference-jamming-spoofing.md
  - ../21-gnss/gnss-receiver-integration-u-blox.md
  - lna-design-walkthrough.md
related:
  - ../21-gnss/gnss-on-rockets-dynamics-and-limits.md
  - ../21-gnss/rtk-ppp-and-corrections.md
  - ../08-antennas/antennas-on-rockets.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../18-components-parts/filter-parts-saw-ceramic-ltcc.md
  - patch-antenna-design-walkthrough.md
  - bandpass-filter-design-walkthrough.md
  - lora-rocket-telemetry-link.md
  - design-review-checklists.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# Recipe — GNSS front end on a rocket that carries 2 W of LoRa

The system recipe that combines the [patch antenna](patch-antenna-design-walkthrough.md), the
[GNSS LNA](lna-design-walkthrough.md), the [harmonic filter](bandpass-filter-design-walkthrough.md) and the
[telemetry link](lora-rocket-telemetry-link.md) so that the flight computers' GNSS receivers (ZED-F9P on the
primary, MAX-M10S on the secondary) keep working while the E22 (433 MHz, 2 W) and E220 (868 MHz in Singapore, 905 MHz at IREC — 902–928 MHz is not a Singapore band; up to
1 W) transmit 25–50 % of the time. Receiver integration details (UBX, rates, dynamic models, limits) are in
[domain 21](../21-gnss/gnss-receiver-integration-u-blox.md); this page is the RF budget and the build plan.
Numbers: `python3 tools/verify/proj_gnss_frontend.py`, plus `gnss_self_interference.py` (domain 21) and the
other recipe scripts.

## Questions this page answers
- How much isolation do I need between my 2 W LoRa antenna and my GNSS antenna?
- Should the SAW go in front of the GNSS LNA on a rocket?
- Can my LoRa transmitter's own noise desense GPS even with no harmonics in the band?
- Which E22 channels must I never use with a ZED-F9P on board, and why is "legal harmonic level" not good enough?
- What active-antenna gain does the ZED-F9P want, and what does the MAX-M10S want?
- Do my MCU clocks (Teensy 24 MHz, ESP32 40 MHz) interfere with GNSS?
- How do I test GNSS coexistence on the bench and on the pad?
- What should I log so I can tell jamming from dynamics after a flight?

## TL;DR
- **Coupling** between a LoRa dipole and a GNSS patch 0.2–1.5 m apart is ≈ −19 to −37 dB at 433 MHz and −21 to −39 dB at 868–905 MHz (free-space Friis with assumed −10/−6 dBi GNSS out-of-band gain); pattern nulls along the axis can add 10–20 dB, coax and airframe currents can remove it — **measure S21 in the assembled vehicle**.
- **Blocking**: the MAX-M10S (immunity ≈ −15 dBm at 400–500 MHz, −17 dBm at 915 MHz, per u-blox via [domain 21](../21-gnss/gnss-interference-jamming-spoofing.md)) needs **48 dB** of isolation from the E22 at 33 dBm, 41 dB from the E220 at 24 dBm, 47 dB at 30 dBm. An active antenna with a BGA524N6 first needs 59/50/56 dB to stay out of compression and 33/24/30 dB just to survive. **A SAW in front (≈ 35 dB) closes the MAX-M10S cases and BGA524N6 survival at ≥ 20 dB of antenna coupling; keeping the BGA524N6 (IP1dB −16 dBm) out of compression needs ≥ 24 dB of coupling for the 2 W E22** — at a cost of ≈ 3 dB of C/N0 with a cold-sky antenna ([LNA recipe](lna-design-walkthrough.md)).
- **Transmitter wideband noise is the hidden killer**: for ≤ 1 dB desense with 25 dB coupling the PA's noise density at 1575 MHz *after its output filter* must be ≤ **−191 dBc/Hz** (33 dBm) — PAs have far-out floors of roughly −130…−150 dBc/Hz (assumed range; measure), so the TX path needs **40–60 dB of low-pass rejection at 1.5 GHz** plus isolation. Without any TX filtering, C/N0 loss is 35–55 dB (no GNSS while transmitting). The [elliptic harmonic filter](bandpass-filter-design-walkthrough.md) gives ≈ 61 dB at 1.5 GHz.
- **Harmonics in GNSS bands**: E22 CH 0–9 put 3f in or beside GPS L2 / GLONASS L2 (tracked by the ZED-F9P; CH 0–3 GPS L2, CH 4–6 GLONASS L2, CH 7–9 filter skirts — [21 interference](../21-gnss/gnss-interference-jamming-spoofing.md)), CH 10–22 in Galileo E6 / BeiDou B3. A *legal* −30 dBm harmonic coupled at −25 dB is a −55 dBm CW jammer: L2 C/N0 45 → −15 dB-Hz. Staying above the 28 dB-Hz tracking threshold needs 3f ≤ −75 dBm (≥ 108 dBc) — **pick CH ≥ 23 (≥ 433.125 MHz)**, never rely on filtering.
- **Clocks**: 25 MHz × 63 and 8 MHz × 197 fall in the L1 C/A main lobe; 24 MHz (Teensy 4.1) × 65 and 40 MHz (ESP32) × 39 = 1560 MHz land in BeiDou B1I, the MAX-M10S default third constellation ([domain 21](../21-gnss/gnss-interference-jamming-spoofing.md)). Keep MCUs and their clock traces away from the GNSS antenna and LNA; consider disabling B1I on the M10S if C/N0 on BeiDou is poor.
- **Gain windows**: ZED-F9P wants 17–50 dB total external gain (30–40 ideal) → a 28–36 dB active antenna with ≤ 2 m of RG-174 (26–35 dB delivered); MAX-M10S accepts passive antennas, and with an active one should run its LNA in bypass/low-gain with ≥ 10–15 dB external gain.
- **Flight logging**: put `UBX-MON-RF` (AGC, jamming indicator, CW suppression, antenna status) and per-satellite C/N0 at 1 Hz into the health frame; tag every LoRa TX burst in the log — then post-flight you can separate RF desense from dynamics and antenna orientation.

## Intuition (no math)
A GNSS receiver listens for signals far below the noise; your telemetry transmitter shouts a metre away. It can hurt the GNSS receiver in three different ways: by being so loud at its own frequency that it overloads the receiver's first amplifier (blocking), by spilling its own background hiss into the GNSS band (wideband noise), or by producing a harmonic right on a GNSS frequency (in-band jamming). Each has a different cure — separation and a filter in front of the GNSS amplifier for the first, a filter *after the transmitter* for the second, and choosing a channel whose harmonics miss the GNSS bands for the third. Then there are your own computers' clocks, whose high harmonics also land in the band.

## Requirements
| ID | Requirement | Value |
|---|---|---|
| N1 | Receivers | primary ZED-F9P (L1/L2, RTK-capable, active antenna); secondary MAX-M10S (L1, passive or active) |
| N2 | Coexistence | mean C/N0 of the strongest 8 satellites drops ≤ 3 dB with every onboard transmitter keyed at flight power and duty |
| N3 | Survivability | no front-end damage with any onboard TX at full power; no compression > 0.5 dB |
| N4 | Harmonics | no onboard-transmitter harmonic in any band the onboard receivers track |
| N5 | Gain | ZED-F9P 17–50 dB external (target 30–35 dB); MAX-M10S per u-blox modes |
| N6 | Observability | MON-RF, per-SV C/N0, fix status at ≥ 1 Hz in the log and the telemetry health frame |
| N7 | Dynamics | follow [domain 21](../21-gnss/gnss-on-rockets-dynamics-and-limits.md): Airborne < 4 g model, expect loss at ignition/burnout, 500 m/s firmware limit |

## Architecture options and trade study
| Option | Pros | Cons | Use |
|---|---|---|---|
| ZED-F9P + commercial multiband active antenna (L1/L2) | spec-compliant gain/NF/group delay; RTK works | size; out-of-band rejection and LNA linearity vary by product — check ≥ 40 dB OOB rejection | **primary FC** |
| ZED-F9P + home-made L1-only active patch | cheap, learning | loses L2 → no fast RTK; still needs SAW-first on a crowded vehicle | bench / learning only |
| MAX-M10S + passive patch on a short U.FL | simplest (internal SAW + LNA) | its front end is LNA-then-SAW: blocking set by the internal LNA | **secondary FC**, add an external SAW in front if isolation < 48 dB |
| MAX-M10S + active antenna (SAW-first) | robust, long cable OK | LNA bypass config, extra board | if the antenna must be far from the board |
| Time-share TX and GNSS-critical epochs | no hardware | u-blox receivers cannot be gated; tracking loops average through bursts | not a design tool |

## The math — design calculations

### Level 1 — the three budgets
1. **Blocking**: $P_{blk} = P_{TX} - C_{ant} - R_{SAW} \le P_{imm}$ (receiver immunity or LNA IP1dB − 10 dB; and < abs-max).
2. **Wideband noise**: $N_{int} = P_{TX} + \mathcal N_{PA}(1575) - R_{LPF}(1575) - C_{ant}$ [dBm/Hz]; desense $= 10\log_{10}(1 + T_{int}/T_{sys})$ with $T_{int} = 10^{N_{int}/10}\,10^{-3}/k$.
3. **In-band CW harmonic**: $J = P_{3f} - C_{ant}$; $1/(C/N_0)_{eff} = 1/(C/N_0) + (J/S)/(Q R_c)$ (Kaplan–Hegarty; Q ≈ 1 for CW, $R_c$ = 1.023 Mchip/s) ([domain 21](../21-gnss/gnss-interference-jamming-spoofing.md)).

### Level 2 — numbers for this vehicle
**Coupling** (`proj_gnss_frontend.py` §1, assumptions in brackets):

| Separation | 433 MHz (dipole 2.15 dBi → patch −10 dBi) | 868 MHz (→ −6 dBi) | 905 MHz (IREC) |
|---|---|---|---|
| 0.2 m | −19.1 dB | −21.1 dB | −21.5 dB |
| 0.5 m | −27.0 dB | −29.0 dB | −29.4 dB |
| 1.0 m | −33.0 dB | −35.1 dB | −35.4 dB |
| 1.5 m | −36.6 dB | −38.6 dB | −39.0 dB |
(At 433 MHz λ/2π = 11 cm: below ≈ 0.2 m the antennas are in each other's reactive near field and Friis is only indicative.)

**Blocking budget** (§2):

| Transmitter | MAX-M10S RF_IN | BGA524N6 active antenna (no compression / survival) |
|---|---|---|
| E22 433 MHz, 33 dBm | 48 dB | 59 / 33 dB |
| E220 868 MHz, 24 dBm (Singapore) | 41 dB | 50 / 24 dB |
| E220 905 MHz, 30 dBm (IREC) | 47 dB | 56 / 30 dB |

With 25–35 dB of coupling and no front SAW every row fails at least its compression target. With a 35 dB SAW in front: the MAX-M10S rows pass with ≥ 20 dB coupling (55 dB ≥ 41–48 dB); BGA524N6 *survival* passes everywhere; BGA524N6 *no-compression* (input P1dB **−16 dBm** from the data-sheet table, − 10 dB headroom) needs **≥ 24 dB of coupling for the E22 at 33 dBm, ≥ 21 dB for the E220 at 30 dBm, ≥ 15 dB at 24 dBm** — at exactly 20 dB coupling the E22 case is 4 dB and the 905 MHz case 1 dB short (consistency audit #3). Measure the coupling (G-T1) before deciding.

**Wideband noise** (§3; T_sys 150 K → −176.8 dBm/Hz):

| TX | PA floor at 1575 MHz (assumed) | TX LPF rejection | Coupling | C/N0 loss |
|---|---|---|---|---|
| E22 33 dBm | −130 dBc/Hz | 0 dB | 25 dB | **54.8 dB** |
| E22 33 dBm | −140 dBc/Hz | 0 dB | 25 dB | 44.8 dB |
| E22 33 dBm | −150 dBc/Hz | 0 dB | 25 dB | 34.8 dB |
| E22 33 dBm | −130 dBc/Hz | 40 dB | 40 dB | 2.9 dB |
| E22 33 dBm | −130 dBc/Hz | 60 dB | 25 dB | 1.2 dB |
| E22 33 dBm | −140 dBc/Hz | 60 dB | 25 dB | 0.1 dB |
| E220 30 dBm | −130 dBc/Hz | 60 dB | 25 dB | 0.6 dB |

Requirement for ≤ 1 dB: (PA floor − LPF) ≤ −190.7 dBc/Hz (33 dBm, 25 dB coupling), −175.7 (40 dB coupling); E220 at 30 dBm: −187.7 / −172.7 dBc/Hz. The modules' internal output filtering at 1.5 GHz is not published — this is the single most important unknown and the reason for test G-T3.

**Harmonic jamming** (§4, L2C at −130 dBm, C/N0 45 dB-Hz without interference):

| 3f at the LoRa antenna | Coupling | J/S | L2C C/N0 |
|---|---|---|---|
| −30 dBm (legal limit) | 25 dB | 75 dB | −15 dB-Hz (lost) |
| −50 dBm | 40 dB | 40 dB | 20 dB-Hz (lost) |
| −70 dBm | 25 dB | 35 dB | 25 dB-Hz (below 28) |
| −90 dBm | 25 dB | 15 dB | 42 dB-Hz |
So a channel whose 3f lands in L2 would need its harmonic ≈ 108 dB below the carrier. Channel choice (CH ≥ 23; see the [telemetry recipe](lora-rocket-telemetry-link.md) and `proj_lora_link.py` §10 for the full table; domain 21 independently finds CH 0–3 → L2, CH 5–6 → G2, CH 10–22 → E6, CH 23–24 clear of tracked GNSS signals — CH 23's 3f is just inside the 1215–1300 MHz RNSS allocation; CH 24 clears it) is the only practical cure. No harmonic of 863–928 MHz lands in any GNSS band.

**Gain window** (§5): a 28 dB active antenna delivers 25.8–27.6 dB through 0.15 m U.FL to 2 m RG-174; 36 dB delivers 33.8–35.6 dB — both in the ZED-F9P window; 17 dB antennas fall out of it once cable loss is counted.

### Level 3 — what the budgets leave out
- Duty cycle: desense and blocking happen only during TX bursts (25–51 % occupancy at the flight schedule); GNSS tracking loops (≈ 10–20 Hz) and the navigation filter partly bridge 20–80 ms gaps, but carrier-phase (RTK) continuity does not — expect RTK float during TX-heavy periods if desense is large.
- Two-transmitter intermodulation in the GNSS LNA (e.g. Wi-Fi 2442 − 2 × 433.125 = 1575.75 MHz) — [domain 21, example 3](../21-gnss/gnss-interference-jamming-spoofing.md): never run Wi-Fi/BLE and the 433 MHz TX together near the GNSS antenna. With the E22 on the KB default CH 24 (434.125 MHz), the products 2 × 434.125 = 868.25 MHz away from the Wi-Fi channel are: **ch 6** 2437 − 868.25 = 1568.75 MHz, which the 22 MHz-wide Wi-Fi signal spreads over ≈ 1558–1580 MHz, covering **GPS L1 C/A and E1/B1C**; **ch 11** 2462 − 868.25 = 1593.75 MHz (≈ 1583–1605 MHz), which hits **GLONASS G1** and misses the L1 C/A main lobe. These are a frequency check only; the product level is not computed ([21 coexistence table](../21-gnss/gnss-interference-jamming-spoofing.md), `s13_gnss_ephemeris.py` §7). Keep the ESP32 Wi-Fi radio off in flight; that removes all of them.
- PA noise is modelled as flat; real PAs have spurs and noise that depend on supply ripple and load VSWR.
- Coupling via the airframe and shared ground/supply (conducted interference) is not in the free-space numbers.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Required isolation (blocking) | $P_{TX} - P_{imm}$: 48 dB for 2 W vs MAX-M10S |
| Required (PA noise − LPF) for 1 dB desense | $-174 + 10\log(T_{sys}/290) - 5.9 - P_{TX} + C_{ant}$ dBc/Hz |
| Harmonic in a tracked band | must be ≈ 105–110 dBc below a 2 W carrier → choose the channel instead |
| Front SAW cost | ≈ 1.5–2 dB NF → ≈ 3 dB C/N0 with a cold-sky antenna |
| ZED-F9P external gain | 17–50 dB, 30–40 ideal |
| Antenna separation | as far as the vehicle allows; ≥ 1 m buys ≈ 6 dB over 0.5 m |

## Worked examples

### 1. Avionics B (ZED-F9P + E22 433 MHz 33 dBm), recommended configuration
- E22 on **CH 24 (434.125 MHz)** (CH 23 = 433.125 MHz only at BW ≤ 125 kHz, so the channel edge stays above 433.05 MHz in Singapore; CH ≥ 23 keeps 3f out of L2/E6); harmonic LPF after the module (≥ 60 dB at 1.2–1.6 GHz — [filter recipe](bandpass-filter-design-walkthrough.md)).
- Multiband active antenna (L1/L2) with stated ≥ 40 dB out-of-band rejection (SAW-first internally) and 28–36 dB gain, at the opposite end of the avionics bay from the 433 MHz antenna (≥ 0.7 m), feed via 1 m RG-174; bias-tee per the F9P integration manual (VCC_RF, high-impedance inductor, ESD).
- Budget: coupling ≈ −30 dB + pattern ≈ −10 dB → 40 dB; antenna's SAW 40 dB → blocker at its LNA ≈ −47 dBm (OK); wideband noise with a −140 dBc/Hz PA and a 60 dB LPF → ≈ 0 dB desense; 3f clean.
- Expected: C/N0 drop with TX keyed ≤ 1 dB (pre-registered G3).

### 2. Avionics C (MAX-M10S + E220 at 24 dBm, 868.125 MHz)
- Passive 25 mm ceramic patch (or the FR-4 patch) on a ≤ 10 cm U.FL → **external L1 SAW in front of RF_IN** (u-blox's SAW–notch–LNA–SAW recommendation, [domain 21](../21-gnss/gnss-interference-jamming-spoofing.md)), because 41 dB of isolation is not available from 0.3–0.5 m of separation (−25 to −29 dB).
- Cost: SAW 1.6 dB before the internal LNA ≈ 1.6 dB NF → ≈ 2–3 dB C/N0; acceptable in open sky.
- E220 at 868 MHz: its 2f (1736 MHz) and 3f (2604 MHz) miss GNSS; wideband noise at 1575 MHz still needs ≥ 40 dB of TX-side filtering at 25 dB coupling (−130 dBc/Hz assumption) — LFCN-1000+ gives ≈ 30 dB only above 1.9 GHz; use the elliptic 905/920 MHz design or a 3-pole LC at the E220 output.

### 3. Self-interference audit (both boards)
From `gnss_self_interference.py`: ESP32 40 MHz × 39 = 1560 MHz and Teensy 24 MHz × 65 = 1560 MHz sit in BeiDou B1I; 25 MHz × 63 = 1575 MHz in L1 C/A. Mitigations: GNSS antenna ≥ 10 cm above and shielded from the MCU area by the ground plane; short, buried clock traces; spread-spectrum clocking where available; check with an SDR at L1 (RTL-SDR + LNA, waterfall) with the board running and the antenna disconnected.

## Part selection
| Function | Part | Notes |
|---|---|---|
| Primary GNSS antenna | commercial L1/L2 multiband active antenna (helical or stacked patch), 28–36 dB, ≥ 40 dB OOB rejection, SMA/U.FL | check data sheet for OOB rejection at 433/868/915 MHz explicitly |
| Secondary GNSS antenna | 25 mm ceramic L1 patch or the [FR-4 patch](patch-antenna-design-walkthrough.md) | ground ≥ 50–70 mm |
| Front SAW (M10S / DIY active) | Murata SAFFB1G56KB0F0AR1X (C91647, 1.6 dB, ≈ US$0.06) or TST TA1575IG (3 × 3 mm, 2 dB) | ([filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)) |
| Active-antenna LNA (DIY) | chain C of the [LNA recipe](lna-design-walkthrough.md) (SAW → BGA524N6 → SAW → BGA524N6) | 34.9 dB, NF 2.2 dB |
| TX harmonic/noise LPF | [elliptic or Chebyshev-7 recipe](bandpass-filter-design-walkthrough.md), or Mini-Circuits LFCN-490+ (433 MHz) | ≥ 40–60 dB at 1.2–1.6 GHz |
| ESD | low-capacitance TVS at every exposed GNSS antenna input | required by u-blox |
| Bias-tee inductor (F9P) | high-impedance-at-L-band inductor (u-blox suggests ≈ 120 nH class) | check SRF vs L1/L2 |

## Block diagram
```
 AVIONICS B (primary)
  [433 MHz sleeve dipole, nose] <-- LPF (>=60 dB @1.2-1.6 GHz) <-- E22-400 (CH>=23, 33 dBm) <-- ESP32 UART
                     ^ >= 0.7 m, pattern-null alignment, measured S21 (target <= -40 dB incl. pattern)
  [L1/L2 active antenna, aft bay/window] --1 m RG-174--> [ESD]--[bias-T 3.3 V via VCC_RF]--> ZED-F9P RF_IN
                                                                                  UBX: NAV-PVT, MON-RF, NAV-SAT @1 Hz -> log + health frame
 AVIONICS C (secondary)
  [868 MHz dipole] <-- LPF/elliptic 868 <-- E220 (CH18, 24 dBm)
  [L1 patch] --U.FL<=10 cm--> [ESD]--[SAW SAFFB1G56]--> MAX-M10S RF_IN (internal LNA -> SAW)   (passive antenna mode)
```

## Layout notes
- GNSS RF trace: 50 Ω CPWG, shortest possible, ground-stitched; nothing digital routed under or beside it ([RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- Put the LoRa module and its output filter under a shield can on the opposite side/end of the board from the GNSS RF input; keep the LoRa supply current loop (≈ 1.2 A bursts) away from the GNSS LNA supply; separate, filtered rails (Avionics B's magnetometer lesson about shared noisy regulators applies to GNSS too) ([shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md), [grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- Ferrite chokes on both antenna coaxes at the antennas (keeps coax shields from becoming coupling paths) ([baluns](../08-antennas/antenna-matching-and-baluns.md)).
- MCU crystals and clock nets: away from the GNSS antenna and LNA; ground-plane between them.
- Avionics B's GPS daughterboard: keep the RF section of the daughterboard self-contained (SAW/ESD/bias-tee) so swaps don't change the front end.

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| Budgets | `proj_gnss_frontend.py`, `gnss_self_interference.py` | all N-requirements met with the assumed coupling |
| Antenna-to-antenna coupling on the airframe | NEC-2 wire model (dipole + patch-as-small-loop/monopole on a cylinder) or openEMS of the nose-cone + bay ([NEC](../16-simulation-tools/nec-antenna-modelling.md), [openEMS](../16-simulation-tools/openems-workflow.md)) | predicted S21 within ±6 dB of the measurement (G-T1) |
| TX filter rejection at 1.2–1.6 GHz | `proj_harmonic_filter.py` | ≥ 60 dB |
| Dynamics | domain 21 tracking-loop scripts with the flight thrust profile | expected loss windows identified (ignition, burnout) |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| G-T1 | Antenna coupling | VNA S21 between the LoRa and GNSS antenna connectors in the assembled airframe, 300 MHz–3 GHz | measured; ≤ −30 dB at 433 and 868/905 MHz, or SAW-first mandatory |
| G-T2 | Conducted blocking | GNSS receiver fed from its antenna outdoors (open sky); inject the LoRa signal via a coupler at the RF input at rising levels | C/N0 drop ≤ 0.5 dB at the expected blocker level + 10 dB |
| G-T3 | TX noise and harmonics at L1/L2 | E22/E220 at flight power into a 40 dB attenuator → notch/high-pass → SDR/LNA at 1.2 and 1.575 GHz; measure dBm/Hz | (PA noise − LPF) ≤ −175 dBc/Hz at 40 dB coupling (or ≤ −191 at 25 dB) |
| G-T4 | Radiated coexistence | full vehicle outdoors, GNSS fixed, then key each transmitter at flight schedule for 5 min each; log NAV-SAT C/N0 and MON-RF | mean C/N0 (top 8) drop ≤ 3 dB; no loss of fix; jamming indicator below "warning" |
| G-T5 | Clock self-interference | antenna disconnected, 50 Ω at RF_IN replaced by an SDR probe near the board; L1/B1I/G1 waterfall with all MCUs running | no lines above the SDR floor in-band, or identified and mitigated |
| G-T6 | Pad rehearsal | 1 h on battery with the flight telemetry schedule | fix maintained, RTK fix (F9P) maintained ≥ 95 % of the time |

## Regulatory check
- Receivers need no licence; GNSS bands are protected — never radiate test signals in them; G-T2 is conducted, G-T3 into a load ([IMDA](../19-regulations-safety/singapore-imda-rules.md)).
- The transmitters' channel and power choices remain governed by the [telemetry recipe](lora-rocket-telemetry-link.md) (Singapore: 433 MHz 10 mW e.r.p. exempt or licensed; 868 MHz ≤ 500 mW e.r.p.).
- Export control: do not modify GNSS firmware to remove the 500 m/s limit ([domain 21](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)).

## Pre-registered predictions
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| G1 | Measured LoRa↔GNSS antenna coupling in the airframe: −25 to −40 dB at 433 MHz | — | outside → redo the budgets with the measured value |
| G2 | Without any TX-side filtering at 1.5 GHz, keying the E22 at 33 dBm drops L1 C/N0 by > 10 dB (wideband noise) | — | if < 3 dB: the module's internal filter is better than −150 dBc/Hz + coupling assumption (record it) |
| G3 | With the harmonic LPF (≥ 60 dB at 1.5 GHz) and CH 23, C/N0 drop ≤ 1 dB (Avionics B configuration) | +2 dB | coupling via cables/supply, not radiation |
| G4 | MAX-M10S with external SAW: C/N0 2–3 dB lower than without SAW when the E220 is off; with E220 keyed at 24 dBm, no further drop > 1 dB | ±1 dB | SAW IL or coupling different |
| G5 | On CH 0–9 (test only, conducted), ZED-F9P L2 tracking is lost while transmitting | — | if not: harmonic at the GNSS input is lower than −95 dBm (record the measured level) |

## Risks and common failure modes
| Failure | Symptom | Cause / fix |
|---|---|---|
| GNSS drops whenever telemetry transmits | C/N0 collapses in bursts | wideband noise or blocking: TX LPF, SAW-first, separation |
| ZED-F9P L2 never tracks | L1-only fixes, no RTK | E22 on CH 0–9 (3f in or beside L2); L1-only antenna; bias-tee issue |
| Fix OK on the bench, lost on the pad | — | bench tests with TX into a dummy load; airframe coupling only appears assembled (G-T1, G-T4) |
| BeiDou weak only on the M10S | B1I C/N0 low | ESP32/Teensy clock harmonics at 1560 MHz; shielding or disable B1I |
| Front end damaged | permanently low C/N0 | LNA-first with high coupling; ESD |
| Misdiagnosis after flight | "GPS failed at apogee" | log MON-RF and TX bursts; see [domain 21](../21-gnss/gnss-on-rockets-dynamics-and-limits.md) for dynamic limits |

## Cost estimate
| Item | Cost (USD) |
|---|---|
| Multiband active antenna (primary) | ≈ 30–80 (est.) |
| Ceramic L1 patch + SAW + ESD (secondary) | ≈ 5–10 |
| TX LPFs (2) | ≈ 5 |
| Test: coupler, attenuators, SDR + LNA for G-T3/G-T5 (mostly from the other recipes) | ≈ 30–60 |

## Practical notes
- Log first, argue later: `UBX-MON-RF` (AGC count, `jamInd`, CW suppression, antenna status), `UBX-NAV-SAT` (per-SV C/N0), `UBX-NAV-PVT`, plus a TX-burst flag in the same log; the domain-21 page lists configuration keys and rates.
- Keep the GNSS receiver powered (V_BCKP) between pad checks to keep hot starts; RESET_N forces a cold start.
- Rehearse with the real schedule: occupancy (25–51 %) matters for averaged C/N0.

## Common mistakes & misconceptions
- **"The harmonic is legal, so it can't hurt GPS."** Legal (−30 dBm) and coexistence-safe (≤ −75 dBm at 25 dB coupling in L2) differ by 45 dB.
- **"No harmonic falls on L1, so the 433 MHz radio is safe."** The PA's broadband noise floor at 1.5 GHz can desense L1 by tens of dB without a TX-side filter.
- **"Put the SAW first, always."** It costs ≈ 3 dB of C/N0; it is the right call only when the measured isolation is insufficient — which on a small rocket it usually is.
- **"The active antenna's LNA has gain, so cable doesn't matter."** It still has to land in the 17–50 dB window and protect itself from the onboard blockers.
- **"Bench test with the transmitter into a dummy load proves coexistence."** It removes the dominant coupling path.

## How to simulate / verify
- `python3 tools/verify/proj_gnss_frontend.py` — coupling, blocking, wideband-noise desense, harmonic jamming, gain windows.
- `python3 tools/verify/gnss_self_interference.py` — clock/radio harmonics and intermods vs every GNSS band, jamming tolerance (domain 21).
- `python3 tools/verify/proj_lora_link.py` §10 — E22/E220 channel harmonic table.

## Open questions / gaps
- Far-out noise floor of the E22/E220 PAs at 1.2–1.6 GHz (G-T3 measures it) — the biggest unknown in this recipe.
- Measured airframe coupling between the 433/868 MHz antennas and the GNSS antenna (G-T1).
- Out-of-band rejection figures of candidate commercial multiband active antennas at 433/868/915 MHz.
- MAX-M10S immunity figures are u-blox's (via domain 21); ZED-F9P raw-input immunity figures were not found.

## Sources
1. This KB, [GNSS interference, jamming and spoofing](../21-gnss/gnss-interference-jamming-spoofing.md) and `tools/verify/gnss_self_interference.py` — Kaplan–Hegarty C/N0 model, MAX-M10S immunity, clock harmonics, E22 channel conflicts, intermod example. (internal; u-blox, Kaplan & Hegarty)
2. This KB, [u-blox receiver integration](../21-gnss/gnss-receiver-integration-u-blox.md) — ZED-F9P active-antenna requirement, MAX-M10S internal LNA/SAW and bypass mode, UBX configuration, V_BCKP/RESET_N. (internal; u-blox integration manuals)
3. This KB, [GNSS antennas](../08-antennas/gnss-antennas.md) — active-antenna specification (17–50 dB, NF < 4 dB, 40 dB OOB rejection), bias-tee, ESD, minimum signal. (internal; u-blox ZED-F9P Integration Manual UBX-18010802)
4. This KB, [GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md) — dynamic limits, export control, flight evidence. (internal)
5. This KB, [LNA recipe](lna-design-walkthrough.md), [filter recipe](bandpass-filter-design-walkthrough.md), [telemetry recipe](lora-rocket-telemetry-link.md) — chains, LPF rejection, channel table. (internal)
6. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House, 2017 — effective C/N0 under interference (via [1]). (textbook)
7. Coordinator note from W5-E1 (2026-10-02): E22 CH 0–6 3rd harmonic in GPS/GLONASS L2 (since extended to CH 0–9, canonical avoid-list). (internal)
