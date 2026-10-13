---
title: Thermal noise and noise temperature
domain: 07-noise-linearity
slug: thermal-noise-and-noise-temperature
tags: [noise, johnson-nyquist, kTB, noise-temperature, antenna-temperature, sky-noise, man-made-noise, ITU-R-P.372, planck, radiometer, dicke, beam-efficiency, sun-noise, G-over-T, interferometry, aperture-synthesis]
prerequisites: [../00-math-foundations/decibels-and-log-units.md, ../00-math-foundations/probability-random-processes-and-psd.md, ../01-circuit-theory/network-theorems-max-power-transfer.md]
related: [noise-figure-and-friis.md, sensitivity-and-mds.md, shot-and-flicker-noise.md, receiver-cascade-analysis.md, ../09-propagation-link-budget/link-budget-methodology.md, ../08-antennas/antenna-fundamentals.md, ../08-antennas/gnss-antennas.md, ../17-test-measurement/noise-figure-measurement.md, ../17-test-measurement/spectrum-analyzers.md, ../17-test-measurement/phase-noise-measurement.md, ../12-phased-arrays/adaptive-beamforming-doa.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Thermal noise and noise temperature

## Questions this page answers
- Where does the "−174 dBm/Hz" noise floor come from, and is it a law of nature?
- Why does a resistor make noise at all, and why does the available noise power not depend on its resistance?
- What is kTB and how much noise is there in a 125 kHz LoRa channel?
- What is "noise temperature", and why do people describe an amplifier with a temperature in kelvin?
- What is antenna noise temperature, and is my antenna noisier pointed at the ground or the sky?
- Why do HF radios not care about receiver noise figure but GNSS receivers care a lot?
- Why does a 3 dB cable in front of my receiver add exactly 3 dB of noise figure?
- When does the quantum (Planck) correction to thermal noise matter?
- Why does my spectrum analyzer show the noise floor 2.5 dB too low in log-average mode?
- How precisely can I measure an antenna temperature with an SDR, and how long do I need to integrate?
- What is a Dicke radiometer, and why switch between the antenna and a load?
- Can I see the Sun with a 433 MHz Yagi and an RTL-SDR, and how do I get G/T from it?
- How does a radio interferometer get fine resolution from small antennas?

## TL;DR
- Any resistance at temperature *T* delivers an **available noise power $kTB$** to a matched load — independent of the resistance value. At the reference temperature $T_0 = 290$ K, $kT_0 = 4.00\times10^{-21}$ W/Hz $= -173.98$ dBm/Hz ≈ **−174 dBm/Hz** (verified: `tools/verify/noise_thermal.py`).
- Handy numbers at 290 K: 125 kHz → **−123.0 dBm**; 250 kHz → −120.0 dBm; 1 MHz → −114.0 dBm; 20 MHz → −101.0 dBm.
- The open-circuit noise voltage is $v_n = \sqrt{4kTRB}$: 0.895 nV/√Hz for 50 Ω, 4.0 nV/√Hz for 1 kΩ.
- **Noise temperature** $T$ is simply "noise power per unit bandwidth divided by *k*". It lets you add noise sources by adding kelvins. An amplifier with 1 dB noise figure has $T_e = 75$ K; NF 6 dB ↔ 865 K.
- A **lossy passive part at physical temperature $T_p$** adds $T_e = (L-1)T_p$; at $T_p = T_0$ its noise figure equals its loss (2 dB cable ⇒ NF 2 dB).
- **Antenna temperature** is the pattern-weighted average brightness of everything the antenna sees. At 433 MHz a sky-pointing Yagi sees ~20–200 K of galactic noise plus ground in its sidelobes; at HF (3–30 MHz) man-made and galactic noise are $10^4$–$10^8$ K, so receiver NF is irrelevant there (ITU-R P.372 [4]).
- **Radiometry:** a noise power is measured to $\Delta T = T_\text{sys}/\sqrt{B\tau}$ (0.14 K for 200 K, 2 MHz, 1 s); Dicke switching costs ×2 but removes gain drift, which otherwise adds $T_\text{sys}\Delta G/G$. The quiet Sun (≈ 35 sfu at 410 MHz) adds ≈ 61 K to an 11 dBi Yagi: Y = 0.29 dB on an RTL-SDR, 1.15 dB behind an LNA (G/T −12 dB/K). Verified: `tools/verify/s7_radiometer.py`.
- Quantum correction: the classical $kT$ is really $hf/(e^{hf/kT}-1)$; at 290 K the error is only −0.03 dB at 77 GHz and −1 dB at 2.7 THz. It matters for cryogenic receivers (−0.26 dB at 10 GHz, 4 K).

## Intuition (no math)
Electrons in a conductor are a hot gas: they jiggle randomly because the conductor has a temperature. Each random move of charge is a tiny current pulse, and the sum of zillions of independent tiny pulses is a noise voltage with a Gaussian distribution and an almost perfectly flat ("white") spectrum up to terahertz frequencies. This is **Johnson–Nyquist** (thermal) noise, measured by Johnson and explained by Nyquist in 1928 [1][2].

Why does the *available power* not depend on resistance? Think of two resistors connected together at the same temperature. The second law of thermodynamics forbids net heat flow between two bodies at the same temperature, so the power resistor A pushes into B must equal what B pushes into A. If power depended on resistance, a 50 Ω and a 1 kΩ resistor at the same temperature would heat one another unequally — a perpetual-motion machine. So the noise power a resistor can deliver into a matched load must be a universal function of temperature and bandwidth only: $kTB$. A bigger resistor has a bigger noise *voltage* but can drive less *current*; the two effects cancel in the power.

**Noise temperature** turns this around: if some device (an amplifier, an antenna, the sky) delivers noise power $N$ in bandwidth $B$, we say it is "as noisy as a resistor at temperature $T = N/(kB)$". That lets us describe very different noise sources on a common scale and simply add their temperatures (uncorrelated noise powers add).

**Antenna temperature.** An antenna is a window. A lossless antenna has no internal noise; the noise at its terminals is the thermal radiation of whatever it looks at, averaged by its pattern. Point it at 290 K ground and you get ~290 K. Point it at the cold sky at microwave frequencies and you get a few kelvin. Point it at the sky at 30 MHz and you get tens of thousands of kelvin, because our galaxy is a bright, non-thermal radio source at low frequencies. And near towns, the "sky" is polluted by man-made noise (power lines, switching supplies, engines, electronics) that is far stronger than thermal noise below a few hundred MHz.

**Lossy parts are noise sources.** An attenuator (cable, filter, switch) at room temperature absorbs signal power and, by the same equilibrium argument, re-emits thermal noise. A matched attenuator's output always looks like a room-temperature resistor, whatever is on its input. So a cable reduces the signal while holding the noise at ~kT — it lowers SNR by exactly its loss. That is why the first thing an RF engineer does is put the low-noise amplifier (LNA) *before* the cable.

## The math

### Level 1 — the results and their units
- Available noise power (classical, $hf \ll kT$):
  $$N = kTB \quad [\text{W}],\qquad k = 1.380649\times10^{-23}\ \text{J/K}$$
  $T$ in kelvin, $B$ the **noise bandwidth** in Hz.
- In dBm: $N_\text{dBm} = -173.98 + 10\log_{10}B + 10\log_{10}(T/290)$.
- Thévenin model of a noisy resistor: an ideal resistor $R$ in series with a random voltage source of mean-square value
  $$\overline{v_n^2} = 4kTRB\quad[\text{V}^2]$$
  (or Norton: current source $\overline{i_n^2} = 4kTB/R$ in parallel).
- Delivered into a matched load $R_L = R$: $P = \overline{v_n^2}/(4R) = kTB$.
- Noise temperature of a source that delivers $N$ in $B$: $T = N/(kB)$.
- Lossy matched passive with loss $L \ge 1$ (linear) at physical temperature $T_p$: added noise referred to its input $T_e = (L-1)T_p$; noise factor $F = 1 + (L-1)T_p/T_0$ (so $F = L$ when $T_p = T_0$).

### Level 2 — derivations

**(a) Nyquist's transmission-line argument [2].** Connect two resistors $R$ by a lossless line of characteristic impedance $R$ and length $\ell$, phase velocity $v$; everything is at temperature $T$. The line is matched at both ends, so whatever each resistor emits is fully absorbed by the other.

Imagine shorting both ends at an instant. The trapped energy now lives in standing-wave modes with frequencies $f_n = n v/(2\ell)$, i.e. $2\ell/v$ modes per hertz. Each mode is a one-dimensional harmonic oscillator; classical equipartition gives each mode mean energy $kT$ ($\tfrac12 kT$ each in electric and magnetic storage). The energy in bandwidth $B$ is therefore
$$E_B = kT\cdot \frac{2\ell B}{v}.$$
Before the short, that energy was travelling, half in each direction, and takes time $\ell/v$ to cross the line. The power arriving at (and absorbed by) each resistor is
$$P = \frac{E_B/2}{\ell/v} = kTB .$$
In equilibrium each resistor must emit what it absorbs, so each resistor's available noise power is $kTB$, independent of $R$. With the Thévenin model, the power a source $v_n$ with internal $R$ delivers into a matched $R$ is $\overline{v_n^2}/4R$, hence $\overline{v_n^2} = 4kTRB$.

**(b) Planck (quantum) form.** Equipartition fails when $hf$ is comparable to $kT$: a mode of frequency $f$ holds mean thermal energy $hf/(e^{hf/kT}-1)$ instead of $kT$ (Bose–Einstein statistics). The available power spectral density becomes
$$\frac{N}{B} = \frac{hf}{e^{hf/kT}-1}\ \ (+\ \tfrac12 hf\ \text{zero-point term, see Level 3}).$$
With $x = hf/kT$, the ratio to the classical value is $x/(e^x - 1) \approx 1 - x/2$ for small $x$. At 290 K, $x = 1$ at $f = kT/h = 6.0$ THz. Computed ratios (`noise_thermal.py`):

| Temperature | 1.575 GHz | 10 GHz | 77 GHz | 300 GHz | 1 THz |
|---|---|---|---|---|---|
| 290 K | −0.0006 dB | −0.004 dB | −0.03 dB | −0.11 dB | −0.36 dB |
| 77 K | −0.002 dB | −0.013 dB | −0.10 dB | −0.41 dB | −1.4 dB |
| 4 K | −0.04 dB | −0.26 dB | −2.2 dB | −9.9 dB | −41 dB |

So for everything in this knowledge base (433 MHz–77 GHz, room temperature) the classical $kTB$ is exact to better than 0.03 dB. Noise-temperature scales used in radio astronomy and cryogenic LNAs sometimes use "Rayleigh–Jeans temperature" by convention; the difference only matters there.

**(c) Noise temperature and addition.** Uncorrelated noise powers add, so temperatures add: a receiver with input-referred excess noise $T_e$ connected to an antenna of temperature $T_a$ has system temperature
$$T_\text{sys} = T_a + T_e,\qquad N = kT_\text{sys}B .$$
Noise figure (see [noise-figure-and-friis](noise-figure-and-friis.md)) is the same information on a different scale: $F = 1 + T_e/T_0$.

**(d) Lossy passive network (attenuator, cable, filter).** Take a matched attenuator of power loss $L$ at physical temperature $T_p$, with a matched resistor at $T_p$ on its input. The whole assembly is one body in equilibrium, so its output must look like a resistor at $T_p$: available output noise $kT_pB$. That output consists of the input resistor's noise attenuated, $kT_pB/L$, plus the attenuator's own contribution $N_a$:
$$kT_pB = \frac{kT_pB}{L} + N_a \;\Rightarrow\; N_a = kT_pB\left(1-\frac1L\right).$$
Referring $N_a$ back to the input (multiply by $L$) gives $T_e = (L-1)T_p$, and $F = 1 + (L-1)T_p/T_0$. The result is independent of what is actually connected to the input — it is a property of the attenuator. A slice-by-slice numerical model (the attenuator as 2000 thin lossy slices) reproduces this exactly (`noise_thermal.py`).

A useful corollary: an antenna of temperature $T_a$ seen through a feeder of loss $L$ at $T_p$ presents
$$T_\text{out} = \frac{T_a}{L} + T_p\left(1 - \frac1L\right)$$
to the receiver. A 1 dB feeder turns a 50 K sky into 99 K, and a 10 K sky into 68 K — loss in front of a low-noise system is devastating.

**(e) Antenna temperature.** For an antenna with directivity pattern $D(\theta,\phi)$ viewing a brightness-temperature distribution $T_B(\theta,\phi)$,
$$T_A = \frac{1}{4\pi}\oint D(\theta,\phi)\,T_B(\theta,\phi)\,d\Omega .$$
If the antenna has radiation efficiency $\eta$ and physical temperature $T_p$, the terminal temperature is $\eta T_A + (1-\eta)T_p$ (the ohmic loss behaves like the attenuator in (d)). An electrically small or badly matched antenna with $\eta = 0.3$ at 290 K therefore contributes ~200 K by itself.

**(f) Noise bandwidth.** "$B$" is the **equivalent noise bandwidth** $B_n = \frac{1}{|H(f_0)|^2}\int_0^\infty |H(f)|^2 df$, not the 3 dB bandwidth. Computed ratios $B_n/B_{3\,\text{dB}}$: one-pole RC $\pi/2 = 1.571$; 2-pole Butterworth 1.111; 3-pole 1.047; 5-pole 1.017; Gaussian 1.065 (`noise_thermal.py`). For LoRa the Semtech sensitivity formula uses the chirp bandwidth BW directly and folds the rest into the demodulator SNR threshold (see [sensitivity-and-mds](sensitivity-and-mds.md)).

**(g) Statistics.** Thermal noise voltage is zero-mean Gaussian. Its envelope is Rayleigh and its detected power is exponentially distributed. Consequences: noise exceeds 2.58× rms 1 % of the time and 3.89× rms 10⁻⁴ of the time (crest factors of 8–12 dB matter for ADC headroom); and averaging a *logarithmic* (dB) display of noise reads low by $10\log_{10}(e)\,\gamma_E = 2.51$ dB ($\gamma_E$ = Euler's constant), which is why spectrum analyzers need a noise-marker correction (verified by Monte-Carlo in `noise_thermal.py`).

### Level 3 — general form and limits of validity
- **Fluctuation–dissipation theorem** (Callen & Welton 1951 [3]): any linear passive system in thermal equilibrium has a one-sided open-circuit noise-voltage spectral density
  $$S_v(f) = 4\,\text{Re}\{Z(f)\}\,\frac{hf}{e^{hf/kT}-1}\ \ \xrightarrow{hf\ll kT}\ \ 4kT\,\text{Re}\{Z(f)\}.$$
  So a capacitor or inductor (reactive) is noiseless; only the dissipative part of an impedance is noisy. An RLC network's noise is that of its real part at each frequency. (Twiss 1955 extended this to non-reciprocal passive networks [10].) A useful consequence: the total noise voltage across a capacitor $C$ shunting any resistor is $\overline{v^2} = kT/C$, independent of $R$ ("kT/C noise" in sample-and-hold and switched-capacitor circuits).
- **Zero-point term.** Quantum field theory adds $\tfrac12 hf$ per mode. It is not "available power" that can heat a load, but it sets the **quantum limit** of a phase-insensitive linear amplifier: added noise temperature of at least about $hf/(2k)$ referred to the input (tens of mK at 1–2 GHz — irrelevant for practical LNAs whose $T_e$ is 30–100 K).
- **Non-equilibrium sources are not thermal.** A transistor's channel, a diode junction, a hot plasma or a switching regulator is not at a single temperature, so $kTB$ does not describe it. Such devices are still *described* by an equivalent noise temperature, but that temperature can be far above (a PA's output noise, a noise diode's ~10⁴ K) or below (a cooled LNA's 5 K) the physical temperature. See [shot-and-flicker-noise](shot-and-flicker-noise.md).
- **Where "white" breaks.** Thermal noise is white until the Planck roll-off (THz) — but the *measured* noise of a real resistor also contains excess (1/f, "current") noise in carbon and thick-film parts when DC flows through them. Metal-film and thin-film resistors are close to pure Johnson noise.

### External noise: ITU-R P.372
ITU-R P.372 [4] characterises the noise an antenna receives from its environment by an **external noise figure** $F_a = 10\log_{10}(T_a/T_0)$ dB, referred to an equivalent lossless antenna. Median man-made noise and galactic noise follow straight lines in $\log f$:
$$F_{am} = c - d\log_{10} f_\text{MHz}\quad\text{(dB above } kT_0B\text{)}$$

| Environment (P.372-13 Table 1) | c | d | $F_{am}$ at 10 MHz | at 30 MHz | at 144 MHz | at 250 MHz |
|---|---|---|---|---|---|---|
| City | 76.8 | 27.7 | 49.1 dB (2.4×10⁷ K) | 35.9 dB | 17.0 dB (1.5×10⁴ K) | 10.4 dB (3200 K) |
| Residential | 72.5 | 27.7 | 44.8 dB | 31.6 dB | 12.7 dB | 6.1 dB (1200 K) |
| Rural | 67.2 | 27.7 | 39.5 dB | 26.3 dB | 7.4 dB | 0.8 dB (350 K) |
| Quiet rural | 53.6 | 28.6 | 25.0 dB | 11.4 dB | −8.1 dB | −15 dB |
| Galactic | 52.0 | 23.0 | 29.0 dB (2.3×10⁵ K) | 18.0 dB | 2.4 dB (500 K) | −3.2 dB (140 K) |

The Table 1 lines are stated valid over 0.3–250 MHz (narrower for quiet-rural and galactic). **At 433 MHz, do not extrapolate them**; P.372-13 Table 3 gives measured European outdoor medians at 425 MHz of **6 dB (city), 4 dB (residential), 3 dB (rural)**, i.e. $T_a \approx$ 1150 K, 730 K and 580 K for an omnidirectional antenna near the ground. P.372 also warns that these data were measured in the 1970s and that modern man-made noise may differ, and that it is often impulsive (non-Gaussian).

Galactic brightness above ~100 MHz scales as $T_b(f) = T_b(f_0)(f/f_0)^{-2.75} + 2.7$ K (P.372 eq. 15). From the 408 MHz sky survey (cold regions ~20 K, typical ~60 K, galactic plane ~200 K): at 433 MHz 20–170 K; at 915 MHz 5–25 K; at 1575 MHz 3–8 K (the P.372 worked example 200 K at 408 MHz → 19.7 K at 1 GHz is reproduced exactly by `noise_thermal.py`).

**Why HF is external-noise limited:** at 10 MHz even a quiet-rural site delivers $F_a \approx 25$ dB (≈ 92 000 K). A receiver with NF = 10 dB ($T_e$ = 2600 K) adds only 0.1 dB to that; improving the receiver NF is pointless. What matters is antenna directivity and siting. At UHF/microwave the opposite holds: the environment can be colder than the receiver, so NF dominates. The crossover for rural sites is around 100–300 MHz.

### Radiometry — when the noise is the signal
A **radiometer** is a receiver whose wanted output *is* the noise power: it measures an antenna temperature. Radio astronomy, passive microwave remote sensing (soil moisture, sea temperature, rain) and every "sky vs load" SDR test are radiometry. The questions are how precisely a noise power can be measured, and what spoils the measurement.

**Level 1 — the radiometer equation.** A total-power radiometer is a filter of noise bandwidth $B$, a square-law (power) detector and an integrator of time $\tau$. It estimates $T_\text{sys} = T_A + T_e$ with an rms error
$$\Delta T = \frac{T_\text{sys}}{\sqrt{B\tau}}\qquad[\text{K}],$$
$B$ in Hz, $\tau$ in s [11]. With 200 K, 2 MHz and 1 s: **0.14 K**, i.e. a noise power measured to 1 part in 1400. A **Dicke** radiometer switches between the antenna and a reference load and subtracts: $\Delta T = 2T_\text{sys}/\sqrt{B\tau}$. Gain wander $\Delta G/G$ adds in quadrature: $\Delta T = T_\text{sys}\sqrt{1/(B\tau) + (\Delta G/G)^2}$ [11]. For a point source of flux density $S$ (W m⁻² Hz⁻¹), unpolarised, received in one polarisation:
$$\Delta T_A = \frac{A_e S}{2k},\qquad A_e = \frac{G\lambda^2}{4\pi}.$$
Units: 1 solar flux unit (sfu) = 10⁻²² W m⁻² Hz⁻¹; 1 jansky = 10⁻²⁶ W m⁻² Hz⁻¹.

**Level 2 — derivations.**
- *Why $1/\sqrt{B\tau}$.* Band-limited noise of bandwidth $B$ carries about $B$ independent complex samples per second. With complex sampling at $f_s = B$ and a flat band the samples are exactly independent. Each $|x|^2$ is exponentially distributed, so its standard deviation equals its mean ($kT_\text{sys}$ per hertz; Level 2 item (g) above). Averaging $N = B\tau$ of them divides the relative scatter by $\sqrt N$, so $\Delta T/T_\text{sys} = 1/\sqrt{B\tau}$. Real sampling gives the same result: $2B\tau$ real samples, each $x^2$ with variance $2\sigma^4$. The error scales with **$T_\text{sys}$**, not $T_A$: a hot receiver makes the measurement noisier even though its offset is subtracted later. Monte-Carlo check: 19.8 / 6.27 / 1.99 K against 20.0 / 6.32 / 2.00 K for $B\tau$ = 10², 10³, 10⁴ at 200 K (`s7_radiometer.py` §1).
- *Dicke switching.* The input is switched at a rate $f_\text{sw}$ much faster than the gain drifts, between the antenna and a load at $T_\text{ref}$, and the two halves are subtracted synchronously. Each half integrates for $\tau/2$, giving an error of $\sqrt2\,T_\text{sys}/\sqrt{B\tau}$. The difference of two independent halves is another $\sqrt2$ worse, hence $2T_\text{sys}/\sqrt{B\tau}$ (MC: 12.66 vs 12.65 K at $B\tau$ = 10³). The benefit is that a gain change now multiplies $T_A - T_\text{ref}$ instead of $T_\text{sys}$. With a balanced reference ($T_\text{ref} \approx T_A$) the drift error disappears: in §3 a 2.1 % rms slow gain wander raised the total-power scatter from 4.47 to 5.63 K (6.16 K predicted), while the Dicke output was unchanged.
- *Gain fluctuations.* A total-power output is $G\,T_\text{sys}$, so a fractional gain change looks exactly like $\Delta T = T_\text{sys}\,\Delta G/G$. It is independent of the thermal scatter, so the two add in quadrature. Gain wander dominates once $\Delta G/G > 1/\sqrt{B\tau}$. For 2 MHz and 1 s that crossover is 0.07 % (0.003 dB), so a 0.01 dB rms drift at 200 K gives 0.48 K, more than 3× the thermal limit. Uncooled SDR tuners drift by tenths of a dB over minutes, which is why integrating longer stops helping after a few seconds unless you switch or calibrate.
- *Beam efficiency.* Split the pattern integral (e) into the main beam and the rest. With $\eta_B = \Omega_{MB}/\Omega_A$, the fraction of the beam solid angle inside the main lobe [11],
  $$T_A = \eta_B\,\bar T_{MB} + (1-\eta_B)\,\bar T_{SL},$$
  where $\bar T_{MB}$ and $\bar T_{SL}$ are the pattern-weighted brightness in the main beam and in the sidelobes. A Yagi with $\eta_B$ = 0.7 whose main beam sees a 60 K sky and whose sidelobes see 290 K ground reads **129 K**; with $\eta_B$ = 0.85, 94 K (§6; this is Example 3's estimate). Remote-sensing retrievals divide out $\eta_B$ and the radiation efficiency. Uncorrected sidelobe pickup ("stray radiation") is the main error of simple radiometers.
- *Point sources.* A source much smaller than the beam delivers a spectral power $\tfrac12 A_e S$ in one polarisation. Half of an unpolarised flux is in each orthogonal polarisation. Dividing by $k$ gives $T_A = A_eS/(2k)$ [11]. The quiet Sun at 410 MHz measured 25–50 sfu in recent Learmonth daily bulletins (e.g. 42 sfu on 2024-01-11) [12]. An 11 dBi Yagi at 433.92 MHz ($A_e$ = 0.478 m²) therefore sees **ΔT_A ≈ 43–87 K, 61 K at 35 sfu** (§4). The Sun's radio disc (≲ 1° at UHF) is tiny against the Yagi's ≈ 57° beam, so the point-source formula applies. Solar radio bursts can exceed the quiet level by orders of magnitude.

**Level 3 — interferometry and aperture synthesis.** Connect two antennas a baseline $b$ apart to two receivers and **cross-multiply** (correlate) their voltages instead of squaring one. A point source in direction $\theta$ from the baseline reaches the two antennas with a path difference $b\cos\theta$. The correlator output is $r \propto S A_e\cos(2\pi b\cos\theta/\lambda)$, a fringe pattern with angular period $\lambda/(b\sin\theta) \approx \lambda/b$ [11]. Three consequences follow:
- *Resolution comes from the baseline, not from the dish.* Each baseline, measured in wavelengths $(u,v)$, samples one 2-D Fourier component (the **visibility**) of the sky brightness. This is the van Cittert–Zernike theorem. As the Earth rotates, each projected baseline traces an arc in the $u$–$v$ plane. With $N$ antennas you get $N(N-1)/2$ baselines, and the image is the inverse Fourier transform of the sampled visibilities, followed by deconvolution such as CLEAN. This is Earth-rotation aperture synthesis. VLBI records each station against an atomic clock and correlates the recordings later.
- *Receiver noise does not bias the output.* Each receiver's own noise is uncorrelated with the other's and averages to zero, as in the cross-correlation phase-noise method ([17 phase noise](../17-test-measurement/phase-noise-measurement.md)). Gain drift multiplies only the (small) source term. For one baseline (real output) the scatter is $\sigma = \sqrt{(T_1T_2 + T_s^2)/(2B\tau)} \to T_\text{sys}/\sqrt{2B\tau}$ for a weak source. Monte Carlo: mean 19.99 K for a 20 K source, std 2.21 vs 2.24 K predicted (§7).
- *Both receivers need a common, phase-stable clock and LO.* Two independent RTL-SDRs are not coherent. A KrakenSDR, a two-channel bladeRF/USRP, or tuners sharing one reference with a phase calibration are. At 433.92 MHz a 10 m east–west baseline (14.5 λ) gives fringes 3.96° apart. The Sun drifts through one fringe every **15.8 min** near transit at declination 0° (5 m: 31.6 min; 20 m: 7.9 min).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $N = kTB$; $-174$ dBm/Hz at 290 K | $hf \ll kT$ (all RF at room temperature) | 125 kHz: −123.0 dBm; 1 MHz: −114.0 dBm |
| $v_n = \sqrt{4kTRB}$ | open-circuit, resistor at $T$ | 50 Ω: 0.895 nV/√Hz; 1 kΩ: 4.0 nV/√Hz |
| $T_e = T_0(F-1)$, $F = 1+T_e/T_0$ | any linear two-port | NF 0.5 dB → 35 K; 1 dB → 75 K; 3 dB → 289 K; 6 dB → 865 K |
| $T_e = (L-1)T_p$; $F = L$ at 290 K | matched passive in equilibrium | 1 dB cable → 75 K; 3 dB → 289 K |
| $T_\text{out} = T_a/L + T_p(1-1/L)$ | antenna through lossy feeder | 50 K sky + 1 dB → 99 K |
| $T_\text{sys} = T_a + T_e$ | system noise at receiver input | GNSS: 100 K + 75 K = 175 K |
| $T_b \propto f^{-2.75}$ | galactic synchrotron, ≳100 MHz | 433 MHz: 20–170 K |
| $F_{am} = c - d\log f$ | P.372 man-made/galactic, 0.3–250 MHz | city 30 MHz: 36 dB |
| $B_n = \frac{\pi}{2}f_{3\,\text{dB}}$ | one-pole RC | Butterworth-3: 1.047 $f_{3\,\text{dB}}$ |
| Log-average reads −2.51 dB | Gaussian noise on log detector | add 2.5 dB to noise markers (analyzer-dependent) |
| $\Delta T = T_\text{sys}/\sqrt{B\tau}$ (total power); $2T_\text{sys}/\sqrt{B\tau}$ (Dicke) | Gaussian noise, $B\tau \gg 1$, stable gain | 200 K, 2 MHz, 1 s: 0.14 K |
| $\Delta T = T_\text{sys}\sqrt{1/(B\tau) + (\Delta G/G)^2}$ | total-power with gain wander | 0.01 dB rms at 200 K → 0.48 K |
| $\Delta T_A = A_eS/(2k)$ | unpolarised point source, one polarisation | quiet Sun 35 sfu, 11 dBi at 434 MHz: 61 K |
| $T_A = \eta_B\bar T_{MB} + (1-\eta_B)\bar T_{SL}$ | beam-efficiency split | η_B 0.7, 60 K sky / 290 K ground: 129 K |
| Fringe spacing $\lambda/b$; period $1/((b/\lambda)\,\omega_E\cos\delta)$ | two-element interferometer, E–W baseline near transit | 10 m at 434 MHz: 3.96°, 15.8 min |
| Sun-noise $G/T = 8\pi k(Y-1)/(S\lambda^2)$ | point source, Y = on/off power ratio | Y 1.15 dB, 35 sfu → −12.0 dB/K |

## Worked examples

**Example 1 — noise in a LoRa channel.** A 50 Ω source at 290 K, bandwidth 125 kHz: $N = -173.98 + 10\log_{10}(125\,000) = -173.98 + 50.97 = -123.0$ dBm (5.0×10⁻¹⁶ W). The open-circuit voltage is $\sqrt{4\cdot1.38\times10^{-23}\cdot290\cdot50\cdot125000} = 316$ nV rms. Into the matched receiver input the voltage is half that (158 nV) and the power is $158\text{ nV}^2/50\ \Omega = 5.0\times10^{-16}$ W — consistent.

**Example 2 — what a cable does to a module.** The E22-400T33D sits at the bottom of a mast with 10 m of cable of 2.6 dB loss (roughly LMR-240 at 915 MHz). Cable $T_e = (10^{0.26}-1)\cdot290 = 238$ K. The SX1268-class receiver has NF ≈ 6 dB ($T_e$ = 865 K), which referred to the cable input becomes $865\times10^{0.26} = 1573$ K. Total $T_e$ = 1811 K ⇒ NF = 8.6 dB. The whole 2.6 dB of cable loss was added to the NF (full cascade in [receiver-cascade-analysis](receiver-cascade-analysis.md); verified in `noise_cascade.py`, example A1).

**Example 3 — does the sky temperature matter for a LoRa ground station?** Take a 433 MHz crossed Yagi pointed at a rocket at 20° elevation. Estimate: main lobe on the sky (galactic ~60 K), sidelobes and back lobe seeing ground (~290 K) with maybe 30 % of the pattern-weighted solid angle → $T_a \approx 0.7\cdot60 + 0.3\cdot290 \approx 130$ K (engineering estimate). Against the module's $T_e$ = 865 K, $T_\text{sys}$ = 995 K vs the datasheet assumption $T_0 + T_e$ = 1155 K: the real noise floor is **0.65 dB better** than the datasheet sensitivity assumes. Add a masthead LNA with $T_e$ = 43 K (NF 0.6 dB) and the system temperature collapses to ~200 K; now the sky/ground split *is* the dominant term, and a site near town with $T_a$ ≈ 1000 K (P.372 Table 3, city) would cost ~7 dB. (Computed in `noise_thermal.py` §7 and `noise_cascade.py` example B.)

**Example 4 — HF receiver.** A 10 MHz receiver with NF 12 dB ($T_e$ = 4300 K) in a residential area: $F_a = 72.5 - 27.7 = 44.8$ dB ⇒ $T_a = 8.8\times10^6$ K. $T_\text{sys}$ is 0.02 dB above $T_a$ alone. A "low-noise" 2 dB NF preamp would change nothing — but a lossy, inefficient antenna (say −20 dB efficiency) would still leave external noise 25 dB above the receiver noise, so small inefficient receive antennas are fine at HF. This is the physical basis of the amateur saying "at HF, receive antennas can be small; at UHF they cannot".

**Example 5 — GNSS antenna.** An upward-looking L1 patch sees mostly cold sky (galactic 3–8 K at 1575 MHz plus a few K of atmosphere) but also ground through its back lobe and low-elevation pattern: $T_a$ ≈ 50–150 K is typical. With an active antenna whose LNA has NF 0.8 dB after 0.3 dB of feed loss, the cascade $T_e$ ≈ 91 K (`noise_cascade.py` example C) and $N_0 = 10\log_{10}(k(100 + 91)) + 30 = -175.8$ dBm/Hz. The GPS L1 C/A minimum received power −128.5 dBm then gives $C/N_0$ = 47.3 dB-Hz.

**Example 6 — lossy, warm antenna.** A chip antenna with 30 % radiation efficiency ($\eta$ = 0.3) on a GNSS board at 330 K contributes $(1-0.3)\cdot330 = 231$ K plus $0.3\times100 = 30$ K from the sky: 261 K, before the LNA. That is why a poor GNSS antenna degrades $C/N_0$ by several dB even with a perfect LNA.

**Example 7 — seeing the Sun with the 433 MHz ground-station Yagi and an SDR (radiometry).** Setup: 11 dBi Yagi ($A_e$ = 0.478 m²), off-Sun $T_A \approx$ 150 K (sky plus ground in the sidelobes, an assumption), quiet Sun 35 sfu → ΔT_A = 61 K (Level 2). Measure total power in $B$ = 2 MHz with the AGC off, at a fixed gain, using power (not log) averaging (`s7_radiometer.py` §5).
- *RTL-SDR V3 alone* (NF 5.4 dB at 437 MHz → $T_e$ = 716 K): $T_\text{sys}$ = 866 K off the Sun, 926 K on it, so **Y_sun = 0.29 dB**. The 1 s radiometer error is 0.61 K, so the Sun is a 100σ detection thermally. But a 0.05 dB gain drift is 10 K, a sixth of the signal. Alternate on-Sun and off-Sun pointing every 30 s (a hand-operated Dicke switch), or swing the Yagi across the Sun and fit a baseline.
- *Masthead LNA* (NF 0.6 dB, 20 dB gain) ahead of the SDR: $T_e$ = 50 K, $T_\text{sys}$ = 200 K, **Y_sun = 1.15 dB**, and a 0.05 dB drift is 2.3 K. The Y-factor also gives the station's figure of merit directly: $G/T = 8\pi k(Y-1)/(S\lambda^2)$ = **−12.0 dB/K**, which matches 11 dBi − 10 log 200 K. This is the "Sun noise" test EME operators use. Its accuracy is limited by knowing $S$ on the day, so take it from the Learmonth or another observatory's bulletin at the nearest frequency.
- *Load vs sky* ([noise-figure measurement](../17-test-measurement/noise-figure-measurement.md)): a 295 K terminator against the sky gives Y = 2.37 dB. That converts to $T_A$ = 150 K only if $T_e$ is known, so measure $T_e$ first with a hot/cold (or noise-source) Y-factor. A sky reading *hotter* than the load at 433 MHz means man-made noise, not the sky.

## Practical notes
- **Use 290 K consistently.** Datasheet sensitivities and noise figures are referred to a source at $T_0$ = 290 K (IEEE/ITU convention). Room temperature is closer to 295–300 K; at 300 K the density is −173.8 dBm/Hz. Singapore outdoor equipment at 35–60 °C has warmer feeders: a 2 dB cable at 330 K adds 193 K instead of 170 K.
- **Resistors:** metal/thin-film resistors show essentially pure Johnson noise; thick-film and carbon-composition resistors add current-dependent excess noise at low frequencies. This matters for audio/baseband and bias networks, not for 50 Ω RF terminations.
- **Measuring antenna temperature with an SDR:** switch the input between a 50 Ω terminator (≈ 295 K) and the antenna, compare noise powers in the same RBW (a "sky vs load" Y-factor). If the antenna reads *hotter* than the load at 433 MHz, you are seeing man-made noise or local interference (laptops, USB 3 hubs, LED drivers, switch-mode supplies, generators at a launch site), not thermal noise. See [17-test-measurement/noise-figure-measurement](../17-test-measurement/noise-figure-measurement.md).
- **The Sun and radio bursts:** pointing a high-gain antenna at the Sun raises $T_a$ substantially (the quiet Sun is a strong UHF source and solar radio bursts can exceed it by orders of magnitude; P.372 Fig. 12 gives the brightness-temperature range). A tracking Yagi following a rocket near the Sun's direction can briefly lose sensitivity. The quiet Sun adds about 60 K to an 11 dBi Yagi at 433 MHz. That is 0.3 dB against an 866 K SDR-only system and 1.2 dB against a 200 K LNA-fronted one (Example 7). Bursts can be far larger.
- **Impulsive man-made noise** (ignition, arcing, switching edges) is not Gaussian. A receiver's error rate in impulsive noise can be much worse than its average noise power suggests; LoRa's long symbols average impulses well, narrowband FSK less so.
- **Spectrum-analyzer noise readings:** convert "dBm per RBW" to dBm/Hz by subtracting $10\log_{10}(\text{RBW}\times\text{noise-bandwidth factor})$ (≈ 1.06 for Gaussian RBW filters) and correct for log averaging (+2.5 dB) unless the analyzer's noise marker already does this. See [spectrum-analyzers](../17-test-measurement/spectrum-analyzers.md).

## Common mistakes & misconceptions
- **"−174 dBm/Hz is a fundamental constant."** It is $kT$ at 290 K. It is the *reference* floor; a real receiver floor is −174 + NF (for a 290 K source) or $10\log_{10}(k(T_a+T_e))$ in general. A cold-sky-pointing antenna with a good LNA can be *below* −174 dBm/Hz (e.g. −177 dBm/Hz for 150 K).
- **"A bigger resistor makes more noise power."** It makes more noise *voltage* ($\propto\sqrt{R}$) but the *available power* is $kTB$ for any $R$. What matters for amplifier design is how the source resistance interacts with the amplifier's voltage and current noise (see noise matching in [noise-figure-and-friis](noise-figure-and-friis.md)).
- **"An attenuator reduces noise."** At the output of a matched attenuator the noise is still ≈ $kT_pB$ — it cannot go below the attenuator's own thermal noise — while the signal drops by $L$. SNR always degrades by $L$ (for a 290 K source). Attenuators are used to *improve match* or *linearity*, never SNR.
- **"The sky is 3 K."** Only toward zenith at microwave frequencies away from the galactic plane, and only for the cosmic background. At 433 MHz galactic emission gives 20–170 K; at 30 MHz tens of thousands of K.
- **"Receiver noise figure is what limits my HF/VHF range."** Below roughly 100–300 MHz, external noise dominates in most places; NF only matters in very quiet sites or with inefficient antennas.
- **Adding noise voltages linearly.** Uncorrelated noises add in *power* (or mean-square voltage): 3 nV/√Hz and 4 nV/√Hz make 5 nV/√Hz, not 7.
- **Using 3 dB bandwidth as noise bandwidth for a gentle filter.** An RC filter's noise bandwidth is 57 % larger than its 3 dB bandwidth (+2 dB of noise).
- **Forgetting that antenna loss is noise.** A 50 %-efficient antenna does not just lose 3 dB of signal; at room temperature it also adds ~145 K of noise. For a GNSS or other low-noise system this double penalty is severe.
- **"Integrate long enough and any temperature step is measurable."** The $1/\sqrt{B\tau}$ law holds only while the gain is stable. Beyond $\Delta G/G \approx 1/\sqrt{B\tau}$, often a few seconds for an SDR, the error stops falling. Switch (Dicke), recalibrate against a load, or correlate two receivers.
- **Putting $T_A$ instead of $T_\text{sys}$ in the radiometer equation.** The receiver's own noise sets the scatter. A 716 K SDR measures a 60 K Sun with 4× the error of a 200 K LNA-fronted system.
- **Dropping the ½ for an unpolarised source.** A single-polarisation antenna (linear, or one sense of CP) receives half the Sun's flux: $T_A = A_eS/(2k)$, not $A_eS/k$.
- **Radiometry with the AGC on or with log averaging.** AGC removes the very power change you want to measure. Log averaging biases noise by −2.51 dB, which cancels in a ratio only if both readings are noise-like.
- **"Fine angular resolution needs a huge dish."** An interferometer resolves about $\lambda/b$ with small antennas on a long baseline. The cost is phase-coherent receivers and the need to synthesise the image.

## How to simulate / verify
- `tools/verify/noise_thermal.py` — kT₀B table, Planck vs Rayleigh–Jeans, resistor noise voltages, lossy-passive $T_e$ vs a slice model, antenna temperature through a feeder, ITU-R P.372 tables and galactic scaling (reproduces the P.372 example), system temperature vs datasheet assumption, log-averaging bias, noise-bandwidth factors, crest factors.
- `tools/verify/s7_radiometer.py` (≈ 3 s, ALL PASS) — total-power and Dicke radiometer Monte Carlo, gain-wander quadrature and Dicke immunity, Sun ΔT_A for an 11 dBi Yagi, SDR Sun Y-factors with and without an LNA, Sun-noise G/T, beam-efficiency split, interferometer fringe spacing/period and correlator sensitivity (MC).
- **SPICE `.noise`** analysis: every resistor is given a $4kTR$ source automatically; integrate output noise over bandwidth and compare with $\sqrt{4kTR_\text{eq}B}$ (domain [16-simulation-tools/spice-circuit-simulation](../16-simulation-tools/spice-circuit-simulation.md)).
- **scikit-rf** `NoisyNetwork`/noise-parameter support can model a lossy line's noise and cascade it with an LNA; check that a matched 3 dB line at 290 K gives NF 3.00 dB.
- **Bench:** measure the noise floor of an SDR with a 50 Ω load, then with a 10 dB attenuator between the load and the SDR — the floor should not change (both look like ~295 K), confirming the equilibrium argument.

## Open questions / gaps
- Quiet-Sun flux is now sourced (Learmonth 410 MHz, 25–50 sfu, giving 43–87 K in an 11 dBi Yagi: Radiometry, Level 2). Flux at 915 MHz and burst statistics (how often, and how strong, during a launch window) are still not quantified. The Sun ΔT values come from a handful of daily bulletins, not a climatology.
- The radiometer, Dicke and correlator formulas are verified by Monte Carlo. A real SDR's gain stability (dB rms over 1–10 min vs temperature) has not been measured; it sets the practical floor of Example 7 (bench task, cross-domain 17).
- Modern (post-2010) man-made noise measurements at 433/868/915 MHz near launch sites and in Singapore are not in the KB. P.372 itself cautions its data are from the 1970s; newer revisions of P.372 (-14 and later) should be checked for updated man-made noise models.
- The pattern-weighted ground/sky split for real Yagis at low elevation (Example 3) is an engineering estimate; NEC modelling with a ground plane (domain 08/16) could compute $T_a$ properly.

## Sources
1. J. B. Johnson, "Thermal agitation of electricity in conductors," *Phys. Rev.* 32, 97–109 (1928). (peer-reviewed) — measurement of thermal noise ∝ R T.
2. H. Nyquist, "Thermal agitation of electric charge in conductors," *Phys. Rev.* 32, 110–113 (1928). (peer-reviewed) — transmission-line derivation; quantum form.
3. H. B. Callen and T. A. Welton, "Irreversibility and generalized noise," *Phys. Rev.* 83, 34–40 (1951). (peer-reviewed) — fluctuation–dissipation theorem; zero-point term.
4. ITU-R Recommendation P.372-13 (09/2016), *Radio noise*, §2 eqs. (1)–(9), §5 Tables 1–5, §6 eq. (14)–(15). https://www.itu.int/rec/R-REC-P.372/en (standard) — $F_a$ definitions, system noise factor with antenna and line losses, man-made and galactic noise coefficients, 425 MHz measured values, galactic spectral index.
5. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, ch. 10 "Noise and nonlinear distortion" (§10.1–10.2). (textbook) — noise temperature, noise of lossy lines, equivalent noise temperature.
6. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall 2011, ch. 2 (§2.3 noise). (textbook) — resistor noise models, noise spectra, kT/C.
7. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley 2016, §2.17 "Antenna temperature". (textbook) — pattern-weighted brightness integral, efficiency term.
8. Keysight Technologies, *Fundamentals of RF and Microwave Noise Figure Measurements*, Application Note 57-1 (5952-8255E). https://www.keysight.com/us/en/assets/7018-06808/application-notes/5952-8255.pdf (app note) — noise temperature/noise figure definitions; passive attenuator NF = loss.
9. `tools/verify/noise_thermal.py` (this KB) — all numerical values on this page.
10. R. Q. Twiss, "Nyquist's and Thevenin's theorems generalized for nonreciprocal linear networks," *J. Appl. Phys.* 26, 599–602 (1955). (peer-reviewed) — noise of general passive networks.
11. J. J. Condon and S. M. Ransom, *Essential Radio Astronomy*, Princeton University Press (2016); online edition, NRAO, ch. 3 https://www.cv.nrao.edu/~sransom/web/Ch3.html (textbook; read 2026-10-12) — antenna temperature of a point source $T_A = A_eS/(2k)$ (eq. 3.48), main-beam efficiency $\eta_B = \Omega_{MB}/\Omega_A$ (eq. 3.58), the radiometer equation $\sigma_T \approx T_s/\sqrt{\Delta\nu\tau}$ (eq. 3.154), gain-fluctuation form (eq. 3.158), Dicke factor 2 (eq. 3.162), the two-element interferometer fringe spacing $\lambda/(b\sin\theta)$ (§3.7.1). Pozar 4th ed. §14.4 "Radiometer systems" treats the same total-power and Dicke results (textbook; cited from the D4 curriculum map, not re-read). All formulas also checked by Monte Carlo [13].
12. Australian Bureau of Meteorology Space Weather Services, "Daily Quiet Sun Radio Fluxes From Learmonth" bulletins, ips-iflux-dailyvalues list archive, e.g. 11 Jan 2024 (410 MHz: 42 sfu, 610 MHz: 66 sfu), https://listserver.ips.gov.au/pipermail/ips-iflux-dailyvalues/2024-January/007098.html (observatory data; read). Other bulletins seen in search listings: 26–51 sfu at 410 MHz across 2008–2026. Units are not stated on the page and are taken as sfu, the standard for this series.
13. `tools/verify/s7_radiometer.py` (this KB) — radiometry numbers above.
