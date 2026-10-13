---
title: Antenna fundamentals — pattern, directivity, gain, efficiency, aperture, impedance, bandwidth
domain: 08-antennas
slug: antenna-fundamentals
tags: [directivity, gain, realized-gain, efficiency, effective-aperture, radiation-resistance, eirp, reciprocity, bandwidth, dBi, dBd]
prerequisites: [../02-electromagnetics/radiation-from-currents-hertzian-dipole.md, ../02-electromagnetics/poynting-vector-power-flow.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md, ../00-math-foundations/decibels-and-log-units.md]
related: [dipoles-and-monopoles.md, small-antenna-limits.md, antenna-polarization-and-circular-polarization.md, antenna-measurement.md, ../09-propagation-link-budget/friis-free-space-path-loss.md, ../09-propagation-link-budget/link-budget-methodology.md, ../02-electromagnetics/near-field-far-field.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, multiband-and-wideband-antennas.md, antenna-identification-guide.md, slot-antennas.md, inductive-coupling-rfid-nfc-wpt.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Antenna fundamentals

## Questions this page answers
- What does an antenna actually do, physically?
- What is the difference between directivity, gain, and realized gain?
- If an antenna has "5 dBi gain", does it amplify my signal?
- What is dBi, dBd, dBic, and how do I convert between them?
- Why does a half-wave dipole have 2.15 dBi and a short dipole 1.76 dBi?
- What is effective aperture, and why is it λ²G/4π for every antenna?
- Why do bigger antennas at low frequency "catch more signal"?
- What is radiation resistance and how is it different from input impedance?
- What are radiation efficiency, mismatch efficiency and total efficiency?
- How do I estimate gain from a beamwidth on a datasheet?
- What does "antenna bandwidth" mean — VSWR, gain, axial ratio, pattern?
- Is an antenna's receive pattern the same as its transmit pattern (reciprocity)?
- How do I calculate EIRP and ERP for my LoRa transmitter?
- Does a good SWR mean my antenna is efficient?
- Does a longer antenna always mean more gain?
- Can I use a 2.4 GHz antenna at 900 MHz (or a 433 MHz antenna at 868/915 MHz)?
- Must an antenna be resonant to radiate well?
- For a receive-only SDR, does the antenna matter?

## TL;DR
- An antenna is a **transducer and impedance transformer** between a guided wave (≈50 Ω cable) and a free-space wave (η₀ ≈ 376.7 Ω). It cannot create power; it only redistributes it in angle and loses some as heat.
- **Directivity** D(θ,φ) = 4πU/P_rad compares the radiation intensity to an isotropic source radiating the same power. **Gain** G = e_rad·D includes ohmic/dielectric loss. **Realized gain** G_R = (1−|Γ|²)·G also includes mismatch; neither includes polarization mismatch (IEEE Std 145 [3]).
- Reference values (verified in `tools/verify/ant_dipole.py`): isotropic 0 dBi; Hertzian/short dipole D = 1.5 (1.76 dBi); λ/2 dipole D = 1.64 (2.15 dBi); λ/4 monopole on an *infinite* ground 3.28 (5.16 dBi, all in the upper half-space). dBd = dBi − 2.15.
- **Effective aperture** A_e = λ²G/(4π) for *every* antenna (derived below from the short dipole plus reciprocity). A λ/2 dipole has A_e ≈ 626 cm² at 433 MHz but only 20 cm² at 2.45 GHz — this, not "air absorption", is why Friis path loss grows with frequency for fixed-gain antennas.
- **Input impedance** Z_in = R_rad + R_loss + jX. Radiation efficiency e_rad = R_rad/(R_rad + R_loss). Small antennas have tiny R_rad, so milliohms of loss matter.
- **Beamwidth → directivity**: D ≈ 41253/(θ₁θ₂) (Kraus) or D ≈ 72815/(θ₁²+θ₂²) (Tai–Pereira), angles in degrees; the latter is within ~0.1 dB for narrow beams, the former overestimates by ~0.4–0.5 dB (verified in `tools/verify/ant_aperture.py`).
- **Bandwidth** is always "bandwidth of *something*": impedance (VSWR ≤ 2, i.e. return loss ≥ 9.5 dB, or RL ≥ 10 dB), gain (−1 or −3 dB), axial ratio (≤ 3 dB), pattern. For a resonant antenna FBW(VSWR ≤ s) ≈ (s−1)/(Q√s) [6].
- **EIRP** = P_accepted·G (dBm + dBi, after cable and mismatch loss); ERP = EIRP − 2.15 dB. Regulations are usually written in one of these (see [19-regulations-safety](../19-regulations-safety/spectrum-allocation-ism-bands.md)).
- A perfect SWR says nothing about efficiency: a 50 Ω resistor has SWR 1.0 and radiates nothing.

## Intuition (no math)

**Where radiation comes from.** A steady current makes a static magnetic field; a steady charge makes a static electric field. Neither radiates. Radiation needs *accelerating charge*, i.e. time-varying current. When a current on a wire oscillates, the fields it creates near the wire cannot rearrange instantly everywhere — changes propagate outward at c. Far from the wire, the part of the field that falls off as 1/r (instead of 1/r² or 1/r³) carries energy away permanently. That is the radiated wave. The full derivation is on [radiation from currents / Hertzian dipole](../02-electromagnetics/radiation-from-currents-hertzian-dipole.md).

**Why a length of wire.** Every bit of current radiates; what you see far away is the phasor sum over the whole current distribution. If a wire is very short compared to λ, you can only push a small current through it for a given voltage (it looks like a tiny capacitor) and the radiation is weak — the antenna has a small *radiation resistance*. A wire about λ/2 long resonates: current and voltage standing waves form, the current can be large for a modest voltage, and radiation resistance is conveniently near 50–75 Ω.

**The antenna as a matching transformer.** A 50 Ω coax carries a wave whose E/H ratio is 50 Ω "in the cable's geometry". Free space has E/H = 376.7 Ω. The antenna is the structure that smoothly converts one wave into the other. A horn does this very literally (a waveguide flared until it looks like free space); a dipole does it with a resonance.

**Directivity is just redistribution.** Imagine a light bulb (isotropic) and the same bulb inside a reflector (a torch). The torch is brighter straight ahead, darker behind, but it uses the same watts. An antenna's "gain" is the torch's forward brightness divided by the bare bulb's brightness. Gain in one direction is always paid for by less radiation elsewhere. **Antennas don't amplify.** An active GNSS antenna appears to "have 28 dB gain" only because it contains an amplifier (LNA) — the radiator itself has a few dBic.

**Effective aperture: the antenna's catching area.** On receive, a wave arrives with a power flux density S (W/m²). The antenna delivers power P = S·A_e to a matched load, so A_e is its equivalent "catching area". For a dish, A_e is close to the physical mouth area. For a thin wire dipole, A_e (626 cm² at 433 MHz) is much larger than the wire's physical area — the wire's field reaches out and interacts with the passing wave over roughly a λ/2 × λ/4 region. A deep result: A_e/G is the same, λ²/4π, for *all* antennas. So at fixed gain, catching area shrinks as 1/f²; that is where the frequency dependence of the Friis equation comes from.

**Reciprocity.** For antennas made of ordinary (linear, passive, non-magnetised) materials, the pattern, gain, impedance and polarization are the same for transmitting and receiving. That lets you measure a receive pattern by transmitting, or vice versa. Exceptions: antennas containing ferrites biased by a magnetic field, active electronics (an active GNSS antenna is *not* reciprocal — its LNA only amplifies one way), or propagation through a magnetised plasma (ionosphere).

**Near field vs far field.** Close to the antenna there is a lot of stored (reactive) energy sloshing back and forth; things placed there (a hand, a battery, the rocket airframe) detune the antenna. The boundary of this region is about λ/2π for small antennas (IEEE Std 145 [3]); at 433 MHz that is 11 cm. Far away (beyond ~2D²/λ for large antennas and at least a few λ), the pattern shape no longer depends on distance. See [near field and far field](../02-electromagnetics/near-field-far-field.md).

## The math

### Level 1 — definitions and algebra

Symbols (SI):
- P_in: power delivered into the antenna terminals (W). P_rad: power radiated (W).
- U(θ,φ): radiation intensity, power per unit solid angle (W/sr). In the far field U = r²·S = r²|E|²/(2η₀) for peak phasors.
- η₀ = √(μ₀/ε₀) ≈ 376.73 Ω. λ = c/f (m). k = 2π/λ (rad/m).

**Directivity**
$$D(\theta,\phi) = \frac{4\pi\,U(\theta,\phi)}{P_\text{rad}},\qquad P_\text{rad} = \oint U\,d\Omega .$$
An isotropic radiator has D = 1 everywhere. When a single number is quoted it is the maximum, D₀.

**Radiation efficiency and gain**
$$e_\text{rad} = \frac{P_\text{rad}}{P_\text{in}} = \frac{R_\text{rad}}{R_\text{rad}+R_\text{loss}},\qquad G = e_\text{rad}\,D .$$

**Mismatch (reflection) efficiency and realized gain**
$$\Gamma = \frac{Z_\text{in}-Z_0}{Z_\text{in}+Z_0},\qquad e_\text{mis} = 1-|\Gamma|^2,\qquad G_R = e_\text{mis}\,G = e_\text{mis}\,e_\text{rad}\,D .$$
Total efficiency e_tot = e_mis·e_rad (Balanis calls these e_r and e_cd, and e₀ = e_r e_cd [1]). A VSWR of 1.5, 2 and 3 costs 0.18, 0.51 and 1.25 dB respectively (−10 log(1−|Γ|²) with |Γ| = (s−1)/(s+1)). See [reflections, VSWR, mismatch](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md).

**Logarithmic units**
- dBi: gain relative to isotropic. dBic: relative to an isotropic *circularly polarized* reference (used for GNSS/CP antennas; for a CP wave, dBic and the co-polar partial gain in dBi are the same number).
- dBd: relative to a λ/2 dipole's peak: dBd = dBi − 2.15 (CONVENTIONS §5).
- EIRP = P_in(dBm) + G(dBi) − (feedline and mismatch losses) — i.e. use the *realized* gain times the power available at the antenna end of the cable. ERP = EIRP − 2.15 dB.

**Input impedance**
$$Z_\text{in} = R_\text{in} + jX_\text{in},\qquad R_\text{in} = R_\text{rad} + R_\text{loss}.$$
Radiation resistance is defined as radiated power over the squared RMS current at a specified point (IEEE Std 145 [3]):
$$R_\text{rad} = \frac{2P_\text{rad}}{|I|^2}\quad(\text{peak phasor } I).$$
Because the current varies along an antenna, R_rad depends on *where* you refer the current. For a λ/2 dipole referred to its centre (current maximum) R_rad = 73.1 Ω; for a full-wave dipole referred to its current maximum R_rad = 199 Ω but the centre (feed) current is near zero so the input resistance there is very high (verified in `tools/verify/ant_dipole.py`).

**Effective aperture**
$$A_e = \frac{\lambda^2}{4\pi}\,G,\qquad P_\text{received} = S\,A_e\;(\text{polarization-matched, conjugate-matched load}).$$

**Beamwidth–directivity approximations** (θ₁, θ₂ = half-power beamwidths in two orthogonal planes, degrees):
$$D_0 \approx \frac{41\,253}{\theta_1\theta_2}\ (\text{Kraus}),\qquad D_0 \approx \frac{72\,815}{\theta_1^2+\theta_2^2}\ (\text{Tai–Pereira [5]}).$$
41 253 = 4π(180/π)² is the number of square degrees on a sphere. Real antennas with sidelobes typically achieve 26 000–32 000/(θ₁θ₂); King & Wong measured 24 000–31 500 for helices [see helical-antennas](helical-antennas.md).

### Level 2 — derivations

**(a) Directivity of the short dipole and the λ/2 dipole.** For a z-directed current, the far field has only E_θ, and
$$U(\theta) = \frac{\eta_0 k^2}{32\pi^2}\sin^2\theta\,\Big|\int I(z')e^{jkz'\cos\theta}dz'\Big|^2 .$$
For a short (Hertzian) element of length l ≪ λ with uniform current I₀: U = (η₀ k² I₀² l²/32π²) sin²θ. Then
$$P_\text{rad} = \frac{\eta_0 k^2 I_0^2 l^2}{32\pi^2}\cdot 2\pi\int_0^\pi\sin^3\theta\,d\theta = \frac{\eta_0 k^2 I_0^2 l^2}{32\pi^2}\cdot\frac{8\pi}{3},$$
so D₀ = 4π·U_max/P_rad = 4π·(3/8π) = **1.5** (1.76 dBi), and R_rad = 2P_rad/I₀² = (η₀/6π)(kl)² = **80π²(l/λ)²** Ω. A short dipole fed at the centre has a *triangular* current (zero at the tips), so its average current is I₀/2 and R_rad = **20π²(l/λ)²** — a quarter of the uniform-current value. Same pattern, same D = 1.5.

For a centre-fed dipole of length l with the standard sinusoidal current I(z) = I₀ sin[k(l/2 − |z|)], the integral gives
$$U(\theta) = \frac{\eta_0 I_0^2}{8\pi^2}\left[\frac{\cos(\tfrac{kl}{2}\cos\theta)-\cos\tfrac{kl}{2}}{\sin\theta}\right]^2 .$$
For l = λ/2 the bracket is cos(π/2·cosθ)/sinθ; integrating numerically gives D₀ = 1.641 (2.15 dBi), R_rad = 73.08 Ω, and a half-power beamwidth of 78.1°. The closed form uses sine and cosine integrals and is derived on [dipoles and monopoles](dipoles-and-monopoles.md). All verified by `tools/verify/ant_dipole.py` (numeric pattern integration agrees with the Si/Ci closed form to 3 decimal places).

**(b) Effective aperture of the short dipole.** A short dipole of length l in an incident field E (peak, polarization-matched, broadside) develops an open-circuit voltage V_oc = E·l_eff with l_eff = l for uniform current (l/2 for triangular). Into a conjugate-matched load (R_L = R_rad, lossless) the available power is |V_oc|²/(8R_rad). The incident flux density is S = |E|²/(2η₀). Therefore
$$A_e = \frac{|V_{oc}|^2/(8R_\text{rad})}{|E|^2/(2\eta_0)} = \frac{\eta_0\,l^2}{4R_\text{rad}} = \frac{120\pi\,l^2}{4\cdot80\pi^2 l^2/\lambda^2} = \frac{3\lambda^2}{8\pi} = \frac{\lambda^2}{4\pi}\cdot 1.5 = \frac{\lambda^2}{4\pi}D .$$
(The triangular-current case gives the same answer because l_eff and R_rad both change consistently.)

**(c) Why A_e/D is universal (reciprocity argument).** Place antenna 1 and antenna 2 a distance r apart in each other's far field, both matched and polarization-aligned. Transmit P from antenna 1: the flux at 2 is P D₁/(4πr²), so P₂ = P D₁ A_e2/(4πr²). Now transmit P from antenna 2: P₁ = P D₂ A_e1/(4πr²). The Lorentz reciprocity theorem says the transfer ratio is the same both ways for linear, passive, isotropic media, so D₁A_e2 = D₂A_e1, i.e. A_e1/D₁ = A_e2/D₂ = a universal constant. Evaluating it for the short dipole in (b) gives λ²/4π. Including losses (which scale transmit and receive identically) gives A_e = λ²G/4π. An independent thermodynamic proof (an antenna in a black-body enclosure at temperature T must deliver kTB to its matched load) gives the same constant; see Kraus & Marhefka [2] and Orfanidis EWA ch. 16 [4].

**(d) Friis from apertures.** Combining: P_r/P_t = G_t A_er/(4πr²) = G_t G_r (λ/4πr)². The (λ/4πr)² term — "free-space path loss" — appears only because A_er shrinks as λ². With *fixed apertures* (e.g., two dishes of fixed diameter), P_r/P_t = A_et A_er/(λ²r²) actually *improves* as f² [see Friis](../09-propagation-link-budget/friis-free-space-path-loss.md).

**(e) Beamwidth approximation.** If all the power were uniformly spread over a rectangular-ish solid angle Ω_A ≈ θ₁θ₂ (radians), D ≈ 4π/Ω_A = 41 253/(θ₁°θ₂°). Real beams are rounded (Gaussian-like), so the true beam solid angle is larger than θ₁θ₂ for pencil beams; Tai & Pereira [5] derived their formula for cos^n-type patterns. Our check against exact D = 2(n+1) of U = cosⁿθ (forward hemisphere) gives (dB): HPBW 42.2° → exact 13.42, Kraus 13.65, Tai–Pereira 13.11; HPBW 13.5° → exact 23.05, Kraus 23.56, Tai–Pereira 23.02. For broad beams (HPBW ≥ 90°) both formulas *under*estimate. Use them only as sanity checks (`tools/verify/ant_aperture.py`).

**(f) Bandwidth and Q.** Near a resonance, a lossless antenna behaves like a series or parallel RLC with quality factor Q = ω₀W_stored/P_rad (W = time-average stored energy, larger of electric/magnetic). If matched at f₀ to Z₀ = R, the fractional bandwidth over which VSWR ≤ s is approximately
$$\text{FBW}_s \approx \frac{s-1}{Q\sqrt{s}},\qquad \text{FBW}_{2} \approx \frac{1}{\sqrt{2}\,Q}$$
(Yaghjian & Best 2005 [6]; the same 1/(√2 Q) appears in Jackson's patch CAD formulas [patch-antennas](patch-antennas.md)). Loss lowers Q and widens bandwidth — at the cost of efficiency. The minimum possible Q for a given size is the Chu–McLean bound, see [small-antenna limits](small-antenna-limits.md).

### Level 3 — general forms and limits of validity

**Vector effective length and received voltage.** Any antenna can be characterised by a complex vector effective length **h**(θ,φ) such that its transmitted far field is E = −jη₀kI_in e^{−jkr}/(4πr)·**h** and, on receive, V_oc = **h**·E_inc. This single vector carries pattern, polarization and phase; power received into load Z_L is |V_oc|²R_L/(2|Z_in+Z_L|²). Polarization mismatch appears naturally as |ĥ·ê_inc|² — see [polarization](antenna-polarization-and-circular-polarization.md).

**Partial gain.** For any direction, G = G_co + G_cross for two orthogonal polarizations. A GNSS patch quoted as "3 dBic" means the RHCP partial gain is 3 dB above an isotropic RHCP reference. A linear antenna has at most −3 dB partial gain for either circular sense relative to its total gain.

**Gain including polarization and mismatch — the full link term.** P_r = P_t · e_mis,t G_t(θ_t,φ_t) · e_mis,r G_r(θ_r,φ_r) · (λ/4πr)² · PLF · (other losses). Realized gain (IEEE) includes mismatch to a specified impedance but *not* PLF [3].

**Antenna noise temperature.** A receiving antenna also collects noise: T_A = (1/4π)∮ G(θ,φ)T_B(θ,φ)dΩ / (normalised to total efficiency), plus (1 − e_rad)T_phys from its own losses. For a GNSS patch looking at cold sky T_A may be ~50–100 K; a patch pointing at warm ground sees ~290 K. See [thermal noise and noise temperature](../07-noise-linearity/thermal-noise-and-noise-temperature.md).

**Limits of validity.**
- D, G and A_e are far-field quantities. At r < 2D²/λ (large antennas) the measured "gain" is lower than the far-field value.
- Reciprocity fails for non-reciprocal media (ferrites, magnetised plasma, active circuits). Pattern reciprocity still holds for the passive radiator part of an active antenna.
- R_rad from P_rad/|I|² requires specifying the reference point; input impedance is unambiguous only at a defined port (a gap, a connector).
- The 1/(√2 Q) bandwidth rule assumes a single dominant resonance; multi-resonant or deliberately broadband (log-periodic, spiral, horn) antennas are not described by one Q.

## Design equations & rules of thumb

| Quantity | Equation | When valid | Typical values |
|---|---|---|---|
| Directivity | D = 4πU/P_rad | far field | isotropic 0 dBi, short dipole 1.76, λ/2 dipole 2.15, patch 6–9, 3-el Yagi 7–9, 11-el Yagi ≈14 dBi |
| Gain | G = e_rad·D | far field | PCB IFA at 868 MHz 0 to 3 dBi; 97% eff. meander monopole measured by TI [8] |
| Realized gain | G_R = (1−\|Γ\|²)G | at the specified reference Z₀ | VSWR 2 → −0.51 dB |
| dBd | dBi − 2.15 | peak-to-peak comparison | "3 dBd" whip = 5.15 dBi (check which!) |
| Effective aperture | A_e = λ²G/4π | matched, pol.-matched | λ/2 dipole: 626 cm² @433 MHz, 140 cm² @915 MHz, 19.6 cm² @2.45 GHz |
| Aperture efficiency | e_ap = A_e/A_phys | apertures | dish 0.55–0.70, optimum horn 0.51 |
| Directivity from beamwidths | 41253/(θ₁θ₂) or 72815/(θ₁²+θ₂²) | single main lobe | ±0.5 dB sanity check only |
| Far field | r > 2D²/λ, r ≫ D, r ≫ λ | radiating aperture of size D | 11-el 433 MHz Yagi: 8.6 m |
| Reactive near field | r ≲ λ/2π | electrically small antennas | 11 cm at 433 MHz, 3 cm at 1575 MHz |
| Impedance bandwidth | FBW_s ≈ (s−1)/(Q√s) | single resonance | Q = 30 → 2.4 % (VSWR 2) |
| EIRP | P_avail,ant + G | — | 33 dBm into 2 dBi, 1 dB cable → 34 dBm EIRP |

## Worked examples

**Example 1 — EIRP of the Avionics-B telemetry radio.** EBYTE E22-400T33D: 33 dBm (2 W) nominal at 433 MHz. It feeds a λ/4 whip through 30 cm of RG-316 (≈0.3 dB at 433 MHz; see [coax and cables](../03-transmission-lines-matching/coax-and-cables.md)) plus an SMA-to-U.FL pigtail (≈0.3 dB). The whip on the small FC board measures VSWR 1.8 (|Γ| = 0.286, e_mis = 0.918 → −0.37 dB). Assume the whip-plus-board achieves G = 1.5 dBi (a λ/4 whip without a proper ground plane rarely achieves the ideal 5.16 dBi — see [dipoles-and-monopoles](dipoles-and-monopoles.md#finite-ground-planes-and-small-boards)).
- Power at antenna connector: 33 − 0.3 − 0.3 = 32.4 dBm.
- Accepted power: 32.4 − 0.37 = 32.03 dBm.
- EIRP = 32.03 + 1.5 = **33.5 dBm** (2.2 W); ERP = 31.4 dBm.
Whether that is legal depends on the band plan and the service (amateur vs licence-exempt SRD) — see [19-regulations-safety](../19-regulations-safety/singapore-imda-rules.md). Many licence-exempt 433 MHz allocations are limited to ~10 mW ERP, i.e. a 2 W module is only usable under an amateur licence or a specific authorisation.

**Example 2 — How much signal does a GNSS patch catch?** Minimum specified GPS L1 C/A received power is −158.5 dBW (= −128.5 dBm) for a user antenna of 3 dBi linear gain at ≥ 5° elevation (IS-GPS-200 [9]; the spec quotes it that way). A 3 dBi antenna at 1575.42 MHz has A_e = λ²G/4π = (0.1903 m)²·2.0/(4π) = 5.76×10⁻³ m² (57.6 cm²). The flux density is therefore S = P/A_e = 1.41×10⁻¹⁶ W / 5.76×10⁻³ m² ≈ **2.5×10⁻¹⁴ W/m²** (−136 dBW/m²). The C/A signal is ~15 dB *below* the thermal noise in its 2 MHz bandwidth (u-blox [10]); the receiver digs it out by correlation gain. A 17 mm patch has less aperture (and gain) than a 25 mm patch — u-blox notes there is "no magic" around this [10]. An LNA cannot restore the lost signal-to-noise ratio; it only overcomes cable loss downstream.

**Example 3 — Directivity from a datasheet beamwidth.** Our MoM model of an 11-element 433 MHz DL6WU Yagi (`tools/verify/ant_yagi.py`) has HPBW 36.4° (element plane) × 39.8° (perpendicular plane).
- Kraus: 41 253/(36.4 × 39.8) = 28.5 → 14.5 dBi.
- Tai–Pereira: 72 815/(36.4² + 39.8²) = 25.1 → 14.0 dBi.
- Full MoM pattern integration: **14.2 dBi**.
Both approximations bracket the true value within 0.3 dB — good enough to catch a datasheet claiming "18 dBi" for a 40° beam.

**Example 4 — What a bad match costs.** A 915 MHz PCB antenna detuned by the enclosure shows S11 = −6 dB (|Γ| = 0.50, VSWR 3.0). e_mis = 1 − 0.25 = 0.75 → **−1.25 dB**. Retuning to S11 = −15 dB (|Γ| = 0.178) recovers all but 0.14 dB. Note that the *LoRa PA* also sees the mismatch; high VSWR can reduce the PA's output power and linearity beyond the simple 1−|Γ|² term (see [power amplifiers](../06-rf-circuits/power-amplifiers.md)).

**Example 5 — Efficiency of a loaded short whip.** A 433 MHz helically wound "rubber duck" 50 mm long behaves like a short monopole with R_rad ≈ 2–4 Ω (short monopole over a good ground with a triangular current: R_rad = 40π²(h/λ)² = 2.1 Ω for h/λ = 0.072; the helical winding and any top capacitance make the current more uniform and can raise this toward 4×; see [dipoles-and-monopoles](dipoles-and-monopoles.md)). If the loading coil and connector contribute R_loss = 3 Ω, e_rad = 2.1/(2.1+3) = 41 % (−3.9 dB), before any ground-plane effects. This is typical of stubby antennas and is why a full λ/4 whip usually outperforms them.

## Practical notes
- **Datasheet gain is usually peak gain on the vendor's test board.** For PCB/chip antennas the ground plane *is* half the antenna; a different board size changes gain, pattern and tuning (TI AN058 [7]; u-blox [10]). Look for *efficiency* and *TRP* (total radiated power), which matter more for omnidirectional links than peak gain.
- **Watch for dBd/dBi games.** Some ground-station antenna vendors quote dBd (makes numbers smaller — rare) or quote gain "over isotropic" including ground reflection gain (makes numbers bigger by up to ~6 dB — common for mobile/vehicle antennas). For a free-space rocket link, use free-space dBi.
- **Active GNSS antennas**: total "gain" = passive antenna gain (dBic) + LNA gain (dB); u-blox warns that a single figure hides the noise figure and passive gain [10].
- **The antenna includes its feed and mount.** Coax outer-braid currents (common mode) make the cable part of the antenna and change the pattern — see [antenna matching and baluns](antenna-matching-and-baluns.md).
- **Power rating** is limited by heating in loading coils/matching components and by voltage breakdown at high-impedance points (ends of dipoles, EFHW feedpoints), not by "gain".
- **TRP** (total radiated power, CTIA-style OTA measurement) = accepted power × e_rad; e.g., TI's DN024 868 MHz meander monopole reports TRP −0.10 dBm for 0 dBm input, i.e. 97.7 % measured efficiency and 5.05 dBi peak gain on a 43 × 63 mm ground [8].

## Common mistakes & misconceptions
- **"The antenna has 5 dBi gain, so it adds 5 dB of power."** No — it redirects power. The integral of gain over the sphere equals 4π·e_rad ≤ 4π. Higher peak gain means narrower beams and deeper nulls.
- **"Low SWR = good antenna."** SWR measures the match only. Lossy antennas (and dummy loads) can have excellent SWR; many cheap "wideband" antennas achieve their flat SWR with resistive loss.
- **"A λ/4 whip is 5.16 dBi."** Only on an infinite perfect ground. On a small PCB or a rocket bay the ground is part of the antenna and the result is typically 0–3 dBi with a distorted pattern.
- **"Path loss is caused by the air absorbing higher frequencies."** Free-space loss is purely geometric spreading plus the λ² in the receive aperture. Atmospheric absorption at 433 MHz–6 GHz over tens of km is negligible (see [atmospheric attenuation](../09-propagation-link-budget/atmospheric-rain-attenuation.md)).
- **"Directivity and gain are the same thing."** Only for lossless antennas. Electrically small and PCB antennas can have directivity 1.5–5 dBi but gain of −10 dBi.
- **"Radiation resistance is a real resistor you can measure with an ohmmeter."** It is an equivalent resistance representing power leaving as radiation; it only exists at RF, depends on the reference point, and is invisible at DC.
- **"dBi and dBic are the same."** They are the same scale but refer to different reference polarizations; a linear 3 dBi antenna is at best 0 dBic for a CP signal.
- **"The near field ends at one wavelength."** The reactive region of a small antenna is ~λ/2π; the radiating near field of a large antenna extends to ~2D²/λ, which can be many metres (an 11-element 433 MHz Yagi needs ≥ 8.6 m for accurate gain measurement).
- **"Using gain from beamwidth is exact."** Beamwidth formulas ignore sidelobes and back lobes; errors of 0.5–2 dB are normal.
- Forum-observed confusion (EE Stack Exchange, r/rfelectronics, r/meshtastic — anecdotal): users swapping a stock 2 dBi whip for a "10 dBi" fibreglass collinear and getting *worse* range to an overhead or nearby node because the collinear's narrow elevation beam puts the target in a null. The physics is the redistribution argument above.

- **"A longer antenna always has more gain."** A centre-fed wire's broadside directivity rises 2.15 → 3.82 → 5.16 dBi at λ/2, λ, 1.25λ and then *falls* as the lobe splits; only phased (collinear) structures turn length into gain — about 10 log(2L/λ) dBi of *elevation* squeeze for an omni ([dipoles](dipoles-and-monopoles.md#longer-is-not-better-whips-beyond-λ4-and-full-wave-dipoles), [identification](antenna-identification-guide.md#level-2--gain-from-size)).
- **"A 2.4 GHz antenna will do for 900 MHz."** A 2.45 GHz λ/4 whip (29 mm) at 915 MHz is 0.09λ: MoM gives Z ≈ 2.5 − j257 Ω, **mismatch loss 21 dB**; at 433 MHz 35 dB. The reverse (a 915 MHz whip at 2.45 GHz, ≈ 0.64λ) is 36 − j115 Ω, 4.6 dB, with an up-tilted pattern. A 433 MHz whip on 868/915 MHz is ≈ 0.5λ — a high-impedance point — 7.1–7.3 dB (`tools/verify/ant2_qa.py` §c). Use an antenna made for the band (or a true dual-band design).
- **"An antenna must be resonant to radiate."** Resonance only makes the input reactance zero. A non-resonant wire with a low-loss matching network (tuner) radiates the same power; what matters is radiation efficiency R_rad/(R_rad + R_loss), including the matching network and feedline loss ([HF wire antennas](wire-antennas-hf-random-wire-fan-dipole.md)).
- **"For receive-only SDR the antenna doesn't matter."** True at HF (man-made/galactic noise 20–50 dB above kT₀ masks antenna loss: −30 dB efficiency costs 0.5 dB at 7 MHz), false at UHF and GNSS, where −3 dB of efficiency costs 2–6 dB of SNR ([wideband/SDR antennas](multiband-and-wideband-antennas.md#receive-only-sdr-antennas-does-length-matter)).
- **"Antennas stop working above some frequency."** Antenna behaviour scales with λ; what changes is practicality — conductor and dielectric losses grow (R_s ∝ √f), tolerances shrink, and at infrared/optical frequencies metals behave as lossy plasmas (nano-antennas use plasmonic resonances). There is no frequency at which "antennas stop".

## How to simulate / verify
- `python3 tools/verify/ant_dipole.py` — directivity by numerical integration, R_rad closed form vs numeric, beamwidths, monopole values.
- `python3 tools/verify/ant_aperture.py` — A_e table, beamwidth–directivity approximations vs exact cosⁿ patterns, aperture/dish/horn efficiencies, far-field distances.
- `python3 tools/verify/ant_mom_wire.py` — a thin-wire MoM that reports Z_in, directivity and the energy check P_rad/P_in (an "average-gain test"; should be 1.000 for lossless wires).
- In NEC-2/4 (4nec2, xnec2c, EZNEC) check the *average gain* — for a lossless free-space model it must be 1.000 (0 dB); deviations indicate a bad model ([antenna-simulation-nec-openems](antenna-simulation-nec-openems.md)).
- Measure realized gain by comparison against a reference antenna, and efficiency by Wheeler cap or reverberation chamber — see [antenna measurement](antenna-measurement.md).

## Open questions / gaps
- A careful table of *realistic* gains for λ/4 whips on small flight-computer boards (e.g., 50 × 100 mm) at 433 and 915 MHz needs full-wave simulation (openEMS) or measurement; the 0–3 dBi figure above is a range from app notes, not a computed value.
- The GPS minimum-power spec detail (reference antenna definition) should be cross-checked against the latest IS-GPS-200 revision by the 09 domain.

## Sources
1. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016 — ch. 2 (fundamental parameters: directivity, efficiency e₀ = e_r e_cd, gain, A_e, Friis), ch. 4 (dipoles). (textbook)
2. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., McGraw-Hill, 2002 — ch. 2 (beam solid angle, D ≈ 41 253/θφ, aperture–directivity relation). (textbook)
3. IEEE Std 145-1993, *IEEE Standard Definitions of Terms for Antennas* — defs 2.107 directivity, 2.115 effective area (= λ²G/4π), 2.143 far-field region (2D²/λ), 2.165 gain (excludes mismatch and polarization), 2.250 reactive near field (λ/2π), 2.308 radiation efficiency, 2.313 radiation resistance, 2.321 realized gain. https://www.ece.mcmaster.ca/faculty/nikolova/antenna_dload/IEEEStandard_AntennaTerms.pdf (standard; the current revision is IEEE Std 145-2013 with the same core definitions)
4. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers, 2016 (free) — ch. 15 "Radiation Fields", ch. 16 "Transmitting and Receiving Antennas" (§16.3 effective area, §16.7 antenna noise temperature), ch. 17 "Linear and Loop Antennas". [chapter numbers checked against the 2016 edition's table of contents, W5-S18 2026-10-13; the 2010 edition numbers ch. 11–18 one lower, with Aperture Antennas as ch. 18 and Currents on Linear Antennas as ch. 21]. https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook)
5. C.-T. Tai and C. S. Pereira, "An approximate formula for calculating the directivity of an antenna," *Proc. IEEE*, vol. 64, no. 2, pp. 235–236, 1976. (peer-reviewed; formula as widely reproduced in Balanis ch. 2)
6. A. D. Yaghjian and S. R. Best, "Impedance, bandwidth, and Q of antennas," *IEEE Trans. Antennas Propag.*, vol. 53, no. 4, pp. 1298–1324, 2005 — FBW ≈ (s−1)/(Q√s). (peer-reviewed)
7. R. Wallace, TI Application Note AN058 (SWRA161), *Antenna Selection Guide* — datasheet gains depend on test board; 91 % (868 MHz) vs 7 % (169 MHz) efficiency in the same board area; VSWR/RL definitions. https://www.ti.com/lit/pdf/swra161 (app note; note: its introductory physics is loose, see [pcb-and-chip-antennas](pcb-and-chip-antennas.md))
8. R. Wallace, TI Design Note DN024 (SWRA227), *Monopole PCB Antenna with Single or Dual Band Option* — CTIA OTA results: 97.7 % efficiency, 5.05 dBi at 868 MHz. https://www.ti.com/lit/pdf/swra227 (app note, measured)
9. IS-GPS-200 (Navstar GPS Space Segment/Navigation User Interfaces), section 3.3.1.6 — minimum received signal power −158.5 dBW (L1 C/A) for a 3 dBi linearly polarised antenna. https://www.gps.gov/technical/icwg/ (standard; value to be cross-checked with the latest revision)
10. u-blox, *GNSS antennas — RF design considerations for u-blox GNSS receivers*, application note UBX-15030289 R03, 2019 — active vs passive gain, patch size vs aperture, GNSS signal ~15 dB below thermal noise. https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf (app note)
11. Verification scripts in this repository: `tools/verify/ant_dipole.py`, `tools/verify/ant_aperture.py`, `tools/verify/ant_mom_wire.py`, `tools/verify/ant_yagi.py`. (derivation/verification)
