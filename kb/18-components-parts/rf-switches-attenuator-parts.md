---
title: RF switches, digital step attenuators, fixed pads, limiters and T/R switching — part selection guide
domain: 18-components-parts
slug: rf-switches-attenuator-parts
tags: [rf-switch, spdt, sp4t, pe4259, pe42420, pe42442, sky13351, sky13453, sky13330, sky13317, as179, hmc849, hmc544, adrf5019, bgs12, digital-step-attenuator, dsa, pe43711, pe4312, pe4314, hmc624, hmc472, dat-31r5a, pi-pad, limiter, pin-diode, t-r-switch, lcsc]
prerequisites:
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
related:
  - ../04-real-components-hf/resistors-at-rf.md
  - ../05-analog-electronics/diodes-schottky-pin-varactor.md
  - ../12-phased-arrays/array-factor-linear-arrays.md
  - lna-pa-gain-block-mmics.md
  - phased-array-and-radar-parts.md
  - filter-parts-saw-ceramic-ltcc.md
level: intermediate
confidence: medium
last_updated: 2026-09-29
---

# RF switches, step attenuators, pads, limiters and T/R switching — part selection guide

## Questions this page answers
- Which SPDT switch should I use to share one antenna between a LoRa radio and a GNSS/second radio, or between TX and RX?
- Can a tiny 1 × 1 mm switch handle +30 dBm from my 1 W PA? What about when the antenna is damaged on landing?
- What is the difference between reflective and absorptive switches, and when does it matter?
- Which digital step attenuator (DSA) should I use for an AGC loop, an array calibration or a bench fixture?
- How do I make a 3/6/10 dB attenuator pad out of JLCPCB basic resistors?
- How do I protect an LNA at a ground station from my own transmitter?
- Which parts should I avoid (75 Ω lookalikes, last-time-buy parts)?

## TL;DR
- **Key switch specs**: insertion loss (IL), isolation, P0.1dB/P1dB (power handling), IIP3/harmonics (a switch after the PA must not generate harmonics), frequency range (low-end limited by DC-blocking caps inside CMOS switches), switching time, control logic level, reflective vs absorptive, supply/negative-voltage generator spurs. Theory: [switches, attenuators & limiters](../06-rf-circuits/rf-switches-attenuators-limiters.md).
- **Small-signal SPDT, deep LCSC stock**: **Skyworks SKY13453-385LF** (10 MHz–6 GHz, IL 0.40 dB @ 2 GHz, isolation > 25 dB, IP1dB +33 dBm, 1×1 mm QFN-6, 61k in stock at ~US$0.46) [2]; **SKY13351-378LF** (20 MHz–6 GHz, IL 0.35 dB, isolation 25 dB @ 3 GHz, IP1dB +30 dBm) [2]; **pSemi PE4259** (10 MHz–3 GHz, IL 0.35 dB @ 1 GHz, isolation 30 dB, P1dB +33.5 dBm, SC-70-6 — easiest to hand-solder, 22k in stock at ~US$0.58) [3].
- **T/R switch for ~1 W**: **SKY13330-397LF** (0.1–6 GHz, IP1dB **+39 dBm**, IIP3 +55 dBm, IL 0.35 dB @ 2 GHz, 2×2 mm, no DC blocks needed, 15.7k in stock at ~US$0.56) [2]; ADI HMC544A (DC–4 GHz, P1dB +39 dBm, SOT-23-6) and ADRF5019 (0.1–13 GHz, +39 dBm, hot-switch capable) [1]. For > 5 W use PIN-diode quarter-wave T/R designs (SMP13xx diodes).
- **High-isolation / absorptive**: **PE42420** (20 MHz–6 GHz, isolation 69/62/50 dB at 1/3/6 GHz, IIP3 +65 dBm, P1dB +33 dBm) [4]; **PE42442** SP4T (30 MHz–6 GHz, 61 dB @ 900 MHz, IIP3 +58 dBm) [5]; HMC849A (DC–6 GHz, up to 60 dB, IL 0.8 dB) [6].
- **Digital step attenuators**: **PE43711** (9 kHz–6 GHz, 7-bit, 0.25 dB steps to 31.75 dB, glitch-less, 4×4 QFN-24, ~US$2.77) [7]; **PE4312** (1 MHz–4 GHz, 6-bit 0.5 dB to 31.5 dB, IIP3 +59 dBm, ~US$2.31, 4.9k stock) [8]; HMC624A (0.1–6 GHz, 6-bit 0.5 dB) [6]; Mini-Circuits DAT-31R5A+ (DC–4 GHz, 0.5 dB, IP3 +52 dBm) [9]. **PE4314 is a 75 Ω part** (CATV) — do not drop it into a 50 Ω design [10].
- **Fixed pads from JLC basic/preferred 0402 resistors** (no feeder fee): 3 dB ≈ 300 Ω shunt / 22 Ω series (3.3 dB, RL −30 dB); 6 dB ≈ 150 / 33 Ω (5.7 dB, RL −34 dB); 10 dB ≈ 100 / 75 Ω (10.1 dB, RL −34 dB) — computed below; exact E96 values give ±0.1 dB. Chip attenuators: Mini-Circuits YAT-3A+, LAT-3+, PAT-3+ [1].
- **Limiters**: Mini-Circuits RLM-33-2W+ (coaxial-style SMD limiter, ~US$17.6) [1]; DIY: anti-parallel PIN/Schottky diodes after a λ/4 or series resistor — see [diodes](../05-analog-electronics/diodes-schottky-pin-varactor.md). Most LNAs die above +15…+22 dBm input.

## Intuition (no math)
A solid-state RF switch is a set of transistors (CMOS-on-insulator such as pSemi UltraCMOS, GaAs pHEMT, or PIN diodes) that are either "on" (a small resistance, which is the insertion loss) or "off" (a small capacitance, which leaks — the isolation). As frequency rises, the off-capacitance leaks more, so isolation falls with frequency. As signal voltage rises, "off" transistors start to turn on during the voltage peaks, causing compression and harmonics — this sets the power rating. Stacking transistors raises the voltage rating, which is why "high-power" switches are bigger.

- **Reflective** switch: the unused port is open — anything arriving there is reflected. Fine for a T/R switch.
- **Absorptive** (non-reflective) switch: the unused port is terminated in 50 Ω, so a PA or filter connected to it still sees a good match. Needed when the off-port device must not see an open (e.g. an amplifier that could oscillate, a filter bank, test fixtures).

A **digital step attenuator** is a chain of switched resistive pads (0.25/0.5/1/2/4/8/16 dB bits). "Glitch-less" parts avoid a momentary high-attenuation spike when several bits change together — important in AGC loops and phased-array amplitude control.

## The math
### Level 1 — power handling and mismatch
A signal of power $P$ into $Z_0$ = 50 Ω has peak voltage $V_{pk}=\sqrt{2PZ_0}$ (1 W → 10 V). With a mismatch of reflection coefficient $|\Gamma|$ at the antenna, the standing-wave voltage maximum is $V_{max}=V_{pk}(1+|\Gamma|)$ ([VSWR](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)). The switch "sees" an equivalent matched power
$$P_{eq}=P(1+|\Gamma|)^2$$
VSWR 3 ($|\Gamma|$ = 0.5): $P_{eq}=2.25P$, i.e. +3.5 dB. A +30 dBm PA into a broken antenna therefore stresses the switch like +33.5 dBm — right at the PE4259's P1dB and 5.5 dB below the SKY13330's.

### Level 2 — isolation, insertion loss and the cascade
Switch IL adds dB-for-dB to NF if it sits before the LNA ([Friis](../07-noise-linearity/noise-figure-and-friis.md)). Isolation $I$ (dB) from the TX port to the RX port means the LNA input sees $P_{TX}-I$: +30 dBm with 25 dB isolation → +5 dBm at the LNA (safe only if the LNA is off or survives it); with 60 dB → −30 dBm.

### Level 3 — pad design
A symmetric 50 Ω π-pad of attenuation $A$ dB ($K=10^{A/20}$) uses
$$R_{shunt}=Z_0\frac{K+1}{K-1},\qquad R_{series}=Z_0\frac{K^2-1}{2K}$$
(T-pad: $R_{series,T}=Z_0\frac{K-1}{K+1}$, $R_{shunt,T}=Z_0\frac{2K}{K^2-1}$). Exact and nearest-E96 values: 3 dB 292.4/17.6 Ω → 294/17.8; 6 dB 150.5/37.4 → 150/37.4; 10 dB 96.2/71.2 → 95.3/71.5; 20 dB 61.1/247.5 → 60.4/249 (all within 0.13 dB and |Z_in − 50| < 0.5 Ω, computed). Resistor parasitics limit 0402 thick film to a few GHz — [resistors at RF](../04-real-components-hf/resistors-at-rf.md). Pad dissipation: the first shunt and series resistors take most of the power — a 10 dB pad at +20 dBm (100 mW) must dissipate ~90 mW, above an 0402's 62.5 mW rating.

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| Choose switch P0.1dB ≥ $P_{out}$ + 10·log₁₀(1+|Γ|)² + 3 dB | TX paths | +30 dBm PA, VSWR 3 → ≥ +36.5 dBm → SKY13330 / HMC544A / ADRF5019 |
| LNA input in TX = $P_{TX}$ − isolation | shared antenna | 25 dB isolation needs LNA off/bypass during TX |
| Isolation falls ~6 dB/octave with frequency (capacitive leakage) | single FET | PE42420: 69 → 62 → 50 dB at 1 → 3 → 6 GHz [4] |
| Low-frequency limit set by internal/external DC blocks | CMOS SOI switches | 10–30 MHz typical; "9 kHz" parts use special designs |
| DSA accuracy degrades with frequency and attenuation | PE4312 | ±(0.10 + 1 % × A) at 1 GHz; ±(0.15 + 8 % × A) at 4 GHz [8] |
| Pad power per resistor ≈ fraction of input absorbed | thick-film 0402 62.5 mW | keep pads ≤ +15 dBm input, else 0603/1206 or chip attenuators |

## Comparison tables (LCSC data: 2026-04 snapshot [1]; US$ qty 1 unless noted)
### A. SPDT / SP3T / SP4T switches
| Part | Type | Range | IL | Isolation | P1dB / IIP3 | Control / supply | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|---|---|
| **Skyworks SKY13453-385LF** | SPDT reflective | 10 MHz–6 GHz | 0.40 dB @ 2 GHz (0.4–0.7) | > 25 dB @ 2 GHz (27–15) | +33 / +57 dBm | single bit, 2.5–3.5 V | QFN-6 1×1 | C150878 / 61k / 0.46 (qty 5) [2] |
| **Skyworks SKY13351-378LF** | SPDT reflective | 20 MHz–6 GHz | 0.35 dB @ 3 GHz | 25 dB @ 3 GHz | +30 (LCSC) / +50 dBm | 1.8–5 V control | QFN-6 1×1 | C129189 / 3.8k / 0.84 (qty 5) [2] |
| **Skyworks SKY13330-397LF** | SPDT, high power | 0.1–6 GHz | 0.35 dB @ 2 GHz, 0.60 @ 6 GHz | 35–16 dB | **+39** / +55 dBm | 1.65–2.7 V logic | QFN-12 2×2 | C2654715 / 15.7k / 0.56 [2] |
| Skyworks SKY13317-373LF | SP3T | 20 MHz–6 GHz | 0.5 dB @ 2.5 GHz | 25 dB | +29 / +50 dBm | 1.8–5 V | DFN-8 1.5×1.5 | C129190 / 5.8k / 1.71 (qty 5) [2] |
| Skyworks AS179-92LF | SPDT (GaAs) | 20 MHz–3 GHz | 0.3 dB @ 0.9 GHz | 25–23 dB | +30 / +43 dBm | 3 V complementary | SC-70-6 | C83422 / 21k / 1.25 [2] |
| Skyworks AS193-73LF | SPDT, 2.5–5 V | 0.1–2.5 GHz | 0.35 dB @ 0.9 GHz | 24 dB | +37 / +55 dBm | | SOT-23-6 | C6199 / 3.0k / 1.29 — **Last Time Buy** [2] |
| **pSemi PE4259** | SPDT reflective | 10 MHz–3 GHz | 0.35 dB @ 1 GHz, 0.5 @ 2 GHz | 30 dB @ 1 GHz | +33.5 dBm | 1.8–3.3 V, single-pin or complementary | SC-70-6 | C470892 / 22k / 0.58 (qty 2) [3] |
| pSemi PE42421 | SPDT | 10 MHz–3 GHz | | | +33.5 dBm | | SC-70-6 | C470893 / 33 / 1.42 |
| **pSemi PE42420** | SPDT **absorptive** | 20 MHz–6 GHz | (see DS) | 69 / 62 / 50 dB @ 1 / 3 / 6 GHz | +33 / +65 dBm | 2.7–5.5 V | LGA-20 4×4 | C3303823 / 39 / 2.78 [4] |
| **pSemi PE42442** | SP4T absorptive | 30 MHz–6 GHz | | 61 dB @ 900 MHz, 55 @ 2.1, 43 @ 4, 32 @ 6 GHz | IIP3 +58, IIP2 +97 dBm | 1.8 V logic, 255 ns | QFN-24 4×4 | C470913 / 21 / 4.35 [5] |
| pSemi PE42540 | SP4T | 10 Hz–8 GHz | | | +33 dBm | 3–3.55 V | LGA-32 5×5 | C17553633 / 25 / 9.01 |
| pSemi PE42820 | SPDT high power, hot-switch | 30 MHz–2.7 GHz | | | (high power; unverified) | 2.3–5.5 V | QFN-32 5×5 | C2654732 / 61 / 15.47 |
| ADI HMC849A | SPDT absorptive, high isolation | DC–6 GHz | 0.8 dB | up to 60 dB | +33 / +52 dBm | 3–5 V | QFN-16 4×4 | C579577 / 65 / 10.56 [6] |
| ADI HMC544A | SPDT | DC–4 GHz | (see DS) | | **+39 dBm** | 5 V | SOT-23-6 | C579555 / 1.4k / 1.67 [1] |
| ADI HMC7992 | SP4T | 0.1–6 GHz | | | +35 dBm | 3.3–5 V | LFCSP-16 3×3 | C514406 / 479 / 5.61 [1] |
| ADI ADRF5019 | SPDT, hot-switch | 0.1–13 GHz | | | +39 dBm | 3.3 V | LFCSP-16 3×3 | C659612 / 92 / 11.52 [1] |
| ADI HMC1118 / ADRF5040 | SPDT / SP4T | 9 kHz–13 / 12 GHz | | | +37 dBm | 3.3 V | LFCSP | C461515 / 806 / 6.56; C481900 / 23 / 14.82 [1] |
| Renesas F2932 | SPDT absorptive, hot-switch | 50 MHz–8 GHz | | | +36.5 dBm | 2.7–5.5 V | QFN-16 4×4 | C3304167 / 76 / 4.99 [1] |
| Infineon BGS12SN6 / BGS12P2L6 | SPDT | 50 MHz–6 GHz | | | — / +37 dBm | 1.65–3.5 V | 0.7×1.1 mm | C114953 / 10.5k / 0.18; C3312945 / 10k / 0.28 [1] |
| Maxscend MXD8625C / MXD8641H | SPDT / SP4T (handset) | 0.1–3 GHz | | | +36 dBm | 2.5–3 V | 0.7×1.1 / 2×2 | C285546 / 4.4k / 0.045; C285560 / 5.7k / 0.10 [1] |
IL/isolation not listed are not on the pages read — check the datasheet at your frequency.

### B. Digital step attenuators
| Part | Range | Steps / bits | Accuracy / linearity | Interface | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **pSemi PE43711** | 9 kHz–6 GHz | 0.25/0.5/1 dB, 7-bit, to 31.75 dB | monotonic 0.25 dB to 4 GHz, 0.5 dB to 5 GHz, 1 dB to 6 GHz; glitch-less; bidirectional | serial + parallel, 1.8 V logic | QFN-24 4×4 | C470929 / 327 / 2.77 [7] |
| **pSemi PE4312** | 1 MHz–4 GHz | 0.5 dB, 6-bit, to 31.5 dB | ±(0.10 + 1 %×A) @ 1 GHz; IIP3 +59 dBm | serial + parallel | QFN-20 4×4 | C500480 / 4.9k / 2.31 [8] |
| pSemi PE4314 | 1 MHz–2.5 GHz | 0.5 dB, 6-bit | glitch-less | | QFN-20 4×4 | C7327101 / 1.0k / 2.02 — **75 Ω** [10] |
| ADI HMC624A | 0.1–6 GHz | 0.5 dB, 6-bit, 31.5 dB | CMOS driver + GaAs die | serial + parallel, 3–5 V | QFN-24 4×4 | C662314 / 718 / 5.35 [6] |
| ADI HMC472A | DC–3.8 GHz | 31–31.5 dB (5- or 6-bit: sources disagree) | IL < 2 dB | parallel | QFN-24 4×4 | C208585 / 392 / 3.03 [6] |
| ADI HMC542B / HMC425A | DC–4 GHz / 2.4–8 GHz | 0.5 dB, 6-bit | | | QFN | C579554 / 554 / 5.28; C494495 / 31 / 9.53 |
| Mini-Circuits DAT-31R5A-PN+ | DC–4 GHz | 0.5 dB, 6-bit, 31.5 dB | IP3 +52 dBm, VSWR 1.2:1; single-supply versions generate −V internally (spurs ≈ −140 dBm) | serial/parallel variants | QFN-20 4×4 | C20231695 / 97 / 9.57 [9] |
| Renesas F1956 | (unverified) | 7-bit | | | QFN-32 | C1511898 / 15 / 17.36 |

### C. Fixed attenuators and pads
| Option | Range | Notes | LCSC / US$ |
|---|---|---|---|
| π-pad from JLC basic/preferred 0402 resistors (thick film) | DC–~3 GHz | 3 dB: 300/22 Ω; 6 dB: 150/33 Ω; 10 dB: 100/75 Ω (basic: 22, 33, 100, 330 Ω…; preferred: 47, 51, 75, 150, 300 Ω) | ~US$0.001 each, no feeder fee |
| π-pad from E96 thin-film 0402 | to ~6 GHz | exact values (294/17.8, 150/37.4, 95.3/71.5, 60.4/249 Ω) | extended parts |
| Mini-Circuits YAT-3A+ / LAT-3+ / PAT-3+ | DC–several GHz | characterised chip attenuators (YAT = SMD-6, LAT = SOT-143, PAT = SMD-4) | C5205332 / 3.21; C7500882 / 4.39; C2683592 / 7.36 [1] |
| Coaxial SMA attenuators (Mini-Circuits VAT/BW-series, cheap marketplace) | DC–6/18 GHz | bench use; marketplace units often mismatched at GHz (anecdotal) | — |

### D. Limiters, PIN and switching diodes
| Part | Role | Notes | LCSC / stock / US$ |
|---|---|---|---|
| Mini-Circuits RLM-33-2W+ | limiter, SMD | 2 W class input (name), protects LNAs | C258934 / 66 / 17.58 |
| Skyworks SMP1320-079LF, SMP1330-005LF, SMP1340-079LF | PIN diodes | switch/attenuator/limiter building blocks (SMP1340 fast-switching) | C150854 / 2.9k / 1.25; C150870 / 5.7k / 1.22; C5365278 / 78 / 3.77 |
| "BAP64-04W", "BAR64-02V" (Jiangsu Changjing clones of NXP/Infineon types) | PIN diodes | cheap second-source lookalikes — verify capacitance/resistance before relying on datasheet of the original | C2910465 / 2.9k / 0.047; C5295579 / 8.1k / 0.028 |
| Infineon BAT15-03W | RF Schottky | detector/limiter/mixer diode | C5310874 / 12k / 0.45 |

## Worked examples
### 1. Shared antenna, 915 MHz, +30 dBm FEM, ground-station LNA path
A SE2435L FEM already contains a T/R switch ([LNA/PA parts](lna-pa-gain-block-mmics.md)); if you add an *external* switch to select between the FEM and a separate GNSS/SDR receiver, it must survive the FEM's output. With VSWR 3 after landing damage: $P_{eq}$ = +30 + 3.5 = +33.5 dBm. SKY13453 (+33 dBm IP1dB) and PE4259 (+33.5 dBm P1dB) are at their limit → harmonics and possible damage. **SKY13330** (+39 dBm) leaves 5.5 dB of margin and costs the same. Its IL of ~0.3 dB at 915 MHz (0.35 dB @ 2 GHz) adds ~0.3 dB to RX NF.

### 2. How much isolation protects the LNA?
TX +30 dBm, SKY13330 isolation ~30 dB near 1 GHz (range 35–16 dB across its band) → +0 dBm at the LNA input. A TQP3M9036 (survives more than a GNSS LNA) will compress but survive; a GNSS LNA (IP1dB −12 dBm) would be driven far beyond compression. Add: disable/bypass the LNA during TX, or add a second switch/limiter.

### 3. 6 dB pad from JLC basic parts
150 Ω shunt (preferred) + 33 Ω series (basic) + 150 Ω shunt: computed attenuation 5.67 dB, Zin 48.0 Ω, return loss −33.6 dB — good enough for a test port or an ADC input pad, zero extended-part fees. For precision (5.99–6.01 dB) use E96 150/37.4 Ω thin film.

## Practical notes
- **DC on RF ports**: most CMOS switches need DC blocks or require 0 V DC on RF pins (SKY13330 and PE42442 state no external blocking caps needed when RF pins are at 0 V DC [2][5]). Never feed a bias-tee LNA voltage through a switch unless the datasheet allows it.
- **Negative-voltage generators**: single-supply CMOS switches/DSAs make an internal negative bias with a charge pump; its clock can produce tiny spurs (DAT-31R5A single-supply versions quote ≈ −140 dBm [9]). Dual-supply or external-VSS options remove them (PE4312/PE42442 "external negative supply option" [5][8]).
- **Hot switching**: switching while RF is applied can damage non-hot-switch-rated parts; sequence TX off → switch → TX on, or pick "hot-switch" parts (ADRF5019, F2932, PE42820).
- **Layout**: 50 Ω CPWG right up to the pins, ground vias at every ground pad, keep control lines away from RF and decouple them (control-line noise couples into RF) — [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md).
- **Hand assembly**: SC-70-6 (PE4259, AS179) and SOT-23-6 (HMC544A) are iron-solderable; 1×1 mm QFN-6 (SKY13453/13351) and 0.7×1.1 mm DFN (BGS12) are machine-only.
- **Phased arrays**: DSAs with glitch-less transitions and fine steps (PE43711) are used for amplitude tapers; see [phased-array & radar parts](phased-array-and-radar-parts.md).

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| Antenna select / diversity at ≤ +20 dBm | SKY13453-385LF (JLC) or PE4259 (hand-solder) | cheap, 0.35–0.4 dB IL, deep stock |
| T/R switch for +27…+30 dBm | SKY13330-397LF | +39 dBm IP1dB, 2×2 mm, US$0.56 |
| Filter-bank / receiver input selector needing high isolation | PE42420 (SPDT) / PE42442 (SP4T) | absorptive, 50–69 dB isolation |
| AGC / array amplitude weight | PE43711 | 0.25 dB steps to 6 GHz, glitch-less |
| Cheap 0.5 dB DSA to 4 GHz | PE4312 | 4.9k in stock |
| Test-port pads | basic/preferred 0402 π-pads | free at JLC |
| LNA protection at a ground station | LNA bypass switch + RLM-33-2W+ or diode limiter | survive own TX and nearby teams |

## Parts to avoid (or use knowingly)
- **PE4314** in 50 Ω systems — it is a 75 Ω DSA [10].
- **AS193-73LF** and other Last-Time-Buy switches for new designs [2].
- **Small handset switches (SKY13453, BGS12, MXD86xx) directly after a 1 W PA** — no margin for antenna mismatch.
- **Clone PIN diodes** sold under the original part number without the original manufacturer — measure first.
- **Absorptive switches as T/R switches for high power** — the internal terminations have limited power rating; check the "terminated port" power spec.

## Common mistakes & misconceptions
- *"Isolation of 25 dB protects my LNA."* +30 dBm − 25 dB = +5 dBm: that kills many LNAs.
- *"The switch's P1dB equals its safe operating power."* Harmonics and IMD rise well below P1dB; for TX paths use P0.1dB and IIP3/harmonic specs.
- *"A switch rated to 6 GHz works at 10 MHz."* Many CMOS switches have a low-frequency limit from internal DC-block capacitors.
- *"Any 0402 resistors make a good pad at 5 GHz."* Thick-film 0402 parasitics degrade return loss above a few GHz — [resistors at RF](../04-real-components-hf/resistors-at-rf.md).

## How to simulate / verify
```python
import math
Z0 = 50
def pi_pad(A):                       # exact 50-ohm pi pad
    K = 10**(A/20); return Z0*(K+1)/(K-1), Z0*(K*K-1)/(2*K)
def pad_perf(rsh, rse):              # attenuation, Zin, return loss for a pi pad into 50 ohm
    zl = 1/(1/rsh + 1/Z0); za = rse + zl; zin = 1/(1/rsh + 1/za)
    vout = zin/(zin + Z0) * zl/za
    g = abs((zin - Z0)/(zin + Z0))
    return -20*math.log10(vout/0.5), zin, 20*math.log10(g)
print([tuple(round(x, 1) for x in pi_pad(a)) for a in (3, 6, 10, 20)])
print(pad_perf(150, 33), pad_perf(100, 75))       # JLC basic/preferred pads
P, gamma = 1.0, 0.5; print(10*math.log10(P*(1+gamma)**2*1000))   # +33.5 dBm equivalent
```
- Measure IL/isolation with a NanoVNA/LibreVNA on a test coupon (SMA edge launches, de-embed the traces — [17-test-measurement](../17-test-measurement/fixtures-and-deembedding.md), planned).

## Open questions / gaps
- IL/isolation at 433 MHz for the Skyworks parts were not read (product-page ranges only).
- HMC472A bit count/LSB: one extract says 6-bit 0.5 dB, the part is widely described as 5-bit 1 dB — check the datasheet (logged as contradiction).
- PE42820 power rating and RLM-33-2W+ limiting threshold not verified.

## Sources
1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29); JLC basic/preferred 0402 resistor list from the same snapshot. (distributor data)
2. Skyworks product pages (specification tables; fetched 2026-09-29): https://www.skyworksinc.com/Products/Switches/SKY13453-385LF, …/SKY13351-378LF, …/SKY13330-397LF, …/SKY13317-373LF, …/AS179-92LF, …/AS193-73LF. (manufacturer)
3. pSemi, *PE4259 UltraCMOS High-power SPDT RF Switch 10 MHz–3.0 GHz* product specification, https://www.psemi.com/pdf/datasheets/pe4259ds.pdf, p. 1. (datasheet)
4. pSemi, *PE42420 UltraCMOS SPDT RF Switch 20–6000 MHz*, https://www.psemi.com/pdf/datasheets/pe42420ds.pdf, p. 1. (datasheet)
5. pSemi, *PE42442 UltraCMOS SP4T RF Switch 30 MHz–6 GHz*, https://www.psemi.com/pdf/datasheets/pe42442ds.pdf, p. 1. (datasheet)
6. Analog Devices product summaries HMC624A, HMC472A, HMC849A (via search extracts; analog.com not reachable by script). (manufacturer, secondary extract)
7. pSemi, *PE43711 UltraCMOS RF Digital Step Attenuator 9 kHz–6 GHz*, https://www.psemi.com/pdf/datasheets/pe43711ds.pdf, p. 1. (datasheet)
8. pSemi, *PE4312 UltraCMOS RF Digital Step Attenuator 1 MHz–4 GHz*, https://www.psemi.com/pdf/datasheets/pe4312ds.pdf, p. 1. (datasheet)
9. Mini-Circuits, *DAT-31R5A+ Series Digital Step Attenuator*, https://www.minicircuits.com/pdfs/DAT-31R5A-PN+.pdf, p. 1. (datasheet)
10. pSemi, *PE4314 UltraCMOS RF Digital Step Attenuator 1 MHz–2.5 GHz* (75 Ω), https://www.psemi.com/pdf/datasheets/pe4314ds.pdf, p. 1. (datasheet)
11. This KB: [RF switches, attenuators and limiters (theory)](../06-rf-circuits/rf-switches-attenuators-limiters.md), [Resistors at RF](../04-real-components-hf/resistors-at-rf.md). (internal)
