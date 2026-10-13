---
title: Recipe — GNSS L1 low-noise amplifier for a rocket active antenna (BGA524N6 MMIC vs ATF-54143 pHEMT): stability, noise match, bias, layout and measurement
domain: 20-projects-recipes
slug: lna-design-walkthrough
tags: [recipe, lna, gnss, l1, bga524n6, atf-54143, phemt, mmic, stability, k-factor, mu-factor, noise-match, gamma-opt, bias-tee, saw, limiter, blocking, y-factor, noise-figure-measurement, active-antenna, zed-f9p, max-m10s, pre-registration]
prerequisites:
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../07-noise-linearity/receiver-cascade-analysis.md
related:
  - ../18-components-parts/lna-pa-gain-block-mmics.md
  - ../18-components-parts/filter-parts-saw-ceramic-ltcc.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../08-antennas/gnss-antennas.md
  - ../17-test-measurement/noise-figure-measurement.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
  - patch-antenna-design-walkthrough.md
  - gnss-front-end-design.md
  - ground-station-tracking-yagi.md
level: intermediate
confidence: medium
last_updated: 2026-10-12
---

# Recipe — GNSS L1 LNA for a rocket active antenna

The amplifier that turns the [FR-4 patch](patch-antenna-design-walkthrough.md) (or any passive L1 patch)
into an *active* antenna for a u-blox receiver on the rocket, designed with two candidate devices. The
system-level questions (which receiver, total gain, coexistence with the LoRa transmitters) are in
[GNSS front-end design](gnss-front-end-design.md); this page is about the amplifier itself. Numbers:
`python3 tools/verify/proj_lna_gnss.py` (≈ 1 s); the discrete design itself is the KB's verified
ATF-54143 L1 design (`tools/verify/rfckt_lna.py`, ≈ 4 min, documented in [LNA design, example 3](../06-rf-circuits/lna-design.md)).

## Questions this page answers
- Should my GNSS LNA be a tiny MMIC (BGA524N6) or a discrete pHEMT (ATF-54143)?
- Why is a bare pHEMT potentially unstable, and how does a real design become unconditionally stable?
- Where does the noise match sit compared with the conjugate match?
- Should the SAW filter go before or after the first LNA on a rocket that carries a 2 W LoRa transmitter?
- How much does a SAW in front cost in C/N0?
- Which datasheet linearity number do I believe when the datasheet disagrees with itself?
- How do I bias it through the coax, and how much power does it take?
- How do I measure gain and a 0.5 dB noise figure with hobby equipment?
- What layout mistakes make an LNA oscillate?

## TL;DR
- **Two devices.** BGA524N6: NF 0.55 dB, 19.6 dB, 2.5 mA, internally matched (one 8.2 nH input inductor), but **in-band IP1dB −16 dBm, IIP3 −9 dBm (data-sheet table), RF input absolute maximum 0 dBm**. ATF-54143 (KB-verified design): **NF 0.74 dB, 19.2 dB, unconditionally stable 0.1–10 GHz with real parts**, OIP3 ≈ +36 dBm class, survives ≈ +20 dBm, but **60 mA × 5 V = 300 mW** and ten parts.
- **Bare ATF-54143 is potentially unstable below ≈ 3.5 GHz** (K 0.07 at 100 MHz, 0.72 at L1; MSG 34 dB at 100 MHz): stability comes from the bias network's resistive terminations, a drain series resistor and (at 433 MHz) R–C feedback, checked from 0.1 to 10 GHz — not from the in-band match.
- **Noise match ≠ conjugate match**: at L1 Γ_opt = 0.29∠99° while S11* = 0.64∠153°; NFmin 0.35 dB, Rn 2 Ω (very forgiving). The realised design trades 0.4 dB of the device's NFmin for stability and real-part losses.
- **Cascades** (to the receiver through 1 m RG-174): patch → BGA → SAW → BGA: **NF 0.58 dB, 36.5 dB**; patch → ATF → SAW → BGA: 0.77 dB, 36.1 dB; **SAW first** (SAW → BGA → SAW → BGA): 2.18 dB, 34.9 dB. All within the ZED-F9P's 17–50 dB / NF < 4 dB active-antenna window.
- **C/N0 price of the SAW first**: with the patch looking at cold sky (100 K), **SAW-first costs 3.1 dB of C/N0** (45.3 vs 48.4 dB-Hz at the minimum GPS signal with the FR-4 patch); at 290 K it costs 1.6 dB.
- **But the rocket's own transmitters decide it**: with −20 dB antenna-to-antenna coupling the E22 (33 dBm, 433 MHz) puts ≈ +3 dBm and the E220 (30 dBm, 905 MHz at IREC; in Singapore 866–869 MHz at ≤ 24 dBm) ≈ +4 dBm on a BGA524N6 input after the patch's own mismatch — **above its 0 dBm absolute maximum**. SAW-first reduces that to ≈ −31 dBm. With ≥ 40 dB isolation (antennas at opposite ends of a long vehicle) LNA-first is safe. The ATF-first chain tolerates −30 dB coupling (≈ 9 dB below its compression).
- **Measurement**: NanoVNA S21 needs ≥ 20 dB of pad on its output (the BGA compresses at −16 dBm). Y-factor with a 15 dB-ENR source and an RTL-SDR as second stage (NF ≈ 7 dB assumed) reads within 0.2 dB of the true NF before correction (but a V3 measured 11.9 dB at 1280 MHz — [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md) — and no L1 figure was found; at 12 dB the uncorrected reading is ≈ 0.6 dB high, so measure the SDR's NF first); with a tinySA (NF ≈ 25 dB) the uncorrected reading is 6.6 dB — always second-stage-correct.

## Intuition (no math)
An LNA must do three things at once: add as little noise as possible, give enough gain that the cable and receiver behind it don't matter, and stay calm — not oscillate and not choke when a strong signal arrives. A pHEMT transistor has huge gain at low frequencies, where you are not looking; give it the wrong impedances there and it becomes an oscillator. So the design is mostly about what the transistor sees *outside* the band (resistors in the bias network, a little feedback), and only then about the best noise impedance at 1575 MHz. An MMIC has all of that done inside the package by the manufacturer, at the price of a fragile input and little linearity. On a rocket the deciding fact is that a 2 W transmitter sits a metre away.

## Requirements
| ID | Requirement | Value |
|---|---|---|
| L1 | Band | 1559–1610 MHz (GPS L1, Galileo E1, BeiDou B1, GLONASS L1) |
| L2 | Chain NF (antenna terminals) | ≤ 1.0 dB without front SAW; ≤ 2.5 dB with front SAW |
| L3 | Gain to the receiver | 30–40 dB including 1 m cable (ZED-F9P ideal window; ≤ 20 dB for MAX-M10S with its LNA in bypass/low-gain) |
| L4 | Stability | unconditional (μ > 1) 10 MHz–10 GHz with the real layout, any passive source/load |
| L5 | Survivability | no damage with the flight transmitters on (E22 33 dBm, E220 30 dBm), worst-case 20 dB antenna coupling |
| L6 | Supply | through the coax (bias-tee), 3.0–3.3 V, ≤ 20 mA preferred |
| L7 | ESD | protected input (exposed antenna) |

## Architecture options and trade study
| Option | NF | Gain | Linearity / survival | Parts / power | Verdict |
|---|---|---|---|---|---|
| BGA524N6 single stage | 0.55 dB | 19.6 dB | IP1dB −16 dBm, abs max 0 dBm | 3 parts, 7 mW | MAX-M10S booster; fragile |
| BGA524N6 + SAW + BGA524N6 | 0.58 dB | 36.5 dB | first stage exposed | 6 parts, 14 mW | best NF; only with ≥ 40 dB TX isolation |
| SAW + BGA + SAW + BGA | 2.18 dB | 34.9 dB | front SAW protects | 7 parts, 14 mW | **robust choice on a crowded rocket** |
| ATF-54143 + SAW + BGA524N6 | 0.77 dB | 36.1 dB | ATF survives ≈ +20 dBm; ≈ 9 dB from compression at −30 dB coupling | ≈ 14 parts, ≈ 300 mW | best NF with robustness; power-hungry |
| limiter + ATF + SAW + BGA | 1.07 dB | 35.8 dB | clamps ≈ +10 dBm out at +20 dBm in | +1 part | belt and braces |
| Buy an active antenna | ≈ 1–3 dB | 26–30 dB | vendor spec | US$5–40 | flight default ([GNSS antennas](../08-antennas/gnss-antennas.md)) |
| Dual-band (L1+L2) for ZED-F9P | — | — | needs an L2 path too | — | use a multiband active antenna; not this recipe |

## The math — design calculations

### Level 1 — what each number means
- Friis: $F = F_1 + (F_2-1)/G_1 + \dots$; a passive loss L before the LNA adds L dB to NF ([Friis](../07-noise-linearity/noise-figure-and-friis.md)).
- Input-referred intercepts: $1/IIP3 = 1/IIP3_1 + G_1/IIP3_2 + \dots$ (mW, linear) ([cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md)); the cascade's *in-band* IIP3/IP1dB is set by the last stage once the gain in front is large (here ≈ −26 / −34 dBm for every two-stage chain).
- C/N0 at the antenna terminals: $C/N_0 = C - 10\log_{10}(k(T_{ant}+T_e))$ with C = −128.5 dBm + antenna gain (minimum GPS L1 C/A for a 0 dBic RHCP antenna, [GNSS antennas](../08-antennas/gnss-antennas.md)).

### Level 2 — stability and noise of the discrete device
ATF-54143 at 3 V / 60 mA, data-sheet S-parameters (`rfckt_atf54143_data.py`):

| f | K | μ | MSG/MAG | $|S_{21}|^2$ |
|---|---|---|---|---|
| 0.1 GHz | 0.07 | 0.04 | 34.4 dB (MSG) | 28.8 dB |
| 0.5 GHz | 0.29 | 0.29 | 28.2 dB | 26.0 dB |
| 1.0 GHz | 0.51 | 0.42 | 24.1 dB | 22.2 dB |
| **1.575 GHz** | **0.72** | **0.68** | 22.4 dB | 19.1 dB |
| 2.0 GHz | 0.81 | 0.77 | 20.9 dB | 17.3 dB |
| 4.0 GHz | 1.06 | 1.10 | 14.9 dB (MAG) | 11.8 dB |
| 8.0 GHz | 1.14 | 1.32 | 9.0 dB | 5.6 dB |

So the bare device can oscillate for some passive terminations everywhere below ≈ 3.5 GHz, most easily at low frequency where it has 30+ dB of gain. Noise at L1: NFmin 0.35 dB, Γ_opt 0.29∠99°, Rn 2 Ω; S11* = 0.64∠153° — the noise and conjugate matches are far apart, so a noise-matched input has only ≈ 9 dB return loss (normal for LNAs; [LNA design](../06-rf-circuits/lna-design.md)).

**The realised design** (KB-verified; "high-pass" topology from the data-sheet application circuit): C1 82 pF series DC block → L1 2.7 nH shunt gate inductor (gate bias via its cold end, bypassed by C2 82 pF with R4 470 Ω as low-frequency termination) → device → Rd 4.7 Ω drain series stabiliser → L4 4.7 nH shunt drain feed with *partial* bypass C5 2.7 pF so that R3 27 Ω loads the drain at RF → C4 56 pF output. Real 0603/0402 models (Q 40): **NF 0.74 dB, G_T 19.2 dB, S11 −9.4 dB, S22 −15.2 dB, μ ≥ 1.05 from 0.1 to 10 GHz**; Q 25 → 0.83 dB, Q 80 → 0.66 dB; Monte-Carlo ±5 %: NF 0.71 mean (max 0.86), 100 % stable. The stabilising resistors cost ≈ 0.4 dB relative to NFmin — the price of μ > 1.

### Level 2 — cascades and C/N0
Stage data: SAW (Murata SAFFB1G56KB0F0A, 1.6 dB listing); BGA524N6 (19.6 dB, 0.55 dB, IIP3 −9, IP1dB −16 dBm); ATF stage (19.2 dB, 0.74 dB, IIP3 ≈ +17 dBm, IP1dB ≈ +2 dBm); limiter 0.3 dB; 1 m RG-174 1.1 dB.

| Chain | NF | Gain | C/N0, FR-4 patch, T_ant 100 K | 290 K |
|---|---|---|---|---|
| A: SAW → BGA → cable (MAX-M10S booster) | 2.16 dB | 16.9 dB | 45.3 dB-Hz | 43.1 |
| **B: BGA → SAW → BGA → cable** | **0.58 dB** | 36.5 dB | **48.4** | 44.7 |
| **C: SAW → BGA → SAW → BGA → cable** | 2.18 dB | 34.9 dB | 45.3 | 43.1 |
| **D: ATF → SAW → BGA → cable** | 0.77 dB | 36.1 dB | 48.0 | 44.5 |
| E: limiter → ATF → SAW → BGA → cable | 1.07 dB | 35.8 dB | 47.3 | 44.2 |
| F: SAW → ATF → SAW → BGA → cable | 2.37 dB | 34.5 dB | 45.0 | 42.9 |

(FR-4 patch gain −0.2 dBic from the cavity model; the openEMS model gives more — see the patch recipe. With a 3 dBic ceramic patch add 3.2 dB.)

### Level 2 — blockers from the vehicle's own radios
LNA-input power = TX power − antenna coupling − out-of-band mismatch of the GNSS patch (assumed 10 dB at 433 MHz, 6 dB at 868/905 MHz — measure it) [− SAW rejection 35 dB if SAW-first]:

| Coupling | E22 433 MHz, 33 dBm: LNA-first / SAW-first | E220 905 MHz, 30 dBm (IREC/US only) | E220 868 MHz, 24 dBm (Singapore) |
|---|---|---|---|
| −20 dB | **+3.0** / −32.0 dBm | **+4.0** / −31.0 dBm | −2.0 / −37.0 dBm |
| −30 dB | −7.0 / −42.0 dBm | −6.0 / −41.0 dBm | −12.0 / −47.0 dBm |
| −40 dB | −17.0 / −52.0 dBm | −16.0 / −51.0 dBm | −22.0 / −57.0 dBm |

Against BGA524N6 limits (abs max 0 dBm; IP1dB −16 dBm; keep blockers ≥ 10 dB below IP1dB for < ≈ 0.5 dB compression ⇒ ≤ −26 dBm) only the −40 dB row is acceptable for LNA-first, and even that is marginal for the 433/905 MHz radios. The ATF-first chain D sees −7 dBm at −30 dB coupling vs ≈ +2 dBm input P1dB (in-band figure; the L1-tuned stage has less gain at 433 MHz, so this is pessimistic). Out-of-band IIP3 matters for intermodulation of two transmitters (data sheet: −5 dBm for 1712.7/1850 MHz tones). Antenna-to-antenna coupling on a 130 mm airframe is not known to better than ±10 dB without a measurement — measure it (test L-T6) before choosing.

### Level 3 — when the data sheet disagrees with itself
BGA524N6 linearity, three Infineon sources (read from the PDFs): **rev 3.0 electrical table**: IP1dB −16 dBm, IIP3 −9 dBm, out-of-band IIP3 −5 dBm; **rev 3.0 feature list**: IP1dB −12 dBm, out-of-band IIP3 −4 dBm; **AN420 (1.8 V, 0201 parts, input resistor)**: IP1dB −12.3 dBm, IIP3 +3.5 dBm, out-of-band IIP3 −7.8 dBm. Design with the conservative table values and measure IP1dB yourself (test L-T4); it decides LNA-first vs SAW-first. (The KB's parts page quotes "−4 / −12", i.e. feature-list values; noted for correction in the research log.)

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Rollett K and μ | $K=\frac{1-|S_{11}|^2-|S_{22}|^2+|\Delta|^2}{2|S_{12}S_{21}|}$; $\mu=\frac{1-|S_{11}|^2}{|S_{22}-\Delta S_{11}^*|+|S_{12}S_{21}|}$; μ > 1 ⇔ unconditionally stable ([stability](../06-rf-circuits/amplifier-stability-and-biasing.md)) |
| Check stability over | 10 MHz … ≥ 3× f_T-region (here to 10 GHz), with the bias network included |
| Loss before the first LNA | dB-for-dB into NF; with a cold-sky antenna (100 K) each dB costs ≈ 1.5–2 dB of C/N0 |
| Blocker headroom | blocker ≤ IP1dB − 10 dB; never above abs-max |
| Total active-antenna gain | ZED-F9P: 17–50 dB (30–40 ideal); u-blox warns > 35 dB with short cables can overload receivers |
| VNA drive for LNA S21 | ≤ IP1dB − 15 dB (pad the VNA output by ≥ 20 dB for a BGA524N6) |
| Y-factor | $Y = (T_{hot}+T_e)/(T_{cold}+T_e)$; $T_e = (T_{hot} - Y T_{cold})/(Y-1)$; correct for the 2nd stage: $F_1 = F_{meas} - (F_2-1)/G_1$ |

## Worked examples

### 1. The recommended board (chain C, robust): SAW → BGA524N6 → SAW → BGA524N6
1. Input: U.FL/probe from the patch → low-capacitance ESD diode (≈ 0.2 pF; RL impact negligible at L1) → SAW1 (SAFFB1G56KB0F0A) → 8.2 nH input inductor (per data sheet) → BGA524N6 #1 → SAW2 → BGA524N6 #2 → DC block → output to the coax.
2. DC: 3.3 V from the receiver via the coax; bias-tee at the output (high-impedance-at-L-band inductor, the F9P manual recommends ≈ 120 nH; check its SRF is far from L1 or use it *at* resonance as a choke), 100 nF + 10 pF decoupling per LNA, a 10 Ω series resistor to each VCC to decouple the two stages, PON pins tied high.
3. Result: NF 2.18 dB, gain 34.9 dB into 1 m RG-174; blockers at −20 dB coupling reach the first LNA at ≈ −31 dBm (OK); 5 mA total.

### 2. The best-NF board (chain D): ATF-54143 → SAW → BGA524N6
Same output stage; first stage = the verified ATF design above (C1 82 pF, L1 2.7 nH, C2 82 pF, R4 470 Ω, Rd 4.7 Ω, L4 4.7 nH, C5 2.7 pF, R3 27 Ω, C4 56 pF; gate bias from a divider/negative-supply-free self-bias network per the data sheet). NF 0.77 dB, 36.1 dB, ≈ 300 mW at 5 V/60 mA — too much for a 1S avionics battery *and* for a coax-fed antenna at 3.3 V; a lower-current bias (e.g. 3 V/20 mA, ≈ 66 mW) needs S-parameters at that bias (not in the KB table) and a re-run of the stability check.

### 3. 433 MHz equivalent (ground station)
For the LoRa ground station the same reasoning picks TQP3M9036 (NF 0.45 dB, OIP3 +36 dBm) or PGA-103+ — linear enough to sit next to a pad-side 2 W transmitter at ≥ 30 m ([ground-station recipe](ground-station-tracking-yagi.md)); the discrete ATF-54143 433 MHz design (NF 0.38 dB, 22.1 dB) needs R–C feedback (1.5 kΩ + 82 pF) for stability ([LNA design, example 2](../06-rf-circuits/lna-design.md)).

## Part selection
LCSC prices (qty 1–9) from the KB parts pages / JLC DB snapshot (USD).

| Function | Part | Key specs | Price | Notes |
|---|---|---|---|---|
| LNA MMIC | Infineon BGA524N6 (C6752883) | 0.55 dB, 19.6 dB, 2.5 mA, TSNP-6 0.7 × 1.1 mm | ≈ 0.33 | needs X-ray-quality assembly; JLC can place |
| LNA MMIC (hand-solderable) | ZHONGKEWEI AT2659S SOT-23-6 (C883443) | 0.8 dB, 21.5 dB (distributor data) | ≈ 0.08 | unverified specs — bench-test |
| Discrete pHEMT | Broadcom ATF-54143 | 0.5 dB @ 2 GHz (DS), 16 dB+, OIP3 ≈ +36 dBm | ≈ 1–2 (est.) | lifecycle: check availability |
| L1 SAW | Murata SAFFB1G56KB0F0AR1X (C91647) | IL 1.6 dB, 35 dB (listing) | ≈ 0.06 | 1.1 × 0.9 mm class |
| Inductors | Murata LQW15 / Coilcraft 0402HP class | Q ≈ 60–100 at 900 MHz | 0.1–1 | gate inductor Q matters (Q 25 → +0.1 dB) |
| ESD | low-C TVS (≈ 0.2 pF class) | — | < 0.2 | required by u-blox for antenna inputs |
| Connector | U.FL with retention | — | ≈ 0.3 | |

## Block diagram
```
 patch --U.FL--+--[ESD]--[SAW1 SAFFB1G56]--[8.2 nH]--[BGA524N6 #1]--[SAW2]--[BGA524N6 #2]--[DC blk]--+--U.FL--> coax to receiver
               |                                     VCC1 (10R, 100n+10p)       VCC2 (10R, 100n+10p)  |
               |                                            \_______________________\________________[L bias-tee 120 nH]
               |                                                                                       (3.3 V from receiver RF line)
 option D: replace [SAW1][8.2 nH][BGA #1] with the ATF-54143 stage (5 V / 60 mA, local supply)
```

## Layout notes
- JLC 4-layer (L2 ground 0.21 mm): 50 Ω ≈ 0.36 mm with mask as microstrip (JLC calculator 0.359 mm), or 0.306 mm as CPWG with a 0.203 mm gap ([canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)); RF path straight, ≤ 15 mm per stage; via fence both sides at ≤ λ/20 of the highest gain frequency ([vias & stitching](../13-pcb-rf-layout-emc/vias-stitching-fencing.md)).
- **Ground the MMIC/pHEMT source pads with several vias directly under/at the pads** — source inductance is feedback; 0.5 nH moves S11* onto Γ_opt but erodes high-frequency stability ([LNA design](../06-rf-circuits/lna-design.md)).
- Input and output of a 35 dB chain must be ≥ 20 mm apart or shielded from each other (35 dB gain + 35 dB isolation = oscillation threshold); a small shield can over the two stages ([shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).
- Decoupling at each VCC pin, smallest cap nearest; RF-isolate the two supplies (10 Ω + caps).
- Keep the gate/bias resistors physically at the device — they are the stability network, not just bias.
- Follow the vendor evaluation-board layout for the MMIC; AN420 documents an 0201 layout.

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| Device stability, noise parameters | `proj_lna_gnss.py` §1, `rfckt_stability.py` | — (characterises the device) |
| Discrete design with real parts, stability 0.1–10 GHz, Monte-Carlo | `rfckt_lna.py` (verified) | μ > 1 everywhere, NF ≤ 0.9 dB |
| Cascade NF/gain/IIP3 | `proj_lna_gnss.py` §2 / `rfcalc.noise.cascade` | L2, L3 met |
| Vendor S2P (BGA524N6, SAW) cascade incl. the two-stage loop gain | scikit-rf ([Python RF toolkit](../16-simulation-tools/python-rf-toolkit.md)) | total in-band ripple ≤ 2 dB; no stability problem with the measured SAW S-parameters |
| Layout EM | openEMS of the input/output CPWG + SAW pads ([openEMS](../16-simulation-tools/openems-workflow.md)) | isolation input↔output ≥ gain + 15 dB |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| L-T1 | DC | bench supply via the bias-tee, current limit 30 mA; measure each stage current | 2.5 ± 0.5 mA per BGA (or 60 ± 6 mA ATF) |
| L-T2 | Oscillation | tinySA on the output, input open, shorted, 50 Ω, and touched with a finger; sweep 10 MHz–6 GHz | no spurs; noise floor rise consistent with gain × kT only |
| L-T3 | S-parameters | LiteVNA (> 70 dB < 3 GHz) with ≥ 20 dB pad on port 1 ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)) | S21 34–37 dB at L1 (chain C), S11 ≤ −8 dB, S22 ≤ −10 dB, out-of-band S21 at 433/905 MHz ≤ −20 dB |
| L-T4 | P1dB | signal generator + step attenuator + tinySA at L1 and at 433/905 MHz (out-of-band compression of the L1 tone with a blocker present) | in-band IP1dB within ±3 dB of −32 dBm (chain C input-referred); L1 gain drops ≤ 0.5 dB with a −30 dBm 433 MHz blocker |
| L-T5 | NF | Y-factor, 15 dB ENR source, RTL-SDR as the receiver (NF measured first, ≈ 7 dB est. at L1; LSF measured 11.9 dB at 1280 MHz on a V3, so ≈ 12 dB is plausible), 2nd-stage corrected ([NF measurement](../17-test-measurement/noise-figure-measurement.md)) | chain C NF ≤ 2.6 dB; chain D ≤ 1.1 dB |
| L-T6 | On the vehicle | antenna-to-antenna coupling (VNA S21 between the LoRa and GNSS antenna ports in the assembled airframe); then u-center C/N0 with each transmitter keyed into its antenna | coupling measured; C/N0 drop with TX on ≤ 3 dB |

Expected Y-factor readings (`proj_lna_gnss.py` §5, T_hot = 9461 K): chain NF 0.97 dB/37 dB gain → Y 14.20 dB (2nd stage hardly matters); single BGA (0.55 dB, 19.6 dB) with RTL-SDR second stage → Y 14.44 dB, uncorrected NF 0.72 dB; with a tinySA as second stage → Y 8.97 dB, uncorrected 6.62 dB. A 0.1 dB error in Y gives ≈ 0.1 dB error in NF — read Y with averaging and a true-RMS (power) detector ([spectrum analyzers](../17-test-measurement/spectrum-analyzers.md)).

## Regulatory check
Receive-only; no licence. The test signal generator at L1 must stay conducted (cables/attenuators) — 1559–1610 MHz is a protected radionavigation band ([IMDA](../19-regulations-safety/singapore-imda-rules.md)); never radiate L1 test signals, and never re-radiate live GNSS outdoors (GNSS repeaters are illegal without authorisation in most jurisdictions).

## Pre-registered predictions
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| N1 | Chain C gain at L1 34.9 dB into 1 m RG-174 (36.0 dB at the board output) | ±2 dB | SAW IL or LNA gain differ from listings |
| N2 | Chain C NF 2.2 dB; chain D 0.8 dB | ±0.4 dB | input loss (ESD, SAW, pads) under-estimated |
| N3 | BGA524N6 in-band IP1dB −16 dBm (table) rather than −12 dBm (feature list) | ±2 dB | tells which data-sheet number to trust |
| N4 | No oscillation 10 MHz–6 GHz in L-T2 for chain C | — | layout feedback; add shield/spacing |
| N5 | On the vehicle with SAW-first, keying the E22 at 33 dBm reduces mean C/N0 by ≤ 3 dB | — | coupling stronger than −20 dB, or TX wideband noise in L1 (see GNSS front-end recipe) |

## Risks and common failure modes
| Failure | Symptom | Cause / fix |
|---|---|---|
| LNA destroyed on the pad | GNSS dead after radio check | LNA-first with high coupling; SAW-first or limiter; measure coupling (L-T6) |
| Oscillation | high noise floor, spurs, receiver "jammed" | input/output coupling at 35 dB gain; ground vias; shield |
| Receiver overload | C/N0 high but positions erratic / AGC railed | > 50 dB total gain with short cable; drop a stage or add a pad |
| Bias-tee resonance | gain dip/peak in band | choke SRF near L1; choose/measure the inductor |
| ESD death | slow degradation of C/N0 | no ESD diode at an exposed antenna |
| Wrong datasheet number | compression earlier than expected | design to the table, verify (N3) |

## Cost estimate
| Item | Cost (USD) |
|---|---|
| Chain C parts (2 × BGA524N6, 2 × SAW, passives, ESD, U.FL) | ≈ 2 |
| JLC 4-layer 5 pcs + assembly of fine-pitch parts | ≈ 15–30 |
| Noise source (15 dB ENR class, hobby) | ≈ 20–60 (est.) |
| Test use of existing LiteVNA / tinySA / RTL-SDR | — |

## Practical notes
- If the receiver is a MAX-M10S, one SAW + one BGA (chain A, 16.9 dB) is enough — and put the module's internal LNA in its low-gain/bypass mode as u-blox advises for active antennas ([GNSS antennas](../08-antennas/gnss-antennas.md)).
- If the receiver is a ZED-F9P, remember it is L1/L2: an L1-only LNA board throws away L2 (and RTK fix quality); a multiband active antenna is the right part for RTK ([GNSS front end](gnss-front-end-design.md)).
- Measure the antenna-to-antenna coupling on the actual airframe before choosing LNA-first vs SAW-first; the decision is worth 3 dB of C/N0 or a dead LNA.

## Common mistakes & misconceptions
- **"Match the LNA input for best return loss."** That is the conjugate match (0.64∠153° here), not the noise match (0.29∠99°).
- **"The LNA is stable in band, so it is stable."** The ATF-54143 has K = 0.07 at 100 MHz; stability must be checked from tens of MHz to ≈ 10 GHz with the bias network.
- **"Lowest-NF MMIC is always best."** On a vehicle with a 2 W transmitter the 0 dBm abs-max input is the binding spec.
- **"SAW-first only costs its insertion loss."** With a cold-sky antenna, 1.6 dB of loss in front costs ≈ 3 dB of C/N0 because the antenna noise temperature is far below 290 K.
- **"Measure NF with the tinySA after the LNA."** Its ≈ 25 dB NF dominates unless the DUT gain is large or you correct for it.

## How to simulate / verify
- `python3 tools/verify/proj_lna_gnss.py` — device stability/noise, six cascades with C/N0, blocker table, data-sheet comparison, measurement planning, power.
- `python3 tools/verify/rfckt_lna.py` (≈ 4 min) — the verified ATF-54143 433 MHz and L1 designs with real parts and Monte-Carlo; `rfckt_stability.py` — K/μ/stability circles.
- Bench: L-T1 … L-T6 above.

## Open questions / gaps
- Measured antenna-to-antenna coupling on a Space Bar airframe (drives the SAW-first decision).
- ATF-54143 S-parameters at a low-current bias (3 V/20 mA) are not in the KB; lifecycle status not checked.
- Out-of-band mismatch of the GNSS patch at 433/905 MHz (assumed 10/6 dB) — measure with the VNA.
- SAFFB1G56KB0F0A rejection at 433 and 905 MHz specifically (listing says "35 dB" without frequency).

## Sources
1. This KB, [LNA design](../06-rf-circuits/lna-design.md) and `tools/verify/rfckt_lna.py` — noise circles, verified ATF-54143 433 MHz and L1 designs, MMIC comparison. (internal; Gonzalez, Pozar)
2. Broadcom/Avago, *ATF-54143 Data Sheet* — S-parameters and noise parameters at 3 V/60 mA, absolute maxima — via `tools/verify/rfckt_atf54143_data.py`. (datasheet)
3. Infineon, *BGA524N6 Data Sheet* Rev 3.0 (2014-01-24), electrical characteristics table p. 9 and feature list p. 6 — read from a distributor PDF mirror (taoic.oss-cn-hangzhou.aliyuncs.com) on 2026-10-02. (datasheet)
4. Infineon, *AN420: BGA524N6 Low Power LNA for GNSS Applications (0201 components)* Rev 1.0 (2015) — 1.8 V/1.5 V results (Farnell mirror). (app note)
5. This KB, [LNAs, PAs, gain blocks](../18-components-parts/lna-pa-gain-block-mmics.md), [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md) — part numbers, LCSC codes, SAW listing. (internal)
6. This KB, [GNSS antennas](../08-antennas/gnss-antennas.md) — u-blox ZED-F9P active-antenna specification (17–50 dB, NF < 4 dB, bias-tee 120 nH), MAX-M10S internal LNA modes, minimum signal level. (internal; u-blox integration manuals)
7. This KB, [Amplifier stability and biasing](../06-rf-circuits/amplifier-stability-and-biasing.md), [RF switches & limiters](../06-rf-circuits/rf-switches-attenuators-limiters.md), [NF measurement](../17-test-measurement/noise-figure-measurement.md). (internal)
