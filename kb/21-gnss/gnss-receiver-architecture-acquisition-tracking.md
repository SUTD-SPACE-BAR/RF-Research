---
title: GNSS receiver architecture — front end, acquisition, tracking loops (DLL/PLL/FLL), measurements and the navigation solution
domain: 21-gnss
slug: gnss-receiver-architecture-acquisition-tracking
tags: [gnss, receiver, front-end, lna, saw, adc, quantization-loss, acquisition, fft-acquisition, coherent-integration, non-coherent-integration, pd-pfa, dll, pll, costas, fll, loop-bandwidth, tracking-threshold, c/n0, pseudorange, carrier-phase, doppler, least-squares, clock-bias, kalman-filter, vector-tracking, sensitivity]
prerequisites: [gnss-signals-and-codes.md, ../10-comms-modulation/synchronization-carrier-timing.md, ../10-comms-modulation/matched-filter-detection.md, ../07-noise-linearity/noise-figure-and-friis.md]
related: [gnss-on-rockets-dynamics-and-limits.md, gnss-error-sources-dop.md, ttff-agps-almanac-ephemeris.md, sdr-gnss-and-diy-receivers.md, gnss-receiver-integration-u-blox.md, ../14-sdr-dsp/nco-ddc-duc.md, ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md, ../08-antennas/gnss-antennas.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# GNSS receiver architecture, acquisition and tracking

## Questions this page answers
- What is inside a GNSS receiver chip, from antenna to position?
- Why can GNSS receivers use 1- or 2-bit ADCs, and how much does that cost?
- How does acquisition work, and why does a cold start take seconds just to find satellites?
- What are coherent and non-coherent integration, and why can't you integrate forever?
- What do the DLL, PLL and FLL do, and what loop bandwidths are used?
- What C/N0 does a receiver need to keep tracking, and why is that different from acquisition sensitivity?
- How does a receiver turn pseudoranges into a position, and why does it need four satellites?
- What is the receiver clock bias and why does it not matter (much)?
- What does a Kalman filter add, and why do update rates vary with constellations?

## TL;DR
- **Chain**: antenna → LNA (NF ≈ 1–2 dB) → SAW/bandpass → down-conversion (low-IF or zero-IF) → 1–3-bit ADC at a few MS/s → digital correlators (dozens to thousands of channels) → tracking-loop software → measurement engine → navigation filter. The ZED-F9P and MAX-M10S implement all of this; an SDR or MAX2769/MAX2771 front end leaves the digital part to you ([SDR page](sdr-gnss-and-diy-receivers.md)).
- **Quantisation is cheap**: 1-bit costs ≈ 1.96 dB (2/π), 2-bit ≈ 0.55 dB of C/N₀ (theory; simulated −2.01 / −0.64 dB in `tools/verify/gnss_acquisition.py`).
- **Acquisition** searches code phase (2046 half-chip cells for C/A) × Doppler (21 bins of 500 Hz over ±5 kHz) ≈ 43 000 cells per satellite. An FFT correlator tests all code phases at once. With a system false-alarm probability of 10⁻³, a 1 ms coherent dwell needs **≈ 44 dB-Hz** for 90 % detection; 10 × 1 ms non-coherent ≈ 36 dB-Hz; 100 × ≈ 29 dB-Hz; 10 ms coherent ≈ 34 dB-Hz (script, non-central χ² theory confirmed by Monte Carlo).
- **Tracking**: a carrier-aided DLL (B_n ≈ 0.1–2 Hz) follows the code; a Costas PLL (B_n ≈ 10–20 Hz, 3rd order for vehicles) or an FLL follows the carrier. Thermal-noise-only thresholds: PLL 3σ = 45° at **≈ 27 dB-Hz** (B_n = 15 Hz, T = 1 ms), FLL ≈ 28 dB-Hz (B_n = 10 Hz, T = 1 ms); narrow, long-integration loops (2 Hz, 20 ms) reach ≈ 17 dB-Hz (script).
- **Measurements**: pseudorange ρ = c(t_rx − t_tx) (code), Doppler (carrier frequency), accumulated carrier phase (cm-level, ambiguous); u-blox exposes them in `UBX-RXM-RAWX`.
- **Position**: ≥ 4 pseudoranges → (x, y, z, receiver clock bias) by iterative least squares; error ≈ DOP × σ_UERE (verified by Monte Carlo in `gnss_dop_errors.py`). Each extra constellation adds an inter-system bias unknown. A Kalman filter smooths and bridges outages using a dynamic model — which is exactly what u-blox's "dynamic platform model" tunes.

## Intuition (no math)
A GNSS receiver is a stack of nested lock-ins. First it must *find* each satellite (acquisition): try every possible code delay and every possible Doppler shift, see which combination makes the correlation light up. Then it must *follow* each satellite (tracking): small feedback loops continuously nudge a local code generator and a local oscillator so the replica stays aligned as the satellite moves and the receiver moves. Finally, it uses the replica timing as a stopwatch reading for each satellite and solves for where (and when) it must be for all those readings to agree.

The loops face a fundamental trade-off: a narrow loop averages away more noise (works with weaker signals) but responds slowly (loses lock under acceleration or jerk). Static high-sensitivity receivers use very narrow, long-integration loops; a rocket needs wide, fast loops — which need stronger signals. Most robust receivers fall back from phase tracking (PLL, precise but fragile) to frequency tracking (FLL, sloppier but tolerant) when things get violent.

## The math

### Level 1 — the blocks and their numbers
**Front end.** Antenna noise temperature $T_A$ (≈ 100 K for an upward patch) plus LNA, cables and receiver: $T_{sys} = T_A + T_{LNA} + (\dots)/G_{LNA}$ — see [noise figure and Friis](../07-noise-linearity/noise-figure-and-friis.md) and the [antennas page cascade](../08-antennas/gnss-antennas.md#the-math). The ZED-F9P's own chain NF is 9.5 dB, which is why it needs 17–50 dB of external (active-antenna) gain; the MAX-M10S has NF 1.5 dB with its internal LNA [1][2].

**Bandwidth and sampling.** The RF passband must hold the signal's main lobe (±1.023 MHz for C/A; ±12 MHz to keep E1/B1C's BOC(6,1) part; ≈ 47 MHz for B1I+L1+G1 together). A complex sampler needs $f_s \gtrsim$ the two-sided bandwidth; a real low-IF sampler $f_s > 2(f_{IF} + B/2)$; classic designs sample the C/A signal at 4–16 MS/s ([bandpass sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)).

**ADC bits.** Thermal noise dominates the signal by ~20 dB at the ADC, so quantisation only adds a little "noise" and the signal survives sign-only sampling: loss $= 10\log_{10}(2/\pi) = -1.96$ dB for 1 bit, ≈ −0.55 dB for 2 bits with the threshold at ≈ 1σ, < 0.2 dB for 3+ bits. More bits are worth having for interference robustness (a strong CW tone captures a 1-bit ADC) and are needed for adaptive notch filtering — [interference page](gnss-interference-jamming-spoofing.md). An **AGC** keeps the 2-bit thresholds at ≈ 1σ; its gain value is a free jamming indicator (u-blox `agcCnt` in `UBX-MON-RF` [3]).

**Search space.**
$$N_{cells} = \frac{L_{code}}{\Delta\tau}\times\frac{2 f_{D,max} + 2\Delta f_{osc}}{\Delta f_{bin}},\qquad \Delta f_{bin}\approx \frac{2}{3T}\ \text{to}\ \frac{1}{T}$$
For C/A: 2046 × 21 = 42 966 cells (½-chip, 500 Hz, ±5 kHz). A ±2 ppm TCXO adds ±3.15 kHz (34 bins; `gnss_ttff.py`), and a rocket moving at 600 m/s along the line of sight adds ±3.2 kHz unless aided.

### Level 2 — acquisition statistics, loop noise, the navigation equations
**Coherent detection statistic.** The correlator output for cell $(\tau, f)$ over coherent time $T$ is $Y = I + jQ$; with noise only, $|Y|^2/\sigma^2$ is exponential (χ² with 2 degrees of freedom). Summing $K$ coherent blocks non-coherently, $S = \sum_{k=1}^{K}|Y_k|^2/\sigma^2$, gives
$$P_{fa,cell} = \Pr\{\chi^2_{2K} > 2\gamma\},\qquad P_d = \Pr\{\chi'^2_{2K}(\lambda) > 2\gamma\},\quad \lambda = 2K\,\frac{C}{N_0}T\,L_{impl}$$
where $L_{impl}$ collects Doppler-bin (sinc²(πΔfT): 0.9 dB at Δf = 250 Hz, T = 1 ms), code-phase (≤ 2.5 dB for ½-chip steps), quantisation and filter losses. Setting the per-cell $P_{fa} = 10^{-3}/N_{cells} = 2.3\times10^{-8}$:

| Integration | C/N₀ for P_d = 0.9 (dB-Hz) |
|---|---|
| 1 ms coherent | 44.1 |
| 2 × 1 ms non-coherent | 41.5 |
| 10 × 1 ms | 36.0 |
| 100 × 1 ms | 29.3 |
| 10 ms coherent (needs 50 Hz bins and data-bit handling) | 34.1 |

Ten non-coherent sums buy ≈ 8 dB, ten-times-longer coherent integration buys 10 dB — the difference is the **squaring loss** (verified, `gnss_acquisition.py`; Monte Carlo agrees with theory within 0.15 in P_d at the tested points, with the simulation running ≈ 0.1 low, i.e. ≈ 0.3 dB implementation loss from sampling).

**Why not integrate forever.** (i) Data bits flip the sign every 20 ms (GPS LNAV) or 4 ms (Galileo E1-B symbols) — coherent sums across an unknown bit edge cancel; pilots and data wipe-off (assistance) avoid this. (ii) Doppler bins must shrink as 1/T, so the number of cells grows. (iii) Receiver oscillator phase noise and user dynamics smear the phase: the coherent time must be short compared with the time for the phase to wander by ~1 rad. On a rocket the dynamics make T ≈ 1 ms the practical limit.

**Correlators and discriminators.** Each channel runs Early, Prompt and Late correlators spaced $d$ chips (typ. $d$ = 1 classic, 0.1–0.2 "narrow correlator").
- DLL, normalised early-minus-late power: $D = \frac{|E|^2-|L|^2}{|E|^2+|L|^2}$.
- Costas PLL (data present): $D = \arctan(Q_P/I_P)$ (±90° range, insensitive to bit sign).
- Pure PLL (pilot): $\operatorname{atan2}(Q_P, I_P)$ (±180°).
- FLL (cross-product / dot-product of successive prompts): $D = \arctan2(\text{cross},\text{dot})/T$ (±1/(2T) Hz, or ±1/(4T) with data).

**Thermal-noise jitter** (Kaplan–Hegarty forms [4]; $c = 10^{(C/N_0)/10}$):
$$\sigma_{PLL} = \frac{360}{2\pi}\sqrt{\frac{B_n}{c}\Big(1+\frac{1}{2Tc}\Big)}\ \text{deg},\qquad
\sigma_{FLL} = \frac{1}{2\pi T}\sqrt{\frac{4FB_n}{c}\Big(1+\frac{1}{Tc}\Big)}\ \text{Hz},$$
$$\sigma_{DLL} = \sqrt{\frac{B_n d}{2c}\Big(1+\frac{2}{Tc(2-d)}\Big)}\ \text{chips}\ (\text{BPSK, wide front end}),$$
with $F$ = 1 at high and 2 near threshold. The **rule of thumb thresholds** are $3\sigma_{PLL} + \theta_e \le 45°$ (Costas), $3\sigma_{FLL} + f_e \le 1/(4T)$, $3\sigma_{DLL} + R_e \le d/2$, where $\theta_e, f_e, R_e$ are dynamic-stress errors [4].

| C/N₀ (dB-Hz) | σ_PLL, B_n 15 Hz, T 1 ms | σ_PLL, 10 Hz, 20 ms | σ_FLL, 10 Hz, 1 ms | σ_DLL, 2 Hz, d = 1 |
|---|---|---|---|---|
| 45 | 1.3° | 1.0° | 5.7 Hz | 1.7 m |
| 35 | 4.2° | 3.2° | 20.5 Hz | 6.7 m |
| 28 | 11.8° | 7.4° | 64 Hz | 24 m |
| 25 | 20.0° | 10.6° | 116 Hz | 45 m |

(script output; the DLL figures are for an *unaided* 2 Hz loop — with carrier aiding the DLL bandwidth can drop to 0.1–0.5 Hz, dividing these by 2–4.)

**Dynamic stress.** An $n$th-order loop has zero steady-state error to an $(n-1)$th-order input and a constant error to the $n$th derivative:
$$\theta_{e,2} = \frac{360}{\lambda}\frac{\ddot R}{\omega_0^2},\ \ \omega_0 = \frac{B_n}{0.53};\qquad \theta_{e,3} = \frac{360}{\lambda}\frac{\dddot R}{\omega_0^3},\ \ \omega_0=\frac{B_n}{0.7845}\quad(\text{deg}).$$
A 2nd-order PLL with $B_n$ = 15 Hz already has 93° of error at 4 g of line-of-sight acceleration; a 3rd-order loop has none for constant acceleration but $\theta_e$ = 26.5° per 10 g/s of jerk at 15 Hz (script). Rockets are therefore jerk-limited — [rocket dynamics page](gnss-on-rockets-dynamics-and-limits.md). **Carrier aiding** scales the PLL frequency estimate by $R_c/f_L$ and feeds it to the code NCO, so the DLL only tracks code–carrier divergence (ionosphere) and can be very narrow.

**Measurements.** Code pseudorange for satellite $i$:
$$\rho_i = \|\mathbf r_i - \mathbf r\| + c(\delta t_r - \delta t^i) + I_i + T_i + \varepsilon_i$$
(m; $\delta t_r$ receiver clock bias, $\delta t^i$ satellite clock error from the broadcast message, $I_i, T_i$ iono/tropo delays). Carrier phase $\Phi_i = \|\mathbf r_i-\mathbf r\| + c(\delta t_r-\delta t^i) - I_i + T_i + \lambda N_i + \epsilon_i$ (note the ionospheric sign flip and the integer ambiguity $N_i$ — [RTK page](rtk-ppp-and-corrections.md)). Doppler gives range rate: $\dot\rho_i = -\lambda f_{D,i}$.

**Least squares.** Linearise about a guess $\mathbf x_0 = (\mathbf r_0, b_0)$, $b = c\,\delta t_r$:
$$\Delta\boldsymbol\rho = \mathbf G\,\Delta\mathbf x + \boldsymbol\varepsilon,\qquad \mathbf G_i = [-\hat{\mathbf u}_i^T,\ 1],\qquad \Delta\mathbf x = (\mathbf G^T\mathbf W\mathbf G)^{-1}\mathbf G^T\mathbf W\,\Delta\boldsymbol\rho,$$
iterating until convergence (2–5 iterations from the Earth's centre; verified — the script recovers a 120 µs = 36 km clock bias exactly). With equal weights, $\mathrm{cov}(\Delta\mathbf x) = \sigma^2_{UERE}(\mathbf G^T\mathbf G)^{-1}$, whose diagonal gives the DOPs ([error/DOP page](gnss-error-sources-dop.md)). Each additional constellation adds one clock (inter-system bias) unknown unless the system time offset is broadcast (GPS–Galileo GGTO) or calibrated; a u-blox receiver needs ≥ 3 satellites for 2D and refuses to navigate with fewer [5]. Velocity comes from the same G matrix applied to Doppler range-rates, plus a clock-drift unknown — which is why GNSS velocity (0.05 m/s spec [1][2]) is far better than differentiated position.

### Level 3 — architectures, filters, high sensitivity, vector tracking
**Navigation filter.** Most receivers run an extended Kalman filter with state $(\mathbf r, \mathbf v, [\mathbf a], b, \dot b)$ and a process-noise model (e.g. white acceleration of spectral density $q$). The filter's assumed $q$ and limits are what a **dynamic platform model** encodes: u-blox's "Airborne <4g" allows larger accelerations and drops altitude/velocity sanity checks other than altitude [5]; picking "Portable" on a rocket makes the filter distrust real motion (lag, and fix invalidation above 12 km or 50 m/s vertical) — [u-blox integration](gnss-receiver-integration-u-blox.md).

*Kalman filter derivation, Q/R tuning, consistency tests and loosely/tightly/deeply coupled GNSS/INS fusion: [Kalman filtering and state estimation](../00-math-foundations/kalman-filter-and-state-estimation.md); pseudorange Cramér–Rao bound vs the DLL formula: [estimation theory](../00-math-foundations/estimation-theory-ml-map-crb.md).*

**Update rate vs constellations.** Every measurement epoch, the baseband must process all channels and the CPU must run the filter; rates therefore fall with the number of signals: MAX-M10S 18 Hz single-GNSS / 10 Hz GPS+GAL / 3 Hz with BDS B1I in default mode (25 / 20 / 12 Hz in "high-performance" configuration); ZED-F9P PVT 25 Hz GPS-only, 9 Hz all four GNSS; RTK 20 Hz → 7 Hz [1][2].

**Lock detectors and state machine.** Phase lock is declared from the ratio $(I_P^2 - Q_P^2)/(I_P^2+Q_P^2)$ (≈ cos 2θ); frequency lock from the FLL discriminator variance; loss of lock triggers FLL mode, then local reacquisition around the last Doppler ("reacquisition sensitivity" −160 dBm for u-blox), then full acquisition. Bit synchronisation uses a histogram of prompt sign changes over 20 ms boundaries; frame sync finds the LNAV preamble (8 bits every 6 s).

**High-sensitivity techniques.** Long coherent integration with data wipe-off (assisted data), massive parallel correlators, and non-coherent accumulation down to ≈ 10 dB-Hz — the source of −160 to −167 dBm datasheet figures. They do nothing for high dynamics.

**Vector tracking and ultra-tight GNSS/INS.** Instead of independent scalar loops, a navigation filter predicts all channels' code and carrier NCOs from its state (optionally propagated by an IMU). Weak or temporarily blocked satellites are carried by the others, and dynamics known from the IMU are removed before the loops see them. This is the standard answer for high-dynamics platforms (projectiles, launchers); DLR's sounding-rocket Orion receiver used a simpler open-loop version — trajectory-polynomial Doppler aiding — to reacquire during boost [6].

**Architectures in practice.**
| Type | Example | Bits / bandwidth | Correlators | Notes |
|---|---|---|---|---|
| Single-chip L1 module | MAX-M10S (UBX-M10050) | multi-GNSS L1, LNA + SAW integrated | many parallel | 25 mW tracking [2] |
| Dual-band RTK module | ZED-F9P | L1 + L2/E5b, needs active antenna | many parallel (count not given in the data sheet) | RTK engine on chip [1] |
| RF front-end IC + FPGA/CPU | MAX2769B / MAX2771 + GNSS-SDR | 1–3 bit, 2–24 MHz IF filters | software | [SDR page](sdr-gnss-and-diy-receivers.md) |
| Software receiver from SDR | RTL-SDR/HackRF + GNSS-SDR/SoftGNSS | 8-bit complex, ≤ 2.4 MS/s (RTL) | software | learning, post-processing |

## Design equations & rules of thumb

| Item | Equation / value | Validity |
|---|---|---|
| Post-correlation SNR | $(C/N_0)T$ | coherent, aligned |
| Doppler bin loss | $\mathrm{sinc}^2(\pi\Delta f T)$; 0.9 dB at Δf = 1/(4T) | coherent T |
| 1-/2-bit ADC loss | −1.96 / −0.55 dB | noise-dominated input |
| Acquisition threshold (P_d 0.9, P_fa 10⁻³) | 44 dB-Hz (1 ms); 36 (10 × 1 ms); 29 (100 × 1 ms) | C/A, ±5 kHz, ½ chip |
| PLL threshold | 3σ_PLL + θ_e ≤ 45° (Costas), 90° (pilot) | Kaplan rule |
| FLL threshold | 3σ_FLL + f_e ≤ 1/(4T) | with data |
| DLL threshold | 3σ_DLL + R_e ≤ d/2 | early–late spacing d |
| 3rd-order PLL jerk error | 360·J/(λω₀³), ω₀ = B_n/0.7845 | constant jerk |
| Typical loop BW | PLL 10–20 Hz (vehicles), 2–5 Hz (static); FLL 2–10 Hz; DLL 0.1–2 Hz (aided) | |
| Position error | DOP × σ_UERE | white, equal-variance errors |

## Worked examples
**1 — Cold-start search with an FFT engine.** Satellite unknown, Doppler ±5 kHz, TCXO ±0.5 ppm (±0.8 kHz): 25 Doppler bins × 1 ms. One FFT correlation of 4092 samples per bin per ms → 25 ms of data per satellite per sweep; at 36 dB-Hz you need 10 non-coherent sweeps → 250 ms per satellite, 32 GPS PRNs → 8 s sequentially, ≈ 1 s with 8 parallel engines. A serial single-correlator search of the same space would take 43 s per satellite per 1 ms sweep (script). Modern modules use thousands of correlators plus FFT engines; the residual TTFF is dominated by decoding ephemeris ([TTFF page](ttff-agps-almanac-ephemeris.md)).

**2 — Can a 15 Hz PLL track at 30 dB-Hz on the pad?** σ_PLL = √(15/1000 × (1 + 1/(2×10⁻³×1000))) rad = √(0.015 × 1.5) = 0.150 rad = 8.6°; 3σ = 26° < 45° → yes, with 19° of margin for dynamic stress and oscillator jitter. At 25 dB-Hz, 3σ = 60° → no; the receiver must narrow the loop (and lose dynamics tolerance) or switch to FLL.

**3 — Code-tracking noise in metres.** C/N₀ 45 dB-Hz, carrier-aided DLL B_n = 0.5 Hz, d = 0.2 chip, T = 20 ms: σ = √(0.5×0.2/(2×31623) × (1 + 2/(0.02×31623×1.8))) = √(1.58×10⁻⁶ × 1.0018) = 1.26×10⁻³ chip = **0.37 m**. With d = 1 and 2 Hz: 1.7 m. This is why narrow correlators and carrier smoothing matter for metre-level single-frequency accuracy.

**4 — Clock bias magnitude.** A free-running receiver TCXO with 0.5 ppm frequency error accumulates 0.5 µs of clock bias per second = 150 m/s of common pseudorange drift. The navigation solution estimates it every epoch together with position; u-blox receivers steer the clock or insert millisecond jumps to keep it bounded — firmware differences in how the bias is handled show up in RAWX data as millisecond steps, which post-processing software must handle.

## Practical notes
- **Use `UBX-NAV-SAT`/`NAV-SIG` C/N₀ and quality indicators** to see what the tracking loops are doing during tests; log `RXM-RAWX` (raw pseudorange/carrier/Doppler with lock-time and half-cycle flags) if you want to post-process or study loss of lock during a flight [3].
- **Oscillator quality is a receiver-performance parameter**: the PLL sees the TCXO's phase noise, temperature slews and acceleration sensitivity (≈ 1 ppb/g × 15 g = 24 Hz at L1) as if they were dynamics — [rocket page](gnss-on-rockets-dynamics-and-limits.md#the-math).
- **Don't starve the module of power**: VCC ripple and series resistance degrade the RF chain and clocks; u-blox asks for < 0.2 Ω series resistance and a 1 µF capacitor at VCC [5].
- **Reacquisition matters more than tracking sensitivity** on vehicles that lose signals (roll, plume, chute): keep the receiver powered and its ephemeris valid so reacquisition is local and fast.

## Common mistakes & misconceptions
- **"More correlators = more sensitivity."** More correlators shorten *search time*; sensitivity comes from integration time and noise figure.
- **"A narrower loop is always better."** Only for static receivers; under dynamics the stress error grows as $1/B_n^3$ (3rd order).
- **"The receiver needs four satellites because space is 3-D."** Three for position plus one for the receiver clock bias; with multiple constellations, one more per extra system-time offset unless known.
- **"Code and carrier are delayed equally by the ionosphere."** Code is delayed, carrier phase is advanced by the same amount (divergence) — [ionosphere](../09-propagation-link-budget/ionospheric-hf-propagation.md).
- **"Datasheet tracking sensitivity is what I get in flight."** It is static and long-integration; dynamic PLL tracking needs ~25–30 dB-Hz.
- **"The GPS receiver talks to the satellites."** It only listens. Each satellite broadcasts one-way; the receiver measures arrival times and solves for its position and its own clock (the four unknowns of the least-squares step above). So there is no transmit licence, no limit on the number of users, and the satellites never learn where the rocket is: the position has to come down your own telemetry link. Assistance data (A-GNSS) arrives over a separate internet or cellular link. Full discussion: [GNSS antennas — common mistakes](../08-antennas/gnss-antennas.md#common-mistakes--misconceptions).

## How to simulate / verify
- `python3 tools/verify/gnss_acquisition.py` — FFT acquisition of a synthetic C/A signal; P_d vs C/N₀ (Monte Carlo vs non-central χ²); Doppler-bin loss; 1-/2-bit quantisation loss; search-time numbers. ALL PASS.
- `python3 tools/verify/gnss_tracking_loops.py` — PLL/FLL/DLL jitter and thresholds, dynamic stress, oscillator terms, 3rd-order PLL (± FLL assist) simulation under rocket dynamics. ALL PASS.
- `python3 tools/verify/gnss_dop_errors.py` — least-squares solution with clock bias and DOP Monte Carlo. ALL PASS.
- A full software receiver: Borre et al.'s SoftGNSS (MATLAB) or GNSS-SDR on a recorded file — [SDR page](sdr-gnss-and-diy-receivers.md).

## Open questions / gaps
- u-blox does not publish its loop bandwidths, orders, integration times or FLL/PLL switching logic; statements about "the receiver" here are generic.
- The quoted thresholds ignore oscillator phase noise, vibration and bit-transition losses — they are optimistic by a few dB.

## Sources
1. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05, 2024 — receiver chain NF 9.5 dB, external gain 17–50 dB, update rates, sensitivity, velocity accuracy. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
2. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — NF 1.5 dB, LNA + SAW, update-rate and sensitivity tables, 25 mW. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
3. u-blox, *u-blox F9 HPG 1.32 Interface Description*, UBX-22008968 R01, 2022 — UBX-MON-RF (agcCnt, jammingState, antStatus), NAV-SAT, RXM-RAWX. https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.32_InterfaceDescription_UBX-22008968.pdf (manufacturer)
4. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House, 2017 — ch. 8 (acquisition, discriminators, loop filters, thermal-noise and dynamic-stress error formulas, tracking thresholds, carrier aiding). (textbook)
5. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — dynamic platform models, ≥3 satellites, gnssFixOK, power-supply checklist. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
6. M. Markgraf, O. Montenbruck, F. Hassenpflug, P. Turner, B. Bull, "A Low Cost GPS System for Real-Time Tracking of Sounding Rockets," 15th ESA Symp. on European Rocket and Balloon Programmes, Biarritz, 2001 (NTRS 20010069267). https://archive.org/details/nasa_techdoc_20010069267 (conference)
7. K. Borre, D. M. Akos, N. Bertelsen, P. Rinder, S. H. Jensen, *A Software-Defined GPS and Galileo Receiver: A Single-Frequency Approach*, Birkhäuser, 2007 — acquisition (parallel code-phase), tracking loops, navigation solution in MATLAB. (textbook; general reference)
8. P. Misra, P. Enge, *Global Positioning System: Signals, Measurements, and Performance*, 2nd ed., 2006 — ch. 6 (least squares, DOP), ch. 10–11 (acquisition and tracking). (textbook; general reference)
9. P. J. G. Teunissen, O. Montenbruck (eds.), *Springer Handbook of Global Navigation Satellite Systems*, Springer, 2017 — ch. 13–14 (receiver architecture, signal processing). (textbook; general reference)
