---
title: RF passives and support parts — C0G capacitors, RF inductors, pads, terminations, DC blocks, bias tees, ESD, low-noise LDOs, zero-drift op-amps, ferrites, shields, couplers, splitters, circulators and DBM spur tables (JLC/LCSC stock)
domain: 18-components-parts
slug: rf-passives-and-support-parts
tags: [c0g, np0, mlcc, high-q-capacitor, rf-inductor, wirewound, multilayer, air-core, micro-spring, srf, q-factor, attenuator-pad, termination, dc-block, bias-tee, esd, low-capacitance-tvs, ldo, psrr, zero-drift, op-amp, ferrite, shield-can, shielding-clip, directional-coupler, power-splitter, hybrid, circulator, isolator, double-balanced-mixer, spur-table, jlcpcb, lcsc, basic-parts, preferred-extended]
prerequisites: [../04-real-components-hf/capacitors-at-rf-mlcc.md, ../04-real-components-hf/inductors-at-rf.md, sourcing-and-eval-boards.md]
related: [../04-real-components-hf/resistors-at-rf.md, ../04-real-components-hf/ferrites-and-beads.md, ../05-analog-electronics/power-supplies-for-rf-and-analog.md, ../05-analog-electronics/op-amps-real-limitations.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md, ../06-rf-circuits/circulators-isolators.md, ../06-rf-circuits/couplers-dividers-combiners.md, ../06-rf-circuits/mixers.md, rf-switches-attenuator-parts.md, filter-parts-saw-ceramic-ltcc.md, connectors-and-cables-parts.md, mixers-plls-vcos-parts.md]
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# RF passives and support parts

## Questions this page answers
- Which C0G capacitors and RF inductors can JLCPCB actually place, and which are "basic" or "preferred"?
- Is a multilayer chip inductor good enough for my 433 MHz filter, or do I need a wire-wound or air-core one?
- What value should a DC block be at 433 MHz, 915 MHz or GNSS L1?
- How do I make a 50 Ω termination or a bias tee from stocked parts?
- Which ESD diode can I put on an antenna port without wrecking the match?
- Which LDO is quiet enough for a VCO or LNA supply, and which op-amp has no drift for a detector or sensor?
- Can I buy shield cans, ferrite toroids, couplers or splitters through JLC?
- Where do I get a 433 MHz or 915 MHz circulator or isolator, and how big is it?
- What is a mixer spur table, and how do I read the Mini-Circuits ADE-1 one?

## TL;DR
- **JLC "basic" RF passives are thin.** In the 2026-09-14 jlcparts snapshot only 350 basic and 987 preferred-extended parts exist. **Basic C0G in 0402 covers only 10, 12, 15, 18, 20, 22, 33, 47 and 100 pF.** The small values 1, 1.5, 2.2, 2.7, 3.3, 4.7, 6 and 6.8 pF, plus 27, 30, 68 and 330 pF, are *preferred* (no extended fee on economic PCBA). **No RF inductor is basic.** Sunlord SDCL1005 3.9, 10 and 15 nH and SDCL1608 68 nH are preferred; everything else is extended.
- **Fees:** on JLC *economic* PCBA each unique extended line costs US$3 and basic or preferred lines cost nothing ([sourcing](sourcing-and-eval-boards.md)). On *standard* PCBA every unique line pays the same loading fee, so basic versus extended stops mattering. There, choose on specification, then reuse lines already on the BOM.
- **Inductor choice at UHF:** multilayer chip inductors (Murata LQG15HS, Sunlord SDCL, TDK MLG) are rated about Q 8 at 100 MHz, which is about Q 17 at 434 MHz. Wire-wound ceramic types (Murata LQW15AN/LQW18AN, Sunlord SDWL, Abracon AISC, Coilcraft 0402CS/0402HP) reach about Q 25–70. Air-core springs (Coilcraft 0906/1606, Q ≥ 100 at 800 MHz) sit in single-digit stock at LCSC. **LCSC files the Murata LQW parts under "Power Inductors"**, so a parametric search in "Inductors (SMD)" misses them.
- **Filter lesson (script):** a 3-pole Butterworth with f_c = 500 MHz loses **1.55 dB at 434 MHz even with ideal parts** (f/f_c = 0.87). Use a 5-pole 0.1 dB Chebyshev instead: E12 values 6.8 pF / 22 nH / 12 pF / 22 nH / 6.8 pF with wire-wound Q 40 give **0.53 dB IL, 21 dB RL, 29 dB rejection at 2f and 53 dB at 3f**.
- **DC block:** choose C near series resonance with its ESL. For an 0402 (0.4 nH) that is 336 pF at 434 MHz, 76 pF at 915 MHz, **25 pF at L1** and 10 pF at 2.45 GHz. A 100 pF block loses < 0.02 dB anywhere from 434 MHz to 2.45 GHz.
- **ESD on RF ports:** 0.4 pF (PESD5V0F1BL) costs 31 dB RL at 434 MHz and 20 dB at L1. **An 80 pF general-purpose TVS (ESD9X3.3) inserts 15 dB of loss at 434 MHz.**
- **Low-noise rails:** TPS7A2033 (10 µVrms, US$0.21) or LP5907 for LNA/MCU-radio rails. Use LT3042/LT3045 (0.8 µVrms, ≈ 76–79 dB PSRR at 1 MHz, about US$6–7) for VCOs and PLLs fed from a switcher. **Zero-drift amplifiers:** OPA333 (2 µV), ADA4528-1, OPA388, 3PEAK TP5551.
- **Not at JLC at all:** circulators and isolators, genuine Fair-Rite toroids and ready-made shield cans in volume. UHF ferrite circulators come from specialist vendors and are 10–36 mm parts: 902–928 MHz SMT units have 0.35–0.5 dB IL and 16–25 dB isolation, 400–470 MHz units are drop-in or Ø36 mm SMT.

## Intuition (no math)
At UHF the "boring" parts set most of the loss and most of the surprises. A capacitor is a capacitor plus a small series inductance, so above its series resonance it behaves as an inductor. An inductor is an inductor plus a small parallel capacitance, so above its self-resonance it behaves as a capacitor. The losses of both (their Q) decide how much signal a filter or matching network eats. Everything that hangs on an RF line adds a little admittance and spoils the match: an ESD diode, a bias choke, a test pad. The work is therefore mostly bookkeeping: know each part's parasitic, keep it small compared with 50 Ω at the frequency of interest, and stay below the self-resonance (or use it deliberately).

The procurement layer adds a second set of rules. JLC can only place what it stocks. Its cheapest tiers ("basic" and "preferred") were chosen for digital boards, not RF. LCSC's category labels are sometimes wrong, and clone vendors copy part numbers without copying performance.

## The math

### Level 1 — the parasitic rules
- Capacitor: $Z_C=\frac{1}{j\omega C}+j\omega L_{ESL}+R_{ESR}$; series resonance $f_s=1/(2\pi\sqrt{L_{ESL}C})$. Above $f_s$ the part is inductive. 0402 mounted ESL ≈ 0.4 nH (canonical value).
- Inductor: $Z_L\approx(R+j\omega L)\parallel\frac{1}{j\omega C_p}$; SRF $f_{SR}=1/(2\pi\sqrt{LC_p})$; $L_{eff}\approx L/(1-(f/f_{SR})^2)$ below SRF. Use matching and filter inductors at ≤ ½–⅓ of SRF ([inductors at RF](../04-real-components-hf/inductors-at-rf.md)).
- A shunt admittance $Y$ on a $Z_0$ line: $\Gamma=-YZ_0/(2+YZ_0)$, $S_{21}=2/(2+YZ_0)$. A shunt capacitor needs $\omega CZ_0\ll1$, and a shunt choke needs $|Z|\gg Z_0$.
- A series impedance $Z$: $S_{21}=2Z_0/(2Z_0+Z)$, so a series DC block needs $|Z|\ll Z_0$.

### Level 2 — filter loss from finite Q
For a band-pass ladder of fractional bandwidth $w$, Cohn's estimate of the dissipation loss at band centre is $4.343\sum_k g_k/(wQ_k)$ dB, where $g_k$ are the prototype values. A low-pass behaves like $w=1$ at low frequency, and its loss grows towards the band edge, where the group delay peaks ([RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)). The inductors dominate: C0G capacitors have Q in the hundreds and chip inductors only 15–70 at UHF. In the 5-pole example below, finite Q accounts for 0.50 dB of the 0.53 dB insertion loss (script §1). Moving from multilayer (Q ≈ 17) to wire-wound (Q ≈ 40) inductors cuts that part of the loss by about 2.4×.

### Level 3 — mixer spur tables
A double-balanced mixer driven hard by the LO acts as a polarity switch. Its output contains every product $|mf_{RF}\pm nf_{LO}|$. For an ideal square-wave switch the odd LO harmonics are weighted $1/n$, so the 1×3 response sits $20\log3=9.5$ dB below the 1×1 IF. Even-order products are suppressed only as well as the diodes and baluns are balanced. An $m$-th order RF product grows as $m$ times the RF drive in dB while the IF grows as 1 times, so **its rejection relative to the IF changes by $(m-1)$ dB per dB of RF level**. That rule lets you scale a vendor table measured at −14 dBm to your own signal levels ([mixers](../06-rf-circuits/mixers.md)). The Mini-Circuits ADE-1 table (below) follows both rules: 1×3 = 11 dBc (ideal 9.5), and 2×1 changes by 8 dB and 3×3 by 18 dB per 10 dB of drive (rule: 10 and 20).

## Design equations & rules of thumb
| Rule | Value | Source |
|---|---|---|
| DC-block value | C at series resonance with ESL: $C=1/((2\pi f)^2L_{ESL})$ → 336 / 76 / 25 / 10 pF at 434 / 915 / 1575 / 2450 MHz (0402, 0.4 nH) | script §5 |
| Any C0G ≥ 100 pF as DC block | < 0.02 dB loss from 434 MHz to 2.45 GHz | script §5 |
| Shunt ESD capacitance | 0.4 pF: RL 31 / 20 / 16 dB at 434 / 1575 / 2450 MHz; 0.2 pF: 37 / 26 / 22 dB | script §3 |
| Multilayer inductor Q at UHF | ≈ Q(100 MHz)·√(f/100 MHz) → ≈ 17 at 434 MHz, 24 at 900 MHz (datasheet LQG15HS10N: 29) | script §2 |
| Stay below SRF | L within 10–30 % of nominal at ≤ ½–⅓ SRF | [04 inductors](../04-real-components-hf/inductors-at-rf.md) |
| Chip termination | 49.9 Ω 0402 + 0.3 nH via: RL 34 / 28 / 23 / 19 dB at 434 / 915 / 1575 / 2450 MHz; 2 × 100 Ω parallel ≈ +3 dB better | script §4, [04 resistors](../04-real-components-hf/resistors-at-rf.md) |
| Bias-tee choke at L1 | 47 nH, SRF 2.9 GHz: \|Z\| ≈ 660 Ω, through-loss 0.02 dB | script §6 |
| Isolator protection | PA sees \|Γ\| ≤ port RL + isolation + load RL: 20/20 dB + 49.9 Ω load → VSWR 1.56; load must absorb the full PA power | script §7, [06 circulators](../06-rf-circuits/circulators-isolators.md) |
| Spur-table scaling | rejection of an $m$×$n$ product changes $(m-1)$ dB per dB of RF drive | script §8 |

## Worked examples

### 1 — A harmonic filter for a 434.125 MHz transmitter, from JLC-stocked parts
*First attempt (a mistake I made in planning, kept on purpose):* a 3-pole Butterworth π (C–L–C) with f_c = 500 MHz has ideal values C = 1/(2πf_cZ₀) = 6.37 pF and L = 2Z₀/(2πf_c) = 31.8 nH. Its response is $|S_{21}|^2=1/(1+(f/f_c)^6)$, so at 434 MHz (f/f_c = 0.868) it **loses 1.55 dB with perfect parts** and only 4.5–5 dB of return loss. With 6.8 pF C0G and a 33 nH wire-wound inductor at Q 40 the loss is 2.24 dB, and the rejection is 17 dB at 2f and 30 dB at 3f. A 3-pole Butterworth must have f_c well above the carrier.

*Better:* a 5-pole 0.1 dB-ripple Chebyshev with its ripple band edge at 500 MHz. Prototype g = 1.1468, 1.3712, 1.9750, 1.3712, 1.1468 gives 7.30 pF, 21.8 nH, 12.6 pF, 21.8 nH, 7.30 pF. In E12 values: **6.8 pF (C1576, preferred) – 22 nH (LQW15AN22NG00D, C86129) – 12 pF (C1547, basic) – 22 nH – 6.8 pF.** With Q_L = 40, Q_C = 400 and 0.4 nH ESL: **IL 0.53 dB, RL 21.1 dB, rejection 29.4 dB at 868.25 MHz and 53.3 dB at 1302.4 MHz** (script §1). With multilayer inductors (Q ≈ 17) the finite-Q part scales by about 40/17, giving roughly 1.2 dB in total. JLC economic-PCBA cost: one extended line (the LQW inductor, US$3), with the C0Gs free. The SAW and LTCC alternatives are on [filter parts](filter-parts-saw-ceramic-ltcc.md); pick by the harmonic level the regulator requires ([harmonic filter sizing](filter-parts-saw-ceramic-ltcc.md#worked-examples)).

*Side effect of SRF:* if a 33 nH inductor's SRF falls near 3f (1.3 GHz), the series arm resonates and *rejection at 3f jumps* (63 dB in the sweep). Just above SRF, though, the arm turns capacitive and rejection falls back to about 30–40 dB. Datasheet SRFs are fixture-dependent, so do not rely on this trap.

### 2 — Bias tee for an active GNSS antenna
DC feed through a 47 nH wire-wound choke (Sunlord SDWL1005C47NGSTF, C95948, SRF 2.9 GHz): at 1575.42 MHz $|Z|$ ≈ 660 Ω and the shunt loss is 0.02 dB. The RF path needs a DC block of about 22–33 pF (series-resonant at L1 with 0402 ESL), e.g. the basic 22 pF C1555 or 33 pF C1562. Add a 10–100 Ω series resistor and a 100 nF decoupler on the DC side, plus current limiting. The u-blox reference designs and the [antenna supervisor notes](../21-gnss/gnss-receiver-integration-u-blox.md) cover short-circuit detection. A connectorised Mini-Circuits TCBT-2R5G+ (C5189220, 113 in stock, US$12.43) is for the bench, not for the flight board.

### 3 — ESD on the 433 MHz antenna port
PESD5V0F1BL (Nexperia C45961, 0.4 pF, US$0.10, 62k in stock) costs 31 dB of return loss and 0.003 dB of insertion loss at 434 MHz, and 20 dB RL at L1. The UMW-branded lookalike (C3001950, US$0.026) lists the same 0.4 pF; verify it on a VNA before trusting it at GHz. A general-purpose ESD9X3.3 (80 pF) on the same port puts **14.9 dB of loss** at 434 MHz, which is a classic "my range dropped" bug ([low-C TVS](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)).

### 4 — Reading the ADE-1 spur table for a 433.92 MHz superhet (IF 10.7 MHz, low-side LO 423.22 MHz)
Mini-Circuits publishes the "harmonics table" at RF −14 dBm and −4 dBm with LO +7 dBm. Rows are the RF harmonic order m, columns the LO order n, and entries are dBc below the IF. The interferer frequencies that produce 10.7 MHz are: the image (1,1) at 412.52 MHz, with no mixer rejection, so a preselector is needed; the half-IF (2,2) responses at 428.57 and 417.87 MHz, **79 dBc** at −14 dBm; and the (3,3) responses at 426.79 and 419.65 MHz, **62 dBc** (script §8). Because the (2,2) response is second order in RF, its rejection improves 1 dB per dB of lower input, so at −34 dBm it is about 99 dBc. The image and the half-IF responses are what the preselector has to remove. Table values (dBc): (1,2) 25, (1,3) 11, (1,4) 38, (1,5) 22, (2,1) 51, (2,3) 52, (3,1) 63 at −14 dBm.

### 5 — Isolator for a 2 W 915 MHz PA (US/IREC use)
With a SKYFR-001770-class SMT circulator (902–928 MHz, 0.35 dB IL, 20 dB isolation, 20 dB RL; web listing) and a 49.9 Ω load, the PA sees at most |Γ| = 0.10 + 0.10 + 0.018 = 0.22 (VSWR 1.56) with the antenna open or shorted. The load then absorbs about 1.85 W, so a 62.5 mW 0402 resistor will fail. Use the circulator vendor's isolator version with an integrated termination, or a rated 2–5 W chip termination. The 433 MHz equivalents are 25–36 mm parts ([06 Example 1](../06-rf-circuits/circulators-isolators.md#example-1--protecting-a-2-w-433-mhz-pa-from-a-broken-antenna)). On a small rocket, mind the magnet near the magnetometer.

## Practical notes

### A. Capacitors (C0G/NP0) — stock on 2026-10-13 (live refresh) unless marked; B = basic, P = preferred, E = extended (flags from the 2026-09-14 snapshot)
| Part | Value / rating | Size | Tier | LCSC / stock / US$ (qty 1) | Use |
|---|---|---|---|---|---|
| FH 0402CG101J500NT | 100 pF 50 V ±5 % | 0402 | B | C1546 / 4.08M / 0.0042 | DC block 434 MHz–2.4 GHz, VCO tank |
| FH 0402CG220J500NT / 330J | 22 / 33 pF | 0402 | B | C1555 / 2.07M / 0.0042; C1562 | GNSS DC block, crystal loads |
| Samsung CL05C100JB5NNNC | 10 pF | 0402 | B | C32949 / 1.52M / 0.0057 | 2.4 GHz DC block |
| FH 0402CG1R0C / 2R2C / 3R3C / 4R7C / 6R8C | 1 / 2.2 / 3.3 / 4.7 / 6.8 pF ±0.25 pF | 0402 | P | C1550 / 886k / 0.0029; C1559; C1565; C1569; C1576 / 200k / 0.0046 | matching, filters (no extended fee) |
| Samsung CL05C680JB5NNNC | 68 pF | 0402 | P | C14441 / 121k / 0.0081 | |
| Murata GJM1555C1H series (high-Q) | 0.3–3.3 pF, ±0.05–0.1 pF | 0402 | E | C76906 (3.3 pF) / 211k / 0.028; C161316 (2 pF); C88891 (3 pF) | tight-tolerance matching, PA tuning |
| Murata GRM1555C1H100FA01D | 10 pF ±1 % | 0402 | E | C161520 / 112k / 0.014 | precision filters |
| Murata GQM1555C2D100JB01D | 10 pF 200 V high-Q | 0402 | E | C2286335 / 3.7k / 0.141 | PA output networks |
| ATC (KYOCERA AVX) 600S3R9BT250XT | 3.9 pF 250 V, very low ESR | 0603 | E | C3849659 / 300 / 1.27 | watt-level matching |

The basic and preferred C0G list above is the *complete* 0402 C0G set in the snapshot. Values such as 8.2, 39, 56 and 82 pF in 0402 are extended, and for 0603 the basic C0G list starts at 10 pF (with 3, 4.7, 6, 6.8 and 8.2 pF preferred). Physics and ESR/ESL: [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md).

### B. Inductors
| Family (technology) | Q at UHF | Examples (LCSC / stock / US$) | Notes |
|---|---|---|---|
| Sunlord SDCL1005 (multilayer) | 8 @ 100 MHz → ≈ 17 @ 434 MHz | **P:** 3.9 nH C14033 / 79k / 0.0046; 10 nH C27147 / 75k / 0.0055; 15 nH C27143 / 217k / 0.0061. E: 1 nH C57117 | free on economic PCBA; fine for chokes and non-critical matching |
| Sunlord SDCL1608 (multilayer) | 12 @ 100 MHz | **P:** 68 nH C13415 / 201k / 0.020 (SRF 900 MHz) | do not use at 915 MHz |
| Murata LQG15HS (multilayer) | 8 @ 100 MHz (29 @ 900 MHz for 10 nH) | 2.2 nH C86061 / 115k / 0.023; 6.8 nH C77110 / 360k / 0.018; 27 nH C12669 (SRF 1.7 GHz) / 135k / 0.019 | 2.4 GHz matching |
| TDK MLG1005S (multilayer) | 7–8 @ 100 MHz | 2.0 nH C76769; 3.9 nH C76775; AEC-Q200 variants (…TD25) | automotive-grade option |
| Murata LQW15AN (wire-wound, 0402) | ≈ 25–40 @ 434 MHz (estimate) | 3.9 nH C98062 / 23k / 0.064; 8.2 nH C84404; 12 nH C86128; 15 nH C98055; 18 nH C91622 / 48k / 0.050; 22 nH C86129 / 31k / 0.049; **33 nH C113114 / 91k / 0.044**; 47 nH C22334 / 65k / 0.064 | **filed under "Power Inductors" at LCSC**; "…80D" variants (e.g. 22 nH C524641) carry ~2× current |
| Murata LQW18AN (wire-wound, 0603) | higher than 0402 | 10 nH C86131 / 82k / 0.048; 18 nH C86133; 100 nH C98088 / 47k / 0.047 | 433 MHz PA matching |
| Sunlord SDWL1005/1608 (wire-wound) | 25 @ 250 MHz | 5.8 nH C408659; 27 nH C408697; 47 nH C95948 (SRF 2.9 GHz); 0603 47 nH C60035 (36 @ 200 MHz) | cheaper wire-wound, small stock |
| Abracon AISC-0402 (wire-wound) | 21–26 @ 250 MHz | 10 nH C186805 / 8.1k / 0.20; 9 nH C186804 | |
| Coilcraft 0402CS / 0402HP / 0603CS (wire-wound) | 0402HP-18N: 58 @ 900 MHz | 0402CS-20N C40284483 / 99 / 0.94; 0402HP-18N C39084920 / 91 / 0.99; 0603CS-68N C19191685 | the reference parts; LCSC stock is small and often from re-sellers |
| Coilcraft Micro Spring 0906 / 1606 (air core) | **Q ≥ 100 @ 800 MHz**, TCL +5…+70 ppm/°C | 0906-5 (5.40 nH) C20416973 / 7 / 1.09; 1606-6 (5.60 nH) C20623555 / 2 / 1.20; values 0906-2/3/4/5 = 1.65/2.55/3.85/5.40 nH, 1606-6…10 = 5.60–12.55 nH [4] | buy at Coilcraft/DigiKey; hand-place |
| Coilcraft Mini Spring A02T (air core) | Q ≥ 140 @ 150 MHz | 5.0 nH, 4 A, C20416981 / 6 / 1.85 [4] | VHF/UHF PA output |
| Sunlord SDFL (multilayer µH) | — | **B:** 10 µH 0805 C1046 / 299k / 0.051; 10 µH 0603 C1035 / 762k / 0.028; **P:** 4.7 µH C1034 | the only basic inductors; 15 mA rating: bias feeds for µA loads only |

### C. Resistive parts: pads and terminations
- **Terminations:** 49.9 Ω 0402 thick film **C25120 (basic, 1.19M, US$0.0027)** or 51 Ω C25125 (preferred). Two 100 Ω in parallel at the pad, with the ground via inside the pad, give about 3 dB better return loss. Power: 62.5 mW for 0402, so a termination that must absorb a PA needs a rated part.
- **Pads:** π-pads from basic or preferred resistors, and characterised chip attenuators: [rf-switches-attenuator-parts §C](rf-switches-attenuator-parts.md#c-fixed-attenuators-and-pads). Fixed SMD attenuators in stock: Panasonic **EXB24AT6AR5X** (6 dB, DC–3 GHz, 40 mW, 0404; C153012 / 4.3k / US$0.126), Susumu **PAT1220-C-6DB** (DC–3 GHz, 100 mW; C32951947 / 247 / US$0.59), Mini-Circuits **YAT-3A+ / YAT-10A+** (DC–18 GHz, 1.7 W; C5205332 / 720 / US$3.39; C5839318 / 178 / US$3.52).

### D. DC blocks, bias tees, adapters
- On-board DC block = one C0G (Table A, sized by the resonance rule). Bench: Mini-Circuits BLK-89-S+ (C6869194, single-digit stock).
- Bias tees: Mini-Circuits **TCBT-14+** (10 MHz–10 GHz, C5240847 / 81 / US$12.11) and **TCBT-2R5G+** (20 MHz–2.5 GHz, C5189220 / 113 / US$12.43). Or build one from a wire-wound choke (Example 2).
- Coax: U.FL→SMA 1.13 mm pigtail BWIPX1-SMA-1.13L100 (C784403 / 2.2k / US$0.91). Connector and adapter selection, genuine versus clone, torque and loss budgets are covered in [connectors](connectors-and-cables-parts.md) and [coax practicalities](coax-and-connector-practicalities.md). JLC sells no between-series SMA adapters in volume; buy those from distributors.

### E. ESD/TVS for RF ports (snapshot data; live where refreshed)
| Part | C_j | Package | LCSC / stock / US$ | Note |
|---|---|---|---|---|
| Nexperia PESD5V0F1BL | 0.4 pF | DFN1006-2 | C45961 / 62k / 0.10 | genuine; 433/915 MHz and L1 ports |
| UMW PESD5V0F1BL | 0.4 pF | SOD-882 | C3001950 / 115k / 0.026 | second source, verify |
| TECH PUBLIC ESD0P2RF-02LRH-TP | 0.18 pF | DFN1006-2 | C907863 / 7.5k / 0.038 | lookalike of Infineon ESD0P2RF; good for 2.4 GHz if it meets its sheet |
| TECH PUBLIC TPD1E0B04DPLR | 0.2 pF | DFN0603-2 | C2987058 / 9.3k / 0.041 | lookalike of TI TPD1E0B04 |
| Leiditech ESD101-B1-02EL | 0.22 pF | DFN1006-2 | C5139332 / 1.7k / 0.055 | the genuine Infineon ESD101-B1 is not stocked |
| onsemi ESD9X3.3ST5G | **80 pF** | SOD-923 | C130456 / 4.1k / 0.044 | GPIO/USB only, **never on RF** |

### F. Quiet supplies and zero-drift amplifiers (LCSC parametrics; check the datasheet curve at your ripple frequency)
| Part | Noise | PSRR (LCSC) | LCSC / stock / US$ | Use |
|---|---|---|---|---|
| TI TPS7A2033PDBVR | 10 µVrms | 65 dB @ 100 kHz | C2862740 / 180k / 0.21 | LNA, radio, GNSS rails; cheapest quiet LDO |
| TI LP5907MFX-3.3 | 10 µVrms | 82 dB @ 1 kHz | C80670 / 59k / 0.16 | same |
| onsemi NCP161ASN330 | 10 µVrms | 98 dB @ 1 kHz | C892187 / 2.8k / 0.51 | |
| ADI LT3042EDD / LT3045EDD | 0.8 µVrms | 79 / 76 dB @ 1 MHz | C580010 / 6.1k / 6.24; C514420 / 4.4k / 7.09 | VCO/PLL/ADC reference rails after a switcher |
| TI TPS7A9401DSCR | 0.46 µVrms | 51 dB @ 1 MHz | C5220127 / 4.4k / 2.87 | 1 A low-noise rail |
| TI TPS7A4701 / ADI ADM7150 | 4 / 1.6 µVrms | 78 dB @ 1 kHz / 86 dB @ 100 kHz | C90084 / 5.2k / 3.03; C208146 / 643 / 10.75 | higher-voltage rails |
| MSKSEMI RT9013-33 (clone) | 50 µVrms | 75 dB @ 1 kHz | C7434207 / 94k / 0.06 | digital only |
| TI OPA333 / OPA2333 | zero-drift, 2 µV offset, 350 kHz | — | C30878 / 9.0k / 1.31; C38732 | detector/thermistor/strain front ends |
| ADI ADA4528-1 | zero-drift, 4 MHz | — | C155684 / 1.4k / 3.89 | |
| TI OPA388 | zero-drift, 10 MHz, 0.25 µV | — | C1850240 / 2.9k / 2.53 | log-detector post-amp, ADC driver |
| 3PEAK TP5551 | zero-drift, 3.5 MHz, 1 µV | — | C2759987 / 1.9k / 1.25 | domestic second source |

There is no basic-tier zero-drift op-amp; the basic OP07CDR (C7433) is a precision bipolar part, not chopper-stabilised. Theory and layout: [power supplies for RF](../05-analog-electronics/power-supplies-for-rf-and-analog.md) and [op-amp limitations](../05-analog-electronics/op-amps-real-limitations.md).

### G. Ferrites and shields
- **Ferrite beads** for rail filtering are plentiful (3k+ parts; the `ferrite_bead` recipe in jlc-trawler; physics in [ferrites and beads](../04-real-components-hf/ferrites-and-beads.md)).
- **Toroids and cores:** no Fair-Rite parts at JLC. The "Accessories – Inductors" cores (e.g. XRRH, F9-BP, US$0.01–0.02) have **no published mix**. Buy FT-37/FT-50 (#43, #61) or Fair-Rite 2643/2661 parts from distributors for baluns and chokes ([baluns](../08-antennas/antenna-matching-and-baluns.md)). TDK ZCAT3035-1330 clamp cores (C89455) showed zero stock on 2026-10-13.
- **Shields:** JLC stocks **shield clips** in volume. Moda-Innochips ICSRC6508-030SFR (C2836609, 1.05M, US$0.023) is soldered along the fence to hold a separately bought can. Board-level shields (Laird BMI-S-205-F frame, C7429170, 182 in stock, US$2.13) exist only in small quantities. Size cans so their first cavity mode (TM110) is well above every frequency inside ([shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)). A 50 × 40 mm can resonates at about 4.8 GHz.

### H. Couplers, splitters and hybrids (2026-09-14 snapshot unless marked)
| Part | Band | Key spec | LCSC / stock / US$ | Use |
|---|---|---|---|---|
| Mini-Circuits ADC-10-4+ | 5 MHz–1 GHz | 10.5 dB coupling, 1 W | C5445194 / 150 / 8.84 (live) | 433/915 MHz power sampling, VSWR monitor |
| KYOCERA AVX CP0603A0902 (C/H) | 890–915 MHz | 14.7 dB, 23 dB directivity, 3 W | C444728 / 0 (live); C2654317 / 47 / 0.95 | 915 MHz PA power detection |
| TDK HHM22152A2 | 450 MHz–3.8 GHz | ≈ 28 dB coupling | C2654262 / 4.0k / 0.099 (live) | detector tap |
| TDK HHM22106B1 | 0.7–2.7 GHz | 28 dB | C380024 / 531 / 0.17 (live) | |
| HenryTech H3-TCD-12-222X+ | 5 MHz–2.25 GHz | 13.4 dB | C22383448 / 752 / 1.79 (live) | Mini-Circuits-style clone: verify |
| Mini-Circuits TCP-2-10+ / ADP-2-1+ / ADP-2-10+ | 5 MHz–1 GHz / 0.5–400 MHz / 5 MHz–1 GHz | 2-way 0°, ≈ 0.5 dB excess loss, 25 dB isolation | C879853 / 674; C2683460 / 743; C879866 / 52 | 433/915 MHz antenna combiners, test splits |
| Mini-Circuits GP2S1+ | 0.5–2.5 GHz | 2-way 0°, 20 dB isolation | C879828 / 1.2k | |
| Mini-Circuits SP-2G+ | 1.42–1.66 GHz | 2-way 0°, 28 dB isolation | C3155058 / 926 | one GNSS antenna feeding two receivers |
| Mini-Circuits QCN-25+ / QCN-19+ | 1.35–2.45 / 1.1–1.925 GHz | 90° hybrid | C2683439 / 965 / 3.89 (live); C879839 / 66 | 2.4 GHz CP feeds, balanced amps |

No SMD 90° hybrid for 433 MHz or 915 MHz turned up in the snapshot. Build one as a lumped branch-line ([couplers](../06-rf-circuits/couplers-dividers-combiners.md)) from C0G and wire-wound parts, or buy one from the distributors. Parts prefixed "H2-", "H3-", "HT-" and "HG-" are third-party copies of Mini-Circuits numbers.

### I. Circulators and isolators (web listings; none at LCSC/JLC; prices quote-only, not captured)
| Part | Band | IL / isolation | Size / mount | Source quality |
|---|---|---|---|---|
| Trans-Tech (Skyworks) SKYFR-001770 | 902–928 MHz | 0.35 dB / 20 dB, RL 20 dB, 80 W avg | 15 mm SMT | everythingRF listing [5] |
| Transko TCDPMX3343C / 3344C | 902–928 MHz | 0.4–0.5 dB / 16–22 dB | 10.2 mm SMT | everythingRF listing [5] |
| Transko TCDP3075C | 902–928 MHz | 0.25 dB / 25 dB | 20.4 mm SMT | everythingRF listing [5] |
| UIY UIYSC36A400T470 | 400–470 MHz | 0.4 dB / 20 dB, VSWR 1.25, 200 W | Ø36 mm SMT | GlobalSpec/everythingRF listing [5] |
| RF & Noise Components DC-435-176 | 400–470 MHz | 0.4–0.5 dB / 20–23 dB | drop-in | everythingRF listing [5] |

These are bulky because the ferrite resonator scales with wavelength (52 mm disk radius for a junction circulator at 433 MHz, [06 circulators](../06-rf-circuits/circulators-isolators.md)). They also carry a magnet. For a small flight board, a PA that tolerates a high VSWR plus a pad or a low-gain stage is often the better trade.

### J. Mixers with published spur tables
ADE-1+ (0.5–500 MHz, level 7: CL 5.0 dB, L-R 55 dB, IIP3 +15 dBm, P1dB +1 dBm [3]; C2942210, **0 stock** on 2026-10-13, US$8.14). Alternatives: ADE-1L+ (level 3, C3176544 / 42), ADE-2+ (5–1000 MHz, C3176642 / 15), ADE-6+ (0.05–250 MHz, C3176578 / 2) and ADEX-10L+ (C118997 / 909). Mini-Circuits publishes the m×n "harmonics" tables in each model's performance-data file. Active mixers and IQ parts are covered in [mixers/PLLs](mixers-plls-vcos-parts.md).

## Common mistakes & misconceptions
- **"Basic parts cover my RF BOM."** No RF inductor is basic, and the basic C0G range starts at 10 pF. Plan on preferred and extended parts, or on standard PCBA, where the tier does not matter.
- **"The LCSC category is right."** The Murata LQW wire-wound inductors are under "Power Inductors", and some couplers and attenuators sit in "RF Misc". Search by part-number prefix.
- **"Any 0402 inductor will do at 433 MHz."** A multilayer part at Q ≈ 17 doubles a filter's loss compared with wire-wound, and a 68 nH multilayer (SRF 900 MHz) is useless at 915 MHz.
- **"A big DC-blocking capacitor is safer."** Above its series resonance a 100 nF cap is an inductor. Choose C near resonance at the operating frequency, or any C0G ≥ 100 pF for UHF.
- **"ESD diodes are all the same."** An 80 pF TVS on a 433 MHz feed costs about 15 dB. Use ≤ 0.4 pF parts on RF lines.
- **"A 49.9 Ω 0402 is a dummy load."** It is good for a few tens of milliwatts. A PA into it (or into an isolator's port 3 with an open antenna) needs a rated termination.
- **"Clone part, same performance."** UMW, TECH PUBLIC, Leiditech, HenryTech and similar copies often match the DC specification but are not characterised at RF. Measure the S-parameters first.
- **"A 3-pole Butterworth with f_c just above the carrier is a harmonic filter."** At f/f_c = 0.87 it already loses 1.5 dB with perfect parts. Use a Chebyshev or elliptic design, or raise f_c.
- **"Mixer spur tables are fixed numbers."** They are measured at one RF level. Scale them by $(m-1)$ dB per dB of drive.

## How to simulate / verify
- `python3 tools/verify/s13_rf_passives.py` — Butterworth versus Chebyshev harmonic filter with finite Q, ESL and SRF; multilayer Q extrapolation; ESD-capacitance mismatch; termination RL; DC-block resonance; bias-tee choke; isolator VSWR protection; ADE-1 spur-table checks; JLC fee arithmetic. ALL PASS. Pre-registered predictions: R1, R3, R5 and R4 (0.4 pF) hit. **R2 (IL < 0.3 dB for the 3-pole Butterworth) missed** (1.55 dB ideal), and the planning error is kept as Example 1. R4 (80 pF > 15 dB) missed by 0.1 dB. Output in `tools/verify/s13_rf_passives_output.txt`.
- Re-check stock before ordering: `python3 ~/.claude/skills/jlc-trawler/scripts/trawl.py refresh <LCSC numbers>`.
- Measure clone parts (ESD capacitance, inductor L/Q, coupler coupling) on a NanoVNA with a de-embedded fixture ([NanoVNA practical](../17-test-measurement/nanovna-librevna-practical.md), [fixtures](../17-test-measurement/fixtures-and-deembedding.md)). See also GAP_REGISTER §7 R10.

## Open questions / gaps
- LQW15AN Q at 434 MHz is estimated (25–40); LCSC lists no Q. Use the Murata SimSurfing data or measure it.
- The circulator data are third-party web listings (everythingRF, GlobalSpec summaries); manufacturer datasheets and prices were not retrieved (403/timeout).
- The ADE-1 spur table is from the older ADE-1 graphs file (REV X2); the ADE-1+ file may differ slightly.
- No UHF SMD 90° hybrid was found at JLC; distributor parts (e.g. Anaren/TTM Xinger) were not surveyed.
- Basic and preferred flags are from the 2026-09-14 snapshot. JLC changes them, so check at order time.

## Sources
1. JLCPCB/LCSC parts data: jlcparts database snapshot (yaqwsx/jlcparts commit 75daa67, newest row 2026-09-14 09:18), queried locally via the jlc-trawler skill; live stock and prices for the finalists via `trawl.py refresh` on 2026-10-13 (unofficial JLC endpoint). Parametric values (Q@f, SRF, C_j, noise, PSRR) are LCSC listings of the manufacturers' data. (distributor data)
2. JLCPCB, *PCB Assembly FAQs* (updated 9 Sep 2026) — economic PCBA US$3 per unique extended part, basic/preferred exempt; via [sourcing](sourcing-and-eval-boards.md). (manufacturer)
3. Mini-Circuits, *ADE-1+ data sheet* REV G (M158496), https://www.minicircuits.com/pdfs/ADE-1+.pdf; *ADE-1 performance data / harmonics tables* REV X2, https://www.minicircuits.com/pages/s-params/ADE-1_GRAPHS.pdf (RF 250.1 MHz at −14/−4 dBm, LO 280.01 MHz +7 dBm). (manufacturer)
4. Coilcraft, *Micro Spring air core inductors 0906/1606*, Document 163-1 (mirror: https://ipv4.pccomponents.com/datasheets/Coilc-09063JLB.pdf); Mini Spring A02T product page, https://www.coilcraft.com/en-us/products/rf/air-core-inductors/mini-spring/axxt-bxxt/a02t (via search summary). (manufacturer)
5. everythingRF product listings for SKYFR-001770, TCDPMX3343C/3344C, TCDP3075C, UIYSC36A400T470 and DC-435-176 (https://www.everythingrf.com/search/surface-mount-circulators), and GlobalSpec UIY datasheet pages — read via search summaries; pages returned 403 to direct fetch. (third-party catalogue — medium/low confidence)
6. KB theory pages: [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md), [inductors at RF](../04-real-components-hf/inductors-at-rf.md) (LQG15HS10N Q 29 @ 900 MHz; 0402HP data), [resistors at RF](../04-real-components-hf/resistors-at-rf.md), [circulators](../06-rf-circuits/circulators-isolators.md), [mixers](../06-rf-circuits/mixers.md), [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md). (KB, verified scripts)
7. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks and Coupling Structures*, 1964/1980 — Chebyshev prototype g-values (0.1 dB, n = 5) and Cohn's dissipation-loss estimate (values recomputed in the script). (textbook)
