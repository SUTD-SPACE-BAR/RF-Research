---
title: LNAs, PAs, gain blocks and front-end modules — part selection guide (sub-GHz, GNSS, 2.4 GHz, microwave)
domain: 18-components-parts
slug: lna-pa-gain-block-mmics
tags: [lna, pa, gain-block, mmic, fem, qpl9547, tql9092, tqp3m9036, tqp3m9037, psa4-5043, pma-5451, pma2-43ln, pga-103, spf5189z, gali-84, era-5, mar-6, bga524, max2659, at2659, se2435l, sky66423, cc1190, rfx2401c, nrf21540, ldmos, rd01mus2, aft05ms004, gan, cgh40010, lcsc]
prerequisites:
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../07-noise-linearity/receiver-cascade-analysis.md
related:
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../05-analog-electronics/amplifier-topologies.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../08-antennas/gnss-antennas.md
  - rf-transceiver-ics.md
  - filter-parts-saw-ceramic-ltcc.md
  - rf-switches-attenuator-parts.md
  - sourcing-and-eval-boards.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# LNAs, PAs, gain blocks and front-end modules — part selection guide

## Questions this page answers
- Which LNA should I put in front of my 433/915 MHz LoRa ground station or my GNSS patch?
- Are the cheap SPF5189Z "LNA 50–4000 MHz" boards any good, and what replaced the SPF5189Z?
- What is the difference between an "LNA", a "gain block" (GALI/ERA/MAR) and a "driver amplifier"?
- How do NF, gain, OIP3 and P1dB of a candidate LNA feed into my receiver cascade?
- Which front-end module gives +27/+30 dBm at 868/915 MHz, and what does it need around it (filter, supply)?
- What do I use for 1–15 W at 433 MHz (LDMOS) or several watts at microwave (GaN)?
- Which of these can JLCPCB assemble from LCSC stock, and roughly what do they cost?

## TL;DR
- **Specs that matter for an LNA**: NF at *your* frequency, gain (enough to bury the next stage's noise, not so much that it kills linearity), OIP3/IIP3 and P1dB (pad-side blockers), maximum survivable input power, current, unconditional stability, internal matching, bypass/enable pin, package. Theory: [LNA design](../06-rf-circuits/lna-design.md), [cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md).
- **Best general sub-6 GHz LNAs in LCSC stock (2026-04 snapshot)**: **Qorvo QPL9547** (0.1–6 GHz, NF 0.3 dB, 19.5 dB, OIP3 +39.3 dBm, P1dB +22.7 dBm, 65 mA, DFN-8 2×2, C5367093, ~US$2.5); **TQP3M9036** (50 MHz–2 GHz, NF 0.45 dB, 19.8 dB, OIP3 +36 dBm — the best fit for **433/915 MHz**, C920261, ~US$2.8); **TQL9092** (0.6–4.2 GHz, NF 0.65 dB, 21 dB, C415716); **Mini-Circuits PSA4-5043+** (50 MHz–4 GHz, NF 0.75 dB @ 1 GHz, OIP3 +33.5 dBm, SOT-343, 3–5 V, C5240848, ~US$2.3) [1][5].
- **GNSS LNAs (1.559–1.615 GHz)**: Infineon **BGA524N6** (NF 0.55 dB, 19.6 dB, 2.5 mA, C6752883, ~US$0.33), Maxim **MAX2659** (NF 0.8 dB, 20.5 dB, C28043, ~US$2.2), ZHONGKEWEI **AT2659** (NF 0.8 dB, 21.5 dB, 79k in stock at ~US$0.10, C92450) [1]. Put the LNA *before* the SAW when the antenna is passive and there are no strong blockers; SAW first when there are.
- **Cheap handset LNAs for 700–1000 MHz** (usable at 868/915): Maxscend MXD8921L (NF 0.65 dB, 13.5 dB, 3.9 mA), Awinic AW15208LFDR (NF 0.6 dB, 13.5 dB) — tiny LGA/FCDFN 0.7×1.1 mm, low IIP3 (+10…+12 dBm), specs only from distributor listings (unverified) [1].
- **Gain blocks** (Darlington InGaP HBT, internally matched, needs bias resistor + choke): GALI-84+ (DC–6 GHz, P1dB +21.9 dBm, OIP3 +38 dBm), GALI-74+ (DC–1 GHz, 25 dB, NF 2.7 dB), ERA-5SM+ (DC–4 GHz, 20 dB, NF 3.5 dB), MAR-6SM+ (DC–2 GHz, NF 2.3 dB, 16 mA, low power), PGA-103+ (ultra-linear, OIP3 +45 dBm, NF 0.6 dB @ 1 GHz; Mini-Circuits' stated replacement for the obsolete **SPF5189Z**) [5]. Use them as IF/LO/driver stages, not as the first LNA.
- **Sub-GHz FEMs (PA + LNA + switch)**: **SE2435L** (860–930 MHz, +30 dBm at 4.0 V/550 mA, RX NF 2 dB, 2nd harmonic only −22 dBc → needs an external low-pass) [3]; **SKY66423-11** (860–930 MHz, +27 dBm, LNA NF 1.5 dB, Semtech SX1261 reference design) [4]; **TI CC1190** (850–950 MHz, +27 dBm, LNA NF 2.9 dB) [6]. At 433 MHz there are few FEMs (Qorvo RFFM6406, 1.5 W — lifecycle unverified); most 433 MHz watt-level radios use a discrete LDMOS stage or a finished module (EBYTE E22-400T33D).
- **2.4 GHz FEMs**: RFX2401C (75k in stock, ~US$0.82), nRF21540 (+21.5 dBm P1dB), CC2592 (+22 dBm), SKY66112-11 [1][7].
- **Watt-level discretes**: Mitsubishi **RD01MUS2** (≥ 0.8 W @ 520 MHz, 7.2 V, 14 dB, 65 % drain eff.) [8]; NXP **AFT05MS004N** (4 W class, 136–941 MHz, 7.5 V, SOT-89, C713822, ~US$5); ST PD55003 (3 W, 17 dB at 500 MHz / 12.5 V, PowerSO-10RF) [14]; GaN: Wolfspeed/MACOM **CGH40010F** (10 W class: 13 W typ. P_sat, 65 % at P_sat, 14.5 dB small-signal gain, DC–6 GHz, 28 V, ~US$107) [1][15].
- **Every one of these is an LCSC "extended" part**; Guerrilla RF, most Skyworks LNAs (SKY67150/9) and Mini-Circuits PMA-5451 were not in the in-stock snapshot [1].

## Intuition (no math)
Think of a receive chain as a relay race where each runner adds some noise and each can only carry so much. The **first** amplifier sets the noise floor: if it is quiet (low NF) and strong enough (gain), later noisy stages hardly matter. But every dB of gain in front also multiplies interfering signals, so a later stage (often the radio chip's mixer) saturates sooner — a rocket ground station on a launch field with other teams' 433 MHz transmitters is a real blocker environment. The engineering choice is therefore "just enough gain, as early as possible, as linear as possible".

Part types:
- **LNA MMICs** (pHEMT/E-pHEMT or SiGe): optimised for NF with decent linearity; often internally matched to 50 Ω (QPL9547, TQP3M903x, PSA4-5043) or needing a simple input match (SAV-541, discrete BFP/BFU transistors).
- **Gain blocks**: Darlington HBTs with resistive feedback — flat gain from near DC to GHz, well matched, very robust, but NF 2–5 dB. The "Swiss-army" amplifier for LO chains, IF strips, test fixtures.
- **Driver / PA MMICs**: higher P1dB (+27…+30 dBm) at the cost of NF and current (TQP7M9102, SKY65162).
- **FEMs**: PA + LNA + T/R switch (+ sometimes harmonic filter) co-designed for one band and one radio family — the lowest-risk way to +27…+30 dBm.
- **Power transistors**: LDMOS (VHF/UHF, 7.2–12.5 V handheld radio parts) and GaN HEMT (28–50 V, to 6 GHz+) — you design the match ([power amplifiers](../06-rf-circuits/power-amplifiers.md)).

## The math — how datasheet numbers feed the cascade
### Level 1 — noise
For stages with noise factors $F_i$ and available gains $G_i$ (linear):
$$F_{sys}=F_1+\frac{F_2-1}{G_1}+\frac{F_3-1}{G_1G_2}+\dots,\qquad NF=10\log_{10}F$$
A passive loss $L$ (dB) at room temperature has $NF=L$ and $G=-L$. So cable or filter loss **before** the LNA adds dB-for-dB to the system NF; loss **after** an LNA of gain $G_1$ is divided by $G_1$ ([Friis](../07-noise-linearity/noise-figure-and-friis.md)).

### Level 2 — linearity
Input-referred third-order intercepts combine (powers in mW, gains linear) as
$$\frac{1}{IIP3_{sys}}=\frac{1}{IIP3_1}+\frac{G_1}{IIP3_2}+\frac{G_1G_2}{IIP3_3}+\dots$$
and $IIP3 = OIP3 - G$ for one stage. Datasheet "IP3" for an LNA is almost always **OIP3**; for GNSS LNAs the small numbers (−5 dBm) are **IIP3**. The 1 dB compression point follows the same pattern approximately. The dynamic range between noise floor and compression/IM limits is traded by the gain you place in front ([nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md), [dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

### Level 3 — what the numbers do not tell you
- NF quoted at 1–2 GHz rises at low frequency for some pHEMT parts (1/f and bias network loss) and at high frequency; check the NF-vs-frequency plot at 433 MHz.
- "Internally matched" parts are matched for *gain/return loss*, not necessarily for minimum NF; the NF plot already includes that mismatch.
- A broadband LNA with 20–30 dB gain at 100 MHz and a sloppy layout will oscillate ([amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md)); datasheet "unconditionally stable" assumes the evaluation board layout and bias network.
- PA "output power" is often saturated power at a specific supply and load; harmonics, ACPR and efficiency at *your* back-off matter more ([power amplifiers](../06-rf-circuits/power-amplifiers.md)).

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| Put LNA gain $G_1$ ≥ (next-stage NF + loss after LNA) + ~10 dB | receive cascade | 15–20 dB for a mast-head LNA driving 3–5 dB of cable |
| Every dB of loss before the first LNA ≈ 1 dB of NF | room temperature | SAW 1.5–2.5 dB, T/R switch 0.3–0.6 dB, U.FL pigtail 0.2–0.5 dB |
| $IIP3_{sys}$ falls ≈ dB-for-dB with LNA gain once the chip dominates | LNA IIP3 ≫ chip IIP3 | +18 dB LNA takes −12 dBm chip IIP3 to −30 dBm system |
| Gain block bias: $R_{bias}=(V_{supply}-V_d)/I_d$, choke $X_L \gg 50\ \Omega$ | GALI/ERA/MAR/PGA | ERA-5: 4.9 V @ 65 mA → 12 V supply: 108 Ω (≥ 0.5 W) |
| PA DC power ≈ $P_{out}/PAE$ | FEM/PA | SE2435L +30 dBm: 550 mA × 4.0 V = 2.2 W (≈ 45 % overall) |
| 2nd-harmonic filter need = $P_{out}$ − dBc(2f) − limit | SRD emissions | +30 dBm, −22 dBc, −36 dBm limit → ≥ 44 dB at 2f |

## Comparison tables (LCSC data: 2026-04 snapshot [1]; US$ at qty 1)
### A. General-purpose low-noise MMICs (sub-6 GHz)
| Part | Range | NF (dB) | Gain (dB) | OIP3 / P1dB (dBm) | Supply | Package | LCSC / stock / US$ | Notes |
|---|---|---|---|---|---|---|---|---|
| **Qorvo QPL9547** | 0.1–6 GHz | 0.3 | 19.5 | +39.3 / +22.7 | 3.15–5.25 V, 65 mA | DFN-8 2×2 | C5367093 / 1.6k / 2.49 (qty 5) | bias-control/low-power mode; distributor parametrics |
| **Qorvo TQP3M9036** | 50 MHz–2 GHz | 0.45 | 19.8 | +36 / +20 | 3.3–5.25 V, 68 mA | DFN-8 2×2 | C920261 / 656 / 2.84 | internally matched, enable pin — **433/868/915 pick** |
| Qorvo TQP3M9037 | 0.7–6 GHz | 0.4 | 20 | +35 / +20 | 3–5 V, 70 mA | DFN-8 2×2 | C415712 / 1.2k / 2.36 | GNSS/2.4 GHz |
| Qorvo TQL9092 | 0.6–4.2 GHz | 0.65 | 21 | +39 / +19 | 3.3–5.25 V, 65 mA | DFN-8 2×2 | C415716 / 3.6k / 3.20 | fast enable |
| Skyworks SKY67151-396LF | 0.7–3.8 GHz | 0.5 | 19 | +38 / +19.7 | 3–5 V, 72 mA | DFN-8 2×2 | C2654170 / 36 / 9.12 | |
| **Mini-Circuits PSA4-5043+** | 0.05–4 GHz | 0.75 @ 1 GHz, 0.98 @ 2 GHz | 18.4 @ 1 GHz | +33.5 / +19.8 | 3 V 33 mA; 5 V 58 mA | SOT-343 | C5240848 / 1.1k / 2.26 | E-pHEMT, Class 1B ESD, internally matched [5] |
| Mini-Circuits PMA2-43LN+ | 1.1–4 GHz | 0.46 @ 1.9 GHz | — | +33 / +19.9 | 5 V, 51 mA | 2×2 MCLP | C2763997 / 100 / 4.07 | survives +22 dBm input for 5 min [5] |
| Mini-Circuits PMA3-83LN+ | 0.5–8 GHz | 1.3 @ 2 GHz | flat ±0.9 dB (0.5–7 GHz) | +35 / +20.7 | 5–6 V | 3×3 QFN-12 | C5200777 / 2.2k / 8.95 | wideband, low additive phase noise [5] |
| Mini-Circuits PMA-5451+ / PSA-5451+ | 0.05–6 / 0.05–4 GHz | 0.6 / 0.7 @ 0.5 GHz | 19 / 18.8 @ 1 GHz | +29 / ~+17 | 3 V, 30 mA | 3×3 MCLP / SOT-363 | not in snapshot | low-current option [5] |
| Mini-Circuits PMA-545G1+ | 0.4–2.2 GHz | 0.9 @ 0.9 GHz | 31.5 | +34 / +22 | 5 V | 3×3 | not in snapshot | high gain for 868/915 |
| Qorvo SPF5043Z | 50 MHz–4 GHz | 0.8 | 18.2 | +35 / +22.7 | 5 V, 46 mA | SOT-343 | C470902 / 1.8k / 2.39 | needs external match |
| **Mini-Circuits PGA-103+** | 0.05–4 GHz | 0.6 @ 1 GHz, 0.9 @ 2 GHz | 11 @ 2 GHz | +45 / +22.5 (5 V) | 3 or 5 V, 97 mA | SOT-89 | C3008207 / 2.3k / 2.41 | "may be used as a replacement for SPF-5189Z" [5] |
| Mini-Circuits TAMP-72LN+ | 400–700 MHz | 1.0 | — | +36 / +21.5 | module | shielded drop-in | not in snapshot | turnkey 433–470 MHz-ish LNA (check lower edge 400 MHz) [5] |

Discrete options (you design bias and match; best NF if done well): Mini-Circuits SAV-541+ (E-pHEMT, NF 0.5 dB, 17 dB @ 2 GHz, OIP3 +33 dBm; drop-in for Avago ATF-54143, C3279678, ~US$3.2) [5]; Infineon BFP420 (fT 25 GHz, C412737, ~US$0.18), BFP640 (fT 42 GHz), BFP740; NXP BFU730F (fT 55 GHz). See [BJT fundamentals](../05-analog-electronics/bjt-fundamentals-small-signal.md).

### B. GNSS L1 LNAs (1.55–1.615 GHz; "IP3" here is **input** IP3)
| Part | NF (dB) | Gain (dB) | IIP3 / IP1dB (dBm) | Supply / current | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **Infineon BGA524N6** | 0.55 | 19.6 | −9 / −16 in-band (data-sheet table; out-of-band IIP3 −5; the feature list's −4 / −12 are not the table values) | 1.5–3.3 V, 2.5 mA | TSNP-6 (0.7×1.1) | C6752883 / 3.0k / 0.33 (qty 5) |
| Maxim MAX2659 | 0.8 | 20.5 | −5 / −12 | 1.6–3.6 V, 4.1 mA | DFN-6 1×1.5 | C28043 / 135 / 2.18 (qty 5) |
| ZHONGKEWEI AT2659 / AT2659S | 0.8 | 21.5 | −5 / −14 | 1.4–3.6 V, 4.3 mA | DFN-6 / SOT-23-6 | C92450 / 79k / 0.10; C883443 / 7.5k / 0.08 |
| Willsemi WS7916 | 0.55–0.6 | 17–19 | | 1.6–3.1 V | DFN-6 1×1.5 | C506128 / 2.5k / 0.04 |
| Maxscend MXDLN14TP | 0.5 | | | | LGA-6 0.7×1.1 | C462320 / 30k / 0.22 |

The SOT-23-6 AT2659S is the only one here that is easy to hand-solder. Dual-band receivers such as the ZED-F9P (-0xB: **L1/L2** — L1 C/A, L1OF, E1, B1I plus L2C, L2OF, E5b, B2I at ≈ 1.20–1.25 GHz; only the ZED-F9P-15B is L1/L5 — u-blox product summary UBX-17005151; see [GNSS signals](../21-gnss/gnss-signals-and-codes.md)) need an LNA covering 1.16–1.3 GHz too (e.g. Maxscend MXDLN14TP lists 1.16–1.3 and 1.55–1.6 GHz bands) — or use an active antenna ([GNSS antennas](../08-antennas/gnss-antennas.md)).

### C. Handset LNAs usable at 868/915 MHz (distributor parametrics only — verify)
| Part | Range | NF | Gain | IIP3 / P1dB | Current | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|---|
| Maxscend MXD8921L | 0.6–1 GHz | 0.65 dB | 13.5 dB | +10 / +10 dBm | 3.9 mA | LGA-6 0.7×1.1 | C462324 / 10k / 0.19 |
| Awinic AW15208LFDR | 703–960 MHz | 0.6 dB | 13.5 dB | +12 / −1 dBm | 9 mA | FCDFN-6 0.7×1.1 | C5125900 / 2.9k / 0.07 |
These are cheap and low-power but have modest linearity and 0.35 mm-class pads (JLC can place them; hand rework is impractical).

### D. Gain blocks and drivers (internally matched, bias via resistor + choke)
| Part | Range | Gain | NF | P1dB / OIP3 (dBm) | Bias | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|---|
| Mini-Circuits **GALI-84+** | DC–6 GHz | 25.6 dB @ 0.1 GHz (11.8 @ 6 GHz) | 5.3 dB (LCSC listing) | +21.9 / +38 | 5.4–6.2 V, 100 mA | SOT-89 | C3193261 / 71 / 4.29 |
| Mini-Circuits GALI-74+ | DC–1 GHz | 25.1 dB @ 0.1 GHz | 2.7 dB | +19.2 / +38 | ~4.8 V, 80 mA | SOT-89 | C879860 / 249 / 4.21 |
| Mini-Circuits GALI-S66+ | DC–3 GHz | — | 2.4 dB | +3.3 / +19.1 | 3.5 V | SOT-89 | C3193274 / 495 / 2.99 |
| Mini-Circuits ERA-5SM+ | DC–4 GHz | 20.2 dB (LCSC), 17.6 dB @ 2 GHz (DS) | 3.5 dB | +18.4 / +33 | 4.9 V, 65 mA | SMD-4 | C879837 / 697 / 3.21 |
| Mini-Circuits MAR-6SM+ | DC–2 GHz | ~18–20 dB | 2.3 dB | +3.7 / +18.1 | 3.5 V, 16 mA | SMD-4 | C6587070 / 507 / 2.96 |
| Mini-Circuits GVA-63+ | 10 MHz–6 GHz | 15.9 dB | 4.6 dB | +18.9 / +34.8 | 5 V, 69 mA | SOT-89 | C3193270 / 4.1k / 2.05 |
| Mini-Circuits PHA-13HLN+ | 1 MHz–1 GHz | 20.4 dB | 1.1 dB | +28.7 / +43 | 8 V, 234 mA | SOT-89 | C2839091 / 536 / 10.33 |
| ADI ADL5611 | 30 MHz–6 GHz | 22.2 dB | 2.1 dB | +21 / +40 | 5 V, 94 mA | SOT-89 | C208262 / 904 / 5.24 |
| ADI ADL5602 | 50 MHz–4 GHz | 20.2 dB | 2.9 dB | +20.1 / +42 | 5 V, 89 mA | SOT-89 | C496494 / 1.0k / 3.20 |
| ADI HMC311SC70E | DC–8 GHz | 15 dB | 5 dB | +15 / +30 | 5 V, 74 mA | SC-70-6 | C661763 / 400 / 7.03 |
| ADI HMC788A | DC–10 GHz | 12 dB | 7 dB | +18 / — | 5 V, 76 mA | LFCSP-6 2×2 | C514405 / 378 / 13.89 |
| NXP BGA2818 | DC–2.2 GHz | 30 dB | 3.3 dB | +4 / +14 | 3.3 V, 17 mA | SOT-363 | C440700 / 2.9k / 1.39 |
| Qorvo TQP3M9028 | 14 MHz–4 GHz | 14.5 dB | 2 dB | +20.7 / +41.9 | 5 V, 85 mA | SOT-89 | C415711 / 101 / 3.36 |
| Qorvo **TQP7M9102** (driver) | 0.4–4 GHz | 17.8 dB | 3.9 dB | **+27.5** / +43.8 | 5 V, 137 mA | SOT-89 | C415714 / 312 / 3.90 |
| Skyworks SKY65162-70LF (driver) | 0.4–2.7 GHz | 23.5 dB | — | **+29** / — | 5 V, 188 mA | SOT-89 | C2654169 / 530 / 3.24 |
Values from Mini-Circuits datasheets [5] where available, otherwise LCSC parametrics [1]; gain blocks' gain falls with frequency — read the curve at your band.

### E. Front-end modules and range extenders
| Part | Band | TX power | RX NF / gain | Supply | Package | LCSC / stock / US$ | Notes |
|---|---|---|---|---|---|---|---|
| **Skyworks SE2435L** | 860–930 MHz | +30 dBm (4.0 V, 550 mA); +27 dBm 380 mA; +24 dBm 275 mA | 2 dB / 16 dB, LNA bypass | 2.0–4.8 V | QFN-24 4×4 | C4748685 / 1.5k / 1.97 | 26 dB PA gain, PAE 64 % (PA port), **2f −22 dBc**, 3f–10f −72 dBc, antenna diversity switch [3] |
| **Skyworks SKY66423-11** | 860–930 MHz | +27 dBm | 1.5 dB | 2.0–4.8 V | MCM-16 3×3 | C7316560 / 292 / 2.14 | TX bypass < 1.5 dB loss, Semtech SX1261 reference design; follow EVB layout exactly [4] |
| TI CC1190 | 850–950 MHz | +27 dBm (PAE 50 % @ 26 dBm) | 2.9 dB (incl. switch + match) | 2.0–3.7 V | VQFN-16 4×4 | C545234 / 227 / 2.30 | pairs with CC1101/CC1200/CC1310 [6] |
| Qorvo RFFM6406 | 400 MHz ISM | ~1.5 W, integrated harmonic filter | LNA with bypass | | | not in snapshot | per Qorvo summary; lifecycle unverified |
| Skyworks SKY65364-21 | 890–960 MHz | +30 dBm | 1.5 dB / 15 dB | 3.0–3.8 V | MCM-28 6×6 | — | **Last Time Buy** — avoid for new designs |
| Skyworks RFX2401C | 2.4–2.525 GHz | +22 dBm typ. P_sat; 25 dB gain; RX 12 dB, NF 2.5 dB, IP1dB −8 dBm [16] | | 2.0–3.6 V | QFN-16 3×3 | C19213 / 75k / 0.82 | common on nRF24/ESP32 "PA+LNA" boards |
| Nordic nRF21540 | 2.36–2.5 GHz | P1dB +21.5 dBm | AGC LNA | 1.7–3.6 V | QFN-16 4×4 | C5357827 / 3.0k / 2.39 | for nRF52/53/54 |
| TI CC2592 | 2.4 GHz | +22 dBm (155 mA @ 3 V) | 4.7 dB incl. switch | | QFN-16 4×4 | not checked | [7] |
| Skyworks SKY66112-11 | 2.4–2.483 GHz | (BLE/ZigBee FEM) | | 1.8–3.6 V | QFN-22 | C2654460 / 7.4k / 2.22 | |

### F. Power transistors (you design the matching networks)
| Part | Technology | Rating | Frequency | Supply | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| Mitsubishi **RD01MUS2** | Si LDMOS | P_out > 0.8 W (0.8–1.3 W), power gain G_power > 14 dB (datasheet "Gp"), η_D 65 % @ 520 MHz | VHF/UHF driver | 7.2 V | SOT-89-class | not in snapshot (Mitsubishi, Mouser) [8] |
| Mitsubishi RD06HHF1 / RD15HVF1 | Si MOSFET | 6 W @ 30 MHz / 15 W @ 175–520 MHz | HF / VHF–UHF | 12.5 V | TO-220 class | not in snapshot [9] |
| NXP **AFT05MS004N** (AFT05MS003N 3 W sibling) | LDMOS | 4 W class | 136–941 MHz | 7.5 V | SOT-89 | C713822 / 293 / 4.99 [10] |
| NXP AFM906N | LDMOS | 6 W class | 136–941 MHz | 7.5 V | DFN-16 4×6 | C3277690 / 10 / 5.09 |
| ST PD55003 | LDMOS | 3 W, 17 dB at 500 MHz [14] | to ~1 GHz | 12.5 V | PowerSO-10RF | C2970926 / 345 / 10.60 |
| Wolfspeed/MACOM **CGH40010F** | GaN HEMT | 13 W typ. P_sat, 65 %, 14.5 dB G_ss [15] | DC–6 GHz | 28 V | flange | C22423412 / 6 / 107 |

### G. Connectorised bench amplifiers (for test setups, not flight)
Mini-Circuits ZX60-P103LN+ (50–3000 MHz, NF 0.5 dB), ZX60-33LN+ (50–3000 MHz, NF 1.1 dB, 17.5 dBm), ZFL-500LN+ (0.1–500 MHz, NF 2.9 dB), ZHL-4240 (0.7–4.2 GHz, ≥ 40 dB, ≥ +28 dBm) [5] — expensive (tens to hundreds of US$) but calibrated and robust; buy direct from Mini-Circuits or authorised distributors.

## Worked examples
### 1. 433 MHz LoRa ground station: where does the LNA go?
Chain: Yagi → 10 m RG-58 (≈ 2.9 dB at 433 MHz [11]; call it 3 dB) → SX1262 receiver (assume NF 6 dB). Candidate LNA: TQP3M9036 or PSA4-5043+ (take NF 0.8 dB, gain 18 dB at 433 MHz — check the curve); SAW filter IL 1.5 dB. Using the Friis formula (script below):
| Arrangement | System NF |
|---|---|
| A: radio at end of cable, no LNA | **9.0 dB** |
| B: SAW → LNA → cable → radio | 2.7 dB |
| C: LNA → SAW → cable → radio | 1.35 dB |
| D: LNA → cable → radio (no SAW) | 1.2 dB |
Mast-head LNA recovers ~6–8 dB (≈ 2–2.5× free-space range). C beats B by 1.3 dB of NF, but B protects the LNA from out-of-band blockers (pagers, cellular at 900 MHz). On a crowded launch field, choose B or a cavity/helical filter with < 1 dB loss ([filters](filter-parts-saw-ceramic-ltcc.md), [ground station design](../15-lora-ism-radios/ground-station-design.md)).

### 2. Linearity price of that LNA
Suppose the SX1262 front end has IIP3 ≈ −12 dBm (assumption for illustration) and the LNA has OIP3 +33.5 dBm, gain 18 dB → IIP3 = +15.5 dBm. Then
$$\frac{1}{IIP3_{sys}}=\frac{1}{10^{1.55}}+\frac{10^{1.8}}{10^{-1.2}}\ \Rightarrow\ IIP3_{sys}\approx-30\ \text{dBm}$$
The LNA's own linearity is irrelevant; its **gain** moved the system IIP3 down 18 dB. Two strong carriers from another team at −35 dBm each at the antenna produce input-referred third-order products at $P_{IM3}=3P_{in}-2\,IIP3 = 3(-35)-2(-30) = -45$ dBm — far above LoRa sensitivity if they land in your channel. Remedies: less LNA gain (10–12 dB is enough to beat 3 dB of cable), a preselector filter, or an LNA with bypass for close-range operations.

### 3. GNSS with a passive patch
Passive patch → SAW (1.5 dB) → MAX2659 (0.8 dB, 20.5 dB) → module (NF 3 dB): system NF 2.33 dB. LNA first: 0.86 dB. With a strong co-located transmitter (e.g. a 915 MHz +30 dBm telemetry radio 10 cm away on the same airframe), the LNA-first choice may compress: BGA524's in-band input P1dB is only −16 dBm (data-sheet table; the feature list says −12 dBm). Rule: SAW first on a rocket with its own transmitters; LNA first on a quiet ground reference station.

### 4. +30 dBm at 915 MHz with the SE2435L
DC input 4.0 V × 550 mA = 2.2 W for 1 W RF (≈ 45 % overall). Second harmonic at 1830 MHz: +30 − 22 = +8 dBm. To meet a −36 dBm spurious limit (typical SRD/ETSI-style; check Singapore rules in 19-regulations) you need **≥ 44 dB** of rejection at 1.83 GHz after the FEM — e.g. a 7th-order LC low-pass or an LTCC low-pass (LFCN-1000+ class, [filter parts](filter-parts-saw-ceramic-ltcc.md)) plus the antenna's own selectivity. Supply: a 3.7 V Li-ion cell sags under 0.55 A bursts; SE2435L output at 3.6 V is only +24 dBm in one datasheet test condition [3] — use a 4.0–4.8 V boost or 2S + buck.

## Practical notes
- **Layout**: copy the vendor evaluation board — ground vias under the exposed pad (several per mm²), short RF traces, bias chokes with SRF above the band, decoupling at each supply pin ([PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md), [inductors at RF](../04-real-components-hf/inductors-at-rf.md)). Skyworks explicitly warns to follow the EVB Gerbers for PA match and VCC bias [4].
- **Stability**: broadband LNAs have high gain at low frequency; a shielded can, a resistive element in the bias network, and proper grounding prevent oscillation (the common failure of home-made SPF5189Z boards, anecdotal).
- **Protection**: LNAs at a ground station next to your own transmitter need a limiter or T/R switch isolation ([switches & limiters](rf-switches-attenuator-parts.md)); PMA2-43LN+ survives +22 dBm for 5 min [5], most GNSS LNAs much less.
- **Bias-tee powering**: mast-head LNAs are usually fed over the coax (bias tee). RTL-SDR Blog V3/V4 provide ~4.5 V; many LNAs need 5 V for full linearity (PSA4-5043+ runs from 3 V at reduced current).
- **Assembly**: DFN-8 2×2 and SOT-89 are JLC-friendly and hand-reworkable with hot air; 0.7×1.1 mm LGA/FCDFN parts are machine-only. SOT-89 gain blocks dissipate 0.3–0.6 W — use the tab pad with thermal vias.
- **Supply noise**: PA supply current bursts modulate other rails; give the PA its own regulator or LC filter ([power supplies for RF](../05-analog-electronics/power-supplies-for-rf-and-analog.md)).
- **First power-up of an LNA/PA board** (pad plan, current limits, what fails): [17 bring-up playbook § G](../17-test-measurement/rf-bring-up-debug-playbook.md#g-amplifier-and-rf-switch-bring-up-failure-modes-and-a-safe-test-set-up).

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| 433 MHz mast-head LNA (ground) | TQP3M9036 (or PSA4-5043+) + SAW/cavity preselector, bias-tee fed | NF ≈ 0.5–0.8 dB, OIP3 +33…+36 dBm, deep LCSC stock |
| 915/923 MHz mast-head LNA | QPL9547 or TQP3M9036; SKY66423/SE2435L if you also transmit | as above; FEM gives T/R switching |
| GNSS on flight computer (passive patch) | SAW → BGA524N6 (or AT2659) → module; or an active antenna | cheap, low current; SAW first because of on-board transmitters |
| +27…+30 dBm at 868/915 MHz | SKY66423-11 (+27) or SE2435L (+30) + LC/LTCC harmonic LPF | integrated switch & LNA, LCSC stock |
| +30 dBm at 433 MHz | EBYTE E22-400T33D module, or SX1268 + AFT05MS004N/RD01MUS2 stage + LPF | few integrated 433 MHz FEMs |
| LO / IF / test-fixture amplification | GALI-84+, ERA-5SM+, GVA-63+, ADL5611 | flat, robust, cheap |
| 2.4 GHz range extension | nRF21540 (Nordic), RFX2401C (generic) | |

## Parts to avoid (or use knowingly)
- **SPF5189Z**: obsolete RFMD/Qorvo part; "SPF5189Z LNA" boards on marketplaces vary wildly in genuine silicon, matching and shielding (forum reports; anecdotal). Use PGA-103+ or TQP3M9036 in a real design; if you buy a board, measure its NF and gain (NanoVNA for S21, an SDR noise-floor comparison for NF — [17-test-measurement](../17-test-measurement/noise-figure-measurement.md), planned).
- **SKY65364-21** and other Last-Time-Buy FEMs — no second source.
- **Gain blocks as first-stage LNAs** (NF 2–5 dB) — fine after a real LNA, wasteful at the antenna.
- **Chip-down GaN/LDMOS PAs without a load-pull or reference design** — use the vendor reference circuit; mismatch during recovery (antenna damaged) can destroy them ([power amplifiers](../06-rf-circuits/power-amplifiers.md)).
- **Unverified Chinese LNAs for flight** unless you have bench-measured them (distributor specs only).

## Common mistakes & misconceptions
- *"More LNA gain is better."* Beyond what the cascade needs, extra gain only lowers IIP3 and raises oscillation risk (example 2).
- *"The LNA's IP3 is +33 dBm so my receiver is linear."* System IIP3 is usually set by the chip after the LNA.
- *"Internally matched means no components."* You still need DC blocks, a bias choke or resistor, decoupling, and often a shunt inductor at low frequency.
- *"NF 0.3 dB"* — at the datasheet frequency on the evaluation board. Connector, trace and ESD-diode losses before it add directly.
- *"+30 dBm FEM = +30 dBm at the antenna."* Subtract the harmonic filter (0.5–1 dB), switch and connector losses; and check the legal limit.

## How to simulate / verify
```python
import math
lin = lambda d: 10**(d/10); dB = lambda x: 10*math.log10(x)
def nf_cascade(stages):          # stages: list of (NF_dB, gain_dB)
    F, G = 0.0, 1.0
    for i, (nf, g) in enumerate(stages):
        F = lin(nf) if i == 0 else F + (lin(nf) - 1)/G
        G *= lin(g)
    return dB(F)
cable, saw, lna, chip = (3, -3), (1.5, -1.5), (0.8, 18), (6, 20)
print(nf_cascade([cable, chip]), nf_cascade([saw, lna, cable, chip]), nf_cascade([lna, saw, cable, chip]))
def iip3_cascade(stages):        # (gain_dB, IIP3_dBm)
    inv, G = 0.0, 1.0
    for g, ip in stages:
        inv += G/lin(ip); G *= lin(g)
    return dB(1/inv)
print(iip3_cascade([(18, 15.5), (0, -12)]))   # ≈ -30 dBm
```
- Load vendor **S2P files** into scikit-rf or Qucs-S to check stability (K, μ) with your bias network ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- Bench: S21/S11 with a NanoVNA/LibreVNA (use an attenuator on the output); NF with a noise source + SDR Y-factor or a spectrum analyser with a preamp.

## Open questions / gaps
- Corrected 2026-10-03 (W5-E9, GAP_REGISTER G-18-01): the ZED-F9P was called "L1+L5"; the standard -0xB modules are L1/L2 (L2C/L2OF/E5b/B2I), only -15B is L1/L5.
- Corrected 2026-10-02 (W5-E9, D6 #13): the BGA524N6 row previously gave the feature-list IIP3/IP1dB (−4/−12 dBm); the electrical table gives −9/−16 dBm in-band (out-of-band IIP3 −5 dBm), matching [06 LNA design](../06-rf-circuits/lna-design.md) and the [20 LNA recipe](../20-projects-recipes/lna-design-walkthrough.md). Rule: quote the electrical-characteristics table at its stated conditions. The MAX2659/AT2659 IIP3/IP1dB cells have not been re-checked against their tables.
- NF of the broadband LNAs **at 433 MHz** was not read from the curves (datasheet pages 1 only); values quoted are at 0.5–2 GHz.
- Chinese handset LNAs (MXD8921L, AW15208, WS7916, AT2659) are characterised here only by LCSC parametric listings — bench data wanted.
- Guerrilla RF (GRF2xxx), NXP BGU7xxx, Skyworks SKY67150/67159 and Qorvo RFFM6406 specs were not verified (not in stock snapshot; vendor sites blocked).
- RFX2401C and CGH40010F were checked against their data sheets on 2026-10-13 (W5-S18b) [15][16]. The PD55003 rating (3 W / 17 dB at 500 MHz, 12.5 V) comes from ST's product-page summary only [14]; its electrical table was not read.

## Sources
1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`, plus LCSC product-page parametrics (https://www.lcsc.com/product-detail/<C-number>.html, fetched 2026-09-29) — stock, prices, NF/gain/IP3/P1dB listings. (distributor data)
2. This KB: [Receiver cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md), [Noise figure & Friis](../07-noise-linearity/noise-figure-and-friis.md). (internal)
3. Skyworks, *SE2435L: 860 to 930 MHz High-Power RF Front-End Module* datasheet, https://www.skyworksinc.com/-/media/D3C064001C9E45EDB6C26EDBFB0FD0F5.pdf, pp. 1–6 — +30 dBm, NF 2 dB, RX gain 16 dB, currents 550/380/275 mA, PAE 64 %, harmonics. (datasheet)
4. Skyworks, *SKY66423-11 860–930 MHz RF Front-End Module* product page, https://www.skyworksinc.com/en/Products/Front-end-Modules/SKY66423-11 (fetched 2026-09-29) — +27 dBm, NF 1.5 dB, 2.0–4.8 V, MCM-16, layout warning; SKY65364-21 page (LTB). (manufacturer)
5. Mini-Circuits datasheets, https://www.minicircuits.com/pdfs/<model>.pdf (fetched 2026-09-27): PSA4-5043+, PMA2-43LN+, PMA3-83LN+, PMA-5451+, PSA-5451+, PMA-545G1+, PMA3-14LN+, PGA-103+, SAV-541+, TAMP-72LN+, GALI-84+, GALI-74+, GALI-S66+, ERA-5SM+, MAR-6SM+, PSA-39+, PHA-13HLN+, ZX60-P103LN+, ZX60-33LN+, ZFL-500LN+, ZHL-4240. (datasheets)
6. Texas Instruments, *CC1190 850–950 MHz RF Front End* datasheet, https://www.ti.com/lit/ds/symlink/cc1190.pdf. (datasheet)
7. Texas Instruments, *CC2592 2.4 GHz range extender* datasheet, https://www.ti.com/lit/ds/symlink/cc2592.pdf. (datasheet)
8. Mitsubishi Electric, *RD01MUS2 Silicon RF Power MOS FET* datasheet (Feb 2017), https://www.mitsubishielectric.com/semiconductors/hf/products/datasheet/rd01mus2.pdf — P_out > 0.8 W, power gain G_power > 14 dB, 65 % @ 520 MHz, 7.2 V. (datasheet)
9. Mitsubishi Electric RD06HHF1 / RD15HVF1 datasheets (via search summary: 6 W @ 30 MHz; 15 W 175–520 MHz). (datasheet, secondary extract)
10. NXP, *AFT05MS003N 3 W CW 1.8–941 MHz 7.5 V LDMOS* and *AFT05MS004N 136–941 MHz 4 W* datasheets, https://www.nxp.com/docs/en/data-sheet/AFT05MS003N.pdf, https://www.nxp.com/docs/en/data-sheet/AFT05MS004N.pdf (titles via search; not re-read). (datasheet, secondary extract)
11. This KB: [Coaxial lines and RF cables](../03-transmission-lines-matching/coax-and-cables.md) — RG-58 2.9 dB/10 m at 433 MHz. (internal)
12. Qorvo RFFM6406 / RFFM6906 product summaries (via search results, qorvo.com blocked to direct fetch). (manufacturer, secondary extract)
13. Forum/marketplace reports on SPF5189Z LNA boards (rtl-sdr.com tag pages, AliExpress listings) — variability and oscillation anecdotes. (forum — anecdotal)
14. STMicroelectronics, *PD55003-E* product page (st.com/en/radio-frequency-transistors/pd55003-e.html) — 3 W, 17 dB at 500 MHz / 12.5 V, PowerSO-10RF (via search summary; data-sheet table not read). (manufacturer, secondary extract)
15. Cree/Wolfspeed, *CGH40010 10 W, DC–6 GHz RF power GaN HEMT*, data sheet Rev 4.0 (read with pdftotext from melcom.co.uk/uploads/cgh40010.pdf, 2026-10-13) — 13 W typ. P_sat, 65 % efficiency at P_sat, 16 dB G_ss at 2 GHz, 14 dB at 4 GHz, table G_ss 14.5 dB (12.5 min), 28 V. (datasheet)
16. Skyworks, *RFX2401C 2.4 GHz Zigbee/ISM front-end module*, data sheet 204359C, Feb 2020, Table 4 (read with pdftotext, 2026-10-13) — P_sat +22 dBm typ., small-signal gain 21.5/25/26.5 dB, 90 mA at +20 dBm, RX gain 12 dB, NF 2.5 dB, input P1dB −8 dBm. (datasheet)
