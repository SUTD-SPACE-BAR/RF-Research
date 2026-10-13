---
title: Antennas on rockets — placement, airframe materials, axial nulls, roll, plume attenuation, recovery phase, ground-station choices
domain: 08-antennas
slug: antennas-on-rockets
tags: [rocket, telemetry, nose-cone, fibreglass, carbon-fibre, wraparound, blade-antenna, axial-null, roll, spin-modulation, plume-attenuation, recovery, ground-station, lora, gnss]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, antenna-polarization-and-circular-polarization.md]
related: [gnss-antennas.md, patch-antennas.md, yagi-uda-and-log-periodic.md, helical-antennas.md, antenna-matching-and-baluns.md, pcb-and-chip-antennas.md, ../02-electromagnetics/boundary-conditions-reflection-refraction.md, ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../15-lora-ism-radios/ground-station-design.md, ../20-projects-recipes/lora-rocket-telemetry-link.md, ../09-propagation-link-budget/link-budget-methodology.md, slot-antennas.md]
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Antennas on rockets

## Questions this page answers
- Where should I put the 433/915 MHz telemetry antenna on my rocket?
- Can I put the antenna inside a fibreglass nose cone? Inside a carbon-fibre or aluminium body tube?
- Why do I lose telemetry near apogee when the rocket is straight above the ground station?
- Why does the signal fade periodically when the rocket rolls?
- Should the ground station use a Yagi, a helix, or a crossed Yagi, and which polarization?
- Does the motor plume block the signal during boost?
- What happens to the link under the parachute and after landing?
- How much does a nose cone detune the antenna?
- What do professional sounding rockets use (wraparound, blade, quadraloop)?
- How do I keep the 2 W LoRa transmitter from deafening the GNSS receiver?

## TL;DR
- **Airframe material decides everything first.** Fibreglass, cardboard, phenolic and plastics are RF-transparent at UHF (a 2–3 mm fibreglass wall costs < 0.1 dB at 433–915 MHz and ≈ 0.1–0.2 dB at 1575 MHz; `tools/verify/em_fresnel_radome.py` from the 02 domain). **Carbon fibre is a conductor**: a 1 mm CFRP wall attenuates 433 MHz by ≈ 46–111 dB (σ 10³–3×10⁴ S/m) — the antenna must be outside or behind a fibreglass section. Aluminium is a perfect shield.
- **Every roll-symmetric antenna along the rocket axis has nulls at the nose and tail.** NASA's wraparound S-band telemetry antennas are "basically omni-directional, with nulls at the nose and tail" [1]. For a vertical rocket the ground station looks at the *aft* end: at 10 km altitude with the station 2 km from the pad the line of sight is only 11° off the axis → an axial dipole is ≈ **16 dB** below its broadside gain (`tools/verify/ant_rocket.py`).
- Link margins are nevertheless large for amateur altitudes in free space: 433 MHz, 2 W, axial dipole, 9 dBi ground Yagi, 10 km apogee, 2 km offset → ≈ −79 dBm received, ≈ 50 dB above LoRa SF9 sensitivity (2 W at 433 MHz needs an amateur licence or permit in Singapore; at the licence-exempt 10 mW e.r.p. the margin is ≈ 27 dB — still enough). The problems are **fades** (roll, pendulum, recovery orientation, terrain), not average path loss.
- **Roll**: a linear rocket antenna and a linear ground antenna produce two deep nulls per revolution. A **CP ground antenna** (helix, crossed Yagi, CP patch) removes them at a constant 3 dB cost; the residual effect is a frequency offset equal to the roll rate (harmless for LoRa). NASA's sounding-rocket ground stations use CP helices for the same reason [1].
- **Plume**: solid-motor exhaust (alumina particles, alkali-impurity ionization) attenuates RF when the line of sight passes close to the aft axis; flight data for the M-V second stage showed strong attenuation for look angles < 22° [2]. A ground station 1 km from the pad sees through that cone once the rocket is above ≈ 2.5 km — mostly after burnout for amateur motors, but plan for boost dropouts.
- **Detuning**: an antenna inside a nose cone or taped to a body tube is loaded by the dielectric within ~λ/2π; measure S11 *in the assembled airframe* and trim. openEMS predictions (2026-10, simulation only, not yet measured; [openEMS workflow Run 3/4c](../16-simulation-tools/openems-workflow.md)): a 3 mm G10 ogive pulls a λ/4 whip **−1.2 % at 915 MHz** and **−2.8 % at 433 MHz**; a conductive av-bay under the bulkhead moves it **+3.4 %**, more than the cone; and a printed IFA inside a fibreglass tube moved **up** (+0.7 %), so "always lower" is not a rule. Whip trim sensitivity at 915 MHz is **≈ 1.25 % per mm** (NEC).
- **Recovery**: under a parachute the airframe hangs roughly horizontal or swings; the axial antenna's null may point at the station, polarization rotates, and the ground-level path loses Fresnel-zone clearance. Expect the link to degrade in the last few hundred metres and after landing — carry a handheld Yagi for direction finding.
- **Coexistence**: keep the 433 MHz 2 W and 900 MHz 1 W antennas as far as practical from the GNSS antenna and use an active GNSS antenna with a SAW pre-filter; u-blox receivers are typically limited to ≈ −5 dBm at the RF input and need tens of dB of isolation from nearby transmitters [3].

## Intuition (no math)
A rocket is a long thin cylinder, and it flies (mostly) straight up and then comes down on a parachute. Almost any practical antenna that is symmetric around the rocket (a wire along the nose cone, a sleeve dipole, a wraparound strip, a pair of blades) radiates like a dipole aligned with the rocket's axis — a doughnut with holes at the nose and tail. That's perfect when the ground station is off to the side (early flight, long-range downrange flights) and bad when the rocket is nearly straight overhead (high vertical flights with a nearby ground station), because then the station is looking up the rocket's tail — into the hole in the doughnut and, during the burn, through the exhaust.

Rocket rotation (roll) spins a linear antenna's polarization; a fixed linear ground antenna then fades twice per revolution. Circular polarization on the ground makes the link immune to the rocket's roll angle.

The airframe material is either invisible (fibreglass, cardboard), a small detuning influence (thick fibreglass, 3D-printed plastics), or a Faraday cage (carbon fibre, aluminium). Any metal in the avionics bay — threaded rods, batteries, the flight computer's ground plane, pyro wiring — becomes part of the antenna if it is within a fraction of a wavelength of it.

## The math

### Level 1 — look angle and pattern loss
For a vertical rocket at altitude h and horizontal distance d from the ground station, the angle between the rocket's aft axis and the line of sight is θ = arctan(d/h). A λ/2 dipole along the axis has relative pattern F(θ) = cos(π/2·cosθ)/sinθ, i.e. gain G(θ) = 2.15 dBi + 20 log F(θ). From `tools/verify/ant_rocket.py`:

| Altitude | Offset 0.5 km | 2 km | 5 km | 15 km |
|---|---|---|---|---|
| 1 km | 26.6° → −8.7 dB | 63.4° → −1.4 dB | 78.7° → −0.2 dB | 86° → 0 dB |
| 3 km | 9.5° → −17.7 dB | 33.7° → −6.6 dB | 59° → −1.9 dB | 79° → −0.2 dB |
| 10 km | 2.9° → −28 dB | 11.3° → −16.2 dB | 26.6° → −8.7 dB | 56° → −2.2 dB |
| 30 km | 1.0° → −38 dB | 3.8° → −25.6 dB | 9.5° → −17.7 dB | 26.6° → −8.7 dB |
(angle from aft axis → loss relative to broadside)

### Level 2 — link budget with the null, and why it still usually closes
Received power: P_r = P_t + G_t(θ) + G_r − L_pol − FSPL − L_misc, FSPL = 20 log(4πRf/c) ([Friis](../09-propagation-link-budget/friis-free-space-path-loss.md)). Script results (2 dB miscellaneous loss, LoRa SF9/125 kHz sensitivity ≈ −129 dBm for SX126x-class receivers — see [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)):

| Radio | Geometry (h, d) | G_t | 9 dBi linear Yagi (aligned) | 9 dBic CP (−3 dB) |
|---|---|---|---|---|
| E22-400T33D, 433 MHz, 33 dBm | 3 km, 1 km | −9.7 dBi | −64.9 dBm (64 dB margin) | −67.9 dBm |
| same | 10 km, 2 km | −14.0 dBi | −79.4 dBm (50 dB) | −82.4 dBm |
| same | 30 km, 5 km | −15.6 dBi | −90.4 dBm (39 dB) | −93.4 dBm |
| E220-900T30D, 915 MHz, 30 dBm | 10 km, 2 km | −14.0 dBi | −88.9 dBm (40 dB) | −91.9 dBm |
| same | 30 km, 5 km | −15.6 dBi | −99.9 dBm (29 dB) | −102.9 dBm |

*Yagi gain note (2026-10-14):* the 9 dBi column is the script's assumption. A buildable 3-element Yagi fed directly from 50 Ω (F/B ≥ 15 dB, VSWR ≤ 1.5 across the band) is ≈ 8.5 dBi in NEC ([NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md)), so subtract ≈ 0.5 dB from every margin; none of the conclusions change.

*Licence note (Singapore):* the 33 dBm / 30 dBm rows are licensed-power cases. At the licence-exempt 433 MHz limit (10 mW e.r.p. ⇒ ≈ 10 dBm conducted into this dipole, whose peak gain is 2.15 dBi) every E22 row drops by 23 dB — margins 41 / 27 / 16 dB; the E220 at 866–869 MHz (TS SRD 29, 500 mW e.r.p., no duty limit stated; CH 17/18 at the 24 dBm step ≈ 23.5 dBm e.r.p. after 0.5 dB of cable) drops by only ≈ 6 dB (34 / 23 dB) — the KB's preferred licence-exempt E220 band ([15 band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)). At the 917–925 MHz LoRa limit (100 mW e.r.p. ⇒ the 21 dBm step plus a ≥ 1 dB pad) it drops by 10 dB (30 / 19 dB) and is also limited to 1 % duty, which cannot carry 10 Hz telemetry (even a 20.5 ms SF7/500 frame at 10 Hz is 20 % duty) ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md), [LoRa link budget Example 3](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md#worked-examples)).

So in free space even the null leaves tens of dB of margin at amateur altitudes. Margin is consumed by: polarization fades with linear-linear links (up to −20…−30 dB), the pattern's *exact* null (the axial dipole's F(θ) → 0 as θ → 0; real bodies fill it only partly), pointing errors of a narrow ground antenna (an 11-element Yagi is −3 dB at ±18°), multipath near the ground, and plume attenuation during boost. Use the margin to choose **faster LoRa settings or a broader ground antenna**, not to ignore these effects. Full methodology: [link budget](../09-propagation-link-budget/link-budget-methodology.md), [margin and availability](../09-propagation-link-budget/link-margin-availability.md).

**Why roll-symmetric antennas have axial nulls (duality argument).** Any radiator whose currents are rotationally symmetric about the rocket axis (an axial wire; a circumferential slot or wraparound microstrip, which is equivalent to a ring of circumferential *magnetic* current) produces a field with no φ variation. By symmetry, on the axis the field would have to point in every transverse direction at once, so it must vanish there: an axisymmetric (m = 0) radiator always has nulls fore and aft. Filling the aft direction requires breaking the symmetry — a transverse dipole, a turnstile, a patch facing aft, or an array phased for aft coverage (NASA's "quadraloop" command antennas are phased "maximally aft or maximally broadside" [1]).

### Level 3 — fields around the airframe, plume, and spin
- **Conductive body as part of the antenna.** A monopole on the end of a metal (or CF) body tube excites currents on the entire airframe, which becomes a long, asymmetric dipole: at 433 MHz a 1.5 m airframe is 2.2λ long, so the pattern develops multiple lobes and nulls along the axis direction rather than a simple doughnut. Model with openEMS (full body) or NEC (wire-grid cylinder) before flight if the airframe is conductive.
- **Wall transmission and detuning.** Thin dielectric walls reflect little (normal-incidence |Γ|² < 1 % for fibreglass up to 6 mm at 433 MHz and 2.8 mm at 915 MHz; [radome analysis in 02](../02-electromagnetics/boundary-conditions-reflection-refraction.md)). The larger effect is loading of the reactive near field: resonances shift down by a few percent (more for thick walls, close spacing, high εr such as wet or conductive-filled composites). Treat any published number as a starting point and measure in situ.
  - *Simulated magnitudes* (openEMS, `tools/verify/sim2_openems_nosecone.py`, 3-mesh study, MUR/PML/large-box checks; [openEMS workflow Run 3](../16-simulation-tools/openems-workflow.md)): 4:1 ogive, 50 mm inner radius, 3 mm wall, εr 4.7, 100 mm bulkhead disc → 78 mm whip **−1.2 %** (935 → 924 MHz), 165 mm whip **−2.8 %** (498 → 484 MHz; the small disc puts it 15 % above 433 MHz before any cone). An εr 4.0 laminate gives 0.92× the shift (pre-registered ≈ 0.8×; missed). A 250 mm conductive av-bay tube below the disc moves the bare whip **+3.4 %**, and the cone then pulls it −1.7 %. The ground system is the bigger unknown.
  - *The sign is antenna-dependent*: an 88 mm printed IFA on a 100 × 40 mm board inside a fibreglass tube moved its best match **+0.7 %** (`tools/verify/sim2_openems_pcb.py`, Run 4c). This was **opposite to the pre-registered downward shift**: the IFA never reaches X = 0 (X ≈ +28 Ω) and the tube's capacitance cancels ~4 Ω of it. A non-resonant (reactive) antenna can move either way; measure.
  - Efficiency and directivity from these openEMS runs are boundary-dependent and are **not** reported as results.
- **Carbon fibre.** CFRP in-plane conductivity 10³–3×10⁴ S/m at UHF (DC values up to ~4×10⁴) gives skin depths of 0.14–0.77 mm at 433 MHz; 1 mm walls transmit −46 to −111 dB (02 domain script). Some "carbon-look" tubes are black fibreglass (RF-transparent) — test with a handheld radio inside the tube [4].
- **Plume attenuation.** Solid propellants with aluminium produce hot alumina particles and an ionized exhaust (free electrons from alkali impurities such as Na and K); the plasma's electron density can exceed the critical density for UHF near the nozzle, and the plume attenuates and diffracts signals whose path passes close to it. Kinefuchi et al. matched M-V flight data (P-band) with a CFD + frequency-dependent FDTD (Drude plasma) model and found strong attenuation at look angles below ≈ 22° from the aft axis, little at larger angles, and weak dependence on altitude/velocity in their range [2]. For amateur APCP motors, published measurements are scarce; forum reports of telemetry dropouts during burn are common but anecdotal. Treat the < 20–25° aft cone during burn as unreliable.
- **Spin modulation.** With CP ground reception, a rotating linear transmitter produces a phase ramp = roll angle, i.e. a frequency offset f_roll (verified: 5 rev/s → 5 Hz). With linear reception, amplitude fades as cos²(roll angle). Coning/pendulum motion under a parachute adds slower fades.

## Antenna options on the vehicle

| Option | Pattern | Pros | Cons | Fits |
|---|---|---|---|---|
| λ/4 wire/whip up a fibreglass nose cone over a bulkhead ground | axial doughnut, nulls fore/aft | simple, efficient if ground is decent | needs a ground (bulkhead plate, radials); detunes; tail null | 433/915 MHz, nose ≥ 20 cm |
| Sleeve dipole / centre-fed dipole with choke along the axis | axial doughnut | no ground needed; predictable | length λ/2 (≈ 33 cm at 433 MHz); tail null | fibreglass sections |
| External whip / blade on the fin can or body | ≈ doughnut + body effects | works on CF/metal airframes | drag, damage on landing, flutter; body currents | CF/metal airframes |
| Two blades 180° apart fed in phase | roll-omni-ish (ripple from interference) | classic sounding-rocket choice | feed network | metal airframes |
| Wraparound microstrip (conformal band) | roll-omni, nulls fore/aft, linear polarization along the axis | flush, robust, supersonic-friendly | design effort, narrowband; needs airframe diameter/band trade | 915 MHz+ (and 433 MHz on large airframes) |
| Crossed dipoles / turnstile perpendicular to the axis (in the nose cone or on a bulkhead) | maximum fore/aft, CP along the axis | fills the tail null (good near apogee for a nearby station) | nulls/weak toward broadside for one sense; feed complexity | combine with an axial antenna (diversity) |
| Patch on an aft- or forward-facing bulkhead behind a dielectric window | hemispherical | GNSS (up) or tail coverage (down) | points the wrong way after apogee/under chute | GNSS during ascent |

Professional practice: NASA's S-band wraparound telemetry antennas (4–22 in diameter, 4–6¾ in axial length) are linearly polarized, "basically omni-directional, with nulls at the nose and tail"; the GPS system uses an L1 wraparound antenna with preamplifier; command uplinks at 437.5 MHz use four-element "quadraloop" antennas phased for circular polarization and aft or broadside coverage; ground stations use selectable RHCP/LHCP helices [1]. Student-rocket work (ITA, Brazil) used a flush circumferential microstrip array on the vehicle and a truncated-corner CP patch at the ground station [5].

## Design equations & rules of thumb

| Rule | Value |
|---|---|
| Look angle from aft axis | θ = arctan(d/h) |
| Keep θ ≥ 30° at apogee (axial antenna) | ground offset d ≥ 0.58h (→ −6 dB or better) |
| Plume cone (solid motors, boost) | avoid LOS within ≈ 20–25° of aft axis during burn |
| Fibreglass wall 2–3 mm | < 0.1 dB at 433–915 MHz, ≈ 0.1–0.2 dB at 1.6 GHz |
| CFRP wall 1 mm | −46 to −111 dB at 433 MHz (σ 10³–3×10⁴ S/m): antenna outside |
| Keep metal away from the antenna | ≥ λ/10 (69 mm @433 MHz, 33 mm @915 MHz) from threaded rods, batteries, boards, except intended ground |
| CP ground antenna | costs 3 dB vs aligned linear; removes roll fades |
| Roll-induced offset (CP RX) | = roll rate in Hz |
| Trim in situ | λ/4 whip in a 3 mm G10 cone: −1.2 % (915 MHz), −2.8 % (433 MHz); conductive av-bay +3.4 %; IFA in a tube +0.7 % (openEMS predictions, unmeasured) |
| Whip trim sensitivity | Δf/f ≈ ΔL/L: ≈ 1.25 %/mm on a 78 mm 915 MHz whip (NEC 77/78/79 mm → 900.3/889.0/878.0 MHz); ≈ 0.6 %/mm on a 165 mm 433 MHz whip |

## Worked examples

**Example 1 — Avionics-B-style 433 MHz link, 3 km flight, station 1 km from the pad.** Rocket: λ/4 whip up the fibreglass nose cone over a 100 mm aluminium bulkhead disc (a small ground: expect Z ≈ 20–35 Ω and a few dB less than ideal; add radials along the cone wall or use a sleeve dipole). At apogee θ = 18.4°, G_t ≈ −9.7 dBi. Ground: 3-element handheld Yagi (≈ 8.5–9 dBi, 59° × 84° beam — easy to hand-point; 9.15 dBi needs a matched ≈ 11 Ω feed, while a directly 50 Ω-fed design held to F/B ≥ 15 dB and VSWR ≤ 1.5 across 433.05–434.79 MHz reaches 8.55 dBi in NEC — [NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md), `tools/verify/sim2_nec_yagi_optimise.py`; this page previously said 9 dBi, ≈ 0.5 dB optimistic for a buildable design). Result ≈ −65 dBm: huge margin; the risks are polarization (keep the Yagi elements vertical, or better, use CP), and the boost-phase plume (the LOS enters the 22° cone above 2.5 km — near burnout for many motors).

**Example 2 — High-altitude flight (30 km) with a nearby station.** θ = 9.5° at 5 km offset → −17.7 dB from the axial antenna; with a linear ground antenna and roll, fades can reach −40 dB total. Options, in order of effectiveness: (1) move the ground station farther downrange/offset (d = 17 km gives θ = 30°), (2) CP ground antenna (helix ≈ 12–13 dBic, [helical-antennas](helical-antennas.md)), (3) add a turnstile (transverse crossed dipoles) in the nose cone combined with the axial whip through a splitter — or two radios — to fill the tail null, (4) lower LoRa spreading factor only after these.

**Example 3 — Nose-cone detuning check.** A 915 MHz λ/4 whip trimmed to 78 mm on the bench resonates lower inside a 3 mm fibreglass cone with 50 mm inner radius. openEMS predicts **−1.2 % (≈ 11 MHz)** for a G10 ogive over a 100 mm bulkhead (`tools/verify/sim2_openems_nosecone.py`; simulation-informed, to be measured), i.e. about one millimetre of trim; the counterpoise (av-bay, coax, wiring) can move it by +3 % or more. Procedure: assemble the nose cone and bulkhead, connect the NanoVNA through the actual coax, sweep 800–1000 MHz, trim the whip in 1 mm steps (**≈ 1.25 % ≈ 11 MHz each** at 915 MHz — NEC, 77/78/79 mm → 900.3/889.0/878.0 MHz; this example previously said ≈ 0.6 %, which is the figure for a 165 mm 433 MHz whip) until S11 is minimum at 915 MHz. For finer control, trim 0.5 mm at a time near the end; re-check with the flight battery and wiring installed. Record the final length in the build log (record-everything ethos).

**Example 4 — Carbon-fibre airframe.** Per Altus Metrum, CF or metal electronics bays need an SMA/edge connector and coax to an antenna outside the conductive section [4]. Options: a fibreglass coupler or nose cone housing the antenna; a flush blade on the fin can (watch fin flutter and landing damage); or a conformal antenna on a fibreglass band ("RF window") in the CF body. GNSS also needs the window (L1 through 1 mm CF: > 100 dB loss).

**Example 5 — Recovery phase.** Under a main parachute at 300 m altitude, 3 km away, the airframe hangs roughly horizontal and swings; if the axial antenna happens to point at the station, the pattern null and the ground-level geometry (Fresnel zone at 433 MHz over 3 km: first-zone radius ≈ 23 m at mid-path, [Fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)) combine. After landing, the ground-level antenna has a very poor path — typical ranges shrink to hundreds of metres to a few km. Transmit the last GNSS fix repeatedly during descent, and walk the last part with a handheld Yagi (RDF by peak or by the rear null).

## Practical notes
- **Mechanical**: whips must survive boost acceleration (tens of g), vibration and landing. Use spring-steel or nitinol; strain-relieve the feed; U.FL connectors need a retention clip or adhesive and are rated for few mating cycles; SMA with thread-locker for flight.
- **Heating**: at high supersonic speeds, nose and leading-edge temperatures rise; PTFE-based substrates and ceramic windows are preferred over FR-4/PLA for conformal antennas on fast vehicles (sounding-rocket antennas offer "varying degrees of thermal protection" [1]).
- **Coax routing**: route the feed coax along the axis (not across the antenna) and put a ferrite choke on it at the antenna base; otherwise the coax becomes part of the antenna and the pattern depends on the wiring harness ([baluns](antenna-matching-and-baluns.md)).
- **Pyro and ESD safety**: a 2 W transmitter near pyro wiring can induce RF currents; range safety rules require documenting transmitting-antenna locations relative to pyrotechnics (NASA handbook requirement [1]). Twist pyro leads, keep them short and away from the antenna, test with the transmitter on (see [19-regulations-safety](../19-regulations-safety/lab-safety-esd-high-power.md)).
- **Coexistence with GNSS**: separate the LoRa antenna and GNSS antenna by the length of the vehicle if possible; the GNSS front end needs its SAW filter; check GNSS C/N₀ with the transmitter keyed on the pad ([gnss-antennas](gnss-antennas.md)).
- **Pre-flight test**: range test with the complete rocket on its side at several roll angles and with a person holding the ground antenna as in flight; record RSSI/SNR (HIL/bench discipline, record everything).
- **Two antennas fed with the same signal** form coherent nulls; switching or Alamouti coding avoids them — see [10 MIMO § Example 7](../10-comms-modulation/mimo-capacity-and-channel-estimation.md#example-7--two-antennas-on-the-rocket-same-signal-switching-or-alamouti).

## Common mistakes & misconceptions
- **"Fibreglass blocks RF."** Thin fibreglass is nearly transparent at 433–915 MHz; it detunes more than it attenuates. (u-blox notes a fibreglass airfoil *attenuates GNSS* — at 1.6 GHz and with thicker/wet laminate the loss grows [3].)
- **"Black tube = carbon = no signal."** Some black tubes are fibreglass; test it.
- **"More ground-station gain fixes apogee dropouts."** Dropouts near apogee are usually the axial null + polarization + pointing; a broader, CP antenna often does better than a bigger linear Yagi.
- **"The rocket is far away, so the pattern doesn't matter."** The pattern term (−16 to −38 dB near the axis) can exceed the path-loss difference between 3 km and 30 km (20 dB).
- **"It worked on the bench, so it works in the airframe."** Bench tuning ignores the nose cone, bulkhead, battery and wiring.
- **"Circular polarization on the rocket solves everything."** CP on the vehicle is hard to make omnidirectional; the usual professional answer is linear (roll-omni) on the vehicle and CP on the ground [1].
- **Forum-reported** (rocketryforum.com, r/rocketry — anecdotal): telemetry loss during motor burn; dead links from antennas routed alongside all-thread; LoRa modules detuned by being taped against the battery.

- **"An antenna taped to the inside of a carbon (or metal) tube still works."** Carbon fibre acts as a lossy conducting sheet: a dipole 0.02λ (14 mm at 433 MHz) from a conducting surface has R ≈ 0.9 Ω and ≈ 30 % efficiency even with only 2 Ω of other loss (MoM, `tools/verify/ant2_qa.py` §d) — and inside a closed conducting tube it is shielded anyway. Put the antenna in a fibreglass section or outside, or make the metal airframe radiate with a **slot or circumferential gap** ([slot antennas](slot-antennas.md#slot-in-a-ground-plane--enclosure-wi-fi-in-metal-laptops-metal-airframes)).

## How to simulate / verify
- `python3 tools/verify/ant_rocket.py` — look-angle/pattern-loss table, link budgets for the reader's radios, plume-cone altitudes.
- `python3 tools/verify/em_fresnel_radome.py` (02 domain) — wall insertion loss for fibreglass and carbon fibre.
- `python3 tools/verify/ant_polarization.py` — roll fades with linear vs CP ground antennas.
- Full-wave: openEMS model of the nose cone (dielectric shell), bulkhead ground and whip for resonance shift and pattern; NEC wire-grid cylinder for a conductive airframe ([simulation](antenna-simulation-nec-openems.md)). Ready-made: `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_nosecone.py` (whip + cone + bay cases, pre-registered) and `tools/verify/sim2_openems_pcb.py` (IFA free / in tube) — results in [openEMS workflow Runs 3 and 4c](../16-simulation-tools/openems-workflow.md). Use them for f_res and S11 only; their NF2FF gain is not yet trustworthy.
- Field: NanoVNA S11 in the assembled airframe; RSSI vs roll angle on the ground with the rocket horizontal on a turntable (a DIY pattern range — [antenna measurement](antenna-measurement.md)).

## Open questions / gaps
- No quantitative amateur-motor (APCP) plume attenuation data at 433/915 MHz was found; the 22° figure is from a large professional motor at P-band. A flight experiment (RSSI log vs look angle during burn) would fill this.
- Nose-cone detuning has now been **simulated** for a representative cone (openEMS 2026-10: −1.2 % / −2.8 % / bay +3.4 % / IFA +0.7 %) but not **measured**, and not for the team's actual cone and bulkhead (their geometry is not recorded). A NanoVNA bench-vs-assembled sweep would test the prediction ([validation campaign](../20-projects-recipes/validation-test-campaign.md)).
- The DTIC report "Wraparound antenna for S-band telemetry" (AD1105046) and ITC papers on wraparound design were not accessible (403); an ITC (International Telemetering Conference) proceedings sweep is recommended for a later wave.

## Sources
1. NASA GSFC Wallops, *NASA Sounding Rockets User Handbook*, 810-HB-SRP, July 2015 — §5.6 Telemetry Antennas (S-band wraparound microstrip, linearly polarized, omni with nulls at nose and tail; quadraloop command antennas phased for CP and aft/broadside coverage; CP helix ground antennas; radar transponder CP helices 180° apart), §5.9.3 GPS wraparound antenna; range-safety documentation of transmitter antennas vs pyros. https://www.nasa.gov/wp-content/uploads/2023/09/sounding-rocket-program-handbook.pdf (government handbook)
2. K. Kinefuchi, K. Okita, I. Funaki, T. Abe, "Prediction of in-flight radio frequency attenuation by a rocket plume," *J. Spacecraft and Rockets* 52(2), 2015 — M-V 2nd stage, P-band, strong attenuation below ≈ 22° look angle; CFD + FD²TD (Drude). https://arc.aiaa.org/doi/10.2514/1.A32957 (peer-reviewed; abstract level)
3. u-blox UBX-15030289, *GNSS antennas* app note — "fiberglass airfoil attenuates the GNSS signal"; receiver input limits and interference/isolation guidance. (app note)
4. Altus Metrum owner's manual — λ/4 wire to the nose; carbon fibre/metal bays are RF-opaque, use SMA + external antenna; some "carbon" is black fibreglass; handheld Yagis for recovery. https://altusmetrum.org/AltOS/doc/altusmetrum.html (manufacturer manual)
5. P. C. Ribeiro Filho, A. F. Tinoco-S., D. C. Nascimento, J. C. da S. Lacava, "A telemetry antenna design for a sounding rocket competition," *IEEE Antennas Propag. Mag.* 59, 2017; and "Flush-mounted telemetry antenna design for a sounding rocket competition," IEEE APS 2013. (peer-reviewed; abstract level)
6. 02-electromagnetics pages in this KB: [boundary conditions / radome](../02-electromagnetics/boundary-conditions-reflection-refraction.md) and [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md) with `tools/verify/em_fresnel_radome.py` — fibreglass and CFRP wall numbers used above. (KB cross-reference)
7. This repository: `tools/verify/ant_rocket.py`, `tools/verify/ant_polarization.py`, `tools/verify/ant_dipole.py`. (verification)
