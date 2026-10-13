# 12-phased-arrays — Phased arrays, beamforming and direction finding

Scope: how arrays of antennas form, steer and shape beams, and how to estimate where signals come from —
from the array factor of a uniform linear array through steering, grating lobes, squint and quantisation,
planar lattices and mutual coupling (active reflection coefficient, scan blindness, Hannan's element-gain
limit), amplitude tapers and error budgets, beamforming architectures (analog/LO/IF/digital/hybrid,
Butler and Rotman), phase shifters/TTD/beamformer ICs, calibration (REV, mutual-coupling, noise-source
coherent-SDR calibration), adaptive beamforming and DOA (MVDR, LCMV, MUSIC, Root-MUSIC, ESPRIT,
spatial smoothing, CRB), and DIY projects at student scale (ADI Phaser, KrakenSDR, coherent SDR arrays,
FR-4 patch arrays, rocket-recovery DF and ground-station tracking). Single antennas (patches, Yagis) live
in [08-antennas](../08-antennas/antenna-fundamentals.md); radar signal processing and MIMO virtual arrays
in [11-radar](../11-radar/mimo-radar-virtual-arrays.md); SDR hardware in
[14-sdr-dsp](../14-sdr-dsp/sdr-hardware-survey.md); part catalogues in
[18-components-parts](../18-components-parts/rf-switches-attenuator-parts.md).

**Conventions used on every page of this domain**: elements at x_n = nd, θ measured from broadside
(array normal), u = sinθ (planar: u = sinθcosφ, v = sinθsinφ), k = 2π/λ, time convention e^{+jωt},
steering weights w_n = a_n e^{−jkx_n u₀}. Balanis measures θ from the array axis (cos instead of sin) —
translate with θ_Balanis = 90° − θ.

## Reading order (beginner → advanced)
1. [array-factor-linear-arrays](array-factor-linear-arrays.md) — the array factor, pattern multiplication, beamwidth, nulls, directivity, array (SNR) gain.
2. [beam-steering-grating-lobes](beam-steering-grating-lobes.md) — steering, visible space, grating lobes, scan loss, squint vs TTD, instantaneous bandwidth, phase-quantisation lobes.
3. [tapering-sidelobe-control](tapering-sidelobe-control.md) — Dolph–Chebyshev, Taylor n̄, windows, taper efficiency, random-error floors, monopulse.
4. [planar-arrays-element-pattern-coupling](planar-arrays-element-pattern-coupling.md) — 2-D lattices, embedded element patterns, active reflection coefficient, scan blindness, Hannan limit.
5. [beamforming-architectures](beamforming-architectures.md) — analog/LO/IF/digital/hybrid, Butler, Rotman, 10 log N, coherence and synchronisation.
6. [phase-shifters-ttd-components](phase-shifters-ttd-components.md) — how phase shifters work, TTD sizing, ADAR1000/ADTR1107 and discrete parts, per-channel budgets.
7. [array-calibration](array-calibration.md) — error sources and budgets, REV, mutual-coupling self-cal, noise-source calibration, beacons.
8. [adaptive-beamforming-doa](adaptive-beamforming-doa.md) — MVDR/LCMV, SMI and diagonal loading, MUSIC/Root-MUSIC/ESPRIT, smoothing, CRB, MDL, UCAs.
9. [diy-phased-array-projects](diy-phased-array-projects.md) — what to build first, rocket-recovery DF, ground-station tracking trade-offs, budgets.
10. [array-pattern-synthesis](array-pattern-synthesis.md) — Schelkunoff zeros, Fourier/Woodward–Lawson shaped beams (sector, csc²), LS and LP min-max synthesis, Bayliss Δ patterns, null steering.
11. [conformal-and-cylindrical-arrays](conformal-and-cylindrical-arrays.md) — element-pattern rotation, wraparound arrays on rocket airframes, commutated cylindrical arrays, polarization on curved surfaces, UCA phase modes, ring DF.
12. [stacking-and-arraying-yagis](stacking-and-arraying-yagis.md) — 2- and 4-Yagi stacks (NEC), stacking-distance formulas, phasing harnesses, H vs V stacking, ground-station trade-offs vs long or crossed Yagis.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [array-factor-linear-arrays](array-factor-linear-arrays.md) | ULA AF derivation, pattern multiplication, far-field 2L²/λ, nulls/sidelobes vs N, HPBW 0.886λ/(Nd cosθ), exact directivity (D = N at λ/2 for any scan), endfire & Hansen–Woodyard (≈1.8×), array/SNR gain, EIRP ∝ N², Schelkunoff, superdirectivity | mixed | high |
| [beam-steering-grating-lobes](beam-steering-grating-lobes.md) | u-space shift, grating-lobe limits (peak and skirt), beam broadening, scan loss, squint sinθ = (f₀/f)sinθ₀, IBW = Θ₃/sinθ₀, TTD & subarray TTD, quantisation lobes 20 log tan(π/2^{P+1}) (≈ −6.02P + 4.4 dB), dither, pointing resolution & error | mixed | high |
| [planar-arrays-element-pattern-coupling](planar-arrays-element-pattern-coupling.md) | 2-D AF, square vs triangular lattice (13.4% saving), Hannan 4πA/λ², embedded element efficiency πd_xd_y/λ², active reflection coefficient (MoM example), embedded patterns, Floquet scan-blindness estimate, edge effects | mixed | medium |
| [tapering-sidelobe-control](tapering-sidelobe-control.md) | taper efficiency, binomial, Dolph–Chebyshev derivation & weights, Taylor n̄ (own implementation), window/pedestal table, random-error floor (σ_a²+σ_φ²)/(Nη), failures, monopulse Σ/Δ, Bayliss, synthesis methods | mixed | high |
| [beamforming-architectures](beamforming-architectures.md) | RF/LO/IF/digital/hybrid, subarrays, Butler (−3.7…−3.9 dB crossovers), Rotman, noise/spur/phase-noise correlation (10 log(N/(1+(N−1)ρ))), LNA-first cascade, coherence/sync, data rates | mixed | medium |
| [phase-shifters-ttd-components](phase-shifters-ttd-components.md) | switched-line, loaded-line (b = tan(Δφ/2)), reflection-type, vector modulator, TTD sizing, ADAR1000 (data sheet), ADTR1107, ADAR4002, HMC64x, QPC2108, PE44820, JSPHS-2484+, AWMF-0108, T/R modules, costs | mixed | medium |
| [array-calibration](array-calibration.md) | error model & accuracy budgets, REV derivation & simulation, noise-source calibration (phase error formula, fractional delay), mutual-coupling self-cal with ±1 gauge ambiguity, beacon/near-field/self-calibration | mixed | medium |
| [adaptive-beamforming-doa](adaptive-beamforming-doa.md) | data model, Bartlett, MVDR derivation, LCMV, SMI/RMB, signal cancellation & diagonal loading, MUSIC/Root-MUSIC/ESPRIT, CRB closed form, resolution tests, spatial smoothing, MDL, UCA vs ULA ambiguity | mixed | high |
| [diy-phased-array-projects](diy-phased-array-projects.md) | project ladder & costs, interferometer, array size vs gain per band, rocket link budgets, tracking kinematics, KrakenSDR recovery DF, Phaser labs, FR-4 panels, switched-array radar | mixed | medium |
| [array-pattern-synthesis](array-pattern-synthesis.md) | Schelkunoff polynomial (cardioid D = 2, arbitrary nulls, off-circle zeros), Fourier sector & Gibbs, Woodward–Lawson (half-amplitude edge −37.8 dB; csc² needs N ≥ 17), LS = Fourier at λ/2, constrained LS, LP min-max reproducing Dolph exactly + null sector, Bayliss from the 1968 polynomial table (sampled −29.3/−30.1/−30.3 dB; 0.3 dB from LP optimum), projection null steering = cancellation beam, error-limited null depth, MVDR equivalence | mixed | high |
| [conformal-and-cylindrical-arrays](conformal-and-cylindrical-arrays.md) | exact 2-D cylinder series (TM vs own MoM 0.016 dB; TE slot limits), element-pattern rotation (1.7 dB pattern-multiplication error), wraparound roll ripple table (54–152 mm tubes, 433 MHz–5.8 GHz, both polarizations; ≲ 0.6λ spacing for < 1 dB), GNSS L1 wraparound, commutated sector (0.09 dB ripple), cross-pol on cylinders/cones, UCA phase modes (KrakenSDR J₀ near zero), Adcock octantal error, pseudo-Doppler | mixed | medium |
| [stacking-and-arraying-yagis](stacking-and-arraying-yagis.md) | G₂/G₁ = 2/(1+ρ) from mutual resistance (NEC within 0.24 dB), PyNEC 433 MHz DL6WU 2-stacks (max +3.07/+3.10 dB; DL6WU spacing +2.94/+3.02 dB, −11/−12 dB lobes), 51/HPBW vs λ/(2 sin(B/2)), 2×2 box +6.02 dB, N in a line, λ/4 75 Ω harness (SWR, bandwidth, tolerance, polarity), electrical tilt, link budget: CP before stacking | mixed | high |

## Domain FAQ (top questions → page#section)
- What element spacing should I use? → [beam-steering-grating-lobes](beam-steering-grating-lobes.md) (TL;DR, Level 2 (b)); printed arrays also [planar arrays](planar-arrays-element-pattern-coupling.md) (scan blindness).
- How narrow is my beam / how much gain? → [array-factor-linear-arrays](array-factor-linear-arrays.md) (Level 1 table, Level 2 (e)(f)).
- Is array gain just 10 log N + element gain? → [array factor](array-factor-linear-arrays.md) (common mistakes) and [planar](planar-arrays-element-pattern-coupling.md) (Hannan limit).
- Why is my matched element mismatched in the array? → [planar arrays](planar-arrays-element-pattern-coupling.md) (Level 2 (c)).
- How many phase-shifter bits do I need? → [beam steering](beam-steering-grating-lobes.md) (Level 2 (g)) and [tapering](tapering-sidelobe-control.md) (example 1).
- Phase shifter or true-time delay? → [beam steering](beam-steering-grating-lobes.md) (Level 2 (d)–(f)); [components](phase-shifters-ttd-components.md).
- How do I get −30 dB sidelobes? → [tapering](tapering-sidelobe-control.md) (Taylor, error budget) and [calibration](array-calibration.md) (accuracy budget).
- Analog or digital beamforming? → [architectures](beamforming-architectures.md).
- Are two SDRs on one 10 MHz reference coherent? → [architectures](beamforming-architectures.md) (Level 2 (e)), [calibration](array-calibration.md).
- Which DOA algorithm, and how accurate? → [adaptive-beamforming-doa](adaptive-beamforming-doa.md) (TL;DR, CRB).
- Why does MUSIC fail with multipath? → [DOA](adaptive-beamforming-doa.md) (Level 2 (h)).
- Can we find our landed rocket with a KrakenSDR? → [DIY projects](diy-phased-array-projects.md) (example 1).
- Phased array or tracking Yagi for the ground station? → [DIY projects](diy-phased-array-projects.md) (Level 2 (c)(d)).
- How do I put a null on an interferer or make a sector/csc² beam? → [pattern synthesis](array-pattern-synthesis.md) (Level 2 (a)–(g)).
- What taper for a monopulse difference pattern (Bayliss)? → [pattern synthesis](array-pattern-synthesis.md) (Level 2 (f), Example 4).
- How many antennas around my rocket body tube for roll-omni coverage? → [conformal arrays](conformal-and-cylindrical-arrays.md) (Level 2 (b) table).
- Why does a KrakenSDR use a circle, and which ring-DF method? → [conformal arrays](conformal-and-cylindrical-arrays.md) (Level 2 (e)–(g)).
- How far apart should I stack two Yagis, and how much gain? → [stacking](stacking-and-arraying-yagis.md) (TL;DR, Level 2 (a)–(d)).
- How is a Starlink-class user terminal built, and do the array formulas reproduce it? → [beamforming architectures § Starlink case study](beamforming-architectures.md#case-study-starlink-class-leo-user-terminal).
- Why does my series-fed (comb-line) patch array squint with frequency? → [DIY arrays § series-fed arrays](diy-phased-array-projects.md#printed-series-fed-patch-and-comb-line-arrays).

## Verification scripts (tools/verify/)
| Script | Checks | Runtime |
|---|---|---|
| `array_factor.py` | AF closed form, HPBW, sidelobes vs N, exact directivity, Hansen–Woodyard, SNR gain, isotropic-noise gain | ~30 s |
| `array_steering.py` | grating-lobe limits, broadening, squint, IBW, subarray TTD, quantisation lobes (FFT search), dither, pointing error | ~4 min |
| `array_planar.py` | lattices, Hannan limit, thin-wire MoM coupling (reuses `ant_mom_wire.py`), Γ_a vs scan, embedded efficiency, TM₀ blindness estimate | ~70 s |
| `array_taper.py` | own Dolph/Taylor vs scipy, windows table, random-error floors, failures, monopulse, realistic 8-element case | ~20 s |
| `array_architecture.py` | DBF noise/spurs, harmonic steering, LO-correlation formula, Butler matrix, analog cascade, sync/data rates | < 1 s |
| `array_components.py` | switched/loaded-line, RTPS range, vector-modulator errors, JSPHS-2484+ nonlinearity, TTD bits, chain NF | < 1 s |
| `array_calibration.py` | REV, noise-source phase/delay estimation, mutual-coupling ALS with gauge check, accuracy budgets | ~20 s |
| `array_doa.py` | Bartlett/MVDR/MUSIC/Root-MUSIC/ESPRIT vs CRB, resolution, smoothing, SMI/RMB, loading, LCMV, MDL, UCA | ~70 s |
| `array_diy.py` | array size vs gain, link budgets, tracking rates, DF geometry, interferometer ambiguity | < 1 s |
| `e8_synthesis.py` | Schelkunoff, Fourier/WL, LS, LP min-max (Dolph check), Bayliss, null steering, MVDR; figures | ~7 s |
| `e8_conformal.py` | cylinder eigenfunction series vs 2-D MoM, wraparound ripple, commutation, cross-pol, UCA modes, Adcock, pseudo-Doppler; figure | ~10 s |
| `e8_yagi_stack.py` | PyNEC DL6WU stacks, ρ prediction, formula spacings, box, N-in-line, harness, tilt, polarization stats; figure | ~6 s |
| `s9_leo_terminal.py` | Starlink-class terminal: element count vs aperture and lattice, scan loss, G/T and link budget cross-check | < 1 s |
| `s9_series_fed_squint.py` | series-fed comb-line arrays: squint sinθ = √εeff(1 − f0/f), conductance taper, 24/60/77 GHz examples | < 1 s |
| `s18_level15_numbers.py` | numbers in the Level 1½ rungs (adaptive-beamforming, calibration, planar, conformal, synthesis) | < 1 s |

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Mailloux *Phased Array Antenna Handbook*; Hansen *Phased Array Antennas*; Van Trees *Optimum Array
Processing*; Balanis *Antenna Theory* ch. 6; Delos/Broughton/Kraft ADI "Phased Array Antenna Patterns"
series; Dolph 1946; Taylor 1955; Hannan 1964; Schmidt 1986; Roy & Kailath 1989; Capon 1969; Krim & Viberg
1996; Mano & Katagi 1982; Aumann et al. 1989; Kildal et al. 2015; ADAR1000 data sheet; KrakenSDR docs.

## Known gaps
- Full-wave (openEMS unit-cell) scan impedance and blind angles for real FR-4 5.8 GHz patch arrays — only Floquet phase-matching estimates and a dipole MoM model so far.
- Measured patch-to-patch coupling on FR-4; measured KrakenSDR field DF accuracy at 433 MHz.
- Rotman-lens design equations are described, not implemented (Bayliss now implemented in [pattern synthesis](array-pattern-synthesis.md)).
- Several component specs rely on manufacturer/distributor page summaries rather than full data-sheet reads (ADTR1107, ADAR4002, HMC64x, QPC2108, PE44820, AWMF-0108, ADL5390).
- Textbook chapter numbers (Mailloux 3e, Hansen 2e, Visser, Haupt, Stutzman & Thiele) not checked against the books; Visser and Haupt were not consulted.
- Circular-aperture Taylor/Bayliss, phase-only and power-pattern synthesis not implemented; TE cylinder series lacks an independent MoM check; no 3-D finite-airframe wraparound model; Yagi stacks modelled in free space only (no ground, mast or H-frame) — see the three W5-E8 pages.
