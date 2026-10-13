---
title: Capacitors at RF — MLCC dielectrics, ESR, ESL, SRF and selection
domain: 04-real-components-hf
slug: capacitors-at-rf-mlcc
tags: [mlcc, c0g, np0, x7r, x5r, y5v, dc-bias, ageing, esr, esl, srf, self-resonance, dc-block, bypass, decoupling, anti-resonance, capacitor-q, rf-capacitor, voltage-rating, electrolytic, tantalum, polymer, film-capacitor, polypropylene, polyester, silver-mica, porcelain, capacitor-selection]
prerequisites:
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../01-circuit-theory/resonance-and-q.md
related:
  - inductors-at-rf.md
  - ferrites-and-beads.md
  - pcb-parasitics-traces-vias-pads.md
  - component-models-s2p-spice.md
  - ../01-circuit-theory/energy-storage-and-reactive-power.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
  - ../18-components-parts/sourcing-and-eval-boards.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Capacitors at RF — MLCC dielectrics, ESR, ESL, SRF and selection

## Questions this page answers
- What is the difference between C0G/NP0, X7R, X5R and Y5V, and which do I use in an RF path?
- Why does my "10 µF" ceramic capacitor measure 3 µF on the 5 V rail?
- What are ESR, ESL and self-resonant frequency (SRF), and how do I get them for a part?
- What value DC-blocking capacitor should I use at 433 MHz, 915 MHz and 2.4 GHz?
- Can I use a capacitor above its self-resonant frequency?
- Why do people put 100 nF and 100 pF (or 10 nF) in parallel — does it help or hurt?
- What is the Q of a chip capacitor and does it matter in a matching network?
- What are "RF-grade" or "high-Q" capacitors (Murata GJM, ATC, Johanson), and are they worth it?
- What voltage rating do I need in a PA matching network or a tuned antenna?
- Does capacitor orientation on the board matter?
- Why don't electrolytic or tantalum capacitors work at RF, and what are they good for?
- How do aluminium, tantalum and polymer capacitors compare in impedance, and what happens to them in the cold?
- Why use polypropylene, mica or porcelain capacitors, and what is the main RF loss in a film capacitor?
- Which capacitor family should I use for bulk decoupling, a filter, a PA tank or an HF transmitter?

## TL;DR
- Model: $Z=\text{ESR}+j\omega\,\text{ESL}+1/(j\omega C)$. **SRF $=1/(2\pi\sqrt{\text{ESL}\cdot C})$**; below it the part is a capacitor, above it an inductor of value ESL; at SRF $|Z|=\text{ESR}$.
- **ESL is set mostly by size and mounting**: measured values range from ≈0.12–0.14 nH (ATC 600S 0603, series-thru on microstrip, derived from published SRFs) to ≈0.7 nH (0603), 0.8 nH (0805) and 1.2 nH (1206) for 100 nF parts on a PCB with vias (Kyocera-AVX). Reverse-geometry/IDC parts reach 25–170 pH.
- **Dielectrics:** Class 1 **C0G/NP0** (0 ± 30 ppm/°C, no DC-bias or ageing effect, low loss) for anything that sets a frequency or impedance — matching, filters, oscillators, DC blocks. Class 2 **X7R/X5R** (±15 % over temperature, *plus* large DC-bias loss and ageing ≈ −2.5 %/decade-hour) only for bypass/decoupling. **Y5V/Z5U** (+22/−82 %) avoid.
- **DC bias** can remove most of a Class-2 part's capacitance: a 4.7 µF 6.3 V 0603 X5R measures 0.33 µF at 5 V (−93 %, Maxim/ADI tutorial). Check the vendor curve (Murata SimSurfing, TDK SEAT, KEMET K-SIM).
- **DC block** in 50 Ω: series loss < 0.05 dB needs $|X_{net}|<10.8\ \Omega$. With 0.4 nH mounted ESL the ideal (SRF ≈ f) values are **≈330 pF at 433 MHz, 75 pF at 915 MHz, 10 pF at 2.45 GHz**, but anything from ~22 pF up is < 0.12 dB at 433 MHz and ~22 pF–1 nF is < 0.025 dB at 915 MHz (script table). **Above SRF a DC block still works** as long as $\omega\,\text{ESL}$ is small.
- **100 nF ∥ 100 pF is not automatically better.** With 0.5 nH each, the pair anti-resonates at ≈500 MHz with a 20–60 Ω peak; at 433.92 MHz the combination is **3.3 Ω vs 1.4 Ω for the 100 nF alone** (worse), at 915 MHz 0.8 Ω vs 2.9 Ω (better). Two equal capacitors never anti-resonate.
- **Q** falls with capacitance and frequency: GJM-class 1 pF ≈ 500–1200, 10 pF ≈ 60–140, 22 pF ≈ 15–40 at 433–915 MHz (ESR at datasheet limits). High-Q ranges matter in filters and PA outputs; in 50 Ω DC blocks they don't.
- **Beyond MLCC** (`tools/verify/s4_cap_families.py`): every 100 µF electrolytic, tantalum or polymer part has its SRF at **0.25–0.32 MHz**. Above that it is its ESL (2.5–4 nH, i.e. 7–11 Ω at 434 MHz), so these are bulk and low-frequency parts only, and their merit is ESR (Al 0.3 Ω > Ta-MnO₂ 0.1 Ω > polymer 0.04 Ω at 100 kHz). Wet Al ESR rises ≥ 2× at −40 °C. **Polypropylene** film (tan δ ≤ 5 × 10⁻⁴), **silver mica** and **porcelain/C0G** are the low-loss families. In a PP film capacitor the *conductor* loss (leads and terminations, rising as √f by skin effect) dominates above ≈ 0.1 MHz (100 nF) or ≈ 7 MHz (1 nF). That is the condition behind the exam answer "skin effect"; in polyester the dielectric dominates to higher frequency.
- **Voltage:** RF peak voltage across a matching or tank capacitor can exceed the line voltage many times (≈390 V across a small-loop tuning capacitor at 2 W). Keep RF peak ≤ ~50 % of the DC rating and check current/heating curves.

## Intuition (no math)
An MLCC is dozens to hundreds of thin metal plates interleaved with ceramic, connected alternately to the two end terminations. The capacitance comes from the stacked plate area and the dielectric constant. But current entering one end has to travel along the plates and back out through the termination and the PCB pads — a small loop, and loops have inductance. So every capacitor is secretly a series LC circuit: at low frequency the capacitance dominates and impedance falls with frequency; at the **self-resonant frequency** the inductance exactly cancels the capacitance and only the tiny resistance remains; above it the part is an inductor.

The ceramic matters just as much. **Class 1** ceramics (C0G) are paraelectric: their permittivity is modest (tens), stable, and almost lossless. **Class 2** ceramics (barium titanate: X7R, X5R) are ferroelectric: permittivity in the thousands, so you get microfarads in a tiny package — but the ferroelectric domains line up with any applied DC field, and once lined up they can't contribute to capacitance. Hence DC-bias loss, temperature swings and slow "ageing" as domains settle. They also have more dielectric loss (higher ESR at low frequency) and are slightly piezoelectric ("singing" capacitors, microphonics).

The consequence for RF: use Class 1 whenever the capacitor's *value* matters (filters, matching, oscillators, DC blocks in an RF path); use Class 2 when you only need "a lot of capacitance, roughly" (supply bypass).

## The math

### Level 1 — the series RLC model
$$Z_C(\omega)=R_{ESR}+j\left(\omega L_{ESL}-\frac{1}{\omega C}\right),\qquad f_{SR}=\frac{1}{2\pi\sqrt{L_{ESL}C}},\qquad |Z(f_{SR})|=R_{ESR}.$$
Effective capacitance below SRF: $C_{eff}=\dfrac{C}{1-(f/f_{SR})^2}$ — a capacitor looks *bigger* as you approach its SRF, which is why a matching capacitor picked from its nominal value can be "off" at UHF. Above SRF, $L_{eff}=L_{ESL}\,[1-(f_{SR}/f)^2]$.

**Q of a capacitor**: $Q=|X_{net}|/R_{ESR}$; equivalently the dissipation factor $\mathrm{DF}=\tan\delta=1/Q$ quoted at 1 kHz/1 MHz for low-frequency specs.

### Level 2 — ESR, ESL and the DC-block / bypass problems

**Where ESR comes from.** At low frequency ESR is dominated by dielectric loss, $R\approx\tan\delta/(\omega C)$ — high for Class 2, very small for Class 1. At RF it is dominated by the electrodes and terminations (metal resistance rising with skin and proximity effects, roughly as $\sqrt f$ once the electrode thickness exceeds a skin depth). RF-optimised parts use copper or silver electrodes instead of nickel (Murata GJM: Cu inner electrodes; ESR ≤ 0.3 Ω for 1–5 pF and ≤ 0.25 Ω for 5–10 pF at 1 GHz, ≤ 0.4 Ω for 10–33 pF at 500 MHz, per the GJM specification).

**Where ESL comes from.** The loop formed by the current path through the part, pads, vias and the return plane. It depends on the part's length-to-width ratio (short, wide = low L — hence reverse-geometry 0306/0508/0612 parts), orientation of the electrodes relative to the board, the pad size, the via length to the reference plane and the via position. The values in the TL;DR differ by 5× partly because they are measured differently: series-through-on-microstrip (current returns in the plane directly under the part — small loop) vs shunt-to-ground through vias (loop includes vias). **ESL is a property of the mounted part, not the part alone.**

**DC block in a 50 Ω line.** A series impedance $Z$ between two 50 Ω ports has $S_{21}=2Z_0/(2Z_0+Z)$. For small $Z$: loss ≈ $4.343\,(R/Z_0)+4.343\,(X/2Z_0)^2$ dB. The reactive term only matters when $|X|\gtrsim10\ \Omega$: 0.05 dB at $|X|=10.8\ \Omega$, 0.1 dB at 15.3 Ω. So a DC block works over a *wide* range of values — anything with $|X_{net}|\ll Z_0$ — and it keeps working **above** SRF while $\omega L_{ESL}$ stays small. ESR contributes ≈ 0.09 dB per 1 Ω.

**Bypass (shunt) capacitors** are judged by $|Z|$ relative to the impedance of the node they are shorting, not relative to 50 Ω; for an RF supply pin fed through a ferrite bead or trace, you want $|Z|$ of order 1 Ω or less at the offending frequency.

**Parallel capacitors and anti-resonance.** Two capacitors in parallel, each with its own ESL: between their SRFs, the larger one has already turned inductive while the smaller is still capacitive, so the pair forms a *parallel* LC tank. Its peak impedance is roughly $X^2/(R_1+R_2)$ where $X$ is the branch reactance at the anti-resonance — i.e. the lower the ESRs, the higher the peak. With equal ESL $L$ in both branches the anti-resonance lies at $\omega_{ar}^2=(1/C_1+1/C_2)/(2L)$. The script finds: 100 nF ∥ 100 pF (0.5 nH each) → **20.8 Ω at 503 MHz** (62 Ω if both ESRs are 20 mΩ); 100 nF ∥ 1 nF → 3.5 Ω at 160 MHz; 2 × 100 nF → no peak, just half the impedance. This is the mechanism behind Archambeault's finding that adding a second value gave no noticeable high-frequency improvement in board decoupling, and behind the rule "same value in parallel is safe; different values need their anti-resonances checked".

### Level 3 — distributed behaviour, Class-2 physics and limits

**Higher-order resonances and orientation.** An MLCC is a stack of parallel-plate transmission lines. Mounted flat ("horizontal electrodes"), a series-through capacitor shows a **parallel resonance** (an attenuation notch) above its SRF; for an ATC 100A101 (100 pF) this first parallel resonance is at 1.6 GHz, and mounting the same part on its edge (electrodes vertical) suppresses it and extends the usable coupling range to ≈2.4 GHz (ATC). Johanson ships "oriented" parts for this reason: vertical orientation eliminates the parallel resonance and lowers inductance; horizontal orientation minimises coupling to neighbours. For 433/915 MHz with 0402 parts this is rarely limiting; for 2.4–6 GHz DC blocks it can be.

**DC-bias loss.** In ferroelectric BaTiO₃ the small-signal permittivity is the slope of the polarisation curve; a DC field saturates the domains and flattens that slope. Loss grows with the field $E=V/t$ in each dielectric layer, so thinner layers (more capacitance per volume, smaller packages, lower voltage ratings) derate worse. The EIA code (X7R, X5R) says *nothing* about voltage coefficient; two "X7R 1 µF" parts can differ by a factor of three at the same bias. Practical rule: for bulk decoupling, choose ≥ 2× the operating voltage and one package size up, then check the vendor DC-bias curve.

**Ageing.** Class-2 capacitance falls logarithmically after the last heating above the Curie point (~125 °C): $C(t)=C(t_0)\left[1-\frac{k}{100}\log_{10}(t/t_0)\right]$ with $k\approx2.5$ %/decade-hour for X7R/X5R and ≈7 % for Y5V (Johanson Dielectrics). From 1 h to 1000 h that is −7.5 % (X7R); 1 h to 10 years −12.4 %. Reflow soldering or a 150 °C bake "de-ages" the part (resetting it to its original value); manufacturers reference tolerance to 1000 h after de-ageing (KEMET, EN 130700). C0G does not age.

**Temperature.** EIA RS-198 Class-2 code: first letter low temperature (X = −55 °C, Y = −30 °C, Z = +10 °C), digit high temperature (5 = +85, 6 = +105, 7 = +125, 8 = +150 °C), last letter the allowed change (R = ±15 %, S = ±22 %, U = +22/−56 %, V = +22/−82 %). C0G is 0 ± 30 ppm/°C (≈±0.3 % from −40 to +125 °C). Note: some older KEMET literature quotes the NP0 range as −55 to +85 °C; current C0G parts (e.g. Murata GJM) specify −55 to +125 °C.

**Piezoelectric effects.** Class-2 parts convert mechanical vibration to voltage and vice versa — relevant on a rocket (vibration → noise on a sensitive analog node; PWM ripple → audible singing). Use C0G, film or tantalum/polymer in vibration-sensitive analog paths.

**Voltage and power limits at RF.** Breakdown is set by peak voltage (dielectric and surface flash-over at the terminations); heating by $\tfrac12|I|^2R_{ESR}$ with a thermal resistance to the board (Johanson publishes "max current vs frequency" curves assuming e.g. 120 °C/W and 65 °C ambient). At UHF a 50 V 0402 C0G is adequate for the 50 Ω line of a 2 W transmitter (14.1 V peak) but not for a high-Q tank ([energy and reactive power](../01-circuit-theory/energy-storage-and-reactive-power.md)).

### Level 3 — capacitor families beyond MLCC: electrolytic, tantalum, polymer, film, mica, porcelain
*(G-04-03. Model as in Level 1, with a frequency-dependent ESR: $ESR(f)=R_{metal}(f)+D/(\omega C)$, where $D$ is the dielectric loss tangent and $R_{metal}$ the electrode, electrolyte, lead and termination resistance. Script `s4_cap_families.py`; values are representative of each class, not of a single part.)*

**Bulk families: what limits them.** An aluminium electrolytic is a thin anodic Al₂O₃ dielectric on an etched foil, with a liquid electrolyte as the second "plate". A tantalum is a Ta₂O₅ film on sintered tantalum powder, with MnO₂ (classic) or a conductive polymer as the cathode. A polymer aluminium uses a polymer cathode too. The enormous area gives µF–mF, but the cathode is a resistive, distributed conductor, and the can and leads are millimetres long. So these parts have high ESR, a few nH of ESL and an SRF in the hundreds of kHz:

| Part (class) | ESR @ 100 kHz | ESL | SRF | |Z| @ 1 MHz | 10 MHz | 100 MHz | 433.92 MHz |
|---|---|---|---|---|---|---|---|
| Al electrolytic 100 µF/16 V SMD (NIC NACZ: Z ≤ 0.44 Ω @ 100 kHz, tan δ 0.16 @ 120 Hz) | 0.30 Ω | 4 nH | 0.25 MHz | 0.30 | 0.39 | 2.5 | 10.9 Ω |
| Ta–MnO₂ 100 µF D case (KEMET T495 code: 100 mΩ) | 0.10 Ω | 2.5 nH | 0.32 MHz | 0.10 | 0.19 | 1.6 | 6.8 Ω |
| Ta–polymer 100 µF D case (KEMET T520 code: 40 mΩ) | 0.04 Ω | 2.5 nH | 0.32 MHz | 0.043 | 0.16 | 1.6 | 6.8 Ω |
| X5R MLCC 22 µF 1206 (≈ 10 µF left at 5 V) | 3 mΩ | 1.2 nH | 1.45 MHz | 0.009 | 0.074 | 0.75 | 3.3 Ω |

ESL values are typical for the case style (assumed). The model reproduces the NACZ datasheet (0.30 Ω modelled vs ≤ 0.44 Ω max at 100 kHz; tan δ 0.160 at 120 Hz). **Lessons:**
- Above about 1 MHz every bulk capacitor is just its ESL. At 433 MHz a "100 µF" bypass is a 7–11 Ω inductor, worse than a 100 pF 0402.
- Bulk parts are chosen for **energy and ESR** at the regulator's switching frequency and load-step timescale (e.g. a LoRa PA's TX burst). Their ESR also usefully damps the bead–capacitor and regulator-output resonances ([ferrites](ferrites-and-beads.md#level-3--the-beadcapacitor-resonance-and-damping)).
- A polymer part's very low ESR can *remove* the damping an LDO's stability relies on. Check the regulator's ESR window.

**Temperature.** The wet electrolyte's conductivity falls in the cold. NACZ (16 V) guarantees Z(−40 °C)/Z(+20 °C) ≤ 2 at 120 Hz, and the 100 kHz ESR ratio is usually larger (vendor curves). A 0.3 Ω part becomes 0.6–3 Ω, so a 1 A TX burst dips the rail by 0.3 → 0.6–3 V (§3), a real failure mode on a cold launch pad. Tantalum and polymer types change much less (from knowledge, check curves). Other limits: MnO₂ tantalums can fail short and ignite under surge, so derate to ≈ 50 % of rated voltage and soft-start; polymer types are more tolerant (≈ 80–90 % derating); electrolytics are polarised and their electrolyte dries out with time × temperature.

**Low-loss families and their loss mechanisms.**

| Family | Dielectric loss (tan δ) | Tempco | What dominates ESR at RF | Typical use |
|---|---|---|---|---|
| Polypropylene film (PP, MKP/FKP) | ≤ 5 × 10⁻⁴ @ 1 kHz (WIMA), non-polar so flat with f | ≈ −200 ppm/°C typ. (WIMA FKP 2 data as reproduced by distributor listings, checked by W5-S18b 2026-10-13; WIMA MKP data sheets state only "negative" capacitance change) | **leads and terminations** (skin effect) above 0.1–7 MHz | audio/RF filters at HF, snubbers, pulse, tank caps at HF |
| Polyester film (PET, MKT) | ≤ 8 × 10⁻³ @ 1 kHz (WIMA), polar, rises with f and T | large, nonlinear | dielectric up to MHz | general coupling, not RF |
| Silver mica | ≈ 3 × 10⁻⁴ (assumed typical) | 0…+70 ppm/°C (CDE CD15) | leads at VHF | HF transmitter tanks, filters, oscillators (stable) |
| C0G MLCC / porcelain (ATC 100B/600S) | ≈ 10⁻⁴ | 0 ± 30 ppm/°C | electrodes (Cu/Ag, skin √f) | everything UHF; porcelain for high power |

**The "skin effect in film capacitors" statement (exam condition).** The US Extra pool (E5D08) gives skin effect as the main RF loss in film capacitors. That is true *for a low-loss film at RF*: in polypropylene the dielectric term $D/(\omega C)$ falls as 1/f, while lead and termination resistance rises as √f once the skin depth (66 µm at 1 MHz, 21 µm at 10 MHz in copper) is below the lead radius. For 100 nF PP with 2 × 10 mm of 0.6 mm leads, the two terms cross at **0.12 MHz**, and at 10 MHz conductor loss is 14 mΩ against 0.08 mΩ dielectric (§2). For 1 nF PP the crossover is ≈ 6.5 MHz, and for 100 nF *polyester* ≈ 1.5 MHz, so a PET part at audio frequencies is dielectric-loss-limited. The metallised electrodes themselves (20–50 nm) are far thinner than δ and show no skin effect. Their loss is a frequency-independent sheet resistance spread from the sprayed end connection. Film-foil types (5–9 µm Al foil) reach the skin regime only near 100 MHz (δ_Al 8.5 µm). So the correct statement is: for low-loss films at RF, conductor loss (skin and proximity effect in leads, terminations and electrodes) dominates; for polar films at low frequency, dielectric loss does.

**Q at RF (§4, assumed tan δ for mica/C0G).** Silver mica 100 pF (leaded): Q ≈ 3200 at 1 MHz, 2400 at 7 MHz, 1000 at 30 MHz, 240 at 100 MHz, falling with the lead skin effect and approaching SRF (225 MHz with 5 nH of leads). A C0G 0402 100 pF gives 1200 at 30 MHz and 290 at 100 MHz. A 100 nF PP film is a fine capacitor at 10 kHz (Q ≈ 1850) and useless near its 6.5 MHz SRF.

**Selection table.**

| Job | Choose | Avoid |
|---|---|---|
| Bulk at a regulator / PA module (TX bursts) | polymer Al/Ta or X7R 1206+ at ≥ 2× voltage, plus a damping ESR; Al electrolytic only if warm or oversized | MnO₂ Ta without derating; tiny X5R at full voltage |
| Bypass at 433–2450 MHz | C0G 0402 chosen by SRF ([above](#level-2--esr-esl-and-the-dc-block--bypass-problems)) | any electrolytic/tantalum "for RF" |
| HF (1–30 MHz) filters, traps, oscillators | silver mica, C0G, PP film (≤ ~1 MHz in large values) | PET, X7R |
| HF/VHF transmitter tanks, EFHW compensation, tuners | mica, porcelain (ATC 100B/C), high-voltage C0G, vacuum/air variables at kW | small ceramic discs (unknown dielectric, ≤ 1 A RF) |
| Audio/analog signal path, anti-alias, timing (µs–ms) | PP or C0G | X7R (piezo, nonlinearity), PET in precision timing |

## Design equations & rules of thumb

| Item | Equation / rule | Typical values |
|---|---|---|
| SRF | $1/(2\pi\sqrt{L_{ESL}C})$ | 100 pF, 0.5 nH → 712 MHz; 10 pF, 0.3 nH → 2.9 GHz; 100 nF, 0.5 nH → 22.5 MHz |
| Effective C below SRF | $C/(1-(f/f_{SR})^2)$ | at $f=0.5f_{SR}$: +33 % |
| Implied ESL from datasheet SRF | $L=1/[(2\pi f_{SR})^2C]$ | ATC 600S (0603): 0.12–0.14 nH; ATC 100A: 0.25–0.27 nH |
| Mounted ESL (PCB, vias) | vendor data | 0603 ≈ 0.7 nH, 0805 ≈ 0.8, 1206 ≈ 1.2 nH (AVX, 100 nF) |
| DC-block loss in 50 Ω | $4.343R/Z_0+4.343(X/2Z_0)^2$ dB | $|X|$ = 10.8 Ω → 0.05 dB |
| "SRF-matched" DC block | $C=1/[(2\pi f)^2L_{ESL}]$ | 0.4 nH: 336 pF (433.92 MHz), 76 pF (915), 10.5 pF (2.45 GHz) |
| Anti-resonance (equal ESL) | $\omega^2=(1/C_1+1/C_2)/(2L)$ | 100 nF ∥ 100 pF, 0.5 nH → ≈500 MHz |
| Class-2 ageing | $-k\log_{10}(t/t_0)$ %, k ≈ 2.5 (X7R/X5R), 7 (Y5V) | — |
| DC-bias derating | vendor curve; choose ≥ 2× V and larger case | 4.7 µF/6.3 V/0603 X5R @ 5 V → 0.33 µF |
| RF voltage margin | $V_{pk,RF}\lesssim0.5\,V_{rated}$ | 2 W/50 Ω line: 14.1 V pk |
| ESR with dielectric term | $ESR=R_{metal}(f)+D/(\omega C)$ | NACZ 100 µF: tan δ 0.16 @ 120 Hz, 0.3 Ω @ 100 kHz |
| Bulk-cap SRF | $1/(2\pi\sqrt{L_{ESL}C})$ | 100 µF, 2.5–4 nH: 0.25–0.32 MHz |
| Film loss crossover | $D/(\omega C)=R_{leads}(f)$ | PP 100 nF: 0.12 MHz; PP 1 nF: 6.5 MHz; PET 100 nF: 1.5 MHz |

## Worked examples

### 1. Choosing DC-block capacitors (`tools/verify/components_mlcc.py` §3)
Series loss in 50 Ω with 0.4 nH mounted ESL and 0.1 Ω ESR:

| C | 433.92 MHz | 915 MHz | 2.45 GHz | SRF |
|---|---|---|---|---|
| 3.3 pF | −3.45 dB | −0.99 dB | −0.09 dB | 4.4 GHz |
| 10 pF | −0.53 | −0.11 | −0.009 | 2.5 GHz |
| 22 pF | −0.11 | −0.022 | −0.013 | 1.7 GHz |
| 47 pF | −0.028 | −0.010 | −0.019 | 1.16 GHz |
| 100 pF | −0.012 | −0.009 | −0.022 | 796 MHz |
| 1 nF | −0.009 | −0.011 | −0.025 | 252 MHz |
| 100 nF | −0.009 | −0.011 | −0.025 | 25 MHz |

Choice: **47–100 pF C0G 0402** covers 433 MHz to 2.45 GHz with < 0.03 dB loss; 22 pF is the classic 2.4 GHz value; 100 nF "works" at 915 MHz only because its ESL (here 0.4 nH, 2.3 Ω) is small — it is an inductor there, and its Class-2 dielectric adds loss and piezo noise. For a GNSS LNA feed (bias-T) use ~47–100 pF at 1575.42 MHz.

### 2. Matching-capacitor Q (§4)
With ESR at the GJM specification limits and 0.35 nH ESL: 1 pF → Q ≈ 1220 (433.92 MHz) / 570 (915); 3.3 pF → 370 / 170; 10 pF → 140 / 62; 22 pF → 39 / 15. In a PA output match the shunt capacitor carries $Q_n P$ vars; at 2 W with $Q_n=3$ and Q_C = 60 that is 0.1 W of heat — worth choosing a high-Q part and a smaller value where the topology allows.

### 3. Does 100 pF across 100 nF help at 433 MHz? (§5)
Each with 0.5 nH mounted: the pair anti-resonates at ≈503 MHz. At 433.92 MHz the combination is **3.3 Ω** vs **1.36 Ω** for the 100 nF alone — adding the "RF cap" made the bypass 2.4× worse at the operating frequency. At 915 MHz it helps (0.82 Ω vs 2.87 Ω). If the 100 pF is mounted with lower inductance (0.3 nH, placed right at the pin with its own via) the anti-resonance moves to 563 MHz and |Z| at 915 MHz becomes 0.10 Ω. **Lesson:** a small bypass capacitor should be chosen so its SRF lands *at* the frequency you want to suppress, placed closest to the pin, and the anti-resonance with its neighbours kept away from frequencies you care about — or simply use two of the same value.

### 4. Bulk capacitance on a LoRa module rail
EBYTE E22-400T33D (2 W) draws of order 1 A peak while transmitting (check the module datasheet for the exact figure). A "22 µF 6.3 V 0805 X5R" on a 5 V rail may deliver only ~5–8 µF (typical vendor curves show 60–80 % loss at 80 % of rating for small X5R cases — check the specific part). Use a 16–25 V rated 1206 X7R or a polymer capacitor for the bulk, plus a damping ESR ([transients](../01-circuit-theory/transient-and-step-response.md)).

### 5. Ageing and temperature on an oscillator load capacitor
A crystal's load capacitors must be C0G: an X7R part would drift ±15 % over temperature and −7.5 % in its first 1000 h, pulling the crystal by tens of ppm ([crystals](crystals-and-resonators.md)).

## Practical notes
- **RF-grade families:** Murata GJM (Cu electrodes, 0201/0402, 0.1–33 pF, tight tolerances W = ±0.05 pF, B = ±0.1 pF), Murata GQM (larger, high power), Johanson R07S/R14S (0402/0603 high-Q, NPO), ATC/Kyocera-AVX 600S/600L/100A/100B (porcelain, very low ESR, high voltage), KEMET HiQ. On JLCPCB/LCSC many GJM parts exist as "extended" parts; ordinary GRM C0G is acceptable at 433/915 MHz for DC blocks and bypass, less so for high-Q filters ([parts sourcing](../18-components-parts/sourcing-and-eval-boards.md)).
- **Package:** 0402 is the sweet spot for 433 MHz – 6 GHz on 1.6 mm FR-4 designs (lower ESL and pad capacitance than 0603, still hand-solderable). 0201 for > 6 GHz.
- **Pads and vias** add ≈0.05–0.2 pF and ≈0.2–0.6 nH respectively ([PCB parasitics](pcb-parasitics-traces-vias-pads.md)); for shunt capacitors to ground, use a via directly in or beside the ground pad, or two vias.
- **Vendor models:** download S-parameters/SPICE from Murata SimSurfing (includes DC bias and temperature), KEMET K-SIM, TDK SEAT, Johanson/ATC tools — then add your own pad/via model ([component models](component-models-s2p-spice.md)).
- **Measuring:** a shunt-to-ground 2-port measurement on a 50 Ω through-line is the most accurate way to see low impedances (tens of mΩ); series-through is better for DC blocks.

## Common mistakes & misconceptions
- **"X7R is fine for RF matching."** Its value moves with bias, temperature and time, and its loss is high. Use C0G for anything whose value matters.
- **"A capacitor is useless above its SRF."** As a DC block, it keeps working while $\omega L_{ESL}\ll Z_0$; as a bypass, it becomes a small inductor — often still fine.
- **"Always put 100 nF + 10 nF + 100 pF on every pin."** Different values anti-resonate; the benefit depends on SRFs, ESRs and placement. Several equal values, or one well-chosen value with a low-inductance connection, is often better. (A perennial forum question [12]; anti-resonance mechanism per Archambeault [9] and script §5.)
- **Trusting the nominal µF of Class-2 parts.** Check DC bias; small, low-voltage X5R parts can lose > 80 %.
- **Picking a DC block by its reactance alone.** Also check SRF (for series use) and the parallel-resonance notch at GHz for flat-mounted larger parts.
- **Ignoring pad capacitance** on sub-pF matching capacitors — a 0.5 pF part can be 0.6–0.7 pF once soldered.
- **Using the DC voltage rating for RF** without checking peak RF voltage in resonant circuits.
- **"A big electrolytic (or tantalum) filters RF."** Its SRF is ≈ 0.3 MHz; at 433 MHz a 100 µF part is a 7–11 Ω inductor. It handles energy and low-frequency ripple; RF bypass needs small C0G parts placed at the pin.
- **"Lower ESR is always better."** An ultra-low-ESR polymer or MLCC bank can make an LDO oscillate or leave a bead–capacitor resonance undamped. Respect the regulator's ESR window or add a series damping resistor.
- **Ignoring cold ESR.** Wet aluminium electrolytics at −40 °C have ≥ 2× (often much more at 100 kHz) the ESR; a cold pad turns a marginal rail into brown-outs during TX bursts.
- **"Skin effect is the main loss in film capacitors" (as an unconditional rule).** True for low-loss polypropylene at RF (the leads and terminations dominate above 0.1–7 MHz). For polyester at audio/LF the dielectric dominates, and in metallised electrodes thinner than δ there is no skin effect at all.
- **Ceramic disc capacitors of unknown dielectric in HF tanks.** Use mica, porcelain or rated C0G; check RF current (e.g. 1.3 A rms in an EFHW compensation cap at 28 MHz/100 W, [ferrites](ferrites-and-beads.md#iron-powder-vs-ferrite-cores-gapped-cores-and-hf-transformers-efhw-491)).

## How to simulate / verify
- `python3 tools/verify/s4_cap_families.py` (output `s4_cap_families_output.txt`) — |Z|(f) and SRF of Al/Ta/polymer/X5R/PP/PET/mica/C0G models (NACZ check), film loss crossover (dielectric vs skin-effect conductor loss), cold-ESR rail dip, Q of mica/C0G/PP.
- `python3 tools/verify/components_mlcc.py` — implied ESL from ATC SRFs, SRF tables, DC-block loss table, capacitor Q, parallel anti-resonance cases, derating arithmetic.
- Simulate with vendor S-parameter models plus your pad/via geometry (scikit-rf cascade, QUCS-S, ADS/AWR); for decoupling networks, plot |Z| of the full PDN ([PDN for RF](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)).
- Measure with a NanoVNA/LibreVNA: shunt-through fixture for bypass caps (|Z| ≈ $25\,S_{21}/(1-S_{21})$ Ω), series-through for DC blocks.

## Open questions / gaps
- 0402 mounted-ESL values on JLCPCB standard stackups (e.g. 4-layer JLC7628 with 0.2 mm to L2) are not measured here; the 0.3–0.5 nH range used is an estimate consistent with the AVX/ATC data (see PCB parasitics page for the via part).
- RF current ratings of generic (non-RF-grade) C0G parts are unpublished.

## Sources
1. R. Fiore (American Technical Ceramics), "Capacitors in coupling and DC blocking applications," *Circuit Designer's Notebook*, Doc. 001-927 Rev. E, 2005 (Kyocera-AVX). https://rfs.kyocera-avx.com/userFiles/uploads/pdfs/capacitors_in_coupling.pdf — FSR/ESR table, parallel resonance at 1.6 GHz, edge mounting. (app note)
2. Murata, "GJM series — high-frequency, high-Q chip capacitors," catalog C-29-C (Modelithics-hosted). https://www.modelithics.com/models/Vendor/Murata/GJM15.pdf — Cu electrodes, C0G range, ESR and Q specifications. (datasheet)
3. Johanson Technology, "Multi-layer high-Q capacitors" catalog, 2022 — R07S/R14S SRF/ESR/Q/current charts, oriented capacitors. https://www.johansontechnology.com/docs/2818/johanson-technology-multi-layer-high-q-capacitors8--4-2022_VRkwKZd.pdf (datasheet)
4. Kyocera-AVX, "Low inductance capacitors — introduction" (LICC/IDC/LICA), ESL by style for 100 nF parts. https://media.digikey.com/pdf/Data%20Sheets/AVX%20PDFs/LICC.pdf (datasheet)
5. KEMET, "General information — ceramic capacitors" (F9000), 2007 — Class 1/2 definitions, EIA RS-198 code table, ageing law and de-ageing, equivalent circuit. https://content.kemet.com/datasheets/F9000_K.pdf (manufacturer technical note)
6. Johanson Dielectrics, "Ceramic capacitor aging made simple" — ageing rates by dielectric, 1000 h reference, de-ageing at 150 °C. https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/ (app note)
7. M. Fortunato, "Temperature and voltage variation of ceramic capacitors, or why your 4.7 µF capacitor becomes a 0.33 µF capacitor," Maxim Integrated tutorial 5527, 2012 (now Analog Devices). https://www.analog.com/en/technical-articles/temperature-and-voltage-variation-ceramic-capacitor--maxim-integrated.html — (fetch timed out; figures taken from search summary and widely reproduced) (app note)
8. Murata, "What are impedance/ESR frequency characteristics in capacitors?" and FAQ on ESR/ESL (SimSurfing). https://article.murata.com/en-us/article/impedance-esr-frequency-characteristics-in-capacitors (manufacturer article)
9. B. Archambeault, "Eliminating the myths about printed circuit board power/ground plane decoupling," *Interference Technology*. https://interferencetechnology.com/eliminating-the-myths-about-printed-circuit-board-powerground-plane-decoupling/ (industry article, expert)
10. Murata, "Multilayer ceramic capacitors — S-parameter measurement conditions." https://www.murata.com/en-us/tool/data/sparameterdata/sparameter-mlcc/condition (manufacturer documentation)
11. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — lumped-element parasitics, series element in a matched line. (textbook)
12. All About Circuits forum, "Common decoupling cap — why 100 nF" (thread 102031) and "Decoupling capacitors" (thread 90980); Hackaday, "Capacitor decoupling chaos, and why you should abandon 100 nF," Jan. 2025. https://forum.allaboutcircuits.com/threads/common-decoupling-cap-why-100nf.102031/ ; https://hackaday.com/2025/01/25/capacitor-decoupling-chaos-and-why-you-should-abandon-100-nf/ — the recurring "100 nF + 10 nF" question and the equal-value counter-argument. (forum — anecdotal; used only for the misconceptions list)
13. Verification script `tools/verify/components_mlcc.py` (this KB).
14. NIC Components, "NACZ series surface-mount aluminium electrolytic capacitors" data sheet — 100 µF/16 V 6.3 × 6.3: tan δ 0.16 @ 120 Hz, max impedance 0.44 Ω @ 100 kHz/20 °C; Z(−40 °C)/Z(+20 °C) ≤ 2 (16 V) at 120 Hz. https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7153/NACZ13-Datasheet.PDF (datasheet)
15. KEMET tantalum part-number conventions: T495 (low-ESR MnO₂) and T520 (polymer) with the ESR in mΩ coded in the suffix (e.g. T495D107K010ATE100 = 100 mΩ, T520D107M006ATE040 = 40 mΩ); voltage-derating guidance (MnO₂ ≈ 50 %, polymer ≈ 80–90 %). (datasheet convention. Checked by W5-S18b, 2026-10-13: T495D107K010 = 100 mΩ at 100 kHz confirmed from the KEMET data sheet of the ATA100 sibling and distributor listings of ATE100; 40 mΩ confirmed for the T520D337M006ATE040 and T520W107M010ATE040 siblings, the exact T520D107M006ATE040 not found; derating: KEMET, "Derating differences," CARTS Europe 2004 (kemet.com technical archive) recommends 50 % for MnO₂ and 20 % (use at ≤ 80 % of rated) for T520/T530 polymer — the 90 % end of the range above is later KEMET guidance for low-voltage polymer parts, not re-read)
16. WIMA short-form catalogue 2019/2025 — dissipation factor at 1 kHz: polypropylene ≤ 5 × 10⁻⁴ (MKP/FKP), polyester ≤ 8 × 10⁻³ (MKT). https://www.wima.de/wp-content/uploads/media/WIMA_Short-form_2025_26.pdf (datasheet; via search summary)
17. Cornell Dubilier CD15 dipped silver-mica capacitors — temperature coefficient 0 to +70 ppm/°C (distributor listings of the datasheet). (datasheet; via search summary; mica tan δ ≈ 3 × 10⁻⁴ is an assumed typical value)
18. ARRL/NCVEC Amateur Extra question pool, E5D08 (main RF loss in film capacitors: skin effect) — used only to state the condition under which that answer holds. (exam pool)
19. Verification script `tools/verify/s4_cap_families.py` (this KB).
