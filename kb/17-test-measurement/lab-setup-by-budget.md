---
title: RF lab setup by budget — what to buy first for a student rocketry team (≈S$300, S$2 000, S$15 000), accessories that matter, and how to buy used HP/Agilent gear safely
domain: 17-test-measurement
slug: lab-setup-by-budget
tags: [lab-setup, budget, nanovna, litevna, librevna, tinysa, siglent, rigol, rtl-sdr, hackrf, pluto, power-meter, attenuator, dummy-load, torque-wrench, cal-kit, esd, used-equipment, hp-8753, hp-8560, agilent, keysight, singapore]
prerequisites: [vna-fundamentals-calibration.md, spectrum-analyzers.md]
related: [nanovna-librevna-practical.md, rf-power-measurement.md, noise-figure-measurement.md, signal-generators-and-sources.md, sdr-as-test-equipment.md, oscilloscopes-and-probing-for-rf.md, fixtures-and-deembedding.md, rf-bring-up-debug-playbook.md, ../19-regulations-safety/lab-safety-esd-high-power.md]
level: intro
confidence: medium
last_updated: 2026-10-13
---

# RF lab setup by budget

## Questions this page answers
- What is the minimum RF test kit a student rocketry team needs for 433/915 MHz LoRa and GNSS?
- What should we buy first: VNA, spectrum analyzer, or power meter?
- What does S$2 000 or S$15 000 buy, new or used?
- Which cheap accessories (attenuators, loads, cables, torque wrench) actually matter?
- How do we buy used HP/Agilent equipment without getting a broken one?

## TL;DR
- **Buy in this order**: (1) a VNA (antennas and matching are the #1 failure point), (2) attenuators + dummy load + good cables, (3) a spectrum analyzer (TX power, harmonics, spurs, "is it transmitting"), (4) an SDR for logging/ground-station work, (5) a real power meter, (6) better VNA/SA and a noise source as the team matures.
- **≈ S$300 tier**: NanoVNA-H4 (≈ US$110 [1]) + tinySA (basic) or tinySA Ultra (≈ US$120–130 [2]) + RTL-SDR V4 + a 30 dB/2 W and a 10 dB pad, a 50 Ω load, SMA adaptors and RG-316 jumpers. Covers 433/915 MHz antenna and TX work; weak above 1.5 GHz.
- **≈ S$2 000 tier**: LiteVNA (≈ US$190 [1]) or LibreVNA (≈ US$600–700 [3]) for GNSS/2.4 GHz and true 2-port; tinySA Ultra+ or a Siglent SSA3021X Plus-class SA (≈ US$1 300–1 700 [4]); a used thermocouple/diode power meter; calibrated pad set, step attenuator, band-pass filters, near-field probes, torque wrench, ESD mat; HackRF or Pluto.
- **≈ S$15 000 tier**: a benchtop VNA to ≥ 6 GHz (new Siglent/Copper Mountain class or used HP 8753ES/ Agilent E5071-class), a 3–7.5 GHz SA with preamp and tracking generator, a calibrated noise source (346B-class), a lab signal generator with modulation, a traceable SOLT cal kit, a 12-bit scope, and shielded test boxes.
- **Accessories are not optional**: at 915 MHz a worn SMA or an un-torqued connector costs more accuracy than the difference between instruments. Budget ~15–25 % of each tier for pads, loads, cables, adaptors and a torque wrench.
- **Used gear**: HP/Agilent classics are excellent value but check the input (damaged front ends are common), stored calibration data/NVRAM batteries, and that accessories (test-port cables, cal kits, sensors) are included.

## Intuition (no math)
For a student team the goal is not a metrology lab but *never flying an untested RF chain*. The questions that matter are: does the antenna match in the rocket? Does the radio transmit the power we think, on the right frequency, without spraying harmonics? Does the ground station hear −130 dBm signals? Does the GNSS front end work with the flight computer switched on? A NanoVNA, a tinySA and an SDR answer most of those for the price of a textbook; each later purchase buys accuracy, frequency range or convenience.

## The math

### Level 1 — how to size the kit
- **Frequency coverage**: highest frequency of interest × harmonics you must check: 915 MHz ×3 = 2.75 GHz; GNSS L1 1.575 GHz; 2.4 GHz video/Wi-Fi ×2 = 4.8 GHz. A 6 GHz SA covers 915 MHz harmonics to H6.
- **Attenuation**: pads ≥ P_TX,max − P_SA,safe (1 W LoRa → tinySA Ultra ≤ 0 dBm: ≥ 30 dB, better 40 dB), first pad rated ≥ 2× CW power ([spectrum analyzers](spectrum-analyzers.md), [RF power](rf-power-measurement.md)).
- **VNA dynamic range**: must exceed the filter/isolation you want to see by ≥ 10 dB (a 50 dB-rejection SAW needs ≥ 60 dB at that frequency — the NanoVNA-H4 has only ~40 dB at 0.9–1.5 GHz [5]).

### Level 2 — what each tier can and cannot measure

| Measurement | ≈ S$300 | ≈ S$2 000 | ≈ S$15 000 |
|---|---|---|---|
| Antenna S11 433/915 MHz | ✓ (NanoVNA-H4) | ✓ | ✓ |
| GNSS/2.4 GHz antenna S11 | marginal (H4 > 1.5 GHz noisy) | ✓ (LiteVNA/LibreVNA) | ✓ |
| Filter S21 stopband | ~40–70 dB | 70–100 dB | 100+ dB |
| TX power | ±2 dB (tinySA) | ±0.1–0.2 dB (power meter) | ±0.1 dB traceable |
| Harmonics of 915 MHz | tinySA Ultra ultra-mode (±2 dB to 5.3 GHz) | same/Siglent to 2.1–3.2 GHz | full |
| Noise figure | not really (gain method ±2 dB) | gain method ±0.9 dB; Y-factor if you borrow a source | Y-factor ±0.1–0.2 dB |
| Phase noise | VCO-grade only | VCO-grade (−98 dBc/Hz floor) | phase-detector/cross-correlation or dedicated analyzer |
| Receiver sensitivity (PER) | coarse (leaky) | good with shielding + step attenuator | good + automated |
| Pattern / range tests | RTL-SDR + turntable | HackRF/Pluto, better sources | + calibrated gain standard |

## Design equations & rules of thumb

| Rule | Value | Notes |
|---|---|---|
| SA upper frequency | ≥ 3 × highest carrier (harmonics) | 915 MHz → ≥ 2.75 GHz; 2.4 GHz → ≥ 7.2 GHz for H3 |
| VNA dynamic range | ≥ (rejection/isolation to verify) + 10 dB | 50 dB SAW → ≥ 60 dB at that frequency |
| Pads before an SA | ≥ P_TX − (−10 dBm) | 2 W (33 dBm) → ≥ 43 dB; first pad ≥ 2× CW power rating |
| Accessory budget | 15–25 % of each tier | pads, loads, cables, adaptors, torque wrench |
| Accuracy anchor | one power meter or calibrated source | every other dBm number chains to it |
| Buying order | VNA → pads/loads/cables → SA → SDR → power meter → noise source | student-rocketry priorities |

## Worked examples (shopping lists)

Prices are approximate 2026 street prices in USD from the sources listed (converted at roughly S$1.30–1.35 per US$); treat them as planning numbers and check current listings.

**Tier 1 — ≈ S$300 ("every team, first week")**

| Item | Approx. price | Why |
|---|---|---|
| NanoVNA-H4 (from an authorised seller) | US$110 [1] | antennas, matching, cables, filters to ~900 MHz |
| tinySA (basic ≈ US$60–70) *or* tinySA Ultra (≈ US$120–130 [2]) | US$60–130 | TX power, frequency, spurs; Ultra reaches 6 GHz harmonics |
| RTL-SDR Blog V4 | ≈ US$35–40 | ground-station/logging, "is anything transmitting" |
| 30 dB 2 W SMA pad + 10 dB + 20 dB pads | ≈ US$20–40 | protect the tinySA; test chains |
| 50 Ω 2 W SMA load, SMA M-F "connector savers", SMA barrels, SMA–U.FL pigtails, 3× RG-316 jumpers | ≈ US$30 | the plumbing everyone forgets |
| Clip-on ferrites (#43/#61 or UHF mix) | ≈ US$10 | cable choking for antenna tests |

Total ≈ US$265–360 (≈ S$350–480); with the basic tinySA and a minimal pad set ≈ S$300–350. Skipped: power meter (use the tinySA ±2 dB), torque wrench (tighten by hand, consistently).

**Tier 2 — ≈ S$2 000 ("the team is building its own RF boards")**

| Item | Approx. price | Why |
|---|---|---|
| LiteVNA 64 (≈ US$190 [1]) — or LibreVNA (≈ US$600–700 [3]) | US$190–700 | 50 kHz–6.3 GHz / true 2-port 6 GHz, GNSS & 2.4 GHz, fixtures, TRL |
| tinySA Ultra+ (≈ US$190–210 [2]) — or Siglent SSA3021X Plus (≈ US$1 300–1 700 [4]) | US$200–1 700 | SA with LNA; the Siglent adds ±0.7 dB level, 1 Hz RBW, preamp, TG, −98 dBc/Hz |
| Used power meter + sensor (HP 437B/438A/E4418B + 8481A/8482A/E9300A) | ≈ US$200–600 used | the accuracy anchor for all other instruments |
| Step attenuator (used HP 8494/8496 or programmable) + calibrated pads | ≈ US$100–300 | receiver sensitivity tests |
| HackRF One or ADALM-Pluto | ≈ US$200–350 | signal source/recorder, pattern logging, SDR experiments |
| SAW/cavity band-pass filters 433/915 MHz, LPFs | ≈ US$50–100 | harmonic tests, ground-station front ends |
| Near-field probe set | ≈ US$20–100 | EMC/spur debugging |
| SMA torque wrench (0.9 N·m / 8 in-lb) | ≈ US$30–120 | repeatability |
| ESD mat, wrist strap | ≈ US$40 | LNAs and SDR front ends are ESD-fragile |
| Metal boxes (shielded enclosures), feed-through filters | ≈ US$50 | sensitivity/leakage control |

Two sensible builds: (A) LiteVNA + tinySA Ultra+ + used power meter + HackRF + accessories ≈ US$1 100–1 400; (B) LibreVNA + Siglent SA (clearance) ≈ US$2 000+ — exceeds the tier unless bought used or shared with a university lab.

**Tier 3 — ≈ S$15 000 ("serious lab" or shared with SUTD labs)**
- **VNA** ≥ 6 GHz with full 2-port 12-term/TRL and a real cal kit: new mid-range (Siglent SNA5000 / Copper Mountain-class) or a used Keysight/Agilent (HP 8753ES, E5071B/C, E5061B) — check test-port cables and cal kits are included.
- **SA** 3–7.5 GHz with preamp and tracking generator (Siglent SSA3000X Plus 3.2/7.5 GHz class, or used Agilent E4402B/E4405B/N9320B, HP 8560E/EC/8594E) plus a noise-figure/phase-noise option if affordable.
- **Noise source** 346A/B-class with ENR table (used), and a low-NF preamp for Y-factor with the SA or SDRangel.
- **Signal generator** with LoRa-capable arbitrary waveform (or an SDR with calibration) and −127 dBm-class calibrated output (used ESG/8648, or new Siglent SSG).
- **Power meter** with a thermocouple and a wide-range diode sensor; a peak/burst sensor for packet measurements.
- **12-bit oscilloscope** (Siglent SDS2000X HD / Rigol DHO900-class) with a current probe.
- **Traceable SOLT cal kit** (3.5 mm/SMA-compatible) and a verification kit (attenuators, a mismatch standard).
- **Shielded box** for conducted/over-the-air receiver tests, programmable step attenuator, a GPSDO 10 MHz reference for all instruments.

## Practical notes
- **Buy from authorised sellers**: counterfeit NanoVNAs ("2.7/3 GHz NanoVNA-H") and clones with poor parts are common [5], [6]; the NanoVNA, NanoRFE and Zeenko sites list genuine sellers.
- **Used-equipment checklist**: power-on self-test and error log; internal calibrator (e.g. 50 MHz/−10 dBm on HP/Agilent SAs) reads correctly; noise floor matches the spec at a few frequencies (a damaged first mixer shows a raised floor or missing band); input attenuator clicks through all steps without jumps; for VNAs, measure your own load/short/open after cal — check all four S-parameters and the dynamic range with two loads; ask for the cal-kit definitions and the service manual. Instruments with battery-backed RAM (e.g. some HP 8560/8753 series) can lose correction constants when the battery dies — ask whether it was replaced and whether the data were backed up. Budget for shipping (20–40 kg instruments) and a check against a known source on arrival.
- **Singapore specifics**: mains 230 V/50 Hz with BS 1363 plugs — most HP/Agilent gear has a universal or selectable supply; check the voltage selector before powering. Sources: local distributors, university surplus, SG online marketplaces; importing from the US/EU adds GST and freight.
- **EMC pre-compliance kit** (LISN, transient limiter, current probe, near-field probes): see the budget kit and prices in [13 EMC § pre-compliance](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#conducted-and-radiated-pre-compliance).
- **Accessory discipline**: label pads with measured loss (433/915/1575/2450 MHz), keep adaptors in a box with caps, never mate a damaged SMA, keep a "gold" set of cables used only for calibration.
- **Share**: many measurements (NF, phase noise, antenna chambers) are best done by borrowing university lab time — book it with a prepared test plan (pre-registration of what will be measured and pass/fail criteria).
- **ESD**: LNAs, SDR inputs and VNA ports are the most frequent casualties — ground yourself and discharge cables before connecting ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).

## Common mistakes & misconceptions
- **Buying an SA first and no VNA** — most RF problems in student rockets are antenna/matching/cable problems.
- **Spending everything on instruments and nothing on pads, loads and cables.**
- **Buying a "3 GHz NanoVNA-H"** — likely a fake.
- **Assuming a used instrument works because it powers on** — verify the RF path with a known source.
- **Forgetting that accuracy chains to one trusted reference** (a power meter or calibrated source); without it every dBm number is ±2 dB.

## How to simulate / verify
- Not a calculation page. Verify a new kit in its first week: VNA — measure a 20 dB pad (S21 = −20.0 ± 0.2 dB), a spare load (RL ≥ 35–40 dB) and a 1 m cable (delay/v_f consistent); SA — read a known −30 dBm tone at several RBWs (level constant) and check the floor falls 10 dB per decade of RBW; SDR — the 10 dB pad linearity test; power meter — zero, then compare with the SA at one level. Record the results as the kit's baseline.

## Open questions / gaps
- Prices are indicative (listings seen 2026-09: R&L, SeeSii, Siglent, retailers); used-equipment prices are general-knowledge ranges, not sourced.
- Local (Singapore) distributor pricing and university-lab access terms were not researched.

## Sources
1. R&L Electronics listings (NanoVNA-H4 US$109.95, LiteVNA64 US$189.95, LibreVNA US$599.95), accessed via search 2026-09. (retailer)
2. rtl-sdr.com, "tinySA Ultra reviews … for $120" and SeeSii tinySA Ultra+ ZS406 listing (~US$187–210). (blog/retailer)
3. SeeSii LibreVNA 2.0 listing (~US$699) and R&L LibreVNA listing. (retailer)
4. Siglent NA store (SSA3021X Plus clearance US$1 299.75, list US$1 733) and Saelig listing. (vendor/retailer)
5. nanovna.com — warnings about fake "2.7 GHz NanoVNA plus" units; dynamic-range bands of NanoVNA-H/H4. (community/vendor; read)
6. NanoRFE, "Authentic NanoVNA vs. clone" guidance on nanorfe.com. (vendor; read)
7. This KB: [VNA](vna-fundamentals-calibration.md), [NanoVNA practical](nanovna-librevna-practical.md), [spectrum analyzers](spectrum-analyzers.md), [RF power](rf-power-measurement.md). (internal)
