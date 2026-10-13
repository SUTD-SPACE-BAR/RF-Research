---
title: Canonical values and conventions — the numbers and sign/unit choices every KB page must agree on
domain: 00-math-foundations
slug: canonical-values-and-conventions
tags: [canonical-values, conventions, constants, kT0, e-jwt, RHCP, dBi, ERP, EIRP, dB, RMS, peak, E/N0, processing-gain, factor-of-two, Singapore, IMDA, LoRa, consistency]
prerequisites:
  - decibels-and-log-units.md
  - complex-numbers-and-phasors.md
related:
  - probability-random-processes-and-psd.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../09-propagation-link-budget/link-budget-methodology.md
  - ../10-comms-modulation/matched-filter-detection.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Canonical values and conventions

## Questions this page answers
- Which value of kT, η0, skin depth or FSPL constant should I use so that my answer matches the rest of the knowledge base?
- Why do two pages give answers 3 dB apart for the same thing, and which one is right?
- Is "SNR" in a link or radar budget E/N0 or 2E/N0?
- Is ADC processing gain 10 log(fs/2B) or 10 log(fs/B)?
- What sign convention does the KB use for phasors and for right-hand circular polarisation?
- Is a gain figure in dBi, dBd or dBic, and is a Singapore power limit ERP or EIRP?
- When do I use 10 log and when 20 log, and are the phasors peak or RMS?
- What are the Singapore licence-exempt limits for 433, 868 and 920 MHz LoRa?
- Which E22 channel is legal in Singapore at 250 kHz bandwidth?
- How much inductance does a ground via have, and how wide is a 50 Ω trace on a JLCPCB board?
- How far can a landed rocket be heard, and why do pages disagree?

## TL;DR
- This page is the KB's single reference for **constants, canonical design values and conventions**. Every value has a source and lists the pages that must match it. It was seeded from the internal consistency audit [1] and records the corrections made on 2026-10-02/03 (W5-E9).
- **Reference conditions:** $T_0$ = 290 K, $kT_0$ = −173.98 dBm/Hz (write −174 in rounded budgets); time convention $e^{j\omega t}$; antenna gain in **dBi** unless stated; S-parameters and Γ referenced to 50 Ω; phasors are **peak** amplitudes with $P=\tfrac12\mathrm{Re}\{VI^*\}$.
- **Factor-of-2 (3 dB) traps:** $\mathcal L(f)=S_\varphi/2$; budgets use **E/N0** (the radar χ), not 2E/N0; processing gain is $10\log(f_s/2B)$ for **real** and $10\log(f_s/B)$ for **complex** sampling; ERP = EIRP − 2.15 dB; dBic vs dBi (3 dB for a linear antenna receiving CP); fade margins quoted vs the **mean**; one-sided PSD $N_0$. State the convention with the number.
- **Corrected canonical values:** Leeson white floor $FkT_0/(2P_s)$ (−177 dBc/Hz at F = 1, 0 dBm); ground via 1.6 mm × 0.3 mm to a plane **0.54 nH**; 50 Ω on JLC04161H-7628 **0.359 mm masked**; BGA524N6 in-band IP1dB **−16 dBm**; RTL-SDR V3 NF **5.4 dB at 437 MHz** (11.9 dB at 1280 MHz); 1.13 mm micro-coax **2.65 dB/m at L1**.
- **Singapore (IMDA TS SRD):** 433.05–434.79 MHz **10 mW e.r.p., ≤ 10 % duty**; 866–869 MHz **500 mW e.r.p.**; 917–925 MHz LoRa end devices **100 mW e.r.p., ≤ 1 % duty**. The **whole channel** $f_c \pm BW/2$ must be inside the band: use **E22 CH 24 (434.125 MHz)**; CH 23 (433.125 MHz) only at BW ≤ 125 kHz.
- **Scenario numbers are not facts:** landed range, "typical" C/N0 and SDR NF depend on assumptions. Quote the assumption set (canonical sets are listed below).
- Verified by `tools/verify/fix_canonical_values.py` (all values on this page recomputed; ALL PASS).

## Intuition (no math)
A knowledge base written by many authors drifts in two ways. First, people round or choose constants differently (copper conductivity, 290 K vs 300 K), so the same quantity appears as 3.13 µm on one page and 3.18 µm on another. That is harmless once you know why, but confusing if you don't. Second, and more dangerous, many RF quantities have **two legitimate definitions that differ by exactly a factor of two**: single- vs double-sideband, real vs complex signals, peak vs RMS, one- vs two-sided spectra. Each page can be right in its own convention and still give an answer 3 dB away from the next page. A reader who copies a formula from one page into a budget built on another convention double-counts or loses 3 dB without noticing.

The cure is to pick one convention per trap, write it down once, and make every page say which one it uses. That is what this page does. The other half of the page is a list of **design values** (the via inductance, the trace width to order, the module's real power steps) chosen from the best source, so that every page quotes the same number.

## The math

### Level 1 — the conventions, one line each
| Convention | KB choice | Why / what to watch |
|---|---|---|
| Time-harmonic sign | $e^{j\omega t}$, $j=\sqrt{-1}$; a wave travelling in +z is $e^{j(\omega t-kz)}$ | Physics texts use $e^{-i\omega t}$: replace $j\to -i$; impedances become complex-conjugated and the sense of circular polarisation flips |
| Circular polarisation | IEEE: **RHCP** = $(\hat x - j\hat y)e^{-jkz}$ under $e^{j\omega t}$ — the field rotates clockwise seen from behind (looking in the propagation direction) | Optics uses the opposite naming. GPS is RHCP; a right-hand-wound axial-mode helix radiates RHCP |
| Antenna gain | **dBi** unless stated; dBd = dBi − 2.15; **dBic** = gain relative to an isotropic CP antenna | A linear antenna receiving CP loses 3 dB (polarisation mismatch): "3 dBi linear ≡ 0 dBic" in the GPS link budget |
| Radiated power | **EIRP** relative to an isotropic radiator; **ERP = EIRP − 2.15 dB** (relative to a half-wave dipole) | Singapore limits below 1 GHz are e.r.p., above 1 GHz e.i.r.p. [7] |
| dB | **power ratios 10 log, voltage/field ratios 20 log** — 20 log gives a power ratio only between equal impedances | dBm (1 mW), dBW, dBµV (0 dBm into 50 Ω = 107 dBµV), dBc, dBFS, dB-Hz |
| Phasor amplitude | **peak** phasors, $P=\tfrac12\mathrm{Re}\{VI^*\}$ | With RMS phasors $P=\mathrm{Re}\{VI^*\}$; state which. 33 dBm into 50 Ω = 9.99 V rms = 14.1 V peak |
| Noise reference | $T_0$ = 290 K; **one-sided** PSD $N_0 = kT$ (W/Hz) | 300 K is used in some analog budgets (05) and must be labelled |
| Noise figure | NF in dB, F linear; Friis with linear F and G | — |
| Phase noise | $\mathcal L(f) \equiv S_\varphi(f)/2$ (IEEE Std 1139), single sideband, dBc/Hz | RMS phase $\sigma_\varphi=\sqrt{2\int\mathcal L\,df}$ |
| Detection SNR in budgets | **E/N0** (complex-envelope bookkeeping; the radar χ) | 2E/N0 is used only as the real-passband matched-filter peak ratio [12] |
| ADC / FFT processing gain | **real** sampling: $10\log(f_s/2B)$, per-bin floor $10\log(N/2)$; **complex IQ** at $f_s$: $10\log(f_s/B)$, per-bin floor $10\log N$ | SDRs deliver complex IQ; a bare ADC is real |
| dBFS | state it: for SDR IQ, 0 dBFS = a full-scale **complex** tone ($\lvert x\rvert$ = 1); some tools use a real full-scale sine (3 dB different) | — |
| Fading margins | relative to the **mean** received power (Rayleigh: 10/20/30 dB for 10/1/0.1 % outage) | vs the median they are 8.2/18.4/28.4 dB |
| Array steering | element response $v_n=e^{+jkx_nu}$, steering weights $e^{-jkx_nu_0}$, $u=\sin\theta$ | 12-phased-arrays throughout |
| Reference impedance | Γ and S-parameters to 50 Ω unless stated | — |
| Inductance of vias/traces | always state the **return path** (plane below, return via at spacing s, or isolated/partial) | partial inductance is not a circuit property on its own |
| PCB widths | order the **fab calculator's width for the named stackup**; quote h, εr, copper and mask with every width | closed forms differ by 3–7 % through model inputs |
| Datasheet numbers | quote the **electrical-characteristics table** at its stated conditions, not the feature list | record vendor self-contradictions |
| LoRa coding rate and bit rate | in formulas **CR is the integer 1–4** (Semtech ToA, $R_b=(SF-2\,DE)\cdot\frac{BW}{2^{SF}}\cdot\frac{4}{4+CR}$, with **DE = 1 when low-data-rate optimisation (LDRO) is on** — mandatory when $T_{sym}=2^{SF}/BW$ ≥ 16.38 ms, i.e. SF11/12 at 125 kHz and SF12 at 250 kHz — else DE = 0: SF12/125 = **244 b/s**, not 293); in text "CR 4/5" names the **code rate 4/(4+CR)**: CR 1 ↔ 4/5, 2 ↔ 4/6, 3 ↔ 4/7, 4 ↔ 4/8 | never put 0.8 (= 4/5) where the integer is expected; forgetting DE overstates an LDRO rate by SF/(SF − 2) (+0.8 dB in $E_b/N_0$ at SF12) |
| Gain symbols | **$G_{power}$** = operating power gain $P_L/P_{in}$ (textbook $G_P$; [03](../03-transmission-lines-matching/s-parameters.md), [06 LNA](../06-rf-circuits/lna-design.md)); **$G_{proc}$** = processing gain (DSSS $W/R_b$, LoRa $2^{SF}$; texts write $G_p$; [10 spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md)); $G_T$, $G_A$, MAG unchanged | $G_P$ and $G_p$ differ only in the case of the subscript; never write either bare |

### Level 2 — where each factor of two comes from
**Phase noise ($\mathcal L$ vs $S_\varphi$; Leeson's prefactor).** Write the amplifier input as $A\cos\omega_0t + n(t)$ with one-sided noise density $N_0=FkT_0$ and $P_s=A^2/2$. Split $n$ into in-phase and quadrature parts; each has one-sided baseband density $2N_0$, and the phase is $\varphi\approx n_s/A$, so $S_\varphi = 2N_0/A^2 = N_0/P_s$. The amplitude noise gets the other half. Since $\mathcal L=S_\varphi/2$, the white floor is $FkT_0/(2P_s)$: **−177 dBc/Hz for F = 1 and 0 dBm**. Lee and Hajimiri write $2FkT/P_{sig}$, with $P_{sig}$ the power dissipated in the tank resistance; it is 6 dB higher **by definition** (open-circuit tank noise $4kTR$ versus matched available noise $kT$) [3, 4]. Monte Carlo check: `tools/verify/fix_leeson_prefactor.py`.

**Matched filter (2E/N0 vs E/N0).** For a real passband pulse of energy E in white noise of two-sided density $N_0/2$, the matched-filter peak is $E^2$ and the noise variance $EN_0/2$, so the peak SNR is $2E/N_0$. The radar range equation computes $P_rT/(kT_s)=E/N_0$, and radar detection curves use $\chi=E/N_0$ (Swerling 0: $P_D=Q_1(\sqrt{2\chi},\sqrt{-2\ln P_{FA}})$). Both are correct, and they are 3 dB apart: $P_D$ = 0.9 at $P_{FA}=10^{-6}$ needs $2E/N_0$ = 15.6/16.2 dB (coherent/non-coherent) = **E/N0 = 12.6/13.2 dB** [12, 13].

**Processing gain (real vs complex).** A real ADC at $f_s$ spreads its noise over 0…$f_s/2$; filtering to B keeps $2B/f_s$ of it. A complex (IQ) sampler at $f_s$ spreads noise over $-f_s/2…f_s/2$, i.e. a width $f_s$, and keeps $B/f_s$. Copying the complex form into a real-ADC budget is 3 dB optimistic. The FFT floor follows the same rule: an N-point real FFT spreads noise over N/2 useful bins, a complex FFT over N (8-bit ideal, 1024 points: −77 vs −80 dBFS per bin) [14, 15].

**ERP vs EIRP.** A half-wave dipole has 2.15 dBi gain, so the same radiated field is 2.15 dB lower when referenced to the dipole: ERP = EIRP − 2.15 dB. A 10 mW e.r.p. limit is 12.15 dBm EIRP.

**Peak vs RMS, 10 vs 20 log.** Power is quadratic in voltage: with peak phasors the time average brings the ½. dB of voltage uses 20 log, so that the same physical change is the same number of dB as power, but only across equal impedances.

### Level 3 — where the conventions bend
- Switching between $e^{j\omega t}$ and $e^{-i\omega t}$ conjugates every phasor. An inductor is $+j\omega L$ in one and $-i\omega L$ in the other, and the polarisation-sense labels flip. Always check a source's convention before copying a CP or impedance formula.
- "dBic" is a partial gain for one circular component. A linear antenna that is 3 dBi in a direction has about 0 dBic for either sense of CP there.
- Mean vs median fading margins differ by $10\log(\ln 2)$ = 1.59 dB for Rayleigh fading. The ITU and many papers quote the median.
- Real-vs-complex conventions extend to dBFS, ENBW in Hz, one- vs two-sided PSD (Welch's default is one-sided for real data) and the meaning of "SNR per sample".
- A "canonical" design value is a convention too: it is the KB's chosen number for a stated condition. Change the condition (another via geometry, another stackup, another cable) and recompute rather than copy.

## Design equations & rules of thumb
Canonical values. "Must match" lists the pages that quote the value (consistent after the 2026-10-03 fixes unless noted).

### A. Physical constants and reference conditions
| Quantity | Canonical value | Source | Must match |
|---|---|---|---|
| Boltzmann k | 1.380 649 × 10⁻²³ J/K (exact) | SI 2019 [5] | 00/decibels, 02/units, 07/thermal-noise |
| Reference temperature | **$T_0$ = 290 K**; state T whenever another is used | IEEE/ITU; CONVENTIONS §4 | all noise pages; 05 analog budgets use 300 K (labelled) |
| $kT_0$ | 4.00 × 10⁻²¹ W/Hz = **−173.98 dBm/Hz** (−174 rounded); 300 K: −173.83 | derived | 00, 07, 09, 15, 17 |
| Resistor noise $\sqrt{4kT_0R}$ | **4.00 nV/√Hz per √kΩ; 0.895 nV/√Hz at 50 Ω** (300 K: 4.07 / 0.910) | derived | 00/probability-psd, 07/thermal, 05/low-noise, 05/op-amps |
| c | 299 792 458 m/s (exact); 3 × 10⁸ only in hand estimates | SI | everywhere |
| μ0, ε0 | 1.256 637 061 27(20) × 10⁻⁶ H/m; 8.854 187 8188(14) × 10⁻¹² F/m | CODATA 2022 [5] | 02/electromagnetic-units-and-constants |
| η0 | **376.730 Ω**; 120π = 376.99 Ω is 0.069 % high (flag it) | CODATA 2022 | 02, 08, 09 |
| Copper (design) | **IACS σ = 5.80 × 10⁷ S/m** (1.7241 µΩ·cm); pure Cu (CRC, 293 K) 1.678 µΩ·cm for reference | IEC IACS; CRC | 02/skin-effect, 04/inductors, 08/patch |
| Cu skin depth (IACS) | δ = 66.1 µm/√(f/MHz): **3.18 µm @ 433 MHz (3.17 @ 433.92), 2.19 @ 915, 1.67 @ 1575, 1.34 @ 2450, 0.66 @ 10 GHz** | derived | 02, 04, 08/inductive-coupling |

### B. Materials and fabrication
| Quantity | Canonical value | Source | Must match |
|---|---|---|---|
| FR-4 | εr 4.3–4.7 at 1 GHz, tanδ 0.015–0.022; examples use **εr 4.4, tanδ 0.02** (JLC 7628 prepreg) and **4.5** (JLC 2-layer core) — always state which | 02/dielectrics; JLC | 02, 03, 06, 08, 12, 18, 20 |
| RO4350B / RO4003C | design Dk **3.66** (process 3.48 ± 0.05), Df 0.0037 @ 10 GHz / design Dk 3.55 (3.38), Df 0.0027 | Rogers data sheets | 02, 08, 13, 18 |
| 50 Ω on JLC04161H-7628 (L1 over L2, 0.2104 mm, εr 4.4) | **0.359 mm masked / 0.377 mm bare** microstrip; CPWG with 0.203 mm gap 0.306 mm masked / 0.335 mm bare (JLC calculator — order this) | [13-stackups canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table) | 03/planar-lines, 04/pcb-parasitics, 13, 20 |
| 50 Ω on JLC 2-layer 1.6 mm (JLC0216A, 1.43 mm core, εr 4.5) | **2.692 mm masked** microstrip; CPWG 0.203 mm gap 0.918 mm masked / 1.089 mm bare. The 2.80 mm (h = 1.51 mm) and 2.97–3.06 mm (h = 1.6 mm) figures are model inputs, not JLC's stack: **1.6 mm is the finished board thickness, 1.43 mm the dielectric (core) between the coppers** — confusing the two caused the 1.43/1.51/1.6 mm spread | same | 03, 04, 08/patch, 16/openems |
| Ground via 1.6 mm × 0.3 mm drill to a plane | **≈ 0.54 nH** (Goldfarb–Pucel, validated against measurement); isolated-barrel partial 0.66–0.69 nH; **never** $5.08h[\ln(4h/d)+1]$ (1.30 nH, ≈ 2× — the loop with a distant return). L1→L2 through 0.21 mm prepreg ≈ 0.015–0.023 nH | [16]; 04, 02 | 02/inductance-from-fields, 03/stubs, 03/matching, 04, 06/stability, 13, 20 |
| Via-short stub extension | $\Delta\ell \approx L_{via}v_p/Z_0$ ≈ 1.8 mm for one 0.54 nH via on a 50 Ω line on 1.6 mm FR-4 (open end ≈ 0.6 mm) | derived | 03/stubs |
| MLCC mounted ESL | 0201 ≈ 0.25, **0402 ≈ 0.4 (0.3–0.6)**, 0603 ≈ 0.65–0.7 nH | 04, 13 | 01, 03, 04, 06, 13, 17, 20 |
| Lumped-element criterion | ℓ < λ/20 (accurate), < λ/10 (rough), in the medium; one-way delay < $t_r/6$ | 02/quasi-static | 00, 01, 02, 03, 04, 16, 17 |
| Coax loss (fits $k_1\sqrt f+k_2f$) | at 433 MHz: RG-58 0.287 dB/m, **RG-316 0.72**, RG-174 0.64, LMR-240 0.17, 1.13 mm 1.35 dB/m; **1.13 mm 2.65 dB/m at 1575 MHz** | [03 coax table](../03-transmission-lines-matching/coax-and-cables.md) | 00/decibels, 07/cascade, 17/vna (illustrative 2.5 dB/m at 1 GHz), 18, 20 |
| CFRP wall | in-plane σ ≈ 10³–3 × 10⁴ S/m at UHF (DC up to ~4 × 10⁴); 1 mm wall: **−46 to −111 dB at 433 MHz**, −50 to −162 dB at 1575 MHz | `em_fresnel_radome.py` §3e | 02, 08, 21 |

### C. Standard results and forms
| Result | Canonical form / value | Must match |
|---|---|---|
| FSPL | **32.45 + 20 log f_MHz + 20 log d_km** = 92.45 (GHz, km) = −147.55 (Hz, m) = −27.55 (MHz, m); ITU-R P.525 rounds to 32.4 | 09, 15, 18, 21 |
| Radio horizon | **4.12√h km** (k = 4/3, h in m); geometric 3.57√h; two ends 4.12(√h₁ + √h₂) | 09, 11, 15, 21 |
| Fresnel radius | $R_1=550\sqrt{d_1d_2/((d_1+d_2)f_{MHz})}$ m (d in km); mid-path ½√(λd) | 00, 08, 09 |
| Dipole / monopole | D = 1.641 (**2.15 dBi**); **73.1 + j42.5 Ω at exactly λ/2**; ≈ 72 Ω resonant at 0.47–0.49 λ; monopole 36.5 + j21.3 Ω, 5.16 dBi; Hertzian D = 1.5 (1.76 dBi), R = 789(l/λ)² Ω | 00, 02, 08, 16 |
| Effective aperture | $A_e=G\lambda^2/(4\pi)$ | 08, 09, 14 |
| Chu–McLean | **Q = 1/(ka)³ + 1/(ka)** (one mode); VSWR-2 FBW ≤ 1/(√2 Q) single-tuned | 03, 08 |
| Helix gain | ≈ **13 dBic for 10 turns** (realistic); Kraus 15(C/λ)²NS/λ is 3–5 dB high | 08, 15, 20 |
| Cascades | Friis $F=F_1+(F_2-1)/G_1+\dots$; $1/IIP3=\sum G_{before}/IIP3_i$; SFDR₃ = ⅔(IIP3 − N) | 07, 14, 18 |
| Sensitivity | **S = −174 + NF + 10 log B + SNR_req** (dBm) | 07, 15, 17 |
| ADC | SQNR 6.02N + 1.76 dB; jitter SNR −20 log(2πfσ_t) (100 fs: 87 dB @ 70 MHz, 71 dB @ 433 MHz); processing gain **10 log(f_s/2B) real, 10 log(f_s/B) complex** | 05, 06, 07, 12, 14, 17, 18 |
| Detection SNR | **budgets use E/N0 (radar χ)**; $P_D$ 0.9 / $P_{FA}$ 10⁻⁶, Swerling 0: χ = 13.2 dB non-coherent, 12.6 dB coherent (= 2E/N0 of 16.2 / 15.6 dB) | 10, 11 |
| Windows | Hann ENBW 1.50 bins (1.76 dB), scalloping 1.42 dB; Hamming 0.54/0.46: ENBW 1.363, scalloping **1.75 dB** (harris' 1.78 dB is the 25/46 "exact" Hamming); Blackman 1.727 / 1.10 dB; 4-term Blackman–Harris 2.00 / 0.83 dB | 11, 12, 14 |
| Radar equation | $P_r=P_tG_tG_r\lambda^2\sigma/((4\pi)^3R^4L)$; (4π)³ = 32.98 dB | 09, 11 |
| Phase noise | **Leeson 𝓛 = 10 log[(FkT₀/2P_s)(1 + (f₀/2Q_Lf_m)²)(1 + f_c/f_m)]**, $P_s$ at the sustaining-amplifier input; floor −177 dBc/Hz (F = 1, 0 dBm); ×N adds 20 log N | 05/oscillators, 06/vco-pll, 07/phase-noise, 17 |
| Phase quantisation | worst lobe **20 log tan(π/2^{P+1})** (3/4/6 bits: −14.0/−20.1/−32.2 dB; mnemonic −6.02P + 4.4) | 12 |
| Rayleigh fading | margin vs **mean**: 10/20/30 dB for 10/1/0.1 % outage (vs median 8.2/18.4/28.4) | 00, 09 |
| Class F | 90.7 % with maximally flat V{1,3} and a half-sine current (even harmonics shorted); 81.6 % with only I{1,2}, V{1,3} controlled | 06/power-amplifiers |

### D. LoRa, modules, GNSS and Singapore regulation
| Quantity | Canonical value | Source | Must match |
|---|---|---|---|
| LoRa SNR_req | −7.5 (SF7) … **−20 dB (SF12)**, 2.5 dB/SF, over the full BW | Semtech SX126x | 07, 10, 14, 15 |
| SX1262 sensitivity, BW 125 kHz | **−124 (SF7) … −137 dBm (SF12)** | SX1261/2 DS | 07, 09, 12, 14, 15, 17 |
| Physical sensitivity at 2.4 kb/s | ≈ **−128 dBm** (Eb/N0 ≈ 6 dB, NF 6 dB); EBYTE "−147/−148 dBm" is not physical | derived | 07, 09, 15 |
| Drift limit | **BW/(3·2^SF)** per packet (×16 with LDRO; SF12/125 LDRO: 163 Hz); LDRO when $T_{sym}$ ≥ 16.38 ms | SX126x DS | 04, 09, 10, 15, 20 |
| Doppler rate | **14.2 Hz/s per g at 433 MHz, 30.2 at 923 MHz** (299 Hz/s at 10 g, 915 MHz). SF12/125 boost tolerance ≈ 3 g (simulation) to 6 g (Semtech rule) | f·a/c | 04, 09, 10, 14, 15, 20 |
| Time on air (CR 4/5, 8-symbol preamble, explicit header, CRC) | 32 B SF7/125 **71.9 ms**; 40 B SF7/500 20.5 ms; 32 B SF12/125 1810 ms | `rfcalc.lora` | 15, 19, 20 |
| E22-400T33D | 33 ± 0.5 dBm; steps 33/30/27/24 dBm; TX 0.85–1.2 A; f = 410.125 + CH MHz; default CH 23 | EBYTE; 15 | 05, 13, 15, 19, 20, 21 |
| E220-900T30D | 30 dBm; steps **30/27/24/21 dBm** (no 20 dBm setting); TX 620 mA; ≥ 5 V; f = 850.125 + CH MHz; default 873.125 MHz is not a Singapore band | EBYTE; 15 | 15, 17, 19, 20 |
| BGA524N6 (GNSS LNA) | 19.6 dB, NF 0.55 dB, **IP1dB −16 dBm, IIP3 −9 dBm in-band** (electrical table; the feature list's −12/−4 are not), out-of-band IIP3 −5 dBm, RF input abs. max 0 dBm | Infineon DS rev 3.0 [10] | 06/lna-design, 18/lna-pa, 18/filter-parts, 20/lna |
| RTL-SDR Blog V3 (R820T2) | low-IF ≈ 3.57 MHz (no LO DC spike); **NF 5.8 / 5.4 / 11.9 dB at 145 / 437 / 1280 MHz** (measured, lowest over gain). Pluto 6.1 dB at 437 MHz; HackRF One 11.1 dB at 435 MHz. V4 (R828D) and any SDR at 915/1575 MHz: not found | Libre Space Foundation 2020 [11]; Rowetel | 06, 14, 17, 20 |
| GPS L1 C/A minimum | **−128.5 dBm** (−158.5 dBW into a 3 dBi linear antenna ≡ 0 dBic) | IS-GPS-200 [9] | 07, 08, 10, 20, 21 |
| GNSS C/N0, open sky | **40–50 dB-Hz** (≥ 45 healthy install; < 35 fault). −130 dBm, NF 2 dB: 42.0 dB-Hz with a 290 K antenna, ≈ 44 dB-Hz with $T_a$ ≈ 100 K | 08, 21 | 00, 07, 13 |
| u-blox envelope | **500 m/s, 80 km (50 km on older FW), 4 g** "assuming Airborne 4 g"; AND/OR logic unstated. 4 g is an envelope: boost dropouts are driven by jerk and oscillator g-sensitivity | u-blox DS; 21 | 18, 20, 21 |
| **SG 433.05–434.79 MHz** | **10 mW e.r.p., ≤ 10 % duty (TS SRD 26a)**, or 1 mW e.r.p. with no duty limit (26b) | IMDA TS SRD Iss 1 Rev 3 (Sep 2023) [7] | ~40 pages |
| **SG 866–869 MHz** | **500 mW e.r.p.**, no duty stated (TS SRD 29, "tracking, tracing and data acquisition"; band under review) | same | 15, 19, 20 |
| **SG 917–925 MHz** | **LPWAN end devices 100 mW e.r.p., ≤ 1 % duty (30c)** (binding; the Exemption Notification says 500 mW); non-specific SRD 100 mW (30d); non-LPWAN / access points 500 mW (30b, APs ≤ 10 % duty) | same | 09, 15, 19 |
| SG spurious | −36 dBm below 1 GHz, −30 dBm above 1 GHz (Table 1-a) | same | 06, 15, 17, 19, 20 |
| SG amateur 70 cm | 430–440 MHz, ≤ 10 W ERP, prior written IMDA consent per frequency | IMDA handbook | 15, 19 |
| SG 77–81 GHz | UWB exemption only: mean ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz e.i.r.p. | Exemption Notification item 17; TS UWB | 11, 18, 19 |
| SG power reference | below 1 GHz **e.r.p.**, above 1 GHz **e.i.r.p.**; e.i.r.p. = e.r.p. + 2.15 dB (TS SRD §3) | [7] | 15, 19 |
| **Channel-edge rule** | the whole channel $f_c \pm BW/2$ (better: the 99 % OBW, ≈ 133 kHz at BW 125 kHz) must lie inside the band. 433.05–434.79 MHz holds a 250 kHz channel only for centres 433.175–434.665 MHz | 19, 20 | 15, 19, 20, 21 |
| E22 channel in Singapore | **CH 24 = 434.125 MHz** (125/250/500 kHz fit; 3f = 1302.4 MHz clears the 1215–1300 MHz RNSS band). CH 23 = 433.125 MHz **only at BW ≤ 125 kHz** (lower edge 433.0625 MHz; 99 % OBW edge 433.058 MHz); at 250 kHz it starts at 433.000 MHz. **Avoid CH 0–9** with an L1/L2 receiver such as the ZED-F9P (CH 0–3 → GPS L2, CH 4 edge / 5–6 → GLONASS L2, CH 7–9 → F9P filter skirts); CH 10–22 put 3f in Galileo E6 / BeiDou B3 (E6 receivers only) | derived; 21 | 15, 19, 20, 21 |
| E220 channel with the E22 | E22 2nd harmonic: 866.25 MHz (CH 23) / 868.25 MHz (CH 24). Pair **CH 24 with E220 CH 17 (867.125 MHz)** and CH 23 with CH 18 (868.125 MHz); never CH 16 | derived | 15, 19, 20 |
| E220 in 917–925 MHz | **21 dBm (lowest step) plus a ≥ 1 dB pad or a ≤ 1.15 dBi antenna, ≤ 1 % duty** (21 − 0.5 + 2.15 − 2.15 = 20.5 dBm e.r.p. is 0.5 dB over 100 mW) | derived | 15, 19, 20 |

### E. Canonical scenario sets (quote the set with the number)
| Scenario | Canonical set | Result | Home page |
|---|---|---|---|
| Landed rocket, 433 MHz | rocket antenna 0.1 m, horizontal; 5 m mast, 11 dBic Yagi, −3 dB polarisation, −1 dB feeder; two-ray over medium-dry ground (εr 15, σ 10⁻³ S/m); 33 dBm; no margin | margin = 0 at **≈ 11.5 km (2.4 kb/s) / ≈ 19 km (SF12)**; at 10 mW e.r.p. ≈ 3.5 / 6 km | [09 Example E](../09-propagation-link-budget/link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery) (other sets compared there) |
| GNSS C/N0 | −130 dBm, NF 2 dB, state $T_a$ | 42.0 dB-Hz (290 K), ≈ 44 dB-Hz (100 K) | 00/decibels Example 7 |
| SDR NF in a Y-factor test | measure the SDR first; assume the measured value at the frequency | RTL V3 5.4 dB @ 437 MHz, 11.9 dB @ 1280 MHz | 14/sdr-hardware-survey |

## Worked examples

### 1. Is E22 CH 23 at SF7/250 kHz legal in Singapore?
$f_c$ = 410.125 + 23 = 433.125 MHz. The channel spans 433.125 ± 0.125 = 433.000–433.250 MHz. The band starts at 433.05 MHz, so 50 kHz of the channel lies outside: **not compliant**, whatever the power. At 125 kHz the span is 433.0625–433.1875 MHz (99 % OBW ≈ 133 kHz: 433.0585 MHz), just inside. Move to CH 24 (434.125 MHz: 434.000–434.250 MHz at 250 kHz, inside). Its 2nd harmonic is then 868.25 MHz, which is 125 kHz from E220 CH 18, so move the E220 to CH 17 (867.125 MHz, 1.125 MHz away).

### 2. Processing gain of an RTL-SDR channel
2.4 MS/s complex IQ into a 125 kHz LoRa channel: $10\log(2.4\times10^6/125\times10^3)$ = **12.8 dB**. A real ADC at 2.4 MS/s would give only $10\log(2.4\times10^6/250\times10^3)$ = 9.8 dB. With ENOB ≈ 7 (43.9 dB) the in-channel dynamic range is 56.7 dB for the complex case.

### 3. A 3 dB argument settled
Page A says the matched filter needs 16.2 dB for $P_D$ = 0.9, $P_{FA}=10^{-6}$; page B says 13.2 dB. Both are right: A quotes the real-passband peak 2E/N0, B the radar χ = E/N0. In a link or radar budget (which computes $P_rT/kT_s$ = E/N0) use 13.2 dB.

### 4. Leeson floor of a 433 MHz VCO
F = 2 (3 dB), $P_s$ = 0 dBm: $10\log(2\cdot kT_0/(2\cdot10^{-3}))$ = −177 + 3 = **−174 dBc/Hz** far from the carrier. With $Q_L$ = 20 at 100 kHz: −132.9 dBc/Hz (the old $2FkT/P_s$ form gave −127, 6 dB too noisy).

## Practical notes
- **Before quoting a number** that appears in more than one domain, check this page. If you need a different value, state the condition that makes it different (temperature, stackup, return path, assumption set).
- **When you correct a canonical value**, update this page, re-run `tools/verify/fix_canonical_values.py`, and grep the KB for the old value (the audit found most errors in pages that copied a number without its condition).
- **Builder's checklist from the conventions:** order trace widths from the fab calculator for the named stackup; via to plane ≈ 0.5 nH per 1.6 mm via (use several, at the pad); check that the whole LoRa channel is inside the band; account for the e.r.p. vs EIRP reference in every power-limit check; measure the SDR's own NF before trusting a Y-factor reading.

## Common mistakes & misconceptions
- **"Both sidebands, so 2FkT/P_s."** $\mathcal L$ is one sideband of the phase noise, and only the quadrature half of additive noise is phase noise: $FkT_0/(2P_s)$ (the 05 oscillator page carried this error until 2026-10-02).
- **Copying $10\log(f_s/B)$ from an SDR page into a real-ADC budget** (3 dB optimistic), or the real FFT floor $10\log(N/2)$ into an IQ spectrum (3 dB pessimistic).
- **Mixing 2E/N0 thresholds with an E/N0 radar equation** (3 dB double count).
- **Treating a centre frequency inside the band as compliance.** The occupied bandwidth must be inside.
- **"About 1 nH per via."** That is the Johnson & Graham "+1" formula, about 2× the inductance of a via to a solid plane.
- **Using feature-list or marketing numbers** (BGA524 "−12 dBm", EBYTE "−148 dBm") instead of the electrical table or a physical derivation.
- **Quoting a scenario number as a property** ("the landed range is 5.6 km").
- **Setting a module to a power step it does not have** (the E220 has no 20 dBm step).

## How to simulate / verify
- `python3 tools/verify/fix_canonical_values.py` — recomputes every number in the tables above from first principles or `tools/rfcalc` (constants, kT0, resistor noise, η0, skin depths, via inductances, coax fits, FSPL/horizon constants, detection thresholds incl. Marcum Q, window scalloping, Leeson floor, quantisation lobes, class-F limits, Rayleigh margins, processing gain and FFT floors, LoRa ToA, Doppler rates, drift limit, Singapore channel-edge checks, C/N0, BGA524 SAW budget, landed ranges). ALL PASS.
- `python3 tools/verify/fix_leeson_prefactor.py` — Monte Carlo proof of $S_\varphi = N_0/P_s$, equal AM/PM split, and the corrected Leeson examples.
- `python3 tools/verify/prop_two_ray.py` §5 — landed-rocket two-ray losses behind the canonical scenario.
- `python3 tools/verify/pcb_stackup_widths.py` §9 (domain 13) — field-solver check of the JLC calculator widths.

## Open questions / gaps
- JLC's 2-layer core thickness (1.43 mm in the calculator template) and a TDR measurement of a JLC 50 Ω coupon are still wanted to close the width question by measurement.
- Measured NF of the RTL-SDR V4 (R828D), HackRF and Pluto at 915 and 1575 MHz; a measured landed-rocket path loss on Space Bar hardware; measured e.r.p. of the E220 at 21 dBm plus a pad on the flight antenna.
- Lee–Hajimiri equation numbers were read from surrounding text only; recheck them from a rendered copy. A worked mapping between the Leeson and Lee–Hajimiri definitions for a concrete Colpitts (known tank R) is not yet in the KB.
- `tools/build_index.py --check` validates body links only, not front-matter `prerequisites`/`related` paths.
- The MAX2659 and AT2659 IIP3/IP1dB cells in 18/lna-pa have not been re-checked against their electrical tables.

## Sources
1. W4-D6, *Internal consistency audit of kb/*, `gaps/D6-consistency-audit.md`, 2026-10-02 — issue table and §3 canonical values (this KB; internal audit).
2. W5-E9 fix log, `research-logs/W5-E9-consistency-fixes.md`, 2026-10-03 — which pages were changed and how (this KB).
3. E. Rubiola, "The Leeson effect — phase noise in quasilinear oscillators," arXiv:physics/0502143, 2005 — Eqs. 1.4, 1.26, 1.39. https://arxiv.org/abs/physics/0502143 (peer-reviewed author's monograph draft)
4. T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial," *IEEE JSSC* 35(3), 326–336, 2000 — $2FkT/P_{sig}$ with tank power. (peer-reviewed)
5. BIPM, *The International System of Units (SI)*, 9th ed., 2019; CODATA 2022 recommended values (NIST). https://physics.nist.gov/cuu/Constants/ (standard)
6. IEEE Std 1139-2008, *Standard Definitions of Physical Quantities for Fundamental Frequency and Time Metrology* — $\mathcal L(f) = S_\varphi(f)/2$. (standard)
7. IMDA, *Technical Specification for Short Range Devices* (TS SRD), Issue 1 Rev 3, Sep 2023, and the Telecommunications (Exemption) Notification — Singapore limits as summarised in [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md). (standard / regulation)
8. IEEE Std 145-2013, *Definitions of Terms for Antennas* — sense of polarisation (right-hand = clockwise for an observer looking in the direction of propagation). (standard)
9. IS-GPS-200 (current revision) — L1 C/A minimum received power −158.5 dBW. (standard)
10. Infineon, *BGA524N6 Data Sheet* Rev 3.0 — electrical table (IP1dB −16 dBm, IIP3 −9 dBm, out-of-band IIP3 −5 dBm) and feature list (−12/−4 dBm), as read in [20 LNA recipe](../20-projects-recipes/lna-design-walkthrough.md). (datasheet)
11. A. Csete, S. Christiansen (Libre Space Foundation), "Evaluation of SDR Boards and Toolchains," v1.0, 2020 — measured SDR noise figures, via [14 SDR survey](../14-sdr-dsp/sdr-hardware-survey.md). (independent measurement report)
12. [10 Matched filter and detection](../10-comms-modulation/matched-filter-detection.md) and B. Sklar, *Digital Communications*, 2nd ed., 2001, ch. 3 — 2E/N0. (textbook)
13. [11 Detection theory and CFAR](../11-radar/detection-theory-cfar.md); M. A. Richards, *Fundamentals of Radar Signal Processing* — χ = E/N0, Swerling 0 thresholds. (textbook)
14. [14 Sampling, aliasing and bandpass sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md) — real vs complex processing gain. (this KB, verified)
15. F. J. harris, "On the use of windows for harmonic analysis with the DFT," *Proc. IEEE* 66(1), 51–83, 1978 — window table (Hamming entry mixes the 0.54 and 25/46 variants). (peer-reviewed)
16. M. E. Goldfarb, R. A. Pucel, "Modeling via hole grounds in microstrip," *IEEE Microwave and Guided Wave Letters* 1(6), 135–137, 1991. (peer-reviewed)
17. F. H. Raab, "Maximum efficiency and output of class-F power amplifiers," *IEEE Trans. MTT* 49(6), 1162–1166, 2001. (peer-reviewed)
18. JLCPCB online impedance calculator, run 2026-09-27, as tabulated in [13 stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table). (manufacturer tool)
19. Hirose, *U.FL series* catalogue — 1.13 mm micro-coax attenuation, as fitted in [03 coax and cables](../03-transmission-lines-matching/coax-and-cables.md). (datasheet)
