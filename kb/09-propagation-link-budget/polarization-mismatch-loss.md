---
title: Polarisation mismatch loss (PLF), axial-ratio mismatch and rocket attitude effects
domain: 09-propagation-link-budget
slug: polarization-mismatch-loss
tags: [polarization, polarization-loss-factor, PLF, axial-ratio, circular-polarization, cross-polarization, XPD, poincare-sphere, jones-vector, rocket-attitude, dipole-null, roll-modulation]
prerequisites: [../02-electromagnetics/wave-equation-plane-waves-polarization.md, friis-free-space-path-loss.md]
related: [link-budget-methodology.md, two-ray-ground-reflection.md, ionospheric-hf-propagation.md, link-margin-availability.md, ../08-antennas/antenna-polarization-and-circular-polarization.md, ../08-antennas/antennas-on-rockets.md, ../08-antennas/dipoles-and-monopoles.md, ../08-antennas/helical-antennas.md, ../08-antennas/gnss-antennas.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Polarisation mismatch loss (PLF), axial-ratio mismatch and rocket attitude effects

## Questions this page answers
- How much signal do I lose when the transmit and receive antennas are not polarised the same way?
- Why does a circularly polarised ground antenna cost exactly 3 dB with a linear rocket antenna, and why is that often a good deal?
- What does a CP antenna's axial ratio do to the mismatch loss?
- What happens to my link as the rocket pitches over, rolls, and swings under the parachute?
- Why is the signal weakest when the rocket flies straight away from (or toward) the ground station?
- Which way should the ground antenna be polarised for a landed rocket?

## TL;DR
- **Polarisation loss factor** $\text{PLF} = |\hat e_w\cdot\hat e_a^*|^2$ (0…1) between the wave's and the antenna's polarisation unit vectors (both described as the wave each would radiate, in a common frame). Linear–linear: $\cos^2\Delta\tau$ — **0.3 dB at 15°, 1.25 dB at 30°, 3 dB at 45°, 6 dB at 60°, 11.7 dB at 75°, 21 dB at 85°**, deep null at 90°.
- **Linear ↔ ideal circular: exactly 3.01 dB for any orientation.** RHCP↔RHCP 0 dB; RHCP↔LHCP → 0 (in practice limited by axial ratio to 10–20 dB of isolation).
- **Axial-ratio formula** (verified against Jones-vector calculation to 8×10⁻¹⁶, `tools/verify/prop_polarization.py`):
$$\text{PLF} = \frac12 + \frac{\pm4\,AR_wAR_a + (AR_w^2-1)(AR_a^2-1)\cos2\Delta\tau}{2(AR_w^2+1)(AR_a^2+1)}$$
($AR$ = voltage axial ratio ≥ 1, + for same hand). A "CP" ground antenna with 3 dB axial ratio receiving a linear wave gives **−1.76 to −4.76 dB** depending on tilt; 6 dB AR: −0.97 to −6.97 dB.
- **Rocket geometry dominates:** an axial dipole's gain toward the GS ∝ $\sin^2\psi$ ($\psi$ = angle between rocket axis and line of sight). A GS 0.5 km from the pad watching a vertical ascent to 3 km sees $\psi$ = 9.5° → **−15.7 dB**; at 10 km downrange $\psi$ = 68° → −0.6 dB. Put the GS well off the flight axis.
- The radiated field of an axial dipole is polarised along the projection of the rocket axis — near-vertical for a GS at low elevation during ascent, **horizontal for a landed rocket lying flat** (then a vertical ground antenna sees a cross-polar null if the body is broadside, and a pattern null if it points at the GS). A CP ground antenna avoids polarisation nulls entirely for 3 dB.

## Intuition (no math)
An antenna responds only to the component of the incoming electric field that lies along its own "polarisation direction". Two linear antennas at right angles are blind to each other; at 45° each receives half the power (−3 dB). A circularly polarised wave has an electric field that rotates, so a linear antenna at *any* angle picks up exactly half — a constant 3 dB, never a null. That is the trade: a CP ground station gives up a fixed 3 dB but can never be caught in a polarisation null, whatever the rocket does.

For a rocket, polarisation and pattern are tied together by geometry. A dipole or monopole along the rocket's axis radiates most strongly broadside to the body and not at all along the axis. Its field is polarised along the body's direction as seen from the observer. So as the rocket climbs away from a nearby ground station, the station sees it almost end-on (weak pattern), and as it tilts, the apparent polarisation angle tilts too. After landing, the body lies on the ground: the polarisation becomes horizontal and near the ground horizontal polarisation propagates badly ([two-ray-ground-reflection](two-ray-ground-reflection.md)).

Axial ratio describes how "circular" a CP antenna really is: 0 dB is perfectly circular; real antennas are elliptical, especially off boresight. A 3 dB axial ratio means the major axis is √2 times the minor, so a linear wave aligned with the major axis loses only 1.76 dB, but aligned with the minor axis loses 4.76 dB.

## The math

### Level 1 — definitions
- Polarisation (Jones) vector of an elliptically polarised wave with tilt $\tau$ (major axis from the x axis) and ellipticity angle $\varepsilon$ ($\tan\varepsilon = \pm1/AR$; sign = hand): $\hat e = R(\tau)\,[\cos\varepsilon,\ j\sin\varepsilon]^T$.
- **PLF** $= |\hat e_w\cdot\hat e_a^*|^2$, with $\hat e_a$ the polarisation the receive antenna would *transmit* in the direction of the incoming wave, expressed in the wave's frame (the convention used in the script, under which co-handed CP gives PLF = 1). Polarisation loss (dB) $= -10\log_{10}\text{PLF}$.
- Special cases: linear–linear $\cos^2\Delta\tau$; linear–circular 1/2; co-circular 1; cross-circular 0.
- **Cross-polar discrimination** XPD = co-pol/cross-pol response ratio (dB). For an antenna of axial ratio $AR$, the isolation between RHCP and LHCP is $20\log_{10}\frac{AR+1}{AR-1}$ (linear AR): 3 dB AR → 15.3 dB; 1 dB → 24.8 dB; 0.5 dB → 30.8 dB.

### Level 2 — the axial-ratio mismatch formula via the Poincaré sphere
Map each polarisation state to a point on the Poincaré sphere with longitude $2\tau$ and latitude $2\varepsilon$. The PLF between wave and antenna (with the matched-reception convention) is
$$\text{PLF} = \cos^2\frac{\gamma}{2} = \frac{1+\cos\gamma}{2},$$
where $\gamma$ is the angle between the two points: $\cos\gamma = \sin2\varepsilon_w\sin2\varepsilon_a + \cos2\varepsilon_w\cos2\varepsilon_a\cos2\Delta\tau$. With $\tan\varepsilon = 1/AR$: $\sin2\varepsilon = 2AR/(AR^2+1)$ and $\cos2\varepsilon = (AR^2-1)/(AR^2+1)$. Substituting gives the formula in the TL;DR (+ sign for the same hand, − for opposite hands). Checks: $AR\to\infty$ both (linear): $\tfrac12 + \tfrac12\cos2\Delta\tau = \cos^2\Delta\tau$; one linear, one ideal CP ($AR_a$ = 1): $\tfrac12$; both ideal CP same hand: 1; opposite: 0. The script confirms the closed form equals the Jones-vector PLF to machine precision over 20 000 random cases.

**Finite axial ratios (script §2):**
| Wave | Antenna | PLF range |
|---|---|---|
| linear | CP, AR 1 dB | −2.54 … −3.54 dB |
| linear | CP, AR 3 dB | −1.76 … −4.76 dB |
| linear | CP, AR 6 dB | −0.97 … −6.97 dB |
| CP AR 3 dB | CP AR 3 dB, same hand | −0.51 … 0.00 dB |
| CP AR 3 dB | CP AR 3 dB, opposite hand | −9.6 dB … null |
| CP AR 6 dB | CP AR 3 dB, same hand | −1.09 … −0.10 dB |

### Level 3 — rocket attitude, roll and other depolarisation
**Axial dipole geometry.** Let the rocket axis be the unit vector $\hat a$ and the line of sight (rocket → GS) $\hat u$. The radiated field direction is the projection $\hat E \propto \hat a - (\hat a\cdot\hat u)\hat u$ and the power pattern is $\sin^2\psi$ with $\cos\psi = \hat a\cdot\hat u$ (for a short dipole; a half-wave dipole's null is slightly narrower). The GS antenna sees:
- **Pattern term** $10\log_{10}\sin^2\psi$ (relative to broadside, 2.15 dBi for a half-wave dipole);
- **Polarisation term** vs a vertical-linear GS antenna: $\cos^2$ of the angle between $\hat E$ and the projected vertical; vs CP: 3 dB.
Script §3 cases:

| Geometry | ψ | Pattern | PLF vs vertical-linear GS | PLF vs CP GS |
|---|---|---|---|---|
| GS 0.5 km from pad, vertical ascent to 3 km | 9.5° | −15.7 dB | 0.0 dB | −3.0 dB |
| GS 2 km, 5° pitch away, 3 km altitude | 28.7° | −6.4 dB | 0.0 dB | −3.0 dB |
| GS 10 km, 5° pitch away, 3 km | 68.3° | −0.6 dB | 0.0 dB | −3.0 dB |
| GS 10 km, 20° pitch sideways, 10 km | 48.4° | −2.5 dB | −1.0 dB | −3.0 dB |
| Descent under chute swinging 60°, 20 km, 1 km alt. | 32.9° | −5.3 dB | 0.0 dB | −3.0 dB |
| Landed, body horizontal pointing at GS (5 km) | 0.3° | −44 dB | – | – |
| Landed, body horizontal broadside to GS | 90° | 0 dB | **null (cross-pol)** | −3.0 dB |

The dominant term during ascent is the pattern null along the axis, not polarisation; polarisation matters when the rocket tilts or lies down.

**Roll.** An axisymmetric axial antenna (dipole along the body, wrap-around/slot arrays designed for omni coverage) is insensitive to roll. A side-mounted linear antenna or a transverse dipole produces a PLF $\cos^2(\omega_rt + \phi)$ against a linear GS: two nulls per revolution (plus pattern modulation). A rocket rolling at 2 rev/s thus fades 4 times per second into nulls — at SF7 (packets ~70 ms) many packets survive; at SF12 (1.6 s) every packet contains nulls. A CP GS removes the polarisation part of this modulation.

**Other depolarisation mechanisms.** Ground reflection changes polarisation (H and V reflect differently; CP reflects with reversed hand above the Brewster angle — [two-ray-ground-reflection](two-ray-ground-reflection.md)); rain depolarises at mm-wave; Faraday rotation rotates linear polarisation on Earth–space paths below ~3 GHz ([ionospheric-hf-propagation](ionospheric-hf-propagation.md)) — irrelevant for rocket-to-ground. Nearby metal (airframe, fins, recovery hardware) couples into cross-polar components, so real rocket antennas radiate some cross-pol even end-on (filling the ideal null partially — measure it).

**Polarisation diversity.** Receiving on two orthogonal linear polarisations and combining (selection or maximal ratio) recovers the 3 dB that a single CP antenna gives away and avoids nulls: with MRC the combined PLF is 1 for any linear incoming polarisation. Crossed Yagis with a hybrid (RHCP/LHCP) or two receivers (H and V) are common in amateur satellite and high-altitude-balloon tracking stations.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| PLF = $\cos^2\Delta\tau$ | linear–linear | 30°: −1.25 dB; 60°: −6.0 dB; 85°: −21.2 dB |
| PLF = 1/2 | linear ↔ ideal CP | −3.01 dB, any tilt |
| AR formula (Poincaré) | general elliptical | 3 dB AR vs linear: −1.76…−4.76 dB |
| RHCP/LHCP isolation $20\log\frac{AR+1}{AR-1}$ | CP antenna | AR 3 dB → 15.3 dB |
| Dipole pattern $\sin^2\psi$ | axial dipole on rocket | ψ = 10°: −15.2 dB; 30°: −6.0 dB |
| Roll modulation: 2 nulls/rev | transverse linear antenna vs linear GS | 2 rev/s → 4 nulls/s |

## Worked examples
**1 — Choosing the ground antenna polarisation for the 433 MHz link.** Rocket: axial dipole (linear). Options: (a) vertical linear Yagi: 0 dB when aligned (most of the ascent), but nulls whenever the projected rocket axis is horizontal (pitch-over broadside, landed broadside); (b) crossed Yagi RHCP: constant −3 dB. With ~50 dB of nominal margin at 30 km ([link-budget-methodology](link-budget-methodology.md)), paying 3 dB for immunity is cheap; (c) dual-linear with two receivers and diversity: best of both (0 dB loss on the stronger branch, no nulls).

**2 — "CP" antenna with poor axial ratio.** A low-cost 433 MHz crossed Yagi measuring 6 dB axial ratio off boresight: a linear rocket signal sees −0.97 to −6.97 dB depending on orientation — still no deep null, but the budget should use −7 dB, not −3 dB.

**3 — GS placement.** A GS 0.5 km from the pad loses 15.7 dB of pattern during a vertical ascent to 3 km (ψ = 9.5°); moving it 2 km off-axis (ψ ≈ 29°) reduces that to 6.4 dB; 10 km downrange, 0.6 dB. Combined with plume attenuation at small look angles (tail-on view), a GS close behind the launch rail is the worst place to receive boost-phase telemetry.

**4 — Landed rocket orientation.** Body lying broadside to a vertical-linear GS antenna: the dipole's field is horizontal → cross-polarised with the GS (deep null) *and* horizontal polarisation near the ground suffers extra ground loss (H-pol minimum effective height ≈ 3 cm). Pointing at the GS: pattern null (−44 dB). Only intermediate orientations work with a linear GS; with a CP GS, broadside works (−3 dB) and end-on still fails. A deployable vertical whip or a second, orthogonal antenna on the recovery beacon fixes both.

## Practical notes
- **Verify the hand** of CP antennas (RHCP vs LHCP) — IEEE definition: clockwise rotation viewed from behind, looking in the direction of propagation, is RHCP. Mixing hands between two CP antennas costs 10–25 dB.
- **Measure axial ratio** with a rotating linear source antenna (the received power ratio max/min is AR²) — see [08-antennas/antenna-measurement](../08-antennas/antenna-measurement.md).
- **GNSS antennas are RHCP;** a linear antenna on a GNSS receiver costs ≈ 3 dB, and CP rejects ground-reflected (mostly LHCP above Brewster) multipath.
- **Log attitude and RSSI together** in flight to back out the installed pattern of the rocket antenna.

## Common mistakes & misconceptions
- **"Circular polarisation loses 3 dB so linear is better."** Linear–linear is 0 dB only when aligned; for a tumbling or tilting source it varies from 0 to > 20 dB. CP's fixed 3 dB is usually the better design choice for a moving source.
- **"A CP antenna gives 3 dB no matter what."** Only if its axial ratio is ~0 dB; real axial ratio (especially off boresight) makes it −1…−7 dB.
- **Treating the rocket's roll as the main polarisation problem** for an axial dipole — roll does nothing to an axisymmetric antenna; pitch and aspect angle (ψ) do.
- **Forgetting the pattern–polarisation coupling:** the same geometry that rotates polarisation also moves the observer into or out of the pattern null.
- **Wrong handedness conventions** between antenna datasheets (some use the optical/physics convention).

## How to simulate / verify
- `tools/verify/prop_polarization.py` — Jones-vector PLF, closed-form axial-ratio formula (verified to 10⁻¹⁵), special cases, rocket attitude geometry (ψ, pattern, PLF vs vertical-linear and CP ground antennas).
- NEC/openEMS models of the installed rocket antenna give co- and cross-polar patterns; convolve with the flight attitude history for a predicted RSSI trace ([08-antennas/antenna-simulation-nec-openems](../08-antennas/antenna-simulation-nec-openems.md)).
- Bench: rotate the rocket (or a mock-up) on a turntable 1–2 km from the GS antenna; record RSSI vs roll and pitch.

## Open questions / gaps
- The installed pattern (including cross-polar fill of the axial null) of the actual flight antennas is unknown — needs simulation/measurement (domain 08).
- Axial-ratio values of commercial 433/915 MHz crossed Yagis were not surveyed (domain 18).

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley 2016, §2.12 (polarisation, PLF, polarisation efficiency, Poincaré sphere). (textbook)
2. T. A. Milligan, *Modern Antenna Design*, 2nd ed., Wiley-IEEE 2005, ch. 1 (polarisation mismatch between elliptically polarised antennas, axial-ratio formula). (textbook)
3. W. L. Stutzman, *Polarization in Electromagnetic Systems*, 2nd ed., Artech House 2018 — Poincaré-sphere treatment of polarisation efficiency. (textbook)
4. IEEE Std 145-2013, *IEEE Standard for Definitions of Terms for Antennas* — handedness convention, axial ratio. (standard)
5. ITU-R P.531-13 §3.2 (Faraday rotation, XPD = −20 log tan Ω). (standard)
6. `tools/verify/prop_polarization.py` (this KB).
