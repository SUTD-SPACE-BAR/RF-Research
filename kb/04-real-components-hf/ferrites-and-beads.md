---
title: Ferrites and ferrite beads — impedance, DC bias, resonance pitfalls and core materials
domain: 04-real-components-hf
slug: ferrites-and-beads
tags: [ferrite-bead, chip-bead, iron-powder, carbonyl-iron, micrometals, mix-2, mix-6, mix-52, gapped-core, A_L, efhw, 49-to-1, compensation-capacitor, core-loss, core-heating, emi, complex-permeability, dc-bias, saturation, lc-resonance, damping, fair-rite, mix-31, mix-43, mix-61, nizn, mnzn, common-mode-choke, cable-ferrite, supply-filtering]
prerequisites:
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../01-circuit-theory/transient-and-step-response.md
  - inductors-at-rf.md
related:
  - capacitors-at-rf-mlcc.md
  - ../02-electromagnetics/magnetic-materials-permeability.md
  - ../01-circuit-theory/transformers-coupled-inductors.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
  - ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md
  - ../06-rf-circuits/baluns-and-rf-transformers.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../08-antennas/dipoles-and-monopoles.md
  - ../17-test-measurement/bench-measurement-recipes.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Ferrites and ferrite beads — impedance, DC bias, resonance pitfalls and core materials

## Questions this page answers
- What does a ferrite bead actually do — is it an inductor or a resistor?
- What does "600 Ω at 100 MHz" on a bead datasheet mean, and what is it at 433 or 915 MHz?
- Why does my bead stop working when the load draws current?
- Can a bead plus a capacitor make supply noise *worse*? How do I damp it?
- Which bead should I put on the supply of a LoRa module or a GNSS receiver?
- What are Fair-Rite 31, 43, 61 (and 73) materials and which do I use on a cable?
- How does a common-mode choke differ from a bead?
- When does a ferrite bead hurt rather than help?
- Iron powder or ferrite — which toroid (T50-2, T68-6, FT240-43, FT240-61) for a filter, a trap, a balun or a 49:1 EFHW transformer?
- How many turns do I need from the A_L value, and why does my ferrite inductor measure less than A_L predicts at HF?
- How hot will my EFHW transformer get at 100 W, and do I need two stacked cores?
- What does the capacitor across the 50 Ω side of an EFHW transformer do, and what rating does it need?
- Which ferrite bead works on a 433 MHz coax, and will it heat up at 2 W?
- Why do modern cables rarely have a ferrite lump on them?

## TL;DR
- A bead's impedance $Z=R+jX$ comes from the ferrite's complex permeability: $Z=j\omega L_0(\mu_s'-j\mu_s'')$, so $X\propto\mu'$ (stored energy) and $R\propto\mu''$ (loss). **Below its crossover it is mostly an inductor; around its rated frequency mostly a resistor (it absorbs noise as heat); above its peak it is capacitive** (winding/pad capacitance).
- The "600 Ω @ 100 MHz" rating is $|Z|$ at one frequency with **no DC current**. A 1 kΩ-class bead (Burket model: 1.21 µH ∥ 1.68 pF ∥ 1.08 kΩ + 0.3 Ω) peaks at ≈1.08 kΩ at 112 MHz but is only **229 Ω (capacitive) at 433.92 MHz, 105 Ω at 915 MHz, 39 Ω at 2.45 GHz** (script). For UHF/2.4 GHz noise use "GHz-band" beads (e.g. Murata BLM15GG/BLM18GG) and read the whole curve.
- **DC bias collapses bead inductance**: at 50 % of rated current inductance can fall by up to ~90 % (e.g. a 100 Ω/3 A 0603 bead drops to ≈10 Ω at 100 MHz). Use beads at ≲20 % of rated current if the impedance matters.
- **Bead + capacitor = LC resonator.** With a low-ESR 10 nF cap the model bead peaks **+27 dB at 1.45 MHz** (Burket measured +10 dB around 2.5 MHz for his parts) — supply noise near that frequency (switching regulators!) is *amplified*. Damp it: best is an extra large capacitor with series R (e.g. 1 µF + 2 Ω → +0.3 dB peak, HF attenuation kept); a resistor across the bead or in series with the cap damps but costs HF attenuation.
- **Fair-Rite materials**: 73 (MnZn, 1–25 MHz, small parts), 31 (MnZn µᵢ 1500, 1–300/500 MHz, large cable cores), 43 (NiZn µᵢ 800, 20–250/300 MHz, the general-purpose suppression mix), 61 (NiZn µᵢ 125, suppression > 200 MHz, inductors < 25 MHz). Impedance scales with **N²** (turns through the core) until winding capacitance takes over.
- **Iron powder vs ferrite** (script `s4_core_turns_loss.py`): carbonyl-iron mixes −2/−6 (μ 10/8.5, +95/+35 ppm/°C, material Q ≈ 370–465 at 7 MHz) are for stable high-Q *tuned* coils; 43 (μ 800, Q ≈ 1 at 7 MHz, 1.25 %/°C) is for *broadband lossy* transformers and chokes. N = √(L/A_L); ferrite A_L is a 10 kHz figure.
- **EFHW 49:1 on one FT240-43, 2:14 turns, loses ≥ 20 % (≈ 1 dB) at 3.6–7 MHz** (small-signal lower bound) and reaches a ≈ 105 °C rise at 100 W key-down. For ≈ 25 °C the limit is about 18 W average, so use 3:21 turns and/or two stacked cores for 100 W digital modes. The 100–150 pF compensation capacitor completes a ≈ 50 Ω π low-pass with the leakage inductance and carries ≈ 1.3 A rms at 28 MHz/100 W.
- **Common-mode choke**: two windings on one core; common-mode currents see $j\omega(L+M)$-type impedance (large), differential currents only leakage $2j\omega L(1-k)$ (small) — so it blocks CM noise without affecting the signal/power.

## Intuition (no math)
A ferrite is a ceramic magnet material that, at low frequency, concentrates magnetic flux (high permeability) — a wire through a ferrite bead gains inductance. As frequency rises, the tiny magnetic domains can no longer follow the field; the material's permeability becomes lossy, and the energy that goes into trying to magnetise it is turned into heat. That is the bead's useful regime: noise current passing through it is *absorbed*, not just reflected. At still higher frequencies the bead's internal capacitance (between its turns or across its body) shorts it out and it becomes ineffective.

Because the "inductance" part depends on the ferrite not being saturated, DC current through the bead matters a lot: a steady current magnetises the core part-way to saturation, the permeability collapses, and the bead's impedance falls — often dramatically, at currents well below its rated (thermal) current.

And because a bead is partly an inductor, putting it in front of a capacitor makes an LC filter — with a resonance. If nothing damps that resonance, noise near it gets *bigger*. That is the classic "I added a ferrite and my supply got noisier" story.

## The math

### Level 1 — the circuit model
Datasheets plot $|Z|$, $R$ and $X$ vs frequency. A convenient model (Burket/ADI):
$$Z_{bead}=R_{DC}+\left(\frac{1}{j\omega L}+j\omega C_{par}+\frac{1}{R_{AC}}\right)^{-1}.$$
Fitted values for a 1 kΩ-class 0805 bead (Tyco BMB2A1000LN2, from Burket): $L=1.208\ \mu$H, $C_{par}=1.678$ pF, $R_{DC}=0.30\ \Omega$, $R_{AC}=1.082$ kΩ. From `tools/verify/components_ferrite_bead.py` §1:

| f | 1 MHz | 10 MHz | 30.7 MHz | 100 MHz | 433.92 MHz | 915 MHz | 2.45 GHz |
|---|---|---|---|---|---|---|---|
| $Z$ (Ω) | 0.4 + j7.6 | 5.7 + j76 | 56 + j239 | 1001 + j285 | 49 − j224 | 10 − j104 | 1.7 − j39 |

$R=|X|$ at 76 and 164 MHz; peak $|Z|=1.08$ kΩ at 112 MHz (where L resonates with $C_{par}$). The model is a fit over ~30–800 MHz; real parts may have a second, broader loss region.

### Level 2 — material physics: complex permeability
For a core with $N$ turns and effective core constant $C_1=\sum\ell/A$ (cm⁻¹), Fair-Rite writes
$$Z=j\omega L_0(\mu_s'-j\mu_s''),\qquad L_0=\frac{4\pi N^2\times10^{-9}}{C_1}\ \text{H},$$
so $X_s=\omega L_0\mu_s'$ and $R_s=\omega L_0\mu_s''$. Materials have high $\mu'$ at low frequency (inductive, reflective suppression); as $\mu'$ rolls off, $\mu''$ peaks (resistive, absorptive suppression). Geometry and turns are frequency-independent multipliers (hence **N² scaling**), until the winding's self-capacitance resonates.

**Material families.** MnZn ferrites (Fair-Rite 31, 73, 75): high permeability (µᵢ ≈ 1500 for 31), low resistivity (3×10³ Ω·cm for 31), effective at low frequencies; large MnZn cores suffer "dimensional resonance" (a standing wave inside the core because of the high εr·µr) — material 31 was formulated to avoid this and is used for large cable cores. NiZn ferrites (43, 44, 52, 61): lower permeability (µᵢ 800 for 43, 125 for 61), very high resistivity (10⁵–10⁸ Ω·cm), effective at higher frequencies. Curie temperatures: >130 °C (31, 43), >300 °C (61).

| Fair-Rite mix | Type | µᵢ | Suppression range (Fair-Rite) | Typical use |
|---|---|---|---|---|
| 73 | MnZn | high | 1–25 MHz | small beads, low-frequency noise |
| 31 | MnZn | 1500 | 1–300 MHz (to 500 MHz per datasheet) | cable snap-ons, large toroids |
| 43 | NiZn | 800 | 20–250/300 MHz | general-purpose beads and cable cores |
| 61 | NiZn | 125 | > 200 MHz (inductive use < 25 MHz) | VHF/UHF suppression, HF inductors |

**DC bias.** A DC current produces a static field $H=1.256\,NI/\ell_m$ (oersted, $\ell_m$ in cm). A single-turn chip bead with $\ell_m\approx0.5$ cm carrying 1 A sees ≈2.5 Oe (200 A/m) — enough to push many ferrites well up their B–H curve. Both $\mu'$ and $\mu''$ fall; the effect is geometry-dependent, so vendors give $|Z|$-vs-frequency curves at several DC currents. Burket reports that at 50 % of rated current the inductance can fall by up to 90 %; the TDK MPZ1608S101A (100 Ω, 3 A) drops from 100 Ω to ~10 Ω at 100 MHz, and a Würth 742 792 510 (70 Ω, 6 A) from 70 to ~15 Ω, both at half rated current.

### Level 3 — the bead–capacitor resonance and damping
Source (regulator) → bead → capacitor → light load is a series RLC driven from a low impedance: resonance $f_r=1/(2\pi\sqrt{L_{bead}C})$, characteristic impedance $\sqrt{L/C}$, and damping only from $R_{DC}$, the capacitor ESR and the bead's own (small) low-frequency loss. For the model bead with 10 nF: $f_r=1.45$ MHz, $\sqrt{L/C}=11\ \Omega$, $Q\approx31$ → **+27 dB peaking** (script §2). If a switching regulator runs near $f_r$, its ripple is amplified.

Damping options (script, same bead and 10 nF, 100 MHz attenuation shown for comparison):

| Method | Peak | Attenuation @ 100 MHz |
|---|---|---|
| none (10 nF, 10 mΩ ESR) | +27.1 dB @ 1.45 MHz | −76.5 dB |
| A: 2 Ω in series with the 10 nF | +13.1 dB | −54.3 dB (HF bypass degraded) |
| B: 10 Ω across the bead | +2.7 dB | −36.1 dB (bead bypassed at HF) |
| C: add 1 µF + 2 Ω branch in parallel with the 10 nF | +0.3 dB @ 76 kHz | −76.8 dB (kept) |

Method C (a larger capacitor with its own series damping resistor, about $\sqrt{L/C}$ in magnitude) is the recommended approach — it matches Burket's conclusion. DC bias makes things worse in a different way: with L collapsed to 30 % or 10 %, the resonance moves up (2.6, 4.6 MHz), the peak remains large (+24, +19 dB) and the 100 MHz impedance drops to 289 / 82 Ω.

**Common-mode chokes.** Two windings of self-inductance $L$ with coupling $k$: a common-mode current (same direction in both, splitting equally) sees $Z_{CM}=j\omega L(1+k)/2$ for the pair; a differential current sees the loop impedance $Z_{DM}=2j\omega L(1-k)$. For $L=10\ \mu$H and $k=0.995$ at 10 MHz: $|Z_{CM}|=627\ \Omega$, $|Z_{DM}|=6.3\ \Omega$. The differential flux cancels in the core, so DC power current does not saturate it — the key advantage over beads on power lines. At RF a coax wound through a ferrite core is the same device: a **current (choke) balun** that suppresses shield currents ([baluns](../06-rf-circuits/baluns-and-rf-transformers.md)).

### Iron-powder vs ferrite cores, gapped cores and HF transformers (EFHW 49:1)
*(G-04-01; all numbers from `tools/verify/s4_core_turns_loss.py`, which reads Fair-Rite's published complex-permeability CSVs [9] and uses Micrometals datasheet constants [10][11].)*

**Two families, opposite strengths.** A *ferrite* (31/43/52/61) is a sintered ceramic magnet with a high, lossy, temperature-sensitive permeability. An *iron-powder* core (Micrometals/Amidon "T" cores, mixes −2, −6, −10, −17) is made of micron-sized carbonyl-iron particles in an insulating binder. Each particle is a tiny metal magnet, but the binder spreads a **distributed air gap** through the whole core, so the effective μ is only 4–35. Because of that dilution the core is stable, low-loss and very hard to saturate (B_sat 1.48 T against 0.25–0.42 T for ferrite). The physics of the dilution is on [magnetic materials](../02-electromagnetics/magnetic-materials-permeability.md#level-2--powdered-iron-and-gapped-cores-the-distributed-air-gap).

| Core | μ | Temp. coefficient of μ | Q of the *material* (μ′/μ″) at 7.1 MHz | Use it for |
|---|---|---|---|---|
| Micrometals −6 (yellow) | 8.5 | +35 ppm/°C | ≈ 465 (eddy term) | tuned circuits, filters and traps 2–50 MHz, where stability matters |
| Micrometals −2 (red) | 10 | +95 ppm/°C | ≈ 370 | tuned circuits 0.5–30 MHz, a bit more L per turn |
| Micrometals −10 / −17 | 6 / 4 | +150 / +50 ppm/°C | high to 80 / 170 MHz | VHF tuned circuits |
| Fair-Rite 61 | 125 | 0.10 %/°C (1000 ppm) | 132 (falls to 2.6 at 28.5 MHz) | HF inductors below ≈ 15 MHz, wideband transformers, UHF suppression |
| Fair-Rite 52 | 250 | 0.8 %/°C | 4.4 | broadband transformers and suppression (μ″ 29 at 434 MHz) |
| Fair-Rite 43 | 800 | 1.25 %/°C | **1.0** | broadband (low-Q) transformers, CM chokes, suppression 20–250 MHz |
| Fair-Rite 31 | 1500 | 1.3 %/°C | 0.74 | CM chokes / suppression 1–300 MHz |

Fair-Rite temperature coefficients are averages over 20–70 °C. Iron-powder Q values are the core's eddy-current loss only, from Micrometals' loss formula; a real wound inductor's Q (typically 100–250) is set by the copper. **What the table means:** if you need a stable, high-Q *resonant* inductor (a VFO coil, a band-pass filter, a trap, a tuned EFHW coupler), use iron powder. If you need *many ohms of reactance with few turns over a decade of frequency*, and loss is acceptable or even wanted, use ferrite (broadband transformers, chokes, beads). Over a 40 °C swing a tuned circuit at 7.1 MHz drifts by 5 kHz on −6, 13.5 kHz on −2, 142 kHz on 61, and on 43 it shifts by about 25 %, which makes 43 unusable for tuning (script §3).

**A_L → turns.** $L=A_LN^2$, so $N=\sqrt{L/A_L}$ (A_L in nH/turn²). Iron-powder A_L values are specified to ±5 % and hold up to the mix's maximum frequency. Ferrite A_L is a 10 kHz value with ±20–25 % tolerance, and at RF you must use μ′(f) instead (script §4):

| Want | Core (A_L, nH/N²) | Turns |
|---|---|---|
| 1.0 µH (40 m filter) | T50-2 (4.9) | 14 |
| 2.0 µH (trap) | T68-6 (4.7) | 21 |
| 4.7 µH | T68-2 (5.7) | 29 |
| 10 µH broadband choke | FT240-61 (170) | 8 |
| "4.3 µH" | FT240-43 (1075) | 2, but at 7.1 MHz it is really 2.16 µH **plus 96 Ω of series loss** (μ′ = μ″ ≈ 395) |

Other A_L values: T37-2 4.0, T50-6 4.0, T106-2 13.5, T130-2 11, T200-2 12, T200-6 10.4, FT140-43 885 nH/N² [10][9]. To measure an unknown core, use the [bench recipe R10](../17-test-measurement/bench-measurement-recipes.md#r10--ferrite-cores-a_l-and-complex-permeability-d1-256-676).

**Gapped cores.** A gap of length $g$ in a core of path length $\ell_e$ gives $\mu_e=\mu/(1+\mu g/\ell_e)$. The temperature coefficient and the loss tangent are both diluted by the same factor $\mu_e/\mu$ (both scale with the share of the field energy stored in the ferrite). An FT240-sized 43 core needs a 3.4 mm gap to reach μ_e = 40. That gives about 630 ppm/°C and Q ≈ 20 at 7 MHz, still worse than a −6 core. Gaps are therefore used to carry DC without saturating (power chokes), not to make good HF tuned inductors.

**The EFHW 49:1 transformer.** The design is a 1:7 turns autotransformer (50 Ω → 2450 Ω), usually 2:14 or 3:21 turns on an FT240-43 or FT140-43 core [12]. The usual rule "magnetising reactance ≥ 4–5 × 50 Ω" assumes a high-Q core. Mix 43 at HF has Q ≈ 0.6–1.6, so the magnetising branch is about half resistor, and that resistor sits directly across the 50 Ω input. The share of the input power it takes is $G_m/(G_m+1/50)$ with $G_m=\mathrm{Re}\{1/Z_m\}$ and $Z_m=j\omega N_1^2(\mu_0A_e/\ell_e)(\mu'-j\mu'')$. FT240: A_e 1.58 cm², ℓ_e 14.5 cm, surface area ≈ 77 cm² [9]. Small-signal results at 100 W (script §6):

| Winding | 3.6 MHz | 7.1 MHz | 14.2 MHz | 28.5 MHz | B_pk at 3.6 MHz, 100 W |
|---|---|---|---|---|---|
| 2:14, one FT240-43 | 20.8 % (1.0 dB) | 20.6 % | 18.1 % | 15.3 % (0.7 dB) | 14 mT |
| 3:21, one core | 10.4 % (0.5 dB) | 10.3 % | 8.9 % | 7.5 % | 9.3 mT |
| 2:14, two stacked | 11.6 % | 11.5 % | 9.9 % | 8.3 % | 7.0 mT |
| 3:21, two stacked | 5.5 % (0.25 dB) | 5.4 % | 4.7 % | 3.9 % | 4.7 mT |

These are **lower bounds**, for two reasons. (1) Fair-Rite's large-signal data for 61 show measured loss 2–3.6× the small-signal (μ″) prediction at 7–14 mT and 2–15 MHz (Pv ∝ B^2.3–2.8, not B²). No such data are published for 43; if it behaves like 61, a single core on 80 m at 100 W loses well over 1 dB. (2) Copper loss and loss in the interwinding capacitance are not included.

**Heating.** Use the empirical Amidon rule $\Delta T\,[^\circ C]\approx(P_{mW}/A_{cm^2})^{0.833}$ for a core in still air [13]. For 2:14 on one FT240-43 at 7.1 MHz, 20.6 W in the core gives a steady rise of ≈ 105 °C at 100 W key-down. That is at the 43 Curie point (> 130 °C), where μ collapses and the transformer runs away thermally. At 20 % average duty (SSB) the rise is ≈ 27 °C, and at 50 % (FT8, alternating 15 s periods) it is ≈ 59 °C. For a 25 °C rise the core can dissipate ≈ 3.7 W, which allows **≈ 18 W average** input for 2:14 on one core, ≈ 35 W for 3:21 and ≈ 63 W for 2:14 on two stacked cores. An independent calculation from older 43 data reaches the same conclusion: 15.6 W continuous on 80 m and ≈ 90 W PEP CW/SSB [12]. Practical consequences:
- For 100 W digital modes, use 3 turns and/or two stacked FT240-43 cores.
- At QRP (≤ 10 W) an FT82-43 or FT140-43 is fine.
- Do not use iron powder for a *broadband* 49:1. Reaching |X_m| ≥ 250 Ω at 3.6 MHz takes a 30-turn primary and a 212-turn secondary on a T200-2, which self-resonates. Iron powder is right for the *tuned* QRP EFHW coupler (a parallel-resonant secondary on a T50-2/T68-2).

**Compensation capacitor.** The leakage inductance $L_{lk}$ (in series, referred to the primary) and the secondary's self-capacitance referred to the primary ($C_s'=49\,C_s$, so 2 pF looks like ≈ 100 pF) form a low-pass L-section that spoils the upper bands. A capacitor of 100–150 pF across the 50 Ω port turns it into a symmetric π section with $\sqrt{L_{lk}/C}\approx50\ \Omega$. In the illustrative model ($L_{lk}$ = 0.25 µH, $C_s'$ = 100 pF) it brings the 28.5 MHz VSWR from 2.35 to 1.38. 200 pF over-compensates (2.1 on 21–28 MHz). Your $L_{lk}$ and $C_s$ will differ, so measure them: with the secondary shorted, the primary reads $L_{lk}$; then trim C on the analyser with a 2.4 kΩ dummy load. At 100 W the capacitor carries **1.27 A rms at 28.5 MHz** (70.7 V rms, 100 V pk), so use a C0G or mica part rated ≥ 500 V and ≥ 2 A RF current, not a small ceramic disc. The secondary sits at 495 V rms (700 V pk) even at VSWR 1, so use PTFE-insulated wire.

## Design equations & rules of thumb

| Item | Equation / rule | Notes |
|---|---|---|
| Core impedance | $Z=j\omega L_0(\mu'-j\mu'')$, $L_0=4\pi N^2\cdot10^{-9}/C_1$ | $C_1=\sum\ell/A$ [cm⁻¹] |
| Turns scaling | $Z\propto N^2$ | until winding C resonates |
| DC field | $H=1.256NI/\ell_m$ Oe | $\ell_m$ in cm |
| Usable DC current | ≲ 20 % of rated if impedance matters | rated current is thermal |
| Bead–cap resonance | $f_r=1/(2\pi\sqrt{L_{bead}C})$ | use L from the inductive region |
| Damping resistor | $R\approx\sqrt{L/C}$ in a large-C branch | method C |
| Pick the bead by | its $|Z|$ at the noise frequency and at your DC current | not the 100 MHz headline |
| CM choke | $Z_{CM}\approx j\omega L(1+k)/2$, $Z_{DM}\approx2j\omega L(1-k)$ | — |
| Turns from A_L | $N=\sqrt{L/A_L}$ | powder ±5 % to max f; ferrite A_L at 10 kHz only |
| Gapped core | $\mu_e=\mu/(1+\mu g/\ell_e)$; tempco, tan δ × μ_e/μ | 43 FT240, 3.4 mm → μ_e 40 |
| Transformer core loss share | $G_m/(G_m+1/R)$, $G_m=\mathrm{Re}\{1/Z_m\}$ | 2:14 FT240-43, 7 MHz: 21 % |
| Peak flux | $B_{pk}=\sqrt2V_{rms}/(\omega N A_e)$ | 100 W, 2 t, 3.6 MHz: 14 mT |
| Core temperature rise | $\Delta T\approx(P_{mW}/A_{cm^2})^{0.833}$ | FT240 77 cm²: 3.7 W → 25 °C |
| EFHW compensation C | $\sqrt{L_{lk}/C}\approx50\ \Omega$ (π with $C_s'=49C_s$) | 100–150 pF, ≥ 500 V, ≈ 1.3 A at 28 MHz/100 W |

## Worked examples

### 1. Supply filter for a 2 W LoRa module (433 MHz)
Goal: keep the module's TX current pulses (≈1 A class) off a sensitive sensor rail, and keep 433 MHz pickup off the module supply.
- A bead rated 3 A at 100 Ω/100 MHz carries 1 A = 33 % of rating: expect its impedance to fall by roughly half or more — check the DC-bias curve. At 433 MHz a 100 MHz-rated bead may already be past its peak.
- Better: power the module from its own regulator (as on Space Bar's secondary FC, which gives the LoRa module a dedicated 5 V buck-boost) and use the bead on the *sensor* rail side, where current is small (tens of mA) and the bead stays unbiased.
- Size the bulk capacitor and damping so the bead–cap resonance is well away from the regulator's switching frequency; use method C.

### 2. GNSS receiver supply
u-blox receivers draw tens of mA; a GHz-band bead (e.g. ≥ 600 Ω at 1–2 GHz, BLM15GG/BLM18GG class) on VCC with a 100 nF + 10 nF local bypass works well at 1575 MHz — but check the anti-resonance of the capacitor pair near 1.5 GHz ([capacitors](capacitors-at-rf-mlcc.md)).

### 3. Cable ferrite on a USB or servo lead
Snap-on 31 material for 1–300 MHz noise; 2 turns through the core gives ≈4× the impedance of 1 turn at low-to-mid frequencies. For 433/915 MHz pickup on long leads, use small NiZn beads close to the entry point rather than large MnZn cores. At these frequencies the bead's size and position matter more than the mix (example 5).

### 4. A 100 W EFHW transformer for 40–10 m (and 80 m)
Wind 3:21 turns (1:7) of PTFE wire on two stacked FT240-43 cores, as an autotransformer, with 100 pF/1 kV C0G or mica across the 50 Ω port. Small-signal core loss is 5.4 % (0.24 dB) at 7.1 MHz and 3.9 % at 28.5 MHz. B_pk at 100 W is 2.4 mT at 7.1 MHz and 4.7 mT at 3.6 MHz, where the large-signal correction is still small. The core reaches ΔT ≈ 19 °C at 100 W key-down. The single-core 2:14 version that many kits use would lose ≈ 20 % and heat by ≈ 105 °C key-down, which is fine for SSB at 100 W PEP (≈ 27 °C) but not for FT8 at 100 W (≈ 59 °C, and more once large-signal loss is included). Check the result with two transformers back to back into 50 Ω, or one transformer into a 2.4 kΩ non-inductive load: half the back-to-back loss is the per-unit loss. Then run 5 minutes key-down at the planned power and feel the core.

### 5. 433 MHz, 2 W: choking the coax of a ground-station or rocket antenna
At 433.92 MHz every Fair-Rite mix has μ′ ≈ 0 and μ″ ≈ 24–29, so a bead is a pure resistor and the mix hardly matters. A slip-on bead of OD 7.5, ID 3.0, length 10 mm gives L₀ = 1.83 nH and **≈ 120–147 Ω per bead** (43: 120 − j6 Ω; 61: 124 + j16 Ω; 52: 147 Ω). Five beads in a row, within the first λ/4 (17 cm) of the feed, give ≈ 620 Ω common-mode. Worst case, with the whole 10 V rms feed voltage driving the shield path, they dissipate 161 mW (8 % of 2 W), or 32 mW per bead, a rise of ≈ 6 °C. Heating is not the problem. The cost is power: a choke on an antenna that really does drive its shield turns that shield current into heat. Fix the antenna's balance first (sleeve or λ/4 choke, [antenna baluns](../08-antennas/antenna-matching-and-baluns.md)) and use the beads as a back-up. Never use a ferrite-cored inductor as the 433 MHz RF choke in a PA bias feed (Q < 1). Use an air-core or ceramic chip inductor ([inductors](inductors-at-rf.md)).

## Practical notes
- **Read the full curve**: |Z|, R and X vs frequency, and |Z| vs DC current. Chip beads come in "general", "high-current" and "GHz" families (Murata BLM…A/…P/…G etc.) optimised for different regions.
- **Place the bead between the noise source and the thing you're protecting**, with the capacitor on the protected side; keep its ground return short.
- **Avoid beads in RF signal paths** (they are lossy and poorly characterised in phase); use them on supplies and control lines.
- **Beads in the PA supply path** add series impedance at the TX burst's current-edge frequencies (tens of kHz–MHz) → supply droop, possible AM of the carrier; place bulk decoupling *after* the bead and damp it.
- **Why cable ferrites are rarer than they were.** Common-mode chokes now sit on the PCB at the connector, as SMD parts designed into the product and passed at certification. Examples are USB/HDMI chokes, which give tens of dB of CM rejection with little loss to the differential signal [14]. Signalling has also moved to low-swing differential pairs in properly shielded, 360°-bonded cables, and snap-on lumps cost money and are usually added as a late compliance fix. *(Engineering inference with industry sources; no authoritative study found.)* Snap-ons are still the right field fix for a noisy legacy cable or a servo/power lead.
- **Thermal**: rated current means temperature rise; the bead's DC resistance (0.05–0.5 Ω) also drops voltage.

## Common mistakes & misconceptions
- **"600 Ω bead = 600 Ω at my frequency."** It's |Z| at 100 MHz with no DC. At 433/915 MHz or with DC it can be a fraction of that.
- **"Beads always reduce noise."** A bead plus a low-ESR capacitor is a resonant circuit that can add 10–30 dB of gain near its resonance (Burket [1]; practitioner reports [7]).
- **Running a bead near its rated current** and expecting its small-signal impedance.
- **Using a bead as an RF choke in a bias-T.** Its lossy impedance loads the RF line; use a proper RF inductor (or accept the loss knowingly).
- **Ignoring the bead's capacitive region**: above its peak, a bead passes high frequencies (e.g. 2.4 GHz) quite well.
- **"A_L = 1075 nH, so 2 turns on an FT240-43 is 4.3 µH at 7 MHz."** A_L is measured at 10 kHz. At 7.1 MHz μ′ ≈ 395 and μ″ ≈ 395, so the winding is 2.16 µH in series with 96 Ω. Use μ′(f), μ″(f).
- **"X_m ≥ 4 × 50 Ω is enough for a 49:1 transformer."** That rule assumes a high-Q core. With 43 (Q ≈ 1) the magnetising branch is a resistor across the input: 2:14 on one FT240-43 takes ≈ 20 % of the power, and you need |Z_m| ≳ 450 Ω for < 10 % loss.
- **"Iron powder is better than ferrite, full stop" (or the reverse).** Iron powder wins on Q, stability and saturation. Ferrite wins on ohms per turn and bandwidth. Choose by job: tuned or broadband.
- **"An EFHW transformer that runs warm is normal; just add power."** 43 heads for its > 130 °C Curie point, where μ collapses and the loss runs away. Size by average power (mode duty) and core count.
- **"The EFHW capacitor tunes the antenna."** It compensates the transformer's leakage inductance (a π low-pass with the secondary capacitance). It does not change the antenna's resonance and it is not a band switch.
- **"Use 61 at UHF, 43 is useless there."** At 434 MHz Fair-Rite's data give 43 and 61 nearly the same μ″ (24 vs 25). Size and position decide the choke, not the mix.
- **Wrong cable-ferrite mix**: large MnZn cores for VHF/UHF or small NiZn beads for 1 MHz noise are both ineffective.

## How to simulate / verify
- `python3 tools/verify/components_ferrite_bead.py` — bead R/X/|Z| model, bead–capacitor resonance and damping comparison, DC-bias collapse effect, Fair-Rite H rule, CM-choke impedances.
- `python3 tools/verify/s4_core_turns_loss.py` (output in `s4_core_turns_loss_output.txt`) — μ′/μ″ of 31/43/52/61 from Fair-Rite CSVs at 1.8 MHz–915 MHz; iron-powder Q from Micrometals' eddy term; tuned-circuit drift; A_L → turns; gapped μ_e; EFHW 49:1 loss, B_pk, ΔT, power limits for four windings; 61 large-signal loss ratio; compensation-capacitor VSWR sweep; 433 MHz bead impedance and dissipation.
- Vendor SPICE/S-parameter models (Murata SimSurfing includes DC-bias-dependent bead models; TDK, Würth REDEXPERT) — use the DC-bias version.
- Bench: VNA shunt-through measurement of the bead with a bias-T feeding DC current; supply ripple measured with a short-ground probe or 50 Ω coax pickoff.

## Open questions / gaps
- The bead model's behaviour above ~1 GHz is extrapolated from a fit ending at 803 MHz; for 915 MHz/2.4 GHz work use the vendor's measured curves.
- Fair-Rite publishes complex-permeability CSVs (now stored in `tools/verify/data/fairrite_mu_*.csv`). **Contradiction:** the older 43 data used by ON5UK/Owen Duffy (μ′ ≈ 470, Q 2.1 at 3.6 MHz) and Fair-Rite's 2020 CSV (μ′ 688, μ″ 423, Q 1.6) give a 2-turn FT240 |Z_m| of 64.5 vs 100 Ω. Both give ≈ 21–25 % loss for 2:14 on 80/40 m. Lot-to-lot spread is within the ±20 % A_L tolerance.
- No large-signal (B–P_v) data for 43 at HF; the 61 data are used as a proxy, so EFHW losses above ≈ 7 mT are lower bounds. No measured back-to-back EFHW loss was found in a reliable source. EFHW leakage inductance and secondary capacitance in the compensation example are illustrative values.

## Sources
1. C. Burket, "Ferrite beads demystified," *Analog Dialogue* 50-02, Feb. 2016 (also ADI AN-1368); reprint via Power Systems Design. https://www.powersystemsdesign.com/articles/ferrite-bead-demystified/95/10031 — bead model values, DC-bias data, bead–cap resonance (+10 dB near 2.5 MHz), damping methods. (app note)
2. Fair-Rite Products, "How to choose ferrite components for EMI suppression," catalog technical section, 14th ed. — complex permeability, $Z=j\omega L_0(\mu'-j\mu'')$, $L_0$, DC-bias field $H=1.256NI/\ell_m$, material table. https://taccomms.org/wp-content/uploads/2019/ham_radio/Choose-Ferrite-For-Emi.pdf (manufacturer technical note)
3. Fair-Rite, material data sheets: 31 (MnZn, µᵢ 1500, ρ 3000 Ω·cm, Tc > 130 °C), 43 (NiZn, µᵢ 800, ρ 10⁵ Ω·cm), 61 (NiZn, µᵢ 125, ρ 10⁸ Ω·cm, Tc > 300 °C). https://fair-rite.com/43-material-data-sheet/ (datasheet)
4. Murata, EMIFIL chip ferrite bead catalogs (BLM series incl. GHz-band BLM15GG). https://www.murata.com/search/productsearch?partno=BLM18 (datasheet)
5. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 — ch. 5 (ferrites, CM chokes), decoupling. (textbook)
6. C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley, 2006 — ferrite beads and common-mode chokes. (textbook)
7. Altium, "How to use (and not use) a ferrite bead in your design to reduce EMI"; All About Circuits, "Choosing and using ferrite beads" — practitioner accounts of bead–capacitor peaking (up to ~10 dB) with large bypass capacitors. https://resources.altium.com/p/how-use-ferrite-bead-your-design-reduce-emi ; https://www.allaboutcircuits.com/technical-articles/choosing-and-using-ferrite-beads/ (industry articles — secondary; misconceptions only)
8. Verification script `tools/verify/components_ferrite_bead.py` (this KB).
9. Fair-Rite Products, material pages and complex-permeability CSVs for 31, 43, 52, 61 (incl. temperature coefficient 20–70 °C, Curie temperature, resistivity) and the 61 "B vs Pv at 25 °C" CSV; toroid pages 5943003801 (FT240-43: A_L 1075 nH ±20 %, A_e 1.58 cm², ℓ_e 14.5 cm, V_e 22.8 cm³), 5961003801 (FT240-61, A_L 170 nH), 5943002701 (FT140-43, A_L 885 nH). https://fair-rite.com/43-material-data-sheet/ , https://fair-rite.com/61-material-data-sheet/ (datasheet; downloaded 2026-10-13)
10. Micrometals, *2019 Iron Powder RF Materials* catalogue — mixes −0…−17: reference μ, A_L tolerance, temperature coefficient, maximum frequency, B_sat, core-loss formula coefficients. https://www.acalbfi.com/media/pdf/RF_materials_micrometals_2019.pdf (datasheet)
11. Micrometals core datasheets T37-2, T50-2/-6, T68-2/-6, T106-2, T130-2, T200-2/-6 (A_L, A_e, ℓ_e, V_e, surface area). https://datasheets.micrometals.com/T200-2-DataSheet.pdf (datasheet)
12. L. ON5UK, "EFHW — resultaten" (Dutch, after ON9CVD and Amidon data): FT240-43 two-turn |Z|, Q, flux and dissipation-limited power per band, stacked-core variant. https://www.tls.uba.be/Files_Web_tls/EFHW_on5uk/EFHW_resultaten.pdf (amateur technical note — secondary; independent calculation that agrees with ours)
13. e-magnetica, "Thermal resistance of ferrite cores" — Amidon rule ΔT = (P[mW]/A[cm²])^0.833 for cores in free air. https://www.e-magnetica.pl/doku.php/thermal_resistance_of_ferrite_cores (wiki — empirical; ±30 % expected)
14. Coilcraft, EMI/common-mode choke product family for USB/HDMI/LVDS (https://www.coilcraft.com/prod_emi.cfm); Academy of EMC, "Inductors in EMC part 3: common-mode noise filtering" (https://www.academyofemc.com/post/inductors-in-emc-part-3-common-mode-noise-filtering). (manufacturer / industry — used only for the on-board-choke trend)
