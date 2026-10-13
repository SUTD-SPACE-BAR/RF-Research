---
title: Impedance and RF calculators — KiCad PCB Calculator, Qucs transcalc, Saturn PCB Toolkit, AppCAD, JLCPCB calculator, online tools and rfcalc, compared against a 2-D field solver
domain: 16-simulation-tools
slug: impedance-and-rf-calculators
tags: [impedance-calculator, microstrip, cpwg, stripline, kicad-pcb-calculator, transcalc, qucs, saturn-pcb-toolkit, appcad, jlcpcb, polar-si9000, ipc-2141, hammerstad-jensen, wheeler, soldermask, field-solver, rfcalc]
prerequisites: [../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md]
related: [python-rf-toolkit.md, openems-workflow.md, simulation-validation.md, ../13-pcb-rf-layout-emc/stackups-and-materials.md, ../03-transmission-lines-matching/coax-and-cables.md]
level: intro
confidence: high
last_updated: 2026-10-12
---

# Impedance and RF calculators

## Questions this page answers
- Which impedance calculator should I trust for a 50 Ω trace on a JLCPCB board?
- Why do KiCad, Saturn, JLCPCB and online calculators give different widths for the same 50 Ω line?
- How accurate is the IPC-2141 microstrip formula?
- How much do copper thickness and soldermask change Z0 on a 2-layer vs a 4-layer board?
- What other RF calculators are worth having (link budget, matching, noise, skin depth, LoRa air time)?
- How do I use this KB's `rfcalc` calculators from the command line?

## TL;DR
- Most calculators implement the **same closed forms** (Hammerstad–Jensen microstrip, Wheeler/Cohn stripline, Ghione–Naldi CPW/CPWG). KiCad's PCB Calculator descends from the Qucs/transcalc code (same authors' headers) [1]; `rfcalc` implements the same equations (ported from `tools/verify/tline_*.py`). Differences between calculators come mostly from **inputs and assumptions** — copper thickness, soldermask, εr — not the mathematics.
- **Against this KB's 2-D field solver** (`tools/verify/tline_fd2d.py`, Richardson-extrapolated), for bare, rectangular-copper geometry: H-J and Wheeler are within **0.1–0.3 %**; the Pozar/Hammerstad "simple" form 0.3–5 % (it ignores thickness); **IPC-2141 is 1.1–3.6 % low**; zero-thickness CPWG conformal mapping is 0.3–1 % high — but 35 µm copper then lowers CPWG Z0 by **3.3–3.7 Ω** and soldermask by another **≈ 3.2 Ω**.
- **Soldermask matters**: 20 µm of εr 3.8 mask lowers a 50 Ω microstrip by 0.3 Ω on the 1.6 mm board but 1.5–1.7 Ω on the 0.21 mm JLC-7628 prepreg, and CPWG by ≈ 3.2 Ω on both. JLCPCB's calculator assumes 1.2 mil base / 0.6 mil on-copper / 1.2 mil between-trace mask with εr 3.8 and 1.6 mil finished outer copper [4].
- Rule: **use the fab's calculator for the fab's stack-up** (it knows its Dk and finished thicknesses), cross-check with one independent method, and put a TDR coupon on the panel if the impedance really matters.
- `python3 -m rfcalc microstrip --h 1.51mm --er 4.5 --z0 50` → W = 2.797 mm (h = 1.51 mm is a model input; JLC's JLC0216A 2-layer stackup is a 1.43 mm core in a 1.6 mm finished board, and its calculator gives 2.69 mm masked — [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)); `python3 -m rfcalc cpwg --s 0.2mm --h 1.51mm --er 4.5 --z0 50`; `rfcalc link | cascade | lmatch | lora | skin | fmcw | …` ([tools/README.md](../../tools/README.md)).

## Intuition (no math)
A trace's impedance is set by how much capacitance and inductance it has per millimetre, and those are set by the electric field's shape: how much of it is in the dielectric, how much in air or soldermask, how much ends on the side grounds of a coplanar line. Closed-form calculators are curve fits to exact field solutions of an *idealised cross-section* (perfectly rectangular copper, homogeneous FR-4, nothing on top). They are superb for that ideal. Real boards have trapezoidal etched copper, 35 µm-thick conductors whose side walls add capacitance, a soldermask coating of uncertain thickness, and glass-weave-dependent εr. On a 1.6 mm two-layer board those corrections are small because the field is spread over a big region; on a 0.2 mm prepreg or a 0.2 mm CPWG gap the corrections are several ohms, because the field is squeezed exactly where the copper walls and mask sit.

## The math

### Level 1 — the formulas behind the buttons
- **Hammerstad–Jensen microstrip** ($u = W/h$): $Z_{0,air} = \frac{\eta_0}{2\pi}\ln\!\left[\frac{f(u)}{u}+\sqrt{1+\frac{4}{u^2}}\right]$, $f(u) = 6+(2\pi-6)e^{-(30.666/u)^{0.7528}}$, $Z_0 = Z_{0,air}/\sqrt{\varepsilon_{eff}}$ with a fitted $\varepsilon_{eff}(u,\varepsilon_r)$; thickness enters as an effective width increase $\Delta u$ [2]. Claimed accuracy better than 0.2–1 % over $0.01 \le u \le 100$.
- **IPC-2141 microstrip**: $Z_0 = \frac{87}{\sqrt{\varepsilon_r+1.41}}\ln\frac{5.98h}{0.8W+t}$ — a simple fit (after Kaupp, 1967) intended for $0.1 < W/h < 2$, $\varepsilon_r$ 1–15.
- **Ghione–Naldi CPWG** (zero thickness): $Z_0 = \frac{60\pi}{\sqrt{\varepsilon_{eff}}}\left[\frac{K(k_0)}{K(k_0')}+\frac{K(k_3)}{K(k_3')}\right]^{-1}$, $k_0 = \frac{W}{W+2S}$, $k_3 = \frac{\tanh(\pi W/4h)}{\tanh(\pi(W+2S)/4h)}$ [3].

### Level 2 — what a 2-D field solver does differently
It solves Laplace's equation $\nabla\cdot(\varepsilon\nabla\phi) = 0$ on the actual cross-section (finite-thickness rectangles, mask layers), computes the capacitance per unit length with and without dielectric, and gets $Z_0 = 1/(c\sqrt{C C_{air}})$, $\varepsilon_{eff} = C/C_{air}$ — no curve fit. `tools/verify/tline_fd2d.py` does this with a graded finite-volume mesh and Richardson extrapolation over three meshes; it reproduces Cohn's exact stripline within 0.3 % (its self-test).

### Level 3 — the error budget of a "50 Ω" trace
| Source | Typical size | Notes |
|---|---|---|
| Formula error (H-J vs exact) | < 0.3 % | negligible |
| εr uncertainty (FR-4 4.1–4.7) | ±1 Ω per ±0.2 in εr | largest on any board without a Dk-controlled stack-up |
| Etch width tolerance (±10–20 µm) | ±1 % on 2.8 mm; ±5 % on 0.36 mm | thin stack-ups suffer |
| Copper thickness (0 → 35 µm) | −0.5 Ω (h 1.5 mm) to −2.5 Ω (h 0.21 mm); CPWG −3.3 Ω | side-wall capacitance |
| Soldermask (20 µm, εr 3.8) | −0.3 Ω (h 1.5 mm) to −1.7 Ω (h 0.21 mm); CPWG −3.2 Ω | mask fills CPWG gaps |
| Trapezoidal etch | +0.5–1.5 Ω | narrower top |

## Design equations & rules of thumb

| Situation | Best tool | Expect |
|---|---|---|
| JLCPCB 4/6-layer impedance-controlled stack-up | JLCPCB calculator (their Dk, mask, finished copper) | fab-guaranteed ±10 % (confirm at order time) |
| 2-layer FR-4 (no impedance control) | any H-J calculator (KiCad, rfcalc) with t = 35 µm and εr ≈ 4.5 | ±2–3 Ω from εr alone |
| CPWG with gaps ≤ 0.3 mm | field solver with thickness + mask (tline_fd2d, openEMS) or the fab's calculator | conformal formula 3–7 Ω high |
| Differential pairs | field solver or fab calculator | IPC-2141 edge-coupled formula ±1–3 % (planar-lines page) |
| Anything critical (antenna feed at 2.4 GHz+) | TDR coupon on the panel | measured truth |

## Worked examples

### 1 — six calculators, three microstrips (bare copper, no mask unless stated)
Computed 2026-09-29 with `tools/rfcalc/tline.py` and the FD solver (`tline_microstrip.fd_ms`, `tline_cpwg.fd_cpwg`):

| Geometry | t | H-J | Wheeler-77 | "simple" | IPC-2141 | **FD solver** | FD + 20 µm mask |
|---|---|---|---|---|---|---|---|
| 2-layer: W 2.80 / h 1.51 mm, εr 4.5 | 0 | 50.44 | 50.34 | 50.64 | — | **50.38** | — |
| same | 35 µm | 49.97 | 49.90 | 50.64 | 49.33 | **49.90** | 49.60 |
| JLC-7628 L1: W 0.36 / h 0.2104 mm, εr 4.4 | 0 | 53.42 | 53.33 | 53.61 | — | **53.36** | — |
| same | 35 µm | 50.92 | 50.98 | 53.61 | 49.08 | **50.89** | 49.37 |
| JLC-7628 L1: W 0.3244 mm (JITX published) | 35 µm | 53.86 | 53.96 | 56.86 | 52.41 | **53.82** | 52.12 |

(Ω; openEMS gave 50.31 Ω for the first row, [openEMS workflow](openems-workflow.md).) H-J and Wheeler track the field solver to ≤ 0.15 Ω. The "simple" formula has no thickness term (+2.7 Ω on the thin stack-up). IPC-2141 is 0.6–1.8 Ω low — acceptable for a first guess, not for final widths.

### 2 — CPWG: the thickness and mask effect dominates
| Geometry | Conformal (t = 0) | FD t = 0 | FD t = 35 µm | FD 35 µm + 20 µm mask |
|---|---|---|---|---|
| 2-layer: W 1.01, S 0.20, h 1.51 mm, εr 4.5 | 53.43 | 53.25 | **49.95** | 46.75 |
| JLC-7628: W 0.34, S 0.20, h 0.2104 mm, εr 4.4 | 52.90 | 52.40 | **48.69** | 45.47 |

A calculator that ignores copper thickness (conformal mapping, zero-thickness) says 53 Ω for a line that is really ≈ 47 Ω once masked — a 12 % error, VSWR 1.13 on its own. This is the "calculators disagree by several ohms" observation of the [planar-lines page](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md#worked-examples), traced to its cause. KiCad's CPW model adds a thickness correction (Gupta et al.) and, in current KiCad source, an approximate soldermask correction (Wan–Hoorfar/Svacina filling factors) [1]; check which KiCad version you run and whether the mask option is enabled.

### 3 — the rest of the RF calculator shelf, from the command line
```bash
cd tools
python3 -m rfcalc microstrip --h 1.51mm --er 4.5 --z0 50 --f 915M   # W 2.797 mm; K-J 49.98 ohm, lambda_g/4 44.58 mm
python3 -m rfcalc cpwg --s 0.2mm --h 1.51mm --er 4.5 --z0 50        # zero-thickness model (see Example 2!)
python3 -m rfcalc coax 2.74mm 7.24mm --er 1.384                      # LMR-400: 49.52 ohm
python3 -m rfcalc lmatch 32.1-18.5j --f 433M                         # 15.61 nH + 5.49 pF, or 67.19 pF + 24.61 nH
python3 -m rfcalc link --f 433.125M --d 30km --pt 33 --tx-loss 0.5 --gr 11 --rx-loss 0.45 --other 4.1 --sf 7 --margin 20
python3 -m rfcalc cascade --stage SAW:-1.5 --stage LNA:18:0.7:8 --stage coax:-2.6 --stage module:0:6:-5 --bw 125k --snr -20
python3 -m rfcalc lora --sf 9 --pl 32                                # 246.78 ms, 1758 b/s, -129.5 dBm
python3 -m rfcalc skin 433M                                          # 3.176 um, 5.429 mohm/sq
python3 -m rfcalc fmcw --f0 77G --bw 4G --tc 40e-6 --fs 10M          # 3.75 cm resolution, 15 m max range
python3 -m rfcalc db vswr 2                                          # RL 9.54 dB, mismatch loss 0.512 dB
```
Every number printed above is also a pytest assertion in `tools/rfcalc/tests/` (with the KB page it comes from).

## Practical notes
- **KiCad PCB Calculator** (built into KiCad; GUI): transmission lines (microstrip, CPW/CPWG, stripline, coupled lines, coax, waveguide, twisted pair), attenuators, E-series, track width vs current (IPC-2221), via properties, colour code. Microstrip = H-J with thickness correction and K-J dispersion (same equations as rfcalc) [1].
- **Qucs / Qucs-S "transcalc"**: the ancestor of KiCad's calculator (same authors: G. Narayanan, C. Girardi, S. Jahn); Qucs-S on macOS is an unsigned cask (Gatekeeper blocks first launch; owner's decision) — not needed, KiCad has the same models.
- **Saturn PCB Toolkit** (free, Windows): impedance (with Default/Wadell/IPC-2141 formula options), current capacity, via current and thermal, crosstalk, conductor impedance, PPM/frequency tools [5]. Popular in hobby and professional use; formula choice changes results by 1–3 %.
- **AppCAD** (Avago/Broadcom, free, Windows; availability varies): line impedances, noise/IP3 cascade, link budget, mixer spurs, bias circuits — a classic RF "pocket calculator"; rfcalc covers the same ground on macOS.
- **JLCPCB impedance calculator** (web): synthesises width for its own stack-ups; states its mask and copper assumptions (above) but not its solver [4]. Polar Si9000 (commercial 2-D field solver) is the industry reference many fabs use internally.
- **Online calculators**: fine for sanity checks; many implement IPC-2141 only (1–4 % low) or ignore thickness; check which model they state.
- **Field solvers you already have**: `tools/verify/tline_fd2d.py` (2-D quasi-static, ~2–5 s per geometry), openEMS (3-D, full-wave, includes dispersion and radiation), scikit-rf `MLine`/`CPW` (closed forms).

## Common mistakes & misconceptions
- **Using the total board thickness as h on a 4-layer board** — h is the distance to the nearest reference plane (0.2104 mm on JLC-7628).
- **Using a zero-thickness CPWG calculator for 0.2 mm gaps** — 3–4 Ω high before mask, 6–7 Ω high after.
- **Believing a calculator's 4 significant figures** — the εr you typed is uncertain by ±5 %; that alone is ±1 Ω.
- **Mixing mask assumptions** — JLCPCB's calculator includes mask; a bare-copper calculator does not; compare like with like.
- **IPC-2141 outside its fitted range** (W/h > 2 or thin dielectrics) — errors grow beyond 5 %.
- **Assuming the 2-layer JLCPCB board is impedance-controlled** — it is not guaranteed; design with margin or measure.

## How to simulate / verify
- `cd tools && python3 -m pytest rfcalc/tests -q` (142 tests; `test_tline.py` pins H-J to the FD solver and the CPWG formula to its zero-thickness FD value).
- `python3 tools/verify/tline_microstrip.py` and `tline_cpwg.py` (W1-A4) — full FD comparisons incl. mask and JLC stack-ups (3–5 min).
- `~/opt/openEMS/venv/bin/python tools/verify/sim_openems_msl.py` — 3-D full-wave check of the 2-layer line.
- Measurement: TDR ([time-domain reflectometry](../03-transmission-lines-matching/time-domain-reflectometry.md)) or a NanoVNA two-line (TRL-style) εeff/Z0 extraction.

## Open questions / gaps
- JLCPCB does not publish which solver its calculator uses; a head-to-head of its CPWG widths against the FD solver with its stated mask thicknesses would pin down its model.
- KiCad's new soldermask correction (source, 2026) was not exercised — the calculator is a GUI and was not launched here.
- Saturn PCB Toolkit and AppCAD were not run (Windows-only); their behaviour is described from documentation/secondary sources.

## Sources
1. KiCad source, `common/transline_calculations/microstrip.cpp`, `coplanar.cpp`, `transline_calculation_base.cpp` (gitlab.com/kicad/code/kicad, master, 2026-09) — H-J/K-J microstrip, Ghione–Naldi CPW with Gupta thickness correction, Wan–Hoorfar/Svacina soldermask correction; copyright headers crediting the transcalc/Qucs authors. (tool source)
2. E. Hammerstad and Ø. Jensen, "Accurate models for microstrip computer-aided design," *IEEE MTT-S Int. Microwave Symp. Digest*, 1980, pp. 407–409; H. A. Wheeler, "Transmission-line properties of a strip on a dielectric sheet on a plane," *IEEE Trans. MTT*, 25(8):631–647, 1977. (peer-reviewed)
3. G. Ghione and C. U. Naldi, "Coplanar waveguides for MMIC applications: effect of upper shielding, conductor backing, finite-extent ground planes, and line-to-line coupling," *IEEE Trans. MTT*, 35(3):260–267, 1987; and *Electronics Letters* 20(4):179–181, 1984. (peer-reviewed)
4. JLCPCB, "User Guide to the JLCPCB Impedance Calculator," https://jlcpcb.com/help/article/User-Guide-to-the-JLCPCB-Impedance-Calculator — mask 1.2/0.6/1.2 mil, εr 3.8; outer copper 1.6 mil finished. (vendor documentation)
5. Saturn PCB Design, "Saturn PCB Toolkit" and help pages, https://saturnpcb.com/saturn-pcb-toolkit/ — features and formula options. (vendor documentation)
6. IPC-2141A, *Design Guide for High-Speed Controlled Impedance Circuit Boards*, IPC, 2004. (standard)
7. B. C. Wadell, *Transmission Line Design Handbook*, Artech House, 1991. (textbook)
8. This repository: `tools/verify/tline_fd2d.py`, `tline_microstrip.py`, `tline_cpwg.py` (W1-A4); `tools/rfcalc/tline.py` and `tests/test_tline.py` (W3-C2). (verification)
