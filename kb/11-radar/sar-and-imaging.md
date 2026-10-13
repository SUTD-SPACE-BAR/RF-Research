---
title: SAR and radar imaging — synthetic aperture principle, stripmap D/2 resolution, range–Doppler and backprojection algorithms, ISAR, DIY SAR, mmWave near-field imaging
domain: 11-radar
slug: sar-and-imaging
tags: [sar, synthetic-aperture, stripmap, spotlight, cross-range-resolution, backprojection, range-doppler-algorithm, omega-k, range-migration, autofocus, isar, rail-sar, drone-sar, coffee-can-sar, mmwave-imaging, near-field-imaging, grating-lobes, doppler-beam-sharpening, dbs, rf-camera, diffraction-limit, mechanical-scan, hits-per-scan, ppi, aperture-outline, octagonal-array, circular-array]
prerequisites:
  - fmcw-radar.md
  - pulsed-radar-and-pulse-compression.md
  - ambiguity-function-waveforms.md
related:
  - mimo-radar-virtual-arrays.md
  - diy-radar-hardware.md
  - clutter-and-mti.md
  - ../12-phased-arrays/array-factor-linear-arrays.md
  - ../12-phased-arrays/beam-steering-grating-lobes.md
  - ../08-antennas/antenna-fundamentals.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# SAR and radar imaging

## Questions this page answers
- How can a small moving antenna produce images as sharp as a huge one?
- Why is stripmap SAR cross-range resolution D/2, independent of range and wavelength?
- What limits range and cross-range resolution in a rail or drone SAR?
- How far apart can the measurement positions be along the track (and what happens if they are too far)?
- What are backprojection, range–Doppler and ω-k (range-migration) image formation, and which should I use?
- What is range migration and why does it matter at short range?
- What is ISAR and how does target rotation give cross-range resolution?
- How did the MIT coffee-can radar and Henrik Forstén's projects do DIY SAR?
- Can I image objects with a TI mmWave board on a scanner?
- What is Doppler beam sharpening and how much does it sharpen a real beam?
- How sharp can an "RF camera" or Wi-Fi imaging radar ever be?
- How many hits per scan does a rotating radar get?
- Why are big phased arrays octagonal or circular rather than square?

## TL;DR
- **Synthetic aperture:** move a radar along a path, record the (range-compressed) echoes coherently at many positions, and sum them with the phase each pixel would produce. The path length $L$ acts like an antenna of length $2L$ (two-way phase), giving **cross-range resolution $\delta_{cr} = \lambda R/(2L)$** (−3 dB width 0.886 × that for a uniform aperture). Range resolution stays $c/(2B)$.
- **Verified by backprojection** (10 GHz, 1.5 GHz sweep, 1.5 m rail at λ/4 steps, target at 5 m): **4.43 cm cross-range, 8.85 cm range** — exactly 0.886λR/2L and 0.886c/2B.
- **Stripmap:** a real antenna of length $D$ illuminates a target over $L_{sa} \approx \lambda R/D$, so $\delta_{cr} \approx D/2$ — **independent of range and wavelength**, and *smaller antennas give finer resolution*. Precisely: the two-way pattern weighting makes the point-spread function a triangle with zeros at ±D/2 (so D/2 is the null-to-peak "Rayleigh" figure) and a −3 dB width of ≈ 0.36 D (simulated: 3.56 cm for D = 10 cm at both 5 m and 10 m).
- **Sampling:** record at least every **λ/4** along track for a wide beam (every ≈ D/4–D/2 for an antenna of length D). At λ spacing a grating-lobe ghost appeared at sin θ = λ/(2Δu) (30°) at −16 dB (the wide bandwidth smears it); at λ/4 nothing exceeded −38 dB.
- **Algorithms:** **time-domain backprojection** (exact for any path, easy, O(N³)); **range–Doppler** and **ω-k / range-migration** (FFT-based, fast, need a straight uniform path); **autofocus** fixes residual path errors, which must be ≪ λ/8 (≈ 4 mm at 10 GHz, 0.5 mm at 77 GHz).
- **ISAR:** the *target* rotates by Δθ instead of the radar moving: $\delta_{cr} = \lambda/(2\Delta\theta)$ — 3.7 cm for 3° at 77 GHz.
- **DIY:** MIT coffee-can rail SAR (2.4 GHz, ~90 MHz sweep: ~1.7 m range, ~0.6 m cross-range at 20 m with a 2 m rail); Forstén's 6 GHz FMCW bicycle/drone SAR with ω-k and backprojection plus autofocus [4]; TI IWR1443 on an x–y rail for near-field concealed-item imaging at 77–81 GHz [5].

- **Real-beam limits:** DBS sharpens a beam to δθ = λ/(2vT sinθ) (X-band, 100 m/s, 50 ms, 45°: 0.24°, ×12) but is blind ahead; a static aperture never beats λ/D (77 GHz, 10 cm: 2.2°, 0.39 m at 10 m); a rotating radar gets n = θ_B·PRF/(6 rpm) hits (≈ 8 for 1.2°, 1 kHz, 24 rpm); a circular outline saves ≈ 21 % of a square's elements for 0.6 dB under a taper ([section](#real-beam-imaging-limits-doppler-beam-sharpening-rf-cameras-mechanical-scanning-and-aperture-outlines)).

## Intuition (no math)
A real antenna's angular resolution is roughly wavelength divided by antenna size: to see fine detail from far away you need a big antenna. SAR builds the big antenna in time instead of in metal. The radar moves along a line, and at each position it records the echo's exact phase. A point on the ground produces a characteristic pattern of phases along the path (the distance to it first shrinks, then grows — a hyperbola). Adding all recordings together after undoing the phase each specific pixel would have produced makes echoes from that pixel add up and those from elsewhere cancel. The result is the resolution of an antenna as long as the path — but because the phase delay is two-way, it behaves like one *twice* as long.

In stripmap mode, a small antenna has a wide beam, so each point stays in view over a longer stretch of the flight path — a longer synthetic aperture exactly compensates the wider beam, and resolution comes out as half the antenna size, whatever the range. It is one of the few places in radar where smaller hardware gives sharper images (at the cost of more data and SNR).

ISAR flips the geometry: the radar is still, the target turns (a ship rolling, a satellite spinning, a car on a turntable), and the changing aspect produces the same phase history.

## The math

### Level 1 — resolution and sampling
- Range resolution: $\delta_r = c/(2B)$ (see [FMCW](fmcw-radar.md), [pulse compression](pulsed-radar-and-pulse-compression.md)).
- Cross-range resolution for synthetic aperture length $L$ at range $R$: $\delta_{cr} = \dfrac{\lambda R}{2L}$ (Rayleigh); uniform-aperture −3 dB width 0.886 $\lambda R/(2L)$.
- Equivalently, for an angular aperture Δθ (spotlight or ISAR): $\delta_{cr} = \lambda/(2\Delta\theta)$.
- Stripmap with antenna length $D$: $L_{sa} = \lambda R/D$ ⇒ $\delta_{cr} = D/2$.
- Along-track sampling: two-way phase changes by $4\pi\Delta u\sin\theta/\lambda$ between positions; no aliasing over the whole illuminated angular range requires $\Delta u \le \lambda/(4\sin\theta_{max})$ — λ/4 for ±90°, ≈ D/4 for a beam of width λ/D.

### Level 2 — derivations

**Phase history of a point target.** Radar at along-track position $u$, target at $(x_0, R_0)$: $R(u) = \sqrt{R_0^2 + (u - x_0)^2} \approx R_0 + \frac{(u-x_0)^2}{2R_0}$. After range compression, the echo phase is $\phi(u) = -4\pi R(u)/\lambda$: a quadratic (chirp) in $u$ — the along-track "Doppler chirp" with spatial chirp rate $-2/(\lambda R_0)$ (in cycles/m²) and instantaneous spatial frequency $k_u = -2(u - x_0)/(\lambda R_0)$ (cycles/m). Over an aperture $L$ the spatial-frequency span is $\Delta k_u = 2L/(\lambda R_0)$, so matched filtering in $u$ (pulse compression in the along-track dimension) resolves $\delta_{cr} = 1/\Delta k_u = \lambda R_0/(2L)$. In time with platform speed $v$: Doppler bandwidth $B_d = 2vL/(\lambda R_0)$ and $\delta_{cr} = v/B_d$ — the Doppler view of SAR [1], [2].

**Stripmap D/2.** The one-way beamwidth of an antenna of length $D$ is ≈ λ/D, so a point stays in the beam over $L_{sa} = \lambda R/D$; substituting, $\delta_{cr} = \lambda R/(2\lambda R/D) = D/2$. A finer statement: the two-way amplitude pattern $\mathrm{sinc}^2(D\sin\theta/\lambda)$ weights the aperture; since the image is (approximately) the Fourier transform of that weighting in the variable $2\sin\theta/\lambda$, the point-spread function is a **triangle of half-width D/2**. Its −3 dB full width is $2(1 - 1/\sqrt2)\,D/2 = 0.29D$ for untruncated weighting; with the aperture truncated at the first sidelobe the simulation gives 0.356 D (3.56 cm for D = 10 cm) at both 5 m and 10 m — range-independent, as predicted.

**Backprojection (time-domain) [3].** For each pixel $\mathbf r$ and each position $u_i$: compute $R_i(\mathbf r)$, interpolate the range-compressed profile $p_i$ at $R_i$, multiply by $e^{+j4\pi f_0R_i/c}$ (undo the carrier phase), and sum:
$$I(\mathbf r) = \sum_i p_i\big(R_i(\mathbf r)\big)\,e^{\,j4\pi f_0R_i(\mathbf r)/c}.$$
It is exact for any trajectory (rail, bicycle, drone with GNSS/INS) and any geometry (near field, wide angle, wideband), and trivially parallel on a GPU; cost ≈ (pixels × positions). The script uses exactly this (with a 16× oversampled range profile and linear interpolation).

**FFT-based algorithms.** For a straight, uniformly sampled path:
- **Range–Doppler algorithm (RDA):** range compression → azimuth FFT → range-cell-migration correction (RCMC, interpolation along range per Doppler frequency) → azimuth matched filter → inverse FFT. Efficient for narrow beams / long ranges.
- **ω-k (range-migration, "wavenumber") algorithm:** 2-D FFT to $(k_r, k_u)$, reference-function multiply, **Stolt interpolation** mapping $k_y = \sqrt{4k^2 - k_u^2}$, inverse 2-D FFT. Exact for straight paths including wide beams and near field; the MIT coffee-can course and Forstén's first bicycle SAR used it [4], [6].
- **Polar-format (spotlight)**, chirp scaling — variants for particular geometries.

**Range migration.** The target's range varies over the aperture by $\Delta R \approx L^2/(8R_0)$ (for a centred aperture); if $\Delta R > \delta_r$, the target migrates through range cells and 1-D (separable) processing fails. The 1.5 m / 5 m rail example: ΔR ≈ 5.6 cm vs 10 cm cells — borderline; short-range, wide-beam DIY SAR almost always needs backprojection or ω-k.

### Level 3 — motion errors, ISAR, near-field imaging, limits

**Motion errors and autofocus.** An unknown path deviation $\delta(u)$ along the line of sight adds phase $4\pi\delta/\lambda$; to keep defocus small, $|\delta| \ll \lambda/8$ (a quarter-wave two-way phase budget): ≈ 3.7 mm at 10 GHz, 1.6 mm at 24 GHz, 0.5 mm at 77 GHz. Consumer GNSS/INS cannot do this, so drone and bicycle SAR rely on **autofocus**: phase-gradient autofocus (PGA), map-drift, or optimisation of an image-sharpness metric over trajectory parameters — Forstén used automatic-differentiation-based autofocus with backprojection [4]. Rails and CNC gantries avoid the problem mechanically.

**ISAR.** A target rotating by Δθ during the coherent interval gives $\delta_{cr} = \lambda/(2\Delta\theta)$: 3° at 77 GHz → 3.7 cm; 5° at 10 GHz → 17 cm; 20° at 2.4 GHz → 18 cm (computed). The image is a range–Doppler map (Doppler ∝ cross-range position × rotation rate), so the rotation rate must be known to scale the cross-range axis, and non-uniform rotation smears it. A turntable ISAR at 24 or 77 GHz is an excellent way to *measure RCS and scattering centres* of a hobby rocket airframe (see [RCS](radar-cross-section.md)).

**Near-field mmWave imaging.** With a TI 77–81 GHz board (4 GHz sweep → 3.75 cm range resolution) raster-scanned on a two-axis rail, Yanik & Torlak formed 2-D/3-D near-field images of concealed objects using the ω-k family of algorithms [5]. At 77 GHz λ/4 sampling is ≈ 1 mm — scanner accuracy and data volume, not radar hardware, are the constraints; MIMO virtual arrays (12 channels per board) reduce the number of mechanical steps (see [MIMO](mimo-radar-virtual-arrays.md)).

**Limits.** SNR per pixel improves with the number of coherently summed looks ($N_{pos}$ × chirps); speckle (coherent interference of many scatterers in a pixel — the same statistics as Swerling 1) makes SAR images grainy and is reduced by multi-look averaging at the cost of resolution; layover and shadowing occur for elevated terrain; moving objects are displaced in azimuth (a moving car appears off its road) because their Doppler adds to the geometric Doppler.

## Design equations & rules of thumb

| Equation / rule | When valid | Example |
|---|---|---|
| $\delta_r = c/(2B)$ | any | 1.5 GHz → 10 cm |
| $\delta_{cr} = \lambda R/(2L)$ (−3 dB: × 0.886) | full-aperture / spotlight / rail | 10 GHz, 1.5 m, 5 m → 5 cm (4.43 cm −3 dB) |
| $\delta_{cr} = D/2$ (null-to-peak), ≈ 0.3–0.36 D (−3 dB) | stripmap, antenna length D | 10 cm antenna → 5 cm / 3.6 cm |
| $\delta_{cr} = \lambda/(2\Delta\theta)$ | ISAR / angular aperture | 77 GHz, 3° → 3.7 cm |
| $\Delta u \le \lambda/4$ (wide beam) | along-track sampling | 10 GHz → 7.5 mm; 77 GHz → 0.97 mm |
| Path error $\ll \lambda/8$ | focusing | 77 GHz → < 0.5 mm |
| Range migration $\Delta R \approx L^2/(8R)$ | compare with $\delta_r$ | 1.5 m / 5 m → 5.6 cm |
| Doppler bandwidth $B_d = 2vL/(\lambda R)$ | moving platform | $\delta_{cr} = v/B_d$ |
| DBS $\delta\theta = \lambda/(2vT\sin\theta)$ | unfocused, $\delta x > \sqrt{\lambda R/2}$ | X-band 100 m/s 50 ms 45° → 0.24° |
| Real aperture $\lambda/D$, ≈ $2D/\lambda$ beams per axis | RF camera | 77 GHz 10 cm → 2.2° |
| Hits per scan $\theta_B\mathrm{PRF}/(6\,\mathrm{rpm})$ | rotating antenna | 1.2°, 1 kHz, 24 rpm → 8.3 |

## Worked examples

**Example 1 — Rail SAR at 10 GHz (verified in the script).** 1.5 GHz sweep, 1.5 m rail, 200 positions at 7.5 mm, point target at 5 m: backprojected image −3 dB widths 4.43 cm × 8.85 cm, target placed within 1 mm. A garden-shed-scale imaging radar with an ADI Phaser-class 10 GHz front end (or an HB100 upgraded to FMCW) is realistic: the sweep bandwidth and rail accuracy (< 4 mm) are the key specifications.

**Example 2 — Coffee-can rail SAR.** 2.44 GHz (λ = 12.3 cm), ~90 MHz sweep, 2 m rail, scene at 20 m: range 1.67 m, cross-range λR/2L = 0.61 m, positions every ≤ 3.1 cm (λ/4). The course used a tape-measured rail stepped by hand and the ω-k algorithm [6]; the VCO nonlinearity ([FMCW](fmcw-radar.md)) blurs range further at the far edge of the scene.

**Example 3 — Drone SAR budget.** A 6 GHz FMCW radar (λ = 5.0 cm) with a 5 cm patch antenna (stripmap cross-range D/2 = 2.5 cm; 1 GHz sweep → 15 cm range) on a drone at 10 m/s, slant range 20 m: the synthetic aperture is $L_{sa} = \lambda R/D$ = 20 m, i.e. 2 s of flight, over which the line-of-sight path error must stay below λ/8 ≈ 6 mm. GNSS alone cannot do that, hence autofocus [4].

**Example 4 — Measuring your rocket's scattering centres by ISAR.** Put the airframe on a turntable 5 m from a 77 GHz TI board (3.75 cm range resolution with 4 GHz), rotate 10° (λ/2Δθ = 1.1 cm cross-range) while recording chirps: the ISAR image shows which parts (nozzle, fin roots, avionics bay) dominate the RCS — exactly the data missing from the [RCS page](radar-cross-section.md).

## Practical notes
- **Record raw data** (complex IF samples per position, plus positions/timestamps); image formation is post-processing. TI boards need a DCA1000 for raw capture.
- **Triggering:** synchronise each chirp/frame to the position (stepper steps, encoder, or GNSS time). Stop-and-go is easiest on rails; continuous motion needs the along-track motion during a chirp to be ≪ λ/4.
- **Calibration:** image a corner reflector first to set range offset (cable/IF delays) and check focus.
- **Compute:** backprojection of 10⁶ pixels × 10³ positions = 10⁹ interpolations — seconds on a GPU, minutes in NumPy; use FFT-based ω-k for large scenes on straight tracks.
- **Legal/safety:** a moving transmitter must still meet band and EIRP limits (e.g. 24.00–24.25 GHz ≤ 100 mW EIRP in Singapore, IMDA TS SRD Sep 2023; 77–81 GHz rail imagers fall under the UWB exemption, mean ≤ −3 dBm/MHz — [DIY radar](diy-radar-hardware.md)); drone flights have their own CAAS rules.

## Real-beam imaging limits: Doppler beam sharpening, "RF cameras", mechanical scanning and aperture outlines

*Added 2026-10-13 (W5-S9, gap G-11-04). Numbers verified by `tools/verify/s9_imaging_limits.py` (ALL PASS).*

**Intuition.** Without a synthetic aperture, angular detail comes from only two places: the size of the real antenna (λ/D) and Doppler, if the radar is moving. Doppler beam sharpening is "SAR lite": it uses the Doppler spread across a real beam, without focusing. An "RF camera" (a static imaging array) can never beat λ/D, which is why mm-wave images are blurry next to optical ones. A mechanically scanned radar trades revisit time against dwell. The outline of a large array (square, octagon, circle) is an engineering trade between elements (cost) and sidelobes, not aesthetics.

**Doppler beam sharpening (DBS).** A platform moving at $v$ sees a scatterer at angle θ from its velocity vector with Doppler $f_D = (2v/\lambda)\cos\theta$, so $|df_D/d\theta| = (2v/\lambda)\sin\theta$. A coherent dwell $T$ resolves $\Delta f = 1/T$, so
$$\delta\theta = \frac{\lambda}{2vT\sin\theta},\qquad \delta x = R\,\delta\theta,\qquad \text{sharpening ratio} = \theta_{beam}/\delta\theta .$$
The same physics as SAR (δx = λR/2L with $L = vT$ at broadside) applies without range-migration or phase-history correction, so DBS is valid only while the synthetic aperture stays *unfocused*. Below $\delta x \approx \sqrt{\lambda R/2}$ you need full SAR focusing. Numbers: X-band aircraft (λ = 3 cm, 100 m/s, T = 50 ms, 45°): δθ = **0.243°**, a ×12.3 sharpening of a 3° beam, 42 m at 10 km (real beam 524 m; unfocused limit 12 m). 77 GHz car (20 m/s, 20 ms, 60°): 0.32°, ×62, 0.17 m at 30 m, *below* the 0.24 m unfocused limit, so it needs focusing. Resolution degrades as $1/\sin\theta$: ×2 at 30° and ×11.5 at 5° from the velocity vector, so DBS is **blind straight ahead**. That is the notch in airborne DBS maps and why automotive radars lean on the antenna array for the forward sector.

**"RF camera" limits.** A static aperture of size $D$ resolves about λ/D in angle (λR/D cross-range) and has about $2D/\lambda$ resolvable beams per axis over ±90° (about as many as λ/2 elements), plus range bins $c/2B$ as the third dimension.

| Aperture | λ/D | beams per axis | cross-range |
|---|---|---|---|
| 77 GHz, 10 cm | 2.2° | ≈ 51 | 0.39 m at 10 m |
| 77 GHz TI EVM, 12 virtual channels (≈ 6λ) | 9.5° | ≈ 12 | 1.7 m at 10 m |
| 60 GHz BGT60, 3 RX (≈ λ) | 57° | ≈ 2 | 2 m at 2 m |
| 2.4 GHz Wi-Fi "camera", 30 cm | 23° | ≈ 5 | 2 m at 5 m |
| 10 GHz, 1 m | 1.7° | ≈ 67 | 30 m at 1 km |

Matching a 1 mrad phone-camera pixel at 77 GHz needs a 3.9 m aperture. Through-wall and Wi-Fi "imaging" claims at 2.4/5 GHz are therefore detection and localisation at metre scale, not pictures. A MIMO virtual array extends the aperture to about $D_t + D_r$ ([MIMO](mimo-radar-virtual-arrays.md)), and mechanical or synthetic motion (this page) extends it further. Near-field focusing changes the geometry but not the λ/aperture scaling.

**Mechanically scanned radars.** A beam of width $\theta_B$ (degrees) rotating at rpm revolutions per minute dwells $\theta_B/(6\cdot\mathrm{rpm})$ seconds on a point target, which collects
$$n = \frac{\theta_B\,\mathrm{PRF}}{6\,\mathrm{rpm}}$$
pulses per scan [3]. Small marine X-band (1.9°, 1 kHz, 24 rpm): 13 hits in 13 ms, 2.5 s revisit. A 1.2° open array: **8.3 hits**. Airport surveillance (1.4°, 1 kHz, 15 rpm): 15.6 hits, 4 s revisit. The scan sets a dwell of a few ms, which caps Doppler resolution (and hence MTI quality), and the target is visited only once per revolution. Electronic scanning ([12 beam steering](../12-phased-arrays/beam-steering-grating-lobes.md)) removes both limits at the cost of elements. A scan-to-scan **PPI** display ([vocabulary](fmcw-radar.md#radar-timing-and-display-vocabulary)) is the classic output.

**Why large arrays are octagonal or circular.** On a λ/2 grid inside a 32 × 32 bounding square (script):

| Outline | Elements | Directivity uniform / tapered | Peak sidelobe uniform (principal / diagonal) | Tapered (principal) |
|---|---|---|---|---|
| Square | 1024 | 35.07 / 34.07 dBi | −13.2 / −26.5 dB | −23.0 dB |
| Octagon | 844 | 34.23 / 33.55 dBi | −17.7 / −17.3 dB | −23.8 dB |
| Circle | 812 | 34.07 / 33.45 dBi | −17.6 / −17.6 dB | −23.5 dB |

(The taper is radial parabolic-on-pedestal, edge 0.2.) Under any low-sidelobe taper the corner elements carry little weight. Dropping them removes **≈ 21 % of the elements (circle) or ≈ 18 % (octagon) for only 0.6 / 0.5 dB of directivity**, and every element dropped saves a T/R channel, its power and its heat. A uniform square has its −13 dB sidelobes in the two principal planes. A round outline spreads sidelobes evenly (−17.6 dB, the circular-aperture value) in every plane. A circular outline also fits round radomes (fighter noses, the original round Starlink dish: [12 LEO terminal case study](../12-phased-arrays/beamforming-architectures.md#case-study-starlink-class-leo-user-terminal)). The octagon is the compromise that tiles cleanly with rectangular subarray boards.

## Common mistakes & misconceptions
- **"A Wi-Fi or 60 GHz radar can take pictures like a camera."** Angular resolution is λ/D: a 30 cm aperture at 2.4 GHz resolves ≈ 23°, so you get blobs in range bins, not images.
- **"Doppler beam sharpening works in every direction."** Its resolution scales as 1/sinθ, so it is blind along the velocity vector, and it stops working once the needed resolution drops below the unfocused limit $\sqrt{\lambda R/2}$.
- **"SAR resolution gets worse with range like a real antenna."** Stripmap resolution is D/2 at any range (the synthetic aperture grows with range); only SNR and required aperture length scale.
- **"Bigger antenna, better SAR."** In stripmap, the opposite: D/2.
- **Undersampling the aperture** (steps > λ/4 for a wide beam) → ghosts/grating lobes.
- **Ignoring range migration** in short-range DIY SAR and using a separable range–Doppler algorithm without RCMC.
- **Expecting GNSS-grade positions to focus a mm-wave SAR** — errors must be sub-mm to few-mm; autofocus or rails are required.
- **Forgetting that moving objects are displaced in azimuth** in SAR images.

## How to simulate / verify
- `tools/verify/radar_sar.py` (~5 s, **ALL PASS**): stepped-frequency/FMCW-equivalent rail SAR data, time-domain backprojection, measured range/cross-range resolution vs theory, grating-lobe ghost from undersampling, stripmap D/2 range-independence, ISAR numbers.
- Extend with your own trajectory errors (add $\delta(u)$ to $R$) and try a simple phase-gradient autofocus; compare with the error-free image.
- `tools/verify/s9_imaging_limits.py` (< 1 s, **ALL PASS**): DBS resolution/sharpening/unfocused limit, RF-camera diffraction table, hits per scan, square/octagon/circle aperture element counts, directivity and sidelobes.
- Open-source references: Forstén's SAR code and blog [4]; MATLAB's "Simplified 2D mmWave near-field imaging" example [5].

## Open questions / gaps
- ω-k (Stolt) and range–Doppler algorithms are described, not implemented in the script.
- Autofocus methods (PGA, map-drift) not simulated.
- MIT coffee-can SAR parameters (rail length, positions) are approximate.
- Interferometric SAR, polarimetric SAR and GMTI not covered.
- DBS is analysed for a straight, constant-velocity platform only; automotive DBS with yaw and multi-target tracking is not covered.

## Sources
1. M. Soumekh, *Synthetic Aperture Radar Signal Processing with MATLAB Algorithms*, Wiley, 1999 — phase history, ω-k (wavenumber) algorithm, sampling. (textbook)
2. I. G. Cumming, F. H. Wong, *Digital Processing of Synthetic Aperture Radar Data*, Artech House, 2005 — range–Doppler algorithm, RCMC, chirp scaling, stripmap D/2. (textbook)
3. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., 2014, ch. 8 (introduction to SAR, backprojection, resolution); M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed. (SAR material — the earlier "ch. 14" pointer is not in the 3rd-ed. chapter list, ch. 1–11, checked by W5-S18; location unverified) and ch. 2 (hits per scan $n=\theta_B f_p/\dot\theta_s$). (textbook)
4. H. Forstén, "Synthetic-aperture radar imaging" and later posts on backprojection and automatic-differentiation autofocus; 6 GHz FMCW radar design files. https://hforsten.com/synthetic-aperture-radar-imaging.html, https://github.com/Ttl/fmcw3 (project report)
5. M. E. Yanik, M. Torlak, "Near-field 2-D SAR imaging by millimeter-wave radar for concealed item detection," IEEE Radio and Wireless Symposium, 2019 — TI IWR1443 (77–81 GHz, 4 GHz) on a two-axis rail; and "Millimeter-wave near-field imaging with two-dimensional SAR data," 2018. (peer-reviewed)
6. G. L. Charvat, A. J. Fenn, B. T. Perry, "The MIT IAP radar course: Build a small radar system capable of sensing range, Doppler, and synthetic aperture (SAR) imaging," IEEE Radar Conference, 2012; MIT OCW RES.LL-003 (2011) — coffee-can rail SAR with range-migration algorithm. (peer-reviewed / lecture notes)
7. `tools/verify/radar_sar.py` — all simulated numbers. (verification script)
8. `tools/verify/s9_imaging_limits.py` — numbers in the real-beam imaging-limits section (W5-S9). (verification script)
