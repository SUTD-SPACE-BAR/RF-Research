---
title: RF connectors and cable assemblies — SMA, SMB, MCX, MMCX, U.FL/MHF, W.FL, N, BNC, 3.5/2.92 mm; pigtails, semi-rigid and sourcing (selection guide)
domain: 18-components-parts
slug: connectors-and-cables-parts
tags: [connector, sma, rp-sma, edge-launch, smb, mcx, mmcx, u.fl, ipex, mhf1, mhf4, mhf-lk, w.fl, x.fl, n-type, bnc, 3.5mm, 2.92mm, torque, mating-cycles, rg-316, rg-174, 1.13mm, semi-rigid, hand-formable, pigtail, lcsc]
prerequisites:
  - ../03-transmission-lines-matching/coax-and-cables.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
related:
  - ../13-pcb-rf-layout-emc/connectors-and-launches.md
  - ../08-antennas/antennas-on-rockets.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../17-test-measurement/fixtures-and-deembedding.md
  - sourcing-and-eval-boards.md
  - rf-modules.md
level: intro
confidence: medium
last_updated: 2026-09-29
---

# RF connectors and cable assemblies — selection guide

## Questions this page answers
- Which RF connector should I put on a rocket flight computer, and which on the ground station and test fixtures?
- How high in frequency can SMA, SMB, MCX, MMCX, U.FL, BNC and N connectors go?
- Why did my U.FL pigtail fall off (or wear out), and what should I use in a vibrating airframe?
- What is RP-SMA, and why doesn't my Wi-Fi antenna fit my LoRa module?
- How tight should an SMA be, and do I need a torque wrench?
- Which edge-launch SMA is good to 6 GHz on a JLC 1.6 mm board, and which LCSC parts are genuine brand-name?
- Which cable (RG-316, RG-174, 1.13 mm, semi-rigid) for pigtails and short jumpers?

## TL;DR
- **Frequency limits (connector families, typical rated maxima)**: BNC ≈ 2–4 GHz; SMB ≈ 3–4 GHz; MCX / MMCX ≈ 6 GHz; U.FL / MHF1, W.FL, X.FL ≈ 6 GHz; MHF4 "up to 12 GHz" (I-PEX) [3]; N 11 GHz (precision 18 GHz); **SMA 18 GHz** (precision to 26.5 GHz); 3.5 mm 26.5 GHz; 2.92 mm (K) 40 GHz; 2.4 mm 50 GHz [1][4][5]. LCSC listings confirm: U.FL 6 GHz, Molex 73251-1150 SMA 18 GHz, Amphenol 901-10510-2 SMA 26.5 GHz, Radiall N 11 GHz, generic BNC/SMB 3 GHz [1].
- **Mating cycles**: U.FL ≈ 30 [3]; SMA/N/BNC/MCX/MMCX ≈ 500 (MIL-style ratings, typical); micro-coax connectors are *assembly* connectors, not test ports.
- **Torque**: SMA brass 0.57 N·m (5 in-lb), stainless SMA / 3.5 mm / 2.92 mm 0.9 N·m (8 in-lb), N 1.4–1.7 N·m (12–15 in-lb) [4]. Finger-tight SMA is not repeatable above ~1 GHz; a US$20–40 8 in-lb wrench is the cheapest RF instrument you will buy.
- **Flight hardware**: U.FL-class connectors are light and cheap but unlatched — use **I-PEX MHF I LK** (U.FL-intermateable, 35 N initial retention with the lock engaged) or MHF 4L LK (23 N) [6], or an SMA/MMCX with thread-locker/cable clamp. Plain U.FL retention is far lower (value not verified here); many teams add RTV/Kapton (anecdotal).
- **Board connectors in LCSC stock**: genuine Hirose **U.FL-R-SMT-1(80)** (C88374, 226k pcs, ~US$0.12) vs clones (BAT Wireless BWU.FL-IPEX1 US$0.036; Kinghelm KH-IPEX-K501-29 rated only 3 GHz); **Molex 73251-1150** SMA end-launch, 18 GHz (C841205, 2.1k, ~US$4.55); Amphenol 132255-11 (18 GHz), 901-10510-2 (26.5 GHz); TE 5-1814832-2 SMA vertical (C482015, 5.3k, ~US$1.46); cheap Chinese SMA/MMCX (BAT Wireless, Kinghelm, DreamLNK: US$0.4–0.9, "6 GHz"); Radiall N-type PCB/panel (~US$16–31) [1].
- **Cables**: see [coax and cables](../03-transmission-lines-matching/coax-and-cables.md) for loss — 1.13 mm micro-coax ≈ 1.4 / 2.0 / 2.6 dB/m at 433 / 915 / 1575 MHz; RG-316 ≈ 0.72 dB/m and RG-174 ≈ 0.64 dB/m at 433 MHz [2]. Use 1.13 mm only for ≤ 15 cm pigtails, RG-316 (PTFE, high-temperature) for internal jumpers, semi-rigid/hand-formable (0.086"/0.141") for fixtures ≥ 3 GHz, LMR-240/400 for ground-station feeders.
- **Avoid**: RP-SMA ↔ SMA mix-ups, marketplace "SMA" parts inside precision (3.5 mm/2.92 mm) instrument ports, clone micro-coax connectors rated 3 GHz used at 2.4/5.8 GHz, and adapter chains on test ports.
- **Handling** (torque technique, cleaning, U.FL cable-pull limits 2–4 N from the Hirose datasheet, weatherproofing, phase matching, cable testing): [coax and connector practicalities](coax-and-connector-practicalities.md).

## Intuition (no math)
A coaxial connector is a short piece of transmission line that must keep the same 50 Ω impedance through its body, dielectric bead, pin and the PCB transition. Above some frequency the geometry allows higher-order modes (and the pin/bead discontinuities reflect), so each family has a maximum usable frequency set by its size — smaller precision connectors go higher. Most real-world problems are not the connector's theoretical limit but: **wear** (gold plating and spring fingers of micro-coax parts wear out after tens of cycles), **mechanical retention** under vibration, **the PCB launch** (an untuned footprint can reflect more than the connector itself), and **mixing incompatible gender/polarity** (SMA vs RP-SMA).

Rules of thumb for Marcus: SMA everywhere on the ground and on test fixtures; U.FL/MHF-LK or MMCX inside the airframe for module-to-antenna runs; N-type for outdoor ground-station feeders; BNC only for low-frequency instruments (oscilloscopes).

## The math
### Level 1 — how much a connector costs you
A connector or launch with return loss $RL$ (dB) has $|\Gamma|=10^{-RL/20}$ and mismatch loss $ML=-10\log_{10}(1-|\Gamma|^2)$ ([reflections & VSWR](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)). RL 20 dB → 0.04 dB; RL 15 dB → 0.14 dB; RL 10 dB → 0.46 dB. Add ≈ 0.05–0.2 dB conductor/dielectric loss per mated pair at UHF (typical class, unverified per part). A 10 cm 1.13 mm pigtail at 915 MHz ≈ 0.2 dB [2].

### Level 2 — higher-order-mode limit
For a coaxial geometry, the first non-TEM mode (TE₁₁) appears near $f_c \approx c/[\pi\sqrt{\varepsilon_r}\,(a+b)]$ ($a$, $b$ inner/outer radii) — derived in [coax and cables](../03-transmission-lines-matching/coax-and-cables.md). SMA's PTFE-filled 4.2 mm outer conductor gives ≈ 18–22 GHz depending on version; air-dielectric 3.5 mm and 2.92 mm push to 26.5–34 and 40–44 GHz. Connector "rated to 6 GHz" normally means reflections/pin-bead design, not TE₁₁.

### Level 3 — repeatability
Contact resistance and pin gap vary with torque and wear; at 1–6 GHz a loose SMA can change S21 by tenths of a dB and S11 by several dB — larger than many effects you are trying to measure. This is why calibration kits specify torque and why micro-coax connectors are unsuitable as repeated test ports ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md), planned).

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| $ML = -10\log_{10}(1-10^{-RL/10})$ | any mismatch | RL 15 dB → 0.14 dB |
| Use connectors rated ≥ 2× your highest frequency | margin for launch/footprint | 5.8 GHz → SMA/MHF4, not SMB/BNC |
| Torque SMA 5 in-lb brass / 8 in-lb stainless; N 12–15 in-lb | coupling nuts | [4] |
| Micro-coax connectors ≈ 30 cycles | U.FL/W.FL/MHF | plan for replacement; don't use as test port |
| Pigtail loss = length × dB/m + ~0.1 dB/connector | 1.13 mm at 915 MHz | 15 cm ≈ 0.3 + 0.2 = 0.5 dB |
| Edge-launch needs footprint tuning above ~3 GHz | 1.6 mm FR-4 | follow vendor layout or simulate in openEMS |

## Comparison tables
### A. Connector families
| Family | Rated max (typ.) | Coupling | Size / mated height | Cycles (typ.) | Where to use | Watch out |
|---|---|---|---|---|---|---|
| BNC 50 Ω | 2–4 GHz (LCSC listings 3 GHz) | bayonet | large | ~500 | scopes, low-freq instruments | 75 Ω BNCs look identical |
| SMB | ~3–4 GHz (listing 3 GHz) | snap-on | medium | ~500 | legacy GNSS, automotive | snap retention only |
| MCX | ~6 GHz | snap-on | small | ~500 | GNSS/SDR modules | |
| **MMCX** | ~6 GHz | snap-on, rotates | small (3.5 mm) | ~500 | flight antennas, GNSS modules, FPV | rotates freely (strain relief!) |
| **U.FL / I-PEX MHF1** | 6 GHz | press-fit | 2.4 mm nominal mated height (1.9–2.4 mm families) [3] | **30** [3] | module-to-antenna inside enclosures | unlatched; clones vary |
| I-PEX MHF I LK | 6 GHz (as MHF1) | press-fit + lock | as U.FL | as MHF1 | **vibration** (drones, rockets) | U.FL-intermateable [6] |
| W.FL | 6 GHz | press-fit | 1.4–1.65 mm nominal [3] | (unverified) | thin products | |
| X.FL | 6 GHz | press-fit | 0.94 / 1.2 mm [3] | | very thin products | |
| I-PEX MHF4 / MHF 4L LK | up to 12 GHz [3] | press-fit (+lock) | 1.2–1.7 mm max | | M.2 Wi-Fi/5G cards, small modules | 0.81 mm cable is lossy |
| **SMA** (and RP-SMA) | 18 GHz (precision 26.5 GHz) | threaded, 1/4-36 | 6.35 mm hex nut | ~500 | ground, test, fixtures, external antennas | RP-SMA swaps pin/socket |
| N | 11 GHz (precision 18 GHz) | threaded | large | ~500 | outdoor feeders, power | heavy |
| 3.5 mm / 2.92 mm (K) | 26.5 / 40 GHz | threaded (SMA-mateable) | SMA size | ~1000 (precision) | instruments, mmWave fixtures | cheap SMA can damage them |

### B. PCB-mount connectors in LCSC stock (2026-04 snapshot [1]; US$ qty 1)
| Part | Type | Rating (listing) | LCSC / stock / US$ | Notes |
|---|---|---|---|---|
| **Hirose U.FL-R-SMT-1(80)** | U.FL receptacle | 6 GHz | C88374 / 226k / 0.115 | the original |
| Hirose U.FL-R-SMT(10) | U.FL receptacle (other reel) | 6 GHz | C434808 / 12.7k / 0.33 | |
| TE 1909763-1 / 2337019-1 | U.FL-compatible | 6 GHz | C392444 / 84k / 0.25; C434807 / 42k / 0.12 | reputable second source |
| TE/Linx CONUFL001-SMD-T | U.FL-compatible | | C22418213 / 5.2k / 0.83 | |
| BAT Wireless BWU.FL-IPEX1 / BWIPX-1-001E | IPEX Gen 1 clone | 6 GHz | C5137195 / 372k / 0.036; C496552 / 327k / 0.064 | cheapest; fine for 433/915 (anecdotal) |
| Kinghelm KH-IPEX-K501-29 | IPEX Gen 1 clone | **3 GHz** | C411563 / 205k / 0.072 | not for 5.8 GHz |
| Kinghelm KH-IPEX4-2020, BAT BWIPX-4-001E | IPEX Gen 4 (MHF4-type) | 3 GHz / 6 GHz | C530666 / 48k / 0.088; C784401 / 18k / 0.081 | |
| TE/Linx CONMHF4-SMD-G-T | MHF4-compatible | 6 GHz | C18221168 / 3.8k / 0.56 | |
| Hirose W.FL2-R-SMT-1(80), X.FL-R-SMT-1(80) | W.FL / X.FL | 6 GHz | C434820 / 59 / 2.65; C434819 / 6.5k / 0.26 | |
| **Molex 73251-1150** | SMA end-launch jack | **18 GHz** | C841205 / 2.1k / 4.55 | board-thickness-specific series (73251-1350 C3175073 also stocked — check drawing) |
| Amphenol 132255-11 | SMA board receptacle | 18 GHz | C3173700 / 7 / 8.16 | |
| Amphenol 901-10510-2 | SMA receptacle (TH) | 26.5 GHz | C3172623 / 69 / 7.29 | |
| Samtec SMA-J-P-H-ST-TH1 / -RA-TH1 | SMA straight / right-angle TH | (see DS) | C5199904 / 114 / 4.94; C6488932 / 125 / 5.82 | |
| TE 5-1814832-2 | SMA vertical TH | 6 GHz | C482015 / 5.3k / 1.46 | |
| TE/Linx CONSMA001-SMD-G-T | SMA vertical SMD | | C22418168 / 97 / 4.67 | |
| BAT BWSMA-KE-P001 / BWSMA-KWE-Z001 / BWSMA-KE-Z001 | SMA SMD vertical / TH right-angle / TH vertical | — / — / — | C496550 / 41k / 0.39; C496551 / 72k / 0.47; C496549 / 29k / 0.38 | Chinese naming: KE = PCB jack, KWE = right-angle PCB jack, KHD ≈ edge/side mount (convention; verify drawing) |
| Kinghelm KH-SMA-KWE17-G | SMA right-angle | 18 GHz (listing) | C530662 / 5.8k / 0.89 | |
| cntitle SMA-KHD9 | SMA edge-type | 6 GHz | C20415780 / 590 / 1.06 | |
| BAT BWMMCX-KE, DreamLNK DL-MMCX-KWE-90 | MMCX vertical / right-angle | 6 GHz | C5137198 / 25.6k / 0.52; C2894793 / 16.5k / 0.82 | |
| TE/Linx CONMMCX002-SMD-T | MMCX SMD | | C22438298 / 16 / 8.34 | |
| DEALON DL-SMB-JE; HanElectricity SMB-JE | SMB jack | 3 GHz | C5180390 / 38k / 0.50; C49118405 / 381 / 0.57 | |
| Kinghelm KH-BNC50-3511 | BNC right-angle | 3 GHz | C2837587 / 4.6k / 0.76 | |
| Radiall R161054000 / R161277300 | N-type | 11 GHz | C3174493 / 78 / 15.86; C3175287 / 50 / 28.34 | |
| Murata MM8130-2600RB8 / MM8030-2610RK0 | RF switch/test connectors (phone-style) | 6 / 11 GHz | C91633 / 10.6k / 0.25; C91632 / 10.3k / 0.068 | insert in-line for conducted tests; needs Murata probe cable |

### C. Cable assemblies and bulk cable
| Cable | OD | Dielectric | Loss @ 433 / 915 MHz | Use | Typical sources |
|---|---|---|---|---|---|
| 1.13 mm micro-coax | 1.13 mm | PTFE/FEP | ≈ 1.4 / 2.0 dB/m [2] | U.FL-to-SMA pigtails ≤ 15 cm | LCSC: BAT BWIPX1-SMA-1.13L100 (C784403, 3.7k, ~US$0.82), HJ-IPEX1-SMA-RG1.13 |
| 0.81 mm micro-coax | 0.81 mm | FEP | higher than 1.13 mm (unverified) | MHF4 pigtails | I-PEX, Taoglas |
| RG-316 | 2.5 mm | PTFE | ≈ 0.72 / 1.18 dB/m [2] | internal jumpers, high-temperature | LCSC: HJ-316-SMA-L150mm (C2838058, ~US$2.75), HJ-316-MMCX-L=220mm (C2693805) |
| RG-174 | 2.8 mm | PE | ≈ 0.64 / 1.0 dB/m [2] | cheap short leads (antenna tails) | everywhere |
| RG-405 (0.086") semi-rigid / hand-formable | 2.2 mm | PTFE | low | fixtures to 18+ GHz | Mini-Circuits hand-flex, Fairview/Pasternack |
| RG-402 (0.141") | 3.6 mm | PTFE | low | fixtures, bench | |
| LMR-240 / LMR-400 | 6.1 / 10.3 mm | foam PE | 1.7 / 0.87 dB per 10 m at 433 MHz [2] | ground-station feeders | Times Microwave (genuine) |

## Worked examples
### 1. Flight computer antenna path at 433 MHz
E22 module (SMA) → 20 cm RG-316 → bulkhead SMA → external antenna. Loss: 0.2 m × 0.72 dB/m = 0.14 dB + 2 mated SMA pairs (~0.1 dB each, assumed) ≈ 0.35 dB total. Replacing with a 1.13 mm U.FL pigtail of the same length: 0.28 dB + connectors ≈ 0.5 dB and a 30-cycle connector — acceptable electrically, but secure it mechanically (MHF I LK or adhesive) for launch loads.

### 2. GNSS at 1575 MHz with a long 1.13 mm pigtail
30 cm of 1.13 mm at 1575 MHz ≈ 0.78 dB [2] *before* the LNA of a passive patch → +0.78 dB system NF (≈ −0.8 dB C/N₀). Either shorten it, use RG-316 (lower loss), or use an active antenna so the loss is after the LNA ([GNSS antennas](../08-antennas/gnss-antennas.md)).

### 3. Edge-launch SMA on a JLC 1.6 mm 4-layer board at 5.8 GHz
An untuned launch with RL ≈ 12 dB costs ML ≈ 0.28 dB and, more importantly, makes S11 measurements of your circuit meaningless. Use a launch designed for the board thickness (Molex 73251 series, Amphenol/Samtec end-launch), CPWG feed, ground vias at the connector legs, and remove the reference plane under the pin where the vendor recommends — see [connectors and launches](../13-pcb-rf-layout-emc/connectors-and-launches.md) (planned) and simulate in openEMS.

## Practical notes
- **Gender and polarity**: SMA female (jack) has a socket and internal thread; SMA male (plug) has a pin and a nut. RP-SMA reverses the pin/socket (common on Wi-Fi antennas and routers). Buy one SMA gender changer kit and label everything.
- **Mixing SMA with precision 3.5/2.92 mm**: mechanically compatible, but out-of-tolerance SMA pins can damage precision ports — use a "connector saver" adapter on instruments (VNA, spectrum analyser).
- **Cleaning and inspection**: isopropyl alcohol and lint-free swabs, compressed air; inspect pin depth and plating ([Anritsu connector care, via 4]).
- **Strain relief in rockets**: clamp the cable within a few centimetres of a micro-coax connector so vibration loads the cable, not the connector; MMCX rotate freely and can back-drive under vibration.
- **Board-edge SMA soldering**: end-launch connectors need both top and bottom ground tabs soldered; JLC can hand-solder THT but end-launches are usually hand-fitted — order them loose and solder yourself, or use SMD vertical SMAs that JLC can reflow.
- **75 Ω lookalikes**: 75 Ω BNC/F/SMB exist and mate (sort of) with 50 Ω — check the part number.
- **Sourcing**: genuine Hirose/I-PEX/TE/Molex/Amphenol are available at LCSC, Mouser, Digikey, Element14 (SG); cheap Chinese connectors are fine for many hobby uses at 433/915 MHz but vary in plating, dimensions and rated frequency ([sourcing](sourcing-and-eval-boards.md)).

## Connector choice by location in a rocket system
| Location | Recommended | Rationale |
|---|---|---|
| Module ↔ antenna inside avionics bay | MHF I LK (locked) or U.FL + adhesive + cable clamp | light, compact; lock or glue against vibration [6] |
| Avionics bay bulkhead ↔ external antenna | SMA bulkhead (stainless, thread-locker) or MMCX with clamp | serviceable, robust |
| Nose-cone / fin antennas | short RG-316 with SMA or MMCX | PTFE survives heat; flexible |
| Ground-station mast | N-type + LMR-400, weatherproofed | low loss outdoors |
| Bench / VNA ports | SMA/3.5 mm with savers, torque wrench | repeatability [4] |

## Cable-assembly quality checks
- Measure S11/S21 of every new pigtail with a VNA (TDR view shows bad crimps/solder joints) ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).
- Flex test: wiggle the cable near the connector while watching S21 at your band; intermittents show up as jumps.
- Label cable length and loss at 433/915/1575 MHz on the cable (tape) so link budgets use measured numbers.

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| Flight PCB to antenna/pigtail | I-PEX MHF I LK (locked) or genuine Hirose U.FL + adhesive | light, vibration-resistant |
| Flight PCB board-edge RF port | Molex 73251-1150 (18 GHz) or TE 5-1814832-2 vertical SMA | known-good footprints |
| GNSS antenna lead | MMCX or U.FL + short 1.13 mm; active antenna | low loss before LNA |
| Ground-station feeder | N-type + LMR-400 | outdoor, low loss |
| Bench fixtures & test coupons | SMA end-launch + RG-405 hand-formable jumpers + 8 in-lb torque wrench | repeatable |
| Conducted test points on production boards | Murata MM8130 switch connector | in-line, tiny |

## Parts to avoid (or use knowingly)
- **3 GHz-rated clone IPEX parts** (e.g. KH-IPEX-K501-29) for 2.4/5.8 GHz links [1].
- **U.FL as a test port** — 30 cycles [3].
- **BNC/SMB above ~2–3 GHz**.
- **Adapter chains** (SMA→BNC→N…) in RF paths — each adds loss, reflection and wear.
- **Unknown-brand SMA inside precision instrument ports** — use savers.

## Common mistakes & misconceptions
- *"All SMAs are 18 GHz."* Cheap SMAs and many PCB launches are only characterised to 3–6 GHz (LCSC listings mostly say 6 GHz).
- *"Tighter is better."* Over-torque damages the interface; under-torque is non-repeatable. Use the torque wrench [4].
- *"U.FL is fine because it clicked."* It clicks with ~30-cycle wear life and no lock; vibration can unseat it.
- *"RG-174 is fine everywhere."* Its PE dielectric softens with soldering heat and it is lossy; use RG-316 where temperatures or lengths matter.

## How to simulate / verify
```python
import math
ml = lambda rl: -10*math.log10(1 - 10**(-rl/10))      # mismatch loss from return loss (dB)
print([round(ml(x), 2) for x in (20, 15, 12, 10)])     # 0.04, 0.14, 0.28, 0.46 dB
pig = lambda L_m, dB_per_m, n_conn=2, c=0.1: L_m*dB_per_m + n_conn*c
print(pig(0.15, 2.0), pig(0.30, 2.6, 1))                # 1.13 mm at 915 / 1575 MHz
```
- Measure connector/launch S11 with a NanoVNA/LibreVNA and TDR mode to locate the discontinuity ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)); simulate launches in openEMS ([16-simulation-tools](../16-simulation-tools/openems-workflow.md), planned).

## Open questions / gaps
- Plain U.FL retention force, W.FL/MHF4 mating-cycle ratings and per-connector insertion loss were not verified from manufacturer drawings.
- Frequency ratings of Chinese SMA/MMCX parts are LCSC listing values only.
- No vibration test data for U.FL vs MHF I LK vs MMCX on a rocket flight computer — a candidate bench test (shaker or flight).

## Sources
1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29) — connector ratings, stock, prices; RF cable assemblies. (distributor data)
2. This KB: [Coaxial lines and RF cables](../03-transmission-lines-matching/coax-and-cables.md) — cable loss table (RG-58/174/316, LMR, 1.13 mm) and TE₁₁ cutoff. (internal)
3. Hirose U.FL/W.FL/X.FL catalogues (U.FL Series 2020–2021: mated height 1.9–2.4 mm; X.FL 0.94/1.2 mm; W.FL 1.4/1.65 mm) and I-PEX MHF4 product page (mated height 1.2–1.7 mm max, "up to 12 GHz") via search extracts; Wikipedia *Hirose U.FL* (30 cycles, DC–6 GHz). https://www.hirose.com/product/en/products/W.FL/, https://www.i-pex.com/product/mhf-4. (manufacturer catalogue, secondary extract)
4. Connector torque guides: Taoglas APN-25-8-001 *SMA connector torque guide*; Times Microwave *Connector torque requirements*, https://timesmicrowave.com/connector-torque-requirements/; Anritsu *RF and microwave connector care* 10100-00031D — SMA 5/8 in-lb, N 12–15 in-lb, 3.5/2.92 mm 8 in-lb (via search extract). (application notes)
5. Wikipedia, *SMA connector*, *N connector* — frequency ratings (secondary). (encyclopedia)
6. I-PEX, *MHF I LK* and *MHF 4L LK* product pages / Future Electronics summary — lock, 35 N / 23 N initial mating force, U.FL-intermateable, https://www.i-pex.com/product/mhf-I-lk. (manufacturer, secondary extract)
