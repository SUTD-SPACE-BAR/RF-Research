---
title: Reflections, VSWR, return loss and mismatch loss
domain: 03-transmission-lines-matching
slug: reflections-vswr-return-loss-mismatch
tags: [reflection-coefficient, vswr, swr, return-loss, mismatch-loss, standing-waves, transmission-coefficient, feedline-loss, swr-myths]
prerequisites:
  - telegrapher-equations-characteristic-impedance.md
  - ../00-math-foundations/decibels-and-log-units.md
  - ../00-math-foundations/complex-numbers-and-phasors.md
related:
  - input-impedance-stubs-quarter-wave.md
  - smith-chart.md
  - s-parameters.md
  - signal-flow-graphs-mason.md
  - coax-and-cables.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../17-test-measurement/nanovna-librevna-practical.md
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Reflections, VSWR, return loss and mismatch loss

## Questions this page answers
- What is the reflection coefficient Γ and how is it related to VSWR, return loss and mismatch loss?
- My antenna has a VSWR of 2:1 — how much power am I actually losing?
- Does "reflected power" burn out my transmitter / LoRa module?
- Why does the SWR reading change when I change the length of my coax?
- Why does a long, lossy cable make a bad antenna look well matched?
- Is return loss positive or negative? Is S11 = −10 dB the same as a return loss of 10 dB?
- Does low SWR mean my antenna is good?
- How high does the voltage on the line get when the load is mismatched?
- Where are the voltage maxima and minima of a standing wave?

## TL;DR
- $\Gamma_L=\dfrac{Z_L-Z_0}{Z_L+Z_0}$, a complex number with $|\Gamma|\le1$ for passive loads. Moving a distance $d$ toward the source: $\Gamma(d)=\Gamma_Le^{-2\gamma d}$.
- $\text{VSWR}=\dfrac{1+|\Gamma|}{1-|\Gamma|}$; return loss $RL=-20\log_{10}|\Gamma|$ (a **positive** number of dB; $S_{11}$ in dB is its negative); mismatch loss $ML=-10\log_{10}(1-|\Gamma|^2)$.
- Key values: VSWR 1.5 → RL 14.0 dB, 4 % reflected, 0.18 dB loss. VSWR 2.0 → RL 9.5 dB, 11 % reflected, 0.51 dB. VSWR 3.0 → RL 6.0 dB, 25 %, 1.25 dB. RL 10 dB ↔ VSWR 1.92.
- On a lossless line the true VSWR is the **same everywhere**. A *measured* SWR that changes with cable length means: line loss, common-mode current on the outside of the shield, or a cable/meter $Z_0$ mismatch (a 75 Ω cable on a 50 Ω meter swings between 1.0 and 2.25).
- **Loss masks mismatch**: $RL_\text{in}=RL_\text{load}+2A$ (A = matched cable loss). 10 m of RG-58 at 433 MHz (2.9 dB) makes an *open circuit* look like VSWR 3.1.
- "Reflected power" is not simply absorbed by the PA. What stresses a PA is the **changed load impedance** — higher peak voltage ($V_\text{max}=|V^+|(1+|\Gamma|)$: 2 W at |Γ| = 0.5 gives 21 V peak vs 14 V) or current, and altered dissipation.
- Low VSWR says only that power *enters* the antenna; it says nothing about radiation efficiency. A dummy load has perfect VSWR.

## Intuition (no math)
A travelling wave on a line has a fixed ratio of voltage to current, $Z_0$. When the wave hits a load whose ratio $V/I$ is different, the load cannot accept the wave "as is". Nature resolves the conflict by launching a second wave back toward the source, with just the amplitude and phase needed so that *incident + reflected* satisfies the load's $V/I$. A load equal to $Z_0$ needs no reflected wave; an open circuit (no current allowed) needs a reflected current wave that exactly cancels the incident current, so the voltage doubles; a short (no voltage allowed) needs a reflected voltage that cancels, so the current doubles.

The forward and reflected waves travel in opposite directions and interfere. At some points along the line they add (voltage maximum), a quarter-wavelength away they subtract (voltage minimum). This fixed pattern of peaks and nulls is the **standing wave**; the ratio max/min is the standing-wave ratio. On a lossless line both waves keep their amplitude, so the ratio is the same everywhere — you can slide along the line and the peaks and nulls move past, but their ratio doesn't change.

Power bookkeeping is simple for a real $Z_0$: the power the load absorbs is the forward power minus the reflected power. If the source is a matched 50 Ω generator, the reflected wave is absorbed in the generator's internal 50 Ω *in the wave model* — but a real power amplifier is not a 50 Ω resistor behind a voltage source, so "where the reflected power goes" is the wrong question. The right question is: *what impedance does the transistor now see, and does that push its voltage, current or dissipation past its limits?*

## The math

### Level 1 — definitions and conversions

| Quantity | Definition | Range | Notes |
|---|---|---|---|
| Reflection coefficient | $\Gamma=V^-/V^+=(Z_L-Z_0)/(Z_L+Z_0)$ | $|\Gamma|\le1$ (passive) | complex; phase matters for matching |
| VSWR | $V_\text{max}/V_\text{min}=(1+|\Gamma|)/(1-|\Gamma|)$ | 1 … ∞ | magnitude only |
| Return loss | $RL=-20\log_{10}|\Gamma|$ dB | 0 … ∞ | positive; $S_{11}\,[\text{dB}]=-RL$ |
| Reflected power fraction | $|\Gamma|^2$ | 0 … 1 | |
| Mismatch loss | $ML=-10\log_{10}(1-|\Gamma|^2)$ dB | 0 … ∞ | loss vs a matched load, for a $Z_0$ source |
| Voltage transmission coefficient | $\tau=1+\Gamma=2Z_L/(Z_L+Z_0)$ | 0 … 2 | can exceed 1 (voltage, not power) |
| Inverse | $|\Gamma|=(\text{VSWR}-1)/(\text{VSWR}+1)=10^{-RL/20}$ | | |

For a purely resistive load $R$: $\text{VSWR}=\max(R/Z_0,\;Z_0/R)$ — e.g. 25 Ω or 100 Ω on a 50 Ω line are both VSWR 2.

**Conversion table** (computed by `tools/verify/tline_reflections.py`):

| VSWR | \|Γ\| | RL (dB) | Reflected power | Mismatch loss (dB) | Power delivered |
|---|---|---|---|---|---|
| 1.01 | 0.005 | 46.1 | 0.002 % | 0.000 | 100.0 % |
| 1.05 | 0.024 | 32.3 | 0.06 % | 0.003 | 99.9 % |
| 1.10 | 0.048 | 26.4 | 0.23 % | 0.010 | 99.8 % |
| 1.20 | 0.091 | 20.8 | 0.83 % | 0.036 | 99.2 % |
| 1.50 | 0.200 | 14.0 | 4.0 % | 0.177 | 96.0 % |
| 1.92 | 0.315 | 10.0 | 9.9 % | 0.454 | 90.1 % |
| 2.00 | 0.333 | 9.54 | 11.1 % | 0.512 | 88.9 % |
| 2.50 | 0.429 | 7.36 | 18.4 % | 0.881 | 81.6 % |
| 3.00 | 0.500 | 6.02 | 25.0 % | 1.249 | 75.0 % |
| 4.00 | 0.600 | 4.44 | 36.0 % | 1.938 | 64.0 % |
| 5.00 | 0.667 | 3.52 | 44.4 % | 2.553 | 55.6 % |
| 10.0 | 0.818 | 1.74 | 66.9 % | 4.807 | 33.1 % |

### Level 2 — derivations

**Reflection at a load.** On the line (load at $z=0$) the phasor solutions of the [telegrapher equations](telegrapher-equations-characteristic-impedance.md) are $V(z)=V^+e^{-\gamma z}+V^-e^{\gamma z}$, $I(z)=(V^+e^{-\gamma z}-V^-e^{\gamma z})/Z_0$. At the load $V(0)/I(0)=Z_L$:
$$Z_L=Z_0\frac{V^++V^-}{V^+-V^-}\;\Rightarrow\;\Gamma_L\equiv\frac{V^-}{V^+}=\frac{Z_L-Z_0}{Z_L+Z_0}=\frac{z_L-1}{z_L+1},\quad z_L=Z_L/Z_0.$$
Use distance $d=-z$ toward the generator. Then $V(d)=V^+e^{\gamma d}[1+\Gamma(d)]$ with
$$\Gamma(d)=\Gamma_Le^{-2\gamma d}=\Gamma_Le^{-2\alpha d}e^{-j2\beta d},\qquad Z(d)=Z_0\frac{1+\Gamma(d)}{1-\Gamma(d)}.$$
On a lossless line $|\Gamma(d)|=|\Gamma_L|$ is constant and $\Gamma$ rotates clockwise (on the [Smith chart](smith-chart.md)) by $2\beta d$ — a full circle every $\lambda/2$.

**Standing wave.** Lossless: $|V(d)|=|V^+|\,|1+|\Gamma_L|e^{j(\phi_L-2\beta d)}|$, with $\phi_L=\angle\Gamma_L$. Maxima $|V^+|(1+|\Gamma_L|)$ where $\phi_L-2\beta d=-2n\pi$; minima $|V^+|(1-|\Gamma_L|)$ where it equals $-(2n+1)\pi$. Hence
$$\text{VSWR}=\frac{V_\text{max}}{V_\text{min}}=\frac{1+|\Gamma|}{1-|\Gamma|},\qquad d_\text{max}=\frac{\phi_L}{2\beta}+n\frac\lambda2,\qquad d_\text{min}=\frac{\phi_L+\pi}{2\beta}+n\frac\lambda2,$$
max and min are $\lambda/4$ apart, and at a voltage minimum the impedance is real and equal to $Z_0/\text{VSWR}$ (at a maximum, $Z_0\cdot\text{VSWR}$). This is the classical slotted-line method: measure VSWR and the position of the first minimum and you know $Z_L$. Verified numerically (first-minimum position to 10⁻⁴ λ).

**Power.** With real $Z_0$ and peak phasors, the time-average power flowing toward the load at any point of a lossless line is
$$P=\tfrac12\mathrm{Re}\{V I^*\}=\frac{|V^+|^2}{2Z_0}\left(1-|\Gamma|^2\right)=P_\text{fwd}-P_\text{ref}.$$
The cross terms $\mathrm{Re}\{\Gamma^*-\Gamma\}$ vanish because they are purely imaginary — they represent reactive power sloshing in the standing wave. (For lossy lines with complex $Z_0$ the cross terms do not vanish and "forward minus reflected" is no longer exact; see [s-parameters: pseudo-waves](s-parameters.md).)

**Mismatch loss.** A source with internal impedance $Z_0$ and EMF $V_s$ has available power $P_\text{av}=|V_s|^2/(8Z_0)$ and launches $V^+=V_s/2$. Then $P_L=P_\text{av}(1-|\Gamma_L|^2)$ for *any* load — verified in the script for seven loads. The general case with a mismatched source ($\Gamma_S\neq0$) is
$$P_L=P_\text{av}\frac{(1-|\Gamma_S|^2)(1-|\Gamma_L|^2)}{|1-\Gamma_S\Gamma_L|^2},$$
derived with a signal-flow graph in [signal-flow graphs](signal-flow-graphs-mason.md). The denominator is why the delivered power *also* depends on the phases — the root of mismatch uncertainty.

**Junction of two lines.** A line $Z_{01}$ feeding a line $Z_{02}$: $\Gamma=(Z_{02}-Z_{01})/(Z_{02}+Z_{01})$, voltage transmission $\tau=1+\Gamma=2Z_{02}/(Z_{01}+Z_{02})$, transmitted power fraction $|\tau|^2Z_{01}/Z_{02}=1-|\Gamma|^2$. E.g. 50 → 75 Ω: $\Gamma=0.2$, $\tau=1.2$, 96 % of the power passes.

**Lossy line between the meter and the load.** With matched one-way loss $A$ dB ($e^{-\alpha\ell}$ in amplitude), the reflection travels out and back: $|\Gamma_\text{in}|=|\Gamma_L|e^{-2\alpha\ell}$, i.e.
$$RL_\text{in}=RL_L+2A.$$
Also the *total* loss of a mismatched lossy line (power into the line ÷ power into the load), with $a=10^{A/10}$:
$$TL=10\log_{10}\frac{a^2-|\Gamma_L|^2}{a(1-|\Gamma_L|^2)}\;\text{dB},$$
which exceeds $A$ because the standing wave raises the RMS current and voltage and hence the ohmic loss. Derivation: at the load put $V^+=1$; power into the load $\propto1-|\Gamma_L|^2$; at the input the forward wave is $e^{\alpha\ell}$ and the reflected wave $|\Gamma_L|e^{-\alpha\ell}$, so input power $\propto e^{2\alpha\ell}-|\Gamma_L|^2e^{-2\alpha\ell}$; divide. The script checks this against direct bookkeeping and scikit-rf's `zl_2_total_loss` (Stearns' form) [7]; it is independent of the load phase for real $Z_0$.

### Level 3 — generalisations and subtleties
- **Complex $Z_0$.** For lossy lines $Z_0$ is slightly complex, and a conjugate-matched load is not the same as a reflectionless load. Two different "reflection coefficients" then exist: the travelling-wave one (w.r.t. $Z_0$, Marks & Williams pseudo-waves) and the power-wave one (Kurokawa, w.r.t. a reference $Z_R$, $\Gamma_p=(Z_L-Z_R^*)/(Z_L+Z_R)$), for which $1-|\Gamma_p|^2$ is exactly the fraction of available power delivered. For RF coax the difference is negligible; for PCB lines at audio or for on-wafer calibration it isn't. See [s-parameters](s-parameters.md).
- **Active loads** can have $|\Gamma|>1$ (negative resistance: oscillators, reflection amplifiers, tunnel diodes). VSWR is then undefined/meaningless.
- **VSWR discards phase.** Two loads with the same VSWR can need completely different matching networks, and in a cascade the phase decides whether mismatches add or cancel (±ripple). Always keep complex Γ (S11) when designing; use VSWR only as an acceptance number.
- **Multiple reflections / cascades.** A cable with a small mismatch at each end gives a frequency-periodic ripple in insertion loss and in input VSWR with period $\Delta f=v_p/(2\ell)$. This is how to recognise connector/adapter mismatches on a VNA sweep: the ripple period gives the distance between the two discontinuities ([TDR](time-domain-reflectometry.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\Gamma=(Z_L-Z_0)/(Z_L+Z_0)$ | any | open +1, short −1, matched 0 |
| $\Gamma(d)=\Gamma_Le^{-2\gamma d}$ | uniform line | rotates 360° per λ/2 |
| VSWR $=(1+|\Gamma|)/(1-|\Gamma|)$ | passive | spec'd VSWR < 2 (RL > 9.5 dB) for most antennas; < 1.5 (RL > 14 dB) for good ones |
| $RL=-20\log|\Gamma|$ | | U.FL connector: VSWR ≤ 1.3–1.4 to 6 GHz (RL ≥ 17.7–15.6 dB) [8] |
| $ML=-10\log(1-|\Gamma|^2)$ | $Z_0$ source | VSWR 2 → 0.51 dB |
| $P_L=P_\text{av}\,(1-|\Gamma_S|^2)(1-|\Gamma_L|^2)/|1-\Gamma_S\Gamma_L|^2$ | general | see Mason page |
| $V_\text{max}=|V^+|(1+|\Gamma|)$, $I_\text{max}=|I^+|(1+|\Gamma|)$ | lossless | 2 W: 14.1 V pk matched; 21.2 V pk at VSWR 3 |
| $RL_\text{in}=RL_L+2A$ | lossy matched line | 3 dB of cable hides 6 dB of RL |
| $TL=10\log[(a^2-|\Gamma_L|^2)/(a(1-|\Gamma_L|^2))]$ | lossy line + mismatch | 2.87 dB line + VSWR 3 → 3.82 dB |
| Ripple period $\Delta f=v_p/2\ell$ | two discontinuities $\ell$ apart | 1 m of VF 0.66 cable: 99 MHz |
| Free-space range $\propto10^{\Delta(\text{dB})/20}$ | link budget | 0.5 dB → −5.6 % range; 3 dB → −29 % |

## Worked examples

### Example 1 — how much does a VSWR 2 antenna cost a 433 MHz LoRa link?
E22-400T33D delivering 2 W (33 dBm) into a 50 Ω load. Antenna VSWR 2.0: $|\Gamma|=1/3$, $ML=0.51$ dB, so 1.78 W reaches the antenna (if the module behaves like a 50 Ω source — see Practical notes). In free space range scales as $10^{-0.51/20}=0.943$: a 20 km link becomes 18.9 km. Peak RF voltage on the line: $V^+=\sqrt{2PZ_0}=14.1$ V; $V_\text{max}=14.1\times(1+1/3)=18.9$ V peak.

### Example 2 — the lossy cable that makes an open circuit look matched
10 m of RG-58 at 433 MHz: Belden's 8.4 dB/100 ft at 400 MHz scaled by $\sqrt{433/400}$ gives 0.287 dB/m, $A=2.87$ dB. With **nothing** on the far end ($RL_L=0$), the radio sees $RL=5.73$ dB = VSWR 3.14. A genuinely poor VSWR 3.0 antenna ($RL_L=6.02$ dB) looks like $RL=11.76$ dB = VSWR 1.70 — "good enough" on a meter, yet from a 1 W-available 50 Ω source only $10^{-0.287}\times(1-0.25)=0.39$ W reaches the antenna (−4.1 dB; bookkeeping as in Example 3). Always measure VSWR at the antenna end, or de-embed the cable ([VNA fixtures](../17-test-measurement/fixtures-and-deembedding.md)).

### Example 3 — 915 MHz, 1 W module, 3 m of RG-58, VSWR 2.5 antenna
Cable loss at 915 MHz: interpolate Belden 13.7 → 14.5 dB/100 ft (900 → 1000 MHz) → 0.452 dB/m, $A=1.36$ dB. Antenna $|\Gamma_L|=1.5/3.5=0.429$, $RL_L=7.36$ dB. At the radio $RL=7.36+2\times1.36=10.08$ dB (VSWR 1.91). Power: from a 1 W-available 50 Ω source the antenna receives $P=10^{-1.36/10}(1-0.429^2)=0.731\times0.816=0.597$ W (−2.24 dB). Of the 2.24 dB, 1.36 dB is plain cable loss, 0.88 dB is mismatch loss at the antenna, and there is no separate penalty at the radio beyond that. (The alternative accounting "line total loss 1.79 dB × input mismatch 0.45 dB" gives the same 0.597 W — both computed in the script.) Fix the antenna, not the cable length.

### Example 4 — reading a VNA sweep
A NanoVNA sweep of a 433 MHz whip shows $S_{11}=-15$ dB at 433 MHz. $RL=15$ dB, $|\Gamma|=0.178$, VSWR 1.43, reflected 3.2 %, $ML=0.14$ dB — excellent. If a 1 m RG-58 pigtail sits between VNA and antenna (0.29 dB), the antenna alone is at most $RL=15-0.58=14.4$ dB — still fine. The *phase* of $S_{11}$ is not interpretable at the antenna until the cable is de-embedded or port extension is applied.

## Practical notes
- **PA/module protection**: many LoRa/ISM module manuals advise never to transmit without an antenna; high VSWR can push the PA transistor's drain/collector voltage past breakdown or alter its heating. The effect depends on the *phase* of the mismatch (which way the load line rotates), so "VSWR x is safe" statements are PA-specific. Integrated PAs often fold back power on detected overcurrent. Cross-link: [power amplifiers](../06-rf-circuits/power-amplifiers.md).
- **The module's output filter assumes 50 Ω**: the harmonic low-pass filter inside/after a PA is designed between 50 Ω terminations; a large mismatch changes its attenuation and can raise harmonic emissions (regulatory issue, [certification](../19-regulations-safety/certification-fcc-ce-imda.md)).
- **Measure at the antenna**: on a rocket, the antenna VSWR also changes with the airframe (fibreglass vs carbon fibre tube, nearby metal) — measure the antenna *installed* in the airframe section ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).
- **Directional couplers/SWR meters** measure forward and reflected *waves* relative to their design impedance (usually 50 Ω). A cheap meter's own directivity (often only 20–25 dB) limits how low an SWR it can read: with 20 dB directivity, a perfect load can read anywhere up to VSWR 1.22 ([mismatch uncertainty](signal-flow-graphs-mason.md)).
- **Common-mode current** (on the *outside* of the coax shield) turns the feedline into part of the antenna. Symptoms: SWR changes when you touch or move the cable or change its length; RF in the ground station; pattern distortion. Cure with a balun or common-mode choke at the feedpoint ([baluns](../06-rf-circuits/baluns-and-rf-transformers.md), [antenna matching and baluns](../08-antennas/antenna-matching-and-baluns.md)).

## Common mistakes & misconceptions
- **"Reflected power burns the PA."** The reflected wave is a bookkeeping device valid on the line. A real PA is not a Thevenin 50 Ω source; its output impedance is generally not 50 Ω and it was designed (load-pulled) for a specific load. A mismatch changes the load impedance at the transistor, which changes peak voltage, peak current and efficiency — that is what can damage it. Our script shows that for a Thevenin 50 Ω source, two loads with the *same* |Γ| = 0.5 (150 Ω and 16.7 Ω) dissipate 0.25 W and 2.25 W respectively in the source resistance — so "reflected power = extra source heating" is not even true in the idealised model [2], [9].
- **"The SWR on the cable changes with its length."** On a lossless line carrying only the coax (differential) mode, true VSWR is length-independent (verified to 10⁻¹²). A measured change indicates (a) loss (small, monotonic: longer ⇒ lower), (b) common-mode current on the shield exterior, or (c) the cable's $Z_0$ differs from the meter's reference: a 75 Ω cable on a 50 Ω meter with a 50 Ω load reads anywhere from 1.00 to 2.25 depending on length; even 52 Ω RG-58 swings between 1.00 and 1.08 [10].
- **"Changing coax length fixes my SWR."** It only changes what the *meter* sees (via loss, common mode, or $Z_0$ mismatch); the power delivered to the antenna is unchanged or worse. The exception is deliberately using the line as a matching element ([stubs, λ/4](input-impedance-stubs-quarter-wave.md)).
- **"Low SWR = good antenna."** SWR measures how much power is accepted, not radiated. A 50 Ω resistor, a lossy antenna, or a long lossy cable all show low SWR. Efficiency must be measured separately (Wheeler cap, gain comparison) — see [antenna measurement](../08-antennas/antenna-measurement.md).
- **"VSWR 2:1 loses half the power."** It loses 11 % (0.51 dB).
- **"Return loss is −15 dB."** Return loss is defined as a positive quantity; $S_{11}=-15$ dB ⇔ RL = 15 dB. The IEEE AP Transactions editor found about 30 % of submitted antenna papers misusing the term in one year [6]. Say "$|S_{11}|=-15$ dB" or "RL = 15 dB", never "RL = −15 dB".
- **"Standing waves make the coax radiate."** The coax mode's fields are confined inside the shield regardless of SWR; radiation comes from common-mode current, which is caused by unbalanced feeding, not by SWR itself (demonstrated experimentally by IZ2UUF [11], (forum/blog — anecdotal)).
- **"All reflected power is lost."** With a lossless line and a conjugate-matching tuner at the source end, the re-reflected power ends up in the load; only the line's ohmic loss (which rises with SWR, formula above) is lost.
- **"$\Gamma$ can be computed from VSWR."** Only $|\Gamma|$; the phase is lost.
- **"High SWR causes ghosting / intersymbol interference on receive."** A mismatch at *both* ends of a line makes a second, re-reflected copy of the signal that arrives one round trip later, $\Delta t = 2\ell/v_p$, attenuated by $|\Gamma_L||\Gamma_S|$ and twice the line loss. For 30 m of RG-58 ($v_p$ = 0.66c) with VSWR 3 at the antenna ($|\Gamma|$ = 0.5), $|\Gamma|$ = 0.3 at the receiver and 1 dB one-way loss: $\Delta t$ = 0.30 µs, echo −18.5 dB. That matters only when the delay is a sizeable fraction of a symbol (or of a picture element): analogue TV (≈ 0.2 µs per pixel at 4–5 MHz video bandwidth) did show cable ghosts; HF voice, FT8/PSK31 (symbols of 32–160 ms), and LoRa (≥ 8 µs chips and ≥ 1 ms symbols at 125 kHz) do not — the echo merely puts a ripple with period $1/\Delta t$ = 3.3 MHz on the frequency response, flat across a 3 kHz or 125 kHz channel. The real costs of high SWR on receive are mismatch loss (0.5 dB at VSWR 3) and extra line loss — usually negligible against HF atmospheric noise. (Half-addressed myth from W4-D1, ham.stackexchange.com/q/15508.)

## How to simulate / verify
- `tools/verify/tline_reflections.py` — conversion table, standing-wave pattern (VSWR, min/max positions), lossy-line masking with scikit-rf, mismatched-line total loss (formula vs bookkeeping vs `skrf.tlineFunctions.zl_2_total_loss`), source-dissipation counter-example, voltage stress, meter/line $Z_0$ mismatch, 915 MHz budget. All checks pass.
- scikit-rf snippet — what a VNA sees through a lossy cable:

```python
import skrf as rf, numpy as np
f = rf.Frequency(433, 433, 1, unit='MHz')
alpha = 0.287/ (20/np.log(10))                  # RG-58 ~0.287 dB/m at 433 MHz
beta  = 2*np.pi*433e6/(0.66*299792458)
cx = rf.media.DefinedGammaZ0(frequency=f, gamma=alpha+1j*beta, z0=50)
ant = cx.load(0.5)                              # antenna with |Gamma| = 0.5 (VSWR 3)
print((cx.line(10, 'm') ** ant).s_vswr)         # -> 1.70 at the radio end
```

## Open questions / gaps
- PA behaviour under mismatch (load-pull contours, VSWR ruggedness specs) is only qualitative here; belongs in [power amplifiers](../06-rf-circuits/power-amplifiers.md).
- Quantitative common-mode (shield-exterior) modelling needs a three-conductor model or full-wave simulation; left to [antenna matching and baluns](../08-antennas/antenna-matching-and-baluns.md).
- Whether EBYTE E22/E220 modules have VSWR protection is not documented in the sources consulted.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — §2.3 (terminated lossless line, Γ, VSWR, RL), §2.6 (generator and load mismatches), §2.7 (lossy line, power loss). (textbook)
2. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online, rev. 2016), chapter "Transmission Lines" — standing waves, power flow, generator/load mismatch — https://eceweb1.rutgers.edu/~orfanidi/ewa/. (textbook, free)
3. R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., 1992 — ch. 3–4 (reflections, power). (textbook)
4. K. Kurokawa, "Power waves and the scattering matrix," *IEEE Trans. MTT*, vol. 13, no. 2, pp. 194–202, Mar. 1965 — power-wave reflection coefficient. (peer-reviewed)
5. R. B. Marks and D. F. Williams, "A general waveguide circuit theory," *J. Res. NIST*, vol. 97, no. 5, pp. 533–562, 1992, doi:10.6028/jres.097.024 — pseudo-waves, complex $Z_0$. (peer-reviewed)
6. T. S. Bird, "Definition and misuse of return loss," *IEEE Antennas and Propagation Magazine*, vol. 51, no. 2, pp. 166–167, Apr. 2009 — RL is positive; widespread misuse. (peer-reviewed editorial)
7. S. D. Stearns (K6OIK), "Transmission line power paradox and its resolution," ARRL Pacificon Antenna Seminar, 2014 — https://www.fars.k6ya.org/docs/K6OIK-A_Transmission_Line_Power_Paradox_and_Its_Resolution.pdf — total loss of a mismatched line (as implemented in scikit-rf). (conference talk)
8. Hirose Electric, "U.FL Series" catalog, 2020 — VSWR 1.3–1.5 max, DC–6 GHz. (datasheet)
9. M. W. Maxwell (W2DU), *Reflections: Transmission Lines and Antennas*, ARRL (1990; 3rd ed. CQ/WorldRadio 2010) — conjugate matching, where reflected power goes; parts disputed by later authors (see [11] and rec.radio.amateur.antenna threads). (book, amateur; contested in places)
10. EE/ham forum discussions of "SWR changes with coax length" (e.g. worldwidedx.com "Does cable length affect SWR?", shop.rf.guru "Does feedline length matter") — used only to identify the confusion; physics verified in the script. (forum — anecdotal)
11. IZ2UUF, "The myth of reflected power" (2017) and "The myth of SWR causing coax radiation" (2016), iz2uuf.net — VNA-based demonstrations. (blog — anecdotal, measurement-based)
12. Verification: `tools/verify/tline_reflections.py`; scikit-rf 2.0.1 `tlineFunctions`. (numerical check)
