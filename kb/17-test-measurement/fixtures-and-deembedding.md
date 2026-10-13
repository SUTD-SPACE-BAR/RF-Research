---
title: Test fixtures and de-embedding — SMD component fixtures, TRL/LRM calibration kits on JLCPCB boards, 2x-thru (IEEE P370) and AFR, open/short compensation, reference-plane management, and measuring chip antennas on small boards
domain: 17-test-measurement
slug: fixtures-and-deembedding
tags: [fixture, de-embedding, 2x-thru, ieee-p370, afr, trl, lrm, reference-plane, port-extension, open-short, smd, 0402, jlcpcb, microstrip, cpwg, sma-edge-launch, chip-antenna, pigtail, common-mode, ferrite, sleeve-balun]
prerequisites: [vna-fundamentals-calibration.md, ../03-transmission-lines-matching/s-parameters.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md]
related: [nanovna-librevna-practical.md, rf-bring-up-debug-playbook.md, ../04-real-components-hf/component-models-s2p-spice.md, ../08-antennas/pcb-and-chip-antennas.md, ../08-antennas/antenna-matching-and-baluns.md, ../13-pcb-rf-layout-emc/connectors-and-launches.md, ../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md, ../13-pcb-rf-layout-emc/stackups-and-materials.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Test fixtures and de-embedding

## Questions this page answers
- How do I measure a 0402 inductor, capacitor or filter that has no connectors?
- What is the difference between port extension, open/short compensation, 2x-thru de-embedding and TRL?
- How do I design TRL standards on a cheap JLCPCB board, and how long should the lines be?
- When does 2x-thru de-embedding go wrong?
- Where exactly is my reference plane when I measure a chip antenna through a U.FL pigtail?
- How do I stop the test cable from becoming part of a small-board antenna?
- Can the same fixture panel measure the permittivity of my FR-4 or nose-cone material?

## TL;DR
- **Hierarchy of methods** (from crude to rigorous): port extension (delay [+ loss]) → open/short compensation (lumped residuals) → 2x-thru de-embedding (IEEE P370; needs a symmetric fixture) → TRL/LRM calibration on the fixture itself (moves the calibration plane to the DUT pads). The theory of cascading and inverting T-matrices is in [S-parameters](../03-transmission-lines-matching/s-parameters.md); calibration algebra in [VNA calibration](vna-fundamentals-calibration.md).
- **Example (script)**: a 10 nH 0402 inductor (series R 1 Ω, 0.08 pF) behind two SMA launches + 15 mm of microstrip reads **28.1 nH raw** at 433 MHz, **12.1 nH** with port extension, **9.8 nH** after P370 2x-thru de-embedding and exactly 10.06 nH with the true fixture removed. At 915 MHz: 20.5/12.5/10.0/10.27 nH. 2x-thru is good to ≈ 3 % here; port extension leaves the launch parasitics in (+20 %).
- **2x-thru assumes FIX-1 = mirror(FIX-2).** Check symmetry by TDR; the P370 "Z-corrected" variant is for fixtures whose impedance differs from the DUT region — applied to a lumped DUT here it made the result *worse* (9.2 nH vs 9.8 nH).
- **Open/short compensation** (Z = (Z_m − Z_s)/(1 − (Z_m − Z_s)Y_o)) is exact for a series-Z/shunt-Y residual: a 2.2 pF capacitor behind 0.8 nH + 0.12 pF of pad reads 35.6 Ω instead of 45.9 Ω at 1575 MHz raw, 43.6 Ω with short-only, 45.96 Ω with open + short.
- **TRL on JLCPCB FR-4** (ε_eff ≈ 3.3 for 50 Ω microstrip on 1.6 mm): two lines, ≈ 31 mm and ≈ 12 mm longer than the thru, cover 0.30–2.40 and 0.75–6.0 GHz; below 0.3 GHz add a match (LRM) or a very long line (~92 mm for 0.1–0.8 GHz).
- **Chip/PCB antennas on small boards**: the test cable's shield carries common-mode current and *extends the ground plane*. Solder a semi-rigid/U.FL pigtail along the ground, exit where the flight cable would, add ferrites or a λ/4 sleeve balun, calibrate at the pigtail end (or port-extend), and confirm with the touch test.

## Intuition (no math)
Your VNA is calibrated at its SMA connectors; your DUT is a 1 × 0.5 mm part soldered to two pads 20 mm further along a PCB. Everything in between — the SMA launch (a small capacitance and inductance), the microstrip (delay and loss), the pads (more capacitance) — is measured together with the DUT. De-embedding means measuring that "in between" separately and removing it mathematically. The simplest assumption (it's just a delay) removes most of the phase error but none of the launch parasitics; better methods measure the fixture itself (a 2x-thru is two fixture halves joined, which you can split in two) or calibrate right at the pads with standards built on the same board (TRL/LRM).

Antennas are special: the "fixture" (cable and board) radiates too. The coax shield is a second conductor that, left alone, becomes part of the antenna, so the measured S11 depends on where the cable runs and whether you touch it.

## The math

### Level 1 — the methods in one line each
- **Port extension**: Γ_DUT = Γ_M e^{+j2ωτ}·10^{2L/20} (one-port); for two-port, remove e^{−jωτ} from each side. Exact only for a matched uniform line.
- **Open/short (1-port, residual Z_s in series then Y_o shunt)**: measure Z_short = Z_s (pads shorted), Y_open = 1/(Z_s + 1/Y_o) (nothing mounted), then Z_DUT = (Z_m − Z_short)/[1 − (Z_m − Z_short)Y_open].
- **T-matrix de-embedding**: T_DUT = T_FIX1⁻¹ T_meas T_FIX2⁻¹ (scikit-rf: `fixL.inv ** meas ** fixR.inv`).
- **2x-thru (IEEE P370)**: measure FIX-1 + FIX-2 joined (2x-thru), split it into two halves by time-domain gating of S11/S22 and a root of S21, then de-embed as above [1].
- **TRL**: calibrate with standards on the fixture — thru (the two halves joined), reflect (open or short at the DUT plane), line(s) (thru + Δl) — see the eigen-problem in [VNA calibration](vna-fundamentals-calibration.md) [2].
- **TRL line length**: Δl = c/(4 f_c √ε_eff), usable 20°–160° → f_c·(0.222 … 1.778).

### Level 2 — why each method works (and fails)
**Open/short** assumes the residual is a series impedance followed by a shunt admittance at the DUT. With Z_m = Z_s + 1/(Y_o + 1/Z), subtracting Z_s and inverting the shunt gives the formula above exactly (script §3: 47 Ω → 47.00 Ω; 2.2 pF → 79.08 vs 79.06 Ω at 915 MHz; 8.2 nH → 81.07 vs 81.15 Ω at 1575 MHz). It is the method used by LCR meters and the NanoVNA-Saver-style "fixture compensation"; its limit is that the residual is only a lumped approximation — once the fixture is an appreciable fraction of a wavelength (≈ λ/20), use a two-port method.

**2x-thru.** If FIX-2 is the mirror image of FIX-1, the 2x-thru's S-parameters contain enough information to recover each half: in the time domain the reflections of the left half arrive before those of the right half; gating S11 of the 2x-thru up to the midpoint and taking a square root of the (return-loss-corrected) S21 yields the half [1]. The scikit-rf implementation notes that this is "crude but robust" and uses a more robust root choice than the original MATLAB code [3]. Errors come from (a) asymmetry — in our script a right launch with 0.35 pF instead of 0.25 pF gave 9.86 nH at 915 MHz (true 10.27; symmetric case 9.98), (b) limited bandwidth → coarse time resolution (the halves' reflections overlap for short fixtures), (c) the DC extrapolation needed for the time transform.

**TRL.** Because the thru, line and reflect are built from the same trace geometry as the fixture, TRL makes the *line's* impedance the reference and needs no lumped model of the launch — the best accuracy for PCB fixtures [2], [4]. Constraints: the line must differ from the thru by 20°–160° at every frequency (8:1 band per line; use multiline or add a match), the reflect must be the same on both ports, and all standards must be manufactured identically (same etch, same launch soldering). Reference plane = the centre of the thru (or wherever you define the thru's length).

### Level 3 — reference planes and small antennas
- **Coax connectors**: the SMA reference plane is the outer-conductor mating plane ([VNA calibration](vna-fundamentals-calibration.md)). A U.FL pigtail adds a mated U.FL pair (a small capacitive discontinuity, modelled as ~0.15 pF in the VNA page) plus 1.13 mm or 1.37 mm micro-coax (v_f ≈ 0.7). Calibrate at the U.FL end with a U.FL SOL kit or de-embed the characterised pigtail; port extension alone leaves the U.FL discontinuity (≈ 1 Ω of error at 915 MHz, several ohms at 2.45 GHz; VNA page §7).
- **Chip antennas on small boards** (TI AN058 method [5]): solder a semi-rigid cable's shield flat along the ground plane from the feed point to the board edge where the real cable/harness leaves, centre conductor to the feed pad; calibrate at the cable's far end and set port extension with an open/short at the feed. Because the shield continues the ground plane, the board "looks bigger" — part of the reason chip-antenna datasheet numbers on large evaluation boards don't transfer to small flight boards ([PCB & chip antennas](../08-antennas/pcb-and-chip-antennas.md)).
- **Common-mode suppression**: ferrite beads/clamps on the cable within a few cm of the board (check the ferrite mix's impedance at 433/915 MHz; below ~300 MHz #43, at UHF #61 or specialised UHF ferrite), or a λ/4 sleeve balun (sleeve length ≈ λ/4 × velocity factor of the sleeve-to-shield line) ([baluns](../08-antennas/antenna-matching-and-baluns.md)). Verify: S11 must not change when you grab or re-route the cable beyond the choke.
- **Material permittivity and loss (εr, tanδ) from fixtures.** The same JLC panel that carries TRL standards can carry material coupons: the phase difference between two lines of different length (the TRL line-minus-thru pair) gives the line's ε_eff and its loss without the launches, and resonant coupons (ring/split-ring resonators) or a cavity give εr and tanδ from resonance shifts and Q. These methods — the perturbation derivation, the two-line and ring-resonator coupons for FR-4 lots, nose-cone fibreglass, coupling and Q₀ extraction and the uncertainty budget — are on the dedicated page [resonator and cavity-perturbation permittivity measurement](resonator-and-cavity-perturbation-permittivity-measurement.md) (W5-E11). Use the coupled-loop Q recipe in [bench recipes R11](bench-measurement-recipes.md#r11--resonance-and-q-with-coupled-loops-dip-meter-substitute) for the resonance and Q readings.

## Design equations & rules of thumb

| Item | Rule / value | Notes |
|---|---|---|
| When is a fixture "lumped"? | length < λ/20 in the substrate | 915 MHz FR-4: ~9 mm |
| Open/short | Z = (Z_m − Z_s)/(1 − (Z_m − Z_s)Y_o) | exact for series-Z/shunt-Y |
| 2x-thru | halves must be mirror images | check by TDR |
| TRL Δl | c/(4 f_c √ε_eff) | ε_eff ≈ 3.3 (1.6 mm FR-4 microstrip) |
| TRL band | 0.222 f_c … 1.778 f_c | 20°–160° |
| Two-line plan 0.3–6 GHz | Δl ≈ 31 mm and ≈ 12 mm | + match below 0.3 GHz |
| SMA edge launch | tune the launch (pad cut-outs, via fence) for RL > 20 dB | see domain 13 connectors |
| Chip antenna test cable | exit where the real cable exits; choke it | touch test |

## Worked examples

**Example 1 — a 0402 inductor on a two-SMA fixture (script §1).** Fixture half = SMA launch (0.25 pF shunt + 0.3 nH) + 15 mm of 50 Ω microstrip (ε_eff 3.3, 3 dB/m at 1 GHz). Reading L = X/ω from the series-through formula:

| Frequency | True | Raw | Port extension | P370 2x-thru | Exact fixture removal |
|---|---|---|---|---|---|
| 433 MHz | 10.06 nH | 28.07 | 12.08 | 9.77 | 10.06 |
| 915 MHz | 10.27 nH | 20.53 | 12.52 | 9.98 | 10.27 |
| 2.45 GHz | 12.34 nH | −12.31 | 14.51 | 12.12 | 12.34 |
| 5.0 GHz | 47.51 nH | 46.13 | 35.69 | 49.28 | 47.51 |

(The apparent L rises toward the 5.6 GHz self-resonance — a real effect.) The raw number is meaningless; port extension is +20 % off because the launch parasitics remain; P370 is within ≈ 3 % below 2.5 GHz; P370 max |S| error below 5 GHz is 0.019.

**Example 2 — measuring a matching capacitor on the flight board's pads.** Remove the antenna, solder a U.FL pigtail at the pi-network output, measure: (1) pads shorted with a 0 Ω link → Z_s, (2) pads empty → Y_o, (3) the part → Z_m; apply the open/short formula. Script §3 shows a 2.2 pF part at 1575 MHz: raw 35.6 Ω, short-only 43.6 Ω, open + short 45.96 Ω (true 45.93 Ω). This is also how you extract the pads' parasitic capacitance (≈ 0.1–0.2 pF) to include in the matching design ([NanoVNA Recipe B](nanovna-librevna-practical.md)).

**Example 3 — a JLCPCB TRL kit for 433 MHz–2.4 GHz.** 2-layer 1.6 mm FR-4, 50 Ω microstrip (or CPWG, which is less sensitive to solder-mask and has a well-defined launch). Standards on one panel, identical SMA edge launches: THRU (2 × 20 mm = 40 mm; reference planes 20 mm from each launch), LINE-1 (40 + 30.6 mm; 0.30–2.40 GHz), LINE-2 (40 + 12.2 mm; 0.75–6.0 GHz), REFLECT (20 mm to an open end, or a short to a via fence, one per port), plus optional MATCH (two 0402 100 Ω in parallel to ground at 20 mm) for LRM below 0.3 GHz. Put the DUT footprints on the same panel with 20 mm lead-ins. Fabrication tolerance on ε_r and trace width shifts Z0 by a few ohms — TRL then references to *that* Z0 (renormalise to 50 Ω if the line impedance is characterised).

**Example 4 — chip antenna for 915 MHz on a 30 × 60 mm flight board.** Following the pigtail method, first measurements show resonance at 880 MHz; after adding three ferrite clamps and moving the cable to exit along the board's short edge (where the harness exits in the rocket), resonance moves to 902 MHz and the touch test changes |S11| by < 0.5 dB. The remaining offset is real (small ground plane) — retune the match in the final enclosure. (Illustrative numbers.)

## Practical notes
- **Build fixtures in pairs** (fixture-DUT-fixture and a 2x-thru with the identical launch) on the same panel; order a few spare boards — soldering SMA edge launches is the main source of asymmetry.
- **Launch quality**: an SMA edge launch on 1.6 mm FR-4 needs the ground cut-out/pad tuned; check the 2x-thru's TDR — a launch bump larger than a few ohms makes every method less accurate ([connectors & launches](../13-pcb-rf-layout-emc/connectors-and-launches.md)).
- **Keep fixtures short** relative to λ/20 where you rely on lumped (open/short) methods.
- **Record fixture files** (2x-thru .s2p, standards .s2p, cal sets) with the DUT data; de-embedding is reproducible only if the fixture data are saved.
- **scikit-rf** provides `IEEEP370_SE_NZC_2xThru`, `IEEEP370_SE_ZC_2xThru`, mixed-mode variants, and `OpenShort`, `ShortOpen`, `SplitPi`, `SplitTee` de-embedding classes in `skrf.calibration.deembedding` [3]; `NISTMultilineTRL` for multiline TRL.
- **Commercial AFR** (automatic fixture removal, e.g. Keysight/Copper Mountain plug-ins) automates 2x-thru and 1x-reflect methods [6].

## Common mistakes & misconceptions
- **Using port extension to "remove" an SMA launch** — it removes delay, not the launch's L and C.
- **2x-thru on an asymmetric fixture** (different launch soldering on each side).
- **Calibrating TRL outside its 20°–160° band** — noisy, wrong results at the band edges.
- **Measuring a chip antenna with a cable that exits in a different direction from the flight harness** — the ground extension differs.
- **Forgetting the pads** — two 0402 pads add ~0.1–0.2 pF, which matters in a 915 MHz matching network.
- **Comparing with a vendor .s2p measured on a different fixture/pad layout** without accounting for pad parasitics ([component models](../04-real-components-hf/component-models-s2p-spice.md)).

## How to simulate / verify
- `python3 tools/verify/meas_deembed.py` — (1) raw vs port extension vs P370 2x-thru vs exact de-embedding of an 0402 inductor; (2) asymmetric-fixture 2x-thru error; (3) one-port open/short compensation; (4) TRL line plan; (5) P370 NZC vs ZC comparison.
- `tools/verify/meas_vna_cal.py` §5 for TRL maths and §7 for port extension vs de-embedding of a U.FL pigtail.
- EM-simulate the launch and fixture (openEMS, domain 16) and compare with the de-embedded 2x-thru halves.

## Open questions / gaps
- The IEEE P370-2020 standard itself was not read; the method description relies on the scikit-rf documentation [3] and its cited references.
- No measured JLCPCB TRL kit data yet; ε_eff 3.3 is a typical value — domain 13 stackup pages give JLCPCB-specific dielectric data.
- Sleeve-balun dimensions for 433/915 MHz test cables should be computed/verified in domain 08.

## Sources
1. IEEE Std 370-2020, *Electrical Characterization of Printed Circuit Board and Related Interconnects at Frequencies up to 50 GHz* — 2x-thru de-embedding, fixture quality metrics. (standard; cited via [3])
2. G. F. Engen and C. A. Hoer, "Thru-Reflect-Line," *IEEE Trans. MTT* 27(12), 1979; Keysight 5989-4840 cal-kit note (TRL ±20° rule). (peer-reviewed / app note; cited, read respectively)
3. scikit-rf documentation, `skrf.calibration.deembedding` — IEEEP370_SE_NZC_2xThru ("S-parameters bisection by time gating S11 and S22, proper square root of S21 … crude results but robust", robust root choice), ZC and mixed-mode variants, OpenShort/SplitPi/SplitTee classes (docstrings, v2.0.1). (open-source docs; read)
4. Agilent AN 1287-3 — TRL for non-coaxial (fixture) measurements. (app note; read)
5. TI AN058 (SWRA161), "Antenna Selection Guide" — VNA measurement of PCB antennas with a semi-rigid cable soldered to ground, calibration and port extension. (app note; cited via domain 08)
6. Copper Mountain Technologies, "VNA Master Class" handout — fixture removal plug-in references. (vendor seminar; read)
7. This repository: `tools/verify/meas_deembed.py`, `tools/verify/meas_vna_cal.py`. (verification)
