---
title: Electromagnetic units and constants (ε0, μ0, c, η0 after the 2019 SI)
domain: 02-electromagnetics
slug: electromagnetic-units-and-constants
tags: [constants, SI, CODATA, mu0, eps0, eta0, impedance-of-free-space, units, gaussian, dBuV/m]
prerequisites: [../00-math-foundations/decibels-and-log-units.md]
related: [maxwells-equations.md, wave-equation-plane-waves-polarization.md, poynting-vector-power-flow.md, ../09-propagation-link-budget/friis-free-space-path-loss.md, ../19-regulations-safety/rf-exposure-safety.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Electromagnetic units and constants (ε0, μ0, c, η0 after the 2019 SI)

## Questions this page answers
- What are the exact values of ε0, μ0, c and the impedance of free space today?
- Is μ0 still exactly 4π×10⁻⁷ H/m after the 2019 SI redefinition, and does it matter for RF work?
- Why is the impedance of free space 376.73 Ω and not exactly 120π Ω?
- How do I convert between V/m, dBµV/m, W/m² and dBm/m²?
- How do I convert a received power in dBm into a field strength in dBµV/m?
- What goes wrong when I mix Gaussian (CGS) and SI formulas from old physics books?
- What are the units of E, H, D, B, J, ρ, σ, ε, μ and how do they fit together?

## TL;DR
- **c = 299 792 458 m/s exactly** (defines the metre). The elementary charge e, Planck's constant h and Boltzmann's constant k are also exact since 20 May 2019 [1][2].
- **μ0 is no longer exact.** CODATA 2022: μ0 = 1.256 637 061 27(20) × 10⁻⁶ N/A² (relative uncertainty 1.6 × 10⁻¹⁰) [1]. It differs from 4π × 10⁻⁷ by **−1.4 × 10⁻¹⁰** (CODATA 2022) or +5.5 × 10⁻¹⁰ (CODATA 2018) — *the sign flipped between adjustments*; either way it is ~10⁶ times smaller than any RF measurement can resolve. Verified by `tools/verify/em_constants.py`.
- **ε0 = 1/(μ0c²) = 8.854 187 8188(14) × 10⁻¹² F/m** (CODATA 2022) [1].
- **η0 = Z0 = μ0c = √(μ0/ε0) = 376.730 313 412(59) Ω** (CODATA 2022) [1]. The textbook shortcut 120π = 376.99 Ω is 0.069 % high — fine for hand calculations, not for calibration standards.
- Engineering shortcuts: c ≈ 3×10⁸ m/s (+0.069 %), ε0 ≈ 10⁻⁹/(36π) F/m (−0.14 %), μ0 ≈ 4π×10⁻⁷ H/m (≈ 1×10⁻¹⁰).
- Plane-wave field ↔ power density in free space: S = E²/η0 (E rms). **1 V/m rms ↔ 2.654 mW/m²**; **dBm/m² = dBµV/m − 115.76**.
- Isotropic receive antenna: **E [dBµV/m] = P [dBm] + 77.2 + 20 log₁₀ f [MHz]** (→ +129.9 dB at 433 MHz, +136.4 dB at 915 MHz).
- Gaussian units hide ε0 and μ0 (and put c into Maxwell's equations); never paste a Gaussian formula into an SI calculation without converting.

## Intuition (no math)
Electromagnetism needs three "exchange rates" between electrical quantities and mechanical ones:
how much force two charges exert (ε0), how much force two currents exert (μ0), and how fast the
disturbance travels (c). Only two are independent because c² = 1/(ε0μ0) — once you know how
strongly space "resists" electric and magnetic fields you know how fast waves move through it.

Before 2019 the SI fixed μ0 by *defining* the ampere through the force between two parallel wires,
so μ0 was exactly 4π×10⁻⁷ by decree. In 2019 the ampere was redefined by fixing the elementary
charge e instead (one ampere = a fixed number of electrons per second) [2]. The price is that μ0
now has to be *measured* — in practice through the fine-structure constant α, because
μ0 = 2αh/(e²c) and h, e, c are all exact. α is known to about 1.6 parts in 10¹⁰, so μ0 is too.

The "impedance of free space" η0 ≈ 377 Ω is the ratio of E to H in a travelling plane wave. It is
not a resistor you can measure with an ohmmeter; it tells you how many volts per metre of electric
field accompany each ampere per metre of magnetic field when energy is flowing freely through
space. It is why a 1 V/m field carries only 2.65 mW/m², and why antennas convert "field" into
"watts" the way they do.

## The math

### Level 1 — the numbers and what they mean

| Symbol | Name | Value (CODATA 2022 unless stated) | SI unit | Status |
|---|---|---|---|---|
| c | speed of light in vacuum | 299 792 458 | m s⁻¹ | exact |
| h | Planck constant | 6.626 070 15 × 10⁻³⁴ | J s | exact |
| e | elementary charge | 1.602 176 634 × 10⁻¹⁹ | C | exact |
| k | Boltzmann constant | 1.380 649 × 10⁻²³ | J K⁻¹ | exact |
| α | fine-structure constant | 7.297 352 5643(11) × 10⁻³ | 1 | measured |
| μ0 | vacuum magnetic permeability | 1.256 637 061 27(20) × 10⁻⁶ | N A⁻² = H m⁻¹ | measured |
| ε0 | vacuum electric permittivity | 8.854 187 8188(14) × 10⁻¹² | F m⁻¹ | measured |
| Z0 = η0 | characteristic impedance of vacuum | 376.730 313 412(59) | Ω | measured |
| Y0 = 1/Z0 | admittance of vacuum | 2.654 419 × 10⁻³ | S | measured |

Digits in parentheses are the one-standard-deviation uncertainty in the last digits [1].
Sources: NIST CODATA 2022 database [1]; exactness statements from the SI Brochure [2].

Key exact relations that survive the redefinition (SI Brochure §2.3.1 [2]):
$$\varepsilon_0\mu_0 = \frac{1}{c^2}\quad(\text{exact}),\qquad \frac{Z_0}{\mu_0} = c\quad(\text{exact}),\qquad \varepsilon_0,\ \mu_0,\ Z_0,\ Y_0 \text{ all share the same relative uncertainty.}$$

### Level 2 — where μ0 comes from now

The fine-structure constant is defined (SI form) as
$$\alpha = \frac{e^2}{4\pi\varepsilon_0\hbar c} = \frac{e^2\mu_0 c}{2h}.$$
Solving for μ0:
$$\boxed{\mu_0 = \frac{2\alpha h}{e^2 c}}$$
With exact h, e, c, the uncertainty of μ0 is exactly that of α. Then ε0 = 1/(μ0c²) and
Z0 = μ0c = 2αh/e² = 2α·R_K where R_K = h/e² = 25 812.807 45… Ω is the (now exact) von Klitzing
constant. So **Z0 = 2α R_K** — a pleasing link between the quantum Hall resistance standard and the
impedance of free space.

Numbers (computed in `tools/verify/em_constants.py`, matching NIST to < 10⁻¹¹):

| Adjustment | α | μ0 / (4π×10⁻⁷ H/m) − 1 |
|---|---|---|
| exact definition (pre-2019) | — | 0 |
| CODATA 2018 | 7.297 352 5693(11)×10⁻³ | +5.47 × 10⁻¹⁰ |
| CODATA 2022 | 7.297 352 5643(11)×10⁻³ | −1.38 × 10⁻¹⁰ |

The SI Brochure notes that at the moment of redefinition μ0 equalled 4π×10⁻⁷ H/m with a relative
standard uncertainty of 2.3×10⁻¹⁰ [2]. The 2018→2022 shift (−6.9×10⁻¹⁰, driven by new α
measurements) moved the value to the other side of 4π×10⁻⁷. **For any RF/antenna/circuit work,
use 4π×10⁻⁷ without hesitation**; the difference is roughly a million times below VNA or antenna
range uncertainty (typically 10⁻³–10⁻²).

### Level 2 — impedance of free space and plane-wave power density

For a uniform plane wave in vacuum (derived in
[wave-equation-plane-waves-polarization](wave-equation-plane-waves-polarization.md)):
$$\eta_0 = \frac{|E|}{|H|} = \sqrt{\frac{\mu_0}{\varepsilon_0}} = \mu_0 c \approx 376.730\ \Omega.$$
The time-averaged power density (see [poynting-vector-power-flow](poynting-vector-power-flow.md)):
$$S = \frac{E_\text{rms}^2}{\eta_0} = \frac{E_\text{pk}^2}{2\eta_0} = \eta_0 H_\text{rms}^2\quad[\text{W/m}^2].$$

**The 120π shortcut.** If c were exactly 3×10⁸ m/s and μ0 exactly 4π×10⁻⁷, η0 = 4π×10⁻⁷ × 3×10⁸ =
120π = 376.99 Ω. The 0.069 % excess comes entirely from rounding c. Many textbooks (e.g. Balanis,
Cheng) use 120π; results that depend on η0 linearly (radiation resistance, field strength) inherit a
0.07 % bias — irrelevant in practice, but a source of apparent "disagreements" in the fourth digit
(e.g. 80π² vs 789.6 Ω in the dipole radiation-resistance constant, see
[radiation-from-currents-hertzian-dipole](radiation-from-currents-hertzian-dipole.md)).

### Level 2 — log units for field strength

Definitions (all rms, all free-space plane wave where power density is involved):
- dBµV/m = 20 log₁₀(E / 1 µV/m)
- dBµA/m = 20 log₁₀(H / 1 µA/m)
- dBm/m² = 10 log₁₀(S / 1 mW/m²)
- dBW/m² = dBm/m² − 30

Relations (derived from S = E²/η0, H = E/η0):
$$\text{dBm/m}^2 = \text{dB}\mu\text{V/m} - 115.76,\qquad \text{dB}\mu\text{A/m} = \text{dB}\mu\text{V/m} - 51.52.$$
(Derivation: dBµV/m = 20 log₁₀E + 120 and dBm/m² = 20 log₁₀E − 10 log₁₀η0 + 30, so the difference is
120 + 25.76 − 30 = 115.76 dB; similarly 20 log₁₀η0 = 51.52 dB.)

**Received power ↔ field strength.** An antenna of gain G (linear) has effective aperture
A_e = Gλ²/(4π) (see [antenna-fundamentals](../08-antennas/antenna-fundamentals.md)). Matched and
polarization-aligned, it delivers P = S·A_e. For an isotropic antenna (G = 1):
$$E_{\text{dB}\mu\text{V/m}} = P_\text{dBm} + 77.2 + 20\log_{10} f_\text{MHz} - G_\text{dBi}.$$
The constant: P_dBm = E_dBµV/m − 115.76 + 20 log₁₀(299.79/f_MHz) − 10 log₁₀(4π) = E − 77.21 − 20 log₁₀ f_MHz.
Verified numerically (constant + 20 log f = 129.95 dB at 433 MHz, 136.44 dB at 915 MHz, 141.16 dB at
1575.42 MHz, 145.00 dB at 2.45 GHz).

Antenna factor (EMC): AF [dB/m] = E [dBµV/m] − V [dBµV] at the receiver's 50 Ω input; for a
matched antenna AF = 20 log₁₀ f_MHz − G_dBi − 29.78 (50 Ω). (Detailed in 17-test-measurement.)

### Level 3 — SI vs Gaussian (CGS) and other systems

Physics texts (Jackson 2nd ed., Landau–Lifshitz, Feynman uses SI but many classics do not) write
Maxwell's equations in Gaussian units:

| Law | SI | Gaussian |
|---|---|---|
| Gauss | ∇·**D** = ρ, **D** = ε0**E** + **P** | ∇·**E** = 4πρ (vacuum) |
| Ampère–Maxwell | ∇×**H** = **J** + ∂**D**/∂t | ∇×**B** = (4π/c)**J** + (1/c)∂**E**/∂t |
| Faraday | ∇×**E** = −∂**B**/∂t | ∇×**E** = −(1/c)∂**B**/∂t |
| Lorentz force | **F** = q(**E** + **v**×**B**) | **F** = q(**E** + (**v**/c)×**B**) |
| Coulomb | F = q₁q₂/(4πε0r²) | F = q₁q₂/r² |

Conversion recipe (SI → Gaussian): replace ε0 → 1/(4π), μ0 → 4π/c², and **B** → **B**/c. Some
conversions you will meet in ferrite/magnetics data sheets:
- 1 gauss (G) = 10⁻⁴ tesla (T); 1 oersted (Oe) = 10³/(4π) A/m ≈ 79.577 A/m.
- In vacuum, 1 Oe of H produces 1 G of B. Ferrite data often quote 4πM_s in gauss (e.g. "4πM_s =
  1800 G" for a YIG-like garnet) — this is μ0M_s = 0.18 T in SI.
- Gyromagnetic ratio for electron spin: γ/2π ≈ 28.0 GHz/T = 2.80 MHz/Oe (used in
  [magnetic-materials-permeability](magnetic-materials-permeability.md)).
- 1 statvolt = 299.792458 V; 1 statcoulomb = 3.335 64 × 10⁻¹⁰ C.

Heaviside–Lorentz (rationalised Gaussian, used in particle physics) removes the 4π's but keeps
the c's. "Natural units" set c = ε0 = 1. None of these change any measurable quantity, but formulas
look different by factors of 4π and c; the classic error is a missing 4π in a radiated-power
formula copied from a Gaussian text.

**Units cheat-sheet (SI):**

| Quantity | Symbol | Unit | In base units |
|---|---|---|---|
| Electric field | **E** | V/m | kg m s⁻³ A⁻¹ |
| Electric flux density (displacement) | **D** | C/m² | A s m⁻² |
| Magnetic field (intensity) | **H** | A/m | A m⁻¹ |
| Magnetic flux density | **B** | T = Wb/m² = V s/m² | kg s⁻² A⁻¹ |
| Current density | **J** | A/m² | |
| Surface current density | **J**s, **K** | A/m | |
| Charge density | ρ | C/m³ | |
| Conductivity | σ | S/m | |
| Permittivity | ε = ε0εr | F/m | |
| Permeability | μ = μ0μr | H/m | |
| Poynting vector / power density | **S** | W/m² | |
| Surface resistance | R_s | Ω (often "Ω/square") | |
| Wave impedance | η, Z_w | Ω | |

## Design equations & rules of thumb

| Equation | When valid | Typical value / note |
|---|---|---|
| c = 1/√(ε0μ0) | always (exact) | 299 792 458 m/s |
| η0 = √(μ0/ε0) = μ0c | vacuum plane wave | 376.730 Ω (≈ 377 Ω; 120π = 376.99 Ω) |
| λ[m] = 299.79 / f[MHz] | vacuum/air | 0.6924 m at 433 MHz, 0.3276 m at 915 MHz, 0.1903 m at 1575.42 MHz |
| S = E²_rms/η0 | far field, free space | 1 V/m → 2.654 mW/m² |
| dBm/m² = dBµV/m − 115.76 | far field | |
| E[dBµV/m] = P[dBm] + 77.2 + 20 log f[MHz] − G[dBi] | matched, co-polarised | 433 MHz: +129.9 dB |
| Air: εr ≈ 1.000 59 (dry, sea level, low freq) | RF | λ in air is 0.03 % shorter than in vacuum; usually ignored |
| μ0 ≈ 4π×10⁻⁷ H/m | all engineering | error ≈ 10⁻¹⁰ |
| ε0 ≈ 8.854 pF/m ≈ 10⁻⁹/(36π) | hand calcs | −0.14 % for the 36π form |

(The air value 1.000 59 is ≈ (n−1) = 2.9×10⁻⁴ for dry air at 0 °C, 1 atm, doubled for εr = n²;
humidity raises it — see [atmospheric effects](../09-propagation-link-budget/atmospheric-rain-attenuation.md).
Medium confidence; standard refractivity N ≈ 315 at the surface corresponds to n − 1 = 3.15×10⁻⁴.)

## Worked examples

**1. Is "4π×10⁻⁷" still OK in my antenna script?**
Relative error = |μ0/(4π×10⁻⁷) − 1| = 1.38×10⁻¹⁰ (CODATA 2022). An antenna gain measured to
±0.1 dB is uncertain by ±2.3 % = 2.3×10⁻². The constant's error is 10⁸ times smaller. Yes — use it.

**2. Field strength of −100 dBm received on a 433 MHz dipole.**
Dipole G = 2.15 dBi. E = −100 + 77.2 + 20 log₁₀(433) − 2.15 = −100 + 77.2 + 52.73 − 2.15 =
**27.8 dBµV/m** ≈ 24.5 µV/m. Power density = 27.8 − 115.76 = −88.0 dBm/m² = 1.6 pW/m².

**3. What field does a 2 W E22-400T33D at 1 km produce?**
(Isotropic radiator assumed; full treatment in
[poynting-vector-power-flow](poynting-vector-power-flow.md).) S = P/(4πr²) = 2/(4π·10⁶) =
1.59×10⁻⁷ W/m². E = √(η0 S) = √(376.73 × 1.59×10⁻⁷) = 7.75 mV/m rms = **77.8 dBµV/m**.
Shortcut: E = √(30 P G)/r = √(30·2)/1000 = 7.75 mV/m. (The "30" is η0/(4π) = 29.98.)

**4. Converting a ferrite datasheet.** A NiZn ferrite lists 4πM_s = 3000 G. In SI, μ0M_s = 0.30 T
and M_s = 0.30/μ0 = 2.39×10⁵ A/m. (Used in the Snoek-limit example in
[magnetic-materials-permeability](magnetic-materials-permeability.md).)

## Practical notes
- Simulation tools (openEMS, NEC-2, HFSS, CST, scikit-rf) hard-code their own constants, usually
  c = 299 792 458 m/s and μ0 = 4π×10⁻⁷ (openEMS's MATLAB/Python interface defines them this way —
  unverified here for the other tools; see [openems-workflow](../16-simulation-tools/openems-workflow.md)).
  Differences between tools at the 10⁻⁴ level are rounding (e.g. c ≈ 3×10⁸ or 120π), not physics.
- When checking a formula in the KB against a textbook, first identify: (a) peak or rms phasors,
  (b) e^{jωt} or e^{−iωt}, (c) SI or Gaussian, (d) 120π or 376.73. Most "discrepancies" in the third
  or fourth significant figure are one of these.
- Regulatory limits (IMDA/FCC/ETSI) and RF exposure limits (ICNIRP) are stated either in field
  strength (V/m, A/m) or power density (W/m²); the plane-wave conversion S = E²/377 is only valid in
  the far field (see [near-field-far-field](near-field-far-field.md)).

## Common mistakes & misconceptions
- **"μ0 is exactly 4π×10⁻⁷."** True only before 20 May 2019. Now it is measured; the difference is
  ~10⁻¹⁰ and practically irrelevant, but statements of "exact" are wrong [2].
- **"η0 is exactly 120π Ω."** It never was; 120π follows from rounding c to 3×10⁸.
- **"377 Ω is a resistance, so free space dissipates power."** η0 relates E and H of a travelling
  wave; power carried away is not dissipated locally. The same is true of the characteristic
  impedance of a lossless transmission line.
- **Peak vs rms.** S = E²/η0 needs rms E; with peak amplitude use S = E²_pk/(2η0). Many online
  calculators silently use peak. Factor-of-2 (3 dB) errors are the most common field-strength error.
- **dBµV vs dBµV/m.** The first is a voltage at a receiver port, the second a field. They differ by
  the antenna factor, which is frequency dependent.
- **Copying Gaussian formulas.** Larmor's formula P = 2q²a²/(3c³) (Gaussian) becomes
  P = q²a²/(6πε0c³) in SI. Dropping the 4πε0 gives answers off by ~10¹¹.

## How to simulate / verify
- `python3 tools/verify/em_constants.py` — recomputes μ0, ε0, Z0 from α, h, e, c and checks them
  against the NIST published values (agreement < 10⁻¹¹ relative); prints field-unit conversions.
- `scipy.constants` exposes `mu_0`, `epsilon_0`, `c`, `physical_constants['characteristic impedance
  of vacuum']`. Check which CODATA release your SciPy uses (`scipy.constants.physical_constants`
  docstring) — older SciPy versions carry CODATA 2018 values.

## Open questions / gaps
- Air permittivity vs humidity at the level needed for precision range measurements is only cited
  at medium confidence here; the 09-propagation domain should give the ITU-R P.453 refractivity
  formula.

## Sources
1. NIST, *CODATA Internationally Recommended 2022 Values of the Fundamental Physical Constants*,
   online database https://physics.nist.gov/cuu/Constants/ (μ0, ε0, Z0, α pages fetched 2026-09-27);
   P. J. Mohr, D. B. Newell, B. N. Taylor, E. Tiesinga, "CODATA recommended values of the fundamental
   physical constants: 2022," *Rev. Mod. Phys.* 97, 025002 (2025), arXiv:2409.03787. (standard)
2. BIPM, *The International System of Units (SI Brochure)*, 9th ed., 2019 (updated), §2.3.1 (definition
   of the ampere and consequences for μ0, ε0, Z0, Y0), Table 1 (defining constants).
   https://www.bipm.org/en/publications/si-brochure (standard)
3. J. D. Jackson, *Classical Electrodynamics*, 3rd ed., Wiley 1999, Appendix "On units and
   dimensions" (SI ↔ Gaussian conversion table). (textbook)
4. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., Cambridge/Pearson 2013/2017,
   Appendix C "Units". (textbook)
5. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley 2016, §2 (use of η ≈ 120π,
   effective aperture Ae = λ²G/4π). (textbook)
6. CODATA 2018 value of α and μ0 (7.297 352 5693(11)×10⁻³; 1.256 637 062 12(19)×10⁻⁶ N/A²):
   E. Tiesinga et al., *Rev. Mod. Phys.* 93, 025010 (2021). (standard)
