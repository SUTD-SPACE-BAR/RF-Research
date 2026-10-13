---
title: DIY phased-array projects — ADI Phaser, KrakenSDR/KerberosSDR, coherent RTL-SDR and Pluto/B210 arrays, FR-4 patch arrays, switched-array radar, rocket ground-station tracking
domain: 12-phased-arrays
slug: diy-phased-array-projects
tags: [diy, student-budget, ADI-Phaser, CN0566, KrakenSDR, KerberosSDR, RTL-SDR, PlutoSDR, B210, LimeSDR, interferometer, direction-finding, rocket-recovery, ground-station, tracking, patch-array, FR-4, JLCPCB, butler-matrix, switched-array-radar, charvat, MIT, link-budget, 433MHz, 915MHz, 2.4GHz, 5.8GHz, series-fed-array, comb-line, travelling-wave-array, beam-squint, 24GHz, 77GHz, RO3003]
prerequisites: [array-factor-linear-arrays.md, beam-steering-grating-lobes.md, beamforming-architectures.md, array-calibration.md, adaptive-beamforming-doa.md]
related: [planar-arrays-element-pattern-coupling.md, tapering-sidelobe-control.md, phase-shifters-ttd-components.md, ../14-sdr-dsp/sdr-hardware-survey.md, ../11-radar/diy-radar-hardware.md, ../11-radar/mimo-radar-virtual-arrays.md, ../15-lora-ism-radios/ground-station-design.md, ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md, ../15-lora-ism-radios/ism-band-plans-duty-cycle.md, ../08-antennas/yagi-uda-and-log-periodic.md, ../08-antennas/patch-antennas.md, ../08-antennas/antennas-on-rockets.md, ../20-projects-recipes/phased-array-starter-build.md, ../20-projects-recipes/ground-station-tracking-yagi.md, ../19-regulations-safety/singapore-imda-rules.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# DIY phased-array projects

## Questions this page answers
- What is the cheapest way to start experimenting with phased arrays?
- What can I learn with the ADI Phaser (CN0566), and what does it cost?
- How do KrakenSDR and KerberosSDR achieve phase coherence, and what are their limits?
- Can I make two RTL-SDRs, two Plutos, or one Pluto/B210 into a coherent array?
- Could a KrakenSDR find our landed rocket from its 433 MHz beacon? How accurately?
- Should our ground station use a phased array or a tracking Yagi?
- How big would a 433 MHz, 915 MHz, 2.4 GHz or 5.8 GHz array be for 15 or 20 dBi?
- How fast must a tracking antenna steer to follow a rocket off the pad?
- How do I build a 2.4/5.8 GHz patch array on FR-4 (JLCPCB), and how do I feed and steer it?
- What is a switched-array (MIT/Charvat-style) radar?
- What is realistic on a student budget, and in what order should I do things?
- How do the series-fed patch and comb-line antennas on 24/60/77 GHz radar boards work, and how much does their beam squint with frequency?

## TL;DR
- **Start digital, small and low-frequency**: a 2-channel coherent interferometer (Pluto Rev C/D second channel, a B210, or two RTL-SDRs on a shared clock with a noise source) teaches steering vectors, calibration and ambiguity for ≈ US$250–2,400 of SDR you may already own ([SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)).
- **KrakenSDR** (5 × R820T2/RTL2832U, shared clock, built-in switched noise source, 24–1766 MHz, 2.56 MHz/channel, ≈ US$750 in 2026) is the best-value coherent DF receiver below 1.77 GHz; it recalibrates automatically after every retune [1][2]. Its predecessor **KerberosSDR** (4 channels, 24 MHz–1.7 GHz) needed antennas disconnected during calibration [3].
- **ADI Phaser (EVAL-CN0566-RPIZ, ≈ US$2,875)**: 8-element 10–10.5 GHz receive array, 14 mm (0.48λ) spacing, two ADAR1000 beamformers, ADF4159 FMCW LO, LTC5548 mixers to a ≈ 2 GHz IF, Pluto + Raspberry Pi, Python labs [4][5][6]. The fastest way to *see* array factors, tapering, grating lobes, squint-free FMCW and monopulse on real hardware.
- **Rocket recovery DF** (most useful array for Space Bar): KrakenSDR + 5-element UCA (s = 0.4 → r = 23.6 cm at 433 MHz) gives ≈ 0.3° noise-limited bearings at 10 dB SNR; realistic field accuracy is set by calibration/multipath (1–5°). At 5 km, 1° ≈ 87 m cross-range; two stations 2 km apart localise a target 5 km out to ≈ 230 m (1° bearings) (script §4).
- **Ground-station tracking**: at 433/915 MHz the telemetry link already has large free-space margins (2 W, SF9/125, 30 km: ≈ 50 dB with a dipole, [LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md); with Singapore's 10 mW e.r.p. limit at 433 MHz, ≈ 36 dB with a 10 dBi Yagi [7]). An array there is large (15 dBi ≈ 17 elements ≈ 1.4 m square at 433 MHz) and buys little — a **GPS-telemetry-pointed Yagi** is the right tool. Electronic steering pays off at **2.4/5.8 GHz high-rate links** (5.8 GHz, 25 dBm, 30 km needs ≈ 20–23 dBi at the ground: an 8 × 8 FR-4 patch panel ≈ 21 cm square).
- **Steering rates**: a rocket at 300 m/s rising past a station 2 km away sweeps elevation at up to 8.6°/s (0.5 km: 34°/s) — easy for electronic steering, hard for hobby rotators; the fix is distance (≥ 2–5 km) or a wide-beam antenna for the first seconds.
- **FR-4 patch arrays** from JLCPCB work at 2.4 GHz and (lossily) at 5.8 GHz: λ/2 grid, corporate or series feed, measured with a NanoVNA; steer with a Butler matrix (4 fixed beams ±14.5°, ±48.6°), analog/digital phase shifters, or by digitising each element. Expect realized gain 2–4 dB below directivity on FR-4 [8].
- **Switched-array radar** (Charvat/MIT): one FMCW radar front end is switched across many antennas; imaging is done digitally from the stored channel combinations (a TDM MIMO/virtual array) [9][10].

- **Series-fed / comb-line columns** (24/60/77 GHz radar boards): patches λg apart beam broadside at f0 and squint as sinθ = √ε_eff(1 − f0/f) — ±0.5° over 24.00–24.25 GHz but −2.9/+2.8° over 76–81 GHz; centre-feed to cancel; FR-4 loses 0.22 dB/mm at 77 GHz, so use RO3003-class laminates ([section](#printed-series-fed-patch-and-comb-line-arrays)).

## Intuition (no math)

**What you are really buying is coherence.** The antennas are cheap. What makes an array is a set of receivers whose phase relationship you *know*. Everything in the budget table below is ranked by how much it costs to get that knowledge: two channels on one chip (Pluto Rev C/D, B210) are coherent by construction; five tuners on one clock plus a noise source (KrakenSDR) are coherent after automatic calibration; eight channels with integrated phase shifters (Phaser) are coherent after a one-time factory-style calibration.

**Low frequency = big but forgiving; high frequency = small but demanding.** A λ/2 spacing is 35 cm at 433 MHz and 2.6 cm at 5.8 GHz. At 433 MHz a millimetre of cable is nothing (0.8°); at 5.8 GHz it's 12°. Direction finding at 433 MHz with whips on a car roof is forgiving and useful; beamforming at 5.8 GHz fits on a PCB but needs careful layout and calibration.

**For rockets, the array problem is usually pointing, not gain.** The LoRa telemetry link closes with huge margin in free space. What actually drops packets is the rocket antenna's pattern nulls, spin, the plume, and the ground station not pointing at the rocket. A narrow high-gain beam makes pointing *harder*. Arrays shine where you need gain *and* agility (high-rate video at 5.8 GHz), or where you need to *find* something (a landed rocket's beacon).

## The math

### Level 1 — the project ladder

| Step | Hardware | Frequency | Channels | What you learn | Approx. cost (2026) |
|---|---|---|---|---|---|
| 0 | numpy simulations (this domain's tools/verify scripts) | any | any | array factor, steering, DOA | free |
| 1 | Pluto Rev C/D (2R, u.FL, needs firmware "2r2t" setting) or B210 | 70 MHz–6 GHz (Pluto 325–3800 spec) | 2 | interferometry, calibration, ambiguity | US$250 / US$2,400 [11] |
| 2 | 2–4 RTL-SDRs on a shared clock + noise source (DIY Kerberos) | 24–1766 MHz | 2–4 | coherence, sample alignment | ≈ US$40 each + work |
| 3 | KrakenSDR + 5 whips | 24–1766 MHz | 5 | DOA (MUSIC), UCA, passive radar | ≈ US$750 [11] |
| 4 | FR-4 2.4 GHz 4-patch array + Butler matrix or phase shifters + 1 SDR | 2.4 GHz | 1 (analog) | feed networks, scan loss, coupling | US$50–400 |
| 5 | ADI Phaser CN0566 | 10–10.5 GHz | 8 (2 digital) | beamformer ICs, taper, FMCW, monopulse | ≈ US$2,875 [6] |
| 6 | Multi-Pluto/bladeRF digital array, or ADAR1000-based custom board | 2–16 GHz | 4–16 | full DBF, adaptive nulling | US$1k–5k+ |

### Level 2 — key calculations

**(a) Two-element interferometer.** Δφ = kd sinθ ([array factor](array-factor-linear-arrays.md)). Estimate θ = arcsin(Δφ/(kd)). With d = λ/2 the mapping is unique over ±90°; with d = λ a source at 20° is indistinguishable from one at −41.1° (script §5) — the two-element grating lobe. Sensitivity: an uncorrected 10° phase error becomes 3.2° of bearing at broadside with d = λ/2, 1.6° with d = λ — longer baselines are more accurate but ambiguous; real DF systems combine a short (unambiguous) and a long (accurate) baseline, which is exactly what a 5-element UCA's different chords give MUSIC.

**(b) How big is an array for a given gain?** Using the large-array relation G ≈ e_ap·4πA/λ² ([planar arrays](planar-arrays-element-pattern-coupling.md)) with e_ap ≈ 0.6 (FR-4 patch + feed losses, an assumption) on a λ/2 grid (script §1):

| Band | 15 dBi | 20 dBi |
|---|---|---|
| 433 MHz | 17 elements, 1.42 m square | 54 el., 2.52 m |
| 915 MHz | 17 el., 0.67 m | 54 el., 1.19 m |
| 2.44 GHz | 17 el., 25 cm | 54 el., 45 cm |
| 5.8 GHz | 17 el., 11 cm | 54 el., 19 cm |
| 10.25 GHz | 17 el., 6 cm | 54 el., 11 cm |

Every element needs a phase-controlled channel. At 433 MHz a 17-channel coherent array to match one 1.7 m Yagi (≈ 14 dBi, [Yagi page](../08-antennas/yagi-uda-and-log-periodic.md)) is not a sensible trade unless the goal is DF or nulling.

**(c) Does the ground station need array gain?** Free-space budgets (script §2; rocket antenna 0 dBi, LoRa SF9/125 sensitivity −129 dBm consistent with [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)):
- 433 MHz, 2 W (E22-400T33D-class), 30 km: −79.6 dBm into a 2.15 dBi dipole → **49 dB margin**; into a 14 dBi Yagi → 61 dB. Under Singapore's 10 mW e.r.p. rule the EIRP is ≈ 21 dB lower ([ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md) gives ≈ 36 dB margin at 30 km with a 10 dBi Yagi [7]).
- 915 MHz, 1 W, 30 km: 40 dB (dipole) … 52 dB (Yagi).
- 2.44 GHz, 100 mW, 0 dBi TX, receiver needing −100 dBm (a wideband link): 30 km → −7.6 dB with a dipole, +4.3 dB with 14 dBi, +10.3 dB with 20 dBi.
- 5.8 GHz analog/digital video, 25 dBm, 2 dBi TX, −90 dBm receiver: 30 km → −18 dB (dipole), −0.3 dB (20 dBi), +2.7 dB (23 dBi). **This is where a steerable 20+ dBi panel is justified.**
Margins in free space are not margins in practice: rocket-antenna nulls (10–25 dB, [antennas on rockets](../08-antennas/antennas-on-rockets.md)), polarisation mismatch, plume and fading eat them. A *second* array use is diversity/nulling rather than gain.

**(d) Tracking kinematics.** For a rocket rising vertically at speed v past a station at horizontal distance D, the elevation angle is atan(h/D) and its rate is vD/(D² + h²), maximal (v/D rad/s) at lift-off (script §3): D = 0.5 km, 300 m/s → 34°/s; D = 2 km → 8.6°/s; D = 5 km → 3.4°/s; above 3 km altitude the rates drop below ≈ 2.6°/s for D = 2 km. A 12.7° beam (8 × 8 at 5.8 GHz) at 5°/s must be re-pointed every ≈ 1.3 s; electronic steering updates in microseconds (ADAR1000 beam switching 20 ns [12]), so an electronically steered panel can follow the boost phase open-loop from telemetry or closed-loop (monopulse/DOA) — a mechanical rotator generally cannot. Practical hybrid: a wide-beam antenna (or a panel tilted toward the expected trajectory) for the first seconds, a narrow beam after burnout.

**(e) DOA accuracy for a recovery beacon.** CRB-level accuracy for a 5-element array at 10 dB SNR with 200 snapshots is ≈ 0.1–0.3° ([DOA](adaptive-beamforming-doa.md) example 1); field systems are limited by calibration and multipath to degrees. Cross-range error = R·σ_θ: 1° at 5 km → 87 m; 3° at 20 km → 1.05 km. With two stations B apart and a target at range R, the position error ≈ R·σ_θ/sin(intersection angle): 2 km baseline, 5 km range → 22.6° intersection → 227 m for 1° bearings (script §4). Walk-in DF (re-measuring as you approach) converges quickly because the error scales with range.

**(f) Switched-array (TDM) imaging radar.** Instead of N coherent receivers, one FMCW transceiver is multiplexed with RF switches across N_t transmit and N_r receive antennas; each (t, r) pair is measured in turn and stored; the image is formed by delay-and-sum over all pairs — a virtual array of N_t·N_r positions at the pair midpoints (the same principle as [MIMO virtual arrays](../11-radar/mimo-radar-virtual-arrays.md)). The target must be quasi-static during a full switch cycle. Charvat's MIT courses built such radars from low-cost parts (pegboard and Wi-Fi antennas in the IAP phased-array course) and his book covers switched-array design [9][10].

### Level 3 — beyond hobby scale
- **Conformal arrays on the rocket** (wraparound elements forming a steerable or diversity array) run into all the coupling and embedded-pattern issues of [planar arrays](planar-arrays-element-pattern-coupling.md) on a curved, metal/composite body — a research project.
- **Hybrid mechanical + electronic**: a small electronically steered panel (±30°) on a slow az/el mount combines fast fine pointing with full-sky coverage.
- **Multi-station coherent arrays** (widely separated receivers with GPSDO timing) become TDOA/interferometric networks — beyond single-array beamforming.

## Design equations & rules of thumb

| Rule | Validity | Value |
|---|---|---|
| Interferometer unambiguous iff d ≤ λ/2 | 2 elements, ±90° | 2.44 GHz: 6.1 cm |
| Bearing error = phase error/(kd cosθ) | 2 elements | 10° at d = λ/2 → 3.2° |
| Elements for gain G: N ≈ G/(π e_ap) (λ/2 grid) | large array | 20 dBi, e_ap 0.6 → 54 |
| Max elevation rate = v/D | vertical ascent | 300 m/s, 2 km → 8.6°/s |
| Cross-range error = R σ_θ | DF | 1°, 5 km → 87 m |
| UCA radius r = sλ/(2 sin(π/n)) | KrakenSDR rule, s = 0.2–0.5 | 5 el., s = 0.4, 433 MHz: 23.6 cm |
| Cables equal within 1 cm below ~900 MHz | KrakenSDR (uncalibrated side) | ≈ 7°/cm at 400 MHz |
| Far field ≥ 2L²/λ for pattern tests | any | Phaser (L ≈ 0.11 m): ≈ 0.8 m |

## Worked examples

**Example 1 — Finding the landed rocket with a KrakenSDR (433 MHz beacon).** Five magnetic-mount whips on a car roof in a UCA of radius 23.6 cm (s = 0.4; the KrakenSDR wiki recommends 0.2 < s < 0.5 [2]), equal-length coax from one reel (within 1 cm), KrakenSDR + Raspberry Pi, MUSIC, squelch set just above the noise floor. A 10 mW beacon at 5 km in a flat landing zone (two-ray-ish, but assume 20 dB SNR per element) gives sub-degree noise-limited bearings; expect 2–5° real-world scatter from multipath and the car body. Drive a few hundred metres sideways to get a second bearing (baseline 1–2 km) → a few-hundred-metre search box at 5 km, shrinking as you approach. Log bearings with GPS positions; KrakenSDR's mapping software supports this workflow [1].

**Example 2 — 5.8 GHz 8 × 8 FR-4 patch panel for a video downlink.** λ/2 = 25.8 mm → 207 × 207 mm; directivity ≈ 23 dBi ([planar arrays](planar-arrays-element-pattern-coupling.md) example 1), realized ≈ 19–21 dBi on FR-4. Free-space margin at 30 km for a 25 dBm, 2 dBi transmitter and −90 dBm receiver: ≈ 0 to +2.7 dB (script §2) — marginal; at 10 km ≈ +9 to +12 dB. Steering: 64 channels with ADAR1000-class ICs are 5.8 GHz-incompatible (8–16 GHz); at 5.8 GHz use four 4 × 4 subpanels each on a mechanical mount, or an analog 1-D steering of 8 columns (8 phase shifters) with fixed corporate feeds in the other dimension. A 4 × 4 subpanel (≈ 17 dBi) on a GPS-driven pan/tilt is the honest student-budget version.

**Example 3 — 4-element 2.44 GHz receive array, three ways.** (i) Butler matrix on 1.6 mm FR-4 (four 90° hybrids, two crossovers, 45° lines; ≈ 60 × 60 mm) + SP4T switch + one Pluto: four beams at ±14.5° and ±48.6° with −3.7 dB crossovers ([architectures](beamforming-architectures.md)); (ii) LNAs + JSPHS-2484+ analog phase shifters (2 in cascade for 360°) + Wilkinson + Pluto — continuous steering, needs a per-frequency LUT ([components](phase-shifters-ttd-components.md)); (iii) two Plutos (2 RX each) sharing an external reference, calibrated with a split noise source after every retune — full digital beamforming and DOA. (iii) teaches the most; (i) is the most robust; (ii) the most "phased-array-like".

**Example 4 — Showing grating lobes on the Phaser.** Its elements are 14 mm apart (0.48λ at 10.25 GHz), so no grating lobes appear. Set the gain of every other element to zero: the active array becomes 4 elements at 28 mm (0.96λ): a steered beam at 20° now has a grating lobe at sinθ = sin20° − 1/0.96 ≈ −0.70 → −44° — sweep the HB100 source and see both. The same trick with a Taylor taper shows beam broadening and sidelobe reduction, and splitting the two ADAR1000 halves gives a monopulse Σ/Δ ([tapering](tapering-sidelobe-control.md) §(h)).

**Example 5 — Tracking the boost phase.** Station 2 km from the pad, rocket to 300 m/s: 8.6°/s peak elevation rate at lift-off, 6.9°/s at 1 km altitude (script §3). A 433 MHz 11-element Yagi (≈ 30° beamwidth) on a rotator tolerates pointing lag of ±15°: if the rotator slews at a few °/s it falls behind by ≈ 10° in the first 3 s — acceptable. A 12.7° 5.8 GHz beam would lose the rocket; use electronic steering or a lower-gain antenna for the boost.

## Practical notes
- **Regulations first.** Singapore's IMDA rules limit 433 MHz short-range devices to 10 mW e.r.p. per the KB's band-plan page; 2.4/5.8 GHz have their own EIRP limits which an array's N² EIRP growth can exceed quickly ([ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md), [IMDA rules](../19-regulations-safety/singapore-imda-rules.md)). Receive-only arrays (DF, passive radar) avoid most of this.
- **Pluto second channel**: Rev C/D boards route RX2/TX2 to u.FL; the factory firmware runs 1R1T and must be switched to AD9361-compatible "2r2t" mode (device-tree/firmware environment setting); some clones (Pluto+) report issues [13]. The two channels share one LO — coherent, but calibrate the path difference.
- **RTL-SDR DIY coherence**: share one 28.8 MHz clock, add a switched noise source, align sample streams by cross-correlation, and run Linux natively (VM USB latency breaks coherence, per the KerberosSDR guide [3]); or just buy a KrakenSDR.
- **Mounting and ground planes**: magnetic whips need a ground plane (car roof); KrakenSDR advises a direct or capacitive ground connection [2]; keep the array away from the car's roof rack and antennas that re-radiate.
- **JLCPCB FR-4**: ε_r ≈ 4.4–4.6 and tanδ ≈ 0.015–0.02 at GHz make 5.8 GHz patches ≈ 50–60% efficient and shift resonance with stackup; simulate with the actual JLC stackup and measure every panel with a NanoVNA ([patch antennas](../08-antennas/patch-antennas.md), [JLCPCB RF manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)).
- **Measure patterns outdoors** at ≥ 2L²/λ, well above the ground, or use the Phaser's HB100 on a tripod; log the source angle with a protractor or a phone compass.
- **Compute budget**: KrakenSDR's DOA runs on a Raspberry Pi 4/5; 5 × 2.4 MS/s × 8-bit IQ ≈ 192 Mb/s — fine. Multi-Pluto arrays at high rates need decimation on the FPGA ([FPGA for SDR](../14-sdr-dsp/fpga-for-sdr.md)).

## Printed series-fed patch and comb-line arrays

*Added 2026-10-13 (W5-S9, gap G-12-03). Verified by `tools/verify/s9_series_fed_squint.py` (ALL PASS). The microstrip model is quasi-static (Hammerstad–Jensen, no dispersion); confirm final dimensions in openEMS.*

**Intuition.** A corporate feed splits power in a tree, with many lines and junctions, each adding loss. A **series-fed** array strings the patches along *one* microstrip line like beads. If they sit exactly one guided wavelength λg apart, every patch is excited in phase at the design frequency and the column beams broadside. A **comb-line** array uses narrow radiating stubs on the side of a straight feed line instead of in-line patches. Both are compact, low-loss columns. They are why the antennas on 24, 60 and 77 GHz radar boards look like rows of little rectangles. The column usually forms the narrow **elevation** beam, while the radar chip's TX/RX channels form the azimuth beam digitally (MIMO, [11 MIMO](../11-radar/mimo-radar-virtual-arrays.md)). TI's xWRL1432BOOST-BSD, for example, uses GCPW-fed series patch antennas on RO3003 with ≈ 13 dBi [15]. The catch is that the phase between patches is set by line length, so **the beam squints with frequency**, just as a phase-steered array does ([beam steering](beam-steering-grating-lobes.md)).

**Two flavours.** A **resonant (standing-wave)** array is open-ended, with the last patch near a voltage maximum. It matches only near $f_0$, and the forward and reflected waves make the pattern symmetric. A **travelling-wave** array ends in a matched load, or its last element radiates what is left. It is broader-band, but its beam moves with frequency. A **centre-fed** column (two halves fed in phase) cancels the squint, because the halves squint in opposite directions.

**Level 1 — design equations.**

| Quantity | Equation | Example (script) |
|---|---|---|
| Element spacing for broadside | $d = \lambda_{g0} = c/(f_0\sqrt{\varepsilon_{eff}})$ (< λ0, so no grating lobe) | 24.125 GHz, RO4350B 0.254 mm: ε_eff 2.86, **7.35 mm**; 78.5 GHz, RO3003 0.127 mm: ε_eff 2.42, **2.45 mm** |
| Patch size | $L \approx c/(2f\sqrt{\varepsilon_{eff,p}}) - 2\Delta L$ (Hammerstad ΔL) | 24.125 GHz: W 4.07 × L 3.16 mm; 60.5 GHz RO3003: 1.75 × 1.37 mm; 78.5 GHz: 1.35 × 1.04 mm |
| Travelling-wave squint | $\sin\theta = \sqrt{\varepsilon_{eff}}\,(1 - f_0/f)$; rate ≈ $\sqrt{\varepsilon_{eff}}/f_0$ rad/Hz | **±0.50°** over 24.00–24.25 GHz (4.0°/GHz); −5.5 / +4.9° over 57–64 GHz (1.47°/GHz); −2.9 / +2.8° over 76–81 GHz (1.14°/GHz) |
| Column beamwidth | HPBW ≈ 0.886 λ0/(N d) | 8 patches at 24 GHz: 10.7°, 59 mm long; 12 at 78.5 GHz: 6.6° |

**Level 2 — where the squint comes from.** With $d = \lambda_{g0}$, the line phase between neighbours is $\beta d = 2\pi f/f_0$ (non-dispersive line). The free-space path difference towards θ is $k_0d\sin\theta$. The beam forms where these differ by a whole cycle, $k_0d\sin\theta = \beta d - 2\pi$. Substituting $k_0d = 2\pi f/(f_0\sqrt{\varepsilon_{eff}})$ gives $\sin\theta = \sqrt{\varepsilon_{eff}}(1 - f_0/f)$. The array-factor peak of a 12-element column agrees to 0.01° at every band edge. Two consequences:
- At 24 GHz the 250 MHz band is only 1 % wide, so squint (±0.5°) is negligible next to a 10° beam.
- A 77–81 GHz FMCW chirp sweeps 5.7° of squint during every ramp, about one beamwidth of a 12-element column. That is fine for a wide elevation fan, a real loss for a narrow pencil beam, and a reason to centre-feed. A centre-fed 2 × 6 column holds the beam at broadside and loses only **0.51 dB** at 76 and 81 GHz.
Microstrip dispersion raises ε_eff with frequency at mm-wave and slightly increases the squint; simulate it.

**Level 2 — reflections add up at broadside.** At exactly $d = \lambda_{g0}$ the small reflection of every element returns in phase, so twelve elements of |Γ| = 0.05 each give $|\Gamma_{in}| \approx 0.60$ (−4.4 dB return loss). Detuning the spacing to 0.97 λg0 tilts the beam by −2.8° and spreads the reflection phases: 0.21 (−13.7 dB). At 0.94 λg0 (−5.7°) it is 0.13 (−17.5 dB). That is why automotive comb-line antennas are often designed a few degrees off broadside, or add a reflection-cancelling slit at each element (Hayashi et al., 27 elements at 76.5 GHz [16]).

**Level 3 — tapering a travelling-wave column.** Each element radiates a fraction $c_n$ of the power *arriving* at it. To radiate element powers $p_n$ (with $\sum p_n = 1 - P_{load}$),
$$c_n = \frac{p_n}{1 - \sum_{m<n}p_m}.$$
For a −25 dB Chebyshev amplitude (N = 10: 0.395 0.506 0.721 0.899 1 1 0.899 0.721 0.506 0.395) with 5 % into the load: $c_n$ = 0.027, 0.046, 0.097, 0.167, 0.248, 0.330, 0.399, 0.426, 0.365, 0.351 (the pattern check gives −25.0 dB sidelobes). Coupling is set by patch width (radiation conductance) in a series patch array, or by stub width and length in a comb-line. The last elements must radiate 35–43 % of what reaches them, which is hard with a single narrow patch, so designers trade a little more load power for realisable widths. Element insertion phase changes with width, so each spacing has to be re-tuned in an EM solver.

**Practical notes.**
- **Substrate.** Dielectric line loss (Pozar quasi-static) is 0.22 dB/mm on FR-4 at 77 GHz, so a 25 mm column loses ≈ 5 dB in the dielectric alone. RO3003 gives 0.010 dB/mm, and RO4350B at 24 GHz 0.012 dB/mm. Use a PTFE/ceramic laminate for 24–77 GHz radiating layers (a thin RF layer on an FR-4 core in a hybrid stackup, as TI's EVMs do); [JLCPCB RF manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md).
- **Feed.** A GCPW launch from the radar chip transitions to microstrip; keep the transition and the first patch clear of the chip's ground vias. A NanoVNA cannot reach 24 GHz, so verify with the radar itself. Put a corner reflector at a known elevation, step the chirp's start frequency, and record the elevation of the peak: the squint law appears directly.
- **Learning path.** First a 2.4 GHz FR-4 series column (λg ≈ 66 mm; NanoVNA-measurable), then a 24 GHz column on RO4350B for an IPM-165/BGT24-class front end, then 60/77 GHz following a TI or Infineon reference layout.

## Common mistakes & misconceptions
- **"A series-fed patch array has a fixed beam."** A travelling-wave column squints by ≈ √ε_eff·Δf/f0 rad: about 1° per GHz at 77 GHz, comparable to the beamwidth over a 4 GHz chirp. Centre-feed it if that matters.
- **"Spacing the patches exactly one guided wavelength apart is always best."** It also makes every element reflection add in phase (N·|Γe| at the input); a slight off-broadside design or per-element reflection cancellation fixes the match.
- **"An array will give our LoRa ground station more range."** The link is rarely gain-limited in free space; pointing, nulls and regulations dominate. A tracking Yagi or diversity dipoles are simpler.
- **"Two SDRs sharing a 10 MHz reference are an array."** They need phase calibration after every retune and sample alignment ([calibration](array-calibration.md)).
- **"The KrakenSDR noise source calibrates the antennas."** It calibrates from its input switches onward; antenna cables and positions must be matched/measured.
- **Using a ULA for 360° DF** — front/back ambiguity; use a UCA or two orthogonal ULAs.
- **Spacing whips > λ/2 "for accuracy"** without an ambiguity-resolution scheme.
- **Testing a 5.8 GHz panel at 1 m** (near field for L = 0.2 m is < 1.7 m) and calling the pattern wrong.
- **Buying a Phaser to track a 433 MHz rocket** — it is a 10 GHz learning platform, not a telemetry front end.
- **Scanning to ±70° with a flat panel** and blaming the software for the 5 dB loss — that's scan loss ([beam steering](beam-steering-grating-lobes.md)).

## How to simulate / verify
- `tools/verify/array_diy.py` (< 1 s): aperture/element counts vs gain and band, link budgets for the Space Bar radios and a 5.8 GHz video link, rocket elevation-rate kinematics, DF cross-range and two-station triangulation errors, two-element interferometer ambiguity and calibration sensitivity.
- `tools/verify/s9_series_fed_squint.py` (< 1 s, **ALL PASS**): ε_eff and patch sizes, squint formula vs array factor at 24/60/77 GHz band edges, centre-fed loss, broadside reflection build-up, travelling-wave coupling taper, feed-line loss.
- The other `tools/verify/array_*.py` scripts reproduce every design step: pattern (`array_factor.py`), scan limits (`array_steering.py`), coupling (`array_planar.py`), tapers (`array_taper.py`), architectures (`array_architecture.py`), components (`array_components.py`), calibration (`array_calibration.py`), DOA (`array_doa.py`).
- Phaser: ADI's Python labs and PySDR's Phaser chapter [5]; KrakenSDR: record 5-channel IQ and run `array_doa.py`-style MUSIC offline to compare with its built-in DOA.

## Open questions / gaps
- No field-measured KrakenSDR bearing-accuracy statistics at 433 MHz were found; the 2–5° field figure is an engineering estimate (low confidence) — worth measuring at a Space Bar launch.
- The Phaser's price (≈ US$2,875) and KrakenSDR's (≈ US$750) come from distributor/vendor listings via search and the SDR survey (2026-09); verify before buying.
- Pluto Rev C/D 2R2T coherence quality and the MIT/Charvat switched-array radar's exact parameters were not taken from primary documents.
- Series-fed section: quasi-static microstrip model (no dispersion, no conductor/roughness loss); element reflections (|Γe| = 0.05) are illustrative, not simulated; the Hayashi paper was read as abstract only.
- Details of the 20-projects "phased-array starter build" recipe are left to that domain; this page gives the options and the maths.

## Sources
1. KrakenRF, *KrakenSDR documentation wiki* (Home; Web Interface Controls; mapping apps), github.com/krakenrf/krakensdr_docs/wiki, and Crowd Supply campaign page — 5 × R820T2/RTL2832U, shared clock, software-activated noise source + switches, correlation vs CH0, 24–1766 MHz, 2.56 MHz BW, 1 ppm, ≈ 11 W. (vendor docs)
2. KrakenRF, KrakenSDR wiki "04. Antenna Array Setup" — UCA/ULA, spacing multiplier 0.2–0.5, radius formula, cable-length tolerance, ground-plane advice. (vendor docs)
3. RTL-SDR.com, *KerberosSDR Quickstart Guide* (rtl-sdr.com/ksdr) and product descriptions — 4 × R820T2, 24 MHz–1.7 GHz, 2.4 MS/s 8-bit, switchable noise source, disconnect antennas when synchronising, run Linux natively. (vendor docs)
4. Analog Devices, *ADALM-PHASER (CN0566) Phased Array Exploration Platform* wiki and CN0566 circuit note, wiki.analog.com / analog.com. (app note)
5. M. Lichtman, *PySDR*, ch. "Hands-on with Phaser," pysdr.org — 8 elements, 14 mm, ≈ 10.25 GHz, HB100 source, ADF4159, LTC5548 to ≈ 2 GHz, 2 × ADAR1000 → Pluto's 2 RX channels, calibration files. (tutorial)
6. DigiKey product listing EVAL-CN0566-RPIZ (via search, 2026-09) — ≈ US$2,875. (distributor)
7. KB page [ISM band plans & duty cycle](../15-lora-ism-radios/ism-band-plans-duty-cycle.md) — Singapore 433 MHz 10 mW e.r.p.; 30 km margin example. (internal)
8. KB page [Patch antennas](../08-antennas/patch-antennas.md) — FR-4 patch efficiency and dimensions at 2.45/5.8 GHz. (internal)
9. G. L. Charvat, *Small and Short-Range Radar Systems*, CRC Press, 2014 — switched-array and phased-array radar builds. (textbook)
10. G. L. Charvat et al., MIT IAP 2012 "Build a small phased array radar" course page (sites.google.com/view/glcharvat) and MIT Professional Education "Build a multi-channel search and track radar" — pegboard + Wi-Fi-antenna phased-array imaging radar. (course pages)
11. KB page [SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md) — 2026-09 prices and specs (Pluto US$250, B210 US$2,387, KrakenSDR US$749–775). (internal)
12. Analog Devices, *ADAR1000* data sheet Rev. B — 20 ns beam switching, 121 stored beams. (datasheet)
13. Analog Devices EngineerZone threads "Pluto Rev C how to activate the 2nd Rx channel" and ADI HDL Pluto project docs; plutoplus GitHub issue #66 — 2R2T mode on Rev C/D and clones. (forum — anecdotal / vendor docs)
14. `tools/verify/array_diy.py` — numbers marked "script". (own verification)
15. Texas Instruments, xWRL1432BOOST-BSD EVM user's guide, SWRU619A (2024) — antennas are high-gain series-fed patch arrays fed by grounded coplanar waveguide on Rogers RO3003, ≈ 13 dBi. (vendor user guide; via search summary)
16. Y. Hayashi, K. Sakakibara, M. Nanjo, S. Sugawa, N. Kikuma, H. Hirayama, "Millimeter-wave microstrip comb-line antenna using reflection-canceling slit structure," *IEEE Trans. Antennas Propag.* 59(2):398–406, 2011, doi:10.1109/TAP.2010.2096180 — λg spacing makes element reflections add in phase at broadside; per-element slit; 27-element 76.5 GHz array. (peer-reviewed; abstract)
17. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012, §3.8 — microstrip ε_eff and dielectric attenuation α_d; Hammerstad–Jensen formulas (via [03 planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)). (textbook)
18. `tools/verify/s9_series_fed_squint.py` — series-fed section numbers. (own verification)
