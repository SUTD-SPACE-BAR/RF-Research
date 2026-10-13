---
title: Inductive coupling — mutual inductance, coupling coefficient, resonant links and the k²Q₁Q₂ limit; RFID (LF/HF/UHF), NFC antenna design and matching, Qi wireless power
domain: 08-antennas
slug: inductive-coupling-rfid-nfc-wpt
tags: [inductive-coupling, mutual-inductance, neumann, coupling-coefficient, resonant-coupling, wpt, wireless-power, qi, rfid, nfc, iso14443, iso15693, 13.56-mhz, 125-khz, uhf-rfid, load-modulation, emc-filter, near-field]
prerequisites: [loop-antennas.md, ../01-circuit-theory/transformers-coupled-inductors.md, ../01-circuit-theory/resonance-and-q.md, ../02-electromagnetics/inductance-capacitance-from-fields.md, ../02-electromagnetics/near-field-far-field.md]
related: [antenna-fundamentals.md, small-antenna-limits.md, ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md, ../04-real-components-hf/inductors-at-rf.md, ../04-real-components-hf/ferrites-and-beads.md, ../19-regulations-safety/rf-exposure-safety.md, ../02-electromagnetics/skin-effect-conductor-loss-roughness.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Inductive coupling: RFID, NFC and wireless power

## Questions this page answers
- How do two coils "talk" or transfer power without radiating, and why is this not an antenna in the usual sense?
- How do I calculate the mutual inductance of two coils (Neumann formula, coaxial loops)?
- What is the coupling coefficient k, and how fast does it fall with distance?
- Why does making both coils resonant help so much, and what is the maximum link efficiency?
- Where does η_max = U²/(1+√(1+U²))² with U = k√(Q₁Q₂) come from?
- How did the MIT "WiTricity" experiment get 40 % efficiency at 2 m?
- How do I design and match a 13.56 MHz NFC/RFID reader antenna (inductance, Q, damping resistor, EMC filter, C1/C2)?
- Why must an NFC antenna's Q be limited to about 20–35?
- How far can an NFC reader read, and what coil size is best for a given distance?
- How do 125 kHz LF tags and 860–960 MHz UHF RFID tags differ from NFC?
- How does a Qi wireless charger work, and what are its coil values?
- Does metal or a ferrite sheet behind an NFC antenna help or hurt?
- How do I build my own RFID reader?
- Can I harvest useful power from ambient RF or from a far-away transmitter?

## TL;DR
- **Inductive links work in the reactive near field** (distance ≪ λ/2π: 3.5 m at 13.56 MHz, 382 m at 125 kHz). The coils exchange energy through mutual inductance M; they hardly radiate — a 45 mm 4-turn NFC coil has R_rad ≈ 6 µΩ against ≈ 1.3 Ω of loss (radiation efficiency ≈ 5 × 10⁻⁶).
- **Mutual inductance**: Neumann $M=\frac{\mu_0}{4\pi}\oint\oint\frac{d\mathbf l_1\cdot d\mathbf l_2}{R}$; coaxial circular loops have Maxwell's closed form in elliptic integrals (verified to < 10⁻⁴ against the double integral, `tools/verify/ant2_inductive.py`). **k = M/√(L₁L₂)** falls roughly as (R/d)³ beyond d ≈ R: two 25 mm-radius loops: k = 0.43, 0.27, 0.098, 0.028, 0.005 at d = 5, 10, 25, 50, 100 mm.
- **Resonant links**: with both coils tuned and an optimal load, the best possible efficiency depends only on the figure of merit **U = k√(Q₁Q₂)**: $\eta_\max=U^2/(1+\sqrt{1+U^2})^2$, reached at $R_L=R_2\sqrt{1+U^2}$ (derived below; checked exactly by numerical load optimisation). 50 %, 80 %, 90 % need U = 2.8, 8.9, 19.
- **"Strongly coupled magnetic resonances"** (Kurs et al., *Science* 2007) are this same physics with very high Q (≈ 10³): 60 W at ≈ 40 % over > 2 m with 30 cm-radius coils [1]; our circuit estimate with Q = 950 gives k = 2.5 × 10⁻³, U = 2.4, η_max ≈ 44 % at 2 m.
- **NFC reader antenna** (NXP AN11755 [2]): La 0.3–3 µH, Ra 0.1–2 Ω, self-resonance ≥ 25 MHz, **Q 20–35** (damp with RQ = ½(ωLa/35 − Ra) per side), EMC low-pass L0 = 160–560 nH resonant at 15.5–17 MHz, then series C1 / shunt C2 to present Rmatch ≈ 30 Ω at the TX pins.
- **Worked 13.56 MHz coil**: 45 × 45 mm, 4 turns, 0.5/0.5 mm → **L = 1.70 µH** (own filament model; Mohan current-sheet 1.704 µH), Q ≈ 114 → RQ = 1.78 Ω/side for Q = 30 → with L0 = 160 nH, C0 = 659 pF: **C1 = 60.7 pF, C2 = 97.2 pF per side** (exact solve; AN11755's approximate formulas agree to 0.4 %).
- **Field needed**: ISO/IEC 14443 cards need 1.5–7.5 A/m [2]; that coil with 100 mA rms gives 3.8 A/m at 20 mm but 1.1 A/m at 40 mm — NFC is a few-centimetre technology. For a target distance d the coil radius that maximises the on-axis field is **a = √2·d**.
- **Qi** (WPC): inductive, not radiating; baseline transmitters resonate their coil with a fixed tank at **100 kHz and operate 110–205 kHz** (A5/A11: 400 nF ⇒ ≈ 6.3 µH coil), regulating power by moving off resonance [3].
- **UHF RFID (860–960 MHz) is different**: far-field backscatter with a real antenna (T-match dipole); forward-link range ≈ 8–25 m at 4 W EIRP depending on chip sensitivity (−14 to −22 dBm).

## Intuition (no math)
Two coils near each other are a loosely coupled transformer. Current in coil 1 makes a magnetic field; some of that flux threads coil 2 and induces a voltage. The fraction of coil 1's flux that reaches coil 2 is the coupling coefficient k: close to 1 in a power transformer with a shared core, a few percent for an NFC phone over a reader, a fraction of a percent at "mid range". Nothing needs to propagate as a wave: the field is the quasi-static near field that every coil has, falling like 1/r³ along the axis.

Why is weak coupling usable at all? Because resonance amplifies currents. If coil 2 is tuned with a capacitor, the small induced voltage drives a current limited only by the coil's own loss resistance — Q times larger than it would otherwise be. Tune coil 1 too and it carries Q times more current for the same drive. What matters is not k alone but k combined with the two quality factors. When k√(Q₁Q₂) ≫ 1, energy sloshes back and forth between the coils faster than either coil loses it, and most of it can be taken out by the load. That is "strongly coupled resonance" — not a new force, just high-Q coupled resonators.

Why isn't this an antenna? An antenna's job is to convert circuit power into a propagating wave, measured by radiation resistance. A 13.56 MHz coil the size of a credit card is 1/500 of a wavelength across; its radiation resistance is micro-ohms, so essentially none of the power leaves as radiation. The reader "sees" the tag the way a transformer primary sees its secondary load: when the tag switches a resistor or capacitor across its coil (load modulation), the reader's coil impedance changes slightly, and the reader detects that. At UHF (915 MHz) the tag antenna is a real resonant dipole and the reader is metres away, in the far field: there the tag works by *backscatter* — switching its antenna impedance to modulate the wave it reflects.

## The math

### Level 1 — the formulas you use
Symbols: L₁, L₂ self-inductances (H); M mutual inductance (H); k coupling coefficient (–); R₁, R₂ coil loss resistances (Ω); Q = ωL/R; R_L load resistance (Ω); a loop radius (m); d axial separation (m); N turns; I current (A rms); μ₀ = 4π × 10⁻⁷ H/m.

| Quantity | Formula | Notes |
|---|---|---|
| Coupling coefficient | $k=M/\sqrt{L_1L_2}$ | 0 ≤ k ≤ 1 |
| Thin circular loop self-inductance | $L\approx\mu_0 a[\ln(8a/r_w)-2]$ (HF, surface current); −1.75 instead of −2 at DC | wire radius r_w ≪ a; ×N² for a tight N-turn coil |
| Coaxial loops, far apart (d ≫ a) | $M\approx \frac{\mu_0\pi a_1^2a_2^2}{2d^3}$ (×N₁N₂) | magnetic-dipole limit |
| On-axis field of a loop | $H=\dfrac{NIa^2}{2(a^2+d^2)^{3/2}}$ (A/m) | maximum vs a at a = √2 d |
| Resonant-link figure of merit | $U=k\sqrt{Q_1Q_2}$ | both coils resonant |
| Maximum efficiency | $\eta_\max=\dfrac{U^2}{(1+\sqrt{1+U^2})^2}$, at $R_L=R_2\sqrt{1+U^2}$ | series- or parallel-tuned, optimal load |
| Critical coupling (splitting threshold) | $k_c\approx1/\sqrt{Q_1Q_2}$ | above it the transfer peak splits to $f_0/\sqrt{1\pm k}$ |
| Radiation resistance of an N-turn loop | $R_r=31\,171\,(NA/\lambda^2)^2$ Ω | from [loop-antennas](loop-antennas.md) |

### Level 2 — derivations

**(a) Neumann's formula.** The vector potential of a current I₁ on loop 1 is $\mathbf A(\mathbf r)=\frac{\mu_0 I_1}{4\pi}\oint\frac{d\mathbf l_1}{|\mathbf r-\mathbf r_1|}$ (quasi-static: all dimensions ≪ λ). The flux through loop 2 is $\Phi_{21}=\oint\mathbf A\cdot d\mathbf l_2$ (Stokes), so
$$M=\frac{\Phi_{21}}{I_1}=\frac{\mu_0}{4\pi}\oint_1\oint_2\frac{d\mathbf l_1\cdot d\mathbf l_2}{|\mathbf r_1-\mathbf r_2|},$$
symmetric in 1 ↔ 2 (reciprocity, M₁₂ = M₂₁). For two coaxial circles of radii a, b at axial distance d, $d\mathbf l_1\cdot d\mathbf l_2=ab\cos(\phi_1-\phi_2)\,d\phi_1 d\phi_2$, and the double integral reduces to complete elliptic integrals (Maxwell):
$$M=\mu_0\sqrt{ab}\left[\Big(\frac{2}{\kappa}-\kappa\Big)K(\kappa)-\frac{2}{\kappa}E(\kappa)\right],\qquad \kappa^2=\frac{4ab}{(a+b)^2+d^2}.$$
Our script compares this with brute-force numerical integration of Neumann's double integral: 67.537 nH = 67.537 nH (a = b = 5 cm, d = 2 cm), agreement < 10⁻⁴ in all cases. Grover's *Inductance Calculations* tabulates the same function for practical coil shapes [4].

**Self-inductance from the same formula.** Treat the wire as a filament on its axis and evaluate M between the axis filament (radius a) and a filament on the wire surface (radius a − r_w): this "geometric mean distance" trick gives the HF self-inductance (current on the surface). Script: 292.6 nH vs μ₀a[ln(8a/r_w) − 2] = 294.3 nH (a = 50 mm, r_w = 0.5 mm), < 1 % for r_w/a ≤ 0.01.

**(b) Planar spirals.** For square PCB spirals with n turns, outer side d_out, inner d_in, Mohan et al. [5] give, with $d_\text{avg}=(d_\text{out}+d_\text{in})/2$ and fill ratio $\rho=(d_\text{out}-d_\text{in})/(d_\text{out}+d_\text{in})$:
- modified Wheeler: $L=2.34\,\mu_0 n^2 d_\text{avg}/(1+2.75\rho)$;
- current sheet: $L=\tfrac{1.27}{2}\mu_0 n^2 d_\text{avg}[\ln(2.07/\rho)+0.18\rho+0.13\rho^2]$.
Our own partial-inductance model (each straight trace segment a thin strip; Grover's mutual inductance of parallel filaments; orthogonal segments contribute nothing) gives 1.701 µH for the 45 mm/4-turn coil: current-sheet 1.704 µH (+0.2 %), modified Wheeler 1.585 µH (−6.8 %); for 60 mm/3 turns and 30 mm/6 turns the differences are +0.2 %/−6 % and +0.2 %/−3 %. (Mohan's fits were made for on-chip spirals; the current-sheet form transfers better to large, hollow PCB coils. The pre-registered "both within 6 %" check missed narrowly for modified Wheeler — reported, not tuned.)

**(c) Maximum efficiency of a resonant two-coil link.** Series-tuned primary (R₁, L₁, C₁) and secondary (R₂, L₂, C₂) with load R_L in series with the secondary, both resonant at ω. KVL with $e^{j\omega t}$ phasors (reactances cancel at resonance):
$$V_1=R_1I_1+j\omega M I_2,\qquad 0=j\omega M I_1+(R_2+R_L)I_2\ \Rightarrow\ I_2=-\frac{j\omega M}{R_2+R_L}I_1 .$$
The secondary reflects into the primary a *resistance* $R_\text{ref}=(\omega M)^2/(R_2+R_L)$. Efficiency = (fraction of input power that crosses into the secondary) × (fraction of secondary power that reaches the load):
$$\eta=\frac{R_\text{ref}}{R_1+R_\text{ref}}\cdot\frac{R_L}{R_2+R_L}.$$
Write $x=R_L/R_2$ and $U^2=(\omega M)^2/(R_1R_2)=k^2Q_1Q_2$ (since $\omega M=k\omega\sqrt{L_1L_2}=k\sqrt{Q_1R_1Q_2R_2}$). Then
$$\eta(x)=\frac{U^2x}{(1+x)(1+x+U^2)}.$$
Setting dη/dx = 0: $(1+x)(1+x+U^2)=x(2+2x+U^2)$ ⇒ $x^2=1+U^2$ ⇒ $x_\text{opt}=\sqrt{1+U^2}$, and substituting,
$$\eta_\max=\frac{U^2}{\left(1+\sqrt{1+U^2}\right)^2}.\quad\blacksquare$$
Limits: U ≪ 1 ⇒ η ≈ U²/4 (efficiency ∝ k² ∝ d⁻⁶ at long range); U ≫ 1 ⇒ η ≈ 1 − 2/U. Inverting, U = 2√η/(1 − η). The script finds the optimum load numerically for four (k, Q₁, Q₂) sets and matches the formula to 10⁻⁶; the same η_max holds for parallel tuning and for the four-coil (drive loop + resonator + resonator + load loop) arrangement of Kurs et al., in which the small loops are just impedance transformers that set the effective R_L.

**(d) Frequency splitting.** Two identical resonators coupled by k have normal modes at $\omega_0/\sqrt{1\pm k}$. When k exceeds roughly $1/\sqrt{Q_1Q_2}$ (critical coupling), the power-transfer curve splits into two peaks and the efficiency at f₀ *falls* if the load is fixed — the classic "my wireless charger works worse when the coils touch" effect, handled by retuning, frequency tracking or adaptive matching (Sample, Meyer & Smith 2011 [6]). At Q = 30, k_c ≈ 0.033 (NFC phone on a reader is often above it); at Q = 950, k_c ≈ 0.001.

### Level 3 — limits and refinements
- **Quasi-static validity.** Neumann's formula ignores retardation; it is accurate for coil size ≪ λ (e.g., < λ/20: 1.1 m at 13.56 MHz). Kurs's coils (0.6 m across at ≈ 10 MHz, λ ≈ 30 m) are near the edge; their self-resonance came from the helix's own distributed capacitance, and their radiation (electric- and magnetic-dipole) was a non-negligible part of Γ [1].
- **Proximity effect and AC resistance.** Skin depth at 13.56 MHz is 17.9 µm; a 35 µm trace is "two skin depths thick" so R_ac ≈ 1.3 R_dc, and closely spaced turns crowd current further (proximity effect). We allow ×1.5; measure Q with a VNA (impedance at 13.56 MHz) — AN11755 asks for exactly this [2]. Above ~Q = 60 the coil is usually *damped deliberately*.
- **Ferrite and metal.** A coil on metal induces eddy currents that oppose its flux: L and Q fall and the resonance moves up — a reader antenna directly on a PCB ground pour or battery can lose most of its range. A thin ferrite sheet (μ' ≫ 1, low μ'' at 13.56 MHz) between coil and metal gives the flux a low-reluctance return path and restores L and Q; typical result: Q drops to < 35 even before damping [2]. In Qi, ferrite shields are mandatory both for k and for keeping fields out of the phone.
- **Radiation and regulation.** Even though radiation is tiny, the H-field at 10 m and the harmonics are regulated (e.g., ETSI EN 300 330 in Europe; 47 CFR 15.225 in the US; see [19](../19-regulations-safety/spectrum-allocation-ism-bands.md)); the EMC low-pass between the reader IC and the antenna exists to remove the square-wave driver's harmonics.
- **Human exposure.** Inductive WPT at kW level is limited by induced current density/SAR, not by far-field power density (link [rf-exposure-safety](../19-regulations-safety/rf-exposure-safety.md)).

## RFID and NFC by band
| Band | Coupling | Standards (examples) | Typical range | Antenna |
|---|---|---|---|---|
| LF 125/134.2 kHz | inductive (near field, λ/2π ≈ 360–380 m) | EM4100-class, ISO 11784/5 (animal), HDX/FDX-B | 2–10 cm (small tags), up to ~1 m with big gate coils | mH-class coils, often on ferrite; 1 mH ↔ 1.62 nF at 125 kHz |
| HF 13.56 MHz | inductive | ISO/IEC 14443 A/B (proximity, NFC), ISO/IEC 15693 (vicinity), ISO/IEC 18092 / NFC Forum | 14443: 0–10 cm; 15693: up to ~1 m with large reader loops | 0.3–3 µH coils, a few turns |
| UHF 860–960 MHz | far-field backscatter | EPC Gen2 / ISO/IEC 18000-63 | 2–25 m | resonant dipoles (T-match), meanders, loops |
| 2.45 GHz | backscatter / active | ISO/IEC 18000-4 | 1–10 m | patches/dipoles |
(Band/standard map after Finkenzeller [7]; ranges are indicative.)

**Load modulation (HF/LF).** The tag switches a load (resistive or capacitive) across its tuned coil at a subcarrier — fc/16 = 847.5 kHz for ISO 14443 — so the reader sees sidebands at 13.56 ± 0.8475 MHz on its own antenna voltage. This is why the reader antenna's Q cannot be too high (next section).

**UHF RFID tags (D2 #43, #109).** The chip input is capacitive (order of 10–30 Ω − j100…200 Ω at 915 MHz, chip-dependent — check the datasheet), so the tag antenna is designed to be *inductive* with the conjugate impedance: a dipole with a **T-match** (a short loop across the centre that adds inductance and steps the resistance), or a small **inductively coupled loop** feeding a separate radiating dipole/meander — the common "loop in the middle, wiggly arms outside" inlay. Read range is usually limited by the forward link (chip power-up): $r=\frac{\lambda}{4\pi}\sqrt{\frac{P_\text{EIRP}G_\text{tag}\tau}{P_\text{th}}}$, τ = power-transfer (match) coefficient. With 4 W EIRP, G_tag 0–2 dBi, τ = 0.9: **7.8–10 m at −14 dBm chip sensitivity, 20–25 m at −22 dBm** (`ant2_inductive.py` §12).

## NFC / HF RFID antenna design (13.56 MHz)

**Step 1 — coil.** Choose the outline from the target distance (a ≈ √2 d maximises H on axis at distance d; bigger coils reach further but couple less to small cards) and 2–6 turns to land L in 0.3–3 µH [2]. Keep self-resonance ≥ 25 MHz (Ca 3–30 pF). Measure La, Ra (series equivalent at 13.56 MHz).

**Step 2 — Q.** Q sets two competing things (script §10):
| Q | 847.5 kHz sideband attenuation | ring-down time Q/(πf) |
|---|---|---|
| 10 | −4.1 dB | 0.23 µs |
| 20 | −8.6 dB | 0.47 µs |
| 30 | −11.8 dB | 0.70 µs |
| 60 | −17.6 dB | 1.41 µs |
| 114 (undamped example) | −23.1 dB | 2.68 µs |
High Q gives more field per ampere of driver current but eats the card's load-modulation sidebands and smears the reader's 2–3 µs ASK pauses (106 kbit/s Type A). NXP's guidance is **Q = 20–35**, implemented by series damping resistors $R_Q=\tfrac12(\omega L_a/35-R_a)$ per side [2].

**Step 3 — EMC filter.** L0 (160–560 nH) and C0 to ground on each TX output, resonant at 15.5–17 MHz [2] — a low-pass that removes driver harmonics and, being above 13.56 MHz, transforms the driver load.

**Step 4 — matching.** Series C1 and shunt C2 (per side, symmetric) transform the damped antenna to the target resistance Rmatch at the TX pins (≈ 30 Ω for small antennas with the PN7150 [2]). Half-circuit (virtual ground at the antenna's centre): source Rmatch/2 → L0 → node A (C0 to ground) → C1 → node B (C2 to ground) → La/2 in series with (Ra + 2RQ)/2, with 2Ca across it. Solve backwards: the impedance required at node A is $Z_A=\big[(R_\text{match}/2-j\omega L_0)^{-1}-j\omega C_0\big]^{-1}$; C2 sets the real part of the antenna branch's admittance-transformed impedance equal to Re Z_A, and C1 supplies the remaining reactance. This is just an L-match ([impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).

**Step 5 — measure and trim** on the final housing with a VNA across TX1/TX2, then tune the Rx divider [2].

## Far-field RF energy harvesting (rectennas) — why ambient RF powers almost nothing
Beyond the near field, power arrives as a wave and Friis applies: $P_r=P_\text{EIRP}G_r(\lambda/4\pi d)^2$. Numbers (`tools/verify/ant2_qa.py` §i, 2 dBi receive antenna): **1 W EIRP at 915 MHz, 10 m → −19.7 dBm (10.7 µW)**; 4 W at 3 m → −3.2 dBm (0.48 mW); 1 W at 2.45 GHz, 1 m → −8.2 dBm; 0.2 W at 2.45 GHz, 5 m → −29 dBm (1.2 µW). Ambient cellular/TV/Wi-Fi levels at typical distances are −40 to −60 dBm (0.1–100 nW). Diode rectifiers need a few hundred mV to conduct efficiently, so conversion efficiency collapses at low input: of order 50–70 % near 0–10 dBm, tens of % around −20 dBm, a few % or less below −30 dBm (survey trend after Valenta & Durgin 2014 [10]; cited, not re-derived). Hence: dedicated-transmitter harvesting (UHF RFID tags, 915 MHz power beacons at a few metres) works for µW sensors; "free power from ambient RF" yields nW (D3 #38, D1 rank 38). Exposure and EIRP limits cap the transmitter ([19](../19-regulations-safety/rf-exposure-safety.md)).

## Design equations & rules of thumb
| Quantity | Equation / value | Valid | Typical |
|---|---|---|---|
| Near-field boundary | λ/2π | — | 382 m (125 kHz), 3.52 m (13.56 MHz), 5.2 cm (915 MHz) |
| k of coaxial equal loops | 0.43 / 0.10 / 0.03 at d/R = 0.2 / 1 / 2 | single-turn, thin wire | falls ≈ (R/d)³ for d ≫ R |
| Link efficiency | $\eta_\max=U^2/(1+\sqrt{1+U^2})^2$ | resonant, optimal load | U = 2.8 → 50 %, 8.9 → 80 % |
| Weak-link limit | η ≈ k²Q₁Q₂/4 | U ≪ 1 | ∝ d⁻⁶ |
| Optimal load | $R_L=R_2\sqrt{1+U^2}$ | series-tuned secondary | — |
| Loop field on axis | $NIa^2/[2(a^2+d^2)^{3/2}]$ | quasi-static | best a = √2 d |
| ISO 14443 field | 1.5–7.5 A/m | PCD operating volume | [2] |
| NFC coil | La 0.3–3 µH, Ra 0.1–2 Ω, f_self ≥ 25 MHz | NXP readers | [2] |
| NFC Q target | 20–35 | 106 kbit/s | RQ = ½(ωLa/35 − Ra) |
| EMC filter | L0 160–560 nH, f_r0 15.5–17 MHz | NXP readers | 160 nH ↔ 659 pF (→ 560 pF std) |
| Qi baseline Tx | tank resonance 100 kHz, operation 110–205 kHz | A5/A11 | 400 nF, ≈ 6.3 µH [3] |
| Qi2 MPP | ≈ 360 kHz | magnetic alignment | secondary sources only |
| LF tag tank | LC = 1/(2π·125 kHz)² | — | 1 mH ↔ 1.62 nF |

## Worked examples

**Example 1 — 13.56 MHz reader antenna, from coil to capacitors** (`ant2_inductive.py` §6). PCB coil 45 × 45 mm, 4 turns, 0.5 mm trace and gap, 35 µm copper.
1. Inductance: d_in = 45 − 2(4 × 0.5 + 3 × 0.5) = 38 mm; filament model **L = 1.701 µH** (current-sheet 1.704 µH). X_L = ωL = **145 Ω**.
2. Loss: trace length 663 mm; skin depth 17.9 µm; R_dc 0.65 Ω; skin-effect R_ac 0.85 Ω; with a ×1.5 proximity allowance **Ra ≈ 1.3 Ω** → **Q ≈ 114** (measure it!). Self-resonance with Ca ≈ 4 pF: 61 MHz (> 25 MHz ✔). Radiation resistance 6.2 µΩ: radiation efficiency 5 × 10⁻⁶ — it is not a radiator.
3. Damping to Q = 30: RQ = ½(145/30 − 1.28) = **1.78 Ω per side** (use 1.8 Ω).
4. EMC filter: L0 = 160 nH, f_r0 = 15.5 MHz → C0 = 1/((2π·15.5 MHz)² × 160 nH) = **659 pF** (AN11755 rounds to 560 pF; we keep 659 pF to compare with its formulas).
5. Matching to Rmatch = 30 Ω differential: required Z_A = 19.63 + j12.34 Ω; the half-antenna's parallel resistance is 2177 Ω; exact solution **C1 = 60.7 pF, C2 = 97.2 pF per side** (e.g., 56 pF + 4.7 pF; 82 pF + 15 pF, C0G). Check: Z_match = 30.0 + j0.0 Ω at 13.56 MHz; 4.0 + j2.0 Ω at 13.00 MHz and 7.5 − j17.3 Ω at 14.00 MHz — the match is narrow, so tolerance (C0G 2 %) and the housing matter.
6. Cross-check with AN11755's approximate formulas (5)–(6): C1 = 60.4 pF, C2 = 97.1 pF (−0.4 %, −0.1 %) — but only when Rtr is taken as the *differential* transformed resistance R_match/[(1 − ω²L0C0)² + (ωR_matchC0/2)²]; halving it, as the text layout of eq. (3) can be read, gives 87.8/73.6 pF (+45 %/−24 %). Use the exact L-match if in doubt.
7. Field: equivalent circular loop radius √(A/π) = 23.4 mm; at 100 mA rms antenna current, H = 3.76 A/m at 20 mm, **1.10 A/m at 40 mm** (below the 1.5 A/m ISO 14443 minimum) → expect ≈ 3–4 cm operating distance, or raise the current to 200 mA (2.2 A/m at 40 mm).

**Example 2 — How far can a 125 kHz reader read a key fob?** (`ant2_inductive.py` §13) Reader coil a = 40 mm, N = 60, I = 0.2 A rms: on-axis H = NIa²/[2(a² + d²)^{3/2}] = **36.6 A/m at 50 mm, 7.7 A/m at 100 mm, 2.6 A/m at 150 mm, 1.1 A/m at 200 mm**. A 20 mm-diameter, 100-turn tag coil picks up V_oc = ωNAμ₀H = 1.13 V, 0.24 V, 0.08 V, 0.035 V rms; its resonant tank (Q ≈ 20, assumed) multiplies that to 23, 4.8, 1.6, 0.7 V. A tag chip that needs roughly 1.5–2 V to run (assumed; chip-dependent) therefore works to ≈ 15 cm — the typical "a few cm to ~15 cm" of hobby 125 kHz readers. Note how the range is set by the d⁻³ fall-off: doubling the reader current buys only 26 % more distance.

**Example 3 — Reproducing the WiTricity result.** Two copper helices, radius 30 cm, 5.25 turns, 3 mm wire radius, 20 cm long, ≈ 10 MHz (parameters as reported by Kurs et al. [1]; the paper's numbers were not re-read here). Wheeler's short-solenoid formula: L ≈ 20.8 µH, X ≈ 1290 Ω; skin-effect loss 0.43 Ω and magnetic-dipole radiation 0.08 Ω ⇒ ideal Q ≈ 2500. The paper's measured Q (≈ 950) is lower (proximity effect and electric-dipole radiation of the self-resonant helix). Coupling of the helices treated as N-turn loops: k = 2.5 × 10⁻³ at 2 m. With Q = 950: U = 2.4 ⇒ **η_max = 44 %** (paper: ≈ 40 % at > 2 m, 60 W). At 1 m: k = 0.017, U = 16 ⇒ 88 %. "Mid-range" WPT is therefore a high-Q game: U falls as d⁻³, so efficiency collapses quickly beyond a few coil diameters.

**Example 4 — Qi coil.** TI's A5/A11 transmitter controller needs a total 400 nF tank for 100 kHz resonance [3] ⇒ L = 1/((2π·100 kHz)² × 400 nF) = **6.33 µH**. The controller operates between 110 and 205 kHz, *above* resonance, and lowers power by raising frequency (moving down the resonance skirt). A 20 mm-radius pair of single-turn air loops at 3/5/8 mm gap has k = 0.53/0.40/0.29 (our filament model) — Qi pads use ferrite backing to raise and stabilise k and to shield the phone.

## Practical notes
- **Measure L and Q first** (VNA in impedance mode at 13.56 MHz, or the series-equivalent readout of an LCR meter at the operating frequency). Calculated Q of PCB coils is usually optimistic.
- **Use C0G/NP0 capacitors** for C0, C1, C2 (tolerance and temperature stability: a 2 % change in C detunes a Q = 30 resonance by 1 % ≈ a third of its bandwidth). AN11755 also lists L0 current rating (≥ 210 mA) and C voltage ratings [2].
- **Metal nearby**: a battery, ground pour or aluminium enclosure under the coil reduces L and Q and can kill operation; use a ferrite sheet and tune in the final assembly.
- **"Build my own RFID reader"** (D1 #171): for 13.56 MHz, use a reader IC (NXP PN5180/PN7150/MFRC522-class, ST ST25R) with its antenna design note and tune the antenna as above; at 125 kHz, a coil + series capacitor driven by a 125 kHz square wave plus an envelope detector is enough to read simple read-only tags (EM4100-class).
- **WPT for rockets?** For charging/arming on the pad through a fibreglass airframe, an inductive link of two coaxial coils a few cm apart easily reaches U > 10 (k ≈ 0.1, Q ≈ 100) — efficiency > 80 % — but check that the 100–200 kHz field does not couple into pyro lines; inductive links are near-field and fall off fast, which is good for EMC.

## Common mistakes & misconceptions
- **"NFC/RFID coils are antennas that radiate."** In the far-field sense, no: radiation efficiency ≈ 10⁻⁶–10⁻⁵ at 13.56 MHz for card-sized coils. They are transformer windings.
- **"Strongly coupled magnetic resonance is a special non-radiative mechanism."** It is ordinary coupled-mode resonance; the figure of merit k√(Q₁Q₂) says everything, and the same η_max formula applies to Qi and NFC.
- **"Higher Q is always better."** For power transfer yes (U ∝ √Q₁Q₂), for NFC data no: Q > ~35 attenuates the 847.5 kHz load-modulation sidebands and slows the ASK pauses.
- **"Matching for maximum power transfer maximises efficiency."** The conjugate-matched load gives at most 50 % efficiency on the secondary side; the efficiency-optimal load is $R_L=R_2\sqrt{1+U^2}$ — larger than R₂.
- **"Closer is always better."** Above critical coupling the response splits and the fixed-frequency efficiency (and NFC detuning) gets worse when coils are too close — retune or use frequency tracking.
- **"A bigger reader coil always reads further."** The on-axis field at distance d is maximised at a = √2 d; a much larger coil spreads its flux and couples worse to a small tag at short range.
- **"Ferrite blocks the field."** A ferrite sheet *behind* a coil concentrates and guides flux, raising L and protecting against metal; it only "blocks" in the sense of shielding the far side.
- **"UHF RFID is just higher-frequency NFC."** UHF tags are far-field backscatter devices with real antennas; ranges of metres, completely different design.

## How to simulate / verify
- `python3 tools/verify/ant2_inductive.py` — Maxwell vs Neumann, loop self-inductance, k vs distance, η_max derivation check, Mohan vs filament model for PCB spirals, the 13.56 MHz coil/damping/EMC/C1–C2 example (exact vs AN11755), field vs distance, Q trade-off, frequency splitting, UHF RFID range, Qi tank, Kurs plausibility. Output saved in `tools/verify/ant2_inductive_output.txt`.
- Circuit: any SPICE ([16 spice-circuit-simulation](../16-simulation-tools/spice-circuit-simulation.md)) with a K (coupling) element reproduces the link equations; NXP's NFC Antenna Design Tool does the same for their ICs [2].
- Fields: FastHenry/quasi-static solvers for coil L and M; openEMS works but needs long runs at 13.56 MHz (λ = 22 m) — a magnetostatic or MoM-quasi-static tool is the right choice.
- Measure: VNA S11 → series R, L of the coil; two-port S21 between coils → k from the split-mode frequencies or from |Z21| = ωM.

## Open questions / gaps
- Mohan coefficient tables were read from search snippets (the PDF tables are images); checked numerically against our filament model (current-sheet form agrees to 0.3 %).
- Kurs et al. coil parameters and measured Q quoted from memory of the paper (paywalled); abstract numbers (60 W, ≈ 40 %, > 2 m, 8 radii) verified.
- Qi2 MPP frequency (≈ 360 kHz) only from secondary sources; the WPC specification was not read.
- UHF RFID chip impedances and sensitivities are indicative; read a chip datasheet (e.g., Impinj, NXP UCODE) for real designs.
- ISO/IEC 15693 field limits (≈ 0.15–5 A/m) quoted from memory/Finkenzeller, not from the standard.

## Sources
1. A. Kurs, A. Karalis, R. Moffatt, J. D. Joannopoulos, P. Fisher, M. Soljačić, "Wireless power transfer via strongly coupled magnetic resonances," *Science* 317(5834), 83–86, 2007. https://www.science.org/doi/10.1126/science.1143254 — 60 W, ≈ 40 %, > 2 m, up to 8 coil radii (abstract read; coil details cited from the paper, not re-read). (peer-reviewed)
2. NXP Semiconductors, *AN11755 PN7150 Antenna Design and Matching Guide*, rev. 1.7, 2019. https://www.nxp.com/docs/en/application-note/AN11755.pdf — antenna L/R/C ranges, Q 20–35 and RQ formula, EMC filter values, Rtr/Xtr and C1/C2 formulas, Rmatch ≈ 30 Ω, ISO 14443 1.5–7.5 A/m, metal/ferrite remarks (app note; READ via pdftotext).
3. Texas Instruments, *bq500212A Low System Cost Wireless Power Controller for WPC TX A5 or A11*, data sheet (SLUSB...); https://www.ti.com/lit/ds/symlink/bq500212a.pdf — 400 nF tank for 100 kHz resonance, 110–205 kHz operation, power control by frequency (datasheet; READ). Wireless Power Consortium, Qi specification overview, https://www.wirelesspowerconsortium.com (standard body; not read in detail).
4. F. W. Grover, *Inductance Calculations*, Van Nostrand 1946 / Dover 2004 — Neumann formula, coaxial-circle and polygon inductance tables. (book; cited)
5. S. S. Mohan, M. del Mar Hershenson, S. P. Boyd, T. H. Lee, "Simple accurate expressions for planar spiral inductances," *IEEE J. Solid-State Circuits* 34(10), 1419–1424, 1999. https://web.stanford.edu/~boyd/papers/pdf/inductance_expressions.pdf (peer-reviewed; read; coefficients from search snippets + numerical check)
6. A. P. Sample, D. T. Meyer, J. R. Smith, "Analysis, experimental results, and range adaptation of magnetically coupled resonators for wireless power transfer," *IEEE Trans. Ind. Electron.* 58(2), 544–554, 2011 — frequency splitting, critical coupling, adaptive tuning. (peer-reviewed; cited)
7. K. Finkenzeller, *RFID Handbook*, 3rd ed., Wiley, 2010 — LF/HF/UHF bands, inductive coupling and load modulation, backscatter, standards map. (handbook; cited)
8. C. A. Balanis, *Antenna Theory*, 4th ed., 2016, ch. 5 (loops: radiation resistance); this KB's [loop-antennas](loop-antennas.md) (R_r = 31 171 (NA/λ²)²). (textbook)
9. This repository: `tools/verify/ant2_inductive.py` (+ `_output.txt`); `tools/verify/ant2_qa.py` §i (far-field harvesting). (verification)
10. C. R. Valenta and G. D. Durgin, "Harvesting wireless power: survey of energy-harvester conversion efficiency in far-field, wireless power transfer systems," *IEEE Microwave Magazine* 15(4), 108–120, 2014. (peer-reviewed; cited)
