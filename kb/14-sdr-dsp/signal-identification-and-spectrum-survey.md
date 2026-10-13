---
title: Signal identification and spectrum surveys — identifying unknown signals (bandwidth, modulation fingerprints, cyclostationary symbol-rate estimation, burst timing), a catalogue of common signals, and surveying 433/868/915 MHz at a launch site
domain: 14-sdr-dsp
slug: signal-identification-and-spectrum-survey
tags: [signal-identification, sigidwiki, waterfall, spectrogram, constellation, symbol-rate, baud, cyclostationary, spectral-correlation, cyclic-autocorrelation, power-law, x-squared, x-fourth, fsk, gfsk, msk, ofdm, cyclic-prefix, lora-chirp, ads-b, ais, aprs, pocsag, flex, hd-radio, spectrum-survey, occupancy, rtl_power, heatmap, sdr++, inspectrum, urh, rtl_433, launch-site, interference]
prerequisites: [fft-spectral-analysis-windows.md, iq-complex-baseband.md, software-demodulation.md, ../10-comms-modulation/digital-modulation-psk-qam-fsk.md]
related: [sdr-hardware-survey.md, sdr-front-end-protection-and-filtering.md, gnu-radio-and-software-stack.md, sampling-aliasing-bandpass-sampling.md, ../10-comms-modulation/ofdm.md, ../10-comms-modulation/pulse-shaping-isi.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../15-lora-ism-radios/ground-station-design.md, ../15-lora-ism-radios/ism-band-plans-duty-cycle.md, ../17-test-measurement/sdr-as-test-equipment.md, ../17-test-measurement/spectrum-analyzers.md, ../17-test-measurement/bench-measurement-recipes.md, ../19-regulations-safety/spectrum-allocation-ism-bands.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md]
level: mixed
confidence: medium
last_updated: 2026-10-02
---

# Signal identification and spectrum surveys

## Questions this page answers
- What is this signal on my waterfall, and how do I work out what it is?
- How do I measure the bandwidth, symbol rate (baud) and modulation of an unknown signal?
- How does "cyclostationary" processing find a symbol rate, and why does squaring a signal reveal its carrier?
- What do FM broadcast, ADS-B, AIS, APRS, POCSAG, LoRa, Wi-Fi, Bluetooth, LTE, GNSS and radar look like, and where are they?
- What are the flat square blocks either side of FM broadcast stations?
- Is that signal real, or is my SDR making it (DC spike, image, overload, USB noise)?
- How do I tell the spreading factor of a LoRa signal from a waterfall?
- How do I survey 433 / 868 / 915 MHz at a launch site before flight day, and how long must I listen?
- How do I use rtl_power, heatmap.py, SDR++, inspectrum, URH and rtl_433 for this?
- rtl_433 cannot decode my 433 MHz signal — what next?
- What does the "dBm" column in rtl_power output actually mean?

## TL;DR
- **Workflow**: frequency → *band plan* (what is allowed there) → **bandwidth and spectral shape** → **time structure** (continuous, bursty, period, duty cycle, hopping) → **modulation fingerprints** (demodulate AM/FM and look; constellation; power-law lines) → **symbol rate** → match against a catalogue (sigidwiki, *community wiki*) → decode with the right tool. Most "unknown" signals are identified at the first two steps.
- **Symbol rate from a spectral line**: a linearly modulated signal with excess bandwidth has a discrete line at $R_s$ in the spectrum of $|x|^2$. For root-raised-cosine pulses its amplitude relative to the mean power is exactly **β/π** (derived below; simulated within 3 %): β = 0.35 → line 19 dB below the DC term of $|x|^2$, but it grows ∝ N against noise ∝ √N, so it stands out after a few hundred symbols.
- **Constant-envelope signals hide the |x|² line** (unfiltered PSK, FSK, MSK/GMSK, LoRa): use a delay-product $x(t)x^*(t-T/2)$ (line amplitude 1/π for rectangular PSK), or FM-discriminate, low-pass and square (GFSK BT 0.5: line 35 dB above its surroundings in the script).
- **Power-law carrier test**: raise the IQ to the M-th power — BPSK shows a line at 2Δf after squaring, QPSK only after the 4th power, 8PSK only after the 8th; MSK squared shows *two* lines at 2Δf ± R_b/2. The lowest power that makes a line tells you the PSK order and the carrier offset.
- **OFDM** (Wi-Fi, LTE, 5G NR, DAB, DVB-T): a flat-topped rectangle; its cyclic prefix makes the autocorrelation peak at lag $N_{FFT}$ with height $T_{cp}/(T_u+T_{cp})$ (Wi-Fi 64 + 16 → 0.2), giving the subcarrier spacing.
- **LoRa**: diagonal chirps; symbol time $2^{SF}/BW$ (SF7/125 kHz 1.024 ms … SF12 32.8 ms); measure one chirp's sweep time across the bandwidth to read SF.
- **Launch-site survey**: rtl_power (or hackrf_sweep) over each candidate band for hours with the *flight-like* antenna and LNA; average linearly (rtl_power does), set a detection threshold from noise statistics (K = 100 averages → 1.3 dB above the mean floor for $P_{fa}=10^{-3}$), and remember that a hopping sweep catches a 50 ms burst only ≈ 27 % of the time when it revisits every 260 ms — record IQ on the chosen channel too.
- **rtl_power's "dbm" is dBFS-like, uncalibrated** (the source code itself notes the dB maths is suspect). Calibrate with a known source if you need dBm ([SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md)).

All numbers marked "script" are reproduced by `tools/verify/e3_signal_id.py` (29/29 PASS).

## Intuition (no math)
Identifying a signal is detective work with three kinds of clue. **Where** it is (frequency, and therefore which services are allowed there), **what shape** it has (how wide it is, whether its spectrum is a smooth hump, a flat block, two peaks, a comb of lines or a sloping streak) and **how it behaves in time** (always on, short bursts at regular intervals, hopping around, sweeping). Each family of modulation leaves its own fingerprints: FM broadcast is a wide fuzzy hump that wobbles with the audio; FSK shows two (or four) tones; PSK and QAM are smooth "haystack" humps with a flat top when pulse-shaped; OFDM is a brick with vertical edges; spread spectrum looks like a raised patch of noise; LoRa draws diagonal lines; pulsed radars are wide, short, perfectly periodic splashes.

The cleverest clue is hidden periodicity. A digital signal changes symbol at a fixed rate, so its *statistics* repeat at that rate even though the data are random. Squaring the signal (or multiplying it by a delayed copy of itself) turns that hidden periodicity into an ordinary spectral line you can measure to a fraction of a hertz. That is what "cyclostationary" means: not periodic, but periodic on average. The same trick — raising the signal to a power — strips the data off a PSK carrier and shows you exactly where the carrier is.

Finally, part of every identification is ruling out *your own* receiver: the spike in the middle, the mirror image of a strong signal, harmonics of broadcast FM created by an overloaded front end, and combs of lines from switching power supplies and USB are the most common "mystery signals" on hobby forums ([front-end protection and filtering](sdr-front-end-protection-and-filtering.md)).

## The math

### Level 1 — the numbers you measure and what they imply
- **Occupied bandwidth** $B_{99}$ (Hz): the band containing 99 % of the power ([spectrum analyzers](../17-test-measurement/spectrum-analyzers.md)). For linear modulation with RRC pulses $B = R_s(1+\beta)$, where $R_s$ is the symbol rate (Bd) and β the roll-off ([pulse shaping](../10-comms-modulation/pulse-shaping-isi.md)). So a flat-topped hump 1.35× wider than its symbol rate suggests β ≈ 0.35.
- **FSK**: tone spacing $2\Delta f$ (peak deviation Δf), modulation index $h = 2\Delta f/R_s$, Carson bandwidth $B_C \approx 2(\Delta f + R_s/2)$ for binary FSK. POCSAG (±4.5 kHz) has h = 17.6 / 7.5 / 3.75 at 512 / 1200 / 2400 b/s (script) — two clearly separate tones; AIS GMSK (h = 0.5, 9.6 kb/s) is a single smooth hump.
- **FM analog**: Carson $B_C \approx 2(\Delta f + f_m)$: broadcast stereo 2(75 + 53) = 256 kHz (264 kHz counting the 57 kHz RDS subcarrier) in a 200 kHz-spaced band — strong stations visibly spill into neighbours.
- **Pulses**: a pulse of width τ occupies ≈ 1/τ either side of the carrier (null-to-null 2/τ); the pulse repetition frequency (PRF) appears as line spacing when the analysis bandwidth is below it ([bench recipes §pulsed signals](../17-test-measurement/bench-measurement-recipes.md)).
- **LoRa**: symbol (chirp) time $T_s = 2^{SF}/BW$, chirp slope $BW^2/2^{SF}$ (Hz/s): SF7/125 kHz sweeps 125 kHz in 1.024 ms (1.22 × 10⁸ Hz/s); SF12/125 kHz in 32.8 ms ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)).
- **OFDM**: subcarrier spacing $\Delta f_{sc} = 1/T_u$; symbol $T_u + T_{cp}$. Wi-Fi 20 MHz: 64-point FFT, 312.5 kHz spacing, 3.2 + 0.8 µs = 4 µs symbols; LTE: 15 kHz, normal CP 4.69 µs (5.21 µs on the first symbol of each slot), 7 symbols per 0.5 ms slot (script) [9].
- **Time signatures**: TDMA frame rates are audible and visible — GSM's 8 × 577 µs frame repeats at 216.7 Hz (the "217 Hz buzz" in audio gear), DMR's 2-slot frame is 60 ms, TETRA's 4-slot frame 56.7 ms [7].

**Fingerprints by modulation family** (what to look for first):

| Family | Spectrum | Waterfall / time | Crude demod shows | Rate measurement |
|---|---|---|---|---|
| AM / ASK / OOK | carrier (AM) + symmetric sidebands; OOK has a sinc-like hump | on/off dashes (OOK) | envelope = audio or pulses | pulse widths in inspectrum; $\lvert x\rvert^2$ line |
| Analog FM | wide hump whose width follows loudness | continuous, wobbling | discriminator = audio | — |
| 2/4-FSK | 2 or 4 peaks (large h) or one hump (h ≲ 1) | parallel tone tracks | discriminator = 2/4 levels | discriminator² line |
| MSK / GMSK | smooth single hump, fast sidelobe decay | continuous or TDMA bursts | discriminator = ±levels | $x^2$ lines at $2\Delta f\pm R_b/2$ |
| PSK / QAM (pulse-shaped) | flat-topped haystack, width $R_s(1+\beta)$ | continuous or bursts | ring/spin until carrier lock | $\lvert x\rvert^2$ line; $x^M$ for order |
| OFDM | flat brick, steep edges, often a DC null | constant texture, pilots | noise-like | CP autocorrelation lag |
| DSSS | noise-like hump of width ≈ 2 × chip rate, sinc² | continuous (GNSS below the noise) | noise | chip-rate line in $\lvert x\rvert^2$ if band-limited |
| FHSS | short narrow dashes scattered over a band | hop pattern | per hop: FSK | hop dwell from the time view |
| Chirp (LoRa, FMCW, sounders) | flat block if averaged; diagonals in a spectrogram | sloped lines | discriminator = ramps (sawtooth) | sweep time → SF or chirp rate |
| Pulsed radar | wide sinc envelope; line comb at the PRF | regular splashes; scan modulation | — | PRF from line spacing or time view |

### Level 2 — cyclostationarity and the symbol-rate line (derivations)
**Model.** A linearly modulated complex baseband signal is $x(t)=\sum_k a_k\,p(t-kT)$ with symbol period $T=1/R_s$, i.i.d. zero-mean symbols of power $\sigma_a^2=E|a_k|^2$, and pulse $p(t)$ with spectrum $P(f)$. Its instantaneous power has expectation
$$E|x(t)|^2=\sum_k\sum_l E[a_k a_l^*]\,p(t-kT)p^*(t-lT)=\sigma_a^2\sum_k |p(t-kT)|^2,$$
which is **periodic in T** — the signal is (wide-sense) cyclostationary [1]. Expand it in a Fourier series $E|x(t)|^2=\sum_n c_n e^{j2\pi nt/T}$:
$$c_n=\frac{\sigma_a^2}{T}\int_{-\infty}^{\infty}|p(t)|^2e^{-j2\pi nt/T}\,dt=\frac{\sigma_a^2}{T}\int P(f)\,P^*\!\left(f-\tfrac{n}{T}\right)df .$$
So the spectrum of $|x|^2$ contains a **discrete line at $n/T$** whose strength is the overlap of the pulse spectrum with a copy of itself shifted by $n/T$. A pulse band-limited to $|f|<1/(2T)$ (zero excess bandwidth) gives no overlap and no line; excess bandwidth is what creates it.

**RRC pulses: the line is β/π of the mean power.** For root-raised-cosine $P(f)=\sqrt{RC(f)}$, the overlap of $P(f)$ and $P(f-1/T)$ occurs only in the roll-off region of width β/T. There the two raised-cosine halves are complementary ($RC(f)+RC(f-1/T)=T$), so writing $RC(f)=T\cos^2\theta$ and $RC(f-1/T)=T\sin^2\theta$ with θ running from 0 to π/2 across the region ($df = \tfrac{2\beta}{\pi T}d\theta$):
$$\int P P^*_{shift}\,df=\int T\cos\theta\sin\theta\,df=\frac{T}{2}\cdot\frac{2\beta}{\pi T}\int_0^{\pi/2}\sin2\theta\,d\theta=\frac{\beta}{\pi}.$$
Since $\int RC\,df=1$, $|c_1/c_0|=\beta/\pi$: 0.032 / 0.064 / 0.111 / 0.159 / 0.318 for β = 0.1 / 0.2 / 0.35 / 0.5 / 1 — simulated 0.033 / 0.065 / 0.110 / 0.158 / 0.319 (script §1). Higher harmonics $c_{n\ge2}$ vanish because RRC overlaps only with its nearest shifted copy.

**Constant-envelope signals.** For rectangular (unfiltered) PSK, $|x(t)|^2=1$ always — no line (script: $|c_1|$ = 4 × 10⁻¹⁶). The *delay product* $x(t)x^*(t-\tau)$ restores it: within a fraction τ/T of each symbol it equals $a_ka^*_{k-1}$ (zero mean), elsewhere $|a_k|^2=1$, so its mean is a periodic train of "holes" of width τ and
$$|c_1(\tau)|=\frac{|\sin(\pi\tau/T)|}{\pi},\qquad\text{maximal }(1/\pi)\text{ at }\tau=T/2$$
(script: 0.328 vs 0.318). This $x(t+\tau/2)x^*(t-\tau/2)$ averaged against $e^{-j2\pi\alpha t}$ is the **cyclic autocorrelation function** (CAF) $R_x^\alpha(\tau)$; its Fourier transform over τ is the **spectral correlation function** (SCF) $S_x^\alpha(f)$ [1], [2]. The simple $|x|^2$ test is the CAF at τ = 0.

**FSK and GMSK.** The FM discriminator output $d(t)=\tfrac{1}{2\pi}\tfrac{d\phi}{dt}$ of a CPFSK signal is a *real PAM signal* of the bits, $d(t)=\Delta f\sum_k b_k g(t-kT)$, so the same argument applies to $d^2$: Gaussian-filtered (GFSK/GMSK) or receiver-filtered FSK shows a line at $R_s$ (script §3: 35 dB above its local spectrum for BT = 0.5); an *ideal* NRZ FSK would not (its $d^2$ is constant) — real receivers' IF filters always provide the transitions.

**Power-law (x^M) carrier lines.** For M-PSK, $a_k^M$ is the same constant for every symbol, so $x(t)^M$ contains a deterministic component at $M\Delta f$ ($\Delta f$ = carrier offset); lower powers average to zero. Squaring MSK (h = ½) doubles its index to h = 1, i.e. Sunde FSK, whose tones are discrete lines at $2\Delta f\pm R_b/2$. Script §2 (QPSK etc. RRC β = 0.35, 10 dB SNR, 8192 symbols): BPSK² line 51 dB above the local spectrum; QPSK² 3.8 dB (no line), QPSK⁴ 38 dB; 8PSK⁴ 1.4 dB (none), 8PSK⁸ 21 dB; MSK² +38 dB at both ±R_b/2 and none at the centre. Noise enhancement grows with M (each power multiplies noise terms), so the 8th-power test needs more SNR or more symbols.

**OFDM cyclic prefix.** Each OFDM symbol repeats its last $N_{cp}$ samples at the front, so $E[x[n]x^*[n+N]]$ is non-zero only during the prefix: the autocorrelation at lag $N$ (the FFT size) is $N_{cp}/(N+N_{cp})$ of the power, and that correlation repeats every $N+N_{cp}$ samples — a cyclic frequency $1/(T_u+T_{cp})$ (script §4: peak at lag 64, height 0.198; 250 kHz cyclic frequency for Wi-Fi at 20 MS/s) [2].

**Survey statistics.** A periodogram bin of noise is exponentially distributed; the linear average of K independent bins is Gamma(K, 1/K) (mean 1). The threshold for false-alarm probability $P_{fa}$ is $\gamma=F^{-1}_{\Gamma(K)}(1-P_{fa})$: K = 1 → $\ln(1/P_{fa})$ = 8.4 dB above the mean for $10^{-3}$; K = 10 → 3.6 dB; K = 100 → 1.3 dB; K = 1000 → 0.4 dB (script §8). The minimum per-bin SNR for $P_d$ = 0.9 (non-central χ²) is 10.8 / 3.4 / −2.9 / −8.3 dB for the same K — averaging buys sensitivity as $\approx 5\log_{10}K$ dB for steady signals but *not* for bursts shorter than the averaging time, which are diluted by the duty cycle.

**Intercept probability.** A receiver that visits a given frequency for a dwell $T_d$ every revisit period $T_r$ (all other hops in between) catches *any part* of a randomly timed burst of length τ with probability $\min(1,(\tau+T_d)/T_r)$ and the *whole* burst with $\max(0,(T_d-\tau)/T_r)$ (script §7, Monte Carlo agrees to 0.002). A 50 ms LoRa packet against 13 hops of 20 ms (260 ms revisit) is glimpsed 27 % of the time and never captured whole; a beacon repeating independently needs ≈ 15 repetitions for 99 % confidence of being seen at all.

### Level 3 — general theory, estimator accuracy and limits
- **Spectral correlation function.** $S_x^\alpha(f)=\lim \frac{1}{\Delta t}E\{X_{\Delta t}(t,f+\alpha/2)X^*_{\Delta t}(t,f-\alpha/2)\}$ measures correlation between spectral components separated by α; it is non-zero only at the signal's cycle frequencies (symbol rate and harmonics for single-carrier signals, $1/(T_u+T_{cp})$ multiples for OFDM, chip rate for DSSS). Stationary noise has no features at α ≠ 0, so the SCF can detect signals buried below the noise floor and separate signals that overlap in frequency but differ in symbol rate [1], [2]. The **conjugate** SCF (using $x(t+\tau/2)x(t-\tau/2)$, no conjugate) shows lines at $2f_c\pm\alpha$ for real-symbol modulations (BPSK, ASK, MSK-type), which is the frequency-domain version of the squaring test [2].
- **Estimators.** Practical estimators compute the FFT accumulation method (FAM) or the strip spectral correlation analyser (SSCA) over all α, or the cheap $|x|^2$ / delay-product line search when only the strongest feature is needed. Maximising the cyclic-correlation magnitude over α gives a symbol-rate estimate whose standard deviation falls as $N^{-3/2}$ for N observed symbols, like a sinusoid-frequency estimate [3] (script §9: relative std 1.5 × 10⁻⁴ / 1.6 × 10⁻⁵ / 2.3 × 10⁻⁶ at 256 / 1024 / 4096 QPSK symbols; fitted slope −1.51).
- **Modulation classification beyond the line tests** uses higher-order cumulants (e.g. $C_{40}$, $C_{42}$ normalised by $C_{21}^2$ separate BPSK/QPSK/8PSK/16QAM in theory) or likelihood/feature-based classifiers; surveys compare these and machine-learning classifiers [4]. For a hobby workflow, constellation inspection after the timing/carrier loop of [software demodulation](software-demodulation.md) is usually conclusive.
- **Where the clean results break**: (i) multipath and fading smear constellations and add spurious cyclic features at the delay spread; (ii) two signals with the same symbol rate on the same carrier are not separable by α; (iii) a sample rate that is an exact multiple of the symbol rate can produce artefact lines at harmonics of $f_s/\text{sps}$ in simulations (PySDR deliberately uses fractional delays [2]); (iv) receiver non-linearity creates cyclic features of its own (IM products of two signals have cycle frequencies of both); (v) frequency hoppers need the time–frequency view first — features are per-hop.

## Design equations & rules of thumb

| Quantity | Relation | When valid | Typical values |
|---|---|---|---|
| RRC occupied BW | $B=R_s(1+\beta)$ | linear modulation | β 0.2–0.5 |
| Symbol line in $\lvert x\rvert^2$ | $\lvert c_1/c_0\rvert=\beta/\pi$ | RRC, i.i.d. symbols | β 0.35 → −19 dB |
| Delay-product line | $\lvert c_1\rvert=\lvert\sin(\pi\tau/T)\rvert/\pi$ | rectangular PSK | τ = T/2 → 1/π |
| PSK order test | line in $x^M$ at $M\Delta f$; lowest M with a line = order | M-PSK | BPSK 2, QPSK 4, 8PSK 8 |
| MSK/GMSK test | $x^2$ lines at $2\Delta f\pm R_b/2$ | h = ½ CPFSK | AIS, GSM |
| FSK index | $h=2\Delta f/R_s$ | 2-FSK | POCSAG 1200: 7.5 |
| OFDM CP | $r(N)/r(0)=N_{cp}/(N+N_{cp})$ | CP-OFDM | Wi-Fi 0.2 |
| LoRa symbol | $T_s=2^{SF}/BW$ | CSS | SF7/125: 1.024 ms |
| Survey threshold | Gamma(K) quantile | linear K-average | K 100: +1.3 dB at $P_{fa}=10^{-3}$ |
| Intercept | $P=\min(1,(\tau+T_d)/T_r)$ | hopping survey | 50 ms burst, 20/260 ms → 0.27 |
| Rs estimator | std ∝ $N^{-3/2}$ | cyclic-correlation peak | 1000 symbols → ~10⁻⁵ relative |
| Spectrogram window for a chirp | $\approx 1/\sqrt{\text{slope}}$ | linear chirps | SF7/125: ≈ 90 µs; SF12: ≈ 0.5 ms |

## Catalogue of common signals
Numbers are from the governing standards where noted, otherwise from sigidwiki (a *community wiki* — good for "what does it look like", verify numbers before relying on them) [5]; Singapore notes refer to [ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md) and [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md).

| Signal | Where | Bandwidth | Modulation / rate | Time signature | Waterfall look | Decode with |
|---|---|---|---|---|---|---|
| AM broadcast | 531–1611 kHz (9 kHz raster in Regions 1/3) | ≈ 9–10 kHz | DSB-AM, carrier | continuous | carrier + symmetric sidebands | any SDR app |
| HF utility/ham | 3–30 MHz | 50 Hz (FT8) – 3 kHz (SSB) | FT8: 8-FSK, 6.25 Hz tones; RTTY 170 Hz shift | FT8 in 15 s slots (12.64 s TX) | stacks of short narrow streaks | WSJT-X, fldigi |
| Ionosonde / chirp sounder | 1–40 MHz | sweeping | FMCW/pulses | slow sweep across HF | slanted line across the waterfall | — |
| Broadcast FM | 87.5–108 MHz | ≈ 200–260 kHz | WFM ±75 kHz, stereo pilot 19 kHz, RDS 57 kHz | continuous | wide fuzzy hump | SDR++ WFM, RDS decoders |
| HD Radio (IBOC, North America) | inside the FM band, ±129–198 kHz from the analog carrier | ≈ 400 kHz total | OFDM sidebands | continuous | **flat rectangles either side** of an FM station | nrsc5 |
| Airband voice / ACARS | 118–137 MHz | 8.33/25 kHz; ACARS ≈ 5 kHz | AM; ACARS MSK on AM | bursty | narrow AM carriers | acarsdec |
| Weather satellites | 137–138 MHz | ≈ 34–40 kHz (APT) / ≈ 120 kHz (LRPT) | FM/AM-subcarrier (APT), QPSK (LRPT) | pass of 10–15 min with Doppler | slanted narrow trace | SatDump |
| APRS | 144.390 (N. America, Malaysia, Indonesia, Thailand), 144.800 (Europe), 145.175 (Australia) MHz; check the local band plan | ≈ 10–12.5 kHz | 1200 b/s Bell-202 AFSK on NFM | bursts ≈ 0.3–1 s | short NFM bursts | direwolf, multimon-ng |
| AIS | 161.975 / 162.025 MHz | 25 kHz channel | GMSK 9.6 kb/s, h = 0.5 | ≈ 26.7 ms slots, bursty | short smooth bursts on both channels | AIS-catcher, rtl-ais |
| POCSAG / FLEX paging | VHF/UHF paging bands (e.g. 138–175, 929–932 MHz in the US) | ≈ 9–15 kHz | POCSAG 2-FSK ±4.5 kHz, 512/1200/2400 b/s; FLEX 2/4-FSK 1600–6400 b/s | long bursts with preamble | **two parallel tone tracks** | multimon-ng, PDW |
| DMR / TETRA / P25 | VHF/UHF land mobile (TETRA 380–400 MHz in many countries) | 12.5 / 25 kHz | DMR 4FSK 4.8 kBd, 2-slot 60 ms; TETRA π/4-DQPSK 18 kBd, 4-slot 56.7 ms | TDMA bursts | pulsing narrow blocks | DSD+, SDRTrunk |
| Radiosondes | 400.15–406 MHz (meteorological aids) | ≈ 10 kHz | GFSK (e.g. 4.8 kBd on common sondes; unverified here) | 1 s frames during a balloon flight | narrow trace drifting with temperature | radiosonde_auto_rx |
| 433 MHz SRDs | 433.05–434.79 MHz (often 433.92) | 10–200 kHz | OOK/ASK, FSK; PWM/Manchester coding | short bursts, repeated 3–10× | dashes at one frequency | rtl_433, URH |
| LoRa | 433, 863–870, 902–928, 917–925 (SG) MHz | 125/250/500 kHz | CSS, SF7–12 | packets of tens of ms–s | **diagonal chirps**, preamble of up-chirps then 2.25 down-chirps | gr-lora_sdr, SDR++ plugin |
| Sigfox | ≈ 868 MHz (EU) / 920 MHz | ≈ 100 Hz | DBPSK ultra-narrowband | 3 repetitions on random frequencies | tiny dots | — |
| DVB-T/T2, ATSC | UHF TV | 6–8 MHz | OFDM (DVB-T/T2) or 8VSB with pilot at the lower edge (ATSC) | continuous | flat brick (DVB) / brick with a lone carrier on the left (ATSC) | gr-dtv |
| GSM | 900/1800 MHz (850/1900 Americas) | 200 kHz | GMSK 270.833 kb/s | TDMA 4.615 ms frame (216.7 Hz) | narrow carriers, BCCH always on | gr-gsm |
| LTE / 5G NR | cellular bands (e.g. band 8 925–960 MHz downlink next to SG 917–925 MHz) | 1.4–20 MHz (LTE), up to 100 MHz (NR FR1) | OFDM 15 kHz (LTE), 15–30 kHz (NR) | continuous downlink, bursty uplink | flat brick with reference-signal texture | LTE-Cell-Scanner, srsRAN |
| ADS-B / Mode S | 1090 MHz (Mode S replies, ADS-B); 1030 MHz interrogations; 978 MHz UAT (US) | ≈ 2 MHz | PPM 1 Mb/s, 8 µs preamble + 112 µs | random short pulses (≈ 120 µs) | faint speckle; obvious in time domain | dump1090, readsb |
| GNSS | 1575.42 (GPS L1/Galileo E1), 1561.098 (BeiDou B1I), ≈ 1602 (GLONASS) MHz | 2.046 MHz null-to-null for C/A | BPSK-DSSS 1.023 Mchip/s; BOC on Galileo | continuous, **below the noise** | invisible; a visible hump means a jammer or your own LNA oscillating | GNSS-SDR |
| Iridium | 1616–1626.5 MHz | 31.5 kHz in 41.667 kHz channels | DE-QPSK, TDMA | 90 ms frames | short bursts with Doppler | gr-iridium |
| Wi-Fi | 2.4 / 5 GHz | 20/40/80 MHz | OFDM (11a/g/n/ac/ax), DSSS 11 Mchip/s (11b, 22 MHz) | bursty frames, beacons ~102 ms | blocks with a dip at DC (null subcarrier) | Wireshark + monitor mode |
| Bluetooth / BLE | 2402–2480 MHz | 1 MHz (BR) / 2 MHz (BLE) | GFSK 1 Msym/s, hopping (BR 1600 hops/s) | short hops; BLE adverts on 2402/2426/2480 | scattered short dashes | Ubertooth, sniffle |
| 802.15.4 / Zigbee | 2405–2480 MHz (5 MHz spacing), 868/915 | 2 MHz | O-QPSK 2 Mchip/s DSSS | bursty | short narrow blocks | Wireshark |
| Radars | marine 2.9–3.1 / 9.3–9.5 GHz; weather 5.6 GHz; automotive 76–81 GHz | MHz–GHz | pulses or FMCW | precise PRF; rotating antennas → bursts every few s | wide periodic splashes; sweeping lines (FMCW) | — |

Sources for rows: AIS, APRS, POCSAG, FLEX, ADS-B, LoRa, DMR, TETRA, Iridium, HD Radio, FT8, ionosonde, ATSC/DAB, GSM, Zigbee, Sigfox from sigidwiki entries [5]; LTE numerology from 3GPP TS 36.211 (script check) [9]; GPS C/A chip rate from IS-GPS-200 (via [GNSS signals](../21-gnss/gnss-signals-and-codes.md)); LoRa from [15](../15-lora-ism-radios/lora-phy-css-math.md); HD Radio sideband offsets and radiosonde baud from general knowledge (unverified here).

### "Signals" your own receiver makes

| Artefact | Fingerprint | Test |
|---|---|---|
| DC spike / LO leakage (zero-IF SDRs; 0 Hz line on a swept SA) | always at the tuned centre | retune by 100 kHz: it follows the centre ([IQ](iq-complex-baseband.md)) |
| IQ image | mirror of a strong signal about the centre, 25–40 dB down | it moves the *opposite* way when you retune |
| Front-end overload / harmonics | e.g. broadcast FM heard at 2×, 3×, 4× (≈ 200–430 MHz) with n× the deviation; IM products between strong stations | add 10 dB of attenuation: an n-th-order product drops 10n dB; an FM band-stop filter removes it ([front-end page](sdr-front-end-protection-and-filtering.md)) |
| Tuner/clock spurs | fixed lines at multiples of the reference (28.8 MHz on RTL-SDRs) | present with a 50 Ω load on the input |
| Switching-supply combs | evenly spaced lines (spacing = switching frequency, tens of kHz–MHz), drifting with load/temperature | run from a battery; move a ferrite; unplug chargers |
| USB 3 / computer noise | broadband rise near 2.4 GHz, combs from displays and buses | longer USB-2 extension, ferrites, different port |
| Aliases (direct sampling) | signals from another Nyquist zone ([sampling](sampling-aliasing-bandpass-sampling.md)) | change the sample rate: aliases move, real signals don't |

## Worked examples

**Example 1 — an unknown burst at 433.92 MHz that rtl_433 will not decode (D2 #478).**
1. Record IQ, not audio: `rtl_sdr -f 433.82M -s 1.024M -g 30 burst.cu8` (100 kHz offset tuning keeps the burst off the DC spike), with a SigMF metadata file ([software stack](gnu-radio-and-software-stack.md)).
2. Open in **inspectrum**: the burst is 30 kHz wide, ≈ 80 ms long, repeated 4× with 10 ms gaps. Amplitude plot shows on/off keying; place the symbol cursors over the pulses: short pulses 250 µs, long 750 µs, period 1 ms → **OOK with PWM** at 1 kBd, 64 bits per repetition.
3. Confirm with `rtl_433 -A` (pulse analyser), which prints the pulse/gap histogram and a guessed coding; if no device decoder exists, write a flex decoder (`-X "n=name,m=OOK_PWM,s=250,l=750,r=4000"`), or use **URH** to demodulate, slice bits and compare repeated transmissions to find checksums.
4. Fingerprint check: an OOK signal shows no line in $x^2$ at a carrier offset (amplitude only) but a strong line at the bit rate in $|x|^2$ — 1 kHz here.

**Example 2 — the "56k modem" on VHF (D1 #493).** A ≈ 12 kHz-wide signal at 152–158 MHz with two parallel traces and a warbling sound. Tone separation measured on a 50 Hz-RBW spectrum: 9.0 kHz → ±4.5 kHz deviation. FM-demodulate, low-pass at 2 kHz and square: line at 1200 Hz (or count bits in inspectrum: 833 µs per bit). Rate 1200 b/s, h = 7.5, long bursts starting with an alternating preamble → **POCSAG 1200** [5]; decode with multimon-ng. If the line were at 1600 or 3200 Hz and four tone levels appeared, it would be **FLEX** [5].

**Example 3 — the flat blocks either side of an FM station (D2 #249, #465).** Two rectangles, each ≈ 70 kHz wide, starting ≈ 130 kHz either side of an FM carrier and ≈ 20–25 dB below it, with vertical edges and a noise-like interior → OFDM sidebands of **HD Radio (IBOC)**, used in North America [5] (offsets from general knowledge). The CP autocorrelation test (lag = FFT size) confirms OFDM; `nrsc5` decodes it. In Singapore you will not see these; similar-looking flat blocks at 174–240 MHz are DAB, at UHF digital TV.

**Example 4 — symbol rate of an unknown PSK carrier.** A 34 kHz-wide flat-topped hump at 437.0 MHz (a CubeSat downlink candidate). Record 0.5 s at 250 kS/s. (a) $|x|^2$ spectrum: line at 25.00 kHz, ≈ 20 dB below the DC term → $R_s$ = 25 kBd, and since $\beta/\pi \approx 0.1$, β ≈ 0.3–0.4, consistent with $B = 25(1+0.35) = 33.8$ kHz. (b) Power-law test: no line in $x^2$, clear line in $x^4$ at 4 × (+1.2 kHz) → QPSK with a +1.2 kHz offset (Doppler + LO error). (c) With 12 500 symbols in the record, the Ciblat-type estimator gives a relative error ≈ 10⁻⁶ (script §9 scaling), i.e. ±0.03 Bd — far better than needed to start a timing-recovery loop ([software demodulation](software-demodulation.md)).

**Example 5 — reading LoRa's spreading factor.** In SDR++ (or inspectrum) with an FFT of ≈ 90 µs (≈ 11 kHz resolution, the optimum $1/\sqrt{\text{slope}}$ for SF7/125 kHz, script §5) the preamble shows eight identical up-chirps. Each sweeps the full 125 kHz in 4.1 ms → $2^{SF} = 4.1\text{ ms} \times 125\text{ kHz} = 512$ → **SF9**. Then 2 sync symbols and 2.25 down-chirps follow ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)). A wrong FFT size (e.g. 8 ms window at SF7) smears chirps into a flat block that looks like OFDM — a common misidentification.

**Example 6 — launch-site survey before flight day (902–928 MHz, US competition).**
1. *Set-up*: the ground-station antenna (Yagi or collinear), the same LNA + SAW chain, RTL-SDR at fixed gain (AGC off), laptop on battery. Terminate the input with 50 Ω first and record a 10-minute "floor" file to learn your own spurs.
2. *Sweep*: `rtl_power -f 902M:928M:10k -c 25% -i 2 -g 30 -e 6h site.csv` → 13 hops at 2.667 MS/s, 5.2 kHz bins (script §6). Convert with `heatmap.py` to a waterfall image; plot per-bin occupancy (fraction of intervals above threshold).
3. *Threshold*: the CSV "samples" column gives K per row; with K ≈ 100 use +1.3 dB over the median floor for $P_{fa}=10^{-3}$ (script §8). Strong, steady occupants (paging at 929 MHz, RFID readers, LoRaWAN gateways, other teams' telemetry, GPS trackers) are obvious; bursty ones are under-counted by the intercept factor (Level 2), so…
4. *Dwell*: after choosing two candidate channels, record IQ continuously on each (1 MS/s, 30 min) — no intercept loss — and run gr-lora_sdr to count foreign LoRa packets and measure their RSSI.
5. *Decide*: choose the channel with the lowest 95th-percentile floor and no co-channel LoRa at your SF/BW; note the raised floor ΔN (sensitivity loss = ΔN dB) in the link budget ([LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)); register it with the competition's frequency coordinator.
For Singapore test sessions repeat at 433.05–434.79 MHz (one hop, script §6) and 917–925 MHz (4 hops), and check 925–960 MHz cellular levels at the site, because band-8 downlinks sit right above the SRD band ([ground station](../15-lora-ism-radios/ground-station-design.md)).

**Example 7 — is there a GNSS jammer at the pad?** GNSS signals are ≈ 20 dB *below* the thermal noise in 2 MHz, so a healthy L1 spectrum is flat. Sweep 1574–1577 MHz (2 hops) through the GNSS antenna and its LNA; any hump or line ≥ 3 dB above the floor measured with the antenna replaced by a 50 Ω load (and the LNA still powered) is either interference or the LNA oscillating — decide by disconnecting the antenna ([bring-up playbook](../17-test-measurement/rf-bring-up-debug-playbook.md)).

**Example 8 — "a big blob of signals next to 7.2 MHz" on 40 m (D2 #62, #72).** Look up the ITU allocation first: in Regions 1 and 3 (Singapore is Region 3) the amateur 40 m band is 7.000–7.200 MHz and broadcasting occupies 7.200–7.450 MHz; Region 2 amateurs have 7.000–7.300 MHz (ITU Radio Regulations Article 5, general knowledge). So the blob is a cluster of **AM shortwave broadcasters** on a 5 kHz raster — each a carrier with ≈ ±4.5 kHz sidebands that fade together. Other HF shapes to recognise: ionosondes draw a slanted line across many MHz [5]; over-the-horizon radars are wide (tens of kHz) repetitive sweeps that sound like rapid ticking; FT8 sits in 3 kHz windows (e.g. 7.074 MHz) as many 50 Hz-wide stacks that start every 15 s [5]; multi-tone HF modems show N equally spaced tones whose spacing is at least the keying rate (orthogonality). If the blob appears at many unrelated frequencies and grows faster than 1 dB per dB when you remove attenuation, it is front-end overload instead.

**Example 9 — mystery signals at 672–682 MHz (D2 #468).** The method, not the answer, is the point: (i) check the national table — in Europe this is DVB-T/T2 UHF TV (8 MHz channels 46–47 span 670–686 MHz); in the US the 600 MHz cellular band (LTE band 71) uses 663–698 MHz for *uplink* (band numbers from general knowledge — verify against 3GPP TS 36.101); (ii) measure the shape: a continuous flat 7.6 MHz brick = DVB-T; bursty 5–20 MHz blocks that come and go with phones nearby = LTE uplink (SC-FDMA, so the CP test still shows a lag-2048-at-30.72-MS/s peak); (iii) confirm with the CP autocorrelation lag, which gives the FFT size and hence the standard (DVB-T 2k/8k modes vs LTE 15 kHz).

## Practical notes

### Step-by-step identification workflow
1. **Is it real?** 50 Ω load on the input → does it vanish? Retune by a non-multiple of the step → does it move the right way? Add 10 dB of attenuation → does it drop exactly 10 dB? (Real: yes / yes / yes.)
2. **Where?** Note the centre frequency to the nearest kHz and look it up in the allocation table and band plan; list the 2–3 services allowed there.
3. **How wide and what shape?** Measure the −3 dB, −20 dB and 99 % bandwidths with a calibrated RBW; classify the shape (carrier + sidebands, two tones, haystack, brick, noise-like hump, comb, chirp).
4. **When?** Continuous or bursty? Burst length, period, duty cycle, slot structure; hopping or sweeping? Use the amplitude-vs-time plot.
5. **Demodulate crudely.** AM (envelope) shows OOK/ASK and pulse coding; FM (discriminator) shows FSK levels, chirp ramps and analog audio; look at the constellation only after carrier recovery.
6. **Measure rates.** Symbol rate from the $|x|^2$ line (pulse-shaped single carrier), the delay product (constant envelope) or the discriminator² line (FSK); PSK order and carrier offset from the power-law test; OFDM FFT size from the CP lag; LoRa SF from the chirp time.
7. **Match and decode.** Compare (frequency, bandwidth, modulation, rate, timing) against sigidwiki and the catalogue above, then decode with the dedicated tool; if none exists, use URH to slice bits and look for preambles, sync words and checksums ([packet framing](../10-comms-modulation/packet-framing-protocols.md)).
8. **Record what you found** (SigMF file + a note of the parameters) — a future team member will see the same signal at the next launch.

### Tools at a glance

| Tool | Best for | Notes |
|---|---|---|
| SDR++ / SDR# / GQRX / SDRangel | browsing, listening, band-plan overlays | SDRangel adds many demodulators and a LoRa plugin |
| inspectrum | measuring burst length, symbol period, chirp time with cursors | opens SigMF / cf32 / cu8 recordings |
| URH (Universal Radio Hacker) | OOK/FSK/PSK demodulation, bit slicing, protocol diffing | autodetects modulation parameters on clean captures |
| rtl_433 | 315/433/868/915 MHz sensors; `-A` pulse analyser; flex decoders | hundreds of device decoders |
| rtl_power + heatmap.py, hackrf_sweep | long surveys, waterfall images, occupancy statistics | uncalibrated levels; check the hop plan |
| multimon-ng, direwolf, dump1090, AIS-catcher | POCSAG/FLEX/AFSK, APRS, ADS-B, AIS | standard public services |
| GNU Radio / Python (numpy) | cyclostationary tests, custom detectors | reuse `tools/verify/e3_signal_id.py` functions |

### What a survey report should contain
Site, date/time span, antenna and its pointing, LNA/filter chain, SDR model and fixed gain, calibration offset (dB) and its date; per band: hop plan, bin width, K per row, threshold rule; noise-floor median and 95th percentile (dBm/Hz after calibration); a list of occupants (frequency, bandwidth, duty cycle, peak level, identification and confidence); the chosen channels and the sensitivity penalty assumed in the link budget. This is the "record everything" discipline applied to RF — it makes next year's survey a comparison rather than a new mystery.

### More notes
- **Look up the band plan first.** National tables (Singapore IMDA spectrum chart, FCC table, ITU Radio Regulations) explain most signals instantly; sigidwiki's search by frequency/bandwidth and its companion app *Artemis* add waterfall images and sound samples [5].
- **Record IQ with metadata** (SigMF): centre, rate, gain, antenna, time — identification often needs a second look later, and a team member can replay it ([software stack](gnu-radio-and-software-stack.md)).
- **Tools**: *SDR++/SDR#/GQRX/SDRangel* to look and listen; *inspectrum* for measuring burst lengths, symbol rates and chirps with cursors; *URH* for OOK/FSK/PSK demodulation, bit slicing and protocol comparison; *rtl_433* (-A) for 315/433/868/915 MHz sensors; *rtl_power* or *hackrf_sweep* for long surveys (heatmap.py for waterfalls); *GNU Radio* or Python for custom feature tests (the snippets in `tools/verify/e3_signal_id.py` are directly reusable on recorded IQ) [2], [6].
- **rtl_power details** (from its source code [6]): hops are evenly sized and ≤ 2.8 MS/s; bins are a power-of-two split; the DC bin is overwritten by its neighbour; power is averaged *linearly* over the integration interval; the "dbm" columns are relative (uncalibrated), and cropping (`-c 20–50 %`) discards the filter-roll-off edges of each hop.
- **Gain and averaging**: fix the gain, keep the strongest signal ≥ 10 dB below clipping (watch for the overload artefacts above), and prefer linear (power) averaging for occupancy; log-averaged displays read noise 2.5 dB low (script) ([FFT](fft-spectral-analysis-windows.md)).
- **Time-domain views** often beat the waterfall: ADS-B, radar and TDMA are obvious in an amplitude-vs-time plot at high sample rate.
- **Legal note**: listening is generally legal but decoding and disclosing some services (cellular, private mobile radio, encrypted traffic) is not in many jurisdictions; keep identification to waveform-level characteristics unless the service is public (ADS-B, AIS, APRS, weather satellites, your own telemetry) ([19](../19-regulations-safety/_index.md)).

## Common mistakes & misconceptions
1. **"It's a mystery signal"** — when it is the SDR's DC spike, IQ image, a harmonic of broadcast FM in an overloaded front end, or a USB/SMPS comb. Always run the 50 Ω-load and 10 dB-pad tests first.
2. **Measuring baud on a constant-envelope signal with |x|²** — there is no line; use the delay product or the discriminator-squared method.
3. **Reading the PSK order from the constellation before carrier recovery** — a spinning constellation is a ring for every PSK; the power-law test gives the order and the offset in one step.
4. **Too short or too long an FFT window on chirps** — smears LoRa into a block; use ≈ $1/\sqrt{\text{slope}}$.
5. **Concluding a band is empty from one sweep** — intercept probability for bursty users can be tens of percent per pass; survey for hours, then dwell on the chosen channel.
6. **Setting an occupancy threshold by eye on a log-averaged waterfall** — the floor is biased 2.5 dB low and its spread depends on K; derive the threshold from the statistics.
7. **Treating rtl_power "dBm" as dBm.** It is a relative level until calibrated.
8. **Assuming a flat-topped block is OFDM** — RRC single carriers with small β are also flat-topped; the CP autocorrelation (OFDM) vs a line in $|x|^2$ (single carrier) decides.
9. **Expecting to see GNSS signals on a spectrum** — they are below the noise; a visible signal at L1 is a problem, not GPS.
10. **Calling FSK "AM" because the SDR app's AM mode makes a noise** — any signal makes noise in an envelope detector; the discriminator view (two levels) or the spectrum (two tones) decides.
11. **Confusing symbol rate with bit rate** — 4FSK at 4.8 kBd carries 9.6 kb/s (DMR); QPSK at 25 kBd carries 50 kb/s before coding. The spectral line gives *symbols* per second.
12. **Surveying with a different antenna or gain than the flight-day ground station** — the occupancy and floor you measure are only valid for that chain; a high-gain Yagi pointed at the horizon sees far more than the whip you surveyed with.

## How to simulate / verify
- `python3 tools/verify/e3_signal_id.py` (output in `tools/verify/e3_signal_id_output.txt`): (1) β/π symbol line vs simulation, rectangular-PSK delay product; (2) power-law lines for BPSK/QPSK/8PSK/MSK with a local-median detector; (3) GFSK discriminator-squared line; (4) OFDM CP autocorrelation, LTE numerology; (5) LoRa chirp times; (6) rtl_power hop plan; (7) burst intercept vs Monte Carlo; (8) Gamma/non-central-χ² thresholds and the −2.51 dB log bias; (9) estimator std ∝ $N^{-1.5}$; (10) catalogue FSK indices, Carson bandwidths, GSM frame rate.
- On real data: apply the same functions to SigMF recordings; PySDR's cyclostationary chapter has SCF (FSM/TSM/FAM) implementations to extend this [2].
- Calibrate a survey receiver's level and check its linearity with the 10 dB pad test before trusting occupancy numbers ([SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md)).

## Open questions / gaps
- No team survey data yet: the first launch-site campaign should replace Example 6 with measured occupancy, floor percentiles and a recommended channel list.
- HD Radio sideband offsets, radiosonde baud rates and HF parallel-tone modem parameters are from general knowledge/sigidwiki and were not checked against the standards (NRSC-5, WMO, MIL-STD-188-110).
- Gardner (1991) and the Ciblat et al. (2002) paper were used via abstracts/citation records and PySDR; the derivations here are our own and checked numerically, not compared line by line with the papers.
- Cumulant-based classification and FAM/SSCA estimators are described, not implemented in `tools/`.
- Singapore-specific occupancy (e.g. what already uses 433.05–434.79 and 917–925 MHz near candidate sites) is unknown.

## Sources
1. W. A. Gardner, "Exploitation of spectral redundancy in cyclostationary signals," *IEEE Signal Processing Magazine* 8(2):14–36 (1991), doi:10.1109/79.81007. (peer-reviewed; citation verified, used for definitions — not re-read)
2. M. Lichtman and S. Brown, "Cyclostationary Signal Processing," in *PySDR: A Guide to SDR and DSP using Python*, https://pysdr.org/content/cyclostationary.html (read 2026-09-29). (online textbook) — CAF/SCF definitions, |x|-FFT shortcut, conjugate SCF lines at 2f_c ± α, OFDM CP cycle frequency, roll-off effects, FSM/TSM/FAM code.
3. P. Ciblat, P. Loubaton, E. Serpedin, G. B. Giannakis, "Asymptotic analysis of blind cyclic correlation-based symbol-rate estimators," *IEEE Trans. Information Theory* 48(7):1922–1934 (2002), doi:10.1109/TIT.2002.1013133. (peer-reviewed; abstract) — consistency, $N^{-3/2}$ convergence.
4. O. A. Dobre, A. Abdi, Y. Bar-Ness, W. Su, "Survey of automatic modulation classification techniques: classical approaches and new trends," *IET Communications* 1(2):137–156 (2007); A. Swami, B. M. Sadler, "Hierarchical digital modulation classification using cumulants," *IEEE Trans. Communications* 48(3):416–429 (2000). (peer-reviewed; cited from the literature, not re-read)
5. Signal Identification Wiki (sigidwiki.com), entries for AIS, APRS, POCSAG, FLEX, ADS-B, LoRa, GSM, DMR, TETRA, Iridium, HD Radio (FM), FT8, Ionosonde, ATSC, DAB, Zigbee, Sigfox, TPMS, RNSS/GPS, and the Signal Identification Guide (raw pages fetched 2026-09-29/10-02). (**community wiki** — anyone can edit; used for signal appearance and typical parameters)
6. Osmocom rtl-sdr, `src/rtl_power.c` (master branch, read 2026-09-29), https://github.com/osmocom/rtl-sdr — hop plan (≤ 2.8 MS/s), power-of-two bins, crop, DC-bin replacement, linear averaging, uncalibrated "dbm"; heatmap.py by K. Keenan (kmkeen.com; not fetched). (open-source code)
7. ETSI EN 300 392 (TETRA) and ETSI TS 102 361 (DMR) frame structures as summarised by sigidwiki [5]; GSM 45.002 frame timing (general knowledge, checked arithmetically in the script). (standards, secondary)
8. RTL-SDR Blog V4 datasheet v1.0 (2024), https://www.rtl-sdr.com/wp-content/uploads/2024/12/RTLSDR_V4_Datasheet_V_1_0.pdf — 28.8 MHz upconverter LO, triplexer/notch, desense test method. (manufacturer)
9. 3GPP TS 36.211, *E-UTRA Physical channels and modulation*, §6.12 (OFDM baseband signal generation: 15 kHz, CP lengths 160/144 samples at 30.72 MS/s) — cited from general knowledge, checked arithmetically. (standard)
10. This repository: `tools/verify/e3_signal_id.py`; [software demodulation](software-demodulation.md); [front-end protection](sdr-front-end-protection-and-filtering.md). (verification / cross-references)
