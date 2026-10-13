---
title: Input impedance, stubs, quarter-wave and half-wave lines
domain: 03-transmission-lines-matching
slug: input-impedance-stubs-quarter-wave
tags: [input-impedance, stub, quarter-wave-transformer, half-wave, impedance-inverter, resonant-line, electrical-length, velocity-factor, harmonic-trap, bias-tee, radial-stub, butterfly-stub, bias-line, distributed-structures]
prerequisites:
  - telegrapher-equations-characteristic-impedance.md
  - reflections-vswr-return-loss-mismatch.md
related:
  - smith-chart.md
  - impedance-matching-lumped-and-distributed.md
  - planar-lines-microstrip-stripline-cpwg.md
  - coax-and-cables.md
  - ../01-circuit-theory/resonance-and-q.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../06-rf-circuits/couplers-dividers-combiners.md
  - microstrip-discontinuities.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Input impedance, stubs, quarter-wave and half-wave lines

## Questions this page answers
- What impedance do I see looking into a length of line terminated in some load?
- Why does a quarter-wave line turn a short into an open (and 12.5 Ω into 200 Ω)?
- How long must a piece of coax be to act as a quarter wave at 433 MHz?
- How can a piece of open or shorted line replace an inductor or capacitor?
- What is a resonant stub, what is its Q, and how is it used as a bias feed or harmonic trap?
- How much bandwidth does a quarter-wave transformer have?
- Why is a half-wave line "transparent", and when is it not?
- How do I convert electrical length (degrees) to millimetres on coax or PCB?
- What is a radial (fan) or butterfly stub, how do I size one, and is it really broadband?
- How accurate are the radial-stub design formulas on ordinary FR-4?
- What do stepped-impedance, hairpin, interdigital, spurline, Lange, Wilkinson and tuning-pad structures do, and where are they covered?

## TL;DR
- $Z_\text{in}=Z_0\dfrac{Z_L+jZ_0\tan\beta\ell}{Z_0+jZ_L\tan\beta\ell}$ (lossless) or with $\tan\beta\ell\to\tanh\gamma\ell$ and $j$ removed (lossy): $Z_\text{in}=Z_0\dfrac{Z_L+Z_0\tanh\gamma\ell}{Z_0+Z_L\tanh\gamma\ell}$.
- **λ/2 line**: $Z_\text{in}=Z_L$ (at one frequency and its multiples). **λ/4 line**: $Z_\text{in}=Z_0^2/Z_L$ — an *impedance inverter*: short ↔ open, 12.5 Ω on a 50 Ω λ/4 → 200 Ω.
- **Quarter-wave transformer**: match real $R_L$ to $Z_S$ with $Z_1=\sqrt{Z_SR_L}$. 12.5 → 50 Ω (Z₁ = 25 Ω) has 35 % bandwidth for VSWR < 1.5; 5 → 50 Ω only 18 %.
- **Stubs**: shorted $Z=jZ_0\tan\beta\ell$ (inductive for $\ell<\lambda/4$), open $Z=-jZ_0\cot\beta\ell$ (capacitive for $\ell<\lambda/4$). For $\ell\ll\lambda$: $L\approx L'\ell$, $C\approx C'\ell$ (1.4 % error at 0.02 λ, 16 % at 0.1 λ).
- **Resonant stubs**: shorted λ/4 ≈ parallel LC ($C=\pi/4\omega_0Z_0$, $L=4Z_0/\pi\omega_0$) — high impedance at $f_0$, a short at $2f_0$ (even-harmonic trap, DC-grounded feed, bias tee). Open λ/4 ≈ series LC — a short (notch) at $f_0$. Loaded Q of a resonant line $=\beta/2\alpha$ (RG-58 at 433 MHz: ≈ 210).
- **Radial (fan) stubs** are open sector-shaped stubs whose narrow apex gives a well-defined, nearly point-like RF short; they are shorter than a uniform λ/4 stub (≈ 9–10 mm radius vs 16 mm at 2.45 GHz on JLC 2-layer). Their radial-line (Bessel) model is exact for an ideal radial line, **but on 1.43 mm FR-4 it missed an openEMS check by 10–23 % in resonant frequency** (pre-registered; all model variants low) — EM-simulate and trim radial stubs on thick boards. A butterfly (two sectors) halves the stub impedance.
- **Physical length** $=\dfrac{\theta}{360°}\cdot\dfrac{VF\cdot c}{f}$. λ/4 at 433 MHz: 114 mm in RG-58 (VF 0.66), 120 mm in RG-316 (0.695), 147 mm in LMR-400 (0.85), ≈94 mm for 50 Ω microstrip on 1.6 mm FR-4.

## Intuition (no math)
A line between you and a load acts like a lens for impedance. The reflected wave from the load returns delayed by the round trip, so its phase relative to the forward wave changes by twice the electrical length. What you see at the input is the combination — so moving along the line, the apparent impedance rotates through every value with the same |Γ|, repeating every half wavelength.

Two special lengths are worth memorising. After **half a wavelength**, the round-trip phase is a full 360°, so the load looks exactly like itself. After a **quarter wavelength**, the round trip is 180°: the reflection comes back inverted, so what was a voltage maximum (high impedance) becomes a voltage minimum (low impedance). A short circuit at the far end appears as an open circuit, and vice versa. That "inversion" is the basis of the quarter-wave transformer, bias tees, and many couplers.

A short piece of shorted line is essentially a loop of wire — an inductor. A short piece of open line is two plates with nothing between them at the end — a capacitor. As the stub gets longer, its reactance grows faster than a lumped component's would, blows up at a quarter-wave (the stub resonates, like a tank circuit), and then changes sign. So stubs are resonators and reactances at the same time, depending on how long they are relative to the wavelength.

## The math

### Level 1 — the formula and special cases
With $\beta\ell$ the electrical length (radians) and $z_L=Z_L/Z_0$:

| Line / load | $Z_\text{in}$ |
|---|---|
| General lossless | $Z_0\dfrac{Z_L+jZ_0\tan\beta\ell}{Z_0+jZ_L\tan\beta\ell}$ |
| Matched ($Z_L=Z_0$) | $Z_0$ for any length |
| Short-circuited | $jZ_0\tan\beta\ell$ |
| Open-circuited | $-jZ_0\cot\beta\ell$ |
| $\ell=\lambda/8$ | $Z_0\dfrac{Z_L+jZ_0}{Z_0+jZ_L}$; short → $+jZ_0$, open → $-jZ_0$ |
| $\ell=\lambda/4$ | $Z_0^2/Z_L$ |
| $\ell=\lambda/2$ | $Z_L$ |

Electrical length ↔ physical length: $\theta\,[°]=360°\,\ell\,f\sqrt{\varepsilon_\text{eff}}/c=360°\,\ell f/(VF\cdot c)$.

### Level 2 — derivation
From [reflections](reflections-vswr-return-loss-mismatch.md), at distance $d=\ell$ from the load $Z(\ell)=Z_0\dfrac{1+\Gamma_Le^{-2\gamma\ell}}{1-\Gamma_Le^{-2\gamma\ell}}$. Substitute $\Gamma_L=(Z_L-Z_0)/(Z_L+Z_0)$ and multiply numerator and denominator by $(Z_L+Z_0)e^{\gamma\ell}$:
$$Z_\text{in}=Z_0\frac{(Z_L+Z_0)e^{\gamma\ell}+(Z_L-Z_0)e^{-\gamma\ell}}{(Z_L+Z_0)e^{\gamma\ell}-(Z_L-Z_0)e^{-\gamma\ell}}
=Z_0\frac{Z_L\cosh\gamma\ell+Z_0\sinh\gamma\ell}{Z_0\cosh\gamma\ell+Z_L\sinh\gamma\ell}
=Z_0\frac{Z_L+Z_0\tanh\gamma\ell}{Z_0+Z_L\tanh\gamma\ell}.$$
For a lossless line $\gamma=j\beta$ and $\tanh j\beta\ell=j\tan\beta\ell$, giving the tangent form. Both forms agree with scikit-rf's cascaded networks to 10⁻¹² Ω (`tools/verify/tline_input_impedance.py`).

The same line as a two-port has the ABCD matrix
$$\begin{bmatrix}A&B\\C&D\end{bmatrix}=\begin{bmatrix}\cosh\gamma\ell&Z_0\sinh\gamma\ell\\ \sinh\gamma\ell/Z_0&\cosh\gamma\ell\end{bmatrix},$$
and $Z_\text{in}=(AZ_L+B)/(CZ_L+D)$ reproduces the formula ([two-ports](../01-circuit-theory/two-port-networks-zyh-abcd.md)).

**Quarter wave.** $\beta\ell=\pi/2$ → $\tan\to\infty$ → $Z_\text{in}=Z_0^2/Z_L$. In admittance terms $Y_\text{in}=Z_L/Z_0^2$: a λ/4 line converts a series element into a shunt one (an ideal *K-inverter* with $K=Z_0$). A series capacitor behind a λ/4 line looks like a shunt inductor — this is how coupled-resonator filters are built from identical resonators ([filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).

**Stubs as reactances.** Shorted: $X=Z_0\tan\beta\ell$, so the equivalent inductance is $L_\text{eq}=Z_0\tan(\beta\ell)/\omega$. Open: $B=\tan(\beta\ell)/Z_0$, so $C_\text{eq}=\tan(\beta\ell)/(\omega Z_0)$. For $\beta\ell\ll1$, $\tan\beta\ell\approx\beta\ell$ and $L_\text{eq}\approx Z_0\ell/v_p=L'\ell$, $C_\text{eq}\approx\ell/(Z_0v_p)=C'\ell$ — the stub is just its total per-unit-length L or C. The approximation's error is $\approx(\beta\ell)^2/3$: 1.4 % at 0.02 λ, 5 % at 0.05 λ, 16 % at 0.1 λ, and useless near 0.2 λ (the script shows 56.6 nH vs 23.1 nH).

**Resonant stubs.** Near $f_0$ where a shorted stub is λ/4, write $f=f_0(1+\delta)$. Then $\beta\ell=\frac\pi2(1+\delta)$ and $Y=1/(jZ_0\tan\beta\ell)\approx j\frac{\pi}{2Z_0}\delta$. A parallel LC gives $Y\approx j2\omega_0C\delta$. Matching: $C=\pi/(4\omega_0Z_0)$ and $L=1/(\omega_0^2C)=4Z_0/(\pi\omega_0)$. Similarly an open λ/4 stub ≈ series LC with $L=\pi Z_0/(4\omega_0)$, $C=4/(\pi\omega_0Z_0)$. Script: the stub's admittance matches the LC model to 0.1 % of $\omega_0C$ across ±3 %.

**Q of a resonant line.** With a small loss $\alpha$, the shorted λ/4 stub input is $Z_0\tanh(\alpha\ell+j\beta\ell)$; at resonance this is $\approx Z_0/(\alpha\ell)$ (a large real resistance), and the half-power bandwidth gives
$$Q=\frac{\beta}{2\alpha}=\frac{\pi}{\alpha\lambda}=\frac{27.3}{\text{(line loss in dB per wavelength)}}.$$
This holds for λ/4 or λ/2 resonators, open or short. Script: sweep gives Q = 343.9 vs β/2α = 343.8, and peak $|Z|=Z_0/\alpha\ell$ to 1 %. For RG-58 at 433 MHz ($\alpha$ = 0.287 dB/m) Q ≈ 208 and the λ/4 stub presents ≈ 13 kΩ at resonance.

**Line as a Pi (or T) network.** From the ABCD matrix a section of electrical length θ equals a Pi network with series $jZ_0\sin\theta$ and two shunt admittances $j\tan(\theta/2)/Z_0$. For small θ: a high-$Z_0$ section is mostly series inductance $L\approx Z_0\theta/\omega$; a low-$Z_0$ section is mostly shunt capacitance $C\approx\theta/(\omega Z_0)$. This is the basis of stepped-impedance low-pass filters and explains why a skinny PCB trace behaves like a series inductor.

**Quarter-wave transformer bandwidth.** For a real load $R_L$, section $Z_1=\sqrt{Z_0R_L}$, TEM line, the fractional bandwidth over which $|\Gamma|\le\Gamma_m$ is
$$\frac{\Delta f}{f_0}=2-\frac4\pi\arccos\!\left[\frac{\Gamma_m}{\sqrt{1-\Gamma_m^2}}\frac{2\sqrt{Z_0R_L}}{|R_L-Z_0|}\right]$$
(Pozar §5.4). Script check against a brute-force sweep: 35.1 % both ways for 12.5 → 50 Ω, VSWR 1.5. The bandwidth shrinks as the ratio grows: 78 % for 2:1, 35 % for 4:1, 18 % for 10:1. Wider bandwidth needs [multi-section or tapered transformers](impedance-matching-lumped-and-distributed.md), with the ultimate limit set by [Bode–Fano](broadband-matching-bode-fano.md).

### Level 3 — limits and refinements
- **Dispersion / non-TEM**: on microstrip $\varepsilon_\text{eff}$ varies with frequency, so a stub that is λ/4 at $f_0$ is not exactly λ/2 at $2f_0$; harmonic traps on microstrip must be tuned at the harmonic.
- **End effects**: an open microstrip end has fringing capacitance equivalent to extra length $\Delta\ell$; Hammerstad's formula $\Delta\ell/h=0.412\frac{(\varepsilon_\text{eff}+0.3)(W/h+0.264)}{(\varepsilon_\text{eff}-0.258)(W/h+0.8)}$ gives ≈0.39 h (0.62 mm on 1.6 mm FR-4 for a 50 Ω line) [5]. A "short" to ground through a via has via inductance (≈0.5–0.7 nH for a 0.3 mm via through a 1.6 mm board to the bottom plane: Goldfarb–Pucel **0.54 nH**, the KB design value; isolated-barrel partial inductance 0.69 nH; ≈0.02 nH for a via through 0.21 mm prepreg to an inner ground — see [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)). The often-quoted $5.08h[\ln(4h/d)+1]$ nH ($h,d$ in inches) gives 1.3 nH, ≈2× high: it is roughly the loop inductance with a distant return, not a via to a plane (see [inductance from fields](../02-electromagnetics/inductance-capacitance-from-fields.md)). The via inductance makes a shorted stub electrically longer by $\Delta\ell\approx L_{via}v_p/Z_0$ ≈ 1.8 mm for 0.54 nH on a 50 Ω line on 1.6 mm FR-4 ($\varepsilon_{eff}$ ≈ 3.4).
- **Junction effects**: a shunt stub attached to a through line has a T-junction discontinuity; full-wave or closed-form junction models are needed above a few GHz.
- **Loss in stubs**: a stub used as a matching reactance dissipates power; its unloaded Q (β/2α) plays the same role as an inductor's Q in [lumped matching loss](impedance-matching-lumped-and-distributed.md).
- **Radiation** from open stubs on thin substrates is small; on thick, low-εr substrates it becomes a loss mechanism (and is exploited by patch antennas, which are essentially radiating λ/2 open resonators — [patches](../08-antennas/patch-antennas.md)).

### Radial and butterfly stubs
**Level 1 — what they are for.** A radial stub is an open stub shaped like a slice of pie, attached at its narrow apex to the line it decorates (usually the far end of a high-impedance λ/4 bias line, or directly to an RF line as a shunt trap). Seen from the apex it behaves like an open stub — capacitive below resonance, a series-resonant short at resonance, inductive above — but (i) the contact point is narrow, so "where the short is" is well defined, unlike a wide low-Z stub whose junction spreads over millimetres; (ii) it is shorter than a uniform λ/4 stub; and (iii) its impedance stays low over a wider band than a uniform stub with the same narrow contact. A **butterfly stub** is two sectors on opposite sides of the line at the same point — two radial stubs in parallel, so its impedance is half that of one.

**Level 2 — the radial-line model.** Between the sector and the ground plane (height h) the lowest mode of a radial parallel-plate line has $E_z=AJ_0(kr)+BY_0(kr)$ and $H_\phi=\tfrac{j}{\eta}[AJ_1(kr)+BY_1(kr)]$, with $k=k_0\sqrt\varepsilon$, $\eta=\eta_0/\sqrt\varepsilon$. With voltage $V=E_zh$ and total radial current $I=H_\phi\,\alpha r$ for a sector of angle α, and an open outer edge ($H_\phi(r_o)=0$), the impedance at the inner radius $r_i$ is
$$Z_\text{in}=j\,\frac{\eta h}{\alpha r_i}\;\frac{J_0(kr_i)Y_1(kr_o)-Y_0(kr_i)J_1(kr_o)}{J_1(kr_i)Y_1(kr_o)-Y_1(kr_i)J_1(kr_o)} .$$
The local "characteristic impedance" $\eta h/(\alpha r)$ falls as the sector widens, which is the physical reason the stub is shorter and lower-impedance than a uniform one. Checks (`tools/verify/s6_radial_stub.py`): at 10 MHz it is exactly the sector's parallel-plate capacitor $\varepsilon\alpha(r_o^2-r_i^2)/2h$; for a very thin sector far from the apex it reduces to $-jZ_{pp}\cot(k\ell)$ of a uniform stub; and a direct numerical integration of the radial telegrapher equations ($L'=\mu h/\alpha r$, $C'=\varepsilon\alpha r/h$) reproduces it to 10⁻⁸. Synthesis: choose α (60–90° is common) and $r_i$ (chord at $r_i$ = feed width, $r_i=W_f/[2\sin(\alpha/2)]$), then root-find $r_o$ for $Z_\text{in}=0$ at $f_0$.

**Level 3 — which permittivity and which radius? The model is not reliable on thick FR-4.** A real microstrip sector has fringing at its arc *and* its straight sides, and only part of its field is in the board. Published practice is ambiguous (HP AN 976 notes that $\varepsilon_r$ suits wide sectors while a microstrip $\varepsilon_\text{eff}$, with a width that halves the stub area, suits narrow ones). Four variants for a 2.45 GHz stub on JLC0216A (h 1.43 mm, εr 4.5), α = 60°, $r_i$ = 0.80 mm (0.8 mm, ≈ 90 Ω feed) need $r_o$ = **9.62 mm** (A: $\varepsilon_r$), **10.36 mm** (B: $\varepsilon_\text{eff}$, AN 976 width), **9.74 mm** (C: B plus an open-end extension of the arc) and **9.22 mm** (D: $\varepsilon_r$ with a disc effective radius) — a 12 % spread; at α = 90° the radii are 8.6–9.6 mm. For comparison a uniform 50 Ω open λ/4 stub is 16.05 mm long.

**openEMS check (pre-registered, missed).** Before any EM run we wrote down: for $r_o$ = 9.70 mm, $f_\text{res}$ = 2.425 / 2.669 / 2.463 / 2.302 GHz (A–D), openEMS within ±4 % of C, and $|X(1.5\text{ GHz})|$ within 15 % of C. The full-wave result (`tools/verify/s6_radial_stub_openems.py`; lossless board, de-embedded to the apex chord by subtracting a matched through run on the same mesh): **$f_\text{res}$ = 2.978 GHz** (coarse mesh 2.915 GHz, +2.1 % on refinement), $X$(1.5 GHz) = −37.0 Ω (models −42 to −65 Ω), low-frequency capacitance **2.28 pF** (models 1.33 pF; parallel-plate area alone 1.36 pF). **Every model variant resonates 10–23 % too low and all three expectations were missed.** The measurement method was checked on a control: a uniform 12 mm open stub of the same 0.8 mm line, run the same way, gave $f_\text{res}$ 3.35 GHz vs ≈ 3.41 GHz expected and $Z$(1 GHz) = −j173 Ω vs −j175 Ω, so the de-embedding is sound and the discrepancy belongs to the radial model in this geometry. Two facts frame it. Side-edge fringing is large here (≈ 0.6 h ≈ 0.86 mm of extra effective width per edge, from the microstrip fringe capacitance); adding it to the model brings the low-frequency capacitance to 2.17 pF, close to openEMS, but moves the resonance *down* to 2.17 GHz — the opposite of what openEMS shows. And the openEMS curve looks much more like a lumped 2.3 pF capacitor in series with ≈ 1.2 nH than like the steep radial-line reactance. The likely reason is that with $r_o/h$ ≈ 7 and a 60° sector the field is not the single radial mode the model assumes (fringing across the straight edges, non-radial current near the narrow apex); this is a hypothesis, not tested here. Radial-stub formulas were developed for thin substrates ($h\ll r_o$, e.g. 0.25 mm at 10 GHz in AN 976), where the single-mode picture should hold better — also untested here.

**Bandwidth (model, so with the same caveat).** Shunt stubs across a 50 Ω line on the same board, width of the band with $|S_{21}|<-20$ dB around 2.45 GHz: uniform stub of the same 0.8 mm contact (91 Ω) 86 MHz; 60° radial 117 MHz; 90° radial 156 MHz; uniform 50 Ω (2.69 mm wide) 156 MHz; butterfly 2 × 60° 235 MHz, 2 × 90° 313 MHz; uniform 20 Ω (9.8 mm wide) 388 MHz. So the radial stub's advantage is **bandwidth for a given narrow contact, plus compactness**. A wide low-Z uniform stub is broader still, but it shorts the line over a wide, poorly defined junction.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $Z_\text{in}=Z_0(Z_L+jZ_0\tan\beta\ell)/(Z_0+jZ_L\tan\beta\ell)$ | lossless uniform line | — |
| $Z_\text{in}=Z_0^2/Z_L$ | λ/4 (odd multiples) | 50 Ω λ/4: 12.5 Ω ↔ 200 Ω |
| $Z_1=\sqrt{Z_SR_L}$ | λ/4 transformer, real loads | 12.5→50 Ω: 25 Ω |
| $L_\text{eq}=Z_0\tan(\beta\ell)/\omega$ | shorted stub | ≈ $L'\ell$ if $\ell<0.05\lambda$ |
| $C_\text{eq}=\tan(\beta\ell)/(\omega Z_0)$ | open stub | ≈ $C'\ell$ if $\ell<0.05\lambda$ |
| $C=\pi/(4\omega_0Z_0)$, $L=4Z_0/(\pi\omega_0)$ | shorted λ/4 near $f_0$ | 50 Ω, 433 MHz: 5.8 pF, 23.4 nH |
| $Q=\beta/(2\alpha)$; $R_\text{peak}=Z_0/(\alpha\ell)$ | resonant line | RG-58 @433 MHz: Q ≈ 210, 13 kΩ |
| Pi-equivalent: series $jZ_0\sin\theta$, shunt $j\tan(\theta/2)/Z_0$ | exact | stepped-impedance filters |
| $\Delta\ell_\text{open}\approx0.4h$ | microstrip open end | 0.6 mm on 1.6 mm FR-4 |
| Radial stub $Z_\text{in}=j\frac{\eta h}{\alpha r_i}\frac{J_0(kr_i)Y_1(kr_o)-Y_0(kr_i)J_1(kr_o)}{J_1(kr_i)Y_1(kr_o)-Y_1(kr_i)J_1(kr_o)}$ | ideal radial line; on 1.43 mm FR-4 openEMS resonance 10–23 % above it | 60°, 2.45 GHz model: $r_o$ ≈ 9.2–10.4 mm |
| Butterfly = two radial stubs in parallel ($Z/2$) | same point on the line | stop band ≈ 2× |
| $r_i=W_f/[2\sin(\alpha/2)]$ | apex chord = feed width | 0.8 mm feed, 60°: 0.80 mm |

**Quarter-wavelength lengths (mm)** — $\lambda/4=VF\cdot c/(4f)$:

| f (MHz) | RG-58/174 (0.66) | RG-316/402 (0.695) | LMR-400 (0.85) | 50 Ω µstrip 1.6 mm FR-4 ($\varepsilon_\text{eff}$ 3.40) | free space |
|---|---|---|---|---|---|
| 433 | 114.2 | 120.3 | 147.1 | 93.9 | 173.1 |
| 868 | 57.0 | 60.0 | 73.4 | 46.8 | 86.3 |
| 915 | 54.1 | 56.9 | 69.6 | 44.4 | 81.9 |
| 1575.42 | 31.4 | 33.1 | 40.4 | 25.8 | 47.6 |
| 2450 | 20.2 | 21.3 | 26.0 | 16.6 | 30.6 |

Include the connector's electrical length (several millimetres for an SMA; measure it with the VNA's port extension) when cutting coax stubs, and trim by measurement.

## Worked examples

### Example 1 — DC-grounding a 433 MHz antenna with a λ/4 shorted stub
A monopole on a rocket fin can accumulate static charge; a shorted λ/4 stub from the feed to ground is invisible at $f_0$ (≈13 kΩ for RG-58, far above the 50 Ω antenna) but a dead short at DC. RG-316 (VF 0.695): length $=0.695\times299.79/(4\times433)$ m = 120.3 mm (cut long, trim while watching S11 on a NanoVNA). RG-316 is lossier than RG-58 (≈0.72 dB/m at 433 MHz), so its stub has Q ≈ 79 and presents ≈5 kΩ at resonance — still 100× the antenna impedance, costing < 0.05 dB. It also shorts the 2nd harmonic (866 MHz) — a free even-harmonic trap — but passes the 3rd (1299 MHz), so it does not replace the low-pass filter.

### Example 2 — quarter-wave transformer for a 12.5 Ω load at 433 MHz
A PA output or a small loop antenna presents 12.5 Ω. $Z_1=\sqrt{50\times12.5}=25$ Ω. On 1.6 mm FR-4 ($\varepsilon_r$ 4.5) a 25 Ω microstrip is ≈8.3 mm wide with $\varepsilon_\text{eff}\approx3.75$ (scikit-rf `MLine`, Hammerstad–Jensen; see the [planar-lines calculator](planar-lines-microstrip-stripline-cpwg.md)); its λ/4 is $c/(4f\sqrt{3.75})=89$ mm — large. Bandwidth for VSWR < 1.5: 35 % (≈ 152 MHz), plenty for the 433 MHz ISM band (433.05–434.79 MHz). At 433 MHz a lumped L-network ([matching](impedance-matching-lumped-and-distributed.md)) is far smaller; the λ/4 transformer wins at 2.4 GHz and above.

### Example 3 — replacing a 3 pF shunt capacitor with an open stub at 915 MHz
Need $B=\omega C=2\pi\times915\times10^6\times3\times10^{-12}=17.2$ mS. With a 50 Ω open stub: $\tan\beta\ell=BZ_0=0.862$ → $\beta\ell=40.8°$. On 1.6 mm FR-4 50 Ω microstrip ($\varepsilon_\text{eff}\approx3.4$): $\ell=\frac{40.8}{360}\cdot\frac{c}{f\sqrt{3.4}}=20.1$ mm, minus the open-end extension (~0.6 mm) → cut to ≈19.5 mm. Note it is not "C'ℓ": $C'\ell$ would give only 2.3 pF for 20 mm — the tangent matters at 41°.

### Example 4 — does a half-wave of cable leave my antenna match unchanged?
At 433 MHz a λ/2 of RG-58 is 228.5 mm. It repeats $Z_L$ exactly at 433 MHz but not across a band: at 434.79 MHz the length is 180.7° (a 0.7° error — negligible), but at 915 MHz the same cable is 380°, i.e. not transparent. Half-wave "magic lengths" only work for narrow bands and they add loss; with a well-matched antenna the cable length is irrelevant anyway ([reflections](reflections-vswr-return-loss-mismatch.md)).

### Example 5 — measuring an unknown line
See [telegrapher page, Example 5](telegrapher-equations-characteristic-impedance.md): $Z_0=\sqrt{Z_\text{oc}Z_\text{sc}}$ and $\tanh\gamma\ell=\sqrt{Z_\text{sc}/Z_\text{oc}}$ — both identities follow from the two stub formulas above (checked in the script with a complex $Z_0$).

## Practical notes
- **Bias tee / DC feed**: a shorted λ/4 stub (or a high-Z λ/4 line bypassed by a capacitor to ground at the far end) injects DC into an RF line with minimal RF loading — used for GNSS active-antenna feeds (3.3 V up the coax to the LNA) though at 1575 MHz an RF choke inductor is usually smaller. The λ/4 line is narrowband; a lumped choke is broadband but must be self-resonant above the band ([inductors at RF](../04-real-components-hf/inductors-at-rf.md)).
- **Harmonic traps**: a λ/4 open stub at $2f_0$ placed at the PA output notches the 2nd harmonic (series resonance) while being a λ/8 open stub (capacitive, −j50 Ω for a 50 Ω stub) at $f_0$ — compensate that capacitance in the match.
- **Tolerance**: FR-4 $\varepsilon_r$ varies ±5–10 % between vendors and with frequency; a λ/4 resonator on FR-4 is only good to a few percent in frequency — fine for 433/915 MHz ISM bands if trimmed, marginal for a high-Q filter.
- **Size at UHF**: λ/4 at 433 MHz is 94 mm on FR-4 — distributed elements are usually impractical below ~1 GHz on small flight computers; use lumped L-C (with their own [parasitics](../04-real-components-hf/capacitors-at-rf-mlcc.md)).

### A zoo of distributed PCB structures (where each is covered)
| Structure | What it does | Where |
|---|---|---|
| Open / shorted stub | reactance, resonator, harmonic trap, DC ground | this page |
| Radial (fan) and butterfly stub, "bias-line fan" | low-impedance RF short at a point, e.g. at the end of a λ/4 bias line | this section |
| λ/4 high-Z bias line + radial stub or bypass capacitor | DC feed that is an RF open at the main line | Practical notes below; [bias tee](../06-rf-circuits/amplifier-stability-and-biasing.md) |
| Stepped-impedance (hi-lo) low-pass | alternating narrow (series L) and wide (shunt C) sections | [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) Ex. 3; Pi-equivalent above |
| Parallel-coupled-line band-pass; hairpin (the same, with resonators folded into U shapes for size) | coupled λ/2 resonators | [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) Ex. 4 |
| Interdigital and combline filters | side-by-side λ/4 (interdigital) or shorter capacitor-loaded (combline) resonators shorted at one end | [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) |
| Spurline | band-stop made by an L-shaped slot that splits the strip into a λ/4 coupled section — a notch with no stub sticking out | this row only (not modelled in the KB) |
| Wilkinson divider, branch-line and rat-race hybrids, coupled-line coupler, Lange coupler (interdigitated 3 dB quadrature coupler with bond wires) | splitting, combining, quadrature | [couplers, dividers, combiners](../06-rf-circuits/couplers-dividers-combiners.md) |
| Tapers, multi-section transformers | broadband impedance transformation | [matching](impedance-matching-lumped-and-distributed.md) |
| Tuning pads / flags (small copper islands beside a line or at a stub's end) | post-fabrication trimming: bridge an island with solder to add capacitance or length; remove copper to shorten | open-end and gap models in [discontinuities](microstrip-discontinuities.md) |
| Open ends, gaps, steps, bends, T-junctions, vias | parasitics that set stub lengths | [discontinuities](microstrip-discontinuities.md) |

## Common mistakes & misconceptions
- **Using the free-space wavelength** (173 mm λ/4 at 433 MHz) instead of the in-line one (114 mm in RG-58). Always include VF or $\varepsilon_\text{eff}$.
- **Microstrip VF from bulk εr** (1/√4.5 = 0.47) instead of $1/\sqrt{\varepsilon_\text{eff}}$ (≈0.54): a 15 % length error.
- **"A λ/4 transformer is broadband."** It is perfect at one frequency; bandwidth falls rapidly with impedance ratio (18 % for 10:1 at VSWR 1.5).
- **"A stub of length ℓ is an inductor of L'ℓ."** Only if ℓ < ~0.05 λ; otherwise use the tangent.
- **Forgetting the harmonics**: a λ/4 shorted stub is transparent at $f_0$ and $3f_0$ — it does not suppress the 3rd harmonic; a λ/4 open stub at $f_0$ is also a short at $3f_0$.
- **Ignoring end effects and via inductance** in PCB stubs — on 1.6 mm FR-4 with a 50 Ω line, ≈0.6 mm for an open end and ≈1.8 mm for a single 0.3 mm via short (0.54 nH; two vias at 1 mm pitch, 0.38 nH, ≈1.25 mm).
- **Trusting a radial-stub closed form on thick FR-4.** On 1.43 mm FR-4 the openEMS resonance was 10–23 % above every model variant; treat calculator radii as a starting point and EM-simulate or trim.
- **"Radial stubs are broadband."** Broader than a uniform stub with the same narrow contact (117 vs 86 MHz in the model), not broader than a wide low-impedance stub (388 MHz for 20 Ω).
- **"Cutting the coax to λ/2 fixes the SWR."** It makes the meter read the antenna's own SWR (only at one frequency); it changes nothing the antenna experiences.

## How to simulate / verify
- `tools/verify/s6_radial_stub.py` — radial-line model, limit checks, model variants A–D, synthesis of $r_o$, the pre-registration printout, stop-band comparison (all pass). `tools/verify/s6_radial_stub_openems.py` — openEMS check (coarse + fine mesh, ≈ 27 min; results appended to `s6_radial_stub_openems_results.txt`); setting `shape="line"` in `run()` gives the uniform-stub control case.
- `tools/verify/tline_input_impedance.py` — Zin (lossless/lossy) vs scikit-rf; λ/4 and λ/2 identities; stub L and C vs their small-length limits; resonant stub ↔ LC; Q = β/2α from a sweep; harmonic behaviour; $Z_\text{oc}Z_\text{sc}=Z_0^2$; λ/4 transformer bandwidth formula vs sweep; Pi-equivalent of a line; the microstrip example used on the telegrapher page. All pass.
- scikit-rf:

```python
import skrf as rf
f = rf.Frequency(300, 1300, 1001, unit='MHz')
# RG-405-like PTFE coax: 0.51 mm centre, 1.68 mm dielectric -> ~49.7 ohm, VF 0.695
cx = rf.media.Coaxial(frequency=f, Dint=0.51e-3, Dout=1.68e-3, epsilon_r=2.07, tan_delta=2e-4, z0_port=50)
stub = cx.line(120.3e-3, unit='m') ** cx.short()   # 1-port shorted stub, lambda/4 at 433 MHz
tee  = cx.shunt(stub)                              # 2-port: stub hung across a through line
tee.plot_s_db(m=1, n=0)                            # deep notch at 866 MHz (2nd harmonic), ~0 dB at 433 MHz
```
- On a NanoVNA: measure a stub as a 1-port (S11) and read $Z$; find the λ/4 frequency from the $|Z|$ peak (shorted) or dip (open) and trim.

## Open questions / gaps
- Radial stubs (W5-S6, 2026-10-13): the openEMS miss on 1.43 mm FR-4 is unexplained. Wanted: openEMS runs on a thin substrate (JLC-7628, h 0.21 mm) and at 90°, a planar-circuit (2-D Green's function) model such as Giannini et al., and a VNA measurement of a fabricated stub. The thin-substrate validity of the radial model is assumed, not shown.
- Corrected 2026-10-03 (W5-E9, D6 #7): this page previously gave ≈1 nH for a 1.6 mm ground via with the Johnson & Graham "+1" formula, while 02 and 04 give 0.69/0.54 nH. The KB value for a via to a plane is Goldfarb–Pucel 0.54 nH; every via inductance quoted should state its return path. The stub-length rule (old "0.5–1.5 mm") was re-derived from $\Delta\ell = L_{via}v_p/Z_0$.
- Closed-form T-junction and via-short models for accurate microstrip stub design above ~3 GHz are not included (→ 04 PCB parasitics and 16 EM solvers).
- The 0.412 open-end formula is Hammerstad's 1975 form as quoted by Wadell (Qucs implements a different, 1981 Hammerstad form and Kirschning–Jansen–Koster; all give ≈ 0.39 h for 50 Ω on FR-4). The more accurate Kirschning–Jansen–Koster model, with an openEMS check, is on the [discontinuities page](microstrip-discontinuities.md) (corrected attribution 2026-10-13, W5-S6, following W5-E11's note).
  (Now covered: KJK model, openEMS comparison and an attribution note in [microstrip discontinuities](microstrip-discontinuities.md).)

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — §2.3 (terminated lossless line, special cases), §2.5 (quarter-wave transformer), §5.2 (stub tuning), §5.4 (λ/4 transformer bandwidth, eq. 5.52), §6.1–6.3 (transmission-line resonators, Q = β/2α), §8.5 (stepped-impedance filters). (textbook)
2. R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., 1992 — ch. 5 (quarter-wave transformers), ch. 7 (resonators). (textbook)
3. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (rev. 2016), chapters "Transmission Lines" and "Impedance Matching" — https://eceweb1.rutgers.edu/~orfanidi/ewa/. (textbook, free)
4. M. Steer, *Microwave and RF Design, Vol. II: Transmission Lines* and *Vol. III: Networks*, 3rd ed., NC State Univ. Libraries, 2019 (open access). (textbook, free)
5. E. O. Hammerstad, "Equations for microstrip circuit design," *Proc. 5th European Microwave Conf.*, Hamburg, 1975, pp. 268–272 — open-end extension formula (as reproduced in B. C. Wadell, *Transmission Line Design Handbook*, Artech House 1991). (peer-reviewed conference, via secondary)
6. Verification: `tools/verify/tline_input_impedance.py`, scikit-rf 2.0.1 (`DefinedGammaZ0`, `MLine`). (numerical check)
7. Hewlett-Packard Application Note 976 — design of an 8–12 GHz microstrip mixer with a 5082-2207 diode, section "Radial Line Stubs" (PDF dated 1998; title as on the document not recorded) — fan-stub reactance after Vinding; εr vs εeff discussion; area-halving width rule. (app note)
8. J. P. Vinding, "Radial line stubs as elements in strip line circuits," *NEREM Record*, 1967; H. A. Atwater, "Microstrip reactive circuit elements," *IEEE Trans. MTT* 31(6), 1983, and "The design of the radial line stub," *Microwave Journal*, Nov. 1985; F. Giannini, R. Sorrentino, J. Vrba, "Planar circuit analysis of microstrip radial stub," *IEEE Trans. MTT* 32(12), 1652–1655, 1984. (peer-reviewed / trade journal; cited, not read)
9. Verification: `tools/verify/s6_radial_stub.py`, `tools/verify/s6_radial_stub_openems.py` (openEMS v0.37). (numerical check)
