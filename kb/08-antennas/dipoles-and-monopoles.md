---
title: Dipoles and monopoles — current distribution, impedance, shortening, ground planes, practical variants
domain: 08-antennas
slug: dipoles-and-monopoles
tags: [dipole, monopole, half-wave, quarter-wave, whip, ground-plane, radials, folded-dipole, sleeve-dipole, j-pole, efhw, loading-coil, top-hat, common-mode, mutual-impedance, induced-emf, coil-position, bandwidth-vs-diameter]
prerequisites: [antenna-fundamentals.md, ../02-electromagnetics/radiation-from-currents-hertzian-dipole.md, ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md]
related: [antenna-matching-and-baluns.md, pcb-and-chip-antennas.md, antennas-on-rockets.md, small-antenna-limits.md, yagi-uda-and-log-periodic.md, antenna-simulation-nec-openems.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Dipoles and monopoles

## Questions this page answers
- Why is a half-wave dipole 73 Ω, and where does the +j42.5 Ω come from?
- How long should I actually cut a 433 MHz or 915 MHz dipole, and why is it shorter than λ/2?
- Does wire thickness change the resonant length and bandwidth?
- Why is a quarter-wave monopole 36.5 Ω, and why does mine measure something else?
- What happens to a λ/4 whip on a small flight-computer board with no real ground plane?
- Why do ground-plane antennas use drooping radials, and what angle gives 50 Ω?
- What is a folded dipole and why is it ~300 Ω? What if the two conductors are different diameters?
- What are sleeve dipoles, J-poles and end-fed half-waves (EFHW), and why a 49:1 transformer?
- How do loading coils and top hats shorten a monopole, and what does it cost in efficiency?
- Why does my dipole's SWR change when I move the coax?
- Does the metal (copper, aluminium, steel, copper tape, conductive filament) change the resonant length or the efficiency?
- How high is the voltage at the tips of a dipole at a given power?
- How does the feed-point impedance change if I move the feed along the antenna (OCF)?
- What happens if I bend or fold the tips of the elements?
- Can an antenna be modelled as an R, L, C circuit?
- How do collinear antennas work, and what are the coils along a vertical for?
- Is a longer whip or a full-wave antenna always better?
- How do handheld radio antennas work without a ground plane, and are aftermarket HT antennas better?
- How does a mag-mount antenna get a ground plane through the paint?
- Why do some antennas have a DC path to ground and some not?
- How do I calculate the mutual impedance between two parallel dipoles, and what does it do to their feed impedance?
- Where should the loading coil go on a short whip: base, centre or top?
- How much bandwidth does a fatter element buy?

## TL;DR
- A thin centre-fed dipole carries an approximately sinusoidal standing-wave current, zero at the tips. For l = λ/2: pattern ∝ [cos(π/2·cosθ)/sinθ]², D = 1.64 (2.15 dBi), HPBW 78°, and the idealised induced-EMF impedance is **73.1 + j42.5 Ω** (verified: `tools/verify/ant_dipole.py`).
- Real wires resonate (X = 0) a few percent **shorter** than λ/2, with R ≈ 72 Ω. Our thin-wire MoM gives the shortening factor K = L_res/(λ/2) = 0.976, 0.968, 0.958, 0.951, 0.943, 0.930 for λ/d = 50 000, 5 000, 1 000, 500, 250, 100 (`tools/verify/ant_mom_wire.py`). A 433 MHz dipole in 2 mm wire resonates at **328 mm** tip-to-tip; a 915 MHz dipole in 1.5 mm wire at **154 mm**.
- A monopole over a perfect infinite ground is half a dipole (image theory): **36.5 + j21.3 Ω**, 5.16 dBi (radiating only into the upper half-space).
- Real ground planes are finite. With four horizontal λ/4 radials, Z ≈ **23 Ω**; drooping them 30°/45°/60° gives 43/55/66 Ω (MoM, `tools/verify/ant_mom_general.py`) — so ~35–40° droop gives 50 Ω.
- A λ/4 whip on a PCB much smaller than λ/4 is really an **asymmetric dipole** whose other arm is the board and the cables: impedance, pattern and gain depend on the board and on common-mode current on attached wires.
- Folded dipole: step-up ratio (1 + ln(s/a₁)/ln(s/a₂))² (a₁ = fed-conductor radius) — 4 for equal conductors (≈288 Ω); MoM confirms 480 Ω vs 479 Ω predicted for a₂ = 3a₁.
- EFHW: the end of a λ/2 wire is a high-impedance point, ≈2–3 kΩ; MoM gives ≈2.1 kΩ at resonance for a 20 m wire with a 0.05λ counterpoise, hence the popular 49:1 (7:1 turns) transformer.
- **Mutual impedance** (induced EMF, λ/2 dipoles side by side): Z₂₁ = 67.3 + j7.5, 40.8 − j28.3, −12.5 − j29.9 and 4.0 + j17.7 Ω at d = 0.1, 0.25, 0.5 and 1λ. The closed form equals the numerical near-field integral to 10⁻¹³ Ω; NEC/MoM two-ports differ by 1–7 Ω. The driving-point impedance is Z₁ = Z₁₁ + Z₁₂ I₂/I₁ (e.g. 110 − j24 Ω in phase, 35 + j45 Ω antiphase at 0.25λ).
- **Loading-coil position** (2.4 m whip at 7.15 MHz, NEC): the best position is ≈ 0.3h with a perfect ground (Q 300: 34.5 % vs 30.9 % base-loaded). With 5 Ω of ground loss it moves to 0.4–0.5h (21.8 % vs 14.1 %, +1.9 dB), because centre loading raises R_in. Above ≈ 0.7h the coil's size and loss grow fast.
- **Diameter vs bandwidth** (433 MHz dipole, NEC): VSWR-2 bandwidth referred to R_res is 9.0/10.3/11.8/14.0/15.5/20.0 % for 0.5/1/2/4/6/12 mm. Q_Z falls from 7.8 to 3.6, roughly linearly in Ω = 2 ln(L/a).
- Short monopoles: R_rad = 40π²(h/λ)² (triangular current); a top hat makes the current more uniform and can raise R_rad by up to 4×; a loading coil of quality factor Q_L adds R_loss = X_L/Q_L. Efficiency collapses quickly below h ≈ λ/10.

## Intuition (no math)

**Opening up a transmission line.** Take an open-circuited two-wire line λ/4 long. The current is a standing wave: zero at the open end, maximum at the source. Fields of the two wires cancel far away because their currents are opposite and close together. Now bend the two wires apart by 90° each, until they are collinear: the currents now flow in the *same* direction in space, the fields add, and the structure radiates. That is a dipole, and it explains why the current is (roughly) sinusoidal and zero at the tips.

**Why λ/2 is special.** At λ/2 total length the input sits at a current maximum and voltage minimum, the stored electric and magnetic energies nearly balance, and the input impedance is mostly resistive and near 50–75 Ω. Shorter than this, the dipole looks capacitive (like a small capacitor with a resistor in series); longer, inductive.

**Why real dipoles are shorter than λ/2.** Two effects: (1) the ends have capacitance (charge piles up at the tips and in the "fringing" field), which makes the wire look electrically longer; (2) a finite-radius wire has lower inductance per unit length than an infinitely thin one, so the wave on it is effectively slowed a little near the ends. Thicker wire → more shortening, and also lower Q → wider bandwidth.

**The monopole and its mirror.** A conducting plane acts like a mirror for currents: a vertical wire above a ground plane behaves as if there were an identical upside-down wire below. So a λ/4 monopole over a big ground behaves like a λ/2 dipole, except that only the top half of space exists. Half the voltage for the same current → half the impedance (36.5 Ω); all the power into half the sphere → double the directivity (5.16 dBi).

**No ground plane? Something else becomes the other half.** A monopole needs a return path for its current. If you don't give it a proper ground (radials, a big metal plate, the car roof), the current returns over whatever is there: the PCB ground, the battery, the outside of the coax shield. Those become radiating parts of the antenna. This is the root cause of "my SWR changes when I touch the cable" and of the poor, unpredictable performance of whips on small boards.

## The math

### Level 1 — the numbers you use

Symbols: l = total dipole length, h = monopole height, a = wire radius, d = 2a, λ = c/f, k = 2π/λ, η₀ = 376.73 Ω.

| Antenna | Pattern (normalized field) | D₀ | R_in at feed | Notes |
|---|---|---|---|---|
| Hertzian (uniform current, l ≪ λ) | sinθ | 1.5 (1.76 dBi) | 80π²(l/λ)² | top-loaded ideal |
| Short dipole (triangular current) | sinθ | 1.5 | 20π²(l/λ)² | real short wire |
| λ/2 dipole | cos(π/2 cosθ)/sinθ | 1.641 (2.15 dBi) | 73.1 (+j42.5 at exactly λ/2) | K·λ/2 for X = 0 |
| Full-wave dipole | [cos(π cosθ)+1]/sinθ | 2.41 (3.82 dBi) | very high (current node at feed) | needs matching |
| 1.25λ ("extended double Zepp") | — | 3.28 (5.16 dBi) | 212 − j (R_I_max 106) | max broadside D of a single wire |
| λ/4 monopole, infinite ground | as λ/2 dipole, upper half | 3.28 (5.16 dBi) | 36.5 + j21.3 | half of dipole |
| Short monopole (triangular) | sinθ upper half | 3.0 (4.77 dBi) | 40π²(h/λ)² | + ground loss! |

(Pattern integration and Si/Ci values: `tools/verify/ant_dipole.py`.)

Practical cutting lengths (free space, resonant, bare wire), from our MoM:
| Frequency | Wire Ø | λ/2 (ideal) | Resonant dipole (tip to tip) | Resonant λ/4 monopole (over big ground) |
|---|---|---|---|---|
| 433 MHz | 2 mm | 346.2 mm | 327.9 mm (K = 0.947) | ≈164 mm |
| 433 MHz | 6 mm tube | 346.2 mm | 322.7 mm (K = 0.932) | ≈161 mm |
| 915 MHz | 1.5 mm | 163.8 mm | 154.2 mm (K = 0.941) | ≈77 mm |
Insulated wire resonates shorter again (the insulation's permittivity slows the wave; typically a further 2–5 %, depending on insulation thickness and εr — measure).

### Level 2 — derivations

**(a) Current distribution.** For a thin wire, the current is well approximated by I(z) = I₀ sin[k(l/2 − |z|)]. This is exact in the limit a → 0 (it is the lowest-order solution of Hallén's integral equation) and is the basis of the induced-EMF method (Carter 1932; Balanis ch. 4 and 8 [1]; Orfanidis ch. 17 and 24 [3]). Its far-field radiation intensity was given on [antenna-fundamentals](antenna-fundamentals.md#level-2--derivations):
$$U(\theta)=\frac{\eta_0 I_0^2}{8\pi^2}\left[\frac{\cos(\tfrac{kl}{2}\cos\theta)-\cos\tfrac{kl}{2}}{\sin\theta}\right]^2 .$$

**(b) Radiation resistance by integrating the Poynting flux.** P_rad = ∮U dΩ. With the substitution u = cosθ and partial fractions, the angular integral becomes a combination of sine and cosine integrals Si(x) = ∫₀ˣ sin t/t dt, Ci(x) = −∫ₓ^∞ cos t/t dt. Referred to the current maximum I₀:
$$R_m=\frac{\eta_0}{2\pi}\Big\{C+\ln(kl)-\mathrm{Ci}(kl)+\tfrac12\sin(kl)[\mathrm{Si}(2kl)-2\,\mathrm{Si}(kl)]+\tfrac12\cos(kl)\big[C+\ln\tfrac{kl}{2}+\mathrm{Ci}(2kl)-2\,\mathrm{Ci}(kl)\big]\Big\},$$
C = 0.5772 (Euler). At the feed, where the current is I₀ sin(kl/2), R_in = R_m / sin²(kl/2). For kl = π: R_m = R_in = **73.08 Ω**. Our script evaluates this closed form and, independently, the numerical flux integral; they agree to 0.001 Ω for l = 0.1…1.5λ.

**(c) Reactance by the induced-EMF method.** Power flow alone cannot give the reactance, which lives in the near field. The induced-EMF method computes the field E_z(z) that the assumed current produces *on the wire surface* (radius a) and integrates the work done against it:
$$Z_\text{in}=-\frac{1}{I_\text{in}^2}\int_{-l/2}^{l/2}E_z(a,z)\,I(z)\,dz .$$
For the sinusoidal current, the near field of each half is a closed-form sum of three spherical waves (from the centre and the two tips), and the integral again reduces to Si/Ci functions. The reactance referred to the current maximum is
$$X_m=\frac{\eta_0}{4\pi}\Big\{2\,\mathrm{Si}(kl)+\cos(kl)[2\,\mathrm{Si}(kl)-\mathrm{Si}(2kl)]-\sin(kl)\big[2\,\mathrm{Ci}(kl)-\mathrm{Ci}(2kl)-\mathrm{Ci}\!\big(\tfrac{2ka^2}{l}\big)\big]\Big\}$$
(Balanis eq. 8-60b form [1]). For kl = π, sin(kl) = 0, so the radius term drops out and X = (η₀/4π)·Si(π)·... = **42.5 Ω** (our script: 42.52 Ω). The fact that the λ/2 result does not depend on a is an artefact of the assumed current; in reality the current departs from a pure sinusoid for finite a, which is why real dipoles resonate short.

**(d) What a full-wave solver says.** Solving the integral equation numerically (our MoM: Galerkin, triangle basis, reduced kernel) for a = 10⁻⁴λ gives Z = 80.1 + j44.6 Ω at exactly l = λ/2 and resonance (X = 0) at l = 0.4838λ with R = 72.0 Ω. So: "73 + j42.5" is the textbook idealisation at exactly λ/2; "≈ 72 Ω resistive at ≈ 0.47–0.49λ" is what you build. NEC-based modellers report the same ≈72 Ω resonant free-space value.

**(e) Monopole by images.** A PEC plane at z = 0 enforces E_tangential = 0. The field of a vertical current I(z) above the plane plus its mirror image I(−z) (same direction for vertical currents) satisfies that condition, so above the plane the monopole field equals the dipole field. The monopole feed sees half the dipole voltage for the same current: Z_mono = Z_dipole/2 = 36.5 + j21.3 Ω. The power radiates into 2π sr instead of 4π, so D_mono = 2 D_dipole = 3.28 (5.16 dBi). Our general MoM, which implements images by mirroring the geometry, reproduces this.

**(f) Folded dipole (mode decomposition).** Two parallel conductors (fed conductor radius a₁, other a₂, spacing s ≪ λ) joined at both ends. Split the feed excitation into (i) a *transmission-line mode*: two shorted λ/4 stubs in series, which at resonance present an open circuit and carry no net current at the feed, and (ii) an *antenna mode*: both conductors at the same potential, radiating as one fat dipole with total current I. In the antenna mode the charge — hence current — divides so that both conductors are equipotential. For two line charges q₁, q₂ at spacing s,
$$\frac{q_1}{2\pi\varepsilon}\ln\frac{1}{a_1}+\frac{q_2}{2\pi\varepsilon}\ln\frac1s=\frac{q_1}{2\pi\varepsilon}\ln\frac1s+\frac{q_2}{2\pi\varepsilon}\ln\frac{1}{a_2}\;\Rightarrow\;\frac{I_1}{I_2}=\frac{\ln(s/a_2)}{\ln(s/a_1)} .$$
The feed current is I₁ = I·ln(s/a₂)/[ln(s/a₁)+ln(s/a₂)]; equating radiated power I²R_d/2 = I₁²R_in/2 gives
$$R_\text{in}=R_d\Big(1+\frac{\ln(s/a_1)}{\ln(s/a_2)}\Big)^2 .$$
Equal conductors → 4R_d ≈ 290 Ω. Making the unfed conductor fatter raises the ratio; our MoM (s = 0.02λ at 433 MHz): equal 288 Ω; a₂ = 3a₁ → 480 Ω (formula 479 Ω); a₁ = 3a₂ → 198 Ω (formula 192 Ω). The folded dipole also resonates shorter than a plain dipole of the same wire (0.457λ vs 0.476λ here) and has a somewhat wider bandwidth. The same formula with unequal conductors is used to set Yagi driven-element impedance.

**(g) Short antennas: capacitance, loading and efficiency.** For l ≪ λ the dipole input reactance is capacitive; a transmission-line estimate gives
$$X_\text{in}\approx -120\Big[\ln\frac{l}{2a}-1\Big]\cot\frac{kl}{2}\quad(\Omega)$$
(Schelkunoff's average-characteristic-impedance picture; Balanis §4.3 [1]). To resonate it, add a series inductance of reactance +|X_in|. With a coil of unloaded quality factor Q_L, R_coil = X_L/Q_L. Efficiency e = R_rad/(R_rad + R_coil + R_wire + R_ground). Because R_rad ∝ (h/λ)² while X_in grows as h shrinks, efficiency falls roughly as h³ once the coil loss dominates — the electrically-small-antenna trade-off discussed on [small-antenna limits](small-antenna-limits.md).

**Top loading.** Adding capacitance at the top (a disc, a "hat" of wires, or a horizontal wire as in an inverted-L) lets the current stay large right up to the top, making the distribution closer to uniform. For a short monopole the effective height approaches h (instead of h/2) and R_rad approaches 160π²(h/λ)² — up to 4× the triangular-current value — while less loading inductance (and so less coil loss) is needed. Top loading is almost always more efficient than base loading.

### Level 3 — thickness, bandwidth and the limits of the thin-wire picture

- **Thickness parameter.** Classical theory (Hallén, King–Middleton [4]) characterises a dipole of half-length h by Ω = 2 ln(2h/a). Larger Ω = thinner. As Ω decreases (fatter), resonance moves shorter, resonant R stays ≈ 65–75 Ω for moderate thickness, and the reactance slope — hence Q — falls, widening the VSWR bandwidth. Our MoM table above spans Ω ≈ 14 to 24.
- **Bandwidth.** A 433 MHz dipole in 2 mm wire (λ/d ≈ 350) has Q ≈ 6 (Yaghjian–Best $Q_Z$ = 5.9 from our MoM) and a VSWR-2 bandwidth of **11.8 % referred to 72 Ω, 8.2 % referred to 50 Ω**; Q ≈ 9 needs a much thinner wire (λ/d ≈ 3500) (`tools/verify/ant2_qa.py` §f; corrected 2026-10-02 from an earlier "Q ≈ 8–10, 8–10 %" statement). A fat cage or biconical dipole reaches octaves ([wideband antennas](multiband-and-wideband-antennas.md)). Thicker elements are also more tolerant of detuning by nearby dielectric (the nose cone).
- **Beyond thin wires.** For l/a < ~30, or for strips and PCB traces, the current is no longer purely axial/uniform around the circumference. A flat strip of width w behaves roughly like a round wire of radius ≈ w/4 (equivalent radius of a thin strip, a widely used conformal-mapping result). PCB traces on dielectric additionally see an effective permittivity — use a full-wave solver ([antenna-simulation-nec-openems](antenna-simulation-nec-openems.md)).
- **Longer dipoles.** Beyond l ≈ 1.25λ the broadside lobe splits into multiple lobes; 1.25λ maximises broadside directivity (5.16 dBi) for a single centre-fed wire.


### Level 3 — mutual impedance of parallel dipoles (induced EMF)
**Derivation.** Assume both dipoles carry the sinusoidal current $I(z)=I_m\sin k(h-|z|)$ (half-length h). The closed-form near field of dipole 1 at radial distance ρ is a sum of three spherical waves, one from each tip and one from the centre (Schelkunoff):
$$E_{z1}(\rho,z)=-j\frac{\eta I_m}{4\pi}\Big[\frac{e^{-jkR_1}}{R_1}+\frac{e^{-jkR_2}}{R_2}-2\cos kh\,\frac{e^{-jkr}}{r}\Big],$$
with $R_{1,2}=\sqrt{\rho^2+(z\mp h)^2}$ and $r=\sqrt{\rho^2+z^2}$. The voltage induced at dipole 2's terminals (open circuit, referred to its current maximum) follows from reciprocity, as the work done by this field on dipole 2's current. Dividing by $I_m$ gives the mutual impedance
$$Z_{21}=-\frac{1}{I_m^2}\int_{-h}^{h}E_{z1}(d,z)\,I_2(z)\,dz .$$
For λ/2 dipoles (cos kh = 0) side by side at spacing d, the integral reduces to sine and cosine integrals:
$$R_{21}=\frac{\eta}{4\pi}\big[2\mathrm{Ci}(u_0)-\mathrm{Ci}(u_1)-\mathrm{Ci}(u_2)\big],\quad X_{21}=-\frac{\eta}{4\pi}\big[2\mathrm{Si}(u_0)-\mathrm{Si}(u_1)-\mathrm{Si}(u_2)\big],$$
where $u_0=kd$ and $u_{1,2}=k(\sqrt{d^2+l^2}\pm l)$ with $l$ = λ/2 (Balanis §8.6 [1]). Putting ρ = a (the wire's own surface) in the same integral gives the **self** impedance 73.08 + j42.48 Ω, which is the textbook 73 + j42.5 — so the self and mutual formulas are one calculation. For two currents the terminal relations are $V_1=Z_{11}I_1+Z_{12}I_2$ and $V_2=Z_{21}I_1+Z_{22}I_2$ with $Z_{12}=Z_{21}$ (reciprocity). The **driving-point impedance** of element 1 in an array is therefore $Z_1=Z_{11}+Z_{12}I_2/I_1$; this is the basis of Yagi, phased-array and stacking analysis ([Yagi](yagi-uda-and-log-periodic.md#level-2--mutual-impedance-induced-emf-and-mom), [12 coupling](../12-phased-arrays/planar-arrays-element-pattern-coupling.md)).

**Numbers** (`tools/verify/s12_mutual_hallen.py` §3–4, all PASS):

| Geometry (λ/2 dipoles) | Induced EMF Z₂₁ (Ω) | NEC-2 two-port Z₂₁ (a = 10⁻⁴λ) |
|---|---|---|
| side by side, d = 0.10λ | 67.3 + j7.5 | 74.8 + j3.4 |
| side by side, d = 0.25λ | 40.8 − j28.3 | 41.9 − j34.4 |
| side by side, d = 0.50λ | −12.5 − j29.9 | −16.5 − j31.4 |
| side by side, d = 1.00λ | 4.0 + j17.7 | 6.1 + j19.0 |
| collinear, centre spacing 0.55λ | 20.3 + j2.5 | 23.2 + j1.8 |
| collinear, 0.75λ | 2.0 − j8.0 | 1.8 − j8.9 |
| echelon, d = 0.25λ, offset 0.25λ | 30.9 − j18.4 | 31.8 − j23.2 |

The closed form and the numeric integral agree to 10⁻¹³ Ω. The KB Galerkin MoM agrees with NEC within 0.6 Ω. The induced-EMF values are 1–7 Ω off at close spacing because the real current is not exactly sinusoidal; for design, use a MoM two-port.

**A coupled pair** (0.48λ resonant dipoles, a = 10⁻³λ, d = 0.25λ): Z₁₁ = 72.7 + j10.5 Ω and Z₁₂ = 37.8 − j34.2 Ω. Fed in phase, each element sees 110.5 − j23.6 Ω. In antiphase it sees 34.9 + j44.7 Ω, and in quadrature (I₂ = −jI₁) 38.5 − j27.2 Ω. A direct two-source NEC run reproduces the in-phase value to 0.01 Ω. So an array's element impedances depend on how it is driven: match for the excitation you will use, or measure the active reflection coefficient ([antenna measurement](antenna-measurement.md)).

**Element diameter vs bandwidth** (NEC, 433 MHz resonant dipoles; `tools/verify/s12_practicalities.py` §B):

| Diameter | λ/d | Ω = 2 ln(L/a) | Resonant length (K) | R_res | Q_Z | VSWR ≤ 2 BW re R_res | re 50 Ω |
|---|---|---|---|---|---|---|---|
| 0.5 mm | 1385 | 14.4 | 332.1 mm (0.959) | 71.9 Ω | 7.75 | 9.0 % | 6.2 % |
| 1 mm | 692 | 13.0 | 329.8 mm (0.953) | 71.8 Ω | 6.85 | 10.3 % | 7.0 % |
| 2 mm | 346 | 11.6 | 326.7 mm (0.944) | 71.8 Ω | 5.95 | 11.8 % | 8.3 % |
| 4 mm | 173 | 10.2 | 322.4 mm (0.931) | 72.0 Ω | 5.04 | 14.0 % | 9.7 % |
| 6 mm | 115 | 9.3 | 319.3 mm (0.922) | 71.9 Ω | 4.52 | 15.5 % | 11.0 % |
| 12 mm | 58 | 7.9 | 313.9 mm (0.907) | 72.8 Ω | 3.59 | 20.0 % | 13.5 % |

Q falls roughly linearly with Ω (fit Q ≈ 0.64Ω − 1.5), so bandwidth grows only logarithmically with diameter. Going from 2 mm to 12 mm wire buys ≈ 1.7× bandwidth, not 6×. For octave bandwidths you need a cage, bicone or sleeve structure ([wideband](multiband-and-wideband-antennas.md)). NEC's resonant lengths here are 0.2–1 % shorter than the own-MoM table above; NEC-2 and our MoM use different gap and end models.

## Practical variants

### Finite ground planes and small boards
- **Large disc ground (radius ≥ ~λ):** impedance near 36 Ω, but the pattern maximum tilts upward (typically tens of degrees) instead of lying on the horizon, because diffraction from the ground edge redistributes radiation; the horizon gain drops by a few dB. Only an infinite (or very large, lossy-earth-backed) ground keeps the maximum on the horizon.
- **Radials (ground-plane antenna).** Four horizontal λ/4 radials give Z ≈ 23 Ω in free space (MoM 22.8 Ω). Drooping them downward reduces their field cancellation and moves the structure toward a dipole: 30° → 43 Ω, 45° → 55 Ω, 60° → 66 Ω (MoM). The vertical element for resonance shortens as droop increases (0.247λ → 0.216λ in our model). The free-space pattern of a radial ground plane is dipole-like with its maximum at the horizon (1.5–2 dBi peak), not 5 dBi.
- **Whip on a small PCB (the flight computer case).** If the board's largest dimension is < λ/4 (< 173 mm at 433 MHz — nearly always true for a flight computer), the board cannot act as an image plane. The whip and the board form an asymmetric dipole; R is typically 10–30 Ω, gain lower than a dipole, and current flows onto every cable leaving the board (battery leads, USB, pyro wires, the coax to a remote antenna). TI's AN058 recommends a pi-network at the feed for exactly this reason and notes datasheet numbers are only valid on the reference board [5]. For 433 MHz on a rocket, the most predictable choices are a **λ/2 sleeve or centre-fed dipole with a choke/balun** (no ground needed) or a **λ/4 whip with 2–4 λ/4 radials/counterpoise** folded along the airframe.
- **The coax as counterpoise.** A monopole connected directly to coax with no ground uses the outer surface of the shield as its other half. The antenna then includes an ill-defined length of cable; touching or moving the cable changes the impedance. Fix with a choke (ferrite, sleeve) at λ/4 below the feed — see [antenna matching and baluns](antenna-matching-and-baluns.md).


### Loading-coil position and efficiency
**Physics.** Moving the coil up from the base has two effects. The current below the coil stays nearly uniform, which raises the radiation resistance (toward the uniform-current 160π²(h/λ)²). But the shorter whip section above the coil is more capacitive, so the coil needs more inductance and dissipates more (R = ωL/Q). The optimum depends on coil Q and on the other losses in series with the feed (ground, matching): a higher R_in makes fixed series losses less important, which pushes the coil up.

**NEC** (`tools/verify/s12_practicalities.py` §A, perfect ground, coil solved for X_in = 0 at each position) — 2.4 m (8 ft), 8 mm whip at 7.15 MHz (h = 0.057λ), coil at fractional height p:

| p | L (µH) | Q 300: R_in / η | Q 100: R_in / η | Q 300 + 5 Ω ground: η | Q 100 + 5 Ω ground: η |
|---|---|---|---|---|---|
| 0 (base) | 19.4 | 4.2 Ω / 30.9 % | 10.0 Ω / 13.0 % | 14.1 % | 8.6 % |
| 0.2 | 24.5 | 5.9 / 34.1 % | 13.7 / 14.7 % | 18.4 % | 10.8 % |
| 0.3 | 27.8 | 6.9 / **34.5 %** | 15.9 / **15.0 %** | 20.0 % | 11.4 % |
| 0.4 | 32.0 | 8.1 / 34.2 % | 18.7 / 14.8 % | 21.1 % | **11.7 %** |
| 0.5 | 37.7 | 9.6 / 33.1 % | 22.4 / 14.2 % | **21.8 %** | 11.6 % |
| 0.6 | 46.1 | 11.7 / 30.9 % | 27.8 / 13.0 % | 21.6 % | 11.0 % |
| 0.8 | 86.0 | 20.9 / 21.7 % | 53.8 / 8.4 % | 17.5 % | 7.7 % |

Over a lossless ground the gain from centre loading is small (+0.5 dB at Q 300, +0.6 dB at Q 100). With a realistic 5 Ω ground (a mobile installation) it is +1.9 dB, and the optimum moves to 0.4–0.5h — the classic "centre-loaded mobile whip". Coil Q matters more than position: Q 100 → 300 is worth +3.6 dB here.

**433 MHz, 60 mm whip, Q = 50 chip-inductor-class coil:**

| Coil position p | L | R_in | η |
|---|---|---|---|
| 0 (base) | 137 nH | 10.5 Ω | 29 % |
| 0.4 | 213 nH | 19.5 Ω | 32 % |
| 0.8 | 541 nH | 49 Ω | 21 % |

Base loading with Q = 100 gives 137 nH, 6.8 Ω and 45 %, which confirms the hand estimate of example 4 below (136 nH, ≈ 7 Ω, 43 %). On a flight board, raising the coil is worth less than a better coil or a top hat. Mid-whip coils are also mechanically fragile.

### Sleeve (coaxial) dipole
The coax runs up inside a λ/4 metal tube (the "sleeve") connected to the shield at the top; the centre conductor continues as a λ/4 radiator. The sleeve forms the lower dipole arm *and* a λ/4 choke (shorted stub) whose open bottom end presents a high impedance to shield currents. It is the classic mast-mounted vertical dipole and a good fit for a rocket body tube or nose cone (the coax enters along the axis). Bandwidth is limited by the choke action (a few %).

### J-pole
A λ/2 end-fed radiator driven from a λ/4 shorted parallel-wire stub: the stub transforms from a short at its base to a very high impedance at its top, matching the high end-impedance of the λ/2 element; the coax taps onto the stub a short distance above the short where the stub impedance is ≈ 50 Ω. Simple and cheap (e.g., from 300 Ω twin-lead), but notorious for common-mode current on the feedline because the feed is unbalanced onto a balanced stub — a choke below the tap is recommended (Cebik [6]).

### End-fed half-wave (EFHW)
The end of a λ/2 wire is a current node / voltage maximum; the feed impedance is a few kΩ, set by the wire thickness and whatever counterpoise the feed "pushes against". Our MoM (20 m band, 1.6 mm wire, 0.05λ counterpoise) finds X = 0 at L ≈ 0.468λ with R ≈ 2.1 kΩ (peak R ≈ 2.8 kΩ slightly longer). A 49:1 impedance transformer (7:1 turns ratio on a ferrite core, 50 Ω → 2450 Ω) therefore matches it to VSWR ≈ 1.2 at resonance, and the same wire is also close to resonant on harmonics (λ, 3λ/2…), giving multiband operation. The feedline shield carries some current by design (the counterpoise), so a choke placed some distance down the coax sets how much. EFHW transformer core heating is a real power limit (see [baluns and RF transformers](../06-rf-circuits/baluns-and-rf-transformers.md)).

### Loaded short monopoles (stubby, rubber duck, helical whips)
Normal-mode helices (the coil *is* the radiator, diameter ≪ λ) and base/centre-loaded whips resonate at a fraction of λ/4. Their bandwidth is narrow and they are easily detuned by the hand or by a dielectric body; their efficiency depends on coil Q and — critically — on the ground they work against. On a handheld ground-station receiver a full λ/4 or λ/2 antenna is typically several dB better than the stubby it replaces (the physics of example 5 on [antenna-fundamentals](antenna-fundamentals.md#worked-examples)).

### Collinear arrays and phasing coils
A collinear stacks several λ/2 radiators end to end and keeps their currents *in phase*. Simply making a wire longer does not do this: on a straight wire the current reverses every half wavelength, so the extra sections radiate in antiphase and split the pattern into lobes. A **phasing element** between sections — a λ/4 shorted stub, a coil (≈ λ/4 of wire wound up), or a coaxial section with crossed inner/outer conductors (the "coaxial collinear") — absorbs the reversed half-cycle so that every radiating section has current in the same direction. The visible coils along a VHF vertical (D2 #73) are these phasing sections.
Result: an omni with gain from *elevation* squeeze. Uniform line source of length L ≥ λ: D ≈ 2L/λ, elevation HPBW ≈ 50.8λ/L degrees (2 λ → 6 dBi/25°, 4 λ → 9 dBi/13°; `tools/verify/ant2_ident.py`). A collinear is a (stacked) dipole and does **not** need a ground plane, but a "base-fed" 5/8-over-5/8 collinear does rely on the mast/coax as the lower half — choke the coax. Mount it at least ≈ 1 λ above or clear of the mast top and roof; the flat beam is aimed at the horizon, so nodes close below a hilltop collinear can fall outside the beam (gateway example on [antenna identification](antenna-identification-guide.md#worked-examples)).

### Longer is not better: whips beyond λ/4 and full-wave dipoles
For a centre-fed wire, broadside directivity grows only up to 1.25 λ (5.16 dBi); beyond that the lobe splits. A full-wave (λ) centre-fed dipole has 3.82 dBi but a feed impedance of several kΩ (current node at the centre) and needs matching. For a vertical whip over a good ground, λ/4 (5.16 dBi over infinite ground) → 5/8 λ (+≈ 3 dB at low angles over a large ground) is the sensible limit; **a 3/4 λ or longer whip points its lobe up** and loses at the horizon. On a handheld or small board, "longer" mainly changes the impedance and moves current onto the radio body; gain changes by a few dB at most, positive or negative.

### Handheld (HT) antennas and the radio as counterpoise
A handheld's antenna is a monopole fed against the radio's metal chassis, PCB and the user's hand — together ≈ 0.05–0.1 λ at 2 m, a small and lossy counterpoise; the system behaves like an asymmetric dipole whose "lower arm" includes the user. A stock stubby is a loaded short monopole: estimate at 146 MHz (`ant2_qa.py` §g, good-ground figures) — 15 cm stubby: R_rad ≈ 2.1 Ω, capacitive X ≈ 490 Ω tuned out by a coil of Q 50–100 (4.9–9.7 Ω loss) → **17–29 % efficiency (−7.6 to −5.3 dB)**, against ≈ 99 % for a 49 cm λ/4 whip. That is why a full-length λ/4 or a "λ/2" (end-fed, e.g. the NA-701-class aftermarket antennas claim) usually beats the stock stubby by several dB on transmit and receive; adding a **λ/4 counterpoise wire ("tiger tail")** hanging from the antenna connector ground gives a better-defined ground and typically a few dB more (forum practice — anecdotal; physics as above). Compare antennas fairly with the same radio, position and a fixed-distance signal source ([antenna measurement](antenna-measurement.md)).

### Vehicle, mag-mount and no-ground-plane (NGP) antennas
A car roof is a good ground plane at VHF/UHF (≥ λ/4 in every direction for f ≳ 150 MHz). A **mag-mount** couples to the roof through the paint as a capacitor: base 90 mm, 0.5 mm paint + rubber (εr ≈ 3) → **C ≈ 340 pF**, X_C ≈ 3.2 Ω at 146 MHz and 1.1 Ω at 446 MHz (negligible) but 17 Ω at 27 MHz (noticeable — CB mag-mounts are larger) (`ant2_qa.py` §h). Bull-bar or edge mounting gives a lopsided ground and a tilted, asymmetric pattern. **"No ground plane" (NGP) mobile antennas** are end-fed half-waves (or 5/8 λ with a matching section) — they present a high impedance and need little ground current, matched by a small LC/transformer in the base ([EFHW](#end-fed-half-wave-efhw)).

### Conductor material, length and loss
Resonant length depends on **diameter, insulation and surroundings, not on the metal**: at RF the current flows in a skin depth of micrometres for every good conductor, so copper, aluminium and steel rods of the same diameter resonate at the same length (D1 #334, #653). The metal matters for *loss*. Half-wave dipole, sinusoidal current, loss referred to the feed $R_\text{loss}=R'L/2$ with $R'=R_s/(2\pi a)$, $R_s=\sqrt{\pi f\mu/\sigma}$ (`ant2_qa.py` §a, 2 mm wire, R_rad = 72 Ω):
| Conductor | 433 MHz efficiency | 7.1 MHz efficiency |
|---|---|---|
| Copper / copper-clad steel | 99.8 % | 98.5 % |
| Aluminium | 99.75 % | 98.1 % |
| Brass | 99.6 % | 97.1 % |
| Stainless 304 | 98.8 % | 91.0 % |
| Mild steel (μr ≈ 100 assumed) | 95.5 % | 73 % |
| "High-conductivity" printing filament (ρ ≈ 6 × 10⁻⁵ Ω m, vendor-class value) | 89.6 % | 27 % |
| Conductive PLA (ρ ≈ 0.15 Ω m) | 0.9 % | 0.02 % |
Practical consequences: any metal is fine at UHF; avoid ferrous wire (fence wire, clotheslines) at HF; **copper tape on 3D-printed parts works** (35 µm copper is many skin depths at > 100 MHz; watch the adhesive joints — overlap and solder them), whereas carbon-loaded "conductive" filament is not an antenna conductor (D2 #5). Thin insulation lowers the resonance by a few percent (dielectric loading).

### Tip voltage and safe power
A resonant dipole is a standing wave: current maximum at the centre, voltage maximum at the tips. A transmission-line estimate gives $V_\text{tip}\approx I_0Z_a$ with $I_0=\sqrt{2P/R}$ and $Z_a=120[\ln(L/2a)-1]$ Ω (`ant2_qa.py` §b): **≈ 116 V peak at 2 W on a 433 MHz dipole** (26 V at 0.1 W); **≈ 1.5 kV at 100 W** and **≈ 5.8 kV at 1.5 kW** on a 14 MHz wire dipole (D1 #564). An EFHW feed point sits at $\sqrt{2PR}$ ≈ 707 V at 100 W into 2.5 kΩ. These are ±30 % estimates (the tip potential depends on the reference), but they set insulator, corona (sharp ends glow at kV) and touch-safety requirements — keep tips out of reach and use end insulators rated for several kV at HF.

### Feed position along the antenna (OCF) and how the impedance varies
For a λ/2 wire carrying $I(z)=I_0\cos kz$, moving the feed a distance z from the centre raises the resistance as $R(z)\approx R_c/\cos^2(kz)$ (fixed radiated power, smaller feed current): ≈ 97 Ω at the 1/3 point, rising toward kΩ at the ends (the EFHW limit) — NEC agrees within 3 % ([OCF on the HF page](wire-antennas-hf-random-wire-fan-dipole.md#level-2--why-the-impedance-swings-and-the-derivations)). Reactance is set by length; position mostly sets R. This is the general answer to "how does an antenna transform impedance along its length" (D1 #566, #611): it is a resonator, and the feed taps it at a chosen current/voltage ratio.

### Bent and folded tips
Bending the outer part of each arm keeps most of its effect on resonance (the charge at the tip still loads the end), but less than if it were straight. Own MoM, 433 MHz, 2 mm wire, total wire length kept at 328 mm (`ant2_qa.py` §e): outer 30 mm bent 45° → **+0.6 %**, bent 90° → **+2.9 %**, outer 60 mm bent 90° → **+4.6 %**, outer 30 mm folded back 10 mm from the arm → **+8.0 %** (the folded part's current opposes the arm's). So bend tips to fit a radome only after trimming in place; folded-back ends need a longer wire. Small bends (≤ 45°) are nearly free.

### The antenna as an R, L, C circuit
Near its first resonance a dipole behaves like a series RLC. From the MoM reactance slope of the 433 MHz, 2 mm-wire dipole (`ant2_qa.py` §f): **R = 72 Ω, L_s ≈ 150 nH, C_s ≈ 0.90 pF** (Q ≈ 6); the model is good within ± 5 % of f₀ but misses R's rise with frequency (MoM at 0.9 f₀: 51 − j82 Ω vs RLC 72 − j86 Ω). Far below resonance the short dipole is a capacitor $C\approx\pi\varepsilon_0 l/(2[\ln(l/2a)-1])$ (≈ 0.4 pF for a 10 cm dipole of 1 mm wire) in series with a small R_rad (small-kl limit of the X_in formula above, using 120 ≈ 1/(πε₀c)). A lumped equivalent is useful for matching-network design and SPICE, never for radiation patterns (D1 #654).

### DC-grounded antennas, static and "why use a ground plane"
A ground plane (or radials, or a car roof) is the *other half* of a monopole: it carries the return current and supplies the image that makes a λ/4 rod behave like a λ/2 dipole. Without it, the coax or the device becomes the other half. Separately, some antennas are **DC grounded** — folded dipoles, J-poles, shunt-fed/gamma-matched elements, hairpin-matched Yagis and most commercial base antennas present a DC short across the feed — which bleeds static charge from wind/precipitation and reduces lightning-induced voltages; others (plain dipoles, whips with series matching) are DC-open and can charge to kV (D1 #170, #595). RF ground (the counterpoise), safety ground (fault/lightning path) and DC ground are different functions; see [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md).

## Design equations & rules of thumb

| Quantity | Equation / value | Valid | Typical |
|---|---|---|---|
| Resonant dipole length | L = K·λ/2, K from thickness table | thin wire, free space | K = 0.94–0.97 at UHF |
| Classic HF rule | L(m) ≈ 142.6/f(MHz) ("468/f ft") | wire, K ≈ 0.951 | agrees with our MoM at λ/d ≈ 500; not universal |
| λ/2 dipole R | 73 Ω ideal; ≈72 Ω at resonance | thin | VSWR 1.44 to 50 Ω |
| Monopole on infinite ground | Z/2, D×2 | PEC image | 36.5 Ω, 5.16 dBi |
| Ground plane, horizontal radials | ≈ 22–25 Ω | 3–4 radials λ/4 | 22.8 Ω (MoM) |
| Ground plane, 45° droop | ≈ 50–55 Ω | 4 radials λ/4 | 55 Ω (MoM) |
| Folded dipole | (1 + ln(s/a₁)/ln(s/a₂))²·R_d | s ≪ λ, resonance | 288 Ω equal wires |
| Short monopole R_rad | 40π²(h/λ)² (triangular) … 160π²(h/λ)² (uniform) | h ≲ λ/8 | 50 mm @433 MHz: 2.1 Ω |
| Short dipole X_in | ≈ −120[ln(l/2a) − 1]cot(kl/2) | l ≲ 0.3λ | hundreds of Ω capacitive |
| Coil loss | R = X_L/Q_L | — | Q_L 50–200 for air coils |
| EFHW feed Z | ≈ 2–3 kΩ | thin wire, short counterpoise | 49:1 transformer |
| Trim sensitivity | ΔL/L ≈ Δf/f | resonant | 1 mm on a 164 mm whip ≈ 0.6 % ≈ 2.6 MHz at 433 MHz; 1 mm on a 78 mm whip ≈ **1.25 % ≈ 11 MHz** at 915 MHz (NEC: 77/78/79 mm → 900.3/889.0/878.0 MHz, [openEMS workflow Run 3](../16-simulation-tools/openems-workflow.md)) — trim 915 MHz whips in ≤ 0.5 mm steps near the end |

## Worked examples

**Example 1 — A 433 MHz ground-station dipole.** 2 mm copper wire, free space. MoM: resonant tip-to-tip length 327.9 mm (0.4737λ), R ≈ 72 Ω. Allow a 5 mm feed gap: each arm ≈ 161.5 mm. Fed with 50 Ω coax through a 1:1 current balun (ferrite choke) — VSWR 72/50 = 1.44, mismatch loss 0.14 dB (acceptable; or use a quarter-wave 60 Ω transformer — see [quarter-wave transformers](../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md)). Cut 3–5 mm long and trim while watching S11 on a NanoVNA, with the balun in place and the dipole ≥ λ/2 (35 cm) from metal.

**Example 2 — A 915 MHz ground-plane antenna for the pad.** Want 50 Ω without a matching network. Use 4 radials of λ/4 = 81.9 mm drooped 40° (between the MoM's 43 Ω at 30° and 55 Ω at 45°). From the MoM trend, the vertical is ≈ 0.228λ ≈ 75 mm for a = 2×10⁻³λ (1.3 mm wire at 915 MHz). Build it 5 % long (79 mm), trim for minimum S11. Peak gain ≈ 2 dBi at the horizon; the pattern has a null straight up — fine for a rocket on the pad, bad for one directly overhead (see [antennas-on-rockets](antennas-on-rockets.md)).

**Example 3 — Folded dipole driven element for a 915 MHz Yagi.** Two 3 mm rods, 15 mm apart (s = 0.046λ). Alone it is ≈ 290 Ω; inside a Yagi the parasitic elements pull it down (for a long DL6WU Yagi a plain dipole driven element was ≈ 50 Ω in our MoM — see [yagi](yagi-uda-and-log-periodic.md#worked-examples)), so a folded dipole there lands near 200 Ω and a 4:1 half-wave coax balun (a λ_coax/2 loop of coax, 4:1 unbalanced-to-balanced) matches it to 50 Ω. Making the fed rod thinner than the unfed rod raises the step-up ratio if you need more.

**Example 4 — A 60 mm loaded whip at 433 MHz.** h = 60 mm, h/λ = 0.0867. R_rad (triangular) = 40π²(0.0867)² = **2.97 Ω** (over a good ground). The unloaded monopole reactance is half a 120 mm dipole's: with a = 0.5 mm, l/2a = 120, X_dipole ≈ −120[ln 120 − 1]cot(π·0.1733) = −120 × 3.79 × 1.63 ≈ −740 Ω → monopole ≈ **−370 Ω**. A base-loading coil needs X_L = 370 Ω (L = 136 nH). With Q_L = 100, R_coil = 3.7 Ω, so e ≈ 2.97/(2.97 + 3.7 + ~0.3 Ω conductor) ≈ **43 % (−3.7 dB)** — and the input R ≈ 7 Ω still needs a match to 50 Ω. A top hat that doubles the effective height would lift R_rad to ~6–9 Ω and cut the needed inductance, improving efficiency to ~65–75 %.

**Example 5 — Checking the EFHW 49:1 claim.** 20 m band (14.2 MHz), 1.6 mm wire, 1 m (0.05λ) counterpoise. MoM: at L = 0.465λ, Z = 1798 + j85 Ω; at 0.470λ, 2196 − j91 Ω. At resonance (≈0.468λ) R ≈ 2.1 kΩ. Through a 49:1 transformer, 2100/49 = 43 Ω → VSWR 1.17. The number depends on the counterpoise and wire diameter; values from 1.8 to 3.5 kΩ are common in practice (forum reports — anecdotal), so the transformer ratio is a compromise, and many builders add a small (100–150 pF) capacitor across the primary to trim the high band (forum practice, unverified).

## Practical notes
- **Measure with the feed arrangement that will fly.** A monopole's impedance measured on a big bench ground plane differs from that on the rocket's avionics bay. A dipole measured without a choke measures the dipole *plus* the coax.
- **Elements near dielectric shift down in frequency**: a whip taped to a fibreglass body tube or inside a nose cone resonates lower than in free space — plan to trim in situ ([antennas-on-rockets](antennas-on-rockets.md)). openEMS predictions for a 3 mm G10 ogive over a 100 mm bulkhead (`tools/verify/sim2_openems_nosecone.py`; simulated, not yet measured): **−1.2 %** for a 78 mm 915 MHz whip (≈ 1 mm of trim) and **−2.8 %** for a 165 mm 433 MHz whip. The counterpoise matters more: a conductive av-bay below the bulkhead moved the whip **+3.4 %**. A reactive (non-resonant) printed IFA in a fibreglass tube moved **up** +0.7 %, the opposite of the pre-registered prediction, so the "always down" rule holds for resonant wires, not for every antenna.
- **Mechanical**: at 433 MHz a λ/4 whip is 164 mm. Spring-steel or nitinol whips survive landing; solid copper work-hardens and snaps at the solder joint. Strain relief at the feed is the main failure point.
- **Connector**: SMA/U.FL mating cycles (U.FL typically rated for only ~30 cycles) — do not use U.FL as a field-serviceable antenna connector.
- **Polarization**: a vertical whip is vertically polarized; a ground-station Yagi must match — or use CP on the ground (see [polarization](antenna-polarization-and-circular-polarization.md)).

## Common mistakes & misconceptions
- **"A dipole is exactly λ/2."** It resonates 2–7 % shorter depending on thickness (table above); cutting to 346 mm at 433 MHz gives a dipole resonant near 410 MHz.
- **"73 Ω is the resonant impedance."** 73 + j42.5 Ω is the idealised value at *exactly* λ/2. At resonance R ≈ 70–72 Ω.
- **"A quarter-wave whip needs no ground because it's resonant."** The resonance of a λ/4 monopole *assumes* the image; without a ground the current goes somewhere else — usually the coax.
- **"Drooping radials increase gain."** They mainly raise the feed impedance toward 50 Ω and change the pattern slightly; the effect on free-space peak gain is a few tenths of a dB (1.55 → 1.87 dBi, 0° → 45°, MoM).
- **"The folded dipole has more gain than a dipole."** Same pattern, same gain (≈2.15 dBi); only the impedance (and bandwidth) differ.
- **"A 5/8-wave vertical always beats a 1/4-wave."** Over a large ground it has a lower-angle, higher-gain lobe (~+3 dB at the horizon over good ground); in free space on a rocket or with a poor ground, the advantage largely disappears and a matching network is required.
- **"The whip on my FC board is 5 dBi."** On a small board 0–2 dBi and a lumpy pattern are typical.
- **"Insulated wire resonates at the same length as bare wire."** Insulation shortens the resonant length by a few percent.
- **"Aluminium and copper elements need different lengths."** The metal enters only through its surface impedance, whose internal inductance is ~10⁻⁴ of the wire's geometric inductance: for a 2 mm, 433 MHz dipole the resonant length shifts by 0.017 % (Cu) vs 0.021 % (Al) — a 16 µm difference on 328 mm — and the loss resistance is 0.14 Ω vs 0.18 Ω (efficiency 99.80 % vs 99.75 %, 0.002 dB apart); even non-magnetic stainless costs only 0.35 mm and 0.06 dB (`tools/verify/fix_element_metal.py`). What *does* change the length is **diameter** (K = 0.968 → 0.930 from λ/d = 5000 to 100, table above), insulation, and the mounting (boom/clamp). Plated or magnetic steel (μr > 1) is lossier and worth avoiding in high-current regions. (Myth flagged by W4-D1, ham.stackexchange.com/q/9451, /q/1388.)
- **"A longer quarter-wave whip is better."** Longer than resonance means inductive reactance and mismatch, not gain: over a perfect ground (thin-wire MoM, 2 mm wire, 433.92 MHz) a monopole 5 / 10 / 20 % too long presents 43 + j21 / 51 + j42 / 73 + j87 Ω — VSWR 1.6 / 2.2 / 4.0, mismatch loss 0.2 / 0.7 / 1.9 dB — while its free-space pattern barely changes. Extra gain at low elevation only appears near 5/8 λ, over a large ground and with a matching network (see the 5/8-wave entry above); on a small FC board or rocket the extra length mostly drives common-mode current onto the coax.
- **"EFHW means no counterpoise."** Some current always flows on the feed side; the counterpoise (or the coax shield) is part of the antenna.

- **"Aluminium elements must be cut longer than copper."** Material does not change resonant length; diameter, insulation and nearby objects do (§ conductor material).
- **"A longer whip (or a full-wave dipole) always has more gain."** Lobes split beyond 1.25 λ; a λ wire is a kΩ feed; extra length on a small radio mostly moves current onto the chassis.
- **"The coils on a tall vertical are loading coils."** On collinears they are phasing sections that keep λ/2 segments in phase.
- **"A mag-mount isn't grounded."** It is — capacitively (≈ 170–650 pF), which is a short circuit at VHF/UHF.
- **"Base loading is as good as any."** With a lossy ground, centre loading is ≈ 2 dB better on an HF mobile whip (NEC table above). Over a perfect ground the difference is only ≈ 0.5 dB, and the coil Q matters more.
- **"Twice the element diameter, twice the bandwidth."** Q falls only with ln(diameter): 2 → 12 mm buys 1.7× (11.8 → 20 % VSWR-2 bandwidth at 433 MHz).
- **"Mutual impedance is a small correction."** At 0.1–0.25λ, Z₁₂ is half to most of Z₁₁. A pair of dipoles fed in phase vs antiphase sees 110 Ω vs 35 + j45 Ω.
- **"Bending the tips doesn't matter."** Up to 45° almost not (+0.6 %); 90° bends +3–5 %; folding back +8 % (MoM).

## How to simulate / verify
- `python3 tools/verify/ant_dipole.py` — induced-EMF and pattern numbers.
- `python3 tools/verify/ant_mom_wire.py` — resonant length vs thickness; Z at exactly λ/2; practical lengths.
- `python3 tools/verify/ant2_qa.py` — conductor-material loss table, tip voltages, wrong-band mismatch, dipole near metal, bent tips, RLC equivalent and bandwidth, HT stubby estimate, mag-mount capacitance (output `tools/verify/ant2_qa_output.txt`).
- `python3 tools/verify/s12_mutual_hallen.py` — induced-EMF mutual impedance (closed form vs numeric near-field integral vs NEC/MoM two-ports), collinear/echelon, coupled-pair driving-point Z; also the Hallén derivation checks used on [antenna simulation](antenna-simulation-nec-openems.md).
- `python3 tools/verify/s12_practicalities.py` §A–B — loading-coil position sweeps (HF mobile whip, 433 MHz whip) and the diameter vs bandwidth table.
- `python3 tools/verify/ant_mom_general.py` — monopole via images, ground-plane antennas vs radial droop, folded dipole step-up ratios, loops, helices. Edit `ground_plane_antenna()` / `folded_dipole()` to try your own geometry.
- NEC-2 (4nec2, xnec2c) reproduces all of the above; guidelines for segmentation are on [antenna-simulation-nec-openems](antenna-simulation-nec-openems.md). For whips on PCBs with dielectric and a finite board, use openEMS.
- Measure: NanoVNA S11 at the feed with a choke; sweep ±10 % around the design frequency; trim. For pattern/gain, see [antenna measurement](antenna-measurement.md).

## Open questions / gaps
- Quantitative numbers for λ/4 whips on the actual Avionics-B/C board outlines (size, battery and cable routing) require an openEMS model; not done here.
- The strip-to-round equivalent radius (≈ w/4) is quoted from common practice; a primary source (e.g., Balanis ch. 8 table of equivalent radii) should be cited by page when available.
- EFHW impedance spread (1.8–3.5 kΩ) is forum-reported; a systematic NEC study versus counterpoise length would firm it up.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016 — ch. 4 (linear wire antennas: short dipole, λ/2 dipole, R_rad and D, image theory, monopole), ch. 8 (integral equations, induced-EMF self/mutual impedance, Si/Ci formulas), ch. 9 (folded dipole, ground-plane antennas). (textbook)
2. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — ch. 6 (cylindrical antennas), ch. 7 (loops/short antennas), folded dipole. (textbook)
3. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, 2016 (free) — ch. 17 "Linear and Loop Antennas" (standing-wave and half-wave dipoles), ch. 24 "Currents on Linear Antennas" (Hallén/Pocklington integral equations, King's three-term approximation, MoM with pulse/triangular/NEC bases). [chapter numbers checked against the 2016 edition's table of contents, W5-S18 2026-10-13; the 2010 edition numbers ch. 11–18 one lower, with Aperture Antennas as ch. 18 and Currents on Linear Antennas as ch. 21]. https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook)
4. R. W. P. King, *The Theory of Linear Antennas*, Harvard Univ. Press, 1956 — Ω thickness parameter, King–Middleton impedance; P. S. Carter, "Circuit relations in radiating systems and applications to antenna problems," *Proc. IRE* 20(6), 1932 — induced-EMF method. (textbook / peer-reviewed; cited through Balanis/Orfanidis)
5. TI AN058 (SWRA161), *Antenna Selection Guide*; TI DN023 (SWRA228) and DN024 (SWRA227) — ground plane is part of monopole-type PCB antennas; pi-network recommended; whip/wire antennas at 433 MHz. https://www.ti.com/lit/pdf/swra161 (app notes)
6. L. B. Cebik (W4RNL) articles (antenna2.github.io/cebik) — J-pole and ground-plane feed behaviour, NEC practice. (expert articles; secondary)
7. ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — dipole length vs diameter chart, EFHW, ground-plane radial droop practice. (handbook)
8. Altus Metrum owner's manual — λ/4 (≈7 in) wire at 435 MHz toward the nose; carbon/metal bays need an external antenna. https://altusmetrum.org/AltOS/doc/altusmetrum.html (manufacturer manual)
9. This repository: `tools/verify/s12_mutual_hallen.py`, `tools/verify/s12_practicalities.py` (W5-S12); `tools/verify/ant_dipole.py`, `ant_mom_wire.py`, `ant_mom_general.py` (own thin-wire MoM; validated against induced-EMF and energy conservation); `tools/verify/ant2_qa.py`, `ant2_ident.py` (W5-E2 additions). (verification)
10. A. D. Yaghjian and S. R. Best, "Impedance, bandwidth, and Q of antennas," *IEEE TAP* 53(4), 2005 — Q_Z = ω|Z′|/2R used in § bandwidth. (peer-reviewed; cited)
