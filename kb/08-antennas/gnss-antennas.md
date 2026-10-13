---
title: GNSS antennas — RHCP patches and helices, active antennas, ground planes, axial ratio, phase centre, multipath, and GNSS on rockets
domain: 08-antennas
slug: gnss-antennas
tags: [gnss, gps, galileo, beidou, glonass, rhcp, ceramic-patch, stacked-patch, helix, qfh, active-antenna, lna, saw, ground-plane, axial-ratio, phase-centre, multipath, zed-f9p, max-m10s, rtk]
prerequisites: [antenna-fundamentals.md, patch-antennas.md, antenna-polarization-and-circular-polarization.md, ../07-noise-linearity/noise-figure-and-friis.md]
related: [helical-antennas.md, antennas-on-rockets.md, pcb-and-chip-antennas.md, small-antenna-limits.md, ../20-projects-recipes/gnss-front-end-design.md, ../06-rf-circuits/lna-design.md, ../07-noise-linearity/receiver-cascade-analysis.md]
level: mixed
confidence: high
last_updated: 2026-10-03
---

# GNSS antennas

## Questions this page answers
- Why are GNSS antennas right-hand circularly polarized?
- Patch or helix — which should I use for GPS/Galileo on a flight computer or a rocket?
- What does an "active antenna" add, and how much LNA gain do the ZED-F9P and MAX-M10S want?
- Why does my GNSS patch perform badly on a small board, or inside a rocket body?
- How big should the ground plane be?
- What are axial ratio and phase-centre variation, and why do RTK users care?
- What bands do L1/L2/L5 and E1/E5b/B1/B2 occupy, and does my antenna cover them?
- Why does my GNSS lose satellites when the LoRa transmitter keys up?
- Is a chip antenna good enough for GNSS?

## TL;DR
- GNSS signals are **RHCP** and extremely weak: the GPS L1 C/A minimum is −158.5 dBW (−128.5 dBm) for a 3 dBi *linear* antenna (≈ a 0 dBic RHCP antenna) — ≈ 15 dB below the thermal noise in the signal bandwidth [5], [6]. CP makes reception independent of the satellite's orientation and rejects once-reflected (LHCP) multipath.
- **Ceramic patch** (25 × 25 mm typical, ≈ 2–5 dBic at zenith on a suitable ground plane) is the default for sky-facing installations; **helix/QFH** types give broad, orientation-tolerant coverage and need little ground plane; **chip and PCB-trace antennas** are linear, lose ≈ 3 dB to polarization and are "not recommended where navigation is essential" (u-blox [6]).
- **Ground plane matters** for patches: u-blox recommends ≈ 50 × 50 to 70 × 70 mm for L1 ceramic patches (gain, AR and centre frequency all change with ground size; one 25 mm patch had AR ≈ 10 dB on a 100 mm ground) [6]; the ZED-F9P multiband antenna spec assumes a **150 mm** ground and asks for **≥ 100–150 mm** for patch antennas [7].
- **Active antennas**: ZED-F9P *requires* one — total gain 17–50 dB including cable losses (ideal 30–40 dB), NF < 4 dB (system ≈ 3 dB), group-delay variation ≤ 10 ns per band, element gain ≈ 3 dBic (L1) / 2 dBic (L2/L5), AR ≤ 2 dB at zenith, PCV < 10 mm, ESD protection mandatory [7]. The MAX-M10S has an internal LNA and SAW filter and works with passive antennas; with an active antenna use its low-gain/bypass LNA mode [8].
- An LNA at the antenna fixes *cable* loss; it cannot recover signal lost by a small, detuned or badly placed radiator (u-blox: "no magic" [6]). Example (this page): passive 3 dBic patch + 3 dB cable → T_sys ≈ 965 K (C/N₀ ≈ 43 dB-Hz at the minimum signal); active antenna (28 dB, NF 2 dB) + 5 dB cable → ≈ 272 K (≈ 49 dB-Hz).
- **GNSS inside a rocket fails** for predictable reasons: conductive airframe (CFRP: ≈ 50–160 dB for 1 mm at L1, σ 10³–3×10⁴ S/m; Al: total), a ground plane much smaller than specified (detuning, AR degradation), patch facing the wrong way (sideways/downward, or rotating with roll under the parachute), dielectric loading by a nose-cone wall right on top of a narrowband ceramic patch, and desensing by the 1–2 W telemetry transmitter.

## Intuition (no math)
A GNSS satellite is 20 000 km away and transmits tens of watts; by the time the signal arrives, the power flux is ~10⁻¹⁴ W/m² ([antenna fundamentals example 2](antenna-fundamentals.md#worked-examples)). The receiver finds it below the noise by correlating against the known code, gaining ~40–60 dB. So every decibel of antenna gain, polarization match and low noise near the antenna is precious, and interference barely above the noise floor is enough to jam it.

The satellites transmit RHCP so that the signal arrives with the same polarization whatever the satellite's attitude and whatever path through the ionosphere (which rotates linear polarization). A reflection off the ground or a building mostly turns RHCP into LHCP, which an RHCP antenna rejects; a linear antenna would accept both the direct and reflected signals equally.

A ceramic patch is a small, high-permittivity resonator. It is efficient and has a nice upward hemispherical beam, but it is narrowband (a few MHz to ~20 MHz) and its resonance, axial ratio and gain depend on the ground plane under it and on anything in its near field. Put it on a different-size ground, behind a radome or near a battery, and it drifts off 1575 MHz.

## The math

### Level 1 — bands and signal levels
| System / signal | Centre (MHz) | Band used by u-blox F9 (MHz) [7] | Notes |
|---|---|---|---|
| GPS L1 C/A, L1C; Galileo E1; BeiDou B1C; QZSS L1 | 1575.42 | 1573–1578 (C/A); E1/B1C wider in principle | MAX-M10S, ZED-F9P |
| BeiDou B1I | 1561.098 | 1559–1563 | |
| GLONASS L1OF | 1602 + k·0.5625 | 1598–1606 | FDMA |
| GPS L2C; QZSS L2C | 1227.60 | 1223–1231 | ZED-F9P-01B/02B/04B/05B |
| GLONASS L2OF | 1246 + k·0.4375 | 1242–1249 | |
| Galileo E5b; BeiDou B2I | 1207.14 | 1192–1212 | ZED-F9P (L1/L2 variants) |
| GPS L5; Galileo E5a; BeiDou B2a | 1176.45 | 1166–1186 | ZED-F9P-15B |

Minimum received power (IS-GPS-200 [5]): L1 C/A −158.5 dBW ≈ −128.5 dBm for a 3 dBi linear (≈ 0 dBic) antenna at ≥ 5° elevation; typical real levels are a few dB higher. Carrier-to-noise density C/N₀ = P_r − 10 log₁₀(k T_sys) (dBm − dBm/Hz = dB-Hz), with 10 log k·290 K = −174 dBm/Hz. Good open-sky tracking: 40–50 dB-Hz; ZED-F9P RTK wants > 40 dB-Hz average [7].

### Level 2 — the front-end noise cascade
With antenna noise temperature T_A (≈ 50–150 K for an upward patch: cold sky plus some warm ground in back lobes and losses), a lossy line of loss L (linear) at T₀ = 290 K, then a receiver of noise temperature T_R:
$$T_\text{sys} = T_A + (L-1)T_0 + L\,T_R\quad(\text{passive}),\qquad T_\text{sys}\approx T_A + T_\text{LNA} + \frac{(L-1)T_0+L T_R}{G_\text{LNA}}\quad(\text{active}).$$
Worked numbers (T_A = 100 K, T_R for NF 3 dB = 289 K; signal = minimum spec into a 3 dBic antenna = −125.5 dBm):

| Configuration | T_sys | C/N₀ at minimum signal |
|---|---|---|
| Passive patch, 3 dB of coax to a NF 3 dB receiver | 965 K | 43.3 dB-Hz |
| Passive patch, 0.3 dB trace to an internal LNA of NF 1.5 dB (MAX-M10S-style, assumed NF) | 249 K | 49.1 dB-Hz |
| Active antenna (LNA 28 dB, NF 2 dB), 5 dB coax, NF 3 dB receiver | 272 K | 48.8 dB-Hz |

This is why u-blox advises an active antenna whenever the cable exceeds ≈ 10 cm, notes 15 dB of LNA gain is usually enough for cables up to 5 m with receivers that also accept passive antennas, and warns that > 35 dB with short cables can overload some receivers [6]. See [noise figure and Friis](../07-noise-linearity/noise-figure-and-friis.md) and [receiver cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md).

### Level 3 — pattern, axial ratio, multipath and phase centre
- **Elevation pattern.** A patch on a finite ground has its maximum at zenith and falls to roughly −5 to −10 dB at 10° elevation; the ground-plane edge diffraction shapes the low-elevation response and creates a back lobe (sensitivity to ground reflections) — larger ground → smaller back lobe [6].
- **Axial ratio vs elevation.** Good at zenith (spec ≤ 2 dB for F9P antennas [7]), worse toward the horizon; low-elevation AR degradation lets LHCP multipath in (a 6 dB AR only rejects the opposite sense by 9.5 dB — see [polarization](antenna-polarization-and-circular-polarization.md#design-equations--rules-of-thumb)).
- **Multipath rejection hardware**: choke rings (concentric λ/4-deep grooves that suppress surface currents and low-angle response), large ground planes, pinwheel/multipath-limiting antennas — used for geodetic/RTK base stations [6].
- **Phase-centre variation (PCV).** The "electrical" point from which the carrier phase appears to originate moves with elevation/azimuth and differs between L1 and L2. For RTK the rover and base should use calibrated or identical antennas; the F9P spec asks for PCV < 10 mm [7].
- **Group delay.** Multiband receivers combine code/phase across bands; filters and LNAs must keep in-band group-delay variation ≤ 10 ns (inter-signal ≤ 50 ns) [7].
- **Stacked patches** (an L1 ceramic patch over an L2/L5 patch, common feed or two probes) provide low-cost dual-band RHCP [7].

## Antenna types compared

| Type | Pol. | Typical gain | Ground plane | Pros | Cons |
|---|---|---|---|---|---|
| Ceramic patch 25 × 25 × 4 mm | RHCP | 2–5 dBic (on 50–70 mm ground) | required, sized | cheap, efficient, good upward pattern | narrowband; detunes with ground/radome; back lobe with small ground |
| Ceramic patch 12–18 mm | RHCP | −3 to +2 dBic | required | small | "moderate navigation performance" below 17 mm [6] |
| Stacked L1/L2 patch (ANN-MB class) | RHCP | ≈ 3 / 2 dBic | 100–150 mm | RTK-capable | size, needs ground |
| Helix / QFH (air or ceramic loaded) | RHCP | 0–3 dBic, broad | little/none (a ground can add 2–3 dB [6]) | orientation tolerant, robust | size (air: ~60 × 45 mm), tolerance-sensitive; more multipath at low angles |
| Chip antenna | linear | ≈ −3 to 0 dBic effective | very sensitive, keep-out ~5 mm | tiny | −3 dB polarization loss, pattern depends on board |
| PCB strip / dipole / FEA | linear | −1 to +2.5 dBic (FEA vs ground) | depends | cheap | not for navigation-critical use [6] |
| Choke-ring / MLA geodetic | RHCP | 5–8 dBic | built in | best multipath and PCV | large, heavy, costly |

## Design equations & rules of thumb

| Item | Rule / value | Source |
|---|---|---|
| Ceramic L1 patch ground | 50 × 50 to 70 × 70 mm | u-blox [6] |
| Multiband patch ground | ≥ 100–150 mm diameter | u-blox F9P [7] |
| Patch size | 25 mm optimal; < 17 mm moderate | [6] |
| Active antenna gain (F9P) | 17–50 dB incl. cable; ideal 30–40 dB | [7] |
| System NF | ≈ 3 dB total; antenna LNA NF < 4 dB | [7] |
| Antenna element | 3 dBic L1, 2 dBic L2/L5, AR ≤ 2 dB zenith, PCV < 10 mm | [7] |
| Use active antenna when | cable > ~10 cm | [6] |
| Max RF input (typical) | ≈ −5 dBm absolute at the receiver input (check the datasheet) | [6] |
| Isolation to a nearby transmitter | plan ≥ 40 dB for watt-level transmitters; add a SAW filter | [6] (GSM example) |
| Chip antenna keep-out | typically 5 mm isolation distance | [6] |
| Shielding effectiveness of a metal can | 30–40 dB practical | [6] |

## Worked examples

**Example 1 — Choosing the antenna for the Avionics-C (MAX-M10S, U.FL).** The MAX-M10S has an internal LNA + SAW, so a *passive* 25 mm ceramic patch on a short U.FL pigtail (< 10 cm) is adequate if the patch sits on its recommended ground (≈ 50–70 mm) and faces the sky. With a longer cable to the nose cone, use an active L1 antenna and set the receiver's LNA to low-gain/bypass mode to avoid overload [8]. Check C/N₀ of the strongest satellites (≥ 45 dB-Hz open sky is a healthy install).

**Example 2 — ZED-F9P for RTK on the Avionics-B.** The ZED-F9P needs an active multiband antenna: pick one meeting the u-blox table (e.g., L1/L2 stacked patch, 28–35 dB LNA gain, ≥ 100 mm ground) [7]. The team's flown antenna was L1-only (Space Bar notes); the F9P then cannot use L2, forfeiting the fast, robust dual-frequency RTK ambiguity resolution the module is designed for, and the receiver configuration must disable L2 signals consistently (the manual requires L1 and L2 to be enabled or disabled together per constellation, except BeiDou B2) [7].

**Example 3 — Ground-plane effect on a 25 mm patch.** u-blox's measurements show the centre frequency of a 25 × 25 mm patch moving with square ground size over 40–100 mm (their Fig. 23 spans 1570–1595 MHz; the shift is comparable to the patch's bandwidth), and an AR minimum at ≈ 50 mm in another example [6]. With a ceramic patch impedance bandwidth of ≈ 0.75 % (≈ 12 MHz; our patch script, [patch-antennas](patch-antennas.md#worked-examples)), a shift of ~10 MHz moves L1 to the band edge (≈ −1 to −2 dB mismatch plus AR degradation). **Buy the variant tuned for your ground size**, or tune it.

**Example 4 — GNSS in a 54 mm airframe.** Constraints: the patch's ground ≤ 50 mm (the tube ID), fibreglass nose cone a few mm above the patch, 2 W LoRa 30 cm away. Better choices: (a) an active **helix/QFH-type** GNSS antenna (the F9P manual notes helical types can work without a substantial ground plane, e.g. on drones [7]) mounted at the nose tip pointing forward; (b) a 25 mm patch on the largest bulkhead possible, tuned in situ (measure with a VNA through the nose cone); (c) keep the LoRa antenna at the other end of the vehicle and verify C/N₀ on the pad with the LoRa transmitting continuously. Expect lower C/N₀ and possible loss of lock under the parachute when the antenna points sideways/down; the flight software must tolerate fix loss (Space Bar flight-software lesson: non-blocking recovery ladder for GPS).

**Example 5 — How much isolation from the telemetry transmitter?** E22-400T33D output +33 dBm at 433 MHz. If the GNSS front end (including its SAW) must see < −40 dBm of out-of-band signal to avoid compression-induced desense (an illustrative figure; check the module's blocking spec), the required isolation is ≈ 73 dB minus the SAW rejection at 433 MHz (often 40–50 dB) → ≈ 25–35 dB of antenna-to-antenna isolation, obtainable with ~0.5–1 m separation and cross-polarization on a rocket. Also check the transmitter's harmonics and spurious (3 × 433.92 = 1301.8 MHz and 2 × 915 = 1830 MHz fall outside the GNSS bands these receivers use; the transmitter's broadband noise and spurs near 1575 MHz, and front-end blocking by the fundamental, matter more) — measure with a spectrum analyser.

## Practical notes
- **Placement (u-blox)**: antenna plane parallel to the horizon with a full sky view; no components, signal traces or metal near or under the patch; keep distance from the housing; keep digital noise sources (MCU, displays, clocks, switching regulators) away — CPU clock harmonics can exceed the noise floor at 1.5 GHz [6].
- **ESD**: GNSS RF inputs are ESD-sensitive; F9P requires ESD protection at the RF input [7]; active antennas need a bias-T (the F9P manual recommends a 120 nH, high-impedance-at-L-band inductor) and supply current 5–20 mA [7].
- **Enclosure/radome**: dielectric covers within a few mm shift ceramic patches downward; many vendors specify an air gap or sell "tuned for cover" variants.
- **Short circuit/open detection**: u-blox receivers can supervise active antenna current; enable it for pad diagnostics.
- **Record** installed C/N₀ vs elevation (u-blox `UBX-NAV-SAT`) as the acceptance test of an antenna installation.

## Common mistakes & misconceptions
- **"A 28 dB active antenna is better than a 3 dBic passive one."** The 28 dB is LNA gain; compare the *element* gains (dBic), NF and pattern [6].
- **"More LNA gain is always better."** Beyond what the cable loss needs it risks receiver overload and jammer compression; F9P max 50 dB [7].
- **"A chip antenna is just a small patch."** It is linear, lossy and board-dependent; −3 dB polarization loss minimum.
- **"The ground plane is optional."** For patches it sets gain, AR and tuning; for helices it is optional but can add 2–3 dB [6].
- **"Fibreglass is transparent, so a nose cone won't affect GNSS."** Transmission is fine; *detuning* of a narrowband ceramic patch by a wall in its near field can cost several dB.
- **"More satellites in view = better antenna."** Helix antennas can show more satellites via multipath, but position accuracy may be worse [6].
- **"LHCP/RHCP doesn't matter for GNSS."** An LHCP antenna rejects the direct signal by 15–25 dB.
- **"The GPS receiver talks to the satellites."** GNSS is a one-way broadcast: each satellite transmits its ranging code and navigation message; the receiver only listens, measures the arrival time of ≥ 4 signals and solves for x, y, z and its own clock offset (four unknowns → four pseudoranges) [10]. Consequences for the builder: an unlimited number of receivers can use the system; a GNSS receiver needs no transmit licence (Singapore's Exemption Notification lists GNSS receivers, item 14 — [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)); the satellites never learn where your rocket is — the position must be sent down by *your* telemetry link; and "assisted" GNSS (A-GNSS/AssistNow) gets its almanac/ephemeris over a separate internet or cellular link, not from the satellites. The only two-way services are separate add-ons with their own transmitters (e.g. COSPAS-SARSAT 406 MHz distress beacons, BeiDou's short-message service — general knowledge, not re-verified here). (Myth flagged by W4-D1, ham.stackexchange.com/q/21314; the pseudorange solution is worked in [21 receiver architecture](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md).)

## How to simulate / verify
- `python3 tools/verify/ant_patch.py` — ceramic-patch dimensions, bandwidth and CP mode-split for L1 (εr, h editable).
- `python3 tools/verify/ant_polarization.py` — AR→cross-pol and multipath sense reversal.
- Cascade: reproduce the T_sys table with any cascade calculator ([receiver cascade](../07-noise-linearity/receiver-cascade-analysis.md)); inputs: T_A, cable loss, LNA gain/NF, receiver NF.
- openEMS: patch on the actual ground/bulkhead with the nose-cone shell to predict detuning and pattern; NEC cannot model the ceramic.
- Field: log C/N₀ per satellite (u-center) for 15 min open sky; compare antennas/installations; test with the telemetry transmitter keyed.

## Open questions / gaps
- Exact MAX-M10S internal LNA noise figure and blocking specifications were not extracted (the integration manual exceeded the fetch size); fill from the datasheet (domain 18).
- Measured detuning of a 25 mm ceramic patch under a fibreglass nose cone — needs openEMS or bench data.
- GPS signal-power numbers should be cross-checked against the latest IS-GPS-200/IS-GPS-800 and Galileo OS-SIS-ICD (domain 09).

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — ch. 14 (CP patches). (textbook)
2. B. Rama Rao, W. Kunysz, R. Fante, K. McDonald, *GPS/GNSS Antennas*, Artech House, 2013 — GNSS antenna types, choke rings, PCV, multipath. (textbook; cited from general knowledge, not read in this pass)
3. D. R. Jackson, U. Houston microstrip antenna notes — patch Q/BW/CP. (lecture notes)
4. P. Misra and P. Enge, *Global Positioning System: Signals, Measurements, and Performance*, 2nd ed., 2006 — C/N₀, correlation gain, multipath. (textbook; general reference)
5. IS-GPS-200 — GPS L1 C/A minimum received power −158.5 dBW (3 dBi linear antenna). https://www.gps.gov/technical/icwg/ (standard)
6. u-blox, *GNSS antennas — RF design considerations for u-blox GNSS receivers*, UBX-15030289 R03, 2019 — active vs passive (15 dB LNA ≤ 5 m cable; ≤ 26 dB needed; > 35 dB overload), patch sizes, ground plane 50–70 mm, AR/ground example, centre frequency vs ground, chip/PCB/FEA/dipole/loop performance, helix vs patch, isolation (40 dB for GSM), interference, shielding 30–40 dB, fibreglass attenuation note. https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf (app note)
7. u-blox, *ZED-F9P Integration Manual*, UBX-18010802 R16 — §4.4 antenna specification table (17–50 dB, NF < 4 dB, group delay ≤ 10 ns, 40 dB out-of-band rejection, 3/2 dBic element gain on 150 mm ground, AR ≤ 2 dB, PCV < 10 mm, ESD), band limits, checklist (30–40 dB ideal, ground ≥ 100–150 mm, C/N₀ > 40 dB-Hz for RTK, 120 nH bias-T), stacked patches, helix without ground plane, L1/L2 enable rule. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer manual)
8. u-blox, *MAX-M10S Integration Manual*, UBX-20053088 — internal LNA (low-gain default, bypass for high-gain active antennas), internal SAW, LTE B13 notch, VCC_RF antenna supply (as summarised by search results; full text not read). https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer manual)
9. Space Bar avionics knowledge base (user's notes): ZED-F9P flown with an L1-only active antenna; MAX-M10S with U.FL; GPS recovery-ladder lesson. (internal)
10. P. Misra, P. Enge, *Global Positioning System: Signals, Measurements, and Performance*, 2nd ed., Ganga-Jamuna Press, 2006, ch. 1–2 (one-way ranging, pseudorange equations with receiver clock bias, four-satellite solution). (textbook)
