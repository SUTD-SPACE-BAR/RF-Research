---
title: Slot antennas — Babinet's principle, slots in ground planes, cavity-backed and microstrip-fed slots, slotted-waveguide arrays, PCB slots at 2.4/5.8 GHz
domain: 08-antennas
slug: slot-antennas
tags: [slot, babinet, booker, complementary-antenna, magnetic-dipole, cavity-backed-slot, microstrip-fed-slot, aperture-coupling, slotted-waveguide, stevenson, annular-slot, pcb-slot, shielding-slot, self-complementary]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, ../02-electromagnetics/maxwells-equations.md, ../02-electromagnetics/waveguides-and-cavity-resonators.md]
related: [patch-antennas.md, horn-reflector-aperture-antennas.md, multiband-and-wideband-antennas.md, antennas-on-rockets.md, pcb-and-chip-antennas.md, antenna-simulation-nec-openems.md, ../12-phased-arrays/array-factor-linear-arrays.md, ../13-pcb-rf-layout-emc/grounding-and-return-paths.md, ../16-simulation-tools/openems-workflow.md]
level: mixed
confidence: high
last_updated: 2026-09-29
---

# Slot antennas

## Questions this page answers
- What is a slot antenna and how can a hole in metal radiate?
- What is Babinet's principle, and why is a slot's impedance η²/(4·Z_dipole)?
- Why is a resonant half-wave slot about 500 Ω instead of 73 Ω, and how do I feed it with 50 Ω?
- Is a slot horizontally or vertically polarized?
- How does Wi-Fi work in a full-metal laptop (or through a metal rocket airframe)?
- How long should a 2.45 GHz slot in the copper of an FR-4 board be?
- How does a microstrip-fed slot work, and what is aperture coupling in a patch antenna?
- What does cavity-backing a slot do to its impedance and pattern?
- Why are the slots in a slotted-waveguide array offset alternately either side of the centreline?
- How do I design a slotted-waveguide omni for 10 GHz, and how critical are the dimensions?
- Why can a seam or cooling slot in my shielded enclosure leak RF?
- Can I make a 915 MHz antenna on my flight-computer board without a copper keep-out area?
- Is a slot antenna wideband?
- Can I simulate a slot antenna in NEC?

## TL;DR
- A **slot** in a conducting sheet is the *dual* of a strip dipole of the same shape: same pattern, but **E and H swapped** — the E field lies *across* the slot, so a vertical slot is horizontally polarized (Booker 1946 [1]).
- **Babinet–Booker relation** (thin, perfectly conducting, infinite plane screen, same medium both sides): $Z_\text{slot}\,Z_\text{dipole}=\eta_0^2/4 = 35\,481\ \Omega^2$. The ideal λ/2 dipole 73 + j42.5 Ω maps to a λ/2 slot of **363 − j211 Ω**; at resonance ~72–75 Ω maps to **≈ 475–490 Ω** (Booker: "about 485 Ω"). Verified: MoM strip + Babinet 474 Ω; **openEMS FDTD of the slot itself 488 Ω at 2.443 GHz** vs 2.45 GHz predicted (`tools/verify/ant2_slot.py`, `ant2_slot_openems.py`).
- Reactance sign is inverted: a slot is **inductive below resonance and capacitive above** (a dipole is the opposite).
- **Feeding**: R falls towards the slot ends as $R(x)\approx R_c\cos^2(kx)$ (x from the centre), so 50 Ω sits near the ends (≈ 0.20λ from the centre of a free-space slot). openEMS: feed at L/4 gives 326 Ω vs 307 Ω predicted (+6 %). Microstrip-fed slots use this offset plus an open stub (≈ λg/4 past the slot) to cancel reactance.
- **Cavity backing** (radiate one side only) roughly **doubles** the impedance and adds ≈ 3 dB directivity; used for flush-mounted antennas on aircraft and rockets.
- **PCB slot, 1.6 mm FR-4 (openEMS)**: resonates at **≈ 0.70 × λ₀/2** — a **2.45 GHz slot is ≈ 42.7 mm long** (not 61 mm), radiation efficiency ≈ 93 %, D ≈ 4.5–5 dBi on a 90 × 60 mm board; centre-fed R is 420–710 Ω depending on board size (so do not trust any single number — simulate your board).
- **Edge-notch (open-ended) slot at 915 MHz** on an 80 × 100 mm FR-4 board: **51.5 mm × 2 mm, feed 9 mm from the closed end → VSWR ≤ 2 from 872–986 MHz** (openEMS) — an antenna that needs no copper keep-out.
- **Slotted-waveguide omni**: longitudinal broad-wall slots spaced λg/2, **alternately offset** about the centreline so the TE₁₀ field reversal every λg/2 is cancelled and all slots radiate in phase; Stevenson's conductance $g = 2.09\,(\lambda_g/\lambda_0)(a/b)\cos^2(\pi\lambda_0/2\lambda_g)\sin^2(\pi x/a)$, Σg = 1 for a match. WR-90, 10.368 GHz, 16 slots: spacing 18.69 mm, offset 2.16 mm (Stevenson) / 2.39 mm (Elliott), ≈ 10 dBi, 9.8° elevation beam — reproduced from W1GHZ [3].
- An unintended **seam or vent about λ/2 long is an efficient antenna** — the same physics makes slots the main leakage path of shielded boxes.

## Intuition (no math)
Take a sheet of metal and drive current across it. If you cut a long thin slot, the current has to flow *around* the slot ends; charge piles up on the two long edges, and a strong electric field appears *across* the gap. That oscillating field across the gap is exactly what a "magnetic current" along the slot would produce. A strip dipole carries electric current *along* its length with the magnetic field circling it; the slot carries (equivalent) magnetic current along its length with the electric field circling it. Everything that is E for the dipole is H for the slot and vice versa — hence the same donut-shaped pattern but with the polarization rotated by 90°.

Why is a slot high-impedance where a dipole is low? At the centre of a resonant dipole the current is maximum and the voltage small — a low-impedance point (≈ 73 Ω). At the centre of a resonant slot the *voltage across the slot* is maximum (the slot ends are short circuits — solid metal) and the current delivered is small — a high-impedance point (≈ 490 Ω). Moving the feed toward a slot end is like moving a dipole's feed toward its tip, but reversed: the slot voltage falls, so the impedance falls, and somewhere near the end you find 50 Ω.

A slot "radiates both ways": in an infinite sheet it sends identical waves out of both faces. Put a metal box (cavity) behind it and the back half is suppressed: all the power goes forward (≈ +3 dB directivity), and because only half the "radiating room" is available for the same slot voltage, the resistance roughly doubles.

A waveguide with slots is a transmission line with shunt radiators tapped along it. The field inside reverses every half guide-wavelength. If every slot sat on the same side of the centreline, neighbours would radiate in antiphase and cancel broadside; flipping each successive slot to the other side of the centreline flips its excitation too, so the two 180° flips add to 360° and every slot radiates in phase.

## The math

### Level 1 — Babinet's principle for antennas (the result)
Symbols: η₀ = 376.73 Ω (free-space wave impedance); Z_d = input impedance of a flat strip dipole (Ω); Z_s = input impedance of the *complementary* slot — a hole of the same shape and size cut in an infinite, perfectly conducting, zero-thickness sheet, fed across its centre (Ω).
$$Z_s\,Z_d=\frac{\eta_0^2}{4}\approx 35\,481\ \Omega^2,\qquad Z_s=\frac{\eta_0^2}{4Z_d}.$$
Consequences:
| Complementary dipole | Z_d (Ω) | Slot Z_s (Ω) |
|---|---|---|
| ideal λ/2 (sinusoidal current, induced EMF) | 73.1 + j42.5 | 362.7 − j211.0 |
| resonant, w = λ/200 (MoM) | 72.1 | 492 |
| resonant, w = λ/100 (MoM) | 72.6 | 489 |
| resonant, w = λ/50 (MoM) | 74.9 | 474 (openEMS direct: 488) |
| short (capacitive, −jX) | R − jX | inductive |

A strip of width w behaves like a round wire of radius ≈ w/4 (equivalent radius of a thin strip; see [dipoles](dipoles-and-monopoles.md#level-3--thickness-bandwidth-and-the-limits-of-the-thin-wire-picture)), so the slot resonates at the length where the complementary strip dipole does: 0.47λ for w = λ/100, 0.465λ for λ/50 (MoM; the Elliott–Kurtz value for a square-ended thin-wall slot is 0.464λ₀ [3]).

Pattern: the slot's far field is the complementary dipole's with $\mathbf E\leftrightarrow\eta_0\mathbf H$; for a slot along z in the plane x = 0, $E_\phi\propto \cos(\tfrac{\pi}{2}\cos\theta)/\sin\theta$ (λ/2) on each side of the sheet — i.e., $E$ is perpendicular to the slot axis. Directivity 2.15 dBi when radiating both ways; ≈ 5.2 dBi if one side is suppressed by an ideal cavity/infinite reflector.

### Level 2 — derivation (Booker's duality argument)
Assumptions: the screen is planar (z = 0), perfectly conducting, infinitely thin and (for the slot) infinite in extent; the same homogeneous medium (η) fills both half spaces; time-harmonic fields ($e^{j\omega t}$).

1. **Duality.** Source-free Maxwell's equations are unchanged by $\mathbf E'=\eta\mathbf H$, $\mathbf H'=-\mathbf E/\eta$ (check: $\nabla\times\mathbf E'=\eta\nabla\times\mathbf H=j\omega\varepsilon\eta\mathbf E=-j\omega\mu\mathbf H'$ using $\eta^2=\mu/\varepsilon$). So any field of the strip problem, dualised, is a valid field.
2. **Boundary conditions of the strip problem in the plane z = 0.** On the metal strip S, $\mathbf E_\text{tan}=0$. The strip's surface current radiates a field whose tangential H is *odd* in z (it flips sign from top to bottom), so on the rest of the plane S_c (no current there) continuity forces $\mathbf H_\text{tan}=0$.
3. **Dual field = slot problem.** In z > 0 take the dual field. On S_c: $\mathbf E'_\text{tan}=\eta\mathbf H_\text{tan}=0$ — so S_c can be solid metal. On S: $\mathbf H'_\text{tan}=-\mathbf E_\text{tan}/\eta=0$ — which is what a slot driven symmetrically must satisfy in its aperture (its aperture E is even in z, its tangential H odd, hence zero). The z < 0 field is the mirror image. So the dualised strip field *is* the field of the complementary slot.
4. **Terminal quantities.** The dipole gap (the small cut in the strip where V_d is applied) becomes, in the complement, a small metal *bridge* across the slot that carries the slot's feed current.
   - Slot voltage: $V_s=\int_\text{across slot}\mathbf E'\cdot d\mathbf l=\eta\int_\text{across strip, top face}\mathbf H\cdot d\mathbf l=\eta\,I_d/2$, because Ampère's loop around the strip ($=I_d$) splits into equal top and bottom halves.
   - Slot current: the bridge current flows on both of its faces, $I_s=2\int_\text{along bridge, top}\mathbf H'\cdot d\mathbf l=\tfrac{2}{\eta}\int_\text{across gap}\mathbf E\cdot d\mathbf l=2V_d/\eta$.
   - Therefore $Z_s=V_s/I_s=(\eta I_d/2)/(2V_d/\eta)=\eta^2/(4Z_d)$. ∎ (Signs drop out of the impedance ratio.)
5. **Self-complementary structures.** If a structure is its own complement (e.g. an infinite 90° bow-tie, a self-complementary spiral), $Z_s=Z_d=Z$ ⇒ $Z=\eta_0/2=188.4\ \Omega$, independent of frequency (Mushiake) — the foundation of [frequency-independent antennas](multiband-and-wideband-antennas.md).

**Offset feed.** Model the slot as a short-circuited slot-line resonator: slot voltage $V(x)=V_0\cos(kx)$ (x from the centre, zero at the ends of a resonant slot). The radiated power is fixed by $V_0$, so the resistance seen by a feed at x is $R(x)=|V(x)|^2/2P=R_c\cos^2(kx)$, with k = π/L_res. For $R_c=490\ \Omega$: 50 Ω at $\cos^2(kx)=0.102$, x = 0.198λ from the centre (0.04λ from the end of a 0.48λ slot) [`ant2_slot.py`]. This is the slot mirror-image of the off-centre-fed dipole, where $R(x)=R_c/\cos^2(kx)$ rises toward the tips.

**One-sided slot.** If a cavity or reflector suppresses one half space and presents an open circuit to the slot, the same aperture field radiates only half the power: $R_\text{one-sided}\approx 2R_\text{two-sided}$ (≈ 950–1000 Ω resonant) and D rises ≈ 3 dB. A real cavity adds its own susceptance, so the resonance shifts; the cavity depth is typically λ/4 (behaves as an open circuit at the slot) or much less with dielectric loading [2].

### Level 3 — where Babinet stops being exact
- **Finite screens.** Babinet needs an infinite sheet. On a finite PCB or airframe, currents flow round the board edges and the board itself radiates; in openEMS the same 57 mm slot on FR-4 changed from 714 Ω (infinite board) to 423 Ω (90 × 60 mm board) while its resonance moved only 1 % (`ant2_slot_openems.py`). Resonant *length* transfers well; *impedance* does not.
- **Dielectric on one side.** The principle holds for a homogeneous medium only. With a substrate under the copper, the slot wave travels in a mixed air/dielectric field: openEMS gives an effective slowing factor 1.315 (εeff ≈ 1.73) for a 2.45 mm slot on 1.6 mm FR-4 (εr 4.4) — between 1 and the thick-substrate limit $\sqrt{(\varepsilon_r+1)/2}=1.64$. The slot then is electrically short in air (0.354λ₀), so its radiation resistance *rises* (488 → 714 Ω, infinite board). (The pre-registered guess "dielectric lowers R" was wrong — recorded in the log.)
- **Wide slots and thick walls.** Width barely affects resonance for w ≲ λ/50; a real wall thickness t lengthens the resonant slot (Elliott–Kurtz: 0.464λ₀ thin wall, square end → 0.483λ₀ in WR-90 with real wall and rounded ends [3]); rounded ends need ≈ 2 % more length than square ends [3].
- **Slots in waveguide walls.** The slot is a shunt admittance on the guide (longitudinal broad-wall slot) or a series impedance (transverse/centred-inclined slots). Stevenson (1948) derived the resonant conductance from the guide's Green's function [3]; Elliott's design equations include mutual coupling, which is ≈ 1 % in length for a linear array but large for planar arrays of parallel slots [3].
- **Magnetic current picture.** By the equivalence principle the aperture field $\mathbf E_a$ in a PEC plane can be replaced by a magnetic surface current $\mathbf M_s = 2\,\mathbf E_a\times\hat{\mathbf n}$ radiating in free space (factor 2 from the image in the PEC plane). This is the route used for patch antennas' "radiating slots" ([patch-antennas](patch-antennas.md#level-2--the-two-models)) and for horn apertures ([aperture antennas](horn-reflector-aperture-antennas.md)).

## Practical slot-antenna family

### Slot in a ground plane / enclosure (Wi-Fi in metal laptops, metal airframes)
A metal chassis can be made to radiate by making the *opening* the antenna: a slot or gap roughly λ/2 long (61 mm in air at 2.45 GHz, less when a plastic or glass window fills it), or a λ/4 open-ended slot (one end open to an edge), excited by a small feed across it. The whole chassis then carries the currents, which is why metal phones and laptops use cut lines, plastic-filled seams or hinge gaps as radiators and why their performance depends on the whole chassis. (Principle from Babinet/Booker [1], [2]; product details are proprietary — not verified here.)

On a **metal rocket airframe**, the same idea gives two useful duals:
- an **axial slot** (along the tube) — like a horizontal ("circumferential") dipole: E is circumferential, so a vertical rocket radiates *horizontally* polarized, with near-omni azimuth coverage when the tube circumference is small (ka ≲ 1; e.g. 100 mm tube at 433 MHz, ka = 0.45);
- a **circumferential gap/slot** (around the tube) — the two halves of the airframe become the arms of a fat dipole (vertical polarization, nulls toward nose and tail).
Either needs a dielectric cover and a structural review; see [antennas-on-rockets](antennas-on-rockets.md#antenna-options-on-the-vehicle). Numbers for a specific airframe need an openEMS model (not done here).

### Cavity-backed and annular slots
A slot backed by a shallow box radiates into one half-space only: flush, rugged, ≈ 5 dBi. An **annular (ring) slot** in a ground plane is the dual of a small loop of magnetic current and radiates like a short vertical monopole — vertical polarization, conical pattern with a zenith null — the classic flush-mounted aircraft blade replacement. Bandwidth of cavity-backed slots is typically a few percent unless the cavity is deep or the slot is widened/tapered [2].

### Microstrip-fed slot and aperture coupling
A microstrip line on the other side of the board crosses the slot at right angles. The line's current, flowing in the ground plane under the strip, is interrupted by the slot and excites it — a transformer coupling whose ratio is set by where the line crosses the slot (offset from the centre reduces coupling, as in $R(x)=R_c\cos^2 kx$). The line continues past the slot and ends open-circuited about λg/4 beyond it, so that the slot sees a current maximum (virtual short) at the crossing; trimming that stub cancels the residual reactance (Yoshimura 1972 [4]). Widening the slot, a forked feed, or a wide rectangular slot gives much larger bandwidth (tens of %).

**Aperture-coupled patch** (Pozar 1985 [5]): a *small, non-resonant* slot in the ground plane between a feed line and a patch. Here the slot is deliberately below resonance so that it mainly couples (it would otherwise radiate backwards); see [patch feed methods](patch-antennas.md#feed-methods). The back-radiation of the slot and its resonance must stay well away from the patch band — a common cause of front-to-back problems.

### PCB slot antennas at 2.4 and 5.8 GHz
openEMS results for a 2.45 mm-wide slot in the copper of 1.6 mm FR-4 (εr 4.4, tan δ 0.02), centre lumped feed (`tools/verify/ant2_slot_openems.py`):
| Case | Slot | Board | f_res (X = 0) | L/(λ₀/2) | R_c | D | e_rad |
|---|---|---|---|---|---|---|---|
| A | 57.0 mm, no substrate | infinite PEC | 2.443 GHz | 0.929 | 488 Ω | — | — |
| B | 57.0 mm | infinite FR-4 | 1.858 GHz | 0.707 | 714 Ω | — | — |
| C | 57.0 mm | 90 × 60 mm | 1.838 GHz | 0.699 | 423 Ω | 4.47 dBi | 94.6 % |
| D | 43.5 mm | 90 × 60 mm | 2.403 GHz | 0.697 | 613 Ω | 5.17 dBi | 93.3 % |
| E | 43.5 mm, feed at L/4 | 90 × 60 mm | 2.423 GHz | 0.703 | 326 Ω | — | — |

Rules from these runs: **L_res ≈ 0.70 λ₀/2 on 1.6 mm FR-4** at 2.4 GHz (so ≈ 42.7 mm for 2.45 GHz); the slot is efficient (> 90 %) because most of its stored energy is in air, unlike a patch on FR-4 (≈ 45 %, [patch](patch-antennas.md#worked-examples)); it radiates from both faces (bidirectional, D ≈ 4–5 dBi on a small board). At **5.8 GHz** the same 1.6 mm board is electrically 2.4× thicker, so εeff rises toward the 1.64² = 2.7 limit and the length factor falls below 0.70 — estimate 0.66–0.70 × λ₀/2 ≈ 17–18 mm (not simulated; verify in openEMS).

**Bandwidth.** From the case-D impedance curve (Y = 1/Z at ±5 % of resonance) the parallel-resonance quality factor is $Q=\frac{\omega_0}{2G}\frac{dB}{d\omega}\approx 6.7$, so a slot *matched* at resonance has a VSWR ≤ 2 bandwidth of $(S-1)/(Q\sqrt S)=1/(6.7\sqrt2)\approx$ **10–11 %** — roughly twice a thin dipole's and five times a 1.6 mm FR-4 patch's (2.2 %). Wider slots and a stub-tuned microstrip feed widen it further.

### Open-ended ("notch") slot on a board edge — a 915 MHz option
Cutting the slot in from the board edge leaves one end open: the open end is a voltage maximum, the closed end a short, so the slot resonates at roughly a *quarter* wavelength (the slot analogue of a λ/4 monopole, and the planar cousin of the IFA). Feeding across the slot a few mm from the closed end gives a low impedance directly. openEMS, 2 mm-wide notch in an 80 × 100 mm, 1.6 mm FR-4 board (copper on one side), 50 Ω lumped feed (`ant2_slot_openems.py F<L>,<feed>`):
| Notch length | Feed from closed end | Best match | Z there | VSWR-2 band | D |
|---|---|---|---|---|---|
| 57 mm | 4 mm | 0.804 GHz, −5.3 dB | 17 + j19 Ω | none | 2.2 dBi |
| 50 mm | 8 mm | 0.933 GHz, −10.6 dB | 39 + j25 Ω | 0.903–0.972 GHz | 2.2 dBi |
| 50 mm | 12 mm | 1.000 GHz, −15.5 dB | 53 + j17 Ω | 0.913–1.256 GHz | 2.3 dBi |
| 53 mm | 9 mm | 0.893 GHz, −14.6 dB | 45 + j17 Ω | 0.849–0.957 GHz | 2.2 dBi |
| **51.5 mm** | **9 mm** | **0.917 GHz, −13.2 dB** | **44 + j20 Ω** | **0.872–0.986 GHz (12 %)** | **2.2 dBi** |

So a **915 MHz notch slot on 1.6 mm FR-4 is ≈ 51.5 mm long (0.63 × λ₀/4)**, fed ≈ 9 mm from its closed end; moving the feed toward the open end raises R and shifts the match up in frequency, exactly as the cos² voltage picture predicts. Radiation efficiency came out at 98–103 % (the ±3 % is NF2FF/port numerical noise; quote "> 95 %"). The residual +j20 Ω can be tuned out with a series capacitor (X = 20.5 Ω → ≈ 8.5 pF at 915 MHz). As with any small-board antenna the *board* radiates too (D 2.2 dBi = dipole-like), so cables leaving the board edge near the notch will detune it — see [pcb-and-chip-antennas](pcb-and-chip-antennas.md).

### Slot versus IFA/monopole on a small board
| | Slot / notch in the ground copper | IFA / meander / whip |
|---|---|---|
| Copper under the antenna | *required* (the slot is cut in it) | must be removed (keep-out) |
| Efficiency on FR-4 | high (> 90 %): fields mostly in air | high for IFA, lower for meander/chip |
| Bandwidth (1.6 mm FR-4) | 10–12 % (VSWR 2) | IFA ≈ 5–10 % |
| Polarization | E across the slot | E along the element |
| Sensitivity to nearby parts | slot ends and edges must stay clear; a trace crossing the slot kills it | element tip and keep-out area must stay clear |
| Mechanical | no protrusion; good for flush/metal enclosures | protrudes or needs board edge |

### Slotted cylinders and the Alford slot
A long axial slot in a metal tube of circumference ≲ 0.25–0.5λ radiates a nearly omnidirectional, *horizontally* polarized (for a vertical tube) pattern — the slotted-cylinder omni used at UHF/L-band; the tube's inside acts as a parallel resonant circuit across the slot. The Alford slot adds folded-back flanges to tune it and raise gain slightly [3]. Azimuth ripple grows as the tube gets larger in wavelengths; a rocket body tube at 433 MHz (ka ≈ 0.45 for 100 mm diameter) is in the good-omni regime.

### Slotted-waveguide arrays
Longitudinal slots in the broad wall of rectangular guide (width a, height b), offset x from the centreline, each ≈ 0.48λ₀ long, spaced λg/2, the last slot λg/4 (or 3λg/4) from the shorted end [3]:
$$\lambda_g=\frac{1}{\sqrt{\lambda_0^{-2}-(2a)^{-2}}},\qquad \frac{G_\text{slot}}{G_0}=2.09\,\frac{\lambda_g}{\lambda_0}\,\frac{a}{b}\cos^2\!\Big(\frac{\pi\lambda_0}{2\lambda_g}\Big)\sin^2\!\Big(\frac{\pi x}{a}\Big)\ \text{(Stevenson)}$$
Because λg/2 spacing makes the inter-slot line sections impedance-repeating, all N slot conductances appear in parallel at the input: a match needs $\sum g_n=1$ (g = 1/N for uniform illumination). Elliott's refinement replaces $\cos^2(\pi\lambda_0/2\lambda_g)$ by $[\cos(0.464\pi\lambda_0/\lambda_g)-\cos(0.464\pi)]^2$ for the true resonant length [3]. Gain ≈ 10 log(N·s/λ₀) (N counting both walls), elevation HPBW ≈ 50.7λ₀/L with L the slot-column length (DK3BA/DG8SG via [3]).

**Why alternate offsets?** The TE₁₀ transverse field at λg/2 spacing reverses sign (180°); a slot on the other side of the centreline samples the wall current with the opposite sign (another 180°). Alternating offsets therefore excite every slot in phase → broadside beam. With all slots on one side the array factor has a *null* at broadside and the beam goes to ±51° for 8 slots at 10.368 GHz (`ant2_slot.py` §5). Slots on the *far* wall use the mirror pattern for an omni; reversing it produces azimuth nulls [3].

**Tolerance.** Slot conductance errors are forgiving (every slot 10 % off → VSWR 1.1), but slot *length* is not: a 2.5 % length error gives VSWR > 2 (Stegen's measurements via [3]); CNC-machined WR-90 arrays designed for 10.368 GHz centred 1.4 % low until the offset formula was corrected [3]. Measured azimuth ripple of these "omnis" was up to 10 dB [3].

### Substrate-integrated-waveguide (SIW) slot arrays for 24/77 GHz radar
At millimetre wave a waveguide can be built *inside* a PCB: two rows of plated vias (pitch p ≲ 2× via diameter, p ≲ λg/10) form the side walls between the top and bottom copper, giving a TE₁₀-like guide of effective width $a_\text{eff}\approx a-d^2/(0.95p)$ (via diameter d; Cassivi/Wu closed form, cited via the SIW literature — not verified here). Longitudinal slots etched in the top copper then follow exactly the slotted-waveguide rules above (λg/2 spacing, alternating offsets, Σg = 1), giving low-loss linear arrays for 24 GHz and 77 GHz radar front ends ([11 diy-radar-hardware](../11-radar/diy-radar-hardware.md), [12 planar arrays](../12-phased-arrays/planar-arrays-element-pattern-coupling.md)). Dielectric loss is in the guide, so low-loss laminates (Rogers RO3003/RO4350B class) are required; FR-4 at 77 GHz is unusable.

### Where slots are used (quick map)
| Application | Slot type | Why a slot | Typical numbers |
|---|---|---|---|
| Aircraft/rocket flush antennas | cavity-backed or annular slot | no protrusion, rugged | ≈ 5 dBi, few % BW |
| Metal phones/laptops | λ/4 or λ/2 slot/gap in the chassis | chassis is the radiator | product-specific |
| Shipboard/radar omni at X-band | slotted waveguide | high-power, horizontally polarized omni | 10–16 dBi (12–24 slots) |
| Marine radar, ATC radar | travelling-wave slotted guide, fan beam | low loss, frequency scanning | squint ≈ 0.8° per 1 % Δf (WR-90 at 10.4 GHz, `ant2_slot.py` §6) |
| 24/77 GHz automotive radar | SIW slot arrays | PCB process, low loss | 10–20 dBi rows |
| Patch feeding | aperture (non-resonant slot) coupling | separates feed and radiator | — |
| UWB/SDR | tapered slot (Vivaldi), wide slots | multi-octave bandwidth | see [wideband](multiband-and-wideband-antennas.md) |
| EMC (unwanted) | seams, vents, connector cut-outs | — | SE ≈ 20 log(λ/2L) |

## Design equations & rules of thumb
| Quantity | Equation / value | Valid | Typical |
|---|---|---|---|
| Babinet–Booker | $Z_sZ_d=\eta_0^2/4=35\,481\ \Omega^2$ | thin PEC infinite screen, same medium both sides | resonant slot 475–490 Ω |
| Resonant slot length (air) | ≈ same as complementary strip dipole (w ↔ wire radius w/4) | w ≲ λ/50 | 0.465–0.475λ |
| Resonant PCB slot (1.6 mm FR-4) | L ≈ 0.70 λ₀/2 | 2.4 GHz, w ≈ 2.5 mm | 42.7 mm at 2.45 GHz |
| Feed offset | $R(x)=R_c\cos^2(\pi x/L_\text{res})$ | resonant slot, first order | 50 Ω near 0.04λ from the end (air) |
| One-sided (cavity-backed) slot | R ≈ 2 × two-sided, D + ≈3 dB | cavity ≈ open circuit | ≈ 1 kΩ, ≈ 5 dBi |
| Self-complementary structure | Z = η₀/2 = 188.4 Ω | infinite, planar | spirals, 90° bow-tie |
| Slotted guide spacing | λg/2, alternating offsets | resonant array | WR-90 @ 10.368 GHz: 18.69 mm |
| Match condition | Σ g_n = 1 | resonant slots | g = 1/N |
| Slot as EMC leak | radiates well when L ≈ λ/2 (single-slot SE ≈ 20 log(λ/2L) dB rule, Ott [6]) | L < λ/2 | 60 mm seam at 2.45 GHz ≈ 0 dB shielding |

## Worked examples

**Example 1 — Impedance of a resonant slot from its dipole complement.** A strip dipole of width 2.45 mm (λ/50 at 2.45 GHz) resonates at 57.0 mm with R = 74.9 Ω (MoM). Babinet: Z_s = 35 481/74.9 = **474 Ω**. openEMS of the slot itself (PEC sheet into the PML, lumped feed across the slot): X = 0 at 2.443 GHz with **R = 488 Ω** — 3 % from the Babinet/MoM value and 0.3 % in frequency. At 0.95 f₀ the slot is 471 + j227 Ω (Babinet from the strip: 493 + j219 Ω): inductive below resonance, as predicted.

**Example 2 — A 2.45 GHz PCB slot and its 50 Ω feed point.** Slot 43.5 mm × 2.45 mm on a 90 × 60 mm, 1.6 mm FR-4 board → resonance 2.403 GHz; scale the length by 2.403/2.45 → **42.7 mm** for 2.45 GHz. Centre R ≈ 613 Ω. For 50 Ω: $\cos^2(\pi x/L)=50/613=0.082$ ⇒ πx/L = 1.283 rad ⇒ x = 0.408L = **17.4 mm from the centre (≈ 3.9 mm from the end)**. The cos² model predicted the L/4 point to within 6 % in openEMS, but so close to the end it is only a starting value; in practice use the microstrip-crossing feed with an open stub (Yoshimura [4]) and tune the stub and crossing point in openEMS. Expected: D ≈ 5 dBi bidirectional, e_rad ≈ 93 %, VSWR-2 bandwidth several percent.

**Example 3 — 16-slot WR-90 omni for 10.368 GHz** (reproduces the W1GHZ sheet [3]). a = 22.86 mm, b = 10.16 mm. λ₀ = 28.92 mm, λ_c = 45.72 mm, λg = 37.33 mm (37.37 mm with c = 3 × 10⁸). g = 1/16 = 0.0625. Stevenson: G1 = 2.09 × (37.33/28.92) × (22.86/10.16) × cos²(π·28.92/74.66) = 0.730; sin²(πx/a) = 0.0625/0.730 ⇒ **x = 2.16 mm**; Elliott: G1 = 0.601 ⇒ **x = 2.39 mm**. Spacing 18.66 mm, end short λg/4 = 9.33 mm from the last slot centre, slot length ≈ 0.485λ₀ ≈ 14.0 mm (Stegen curves via [3]), width 1.6 mm. Gain ≈ 10 log(16 × 18.66/28.92) = **10.1 dB**, elevation HPBW ≈ **9.8°**. Measured units show up to 10 dB azimuth ripple [3].

**Example 4 — A 915 MHz antenna with no keep-out area.** The flight computer board is 80 × 100 mm with solid ground copper and no room for a keep-out. Cut a 2 mm × 51.5 mm notch inward from one short edge (in a corner region free of traces), feed it with 50 Ω coax or a grounded-CPW stub across the slot 9 mm from the closed end, and add a series capacitor footprint (start ≈ 8.5 pF) at the feed. openEMS: best match 917 MHz, VSWR ≤ 2 from 872 to 986 MHz (covers 902–928 MHz with margin for detuning by a nose cone), D ≈ 2.2 dBi, efficiency > 95 %. Route no traces across the slot (a crossing trace shorts it at that point and moves the resonance up), and keep battery/pyro leads away from the open end.

**Example 5 — Is my enclosure seam an antenna?** A 1 mm × 60 mm unfilled seam in an aluminium avionics box. At 2.45 GHz λ/2 = 61 mm: the seam is a resonant slot and leaks almost as well as a dipole; at 433 MHz (λ/2 = 346 mm) the single-slot rule gives SE ≈ 20 log(692/120) ≈ **15 dB** — weak. Fix: stitch seams at ≤ λ/20 of the highest harmonic of concern or add conductive gasket (see [13-pcb-rf-layout-emc](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).

## Practical notes
- **Build/tune**: slot length sets frequency (ΔL/L ≈ Δf/f); feed offset or stub sets impedance. Trim the slot *shorter* with copper tape bridged across one end (solder or conductive tape) to raise frequency.
- **Polarization check**: E is across the slot. A vertical slot on a vertical mast radiates horizontal polarization — match the other end of the link ([polarization](antenna-polarization-and-circular-polarization.md)).
- **Keep copper pour intact around the slot** — the slot's currents flow in the surrounding ground; cuts, vias fences or components near the slot ends detune it. Unlike an IFA, a slot *needs* the metal around it.
- **Feed cable**: the slot is balanced across its two edges; a coax soldered directly across it puts current on the braid unless the braid runs along the metal (bonded to the sheet) away from the slot — standard practice is to run the coax on the sheet and solder the braid to one edge, the centre to the other edge.
- **Radome/cover**: a plastic or glass window over a slot lowers its resonance like a dielectric substrate does; model it.
- **Ground-plane size**: the slot's resonant frequency is robust to board size (1 % in our runs), its impedance is not (420–710 Ω) — design the feed on the real board outline.

## Common mistakes & misconceptions
- **"A slot is just a dipole."** Same pattern shape, but polarization rotated 90°, reactance of opposite sign, and impedance η²/(4Z_d) ≈ 490 Ω, not 73 Ω.
- **"A narrow slot can't radiate — there's hardly any hole."** Radiation depends on the slot length (resonance) and the voltage across it, not the open area; a λ/2 slot of width λ/200 radiates as well as a dipole (492 Ω resonant, MoM + Babinet).
- **"A 2.45 GHz PCB slot is 61 mm (λ/2)."** On 1.6 mm FR-4 it is ≈ 42.7 mm (0.70 × λ₀/2, openEMS); in free-standing metal ≈ 57 mm (0.465λ).
- **"Babinet gives me the PCB slot impedance."** Only for an infinite, thin, perfectly conducting sheet in a homogeneous medium; a real board changed R_c from 714 to 423 Ω.
- **"Cavity-backing doesn't change the impedance."** Radiating into one half-space doubles R (and the cavity adds reactance).
- **"Put all waveguide slots on one side of the centreline."** Then adjacent slots are in antiphase and broadside becomes a null; alternate them (§ slotted-waveguide).
- **"Slot antennas are wideband."** A thin resonant slot is as narrowband as a dipole (few %); wide, tapered or stub-matched slots are wideband (see the Vivaldi on [multiband-and-wideband](multiband-and-wideband-antennas.md)).
- **"A slotted-waveguide omni is a perfect omni."** Measured azimuth ripple of ham 10 GHz units reaches 10 dB, and elevation sidelobes are high [3]; it is a convenient beacon antenna, not a precision one.
- **"Any FR-4 slot will do at 77 GHz."** At mm-wave the substrate loss and the via-wall geometry (SIW) dominate; use a radar laminate.
- **"Metal enclosures are RF-tight."** Every seam or vent ≈ λ/2 long at some frequency of interest is an antenna (single-slot SE ≈ 20 log(λ/2L)).
- **"Running a trace across the slot is harmless."** The trace's return current must detour round the slot (an EMC disaster on a digital board) and, on an antenna slot, the crossing shorts it locally and retunes it.
- **"A notch slot is a quarter wave long."** On 1.6 mm FR-4 it resonates at ≈ 0.63 × λ₀/4 (51.5 mm at 915 MHz, openEMS) because of the substrate and the open-end fringing.
- **"NEC can simulate my slot."** NEC-2 models wires only; model the complementary strip and apply Babinet, or use openEMS/FEM for the actual slot.

## How to simulate / verify
- `python3 tools/verify/ant2_slot.py` — Babinet numbers, MoM strip → slot, offset-feed model, WR-90 slotted-array design (reproduces W1GHZ), array-factor proof of alternating offsets, squint vs frequency.
- `~/opt/openEMS/venv/bin/python tools/verify/ant2_slot_openems.py [A B C D E F<L>,<feed>]` — FDTD of a free slot (Babinet check), of PCB slots on infinite and 90 × 60 mm FR-4 with centre and offset feeds, and of edge-notch slots (case F, 915 MHz); results in `tools/verify/ant2_slot_openems_results.txt` (each case 13–78 s on an M-series Mac, 0.31–1.0 M cells). Mesh: ≥ 4 cells across the slot, thirds rule on its edges and ends ([openEMS workflow](../16-simulation-tools/openems-workflow.md)).
- NEC/MoM: model the complementary strip (radius w/4), then map with Babinet; valid only for the infinite-screen case.
- Measure: NanoVNA S11 with the coax braid bonded along the sheet; confirm polarization with a linear reference antenna rotated 90°.

## Open questions / gaps
- Microstrip-crossing feed (Yoshimura) not simulated here; the cos² offset model is first-order and weakest near the slot ends.
- 5.8 GHz PCB-slot length factor is an estimate (0.66–0.70); run `ant2_slot_openems.py` scaled.
- Slots in metal rocket airframes (axial slot, circumferential gap) need an openEMS airframe model with the real tube diameter, fibreglass cover and internal wiring.
- Booker 1946 and Stevenson 1948 read via abstracts/secondary (W1GHZ) only; Yoshimura 1972 and Pozar 1985 cited, not read.

## Sources
1. H. G. Booker, "Slot aerials and their relation to complementary wire aerials (Babinet's principle)," *J. IEE* Part IIIA, 93(4), 620–626, 1946. https://digital-library.theiet.org/content/journals/10.1049/ji-3a-1.1946.0150 — Booker's vector Babinet principle; resonant slot ≈ 485 Ω (abstract read). (peer-reviewed)
2. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016 — aperture antennas and Babinet's principle; slot/dipole impedance relation; equivalence principle (M_s = 2E × n); cavity-backed slots (textbook; cited). Also J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — slot, complementary and cavity-backed antennas. (textbook; cited)
3. P. Wade (W1GHZ), *Online Microwave Antenna Book*, ch. 7 "Slot Antennas," 2000/2019. http://www.w1ghz.org/antbook/ch7_part1.pdf — Booker/Babinet summary; Stevenson (1948, *J. Appl. Phys.* 19, 24–38) slot conductance; Elliott–Kurtz resonant length 0.464/0.483λ₀; Stegen measurements; λg/2 alternating offsets; 10.368 GHz WR-90 design sheet; tolerance and measured patterns (expert article; READ via pdftotext).
4. Y. Yoshimura, "A microstripline slot antenna," *IEEE Trans. MTT* 20(11), 760–762, 1972 — microstrip-crossing slot feed with open stub. (peer-reviewed; cited)
5. D. M. Pozar, "Microstrip antenna aperture-coupled to a microstripline," *Electron. Lett.* 21(2), 49–50, 1985. (peer-reviewed; cited)
6. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 — aperture/slot leakage and the single-slot shielding rule of thumb. (textbook; cited)
7. Y. Mushiake, "Self-complementary antennas," *IEEE APM* 34(6), 23–29, 1992 (review of his 1948–49 principle: Z = η₀/2). (peer-reviewed; cited)
8. This repository: `tools/verify/ant2_slot.py`, `tools/verify/ant2_slot_openems.py` (+ results file); strip-dipole MoM from `tools/verify/ant_mom_wire.py`. (verification)
