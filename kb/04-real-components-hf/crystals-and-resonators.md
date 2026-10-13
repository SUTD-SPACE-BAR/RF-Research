---
title: Crystals and resonators — BVD model, load capacitance, pulling, XO/TCXO/OCXO and LoRa frequency budgets
domain: 04-real-components-hf
slug: crystals-and-resonators
tags: [crystal, quartz, butterworth-van-dyke, motional-capacitance, load-capacitance, pullability, pierce-oscillator, drive-level, esr, at-cut, temperature-stability, ageing, tcxo, ocxo, vcxo, mems-oscillator, g-sensitivity, lora, frequency-error, sx1262, 32768-hz, tuning-fork, rtc, parabolic-tempco, rc-oscillator, hsi, uart-tolerance]
prerequisites:
  - ../01-circuit-theory/resonance-and-q.md
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
related:
  - capacitors-at-rf-mlcc.md
  - ../05-analog-electronics/oscillators.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../15-lora-ism-radios/lora-phy-css-math.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
  - ../15-lora-ism-radios/semtech-chip-family.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Crystals and resonators — BVD model, load capacitance, pulling, XO/TCXO/OCXO and LoRa frequency budgets

## Questions this page answers
- What is inside a quartz crystal electrically (motional R, L, C and C0)?
- What are series and parallel (anti-)resonance, and what does "load capacitance" on the datasheet mean?
- How do I pick the two load capacitors for a crystal?
- How many ppm does 1 pF of extra stray capacitance pull my crystal?
- What is ESR, negative resistance and gain margin in a Pierce oscillator, and what is drive level?
- What is the difference between XO, TCXO, VCXO, OCXO and MEMS oscillators?
- How big is a 10 ppm error at 433 MHz and 915 MHz?
- When does LoRa need a TCXO? Why do narrow bandwidths and high spreading factors care about crystal drift?
- Does rocket acceleration or vibration shift my radio's frequency?
- Why are watch/RTC crystals 32.768 kHz, and why do they drift so much in the cold?
- How many seconds per day will my flight computer's RTC lose at a cold launch site?
- Is the MCU's internal RC oscillator good enough, or do I need a crystal (UART, CAN, USB, RTC)?

## TL;DR
- **BVD model:** motional $R_1,L_1,C_1$ in series, shunted by $C_0$. For the SX1261/2 reference crystal (32 MHz, $C_1=1.89$ fF, $C_0=0.6$ pF, $R_1=30\ \Omega$): $L_1=13.1$ mH, **Q ≈ 88 000**; parallel resonance 50 kHz (1574 ppm) above series resonance.
- **Load resonance:** $f_L\approx f_s\left[1+\dfrac{C_1}{2(C_0+C_L)}\right]$; **pulling sensitivity** $S=-\dfrac{C_1}{2(C_0+C_L)^2}$ = **−8.4 ppm/pF** for that crystal at $C_L=10$ pF. Every picofarad of unaccounted PCB/pin capacitance moves the frequency by ~8 ppm.
- **Load capacitors:** $C_L=\dfrac{C_1'C_2'}{C_1'+C_2'}+C_{stray}$ ⇒ for equal caps $C_x=2(C_L-C_{stray})$: CL = 10 pF, 3 pF stray → 14 pF each (C0G!). SX126x has internal trim caps (11.3–33.4 pF per pin) instead — ≈ +33 to −39 ppm of pulling range with this crystal.
- **ppm → Hz:** 1 ppm = 434 Hz at 433.92 MHz, 915 Hz at 915 MHz. A ±10 ppm crystal is ±4.3 kHz / ±9.2 kHz; the TX–RX difference can be twice that.
- **LoRa limits (SX1261/2):** TX–RX offset ≤ ±25 % of BW (and ≤ ±50/100/200 ppm timing limits at SF12/11/10). At BW 125 kHz that is 72 ppm at 433.92 MHz / 34 ppm at 915 MHz — easy with crystals. At **BW 7.8–20.8 kHz** it is only **2–12 ppm** → TCXO (±0.5–2.5 ppm) needed.
- **In-packet drift limit** = $\mathrm{BW}/(3\cdot2^{SF})$ of total drift over the packet (×16 with LowDataRateOptimize; SX1261/2 DS §4.1.2, confirmed from the rendered datasheet): **10 Hz for SF12/BW125** (11 ppb at 915 MHz), 163 Hz with LDRO (0.18 ppm). With an AT-cut slope of ~0.3 ppm/K that allows only ≈0.6 K of crystal warming during a packet — why Semtech warns about PA self-heating and recommends thermal isolation or a TCXO.
- **Rocket specifics:** acceleration sensitivity ~2 ppb/g (Semtech "typical" low-g crystal) → 15 g boost = 27 Hz at 915 MHz; step changes at ignition/burnout exceed the SF12/BW125 in-packet limit. **Doppler rate** (100 m/s² of range acceleration → 305 Hz/s at 915 MHz) is larger still; the acceleration that counts is the **range** acceleration $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$ seen by the station, up to ≈ 1.4× the vehicle's acceleration near the pad ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)). Use lower SF / wider BW during boost, a low-g-sensitivity TCXO, and mount the crystal to minimise the acceleration component along its sensitive axis.
- **32.768 kHz = 2¹⁵ Hz** (15 binary dividers → 1 Hz) in a flexural **tuning fork**. An AT plate at that frequency would be ≈ 51 mm thick. Its temperature curve is a downward **parabola**, Δf/f = B(T − T₀)², B ≈ −0.034 ppm/°C² (−0.04 max), T₀ = 25 ± 5 °C. That gives −13.6 ppm (−1.2 s/day) at 5 °C, −42 ppm (−3.6 s/day) at −10 °C and −144 ppm (−12 s/day) at −40 °C, always *slow*, plus ±20 ppm initial tolerance (`tools/verify/s4_rtc_crystal.py`).
- **MCU internal RC oscillators are ~10³× worse than a crystal**: STM32 HSI ±1 % at 25 °C (−8/+5.5 % over −40…125 °C); LSI/RC-slow clocks ±25–50 % uncalibrated; the ESP32-S3 RC drifts "several seconds per day" even after calibration. They are fine for UART (±2–3.3 % total mismatch for both ends together) at room temperature, marginal for CAN (≲ 0.5 %) and inadequate for USB full-speed (±0.25 %) without crystal-less recovery.
- Oscillator classes (Vig): XO 10⁻⁵–10⁻⁴, TCXO ~10⁻⁶, MCXO 10⁻⁸–10⁻⁷, OCXO ~10⁻⁸ (incl. temperature and one year of ageing).

## Intuition (no math)
A quartz crystal is a thin slab of quartz with electrodes on both faces. Quartz is piezoelectric: a voltage makes it flex, and flexing makes a voltage. The slab has a mechanical resonance (for an AT-cut, a thickness-shear mode) with extremely low loss, so electrically it looks like a series RLC with an absurdly large inductance and tiny capacitance — a resonator with Q in the tens of thousands to millions. Across it sits the ordinary capacitance of the two electrodes, $C_0$.

Below its series resonance the crystal is capacitive; between the series resonance $f_s$ and the parallel resonance $f_p$ (a fraction of a percent higher) it is **inductive**; above $f_p$ capacitive again. An oscillator makes the crystal operate in that narrow inductive window, resonating with the circuit's capacitance — the **load capacitance** $C_L$. The crystal is manufactured to be exactly on frequency *for a specified $C_L$*. If your board presents a different capacitance, the frequency moves ("pulling"). That is why load capacitors, pin capacitance and PCB stray capacitance matter at the ppm level.

Frequency also moves with temperature (a cubic curve for AT-cut), with time (ageing), with drive level, and — important on a rocket — with acceleration and vibration, because the quartz slab physically deforms. TCXOs measure temperature and correct for it; OCXOs keep the crystal hot at its turnover point; MEMS oscillators use a silicon resonator plus electronic compensation.

## The math

### Level 1 — the Butterworth–Van Dyke (BVD) model
$$Z(\omega)=\left[j\omega C_0+\frac{1}{R_1+j\omega L_1+1/(j\omega C_1)}\right]^{-1}.$$
- Series resonance $f_s=\dfrac{1}{2\pi\sqrt{L_1C_1}}$ (Z ≈ $R_1$), quality factor $Q=\dfrac{\omega_sL_1}{R_1}=\dfrac{1}{\omega_sR_1C_1}$.
- Parallel (anti-)resonance $f_p=f_s\sqrt{1+C_1/C_0}\approx f_s\left(1+\dfrac{C_1}{2C_0}\right)$.
- With a series (or effectively loading) capacitance $C_L$: $f_L\approx f_s\left(1+\dfrac{C_1}{2(C_0+C_L)}\right)$.
SX1261/2 crystal specification (datasheet rev 1.2): 32 MHz, $C_L=10$ pF, $C_0$ 0.3–2 pF (typ 0.6), $R_1$ ≤ 60 Ω (typ 30), $C_1$ 1.3–2.5 fF (typ 1.89), drive ≤ 100 µW. Computed (`tools/verify/components_crystal.py` §1): $L_1=13.09$ mH, $Q=87\,718$, $f_p-f_s=50.4$ kHz, $f_L-f_s=2853$ Hz (+89 ppm); a numerical search of the BVD impedance with 10 pF in series finds the same $f_L$ to within 1 Hz.

### Level 2 — pulling, load capacitors and the Pierce oscillator
**Pulling (trim) sensitivity:**
$$S=\frac{\partial(\Delta f/f)}{\partial C_L}=-\frac{C_1}{2(C_0+C_L)^2}.$$
SX126x crystal at 10 pF: −8.41 ppm/pF. Vig's example ($C_0=5$ pF, $C_1=14$ fF, $C_L=20$ pF): a 10 fF change in $C_L$ gives 1.1×10⁻⁷ (Vig: ≈1×10⁻⁷). Sensitivity falls as $1/(C_0+C_L)^2$ — higher $C_L$ crystals are less sensitive to strays but need more oscillator gain.

**Load capacitors (Pierce, two capacitors to ground):** the crystal sees $C_1'$ and $C_2'$ in series plus stray:
$$C_L=\frac{C_1'C_2'}{C_1'+C_2'}+C_s\quad\Rightarrow\quad C_1'=C_2'=2(C_L-C_s).$$
$C_s$ (pin + PCB) is typically 2–5 pF; for $C_L=10$ pF: 16 / 14 / 10 pF for 2 / 3 / 5 pF stray. Use **C0G** (an X7R load capacitor drifts ±15 % with temperature ⇒ ±10 ppm). The SX126x integrates programmable foot capacitors (11.3–33.4 pF per pin, 0.47 pF steps; reset value 13.6 pF, 19.7 pF once in STDBY_XOSC): with the reference crystal and ~1.5 pF stray the achievable offset is ≈ +33 ppm to −39 ppm about $C_L=10$ pF (script §3), consistent with the datasheet's ±15 ppm minimum / ±30 ppm typical trimming range.

**Oscillation condition.** A Pierce amplifier must present a negative resistance larger than $R_1$. ST's AN2867 expresses this as a critical transconductance $g_{m,crit}=4R_1\omega^2(C_0+C_L)^2$ and requires a **gain margin** $g_m/g_{m,crit}\ge5$: for the SX126x crystal $g_{m,crit}=0.545$ mA/V → need ≥ 2.7 mA/V (the chip is designed for this; relevant when you choose a crystal with higher ESR than specified).

**Drive level** $P=I_{rms}^2R_1$: 100 µW in 30 Ω is 1.8 mA rms. Over-driving causes frequency shift, accelerated ageing and possible damage; "drive-level dependence" can prevent start-up of marginal crystals.

### Level 3 — stability: temperature, ageing, acceleration; oscillator classes; LoRa budgets
**AT-cut temperature curve.** $\Delta f/f\approx a_1(T-T_0)+a_3(T-T_0)^3$ with inflection $T_0\approx25$ °C (IQD: 25 °C; generally 25–35 °C depending on cut and mounting), $a_1$ set by the cut angle and $a_3\approx1.1\times10^{-4}$ ppm/K³ (Bechmann-type coefficients; value from standard quartz literature, **medium confidence**). Choosing $a_1=-\tfrac34a_3X^2$ for a range $T_0\pm X$ gives equiripple deviation $a_3X^3/4$ (script §6): −20…70 °C → ±2.5 ppm; −40…85 °C → ±7.5 ppm; −40…105 °C → ±14 ppm. The slope is ≈ −0.17 to −0.53 ppm/K near 25 °C and 0.5–1.6 ppm/K at the hot end — i.e. **any temperature change of the crystal during a packet shifts frequency by tenths of ppm per kelvin** (Vig also notes TCXO residual slopes up to ~1 ppm/°C at the extremes).

**Ageing.** Quartz ageing is logarithmic-ish in time, largest in the first weeks; typical small SMD crystals are specified ±1–5 ppm in the first year. Vig's comparison table lists TCXO ageing ≈5×10⁻⁷/yr, OCXO 5×10⁻⁹/yr.

**Oscillator classes** (Vig, including environment and one year of ageing): XO 10⁻⁵–10⁻⁴; TCXO ~10⁻⁶ (analog TCXOs ≈20× better than the bare crystal's f–T curve); MCXO 10⁻⁸–10⁻⁷; OCXO ~10⁻⁸ (>1000× better than the bare f–T curve), with warm-up of minutes and ~0.6 W. VCXOs trade stability for a voltage-controlled pull range (tens of ppm). MEMS oscillators are silicon resonators with electronic compensation — robust to shock; compare vendor data for stability, phase noise and g-sensitivity before assuming superiority.

**Acceleration sensitivity (Γ).** Frequency shifts in proportion to acceleration along a sensitivity vector: $\Delta f/f=\boldsymbol\Gamma\cdot\mathbf a$. Semtech's AN1200.14 lists 2 ppb/g as a typical crystal spec and recommends low-g crystals and careful orientation for mobile/vibrating use; Vig's tutorial uses 10⁻⁹/g as a good reference oscillator and lists **missile boost ≈ 15 g peak**. Static: 15 g × 2 ppb/g = 30 ppb → 13 Hz at 433.92 MHz, 27 Hz at 915 MHz. Sinusoidal vibration at $f_v$ produces FM with peak deviation $\Gamma Af_0$ and sidebands at $\pm f_v$ of level ≈ $20\log(\beta/2)$, $\beta=\Gamma Af_0/f_v$: 10 g rms at 100 Hz → −24 dBc (433.92 MHz) and −18 dBc (915 MHz) sidebands at ±100 Hz.

**LoRa frequency budgets (Semtech SX1261/2 datasheet, AN1200.14, AN1200.37).**
- *Static offset* between TX and RX: tolerated up to ±25 % of BW "with no sensitivity degradation" (AN1200.14 Fig. 1 shows ≤ 10 % PER at ±25 % for SF7 and SF12 at 125 kHz), and separately ±50 / ±100 / ±200 ppm for SF12 / SF11 / SF10 (the tighter limit applies). In ppm of carrier: BW 125 kHz → 72 ppm (433.92) / 34 ppm (915); BW 62.5 kHz → 36 / 17 ppm; BW 20.8 kHz → 12 / 5.7 ppm; BW 7.8 kHz → 4.5 / 2.1 ppm. LoRaWAN end-devices are expected to hold ±30 ppm total.
- *Drift during a packet* (the tighter constraint for long packets): datasheet gives Freq_drift_max, which evaluates to ≈ $\mathrm{BW}/(3\cdot2^{SF})$ — 10.2 Hz at SF12/BW125, relaxed 16× (≈163 Hz) with LowDataRateOptimize (recommended when $T_{sym}>16.38$ ms, i.e. SF11/12 at 125 kHz). [Confirmed 2026-09-27 by W2-B6, who rendered the equation image on p. 23 of the SX1261/2 datasheet Rev 1.2 (§4.1.2): $Freq\_drift\_max = BW_L/(3\cdot2^{SF})$, applied to the *total* drift over the packet, ×16 with LDRO — see [LoRa impairments § Doppler rate](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md) and `tools/verify/lora_doppler.py` §5b. It gives 10.17 Hz and 162.8 Hz at SF12/BW125, matching the figures quoted in Semtech's material.] AN1200.37 measured that an SX1262 at +22 dBm on a standard PCB drifts beyond the limit within a long packet; thermal isolation (copper cuts around the crystal) kept it within limit for 400–500 ms but not 1 s; below −20 °C or above 70 °C, or for long +22 dBm packets, use a TCXO.
- *TCXO hookup (SX126x)*: clipped-sine TCXO into XTA via 220 Ω + 10 pF, XTB open, powered from DIO3 (1.6–3.3 V, up to 4 mA), ≤ 1.2 Vpp.

### Level 3 — 32.768 kHz watch crystals and MCU RC oscillators (RTC timekeeping)
**Why 32 768 Hz.** Three reasons. (1) $2^{15}$ = 32 768, so a chain of 15 toggle flip-flops gives exactly 1 Hz with no arithmetic. (2) CMOS power ∝ $fCV^2$, so a low frequency costs nanowatts to microwatts; the crystal drive is only ≤ 0.5 µW (Epson FC-135 [12]). (3) It is above the audible range. A thickness-shear AT plate scales as $f=N/t$ with $N\approx1.66$ MHz·mm, so at 32.768 kHz it would be **51 mm thick** (s4_rtc_crystal.py §1). Watch crystals therefore use a different mode: a quartz **tuning fork** vibrating in flexure, whose frequency scales as width/length², so a 2 × 1.2 mm package resonates at 32 kHz. In the BVD model of an FC-135 class part ($C_1$ 3.4 fF, $C_0$ 1.0 pF, $R_1$ ≤ 70 kΩ): $L_1$ = 6.9 kH, Q ≥ 20 000. The pulling is −9.3 ppm/pF at $C_L$ = 12.5 pF and −35 ppm/pF at 6 pF. The required oscillator transconductance is tiny (≈ 2 µA/V), but the ESR is huge, so leakage, flux residue and moisture on the board easily stop a low-$C_L$ RTC oscillator.

**Parabolic temperature curve.** A flexural tuning fork is cut so its first-order coefficient vanishes at the turnover $T_0$, leaving
$$\frac{\Delta f}{f}=B\,(T-T_0)^2,\qquad B\approx-0.034\ \text{ppm}/^\circ\text{C}^2\ (\text{typ}),\ -0.04\ \text{max};\ T_0=25\pm5\ ^\circ\text{C}.$$
Because B < 0, the crystal is slow both hot and cold, and the error grows quadratically. In clock terms 1 ppm = 0.0864 s/day (1 s/day = 11.6 ppm). Script §2, typical part:

| T (°C) | 35 / 15 | 5 | 0 | −10 | −20 | −40 | 60 | 85 |
|---|---|---|---|---|---|---|---|---|
| Δf/f (ppm) | −3.4 | −13.6 | −21.2 | −41.7 | −68.9 | −144 | −41.7 | −122 |
| s/day | −0.29 | −1.18 | −1.84 | −3.60 | −5.95 | −12.4 | −3.60 | −10.6 |

Worst case (B = −0.04, T₀ off by 5 °C, −20 ppm tolerance) roughly doubles these: −84 ppm (−7.3 s/day) at −10 °C. Compare an AT-cut MHz crystal, whose *cubic* curve stays within ±7.5 ppm over −40…85 °C (above): the watch crystal is the worse frequency reference by an order of magnitude away from room temperature. A TCXO-based RTC (e.g. ±2–3.5 ppm parts) or GNSS time fixes it.

**MCU internal RC oscillators.** On-chip RC/relaxation oscillators set frequency with an on-die R and C, so their temperature and supply coefficients are hundreds to thousands of ppm/°C. Factory trim centres them only at one temperature:

| Clock | Accuracy | ≈ s/day | Source |
|---|---|---|---|
| STM32F412 HSI 16 MHz | ±1 % at 25 °C; −8/+5.5 % over −40…125 °C | 864; 6900 | ST datasheet [13] |
| STM32F417 LSI (32 kHz nominal) | 17–47 kHz (−47/+47 %) | ~40 000 | ST datasheet [13] |
| ESP32-S3 RTC RC (90–150 kHz) | calibrated against the main crystal at wake; "several seconds per day" drift | ~3 (≈ 35 ppm) | Espressif [14] |
| 32.768 kHz crystal at −10 °C | −42 ppm (+ ±20 ppm tolerance) | 3.6 | FC-135 [12] |
| ±2.5 ppm TCXO | 2.5 ppm | 0.2 | — |

What each interface needs: **UART** 8N1 with 16× oversampling tolerates a **total** clock mismatch (transmitter plus receiver) of ±3.3 % on a benign link and ±2 % on a "nasty" one (long capacitive RS-232), i.e. about ±1–1.6 % per side if split evenly (Maxim AN2141 [15]; corrected 2026-10-13 from "±2 % per side"). So the HSI (±1 % at 25 °C) is fine at room temperature against a crystal-clocked partner and risky at the cold or hot extremes. **CAN** typically needs ≲ 0.5 % (it depends on the bit-timing configuration; from knowledge), so use a crystal. **USB full-speed** needs 12 Mb/s ±0.25 %, so use a crystal or the vendor's crystal-less clock recovery from USB SOF packets. **RTC timekeeping** needs a crystal or TCXO. **RF synthesiser references** need a crystal or TCXO (sections above). A flight computer that timestamps logs from an RC-clocked RTC can be minutes out by the end of a day on the pad. Discipline it from GNSS time/PPS (the KB's [GNSS timing](../21-gnss/gnss-timing-1pps.md)) or log the main-crystal tick count instead.

## Design equations & rules of thumb

| Quantity | Equation | Typical / example |
|---|---|---|
| Series resonance | $1/(2\pi\sqrt{L_1C_1})$ | 32 MHz: $L_1$ 13 mH, $C_1$ 1.9 fF |
| Q | $1/(\omega_sR_1C_1)$ | 10⁴–10⁶ (88 000 for SX126x ref.) |
| Load resonance | $f_s[1+C_1/(2(C_0+C_L))]$ | +89 ppm at 10 pF |
| Pulling | $-C_1/[2(C_0+C_L)^2]$ | −8.4 ppm/pF |
| Load caps | $C_x=2(C_L-C_s)$ | 10 pF, 3 pF stray → 14 pF |
| Critical gm | $4R_1\omega^2(C_0+C_L)^2$ | gain margin ≥ 5 |
| ppm → Hz | $f_c\cdot10^{-6}$ | 434 Hz (433.92 MHz), 915 Hz (915 MHz) |
| LoRa static offset | ±25 % BW | 125 kHz: ±31 kHz |
| LoRa in-packet drift | ≈ BW/(3·2^SF) (×16 LDRO) | SF12/125k: 10 Hz (163 Hz) |
| g-shift | $\Gamma a f_c$ | 2 ppb/g, 15 g, 915 MHz: 27 Hz |
| AT-cut best-case | $\pm a_3X^3/4$ | −40…85 °C: ±7.5 ppm |
| 32.768 kHz tuning fork | $B(T-T_0)^2$, B ≈ −0.034 ppm/°C² | −10 °C: −42 ppm = −3.6 s/day |
| ppm → clock error | 1 ppm = 0.0864 s/day | 1 s/day = 11.6 ppm |
| MCU RC (HSI) | ±1 % at 25 °C, several % over T | UART ok, USB/CAN no |

## Worked examples

### 1. Load capacitors for a 32 MHz crystal on a discrete transceiver (SX127x style, external caps)
Crystal $C_L=10$ pF; MCU/RF pins ≈1.5 pF each side plus 1 pF of trace → $C_s\approx2.5$ pF. $C_x=2(10-2.5)=15$ pF → use 15 pF C0G 0402 (E24). Measure frequency on a few boards (with a spectrum analyser on the CW carrier or a frequency counter on a buffered clock output) and adjust: each +1 pF of $C_x$ changes $C_L$ by +0.5 pF → −4.2 ppm.

### 2. When a 433 MHz LoRa link needs a TCXO
Ground station and rocket both with ±10 ppm crystals (worst case 20 ppm apart, 8.7 kHz at 433.92 MHz). BW 125 kHz tolerates ±31 kHz → fine. BW 20.8 kHz (for more sensitivity) tolerates ±5.2 kHz → **fails** worst-case; needs ±2.5 ppm TCXOs (or frequency-offset compensation by retuning the ground station using the measured FEI). At 915 MHz the same crystals give 18.3 kHz — BW 62.5 kHz (±15.6 kHz) already fails.

### 3. Crystal warming during an SF12 packet
SF12/BW125 with LDRO allows ~163 Hz of drift ≈ 0.18 ppm at 915 MHz. Near 25 °C a wide-range AT-cut has slope ≈ −0.3 ppm/K → the crystal may warm by only ≈0.6 K during the 1.5–2.8 s packet. A 1 W PA 10 mm away on a 2-layer board can easily do more — hence Semtech's thermal-isolation cuts or a TCXO.

### 4. Boost-phase effects on a rocket (915 MHz)
Static: 15 g × 2 ppb/g → 27 Hz (steps of this size at ignition/burnout exceed the 10 Hz no-LDRO limit). Doppler: at 300 m/s the carrier is 915 Hz off (fine for static tolerance), but at 100 m/s² of range acceleration (a·r̂ + v⊥²/R, which near the pad is up to ≈ 1.4× the motor's acceleration, [15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)) the Doppler *changes* by 305 Hz/s, i.e. ~460 Hz over a 1.5 s SF12 packet — beyond even the 163 Hz LDRO limit. **Conclusion:** during boost use short packets (SF7–8 at 125 kHz, SF ≤ 9 at 250 kHz at 868/915 MHz; SF ≤ 9 at 125 kHz is fine at 433 MHz), and treat high-SF modes as coast/descent modes; see [rocket telemetry radio design](../15-lora-ism-radios/rocket-telemetry-radio-design.md) and [Doppler](../09-propagation-link-budget/multipath-fading-doppler.md).

### 5. RTC drift on a cold launch morning
A flight computer's RTC runs from a 32.768 kHz crystal (typ. B = −0.034 ppm/°C²). The board soaks overnight and sits on the pad from −10 °C at dawn to +10 °C by mid-morning. A sinusoidal day between those limits averages −22.9 ppm. That is −1.98 s/day, or −0.33 s over a 4 h pad wait (script §3). In Singapore (25–33 °C) the same crystal loses only 12 ms in 4 h, and in a pad box in direct sun (20–55 °C) 0.15 s. Sub-second differences matter only when you merge logs from boards with different clocks, or align them with ground-station or GNSS data. Fix this by recording GNSS time/PPS on every board, or by syncing all boards to one timestamp at arming. An RC-clocked RTC (±1–8 %) would be 2–20 *minutes* out over the same 4 h.

## Practical notes
- **Layout:** crystal as close as possible to the XTA/XTB pins, ground guard around it, no signals under it, and keep it away from the PA and regulators; Semtech AN1200.37 shows slots in the copper around the crystal to delay heat flow from the transceiver.
- **Crystal choice:** use a crystal from the transceiver vendor's recommended list (AN1200.14 lists NDK, Epson, Murata, KDS, Kyocera, Rakon, Taitien, NSK 32 MHz parts and TCXOs) with matching $C_L$, $R_1$ and drive level.
- **Modules:** check whether your LoRa module (e.g. EBYTE E22/E220 series) uses a TCXO or a crystal — this determines which BW/SF combinations are safe across temperature. Verify in the module datasheet; don't assume.
- **Frequency calibration:** measure the carrier of each unit once (spectrum analyser or SDR with a GPSDO reference) and store the offset; LoRa receivers also report the frequency error of each packet (FEI), which can be used to track and correct the ground station.
- **GNSS as a reference:** u-blox receivers provide a disciplined timepulse; a PLL or software correction against it can calibrate crystal offsets on the ground.
- **Ceramic resonators** (±0.3–0.5 %) are for MCU clocks, never for RF synthesiser references; **SAW resonators** (e.g. 433.92 MHz one-port SAW) are used in simple OOK transmitters.

## Common mistakes & misconceptions
- **Computing load caps as $C_x=C_L$** (a common forum/article misconception [10]). Two caps in series: $C_x=2(C_L-C_s)$.
- **Forgetting stray capacitance** (2–5 pF) → frequency 10–40 ppm off.
- **X7R/X5R load capacitors** → temperature and DC-bias drift, ageing.
- **"LoRa doesn't care about frequency error."** It tolerates *static* offset well (±25 % BW) but is intolerant of *drift within a packet* at high SF and narrow BW.
- **Assuming the TX's 10 ppm spec is the link budget.** The error that matters is TX minus RX (both ends) plus Doppler.
- **Ignoring g-sensitivity and thermal transients on a rocket** — static tests on the bench won't show them.
- **"A 32.768 kHz crystal is as good as the 20 ppm on its label."** That is the 25 °C tolerance. The parabolic tempco adds −42 ppm at −10 °C and −144 ppm at −40 °C, always slow. Budget timekeeping from the temperature profile, or use a TCXO RTC.
- **"The internal RC oscillator is calibrated, so it is accurate."** Factory trim is ±1 % at one temperature (10 000 ppm, 864 s/day). It is fine for UART at room temperature, not for USB, CAN, RTC or radio references.
- **Low-C_L watch crystals with dirty boards.** With R₁ up to 70 kΩ, flux residue and moisture load the oscillator and stop it in the cold. Clean the board, keep the traces short and guarded, and check start-up at the coldest expected temperature.
- **Over-driving the crystal** by adding series resistance wrongly or choosing a high-gain oscillator with a low-drive-rated crystal.

## How to simulate / verify
- `python3 tools/verify/s4_rtc_crystal.py` (output `s4_rtc_crystal_output.txt`) — 2¹⁵ divider and AT-plate thickness at 32 kHz; parabolic tempco ppm and s/day vs temperature incl. worst case; launch-day temperature cycles; MCU RC vs crystal vs interface tolerances; FC-135 BVD, pulling, g_m,crit.
- `python3 tools/verify/components_crystal.py` — BVD numbers and numerical load-resonance check, pulling sensitivity (incl. Vig example), load-cap table, SX126x trim range, $g_{m,crit}$, ppm/Hz and LoRa tolerance tables, in-packet drift limits, AT-cut equiripple optimisation, g-sensitivity/vibration sidebands, Doppler rate.
- SPICE: BVD model + Pierce inverter; run `.tran` with a small kick to see start-up time (thousands of cycles because Q is huge — use `.ic`).
- Bench: frequency counter on a buffered clock or spectrum analyser on the CW carrier; thermal chamber or hot-air gun for f–T; shaker table (or vehicle test) for vibration sidebands.

## Open questions / gaps
- AT-cut cubic coefficient ($a_3$) and angle sensitivity are quoted from standard quartz literature (Bechmann et al.) without a fetched primary source in this pass — medium confidence; a crystal vendor's f–T curve should be used for real budgets.
- ~~SX1261/2 Freq_drift_max formula is inferred~~ — **resolved 2026-09-29**: confirmed from the rendered SX1261/2 DS Rev 1.2 p. 23 (W2-B6; [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)). Still open: how much in-packet frequency tracking the chip does beyond this guidance (the 16× LDRO relaxation, versus 4× from bin folding alone, implies some).
- g-sensitivity of the specific crystals/TCXOs in EBYTE modules is unknown; worth a vibration test before flight.
- MEMS oscillator comparisons (stability, g-sensitivity) not quantified here.

## Sources
1. Semtech, "SX1261/2 data sheet," rev. 1.2, June 2019 — crystal specification table, FERR_L limits (±25 % BW; SF12/11/10 ppm limits), Freq_drift_max and LDRO, internal trim capacitors, TCXO control block. https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet)
2. Semtech, "LoRa® modulation crystal oscillator guidance," AN1200.14 rev. 2.1, Aug. 2018 — typical crystal spec, ±25 % BW offset tolerance (PER plot), g-sensitivity and orientation, recommended crystals/TCXOs. https://www.mouser.com/pdfdocs/an120014-xo-guidance-lora-modulation.pdf (app note)
3. Semtech, "SX1261/2 recommendations for best performance," AN1200.37 rev. 1.1, Jan. 2018 — PA self-heating drift, packet durations, thermal isolation, TCXO recommendations. https://cdn.sparkfun.com/assets/f/f/b/4/2/SX1262_AN-Recommendations_for_Best_Performance.pdf (app note)
4. J. R. Vig, "Quartz crystal resonators and oscillators for frequency control and timing applications — a tutorial," US Army CECOM SLCET-TR-88-1 rev. 8.5.2.0, Jan. 2004 — oscillator hierarchy and comparison table, pulling formula and example, acceleration environments, vibration-induced sidebands. https://www.pletronics.com/wp-content/uploads/2025/08/Vig_tutorial.pdf (technical report/tutorial)
5. STMicroelectronics, "Oscillator design guide for STM8AF/AL/S and STM32 MCUs," AN2867 — load-capacitance formula, $g_{m,crit}$, gain margin ≥ 5, drive level. https://www.st.com/resource/en/application_note/an2867-guidelines-for-oscillator-design-on-stm8afals-and-stm32-mcusmpus-stmicroelectronics.pdf (app note; content via search summary — fetch timed out)
6. IQD Frequency Products, "A guide to AT-cut crystals" — cut angle 35°15′, inflection ≈25 °C, symmetry of the curve. https://www.iqdfrequencyproducts.com/en/news?d=at-cut-crystals (manufacturer article)
7. R. Bechmann, A. D. Ballato, T. J. Lukaszek, "Higher-order temperature coefficients of the elastic stiffnesses and compliances of alpha-quartz," *Proc. IRE*, 50(8), 1812–1822, 1962 — basis of AT-cut cubic coefficients. (peer-reviewed; not re-fetched)
8. R. L. Filler, "The acceleration sensitivity of quartz crystal oscillators: a review," *IEEE Trans. UFFC*, 35(3), 297–305, 1988. (peer-reviewed, via AN1200.14)
9. arXiv:2101.06016, "Impact of phase noise and oscillator stability on ultra-narrow-band-IoT waveforms for satellite" — LoRa maximum in-frame frequency drift expression (search summary). (preprint)
10. All About Circuits, "Assessing the effect of load capacitance on the frequency of a quartz crystal" (technical article) and Electronics-Notes, "Calculating load capacitance for quartz crystal resonators" — the common "use two caps equal to C_L" misconception and 2–7 pF stray range. https://www.allaboutcircuits.com/technical-articles/assessing-effect-of-load-capacitance-on-frequency-of-quartz-crystal/ ; https://www.electronics-notes.com/articles/electronic_components/quartz-crystal-xtal/load-capacitance-calculation.php (article — secondary; misconceptions only)
11. Verification script `tools/verify/components_crystal.py` (this KB).
12. Seiko Epson, "FC-135 / FC-135R 32.768 kHz crystal unit" data sheet — f_tol ±20 ppm at 25 °C, turnover 25 ± 5 °C, parabolic coefficient −0.04 ppm/°C² max, R₁ ≤ 70 kΩ (FC-135R ≤ 50 kΩ), C₁ 3.4 fF typ, C₀ 1.0 pF typ, drive ≤ 0.5 µW, C_L 7/9/12.5 pF, ageing ±3 ppm first year. Copy: https://www.mikrocontroller.net/attachment/18916/Crystal_Epson_FC-135.pdf (datasheet; values via search-result summary of hosted copies; typical B ≈ −0.034 ppm/°C² is the common tuning-fork value, from knowledge)
13. STMicroelectronics, STM32F412 and STM32F417 data sheets, "Internal clock source characteristics" — HSI 16 MHz ±1 % at 25 °C, −8/+5.5 % over −40…125 °C (by design); LSI 17/32/47 kHz min/typ/max. (datasheet; via search-result summaries of the hosted datasheets)
14. Espressif, ESP-IDF Programming Guide (ESP32-S3), "System Time" — RTC clock sources: internal RC 90–150 kHz (temperature-dependent; "several seconds per day" acceptable drift), external 32 kHz crystal (better stability, +1 µA), 8.5–17.5 MHz/256. https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/system_time.html (vendor documentation)
15. Maxim Integrated (now Analog Devices), "Determining clock accuracy requirements for UART communications," AN2141, https://www.analog.com/en/resources/technical-articles/determining-clock-accuracy-requirements-for-uart-communications.html — 16× receive clock, stop-bit centre 152 clocks after the start edge; total mismatch ±5/152 = ±3.3 % (75 % sampling window) and ±3/152 = ±2 % (50 % window), shared between both ends (app note; PDF read with pdftotext by W5-S18b, 2026-10-13). USB 2.0 Specification §7.1.11 (full-speed data rate 12.000 Mb/s ±0.25 %, i.e. 2500 ppm; high speed 480 Mb/s ±0.05 %) — spec text not read; the section number and values are confirmed by the USB-IF *USB 2.0 Electrical Compliance Test Specification* (which cites §7.1.11 for the HS rate) and the OpenTitan usbdev documentation (2500 ppm), checked by W5-S18b 2026-10-13. (app note / standard)
16. Verification script `tools/verify/s4_rtc_crystal.py` (this KB).
