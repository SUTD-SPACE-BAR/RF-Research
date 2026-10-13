---
title: PA control, protection and sequencing — ALC loops, ramping and key clicks, VSWR foldback, mismatch stress, T/R and bias sequencing, thermal limits, and class-D switching PAs
domain: 06-rf-circuits
slug: pa-control-protection-and-sequencing
tags: [alc, automatic-level-control, power-control, log-detector, integrator-windup, ramp-time, key-clicks, spectral-splatter, vswr-protection, foldback, directional-coupler, directivity, mismatch, ruggedness, t-r-sequencing, hot-switching, coaxial-relay, ptt, bias-sequencing, gan, gaas, thermal-shutdown, duty-cycle, class-d, vmcd, cmcd, zero-voltage-switching, neutralisation]
prerequisites:
  - power-amplifiers.md
  - amplifier-stability-and-biasing.md
  - detectors-and-power-meters.md
  - couplers-dividers-combiners.md
  - agc-loops-and-receiver-gain-control.md
related:
  - rf-switches-attenuators-limiters.md
  - circulators-isolators.md
  - transmitter-architectures.md
  - co-site-interference-and-transmitter-intermod.md
  - ../13-pcb-rf-layout-emc/thermal-management-rf.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../17-test-measurement/rf-power-measurement.md
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# PA control, protection and sequencing

## Questions this page answers
- What does ALC do on a transmitter, and why should it be idle for AFSK and other data modes?
- How do I design a power-control (ALC) loop, and why does it get slow or misbehave near saturation?
- Why does a transmitter "splatter" when it keys up, and what ramp time should I pick on an SX126x?
- How does VSWR protection (foldback) work, and how much does coupler directivity spoil the measurement?
- What actually happens inside a PA when the antenna breaks off or shorts: voltage, current, heat?
- Why must RF be delayed after keying an external amplifier or T/R relay (sequencing), and by how much?
- In what order do I bias a GaN or GaAs PA?
- How hot does a duty-cycled LoRa transmitter get, and when does thermal shutdown matter?
- What is a class-D RF amplifier (voltage-mode vs current-mode), and why is it rare at UHF?
- Why do old VHF amplifiers have an "SSB/FM" switch?

## TL;DR
- **ALC is an AGC for transmitters**: coupler → log/RMS detector → integrator → drive or gain control. With a dB-linear control the loop time constant is $\tau=1/(K_vK_dK_I\,S)$, where $S=dP_{out}/dP_{in}$ is the PA's compression slope. In simulation, S falling from 1.0 to 0.37 dB/dB at 1 dB below $P_{sat}$ made the loop **2.7× slower** (1.0 → 2.7 ms). An unreachable set point winds up the integrator; a drive clamp cut the recovery from 11.4 to 4.0 ms and kept the PA out of 22 dB overdrive.
- **ALC must act slower than the modulation, or not at all.** Inside the envelope bandwidth it becomes an amplitude modulator, which means IMD and splatter. For AFSK or other data through an SSB rig, set the drive so the ALC is idle.
- **Ramp the carrier.** For a 4 ms keyed burst, the power in 10 kHz at +100 kHz offset is −49 dBc with a rectangular edge, −58 dBc with a 10 µs raised-cosine ramp and −116 dBc with 200 µs (simulated). The SX126x offers 10 µs to 3.4 ms (RampTime) [1].
- **VSWR measurement error from directivity D**: the reading lies in $|\Gamma|\pm10^{-D/20}$. With 20 dB directivity a true 3:1 reads anywhere from 2.33:1 to 4:1. **Foldback** $P_{fwd}=\min(P_{set},P_{r,max}/|\Gamma|^2)$ limits a 2 W PA with a 0.5 W reflected limit to 0.5 W forward into an open.
- **Mismatch stress** (class-B, 7.5 V, 2 W, $R_{opt}$ = 12.3 Ω): matched dissipation 0.73 W. Worst case over phase is 1.73 W at 2:1, 2.06 W at 3:1 and **2.73 W into a short or open** (all DC power becomes heat). The drive tries to swing up to VSWR × the allowed voltage on the high-impedance side.
- **Sequencing:** key → receiver protected → relay operates (coax relays 15–20 ms [7]) → contacts settle → PA bias on → RF ramp. Release in the reverse order. GaN: gate to pinch-off *before* drain voltage ([biasing Ex. 8](amplifier-stability-and-biasing.md#example-8--gan-hemt-turn-on--turn-off-sequence)).
- **Class D** (ngspice, 7 MHz, 12 V):
  - *Voltage-mode* gave 2.81 W and η = 98.0 % = R/(R+R_on). Adding 200 pF of switch capacitance cost exactly **C V² f** = 0.20 W.
  - *Current-mode* (parallel tank, zero-voltage switching) absorbed the same 200 pF with < 0.2 points of efficiency loss. It delivers $P=\frac{\pi^2V^2}{2R}\eta^2$ with $\eta=1/(1+\pi^2R_{on}/2R)$.
  - At 433 MHz a 20 pF, 7.5 V switch node wastes 0.49 W by $CV^2f$. That is why UHF switching PAs are class E or current-mode D.

## Intuition (no math)
A transmitter's power amplifier is the most stressed part of a radio. It runs hot, it is driven close to its limits, and it sits next to an antenna that can be detuned, broken, shorted by a launch rail or soaked in exhaust plume. Four kinds of control keep it alive and legal:
1. **Level control (ALC / power control).** Measure the output and adjust the drive, so the output stays at the set power regardless of temperature, supply voltage and part spread. It is a feedback loop like an AGC, with one twist. As the PA approaches saturation, extra drive no longer buys extra output, so the loop loses authority. A naive integrator then keeps pushing ("wind-up") and the PA is driven hard into compression.
2. **Shaping.** Switching a carrier on instantly is like hitting a bell. The sudden edge contains energy at all frequencies (key clicks). A smooth ramp of a few hundred microseconds confines the spectrum.
3. **Protection.** Into a bad load the forward wave returns. The transistor sees an impedance far from its design value: too high (voltage peaks, breakdown) or too low or reactive (high current, heat). Detecting reflected power and folding back the drive, or adding an isolator, keeps the device in its safe area.
4. **Sequencing.** Relays take milliseconds to move, and depletion-mode transistors are *on* when their gate is unbiased. Things must happen in a safe order: protect the receiver, move the relay, wait for it, bias the PA, then ramp the RF. Undo it in reverse.

Class D belongs here because switching PAs are the extreme of "control by saturation". The transistor is a switch, and the efficiency question becomes how much energy is lost at each switching edge.

## The math

### Level 1 — the loops and the protections
- **ALC loop** (all in dB): $P_{out}=f(P_{drv})$, $P_{drv}=P_0+K_vV_c$, $\dot V_c=-K_IK_d(P_{out}-P_{set})$. Linearised, $\tau=1/(K_vK_dK_IS)$ with $S=dP_{out}/dP_{drv}$ in dB/dB.
- **Ramp:** carrier envelope $e(t)$ rising over $t_r$; the spectrum is the Fourier transform of $e(t)$, shifted to $f_c$.
- **Directional coupler reading:** $|\Gamma_{meas}|\in[|\Gamma|-\varepsilon,\ |\Gamma|+\varepsilon]$ with $\varepsilon=10^{-D/20}$ (directivity D in dB, ignoring connector and termination errors).
- **Foldback law:** $P_{fwd}=\min\big(P_{set},\ P_{r,max}/|\Gamma|^2\big)$.
- **Device load under mismatch:** a lossless matching network preserves $|\Gamma|$ (it maps the reference $50\ \Omega$ to $R_{opt}$), so the device sees $Z=R_{opt}\frac{1+\Gamma'}{1-\Gamma'}$ with $|\Gamma'|=|\Gamma_{ant}|$ and some phase.
- **Class D:** voltage-mode (VMCD) $P=\frac{2V_{DD}^2}{\pi^2}\frac{R}{(R+R_{on})^2}$, $\eta=\frac{R}{R+R_{on}}$, hard-switching loss $C_{sw}V_{DD}^2f$. Current-mode (CMCD) $P=\frac{\pi^2V_{DD}^2}{2R}\eta^2$, $\eta=\frac{1}{1+\pi^2R_{on}/2R}$, peak drain voltage $\pi V_{DD}$.

### Level 2 — derivations
**(a) ALC loop gain depends on compression.** Exactly as in the [AGC page](agc-loops-and-receiver-gain-control.md#level-2--derivations), the dB-domain loop is first order. The plant gain, however, is the PA's local slope $S$, which falls from 1 dB/dB (linear) to 0 at hard saturation. For a Rapp PA ($P_{sat}$ = 33 dBm, 30 dB gain, $p$ = 2) with $K_v$ = 20 dB/V, $K_d$ = 25 mV/dB and $K_I$ = 2000 s⁻¹, the script gives (§A):

| Set point | PA input | S (dB/dB) | τ |
|---|---|---|---|
| 20 dBm (13 dB back-off) | −10 dBm | 0.997 | 1.00 ms |
| 30 dBm | +0.6 dBm | 0.749 | 1.34 ms |
| 32 dBm (1 dB below $P_{sat}$) | +4.2 dBm | 0.369 | 2.71 ms |

A loop designed for the linear region becomes sluggish at full power. A loop designed at full power becomes too fast, possibly unstable once the detector filter pole is included, at low power. Remedies: gain-schedule $K_I$ (divide by S from a table), keep the full-power set point ≥ 1–2 dB below $P_{sat}$, or regulate the PA *supply* (an envelope or drain modulator), whose slope stays nearly constant.

**(b) Wind-up.** If the set point exceeds what the PA can deliver (cold battery, mismatch, a set point above $P_{sat}$), the error never reaches zero and the integrator runs to its rail. In §A the drive rose to +30 dBm, 22 dB beyond the compression point, for the whole 100 ms. When the set point was then lowered to 30 dBm, the loop first had to integrate back through the excess. That took 11.4 ms, against 4.0 ms with an anti-wind-up clamp that stops the drive at +8 dBm. Clamp the integrator, or freeze it when the detector shows saturation, i.e. when $\Delta P_{out}/\Delta V_c$ falls below a threshold.

**(c) Ramps and key clicks.** A rectangular burst envelope has a sinc spectrum whose sidelobes fall at only 20 dB/decade (1/f²). A linear ramp of length $t_r$ has a discontinuous slope, which gives 40 dB/decade beyond $1/t_r$. A raised-cosine ramp has a continuous slope and falls at 60 dB/decade. For a 4 ms burst, measured in 10 kHz at +25 / +100 / +250 kHz (§B):

| Ramp | +25 kHz | +100 kHz | +250 kHz |
|---|---|---|---|
| rectangular | −36.8 dBc | −49.0 | −56.9 |
| 10 µs linear | −37.7 | −79.7 | −74.9 |
| 10 µs raised-cosine | −37.3 | −58.4 | −105.6 |
| 40 µs raised-cosine | −45.2 | −85.4 | −109.5 |
| 200 µs raised-cosine | −78.1 | −115.7 | −139.6 |
| 800 µs raised-cosine | −101.5 | −138.8 | −162.8 |

The numbers depend on where the offset falls relative to the ramp's spectral nulls, so compare trends, not single entries. The ramp only has to be long compared with the inverse of the channel spacing you must protect. A 25 kHz-spaced neighbour needs a ramp of order 100 µs or more; the SX126x's 10 µs default is fast. The real PA adds its own nonlinearity during the ramp (AM–PM as it passes through compression), so measure the result with a spectrum analyser in zero-span or channel-power mode.

**(d) Coupler directivity limits VSWR detection.** The "reflected" port of a coupler of directivity D also receives a leakage of the forward wave $\varepsilon=10^{-D/20}$ at an unknown phase. That leakage adds vectorially to the true reflection (§C):

| Directivity | true 2:1 (\|Γ\| = 0.333) reads | true 3:1 (0.5) reads |
|---|---|---|
| 15 dB | 1.37 – 3.09 | 1.95 – 5.21 |
| 20 dB | 1.61 – 2.53 | 2.33 – 4.00 |
| 30 dB | 1.86 – 2.15 | 2.76 – 3.27 |

A microstrip coupler on FR-4 has only 6–11 dB of directivity ([couplers Ex. 6](couplers-dividers-combiners.md#example-6--10-db-and-20-db-microstrip-couplers-why-directivity-is-poor)). It is good enough to detect an open or short ($|\Gamma|$ ≈ 1 reads > 0.7) but not to trip reliably at 2:1. For a threshold that must catch a true 3:1, choose a coupler with D ≥ 25–30 dB, or calibrate the leakage vector at a known good load and subtract it.

**(e) What a mismatch does to the device.** Model a class-B current source with load line $R_{opt}=V_m^2/2P$ ($V_m=V_{DD}-V_k$), driven so that its fundamental current would be $I_1=V_m/R_{opt}$. If $|Z|>R_{opt}$ the voltage would exceed $V_m$, so the device saturates and the current falls to $V_m/|Z|$. Then $P_{out}=\tfrac12I^2\text{Re}Z$, $P_{DC}=V_{DD}(2I/\pi)$ and $P_{diss}=P_{DC}-P_{out}$. Sweeping the reflection phase (§D) for $V_{DD}$ = 7.5 V, $V_k$ = 0.5 V, 2 W ($R_{opt}$ = 12.25 Ω, η = 73 %):

| VSWR | worst $P_{diss}$ | × matched | min $P_{out}$ | drive would force $V$ up to |
|---|---|---|---|---|
| 1.5 | 1.40 W | 1.9 | 1.33 W | 1.5 $V_m$ |
| 2 | 1.73 W | 2.4 | 1.00 W | 2 $V_m$ |
| 3 | 2.06 W | 2.8 | 0.67 W | 3 $V_m$ |
| 10 | 2.53 W | 3.5 | 0.20 W | 10 $V_m$ |
| ∞ (open/short) | 2.73 W | 3.7 | 0 | — |

Two failure mechanisms follow. *Thermal:* on the low-impedance or reactive side, current flows at full value while little power leaves, so dissipation approaches the whole DC input. *Voltage:* on the high-impedance side the device saturates, and drain voltage peaks are set by the stored energy of the matching network and by harmonics. LDMOS and GaN parts quote ruggedness (survives 65:1 at stated power and supply; [PA page](power-amplifiers.md#example-1--a-2-w-433-mhz-pa-with-an-ldmos-transistor)), but the board's thermal design must handle the 3–4× dissipation for as long as the fault lasts.

**(f) Voltage-mode class D.** A complementary pair (or bridge) switches the output node between $V_{DD}$ and 0. A series-resonant filter passes only the fundamental of the square wave, of amplitude $\frac{2}{\pi}V_{DD}$, so the current is $I_1=\frac{2V_{DD}}{\pi(R+R_{on})}$. Then $P=\tfrac12I_1^2R$, the conduction loss is $\tfrac12I_1^2R_{on}$, and $\eta=R/(R+R_{on})$. ngspice (7 MHz, 12 V, R = 10 Ω, $R_{on}$ = 0.2 Ω, $Q_L$ = 5): 2.807 W vs 2.805 W theory, η = 98.04 % vs 98.04 % (§F). **Capacitive switching loss:** every transition charges or discharges the switch-node capacitance through a switch, losing $\tfrac12CV^2$ per edge, two edges per cycle: $P_C=CV_{DD}^2f$. 200 pF at 12 V and 7 MHz gave 0.201 W simulated vs 0.202 W theory, cutting η to 91.6 %.

**(g) Current-mode class D (CMCD).** Two switches each have an RF choke from $V_{DD}$, with a parallel RLC tank between the drains. The switches steer the constant choke current $I_{DC}$ alternately, so the tank sees a square current and develops a sinusoidal voltage. Each drain is 0 while its switch is on and a half-sine while it is off. Because the choke's average voltage is $V_{DD}$, the half-sine peak is $\pi V_{DD}$. The differential fundamental is $\pi V_{DD}$, so $P=\pi^2V_{DD}^2/2R$. The conduction loss is $I_{DC}^2R_{on}$ with $I_{DC}=P/V_{DD}$, so $\eta=1/(1+\pi^2R_{on}/2R)$, and the on-voltage reduces the swing so that $P\to P_{ideal}\eta^2$. ngspice (7 MHz, 12 V, R = 20 Ω differential, $Q_L$ = 10): 32.27 W = $35.53\times0.953^2$, η = 95.30 % vs 95.30 % theory, drain voltage at turn-on ≈ 1 V (near zero-voltage switching). With 200 pF on each drain absorbed into the tank (tank C reduced by 100 pF), η stayed at 95.2 % (§F). That is the CMCD advantage: the device capacitance becomes part of the tank. The cost is a drain voltage of π × $V_{DD}$ (37.7 V from 12 V), which sets the device breakdown requirement.

**(h) Duty-cycled heating.** A one-pole thermal model, $\tau_{th}\dot T_j=T_a+P_d\theta_{ja}\cdot\text{on}(t)-T_j$, with 3 W dissipated while transmitting, 25 °C/W, τ = 5 s and 40 °C ambient, gives (§G): 1.5 s on / 15 s period → peak 60.5 °C (duty-average estimate 47.5 °C); 1.5 s / 3 s → 83.1 °C vs 77.5 °C; continuous → 115 °C. When packets are as long as the thermal time constant (SF12 packets last seconds), the peak, not the average, is what reaches the thermal-shutdown threshold.

### Level 3 — practice and system aspects
- **ALC on linear (SSB/data) transmitters.** On an HF rig the external amplifier feeds back an ALC voltage that throttles the exciter's drive. This is fine as a slow peak limiter, but any gain change inside the envelope bandwidth is amplitude modulation of the signal. For AFSK, PSK31, FT8 or any data mode sent through an SSB transmitter, adjust the audio drive so that ALC never acts. Otherwise the ALC adds distortion and IMD sidebands that look like splatter. LoRa/FSK are constant-envelope, so their power control can be slow and set once per packet. LoRa chips have no closed-loop ALC: the SX126x sets power open-loop (SetTxParams), and modules such as the E22 add an external PA whose output varies with supply and temperature by a dB or two.
- **Where to sense.** Sense after the harmonic filter and before the antenna, so that the measured power is what is radiated and VSWR includes the filter. Use RMS detectors for non-constant envelopes ([detectors](detectors-and-power-meters.md)). For VSWR, sense forward and reflected separately with a dual-directional coupler.
- **Protection architecture, from cheapest to best:**
  1. Rely on device ruggedness, a big heat sink and a fuse.
  2. Detect reflected power and fold back.
  3. Shut down and latch on severe VSWR.
  4. Fit an isolator: a circulator plus load rated for the full forward power. It holds the PA load near 50 Ω whatever the antenna does, and it also cuts transmitter intermodulation ([circulators](circulators-isolators.md), [co-site](co-site-interference-and-transmitter-intermod.md)).
  On a rocket, antenna damage at separation, deployment or landing is likely, so either buy a rugged PA module or add foldback.
- **Neutralisation.** A transistor's (or tube's) feedback capacitance $C_{gd}$/$C_{re}$ couples output to input. In a high-gain tuned PA that can oscillate. *Neutralisation* injects an equal, anti-phase current from the output, e.g. through a small capacitor from the opposite end of a centre-tapped output transformer, so the net feedback cancels. Modern solid-state PAs mostly use resistive stabilisation and low-feedback devices instead ([stability](amplifier-stability-and-biasing.md)).
- **Linear vs saturated operation (the old "SSB/FM" switch).** A VHF amplifier biased class C (no idle current) is efficient for FM but distorts SSB and data. The switch adds class-AB bias for linear modes and removes it for FM. A LoRa PA can always run saturated ([PA classes](power-amplifiers.md#level-1--definitions)).
- **T/R sequencing and hot switching.** Relay contacts that open or close while carrying RF arc, pit and weld. The interruption also hits the PA with a momentary open circuit, and an unprotected receiver may be exposed to the full PA output for the contact transit time. The sequence is:
  1. PTT.
  2. Disable the RX LNA (bias off) and switch it to bypass.
  3. Energise the T/R relay.
  4. Wait for the maximum operate time plus bounce: coax relays like the CX-140D are 15 ms typical, CX-600NC 20 ms maximum, small RF relays 2–6 ms [7].
  5. Enable PA bias.
  6. Ramp the RF.

  On release, reverse the order and also wait for the relay's release time (10–15 ms typical for coax relays) before re-enabling the LNA. A PIN or SOI switch ([switches](rf-switches-attenuators-limiters.md)) switches in microseconds, which removes most of the delay, but its power and linearity limits apply.
- **Bias sequencing.** Depletion-mode GaN and GaAs pHEMTs conduct at $V_{GS}$ = 0. Apply negative gate bias (pinch-off) *before* drain voltage, raise the gate to the quiescent point, apply RF last, and power down in reverse. Bias controllers with negative charge pumps and sequencing (e.g. HMC920-class) automate it ([biasing Ex. 8](amplifier-stability-and-biasing.md#example-8--gan-hemt-turn-on--turn-off-sequence)). Enhancement LDMOS and SiGe/CMOS PAs need no negative rail but still want RF off until bias is stable.
- **Thermal shutdown.** Integrated PAs and FEMs often include an over-temperature cut-out with hysteresis; thresholds are vendor-specific, so check the data sheet. Treat it as a last line of defence. Design for the *peak* junction temperature of the longest packet, (h).
- **Class D at RF.** Voltage-mode class D works up to some tens of MHz with discrete MOSFETs, e.g. 13.56 MHz ISM, HF transmitters and induction heating, where $CV^2f$ stays small. At UHF the switch-node capacitance kills efficiency. A 20 pF, 7.5 V node at 433 MHz loses 0.49 W, a quarter of a 2 W output (§F). Current-mode D and class E absorb the capacitance and are the UHF switching choices. In CMOS, "digital" or switched-capacitor PAs are class-D arrays whose segments are switched on and off to form polar transmitters at GHz frequencies ([transmitter architectures](transmitter-architectures.md)).

### Level 3 — choosing a protection scheme
| Scheme | What it protects against | Response time | Cost / loss | Weak point |
|---|---|---|---|---|
| Rugged device only (e.g. LDMOS rated > 20:1) | breakdown at high VSWR | instant (device physics) | none | dissipation still 3–4× (§D); needs heat sink for the fault duration |
| Reflected-power foldback (coupler + detector + MCU/comparator) | dissipation and voltage, partially | 1 µs (comparator) – 100 µs (firmware) | 0.1–0.3 dB coupler loss | directivity error (§C); firmware crash |
| Latched shutdown on severe VSWR | everything, by stopping TX | as above | link lost until reset | a transient (plume, landing) kills telemetry |
| Isolator / circulator + load | all load-pull effects, reverse IMD | instant | 0.3–0.6 dB, size/mass, load must take full power | narrowband; magnets near magnetometers |
| Drain-current limit / fuse | thermal runaway, shorts | ms (fuse: s) | small | does not catch high-Z (voltage) faults |
| Thermal shutdown | over-temperature | thermal τ (s) | none | acts after damage may have started; a last resort |

For a flight vehicle the usual answer is a rugged PA module plus firmware foldback that *reduces* power rather than latching off. Telemetry during a fault matters more than full power. On a ground station with a 25–100 W PA, add a hardware comparator trip and consider an isolator.

## Design equations & rules of thumb

| Quantity | Equation | Typical numbers |
|---|---|---|
| ALC τ | $1/(K_vK_dK_IS)$ | S = 1 → 1 ms; S = 0.37 (1 dB below Psat) → 2.7 ms |
| Ramp needed | $t_r\gtrsim$ several × 1/(channel spacing) | 25 kHz → ≥ 100–200 µs raised-cosine |
| VSWR reading band | $\|\Gamma\|\pm10^{-D/20}$ | D = 20 dB: true 3:1 → 2.33–4.0 |
| Foldback | $P_{fwd}=\min(P_{set},P_{r,max}/\|\Gamma\|^2)$ | 2 W, 0.5 W limit: open → 0.5 W |
| Worst mismatch dissipation | → $P_{DC}$ as VSWR → ∞ | 3:1: 2.8× matched |
| VMCD | $P=\frac{2V^2R}{\pi^2(R+R_{on})^2}$, $\eta=\frac{R}{R+R_{on}}$ | 12 V, 10 Ω: 2.8 W, 98 % |
| Hard-switching loss | $CV^2f$ | 200 pF, 12 V, 7 MHz: 0.20 W |
| CMCD | $P=\frac{\pi^2V^2}{2R}\eta^2$, $\eta=\frac{1}{1+\pi^2R_{on}/2R}$, $V_{pk}=\pi V_{DD}$ | 12 V, 20 Ω: 32 W, 95 %, 37.7 V |
| Relay delay | operate + bounce + margin | coax relay: 20–25 ms before RF |
| Duty-cycled $T_j$ | one-pole RC with $\tau_{th}$ | long packets → peak ≫ average |

## Worked examples

### Example 1 — Closed-loop power control for an external 2 W, 433 MHz PA
Take an E22-class driver followed by a 2 W LDMOS stage, a 40 dB sampling coupler and an AD8307 (25 mV/dB). The DAC sets the reference and an op-amp integrator drives a dB-linear attenuator at 20 dB/V before the PA. For τ = 1 ms in the linear region, $K_I$ = 2000 s⁻¹ (R = 50 kΩ, C = 10 nF). Run at a +32 dBm set point, 1 dB below the stage's $P_{sat}$, and τ grows to 2.7 ms, which is still fine for once-per-packet levelling. Clamp the integrator at the attenuator setting that gives about 2 dB compression, so a low battery cannot wind the loop into hard saturation (§A). Settle the loop during the LoRa preamble or with a dummy carrier, then *hold* the control voltage during the packet.

### Example 2 — Choosing SX126x RampTime
The chip's ramp options are 10, 20, 40, 80, 200, 800, 1700 and 3400 µs [1]. Neighbouring channels at a launch site may be 25–100 kHz away. The table in (c) shows that 10 µs leaves the +100 kHz key-click at about −58 dBc in 10 kHz, while 200 µs pushes it below −110 dBc. The cost is negligible: a 200 µs ramp against an SF9 symbol of 4.1 ms. Choose ≥ 200 µs unless timing is critical, and verify with a spectrum analyser in max-hold over many packets.

### Example 3 — Setting a VSWR trip with a real coupler
The goal: trip at a true 3:1 without false trips at a true 2:1. With D = 20 dB the 3:1 reading can be as low as 2.33:1 and the 2:1 reading as high as 2.53:1, so the ranges overlap and no single threshold works. With D = 30 dB, 3:1 reads 2.76–3.27 and 2:1 reads 1.86–2.15, so a threshold at 2.5:1 separates them (§C). Alternatively calibrate: with a known good 50 Ω load, record the complex leakage (an I/Q or gain-phase detector is needed) and subtract it. Or use a magnitude-only threshold at 2:1 and accept false trips when the antenna is merely detuned by rocket proximity.

### Example 4 — What the PA sees when the whip breaks off
A 2 W, 7.5 V class-AB stage dissipates 0.73 W normally. A broken quarter-wave whip can present anything from a short to an open at the PA, depending on cable length. Worst case is 2.73 W of heat (3.7×) at zero output, or a drain trying to swing 10× its limit at high VSWR (§D). Through a foldback set to 0.5 W reflected the forward power drops to 0.5 W and dissipation falls accordingly. With an isolator, the PA sees about 1.6:1 or better whatever the antenna does, but the isolator's load must absorb up to 2 W ([circulators Ex. 1](circulators-isolators.md#example-1--protecting-a-2-w-433-mhz-pa-from-a-broken-antenna)).

### Example 5 — Ground station with a masthead LNA and a relay-switched PA
The chain: a 433 MHz transceiver, a 25 W PA, a CX-140D-class coax relay (15 ms typical pull-in, 10 ms drop-out [7]) and a masthead LNA with its own bypass relay. The sequencer:
- t = 0: PTT.
- t = 1 ms: LNA bias off and LNA relay to bypass.
- t = 2 ms: T/R relay energised.
- t = 25 ms: (2 + 20 ms maximum operate + 3 ms bounce) PA bias on.
- t = 26 ms: RF ramp (200 µs).

On release: RF ramp-down → PA bias off → wait 1 ms → relays released → after 15–20 ms, LNA bias on. Start the LoRa packet only after t = 26 ms, i.e. the MCU waits on the sequencer's "ready" line before commanding TX. The script's timeline check (§E) flags any RF before relay settling.

### Example 6 — Why not class D at 433 MHz
VMCD at 433 MHz with a 2 W, 7.5 V device whose output capacitance is ≈ 20 pF: $CV^2f$ = 0.49 W lost before any conduction loss, plus gate-drive power for a complementary pair at 433 MHz. Class E (shunt capacitor absorbed; [PA Ex. 3](power-amplifiers.md#example-3--class-e-at-433-mhz-component-values)) or CMCD absorb that capacitance into the network, and harmonic-tuned class AB is the common practical answer. At 7 MHz the same 200 pF costs only 0.2 W of a 2.8 W output (§F).

## Practical notes
- **Build the coupler-detector pair first and test it with a known mismatch:** a 25 Ω or 100 Ω load (2:1), an open and a short, rotated through a length of cable. Check that the reflected reading tracks the known value over all phases before trusting the trip.
- **Detection speed:** log detectors respond in about 10 ns – 1 µs ([detectors](detectors-and-power-meters.md)). Firmware foldback through an MCU ADC is typically 10–100 µs. Hardware comparators that pull the PA enable line are faster and survive firmware crashes.
- **Ramp and ALC interplay:** freeze the ALC integrator during ramps, otherwise it fights the ramp.
- **Relay life:** never hot-switch. A relay rated for 1 kW cold-switched may be rated for only a few watts hot-switched.
- **Sequencer failure modes:** a stuck relay, loss of negative gate bias in a GaN PA, or brown-out during TX. A hardware interlock (gate-bias-OK signal enabling the drain supply) is better than firmware ordering alone.
- **Thermal measurement:** a thermocouple on the PA tab during a continuous-carrier test at full power, plus a duty-cycled test matching the flight packet schedule. Check margins for 50–60 °C on a launch pad in the sun.
- **Class-D construction (HF):** gate drive with very short edges and a defined dead time; bridge topologies to double the swing; a low-inductance switch-node layout. The series-resonant output filter doubles as the harmonic filter but usually needs another low-pass stage for spectral purity.

- **ALC / power-control bench test:**
  1. Put a calibrated attenuator and power meter on the output, with a spectrum analyser on a coupled port.
  2. Step the set point over the full range in 1 dB and 10 dB steps. Log the control voltage and output: check the settling time at both ends of the range (the compression slope changes τ, §A).
  3. Lower the supply to the minimum battery voltage and command full power. The loop must clamp (no wind-up) and recover cleanly when the set point drops.
  4. Repeat into a 2:1 and a 3:1 load at several cable lengths. Check that foldback acts and the loop stays stable.
  5. Key the transmitter repeatedly with max-hold on the analyser and confirm the ramp keeps key clicks below the mask.

## Common mistakes & misconceptions
- *"ALC improves linearity."* It holds average power. Acting within the modulation bandwidth, it *adds* distortion.
- *"If the loop is stable at low power it is stable at full power."* Loop gain changes with compression slope; check both ends, including the detector filter.
- *"VSWR protection with a microstrip coupler is accurate."* With 6–15 dB directivity it can only tell matched from grossly mismatched.
- *"A high VSWR just reduces output power."* It also moves the device to a load where dissipation or voltage stress is several times higher.
- *"Key up the PA and the relay together; it's only milliseconds."* Contact arcing and receiver exposure happen in exactly those milliseconds.
- *"Class D is just a more efficient class E."* VMCD loses $CV^2f$ in its device capacitance; class E and CMCD are designed around that capacitance.
- *"The datasheet efficiency holds at any duty cycle."* Self-heating lowers gain and efficiency during long packets; plan for the hot case.

## How to simulate / verify
- `python3 tools/verify/rf2_pa_control.py` (≈ 3 s; requires ngspice; ALL PASS) covers: §A ALC on a Rapp PA, τ vs compression, wind-up and clamp; §B ramp spectra for rectangular, linear and raised-cosine ramps; §C VSWR reading bounds vs directivity and the foldback law; §D mismatch dissipation and voltage sweep; §E sequencing timeline check; §F ngspice VMCD (ideal and with 200 pF), CMCD (ideal and with 200 pF absorbed), UHF $CV^2f$ scaling; §G duty-cycled junction temperature.
- For a real PA, use vendor nonlinear models in a harmonic-balance or transient simulator with load-pull to map dissipation and drain voltage across the VSWR circle. Bench test with a mechanical stub tuner or a set of mismatched loads ([17 RF power](../17-test-measurement/rf-power-measurement.md)).

## Open questions / gaps
- Relay timings are vendor figures obtained from search summaries (Tohtsu CX-140D/CX-600NC, Teledyne RF3xx); confirm on the actual part's data sheet.
- The class-B mismatch model ignores knee softness, harmonics, thermal effects and package parasitics. Real worst-case phases and peaks need load-pull or harmonic-balance data.
- The thermal-shutdown thresholds of the EBYTE E22/E220 PAs are not published.
- ALC voltage conventions on amateur HF transceivers and amplifiers (range, polarity) were not re-checked against the ARRL Handbook this session.
- The ramp-spectrum table models only the envelope of an unmodulated carrier. The real splatter of a LoRa/FSK burst also includes the PA's AM–PM during the ramp and the modulation's own spectrum; measure it.
- The protection-scheme table is a qualitative synthesis; response times are typical orders of magnitude, not measured values for specific parts.
- CMCD was simulated with ideal switches and chokes; gate-drive power and finite switching speed (which dominate at UHF) are not modelled.
- No measured data were taken on the team's E22/E220 modules into mismatched loads; a 2:1/3:1/open/short test at several cable lengths is recommended before flight.

## Sources
1. Semtech, *SX1261/2 data sheet*, §13.4.4 SetTxParams (power, RampTime 10–3400 µs). https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet; read)
2. S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech House, 2006 (load line, mismatch behaviour, switching modes). (textbook; background)
3. F. H. Raab et al., "Power amplifiers and transmitters for RF and microwave," *IEEE Trans. MTT* 50(3), 814–826, 2002 (class D voltage/current mode, class E, control). (peer-reviewed)
4. A. Grebennikov, *RF and Microwave Power Amplifier Design*, 2nd ed., McGraw-Hill, 2015, chapters on switching-mode (class D/E) PAs. (textbook; cited)
5. ARRL, *The ARRL Handbook*, transmitter/amplifier chapters: ALC, T/R sequencing, ruggedness, neutralisation. (handbook; background, not re-read)
6. Analog Devices, AD8307/AD8318 data sheets (log detectors, controller mode) as summarised in [detectors](detectors-and-power-meters.md); HMC920 bias controller as cited in [biasing](amplifier-stability-and-biasing.md). (datasheets)
7. Tohtsu CX-140D (15 ms pull-in, 10 ms drop-out, typical) and CX-600NC (20 ms / 15 ms max) coaxial relay data; Teledyne RF341/RF300/RF303 (2/4/6 ms max operate). https://www.wimo.com/en/cx-140d, https://www.teledynedefenseelectronics.com/relays/Datasheets/rf341.pdf (vendor data; via search summaries)
8. `tools/verify/rf2_pa_control.py` (this KB).
