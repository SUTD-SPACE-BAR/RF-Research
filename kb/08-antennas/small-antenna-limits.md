---
title: Electrically small antennas — Wheeler, Chu, McLean limits; efficiency–bandwidth trade-off; fractal and "tiny antenna" claims
domain: 08-antennas
slug: small-antenna-limits
tags: [electrically-small-antenna, chu-limit, mclean, wheeler, radiansphere, q-factor, bandwidth, efficiency, fractal-antenna, chip-antenna, superdirectivity]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, ../01-circuit-theory/resonance-and-q.md]
related: [pcb-and-chip-antennas.md, loop-antennas.md, antennas-on-rockets.md, gnss-antennas.md, ../03-transmission-lines-matching/broadband-matching-bode-fano.md, multiband-and-wideband-antennas.md, inductive-coupling-rfid-nfc-wpt.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Electrically small antennas and their fundamental limits

## Questions this page answers
- Why can't I make a tiny 433 MHz antenna that is efficient *and* wideband?
- What is the Chu limit, and what exactly does "ka" measure?
- What is the difference between Chu's, Hansen's and McLean's Q formulas?
- How much bandwidth can a chip antenna at 915 MHz possibly have?
- Why does a lossy small antenna look "wideband"?
- What is Wheeler's radiansphere?
- Do fractal antennas beat the limit? What about "nano" or crowdfunded "tiny long-range" antennas?
- Can a small antenna be directional (superdirective)?
- Does a matching network fix a small antenna's bandwidth?

## TL;DR
- Enclose the antenna — **including its ground plane and any structure carrying significant current** — in the smallest sphere of radius a. With k = 2π/λ, an antenna is electrically small when ka < 1 (a < λ/2π, Wheeler's radiansphere).
- **Minimum radiation Q** of a linearly polarized antenna radiating a single dipole mode (McLean 1996 [4], exact; our numerical energy integral agrees to every digit shown, `tools/verify/ant_small_limits.py`):
$$Q_\text{min}=\frac{1}{(ka)^3}+\frac{1}{ka}.$$
  For a CP antenna using both TE₁ and TM₁ modes, Q_min = ½[1/(ka)³ + 2/(ka)]. The often-quoted Hansen form of Chu's result, (1+3k²a²)/[k³a³(1+k²a²)], is up to 12 % higher at ka ≈ 0.5 and agrees as ka → 0 or 1.
- **Bandwidth ≤ (s−1)/(Q√s)**; for VSWR 2, FBW ≤ 1/(√2 Q_min) at 100 % efficiency. A lossy antenna's Q is η_rad·Q_rad, so bandwidth can be "bought" only with efficiency: **FBW·(1/η) is bounded**.
- Reader's bands: 433 MHz in a 20 mm-radius sphere: Q ≥ 172 → ≤ 1.8 MHz (VSWR 2) at 100 % efficiency; 915 MHz in a 15 mm sphere: ≤ 14 MHz, less than the 26 MHz US ISM band unless efficiency < 55 %; a GNSS L1 antenna in a 10 mm sphere: ≤ 36 MHz.
- Real antennas sit well **above** the bound: wire/planar small antennas typically 1.5–3× Q_min (Thal and Gustafsson tightened bounds for specific geometries). Our 30 mm loop at 433 MHz has radiation Q ≈ 6.5× the bound.
- TI measured 91 % efficiency for an 868 MHz PCB antenna and **7 %** for a 169 MHz antenna in the identical board area [8] — the limit in action.
- **Fractal geometry does not beat the limit.** Best (2003) showed that resonant frequency of small wire antennas depends mainly on total wire length and occupied volume, not on fractal dimension; fractals offer no Q or efficiency advantage over meanders/helices of the same size [6]. u-blox measured fractal GNSS antennas at −1.2 to +2.5 dBic depending on ground plane, ≈ 3 dB below a patch [9].
- Matching networks cannot beat Bode–Fano: they can shape, not create, bandwidth ([broadband matching](../03-transmission-lines-matching/broadband-matching-bode-fano.md)).

## Intuition (no math)
Every antenna is surrounded by stored (reactive) energy — electric energy near its charges, magnetic energy near its currents. Radiation is energy that escapes; stored energy sloshes back and forth each cycle. The ratio of stored to radiated energy per cycle is Q. High Q means narrow bandwidth, high circulating currents, high voltages — and extreme sensitivity to loss and to nearby objects.

Here is the key physical fact (Chu 1948, Wheeler 1947): even for the *best possible* antenna of a given size, the fields just outside a sphere of radius a must contain a certain amount of non-radiating energy, because the wave has to "pull away" from a region that is small compared to λ/2π. Inside radius λ/2π (the radiansphere), fields are mostly reactive; outside, mostly radiating. If your whole antenna sits deep inside the radiansphere, the field it produces has a large reactive part no matter how clever the shape. So a small antenna is necessarily high-Q, narrowband and loss-sensitive. Filling the sphere with conductor (or magnetic material) is the only way to approach the bound; shapes that fill only a small part of it (thin wires, flat traces) are further from it.

Loss "helps" bandwidth because a resistor in the antenna absorbs energy, lowering Q — the same way adding a resistor to a tuned circuit broadens it. That bandwidth is real, but the power is heat, not radiation. A small antenna that is "surprisingly wideband" is usually surprisingly inefficient.

## The math

### Level 1 — definitions and the formulas you use
- a: radius of the smallest sphere enclosing all significant current-carrying structure (m). k = 2π/λ.
- Q = 2ω₀·max(W_e, W_m)/P_rad (radiation Q; W = time-averaged *non-radiating* stored energy).
- McLean (exact, single TM₁₀ or TE₁₀ mode): Q_lp = 1/(ka)³ + 1/(ka). Both TE and TM (CP or a Huygens source): Q_cp = ½[1/(ka)³ + 2/(ka)].
- Hansen's version of Chu: Q_Chu ≈ (1 + 3(ka)²)/[(ka)³(1 + (ka)²)].
- Matched fractional bandwidth (VSWR ≤ s): FBW ≈ (s−1)/(Q√s) (Yaghjian & Best [5]); s = 2: FBW = 0.707/Q.
- Lossy antenna: Q_tot = η·Q_rad, so FBW_tot ≈ FBW_rad/η.

Table (script output):

| ka | numeric energy integral | McLean | Hansen/Chu | Chu circuit energy | CP bound |
|---|---|---|---|---|---|
| 0.05 | 8020 | 8020 | 8040 | 8020 | 4020 |
| 0.10 | 1010 | 1010 | 1020 | 1010 | 510 |
| 0.20 | 130.0 | 130.0 | 134.6 | 130.0 | 67.5 |
| 0.30 | 40.37 | 40.37 | 43.15 | 40.37 | 21.85 |
| 0.50 | 10.00 | 10.00 | 11.20 | 10.00 | 6.00 |
| 1.00 | 2.00 | 2.00 | 2.00 | 2.00 | 1.50 |

### Level 2 — derivation of the McLean bound
Outside the sphere r > a, any radiated field can be expanded in spherical modes. The lowest-order TM mode (the field of an electric dipole) has, for e^{jωt},
$$H_\phi=A\,h_1^{(2)}(kr)\sin\theta,\quad E_r=\frac{2A\cos\theta}{j\omega\varepsilon r}h_1^{(2)}(kr),\quad E_\theta=-\frac{A\sin\theta}{j\omega\varepsilon r}\frac{d}{dr}\big[r\,h_1^{(2)}(kr)\big],$$
with h₁⁽²⁾ the outgoing spherical Hankel function. The total electric energy density contains a part that belongs to the outward-travelling wave (energy moving at c carrying power P: per unit radius P/c, split equally between electric and magnetic). Subtracting it (Collin & Rothschild's procedure) leaves the stored energy:
$$W_e'=\int_a^\infty\Big[\oint\frac{\varepsilon}{4}|\mathbf E|^2r^2d\Omega-\frac{P}{2c}\Big]dr .$$
Carrying out the integral in closed form gives 2ωW_e'/P = 1/(ka)³ + 1/(ka) (McLean [4]). We verified this numerically by direct quadrature of the fields above for ka from 0.05 to 1 — matching McLean to all printed digits — and found the magnetic stored energy is smaller (Q_m = 1/(ka)), so W_e dominates for the TM mode. The assumption "no energy stored inside the sphere" is what makes this a *lower* bound: any real antenna also stores energy inside r < a.

**Chu's equivalent circuit.** Chu represented the TM₁ mode's wave impedance at r = a by a ladder: series capacitance C = εa, shunt inductance L = μa, terminated in η. Computing the circuit's stored energies directly gives exactly the same Q as the field integral (our script, "circuit" column). The Hansen formula arises from Chu's approximate treatment of the tuned network and is slightly higher.

**Bandwidth.** Near resonance a single-mode antenna is modelled by a series (or parallel) RLC with Q as above; the frequency range where a matched source sees VSWR ≤ s is FBW = (s−1)/(Q√s) for Q ≫ 1 (Yaghjian & Best [5]). Bode–Fano says a lossless matching network cannot enlarge the reflection-coefficient-weighted bandwidth of an RLC load beyond π/(Q·ln(1/|Γ|)) — so a multi-element match can widen the VSWR-2 band by a factor of up to ~3–4 over the single-tuned result, but never beyond that ceiling.

### Level 3 — refinements and what they mean in practice
- **Directivity limits (Harrington 1960 [3])**: a "normal" (non-superdirective) antenna limited to modes n ≤ N ≈ ka has D_max ≈ N² + 2N; for a small antenna the practical maximum is D = 3 (4.77 dBi) with a combined electric + magnetic dipole (Huygens source). Higher directivity from a small aperture ("superdirectivity") requires exciting higher-order modes whose Q grows as roughly (ka)^−(2n+1) — impractically narrowband and lossy.
- **Wheeler (1947 [1])**: for a small capacitor-type (electric) or inductor-type (magnetic) antenna of volume V, the "radiation power factor" (≈ 1/Q) is proportional to V/(λ/2π)³ — the same scaling as (ka)³ in Chu's bound. Wheeler's *radiansphere* of radius λ/2π marks the transition between stored and radiated fields and also underlies the Wheeler-cap efficiency measurement ([antenna measurement](antenna-measurement.md)).
- **Tighter shape-specific bounds**: Thal (2006) showed that antennas whose currents lie on a spherical *surface* (wire antennas) cannot reach Chu–McLean; for TM radiators the bound is ≈ 1.5× McLean. Gustafsson et al. (2007) derived bounds for arbitrary shapes from the static polarizabilities of the enclosing volume — a thin planar antenna (the typical PCB case) has far higher minimum Q than the sphere enclosing it [7]. Treat McLean as an absolute floor; expect 1.5–3× (or more for flat antennas).
- **Magnetic materials**: a high-permeability core (ferrite rod) or a magnetic "material-loaded" antenna can reduce Q for TE-mode (magnetic dipole) antennas, but ferrite loss at RF typically cancels the gain above a few tens of MHz ([loop antennas](loop-antennas.md)).
- **Active/non-Foster matching** can in principle exceed passive bandwidth limits using negative capacitors/inductors; practical issues are stability, noise and power handling — not used in amateur rocket hardware.

## Design equations & rules of thumb

| Quantity | Formula | Example |
|---|---|---|
| Radiansphere | a = λ/2π | 110 mm @433 MHz, 52 mm @915 MHz, 30 mm @1575 MHz |
| Q floor (LP) | 1/(ka)³ + 1/ka | ka = 0.3 → 40 |
| Q floor (CP) | ½[1/(ka)³ + 2/ka] | ka = 0.3 → 22 |
| Max VSWR-2 BW | 0.707/(Q·η⁻¹) | η = 1: 1.8 % at ka = 0.3 |
| Realistic Q | 1.5–3 × McLean (wires/planar) | budget accordingly |
| Max D of a small antenna | 1.5 (single dipole), 3 (Huygens) | 1.76 / 4.77 dBi |
| Efficiency trade | FBW_realised ≈ FBW_rad/η | 7 % efficient → 14× wider |

## Worked examples

**Example 1 — Can a 433 MHz chip antenna on a 30 × 40 mm board cover the 433.05–434.79 MHz band?** The ground plane carries the antenna current, so a ≈ half-diagonal = 25 mm → ka = 2π(0.025)/0.692 = 0.227 → Q_min = 85.5 + 4.4 ≈ 90 → FBW_max = 0.707/90 = 0.79 % = **3.4 MHz** at 100 % efficiency. Realistic Q (≈ 2–3 × 90) gives 1.1–1.7 MHz at 100 % efficiency — marginal for the 1.74 MHz band, which is why 433 MHz chip antennas either need per-board tuning or run at efficiencies of 10–40 % (their datasheet bandwidths are only achieved on their specified evaluation boards; TI AN058 [8]).

**Example 2 — 915 MHz, US ISM band (902–928 MHz, 2.8 %).** a = 15 mm (a small tag): ka = 0.288, Q_min = 45.5, BW ≤ 14.2 MHz at η = 1 — the full band requires η ≤ 55 % *at the bound*, i.e. in reality ≈ 20–35 %. With a = 30 mm (a 42 × 42 mm board) ka = 0.575, Q_min = 7.0, BW ≤ 93 MHz — comfortably possible; this is why TI's 868/915 MHz PCB antennas on 40–60 mm boards reach 90 %+ efficiency [8], [10].

**Example 3 — TI's same-area comparison.** TI's CC-Antenna-DK board 6 (868 MHz) and board 14 (169 MHz) share the same board and antenna area; measured efficiencies 91 % and 7 % [8]. With a ≈ 52 mm (half-diagonal of a ≈ 45 × 95 mm board): at 868 MHz ka = 0.95 (not small; Q_min ≈ 2.2), at 169 MHz ka = 0.184 (Q_min ≈ 166 → at most 0.72 MHz bandwidth at η = 1). The measured 7 % is consistent: the 169 MHz antenna trades efficiency for a usable bandwidth.

**Example 4 — A GNSS "chip" antenna.** L1 C/A needs ±1 MHz; Galileo E1/BeiDou B1C need ≈ ±2–12 MHz. A chip antenna whose currents fill a sphere of a = 10 mm (chip plus the ground-plane edge region) has ka = 0.33, Q_min ≈ 31, BW ≤ 36 MHz at 100 % efficiency — so bandwidth is not the obstacle; linear polarization (−3 dB), pattern distortion from the ground plane and near-field detuning are (u-blox [9]; see [gnss-antennas](gnss-antennas.md)).

**Example 5 — Evaluating a claim.** A crowdfunded "1 cm antenna" claims "equal range to a whip" at 433 MHz. a = 5 mm → ka = 0.045 → Q_min ≈ 10 700 → BW ≤ 29 kHz at 100 % efficiency. A LoRa 125 kHz channel needs more than that; to get even 125 kHz the efficiency must be ≤ 23 % *at the bound*, realistically a few %. The claim fails by 10–20 dB unless the "antenna" is really coupling to a larger structure (a cable, the device body) that is the actual radiator.

## Practical notes
- **The ground plane is part of a.** For monopole-type chip/PCB antennas, the board and attached cables carry the image current; a bigger board is a bigger antenna. Chip-antenna vendors specify the test board for this reason.
- **Small antennas need re-tuning in situ**: a hand, the plastic enclosure or the fibreglass nose cone shifts a high-Q resonance by more than its bandwidth. Leave a pi-network footprint (TI AN058 [8]).
- **Losses scale badly**: with R_rad of a few ohms or less, every 0.1 Ω of matching-inductor ESR, via, or solder joint matters. Use high-Q (wire-wound or air-core) inductors and C0G capacitors.
- **Receive-only small antennas** (ferrite rods, small loops) can be very inefficient yet perfectly adequate below ~30 MHz, where external (atmospheric/man-made) noise dominates the receiver noise ([loop antennas](loop-antennas.md)).
- **High voltages**: a 2 W transmitter into a Q = 100 antenna develops large reactive voltages/currents in the matching components — check component ratings for the E22 2 W module on a small antenna.

## Common mistakes & misconceptions
- **"The chip is 3 mm, so a is 1.5 mm."** The ground plane radiates too; a is set by the board (and cables).
- **"This small antenna has great bandwidth, so it's a good design."** Check efficiency; resistive loss is the usual source of bandwidth.
- **"A matching network can make a small antenna wideband."** It can only redistribute a bounded amount of bandwidth (Bode–Fano); it adds loss.
- **"Fractal antennas are better small antennas."** Resonance compression comes from wire length packed into a volume, not fractal dimension; Q and efficiency are no better than meanders or helices of the same size (Best 2003 [6]).
- **"The Chu limit is an efficiency limit."** It is a Q (bandwidth) limit at 100 % efficiency; efficiency enters through FBW·(1/η).
- **"Chu, Hansen and McLean disagree."** They differ only in how stored energy is approximated; McLean's form is exact for the single-mode sphere and is what our numerical field integration reproduces.
- **"Small antennas have low gain because of low directivity."** Directivity stays ≈ 1.5 (1.76 dBi); low *gain* comes from low efficiency.

- **"EH / crossed-field / Poynting-vector antennas beat the size limits."** Claimed antennas that are tiny in wavelengths yet as efficient as a dipole would violate the Chu–McLean Q bound for their size combined with realistic loss; published performance claims for such antennas have generally been attributed by independent testers to radiation from the feedline (common-mode current) rather than the structure (forum/club test reports — unverified). Measure with a choked feedline and a reference dipole at the same site ([antenna measurement](antenna-measurement.md)).

## How to simulate / verify
- `python3 tools/verify/ant_small_limits.py` — numeric stored-energy Q vs McLean/Hansen/circuit; bandwidth limits for the reader's bands; loop and ferrite-rod numbers.
- To compare a real design to the bound: simulate (openEMS/NEC) or measure Z_in(f), then use the Yaghjian–Best impedance-based Q, Q(ω₀) ≈ (ω₀/2R)|Z'(ω₀)| (with Z tuned to resonance), and compute Q/Q_McLean using the true enclosing-sphere radius.
- Measure efficiency with a Wheeler cap (small antennas are ideal candidates) — [antenna measurement](antenna-measurement.md).

## Open questions / gaps
- Thal's and Gustafsson's bounds are summarised from secondary knowledge; primary papers not read in this pass.
- The "1.5–3× McLean" realistic factor is a rule of thumb; a table of measured Q/Q_min for common chip antennas would be useful (Wave-5 gap).

## Sources
1. H. A. Wheeler, "Fundamental limitations of small antennas," *Proc. IRE* 35, pp. 1479–1484, 1947; H. A. Wheeler, "The radiansphere around a small antenna," *Proc. IRE* 47, pp. 1325–1331, 1959. (peer-reviewed)
2. L. J. Chu, "Physical limitations of omni-directional antennas," *J. Appl. Phys.* 19, pp. 1163–1175, 1948. (peer-reviewed)
3. R. F. Harrington, "Effect of antenna size on gain, bandwidth, and efficiency," *J. Res. NBS* 64D, pp. 1–12, 1960. (peer-reviewed)
4. J. S. McLean, "A re-examination of the fundamental limits on the radiation Q of electrically small antennas," *IEEE Trans. Antennas Propag.* 44(5), pp. 672–676, 1996 — exact Q = 1/(ka)³ + 1/(ka); CP form. (peer-reviewed; formula verified numerically here)
5. A. D. Yaghjian and S. R. Best, "Impedance, bandwidth, and Q of antennas," *IEEE Trans. Antennas Propag.* 53(4), pp. 1298–1324, 2005. (peer-reviewed)
6. S. R. Best, "A discussion on the significance of geometry in determining the resonant behavior of fractal and other non-Euclidean wire antennas," *IEEE Antennas Propag. Mag.* 45(3), pp. 9–28, 2003. https://ieeexplore.ieee.org/document/1232160/ (peer-reviewed; abstract level)
7. H. L. Thal, "New radiation Q limits for spherical wire antennas," *IEEE Trans. Antennas Propag.* 54(10), 2006; M. Gustafsson, C. Sohl, G. Kristensson, "Physical limitations on antennas of arbitrary shape," *Proc. R. Soc. A* 463, 2007; R. E. Collin and S. Rothschild, "Evaluation of antenna Q," *IEEE Trans. Antennas Propag.* 12, 1964. (peer-reviewed; cited from secondary knowledge)
8. TI AN058 (SWRA161), *Antenna Selection Guide* — board 6 (868 MHz) 91 % vs board 14 (169 MHz) 7 % in the same area; chip-antenna datasheet caveats; pi-network recommendation. https://www.ti.com/lit/pdf/swra161 (app note)
9. u-blox UBX-15030289 — chip/fractal GNSS antennas: linear-polarization loss ≈ 3 dB; fractal element antenna gains −1.2…+2.5 dBic vs ground-plane size. (app note)
10. TI DN024 (SWRA227) — 868 MHz meander monopole, 97.7 % efficiency on 43 × 63 mm ground. (app note)
11. This repository: `tools/verify/ant_small_limits.py`. (verification)
