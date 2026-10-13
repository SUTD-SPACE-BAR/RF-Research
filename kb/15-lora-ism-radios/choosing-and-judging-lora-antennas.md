---
title: Choosing and judging LoRa antennas — gain vs pattern (why a high-gain omni is bad for a rocket overhead), spotting fake gain claims, measuring with a NanoVNA and comparative RSSI tests, ground planes, connectors, cable loss and mounting, and what to use on the airframe and at the ground station
domain: 15-lora-ism-radios
slug: choosing-and-judging-lora-antennas
tags: [lora, meshtastic, antenna, dbi, gain, pattern, elevation-pattern, collinear, high-gain-omni, stubby, rubber-duck, whip, dipole, ground-plane, fake-gain, gain-claims, nanovna, s11, vswr, rssi, snr, a-b-test, statistics, sma, rp-sma, u.fl, cable-loss, mounting, rocket, ground-station, yagi, circular-polarisation, beginner]
prerequisites: [../08-antennas/antenna-fundamentals.md, lora-sensitivity-and-link-budget.md]
related:
  - ../08-antennas/dipoles-and-monopoles.md
  - ../08-antennas/antennas-on-rockets.md
  - ../08-antennas/antenna-measurement.md
  - ../08-antennas/small-antenna-limits.md
  - ../08-antennas/antenna-identification-guide.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../08-antennas/yagi-uda-and-log-periodic.md
  - ../03-transmission-lines-matching/coax-and-cables.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/bench-measurement-recipes.md
  - ../18-components-parts/connectors-and-cables-parts.md
  - ground-station-design.md
  - lora-mesh-capacity-and-congestion.md
  - rocket-telemetry-radio-design.md
  - ../20-projects-recipes/ground-station-tracking-yagi.md
  - ../20-projects-recipes/beginner-project-ladder.md
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# Choosing and judging LoRa antennas

The antenna is the cheapest part of a LoRa link and the one most often wrong. This page is the
practical buyer's and tester's guide: what "dBi" really buys you, why the highest-gain omni can be the
worst choice for a rocket, how to recognise impossible gain claims from the antenna's size, how to test an
antenna with a NanoVNA and with a statistically sound RSSI comparison, and what to fit on the airframe
and at the ground station. The physics is in [08-antennas](../08-antennas/_index.md); link budgets are in
[LoRa sensitivity and link budget](lora-sensitivity-and-link-budget.md).

## Questions this page answers
- Will a higher-dBi antenna give my LoRa / Meshtastic node more range?
- Why did my "10 dBi" fibreglass omni do worse than the stock whip?
- Is a high-gain omni good for receiving a rocket's telemetry?
- How can I tell whether an antenna's gain claim is plausible?
- My board came with a stubby antenna — is it any good, and is it even for my band?
- How do I test an antenna with a NanoVNA, and what SWR is good enough?
- How do I compare two antennas with RSSI properly — how many packets do I need?
- Does a quarter-wave whip need a ground plane?
- SMA or RP-SMA? Why doesn't my antenna fit?
- How much does the cable between the radio and the antenna cost me?
- Where and how should I mount a LoRa antenna?
- What antenna should go on the rocket, and what at the ground station?

## TL;DR
- **Gain is pattern, not power.** An omni's extra dBi comes from squashing its doughnut flat toward the horizon. A vertical 4-element collinear (≈ 8 dBi) beats a dipole by ≈ 6 dB at the horizon but is **below 0 dBi over 89 % of elevations from 5° to 80°**, with nulls deeper than −60 dBi (script §2).
- **For a rocket overhead, high-gain omnis lose.** From a station 2 km from the pad, apogee at 10 km is at 79° elevation: a dipole offers −14 dBi there, a 4-element collinear −33 dBi; during early boost (27° elevation) the dipole gives +0.8 dBi vs −5.4 / −8.9 dBi for 4- and 8-element collinears. Use a **tracked directional antenna** (Yagi, ideally circular) for flight and keep a dipole or low-gain omni for the pad and landed rocket ([ground station](ground-station-design.md), [Yagi recipe](../20-projects-recipes/ground-station-tracking-yagi.md)).
- **Size check for gain claims** (upper bound from stacked half-wave dipoles, best spacing; script §3): an honest omni of **5 dBi needs ≥ 1.24 λ** of radiator (≈ 41 cm at 915 MHz, 86 cm at 433 MHz); **8 dBi ≥ 2.8 λ** (≈ 93 cm at 915 MHz); **10 dBi ≥ 4.7 λ** (≈ 1.5 m at 915 MHz). A 15 cm "8 dBi" whip is impossible. A quarter-wave monopole is 5.16 dBi only over an *infinite* ground — sometimes quoted, never achieved on a small board.
- **Measure before trusting**: in its final mounting, a LoRa antenna should show its S11 minimum inside your band with VSWR < 2 across the channel (Meshtastic's antenna docs use the same < 2 criterion). VSWR 2 costs only 0.5 dB; VSWR 5 costs 2.6 dB; an antenna for the wrong band (VSWR ~10) costs ~5 dB of mismatch alone. **A good S11 proves a match, not radiation** — a dummy load has perfect S11.
- **Compare antennas statistically**: with a 4 dB packet-to-packet RSSI spread, detecting a real 2 dB difference needs ≈ **63 packets per antenna**, and 1 dB needs ≈ 250; **interleave A and B** — a slow drift makes "all A then all B" report fake differences 40 % of the time vs 4 % interleaved (script §6).
- **The cable is part of the antenna**: 3 m of RG-174 at 915 MHz (3 dB) cancels a +3 dB antenna upgrade. Keep pigtails short, use LMR-240/400 for runs, or put the radio at the antenna ([coax](../03-transmission-lines-matching/coax-and-cables.md)).
- **Connectors**: LoRa boards use SMA (and U.FL inside); Wi-Fi gear uses **RP-SMA** — they mate mechanically but not electrically. Never power a LoRa transmitter without an antenna or load.

Numbers marked "script" are from `tools/verify/e6_lora_antennas.py` (20/20 PASS).

## Intuition (no math)
Think of an antenna's pattern as a balloon. A dipole is a fat doughnut: plenty of signal at the horizon,
a fair amount up to about 45°, little straight up. Pressing the balloon flat makes the rim stick out
further — that is what a high-gain omni does — but the top and bottom get thinner, and the flattening
also creates ripples (sidelobes and nulls) at in-between angles. All antennas radiate the same total power;
gain is just where it goes.

So "which antenna is best" has no answer without "best toward *what*". A Meshtastic router on a hill
talking to nodes on the plain below wants the flat rim. A node in a valley talking to that hilltop
router wants more upward coverage. A ground station watching a rocket climb from the horizon to almost
overhead wants either a broad pattern or a narrow beam that it points at the rocket. A high-gain omni is
the worst of both: narrow in elevation and not steerable.

Judging an antenna then has three steps. **Does its size make its claim possible?** (Gain needs
aperture — a physically short antenna cannot be high-gain.) **Is it tuned to your band in your mounting?**
(A NanoVNA answers in a minute.) **Does it work better in your actual link?** (A careful A/B test answers
that, but only with enough packets, because RSSI wanders by several dB from packet to packet.)

## The math

### Level 1 — gain, elevation and mismatch
**Gain toward the target.** For a vertical antenna at a ground station, a target at height $h$ and
horizontal distance $D$ is seen at elevation $\epsilon = \arctan(h/D)$; the relevant gain is the pattern
value at that elevation, not the peak.

| Geometry (vertical omni at the station) | Elevation | Dipole (2.15 dBi peak) | 2-el collinear (5.0) | 4-el (7.9) | 8-el (10.9) |
|---|---|---|---|---|---|
| rocket on the pad, 100 m up, station 2 km away | 2.9° | 2.1 | 5.0 | 7.6 | 9.5 |
| early boost, 1 km altitude, 2 km away | 26.6° | 0.8 | −2.5 | −5.4 | −8.9 |
| 3 km altitude, 2 km away | 56.3° | −4.4 | −9.9 | −10.0 | −45.4 |
| apogee 10 km, station 5 km away | 63.4° | −6.5 | −9.4 | −13.0 | −15.3 |
| apogee 10 km, station 2 km away | 78.7° | −14.0 | −14.5 | −32.5 | −29.7 |
| landed rocket 5 km away (horizon) | 0° | 2.2 | 5.0 | 7.9 | 10.9 |

(Uniform in-phase collinears with 0.75 λ element spacing, no ground or losses; script §2. The dipole's
−14 dBi at 79° is the same ≈ 16 dB below broadside that the
[rocket-antenna page](../08-antennas/antennas-on-rockets.md) finds for an axial dipole on the rocket.)

**Mismatch loss.** $\Gamma = (Z_A - 50)/(Z_A + 50)$, mismatch loss $= -10\log_{10}(1 - |\Gamma|^2)$:

| VSWR | 1.2 | 1.5 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|---|
| Return loss (dB) | 20.8 | 14.0 | 9.5 | 6.0 | 3.5 | 1.7 |
| Mismatch loss (dB) | 0.04 | 0.18 | 0.51 | 1.25 | 2.55 | 4.81 |

**Range effect of a dB.** In free space range scales as $10^{\Delta/20}$: +3 dB → ×1.41, −3 dB → ×0.71;
in the two-ray region beyond the breakpoint as $10^{\Delta/40}$ (+3 dB → ×1.19)
([LoRa link budget](lora-sensitivity-and-link-budget.md)).

### Level 2 — why gain needs length, and how to test two antennas
**Directivity of a stacked omni.** $N$ collinear half-wave elements with in-phase currents and spacing $s$
have the pattern $E(\theta) = \dfrac{\cos(\tfrac{\pi}{2}\cos\theta)}{\sin\theta}\,\sum_{n} e^{jk s n\cos\theta}$
($\theta$ from the vertical axis). Integrating $|E|^2$ over the sphere gives the directivity
(script §1): 2.15, 5.4, 7.3, 8.6, 11.8 dBi for N = 1, 2, 3, 4, 8 at the best spacing (≈ λ), with
elevation half-power beamwidths 78°, 28°, 18°, 13°, 6°. A long uniform line source has $D \approx 2L/\lambda$,
which the collinear numbers follow within ≈ 1.5 dB for 8–10 dBi. Real collinears have phasing coils,
feed losses and imperfect currents, so they fall *below* these bounds — which makes the size test a safe
filter: if the bound says "impossible", it is.

**Minimum length for a claimed gain** (search over N = 1–10 and s = 0.5–1.0 λ, script §3):

| Claimed omni gain | Minimum radiator length | at 433 MHz | at 868 MHz | at 915 MHz |
|---|---|---|---|---|
| 3 dBi | 1.0 λ | 69 cm | 35 cm | 33 cm |
| 5 dBi | 1.24 λ | 86 cm | 43 cm | 41 cm |
| 6 dBi | 1.74 λ | 120 cm | 60 cm | 57 cm |
| 8 dBi | 2.84 λ | 196 cm | 98 cm | 93 cm |
| 10 dBi | 4.7 λ | 325 cm | 162 cm | 154 cm |

**A/B RSSI comparison.** Packet RSSI varies by $\sigma$ dB from fading, body movement and quantisation.
To detect a true difference $\Delta$ with a two-sample test at 5 % significance and 80 % power, each antenna
needs $n \approx 2(z_{0.975} + z_{0.8})^2\sigma^2/\Delta^2 = 15.7\,\sigma^2/\Delta^2$ packets:

| σ (dB) | Δ = 0.5 dB | 1 dB | 2 dB | 3 dB |
|---|---|---|---|---|
| 2 | 252 | 63 | 16 | 7 |
| 4 | 1 005 | 252 | 63 | 28 |
| 6 | 2 261 | 566 | 142 | 63 |

A Monte-Carlo with 1 dB RSSI steps reproduces the 80 % power at 63 packets (σ 4, Δ 2 dB). With a slow
random drift (0.15 dB per packet) and *no* real difference, interleaved A/B tests flag a difference 4 % of
the time (as designed); "all of A, then all of B" flags one 40 % of the time (script §6).

### Level 3 — what the simple pictures leave out
- **Ground and mounting reshape the pattern.** Over real ground, the elevation pattern acquires lobes and
  nulls from the ground reflection; a mast-mounted omni a few wavelengths up has several lobes below 30°
  ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)). The "doughnut" is a free-space
  idealisation.
- **Efficiency is invisible to S11.** A lossy stubby can show a lovely match because its loss resistance
  provides the 50 Ω. Efficiency needs a Wheeler cap or a comparison against a reference dipole
  ([bench recipe R7](../17-test-measurement/bench-measurement-recipes.md),
  [small-antenna limits](../08-antennas/small-antenna-limits.md)).
- **Common-mode current makes the cable part of the antenna**, especially for monopoles without a ground
  plane and for end-fed designs: the "grab the cable" test on a NanoVNA reveals it
  ([NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md)).
- **Polarisation**: a rolling rocket with a linear antenna gives cos² fades against a linear ground antenna;
  circular polarisation at the ground costs a steady 3 dB and removes the nulls
  ([polarisation](../08-antennas/antenna-polarization-and-circular-polarization.md)).
- **Bandwidth**: a narrow, high-Q antenna that is perfectly matched on the bench detunes when touched or
  placed in a nose cone; thicker elements are more tolerant ([dipoles](../08-antennas/dipoles-and-monopoles.md)).

## Design equations & rules of thumb
| Rule | Value / test | Source |
|---|---|---|
| Choose gain from the geometry | target elevations ≤ a few degrees → higher-gain omni; wide elevation range → dipole/low gain or a tracked beam | script §2 |
| Size test | 5 dBi omni ≥ 1.24 λ, 8 dBi ≥ 2.84 λ of radiator | script §3 |
| "5 dBi" quarter-wave | only over an infinite ground (5.16 dBi); expect ≈ 2 dBi on a small plane, tilted upward | script §3 |
| Match target | S11 minimum in band, VSWR < 2 over the channel in the final mounting | Meshtastic docs [2]; mismatch table |
| A/B packets | n ≈ 15.7 σ²/Δ² per antenna; interleave | script §6 |
| Pigtail/feeder | ≤ 0.5 dB total if possible; RG-174/316 only for ≲ 30 cm | [coax](../03-transmission-lines-matching/coax-and-cables.md) |
| λ/4 ground plane | ≥ λ/4 radius (≈ 17 cm at 433 MHz, 8 cm at 915 MHz) or 3–4 radials drooped ≈ 40° | [dipoles](../08-antennas/dipoles-and-monopoles.md) |
| Clearance | ≥ λ/4 from metal masts and walls, above head height, clear line of sight | [Fresnel](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md) |
| SMA vs RP-SMA | check pin vs socket before ordering | [connectors](../18-components-parts/connectors-and-cables-parts.md) |
| U.FL | ≈ 30 mating cycles; secure against vibration | [connectors and launches](../13-pcb-rf-layout-emc/connectors-and-launches.md) |

## Worked examples
**1. Ground antenna for a 10 km flight, station 2 km from the pad.** The rocket sweeps from ≈ 3° to 79°
elevation. A fixed 8-element collinear is the best of the omnis only below a few degrees (pad, landing)
and drops to −9 dBi by 27° and into nulls beyond; a dipole stays within 2.1 to −14 dBi with no nulls; a
tracked 6-element Yagi (11.2 dBi, 50° × 61° beam) keeps ≈ 8–11 dBi on the rocket if pointed within ±25° (half its beamwidth)
([Yagi recipe](../20-projects-recipes/ground-station-tracking-yagi.md)). Choice: the tracked Yagi (CP if
possible) for flight, plus a dipole or 2–5 dBi omni on a mast for pad checks and the landed beacon.
Placing the station 3–5 km cross-range also keeps the rocket out of the tail null of its own antenna
([LoRa telemetry link](../20-projects-recipes/lora-rocket-telemetry-link.md)).

**2. Is a 30 cm "10 dBi" 915 MHz omni real?** 30 cm is 0.92 λ at 915 MHz. The size table says 10 dBi
needs ≥ 4.7 λ (≈ 1.5 m) and even 3 dBi needs ≈ 1 λ. A 30 cm radiator can honestly be ≈ 2–3 dBi.
Verdict: the claim is not physical; treat it as a dipole-class antenna and measure it.

**3. A stubby that came with the board.** NanoVNA in the final enclosure: minimum at 870 MHz, VSWR 5 at
915 MHz — it is an 868 MHz part. Mismatch loss 2.55 dB, plus a loaded stubby's low radiation efficiency
(the [antenna-fundamentals](../08-antennas/antenna-fundamentals.md) example gives ≈ 41 %, −3.9 dB, for a
50 mm 433 MHz helical whip). Replacing it with a measured λ/4 whip on a proper ground plane, or a dipole,
plausibly recovers ≈ 5 dB — the kind of improvement the community reports as "doubling range" (D2 §3a,
◐ myth now addressed). Confirm with an A/B test, not by eye.

**4. Designing the A/B test.** Two antennas, fixed node 1.5 km away, RSSI spread σ ≈ 4 dB observed.
To see a 2 dB difference: ≥ 63 packets each; swap antennas every 5 packets (or use an RF switch and
alternate every packet), keep the node, cable, orientation and your body position fixed, log SNR as well
as RSSI (RSSI saturates near the noise floor), and compare means with their standard errors. To see 1 dB
you need ≈ 250 each — usually not worth it; a NanoVNA match check plus a 2–3 dB A/B test is enough to
choose.

**5. The pigtail trap.** A +3 dBi-better antenna mounted on the roof with 3 m of RG-174 at 915 MHz gains
3 − 3.0 = 0 dB. With 3 m of LMR-240 (0.75 dB) it gains ≈ 2.3 dB; with the radio in a box at the antenna
and a USB/serial cable down, the full 3 dB. At 433 MHz the same 3 m of RG-174 costs 1.9 dB.

**6. On the airframe.** For a fibreglass airframe: a 433 MHz sleeve or centre-fed dipole along the axis in
a radio-transparent section, matched **in the assembled airframe** (it resonates lower near the dielectric),
with a ferrite choke on the coax; for 868/915 MHz the same at half the size, or a monopole against the
avionics-bay ground. Expect the tail null (−16 dB at 11° off axis), and carbon fibre or aluminium to block
RF entirely ([antennas on rockets](../08-antennas/antennas-on-rockets.md),
[rocket telemetry design](rocket-telemetry-radio-design.md)). Gain claims are irrelevant here; the pattern
along the trajectory is what matters.

## Practical notes
- **Red flags in listings** (community consensus, 9 posts in the D2 cluster #8, plus Meshtastic's antenna
  guidance [2]): no stated tuned frequency or band; "868/915" sold as one part without a VSWR plot; omni
  gains that fail the size table; "dBi" figures without a pattern; prices too low for a fibreglass
  collinear of the claimed length.
- **Test recipe** (NanoVNA, ≈ 15 minutes): calibrate SOL at the end of the cable you will use; mount the
  antenna as it will be used (on the board, in the enclosure, on the mast bracket); sweep ±10 % around the
  band; record the minimum frequency, VSWR at your channel and the VSWR-2 bandwidth; repeat the
  "grab the cable" test; save the Touchstone file ([NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md),
  [antenna measurement](../08-antennas/antenna-measurement.md)).
- **Ground planes**: a λ/4 whip needs a ground plane of ≥ λ/4 radius or radials; on a small node the
  board and battery are the ground, so the match changes with the case — tune in the case. Many stubby
  antennas are quarter-wave types that rely on a ground plane (Meshtastic notes the same [2]).
- **Connectors**: SMA (pin on the male plug) is standard on LoRa modules; RP-SMA swaps pin and socket and is
  common on Wi-Fi antennas; buy a gender-changer kit and label everything; torque SMA to spec; U.FL
  survives ≈ 30 matings and needs strain relief on a rocket.
- **Mounting**: vertical (match polarisation with the other end), above head height and clear of metal by
  ≥ λ/4; away from other antennas (≥ a few λ, or the strong neighbour desenses the receiver —
  [front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)); weatherproof the
  connector (self-amalgamating tape); DC-ground and bond mast antennas for lightning
  ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).
- **Never transmit without an antenna or load** — the reflected power can damage the PA (Meshtastic's
  getting-started warning [3]).
- **Legal note**: antenna gain counts toward e.r.p./EIRP limits; a 5 dBi antenna on a 20 dBm Singapore
  917–925 MHz node already exceeds 100 mW e.r.p. ([band plans](ism-band-plans-duty-cycle.md)).

## Common mistakes & misconceptions
- **"A higher-dBi omni always gives more range."** Only toward the horizon; overhead and nearby targets can
  fall in its nulls (D2 §3a; [antenna fundamentals](../08-antennas/antenna-fundamentals.md) forum note).
  For rockets, a dipole or a tracked beam beats a high-gain omni.
- **"Anything sold for 868/915 MHz is tuned for my band."** Measure it; many stock and marketplace antennas
  are off-band or mistuned (D2 §3a ◐ — now addressed).
- **"Good SWR means a good antenna."** It means a good match; efficiency and pattern are separate.
- **"A 5 dBi quarter-wave whip."** 5.16 dBi needs an infinite ground; on a node it is ≈ 2 dBi and tilted.
- **"I swapped antennas and RSSI went up 2 dB, so B is better."** With σ ≈ 4 dB you need ~60 packets each,
  interleaved, before 2 dB means anything.
- **"The longer the extension cable, the higher I can mount it, so it's always worth it."** Only if the
  height gain (≈ 6 dB per doubling in the two-ray region) exceeds the cable loss.
- **"Meshtastic shows a node 500 km away, so this antenna is amazing."** Check `via_mqtt`; internet-bridged
  packets show far-away positions with local RF reception ([LoRa link budget — common mistakes](lora-sensitivity-and-link-budget.md)).
- **"RP-SMA and SMA are the same."** They thread together but the centre contacts do not mate.

## How to simulate / verify
- `python3 tools/verify/e6_lora_antennas.py` — collinear directivity and elevation beamwidth, gain toward a
  rocket at each flight phase, minimum length per claimed gain (with the 2L/λ cross-check), monopole over an
  infinite ground, mismatch table, feeder trade, A/B sample sizes and the drift/interleaving Monte-Carlo
  (20/20 PASS).
- Pattern of a real antenna on its mount: NEC-2 ([NEC modelling](../16-simulation-tools/nec-antenna-modelling.md))
  or openEMS ([antenna simulation](../08-antennas/antenna-simulation-nec-openems.md)); compare with the
  idealised table above.
- Bench and field: NanoVNA S11 (ladder rung 4), Wheeler-cap efficiency (bench recipe R7), A/B RSSI test
  (ladder rung 7) ([beginner project ladder](../20-projects-recipes/beginner-project-ladder.md)).

## Open questions / gaps
- The collinear model ignores mutual coupling, phasing-coil loss and the mast; measured patterns of common
  commercial LoRa collinears are not in the KB.
- The RSSI spread σ depends on site and motion; the 4 dB used here is an assumption — measure it from your own
  logs before planning a test.
- No independent measurements of popular Meshtastic antennas (gain or efficiency) were found that meet the
  KB's sourcing rules; community reports are anecdotal.
- Efficiency of typical stubby/helical LoRa antennas is quoted from one worked example (08 page), not a
  survey.

## Sources
1. This KB: [antenna fundamentals](../08-antennas/antenna-fundamentals.md) (gain redistribution, stubby efficiency example, collinear forum note), [dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md) (ground planes, radials, long-whip myth), [antennas on rockets](../08-antennas/antennas-on-rockets.md) (tail null, airframe materials, detuning), [ground-station Yagi recipe](../20-projects-recipes/ground-station-tracking-yagi.md) (6-el 11.2 dBi, 50° × 61°), [coax and cables](../03-transmission-lines-matching/coax-and-cables.md) (loss per 10 m), [connectors](../18-components-parts/connectors-and-cables-parts.md) and [launches](../13-pcb-rf-layout-emc/connectors-and-launches.md) (SMA/RP-SMA, U.FL 30 cycles), [bench recipe R7](../17-test-measurement/bench-measurement-recipes.md) (Wheeler cap), [band plans](ism-band-plans-duty-cycle.md). (internal)
2. Meshtastic documentation, "LoRa antenna selection" (50 Ω SMA; RP-SMA not interchangeable; stubby quarter-wave antennas need ground planes; cable loss) https://meshtastic.org/docs/hardware/antennas/lora-antenna/ and "Antenna testing" (VSWR < 2 at the tuned frequency, > 0 dBi, avoid suppliers who state no tuned frequency or claim huge omni gains; a VNA shows match, not radiation) https://meshtastic.org/docs/hardware/antennas/antenna-testing/ (project docs; fetched 2026-10-02)
3. Meshtastic documentation, "Getting started" — do not power a radio without an antenna. https://meshtastic.org/docs/getting-started/ (project docs; search summary)
4. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley (2016), ch. 4 (half-wave dipole pattern) and ch. 6 (uniform linear arrays, directivity) — the pattern-multiplication model used in the script. (textbook)
5. Community demand and myths: [gaps/D2-reddit.md](../../gaps/D2-reddit.md) §2 rank 8 (choosing and judging LoRa/ISM antennas, 9 posts, 8 from r/meshtastic) and §3a (higher-dBi myth, stock-antenna myth). (gap analysis — anecdotal posts)
6. D. C. Montgomery, G. C. Runger, *Applied Statistics and Probability for Engineers*, Wiley — two-sample sample-size formula $n = 2(z_{\alpha/2}+z_\beta)^2\sigma^2/\Delta^2$. (textbook; standard result, checked by Monte-Carlo in the script)
