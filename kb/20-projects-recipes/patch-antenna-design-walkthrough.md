---
title: Recipe — GNSS L1 RHCP patch antenna on JLCPCB FR-4 (TL model → openEMS → fabrication → NanoVNA tuning), with the 2.45 GHz linear reference
domain: 20-projects-recipes
slug: patch-antenna-design-walkthrough
tags: [recipe, patch-antenna, microstrip-antenna, gnss, l1, rhcp, circular-polarization, truncated-corner, axial-ratio, fr-4, jlcpcb, openems, fdtd, nanovna, tuning, cavity-perturbation, pre-registration]
prerequisites:
  - ../08-antennas/patch-antennas.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../08-antennas/gnss-antennas.md
  - ../16-simulation-tools/openems-workflow.md
related:
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../08-antennas/antenna-measurement.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/antenna-range-ota-testing.md
  - ../16-simulation-tools/simulation-validation.md
  - lna-design-walkthrough.md
  - gnss-front-end-design.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# Recipe — GNSS L1 RHCP patch on JLCPCB FR-4

A single-feed, truncated-corner square patch for GPS L1 (1575.42 MHz) on the cheapest board JLCPCB makes
(2-layer, 1.6 mm FR-4), carried from hand calculation through an openEMS model to fabrication and tuning.
Analytic numbers: `python3 tools/verify/proj_patch_gnss.py`; full-wave numbers:
`~/opt/openEMS/venv/bin/python tools/verify/proj_openems_gnss_patch.py quick|design|final …` (each run
1–2 min on the coarse mesh; the expectations were written into the script *before* the first run and every
result is appended to its docstring).

## Questions this page answers
- How big is a GPS L1 patch on JLCPCB FR-4, and how much gain will it really have?
- How do I make a single-feed patch circularly polarised, and how big should the cut corners be?
- Which corners do I cut to get RHCP rather than LHCP?
- Why does an FR-4 GNSS patch need tuning after fabrication, and how do I tune it?
- How well do the transmission-line model and openEMS agree?
- What axial ratio and bandwidth can I expect, and is it enough for GPS, Galileo and BeiDou?
- Is a home-made FR-4 patch good enough for a ZED-F9P or MAX-M10S on a rocket, compared with a ceramic patch?
- How do I measure axial ratio and handedness without an anechoic chamber?

## TL;DR
- **Design (JLC 2-layer 1.6 mm FR-4, εr 4.5, tan δ 0.02, dielectric modelled as 1.51 mm, 80 × 80 mm ground; JLC's JLC0216A stackup is a 1.43 mm core in the 1.6 mm finished board — [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table); the TL model moves only +0.02 % (≈ +0.4 MHz) for 1.43 mm, so the predictions stand, but measure h in [validation F2-M1](validation-test-campaign.md))**: square side 44.88 mm from the TL model (resonance check in openEMS: **1558.5 MHz, −1.07 %**); corners cut by right isosceles triangles of leg **a ≈ 5.9 mm** (cavity-perturbation prediction 5.36 mm, i.e. ΔS/S = 1/(2Q); openEMS optimum 10 % larger); probe 15 mm from centre on the axis; **final side 44.71 mm** (after a mesh-convergence correction — see below).
- **openEMS result (final, mesh-converged)**: AR minimum **0.23 dB at 1575.0 MHz** (fine mesh; coarse mesh 1577.5 MHz — 0.16 % apart), AR ≤ 3 dB over **15 MHz** (1 %); at L1: AR 0.35 dB, S11 −15.6 dB (Z = 45 + j15 Ω); RHCP directivity 6.3 dBic, cross-pol (LHCP) −28 dBic; radiation efficiency **35.6 %** → **realised RHCP gain ≈ +1.7 dBic**; HPBW ≈ 96°; AR 1.1 dB at 60° from zenith, 1.9 dB at the horizon.
- **Mesh trap (found here)**: with a free uniform grid the patch edges were not mesh lines, so the staircased patch size changed with the mesh — the "final" design moved from 1575.0 MHz (0.8 mm mesh) to **1545 MHz (0.5 mm mesh)**. Locking mesh lines to the patch edges with the thirds rule fixed it (coarse/fine now agree to 0.16 %) and cost a 0.5 % size correction (44.94 → 44.71 mm). Always run the convergence check before trusting a high-Q resonant result.
- **Handedness is set by which diagonal you cut**, relative to the feed: with the probe on the −x axis, cutting (+x,+y)/(−x,−y) gave **LHCP**; cutting (+x,−y)/(−x,+y) gave **RHCP** (both simulated). Get it wrong and you lose ≈ 20+ dB against the satellites.
- **FR-4 is the problem**: Dk 4.3–4.7 moves the resonance by −33…+35 MHz — **twice the 15 MHz AR bandwidth**. Thickness ±10 % only ±0.8 MHz; etch ±0.05 mm ±1.7 MHz. Plan one "calibration" fab (three sizes) and/or trim: −1 mm of side ≈ +36 MHz.
- **Models vs full wave**: TL/cavity model 24 % efficiency (G ≈ −0.2 dBi) vs openEMS 35.6 % (+1.7 dBic) — the analytic Q budget is pessimistic on FR-4 by ≈ 1.5–2 dB, the same direction as the KB's 2.45 GHz FR-4 case (40 % vs 44.5 %).
- **Is it good enough?** At the minimum GPS signal, C/N0 ≈ 45 dB-Hz into a MAX-M10S (internal LNA) vs ≈ 48 dB-Hz with a 25 mm ceramic patch; with a masthead LNA at the feed the FR-4 patch recovers to ≈ 47.5 dB-Hz. Fine for L1-only; for ZED-F9P RTK use a multiband ceramic/helix active antenna (this patch is single-band).
- **CP bandwidth limits constellations**: 15 MHz AR bandwidth covers GPS L1 C/A and Galileo E1 (±2 MHz) but not BeiDou B1I (1561.1 MHz, −14 MHz) or GLONASS L1 (1598–1606 MHz).

## Intuition (no math)
A square patch is a flat resonant cavity with two identical modes at right angles (one with the field varying along x, one along y). Feed it on one axis and only one mode is excited: linear polarisation. Cut two opposite corners and the two "diagonal" modes see different shapes — the one whose field is strong at the cut corners loses some area and resonates a little higher. Feed the patch on an axis and you excite both diagonal modes equally; if their resonances are split by just the right amount, at the frequency halfway between them one mode leads by 45° and the other lags by 45°, i.e. they are 90° apart: circular polarisation. Too small a cut and they are less than 90° apart; too big and the axial ratio minimum is shallow and the input match suffers. Which diagonal you cut decides which mode leads, and so whether the field rotates clockwise or anticlockwise.

## Requirements
| ID | Requirement | Value |
|---|---|---|
| A1 | Frequency | GPS L1 1575.42 MHz (± 1.023 MHz C/A main lobe; Galileo E1 ± ≈ 2 MHz) |
| A2 | Polarisation | RHCP, AR ≤ 3 dB at zenith over ≥ ±2 MHz; ≤ 3 dB down to 30° elevation |
| A3 | Match | S11 ≤ −10 dB at L1 into 50 Ω |
| A4 | Gain | ≥ 0 dBic realised at zenith |
| A5 | Board | JLCPCB 2-layer 1.6 mm FR-4, ≤ 80 × 80 mm, ENIG, no soldermask on the patch |
| A6 | Feed | coaxial probe from the back (U.FL or SMA) |
| A7 | Robustness | survive ±0.2 Dk lot variation by tuning, not redesign |

## Architecture options and trade study
| Option | AR bandwidth | Gain | Cost / effort | Verdict |
|---|---|---|---|---|
| **Single-feed truncated-corner square** | ≈ 1 % (15 MHz here) | ≈ +1.7 dBic on FR-4 | one board, no parts | **chosen** (cheapest, adequate for L1) |
| Nearly-square patch fed on the diagonal | similar | similar | same | equivalent alternative (L/W = 1 + 1/Q) ([patch antennas](../08-antennas/patch-antennas.md)) |
| Dual-feed + 90° hybrid (branch-line or chip hybrid) | ≈ impedance bandwidth (≈ 2–3 %) | similar minus hybrid loss | +1 part, more area | if BeiDou/GLONASS needed |
| Ceramic patch (εr ≈ 20, 25 × 25 mm) bought | ≈ 0.4 % | 2–5 dBic | US$2–10 | flight default for size ([GNSS antennas](../08-antennas/gnss-antennas.md)) |
| Low-loss laminate (RO4003C) patch, 63 × 50 mm | ≈ 0.5 % | ≈ 4.8 dBi | JLC Rogers 2-layer from ≈ US$47 | when efficiency matters ([stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md)) |
| Quadrifilar helix | wide, hemispherical | ≈ 2–3 dBic | hand-built | tumbling vehicles ([helical antennas](../08-antennas/helical-antennas.md)) |

## The math — design calculations

### Level 1 — size, Q, bandwidth, feed
Transmission-line model with Hammerstad fringing ([patch antennas](../08-antennas/patch-antennas.md)), iterated with W = L for a square patch, and the Jackson–Alexopoulos cavity-model Q budget (`ant_patch.py` functions):

| Quantity | Value |
|---|---|
| Side L = W | **44.88 mm** (ε_eff 4.227, ΔL 0.697 mm) |
| Q budget | Q_d 50, Q_c 907, Q_sp 144, Q_sw 2079 → **Q = 35.1** |
| VSWR-2 bandwidth (one mode) | 2.02 % = 31.8 MHz |
| Radiation efficiency / directivity / gain (one mode) | 24.3 % / 5.94 dBi / −0.2 dBi |
| Edge resistance | 133 Ω; 50 Ω point 13.0 mm in from the edge (linear patch) |

FR-4's loss tangent sets the efficiency: Q_d = 1/tan δ = 50 is the dominant loss term, so radiation is only ≈ ¼ (model) to ⅓ (openEMS) of the input power.

### Level 2 — the corner cut (derivation)
For the two degenerate modes $\psi_x=\cos(\pi x/L)$, $\psi_y=\cos(\pi y/L)$ (corner at the origin), the diagonal modes are $\psi_\pm=(\psi_x\pm\psi_y)/\sqrt2$. At the corners (0,0) and (L,L), $|\psi_+|^2 = 2$ and $\psi_- = 0$; over the patch $\int|\psi_\pm|^2dS = S/2$. Removing a small total area ΔS of the (magnetic-wall) cavity where the electric field is maximal and the magnetic field ≈ 0 raises the resonance by (cavity perturbation)
$$\frac{\delta f_+}{f}\approx\frac{\int_{\Delta S}|\psi_+|^2\,dS}{2\cdot\tfrac12\int_S|\psi_+|^2\,dS}\cdot\frac12\cdot 2=\frac{2\,\Delta S}{S},\qquad \delta f_-=0 .$$
CP at the midpoint needs the split $\Delta f/f = 1/Q$ (each mode ±45°; verified by the two-mode model in `ant_patch.py`), so
$$\frac{\Delta S}{S}=\frac{1}{2Q}$$
— the classic Sharma–Gupta design rule, here derived. With Q = 35.1: ΔS/S = 1.43 %, ΔS = 28.7 mm², and two triangles of leg $a$ give ΔS = $a^2$ → **a = 5.36 mm**. The two-mode model then predicts an AR < 3 dB bandwidth of 15.5 MHz (0.99 %), and ±20 % error in the split raises the AR minimum to 1.6–1.9 dB.

Feed: a probe on the x axis couples to each diagonal mode with cos 45°, and at the CP frequency each modal impedance is $(R/2)e^{\mp j45°}$, so $Z_{in}\approx R_x/2$: put the probe where the *linear* patch would show ≈ 100 Ω — 7.4 mm in from the edge, ≈ 15 mm from the centre.

### Level 2 — full-wave results (openEMS EC-FDTD)
Model: PEC patch and ground (zero thickness), FR-4 εr 4.5 with tan δ 0.02 as conductivity at 1.575 GHz, 80 × 80 mm board, 50 mm air margin, MUR boundaries, 0.8 mm uniform mesh over the patch (staircases the 45° cuts), 4 cells through the substrate, lumped 50 Ω probe port; end criterion −40 dB ([openEMS workflow](../16-simulation-tools/openems-workflow.md)).

| Run | Geometry | Result |
|---|---|---|
| linear #1 (sliver cell at the feed, Δt 0.37 ps) | 44.88 mm, a = 0, probe 9.41 mm | S11 −19.7 dB at **1558.5 MHz** (−1.07 %), Z 41.3 + j3.8 Ω, BW 29.5 MHz |
| linear #2 (mesh fixed, Δt 1.08 ps, 448 844 cells, 74 s) | same | −19.6 dB at **1558.5 MHz**, BW 29.8 MHz — mesh change did not move it |
| CP, predicted cut | a 5.36, probe 15, corners (+,+)/(−,−) | AR min 1.80 dB at 1572.5 MHz, **LHCP**, AR BW 10 MHz, Z 54.7 + j13.4 Ω |
| CP, mirrored | a 5.36, probe 13.5, corners (+,−)/(−,+) | AR min 1.76 dB at 1572.5 MHz, **RHCP**; Z 47.5 + j13 Ω |
| CP sweep | a 4.8 / a 5.9 (probe 15) | AR min 4.53 dB (under-split) / **0.77 dB at 1577.5 MHz**, AR BW 15 MHz |
| "final" v1 (free grid) | 44.94 mm, a 5.9, probe 15, mirrored | coarse: AR 0.72 dB at 1575.0 MHz — **fine mesh: AR min at 1545.0 MHz, AR 10.2 dB at L1 → not converged** |
| v1 with edge-locked mesh (thirds rule) | 44.94 mm | coarse: AR min 0.65 dB at 1567.5 MHz |
| **final v2, edge-locked, coarse (0.8 mm, 444 400 cells)** | **44.71 mm, a 5.9, probe 15, mirrored** | AR min 1.01 dB at 1577.5 MHz; at L1 AR 1.04 dB, S11 −15.1 dB |
| **final v2, edge-locked, fine (0.5 mm, 6 substrate cells, 1.28 M cells, 355 s)** | same | **AR min 0.23 dB at 1575.0 MHz; at L1 AR 0.35 dB, S11 −15.6 dB (Z 44.7 + j15.1 Ω); AR ≤ 3 dB BW 15 MHz; S11 min −25.7 dB at 1599 MHz, S11 ≤ −10 dB over 73 MHz** |
| final v2, far field at L1 (fine) | — | D_RHCP 6.29 dBic, D_LHCP −28.3 dBic, e_rad 35.6 %, G_RHCP 1.81 dBic, mismatch 0.12 dB → **+1.7 dBic realised**; HPBW 96°; AR 0.3 / 0.5 / 0.8 / 1.1 / 1.5 / 1.9 dB at θ = 0 / 30 / 45 / 60 / 75 / 90° |

Scoring the pre-registered expectations: resonance within ±3 % ✔ (−1.1 %); AR minimum < 3 dB with the predicted cut ✔ (1.8 dB) but the best cut is 10 % larger than ΔS/S = 1/(2Q); AR bandwidth ≈ 15 MHz ✔ (10 MHz at the predicted cut, 15 MHz at the optimum); $Z_{in}$ at the AR minimum ≈ half the single-mode value ✔ (42–55 Ω real part); gain ≈ 0 dBic ✘ — openEMS is 1.7–1.9 dB better than the cavity model because the model's efficiency (24 %) is pessimistic (openEMS 35.6 %). Note: the S11 minimum (1599 MHz) is *not* where the AR is best (1575 MHz) — tune for AR, not for S11. The coarse-mesh far-field numbers (D, efficiency) were already stable (6.29–6.31 dBi, 35.5–35.6 %); only the frequency of best AR was mesh-sensitive.

Convergence criterion (pre-set): AR-minimum frequency moves ≤ 0.3 % between the 0.8 mm and 0.5 mm patch meshes — met (0.16 %) only after the edge-locking fix. All rows above the v2 lines (including the linear 1558.5 MHz check) used the free grid, whose effective patch size is quantised by up to one 0.8 mm cell (≈ ±28 MHz): their *trends* (cut size vs AR, handedness, probe position vs Z) stand, their absolute frequencies do not.

### Level 3 — what the model leaves out
- Probe = lumped port (no coax inductance; at 1.51 mm height its reactance is small but it shifts Z by a few Ω).
- No soldermask, no copper thickness, no ENIG, no surface roughness (all lower the frequency or Q slightly).
- Finite ground fixed at 80 × 80 mm; the rocket's mounting (bulkhead, nose cone wall 1–3 mm away) detunes a high-Q patch by a few MHz — simulate the installation or measure in situ ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).
- Dk of FR-4 at 1.575 GHz and its anisotropy (woven glass) are uncertain by ±0.2 ([stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md)) — the dominant real-world error.

## Design equations & rules of thumb
| Rule | Value here |
|---|---|
| Square patch side | $L \approx c/(2f\sqrt{\varepsilon_{eff}}) - 2\Delta L$ → 44.88 mm (sim. −1.1 % low) |
| CP corner cut | $\Delta S/S = 1/(2Q)$ (derived) → a = 5.36 mm; full-wave optimum ≈ 1.1× |
| CP probe position | where the linear patch shows ≈ 2 × 50 Ω |
| AR bandwidth | ≈ ½ the impedance bandwidth (two-mode model 15.5 MHz; sim 15 MHz) |
| Trim sensitivity | −1 mm side → +36 MHz (2.3 %); cut leg ±0.5 mm → split ±20 % |
| Dk sensitivity | ±0.1 Dk → ∓17 MHz |
| Handedness | swapping the cut diagonal (or moving the feed to the other axis) flips RHCP ↔ LHCP |

## Worked examples

### 1. Board drawing (final)
```
 80 x 80 mm, 2-layer 1.6 mm FR-4, ENIG, bottom = solid ground, top = patch only (no mask on patch)
          y
          ^      cut (-x,+y): leg 5.9 mm          (patch side 44.71 mm, centred)
          |   ____________________
          |  /                    |
          | /                     |
          ||           o          |      o = centre
          ||  X(feed)             |      X = probe at (-15.0 mm, 0) -> via to U.FL/SMA on the bottom
          ||                      /
          ||_____________________/   cut (+x,-y): leg 5.9 mm
          +-----------------------------> x
 RHCP (IEEE) towards +z (sky) for this geometry in openEMS; verify on the bench (test P4).
```
Feed: plated via (0.4–0.6 mm drill) from the patch to the bottom; U.FL (or edge SMA via a short CPWG) on the bottom ground with a 1.5 mm anti-pad. Add three extra copies on the same JLC order at side 43.8 / 44.71 / 45.7 mm (≈ +33 / 0 / −34 MHz) — the "Dk calibration set".

### 2. Tuning after fabrication
1. Measure S11 and (better) the AR minimum frequency of the nominal board (test plan T2–T3).
2. Frequency high → the board's Dk is lower than 4.5: use the larger calibration board, or extend all four edges equally with copper tape (≈ −36 MHz per mm of side length, i.e. ≈ −70 MHz per mm added to *each* edge, because each side grows by twice the per-edge extension).
3. Frequency low → Dk higher than 4.5: use the smaller calibration board, or trim all four edges equally with a scalpel (≈ +36 MHz per mm of side length, i.e. ≈ +70 MHz per mm removed from *each* edge) — keep the square symmetric.
4. AR minimum shallow (> 2 dB) but centred → adjust the split: enlarge both corner cuts (more split) or add tape to them (less split), in 0.25 mm steps.
5. Re-measure; record every trim in the build log with the measured result (record-everything).

### 3. Link to the receiver
C/N0 at the minimum GPS L1 C/A signal (−128.5 dBm for a 0 dBic RHCP antenna), sky-pointing antenna temperature 100 K (`proj_patch_gnss.py` §5):
| Chain | Antenna gain | T_sys | C/N0 |
|---|---|---|---|
| this patch (TL-model gain −0.2 dBic) → 10 cm U.FL → MAX-M10S (internal LNA, NF ≈ 2 dB assumed) | −0.2 | 302 K | 44.8 dB-Hz |
| 25 mm ceramic patch (≈ 3 dBic) → same | 3.0 | 302 K | 48.0 dB-Hz |
| this patch + own LNA at the feed (NF 0.8 dB, 20 dB) → 30 cm RG-316 → MAX-M10S | −0.2 | 169 K | 47.5 dB-Hz |
With the openEMS gain (+1.7 dBic) add ≈ 1.9 dB to the FR-4 rows. Acquisition thresholds of modern receivers are in the high 20s dB-Hz and tracking holds to the low 20s, so all rows track comfortably in open sky; what kills GNSS on rockets is blockage, orientation and desense ([GNSS front end](gnss-front-end-design.md)).

### 4. The 2.45 GHz linear reference
The KB's verified 2.45 GHz FR-4 patch (37.23 × 28.81 mm, probe 8.3 mm from the edge; TL model Q 26.9, BW 2.63 %, e 40 %) resonated in openEMS at 2.397 GHz (−2.2 %) with D 6.95 dBi, e 44.5 %, G 3.44 dBi ([openEMS workflow](../16-simulation-tools/openems-workflow.md)). The same pattern — TL model a little high in frequency, a little pessimistic in efficiency — repeats at L1 (−1.1 %, 24 % vs 36 %).

## Part selection
| Item | Choice | Price | Notes |
|---|---|---|---|
| Board | JLCPCB 2-layer 1.6 mm FR-4 (Dk 4.5 nominal), ENIG, 80 × 80 mm, 5 pcs per design | ≈ US$2–8 per design + shipping | specify "no soldermask on patch" (or model the mask) |
| Connector | U.FL (Hirose U.FL-R-SMT class) or edge/through-hole SMA | ≈ US$0.2–2 | U.FL for flight (retention clip), SMA for the bench |
| Cable | 1.13 mm U.FL pigtail ≤ 10 cm (0.27 dB at L1) | — | ([coax & cables](../03-transmission-lines-matching/coax-and-cables.md)) |
| ESD | low-capacitance TVS at the feed if the patch is exposed (≈ 0.2 pF → RL impact negligible at L1) | < US$0.2 | mandatory per u-blox for active antennas ([GNSS antennas](../08-antennas/gnss-antennas.md)) |
| Alternative | Rogers RO4003C/RO4350B 1.52 mm at JLC (2-layer only) | from ≈ US$47 for 5 | patch 63 × 50 mm class, e ≈ 70 % |

## Block diagram
```
 sky (RHCP) -> [truncated-corner patch, 80 mm FR-4 ground] -> probe via -> U.FL -> 10 cm 1.13 mm pigtail
            -> MAX-M10S RF_IN (internal SAW + LNA)           [passive configuration]
            or -> SAW -> LNA -> ... -> ZED-F9P (needs an ACTIVE, multiband antenna instead)  -> see LNA / GNSS recipes
```

## Layout notes
- Patch on top, *solid* ground on the bottom; nothing else on the top layer within λ/10 (≈ 19 mm) of the patch edges; no vias through the patch except the feed.
- Probe via: plated, ≥ 0.4 mm drill; ground anti-pad ≈ 1.5 mm diameter under the U.FL centre pin; 4–6 ground vias around the U.FL pad.
- Board outline = ground size used in the simulation (80 mm); a smaller ground shifts frequency and degrades AR (u-blox: 50–70 mm for L1 ceramic patches, ZED-F9P multiband antennas assume 150 mm [GNSS antennas](../08-antennas/gnss-antennas.md)).
- Mounting: nylon standoffs; keep the nose-cone wall ≥ 5 mm above the patch and simulate/measure with it in place.

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| TL/cavity design | `proj_patch_gnss.py` | dimensions, Q, cut, probe point |
| Linear resonance check | openEMS `quick` | within ±3 % of the TL model |
| CP cut and probe sweep | openEMS `design` | AR min ≤ 1 dB, sense RHCP |
| Final + convergence | openEMS `final` (coarse 0.8 mm and fine 0.5 mm patch mesh) | AR-min frequency moves ≤ 0.2 % between meshes |
| Sensitivity | rerun `final` with εr 4.3 / 4.7 and a 60 mm ground | quantifies the tuning range needed |
| Independent check | a second solver (e.g. NEC-2 cannot do dielectrics well; use openEMS vs the cavity model, plus the measurement) ([simulation validation](../16-simulation-tools/simulation-validation.md)) | measurement within the stated tolerances |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| T1 | Fab check | measure patch side and cut legs with calipers; board thickness | within ±0.1 mm of the drawing |
| T2 | S11 | **LiteVNA/NanoVNA V2-class** (NanoVNA-H4 is only > 40 dB to 1.5 GHz), SOL at the U.FL pigtail end, port extension to the pad ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)); patch facing the sky, nothing within 0.5 m | S11 ≤ −10 dB at 1575.42 MHz; record the dual-dip shape (two modes) |
| T3 | AR and frequency of best AR | **only inside a shielded, absorber-lined enclosure or an anechoic chamber** (e.g. SUTD's): VNA S21 from a rotated linear dipole at ≥ 2D²/λ ≈ 0.11 m in 15° steps, or a frequency sweep at 0°/90° ([antenna measurement](../08-antennas/antenna-measurement.md)); containment check: a GNSS receiver outside shows no C/N0 change. **Never radiate a test signal in the open lab or outdoors** (see Regulatory check). Without an enclosure, skip T3: infer the AR-minimum frequency from the T2 S11 dual-dip shape and rely on the receive-only T4 sky test and T5 | AR ≤ 3 dB at L1; AR minimum within ±5 MHz of L1 |
| T4 | Handedness | compare with an LHCP and an RHCP reference (two oppositely wound helices), or the sky test: GNSS C/N0 drops ≈ 15–20 dB with the wrong sense | co-pol ≥ 15 dB above cross-pol |
| T5 | Real-sky C/N0 | MAX-M10S + u-center, 30 min open sky, compare with a commercial ceramic patch on the same ground size, same time | mean C/N0 of the top-8 satellites within 3 dB of the ceramic patch |
| T6 | In airframe | repeat T2 and T5 with nose cone/bulkhead installed | S11 still ≤ −10 dB; C/N0 loss ≤ 2 dB |

## Regulatory check
A GNSS receive antenna is receive-only (GNSS receivers are explicitly licence-exempt in Singapore — [IMDA](../19-regulations-safety/singapore-imda-rules.md)). The CP test source in T3 is a transmitter, and **1575 MHz is a protected radionavigation band with no licence-exempt SRD allocation**: transmitting there is prohibited (ITU RR 5.328B; RNSS 1164–1300 and 1559–1610 MHz — [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)), and "low power, indoors" is not an exemption: even −20 dBm EIRP is far above the −128.5 dBm GNSS signal at nearby receivers. So: (1) measure **S11 only** (T2) in the open; (2) do any radiated test at L1 (T3) **only in a shielded enclosure or chamber**, with the containment check; (3) test receivers **conducted** (cabled, attenuated, as in the [LNA recipe](lna-design-walkthrough.md)); (4) otherwise use **real GNSS signals** (T4 sky sense test, T5 C/N0). Never re-radiate GNSS signals.

## Pre-registered predictions (for the fabricated board)
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| P1 | Best-AR frequency of the nominal board = 1575 MHz × √(4.5/Dk_actual) | ±5 MHz after correcting for the measured Dk (from the linear calibration board) | model error beyond Dk (mask, copper, probe) |
| P2 | AR at the best frequency ≤ 1.5 dB at zenith (openEMS: 0.23 dB) | — | cut legs or probe position off; trim per worked example 2 |
| P3 | AR ≤ 3 dB bandwidth 12–18 MHz | — | Q different (loss tangent ≠ 0.02) |
| P4 | Sense RHCP for the drawn geometry (cut on the (+x,−y)/(−x,+y) diagonal, probe on −x, patch facing +z) | — | mirror the cut |
| P5 | Realised RHCP gain at zenith +1.7 dBic (openEMS, mesh-converged); the cavity model says −0.2 dBic | ±1.5 dB | efficiency model error |
| P6 | Real-sky C/N0 1–3 dB below a 25 mm ceramic patch on the same ground | ±2 dB | detuning or wrong sense (≈ −20 dB) |

## Risks and common failure modes
| Failure | Symptom | Fix |
|---|---|---|
| Wrong handedness | C/N0 15–20 dB low, fix slow or impossible | mirror the cut; check P4 before the flight board |
| Dk lot off nominal | AR minimum 20–40 MHz from L1 | calibration boards; trim |
| Tuned for S11 instead of AR | good match, AR 4–8 dB at L1 | tune on the AR measurement (S11 minimum is 24 MHz above the AR minimum here) |
| Soldermask/coating added later | frequency drops a few MHz | specify no mask; conformal coat before final tuning, not after |
| Small or interrupted ground | AR degrades, frequency moves | keep the simulated ground; no slots under the patch |
| Detuning by the nose cone | in-situ shift | T6; simulate the cone |
| Desense by onboard LoRa | C/N0 collapses when telemetry transmits | SAW, isolation, timing — [GNSS front end](gnss-front-end-design.md) |

## Cost estimate
| Item | Cost (USD) |
|---|---|
| JLC boards: nominal + 2 calibration sizes, 5 pcs each | ≈ 10–25 + shipping |
| U.FL connectors, pigtails | ≈ 5 |
| Copper tape, scalpel | ≈ 5 |
| LiteVNA 64 (if not owned) | ≈ 190 ([lab setup](../17-test-measurement/lab-setup-by-budget.md)) |
| Reference ceramic patch for T5 | ≈ 5–15 |

## Practical notes
- Measure the Dk of your JLC lot from the *linear* calibration board: $\varepsilon_{eff}$ scales as $(f_{design}/f_{meas})^2$; then compute the final size instead of trimming by trial.
- The two-mode S11 trace shows two shallow dips straddling the AR frequency — that shape itself confirms the split is roughly right.
- For a rocket, a patch looks one way; under the parachute it may point at the ground. Plan GNSS coverage of descent separately ([GNSS antennas](../08-antennas/gnss-antennas.md)).

## Common mistakes & misconceptions
- **"A low-power L1 test source indoors is harmless and legal."** It is neither: 1559–1610 MHz (and 1164–1300 MHz) is a protected RNSS band with no licence-exempt allocation, and a few microwatts swamp every GNSS receiver nearby. Measure S11, test conducted or in a shielded enclosure, or use the real sky.
- **"Tune the CP patch for the best S11."** The S11 minimum (1599 MHz) is 24 MHz above the best AR (1575 MHz) in the final model.
- **"The coarse openEMS run looked right, so it is right."** Here a free-grid coarse mesh happened to land on 1575.0 MHz; the fine mesh put the same geometry at 1545 MHz. Lock mesh lines to metal edges (thirds rule) and always compare two meshes.
- **"Any corner cut gives RHCP."** The diagonal relative to the feed decides the sense; the first simulation of this recipe came out LHCP.
- **"The design formula gives the final dimensions."** It gave a cut 10 % too small and a side 0.4 % too large (44.88 vs 44.71 mm) on FR-4 even before Dk tolerance.
- **"FR-4 is too lossy for a GNSS patch."** It costs ≈ 3 dB versus Rogers (36 % vs ≈ 70 % efficiency) — acceptable for L1 in open sky, not for marginal installations.
- **"A bigger AR bandwidth comes from a better cut."** It is set by Q (≈ ½ the impedance bandwidth); use a thicker substrate or dual feed for more.

## How to simulate / verify
- `python3 tools/verify/proj_patch_gnss.py` — TL/cavity design, cut, tolerances, trim sensitivity, C/N0 budget.
- `~/opt/openEMS/venv/bin/python tools/verify/proj_openems_gnss_patch.py quick` (linear check + predicted CP), `design` (cut/probe sweep, RHCP), `edges 44.71 5.9 15.0` (final geometry, edge-locked coarse + fine mesh, far field). Results log in the script's docstring (append-only, including the non-converged v1).
- Fine-mesh convergence of the final design: 0.8 mm vs 0.5 mm edge-locked meshes agree to 0.16 % in AR-minimum frequency (script docstring, 2026-10-02).

## Open questions / gaps
- Measured Dk of JLC 2-layer FR-4 at 1.5 GHz (lot to lot) — the calibration board answers it.
- Effect of a nose-cone wall and of a 60 mm ground on AR (not simulated yet).
- Galileo E1 / BeiDou B1 coverage would need a dual-feed design; not modelled here.

## Sources
1. This KB, [Microstrip patch antennas](../08-antennas/patch-antennas.md) and `tools/verify/ant_patch.py` — TL model, Hammerstad fringing, Jackson–Alexopoulos Q/efficiency, two-mode CP model. (internal; Balanis 4th ed. ch. 14, Jackson in Volakis' *Antenna Engineering Handbook* ch. 7)
2. P. C. Sharma, K. C. Gupta, "Analysis and optimized design of single feed circularly polarized microstrip antennas," *IEEE Trans. Antennas Propag.* 31(6), 949–955, 1983 — truncated-corner CP patch (design rule rederived here by cavity perturbation). (peer-reviewed; not read in full)
3. This KB, [openEMS workflow](../16-simulation-tools/openems-workflow.md) and `tools/verify/sim_openems_patch.py` — mesh rules, end-criterion trap, 2.45 GHz FR-4 validation. (internal)
4. This KB, [GNSS antennas](../08-antennas/gnss-antennas.md) — ground-plane guidance, active-antenna requirements, minimum signal level, rocket failure modes. (internal; u-blox integration manuals)
5. This KB, [Stackups and materials](../13-pcb-rf-layout-emc/stackups-and-materials.md) — JLC 2-layer Dk 4.5 (capabilities page), core Dk 4.6, prepreg values, Rogers availability. (internal; JLCPCB)
6. This KB, [Antenna measurement](../08-antennas/antenna-measurement.md) and [NanoVNA practical](../17-test-measurement/nanovna-librevna-practical.md) — AR by rotating linear source, sense test, VNA ranges. (internal; IEEE Std 149)
7. T. Liebig, openEMS / CSXCAD v0.37 (EC-FDTD), https://openems.de — solver used for all full-wave results here. (software)
