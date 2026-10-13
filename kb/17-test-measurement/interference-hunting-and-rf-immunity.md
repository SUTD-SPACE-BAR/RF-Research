---
title: Interference hunting and RF immunity — finding noise sources (portable SDR, H-field loop, attenuators, DF, body fade), why RCDs/GFCIs trip and Ethernet, audio and sensors get upset, motors and switch-mode supplies as noise sources, ferrites and how to prove a fix, and transmitter RF inside a rocket av-bay
domain: 17-test-measurement
slug: interference-hunting-and-rf-immunity
tags: [rfi, emi, interference-hunting, qrm, noise-floor, near-field-probe, h-field-loop, direction-finding, body-fade, offset-attenuator, rcd, gfci, afci, y-capacitor, ethernet, common-mode, ferrite, choke, threshold-effect, smps, motor-noise, shine, rein, gsm-buzz, immunity, iec-61000-4-3, av-bay, pyro, magnetometer]
prerequisites:
  - spectrum-analyzers.md
  - sdr-as-test-equipment.md
  - ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md
related:
  - oscilloscopes-and-probing-for-rf.md
  - bench-measurement-recipes.md
  - rf-bring-up-debug-playbook.md
  - antenna-range-ota-testing.md
  - ../14-sdr-dsp/signal-identification-and-spectrum-survey.md
  - ../14-sdr-dsp/sdr-front-end-protection-and-filtering.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../13-pcb-rf-layout-emc/shielding-and-isolation.md
  - ../19-regulations-safety/lab-safety-esd-high-power.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Interference hunting and RF immunity

## Questions this page answers
- How do I systematically find what is making noise in my receiver (QRM, "RFI")?
- Can I hunt RFI with a tinySA or an RTL-SDR, and what else do I need?
- What is the "body fade" trick, and why do attenuators stop working when I get close to a transmitter?
- How do I find power-line, PLC, switch-mode-supply or LED noise?
- Why does my RCD/GFCI trip, and can radio interference cause it?
- Ethernet is transformer-coupled, so can ferrites even matter? Where along the cable should the ferrite go?
- Does an iperf throughput test prove that a ferrite fixed my RFI?
- How do I stop a brushed motor or an ignition system from upsetting my electronics?
- Why did my Arduino reset next to a microwave oven, and why did GSM phones buzz in speakers?
- How can one faulty TV knock out a village's broadband?
- Will my own 2 W telemetry transmitter upset the barometer, IMU, magnetometer or pyro channels in the av-bay, and how do I test for that?

## TL;DR
- **Hunt in four steps: characterise, localise, confirm, fix.**
  1. *Characterise* the noise: its frequency span, harmonic spacing, AM buzz at 100/120 Hz, and time pattern.
  2. *Localise*: cut the power to the whole house while listening on a battery receiver, then go breaker by breaker; outdoors, walk with a portable receiver and a directional antenna.
  3. *Confirm*: close in with an H-field loop, and unplug the suspect.
  4. *Fix* it at the source.
- **Distance laws tell you where you are.** Deep in a source's near field ($r \ll \lambda/2\pi$), halving the distance raises the signal by about **18 dB**. In the far field it raises it by 6 dB (`e10_rfi.py`). At 7 MHz, λ/2π is 6.8 m; at 433 MHz it is 11 cm.
- **Close in, plain attenuators fail**, because the signal leaks into the receiver case. A 1 W fox at 10 m is 67 dB above S9 at 146 MHz. Use the **body fade** (hold the receiver to your chest; the null points *away* from the source), tune to the **3rd harmonic** (≈ 40–60 dB down), or use an **offset attenuator** (20–100 dB) [1].
- **RCD/GFCI nuisance trips** usually have one of two causes:
  - *Leakage*: Y-capacitor leakage adds up (4.7 nF at 230 V/50 Hz = 0.34 mA per device). BS 7671 limits standing leakage to 30 % of IΔn (9 mA for a 30 mA RCD), because RCDs may trip anywhere from 50 % to 100 % of IΔn [2]. Mains transients through the same capacitance add to this [2].
  - *Direct RF upset* of a GFCI or AFCI's detector electronics by a nearby transmitter. ARRL's first fix is to replace the device with a less susceptible unit [3].
- **Ferrites work by series impedance, and only above a threshold.** A choke reduces current by $|Z_{loop}+Z_{choke}|/|Z_{loop}|$. On a 300 Ω common-mode loop, 300 Ω of resistive choke gives 6 dB and 3 kΩ gives 21 dB. A reactive choke can even *increase* current by resonating with the loop. Detected interference falls twice as fast in dB, because detection is square-law [4].
  - At HF you need **turns**: 9 turns of Ethernet cable on a 2.4-inch #31/#43 toroid give ≥ 2 kΩ at 10–30 MHz [4].
  - At VHF you need ≥ 500–1000 Ω (several clamp-ons).
- **Ethernet radiates and picks up in common mode**, even though it is transformer-coupled, because the line drivers have poor common-mode balance [4]. **Throughput tests (iperf) do not prove an RFI fix.** The data link has a large SNR margin plus CRC/retransmission, so it is unaffected by noise that ruins a nearby HF receiver. Verify fixes on the *victim receiver's noise floor* with enough averaging. A 1 dB change at 3σ needs about 340 averaged power samples per reading.
- **Rocket av-bay**:
  - A 2 W 433 MHz dipole gives **≈ 99 V/m at 10 cm** (≈ 10 V/m at 1 m). Commercial immunity tests use 3–10 V/m (IEC 61000-4-3 levels 2–3), so sensors next to the antenna are tested 20–30 dB below what they will see.
  - PA supply bursts (≈ 1 A) on a separated wire pair produce **≈ 10 µT at 2 cm**, about a quarter of the Earth's field, right at the magnetometer.
  - Test with the transmitter keyed in flight configuration while logging every sensor, and protect pyro lines per [EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md) and [HERO](../19-regulations-safety/lab-safety-esd-high-power.md).

## Intuition (no math)
Interference needs three things: a **source** (something switching fast or transmitting), a **path** (conduction along wires, or radiation, usually via a cable acting as an antenna), and a **victim** (a receiver, or any circuit with a non-linear junction that can rectify RF). Fixing any one of the three works. Fixing the source fixes every victim at once, so hunting is worthwhile.

Most "mystery" noise is **common-mode** current on cables: the whole cable, all conductors together, carrying RF relative to its surroundings. Twisted pairs, transformers and shields do nothing for this current, because it flows on the outside of everything. A ferrite choke works by putting a series impedance in that common-mode path. Like any series resistor, it does little until it is comparable to the rest of the loop's impedance. That is why one clip-on bead "does nothing" at HF and nine turns through a big toroid works.

The victim side is just as simple. A transistor junction or a protection diode is a detector. It turns an RF burst into a DC step or an audio-frequency buzz at the burst rate: the 217 Hz "GSM buzz", or an offset that follows the LoRa packet rate. RF immunity means keeping RF out of the junctions, using filters at the pins and shields and chokes on the cables, and keeping transmit antennas away from them.

Finding a source is a game of "warmer, colder". The trick is to keep the receiver from being overloaded as you get close, and to know when you have entered the near field, where the signal climbs very steeply with every step.

## The math

### Level 1 — dB bookkeeping you need in the field
- Received level change with distance: far field $\Delta P = 20\log(r_1/r_2)$ (6 dB per halving); near field of a small loop or dipole source, $60\log(r_1/r_2)$ (18 dB per halving). The boundary is at $r \approx \lambda/2\pi$.
- Field strength from a transmitter of power $P$ (W) and gain $G$ (linear) at distance $r$ (m), far-field: $E = \sqrt{30PG}/r$ (V/m).
- Leakage current of a capacitor $C$ to earth at mains voltage $V$, frequency $f$: $I = 2\pi f C V$.
- Choke attenuation: $A = 20\log_{10}\left|\frac{Z_{loop}+Z_{choke}}{Z_{loop}}\right|$ dB.
- Detected (rectified) interference is square-law, so it changes **twice** as many dB as the RF current.

### Level 2 — derivations

**Near-field distance law.** A small loop's fields contain terms in $1/(kr)$, $1/(kr)^2$ and $1/(kr)^3$, with $k = 2\pi/\lambda$ ([near/far field](../02-electromagnetics/near-field-far-field.md)). For $kr \ll 1$ the $1/(kr)^3$ term dominates. Halving $r$ multiplies $|H|$ by 8, which is +18 dB. For $kr \gg 1$ only $1/(kr)$ survives: +6 dB. The script evaluates the full expression at 7, 30, 146 and 433 MHz (18.2 dB and 6.0 dB). Practical use: if a 2× step closer gives about +18 dB, you are within λ/2π of the radiator. At HF that means within a few metres, so the source is in *this* house or on *this* pole.

**Close-in overload.** Free-space loss $20\log(4\pi d f/c)$ at 146 MHz is 35.7 dB at 10 m. A 1 W fox therefore delivers −5.7 dBm, 67 dB above S9 (−73 dBm). A handheld's case and wiring typically provide much less isolation than that from the field around it. Signal leaks *around* an external attenuator, so beyond a few steps the S-meter stops responding [1]. An **offset attenuator** solves this: it mixes the strong signal with a local oscillator and you listen to the weak product a few MHz away, where the case leakage is at the wrong frequency. HomingIn describes about 4 MHz offset and 20–100 dB range [1]. The **3rd-harmonic trick** works the same way: the fox's own harmonic is 40–60 dB weaker [1].

**Why RCDs trip on "interference".** An RCD trips when the vector sum of line and neutral currents (the residual current) exceeds its threshold. Anything that sends current to earth by another route contributes:
- **Standing leakage.** Every EMI filter's Y capacitor from line to protective earth passes $I = 2\pi fCV$: 0.34 mA for 4.7 nF at 230 V/50 Hz, 0.16 mA for 2.2 nF. IEC 61008 lets a 30 mA RCD trip anywhere from 15 to 30 mA. BS 7671 therefore limits *standing* protective-conductor current to 30 % of IΔn, i.e. 9 mA [2]. That is reached by 27 devices with 4.7 nF each, or fewer with bigger filters, plus cables and heating elements.
- **Transients.** A mains spike charges the same capacitance much faster, and the current scales with dV/dt. BEAMA's worked example: a 1 kV pulse with 50 µs rise, treated as about 5 kHz, needs only **1.6 nF** of capacitance to earth to send 50 mA [2]. Contactors, motor switching, discharge-lamp ballasts and lightning-induced surges kilometres away are all documented causes [2]. Surge suppressors from line to neutral do not help, because the current that trips is the one to *earth* [2].
- **RF upset of electronic detectors.** Voltage-dependent RCDs, GFCIs (US electronic devices, which trip at about 4–6 mA) and AFCIs (which look for HF "arc noise" by design) contain amplifiers. RF on the wiring can be rectified in them and read as a fault [3]. AFCIs are especially exposed, because noise on the wiring is literally what they are built to detect.

**Common-mode chokes and the threshold effect.** Model the common-mode path as a source driving a loop of impedance $Z_{loop}$: cable as antenna, plus the stray return through power supplies and "ground". The current is $I = V/Z_{loop}$; with a choke, $I' = V/(Z_{loop}+Z_{choke})$. With $Z_{loop}$ = 300 Ω resistive (K9YC's example [4]):
- 100 Ω → 2.5 dB; 300 Ω → 6.0 dB; 1 kΩ → 12.7 dB; 3 kΩ → 20.8 dB (`e10_rfi.py`).
- If the loop is capacitive, say 50 − j300 Ω, a lossless inductive choke of +j200 Ω *reduces* $|Z|$ and raises the current by 8.7 dB. Lossy (resistive) chokes such as #31/#43 near their resonance avoid this, which is why resistive impedance is what counts [4].
- Below self-resonance, choke impedance grows roughly as $N^2$ (turns through the core). Interwinding capacitance then sets an upper resonance that moves down as turns are added [4]. That is why one core with many turns covers HF, and several single-pass clamp-ons cover VHF.
- **Where to put it.** The choke must sit in the path of the common-mode current, where it adds impedance to the loop. That usually means at the noisy device's port, or at the victim's input, not mid-cable where the current may be at a standing-wave minimum anyway. A long cable often needs chokes at both ends [4].

**Verifying a fix statistically.** A spectrum analyser or SDR power reading of noise is exponentially distributed per bin. Averaging $K$ samples gives a dB reading with standard deviation $\approx 4.34/\sqrt{K}$ dB (Monte-Carlo confirms: 1.39, 0.43, 0.14 dB at K = 10, 100, 1000). A single sample is biased by −2.5 dB, the [log-averaging bias](spectrum-analyzers.md). A before/after difference has $\sqrt2$ times that spread. Detecting a 1 dB improvement at 3σ needs $K \gtrsim 2(3\times4.34)^2 \approx 340$ samples per reading: keep RBW, gain and antenna fixed, and log a few seconds of averaged FFT frames.

**Own-transmitter field in an av-bay.** $E = \sqrt{30PG}/r$ for 2 W into a 2.15 dBi dipole gives 99 V/m at 10 cm, 33 V/m at 30 cm and 9.9 V/m at 1 m. A 1 W, 915 MHz dipole gives 70 V/m at 10 cm. Inside $\lambda/2\pi$ (11 cm at 433 MHz) the far-field formula is only an order-of-magnitude guide. Coupling there is reactive and depends on geometry, so *measure*. Compare IEC 61000-4-3 radiated-immunity levels of 1/3/10/30 V/m (levels 1–4, 80 MHz–6 GHz; standard as commonly quoted). A sensor module "tested to 10 V/m" sits 20 dB below what it sees 10 cm from the antenna.

**Magnetic upset of the magnetometer.** A PA drawing current $I$ in bursts on a wire at distance $r$ produces $B = \mu_0 I/(2\pi r)$: 10 µT at 2 cm for 1 A. If the return current runs in a plane 0.2 mm below the trace, the pair forms a two-wire line with $B \approx \mu_0 I h/(\pi r^2)$: 0.2 µT at 2 cm. That is 50× less, because the loop area collapses. Earth's field is about 25–65 µT. A battery lead pair routed apart past the magnetometer injects a packet-synchronous heading error. This is not RF at all, but it is the commonest "transmitter upsets my sensors" mechanism in small av-bays.

### Level 3 — direction finding and stubborn cases
- **Bearings.**
  - VHF/UHF: a small Yagi gives ±10–20°.
  - HF: a loop (or a ferrite-rod receiver at MF) gives sharp **nulls** off its axis. Nulls are sharper than peaks, so use the null.
  - Arrays and KrakenSDR: [adaptive beamforming/DOA](../12-phased-arrays/adaptive-beamforming-doa.md).
  - Multipath in streets and near fences corrupts all bearings, so take several bearings from different spots [1].
- **Go up in frequency to pinpoint.** Broadband sources such as power-line arcing, SMPS and motor commutators are audible far away at HF, where propagation is good. Their VHF/UHF components fall off fast. Switching the portable receiver to 150–450 MHz narrows the search from a street to a pole or a box (practice from the ARRL RFI literature [5]).
- **Time signatures.** Correlate the noise with clocks and events: solar inverters (daylight only), heating thermostats, a 7 am TV (example 6), electric fences (about 1 click/s), plus 100/120 Hz buzz (mains-related arcing or rectifiers) and switching-frequency harmonics (SMPS combs spaced 30–500 kHz that drift with load).
- **Impulse noise on DSL (SHINE/REIN).** VDSL uses spectrum up to about 17–35 MHz on unshielded telephone pairs. Broadband impulses from a faulty appliance couple into the pairs in common mode and convert to differential through line imbalance. The modem then retrains or drops (example 6).
- **Conducted vs radiated.** If the noise disappears when a device runs on a battery, or with a ferrite on its mains lead, the path is conducted on the mains wiring. If it persists with the mains cord choked, the device itself or its other cables radiate.

## Design equations & rules of thumb

| Quantity | Equation / rule | Typical value |
|---|---|---|
| Near-field boundary | $\lambda/2\pi$ | 6.8 m (7 MHz), 0.33 m (146 MHz), 0.11 m (433 MHz) |
| Distance law | +18 dB per halving (near), +6 dB (far) | tells you which zone you are in |
| Far-field E | $\sqrt{30PG}/r$ | 2 W dipole: 99 V/m at 0.1 m |
| Y-cap leakage | $2\pi fCV$ | 4.7 nF, 230 V, 50 Hz: 0.34 mA |
| RCD standing-leakage guidance | ≤ 30 % IΔn (BS 7671 531.3.2) | 9 mA for 30 mA RCD |
| RCD trip window | 50–100 % IΔn (IEC 61008) | 15–30 mA |
| Choke attenuation | $20\log|Z_{loop}+Z_c|/|Z_{loop}|$ | 300 Ω loop + 3 kΩ: 21 dB |
| HF Ethernet/cable choke | 7–9 turns on 2.4″ #31/#43 toroid | ≥ 2 kΩ, 10–30 MHz [4] |
| VHF choke | ≥ 500–1000 Ω (several clamp-ons) | 2 m band: about 3 cores [4] |
| Brushed motor | 0.1 µF across terminals + each terminal to case; twisted short leads [6] | — |
| Noise-floor averaging | σ ≈ 4.34/√K dB | 1 dB at 3σ (difference): K ≈ 340 |
| Magnetometer vs PA current | $\mu_0 I/(2\pi r)$; with adjacent return, $\mu_0 I h/(\pi r^2)$ | 1 A at 2 cm: 10 µT vs 0.2 µT |

**Noise signatures** (what the SDR waterfall shows; from the RFI literature [4][5] and the KB's [signal-ID page](../14-sdr-dsp/signal-identification-and-spectrum-survey.md); medium confidence):

| Source | Signature | Quick test |
|---|---|---|
| Switch-mode supply / charger / LED driver | comb of carriers at the switching frequency (30–500 kHz spacing), drifting with load; or broad "hash" | unplug; battery receiver next to it |
| Solar PV inverter / optimisers | SMPS-like comb, daylight only | correlate with sunlight; inverter off at the isolator |
| Power-line arcing (loose hardware, insulators) | broadband, 100/120 Hz buzz in AM mode, worse in dry wind, extends to UHF near the source | go up in frequency to pinpoint the pole |
| Ethernet devices | birdie clusters at fixed spots on HF/6 m (e.g. near 10.107/10.122 MHz) [4] | power off your own router and switch first [4] |
| PLC adapters (HomePlug) | OFDM blocks 2–30 MHz with notches in amateur bands | unplug the adapters |
| VDSL modem/line | wideband hiss to about 17–35 MHz | modem off |
| Brushed motors, ignition | impulsive, rate follows rpm | run the motor on a bench supply with and without caps |
| Plasma / old CRT TV, faulty appliance | broadband impulse; time-of-day pattern | the Aberhosan story (example 6) |
| Electric fence | sharp click about every second, very wideband | walk the fence line with an AM receiver |
| Your own SDR's USB/PC | comb tied to USB/PC clocks; vanishes on a laptop running on battery | [SDR test](../17-test-measurement/sdr-as-test-equipment.md): 50 Ω load test |

## Worked examples

**1. A noisy HF receiver at home.** Symptom: S7 broadband hash on 7 MHz.
1. Run the receiver on battery (laptop on battery, SDR with whip). Switch off the house's main breaker. If the noise stays, the source is outside; if it goes, restore circuits one by one.
2. Say it is on circuit 3. Unplug devices on that circuit; the noise vanishes with a phone charger.
3. Check: an H-field loop on a tinySA, 10 cm from the charger, shows a comb with about 65 kHz spacing.
4. Fix: replace the charger, or add a clamp-on #31 core with 5–7 turns of its output lead (aiming for ≥ 1 kΩ at 7 MHz).
5. Verify: noise floor before and after, same RBW and gain, K ≥ 340 frames each. Expect a 10–20 dB drop, not 1–2 dB.

**2. Ethernet birdies at 10 MHz.** Follow K9YC's design [4]:
1. Power off your own router and switch. If the birdies vanish, they are yours.
2. Wind 9 turns of the Cat-5 lead from the router onto a 2.4-inch #31 toroid (≥ 2 kΩ at 10–30 MHz) at the router end. Add a second at the far end if the cable is long.
3. With $Z_{loop}$ around 300 Ω, 2 kΩ gives about 18 dB less common-mode current. The receiver's noise reduction depends on how much of the noise this cable was radiating.
4. **Do not judge it with iperf.** The Ethernet link's SNR margin is tens of dB, with CRC and retransmission on top. A cable can radiate enough to raise an HF noise floor by 20 dB while transferring data perfectly. The Hackaday test found no throughput change with any ferrite [7], which is exactly what the physics predicts, and is not evidence that ferrites do nothing.

**3. RCD trips when a lab bench is switched on.** The bench has 12 instruments, a PC and 6 LED lamps, each with roughly 2.2–4.7 nF line-to-earth. Standing leakage: 12 × 0.34 + 7 × 0.16 ≈ 5.2 mA, within the 9 mA guidance but already a third of the 15 mA lower trip limit. Switching on a motor or a big SMPS adds a transient through the same capacitance (BEAMA: 1.6 nF suffices for 50 mA on a 1 kV/50 µs spike [2]). Fixes:
- Measure the standing leakage with a milliamp clamp around L+N [2].
- Spread the loads across RCBOs.
- Choose RCD types suited to electronic loads (Type A/F per BEAMA [2]).
- Never remove earths or Y capacitors: that is a safety hazard.

**4. A GFCI trips whenever the ground station transmits.** Some electronic GFCIs and AFCIs are susceptible to strong RF on the wiring [3]. Steps:
1. Confirm by transmitting into a dummy load (no trip) and then into the antenna (trip).
2. Move the antenna, or its feedline's common-mode current, away from the building wiring: add a feedline choke at the antenna and at the shack entry ([baluns/chokes](../08-antennas/antenna-matching-and-baluns.md)).
3. Replace the device with a newer, less susceptible model, which is ARRL's first recommendation [3].
- Do not bypass protective devices.

**5. Av-bay immunity test for the flight computer** (E22 2 W at 433 MHz, antenna 10–15 cm from the board):
- Expected field: about 70–100 V/m (far-field estimate), 20–30 dB above typical commercial test levels.
- Procedure:
  1. Assemble in flight configuration (harness, antenna, battery).
  2. Log baro, IMU, magnetometer and ADC channels for 60 s with TX off, then 60 s with TX keyed in the flight packet pattern, then 60 s with continuous carrier.
  3. Compute each channel's mean and standard deviation per phase, and cross-correlate with the TX-on gate signal.
- Pass: shifts below the sensor's noise and no resets.
- Magnetometer: check for a step synchronised with packets. That is usually supply current, not RF, so fix the routing as in Level 2.
- Pyro: dummy bridge with an RF-current indicator, procedure in [lab safety/HERO](../19-regulations-safety/lab-safety-esd-high-power.md).
- Typical fixes are in [EMC fundamentals](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md): RC filters at sensor pins, twisted pyro leads with RF bypass, a choke on the antenna coax, and keeping the antenna's radiating section away from the board.

**6. The TV that broke a village's broadband.** In Aberhosan (Wales), broadband dropped every morning for 18 months. Engineers replaced cable without success. A spectrum analyser finally caught a burst of SHINE (single high-level impulse noise) at 7 am from an old TV being switched on [8]. The lessons generalise:
- Look for time correlation.
- Hunt with a receiver, not with service tests. The line passed every test because the fault was intermittent and external.

**7. GSM buzz and its LoRa cousin.** GSM transmits 577 µs bursts every 4.615 ms, which is 216.7 Hz (`e10_rfi.py`). A rectifying junction turns the RF into a 217 Hz square wave, audible in audio amplifiers. A LoRa telemetry link sending 10 packets/s produces a 10 Hz step pattern in a sensor ADC by the same mechanism. Fix at the pin with 100 Ω–1 kΩ plus 100 pF–1 nF C0G, and a filter at the cable entry ([EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)).

## Practical notes
- **Hunting kit (about S$100–300)**:
  - battery-powered SDR or tinySA with AM demodulation;
  - a short whip, and a small directional antenna (VHF tape-measure Yagi; HF/MF loop);
  - an H-field probe loop (a few turns, 1–3 cm, on coax);
  - a step attenuator, plus an offset attenuator for close-in work;
  - a clamp-on RF current probe, or a ferrite-core current transformer made into a probe;
  - an assortment of #31 (HF) and #43/#61 (VHF/UHF) cores;
  - a notebook for times and conditions.
- **Measure first, fix second.** Record the noise floor (dBm/Hz or dBFS at fixed gain) with frequency, time and conditions before changing anything.
- **Motors and servos** (rocket fins, rotators, ground-station trackers): use 0.1 µF ceramics across the terminals and from each terminal to the case, keep leads short and twisted, route them away from signal lines, and add bulk capacitance at the electronics [6]. Brushless ESCs and servo PWM add their own switching noise: put ferrite chokes on the ESC leads.
- **Switch-mode supplies near receivers**: choose units with CISPR 32 class B compliance. Add common-mode chokes on input and output, keep the switch node small, and use linear post-regulators for the receiver's supply ([PDN](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)).
- **Microwave ovens** leak 2.45 GHz and their magnetron supplies are noisy. A sensor reset near one is usually RF rectified on a long sensor lead (filter the lead), or a supply dip.
- **Ground-station site discipline**: generator, chargers, laptops and LED floodlights should be at least tens of metres from the receive antenna. Do the noise-floor check with everything on, then off.

## Common mistakes & misconceptions
- **"Ethernet is transformer-coupled, so a ferrite cannot matter"** (D3 #518). The transformer blocks *differential* DC. The noise is *common-mode* current on the whole cable, driven by unbalanced line drivers and the device's stray coupling to ground [4]. A common-mode choke is exactly the right tool.
- **"An iperf test proves whether the ferrite worked"** (D3 #519). Throughput measures the data link, not the RF the cable radiates or picks up. Verify on the victim receiver's averaged noise floor, or with a common-mode current probe.
- **"One clip-on bead did nothing, so ferrites don't work."** It was below the threshold impedance [4]. At HF you need turns through a large #31 core, and at VHF several cores.
- **"Put the ferrite in the middle of the cable."** Put it at the source's or the victim's port, where it adds impedance to the loop that carries the current. Use both ends on long cables [4].
- **"Radio interference trips RCDs, so the transmitter is to blame."** Most RCD trips come from cumulative Y-capacitor leakage plus mains transients [2]. Direct RF upset happens mainly with electronic GFCIs and AFCIs near strong transmitters [3]. Diagnose which one with the dummy-load test.
- **"The noise is in my SDR."** Sometimes it is (USB, PC). Check with a 50 Ω load, then a battery laptop, then a short antenna, *before* hunting outside ([SDR test](sdr-as-test-equipment.md)).
- **"If the device passed EMC certification it cannot be the source."** Certification is a sample test at fixed distances. A faulty, aged or modified unit, or one 2 m from your antenna, can still wipe out a weak-signal band. CE in particular is self-declared.
- **"My sensors are rated for EMC, so the av-bay transmitter is fine."** Commercial immunity test levels (3–10 V/m) are 20–30 dB below the field 10 cm from a 2 W antenna.
- **"Use an attenuator when the S-meter pins."** Close in, the signal leaks around the attenuator through the receiver case. Use body fade, the 3rd harmonic or an offset attenuator [1].

## How to simulate / verify
- `python3 tools/verify/e10_rfi.py` (output `tools/verify/e10_rfi_output.txt`, all checks pass). It covers near-field vs far-field distance laws per band, close-in fox levels, Y-capacitor leakage and the BEAMA transient example, the choke threshold effect (resistive and resonating loops), own-transmitter fields vs IEC levels, Monte-Carlo averaging statistics for verifying a fix, the GSM frame rate, and PA-current magnetic fields with and without an adjacent return.
- Before/after noise-floor comparison from two logged SDR power arrays (same gain, RBW, antenna):

```python
import numpy as np
def floor_db(p_lin):                     # p_lin: K x Nbins linear power (FFT |X|^2) frames
    m = p_lin.mean(axis=0)               # average power per bin first, then convert to dB
    return 10*np.log10(np.median(m))     # median across bins rejects narrow carriers
def change_db(before, after):
    K = min(len(before), len(after))
    sigma = np.sqrt(2) * 4.343 / np.sqrt(K)   # std of the difference (this page, Level 2)
    return floor_db(after) - floor_db(before), sigma
# accept the fix only if |change| > 3*sigma
```

- **Make a common-mode current probe** from a split ferrite core (#43, 2–3 turns of secondary into 50 Ω on the SDR or tinySA). Clamp it around the whole cable: a rising reading means more common-mode current. Calibrate it against a known current, using a signal generator into 50 Ω through the probe, before quoting amperes.
- Ngspice: model the common-mode loop (cable as a capacitor or short antenna plus a 50–300 Ω source), sweep a choke model (R‖L‖C from the vendor's curves), and see the resonance effect ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).
- A choke's impedance can be measured on a NanoVNA with a series-through fixture ([bench recipes](bench-measurement-recipes.md)).

## Open questions / gaps
- No measured av-bay data yet. The 70–100 V/m figure is a far-field estimate inside the reactive near field. A measurement with a small calibrated E-field probe, or a dummy sensor with a diode detector, would replace it.
- UL 943 GFCI thresholds (4–6 mA) and IEC 61000-4-3 levels are quoted from common knowledge of the standards, not read from them.
- The noise-signature table is from practitioner literature (K9YC, ARRL), not peer-reviewed, and the VDSL/PLC band edges were not checked against ITU-T G.993.2 or IEEE 1901.
- Not covered here: TEMPEST and compromising emanations (D3 below the cut); LISN-based conducted-emission measurement is covered in [13 EMC § conducted and radiated pre-compliance](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#conducted-and-radiated-pre-compliance) (LISN set-up, LPDA pre-scan, budget kit).

## Sources
1. J. Moell (K0OV), "Equipment Ideas for Radio Foxhunting," HomingIn — body-fade method, offset attenuator (about 4 MHz offset, 20–100 dB, immune to case leakage), failure of resistive attenuators close in, 3rd-harmonic trick (40–60 dB). http://www.homingin.com/equipment.html (practitioner guide — anecdotal but long-standing); see also J. Moell, T. Curlee, *Transmitter Hunting: Radio Direction Finding Simplified*, TAB/McGraw-Hill, 1987. (book)
2. BEAMA, *The RCD Handbook — Guide to the Selection and Application of Residual Current Devices* (2023 ed.) — voltage-dependent vs independent RCDs, Types AC/A/F/B, unwanted tripping from transients and capacitance to earth (worked 1.6 nF example), RFI suppression capacitors, IEC 61009 ring-wave test, clamp-meter measurement of standing leakage. https://www.beama.org.uk/static/ae8fee0a-3c8c-4751-a91cad970f4133f4/BEAMA-Guide-Selection-and-Application-of-RCDs.pdf (industry guide); BS 7671:2018+A2:2022 Reg. 531.3.2 (≤ 30 % IΔn standing leakage) and IEC 61008-1 (trip between 50 % and 100 % IΔn), as summarised by the IET. (standard, secondary)
3. ARRL, "GFCI and AFCI Devices" — RF upsetting the imbalance/arc-detection circuits; replacement preferred over filtering; manufacturer cooperation on AFCI fixes. https://www.arrl.org/gfci-and-afci-devices (organisation guidance)
4. J. Brown (K9YC), *A Ham's Guide to RFI, Ferrites, Baluns, and Audio Interfacing*, Rev. 7, Jan 2019 — common-mode mechanisms, Ethernet line-driver imbalance, threshold effect and square-law detection, #31/#43 choke design (9 turns on 2.4″ toroid ≥ 2 kΩ at 10–30 MHz), VHF ≥ 500–1000 Ω rule, placement at both ends, Ethernet birdie clusters. http://audiosystemsgroup.com/RFI-Ham.pdf (expert tutorial with measured data)
5. M. Gruber (ed.), *The ARRL RFI Book*, 3rd ed., ARRL, 2010 — RFI hunting procedures, power-line noise location, appliance and SMPS signatures; and H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 — common-mode coupling, filtering and shielding theory. (books; background)
6. Pololu, "Dealing with Motor Noise" — 0.1 µF ceramic across terminals and terminal-to-case, short twisted leads, routing away from signals, bulk capacitance. https://www.pololu.com/docs/0J15/9 (app note)
7. Hackaday, "Ferrites Versus Ethernet in the Ham Shack," 17 Sep 2024 — NanoVNA test (2 ferrites × 2 turns ≈ 17 dB), iperf showed no throughput change; comment debate. https://hackaday.com/2024/09/17/ferrites-versus-ethernet-in-the-ham-shack/ (blog — anecdotal)
8. ISPreview UK, "18 Months of Village Broadband Disruption Traced to Old TV Set," Sep 2020 (also Irish Times, 22 Sep 2020) — Openreach traced SHINE at 7 am to a TV in Aberhosan. https://www.ispreview.co.uk/index.php/2020/09/18-months-of-village-broadband-disruption-traced-to-old-tv-set.html (news)
9. IEC 61000-4-3, *Radiated, radio-frequency, electromagnetic field immunity test* — test levels 1/3/10/30 V/m, 80 MHz–6 GHz (as commonly quoted); UL 943 GFCI Class A trip at 4–6 mA (as commonly quoted). (standards, not read)
10. Forum demand: Arduino forum (RCD tripping, brushed motor, microwave-oven resets, motorbike ignition, home-automation relays), Hackaday (Ethernet ferrites; SHINE), EEVblog/SOTA/YouTube RFI hunting (HB9BLA, IMSAI Guy tinySA), r/amateurradio (PS5 RFI, SMPS RFI), r/rfelectronics (GSM buzz) — `gaps/D3-forums-youtube.md` rows 43, 178, 258, 359, 383, 388, 394, 396, 436, 439, 473, 484, 518–520, 619, 625; `gaps/D2-reddit.md` rows 18, 30, 39, 77, 125, 462. (forum — anecdotal)
