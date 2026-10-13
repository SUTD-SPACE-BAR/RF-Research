---
title: NanoVNA, LiteVNA and LibreVNA in practice — models, firmware, accuracy vs frequency, software, and step-by-step recipes (antenna S11 in situ, matching, filters, cables, TDR, SMD parts)
domain: 17-test-measurement
slug: nanovna-librevna-practical
tags: [nanovna, nanovna-h4, nanovna-v2, litevna, librevna, nanovna-saver, nanovna-app, dislord, tdr, antenna-measurement, matching, pi-network, filter, velocity-factor, cable-loss, common-mode, smd-measurement]
prerequisites: [vna-fundamentals-calibration.md, ../03-transmission-lines-matching/smith-chart.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md]
related: [fixtures-and-deembedding.md, lab-setup-by-budget.md, rf-bring-up-debug-playbook.md, antenna-range-ota-testing.md, ../08-antennas/antenna-measurement.md, ../08-antennas/antenna-matching-and-baluns.md, ../08-antennas/pcb-and-chip-antennas.md, ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md, ../03-transmission-lines-matching/coax-and-cables.md, ../03-transmission-lines-matching/time-domain-reflectometry.md]
level: intro
confidence: medium
last_updated: 2026-10-12
---

# NanoVNA, LiteVNA and LibreVNA in practice

## Questions this page answers
- Which low-cost VNA should I buy (NanoVNA-H4, NanoVNA V2 Plus4, LiteVNA, LibreVNA) for 433 MHz, 915 MHz and GNSS work?
- Why does my NanoVNA get noisy above 300 MHz, and how far can I trust it at 915 MHz and 1.5 GHz?
- Which firmware and PC software should I use?
- How do I measure my rocket's antenna S11 in its final position without the cable lying to me?
- How do I tune a pi-match footprint on my board with a NanoVNA?
- How do I measure a filter's S21, a cable's loss and velocity factor, or find a fault with TDR?
- How do I measure an SMD inductor, capacitor or ferrite bead with a NanoVNA?
- Why does the SWR change when I touch the cable, and how do I stop it?
- Can I connect an LNA or a transmitter directly to the NanoVNA?
- How do I build and characterise my own SMA calibration kit, and is LibreCAL worth it?
- How do I calibrate through a UHF, BNC, MMCX or U.FL adapter?
- Can I set the NanoVNA to 73 Ω or 75 Ω to measure a dipole or TV coax?

## TL;DR
- **Model choice (2026)**: NanoVNA-H4 (≈ US$110 [11]) is fine up to ~900 MHz: > 70 dB dynamic range to 300 MHz, > 60 dB to 900 MHz, > 40 dB to 1.5 GHz [3], [4]. For GNSS (1.575 GHz) and 2.4 GHz buy a **LiteVNA 64** (50 kHz–6.3 GHz, > 70 dB below 3 GHz, ≈ US$190 [5], [11]) or **NanoVNA V2 Plus4** (to 4.4 GHz, 90 dB at 1 GHz with averaging, no harmonic mode [6]). **LibreVNA** (100 kHz–6 GHz, true two-receiver 2-port, 85–105 dB S21 range to 2.94 GHz, PC-only) is the "serious" open-source option [7].
- **Harmonic mode**: NanoVNA-H/H4 use the Si5351's odd harmonics above ~300 MHz; the output drops ~10–13 dB and trace noise rises [3], [8]. Expect ±0.5–1 dB and a few degrees of noise at 900 MHz; average and narrow the IF bandwidth.
- **Output power** is only ≈ −12 to −15 dBm below 300 MHz [9]; fine for passives and small-signal amplifiers, but **never connect a transmitter** to either port — use ≥ 40 dB of rated attenuation or a coupler, or a spectrum analyzer instead.
- **Firmware/software**: DiSlord firmware (NanoVNA-D) on H/H4; NanoVNA-Saver (multi-segment sweeps > 10 k points, averaging, non-ideal cal kits, TDR, Touchstone) [10]; NanoVNA-App (Windows); NanoVNA-QT for V2; LibreVNA-GUI; then scikit-rf for analysis.
- **Antenna S11 in situ**: calibrate at the end of the test cable (or at the U.FL pigtail end), choke the cable with ferrites at the antenna, measure in the final airframe/enclosure, and use the "grab the cable" test — if S11 moves, common-mode current is flowing.
- **TDR**: alias-free one-way length = v_f·c/(2Δf); resolution ≈ v_f·c·(0.98/span)/2. NanoVNA-H at 101 points to 900 MHz: ~11 m range and ~0.11 m resolution in v_f 0.66 coax; LiteVNA 1001 points to 6.3 GHz: ~16 m and ~15 mm (script).
- **Calibration practice**: build DIY standards short, characterise them once against a trusted kit (delay + C0/C1, load as data), use LibreCAL with LibreVNA, calibrate at the far end of any UHF/MMCX/U.FL adapter, and renormalise in software instead of "calibrating for 73 Ω" ([section below](#calibration-practice--diy-kits-librecal-adapters-reference-and-the-73-ω-myth)).
- **SMD parts**: use reflection for 5 Ω–1 kΩ, **series-through** (Z = 2Z0(1/S21 − 1)) for high impedances (chokes, beads, small C: 1–100 kΩ) and **shunt-through** (Z = Z0·S21/(2(1 − S21))) for low impedances (< 2 Ω: big capacitors, ESR) — accuracy map in `tools/verify/meas_nanovna.py`.

## Intuition (no math)
A NanoVNA is a real vector network analyzer squeezed into a pocket: a signal source, a resistive bridge to separate the wave going out of port CH0 from the one coming back, a second receiver on CH1 for transmission, and a microcontroller doing the error correction. It is a **1.5-port** instrument — it measures S11 and S21 only. Its weaknesses are the ones you'd expect from a US$100 device: low output power, a square-wave source whose harmonics are used above 300 MHz (less signal, more noise), modest shielding, drift with temperature, and a simple SMA cal kit whose exact electrical definition nobody publishes. None of that stops it from telling you, correctly, that your 433 MHz whip resonates at 410 MHz, or that your 915 MHz match is 12 pF instead of 1.2 pF. Most "the NanoVNA lied" stories are really about *where* the calibration plane was, a cable that became part of the antenna, or an overdriven DUT.

## The math

### Level 1 — what the instrument reports
- Reflection: Γ = S11; RL = −20 log|Γ|; VSWR = (1 + |Γ|)/(1 − |Γ|); Z = Z0(1 + Γ)/(1 − Γ). Series equivalent R + jX, and L = X/ω or C = −1/(ωX) at each point.
- Transmission: S21 in dB (insertion loss/gain), phase, group delay τ_g = −dφ/dω.
- Q of a component from a reflection measurement: Q = |X|/R (only meaningful when R is well above the residual directivity limit — see the accuracy map).

### Level 2 — formulas behind the recipes
**Series-through and shunt-through fixtures** (DUT between CH0 and CH1 of a 2-port setup):
$$S_{21}^{\text{series}}=\frac{2Z_0}{2Z_0+Z}\;\Rightarrow\;Z=2Z_0\Big(\frac{1}{S_{21}}-1\Big),\qquad
S_{21}^{\text{shunt}}=\frac{2Z}{2Z+Z_0}\;\Rightarrow\;Z=\frac{Z_0\,S_{21}}{2(1-S_{21})}.$$
The reflection method is limited by the residual directivity and source match (errors of ~0.005 in Γ); the transmission methods by the S21 noise floor (~10⁻⁴, −80 dB) and tracking. With those error levels (script §2) the worst-case |Z| error is < 10 % for: reflection 5 Ω–~500 Ω (2 % at 50 Ω, 25 % at 1 kΩ); series-through ~20 Ω–100 kΩ (2 % at 1–5 kΩ); shunt-through 0.05–~50 Ω (2–3 % at 0.2–20 Ω).

**Velocity factor and loss of a cable** (open-ended cable of length L on CH0): the first frequency where the input looks like a short (S11 phase = −180°) is the quarter-wave resonance, so v_f = 4 L f_λ/4 / c. Or use the group delay of S11, τ_rt = 2L/(v_f c). Loss: the open reflects everything, so the one-way cable loss is RL/2. Script §3: a 2.000 m cable shows its −180° point at 26.03 MHz → v_f = 0.6946 (true 0.695); open-end RL 0.835 dB at 100 MHz → 0.417 dB one-way (exact).

**Time-domain transform** (TDR from frequency data, AN 1287-12 [12]): the transform aliases every 1/Δf, so the alias-free one-way length for reflection is
$$L_{\max}=\frac{v_f\,c}{2\,\Delta f},\qquad \Delta f=\frac{\text{span}}{N-1}.$$
Resolution for equal-size responses: low-pass step rise (10–90 %) ≈ 0.45/0.99/1.48 ÷ span and low-pass impulse width ≈ 0.60/0.98/1.39 ÷ span for minimum/normal/maximum window (Kaiser β ≈ 0, 6, 13 on LiteVNA [5]); bandpass mode is twice as coarse (1.20/1.95/2.77 ÷ span) [12]. One-way resolvable separation = v_f c t/2. Low-pass mode needs a harmonic grid (f_start = f_stop/N) because it extrapolates DC.

**L-match to a measured antenna impedance** R_A + jX_A (R_A < 50 Ω) with the shunt element on the 50 Ω side: Q = √(50/R_A − 1), series reactance X_1 = Q R_A − X_A, shunt susceptance B_2 = Q/50. Design theory in [impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md).

### Level 3 — why accuracy degrades with frequency on NanoVNA-H/H4
The Si5351 clock generator produces square waves up to ~300 MHz. Above that, the firmware tunes the fundamental to f/3 (later f/5) and relies on the square wave's odd harmonics, which are ≈ 9.5 dB (1/3) and 14 dB (1/5) below the fundamental in an ideal square wave; with the drive boosted from 2 mA to 8 mA above 300 MHz (community reports) the net measured drop is ~10–13 dB [8]. Both the stimulus and the LO are harmonics, so the IF signal falls by the product while the noise floor stays put — hence 70 → 60 → 40 dB dynamic range through the three bands [4]. Two side effects follow from the physics (our reasoning, not a vendor statement): (1) the DUT is driven by a *multi-tone* signal whose strongest component is at f/3 — harmless for passive linear DUTs, but it can compress or even be amplified by an active DUT; (2) a DUT with a deep null exactly at the measured frequency can let fundamental-related spurious responses show through. The NanoVNA V2 family and LiteVNA use a real synthesiser (no harmonic mode) [6], [5]; LibreVNA uses a MAX2871 above 25 MHz with harmonic mixing only above 6 GHz [7].

## Design equations & rules of thumb

| Task | Formula / rule | Notes |
|---|---|---|
| VSWR ↔ RL | RL 10 dB = VSWR 1.92; 14 dB = 1.50; 20 dB = 1.22 | |
| Cable v_f from open stub | v_f = 4 L f_(−180°) / c | or 2L/(c τ_rt) from group delay |
| Cable one-way loss | = RL_open-end / 2 | at each frequency |
| TDR range | L_max = v_f c / (2Δf) | more points or narrower span → longer |
| TDR resolution | ≈ v_f c (0.98/span)/2 (normal window) | wider span → finer |
| Series-through Z | Z = 2Z0 (1/S21 − 1) | 1 kΩ–100 kΩ |
| Shunt-through Z | Z = Z0 S21 / (2(1 − S21)) | < 2 Ω |
| Reflection Z | Z = Z0 (1+Γ)/(1−Γ) | 5 Ω–1 kΩ |
| Stimulus level | NanoVNA-H: −12 to −15 dBm below 300 MHz [9] | LibreVNA −40…0 dBm [7] |
| Max safe input | treat CH0/CH1 as ≤ 0 dBm receivers | pad or couple anything stronger |
| Cal validity | recal after warm-up, temperature change, cable move | V2 Plus4 claims months [6] |

## Model and software overview

| Model | Range (usable) | Source / architecture | Calibrated dynamic range | Notes |
|---|---|---|---|---|
| NanoVNA (edy555 V1, 2019) | 50 kHz–300 MHz (900 MHz harmonic) | Si5351 + SA612 mixers + audio codec ADC | ~40 dB at 900 MHz [3] | original; many clones |
| NanoVNA-H rev3.x / **H4** rev4.x (hugen) | 50 kHz–1.5 GHz (fw to 2.7 GHz, "substantial noise" > 1.5 GHz [3]) | same, improved PCB/shield; H4: 4″ screen, STM32F303 | > 70 / 60 / 40 dB (≤ 300 M / ≤ 900 M / ≤ 1.5 G) [4] | H v3.7 and H4 v4.4 replace the discontinued SA612 with a Zeenko NE602A [3]; "2.7 GHz NanoVNA plus" sellers are usually fakes [3] |
| NanoVNA V2_2 / V2 Plus (S-A-A-2) | 50 kHz–3 GHz | synthesiser, no harmonics | 60 dB [6] | discontinued |
| **NanoVNA V2 Plus4 / Plus4 Pro** | 50 kHz–4.4 GHz | "VNA-R" drift-cancelled | 90 dB (AVG 20, 1 GHz), 80 dB at 3 GHz; S11 floor −50 dB < 1.5 GHz [6] | NanoVNA-QT software |
| **LiteVNA 62/64** (Zeenko) | 50 kHz–6.3 GHz | single mixer + RF switches | > 70 dB < 3 GHz, > 50 dB ≥ 3 GHz; S11 floor −50/−40 dB [5] | 10–1001 points on device, > 550 pts/s [5] |
| **LibreVNA** (jankae) | 100 kHz–6 GHz (8 GHz harmonic) | MAX2871 + Si5351, resistive bridges, 2 independent receivers | S21 85–105 dB (5–2940 MHz), 50–60 dB > 2.94 GHz, 10 Hz IFBW [7] | PC-only (USB); also SA (−103 dBc/Hz @ 1 GHz/10 kHz) and generator (−40…0 dBm) [7] |

Software: **DiSlord NanoVNA-D** firmware for H/H4 (F072 = H, F303 = H4 builds; flashed by DFU) [13]; **NanoVNA-Saver** (Python/PySide6; supports NanoVNA/H/H4/F, LiteVNA, tinySA; segmented sweeps "tried up to > 10 k points", averaging, calibration with non-ideal standards but no load capacitance, TDR, filter analysis, Touchstone export) [10]; **NanoVNA-App** (OneOfEleven, Windows) [13]; **NanoVNA-QT** (V2); **LibreVNA-GUI** (Windows/Ubuntu/macOS; SCPI scripting) [7]. Save every sweep as Touchstone (.s1p/.s2p) and analyse in scikit-rf.

## Step-by-step recipes

### Recipe A — antenna S11 in situ (rocket nose cone or av-bay)
1. **Warm up** 10–20 min. Set span ±20–30 % around the band (e.g. 350–520 MHz for 433 MHz; 800–1030 MHz for 915 MHz), 201–401 points, IFBW ≤ 1 kHz (or averaging 4–8).
2. **Calibrate at the plane you will connect to** — the end of the test cable, not the NanoVNA's front panel. If the antenna has a U.FL, either calibrate at the end of the U.FL pigtail (U.FL SOL kit, e.g. MegiQ [14]) or calibrate at the SMA end and apply **port extension** (delay; plus loss if you care about impedance) measured by attaching an open/short at the U.FL end ([VNA page §Level 3](vna-fundamentals-calibration.md)). Check the cal: load ≥ 35–40 dB RL.
3. **Choke the cable**: 3–5 clip-on ferrites (e.g. Fair-Rite #43 below 300 MHz, #61 or #31/#43 combinations at 433–915 MHz — check the bead's impedance curve) within a few cm of the antenna feed, or a λ/4 sleeve balun. Route the cable away from the antenna, perpendicular to dipole arms, out through the same path as the flight harness if possible.
4. **Install everything** that will fly: nose cone/airframe (fibreglass shifts resonance down; carbon fibre kills it), battery, flight computer, other harnesses. Tape the cable where it will sit.
5. **Measure**; save .s1p. Record resonance (minimum |S11| and where X = 0), −10 dB bandwidth, and Z at 433.175/868/915 MHz.
6. **Touch test**: grab the cable 30–50 cm from the antenna, then the NanoVNA body. If S11 or resonance moves noticeably, common-mode current is flowing on the cable shield — add more choking. Hands within ~λ/10 of the antenna itself will always detune it (body loading), which is real, not an error [15].
7. **Interpretation**: S11 < −10 dB means ≥ 90 % of power is *accepted*, not radiated. A lossy match looks great on S11 ([antenna measurement](../08-antennas/antenna-measurement.md)).

### Recipe B — tuning a pi-match footprint (shunt–series–shunt) on the board
1. Populate the series position with a 0 Ω link and leave both shunts empty. Measure the antenna at the pi input (port extension to the pad).
2. Plot on the Smith chart; decide an L-match (use one shunt + the series part) with the formulas above or a Smith-chart tool; the pi's extra shunt lets you lower Q or choose either L orientation.
3. Worked first guess (script §4): measured 18 − j32 Ω at 915 MHz (a chip antenna on a small ground, modelled as series RLC with Q ≈ 8) → Q = 1.33, series L = 9.74 nH, shunt C (port side) = 4.64 pF. Nearest parts 10 nH + 4.7 pF → |S11| = −26.9 dB; with ±2 % L and ±0.1 pF C the worst case is −21.5 dB; adding 0.15 pF of pad capacitance at both nodes moves the best match to 909 MHz (−23 dB at 915 MHz). The −10 dB band is only 886–943 MHz — typical for a small antenna.
4. Solder, re-measure, **change one part at a time** and log every step (value, S11 at centre, band edges). Use high-Q 0402 wire-wound or multilayer RF inductors and C0G capacitors.
5. Re-check in the final enclosure — the enclosure usually moves resonance more than the component tolerance.

### Recipe C — filter S21 (e.g. 915 MHz SAW, 433 MHz LC, GNSS SAW)
1. Full cal: SOL on CH0, isolation (loads on both ports; skip if not measuring > 60 dB), thru. Include any pads in the cal.
2. Put a 6–10 dB attenuator on CH1 to improve its (uncorrected) match — the 1.5-port error on S21 falls from ±0.5 dB to < ±0.1 dB for a filter with 10 dB output RL (VNA page Example 5).
3. Narrow IFBW / average for the stopband. Check dynamic range first: replace the DUT by two loads and look at the S21 floor. On an H4 at 1.5 GHz you only have ~40 dB — not enough to verify a GNSS SAW's 50 dB rejection; use LiteVNA/V2/LibreVNA.
4. SAW filters are often not 50 Ω at the unused ports — use the vendor's matching network on the test board.
5. For S22/S12, reverse the DUT and repeat. Export .s2p (two sweeps merged) for simulation.

### Recipe D — cable loss, velocity factor and connector check
1. Calibrate at the NanoVNA port (SOL). Connect the cable, far end open.
2. v_f: read the frequency where S11 phase first reaches −180° (or read group delay) → v_f = 4 L f / c. Script §3 recovers 0.6946 for a 2 m cable of true v_f 0.695.
3. Loss: |S11| of the open-ended cable in dB, divided by 2, at each frequency (or do a 2-port S21 with a thru cal: more accurate for low-loss cables).
4. Connector/cable integrity: TDR (Recipe E) and a "wiggle test" (watch S11 phase while flexing).

### Recipe E — TDR fault finding (NanoVNA TRANSFORM, NanoVNA-Saver TDR, LiteVNA)
1. Use low-pass mode with a harmonic grid starting at the lowest frequency; step response for impedance vs distance, impulse for locating discontinuities.
2. Choose span and points for the job (script §1): NanoVNA-H 101 pts to 900 MHz → Δf = 9 MHz, range 11.0 m, resolution ~0.11 m (v_f 0.66); H4 401 pts to 1.5 GHz → 26 m, 65 mm; LiteVNA 1001 pts to 6.3 GHz → 16 m, 15 mm; LibreVNA 4501 pts to 6 GHz → 74 m, 16 mm.
3. Set the velocity factor (from Recipe D or the datasheet). A synthetic check (script §1): 1 m of 50 Ω + 0.3 m of 75 Ω + 0.5 m of 50 Ω into an open reads 50.0 Ω, 75.0 Ω, 50.8 Ω along the line.
4. Capacitive discontinuities dip, inductive ones bump (step mode). A connector crimped badly shows as an inductive bump.

### Recipe F — SMD component on a fixture
1. Build a small fixture: SMA edge connectors, short 50 Ω CPWG, pads for 0402/0603, with a matching "thru", "short" and "open" footprint for calibration or de-embedding ([fixtures](fixtures-and-deembedding.md)).
2. Pick the method by expected impedance (TL;DR): 12 nH at 915 MHz (69 Ω) → reflection; a 1 kΩ-at-900-MHz ferrite bead → series-through; a 100 nF decoupling capacitor (ESR ~ 20 mΩ, ESL ~ 0.5 nH) → shunt-through.
3. Sweep beyond the self-resonant frequency to see the parasitics; fit an R-L-C model; compare with the vendor's .s2p ([component models](../04-real-components-hf/component-models-s2p-spice.md)).

### Recipe G — measuring an LNA or gain block
- NanoVNA output (−13 dBm) into a 20 dB LNA gives +7 dBm into CH1 and may compress the LNA; add a 20 dB input pad (LNA sees −33 dBm, CH1 −13 dBm) or reduce the power setting (script §5). Bias the LNA from a current-limited supply through its bias-T, never through the VNA port. Stability: check S11/S22 < 0 dB everywhere and look for oscillation on a spectrum analyzer ([amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md)).

## Calibration practice — DIY kits, LibreCAL, adapters, reference and the 73 Ω myth
The theory is in [VNA calibration, Level 3b](vna-fundamentals-calibration.md#level-3b--calibration-practice-diy-standards-electronic-cal-adapters-reference-renormalisation); this is the bench procedure.

### Recipe H — build and characterise a DIY SOL kit
1. **Build**: open = an SMA jack/plug with nothing fitted (keep the dielectric flush); short = a brass/copper disc soldered across the whole face; load = two 0402 1 % 100 Ω resistors in parallel, pin to flange, as short as possible (each 0.1 nH of mounting inductance costs directivity: 0.3 nH → 35 dB, 0.5 nH → 31 dB, 1 nH → 25 dB at 915 MHz; `s10_cal_practice.py` §A).
2. **Characterise** against a trusted kit (a commercial kit with published definitions, a borrowed one, or a LibreCAL): calibrate with it, then measure the three DIY standards and save .s1p files.
3. **Fit**: offset delay from the short's phase slope; open C0 (+ C1) after removing that delay; keep the load as data. NanoVNA-Saver accepts non-ideal standard definitions (but no load capacitance; check its calibration dialog for the exact fields) [10]; the LibreVNA-GUI and scikit-rf accept data-based standards.
4. **Verify** with an item not used in the calibration (a 20 dB attenuator + load, or a 25 Ω/100 Ω mismatch measured on the trusted kit).
Expected payoff (simulated): at 915 MHz the DUT error falls from |ΔΓ| ≈ 0.06 (ideal definitions) to 0.03 (O/S fitted) to the repeatability floor (load as data too); at 433 MHz an uncharacterised kit already gives < 0.03 (§B).

### Electronic calibration with LibreCAL
LibreCAL (9 kHz–6 GHz, 4 SMA ports, each switchable to open/short/50 Ω, factory-measured coefficients stored on the device, temperature-stabilised) is driven directly by the LibreVNA-GUI and over SCPI [17]. It speeds up multi-port and repeated calibrations and removes torque/handling errors, but it is only as good as its coefficients — keep them (they can be re-downloaded by serial number) and treat a unit without official coefficients as uncalibrated [17]. For NanoVNAs without eCal support it can still serve as the *trusted kit* in Recipe H.

### Calibrating through UHF, BNC, MMCX and U.FL adapters
- Best: calibrate *at the far end of the adapter chain* with standards in that connector (U.FL kits exist [14]; for UHF/BNC, a homemade open/short/load on the connector).
- Next: calibrate at SMA and de-embed the characterised adapter (its .s2p from a two-port measurement, or from cals at both faces), or use port extension only when the adapter is close to 50 Ω.
- Know the cost if you do neither: an adapter's own return loss becomes your directivity. A UHF adapter modelled as 25 mm of 35 Ω gives 42 dB at 30 MHz but only 19 dB at 433 MHz and 13 dB at 915 MHz (§D). Avoid UHF connectors above ~150 MHz on anything you want to measure accurately.
- MMCX/U.FL: mate straight, count mating cycles, re-check the cal after every re-mate.

### Frequency reference
NanoVNA-class instruments run from an internal crystal; LibreVNA has a 10 MHz reference input/output [7]. 20 ppm is 8.7 kHz at 434 MHz — irrelevant for antennas (−10 dB bandwidths of MHz) but 20 % of the bandwidth of a Q-10 000 resonator. For crystal, SAW or cavity work, lock to a GPSDO or calibrate the frequency axis against a counter ([basic bench instruments](basic-bench-instruments.md)).

### "Calibrate for 73 Ω" (or 75 Ω) — renormalise instead
Using a 73 Ω resistor as the "load" in a 50 Ω calibration produces the same Γ as mathematically renormalising to 73 Ω — *if* the resistor were a perfect 73 Ω at the reference plane (§C). It is not: its parasitics add an error comparable to a mediocre load (≈ 0.01 in Γ at 915 MHz for 0.8 nH/0.1 pF), the impedance and Smith-chart readouts still assume 50 Ω (a 70 + j5 Ω dipole then reads 47.9 + j3.4 Ω), and the antenna's match to the real 50 Ω cable is unchanged (73 Ω on 50 Ω is VSWR 1.46 whatever the display says). Do a normal 50 Ω cal, save Touchstone, and renormalise in software (scikit-rf `ntw.renormalize(73)`); for a real 75 Ω system (TV/F-connector coax) use 75 Ω standards and connectors.

## Worked examples
**Example 1 — 433 MHz monopole in a fibreglass nose cone.** Bench (no cone): resonance 441 MHz, RL 18 dB. In the cone with battery and harness: resonance 424 MHz, RL 13 dB at 433 MHz (fibreglass ε_r ≈ 4–5 loads the antenna). Touch test on the cable shifts resonance ±3 MHz → add two more ferrites until the shift is < 0.5 MHz. Trim or re-match *in the cone*. (Illustrative numbers; the physics is in [antennas on rockets](../08-antennas/antennas-on-rockets.md).)

**Example 2 — "SWR 1.3 at the radio" through 10 m of RG-58.** RL at the radio end 17.7 dB. Cable loss at 433 MHz ≈ 2.9 dB one-way (Recipe D) → the antenna itself has RL ≈ 17.7 − 5.8 = 11.9 dB (VSWR 1.7): the cable is hiding the mismatch ([reflections page, Example 2](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)). Measure at the antenna end.

**Example 3 — ferrite bead check.** Series-through on a 0603 bead: |S21| = −20.0 dB at 100 MHz, phase ≈ −8° → Z = 2·50(1/S21 − 1) ≈ 890 + j139 Ω — mostly resistive, as a good lossy bead should be. Using reflection instead would give ~±25 % error at this impedance (script §2).

**Example 4 — cable fault.** A ground-station feeder shows an S11 ripple; TDR on an H4 (401 points to 1.5 GHz, v_f 0.85 for LMR-400-like foam) shows a 60 Ω inductive bump at 7.3 m — a crushed section under a door hinge.

## Practical notes
- **Connectors**: the NanoVNA's SMA jacks wear out; fit a "connector saver" (SMA M-F adaptor) and replace that instead. Torque to 0.9 N·m.
- **Cables**: use short, good cables (RG-316 or semi-flexible 0.141″); cheap RG-174 jumpers change phase when flexed. Tape them down after cal.
- **Memory slots and interpolation**: calibrate for the span you use; wide→narrow interpolation of a stored cal is OK for short cables, poor for long ones.
- **Power**: DiSlord firmware exposes the Si5351 drive level; community reports suggest the 8 mA setting can cause non-linearity in harmonic mode, so leave it on automatic [8] (forum — anecdotal).
- **USB/laptop**: a laptop on its charger connects the NanoVNA ground to the mains; for antenna work run on battery and disconnect USB, or use a choke on the USB cable (the user and laptop become part of the antenna otherwise) [15].
- **Fakes**: buy from the vendor lists on nanovna.com / nanorfe.com / zeenko.tech; "3 GHz NanoVNA-H" and "2.7 GHz NanoVNA plus" listings are usually fakes [3].
- **Beyond 1.5 GHz**: GNSS antennas, 2.4 GHz and 5.8 GHz video need LiteVNA, NanoVNA V2 Plus4 or LibreVNA; at 5.8 GHz a 1 mm error in reference plane is ~14° of round-trip phase in air — calibrate at the connector.

## Common mistakes & misconceptions
- **Calibrating at the front panel, then measuring through a 1 m cable.** The cable's delay rotates the Smith chart and its loss improves the apparent RL.
- **Calibration at the SMA, measurement through an SMA–U.FL adaptor.** Adds uncorrected mismatch (VSWR 1.2 adaptor → only ~21 dB effective directivity).
- **"The antenna reads 1.1:1 so it's efficient."** A 50 Ω resistor reads 1.0:1. Use range/OTA tests for radiation.
- **Common-mode current on the cable** makes the cable part of the antenna; readings then depend on cable routing and on touching it [15].
- **Hand effects**: body within ~λ/10 detunes small antennas — measure hands-off.
- **Overdriving**: pointing a 1 W LoRa module into CH1 destroys the receiver; even a 20 dB LNA can compress the NanoVNA's CH1.
- **Calibrating with a 73 Ω resistor** to make a dipole read 1:1 — see the calibration-practice section; renormalise instead.
- **Leaving a UHF adapter outside the calibration** at 433 MHz — only ≈ 19 dB effective directivity.
- **Trusting 2.7 GHz** readings on an H4: dynamic range and trace noise are poor above 1.5 GHz [3].
- **Measuring a filter stopband deeper than the instrument's dynamic range** and reporting the noise floor as "rejection".
- **Reading marker values between sweep points** on a narrowband device (crystal, high-Q resonator) with 101 points: use segmented sweeps (Saver) or narrower spans. Note NanoRFE states only the V2 Plus4 Pro can measure crystals (its IF bandwidth is adjustable) [6].

## How to simulate / verify
- `python3 tools/verify/meas_nanovna.py` — (1) TDR range/resolution for four instruments and a synthetic low-pass TDR of a 75 Ω section; (2) accuracy map of reflection vs series-through vs shunt-through methods; (3) v_f and loss from open-stub S11 (phase and group delay methods); (4) L-match of a chip antenna, standard values, tolerance and pad parasitics; (5) LNA headroom at −13 dBm stimulus.
- `python3 tools/verify/s10_cal_practice.py` — DIY-kit directivity and characterisation, 73 Ω cal vs renormalisation, UHF adapter, frequency-reference effects (ALL PASS).
- Load your .s1p/.s2p into scikit-rf: `rf.Network('ant.s1p').plot_s_smith()`, time-domain with `ntw.s11.extrapolate_to_dc().time_step()` (low-pass step) to cross-check the instrument's TDR.
- Verification artefacts to keep in the kit: a 20 dB SMA attenuator (S21 = −20.0 dB, flat), a 50 Ω load you did *not* use for calibration, a 1 m cable of known length.

## Open questions / gaps
- CH1 input match and absolute maximum input level of NanoVNA-H/H4 are not in the official docs; values quoted in forums vary.
- Point limits per firmware (DiSlord: 101 on H, 401 on H4 is commonly stated) should be checked against the current release notes.
- The nose-cone numbers in Example 1 are illustrative, not measured; a team measurement should replace them.
- Street prices move quickly (R&L listings used here were for USD retail in 2026).

## Sources
1. D. Rytting, "Network Analyzer Error Models and Calibration Methods" (seminar slides) — 1.5-port / 12-term background. (app note; read)
2. Agilent AN 1287-3, "Applying Error Correction to Network Analyzer Measurements," 2002 — enhanced-response calibration and adapter effects. (app note; read)
3. nanovna.com (Hugen), NanoVNA overview page — edy555 original 50 kHz–300 MHz, harmonic extension to 900 MHz, 40 dB at 900 MHz, H rev3.4+ 40 dB to 1.5 GHz, 2.7 GHz firmware noise warning, fake "2.7 GHz" units, NE602A substitution. Accessed 2026-09-27. (community/vendor; read)
4. hugen79/NanoVNA-H README (> 70 dB 50 kHz–300 MHz) and retailer spec tables for NanoVNA-H4 (> 70/60/40 dB, port SWR < 1.1). (vendor; read)
5. Zeenko, LiteVNA product page and *LiteVNA User Guide* (PDF, randl.com mirror) — ranges, dynamic range, S11 floor, points, sweep rate, TDR windows (normal = Kaiser β 6, maximum = β 13). (vendor manual; read)
6. NanoRFE, "NanoVNA V2" page, nanorfe.com/nanovna-v2.html — V2_2/Plus/Plus4/Pro specifications, no harmonics, drift claim, crystal measurement note. (vendor; read)
7. J. Käsemann, LibreVNA README and Preliminary Specifications (github.com/jankae/LibreVNA). (open-source vendor; read)
8. hugen79/NanoVNA-H issue #18 "SI5351 8mA out causes non-linearity in harmonics mode" and nanovna-users@groups.io threads on output level (via search snippets). (forum — anecdotal)
9. "nVhelp — nanoVNA user documentation," oristopo.github.io/nVhelp — measured output level −12.1 to −14.9 dBm at 10–200 MHz; boosted 3rd-harmonic operation above 300 MHz. (community docs; WebFetch summary, numbers quoted)
10. NanoVNA-Saver README, github.com/NanoVNA-Saver/nanovna-saver — features and calibration notes. (open-source docs; read)
11. R&L Electronics listings: NanoVNA-H4 US$109.95, LiteVNA64 US$189.95 (search listing, 2026). (retailer)
12. Agilent AN 1287-12, "Time Domain Analysis Using a Network Analyzer," 5989-5723EN — resolution Table 1-3, alias-free range. (app note; read)
13. DiSlord, NanoVNA-D firmware README, github.com/DiSlord/NanoVNA-D — H/H4 builds, DFU, companion tools. (open-source docs; read)
14. MegiQ, Balanced and UFL Calibration Kit user guide. (vendor; cited from listing)
15. nanovna-users@groups.io threads "Question about measuring an antenna with the nanovna-h," "Measuring a common mode coaxial choke" (search snippets) — user/NanoVNA become part of the antenna; chokes required. (forum — anecdotal)
16. This repository: `tools/verify/meas_nanovna.py`, `tools/verify/meas_vna_cal.py`, `tools/verify/s10_cal_practice.py`. (verification)
17. J. Käsemann, LibreCAL README, github.com/jankae/LibreCAL, accessed 2026-10-12 — 9 kHz–6 GHz 4-port eCal, factory coefficients, heater, GUI/SCPI. (open-source vendor docs; WebFetch summary)
