---
title: Receiver cascade analysis (gain, NF, IIP3, P1dB budget)
domain: 07-noise-linearity
slug: receiver-cascade-analysis
tags: [cascade, receiver-budget, level-diagram, noise-figure, IIP3, P1dB, LNA-placement, ground-station, GNSS-active-antenna, python-tool]
prerequisites: [noise-figure-and-friis.md, nonlinearity-p1db-ip3-intermod.md, dynamic-range-sfdr-blocking.md]
related: [sensitivity-and-mds.md, thermal-noise-and-noise-temperature.md, ../06-rf-circuits/receiver-architectures.md, ../06-rf-circuits/lna-design.md, ../08-antennas/gnss-antennas.md, ../15-lora-ism-radios/ground-station-design.md, ../20-projects-recipes/gnss-front-end-design.md, ../09-propagation-link-budget/link-budget-methodology.md]
level: intermediate
confidence: high
last_updated: 2026-10-03
---

# Receiver cascade analysis (gain, NF, IIP3, P1dB budget)

## Questions this page answers
- How do I build a stage-by-stage budget for a receiver (gain, noise figure, IIP3, compression)?
- Where should the LNA, the SAW filter and the long cable go on a LoRa ground station?
- How much does each stage contribute to the total noise, and which stage limits linearity?
- What does a "level diagram" show, and how do I check headroom for a strong interferer?
- How does a GNSS active antenna chain work out, and what C/N0 should I expect?
- Is there a script I can reuse for my own chains?

## TL;DR
- A cascade budget tracks, stage by stage: **cumulative gain**, **cumulative NF** (Friis), **cumulative IIP3** ($1/IIP3 = \sum G_\text{before}/IIP3_i$), **input P1dB**, and each stage's **share of the total noise**. The reusable tool is `tools/verify/noise_cascade.py` (`Stage`, `cascade`, `print_cascade`, `level_diagram`).
- **915 MHz ground station** (SX1262-class module, 10 m of coax): module at the end of the coax → NF 8.6 dB, sensitivity (SF12/BW125) −134.4 dBm, IIP3 −2.4 dBm. Masthead SAW+LNA → **NF 2.55 dB, −140.5 dBm**, IIP3 −18.9 dBm. LNA at the module end (after the coax) → NF 4.97 dB, −138.0 dBm.
- **433 MHz station, sky-pointing Yagi ($T_a$ ≈ 150 K), 5 m of LMR-400:** module only → floor −117.1 dBm (125 kHz), sensitivity ≈ −137.1 dBm; masthead LNA (0.6 dB) → system 203 K, **≈ −144.6 dBm** (7.5 dB better) at a cost of ~8 dB of SFDR.
- **GNSS active antenna** (patch → LNA → SAW → LNA → 3 m RG-174 → receiver): **NF 1.19 dB**, 92 % of the noise from the patch loss + first LNA; $C/N_0$ ≈ 47 dB-Hz at the −128.5 dBm GPS L1 C/A minimum ($T_a$ = 100 K). The same patch *passive* on 3 m of RG-174: NF 7.5 dB, −8.8 dB of $C/N_0$.
- Rules: (1) nothing lossy before the first LNA except the protection/filtering you truly need; (2) enough LNA gain to bury later noise (~15–20 dB when the rest is ~6–9 dB NF), no more; (3) check the *last* stages for linearity and the level diagram for headroom against the strongest expected interferer.

## Intuition (no math)
Think of the chain as a sequence of pipes, each adding a little dirt (noise) and each with a maximum pressure it tolerates before leaking (compression). Dirt added early is amplified by every stage afterwards — so it matters most; dirt added late is diluted by the gain before it. Pressure is highest at the end, after all the gain — so late stages are the first to leak. A good budget puts the cleanest pipe first (low-NF LNA), just enough amplification to make the rest of the dirt irrelevant, and filters early enough to keep strong unwanted flows from over-pressuring anything.

A **level diagram** makes this visible: plot, at each stage input, the wanted signal, the noise floor and the strongest interferer. The SNR is set almost entirely by the first stage; the interferer's headroom to each stage's compression point shows where the chain will break.

## The math

### Level 1 — the per-stage recursion
For stages $i = 1..n$ with available gain $G_i$, noise factor $F_i$, input-referred $IIP3_i$ and $P_{1dB,i}$ (linear units), and $G_{<i} = \prod_{j<i}G_j$:
$$F_{\le i} = F_{\le i-1} + \frac{F_i-1}{G_{<i}},\qquad \frac{1}{IIP3_{\le i}} = \frac{1}{IIP3_{\le i-1}} + \frac{G_{<i}}{IIP3_i},\qquad \frac{1}{P_{1dB,\le i}} \approx \frac{1}{P_{1dB,\le i-1}} + \frac{G_{<i}}{P_{1dB,i}}.$$
- Noise contribution of stage $i$ (fraction of total input-referred excess noise): $\dfrac{T_{e,i}/G_{<i}}{\sum_j T_{e,j}/G_{<j}}$.
- Sensitivity $= 10\log_{10}(k(T_a + T_{e,\text{tot}})B) + 30 + \text{SNR}_\text{min}$ dBm.
- SFDR $= \tfrac23(IIP3_\text{tot} - N)$.

### Level 2 — assumptions behind the recursion
1. **Matched interfaces.** Datasheet NF and gain are for 50 Ω source/load; with a mismatched interstage (e.g. a SAW filter whose out-of-band impedance is reactive), use available gains and the NF at the actual source impedance (see [noise-figure-and-friis](noise-figure-and-friis.md) Level 3).
2. **Temperatures.** Passive stages use $F = L$, valid at 290 K; hot or cold feeders need $T_e = (L-1)T_p$.
3. **Coherent IIP3 addition** (worst case) — the power-sum variant is printed alongside; real chains usually fall between.
4. **P1dB combination is approximate** — compression points do not combine exactly by that formula (they depend on how each stage saturates); use it for "which stage compresses first", then check with the level diagram.
5. **Bandwidth.** Noise is integrated in the final (narrowest) channel bandwidth; broadband noise from early stages matters where it can alias (ADC Nyquist zones) or where image bands are not filtered (SSB mixer noise — see [noise-figure-and-friis](noise-figure-and-friis.md)).

### Level 3 — the level diagram
At the input of stage $i$: signal $P_s + G_{<i}$; noise $10\log_{10}(kB\,G_{<i}(T_a + \sum_{j<i}T_{e,j}/G_{<j}))$; interferer $P_b + G_{<i}$; headroom $P_{1dB,i} - (P_b + G_{<i})$. The SNR column changes only where a stage adds significant noise; the headroom column shows where the interferer approaches compression. Implemented as `level_diagram()`; for the masthead 915 MHz chain with the wanted signal at sensitivity (−140.5 dBm) and a −40 dBm blocker:

| At input of | G before | Signal | Blocker | Noise (125 kHz) | SNR | Headroom to IP1dB |
|---|---|---|---|---|---|---|
| SAW | 0.0 | −140.5 | −40.0 | −123.0 | −17.5 | – |
| LNA | −1.5 | −142.0 | −41.5 | −123.0 | −19.0 | 36.5 dB |
| 10 m coax | 16.5 | −124.0 | −23.5 | −104.3 | −19.7 | – |
| SX1262 | 13.9 | −126.6 | −26.1 | −106.9 | −19.7 | 11.1 dB |
| (output) | 13.9 | −126.6 | −26.1 | −106.6 | **−20.0** | |

The SNR at the output equals the SF12 threshold (−20 dB), as it must at sensitivity; the SAW's 1.5 dB loss appears in the first SNR step; the receiver chip is the stage closest to compression (11 dB of headroom, with an *assumed* chip input P1dB of −15 dBm — Semtech does not publish one).

## Design equations & rules of thumb

| Rule | Why | Numbers |
|---|---|---|
| NF(total) ≥ NF(first stage) | Friis | |
| Loss before LNA adds dB-for-dB | $F = L\cdot F_\text{LNA}$ | 1.5 dB SAW → +1.5 dB NF |
| LNA gain ≳ NF_rest(linear) × 10 | later noise < ~10 % | rest at 8.6 dB (F = 7.2) → $G_1$ ≳ 18 dB |
| Cascade IIP3 ≈ IIP3_last − G_before (when last dominates) | linearity accumulates at the output | −5 − 13.9 = −18.9 dBm |
| Headroom: strongest interferer ≥ 10 dB below each stage's P1dB | stay in weakly nonlinear region | |
| Active GNSS antenna net gain within receiver's allowed range | too little → cable NF; too much → overload | MAX-M10S: ≤ 30 dB (low-gain mode) |

## Worked examples
All numbers are printed by `python3 tools/verify/noise_cascade.py`.

### Example A — 915 MHz LoRa ground station (secondary link, E220-900T30D/SX1262-class receiver)
Assumptions (typical, not measured): 10 m of LMR-240-class coax ≈ 2.6 dB at 915 MHz; SAW filter 1.5 dB loss; LNA NF 0.7 dB, G 18 dB, IIP3 +8 dBm, IP1dB −5 dBm; module NF 6 dB (from the SX126x sensitivity table), IIP3 −5 dBm (datasheet), IP1dB −15 dBm (assumed). Bandwidth 125 kHz, SF12 (SNR −20 dB), $T_a$ = 290 K.

| Chain | NF | $T_{e}$ | Floor (125 kHz) | SF12 sensitivity | IIP3 | IP1dB (in) | SFDR |
|---|---|---|---|---|---|---|---|
| A1: antenna → 10 m coax → module | 8.60 dB | 1811 K | −114.4 dBm | −134.4 dBm | −2.4 dBm | −12.4 dBm | 74.7 dB |
| A2: SAW → LNA (mast) → coax → module | **2.55 dB** | 232 K | −120.5 dBm | **−140.5 dBm** | −18.9 dBm | −28.9 dBm | 67.7 dB |
| A3: coax → SAW → LNA (at module) → module | 4.97 dB | 621 K | −118.0 dBm | −138.0 dBm | −18.9 dBm | −28.9 dBm | 66.1 dB |

Noise shares in A2: SAW 51.6 %, LNA 30.9 %, coax 2.3 %, module 15.2 %. The SAW is the biggest single contributor — worth it only if strong out-of-band signals exist (it protects the LNA). In A3 the coax contributes 38 % — the cable in front of the LNA costs 2.4 dB relative to A2. **Masthead placement is worth 6.1 dB over no LNA and 2.4 dB over an LNA at the module end.**

### Example B — 433 MHz ground station (primary link, E22-400T33D/SX1268-class receiver)
Sky-pointing crossed Yagi, $T_a$ ≈ 150 K assumed (see [thermal-noise-and-noise-temperature](thermal-noise-and-noise-temperature.md) Example 3), 5 m of LMR-400 (0.45 dB).

| Chain | NF | $T_\text{sys}$ | Floor (125 kHz) | SF12 sensitivity | IIP3 | SFDR |
|---|---|---|---|---|---|---|
| B1: coax → module | 6.45 dB | 1141 K | −117.1 dBm | −137.1 dBm | −4.5 dBm | 75.0 dB |
| B2: masthead LNA (0.6 dB, 20 dB, IIP3 +10 dBm) → coax → module | 0.73 dB | 203 K | −124.6 dBm | **−144.6 dBm** | −24.6 dBm | 66.7 dB |

With a cold antenna the LNA's benefit is larger (7.5 dB) than the NF difference alone suggests, because the module's 865 K dominated $T_\text{sys}$ in B1. In range terms (free space), 7.5 dB is a factor 2.4. But the link budget in [09-propagation-link-budget/link-budget-methodology](../09-propagation-link-budget/link-budget-methodology.md) shows the 433 MHz downlink has > 50 dB of free-space margin at 30 km — so the LNA mainly helps the *hard* cases (landed rocket, antenna nulls, terrain), while its linearity cost matters at crowded launch sites.

### Example C — GNSS L1 active antenna
Patch feed loss 0.3 dB → LNA1 (NF 0.8 dB, G 17 dB, IIP3 −5 dBm) → SAW 1.2 dB → LNA2 (1.5 dB, 12 dB, IIP3 0 dBm) → 3 m RG-174 (≈ 1.4 dB/m → 4.2 dB, typical datasheet value at 1.5 GHz) → GNSS RF front end (NF 3 dB assumed, G 20 dB, IIP3 −20 dBm).

| Stage | G_cum | NF_cum | Noise share | IIP3_cum |
|---|---|---|---|---|
| patch/feed loss | −0.3 | 0.30 | 22.8 % | ∞ |
| LNA1 | 16.7 | 1.10 | 69.0 % | −4.7 dBm |
| SAW | 15.5 | 1.12 | 2.2 % | −4.8 dBm |
| LNA2 | 27.5 | 1.16 | 3.7 % | −15.9 dBm |
| 3 m RG-174 | 23.3 | 1.17 | 0.9 % | −15.9 dBm |
| receiver | 43.3 | **1.19** | 1.5 % | −43.3 dBm |

$T_e$ = 91 K. $C/N_0$ for the GPS L1 C/A specified minimum (−128.5 dBm): 48.6 / 47.3 / 46.3 dB-Hz for $T_a$ = 50 / 100 / 150 K; typical open-sky signals (≈ −125 dBm) give ~51 dB-Hz. The net gain of 23.3 dB into the receiver is within the MAX-M10S's 30 dB maximum for its default low-gain mode [4]; a 40 dB-gain "high-gain" active antenna on a short cable could exceed it. Low overall IIP3 (−43 dBm) is normal for GNSS (signals are far below the noise), which is exactly why the SAW between the LNAs (and ideally one before LNA1) is essential near a 2 W telemetry transmitter.

### Example D — the lesson in three lines
3 dB cable → LNA (0.8 dB, 20 dB) → module (6 dB): **3.91 dB**. LNA → 3 dB cable → module: **1.04 dB**. 3 dB cable → module: **9.0 dB**.

## Practical notes
- **Get real numbers.** Cable loss per metre at your frequency (from the cable datasheet, including connectors, ~0.1–0.2 dB each at UHF), SAW insertion loss at the *band edge* and temperature, LNA NF at the actual bias. Budgets built on typical values are optimistic by 1–2 dB.
- **Masthead LNAs** need weatherproofing, DC feed (bias tee), ESD/lightning protection (a gas discharge tube or quarter-wave stub before the LNA adds little loss) and a limiter if a transmitter is nearby. Every one of these sits before the LNA and adds to NF — budget them.
- **Sequencing with transmitters:** a masthead LNA on a transceive antenna needs a T/R switch or sequencer; for Marcus's downlink-only telemetry this is not needed at the ground station unless the same antenna also sends commands/RTK.
- **GNSS on the flight computer:** keep the active-antenna cable short (U.FL 1.13 mm cable loses ≈ 2.6 dB/m at 1.575 GHz — Hirose fit in the [coax table](../03-transmission-lines-matching/coax-and-cables.md); check your cable's datasheet), choose an active antenna with a pre-LNA SAW if the 433/915 MHz transmitter antenna is nearby, and verify the antenna supply (MAX-M10S and ZED-F9P both support active-antenna supervision).

## Common mistakes & misconceptions
- **Budgeting in dB for NF** — add *noise temperatures* (or use linear Friis); only losses before the first amplifier add in dB.
- **Using the LNA's NF as the system NF** while forgetting the connector, ESD diode, matching-network loss and the SAW before it.
- **Counting the cable after the LNA as if it were before it** (or vice versa).
- **Ignoring linearity when adding gain.** The budget must show IIP3/P1dB, not just NF.
- **Assuming datasheet sensitivity with a real antenna.** Datasheet sensitivity assumes a 290 K, 50 Ω source at the chip pins; the station's sensitivity at the antenna connector includes all losses and $T_a$.
- **Too much GNSS antenna gain.** Receivers specify a maximum external gain; exceeding it compresses the receiver's front end or triggers its internal attenuation, degrading performance.

## How to simulate / verify
- `tools/verify/noise_cascade.py` — run it to reproduce every table; import it to budget your own chain:
  ```python
  from noise_cascade import Stage, print_cascade, level_diagram
  chain = [Stage('SAW', -1.5, iip3=35), Stage('LNA', 18, nf=0.7, iip3=8, ip1db=-5),
           Stage('coax 10 m', -2.6), Stage('module', 0, nf=6.0, iip3=-5, ip1db=-15)]
  print_cascade(chain, 'my station', B=125e3, snr_min=-20, Ta=290)
  level_diagram(chain, P_sig=-140, P_blk=-40, B=125e3)
  ```
  It includes a Monte-Carlo check of the Friis formula and a two-tone time-domain check of the cascaded IIP3.
- scikit-rf can cascade measured S-parameters *and* noise data of real parts (Touchstone files with noise sections) to include mismatch effects.
- Validate with measurements: a noise-figure analyzer or an SDR Y-factor test at the antenna connector of the finished station ([17-test-measurement/noise-figure-measurement](../17-test-measurement/noise-figure-measurement.md)).

## Open questions / gaps
- The SX126x/LLCC68 input P1dB and the EBYTE modules' effective NF/IIP3 are not published (assumed −15 dBm and 6 dB/−5 dBm here).
- Real part numbers and measured data for the LNA/SAW in Examples A–C belong to [18-components-parts](../18-components-parts/lna-pa-gain-block-mmics.md) and [20-projects-recipes/gnss-front-end-design](../20-projects-recipes/gnss-front-end-design.md).
- RG-174 / 1.13 mm cable loss at 1.575 GHz: checked 2026-10-03 (W5-E9, D6 #24) against the 03 [coax table](../03-transmission-lines-matching/coax-and-cables.md) fits — RG-174 ≈ 1.39 dB/m (the 1.4 dB/m used above stands); 1.13 mm micro-coax ≈ 2.65 dB/m, not the 1.5–2 dB/m previously quoted on this page.

## Sources
1. H. T. Friis, "Noise figures of radio receivers," *Proc. IRE* 32(7), 419–422 (1944). (peer-reviewed)
2. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.2.5 (cascaded nonlinear stages), §2.3.6 (cascaded noise), ch. 4 (transceiver architectures and budgets). (textbook)
3. Semtech, *SX1261/2 Data Sheet* Rev 1.2/2.2: sensitivity table, IIP3 −5 dBm, blocking. (datasheet)
4. u-blox, *MAX-M10S Data sheet* UBX-20035208: external gain limits (30 dB low-gain mode / 40 dB bypass), sensitivity. (datasheet)
5. IS-GPS-200 (Navstar GPS Space Segment/Navigation User Interfaces): minimum received L1 C/A power −158.5 dBW (= −128.5 dBm) for a 3 dBi linearly polarised antenna at ≥ 5° elevation. https://www.gps.gov/technical/icwg/ (standard)
6. `tools/verify/noise_cascade.py` (this KB).
