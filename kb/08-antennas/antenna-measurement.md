---
title: Antenna measurement — S11 and what it hides, far-field distance, ranges, gain (comparison and three-antenna), efficiency (Wheeler cap), polarization, DIY SDR pattern measurement
domain: 08-antennas
slug: antenna-measurement
tags: [antenna-measurement, vna, s11, return-loss, far-field, anechoic, outdoor-range, gain-transfer, three-antenna-method, wheeler-cap, efficiency, axial-ratio, sdr, rssi, nanovna, pattern, antenna-temperature, g-over-t, sky-noise, ground-spillover]
prerequisites: [antenna-fundamentals.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md, ../03-transmission-lines-matching/s-parameters.md]
related: [../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../17-test-measurement/noise-figure-measurement.md, yagi-uda-and-log-periodic.md, ../17-test-measurement/vna-fundamentals-calibration.md, ../17-test-measurement/nanovna-librevna-practical.md, ../17-test-measurement/antenna-range-ota-testing.md, ../17-test-measurement/sdr-as-test-equipment.md, antenna-matching-and-baluns.md, small-antenna-limits.md, antenna-polarization-and-circular-polarization.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Antenna measurement

## Questions this page answers
- What does an S11/SWR measurement tell me about my antenna, and what can it not tell me?
- How far away must the test antenna be for a valid gain or pattern measurement?
- How do I measure gain without a calibrated reference antenna (three-antenna method)?
- How do I measure radiation efficiency of a small antenna (Wheeler cap)?
- How do I measure axial ratio and polarization sense?
- Can I measure a pattern in my backyard with an SDR, and how accurate is it?
- Why do my range-test RSSI numbers jump around by ±5 dB?
- How do I avoid the test cable becoming part of the antenna?
- What is my ground-station Yagi's antenna temperature, and how does it change with elevation?
- Does pointing the Yagi up at the rocket lower the noise, and does it matter without an LNA?

## TL;DR
- **S11 (return loss)** with a calibrated VNA (NanoVNA/LiteVNA/LibreVNA) tells you *impedance match and resonance* at the reference plane. It says nothing about efficiency, gain, pattern or polarization — a resistor has perfect S11. Put a CM choke on the test cable, use port extension to the feed, and measure in the final mechanical environment.
- **Far field** for gain/pattern: R ≥ 2D²/λ (edge phase error 22.5°; gain error ≈ −0.13 dB for a uniform aperture, `tools/verify/ant_measurement.py`), and also R ≫ D and R ≫ λ (practically ≥ 3–10λ for small antennas). An 11-element 433 MHz Yagi needs ≥ 8.6 m; a 1.2 m dish at 5.8 GHz ≥ 56 m.
- **Gain by comparison (gain transfer)**: swap the AUT with a reference of known gain (dipole 2.15 dBi, standard-gain horn) in the same setup; G_AUT = G_ref + P_AUT − P_ref.
- **Three-antenna method**: three pairwise Friis measurements give G_A + G_B, G_B + G_C, G_A + G_C → solve for all three without any reference (IEEE Std 149 [1]); each result's error is ≈ 0.87 × the per-measurement error (Monte Carlo: 0.174 dB for 0.2 dB).
- **Wheeler cap efficiency**: η ≈ (R_free − R_cap)/R_free for a series-resonant small antenna, with a conducting cap of radius ≥ λ/2π around it (110 mm at 433 MHz, 52 mm at 915 MHz) [2], [3]; accuracy is limited by how well small R's are measured (a 0.1 Ω error changes η from 33 % to 22 % when R_free = 0.9 Ω).
- **Axial ratio**: rotate a linear source antenna in front of the AUT; AR = max/min of the received power (IEEE Std 149 [1]); check sense with an RHCP reference or a real GNSS/satellite signal.
- **Antenna temperature (433 MHz 11-element Yagi, 3 m over average ground, NEC)**: T_A = 49 K pointing up. At 10° elevation it is 68 K (H-pol) or 101 K (V-pol), and at the horizon 82/151 K. The sky (P.372 galactic ≈ 40 K) dominates overhead; ground spill-over dominates low down, worse for V-pol. With a 0.5 dB-NF masthead LNA, G/T changes by 1.4–3.4 dB from horizon to zenith. With only the module (NF ≈ 6 dB behind 1 dB of coax, T_rx ≈ 1160 K) it changes by < 0.4 dB: receiver noise dominates. These swings are for sky and ground only; if the P.372 Table 3 man-made medians (580–1150 K, [below](#antenna-temperature-and-gt-vs-elevation-over-ground)) enter at the horizon, the swing grows to ≈ 9–12 dB with the LNA and ≈ 2–3 dB with the module alone (hand estimate: T_A,horizon + T_man vs the 49 K zenith).
- **DIY SDR pattern**: CW source ≥ 2D²/λ away, AUT on a turntable, fixed-gain SDR (AGC off, no overload), average enough samples per angle (N ≥ (σ/0.5 dB)²), antennas high and the specular ground point low in the pattern. Expect ±1–2 dB repeatability — good for patterns and comparisons, not for absolute gain.

## Intuition (no math)
An antenna has three separate jobs: accept power from the cable (match), turn it into radiation instead of heat (efficiency), and send it in the right directions with the right polarization (pattern, gain, polarization). A VNA at the connector only checks the first job. The other two need a *radiated* measurement (two antennas and a path) or a trick like the Wheeler cap that separates radiation from loss.

Radiated measurements go wrong for three reasons: (1) too close — the far-field pattern hasn't formed yet; (2) reflections — the ground, walls, cars, people add a second path that interferes with the direct one; (3) the measurement hardware becomes part of the antenna — cables with common-mode current, hands, the turntable's metal parts. Good practice is mostly about avoiding these.

## The math

### Level 1 — the equations you use
- Return loss RL = −20 log|Γ| (dB); VSWR = (1+|Γ|)/(1−|Γ|); mismatch loss = −10 log(1 − |Γ|²).
- Friis for a measurement pair (matched, aligned polarization): P_r/P_t = G_t G_r (λ/4πR)².
- **Gain transfer**: G_AUT(dBi) = G_ref(dBi) + P_AUT(dBm) − P_ref(dBm).
- **Two identical antennas**: G = ½[10 log(P_r/P_t) + 20 log(4πR/λ)] (dB).
- **Three antennas**: with M_ij = 10 log(P_r/P_t)_ij + 20 log(4πR/λ) = G_i + G_j:
$$G_A=\tfrac12(M_{AB}+M_{AC}-M_{BC}),\quad G_B=\tfrac12(M_{AB}+M_{BC}-M_{AC}),\quad G_C=\tfrac12(M_{AC}+M_{BC}-M_{AB}).$$
- **Far field**: phase error across aperture D at range R: Δφ ≈ πD²/(4λR); = π/8 at R = 2D²/λ.
- **Wheeler cap** (series-RLC small antenna): R_free = R_r + R_loss; with the cap, R_r → 0, R_cap = R_loss; η = (R_free − R_cap)/R_free. For a parallel-RLC antenna use conductances: η = (G_free − G_cap)/G_free.
- **Series-through choke/impedance measurement**: Z = 2Z₀(1/S₂₁ − 1) ([baluns](antenna-matching-and-baluns.md)).

### Level 2 — where the far-field rule comes from, and range reflections
For a source at distance R, the path to the edge of an aperture of width D is longer by √(R² + (D/2)²) − R ≈ D²/(8R). At R = 2D²/λ that is λ/16, a phase error of 22.5° — the conventional tolerance. The resulting on-axis gain error of a uniformly illuminated aperture (numerical integration of the quadratic phase): −0.53 dB at D²/λ, −0.13 dB at 2D²/λ, −0.03 dB at 4D²/λ (script, 4λ and 10λ squares give the same numbers). Tapered apertures (dishes, horns) are less sensitive; sidelobe measurements need larger R.

**Ground reflections on an outdoor range.** A reflected ray of relative amplitude ρ adds a ripple between 20 log(1+ρ) and 20 log(1−ρ): ρ = −10 dB → +2.4/−3.3 dB; −20 dB → ±0.9 dB; −30 dB → ±0.3 dB (script). The reflected ray's strength is the product of the ground reflection coefficient and *both antennas' patterns toward the specular point*. With equal heights h and range R the specular point is arctan(2h/R) below boresight: 1.5 m masts at 10 m range → 17° (inside most beams!), 3 m masts → 31°. Raise the antennas, use directional source antennas whose pattern is low toward the ground, put absorber or a sloped surface at the specular point, or use a *ground-reflection range* that deliberately includes the reflection with a known geometry (IEEE Std 149 [1]).

**Reactive-region loading.** Small antennas measured with the source or objects within ~λ/2π interact (the "mutual coupling" error); the cap in the Wheeler method exploits exactly this region boundary.

### Level 3 — efficiency methods compared
- **Wheeler cap (1959)** [2]: a closed conducting sphere/box around the antenna, just large enough not to disturb the near-field current distribution (radius ≈ radiansphere λ/2π), suppresses radiation while leaving loss unchanged. Assumes the antenna is a single-resonance series or parallel RLC near the frequency of interest; cavity resonances of the cap itself (when the cap is too large) corrupt the result. **McKinzie (1997)** transformed the measured reflection coefficient so that a series or parallel RLC model always applies near resonance, stabilising the method [3].
- **Pattern integration (TRP)**: measure the full 3D pattern in both polarizations in an anechoic chamber; η = P_rad/P_accepted. CTIA-style OTA systems (used for TI's DN024 numbers [4]) report TRP and efficiency directly.
- **Reverberation chamber**: statistical averaging of many stirred modes measures total efficiency quickly for small antennas.
- **Directivity/gain method**: η = G/D with D from a pattern measurement or simulation; sensitive to errors in both.

## Measurement recipes

### A. S11 with a NanoVNA (every antenna, every time)
1. Calibrate SOL(T) at the end of the test cable (the connector you will attach to the antenna) over a span ±20–30 % around the design frequency. See [NanoVNA practical](../17-test-measurement/nanovna-librevna-practical.md).
2. Put a CM choke (ferrite beads or a sleeve) on the cable near the antenna; route the cable away, perpendicular to dipole arms.
3. For impedance at the feed of a PCB antenna, solder a short semi-rigid/U.FL pigtail and set port extension (electrical delay) using an open/short at the pad (TI AN058 method [5]). Return loss magnitude doesn't need the extension; impedance does.
4. Measure in the final environment (enclosure, nose cone, battery installed). Grab the cable 0.5–1 m away: if S11 moves, you have CM current.
5. Record S11, the −10 dB (or VSWR 2) bandwidth, and Smith chart; save the Touchstone file (record everything).

### B. Pattern and relative gain with an SDR (backyard range)
- Source: a signal generator, a LoRa module in CW/test mode, or a cheap VCO with a known stable output; a directional source antenna reduces ground reflections.
- Geometry: R ≥ max(2D²/λ, 5λ); masts as high as practical (≥ 3 m at 433 MHz); clear of metal, cars and people.
- Receiver: RTL-SDR/HackRF/Airspy with **fixed gain (AGC off)**; confirm linearity by inserting a known 10 dB attenuator (reading must drop by 10 dB ± 0.5); compute power in a narrow FFT bin around the carrier; log vs turntable angle (manual protractor or a servo/stepper).
- Averaging: with sample fluctuation σ (dB), N ≥ (σ/0.5)² samples per angle for ±0.5 dB on the mean (σ = 2 dB → 16 samples).
- Absolute gain: add the gain-transfer step with a reference dipole (2.15 dBi) or use three antennas.
- See [SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md) and [antenna range / OTA testing](../17-test-measurement/antenna-range-ota-testing.md).

### C. Axial ratio and sense
Rotate a linear source (a dipole) in 15° steps about the line of sight while the CP AUT stays fixed: the received-power ratio max/min is the AR (the "polarization pattern" dumbbell; IEEE Std 149 [1]). Sense: compare received power from RHCP and LHCP references (e.g., two helices wound oppositely); the co-polar one should be 15–25 dB stronger for a good CP antenna. A real-sky check for RHCP: GNSS C/N₀ drops by ≈ 15–20 dB with an LHCP antenna. **For a GNSS-band AUT the rotating source is a transmitter in a protected RNSS band (1164–1300, 1559–1610 MHz), where transmitting is prohibited at any power:** do this recipe only inside a shielded, absorber-lined enclosure or chamber (check that a GNSS receiver outside sees no C/N₀ change); otherwise measure S11 only and use the real-sky sense/C/N₀ checks ([patch recipe T3](../20-projects-recipes/patch-antenna-design-walkthrough.md)).

### D. Wheeler cap for a chip/PCB antenna
Build a closed box from copper-clad FR-4 or a metal can, inner radius (or half-dimension) ≥ λ/2π (52 mm at 915 MHz) but small enough that its first cavity resonance is well above the test frequency; seal the seams with copper tape; measure Z_in with and without the cap at the same port extension. Example: R_free = 12.0 Ω, R_cap = 1.5 Ω → η = 87.5 % (−0.58 dB). Beware tiny R: with R_free = 0.9 Ω, a 0.1 Ω error swings η from 33 % to 22 %.

### E. Embedded (active) element pattern of an array element
Drive one element through its port and terminate **every other element in a matched 50 Ω load** (not open, not shorted); measure the pattern as in recipe B. This *embedded element pattern* (EEP) $g_n(\theta,\phi)$ already contains the coupling to, and re-radiation by, the neighbours; for any excitation vector $a_n$ (with matched sources) the array field is exactly $\sum_n a_n g_n(\theta,\phi)$, and for a large regular array the centre-element EEP times the array factor predicts the scanned pattern, including scan blindness [9]. Record the full S-matrix with a VNA at the same time: the active reflection coefficient of element m is $\Gamma_m^{act} = \sum_n S_{mn}a_n/a_m$ ([S-parameters](../03-transmission-lines-matching/s-parameters.md), [12 planar arrays & coupling](../12-phased-arrays/planar-arrays-element-pattern-coupling.md)). Element-by-element amplitude/phase calibration of an assembled array with only a power meter (REV method) is in [12 array calibration](../12-phased-arrays/array-calibration.md).

*Antenna factor* (EMC field probes): $AF_{dB} = 20\log_{10}f_{MHz} - G_{dBi} - 29.77$ dB(1/m) at a 50 Ω port, derived in [decibels](../00-math-foundations/decibels-and-log-units.md) — the bridge between dBµV at the receiver and dBµV/m in space.

## Antenna temperature and G/T vs elevation over ground

**Idea.** A receiving antenna delivers noise power $kT_Ab$. Its temperature $T_A$ is the brightness temperature of everything it looks at, weighted by its power pattern. For a ground station: the sky (galactic background, CMB, atmosphere), the warm ground through side and back lobes, and the ground's reflection of the sky. Low-elevation pointing puts half the main beam on or near the ground and raises $T_A$.

**Level 1.** $T_A=\frac{1}{4\pi}\oint G(\Omega)\,T_B(\Omega)\,d\Omega$ for a lossless antenna (with radiation efficiency $e$: $T_A' = eT_A+(1-e)T_\text{phys}$). The figure of merit is $G/T = G - 10\log_{10}(T_A + T_\text{rx})$ in dB/K, with $T_\text{rx}$ referred to the antenna terminals: $T_\text{rx}=(L-1)T_0+L\,T_\text{LNA}$ for a feeder of loss L in front of the receiver.

**Level 2 — detailed balance with a real ground (method A).** NEC with a Sommerfeld/Norton ground computes the far field over the upper hemisphere only. That field already contains the direct and ground-reflected waves, added coherently. Of the power the antenna transmits, a fraction $\eta_\text{up}=\frac{1}{4\pi}\int_\text{up}G\,d\Omega$ reaches the sky, and the rest is absorbed in the ground. Reciprocity plus Kirchhoff's law (a body in equilibrium emits what it absorbs) then give, for a ground at uniform physical temperature $T_g$,
$$T_A=\frac{1}{4\pi}\int_\text{up}G(\Omega)\,T_\text{sky}(\text{el})\,d\Omega+(1-\eta_\text{up})\,T_g .$$
No ground emissivity model is needed beyond what NEC already uses. **Method B (cross-check)** uses the free-space pattern. Directions below the horizon see $(1-|\Gamma|^2)T_g+|\Gamma|^2T_\text{sky}$, with Fresnel Γ for the E_θ (TM) and E_φ (TE) parts, added incoherently.

**Level 3 — the sky model and its limits.**
- **Sky:** $T_\text{sky}(\text{el})=T_\text{bg}10^{-A/10}+T_m(1-10^{-A/10})$.
  - $T_\text{bg}$ is the P.372 median galactic noise, $F_a = 52-23\log f_\text{MHz}$. That is 39.7 K at 433 MHz and 7.1 K at 915 MHz.
  - The atmosphere has zenith attenuation $A_z ≈ 0.033$ dB (an approximate UHF oxygen value), scaled by a Kasten–Young air mass, with $T_m$ = 275 K.
  - Resulting $T_\text{sky}$: 41.5 K at the zenith, 49.5 K at 10°, 72 K at 2° and 99 K at 0°.
- **The real galaxy is not uniform.** At 408 MHz the brightness runs from ≈ 15–20 K in the coldest high-latitude regions to hundreds of K along the galactic plane (Haslam all-sky survey; from memory). A beam crossing the plane can add tens of K.
- **Man-made noise is not in the model.** P.372-13 Table 3 gives measured medians at 425 MHz of ≈ 1150 / 730 / 580 K (city / residential / rural; 1970s European data, omnidirectional antenna near the ground; [07 thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md#external-noise-itu-r-p372)). The Table 1 man-made lines extrapolated past their 250 MHz limit give much less (690 / 257 / 76 K) and should not be used. Even the rural median is ≈ 12× the 49 K zenith T_A above. It arrives mostly near the horizon, and at any populated site it, not the sky, sets T_A at low elevation. Measuring it is experiment R13 in [GAP_REGISTER §7](../../gaps/GAP_REGISTER.md); a sky-vs-load Y-factor check is R14.

**NEC results** (`tools/verify/s12_yagi_tant.py`):
- **Model:** the KB 11-element DL6WU Yagi (14.30 dBi free space), boom centre 3 m (4.3λ) above average ground (εr 13, 5 mS/m), tilted to elevation el, $T_g$ = 290 K.
- **Cross-checks:** methods A and B agree within 1.8 K everywhere. The reflection-coefficient ground (GN 0) and the Sommerfeld ground agree to 0.1 K.

| el | H-pol: η_up / T_sky part / T_ground part / **T_A** | V-pol: η_up / T_sky / T_ground / **T_A** | G/T, LNA 0.5 dB (H / V) | G/T, module only (H / V) |
|---|---|---|---|---|
| 0° | 0.879 / 46.7 / 35.1 / **81.8 K** | 0.590 / 32.5 / 118.9 / **151.4 K** | −6.4 / −8.4 dB/K | −16.7 / −16.9 |
| 5° | 0.908 / 47.7 / 26.6 / **74.3 K** | 0.699 / 37.3 / 87.2 / **124.5 K** | −6.1 / −7.7 | −16.6 / −16.8 |
| 10° | 0.930 / 47.7 / 20.3 / **68.1 K** | 0.792 / 40.8 / 60.4 / **101.2 K** | −5.8 / −7.1 | −16.6 / −16.7 |
| 20° | 0.955 / 45.7 / 13.1 / **58.8 K** | 0.904 / 43.1 / 27.9 / **71.1 K** | −5.4 / −6.0 | −16.6 / −16.6 |
| 30° | 0.961 / 43.0 / 11.2 / **54.2 K** | 0.938 / 42.0 / 17.9 / **60.0 K** | −5.2 / −5.5 | −16.6 / −16.6 |
| 45° | 0.966 / 41.6 / 9.9 / **51.6 K** | 0.955 / 41.2 / 12.9 / **54.2 K** | −5.1 / −5.2 | −16.5 / −16.5 |
| 90° | 0.970 / 40.8 / 8.7 / **49.4 K** | same | −5.0 | −16.5 |

G here is the free-space boresight gain (14.30 dBi). Over the ground, the coherent reflection also produces lobing: the boresight gain is +2 to +4 dB at 2–10° and the peak lobe is at ≈ 3.5° (H) or 3° (V), the first lobe of a 4.3λ-high antenna at ≈ λ/(4h) rad.

Vertical polarization is worse low down. The ground reflects TM waves weakly near the pseudo-Brewster angle and absorbs them, so it "glows" more in V-pol. **For the reader:** a bare E22/E220 receiver (NF ≈ 6 dB) is receiver-noise limited at 433 MHz, and pointing up buys gain, not noise. Adding a masthead LNA cuts T_sys from ≈ 1210 K to ≈ 85–185 K. That is about +8.5 to +11.5 dB of G/T, and only then does the elevation dependence (≈ 1.5–3.4 dB) matter ([LNA design](../06-rf-circuits/lna-design.md), [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).

## Design equations & rules of thumb

| Item | Rule / value |
|---|---|
| Far field | R ≥ 2D²/λ and R ≥ ~5λ; gain error ≈ −0.13 dB at 2D²/λ (uniform aperture) |
| Range reflection | specular ray ≤ −20 dB → ±0.9 dB ripple; ≤ −30 dB → ±0.3 dB |
| Three-antenna accuracy | σ_G ≈ 0.87 σ_meas |
| Wheeler cap size | radius ≈ λ/2π; below the cap's cavity resonance |
| SDR averaging | N ≥ (σ/Δ)² |
| Cable effects | choke the cable; S11 must not change when the cable is touched |
| Absolute accuracy (DIY) | ±1–2 dB; comparisons ±0.5 dB with care |
| Antenna temperature | T_A = (1/4π)∫_up G T_sky dΩ + (1 − η_up)T_g (lossless antenna, NEC over ground) | 433 MHz 11-el Yagi at 3 m: 49 K up, 68/101 K at 10° (H/V) |
| G/T | G − 10 log(T_A + T_rx) | elevation matters only when T_rx ≲ T_A (masthead LNA) |

## Worked examples

**Example 1 — Gain of a homemade 3-element 433 MHz Yagi by comparison.** Range 20 m (≥ 5λ = 3.5 m, ≥ 2D²/λ ≈ 0.2 m for a 0.34 m element span — fine), both antennas 3 m high. Reference: a choked λ/2 dipole (2.15 dBi) gives −41.3 dBm; the Yagi gives −34.5 dBm → **8.95 dBi**, close to the 9.15 dBi MoM prediction (`tools/verify/ant_yagi.py`). Repeat after rotating the setup 180° to check for reflections.

**Example 2 — Three-antenna method with no reference.** Antennas A (3-el Yagi), B (dipole), C (11-el Yagi) at 433 MHz, 20 m range (FSPL 51.20 dB). Measuring the three pairs with 0.2 dB rms error recovers the gains with 0.17 dB rms error (Monte Carlo); one simulated trial: 9.65/2.06/13.78 dBi for true 9.15/2.15/14.20 — note the far-field distance for C (8.6 m) is satisfied at 20 m.

**Example 3 — Range test with LoRa RSSI.** Two E22 modules at 1 km over open ground report RSSI varying ±5 dB as people walk around or the handheld antenna is tilted. Causes: ground-reflection interference (two-ray, [two-ray model](../09-propagation-link-budget/two-ray-ground-reflection.md)), polarization angle, body loss, and RSSI quantisation/accuracy (a few dB for integrated transceivers). Use a fixed tripod, fixed polarization, average ≥ 16 packets per position, and log SNR too ([LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).

**Example 4 — Detecting a bad measurement.** A PCB antenna shows S11 = −25 dB at 868 MHz, but the link is poor. Wheeler cap: R_free ≈ R_cap → η ≈ 10 %: the "match" is loss (e.g., a lossy inductor or an antenna shorted by an unexpected ground pour). S11 alone could not show it.

## Practical notes
- **Time-domain gating** (on VNAs that support it) can remove reflections from a cable or nearby objects in S11/S21 measurements — useful indoors.
- **Absorber**: even a few pyramidal absorber panels behind the AUT and at the specular point improve indoor measurements at ≥ 1 GHz; below 1 GHz absorbers must be large.
- **Turntable metal** near the AUT disturbs small antennas; use wood/plastic and put the rotator ≥ λ/2 below.
- **Near-field scanners** (planar/cylindrical/spherical) with NF→FF transformation are the professional alternative when far-field distances are impractical.
- **Record** setup geometry, heights, weather, cable routing, and calibration files; repeat a reference measurement at the start and end of each session.

## Common mistakes & misconceptions
- **"S11 < −10 dB means the antenna is good."** It means ≥ 90 % of the power is accepted — not radiated.
- **"The NanoVNA is calibrated, so the reading is at the antenna."** Only at the calibration plane; the pigtail and connector add phase and loss; use port extension.
- **"Indoors is fine for pattern measurements."** Room reflections at 433–915 MHz easily exceed −10 dB; patterns will be distorted by several dB.
- **"The SDR reading is in dBm."** Uncalibrated SDRs report relative dBFS; calibrate against a known source/attenuator, and disable AGC.
- **"Measuring at 2 m is far enough for my Yagi."** Check 2D²/λ (8.6 m for the 11-element 433 MHz design).
- **"Pointing the Yagi at the sky makes the receiver quieter."** Only with a low-noise front end. With T_rx ≈ 1000 K the 50–150 K change in T_A moves G/T by < 0.4 dB.
- **"T_A is the sky temperature."** Overhead it is the sky plus 9 K of ground spill-over (back and side lobes). At 10° elevation, 20–60 K comes from the ground, more for V-pol.
- **"Wheeler cap works for any antenna."** It assumes an electrically small, single-resonance antenna; for larger antennas the cap perturbs the current distribution or resonates.

## How to simulate / verify
- `python3 tools/verify/ant_measurement.py` — far-field phase and gain error, three-antenna solve and Monte Carlo accuracy, Wheeler-cap sensitivity, range-reflection ripple and specular geometry, averaging rule.
- `python3 tools/verify/s12_yagi_tant.py` (≈ 5 min, PyNEC): T_A and G/T vs elevation for H/V-pol Yagis over average ground; method A (NEC ground, detailed balance) vs method B (free-space pattern + Fresnel); GN 0 vs Sommerfeld check. Edit H, EPS_G/SIG_G, T_bg and T_rx for your site.
- Compare measured patterns with the MoM (`tools/verify/ant_mom_wire.py`, `ant_mom_general.py`) or NEC/openEMS predictions; disagreements > 2 dB in the main lobe usually indicate a setup problem.

## Open questions / gaps
- IEEE Std 149 (test procedures) was cited via IEEE Std 145 and textbooks, not read directly; its range-design clauses (e.g., ground-reflection range heights) should be summarised by domain 17.
- The T_A model uses a uniform galactic background and a uniform 290 K ground; it has no man-made noise, no mast or cable, and no galactic-plane hot spots. Measure it (Y-factor, R14).
- Accuracy of SX126x/SX127x RSSI readings vs a calibrated power meter should be measured and documented (domain 15/17).

## Sources
1. IEEE Std 149-1979 (R2008), *IEEE Standard Test Procedures for Antennas* — ranges, gain measurement (comparison, two/three-antenna), polarization measurement. (standard; cited)
2. H. A. Wheeler, "The radiansphere around a small antenna," *Proc. IRE* 47, pp. 1325–1331, 1959 — cap method for radiation efficiency. (peer-reviewed)
3. W. E. McKinzie III, "A modified Wheeler cap method for measuring antenna efficiency," *IEEE AP-S Int. Symp.*, 1997; W. Wang, "Design and construction of a Wheeler cap test set-up" (thesis, diva-portal). (peer-reviewed / thesis; abstract level)
4. TI DN024 (SWRA227) — CTIA OTA measurement summary (TRP, efficiency, NHPRP). (app note)
5. TI AN058 (SWRA161) — VNA measurement of PCB antennas with semi-rigid cable, calibration, port extension via electrical delay; spectrum-analyser frequency-sweep method. (app note)
6. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — ch. 17 (antenna measurements: ranges, far-field criteria, gain methods, polarization, efficiency). (textbook)
7. IEEE Std 145-1993 — far-field region 2D²/λ note; reactive near-field λ/2π. (standard)
8. This repository: `tools/verify/ant_measurement.py`, `tools/verify/s12_yagi_tant.py`. (verification)
9. D. M. Pozar, "The active element pattern," *IEEE Trans. Antennas Propag.* 42(8), 1176–1178, 1994 — EEP definition with matched terminations, array pattern as superposition of EEPs, relation to scan impedance. (peer-reviewed)
10. ITU-R Recommendation P.372, *Radio noise* — galactic noise Fa = 52 − 23 log f; man-made noise lines Fa = c − d log f (0.3–250 MHz). Constants checked via the ITU table reproduced in IEEE 802.18-12-0057. (standard; secondary copy)
11. J. D. Kraus, *Radio Astronomy*, 2nd ed., Cygnus-Quasar, 1986 — antenna temperature as the pattern-weighted brightness, ground spill-over. (textbook; cited)
