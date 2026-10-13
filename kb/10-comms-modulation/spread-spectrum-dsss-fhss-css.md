---
title: Spread spectrum — DSSS, FHSS, chirp spread spectrum and CDMA
domain: 10-comms-modulation
slug: spread-spectrum-dsss-fhss-css
tags: [spread-spectrum, DSSS, FHSS, CSS, chirp, LoRa, processing-gain, jamming-margin, PN-sequence, m-sequence, Gold-code, GPS-C/A, CDMA, near-far, LPI, RAKE]
prerequisites:
  - matched-filter-detection.md
  - ber-ebn0-and-shannon.md
  - digital-modulation-psk-qam-fsk.md
related:
  - synchronization-carrier-timing.md
  - channel-coding-fec.md
  - modulation-choice-guide.md
  - ../15-lora-ism-radios/lora-phy-css-math.md
  - ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md
  - ../08-antennas/gnss-antennas.md
  - ../11-radar/pulsed-radar-and-pulse-compression.md
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Spread spectrum — DSSS, FHSS, chirp spread spectrum and CDMA

## Questions this page answers
- What is spread spectrum, and what is "processing gain"?
- Does spreading improve performance against ordinary thermal noise?
- What is jamming margin, and how do I compute it?
- What are m-sequences and Gold codes, and how are GPS C/A codes generated?
- How does frequency hopping differ from direct sequence, and what does it protect against?
- How does chirp spread spectrum (LoRa) work, and why is it equivalent to M-ary FSK?
- Why does a frequency offset look like a timing offset in LoRa, and what does rocket Doppler do to it?
- How can GPS signals be received when they are ~18 dB below the thermal noise floor?
- How does CDMA let many users share a channel, and what is the near–far problem?

## TL;DR
- **Spread spectrum** deliberately occupies a bandwidth $W$ much larger than the data rate $R_b$. **Processing gain** $G_{proc}=W/R_b$ (DSSS: chips per bit $R_c/R_b$). Many texts write $G_p$; the KB writes $G_{proc}$ so it cannot be confused with the operating power gain $G_{power}$ (textbook $G_P$) of [S-parameters](../03-transmission-lines-matching/s-parameters.md) and [LNA design](../06-rf-circuits/lna-design.md).
- **Against white noise, spreading gains nothing**: BER still depends only on $E_b/N_0$. It helps against *narrowband* interference/jamming, multipath (resolvable paths), multiple access (CDMA), interception (LPI), and gives fine timing (ranging).
- **Jamming margin** $M_J=G_{proc}-(E_b/J_0)_{req}-L$ (dB). A 63-chip DSSS BPSK link ($G_{proc}$ = 18.0 dB) needing 9.6 dB + 2 dB loss tolerates a jammer 6.4 dB stronger than itself at BER 1e-5; at J/S = +13 dB the simulated BER is 6.4e-3 (theory 6.0e-3) versus 0.37 without spreading (`tools/verify/comms_spread_spectrum.py`).
- **m-sequences** (maximal-length LFSR, period $2^n-1$): balanced, two-valued autocorrelation $\{N,-1\}$. **Gold codes** (XOR of a preferred pair): large families with three-valued cross-correlation $\{-t(n),-1,t(n)-2\}$; for $n=10$, {−65, −1, 63}. GPS L1 C/A = 1023-chip Gold codes at 1.023 Mcps (1 ms period), $G_1=1+x^3+x^{10}$, $G_2=1+x^2+x^3+x^6+x^8+x^9+x^{10}$ — PRN 1 starts 1440 (octal); SBAS PRNs match the gps.gov table (all verified).
- **FHSS** hops a narrowband carrier over many channels; a narrowband interferer hits only a fraction of hops (fix with FEC/interleaving). Bluetooth BR: 79 × 1 MHz channels, 1600 hops/s.
- **CSS / LoRa:** each symbol is one of $2^{SF}$ cyclic shifts of a chirp spanning bandwidth BW; dechirp + FFT = bank of $2^{SF}$ matched filters → non-coherent M-ary orthogonal signalling (≈ 6 dB Eb/N0). A carrier offset of $\mathrm{BW}/2^{SF}$ Hz shifts the decision by exactly one symbol (verified) — 1.44 kHz of 433 MHz Doppler is 1.5 bins at SF7 but **47 bins at SF12**, which the preamble must estimate and remove; Doppler *rate* then drifts the bins within a long packet.
- **GPS example:** −128.5 dBm spread over 2.046 MHz → −191.6 dBm/Hz, ≈ 18 dB below kT; still C/N0 ≈ 43.5 dB-Hz (NF 2 dB) because the correlator's 43 dB processing gain collapses the spread energy back into the 50 b/s data.

## Intuition (no math)
Imagine you have to shout a message across a room where one person is singing a single loud note. If you speak on the same pitch, you're drowned out. If instead you smear your voice across all pitches in a known, pseudo-random way, the listener — who knows your pattern — can "un-smear" it. Un-smearing collects your scattered energy back into one place, while the singer's single note gets smeared out by the same operation, so only a small slice of it lands where your message now is. That ratio of "how spread" to "how concentrated" is the **processing gain**.

But thermal noise is already spread over all frequencies. Un-smearing reshuffles noise into … more noise with the same density. So against plain noise, spreading neither helps nor hurts: the energy per bit you transmit is the same, and that's what determines BER. This is the most important (and most misunderstood) point: a LoRa or GPS signal can be decoded "below the noise floor" only in the sense that its power is lower than the noise power *across the whole wide band*; per bit, the ratio of signal energy to noise density is comfortably positive.

**Direct sequence** multiplies the data by a fast pseudo-random ±1 chip sequence. **Frequency hopping** keeps a narrow signal but jumps its carrier around pseudo-randomly. **Chirp spread spectrum** sweeps the frequency linearly across the band during each symbol, and encodes data in *where* the sweep starts. All three need the receiver to know the pattern and to be synchronised to it.

## The math

### Level 1 — definitions
| Symbol | Meaning |
|---|---|
| $R_b$, $T_b$ | data rate, bit time |
| $R_c=1/T_c$ | chip rate (DSSS), $N=T_b/T_c$ chips per bit |
| $W$ | spread bandwidth (≈ $R_c$ Nyquist, $2R_c$ null-to-null for rectangular chips) |
| $G_{proc}=W/R_b\approx N$ | processing gain (dB: $10\log_{10}G_{proc}$) |
| $J$, $J_0=J/W$ | jammer power, equivalent jammer PSD |
| $M_J=G_{proc}-(E_b/J_0)_{req}-L$ | jamming margin (dB): tolerable J/S |

With jammer power $J$ spread evenly over $W$, $E_b/J_0=\frac{ST_b}{J/W}=G_{proc}\frac SJ$. So in dB: $E_b/J_0=G_{proc}+S/J$.

### Level 2 — DSSS, codes, FHSS, CSS
**DSSS model.** Transmit $s(t)=\sqrt{2S}\,d(t)c(t)\cos\omega_ct$, where $d(t)=\pm1$ data and $c(t)=\pm1$ chips. Receive $r=s+j+w$. Multiply by the synchronised replica $c(t)$ ($c^2=1$) and integrate over a bit (the matched filter for the chip sequence):
- signal: $c^2=1$, so the data collapses back to bandwidth $R_b$ with full energy $E_b$;
- narrowband jammer: multiplied by $c(t)$, it is *spread* over $W$; only ≈ $1/G_{proc}$ of its power falls in the data bandwidth;
- white noise: $c(t)w(t)$ is still white with the same PSD — no change.

Hence $P_b=Q\big(\sqrt{2E_b/(N_0+J_0)}\big)$ with $J_0=J/W$ (Gaussian approximation for the despread jammer, accurate for large $N$). The script checks this for a broadband Gaussian jammer (6.4e-3 vs 6.0e-3 theory) and a CW tone jammer (5.1e-3) at $N=63$, J/S = +13 dB [1], [2].

**Pseudo-noise (PN) sequences.** An $n$-stage linear-feedback shift register with a *primitive* feedback polynomial produces an **m-sequence** of period $N=2^n-1$ with [3]:
- balance: $2^{n-1}$ ones and $2^{n-1}-1$ zeros (512/511 for $n=10$, verified);
- run property: half the runs have length 1, a quarter length 2, …;
- two-valued periodic autocorrelation (±1 mapping): $R(0)=N$, $R(k)=-1$ otherwise (verified) — ideal for acquisition and ranging.

Cross-correlation between different m-sequences can be large, so for multiple access use **Gold codes** [4]: XOR a *preferred pair* of m-sequences with all relative shifts, giving $N+2$ codes whose periodic cross-correlations take only three values $\{-t(n),-1,t(n)-2\}$, $t(n)=2^{\lfloor(n+2)/2\rfloor}+1$. For $n=10$: $t=65$, values {−65, −1, 63} — i.e. worst-case −23.9 dB relative to the 1023 peak. **GPS L1 C/A** codes are such Gold codes: $G_1=1+x^3+x^{10}$, $G_2=1+x^2+x^3+x^6+x^8+x^9+x^{10}$, both registers initialised to all ones; each satellite's code is $G_1\oplus G_2$ delayed by a PRN-specific number of chips (implemented in hardware by XOR-ing two $G_2$ taps, e.g. taps 2 and 6 for PRN 1 = delay 5) [5], [6]. The script regenerates PRN 1 (first 10 chips 1440₈), PRN 2 (1620₈) and SBAS PRNs 120, 131, 133, 138 from their published G2 delays and matches the gps.gov Jan-2026 table (0671, 1226, 0046, 1327). Orthogonal alternatives for *synchronous* users: Walsh–Hadamard codes (zero cross-correlation when aligned, poor when not).

**FHSS.** The carrier hops among $N_h$ channels per a PN pattern. *Slow* hopping: several symbols per hop; *fast*: several hops per symbol. Processing gain ≈ $N_h$ (total hopped bandwidth / channel bandwidth). A narrowband interferer occupying one channel corrupts a fraction $1/N_h$ of hops; with FEC and interleaving across hops those become correctable erasures. FHSS also gives frequency diversity against frequency-selective fading. Bluetooth BR/EDR hops over 79 × 1 MHz channels at 1600 hops/s (adaptive hopping avoids busy channels) [7]; many ISM rules define FHSS channel counts and dwell times (see [ISM bands](../19-regulations-safety/spectrum-allocation-ism-bands.md)).

**Chirp spread spectrum (LoRa).** Complex-baseband up-chirp sampled at $f_s=\mathrm{BW}$ (one sample per "chip"), $M=2^{SF}$ samples per symbol:
$$x_m[n]=\exp\!\left\{j2\pi\left[\frac{n^2}{2M}+\left(\frac mM-\frac12\right)n\right]\right\},\quad n=0,\dots,M-1,$$
i.e. a sweep across BW whose starting frequency (and wrap point) encodes the symbol $m\in\{0,\dots,M-1\}$, $SF$ bits per symbol, symbol time $T_s=2^{SF}/\mathrm{BW}$. **Demodulation:** multiply by the conjugate base chirp (dechirp) → a pure tone at frequency $m\,\mathrm{BW}/M$; an $M$-point FFT and "pick the largest magnitude" decides $m$ [8], [9]. The $M$ dechirped candidates are orthogonal tones, so LoRa is **non-coherent $M$-ary orthogonal FSK in disguise**: its BER follows the M-FSK curve (≈ 6.3 dB Eb/N0 at 1e-5 for M = 128, [BER page](ber-ebn0-and-shannon.md)), and each symbol's "processing gain" is $10\log_{10}2^{SF}$ (21 dB at SF7, 36 dB at SF12) relative to the per-chip SNR.

**CFO–timing coupling in CSS.** A carrier offset $\Delta f$ adds a tone $\Delta f$ to the dechirped signal, i.e. shifts the FFT peak by $\Delta f/(\mathrm{BW}/M)$ bins — indistinguishable from a timing offset (a chirp delayed in time is also a frequency-shifted chirp). The script confirms a one-bin offset (976.6 Hz at SF7/125 kHz; 30.5 Hz at SF12) moves the decision by exactly one symbol. LoRa resolves it with a preamble of up-chirps plus down-chirps (up-chirps shift one way under CFO, down-chirps the other), after which static offsets are removed. The details — and the SX127x frequency-tolerance limits — belong to [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md).

### Level 3 — CDMA, multipath, LPI and the "spreading vs coding" question
**CDMA capacity (single cell, heuristic).** With $K$ equal-power users each seeing the others as noise, $E_b/I_0\approx\frac{G_{proc}}{K-1}$ (ignoring thermal noise), so $K\approx1+G_{proc}/(E_b/I_0)_{req}$ — capacity grows with processing gain and with anything that lowers the required $E_b/I_0$ (coding, voice activity, sectorisation) [10]. **Near–far problem:** a nearby user 30 dB stronger swamps a distant one unless all arrive at equal power — hence fast closed-loop power control in IS-95/UMTS. GPS avoids it because all satellites are roughly equidistant (received powers within a few dB); near a pseudolite or jammer it reappears.

**Multipath and RAKE.** Paths separated by more than a chip ($T_c$) are resolvable: the despreader sees each as a separate correlation peak. A **RAKE receiver** correlates at each path delay and combines them (maximal-ratio), turning multipath from a fading nuisance into diversity. With GPS at 1.023 Mcps, one chip = 293 m; multipath shorter than that biases the pseudorange instead (a GNSS error source).

**LPI / LPD.** Spreading lowers the PSD by $G_{proc}$; to an unintended wideband radiometer the signal is a small rise in the noise floor. GPS at −128.5 dBm over 2.046 MHz is −191.6 dBm/Hz — 17.6 dB under kT = −174 dBm/Hz.

**Spreading vs coding.** DSSS is equivalent to a rate-$1/N$ *repetition* code followed by BPSK. A real low-rate code (e.g. rate-1/N orthogonal or turbo) would give coding gain *and* the same bandwidth expansion — against interference the two can be combined. Viterbi's classic observation: the processing gain against jammers is set by bandwidth expansion, while coding determines how little $E_b/J_0$ you need [10], [11].

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $G_{proc}=W/R_b$ (DSSS $\approx R_c/R_b$) | any spread system | GPS C/A 43.1 dB; 802.11b Barker-11: 10.4 dB |
| $E_b/J_0=G_{proc}\cdot S/J$ | jammer spread over W | – |
| $M_J=G_{proc}-(E_b/J_0)_{req}-L$ | jamming margin | 63 chips: 6.4 dB (BPSK 1e-5, L = 2 dB) |
| m-seq period $2^n-1$, autocorr $\{N,-1\}$ | primitive LFSR | n = 10: 1023 |
| Gold cross-corr $\{-t,-1,t-2\}$, $t=2^{\lfloor(n+2)/2\rfloor}+1$ | preferred pairs | n = 10: 65 (−23.9 dB) |
| CSS: $T_s=2^{SF}/BW$, bin $=BW/2^{SF}$ | LoRa-type | SF7/125k: 1.024 ms, 977 Hz |
| CFO shifts CSS symbol by $\Delta f\,2^{SF}/BW$ bins | CSS | 1.44 kHz @ SF12 = 47 bins |
| CDMA $K\approx1+G_{proc}/(E_b/I_0)$ | equal power, single cell | – |
| Resolvable multipath if delay > $T_c$ | DSSS | GPS: 293 m |
| PSD below kT: $P-10\log W+174$ | LPI | GPS C/A ≈ 18 dB below |

## Worked examples

### Example 1 — GPS L1 C/A link numbers
Minimum received power −128.5 dBm (IS-GPS-200 specifies −158.5 dBW) [5]. PSD over the 2.046 MHz main lobe: $-128.5-63.1=-191.6$ dBm/Hz. With a receiver NF of 2 dB, $N_0=-172$ dBm/Hz → $C/N_0=43.5$ dB-Hz. Data at 50 b/s: $E_b/N_0=43.5-17.0=26.5$ dB — plenty; the hard part is *acquisition* (searching 1023 code phases × Doppler bins of ≈ ±5 kHz satellite + receiver dynamics, verified Doppler figures on the [sync page](synchronization-carrier-timing.md)). Processing gain $10\log_{10}(1.023\times10^6/50)=43.1$ dB. For the ZED-F9P/MAX-M10S on a rocket, the receiver's own tracking loops must tolerate the vehicle's acceleration — a separate GNSS topic ([GNSS antennas](../08-antennas/gnss-antennas.md)).

### Example 2 — Jamming margin of a small DSSS link
BPSK, $N=63$ chips/bit ($G_{proc}=18.0$ dB), required $E_b/J_0=9.6$ dB at 1e-5, 2 dB implementation loss: $M_J=18.0-9.6-2.0=6.4$ dB — the link survives a jammer up to 4.4× stronger than itself. Verified point: at J/S = +13 dB (beyond the margin), BER ≈ 6e-3 with spreading vs 0.37 without. To gain 10 dB more margin, use 10× more chips (bandwidth) or strong FEC (lower $E_b/J_0$ requirement).

### Example 3 — LoRa and rocket Doppler
At 433 MHz and 1000 m/s the Doppler is 1.44 kHz. At SF7/125 kHz one bin is 977 Hz: offset = 1.5 bins, easily estimated from the preamble. At SF12/125 kHz one bin is 30.5 Hz: offset = 47 bins — still estimable from the up/down-chirp preamble, but the Doppler *rate* (142 Hz/s at 10 g — the **range** acceleration $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$ seen by the station, up to ≈ 1.4× the vehicle's acceleration near the pad ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term))) drifts the tone by ≈ 4.7 bins over a 1-second SF12 packet unless the receiver tracks it. (Crystal drift adds to this; LoRa's "low data rate optimisation" for long symbols addresses the same problem.) This is one reason to prefer lower SF, higher BW, or a TCXO during boost. Domain 15 quantifies it: Semtech's drift limit of $\mathrm{BW}/(3\cdot2^{SF})$ per packet allows only a few g at SF10–12/125 kHz, and recommends SF7–8 at 125 kHz (or SF ≤ 9–10 at 250–500 kHz) during boost — see [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md) and [rocket telemetry radio design](../15-lora-ism-radios/rocket-telemetry-radio-design.md).

### Example 4 — FHSS against a single narrowband interferer
50 hop channels, one fixed narrowband interferer strong enough to destroy any hop it hits: 2 % of hops lost. With one packet per hop and no FEC, PER = 2 %; with a code interleaved across 8 hops that can recover any 1 lost hop of 8, a packet fails only if ≥ 2 of its 8 hops are hit: $1-\sum_{i\le1}\binom8i0.02^i0.98^{8-i}=1.0\%$; codewords spanning more hops (with proportionally more redundancy) do better still. Illustrative numbers; real interference is bursty and frequency-selective.

### Example 5 — CDMA back-of-envelope
$G_{proc}=128$ (21.1 dB), required $E_b/I_0=7$ dB (5.0): $K\approx1+128/5=26$ equal-power users in one cell before accounting for thermal noise, neighbouring cells or voice activity.

## Practical notes
- **Acquisition is the hard part.** A DSSS receiver must search code phase (N positions, half-chip steps) × frequency (bins ≈ $1/(2T_{coh})$ wide). FFT-based parallel code search (circular correlation via FFT, as in the script's cross-correlation check) makes this fast on an SDR.
- **Tracking:** a delay-locked loop (early–late correlators ½ chip apart) keeps code alignment; a Costas/PLL tracks carrier ([sync](synchronization-carrier-timing.md)).
- **Chip-rate spectrum:** rectangular chips give $\mathrm{sinc}^2$ spectra with slow sidelobes; filter them (RRC chips, or half-sine O-QPSK chips as in 802.15.4).
- **Near–far at the launch site:** a 2 W LoRa transmitter on the pad is enormously stronger than a distant one; LoRa's SF orthogonality is imperfect (inter-SF rejection is finite), so co-located gateways and transmitters can still desensitise each other.
- **Regulatory view:** ISM rules in some regions treat "digital modulation" (e.g. ≥ 500 kHz 6-dB bandwidth in the US 902–928 MHz band) and FHSS differently; LoRa at 125 kHz is usually operated under hopping or duty-cycle rules — see domain 19 (unverified here).

## Common mistakes & misconceptions
- **"Spread spectrum improves SNR against thermal noise."** It does not; BER depends on Eb/N0 alone. The gain is against narrowband interference, jamming, multipath and multiple access.
- **"Processing gain is free coding gain."** Processing gain is bandwidth expansion; coding gain is Eb/N0 reduction. You can have either or both.
- **"Gold codes are orthogonal."** They have *low* cross-correlation (−24 dB for 1023-chip codes), not zero; with a much stronger interfering user, cross-correlation limits sensitivity (near–far).
- **"LoRa works below the noise floor, so it beats Shannon."** Its Eb/N0 is ≈ 6 dB; the negative SNR is relative to 125 kHz of noise.
- **Ignoring the CSS frequency/timing ambiguity** — a static frequency offset reads as a symbol shift; without the preamble's correction every symbol is wrong.
- **Choosing a code length without considering acquisition time** — longer codes give more gain but a larger search.

## How to simulate / verify
- **`tools/verify/comms_spread_spectrum.py`** (< 1 s): m-sequence properties; GPS C/A generation from taps and G2 delays vs IS-GPS-200 / gps.gov; three-valued Gold cross-correlation; DSSS BER vs broadband and CW jammers; CSS dechirp/FFT demodulation and one-bin CFO shift at SF7/SF12; GPS link numbers. All PASS.
- **GNU Radio:** *GLFSR Source* (m-sequences), `gr-gps`/GNSS-SDR for C/A acquisition and tracking; `gr-lora_sdr` (EPFL) for a full LoRa PHY [9].
- **Python acquisition sketch:** `np.fft.ifft(np.fft.fft(rx_1ms) * np.conj(np.fft.fft(code_upsampled)))` for each Doppler bin; pick the max over (bin, code phase).

## Open questions / gaps
- ISM regulatory treatment of LoRa/DSSS/FHSS per region (FCC 15.247, ETSI EN 300 220, IMDA) is left to domain 19.
- LoRa inter-SF rejection values and preamble-based CFO estimation limits are left to domain 15.
- Quantified acquisition-time vs code length/Doppler search for a custom DSSS rocket link would be a useful project page.

## Sources
1. R. L. Pickholtz, D. L. Schilling, L. B. Milstein, "Theory of spread-spectrum communications — a tutorial," *IEEE Trans. Communications* COM-30(5):855–884, 1982 — processing gain, jamming margin, PN sequences, FHSS. (peer-reviewed tutorial)
2. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — ch. 12 (spread-spectrum signals: DSSS, FH, jamming, CDMA, PN sequences). (textbook)
3. S. W. Golomb, *Shift Register Sequences*, Holden-Day, 1967 (rev. Aegean Park Press, 1982) — m-sequence properties. (textbook)
4. R. Gold, "Optimal binary sequences for spread spectrum multiplexing," *IEEE Trans. Inf. Theory* IT-13(4):619–621, 1967. (peer-reviewed, primary)
5. U.S. Space Force, *IS-GPS-200 Revision N*, NAVSTAR GPS Space Segment/Navigation User Segment Interfaces — §3.2.1.3 (C/A code: G1, G2 polynomials, 1.023 Mcps, 1023 chips), Table 3-Ia (G2 taps/delays, first 10 chips octal), §3.3.1.6 (minimum received power −158.5 dBW). https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-200N.pdf (standard)
6. GPS.gov, "L1 C/A PRN Code Assignments," Jan. 2026 edition — G2 delay, initial G2 setting and first 10 chips for PRNs 120–210 (SBAS). https://www.gps.gov/sites/default/files/2026-02/L1CA-PRN-code-assignments-2026-Jan_2.pdf (standard / official table)
7. Bluetooth SIG, *Bluetooth Core Specification* v5.4, Vol. 2 Part A/B — 79 RF channels, 1600 hops/s, adaptive frequency hopping. (standard)
8. L. Vangelista, "Frequency shift chirp modulation: the LoRa modulation," *IEEE Signal Processing Letters* 24(12):1818–1821, 2017 — FSCM model, orthogonality, dechirp+FFT detection. (peer-reviewed)
9. J. Tapparel et al., "An open-source LoRa physical layer prototype on GNU Radio," *IEEE SPAWC* 2020 (arXiv:2002.08208); A. Maleki, H. H. Nguyen, E. Bedeer, R. Barton, "A tutorial on chirp spread spectrum for LoRaWAN: basics and key advances," arXiv:2310.10503, 2023. (peer-reviewed / preprint tutorial)
10. A. J. Viterbi, *CDMA: Principles of Spread Spectrum Communication*, Addison-Wesley, 1995 — CDMA capacity, power control, coding vs spreading. (textbook)
11. M. K. Simon, J. K. Omura, R. A. Scholtz, B. K. Levitt, *Spread Spectrum Communications Handbook*, rev. ed., McGraw-Hill, 1994. (textbook)
12. E. D. Kaplan and C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., Artech House, 2017 — C/A code properties, acquisition search, multipath, RAKE-like correlators. (textbook)
