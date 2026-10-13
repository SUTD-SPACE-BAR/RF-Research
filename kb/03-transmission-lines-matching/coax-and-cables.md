---
title: Coaxial lines and RF cables
domain: 03-transmission-lines-matching
slug: coax-and-cables
tags: [coax, coaxial-cable, 50-ohm, cable-loss, velocity-factor, lmr-400, rg-58, rg-316, rg-174, semi-rigid, u.fl, power-handling, phase-stability, ground-station, ladder-line, open-wire-line, twin-lead, twisted-pair, balanced-line, common-mode-choke]
prerequisites:
  - telegrapher-equations-characteristic-impedance.md
  - reflections-vswr-return-loss-mismatch.md
related:
  - input-impedance-stubs-quarter-wave.md
  - time-domain-reflectometry.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
  - ../13-pcb-rf-layout-emc/connectors-and-launches.md
  - ../18-components-parts/connectors-and-cables-parts.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../09-propagation-link-budget/link-budget-methodology.md
  - antenna-tuners-and-atus.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../06-rf-circuits/baluns-and-rf-transformers.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Coaxial lines and RF cables

## Questions this page answers
- How is the characteristic impedance of coax calculated from its dimensions?
- Why is 50 Ω the standard (and why is TV cable 75 Ω)?
- How much loss do RG-58, RG-174, RG-316, RG-402/405, LMR-195/240/400 and U.FL micro-coax have at 433, 915, 1575 and 2450 MHz?
- Which cable should I use for a LoRa ground station, and how much range does cable loss cost?
- How much power can a cable carry, and why does the rating fall with frequency?
- What limits the maximum frequency of a coax?
- Which cables are phase-stable (for arrays and interferometry)?
- How long can a U.FL pigtail be before it hurts a GNSS receiver?
- What is the impedance of ladder line or open-wire line, and why is it so low-loss at HF?
- How does ladder line compare with coax when the SWR is high?
- Does balanced line need a choke or balun?
- Can I use twisted pair or Ethernet cable as an RF feeder?

## TL;DR
- $Z_0=\dfrac{\eta_0}{2\pi\sqrt{\varepsilon_r}}\ln\dfrac Dd\approx\dfrac{60}{\sqrt{\varepsilon_r}}\ln\dfrac Dd$ Ω ($D$ = dielectric/outer-conductor inner diameter, $d$ = centre-conductor diameter). $VF=1/\sqrt{\varepsilon_r}$: solid PE 0.66, PTFE ≈ 0.69–0.70, foam PE 0.80–0.85.
- **Why 50 Ω**: for a fixed outer size, conductor loss is minimum at $D/d=3.591$ (**76.7 Ω** in air), peak power at breakdown is maximum at $D/d=\sqrt e$ (**30 Ω**), peak voltage at $D/d=e$ (60 Ω). 50 Ω is the compromise (arithmetic mean 53.5, geometric 48); a 50 Ω air line has only ≈10 % more loss than the optimum. With solid PE the minimum-loss geometry is itself 51 Ω; with foam (εr ≈ 1.4) it is ≈ 64 Ω, near 75 Ω video cable.
- **Loss** follows $A(f)=k_1\sqrt f+k_2f$ (conductor + dielectric). Interpolated datasheet values (dB per 10 m): at 433 MHz — LMR-400 0.87, LMR-240 1.7, LMR-195 2.5, RG-58 2.9, RG-174 6.4, RG-316 7.2; at 915 MHz — 1.3, 2.5, 3.7, 4.5, 10, 11.8. U.FL 1.13 mm: ≈1.4 dB/m at 433 MHz, 2.0 at 915, 2.6 at 1575, 3.7 at 3 GHz.
- **Ground station**: every dB of feeder loss before the first LNA costs ~11 % of free-space range. 10 m of RG-58 at 915 MHz (4.5 dB) cuts range to 59 %; LMR-400 (1.3 dB) keeps 86 %. Better: put the LNA/radio at the antenna.
- **Power**: average-power ratings are thermal: $P_\text{avg}\times\alpha\approx$ constant (LMR-400: 74 W·dB/m, i.e. the rated power always dissipates ≈ 0.23 × 74 ≈ 17 W per metre, from 50 MHz to 5.8 GHz). Peak power is set by dielectric breakdown/connector.
- **Upper frequency**: TE₁₁ cutoff $f_c\approx c/[\pi\sqrt{\varepsilon_r}(d+D)/2]$ (LMR-400: 16.3 GHz vs 16.2 GHz datasheet); datasheet max is usually lower (connector, braid, loss).
- **Balanced lines** ([§ below](#open-wire-ladder-line-and-twisted-pair)): two-wire $Z_0=\frac{\eta_0}{\pi\sqrt{\varepsilon_\text{eff}}}\cosh^{-1}(D/d)$ — 600 Ω for #12 wire at 150 mm, ≈ 400 Ω for commercial "450 Ω" window line (measured 359–405 Ω). Dry ladder line loses ≈ 0.6–0.7 dB/100 m at 14 MHz (RG-58: 4.4), so it tolerates high SWR (30 m at SWR 20: 1.6–1.7 dB vs 6.2 dB) — but **wet** line is 12–18× lossier, and open lines radiate and pick up when unbalanced or near metal. Twisted pair is a real ≈ 100–120 Ω balanced line (Cat 6A: 42 dB/100 m at 433 MHz, RG-58 29), but home-made PVC pairs are far lossier and unshielded.
- **Phase stability**: solid PTFE has a "knee" near 19 °C (≈ −130 ppm/°C between 15 and 25 °C); use phase-stable (special PTFE/foam) cables for arrays.

## Intuition (no math)
A coaxial cable is a transmission line whose fields are completely enclosed: the electric field points radially from the centre conductor to the shield, the magnetic field circles the centre conductor, and nothing leaks out (if the shield is perfect and currents are balanced). A thicker centre conductor relative to the shield means more capacitance and less inductance per metre — lower impedance. The dielectric slows the wave and raises capacitance.

Loss comes mostly from the resistance of the thin skin of metal the current flows in — especially the small centre conductor, whose surface is small, carrying the same current as the large shield. Make the cable bigger and the conductor surfaces grow, so loss per metre falls roughly as 1/diameter. That is the whole story of why LMR-400 (10.3 mm) loses a third of what RG-58 (4.9 mm) does, and why tiny 1.13 mm micro-coax is so lossy.

## The math

### Level 1 — the formulas
With $d$ the centre-conductor diameter, $D$ the inner diameter of the shield (≈ dielectric OD), $\varepsilon_r$ the dielectric constant:
$$L=\frac{\mu_0}{2\pi}\ln\frac Dd,\qquad C=\frac{2\pi\varepsilon_0\varepsilon_r}{\ln(D/d)},\qquad Z_0=\sqrt{\frac LC}=\frac{59.96}{\sqrt{\varepsilon_r}}\ln\frac Dd\ \Omega,\qquad v_p=\frac{c}{\sqrt{\varepsilon_r}}.$$
Loss (TEM, low loss): $\alpha=\alpha_c+\alpha_d$,
$$\alpha_c=\frac{R}{2Z_0},\ R=\frac{R_s}{\pi}\left(\frac1d+\frac1D\right),\ R_s=\sqrt{\frac{\pi f\mu_0}{\sigma}};\qquad \alpha_d=\frac{\pi\sqrt{\varepsilon_r}\tan\delta}{\lambda_0}\quad[\text{Np/m}].$$

### Level 2 — the "why 50 Ω" derivations
Fix the shield inner radius $b$ and vary the centre radius $a$; let $x=b/a$.

**Minimum conductor loss.** $\alpha_c=\dfrac{R_s(1/a+1/b)/(2\pi)}{2\cdot\frac{\eta}{2\pi}\ln x}\propto\dfrac{1+x}{\ln x}$ (after multiplying by $b$). Setting the derivative to zero: $\ln x=1+1/x$ → $x=3.591$ → $Z_0=60\ln3.591=76.7$ Ω in air; $76.7/\sqrt{\varepsilon_r}$ in a dielectric: 51.1 Ω (solid PE, 2.25), 53.3 Ω (PTFE, 2.07), ≈64 Ω (foam, 1.43). Script: the optimum is broad — a 50 Ω air line has 10.3 % more conductor loss, a 93 Ω line 2.6 % more.

**Maximum power at breakdown.** The peak field is at the centre conductor: $E_\text{max}=V/(a\ln x)$. Power $P=V^2/(2Z_0)\propto E_\text{max}^2a^2\ln x\propto\ln x/x^2$ at fixed $b$ → maximum at $x=\sqrt e=1.649$ → **30.0 Ω** (air).

**Maximum voltage at breakdown.** $V=E_\text{max}a\ln x\propto\ln x/x$ → $x=e$ → **60 Ω**.

No single impedance is best. 50 Ω sits between the 30 Ω (power) and 77 Ω (loss) optima (and at 50 Ω the power capacity is still 86 % of the 30 Ω maximum — script). The standard dates from coax development for kilowatt transmitters in the 1930s [7]. 75 Ω (video, CATV) is closer to the low-loss optimum for foam and was a compromise with conductor size/flexibility [7]. All optima verified numerically in `tools/verify/tline_coax.py`.

### Level 3 — real cables
- **Stranded, braided, clad conductors.** Stranded centre conductors (RG-174, RG-316) have an effective diameter below their overall diameter; nominal dimensions + VF give 45–46 Ω for these cables in the script, although they are 50 Ω cables. Braids add loss and leakage; copper-clad aluminium/steel centres (LMR-400 CCA, RG-402/405 CCS) are fine at RF because the current flows in the copper skin (skin depth ≈ 3 µm at 433 MHz), but CCS/CCA raise DC resistance (relevant for bias-tee-powered masthead LNAs).
- **Theory vs datasheets.** Foil-shield LMR-400 and solid-shield RG-402 are within 1–12 % of smooth-copper theory; braided RG-58 exceeds it by 10–26 % (telegrapher-page script).
- **Loss law and datasheet sanity checks.** Every table except one fits $k_1\sqrt f+k_2f$ within 5 %. The Fairview RG-316 table is not consistent (its 1→3 GHz rise is 1.53× where √3 = 1.73 would be the *minimum* for conductor loss) — treat its 3 GHz figure with suspicion.
- **Higher-order modes.** The first non-TEM mode (TE₁₁) cuts off at $k_c\approx2/(a+b)$: $f_c\approx\dfrac{c}{\pi\sqrt{\varepsilon_r}(a+b)}$. LMR-400: 16.3 GHz (datasheet 16.2 GHz); RG-402: 34 GHz (datasheet max 34 GHz); RG-405: ≈60 GHz (rated 40 GHz, connector-limited).
- **Power handling.** Average power is limited by heating of the centre conductor/dielectric: allowed dissipation per metre is fixed, so $P_\text{avg}\propto1/\alpha$. LMR-400's table has $P\times\alpha$ = 7400 ± 3 % W·dB/100 m from 50 MHz to 5.8 GHz — i.e. the rating is "the power at which the cable dissipates ≈ 17 W per metre" (dissipation per metre $P(1-10^{-\alpha/10})\approx0.2303\,P\,\alpha_{\text{dB/m}}$ = 0.23 × 74 W). Ratings drop with high ambient temperature, altitude (air cooling), and VSWR (current maxima).
- **Phase vs temperature and flexure.** Solid PTFE dielectric has a crystalline transition near 19 °C producing a phase "knee" (≈ −130 ppm/°C between +15 and +25 °C vs ≈ −30 ppm/°C below) and some hysteresis; ordinary PTFE cables drift 200–600 ppm/°C; phase-stable designs use modified PTFE or foam to reach < 50 ppm/°C [9], [10]. For a phased array feed: 1 m of cable is 7.2 wavelengths at 1.575 GHz (VF 0.7) → 200 ppm = 0.5° — matters for interferometric GNSS or calibrated arrays, not for a single LoRa link.

### Open-wire, ladder line and twisted pair
**Level 1.** A balanced line is two identical conductors carrying equal and opposite currents; the field is concentrated between and around the wires, and nothing encloses it. For two round wires of diameter d at centre spacing D,
$$Z_0=\frac{\eta_0}{\pi\sqrt{\varepsilon_\text{eff}}}\cosh^{-1}\frac Dd\approx\frac{120}{\sqrt{\varepsilon_\text{eff}}}\ln\frac{2D}{d}\ \Omega\quad(D\gg d).$$
#12 AWG (2.05 mm) at 150 mm in air: 598 Ω ("600 Ω open-wire"). #16 (1.29 mm) at 19 mm: 406 Ω — N7WS measured 399 Ω on such a line [12]. Commercial "450 Ω" window line (wires in a slotted polyethylene web, $VF$ ≈ 0.9) measured **359–405 Ω** dry and ≈ 4 % lower wet [12] — treat "450 Ω" as a name. 300 Ω twin-lead (#22 in solid PE ribbon) and ≈ 100–120 Ω twisted pairs complete the family.

**Level 2 — why the loss is so low.** Conductor loss is $\alpha_c=R'/(2Z_0)$ with, for two wires and the proximity effect,
$$R'=\frac{2R_s}{\pi d}\,\frac{D/d}{\sqrt{(D/d)^2-1}},\qquad R_s=\sqrt{\pi f\mu_0/\sigma}.$$
A high $Z_0$ means a small current for the same power, so $I^2R$ falls; and the wire surface is larger than a small coax's centre conductor. This model gives **0.297 dB/100 ft at 50 MHz** for the #16 line, against **0.30 dB/100 ft measured** [12] (`tools/verify/s6_ladder_line.py`). Commercial window line measured 0.33–0.41 dB/100 ft dry at 50 MHz; scaled by $\sqrt f$ this is 0.175–0.217 dB/100 ft at 14 MHz — consistent with the 0.2 dB/100 ft assumed on the [ATU page](antenna-tuners-and-atus.md). **Wet** it measured 4.8–6.1 dB/100 ft, **12–18× worse**: a water film on the web adds a dielectric loss right where the field is strongest. Copper-clad-steel wires are fine where the copper is thicker than a few skin depths (δ = 35 µm at 3.6 MHz), worse at the lowest HF bands.

**Matched loss (dB/100 m)** — models and datasheet fits (script):

| f (MHz) | 600 Ω open wire (#12) | 450 Ω window line (measured, √f-scaled) | 300 Ω twin-lead (model) | Cat 6A pair (TIA limit fit) | home-made 24 AWG PVC pair (model) | RG-58 | LMR-400 |
|---|---|---|---|---|---|---|---|
| 3.6 | 0.11 | 0.29–0.36 | 0.69 | 3.5 | 3.6 | 2.2 | 0.77 |
| 14 | 0.22 | 0.57–0.71 | 1.4 | 6.9 | 8.6 | 4.4 | 1.5 |
| 28 | 0.31 | 0.81–1.01 | 2.0 | 9.9 | 14 | 6.3 | 2.2 |
| 144 | 0.71 | 1.8–2.3 | 4.6 | 23 | 48 | 15 | 5.0 |
| 433 | 1.2 | 3.2–4.0 | 8.3 | 42 | ≈ 120 | 29 | 8.7 |

(Cat 6A from the TIA-568-C.2 cable limits 19.1 dB at 100 MHz and 45.3 dB at 500 MHz [13], fitted to $k_1\sqrt f+k_2f$; the PVC pair assumes a filling-weighted tanδ of 0.015, so its UHF figure is only indicative. RG-58/LMR-400 below 50 MHz are extrapolations of the fits above.)

**Loss versus SWR.** The total loss of a line with matched loss $A$ (ratio $a=10^{A/10}$) at load reflection |Γ| is $10\log_{10}\frac{a^2-|\Gamma|^2}{a(1-|\Gamma|^2)}$ ([reflections](reflections-vswr-return-loss-mismatch.md), derived on the [ATU page](antenna-tuners-and-atus.md)). For 30 m at 14 MHz:

| Line | matched | SWR 3 | SWR 10 | SWR 20 |
|---|---|---|---|---|
| RG-58 | 1.31 | 1.92 | 4.14 | 6.15 dB |
| LMR-400 | 0.46 | 0.72 | 1.87 | 3.14 dB |
| 450 Ω ladder, dry (0.2–0.22 dB/100 ft) | 0.20–0.21 | 0.32–0.35 | 0.90–0.97 | 1.63–1.74 dB |
| 450 Ω ladder, wet (50 MHz wet figure scaled ∝ f — an assumption) | 1.68 | 2.40 | 4.89 | 7.04 dB |

And the SWR itself is lower on ladder line when the antenna impedance is high (a 2000 + j500 Ω load is SWR 42 on 50 Ω but 4.7 on 450 Ω — ATU page). This is the case for "one antenna, many bands, tuner at the rig". In the rain, though, wet ladder line can be as lossy as RG-58.

**Level 3 — balance, common mode and chokes.** A balanced line only behaves as a line for the *differential* (equal-and-opposite) current. Any common-mode current — from an asymmetric antenna, a feedline not perpendicular to the antenna, a nearby mast, or an unbalanced tuner — flows on both wires in the same direction, radiates, and brings RF into the shack. Keep the line ≥ 2–3 spacings away from metal, run it perpendicular to the antenna, twist it a half turn every metre or so to average out coupling, and at the transition to coax or an unbalanced tuner use a **1:1 current balun / common-mode choke** whose choking impedance is high and mostly resistive (K9YC's guidance is several kΩ, ≥ 5 kΩ for transmitting chokes — via [14]) — see [ATU page](antenna-tuners-and-atus.md) "ladder line needs no balun", [antenna baluns](../08-antennas/antenna-matching-and-baluns.md) and [RF transformers and baluns](../06-rf-circuits/baluns-and-rf-transformers.md). Open lines also radiate from discontinuities and imbalance, a loss that grows with $(\beta D)^2$: at 433 MHz a 25 mm spaced line has $\beta D$ ≈ 0.23, which is one reason open lines are an HF/VHF technique and coax is used at UHF.

**Twisted pair.** It *is* a transmission line: Ethernet pairs are specified as 100 Ω balanced lines to 500 MHz (Cat 6A) and beyond, and twisted enamelled pairs are the windings of transmission-line transformers and baluns. As an antenna feeder it has four problems: (1) its 100–120 Ω balanced impedance needs a balun to reach 50 Ω coax-world equipment; (2) it is unshielded, so any imbalance (connector, nearby metal, a carbon-fibre airframe) turns into common-mode pickup and radiation; (3) loss depends on the insulation — FEP/PE data cable at 433 MHz is ≈ 42 dB/100 m (1.4× RG-58), PVC hook-up pairs several times worse (≈ 120 dB/100 m in the model above); (4) its impedance is poorly controlled unless made as cable (±15 %), and it handles little power. Short pairs inside equipment are fine; for an antenna feed use coax.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $Z_0=\frac{59.96}{\sqrt{\varepsilon_r}}\ln\frac Dd$ | TEM coax | LMR-400: 2.74/7.24 mm, εr 1.38 → 49.6 Ω |
| $VF=1/\sqrt{\varepsilon_r}$ | homogeneous dielectric | PE 0.66, PTFE 0.69–0.70, foam 0.80–0.85 |
| $A(f)=k_1\sqrt f+k_2f$ | datasheet interpolation | see table |
| Loss ∝ 1/diameter (same materials) | rough scaling | 2× diameter ≈ ½ loss |
| $b/a$ = 3.591 / √e / e | min loss / max power / max voltage | 76.7 / 30 / 60 Ω in air |
| $f_c(TE_{11})\approx c/[\pi\sqrt{\varepsilon_r}(a+b)]$ | coax | LMR-400 16 GHz, RG-402 34 GHz |
| $P_\text{avg}\alpha\approx$ const | thermal rating | LMR-400 ≈ 74 W·dB/m |
| Range factor $10^{-A/20}$ | free-space link, loss before LNA / after PA | 3 dB → 0.71 |
| Two-wire $Z_0=\frac{\eta_0}{\pi\sqrt{\varepsilon_\text{eff}}}\cosh^{-1}(D/d)$ | balanced line | #12 at 150 mm: 598 Ω |
| $\alpha_c=R'/2Z_0$, $R'=\frac{2R_s}{\pi d}\frac{D/d}{\sqrt{(D/d)^2-1}}$ | open-wire conductor loss | #16 at 19 mm: 0.30 dB/100 ft @ 50 MHz |
| Total loss $10\log\frac{a^2-\lvert\Gamma\rvert^2}{a(1-\lvert\Gamma\rvert^2)}$ | any line at SWR | 30 m ladder, SWR 20: 1.6 dB |

**Attenuation, interpolated from manufacturer tables (dB/100 m; k₁, k₂ fitted with f in MHz):**

| Cable (source) | OD | VF | k₁ | k₂ | 433 | 868 | 915 | 1575 | 2450 | 5800 |
|---|---|---|---|---|---|---|---|---|---|---|
| LMR-400 (L-com/Times) [1] | 10.3 mm | 0.85 | 0.403 | 0.00082 | 8.7 | 12.6 | 12.9 | 17.3 | 22.0 | 35.5 |
| LMR-240 [1] | 6.1 mm | 0.84 | 0.796 | 0.00109 | 17.0 | 24.4 | 25.1 | 33.3 | 42.0 | 66.9 |
| LMR-195 [1] | 4.95 mm | 0.80 | 1.169 | 0.00157 | 25.0 | 35.8 | 36.8 | 48.9 | 61.7 | 98.1 |
| RG-58 (Belden 8240) [2] | 4.9 mm | 0.66 | 1.123 | 0.0123 | 28.7 | 43.8 | 45.2 | 64* | 86* | — |
| RG-174 (Fairview) [3] | 2.8 mm | 0.66 | 2.63 | 0.0220 | 64 | 97 | 100 | 139* | 184* | — |
| RG-316 (Fairview) [3] | 2.6 mm | 0.69 | (poor fit) | | 72† | 114† | 118† | 149† | 176† | — |
| RG-402 semi-rigid 0.141″ (Pasternack) [4] | 3.6 mm | 0.695 | 1.031 | 0.0039 | 23 | 34 | 35 | 47 | 61 | 101 |
| RG-405 semi-rigid 0.086″ (Pasternack) [4] | 2.2 mm | 0.695 | 2.19 | 0.0042 | 47 | 68 | 70 | 94 | 119 | 191 |
| U.FL 1.13 mm micro-coax (Hirose) [5] | 1.13 mm | ≈0.7 | 6.30 | 0.0094 | 135 | 194 | 199 | 265 | 335 | 534 |

(* = extrapolated beyond the datasheet's rated/tabulated range — RG-58 is rated to 1 GHz, RG-174 to 1 GHz. † = piecewise log-log interpolation of the Fairview table, because that table does not follow $k_1\sqrt f+k_2f$. U.FL fit uses only the 3 and 6 GHz points, so its UHF values are an extrapolation of the loss law.) Times Microwave's own LMR-400 equation ($0.12229\sqrt f+0.00026f$ dB/100 ft) matches its table within 3 %.

## Worked examples

### Example 1 — ground-station feeder for 433 MHz and 915 MHz LoRa
A Yagi on a 10 m mast run: loss (script) for 10 m / 20 m —

| | 433 MHz, 10 m | 433 MHz, 20 m | 915 MHz, 10 m | 915 MHz, 20 m |
|---|---|---|---|---|
| LMR-400 | 0.87 dB | 1.75 dB | 1.29 dB | 2.59 dB |
| LMR-240 | 1.70 dB | 3.41 dB | 2.51 dB | 5.01 dB |
| LMR-195 | 2.50 dB | 5.00 dB | 3.68 dB | 7.36 dB |
| RG-58 | 2.87 dB | 5.74 dB | 4.52 dB | 9.05 dB |

On receive, feeder loss before the first amplifier adds almost directly to the system noise figure (a passive loss of $L$ dB at ≈290 K is a noise figure of $L$ dB — [Friis](../07-noise-linearity/noise-figure-and-friis.md)), so it reduces sensitivity dB-for-dB unless the sky/antenna noise dominates. In free-space conditions range scales as $10^{-L/20}$: RG-58 at 915 MHz over 10 m keeps only 59 % of the range, LMR-400 86 %. For a 30 km rocket downlink this is the difference between 17.7 km and 25.8 km. The better architecture: put the receiver (or a masthead LNA with a SAW filter) at the antenna and run USB/Ethernet/DC down the mast → [ground station design](../15-lora-ism-radios/ground-station-design.md).

### Example 2 — flight harness: U.FL pigtail lengths
From the table: 10 cm of 1.13 mm micro-coax costs 0.14 dB at 433 MHz, 0.20 dB at 915 MHz and 0.27 dB at 1575.42 MHz (20 cm: 0.27/0.40/0.53 dB). For the GNSS receiver (passive patch → U.FL → module) every 0.1 dB before the LNA raises the noise figure by ≈0.1 dB and lowers C/N₀ by ≈0.1 dB-Hz — keep the pigtail < 10 cm or use an active antenna ([GNSS antennas](../08-antennas/gnss-antennas.md)). For the 2 W 433 MHz module, 30 cm of RG-316 (0.22 dB) wastes ≈ 0.1 W as heat — trivial electrically, but the cable's rating near a hot motor section and its 30-mating-cycle U.FL connector are the real concerns.

### Example 3 — check a cable's impedance from its datasheet
LMR-400: $d=2.74$ mm, $D=7.24$ mm, VF 0.85 → $\varepsilon_r=1.384$ → $Z_0=\frac{59.96}{1.176}\ln2.642=49.6$ Ω; $1/(v_pC)=1/(0.85c\times78.41\text{ pF/m})=50.05$ Ω. Both ≈ 50 Ω: this datasheet is self-consistent. (Belden RG-58 is not: 49.8 / 54.1 / "52" Ω — see the telegrapher page.)

### Example 4 — power: can RG-316 carry the 2 W E22 output?
Easily — RG-316-class PTFE cables are rated for tens to hundreds of watts at 433 MHz; the limit is its SMA/U.FL connector (U.FL is specified for signal use; see [connectors](../13-pcb-rf-layout-emc/connectors-and-launches.md)). With VSWR 3 on the cable, current maxima are 1.5× the matched value → local heating 2.25× in those regions; derate accordingly.

## Practical notes
- **Connector choice** matters as much as cable: U.FL is rated DC–6 GHz, VSWR ≤ 1.3–1.5, and only **30 mating cycles** [5] — secure it (hot glue/Kapton or a retention clip) against rocket vibration and never use it as a bench connector; use an SMA or MMCX bulkhead for anything re-mated.
- **Minimum bend radius**: LMR-400 25 mm once / 102 mm repeated [1]; kinks change $Z_0$ locally (visible on [TDR](time-domain-reflectometry.md)).
- Handling practice (torque, cleaning, weatherproofing, phase matching, NanoVNA cable tests, 75 Ω on 50 Ω): [coax and connector practicalities](../18-components-parts/coax-and-connector-practicalities.md).
- **Outdoor**: UV-rated PE jackets; water ingress into braid/foam raises loss permanently — seal N/SMA connectors with self-amalgamating tape.
- **Common-mode**: the shield's outer surface is a separate conductor — chokes/baluns at the antenna keep current off it ([reflections page](reflections-vswr-return-loss-mismatch.md)).
- **Measure what you bought**: a NanoVNA S21 through the cable (after a THRU cal) gives loss vs frequency; a TDR shows Z0 and connector quality.

## Common mistakes & misconceptions
- **"RG-58 is fine for everything."** At 915 MHz it loses 4.5 dB per 10 m — more than a factor 2 in power.
- **"Thicker is always better."** Loss falls with size, but flexibility, weight (rocket), bend radius and connector availability suffer; in the airframe short thin cables are fine.
- **"The cable's power rating is a fixed number."** It falls as $1/\alpha$ with frequency and with temperature/altitude/VSWR.
- **"75 Ω cable is fine for a 50 Ω system if short."** Short 75 Ω sections are a 1.5:1 mismatch at each end; they transform the load (up to VSWR 2.25 for a λ/4 section — [reflections](reflections-vswr-return-loss-mismatch.md)).
- **"VF 0.66 for any coax"** — foam and PTFE differ (0.80–0.85, 0.69–0.70).
- **"Ladder line is lossless."** Dry, at HF, it is 5–20× better than RG-58; wet it can be 12–18× worse than dry — about RG-58 territory.
- **"Ladder line needs no balun or choke."** Any unbalance puts common-mode current on it; choke at the unbalanced transition.
- **"Twisted pair isn't a transmission line."** It is (≈ 100 Ω, used to 500 MHz in Ethernet); it is a poor *antenna feeder* because it is unshielded, balanced and lossy with PVC insulation.
- **Trusting datasheet tables blindly** — check them against $k_1\sqrt f+k_2f$; inconsistent points exist (RG-316 example).

## How to simulate / verify
- `tools/verify/s6_ladder_line.py` — two-wire Z0 and conductor loss vs N7WS's measured line, window-line range vs the ATU page's assumption, matched-loss table, Cat 6A fit, loss vs SWR (reproduces the ATU page's ladder row). All pass.
- `tools/verify/tline_coax.py` — formula vs scikit-rf, datasheet self-consistency, optimum-ratio derivations, loss-law fits and interpolation table, theory vs datasheet, TE₁₁ cutoffs, thermal power law, ground-station and pigtail examples. All pass.
- scikit-rf: `rf.media.Coaxial(frequency, Dint, Dout, epsilon_r, tan_delta, sigma)` builds a physical coax; `rf.media.DefinedAEpTandZ0` builds a line from a measured attenuation/permittivity; for a datasheet cable, use `DefinedGammaZ0` with $\alpha(f)$ from the fitted $k_1,k_2$ (see the reflections page snippet).

## Open questions / gaps
- Huber+Suhner / Times primary datasheets for RG-316, RG-174 and LMR were accessed via distributor copies (L-com, Fairview, Pasternack); primary Times Microwave PDFs returned HTTP 403.
- Braid transfer impedance and shielding effectiveness are not modelled (→ [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).
- Peak-power (breakdown) numbers for small cables and connectors are not tabulated.
- Balanced lines: measured ladder-line loss is a single amateur data set at 50 MHz (N7WS via KB6NU); the wet-loss frequency scaling is assumed (∝ f); radiation loss of open line versus frequency and spacing is stated qualitatively only; the K9YC choke guidance was read via a secondary summary.

## Sources
1. L-com (Infinite Electronics), LMR-400 / LMR-240 / LMR-195 datasheets (Times Microwave Systems data), rev. 2019 — https://www.l-com.com/Images/Downloadables/Datasheets/ds_LMR-400.pdf (and -240, -195) — dimensions, VF, capacitance, attenuation and CW power 50 MHz–5.8 GHz. (datasheet)
2. Belden, 8240 RG-58 technical data sheet, rev. 0.541 (2026) — https://catalog.belden.com/techdata/EN/8240_techdata.pdf. (datasheet)
3. Fairview Microwave, RG174 (rev 1.4) and RG316 (rev 1.5) datasheets — https://www.fairviewmicrowave.com/ (product-datasheets/RG174.pdf, RG316.pdf). (datasheet)
4. Pasternack, RG402/U and RG405/U semi-rigid datasheets — https://www.pasternack.com/images/ProductPDF/RG402-U.pdf, RG405-U.pdf. (datasheet)
5. Hirose Electric, *U.FL Series* catalog (2020) — frequency range, VSWR, 30 mating cycles, micro-coax attenuation at 3 and 6 GHz. (datasheet)
6. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — §2.2 (coax L, C, Z0), §2.7 (coax loss), §3.5 (coax higher-order modes). (textbook)
7. Microwaves101, "Why fifty ohms?" — https://www.microwaves101.com/encyclopedias/why-fifty-ohms — 30/77 Ω optima, 1930s transmitter origin (citing A. S. Gilmour, *Microwave Tubes*), 64 Ω foam optimum and 75 Ω rationale. (web tutorial; numbers re-derived here)
8. Times Microwave Systems, LMR-400 attenuation equation (0.12229 √f + 0.00026 f dB/100 ft) as quoted in the LMR-400 datasheet. (datasheet)
9. Times Microwave Systems, "Current innovations in phase stable coaxial cable design," https://timesmicrowave.com/current-innovations-in-phase-stable-coaxial-cable-design/ — PTFE knee, ppm/°C figures. (manufacturer article)
10. Microwave Journal, "Minimizing temperature induced phase errors in coaxial cables" (2017) — https://www.microwavejournal.com/articles/27954 — PTFE knee 18–24 °C, 200–600 ppm/°C vs < 50 ppm/°C phase-stable. (trade journal)
11. Verification: `tools/verify/tline_coax.py`, `tools/verify/tline_telegrapher.py`. (numerical check)
12. D. Romanchik (KB6NU), "You're all wet!", 2016, summarising W. Stewart (N7WS), "Balanced transmission lines in current amateur practice" — measured Z0 and loss (dry/wet) of four commercial 450 Ω ladder lines and a home-made #16 open-wire line at 50 MHz. https://www.kb6nu.com/youre-all-wet/ (amateur measurement, secondary)
13. ANSI/TIA-568-C.2 category cable limits as reproduced by Superior Essex technical guides TG039 (Cat 6A: 19.1 dB/100 m at 100 MHz, 45.3 dB/100 m at 500 MHz) and TG041 (Cat 5e: 22.0 dB/100 m at 100 MHz). (standard, via vendor reproduction)
14. J. Brown (K9YC), *A Ham's Guide to RFI, Ferrites, Baluns, and Audio Interfacing* and the transmitting-choke cookbook (2018), as summarised at https://pa0nhc.nl/CommonModeChokes/indexE.htm — resistive choking impedance ≥ 5 kΩ. (amateur engineering guide, via secondary)
15. Verification: `tools/verify/s6_ladder_line.py`. (numerical check)
