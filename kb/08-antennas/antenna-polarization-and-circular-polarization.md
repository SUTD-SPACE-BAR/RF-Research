---
title: Antenna polarization and circular polarization — axial ratio, IEEE handedness, generating CP, polarization loss factor
domain: 08-antennas
slug: antenna-polarization-and-circular-polarization
tags: [polarization, circular-polarization, rhcp, lhcp, axial-ratio, cross-polarization, plf, polarization-mismatch, turnstile, crossed-dipole, handedness, spin-modulation, eggbeater, lindenblad, omni-cp, ground-station]
prerequisites: [antenna-fundamentals.md, ../02-electromagnetics/wave-equation-plane-waves-polarization.md, ../00-math-foundations/complex-numbers-and-phasors.md]
related: [../09-propagation-link-budget/polarization-mismatch-loss.md, helical-antennas.md, patch-antennas.md, gnss-antennas.md, antennas-on-rockets.md, yagi-uda-and-log-periodic.md, antenna-measurement.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Antenna polarization and circular polarization

## Questions this page answers
- What is the polarization of an antenna, and how is it defined when receiving?
- What does RHCP actually mean — clockwise from where?
- What is axial ratio, and how does it relate to cross-polarization?
- How much signal do I lose with a linear antenna receiving a circularly polarized signal, or two linear antennas at an angle?
- Why does reflection turn RHCP into LHCP, and why does that help GNSS reject multipath?
- How do I make circular polarization (crossed dipoles, patches, helices)?
- My rocket rolls — should the ground station be circularly polarized?
- What is "spin Doppler"?
- Is a truly isotropic antenna possible, and what does the hairy-ball theorem have to do with it?
- Which fixed circularly polarized antenna covers a rocket overhead without tracking: turnstile, eggbeater or Lindenblad?
- When is an omni-CP antenna better than a crossed Yagi for a ground station?

## TL;DR
- The **polarization of an antenna** in a direction is the polarization of the wave it *transmits* in that direction (IEEE Std 145 [1]); by reciprocity it receives best a wave with the same polarization arriving from that direction.
- **IEEE handedness**: viewed looking *along the direction of propagation* (from behind the wave), clockwise rotation of E = **right-hand** (RHCP). Equivalently: thumb along propagation, fingers curl with E. Optics texts often use the opposite convention. In e^{+jωt} phasor form with propagation along +z, (x̂ − jŷ)/√2 is RHCP — computed, not assumed, in `tools/verify/ant_polarization.py`.
- **Axial ratio** AR = major/minor axis of the polarization ellipse (1 = 0 dB is perfect CP; ∞ is linear). For a CP antenna, the cross-polar (opposite-sense) component relative to co-polar is (AR−1)/(AR+1): AR = 3 dB → −15.3 dB cross-pol.
- **Polarization loss factor** (both states in the wave's frame): linear–linear at angle ψ: cos²ψ (45° → −3 dB, 90° → null); CP–linear: −3.01 dB at any angle; RHCP–LHCP: null (in practice −15 to −25 dB); a 3-dB-AR "CP" antenna receiving a linear wave: **−1.76 to −4.76 dB** depending on orientation (script).
- **Reflection from a conductor at normal incidence reverses handedness** (verified): GNSS antennas are RHCP partly so that once-reflected (LHCP) multipath is rejected.
- **Omni-CP without tracking** (NEC, 433/915 MHz, `s12_corner_omnicp.py`):
  - **Turnstile over a crossed reflector** (0.25λ) puts its gain overhead: +5.1 dBic at the zenith, +2.9 at 45°, +1.0 at 30°, −2.5 dBic at 10°.
  - **Eggbeater** (two crossed full-wave loops, reflector 0.2λ below) is nearly flat: +0.5 to +1.2 dBic from 20° to 90°, and −0.2 dBic at 10°.
  - **Lindenblad** has a zenith null but +0.6 to +1.1 dBic from 30° down to the horizon, with AR ≤ 1.5 dB.
  - **A crossed 7-element Yagi** gives 12.0 dBic but only within ±24° (−3 dB).
- **For a rolling rocket with a linear antenna**, a linear ground antenna sees two deep nulls per revolution; a CP ground antenna sees a constant −3 dB and a carrier phase that advances at the roll rate (frequency offset = roll rate, e.g. 5 Hz — negligible for LoRa).

## Intuition (no math)
A radio wave's electric field points somewhere in the plane perpendicular to its travel. If it always points along one line (say vertically) the wave is linearly polarized. If it rotates at the RF frequency with constant length, it is circularly polarized; in general its tip traces an ellipse.

A wire antenna responds to the component of E along the wire. Two linear antennas crossed at 90° hear nothing from each other. A circularly polarized wave, by contrast, always has *some* field along any wire — but only half its power lies along any one direction, so a linear antenna always loses 3 dB against a CP wave. Two CP antennas of the same sense match perfectly regardless of how they are rotated about the line between them; of opposite sense, they reject each other.

Handedness flips on reflection because the reflected wave travels the other way while its field keeps rotating the same way in space; since handedness is defined relative to the travel direction, the label changes.

## The math

### Level 1 — describing polarization
A plane wave travelling along +z: **E**(t) = Re{(E_x x̂ + E_y ŷ)e^{j(ωt−kz)}}, with complex E_x = a_x, E_y = a_y e^{jδ}. The normalized complex vector ê = (E_x, E_y)/|E| is the **Jones vector**.
- Linear: δ = 0 or π. Circular: a_x = a_y and δ = ±90°. Otherwise elliptical.
- **Axial ratio** AR = OA/OB ≥ 1 (dB: 20 log AR); **tilt** τ = orientation of the major axis; **sense** = rotation direction.
- For e^{+jωt}, +z: ê = (1, −j)/√2 is RHCP; (1, +j)/√2 is LHCP (IEEE) — i.e. E_y lags E_x by 90° for RHCP.

**Polarization loss factor** PLF = |ê_w · ê_a*|² where ê_w is the wave's and ê_a the antenna's receive-matched polarization, both expressed in the same (wave) coordinate frame. Closed form for ellipses with signed axial ratios r_w, r_a (same sign = same sense) and tilt difference Δτ (Stutzman [3]):
$$\text{PLF}=\frac12+\frac{2r_wr_a}{(1+r_w^2)(1+r_a^2)}+\frac{(1-r_w^2)(1-r_a^2)\cos2\Delta\tau}{2(1+r_w^2)(1+r_a^2)} .$$
Our script checks this against the Jones overlap for 2000 random ellipses (max difference 8×10⁻¹⁶).

### Level 2 — co-/cross-polar decomposition and AR
Any polarization can be written as a sum of RHCP and LHCP components, ê = c_R ê_R + c_L ê_L. Then
$$\text{AR}=\frac{|c_R|+|c_L|}{\big||c_R|-|c_L|\big|},\qquad \frac{|c_L|}{|c_R|}=\frac{\text{AR}-1}{\text{AR}+1}\ (\text{for an RHCP-dominant wave}).$$
So "AR < 3 dB" (r = 1.413) means cross-pol ≤ −15.3 dB; AR 1 dB → −24.8 dB; AR 6 dB → −9.5 dB. Antenna patterns quoted in dBic are the co-polar (RHCP) partial gain; a linear antenna has equal RHCP and LHCP partial gains, each 3 dB below its total gain.

**Receiving frame subtlety.** A transmitting antenna's polarization is described looking outward along its own propagation direction; a *receiving* antenna faces the other way. With a common global frame, a matched receive antenna for an incoming RHCP wave is one that would *transmit* RHCP toward the source; IEEE Std 145 [1] and IEEE Std 149 [2] warn that the two coordinate systems are oppositely oriented and one must be transformed. The practical rule: **RHCP transmit antenna ↔ RHCP receive antenna** (both labelled by their transmit sense), after a direct path; each reflection swaps the required sense.

**Reflection.** At normal incidence on a perfect conductor, E_tan,reflected = −E_tan,incident: the field rotates the same way in space, the direction of travel reverses, so the handedness label flips (script: RHCP in → LHCP out). At oblique incidence on real ground, vertical (TM) and horizontal (TE) components reflect with different magnitudes and phases (near the Brewster angle the TM component nearly vanishes), so a CP wave becomes elliptical with either sense depending on angle ([boundary conditions and reflection](../02-electromagnetics/boundary-conditions-reflection-refraction.md), [two-ray ground reflection](../09-propagation-link-budget/two-ray-ground-reflection.md)).

### Level 3 — generating CP, and time-varying polarization
**Two orthogonal linear radiators in quadrature.** Crossed dipoles (turnstile) fed 0°/90° through a λ/4 line or a hybrid; dual-fed patches with a 90° hybrid; crossed Yagis. Errors: with equal amplitudes and a phase error Δφ from 90°, |c_L/c_R| = tan(Δφ/2) exactly, so AR = [1 + tan(Δφ/2)]/[1 − tan(Δφ/2)] — a 10° error gives AR = 1.19 (1.52 dB). For small amplitude imbalance ε (fractional) and phase error Δφ (radians) together, AR ≈ 1 + √(ε² + Δφ²).

**Single-feed two-mode radiators.** Nearly-square/truncated-corner patches and self-phased QFHs split two orthogonal resonances by ≈ f₀/Q so that at the centre they are ±45°; axial-ratio bandwidth ≈ half the impedance bandwidth ([patch-antennas](patch-antennas.md), [helical-antennas](helical-antennas.md#quadrifilar-helix-qfh)).

**Travelling-wave CP.** The axial-mode helix produces CP intrinsically (current wave rotating once per turn), AR ≈ (2N+1)/2N on axis, over a wide band.

**Rotating linear source (roll).** A linear transmitter rotating at ω_r about the line of sight, received by:
- a fixed linear antenna: PLF(t) = cos²(ω_r t + ψ₀) → two nulls per revolution; averaged −3 dB but with deep fades;
- a CP antenna: the linear wave = equal RHCP + LHCP components; rotation by angle ω_r t multiplies the RHCP component by e^{∓jω_r t}. The CP receiver sees constant amplitude (−3 dB) and a phase ramp — a frequency offset equal to the roll rate (script: 5 rev/s → −5.00 Hz). This is the "spin Doppler" or "spin modulation" effect in spinning-vehicle telemetry.
- Two orthogonal linear receivers with diversity combining recover the full signal without the 3 dB CP penalty but need two receive chains.

**Ionospheric Faraday rotation** rotates linear polarization on Earth–space paths at VHF/UHF (large at 145/435 MHz, much smaller at L-band); CP is immune except for handedness-independent loss. For suborbital amateur rockets below ~100 km it is negligible; for satellite links it is a reason for CP ([ionospheric propagation](../09-propagation-link-budget/ionospheric-hf-propagation.md)).

## Omni-CP antennas for overhead passes: turnstile, eggbeater, Lindenblad

**Why.** A ground station 1–3 km from the pad sees the rocket climb from about 0° to 50–80° elevation in seconds, often with an uncertain azimuth during descent. A fixed antenna that is circularly polarized over most of the sky needs no tracker and no polarization alignment. The price is gain: it gets 0–5 dBic where a crossed Yagi gets 10–12 dBic. All three classic designs use two orthogonal radiators in quadrature (Level 3 above) and differ in where the CP coverage falls.

**NEC models** (`tools/verify/s12_corner_omnicp.py`) use free space, ideal 0°/90° phasing and the azimuth-mean RHCP partial gain. The sense is checked from NEC's complex E_θ/E_φ with c_R = (E_θ + jE_φ)/√2 under e^{jωt}. A turnstile with its second dipole lagging by 90° gives RHCP upward, 26.9 dB above LHCP. Every model passes the average-gain test (0.998–1.000).
- **Turnstile:** two crossed resonant dipoles, 319 mm at 433 MHz (6 mm) and 151 mm at 915 MHz (3 mm). Free space gives 2.1 dBic at the zenith; it becomes linear (horizontal) at the horizon. Over crossed 0.52λ reflector rods (a crossed 2-element Yagi pointing up): with the reflector 0.20/0.25/0.30λ below, the zenith gain is 5.5/5.1/4.4 dBic and Z is 75 + j31 / 86 + j20 / 91 + j8 Ω.
- **Eggbeater:** two crossed circular loops, resonant at C = 1.088λ (753 mm, 240 mm diameter at 433 MHz in 4 mm wire; 357 mm, 114 mm diameter at 915 MHz). Each loop is ≈ 150–160 Ω, fed at the top in quadrature. Crossed 0.55λ reflector rods sit a distance d below the loop bottoms. The reflector spacing trades zenith gain for low-angle gain (zenith / 30° / 10°):
  - no reflector: −0.4 / −0.1 / −0.9 dBic;
  - d = 0.1λ: +2.3 / +1.0 / −0.9 dBic;
  - d = 0.2λ: +0.5 / +1.1 / −0.2 dBic;
  - d = 0.3λ: −2.0 / +0.7 / +0.2 dBic.
- **Lindenblad:** four λ/2 dipoles on a λ/3-diameter circle (231 mm at 433 MHz, 109 mm at 915 MHz), each tilted 30° from horizontal and fed in phase (≈ 102 + j40 Ω each). It is CP toward the horizon and has a null overhead.

| Elevation | Eggbeater (d = 0.2λ) | Turnstile + reflector (0.25λ) | Lindenblad | Crossed 7-el Yagi aimed at 45° |
|---|---|---|---|---|
| 90° | +0.5 dBic | +5.1 | null | −1.8 |
| 75° | +0.6 | +4.9 | −8.6 | +7.3 |
| 60° | +1.0 | +4.1 | −2.8 | +11.0 |
| 45° | +1.2 | +2.9 | −0.6 | +12.0 |
| 30° | +1.1 | +1.0 | +0.6 | +11.0 |
| 20° | +0.6 | −0.6 | +0.9 | +8.9 |
| 10° | −0.2 | −2.5 | +1.1 | +5.2 |
| 5° | −0.6 | −3.3 | +1.1 | +2.3 |

Axial ratio (azimuth mean):
- **Turnstile and eggbeater:** ≤ 2 dB above 60°, ≈ 4 dB at 45°, ≈ 7 dB at 30° and 13–16 dB at 10°. Near the horizon they are nearly horizontally polarized, so a vertical rocket whip on the pad sees mainly the −3 dB-plus-AR mismatch.
- **Lindenblad:** ≤ 1.5 dB from −10° to 60°.
- **Crossed 7-element Yagi** (DL6WU, 1.2λ boom): 12.0 dBic on axis, 10.1 dBic at 20° off axis, 7.3 dBic at 30° and 2.3 dBic at 40°.

**Choosing.** Gains below are for a linear rocket antenna (−3 dB to any CP antenna):
- **Rocket mostly overhead** (station close to the pad, high apogee): a turnstile over a reflector. It is the simplest build and gives the most gain where the rocket spends its flight.
- **Rocket anywhere from 10° to 90°**, or recovery-phase links at mid elevation: an eggbeater with d ≈ 0.2λ. Within ±1.5 dB it is a "hemisphere" antenna.
- **Low-elevation links** (long ground range, descent under canopy far away, pad-to-station on the horizon): a Lindenblad. A vertical collinear is the linear alternative ([dipoles](dipoles-and-monopoles.md#collinear-arrays-and-phasing-coils)).
- **Margin-limited flights** (Singapore 10 mW e.r.p., high apogee): a crossed Yagi with a tracker or an elevation-only mount. The 9–11 dB advantage over an omni-CP antenna is worth the pointing effort only when the [link budget](../09-propagation-link-budget/link-budget-methodology.md) needs it. The fixed-aim Yagi column shows that ±25° of pointing error already costs 3 dB.

**Real ground.** These are free-space numbers. On a 1.5–3 m tripod (2–4λ at 433 MHz), ground reflection adds a lobing ripple of several dB below ≈ 15° elevation. Each reflection also reverses the CP sense, so the reflected wave is partly rejected; the ripple is less than with a linear antenna but not zero. A Yagi T_A study over the same ground is in [antenna measurement](antenna-measurement.md#antenna-temperature-and-gt-vs-elevation-over-ground). Phasing networks:
- **Turnstile and eggbeater:** a λ/4 delay line (eggbeater builders use 93 Ω coax, forum practice) or a 90° hybrid; Level 3 above gives the AR cost of phase errors (10° → 1.5 dB).
- **Lindenblad:** an equal-phase 4-way harness. AA2TX's parasitic-polarizer version avoids the harness (AMSAT literature [8]).

## Design equations & rules of thumb

| Situation | Loss / value |
|---|---|
| Linear vs linear, angle ψ | 10 log cos²ψ: 30° → −1.25 dB, 45° → −3.0 dB, 60° → −6.0 dB, 80° → −15.2 dB |
| Linear vs CP | −3.01 dB |
| RHCP vs LHCP | ideal null; practical −15 to −25 dB |
| AR → cross-pol | 20 log[(AR−1)/(AR+1)]: 1 dB → −24.8, 3 dB → −15.3, 6 dB → −9.5 dB |
| 3-dB-AR antenna, linear wave | −1.76 … −4.76 dB |
| 3-dB-AR antenna, same-sense CP wave | −0.13 dB |
| 3-dB-AR antenna, opposite-sense CP wave | −15.5 dB |
| Quadrature phase error Δφ | AR = (1+tan(Δφ/2))/(1−tan(Δφ/2)): 5° → 0.76 dB, 10° → 1.52 dB, 20° → 3.1 dB |
| Roll with CP receive | constant −3 dB; frequency offset = roll rate |
| Turnstile + reflector 0.25λ | +5.1 dBic zenith, +1.0 at 30°, −2.5 at 10° (NEC) |
| Eggbeater, reflector 0.2λ | +0.5…+1.2 dBic 20–90°, −0.2 at 10° |
| Lindenblad (λ/3 circle, 30° tilt) | null at zenith; +0.6…+1.1 dBic 30° to horizon |

## Worked examples

**Example 1 — Rocket on the pad, horizontal Yagi.** The rocket's 433 MHz whip is vertical; the ground-station Yagi is mounted horizontally (common when copied from satellite setups). ψ = 90°: theoretical null; in practice ground reflections and imperfect antennas give −15 to −25 dB. Packets are lost on the pad even at 100 m, then appear when the rocket tilts. Fix: mount the Yagi vertically, or use CP.

**Example 2 — Crossed-Yagi ground station for a rolling rocket.** A 2 × 6-element crossed Yagi fed through a 90° hybrid: co-polar gain ≈ 10 dBic. Receiving the rocket's linear dipole: −3 dB → ≈ 7 dB effective, *constant* through roll. The best-case linear Yagi (10 dBi, aligned) is 3 dB better only when aligned and suffers nulls twice per revolution — at 5 rev/s roll, 10 fades per second, each long enough to corrupt a LoRa packet of tens of ms.

**Example 3 — GNSS antenna AR and multipath.** A ceramic patch with AR = 3 dB at zenith but 10 dB at 10° elevation (typical of small ground planes; u-blox reports AR ≈ 10 dB on an unsuitably large 100 mm ground in one case [4]) accepts a single-bounce LHCP reflection from a building with only ≈ 2–5 dB rejection at low elevation instead of 15+ dB — degrading pseudorange accuracy. See [gnss-antennas](gnss-antennas.md).

**Example 4 — LoRa and spin Doppler.** LoRa demodulators tolerate a carrier frequency offset of a sizeable fraction of the bandwidth (tens of kHz for 125 kHz BW) — see [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md). A roll rate of 10 rev/s adds a 10 Hz offset: irrelevant. (Vehicle Doppler at 300 m/s is 433 Hz at 433 MHz — also small.)

## Practical notes
- **Label your antennas by transmit sense.** Datasheets for GNSS and satellite antennas state RHCP/LHCP as transmit sense (IEEE).
- **Check sense empirically**: with an RHCP reference source and the AUT facing it, co-polar reception should be 15–25 dB stronger than with an LHCP reference; or compare against a known satellite signal (GNSS is RHCP).
- **Mirror/dish**: a prime-focus dish reverses sense — the feed must be the opposite sense of the incoming wave.
- **Measure AR** by rotating a linear source antenna in front of the AUT and recording the received level vs angle (the polarization pattern "dumbbell"): AR = max/min (IEEE Std 149 [2]; [antenna measurement](antenna-measurement.md)).
- **Near-ground CP antennas** (tripod height ≈ 1–2 m) receive strong ground-reflected components at low elevations; the reflected wave has altered sense and AR, so fading can still occur for a rocket near the horizon.

## Common mistakes & misconceptions
- **"RHCP means clockwise as seen by the receiver."** IEEE defines it looking in the direction of propagation (from the transmitter's side). The optics convention is reversed; always check which one a source uses.
- **"Linear to CP costs 3 dB, so linear to linear must be free."** Linear–linear is free only when aligned; misalignment can cost anything up to a null.
- **"A CP antenna receives both RHCP and LHCP."** It rejects the opposite sense; a linear antenna receives both at −3 dB each.
- **"Axial ratio is an efficiency."** AR describes the polarization state; the loss it causes depends on the incoming wave's polarization.
- **"Circular polarization penetrates better."** Polarization doesn't change attenuation in foliage/buildings materially; CP helps with orientation independence, Faraday rotation and odd-bounce multipath rejection.
- **Forum-observed** (r/meshtastic, r/amateurradio — anecdotal): people mixing a horizontally-mounted Yagi with vertical whips and blaming "range"; people winding a helix the wrong way (LHCP) for GNSS or weather satellites and losing ~15–20 dB.

- **"An eggbeater/turnstile is CP everywhere."** Only overhead. The AR passes 6 dB below ≈ 30° elevation, and the pattern is horizontally polarized at the horizon. Use a Lindenblad if the low angles matter.
- **"An omni-CP antenna is as good as a crossed Yagi if the rocket is close."** It is 9–11 dB lower everywhere inside the Yagi's beam; it only wins when the Yagi would be mis-pointed by more than ≈ 30°.

- **"An isotropic antenna is just hard to build."** With a single, everywhere-defined linear polarization it is impossible: the far-field E vector is tangent to the sphere of directions, and a continuous tangent field on a sphere must vanish somewhere (hairy-ball theorem; Mathis 1951 gave the antenna proof). Even combining electric dipoles with complex weights p cannot help: the radiated power ∝ |p|² − |p·r̂|², and |p·r̂|² = r̂ᵀ(Re p Re pᵀ + Im p Im pᵀ)r̂ is a rank-≤2 quadratic form, never constant over all directions. "Isotropic" (0 dBi) is a reference, not a device; real "omnis" have nulls (the dipole's axis) or polarization that changes with direction (D2 #248).

## How to simulate / verify
- `python3 tools/verify/ant_polarization.py` — IEEE sense computed from Jones vectors, PLF closed form vs overlap, AR→cross-pol, reflection handedness, rotating-source fades vs CP.
- `python3 tools/verify/ant_mom_general.py` — `U_components()` returns RHCP and LHCP partial intensities for any wire model (used to confirm a right-hand helix radiates RHCP).
- `python3 tools/verify/s12_corner_omnicp.py` — turnstile, eggbeater and Lindenblad patterns vs elevation (RHCP/LHCP partial gains, AR), crossed 7-element Yagi, and a comparison table (≈ 5 min, PyNEC). Note: PyNEC's `get_e_theta()` is flat with θ varying fastest.
- In NEC/openEMS, request RHCP/LHCP (or E_θ/E_φ amplitude and phase) far-field components; compute AR from them.

## Open questions / gaps
- The small-error AR formula for quadrature networks is a linearised result; a table from the exact expression could be added to the script.
- The omni-CP models use ideal quadrature sources and free space. Real phasing lines, mast and tripod, and ground lobing are not modelled.
- Measured roll-induced fade statistics for amateur rocket telemetry would be valuable (none found in this pass).

## Sources
1. IEEE Std 145-1993, *Definitions of Terms for Antennas* — polarization of an antenna (2.280), sense of polarization (2.355: clockwise viewed in the direction of propagation = right-hand), axial ratio (2.31), partial gain/directivity, and the receive-frame caveat in the introduction. https://www.ece.mcmaster.ca/faculty/nikolova/antenna_dload/IEEEStandard_AntennaTerms.pdf (standard)
2. IEEE Std 149-1979 (R2008), *Standard Test Procedures for Antennas* — clause 11 polarization measurement (rotating-source method, polarization pattern). (standard; cited via IEEE 145)
3. W. L. Stutzman and G. A. Thiele, *Antenna Theory and Design*, 3rd ed., Wiley, 2012 — ch. 1–2 polarization, PLF in terms of axial ratios and tilt; W. L. Stutzman, *Polarization in Electromagnetic Systems*, Artech House, 1993. (textbooks)
4. u-blox UBX-15030289, *GNSS antennas* app note — GNSS is RHCP; AR vs ground-plane size example; linear antennas lose ≈ 3 dB. (app note)
5. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — §2.12 polarization, PLF, polarization efficiency; §4.7 ground effects. (textbook)
6. This repository: `tools/verify/ant_polarization.py`, `tools/verify/s12_corner_omnicp.py`. (verification)
7. G. H. Brown, "The turnstile antenna," *Electronics* 9, 14–17, 1936; N. E. Lindenblad, "Antennas and transmission lines at the Empire State television station," *Communications* 21, 1941 — origins of the turnstile and Lindenblad (cited via secondary literature, not read).
8. AMSAT literature: J. Brown (K5OE), "The Eggbeater II" (archived at observations.biz/K5OE); T. Monteiro (AA2TX), "A parasitic Lindenblad antenna for 70 cm," AMSAT Symposium 2006; AMSAT "Getting started" guide (λ/3 circle, 30° tilt). Design practice only; the NEC numbers above are the KB's own. (amateur literature / forum — anecdotal)
