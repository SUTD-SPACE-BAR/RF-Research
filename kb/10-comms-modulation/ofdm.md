---
title: OFDM — orthogonal frequency-division multiplexing
domain: 10-comms-modulation
slug: ofdm
tags: [OFDM, subcarrier, DFT, FFT, cyclic-prefix, guard-interval, orthogonality, PAPR, CFO, ICI, Schmidl-Cox, pilots, channel-estimation, Wi-Fi, LTE, DVB-T, OFDMA]
prerequisites:
  - digital-modulation-psk-qam-fsk.md
  - pulse-shaping-isi.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
related:
  - synchronization-carrier-timing.md
  - channel-coding-fec.md
  - modulation-choice-guide.md
  - ber-ebn0-and-shannon.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - ../14-sdr-dsp/iq-complex-baseband.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# OFDM — orthogonal frequency-division multiplexing

## Questions this page answers
- What is OFDM, and why do Wi-Fi, LTE/5G and DVB-T all use it?
- Why are the subcarriers "orthogonal" even though their spectra overlap?
- How does an inverse FFT generate OFDM, and what does the cyclic prefix do?
- How long must the cyclic prefix be?
- Why does OFDM have such a high peak-to-average power ratio, and what does that do to my PA?
- Why is OFDM so sensitive to frequency offset and phase noise?
- How are timing and frequency synchronised (Schmidl–Cox), and what are pilots for?
- Should I use OFDM for a custom rocket telemetry or video link?
- What are the 5G NR numerologies (15/30/60/120 kHz…), and why does NR scale the subcarrier spacing?
- What do LTE and Wi-Fi signals look like on a spectrum analyser (DC null, idle cell, resource-block loading, bursts)?
- How are MIMO antennas on a Wi-Fi router spaced and oriented?

## TL;DR
- OFDM sends $N$ low-rate QAM streams on subcarriers spaced $\Delta f=1/T_u$ ($T_u$ = useful symbol time). At that spacing the subcarriers are orthogonal over $T_u$ despite overlapping sinc-shaped spectra. An **N-point IFFT** builds the symbol; an **FFT** demodulates it [1], [2].
- A **cyclic prefix (CP)** — the last $N_{CP}$ samples copied to the front — makes linear convolution with the channel look circular, so each subcarrier sees a single complex gain $H_k$: **one-tap equalisation**, exact when CP ≥ channel memory (verified: EVM −307 dB with CP 16 vs 7-tap channel; −19 dB with CP 4). Cost: $T_{CP}/(T_u+T_{CP})$ of time and power (20 % in 802.11a).
- **PAPR is high:** 52-subcarrier QPSK OFDM exceeds **10.5 dB** in 1e-3 of symbols (simulated; Nyquist-sampled approximation $1-(1-e^{-\gamma})^N$ gives 10.4 dB), versus ≈ 3–4 dB for single-carrier RRC QPSK. Expect ≈ 8–11 dB PA back-off or PAPR reduction (clipping+filtering, tone reservation, DPD).
- **Frequency-offset sensitivity:** a CFO of ε subcarrier spacings scales the wanted signal by ≈ sinc(ε) and creates inter-carrier interference with power ≈ $(\pi\varepsilon)^2/3$ → SIR 28.8 dB at ε = 0.02, 20.8 dB at 0.05, 14.7 dB at 0.1 (verified). Keep residual CFO below ≈ 1–2 % of Δf for 64-QAM.
- **Schmidl–Cox** sync: a training symbol with two identical halves gives a timing metric plateau and CFO estimate $\hat\varepsilon=\angle P/\pi$ (unambiguous within ±1 spacing; verified within 0.016 spacing at 20 dB SNR); a second symbol resolves the integer part [3].
- Numerology (verified): **802.11a/g** 20 MHz, 64-FFT, Δf = 312.5 kHz, $T_u$ 3.2 µs + GI 0.8 µs, 48 data + 4 pilot subcarriers, 6–54 Mb/s; **LTE** Δf = 15 kHz, $T_u$ 66.7 µs, normal CP 4.69 µs (5.21 µs first symbol), 2048-FFT at 30.72 MS/s, 1200 subcarriers (18 MHz) in 20 MHz; **DVB-T** 8 MHz: 2k mode 4464 Hz / 224 µs, 8k mode 1116 Hz / 896 µs, guard ¼…1/32.
- For a **power-limited, long-range, low-rate rocket telemetry link OFDM is the wrong tool** (PAPR, sync overhead, CFO sensitivity; the channel is not frequency-selective at kb/s rates). It shines for **high-rate video** through multipath (e.g. COTS Wi-Fi or DVB-T hardware).

## Intuition (no math)
A single high-rate carrier has short symbols. Multipath echoes that arrive a few hundred nanoseconds late smear each symbol into the next (ISI), and undoing that needs a long, adaptive equaliser ([pulse shaping & ISI](pulse-shaping-isi.md)). OFDM's trick: instead of one fast stream, send hundreds of slow streams side by side in frequency. Each slow stream has long symbols, so an echo is a small fraction of a symbol. Add a short **guard interval** in front of each symbol, filled with a copy of the symbol's own tail, and the echo's spill-over falls entirely inside the guard, which the receiver throws away.

Why can the subcarriers overlap? Over one symbol period, each subcarrier completes an integer number of cycles, and any two of them differ by an integer number of cycles. The receiver's FFT correlates against each subcarrier over exactly that period; every *other* subcarrier contributes a whole number of cycles, which integrates to zero. Their spectra overlap, but at the centre of each subcarrier all the others pass through a null.

The price: the sum of hundreds of independent sinusoids looks like Gaussian noise — occasionally the phases line up and the peak is far above average (high PAPR). And orthogonality depends on the subcarriers being exactly where the FFT expects them: a small frequency offset makes every subcarrier leak into its neighbours.

## The math

### Level 1 — construction and parameters
Useful symbol duration $T_u$, subcarrier spacing $\Delta f=1/T_u$, $N$ subcarriers (FFT size), sample rate $f_s=N\Delta f$. With complex data $X_k$ on subcarrier $k$:
$$x[n]=\frac1{\sqrt N}\sum_{k=0}^{N-1}X_ke^{j2\pi kn/N},\quad n=0,\dots,N-1\qquad(\text{IFFT})$$
Cyclic prefix: transmit $x[N-N_{CP}],\dots,x[N-1],x[0],\dots,x[N-1]$. Symbol duration $T_s=T_u+T_{CP}$.

| Quantity | Formula | 802.11a | LTE (20 MHz) |
|---|---|---|---|
| Δf | $f_s/N$ | 312.5 kHz | 15 kHz |
| $T_u$ | $1/\Delta f$ | 3.2 µs | 66.7 µs |
| $T_{CP}$ | $N_{CP}/f_s$ | 0.8 µs (16 samples) | 4.69 µs (144 samples) |
| Used subcarriers | – | 52 (48 data + 4 pilots) | 1200 |
| CP overhead | $T_{CP}/T_s$ | 20 % | 6.7 % |
| Data rate | $N_{data}\,k\,r/T_s$ | 48·6·¾/4 µs = 54 Mb/s | – |

[4], [5], [6]

### Level 2 — orthogonality, the cyclic prefix and equalisation
**Orthogonality.** Over $0\le t<T_u$, $\int e^{j2\pi k\Delta f t}e^{-j2\pi l\Delta f t}dt=T_u\delta_{kl}$ because $(k-l)$ is an integer number of cycles. Each subcarrier's spectrum is a sinc (rectangular time window) with nulls at every other subcarrier's centre. The DFT is exactly the bank of correlators, and the IFFT/FFT pair makes $N$-subcarrier modulation cost $O(N\log N)$ — Weinstein & Ebert's 1971 insight [2]; Chang (1966) had shown the orthogonal band-limited multitone concept [1].

**Cyclic prefix.** Channel impulse response $h[0..L]$. Received $y=h*x+w$ (linear convolution). If $N_{CP}\ge L$, then after discarding the CP the remaining $N$ samples equal the *circular* convolution $h\circledast x$ (the prefix supplies exactly the "wrapped" samples). The DFT diagonalises circular convolution:
$$Y_k=H_kX_k+W_k,\qquad H_k=\sum_{l}h[l]e^{-j2\pi kl/N}.$$
So each subcarrier needs only a complex division (zero-forcing per subcarrier) or an MMSE scaling $\hat X_k=\frac{H_k^*}{|H_k|^2+\sigma^2}Y_k$. The script checks exact recovery with CP = 16 over a 7-tap channel and shows residual ISI/ICI (EVM −19 dB) with CP = 4 [7], [8].

**How long a CP?** $T_{CP}\ge$ maximum excess delay of significant paths (plus filter and timing-uncertainty margins). 802.11a's 0.8 µs covers ≈ 240 m path differences (indoor/campus); LTE's 4.69 µs ≈ 1.4 km (macro-cell); DVB-T's up to 224 µs (8k, ¼) allows single-frequency networks with transmitters tens of km apart.

**Subcarrier fading and coding.** In a frequency-selective channel some $H_k$ are deep nulls; those subcarriers are lost. OFDM *relies on* FEC with interleaving across subcarriers (COFDM) to recover them — uncoded OFDM in multipath performs like flat Rayleigh fading per subcarrier ([BER page](ber-ebn0-and-shannon.md), [channel coding](channel-coding-fec.md)).

**Pilots and channel estimation.** Known symbols on some subcarriers/symbols (802.11a: 4 continuous pilots for phase tracking; LTE: scattered reference signals in time and frequency) let the receiver interpolate $H_k$ in frequency and time. Pilot spacing must satisfy sampling limits: in frequency ≤ coherence bandwidth, in time ≤ coherence time (Doppler) [8], [9].
Pilot-spacing derivation, LS/MMSE estimation and MIMO-OFDM: [MIMO capacity and channel estimation](mimo-capacity-and-channel-estimation.md).

### Level 3 — PAPR, synchronisation errors, and variants
**PAPR statistics.** For large $N$ the time samples are ≈ complex Gaussian, so instantaneous power is exponentially distributed. Treating the $N$ Nyquist-rate samples as independent, $P(\mathrm{PAPR}>\gamma)\approx1-(1-e^{-\gamma})^N$ — 10.4 dB at 1e-3 for N = 52; 4× oversampling catches peaks between samples and adds ≈ 0.2–0.5 dB (simulated 10.5 dB) [10]. Single-carrier RRC QPSK sits at ≈ 3–4 dB ([digital modulation](digital-modulation-psk-qam-fsk.md)). Consequences: PA back-off of ≈ 8–11 dB, or PAPR reduction (clipping and filtering, selected mapping, partial transmit sequences, tone reservation, active constellation extension) plus DPD. LTE's uplink uses **SC-FDMA** (DFT-spread OFDM) precisely to lower PAPR for battery-powered phones [6], [10].

**Carrier-frequency offset (CFO).** With normalised offset $\varepsilon=\Delta f_{off}/\Delta f$, the received subcarrier $k$ is
$$Y_k=X_k\underbrace{\frac1N\sum_ne^{j2\pi\varepsilon n/N}}_{\approx\,\mathrm{sinc}(\varepsilon)e^{j\pi\varepsilon}}+\underbrace{\sum_{l\ne k}X_lI_{l-k}(\varepsilon)}_{\text{ICI}}+W_k,$$
a common attenuation/rotation plus inter-carrier interference whose power (unit-power data) is $1-|\text{gain}|^2\approx(\pi\varepsilon)^2/3$ for small ε. Verified: SIR from ICI 28.8 / 20.8 / 14.7 dB at ε = 0.02 / 0.05 / 0.1 [11], [12]. The SNR degradation is approximately $\frac{10}{3\ln10}(\pi\varepsilon)^2\frac{E_s}{N_0}$ dB at high SNR [11]. Because Δf is small (15 kHz in LTE), the same absolute Hz of Doppler or crystal error is a much larger ε than for a single-carrier system of the same total bandwidth.

**Phase noise** does two things: a common phase error (CPE) rotating all subcarriers equally (tracked by pilots) and ICI from the part of the phase noise spectrum wider than Δf — the reason mmWave 5G uses wider subcarrier spacings (up to 120 kHz+) ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**Timing.** An FFT window starting anywhere inside the "clean" part of the CP (after the channel's echoes) only rotates each subcarrier's phase linearly with $k$ — absorbed by channel estimation. Starting outside it causes ISI.

**Synchronisation (Schmidl–Cox).** A training symbol whose first and second halves are identical (only even subcarriers used). Metric $P(d)=\sum_{m=0}^{N/2-1}r^*_{d+m}r_{d+m+N/2}$, $R(d)=\sum|r_{d+m+N/2}|^2$, $M(d)=|P|^2/R^2$ has a plateau (length of the CP) at the symbol start. At the right timing, the phase of $P$ is $\pi\varepsilon$, so $\hat\varepsilon=\angle P/\pi$ resolves fractional offsets within ±1 spacing; a second training symbol with a known differential pattern resolves the integer part [3]. Moose's method uses two repeated full symbols [13]. 802.11a's preamble (10 short + 2 long training symbols) serves the same purposes: AGC, coarse/fine CFO, timing, channel estimate [4].

**Doppler.** A single line-of-sight path's Doppler is just a CFO (estimated and removed). A Doppler *spread* (paths with different Doppler, as for a fast vehicle among reflectors) cannot be removed by one correction and causes ICI proportional to $(f_D/\Delta f)^2$; keep $f_{D,max}\ll\Delta f$ (LTE's 15 kHz spacing handles ≈ 500 km/h at 2 GHz: 926 Hz ≈ 6 % of Δf) [6], [8].

**Variants.** OFDMA (subcarrier blocks to different users: LTE downlink, Wi-Fi 6); DFT-s-OFDM/SC-FDMA (low PAPR uplink); windowed/filtered OFDM (lower out-of-band emission — plain OFDM's sinc sidelobes decay slowly, so guard subcarriers and spectral shaping are needed); OTFS (delay-Doppler domain, research for high mobility).

### Level 3b — consumer systems: 5G NR numerology, what LTE and Wi-Fi look like on an analyser, router MIMO antennas (W5-S8)
Numbers are computed in `tools/verify/s8_sync_extras.py` §6 (34/34 PASS). Standards details are from TS 38.211 / 38.101 and IEEE 802.11 as commonly tabulated. The maximum-RB values were cross-checked against a 3GPP RAN4 draft and a vendor poster (secondary sources, see the [S8 log](../../research-logs/W5-S8-comms-phy.md)).

**5G NR numerology.** NR scales LTE's 15 kHz grid by powers of two: $\Delta f=15\cdot2^\mu$ kHz. A slot is always 14 symbols (normal CP), so it shrinks as $1/2^\mu$. The time unit is $T_c=1/(480\,\text{kHz}\cdot4096)$, with $\kappa$ = 64. The useful symbol is $2048\kappa T_c/2^\mu$ and the normal CP is $144\kappa T_c/2^\mu$. The first symbol of every 0.5 ms gets $16\kappa T_c$ extra, which keeps the half-subframes aligned with LTE.

| μ | Δf (kHz) | Slot (ms) | Slots per ms | $T_u$ (µs) | Normal CP (µs) | Used in | Max channel (max RB) |
|---|---|---|---|---|---|---|---|
| 0 | 15 | 1 | 1 | 66.67 | 4.69 (5.21 first) | FR1 (≤ 7.125 GHz) | 50 MHz (270 RB) |
| 1 | 30 | 0.5 | 2 | 33.33 | 2.34 | FR1, the usual mid-band choice (n78) | 100 MHz (273 RB) |
| 2 | 60 | 0.25 | 4 | 16.67 | 1.17 (extended CP allowed) | FR1 and FR2 | 100 MHz FR1 (135 RB); 200 MHz FR2 (264 RB) |
| 3 | 120 | 0.125 | 8 | 8.33 | 0.586 | FR2 (24–52 GHz) | 400 MHz (264 RB) |
| 4 | 240 | 0.0625 | 16 | 4.17 | 0.293 | FR2 synchronisation blocks | – |
| 5–6 | 480 / 960 | 0.031 / 0.016 | 32 / 64 | 2.08 / 1.04 | 0.146 / 0.073 | FR2-2 (52.6–71 GHz, Rel-17) | – |

An RB is always 12 subcarriers, and the maximum allocations fill 95–98 % of the channel (273 × 12 × 30 kHz = 98.3 MHz of 100 MHz). A 100 MHz carrier at 30 kHz needs a 4096-point FFT at 122.88 MS/s.

**Why the scaling.** A wider spacing makes the system robust to phase noise and Doppler, since ICI scales with $(f/\Delta f)^2$ (Level 3). The cost is a shorter CP, which suits mmWave's small cells and short delay spreads. A narrower spacing gives a longer CP for wide-area low bands. The trade is the CFO and phase-noise argument of this page in standard form.

**What LTE and Wi-Fi look like on a spectrum analyser** (practical reading; measurement technique in [spectrum analysers](../17-test-measurement/spectrum-analyzers.md)):
- **Wi-Fi 802.11a/g (20 MHz):** a flat-topped block 16.6 MHz wide (52 subcarriers plus the empty DC subcarrier at 312.5 kHz spacing), with steep skirts and then the spectral-mask shoulders.
  - The **DC null** shows as a narrow notch at the centre only if the RBW is well below 312.5 kHz.
  - HT20 (802.11n) is a little wider: 56 subcarriers, 17.8 MHz.
  - Wi-Fi is **bursty**. Beacons every 102.4 ms and data packets of tens of µs to a few ms make a swept display show random fragments. Use max-hold, a time-gated sweep, or an SDR waterfall.
  - An 802.11b/DSSS beacon at 2.4 GHz looks different: a rounded ≈ 22 MHz sinc-like hump rather than a flat top.
- **LTE downlink (FDD):** always on. Even an **idle cell** radiates its cell-specific reference signals across the full 18 MHz (20 MHz channel) at about **−13 dB** relative to a fully loaded cell. With one port and equal resource-element power, the CRS occupy 8 of 168 resource elements per RB per subframe.
  - The synchronisation and broadcast channels sit in the **central 6 RB (1.08 MHz)**, a small bump on an idle cell.
  - Load appears as PDSCH filling resource blocks. On a spectrogram with ≈ 1 ms resolution you can see 180 kHz × 1 ms blocks switching on and off.
  - The LTE downlink leaves its DC subcarrier unused. The uplink (SC-FDMA) instead shifts all subcarriers by half a spacing (7.5 kHz) and has no hole. Uplink activity appears as bursts at the channel edges (control channel) and in scheduled chunks.
- **NR and TDD** (for example n78 at 3.5 GHz): the downlink is time-gated by the TDD pattern, so channel power depends on the DL/UL split. Use gated or zero-span measurements. NR has no reserved DC subcarrier. The synchronisation block (SSB) is 20 RB, 7.2 MHz at 30 kHz, and need not sit at the channel centre.
- **Detector and RBW:** OFDM is noise-like, so measure with an RMS detector and channel-power integration, with RBW ≈ 30–100 kHz and video bandwidth ≥ 3 × RBW. A peak detector overstates the power by up to the PAPR (≈ 10 dB).

**MIMO antennas on routers and modems.** These are 2–8 dipoles or sleeve dipoles of typically 2–5 dBi (internal PIFA or ceramic antennas in mesh units), spaced at least λ/2: **6.1 cm at 2.44 GHz and 2.7 cm at 5.5 GHz**.
- Indoors the channel is rich-scattering, so this spacing decorrelates the branches (the [MIMO page](mimo-capacity-and-channel-estimation.md) uses ≈ 0.4–0.5 λ). Spatial multiplexing then roughly doubles throughput per added stream at good SNR.
- The **envelope correlation coefficient** between ports (from the measured or simulated patterns) is the design figure; a common target is < 0.5.
- Mixing orientations (one vertical, one tilted) adds polarisation diversity for clients held at odd angles. That advice is vendor practice, not a measured result here.
- 802.11ac/ax **transmit beamforming** uses the sounding/feedback exchange described in [MIMO §18](mimo-capacity-and-channel-estimation.md#level-2b--space-time-block-codes-detectors-compared-mimo-ofdm-and-csi-sounding-w5-s8). Its gain is at most ≈ 10 log N_t for one client and erodes when the channel changes faster than it is re-sounded.
- None of this helps a long LOS link (rank 1); there the antennas give array and diversity gain only.

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $\Delta f=1/T_u$, $f_s=N\Delta f$ | OFDM | 312.5 kHz / 15 kHz |
| $T_{CP}\ge$ max excess delay (+margins) | CP design | 0.8 µs ≈ 240 m; 4.7 µs ≈ 1.4 km |
| CP overhead $T_{CP}/(T_u+T_{CP})$ | power & time loss | 802.11a 20 % (0.97 dB) |
| $Y_k=H_kX_k+W_k$ | CP ≥ channel memory | one-tap EQ |
| PAPR CCDF ≈ $1-(1-e^{-\gamma})^N$ | large N, Nyquist samples | N = 52: 10.4 dB @ 1e-3 |
| ICI power ≈ $(\pi\varepsilon)^2/3$ | small CFO ε (in spacings) | ε = 0.02 → SIR 28.8 dB |
| $\hat\varepsilon=\angle P/\pi$ | Schmidl–Cox, |ε| < 1 | + integer search |
| Pilot spacing ≤ coherence BW (freq), ≤ coherence time (time) | channel estimation | – |
| Keep $f_D\ll\Delta f$ (≲ 5–10 %) | mobility | LTE: ≈ 900 Hz max |
| NR: $\Delta f=15\cdot2^\mu$ kHz, slot $=1/2^\mu$ ms, CP $=4.69/2^\mu$ µs | TS 38.211 normal CP | μ = 1: 30 kHz, 0.5 ms, 2.34 µs |
| NR max RB × 12 × Δf ≈ 95–98 % of channel | TS 38.101 | 273 RB at 30 kHz = 98.3 MHz of 100 |
| Idle LTE cell ≈ −13 dB vs full load | 1 CRS port, equal EPRE | 8/168 REs |
| Measure OFDM with RMS detector + channel power | noise-like signal | peak detector reads up to PAPR high |

## Worked examples

### Example 1 — 802.11a numbers from first principles
20 MS/s, 64-point FFT → Δf = 312.5 kHz, $T_u$ = 3.2 µs; GI 16 samples = 0.8 µs → 4 µs symbols. 48 data subcarriers: BPSK rate ½ → 48 × 1 × ½ / 4 µs = 6 Mb/s; 64-QAM rate ¾ → 54 Mb/s. Occupied width ≈ 53 × 312.5 kHz ≈ 16.6 MHz. CP overhead 0.97 dB of energy.

### Example 2 — Why OFDM is wrong for a 10 kb/s rocket telemetry link
(a) Channel: the ground-reflection delay is ≈ 30 ns ([pulse shaping](pulse-shaping-isi.md) Example 2), so a 10 kbaud single-carrier signal is not frequency-selective — OFDM's main advantage is irrelevant. (b) PAPR: ≈ 10 dB back-off turns a 2 W PA into ≈ 0.2 W average. (c) CFO: with, say, 64 subcarriers in 12.5 kHz (Δf ≈ 195 Hz), 1.44 kHz of Doppler is ε ≈ 7.4 spacings and a 10 ppm crystal adds 22 more; after correction, a residual of just 4 Hz is 2 % of Δf. (d) Sync overhead of preambles on short packets. A single-carrier GFSK/BPSK or LoRa link wins on every axis.

### Example 3 — When OFDM *does* make sense: high-rate video from the vehicle
A 5.8 GHz video downlink at several Mb/s through a cluttered pad area with multipath delays of up to ~1 µs: single-carrier would need an adaptive equaliser spanning several symbols; COTS OFDM (802.11 at 20 MHz with 0.8 µs GI) handles it natively, and chips and SDR stacks are cheap. Community systems such as wifibroadcast/OpenHD reuse Wi-Fi OFDM hardware in raw injection mode with added FEC for exactly this role (not independently verified here). Doppler at 5.8 GHz and 300 m/s is 5.8 kHz = 1.9 % of 312.5 kHz — a plain CFO, removed by the preamble, with negligible residual ICI if the geometry is line-of-sight.

### Example 4 — Residual CFO budget for 64-QAM
64-QAM rate ¾ needs ≈ 25 dB SINR. Allowing ICI to cost ≤ 0.5 dB means ICI-limited SIR ≥ ≈ 34 dB → $(\pi\varepsilon)^2/3\le4\times10^{-4}$ → ε ≤ 0.011, i.e. residual CFO ≤ 3.4 kHz at 312.5 kHz spacing (≈ 0.6 ppm at 5.8 GHz) — hence the per-packet fine CFO estimate from the long training symbols.

### Example 5 — CP choice for a DVB-T-like link
A ground station receiving from two relays 20 km apart (SFN-like): delay difference up to 67 µs. DVB-T 8k with guard ¼ (224 µs) or ⅛ (112 µs) covers it; 2k with ¼ (56 µs) does not.

## Practical notes
- **IQ imbalance** mirrors subcarrier $k$ onto $-k$ (image interference); DC offset hits the centre subcarrier (which is why 802.11a leaves DC empty).
- **Spectral mask:** sinc sidelobes of the rectangular-windowed subcarriers decay slowly; use guard subcarriers, windowing (raised-cosine edges between symbols) or filtering.
- **ADC/DAC dynamic range:** PAPR means more converter bits and headroom ([data converters](../05-analog-electronics/data-converters-adc-dac.md)).
- **SDR implementations:** GNU Radio's `gr-digital` OFDM blocks and `gr-ieee802-11` (Bloessl) are working references; for DVB-T, `gr-dvbt`.
- **Test:** measure EVM per subcarrier (a VSA or GNU Radio constellation per carrier) to see CFO/phase-noise ICI, IQ imbalance (mirror pattern) and PA compression (outer QAM points pulled in).

## Common mistakes & misconceptions
- **"OFDM beats single-carrier in AWGN."** In a flat AWGN channel, coded OFDM and coded single-carrier have the same Eb/N0 requirement — minus OFDM's CP and pilot overhead and PA back-off. The benefit is in frequency-selective channels.
- **"The CP removes multipath."** It converts multipath into per-subcarrier gains; the nulls remain and must be handled by coding across subcarriers.
- **Ignoring PAPR in the PA budget** — clipped OFDM produces spectral regrowth that fails the mask long before EVM looks bad.
- **Assuming CFO tolerance scales with total bandwidth** — it scales with subcarrier spacing.
- **Expecting a DC notch on every OFDM signal.** 802.11 and the LTE downlink leave DC empty, but the LTE uplink shifts by 7.5 kHz and NR does not reserve DC. The notch is also invisible at RBW above the subcarrier spacing.
- **Reading an idle LTE cell as "no signal".** Reference and synchronisation signals are always on, ≈ 13 dB below a loaded cell; the level rises with traffic, not with distance.
- **Measuring bursty Wi-Fi with a normal sweep.** You catch random fragments; use gating, max-hold or IQ capture.
- **Assuming NR's wider spacings are "faster".** They shorten symbols and CPs to tolerate phase noise and Doppler at mmWave; capacity comes from the bandwidth, not the spacing.
- **Placing the FFT window at the very start of the CP** in heavy multipath — earlier-arriving energy is fine, but window placement must leave room for the echoes.

## How to simulate / verify
- **`tools/verify/s8_sync_extras.py`** §6 (W5-S8): NR numerology (μ = 0…6 symbol, CP and slot durations; slot fill; max-RB occupancy), 802.11a/HT20 widths, LTE 18 MHz / 6-RB / idle-cell CRS fraction, NR SSB width, router λ/2 spacings.
- **`tools/verify/comms_ofdm.py`** (< 1 s): CP + one-tap EQ exact recovery vs short-CP ISI; PAPR CCDF vs approximation; CFO gain/ICI vs sinc and $(\pi\varepsilon)^2/3$; Schmidl–Cox CFO estimate; 802.11a/LTE/DVB-T numerology. All PASS.
- **Minimal OFDM in Python:** `x = np.fft.ifft(X)*np.sqrt(N); tx = np.r_[x[-cp:], x]`; receiver `Y = np.fft.fft(rx[cp:cp+N])/np.sqrt(N); Xhat = Y/H`.
- **GNU Radio:** *OFDM Transmitter/Receiver* hierarchical blocks (Schmidl–Cox sync, pilots, equaliser), `gr-ieee802-11` for real Wi-Fi frames.

## Open questions / gaps
- 802.11 EVM and spectral-mask numbers are not tabulated here (see digital-modulation gap note).
- The analyser descriptions of LTE/Wi-Fi/NR are from knowledge of the standards and common practice, not from captured spectra; an SDR capture of a local LTE/NR cell and a Wi-Fi AP would make them first-hand. The ECC < 0.5 target and router antenna-orientation advice are vendor practice (unverified).
- DVB-T carrier counts (1705 / 6817, of which 1512 / 6048 carry data) and T = 7/64 µs (8 MHz) were confirmed by W5-S18b on 2026-10-13 from secondary sources (a Rohde & Schwarz DVB-T page and a university DVB-T lecture). The guard fractions ¼–1/32 rest on secondary sources only. The ETSI PDF could not be downloaded. Only the timing numerology was computed here.
- A worked OFDM-over-Rayleigh-with-coding simulation (showing why COFDM needs interleaving) would strengthen the page.

## Sources
1. R. W. Chang, "Synthesis of band-limited orthogonal signals for multichannel data transmission," *Bell System Technical Journal* 45(10):1775–1796, 1966. (peer-reviewed, primary)
2. S. B. Weinstein and P. M. Ebert, "Data transmission by frequency-division multiplexing using the discrete Fourier transform," *IEEE Trans. Communication Technology* COM-19(5):628–634, 1971. (peer-reviewed, primary)
3. T. M. Schmidl and D. C. Cox, "Robust frequency and timing synchronization for OFDM," *IEEE Trans. Communications* 45(12):1613–1621, 1997. (peer-reviewed)
4. IEEE Std 802.11-2020, §17 (OFDM PHY: 20 MHz, 64-FFT, 312.5 kHz, 0.8 µs GI, 48 data + 4 pilot subcarriers, preamble structure, rates 6–54 Mb/s). (standard)
5. ETSI EN 300 744 V1.6.1, *DVB-T framing structure, channel coding and modulation for digital terrestrial television* — 2k/8k modes, elementary period 7/64 µs (8 MHz), guard ¼–1/32. (standard)
6. 3GPP TS 36.211, *E-UTRA Physical channels and modulation* — 15 kHz spacing, normal/extended CP (160/144 samples at 30.72 MS/s), resource blocks of 12 subcarriers, SC-FDMA uplink. (standard)
7. A. Peled and A. Ruiz, "Frequency domain data transmission using reduced computational complexity algorithms," *Proc. IEEE ICASSP* 1980, pp. 964–967 — cyclic prefix. (peer-reviewed)
8. A. Goldsmith, *Wireless Communications*, Cambridge University Press, 2005 — ch. 12 (multicarrier modulation, OFDM, CP, PAPR, CFO, pilots). (textbook)
9. R. van Nee and R. Prasad, *OFDM for Wireless Multimedia Communications*, Artech House, 2000. (textbook)
10. S. H. Han and J. H. Lee, "An overview of peak-to-average power ratio reduction techniques for multicarrier transmission," *IEEE Wireless Communications* 12(2):56–65, 2005. (peer-reviewed review)
11. T. Pollet, M. Van Bladel, M. Moeneclaey, "BER sensitivity of OFDM systems to carrier frequency offset and Wiener phase noise," *IEEE Trans. Communications* 43(2/3/4):191–193, 1995. (peer-reviewed)
12. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — ch. 11 (multichannel and multicarrier systems). (textbook)
13. P. H. Moose, "A technique for orthogonal frequency division multiplexing frequency offset correction," *IEEE Trans. Communications* 42(10):2908–2914, 1994. (peer-reviewed)
14. 3GPP TS 38.211, *NR; Physical channels and modulation* — numerologies μ, T_c, κ, CP lengths, slot structure; TS 38.101-1/-2 — maximum transmission bandwidth configurations (N_RB). Values cross-checked via a RAN4 draft (R4-2006846) and an iBwave NR poster. (standard; secondary access for N_RB)
15. 3GPP TS 36.211 (ref. 6) — LTE CRS pattern, central 6-RB PSS/SSS/PBCH, unused DC subcarrier in DL, 7.5 kHz UL shift (from knowledge). (standard)
16. Verification: `tools/verify/s8_sync_extras.py` §6 (W5-S8). (numerical check)
