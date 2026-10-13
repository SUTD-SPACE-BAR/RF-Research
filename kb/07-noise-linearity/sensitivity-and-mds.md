---
title: Receiver sensitivity and minimum detectable signal (MDS)
domain: 07-noise-linearity
slug: sensitivity-and-mds
tags: [sensitivity, MDS, noise-floor, SNR, Eb/N0, LoRa, spreading-factor, negative-SNR, EBYTE, GNSS-sensitivity, C/N0, S-meter, S-units, IARU-R1]
prerequisites: [thermal-noise-and-noise-temperature.md, noise-figure-and-friis.md]
related: [receiver-cascade-analysis.md, dynamic-range-sfdr-blocking.md, ../09-propagation-link-budget/link-budget-methodology.md, ../10-comms-modulation/ber-ebn0-and-shannon.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md, ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md, ../17-test-measurement/signal-generators-and-sources.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Receiver sensitivity and minimum detectable signal (MDS)

## Questions this page answers
- How do I calculate a receiver's sensitivity from its noise figure and bandwidth?
- What is the difference between sensitivity, noise floor and MDS?
- How can LoRa receive signals *below* the noise (negative SNR)? Doesn't that break physics?
- Why does each LoRa spreading-factor step give ~2.5 dB more sensitivity?
- Is the EBYTE datasheet's "−147 dBm at 2.4 kbps" believable?
- What sensitivity does my ground station really have at the antenna connector?
- How do GNSS sensitivity figures like "−167 dBm tracking" relate to C/N0?
- What does S9 mean in dBm and microvolts, and how many dB is one S-unit?

## TL;DR
- **Sensitivity** $S = -174 + 10\log_{10}B + \text{NF} + \text{SNR}_\text{min}$ dBm (source at 290 K), for a *stated* error criterion (BER/PER, packet length). General form: $S = 10\log_{10}(k(T_a+T_e)B) + 30 + \text{SNR}_\text{min}$. **MDS** usually means SNR = 0 dB in a stated bandwidth ($-174 + 10\log B + \text{NF}$).
- **LoRa:** the SX126x table is reproduced with NF ≈ 6 dB and SNR thresholds −7.5 (SF7) … −20 dB (SF12): e.g. SF12/BW125 **−137 dBm**, SF7/BW125 −124 dBm, SF12/BW10.4 −148 dBm (`tools/verify/noise_sensitivity.py`).
- **Negative SNR is not magic.** SNR is measured in the full chirp bandwidth; the demodulator correlates over $2^{SF}$ chips. Referred to the bit rate, LoRa needs **Eb/N0 ≈ 6.1–6.3 dB** for 1 % PER (all SF, CR 4/5) — comfortably above the Shannon limit (−1.59 dB). The −2.5 dB/SF step follows from constant Eb/N0: $10\log_{10}\frac{SF+1}{2\,SF} \approx -2.4$ dB.
- **Rule: sensitivity is set by bit rate.** $S \approx -174 + \text{NF} + 10\log_{10}R_b + 6$ dBm: at 2.4 kb/s and NF 6 dB, **≈ −128 dBm** whatever SF/BW combination gives that rate (candidates: −127.0 to −129.0 dBm).
- **EBYTE's "−147 dBm at 2.4 kbps"** (E22-400T33D, E220-900T30D datasheets) would need Eb/N0 = −12.8 dB — **physically impossible**; −147/−148 dBm is the chip's best case at ~20–300 b/s. Use ≈ −128 dBm for 2.4 kb/s in link budgets (19 dB less ⇒ ~9× less free-space range than the datasheet implies).
- **Station sensitivity at the antenna** includes cable, filters and LNA: e.g. 915 MHz module behind 10 m coax −134.4 dBm vs masthead LNA −140.5 dBm (SF12/BW125).

## Intuition (no math)
A receiver can detect a signal when it stands out from the noise by enough for the demodulator to decide correctly. Three things set that level: the noise per hertz (thermal, $kT$, made worse by the receiver's noise figure), the bandwidth over which the receiver collects noise, and how much SNR the modulation needs.

Narrower bandwidth means less noise, but also a slower data rate. Robust modulations need less SNR for the same error rate. LoRa takes an extreme position: it spreads each symbol over a wide chirp (e.g. 125 kHz) but makes each symbol last a long time ($2^{SF}$ chip periods). The receiver "de-chirps" and effectively collects all the energy of a long symbol into one FFT bin while the noise spreads over all $2^{SF}$ bins. Measured in the *full* 125 kHz bandwidth, the signal can be 20 dB below the noise at SF12 and still be decoded — but per *bit* the signal energy is still ~6 dB above the noise density. Negative in-band SNR simply reflects that the bandwidth is much wider than the bit rate.

That leads to the most useful rule for choosing radio settings: **for a given noise figure and a sensible modulation, the sensitivity is fixed by the bit rate.** Halve the bit rate, gain 3 dB, however you do it. No setting can deliver both −147 dBm sensitivity and 2.4 kb/s.

## The math

### Level 1 — definitions
- **Noise floor** (input-referred): $N = 10\log_{10}(kT_0B) + \text{NF} = -173.98 + 10\log_{10}B + \text{NF}$ dBm.
- **Sensitivity**: $S = N + \text{SNR}_\text{min}$, where $\text{SNR}_\text{min}$ is the SNR (in bandwidth $B$) needed for the specified BER/PER.
- **With an antenna of temperature $T_a$**: $S = 10\log_{10}(k(T_a + T_e)B) + 30 + \text{SNR}_\text{min}$ dBm, $T_e = T_0(F-1)$.
- **MDS** (one common definition): signal power equal to the noise floor, $S_\text{MDS} = N$ (SNR = 0 dB in $B$). Variants: "3 dB above the floor" (signal + noise = 2× noise), and radar *tangential sensitivity* (a visual criterion commonly quoted as roughly 8 dB SNR at the video output — historical and subjective).
- **Eb/N0 form**: $\text{SNR} = \frac{E_b}{N_0}\cdot\frac{R_b}{B}$, so $S = -173.98 + \text{NF} + 10\log_{10}R_b + (E_b/N_0)_\text{req}$.

### Level 2 — LoRa's thresholds and the bit-rate rule
LoRa symbol rate $R_s = BW/2^{SF}$; information bit rate $R_b = (SF-2\,DE)\cdot\frac{BW}{2^{SF}}\cdot\frac{4}{4+CR}$, where **DE = 1 when low-data-rate optimisation (LDRO) is on** (mandatory when $T_{sym}$ ≥ 16.38 ms: SF11/12 at 125 kHz, SF12 at 250 kHz) and DE = 0 otherwise ([15 LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)). **Notation:** in formulas CR is the integer $CR\in\{1,2,3,4\}$ (Semtech's ToA convention); in text "CR 4/5" names the code rate $4/(4+CR)$, so CR = 1 ↔ 4/5, 2 ↔ 4/6, 3 ↔ 4/7, 4 ↔ 4/8 (see [canonical conventions](../00-math-foundations/canonical-values-and-conventions.md)). The Semtech demodulator SNR thresholds (SX1261/2 Table 6-1 [1]) are −2.5, −5, −7.5, −10, −12.5, −15, −17.5, −20 dB for SF5…SF12. Converting to Eb/N0 at CR 4/5:
$$\frac{E_b}{N_0} = \text{SNR}_\text{th} - 10\log_{10}\frac{R_b}{BW} = \text{SNR}_\text{th} - 10\log_{10}\frac{0.8\,SF}{2^{SF}}.$$
SF7: $-7.5 - 10\log_{10}(0.04375) = -7.5 + 13.59 = 6.09$ dB. SF12: $-20 - 10\log_{10}(0.002344) = -20 + 26.30 = 6.30$ dB. Every SF lands at 6.1–6.3 dB (script §2). These use DE = 0; with LDRO on, an SF carries only SF − 2 information bits per symbol, so the same SNR threshold means $10\log_{10}\frac{SF}{SF-2}$ more $E_b/N_0$ (SF12: +0.79 dB → 7.09 dB).

*Why −2.5 dB per SF step:* at constant Eb/N0, $\text{SNR}_\text{th}(SF+1) - \text{SNR}_\text{th}(SF) = 10\log_{10}\frac{SF+1}{2\,SF}$: −2.42 dB (SF7→8) … −2.64 dB (SF11→12). Semtech's round −2.5 dB is this relation.

*Reproducing the datasheet* (Rx boosted gain, PER 1 %, 64-byte packets, CR 4/5): $S = -173.98 + 10\log_{10}BW + \text{NF} + \text{SNR}_\text{th}$. Solving for NF from each datasheet entry gives 5.8–7.3 dB for BW ≤ 250 kHz (≈ 6.0 dB for SF12 at 125/250 kHz) and 7.5–8.0 dB at 500 kHz — i.e. the chip's effective NF is ~6 dB and the wide-bandwidth entries carry ~1.5–2 dB extra implementation loss.

| BW | SF | SNR_th | Datasheet S | Implied NF | NF = 6 dB prediction | $R_b$ (CR 4/5, DE = 0) |
|---|---|---|---|---|---|---|
| 10.4 kHz | 7 | −7.5 | −134 | 7.3 | −135.3 | 455 b/s |
| 10.4 kHz | 12 | −20 | −148 | 5.8 | −147.8 | 24 b/s |
| 125 kHz | 7 | −7.5 | −124 | 6.5 | −124.5 | 5.47 kb/s |
| 125 kHz | 12 | −20 | −137 | 6.0 | −137.0 | 293 b/s |
| 250 kHz | 7 | −7.5 | −121 | 6.5 | −121.5 | 10.9 kb/s |
| 250 kHz | 12 | −20 | −134 | 6.0 | −134.0 | 586 b/s |
| 500 kHz | 7 | −7.5 | −117 | 7.5 | −118.5 | 21.9 kb/s |
| 500 kHz | 12 | −20 | −129 | 8.0 | −131.0 | 1.17 kb/s |

The $R_b$ column is the nominal DE = 0 rate. The three SF12 rows at 10.4, 125 and 250 kHz have $T_{sym}$ ≥ 16.38 ms, so LDRO is mandatory and the real rates are **20 b/s, 244 b/s and 488 b/s** (`rfcalc.lora.bitrate(..., ldro=True)`). The sensitivities do not change.

**Bit-rate floor.** With NF = 6 dB and Eb/N0 = 6.1 dB: $S \approx -161.9 + 10\log_{10}R_b$ dBm → 293 b/s: −137.2; 1 kb/s: −131.9; **2.4 kb/s: −128.1**; 9.6 kb/s: −122.1; 62.5 kb/s: −113.9 dBm. The absolute (Shannon, infinite-bandwidth) floor at NF 6 dB is 7.7 dB lower still: −135.8 dBm at 2.4 kb/s (script §3).

### Level 3 — the EBYTE claim, error criteria and GNSS
**The EBYTE contradiction.** The E22-400T33D (SX1268) and E220-900T30D (LLCC68) datasheets list receive sensitivity "−147 ± 1 dBm" and "−147 dBm (typ) / −148 (max)" respectively, both "at air data rate 2.4 kbps" [2][3]. For that to hold with NF = 6 dB would require Eb/N0 = −147 − (−173.98 + 6 + 33.8) = **−12.8 dB**; even a noiseless receiver (NF = 0 dB) would need −6.8 dB. Both are below the Shannon limit of −1.59 dB, so the claim cannot be right for 2.4 kb/s. The −147/−148 dBm figure coincides with the Semtech chip's narrowest-bandwidth SF12 entry (−148 dBm at 10.4 kHz, ≈ 24 b/s). The LoRa settings that produce ≈ 2.4 kb/s (SF7/62.5 kHz, SF8/125 kHz, SF10/250 kHz, SF11/500 kHz) all predict **−127.0 to −129.0 dBm**. EBYTE does not publish its air-rate → SF/BW mapping; domain 15 should measure it. *Recorded as a contradiction in the research log.*

**Sensitivity is only defined with its test conditions.** Packet error rate (1 % PER for Semtech LoRa; 0.1 % BER for FSK), packet length (longer packets need higher SNR for the same PER), coding rate, frequency, temperature, gain mode (SX1262 SF12/BW125: −137 dBm boosted vs −133 dBm power-saving [1]) and whether RF switch loss is included. Comparing datasheet sensitivities without these is meaningless. Radiated (OTA) sensitivity of a module on its board also includes antenna efficiency and self-generated noise (digital clocks, switching regulators) — often several dB worse than conducted sensitivity.

**FSK check.** SX1262 FSK 4.8 kb/s, $B$ = 20 kHz: datasheet −118 dBm (boosted) [1]. With NF 6 dB the implied SNR is −118 − (−173.98 + 43.0 + 6) = +7.0 dB in 20 kHz, i.e. Eb/N0 = 7.0 + 10log(20/4.8) = 13.2 dB — consistent with non-coherent FSK at 0.1 % BER with some implementation margin. At the *same bit rate* LoRa would reach about −125 dBm: the difference (≈ 7 dB) is LoRa's real advantage, not the "−20 dB SNR".

**GNSS.** GNSS receivers quote sensitivities like MAX-M10S "tracking −166/−167 dBm, cold start −148 dBm" [4]. Convert with $C/N_0 = P - N_0$, $N_0 = -173.98 + \text{NF}_\text{sys}$ (or $10\log_{10}k(T_a+T_e)$): with a 1.5 dB system NF, −148 dBm ↔ ≈ 24 dB-Hz (acquisition), −160 dBm ↔ ≈ 12.5 dB-Hz, −166 dBm ↔ ≈ 6.5 dB-Hz (tracking with long integration after acquisition, under the datasheet's "good external LNA" condition). Nominal open-sky L1 C/A signals (−128.5 dBm minimum) give ≈ 45–50 dB-Hz — the figure you see in u-center.

**S-meters and S-units.** Amateur and communications receivers report signal strength in S-units. IARU Region 1 Technical Recommendation R.1 (1981) fixes the scale. On HF (below 30 MHz) **S9 = −73 dBm**, i.e. 50 µV into 50 Ω. On VHF/UHF **S9 = −93 dBm** (5 µV). Each S-unit is **6 dB** (a factor of 2 in voltage), and stronger signals are reported as "S9 + 20 dB" [9]. So HF S1 = −121 dBm (0.20 µV) and VHF/UHF S1 = −141 dBm. The meter reads the **total power in the receiver's filter**, signal plus noise, so its reading depends on bandwidth. On a quiet band it shows the noise floor, not "nothing". Examples (`tools/verify/s7_receiver_numbers.py` §2):
- HF, 10 MHz, 2.4 kHz SSB filter, residential site ($F_a$ = 44.8 dB, [thermal noise](thermal-noise-and-noise-temperature.md#external-noise-itu-r-p372)): the band noise is −95.4 dBm = **S5.3**. A 290 K source alone would be −140.2 dBm, below S1. This is the HF external-noise limit expressed in S-units.
- VHF, 144 MHz, rural ($F_a$ = 7.4 dB), NF 2 dB, 12.5 kHz: noise −125.2 dBm = S3.6 on the VHF scale.
- A just-decodable SF12/BW125 LoRa packet (−137 dBm) would read S1.7 on the VHF/UHF scale. On a 125 kHz meter, though, it is buried in noise that itself reads S5.0, since the SX1262 noise floor −117 dBm is 20 dB above the packet. S-meters (and RSSI) cannot see below-noise signals; use the demodulator's SNR report.
Many commercial receivers do not follow R.1 closely: S-units are often smaller than 6 dB at the bottom of the scale, and the meter is AGC-derived (unverified — forum; calibrate your own receiver with a signal generator and step attenuator). An SDR's software S-meter is a dBFS power reading plus a calibration offset, valid only at the gain and frequency where it was calibrated ([FFT scaling](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

**Beyond AWGN.** Sensitivity is an AWGN (static channel) number. With fading the average SNR must be higher by the fade margin ([09-propagation-link-budget/link-margin-availability](../09-propagation-link-budget/link-margin-availability.md)); with frequency drift (Doppler rate during boost) LoRa's effective sensitivity degrades once the drift exceeds the chip limit ([09-propagation-link-budget/multipath-fading-doppler](../09-propagation-link-budget/multipath-fading-doppler.md)); with impulsive or co-channel interference the usable level is set by the interference, not by kTB.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $S = -174 + 10\log B + \text{NF} + \text{SNR}_\text{min}$ | 290 K source | SX1262 SF12/BW125: −137 dBm |
| $S = 10\log(k(T_a+T_e)B) + 30 + \text{SNR}_\text{min}$ | real antenna | cold sky improves by up to ~0.7 dB for NF 6 dB receivers |
| $S \approx -174 + \text{NF} + 10\log R_b + E_b/N_0$ | any modulation | LoRa: Eb/N0 ≈ 6 dB; 2.4 kb/s ⇒ −128 dBm |
| LoRa $\text{SNR}_\text{th} \approx -2.5\,(SF - 4)$ dB | SX126x/SX127x, CR 4/5 | SF7 −7.5 … SF12 −20 |
| Each SF step: +2.5 dB sensitivity, ~×2 time on air | fixed BW | |
| Each BW halving: +3 dB sensitivity, ×2 time on air | fixed SF | |
| MDS = floor (SNR = 0 dB) | stated $B$ | NF 6, 125 kHz: −117 dBm |
| S-meter (IARU R.1): S9 = −73 dBm HF, −93 dBm VHF/UHF; 6 dB per S-unit | calibrated receivers | HF S1 = −121 dBm; residential 10 MHz band noise in 2.4 kHz ≈ S5 |
| $C/N_0 = P_r - N_0$ | GNSS, any | −128.5 dBm, NF 1.5 dB → ≈ 44 dB-Hz at the T0-referred floor |

## Worked examples
**1 — SF choice for the 433 MHz rocket link.** With NF 6 dB: SF7/BW125 −124.5 dBm (5.5 kb/s), SF9/BW125 −129.5 dBm (1.76 kb/s), SF10/BW125 −132.0 dBm, SF12/BW125 −137.0 dBm (244 b/s with the mandatory LDRO; 293 b/s nominal). The link budget ([09 link-budget-methodology](../09-propagation-link-budget/link-budget-methodology.md)) shows > 50 dB of free-space margin at 30 km even at 2.4 kb/s, so higher SF buys margin the ascent link does not need — and SF ≥ 10 at BW125 runs into the Doppler-rate limit during boost ([multipath-fading-doppler](../09-propagation-link-budget/multipath-fading-doppler.md)). A sensible split: SF7–9 during flight, SF11–12 as a post-landing beacon mode (landed rocket = ground-level link with 30–50 dB extra loss).

**2 — Believable sensitivity for the EBYTE default air rate.** Use −128 dBm (NF 6 dB, 2.4 kb/s) instead of −147 dBm. At a fixed link, 19 dB less sensitivity is 19 dB less margin — in free space a factor $10^{19/20} = 8.9$ in range. (If EBYTE's 2.4 kb/s actually used SF11/BW500 the prediction is −128.5 dBm; SF10/BW250 −129 dBm.)

**3 — Sensitivity at the ground-station antenna connector (915 MHz, SF12/BW125).** Module after 10 m coax: NF 8.6 dB → −134.4 dBm. Masthead SAW + LNA: NF 2.55 dB → −140.5 dBm. LNA after the coax: −138.0 dBm (`noise_cascade.py` A1–A3).

**4 — GNSS C/N0 budget.** Active antenna chain NF 1.19 dB, $T_a$ = 100 K → $N_0$ = −175.8 dBm/Hz; −128.5 dBm → 47.3 dB-Hz. Acquisition needs ≳ 24 dB-Hz (MAX-M10S cold start −148 dBm), so the margin for foliage, body shadowing and plume/antenna pattern is ~23 dB.

**5 — MDS of an SDR spectrum display.** NF 6 dB, RBW 1 kHz: MDS ≈ −138 dBm; the same SDR in 125 kHz: −117 dBm. A LoRa SF12 packet at −130 dBm is 13 dB *below* the 125 kHz floor — invisible in a waterfall with a wide RBW, yet decodable. (Values in `noise_sensitivity.py` §4.)

## Practical notes
- **Measuring sensitivity:** a calibrated signal generator + step attenuator into the receiver in a shielded box; count PER at decreasing levels. Leakage from the generator around the attenuator (unshielded cables, a phone-sized box) makes receivers look better than they are. See [17-test-measurement/signal-generators-and-sources](../17-test-measurement/signal-generators-and-sources.md).
- **Use the chip's SNR report:** SX126x reports packet SNR (SnrPkt/4 dB); link margin ≈ reported SNR − SNR threshold for the SF in use. RSSI alone is ambiguous below the noise floor (at SF12 a decodable signal can be 20 dB below the in-band noise, so RSSI shows the noise).
- **Self-noise on the flight computer:** switching regulators, the Teensy/ESP32 clocks and SD-card bursts radiate; a receiver on the same board (e.g. an RTK corrections receiver) can lose several dB of sensitivity. Test with the full system powered.
- **Temperature:** NF and oscillator stability change with temperature; datasheets specify 25 °C.

## Common mistakes & misconceptions
- **Using −148 dBm for every LoRa setting** or trusting module "−147 dBm @ 2.4 kbps" claims. Sensitivity follows bit rate.
- **"Negative SNR beats Shannon."** In-band SNR is negative; Eb/N0 is +6 dB. Shannon is respected.
- **Comparing FSK and LoRa sensitivities at different bit rates** — compare at equal $R_b$.
- **Forgetting losses before the receiver** — sensitivity at the chip pin is not sensitivity at the antenna.
- **Adding more LNA gain to "improve sensitivity"** once the NF is already set by the LNA — sensitivity depends on NF, not gain.
- **Thinking MDS is universal** — it depends on bandwidth and the chosen criterion; always state both.
- **Reading an S-meter as signal strength alone.** It shows signal plus noise in its filter bandwidth: S5 of band noise on HF is the noise floor, not a signal. A LoRa packet below the noise does not move the meter at all.
- **Assuming sensitivity equals usable level in the field** — interference, fading and drift raise the level needed.

## How to simulate / verify
- `tools/verify/noise_sensitivity.py` — sensitivity formula, SX126x table reproduction with implied NF and Eb/N0, the bit-rate floor and the EBYTE check, candidate settings at ~2.4 kb/s, MDS variants, LoRa time-on-air helper.
- `tools/verify/noise_cascade.py` — station sensitivity including cables, filters, LNA and $T_a$.
- `tools/verify/s7_receiver_numbers.py` §2 — S-unit table (dBm and µV in 50 Ω), band noise expressed in S-units.
- A GNU Radio / Python LoRa modem (e.g. gr-lora_sdr) with an AWGN channel reproduces the SNR thresholds and PER curves ([14-sdr-dsp](../14-sdr-dsp/software-demodulation.md), [15-lora-ism-radios/lora-phy-css-math](../15-lora-ism-radios/lora-phy-css-math.md)).

## Open questions / gaps
- EBYTE's air-rate-to-SF/BW mapping and the modules' real sensitivity per air rate need measurement (SDR capture of the transmitted chirp gives SF/BW directly) — cross-domain note to 15.
- LLCC68 (E220) supports only a subset of SF/BW combinations; its sensitivity table was not re-read here (assumed similar NF to SX126x).
- GNSS C/N0 ↔ sensitivity conversions depend on u-blox's test conditions ("good external LNA"); the numbers above are consistency checks, not specifications.

## Sources
1. Semtech, *SX1261/2 Data Sheet*, Rev 1.2 (June 2019) and Rev 2.2 (Dec 2024): Table 3-8 (sensitivity LoRa/FSK, boosted vs power-saving), Table 6-1 (demodulator SNR per SF), §6 (LoRa rate equations). https://www.semtech.com/products/wireless-rf/lora-connect/sx1262 (datasheet)
2. Chengdu Ebyte, *E22-400TXXX Data Sheet* (2022): E22-400T33D 33 dBm, 410.125–493.125 MHz, receiving sensitivity −147 ± 1 dBm "air data rate 2.4 kbps", 2.4–62.5 kbps. https://www.cdebyte.com/products/E22-400T33D (datasheet) — **claim contradicted by physics; see Level 3.**
3. Chengdu Ebyte, *E220-900T30D User Manual*: LLCC68, 850.125–930.125 MHz, 30 dBm, sensitivity −147 (typ)/−148 dBm "air data rate 2.4 kbps". https://www.cdebyte.com/products/E220-900T30D (datasheet) — same issue.
4. u-blox, *MAX-M10S Data sheet* UBX-20035208: sensitivity tracking −166/−167 dBm, reacquisition −160, cold start −148, hot start −160 dBm (with good external LNA). (datasheet)
5. Semtech, AN1200.22 "LoRa Modulation Basics" (2015): sensitivity $S = -174 + 10\log BW + NF + SNR$. (app note)
6. C. E. Shannon, "A mathematical theory of communication," *Bell Syst. Tech. J.* 27 (1948): capacity bound, Eb/N0 ≥ −1.59 dB. (peer-reviewed)
7. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.4.1 (sensitivity). (textbook)
8. `tools/verify/noise_sensitivity.py`, `tools/verify/noise_cascade.py`, `tools/verify/s7_receiver_numbers.py` (this KB).
9. IARU Region 1, Technical Recommendation R.1 (1981), S-meter calibration for HF and VHF/UHF receivers: S9 = −73 dBm (HF) / −93 dBm (VHF/UHF), 6 dB per S-unit. Read via Wikipedia, "S meter" https://en.wikipedia.org/wiki/S_meter, and hamwaves.com "Decibel & S-readings" https://hamwaves.com/decibel/en/ (secondary summaries of the standard; read 2026-10-12). The R.1 text itself was not retrieved. The 30 MHz HF/VHF boundary is the usual reading but was not confirmed in these sources.
