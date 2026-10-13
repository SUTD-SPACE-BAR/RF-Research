---
title: RF concepts for beginners — a Level-1 tour with high-school maths (what RF is, frequency and wavelength, dB, impedance and 50 Ω, antennas, modulation and bandwidth, noise, sharing the air, penetration, and why RF is non-ionising)
domain: 00-math-foundations
slug: rf-concepts-for-beginners
tags: [beginner, level-1, intro, what-is-rf, electromagnetic-spectrum, frequency, wavelength, speed-of-light, decibel, dbm, impedance, 50-ohm, antenna, dipole, modulation, bandwidth, noise, snr, ktb, superposition, selectivity, penetration, wall-loss, non-ionising, photon-energy, electron-volt, rf-safety]
prerequisites: []
related:
  - rf-learning-roadmap.md
  - math-roadmap-for-rf.md
  - decibels-and-log-units.md
  - complex-numbers-and-phasors.md
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../03-transmission-lines-matching/coax-and-cables.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../08-antennas/antenna-fundamentals.md
  - ../09-propagation-link-budget/friis-free-space-path-loss.md
  - ../09-propagation-link-budget/atmospheric-rain-attenuation.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../19-regulations-safety/rf-exposure-safety.md
  - ../20-projects-recipes/beginner-project-ladder.md
level: intro
confidence: high
last_updated: 2026-10-02
---

# RF concepts for beginners — a Level-1 tour with high-school maths

This page is the genuine first rung of the knowledge base. It needs only algebra, powers of ten and a
calculator with a `log` key. Each of the ten ideas ends with **Go deeper →** links to the pages that
take it further. If you want a study plan rather than a tour, read the
[RF learning roadmap](rf-learning-roadmap.md); if you want something to build, use the
[beginner project ladder](../20-projects-recipes/beginner-project-ladder.md).

## Questions this page answers
- What actually is "RF", and how is a radio wave related to light?
- How do I get the wavelength from the frequency, and why does it matter for antenna size?
- What is a decibel, and why do RF people add dB instead of multiplying?
- What does dBm mean, and how many watts is 33 dBm?
- What is impedance, and why is almost everything in RF 50 Ω?
- What does an antenna really do — does a bigger antenna "amplify" the signal?
- What is bandwidth, and why does a faster data rate need more of it?
- What is noise, and why can't a receiver hear an arbitrarily weak signal?
- With millions of radio signals in the air at once, why don't they all interfere?
- Do higher frequencies penetrate walls better?
- Is radio-frequency radiation "radiation" like X-rays? Can my LoRa radio or a 5G mast damage DNA?
- What is the one-paragraph intuition behind each of these that I should keep in my head?

## TL;DR
- **RF is light you cannot see.** Radio waves, microwaves, visible light and X-rays are all electromagnetic waves travelling at $c \approx 3\times10^8$ m/s; they differ only in frequency. "RF" usually means roughly 3 kHz–300 GHz.
- **Wavelength = speed of light ÷ frequency**: $\lambda = c/f$. At 433.92 MHz, λ = 69 cm; at 915 MHz, 33 cm; at 2.45 GHz, 12 cm. Antennas are sized in wavelengths (a dipole is about λ/2), which is why a 433 MHz antenna is about 33 cm long.
- **Decibels turn multiplication into addition**: +3 dB ≈ ×2, +10 dB = ×10, +20 dB = ×100. **dBm** is power compared with 1 mW: 0 dBm = 1 mW, 30 dBm = 1 W, 33 dBm ≈ 2 W, −100 dBm = 0.1 pW. A whole radio link is then just a sum of dB numbers.
- **Impedance** is "resistance for AC": the ratio of voltage to current, which for capacitors and inductors depends on frequency. Cables, connectors, amplifiers and antennas are designed around **50 Ω**, a historical compromise between lowest cable loss (≈ 77 Ω) and highest power handling (≈ 30 Ω). If parts are not matched, part of the power reflects back.
- **An antenna is a converter**, not an amplifier: it turns a guided wave on a cable into a free wave in space (and back). "Gain" means *focusing* power in some directions at the expense of others.
- **Bandwidth** is the width of the slice of spectrum a signal uses. More data per second needs more bandwidth (or more signal-to-noise ratio). **Noise** is the random hiss every warm object produces: $kTB$ = −174 dBm in each hertz at room temperature, so a 125 kHz LoRa channel starts with −123 dBm of noise before the receiver adds its own.
- **Signals share the air by superposition**: waves pass through each other without changing; a receiver's filters pick out one frequency. Trouble only starts inside non-linear electronics (overload).
- **Higher frequency does not penetrate better**: 20 cm of concrete costs ≈ 5 dB at 433 MHz, ≈ 15 dB at 2.45 GHz and ≈ 90 dB at 28 GHz ([09 atmospheric/building loss](../09-propagation-link-budget/atmospheric-rain-attenuation.md)).
- **RF is non-ionising**: one 433 MHz photon carries 1.8 × 10⁻⁶ eV, about **7 million times less** than the ≈ 12 eV needed to knock an electron out of a water molecule — even a 77 GHz radar photon is ~39 000 times too weak. RF's established biological effect is heating, which the exposure limits control ([RF exposure safety](../19-regulations-safety/rf-exposure-safety.md)).

All numbers on this page are reproduced by `tools/verify/e6_beginner_numbers.py` (43/43 PASS).

## Intuition (no math)
Shake one end of a long rope and a wave runs along it. Shake a bunch of electrons up and down in a
piece of wire, and a wave of electric and magnetic field runs away from the wire at the speed of light.
That wave is a radio wave. The *frequency* is how many times per second you shake; the *wavelength* is
the distance between crests; the faster you shake, the shorter the wavelength, because every wave
travels at the same speed.

A radio link is that idea twice. A transmitter shakes electrons in its antenna; the wave spreads out
like ripples from a stone in a pond and gets weaker with distance; far away it shakes the electrons in
another antenna a tiny bit; the receiver amplifies those tiny wiggles and decodes the pattern
(modulation) you put on the wave. Almost everything in RF engineering is about four questions: how much
power arrives (decibels and link budgets), how to get it into and out of the hardware without
reflecting it (impedance and matching), how wide a slice of spectrum the pattern needs (bandwidth),
and how loud the background hiss is (noise).

Two everyday facts help with the rest of the page:
- **Waves add and pass through each other.** Two ripples on a pond cross and carry on unchanged. That
  is why thousands of stations can share the same air; a tuned receiver listens to one of them.
- **Light is made of packets (photons) whose energy grows with frequency.** Radio photons are so weak
  that no single one can break a chemical bond, however many of them arrive. They can only warm things
  up, collectively — like a lot of very gentle pushes.

## The math

### Level 1 — the ten ideas with high-school maths

#### 1. What "RF" is
Electromagnetic waves span an enormous range of frequency. Roughly, from low to high:

| Name | Frequency | Wavelength | Everyday example |
|---|---|---|---|
| Mains "radiation" | 50 Hz | 6 000 km | power lines (not really a radio wave at all at human scales) |
| LF/MF radio | 30 kHz – 3 MHz | 10 km – 100 m | AM broadcast near 1 MHz |
| HF ("shortwave") | 3 – 30 MHz | 100 – 10 m | amateur and international broadcast |
| VHF | 30 – 300 MHz | 10 – 1 m | FM radio 88–108 MHz, airband, weather satellites at 137 MHz |
| UHF | 300 MHz – 3 GHz | 1 m – 10 cm | LoRa 433/868/915 MHz, GPS 1575 MHz, Wi-Fi 2.4 GHz |
| SHF (microwave) | 3 – 30 GHz | 10 – 1 cm | 5.8 GHz Wi-Fi, 10.5 GHz motion sensors, satellite TV |
| EHF (mm-wave) | 30 – 300 GHz | 1 cm – 1 mm | 60 GHz links, 77 GHz car radar |
| Infrared, visible, ultraviolet | ~300 GHz – 3 × 10¹⁶ Hz | 1 mm – 10 nm | heat lamps, light, sunburn |
| X-rays, gamma rays | above that | below 10 nm | medical imaging |

The band names (VHF, UHF…) are the ITU's decade bands. "RF" in this knowledge base means everything
from audio-range radio up to about 300 GHz. Above that, the same physics continues into optics, but the
hardware changes completely ([wave equation](../02-electromagnetics/wave-equation-plane-waves-polarization.md)).

**Go deeper →** [Electromagnetic units and constants](../02-electromagnetics/electromagnetic-units-and-constants.md) · [Maxwell's equations](../02-electromagnetics/maxwells-equations.md) · [spectrum allocation and ISM bands](../19-regulations-safety/spectrum-allocation-ism-bands.md)

#### 2. Frequency, wavelength and the speed of light
Every electromagnetic wave in vacuum (and, to within 0.03 %, in air) travels at
$c = 299\,792\,458$ m/s ≈ 3 × 10⁸ m/s. In one cycle, lasting $1/f$ seconds, the wave moves one
wavelength, so

$$\lambda = \frac{c}{f}\qquad\text{or, handily,}\qquad \lambda[\text{m}] \approx \frac{300}{f[\text{MHz}]}.$$

| Frequency | λ | λ/2 (dipole) | λ/4 (whip) |
|---|---|---|---|
| 137.9 MHz (Meteor weather satellite) | 2.17 m | 1.09 m | 54 cm |
| 433.92 MHz (LoRa, SRD) | 69.1 cm | 34.5 cm | 17.3 cm |
| 915 MHz (US LoRa) | 32.8 cm | 16.4 cm | 8.2 cm |
| 1090 MHz (aircraft ADS-B) | 27.5 cm | 13.8 cm | 6.9 cm |
| 1575.42 MHz (GPS L1) | 19.0 cm | 9.5 cm | 4.8 cm |
| 2.45 GHz (Wi-Fi, microwave oven) | 12.2 cm | 6.1 cm | 3.1 cm |
| 10.525 GHz (HB100 motion sensor) | 2.85 cm | 1.42 cm | 0.71 cm |

Why it matters: an antenna radiates well when its size is a sizeable fraction of a wavelength, and a
circuit starts behaving "like RF" (wires become transmission lines, layout matters) once its
dimensions approach about a tenth of a wavelength. At 50 Hz a 10 cm wire is 0.000 000 02 λ; at
2.45 GHz it is 0.8 λ.

**Go deeper →** [Dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md) · [Quasi-static vs full-wave](../02-electromagnetics/quasi-static-vs-full-wave.md) · [Wave equation and plane waves](../02-electromagnetics/wave-equation-plane-waves-polarization.md)

#### 3. Decibels: multiplying by adding
RF powers span absurd ranges. A 2 W transmitter and a −120 dBm received signal differ by a factor of
2 × 10¹⁵. Writing such ratios as powers of ten and adding the exponents is easier; that is what the
decibel does:

$$\text{ratio in dB} = 10\log_{10}\frac{P_2}{P_1}, \qquad P\,[\text{dBm}] = 10\log_{10}\frac{P}{1\ \text{mW}}.$$

Memorise four facts and you can do most RF arithmetic in your head:
- ×2 ≈ +3 dB, ×10 = +10 dB, ×100 = +20 dB, ×1/2 ≈ −3 dB.
- 0 dBm = 1 mW; 10 dBm = 10 mW; 20 dBm = 100 mW; 30 dBm = 1 W; 33 dBm ≈ 2 W.
- **Gains and losses in dB just add.** A 2 W (33 dBm) transmitter, a 2 dB cable loss and a 6 dBi
  antenna radiate the equivalent of 33 − 2 + 6 = 37 dBm.
- Add dB to dBm (a gain applied to a power), never dBm to dBm (two powers): 30 dBm + 30 dBm is 33 dBm,
  not 60 dBm.

A dB is a *ratio*; a dBm is an *absolute power*. "dBi" is antenna gain compared with an imaginary
antenna that radiates equally in all directions (isotropic).

**Go deeper →** [Decibels and logarithmic units](decibels-and-log-units.md) (every dB unit, 10 vs 20 log, volts in 50 Ω) · [Link budget methodology](../09-propagation-link-budget/link-budget-methodology.md)

#### 4. Impedance, and why 50 Ω
For DC, Ohm's law says $V = IR$. For AC, capacitors and inductors also "resist" current, but by an
amount that depends on frequency:

$$X_C = \frac{1}{2\pi f C}, \qquad X_L = 2\pi f L .$$

A 10 pF capacitor is 3.7 kΩ at 4.3 MHz but only 37 Ω at 433 MHz; a 10 nH inductor is 0.27 Ω at
4.3 MHz and 27 Ω at 433 MHz. The general name for "voltage ÷ current at a frequency" is
**impedance**, $Z$, in ohms. (It is a complex number, because the voltage and current can be out of
step; you meet that on the [phasors page](complex-numbers-and-phasors.md).)

At RF a cable is not just a wire: it has its own **characteristic impedance**, set by its shape — the
ratio of voltage to current of a wave travelling along it. If the cable feeds something with a
different impedance, part of the wave **reflects**, exactly like a pulse on a light rope reflecting
where it is tied to a heavy one. The reflected fraction is

$$\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0},\qquad \text{reflected power fraction} = |\Gamma|^2 .$$

A 100 Ω antenna on 50 Ω cable reflects |Γ|² = (50/150)² = 11 % of the power (a VSWR of 2 — only
0.5 dB lost, which is why "SWR under 2" is a common target).

**Why 50 Ω?** For coaxial cable of a given outer size, the impedance that gives the **lowest loss**
is about **77 Ω** and the one that carries the **most power** before the air breaks down is about
**30 Ω**. 50 Ω sits between them and costs only about 10 % more loss than the minimum. It became the
standard in the 1930s–40s and everything since — connectors, amplifiers, instruments — was built to
match it. (Cable TV chose 75 Ω because it only cares about loss.)

**Go deeper →** [Lumped elements, impedance and admittance](../01-circuit-theory/lumped-elements-impedance-admittance.md) · [Coax and cables (the 30/60/77 Ω derivation)](../03-transmission-lines-matching/coax-and-cables.md) · [Reflections, VSWR and return loss](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md) · [Impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)

#### 5. What an antenna does
An antenna is a **converter** between a wave guided by a cable and a wave in free space. It works the
same in both directions (reciprocity): a good transmitting antenna is an equally good receiving one at
the same frequency.

Three facts carry most of antenna engineering:
1. **Size follows wavelength.** The simplest efficient antenna is a half-wave dipole, two rods each
   λ/4 long; a quarter-wave whip over a metal ground plane is the "half" version. Much smaller antennas
   can be made to work, but they become narrow-band and lossy ([small-antenna limits](../08-antennas/small-antenna-limits.md)).
2. **Gain is focusing, not amplifying.** An antenna cannot create power. A "6 dBi" antenna sends four
   times more power in its best direction than an isotropic one would, *because* it sends less
   elsewhere — think of the reflector behind a torch bulb. A high-gain "omni" squashes its doughnut
   pattern flat towards the horizon, which is bad for a rocket overhead
   ([choosing LoRa antennas](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md)).
3. **Polarisation must line up.** A vertical rod radiates vertically polarised waves; a horizontal
   receiving rod hears much less of them. Circular polarisation avoids the problem at a fixed 3 dB cost.

**Go deeper →** [Antenna fundamentals](../08-antennas/antenna-fundamentals.md) · [Dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md) · [Polarisation](../08-antennas/antenna-polarization-and-circular-polarization.md) · [Antennas on rockets](../08-antennas/antennas-on-rockets.md)

#### 6. Modulation and bandwidth
A pure, unchanging sine wave carries no information. To send something you **modulate** the wave:
change its amplitude (AM), its frequency (FM), its phase (PSK), or — in LoRa — sweep its frequency
in chirps. Any change in time spreads the signal over a range of frequencies; that range is its
**bandwidth** $B$, in hertz.

A rule of thumb you can check on any spectrum display: the faster the signal changes, the wider it
gets. Changing state $R$ times per second needs a bandwidth of roughly $R$ hertz (more for crude
modulation, less for clever pulse shaping). So AM voice is about 10 kHz wide, FM broadcast about
200 kHz, a 1 Mb/s ADS-B reply about 2 MHz, and Wi-Fi 20–160 MHz. LoRa trades the other way: it
spreads a slow data stream over 125–500 kHz so it can be received far below the noise.

**Go deeper →** [AM, FM, PM and SSB](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md) · [Digital modulation](../10-comms-modulation/digital-modulation-psk-qam-fsk.md) · [LoRa chirp maths](../15-lora-ism-radios/lora-phy-css-math.md) · [Fourier series and transform](fourier-series-and-transform.md)

#### 7. Noise and signal-to-noise ratio
Every resistor, every antenna looking at warm ground, and every amplifier produces random electrical
hiss, because electrons in anything warm jiggle about. The available noise power in a bandwidth $B$ at
temperature $T$ is

$$N = kTB, \qquad k = 1.38\times10^{-23}\ \text{J/K}.$$

At room temperature (290 K) that is **−174 dBm in every hertz**. In dB, just add $10\log_{10}B$:

| Bandwidth | Noise floor kTB |
|---|---|
| 12.5 kHz (APRS, AIS channel) | −133 dBm |
| 125 kHz (LoRa) | −123 dBm |
| 200 kHz (FM broadcast) | −121 dBm |
| 2 MHz (ADS-B) | −111 dBm |

A real receiver adds its own noise, stated as its **noise figure** NF in dB, so its floor is
−174 + 10 log B + NF. What matters for decoding is the **signal-to-noise ratio** (SNR): signal power
minus noise power, in dB. FM radio wants roughly +10 to +20 dB; LoRa at SF12 still decodes at about
−20 dB, because its chirps are matched to the receiver's correlator. There is always a weakest
decodable signal, the **sensitivity**, set by noise — no amount of "amplification" removes noise that
arrived with the signal.

**Go deeper →** [Thermal noise and noise temperature](../07-noise-linearity/thermal-noise-and-noise-temperature.md) · [Noise figure and Friis](../07-noise-linearity/noise-figure-and-friis.md) · [Sensitivity and MDS](../07-noise-linearity/sensitivity-and-mds.md) · [LoRa sensitivity and link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)

#### 8. How millions of signals share the air
Electromagnetic waves in air obey **superposition**: the total field is simply the sum of all the
individual fields, and each wave passes through the others unchanged. Your FM station, a phone call, a
GPS signal and a LoRa packet all occupy the same space at once; nothing in the air "mixes" them.

The receiver separates them with **filters**, which pass a narrow range of frequencies and reject the
rest (the tuning knob of an old radio moves a filter). Interference happens only when
1. two transmitters use the **same frequency at the same time and place** (that is why spectrum is
   licensed and shared by rules), or
2. a strong signal **overloads** a receiver's amplifiers or mixer. Electronics pushed beyond their
   linear range *do* mix signals, creating new frequencies that were never transmitted
   ([dynamic range and blocking](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). That is the
   origin of most "phantom" signals on cheap SDRs.

**Go deeper →** [Linear systems and convolution](linear-systems-convolution.md) · [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) · [Receiver architectures](../06-rf-circuits/receiver-architectures.md) · [Nonlinearity, P1dB and IP3](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)

#### 9. Why higher frequency does *not* "penetrate better"
A popular myth runs: "higher frequency = more energetic = goes through things better". For radio, the
opposite is usually true:
- **Walls and bodies absorb more at higher frequency.** Building materials are lossy dielectrics whose
  losses grow roughly in proportion to frequency. ITU-R's material model gives, for 20 cm of concrete,
  ≈ 5 dB at 433 MHz, 7 dB at 915 MHz, 15 dB at 2.45 GHz, 28 dB at 5.8 GHz and ≈ 90 dB at 28 GHz.
  Water and tissue behave similarly: a 2.45 GHz microwave oven heats food because only the outer
  couple of centimetres absorb most of the energy.
- **Metal reflects everything** at any radio frequency; the field only enters a skin a few
  micrometres deep.
- **"Free-space loss rises with frequency" is an antenna-size effect**, not absorption. Between two
  *dipoles* the path loss rises by 20 log(f) because a higher-frequency dipole is smaller and catches
  less of the wave. Between two antennas of the *same physical area*, the higher frequency actually
  wins ([Friis](../09-propagation-link-budget/friis-free-space-path-loss.md)).
- X-rays go through you for a different reason: their photons are so energetic that they interact
  with tissue in a completely different, much weaker way per unit thickness. That regime is far beyond
  RF.

**Go deeper →** [Atmospheric, rain and building loss (with the wall table)](../09-propagation-link-budget/atmospheric-rain-attenuation.md) · [Dielectrics and loss tangent](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md) · [Skin effect](../02-electromagnetics/skin-effect-conductor-loss-roughness.md)

#### 10. Why RF is non-ionising
Light comes in packets called photons. Each photon's energy is fixed by its frequency alone:

$$E = h f, \qquad h = 6.626\times10^{-34}\ \text{J·s}, \qquad 1\ \text{eV} = 1.602\times10^{-19}\ \text{J}.$$

To **ionise** an atom or molecule — knock an electron clean off, which is what can break DNA — a
single photon needs roughly 10–12 eV or more (≈ 12.6 eV for a water molecule). European radiation
law draws the line at a wavelength of 100 nm, which is 12.4 eV, in the far ultraviolet.

| Source | Frequency | Energy per photon | Ionisation scale ÷ photon |
|---|---|---|---|
| LoRa 433.92 MHz | 4.3 × 10⁸ Hz | 1.8 × 10⁻⁶ eV | ≈ 7 million |
| Wi-Fi / microwave oven 2.45 GHz | 2.45 × 10⁹ Hz | 1.0 × 10⁻⁵ eV | ≈ 1.2 million |
| Car radar 77 GHz | 7.7 × 10¹⁰ Hz | 3.2 × 10⁻⁴ eV | ≈ 39 000 |
| Green light 550 nm | 5.5 × 10¹⁴ Hz | 2.3 eV | ≈ 5.5 |
| Far UV 100 nm | 3.0 × 10¹⁵ Hz | 12.4 eV | 1 |
| Medical X-ray | ~1.5 × 10¹⁹ Hz | ~60 000 eV | far above |

Ionisation is a **one-photon** event: a million weak photons do not add up to one strong one, just as
a million table-tennis balls cannot knock down a wall that a single cannonball would. An RF photon is
even about **15 000 times smaller than the random thermal energy** (≈ 0.027 eV) that every molecule in
your body already has at 37 °C. What RF *can* do, when the power is high, is make molecules jiggle
collectively — it **heats** tissue. That is the effect the exposure limits are built on.

**Go deeper →** [RF exposure safety — the non-ionising section and the limits](../19-regulations-safety/rf-exposure-safety.md) · [Poynting vector and power flow](../02-electromagnetics/poynting-vector-power-flow.md) · [Lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)

### Level 2 — where the Level-1 formulas come from (one step up)
- **λ = c/f** is the wave equation's travelling solution $\cos(2\pi f t - 2\pi z/\lambda)$: a crest
  moves at $\lambda f$, which Maxwell's equations fix at $c = 1/\sqrt{\mu_0\varepsilon_0}$ in vacuum
  and $c/\sqrt{\varepsilon_r}$ in a dielectric — which is why a wave in PTFE coax is ~30 % slower
  (velocity factor 0.69) ([wave equation](../02-electromagnetics/wave-equation-plane-waves-polarization.md)).
- **10 log vs 20 log.** Power is proportional to voltage squared ($P = V^2/R$), so a voltage ratio in
  dB is $20\log_{10}(V_2/V_1)$ — the same dB number as the power ratio, as long as the impedance is the
  same ([decibels Level 2](decibels-and-log-units.md)).
- **Impedance as a complex number.** Writing $Z = R + jX$ with $j = \sqrt{-1}$ lets one number hold both
  the size and the timing (phase) of the current; $X_L = \omega L$ and $X_C = -1/(\omega C)$ come from
  $v = L\,di/dt$ and $i = C\,dv/dt$ with sinusoids ([phasors](complex-numbers-and-phasors.md)).
- **Reflection coefficient.** At a junction the voltage and current must be continuous; solving those
  two conditions for the reflected wave gives $\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$
  ([reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)).
- **Free-space path loss.** A transmitter's power spreads over a sphere of area $4\pi d^2$; a receiving
  antenna with effective area $A_e = G\lambda^2/4\pi$ collects a fraction of it. Putting the two together
  gives Friis' $P_r = P_t G_t G_r (\lambda/4\pi d)^2$, the $\lambda^2$ coming from the receiving
  aperture ([Friis](../09-propagation-link-budget/friis-free-space-path-loss.md)).
- **Noise power $kTB$** follows from thermodynamics: each independent "mode" of a system at temperature
  $T$ holds about $kT$ of energy; a bandwidth $B$ carries $B$ such modes per second
  ([thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).
- **Data rate and bandwidth.** Shannon's limit, $C = B\log_2(1 + \text{SNR})$, says capacity grows with
  bandwidth and only slowly (logarithmically) with signal power ([BER and Shannon](../10-comms-modulation/ber-ebn0-and-shannon.md)).

### Level 3 — where the beginner pictures break
- **"RF" and "light" really are one spectrum**, but conductors stop behaving like perfect mirrors in the
  infrared, so antenna ideas carry over to optics only with new physics (plasmonics, nano-antennas).
- **Antennas are not always λ/2.** Electrically small antennas trade bandwidth and efficiency for size
  (the Chu limit); large arrays and dishes are many wavelengths across. The λ/2 rule is the efficient
  middle ground ([small-antenna limits](../08-antennas/small-antenna-limits.md)).
- **50 Ω is a convention, not a law.** Antenna terminals, transistor inputs and chip pins rarely are
  50 Ω; matching networks transform them ([matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).
- **Noise is not always 290 K.** An antenna pointed at cold sky sees tens of kelvin; one in a city at
  HF sees man-made noise thousands of times stronger than kTB
  ([thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).
- **Penetration has exceptions.** Thin slabs have thickness resonances, and metallised-glass buildings
  can let 2.4 GHz in through apertures more easily than 433 MHz
  ([building loss](../09-propagation-link-budget/atmospheric-rain-attenuation.md)).
- **Non-ionising does not mean harmless at any power.** High RF power density heats tissue; the eye and
  testes are poorly cooled and most sensitive; RF burns happen on contact with transmitting antennas.
  That is why limits exist ([RF exposure safety](../19-regulations-safety/rf-exposure-safety.md)).

## Design equations & rules of thumb
| Quantity | Formula | Handy number |
|---|---|---|
| Wavelength | $\lambda = c/f$ | λ[m] ≈ 300 / f[MHz]; 433.92 MHz → 0.691 m |
| Half-wave dipole length | ≈ 0.95–0.97 × λ/2 (thin wire) | 433.92 MHz → ≈ 33 cm tip to tip |
| Power in dBm | $10\log_{10}(P/1\,\text{mW})$ | 2 W = 33 dBm; 10 mW = 10 dBm |
| Power doubling | +3 dB | ×2 power = ×1.41 free-space range |
| Volts in 50 Ω | $V_{rms} = \sqrt{P\cdot50}$ | −100 dBm = 2.24 µV; 2 W = 10 V rms |
| Reactance | $X_L = 2\pi fL$, $X_C = 1/(2\pi fC)$ | 10 nH at 433 MHz = 27 Ω; 10 pF = 37 Ω |
| Reflected power | $|\Gamma|^2$, $\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ | VSWR 2 → 11 % reflected, 0.5 dB loss |
| Free-space path loss | $20\log_{10}(4\pi d f/c)$ | 433.92 MHz: 85.2 dB at 1 km, +20 dB per ×10 distance |
| Noise floor | −174 dBm/Hz + 10 log B + NF | LoRa 125 kHz, NF 6 dB → −117 dBm |
| Photon energy | $E = hf$ | 433.92 MHz → 1.8 µeV; ionising ≳ 12 eV |
| Radio horizon (4/3 Earth) | $d[\text{km}] \approx 4.12(\sqrt{h_1} + \sqrt{h_2})$, h in m | 10 m mast to 35 000 ft aircraft: ≈ 439 km |

## Worked examples
**1. Cut a 433 MHz dipole.** λ = 299.79/433.92 = 0.691 m; λ/2 = 345 mm. Thin wire resonates a few
per cent short, so cut each arm to ≈ 172 mm (345 mm total), then trim a few mm at a time while
watching the dip on a NanoVNA. The finished antenna is usually 328–335 mm tip to tip
([dipoles](../08-antennas/dipoles-and-monopoles.md); project 3 of the
[ladder](../20-projects-recipes/beginner-project-ladder.md)).

**2. A first link budget, entirely in dB.** A 2 W (33 dBm) LoRa transmitter with a 2.15 dBi dipole,
10 km of clear line of sight to a 2.15 dBi dipole receiver at 433.92 MHz:
- free-space path loss = 20 log₁₀(4π × 10 000 × 433.92 × 10⁶ / 2.998 × 10⁸) = **105.2 dB**;
- received power = 33 + 2.15 − 105.2 + 2.15 = **−67.9 dBm**;
- an SX1262 at SF9/125 kHz decodes near −129.5 dBm (datasheet, per the 15 page), so the margin is
  about **60 dB** before fading,
  cable loss and pattern nulls — which is why rocket links are limited by geometry and orientation, not
  power ([LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).
(At Singapore's licence-exempt 10 mW e.r.p. the margin is ≈ 23 dB smaller — still positive.)

**3. What does −100 dBm look like on an oscilloscope?** P = 10⁻¹⁰ mW = 10⁻¹³ W; in 50 Ω,
V = √(10⁻¹³ × 50) = **2.24 µV rms**. A scope's noise is about a millivolt, so you cannot see it — this
is why receivers need tens of dB of low-noise gain before anything useful happens.

**4. Noise floor and LoRa's "below the noise" trick.** Channel 125 kHz: 10 log₁₀(125 000) = 51 dB.
Receiver NF 6 dB → floor = −174 + 51 + 6 = **−117 dBm**. LoRa SF12 decodes at SNR ≈ −20 dB, i.e. at
about **−137 dBm**: 20 dB *below* the noise. It can do this because each symbol is a long chirp that the
receiver correlates against a known pattern, collecting energy over 2¹² samples
([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)).

**5. Is a microwave oven's 2.45 GHz "more dangerous" than visible light because it's more powerful?**
A 1 kW oven emits 1000 / (6.626 × 10⁻³⁴ × 2.45 × 10⁹) ≈ 6 × 10²⁶ photons per second, each carrying
10⁻⁵ eV — huge in number, tiny in individual energy. It cooks by **heating** (the water molecules are
jostled by the field). A sunlit window lets through far fewer, but individually far more energetic,
photons; those in the UV part can break bonds (sunburn). The two hazards are different in kind, which is
why ionising and non-ionising radiation have separate rules and separate commissions (ICRP vs ICNIRP).

**6. A concrete wall at three frequencies.** Using the KB's ITU-R P.2040 wall model for 20 cm of
concrete: 433 MHz loses ≈ 5 dB, 2.45 GHz ≈ 15 dB, 28 GHz ≈ 90 dB. A sensor inside a concrete
building is ≈ 10 dB better off at 433 MHz than at 2.4 GHz from the wall alone
([building loss](../09-propagation-link-budget/atmospheric-rain-attenuation.md)).

## Practical notes
- **Carry a dB cheat-sheet** (the four facts in idea 3) and a λ table for your bands; most bench
  arithmetic is one of these two.
- **Units are where beginners lose marks**: write dB vs dBm vs dBi every time, and say peak or rms for
  voltages ([decibels](decibels-and-log-units.md)).
- **Measure early.** A NanoVNA, a tinySA and an RTL-SDR (≈ US$110 + US$120 + US$40 in 2026) make every
  idea on this page visible: see the dip of your antenna's resonance, the bandwidth of a signal and the
  noise floor move when you add an LNA ([lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md),
  [project ladder](../20-projects-recipes/beginner-project-ladder.md)).
- **Never transmit into nothing.** Always connect an antenna or a 50 Ω dummy load before powering a
  transmitter; the reflected power can destroy the output stage (Meshtastic's getting-started guide
  gives the same warning for LoRa boards) ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).
- **Know what you may transmit.** Receiving is generally unrestricted; transmitting needs either a
  licence-exempt band within its power and duty limits or a licence
  ([Singapore rules](../19-regulations-safety/singapore-imda-rules.md),
  [amateur licensing](../19-regulations-safety/amateur-radio-licensing.md)).

## Common mistakes & misconceptions
- **"An antenna amplifies the signal."** It only redirects power; gain in one direction is paid for by
  less power elsewhere.
- **"A bigger dBi number always means more range."** Only towards the antenna's best direction; a
  10 dBi omni can be *worse* than a 2 dBi dipole for a target overhead
  ([LoRa antennas](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md)).
- **"30 dBm + 30 dBm = 60 dBm."** Two 1 W signals make 2 W = 33 dBm. Add dB (ratios) to dBm, never dBm
  to dBm ([decibels](decibels-and-log-units.md)).
- **"Doubling power doubles range."** In free space range grows with the square root of power: +3 dB
  gives ×1.41.
- **"A multimeter should read 50 Ω across a coax cable."** Characteristic impedance is a wave property;
  a DC ohmmeter sees an open circuit (or the antenna's DC path)
  ([telegrapher equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md)).
- **"With so many signals in the air they must all interfere."** Waves superpose linearly; only
  receivers overloaded into non-linearity, or transmitters on the same channel, interfere.
- **"Higher frequencies penetrate better."** Not for walls, foliage, water or people at radio
  frequencies — see idea 9.
- **"RF is radiation like X-rays, so any exposure risks cancer."** RF photons are millions of times too
  weak to ionise; the established hazard is heating, controlled by exposure limits. Conversely,
  **"non-ionising means harmless at any power"** is also wrong — standing in front of a high-power
  transmitting antenna can heat tissue and burn ([RF exposure safety](../19-regulations-safety/rf-exposure-safety.md)).
- **"You must master Maxwell's equations before building anything."** Most practical RF needs ideas 1–8
  plus complex numbers; build alongside the maths ([learning roadmap](rf-learning-roadmap.md)).

## How to simulate / verify
- `python3 tools/verify/e6_beginner_numbers.py` — photon energies vs the 12.4 eV ionising boundary,
  kT at 37 °C, wavelengths, dB/dBm and volts-in-50 Ω examples, dipole and whip lengths, velocity factor
  from a quarter-wave resonance, kTB floors, ADS-B horizon, HB100 Doppler, LEO satellite Doppler and the
  path-loss "aperture effect" (43/43 PASS).
- Wall-loss numbers: `tools/verify/fix_penetration_vs_frequency.py` (ITU-R P.2040-3 slab model, owned
  by domain 09).
- `tools/rfcalc` has unit converters for dBm ↔ W ↔ V and λ ([calculators](../16-simulation-tools/impedance-and-rf-calculators.md)).
- Bench check: measure a dipole's resonance and a cable's velocity factor with a NanoVNA (projects 3–4 of
  the [ladder](../20-projects-recipes/beginner-project-ladder.md)).

## Open questions / gaps
- The ionising threshold has no single legal or physical value: texts quote ~4–25 eV (valence
  electrons), 10 eV, 12.4 eV (EU, 100 nm) or ~34 eV (mean energy per ion pair in tissue). The conclusion
  (RF is 10⁴–10⁷ times below any of them) does not depend on the choice; the page uses 12.4 eV.
- Band-name boundaries (VHF/UHF) are ITU decade conventions; industry "microwave" and "mm-wave" usage
  varies.
- The "eye and testes are most sensitive" statement is standard in exposure guidance but was not
  re-read in a primary source for this page (see [RF exposure safety](../19-regulations-safety/rf-exposure-safety.md)).

## Sources
1. This KB: [decibels](decibels-and-log-units.md), [phasors](complex-numbers-and-phasors.md), [coax and cables](../03-transmission-lines-matching/coax-and-cables.md) (30/60/77 Ω optima, derived and verified in `tools/verify/tline_coax.py`), [atmospheric and building loss](../09-propagation-link-budget/atmospheric-rain-attenuation.md) (ITU-R P.2040-3 wall table, P.2109-2), [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md), [Friis](../09-propagation-link-budget/friis-free-space-path-loss.md), [LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md), [RF exposure safety](../19-regulations-safety/rf-exposure-safety.md). (internal, each with primary sources)
2. BIPM, *The International System of Units (SI Brochure)*, 9th ed. (2019) — exact values of $c$, $h$, $e$ and $k$ used in every calculation here. https://www.bipm.org/en/publications/si-brochure (standard)
3. M. Tschurlovits, "What is 'ionizing radiation'?", IAEA-CN-67/153 (IRPA/IAEA conference paper, 1997) — review of definitions: ICRU 33 says the cut-off depends on circumstances; Attix's 4–25 eV valence-electron range; BEIR's ~34 eV per ion pair; the 1996 EURATOM boundary of 100 nm (≈ 12.4 eV for photons). https://www.osti.gov/etdeweb/servlets/purl/593131 (conference paper; read via pdftotext)
4. ICNIRP, "Guidelines for limiting exposure to electromagnetic fields (100 kHz to 300 GHz)", *Health Physics* 118(5):483–524 (2020) — heating as the established mechanism; reduction factors. https://www.icnirp.org/cms/upload/publications/ICNIRPrfgdl2020.pdf (peer-reviewed guideline; via the 19 page)
5. ITU-R V.431-8, *Nomenclature of the frequency and wavelength bands used in telecommunications* (2015) — decade band names (VLF … EHF). (standard; recalled — not re-read)
6. Microwaves101, "Why fifty ohms?" — 30/77 Ω optima and the historical origin (via 03/coax-and-cables). https://www.microwaves101.com/encyclopedias/why-fifty-ohms (web tutorial; numbers re-derived in the KB)
7. A. Winter, *dB or not dB?*, Rohde & Schwarz application note 1MA98 (v14e, 2024) — dB conventions. (app note; via 00/decibels)
8. Meshtastic documentation, "Getting started" — warning not to power a radio without an antenna. https://meshtastic.org/docs/getting-started/ (project docs; search summary)
9. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge University Press (2015), ch. 1 and 13 — reactance, impedance and RF intuition at an introductory level. (textbook; recalled)
