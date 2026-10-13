---
title: Diodes for analog and RF — pn junction, Schottky, PIN, varactor, step-recovery, Zener/TVS
domain: 05-analog-electronics
slug: diodes-schottky-pin-varactor
tags: [diode, shockley-equation, thermal-voltage, junction-capacitance, schottky, detector, pin-diode, rf-switch, varactor, vco-tuning, step-recovery, comb-generator, zener, tvs, esd]
prerequisites:
  - ../00-math-foundations/decibels-and-log-units.md
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
related:
  - bjt-fundamentals-small-signal.md
  - oscillators.md
  - analog-signal-conditioning.md
  - op-amps-real-limitations.md
  - ../06-rf-circuits/detectors-and-power-meters.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../06-rf-circuits/mixers.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../06-rf-circuits/frequency-multipliers-dividers.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../04-real-components-hf/package-parasitics-bondwires.md
  - ../17-test-measurement/noise-figure-measurement.md
level: mixed
confidence: high
last_updated: 2026-10-12
---

# Diodes for analog and RF — pn junction, Schottky, PIN, varactor, step-recovery, Zener/TVS

## Questions this page answers
- What do n-type, p-type and "depletion region" mean, and why does a junction have a built-in voltage?
- What forward voltage should I expect from a silicon, germanium, Schottky or LED diode?
- How do diodes fail?
- How efficient is an RF energy harvester (rectenna) at −30, −10 or 0 dBm?
- Can I power a sensor from ambient RF, or charge a phone across a room with radio waves?
- What does the diode equation actually say, and where do 26 mV and "60 mV per decade" come from?
- Why does a diode's forward voltage drop by about 2 mV per °C?
- Why is a Schottky diode fast and low-drop, and why is it the default RF detector and mixer diode?
- How much DC voltage will a Schottky detector give me for a given RF power, and where does square-law detection stop?
- Why does my zero-bias detector read differently when it gets hot?
- How does a PIN diode act as a current-controlled resistor at RF but a rectifier at low frequency?
- How do I estimate insertion loss and isolation of a series or shunt PIN switch?
- What is the C–V law of a varactor, what is gamma, and how much can I tune a VCO with one?
- Why does a varactor VCO get noisy or distorted when the RF swing is large?
- What is a step-recovery (snap-off) diode and what are comb generators used for?
- Can I put an ordinary TVS or ESD diode on an antenna line?
- Why are Zener diodes noisy, and which voltage has the lowest temperature coefficient?

## TL;DR
- **Shockley law:** $I = I_S\,(e^{V/(nV_T)}-1)$ with $V_T = kT/q = 25.7$ mV at 25 °C. Current changes ×10 per $nV_T\ln 10 \approx 59$ mV (n = 1, 25 °C). Small-signal resistance $r_d = nV_T/I$ (26 Ω at 1 mA). At fixed current $dV_F/dT \approx -1.8$ mV/K for silicon (derived below). Verified by `tools/verify/analog_diodes.py`.
- **Junction capacitance** $C_j = C_{j0}/(1+V_R/\phi)^{\gamma}$, with $\gamma = 1/2$ for an abrupt junction (≈ 0.47 in practice), 1/3 for linearly graded, 0.75–2 for hyperabrupt varactors [1][2]. Forward bias adds *diffusion capacitance* $C_d = \tau_T I/(nV_T)$.
- **Schottky** (metal–semiconductor, majority carriers): low $V_F$ (0.15–0.45 V), no stored minority charge → picosecond switching. Detector current responsivity $\beta = 1/(2nV_T) \approx 18$ A/W; open-circuit voltage responsivity $\gamma_0 = 1/(2(I_S+I_b))$ V/W when matched. Square law holds while the junction RF voltage is ≲ 40 mV peak (1 dB error point) — about −18 dBm for a 50 Ω-terminated detector, but ~−40 dBm if conjugate-matched to its ~9 kΩ video resistance [3][4].
- **PIN** (thick intrinsic layer): forward-biased it is a resistor $R_S = W^2/[(\mu_n+\mu_p)I_F\tau]$ — set by DC current, independent of area — valid well above $1/(2\pi\tau)$ and above the transit frequency ≈ $1300/W^2$ MHz (W in µm) [1]. Reverse-biased it is a small, nearly constant capacitor $C_T = \varepsilon A/W$. Series switch: IL $= 20\log(1+R_S/2Z_0)$, isolation $= 10\log[1+(4\pi f C_T Z_0)^{-2}]$; shunt switch: IL $= 10\log[1+(\pi f C_T Z_0)^2]$, isolation $= 20\log(1+Z_0/2R_S)$.
- **Varactor:** tuning ratio in frequency is only $\sqrt{C_{max}/C_{min}}$ and is diluted by fixed capacitance; $Q = 1/(2\pi f R_S C)$ falls as $1/f$. Rules of thumb: usable in a VCO up to where Q ≈ 10, in a tunable filter up to Q ≈ 100 [2]. A hyperabrupt $\gamma = 2$ gives $f \propto V$ (linear tuning).
- **Step-recovery diode:** stores charge in forward bias, then snaps off in tens to hundreds of ps → impulse/comb generators and harmonic multipliers [6].
- **Zener/TVS:** below ~5 V breakdown is tunnelling (negative tempco), above ~6 V avalanche (positive tempco); ~5–6 V is the flattest. Avalanche is very noisy (that is why noise sources use it). General-purpose TVS parts are hundreds of pF or more — a short at RF; RF lines need ≤ 0.3 pF parts (e.g. 0.2 pF class [5]).

- **Primer:** $\phi = V_T\ln(N_AN_D/n_i^2)$ ≈ 0.78 V for 10¹⁷/10¹⁶ cm⁻³; $V_F$ ≈ 0.6–0.75 V Si, 0.2–0.35 V Ge, 0.25–0.45 V Schottky, ≥ $hc/q\lambda$ for LEDs (1.97 V red, 2.64 V blue floor; 2.8–3.5 V real blue/white) (`tools/verify/s3_primer.py`).
- **Rectennas:** ngspice upper-bound efficiency of an HSMS-2850 at 915 MHz with a realistic matching inductor: **3 % at −40 dBm, 16 % at −30, 31 % at −20, 58 % at 0 dBm**, falling above 0 dBm by breakdown (`tools/verify/s3_rectenna.py`). Ambient RF (−40 to −60 dBm) gives nW. Exposure limits cap what any 2 dBi antenna can collect where people stand at **≈ 131 / 62 / 19 mW** at 433 MHz / 915 MHz / 2.45 GHz — so far-field room-scale phone charging is out by 40–270×.

## Intuition (no math)
**The junction as a hill.** At a pn junction, electrons on the n side and holes on the p side face an energy hill (the built-in potential, ~0.7 V for silicon). Only the few carriers with enough thermal energy climb over. Thermal energies follow a Boltzmann distribution, so each extra $kT/q \approx 26$ mV of forward bias lowers the hill enough to let $e \approx 2.7$ times more carriers over. That exponential is the whole diode equation; everything else is bookkeeping. Heat the diode and more carriers have the energy to cross, so you need *less* voltage for the same current — hence the negative temperature coefficient.

**Two kinds of capacitance.** Reverse bias pulls carriers away from the junction, leaving a carrier-free *depletion layer* — an insulator between two conductors, i.e. a capacitor whose plate spacing grows with reverse voltage. That is a varactor. Forward bias floods the neutral regions with injected minority carriers; that stored charge has to be pulled out before the diode can turn off, which looks like a large *diffusion capacitance* and a reverse-recovery time.

**Schottky: no storage.** In a metal–semiconductor contact, current is carried by majority carriers spilling over a lower barrier (0.5–0.9 eV instead of ~1.1 eV). Lower barrier → lower forward voltage; no minority-carrier storage → nothing to recover → switches in picoseconds. The same low barrier means much higher reverse leakage, which rises steeply with temperature.

**Detector: curvature makes DC.** Near zero bias the I–V curve is a gentle exponential. Wiggle the voltage symmetrically and the positive half pushes out more current than the negative half pulls back, so the average current is not zero — it is proportional to the square of the RF amplitude, i.e. to RF *power*. At large amplitudes the diode instead behaves like a switch that charges a capacitor to the peak — a linear (envelope) detector.

**PIN: a bucket of charge.** A PIN diode has a thick undoped middle. Forward current fills it with electrons and holes that live for a lifetime τ (microseconds). At RF the signal swings far faster than the charge can change, so the bucket just sits there as a *conductor* whose resistance depends on how much charge DC current keeps in it: more DC → less resistance. Reverse-biased the middle is empty, so the diode is just a small fixed capacitor. That is why a PIN diode can switch watts of RF with milliamps of DC. At frequencies low enough for the charge to follow the RF, it becomes an ordinary rectifier again and distorts.

**Varactor: squeeze the plates.** More reverse bias widens the depletion layer, so capacitance falls. Put it in a tank and the resonant frequency rises with control voltage. But capacitance only goes as a weak power of voltage, and frequency as the square root of capacitance, so a big capacitance ratio buys a modest frequency range.

**Snap-off.** A step-recovery diode is designed so that stored charge is removed at an almost constant rate, and when the last charge is gone the current stops abruptly — in tens of picoseconds. That abrupt edge is rich in harmonics.

## The math

### Level 0 — semiconductor primer (doping, depletion, forward voltages, how diodes fail)
*High-school level. Numbers are from `tools/verify/s3_primer.py` §2 (ngspice where marked).*

**Doping.** Pure silicon conducts poorly: at room temperature only about 10¹⁰ electrons per cm³ are free ($n_i$ ≈ 9.65 × 10⁹ cm⁻³ at 300 K [13]), against about 5 × 10²² atoms per cm³. Adding a few parts per million of phosphorus or arsenic (5 outer electrons) gives **n-type** silicon, with free electrons as the majority carriers. Boron (3 outer electrons) gives **p-type**, with "holes", the missing electrons, as the majority carriers. Doping levels of 10¹⁵–10²⁰ cm⁻³ set the resistivity and every junction property below.

**The pn junction and its depletion region.** Where p meets n, electrons diffuse into the p side and holes into the n side and recombine. That leaves a thin layer stripped of free carriers (the **depletion region**) and holding fixed charge: positive donor ions on the n side, negative acceptor ions on the p side. The charge sets up the **built-in potential** $\phi = V_T\ln(N_AN_D/n_i^2)$, which stops further diffusion. For $N_A$ = 10¹⁷ and $N_D$ = 10¹⁶ cm⁻³, φ = 0.78 V. The layer is $W = \sqrt{2\varepsilon_s(\phi+V_R)(1/N_A+1/N_D)/q}$ thick: 0.33 µm at 0 V, 0.91 µm at 5 V reverse. 91 % of it lies on the lightly doped side, which is why the light side sets breakdown and capacitance. The layer acts as a capacitor (31 → 11 nF/cm² over that range), which is the varactor of Level 2.
- **Forward bias** (p positive) lowers the barrier, and current rises exponentially (Level 1).
- **Reverse bias** widens the layer, and only a tiny leakage flows until **breakdown** (Zener/avalanche, Level 3).

**Typical forward voltages** (at a few mA, 25 °C; each decade of current adds ≈ 60 mV × n):

| Diode | $V_F$ | ngspice model check (1 mA / 10 mA) |
|---|---|---|
| Silicon small-signal (1N4148) | 0.6–0.75 V | 0.589 / 0.698 V |
| Silicon power rectifier (1N400x at 1 A) | 0.8–1.1 V | — (datasheet max 1.1 V at 1 A) |
| Germanium (1N34A class) | 0.2–0.35 V | — |
| Schottky, ordinary (HSMS-282x, BAT54 class) | 0.25–0.45 V | 0.311 / 0.429 V |
| Schottky, zero-bias detector (HSMS-285x) | 0.1–0.2 V at µA–1 mA, then $R_S$-limited | 0.191 / 0.479 V |
| LED: IR 940 nm / red 630 / amber 590 / green 525 / blue–white 470 nm | ≈ 1.2–1.5 / 1.8–2.1 / 2.0–2.2 / 2.8–3.4 / 2.8–3.5 V | red LED model 1.89 / 2.03 V |

An LED's $V_F$ is at least the photon energy in eV: $hc/(q\lambda)$ gives 1.32, 1.97, 2.10, 2.36 and 2.64 V for those wavelengths. InGaN green and blue parts sit 0.4–0.8 V above that floor because of heterojunction offsets and series resistance. A 3.3 V rail therefore drives red LEDs easily but blue and white ones with very little headroom for the current-setting resistor (→ [DC basics](../01-circuit-theory/lumped-elements-impedance-admittance.md#level-0--dc-basics-ohms-law-power-si-prefixes)).

**How diodes fail.**
1. **Over-current / over-temperature.** $I^2R_S$ + $V_FI$ heats the junction. Surge ratings ($I_{FSM}$, $I^2t$) cover capacitor-input rectifiers and hot-plug inrush.
2. **Reverse over-voltage.** Above $V_{BR}$ the junction avalanches, and an ordinary diode without avalanche rating is destroyed by the dissipation. Zener and TVS parts are designed to survive it.
3. **ESD.** Small RF Schottky and PIN diodes can be damaged by a few hundred volts of human-body discharge (→ example 4).
4. **Schottky thermal runaway.** Leakage roughly doubles every 10 °C (Level 3, Practical notes). In a hot bay a reverse-biased power Schottky can heat itself into runaway.
5. **Slow-recovery stress.** Stored charge in a pn rectifier makes reverse-current spikes in switchers, which cause heating and EMI; use Schottky or fast-recovery parts.
6. **Long-term degradation.** LEDs lose output with current density and temperature. Detector diodes drift or fail after RF overdrive: check the absolute-maximum RF input and dissipation.

### Level 1 — the equations you use every day

**Shockley diode equation**
$$I = I_S\left(e^{V/(nV_T)} - 1\right),\qquad V_T = \frac{kT}{q}$$
- $I$ (A) current, $V$ (V) junction voltage, $I_S$ (A) saturation current (fA for small silicon junctions, µA for zero-bias Schottkys), $n$ ideality factor (1.0–1.1 for good junctions, up to 2 at high injection or with recombination), $k = 1.380649\times10^{-23}$ J/K, $q = 1.602\times10^{-19}$ C.
- $V_T$ = 25.0 mV at 290 K, 25.7 mV at 25 °C, 25.85 mV at 300 K, 30.9 mV at 85 °C.
- Forward, $V \gg nV_T$: $V = nV_T\ln(I/I_S)$ → a decade of current per $nV_T\ln 10$ = 59.2 mV (n = 1, 25 °C).

**Small-signal (incremental) resistance**
$$r_d = \frac{dV}{dI} = \frac{nV_T}{I + I_S}\approx\frac{nV_T}{I}\quad(26\ \Omega\text{ at 1 mA},\ 2.6\ \Omega\text{ at 10 mA})$$
Plus the ohmic series resistance $R_S$ of the bulk and contacts.

**Junction (depletion) capacitance**
$$C_j(V_R) = \frac{C_{j0}}{(1+V_R/\phi)^{\gamma}}$$
$\phi$ built-in potential (≈ 0.7 V Si, 1.3 V GaAs [2]; 0.3–0.5 V is typical in Schottky SPICE models), $\gamma$ grading exponent (SPICE parameter M).

**Diffusion capacitance (forward bias)**
$$C_d = \tau_T\,\frac{dI}{dV} = \frac{\tau_T\,I}{nV_T}$$
$\tau_T$ transit time (SPICE TT). For a 1N4148-class junction with nanoseconds of storage at 10 mA this is hundreds of pF — why ordinary diodes are slow.

### Level 2 — derivations

**Law of the junction → Shockley.** In equilibrium the minority-hole density on the n side is $p_{n0} = n_i^2/N_D$. A forward bias $V$ lowers the barrier by $qV$; with Boltzmann statistics the hole density at the depletion edge becomes $p_n(0) = p_{n0}e^{V/V_T}$. The excess $p_{n0}(e^{V/V_T}-1)$ diffuses away and recombines with diffusion length $L_p = \sqrt{D_p\tau_p}$, so the excess decays as $e^{-x/L_p}$ and the diffusion current density at $x = 0$ is $J_p = qD_p\,p_{n0}(e^{V/V_T}-1)/L_p$. Adding the electron term,
$$I = qA\,n_i^2\left(\frac{D_p}{L_pN_D}+\frac{D_n}{L_nN_A}\right)\left(e^{V/V_T}-1\right)\ \Rightarrow\ I_S\propto n_i^2 .$$
(Standard treatment: Sedra & Smith ch. 3; Gray et al. ch. 1 [7][8].) Recombination in the depletion layer adds a component $\propto e^{V/2V_T}$, which is why $n \to 2$ at low currents in poor junctions; high injection also drives $n$ toward 2.

**Temperature coefficient.** $n_i^2 \propto T^3 e^{-E_g/kT}$, so $I_S \propto T^{XTI}e^{-E_g/kT}$ (XTI ≈ 3 for pn, ≈ 2 for Schottky in SPICE). With $V = V_T\ln(I/I_S)$ at constant $I$:
$$\frac{dV}{dT} = \frac{V}{T} - V_T\frac{d\ln I_S}{dT} = \frac{V - E_g/q - XTI\cdot V_T}{T}.$$
Silicon, $V = 0.65$ V, $E_g = 1.12$ eV, T = 300 K: $dV/dT = (0.65-1.12-0.078)/300 = -1.83$ mV/K. A Schottky ($E_g$ → barrier 0.69 eV, $V$ = 0.30 V) gives −1.5 mV/K. These are the "−2 mV/°C" rule and its origin (script §1).

**Depletion capacitance and the exponent γ.** Solve Poisson's equation for a one-sided junction whose doping varies with depth as $N(x) = Bx^m$. The depletion width $W$ needed to support $\phi+V_R$ scales as $(\phi+V_R) \propto W^{m+2}$, and $C = \varepsilon A/W$, so
$$C \propto (\phi+V_R)^{-1/(m+2)}\quad\Rightarrow\quad \gamma = \frac{1}{m+2}.$$
Uniform doping ($m = 0$): $\gamma = 1/2$ (abrupt). Linearly graded ($m = 1$): $\gamma = 1/3$. Hyperabrupt varactors have doping that *falls* away from the junction ($m < 0$): $m = -1$ gives $\gamma = 1$, $m = -3/2$ gives $\gamma = 2$.

**Varactor tank tuning.** With only the varactor in an LC tank, $f = 1/(2\pi\sqrt{LC}) \propto (\phi+V_R)^{\gamma/2}$. For $\gamma = 2$, $f \propto \phi+V_R$: linear tuning (script §4 shows constant $df/dV$). For an abrupt junction, $f \propto (\phi+V)^{0.25}$ — most of the tuning happens at low voltage, which is also where the RF swing can forward-bias the junction. Frequency ratio available: $f_{max}/f_{min} = \sqrt{C_{max}/C_{min}}$ with all fixed capacitance included:
$$\frac{f_{max}}{f_{min}} = \sqrt{\frac{C_{fix} + C_{v,max}}{C_{fix}+C_{v,min}}}.$$

**Varactor Q.** A reverse-biased varactor is well modelled as $C_j$ in series with the undepleted-epi and contact resistance $R_S$ [2]:
$$Q = \frac{1}{2\pi f R_S C_j}.$$
Q scales as $1/f$ — a Q of 800 at 50 MHz is 92 at 433 MHz and 16 at 2.45 GHz for $R_S = 0.8\ \Omega$, $C = 5$ pF (script §4). Q rises with reverse bias (less C, less undepleted epi).

**Schottky thermionic emission.** For a barrier $\phi_B$:
$$I = A\,A^{**}T^2 e^{-q\phi_B/kT}\left(e^{qV/nkT}-1\right),$$
with $A^{**}$ the effective Richardson constant (~110 A cm⁻² K⁻² for n-Si [9]). Same exponential form; the prefactor is many orders of magnitude larger than a pn junction's, giving a lower forward voltage for the same current and higher leakage. Choosing a low barrier (p-type silicon or special metals) makes $I_S$ large enough (µA) to detect without bias — the "zero-bias" detector [3][4].

**Square-law detector responsivity (derivation).** Drive the junction with $v = V_p\cos\omega t$ around zero bias. Expand the exponential:
$$i = I_S\left[\frac{v}{nV_T} + \frac{v^2}{2(nV_T)^2} + \dots\right]\ \Rightarrow\ \overline{i} = \frac{I_S V_p^2}{4(nV_T)^2}\quad(\overline{\cos^2}=1/2).$$
The RF power absorbed by the junction conductance $g = I_S/(nV_T)$ is $P = gV_p^2/2 = I_SV_p^2/(2nV_T)$. Dividing,
$$\beta \equiv \frac{\overline{i}}{P} = \frac{1}{2nV_T}\ \ [\text{A/W}]\approx 18.4\ \text{A/W at } n = 1.06,\ 25\ ^\circ\text{C}.$$
The open-circuit DC voltage is $\overline{i}\,R_v$ with video resistance $R_v = nV_T/(I_S+I_b)$ ($I_b$ = any DC bias current), so
$$\gamma_0 = \beta R_v = \frac{1}{2(I_S+I_b)}\ \ [\text{V/W}] .$$
For $I_S = 3$ µA, $\gamma_0 = 1.67\times10^5$ V/W = 167 mV/µW — an ideal ceiling (lossless conjugate match, no $R_S$, no $C_j$). Avago AN969 gives ≈ $0.52/(I_S+I_b)$ [4] — within 4 % of this. A time-domain brute-force average of the diode equation reproduces $\beta$ to 4 digits (script §2). Two real-world factors:
- Junction capacitance steals current from $R_j$ and dumps it in $R_S$. For a matched detector the sensitivity falls by $1/(1+\omega^2C_j^2R_SR_j)$: for the HSMS-285x values that is −0.2 dB at 433 MHz, −0.9 dB at 915 MHz, −4.4 dB at 2.45 GHz, −10 dB at 5.8 GHz (script §2).
- A load $R_L$ divides the output: $V_{out} = V_{oc}R_L/(R_L+R_v)$.

**Square law → linear (exact).** With an open-circuit load, the DC output $V_o$ self-biases the diode until the average current is zero: $I_S[e^{-V_o/nV_T}I_0(a) - 1] = 0$ with $a = V_p/nV_T$ and $I_0$ the modified Bessel function. Hence
$$V_o = nV_T\ln I_0\!\left(\frac{V_p}{nV_T}\right)\ \to\ \begin{cases}\dfrac{V_p^2}{4nV_T} & V_p \ll nV_T\ \text{(square law, } \propto P)\\[2mm] V_p - \tfrac{nV_T}{2}\ln\!\left(2\pi \dfrac{V_p}{nV_T}\right) & V_p \gg nV_T\ \text{(peak/linear)}\end{cases}$$
The output falls 1 dB below the square-law line at $V_p \approx 40$ mV (n = 1.06, 25 °C), and approaches $0.93V_p$ at 1 V (script §2). **Where that is in dBm depends on the voltage step-up in front of the diode**: a 50 Ω-terminated broadband detector ($V_p = \sqrt{2\cdot 50\cdot P}$) reaches it at −18 dBm — the origin of the usual "square law up to about −20 dBm" statement [3][10]; a detector conjugate-matched to $R_v \approx 9$ kΩ gets a $\sqrt{R_v/50}$ voltage gain and leaves square law at about −41 dBm (script §6). Matching buys sensitivity at the cost of square-law range.

**Temperature dependence of the detector.** In square law $V_o = V_p^2/(4nV_T) \propto 1/T$: −0.34 %/K at 25 °C, *before* counting the strong variation of $I_S$ (which changes $R_v$, loading and match). This is why precision detectors use a matched reference diode (dual-diode packages) or temperature-compensated log/RMS detector ICs (→ [detectors page](../06-rf-circuits/detectors-and-power-meters.md)).

**PIN resistance (derivation).** Forward current $I_F$ maintains stored charge $Q = I_F\tau$ in the I-region of width $W$ and area $A$. With electron and hole densities equal (high injection), $n = p = Q/(qAW)$, conductivity $\sigma = q(\mu_n+\mu_p)n = (\mu_n+\mu_p)Q/(AW)$, and resistance
$$R_S = \frac{W}{\sigma A} = \frac{W^2}{(\mu_n+\mu_p)\,I_F\,\tau}$$
— the area cancels [1]. With low-field silicon mobilities (0.135 + 0.048 m²/Vs), $W = 50$ µm, $\tau = 1.5$ µs: $R_S$ = 9.1 Ω at 1 mA, 0.9 Ω at 10 mA (script §3). Real diodes read higher (contact and package resistance; mobility is reduced at high injection): the BAR64-02V is 2.1 Ω at 10 mA, 100 MHz [11].

Validity: the RF must not appreciably change $Q$ in one cycle, $Q \gg I_{RF}/(2\pi f)$ [1], which requires $f \gg 1/(2\pi\tau)$ (~100 kHz for τ = 1.55 µs), and $f$ must exceed the I-region transit-time frequency, ≈ $1300/W^2$ MHz with $W$ in µm (0.52 MHz for 50 µm) [1]. Below that the PIN rectifies and generates harmonics like any diode.

**PIN switching times.** Forward-to-reverse: the stored charge is pulled out by reverse current $I_R$ while recombination continues, giving $T_{FR} = \tau\ln(1+I_F/I_R)$ [1]; a driver that pulls 10× the forward current in reverse gets $T_{FR} \approx 0.095\tau$ (148 ns for τ = 1.55 µs). Reverse-to-forward is limited by filling the I-region and is longer for thick diodes (µs for 175 µm, 0.1–0.5 µs for 50 µm [1]).

**PIN switch formulas (derivation).** A series impedance $Z$ in a matched $Z_0$ line has $S_{21} = 2Z_0/(2Z_0+Z)$; a shunt admittance $Y$ has $S_{21} = 2/(2+YZ_0)$. Substituting:

| Configuration | ON state | OFF state |
|---|---|---|
| Series diode | IL $= 20\log_{10}(1+R_S/2Z_0)$ | Isolation $= 10\log_{10}\!\left[1+\left(\frac{1}{4\pi fC_TZ_0}\right)^2\right]$ |
| Shunt diode | Isolation (diode on) $= 20\log_{10}(1+Z_0/2R_S)$ | IL (diode off) $= 10\log_{10}[1+(\pi fC_TZ_0)^2]$ |

These match the exact two-port S21 to 4 digits (script §3) and the forms in the Skyworks note [1]. Add 6 dB of isolation for a multi-throw switch, because the "off" diode sees the generator voltage halved by the terminated source [1].

**Reverse-bias PIN model.** $C_T = \varepsilon A/W$, valid above the dielectric-relaxation frequency $1/(2\pi\rho\varepsilon)$ of the I-region [1]; below it, the PIN behaves like a varactor. The reverse voltage must hold off the negative RF peak; brief positive RF excursions do not turn it on because turn-on is slow [1].

### Level 3 — limits and subtleties
- **High injection and series resistance.** Above ~1–10 mA in small diodes, $R_S$ dominates and the log-linear I–V droops. For log converters use a diode-connected BJT (n ≈ 1.00 over many decades) — see [BJT page](bjt-fundamentals-small-signal.md).
- **Detector video bandwidth vs sensitivity.** Video resistance $R_v$ with the video bypass capacitor sets the output time constant. Biasing with $I_b$ lowers $R_v$ (faster, lower impedance, less temperature sensitivity) but lowers $\gamma_0 = 1/2(I_S+I_b)$ and adds shot and 1/f noise; a zero-bias diode has only thermal noise $\sqrt{4kTR_v B}$ (17 µV rms for 9 kΩ in 2 MHz, script §8). Tangential signal sensitivity (TSS) of the HSMS-2850 is −57 dBm in a 2 MHz video bandwidth at 915 MHz [3].
- **Varactor large-signal behaviour.** The RF swing modulates $C$; the average capacitance shifts (AM→PM conversion), harmonics appear, and if $V_{pk,RF} > V_R + \phi$ the junction conducts, rectifies, de-Q's the tank and adds noise. Back-to-back (anti-series) varactors cancel even-order terms and let the DC bias see only half the RF swing each. Noise on the tuning line directly frequency-modulates the VCO: $K_V$ (Hz/V) × tuning-line noise (V/√Hz) → FM noise (→ [oscillators](oscillators.md), [phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).
- **Varactor temperature coefficient.** Skyworks give an empirical TCC $= K\gamma/(V+\phi)$ ppm/°C with K ≈ 2300 (abrupt) or 1700 (hyperabrupt) [2]: higher γ → more tuning per volt *and* more drift per degree.
- **PIN distortion** improves with thicker I-region and longer lifetime (more charge relative to RF-induced charge change) at the cost of switching speed [1].
- **Step-recovery physics.** Stored charge $Q_s \approx I_F\tau$ (for $\tau \gg$ drive period) is removed by reverse current in the storage time $t_s \approx \tau\ln(1+I_F/I_R)$ — same physics as PIN $T_{FR}$ — followed by a transition time $t_t$ of tens to ~200 ps [6]. A diode driven by a sinusoid at $f_{in}$ produces a comb of harmonics out to roughly $1/t_t$. Modern alternatives: nonlinear transmission lines, fast logic edges, and PLL synthesis.
- **Breakdown physics.** Heavily doped junctions break down by band-to-band tunnelling (Zener effect) below ~5 V, with negative tempco because the bandgap shrinks with temperature; lightly doped junctions break down by impact ionisation (avalanche) above ~6–7 V with positive tempco. Near 5–6 V the two cancel [7][12]. Avalanche is a multiplication process and so is very noisy — calibrated noise sources for NF measurement use it (→ [NF measurement](../17-test-measurement/noise-figure-measurement.md)); the same noise makes Zeners poor references (→ [power supplies](power-supplies-for-rf-and-analog.md) for bandgap/buried-Zener references).

### Rectennas — far-field RF energy harvesting (efficiency vs input power, ambient budgets, the exposure cap)
A rectenna is an antenna, a matching network and a rectifier diode: the detector of Level 2 run at higher power and optimised for DC *power*, not voltage sensitivity. The physics of the low-power collapse is the detector physics above. Below about 100 mV of RF at the junction the diode works in square law: the DC output scales as $V_p^2$, but the conduction loss and the leakage through $R_v$ do not shrink proportionally, so the efficiency falls roughly in proportion to input power. The matching network can raise the junction voltage, but only up to the limit set by the diode's $C_j$ and $R_S$, and by the matching inductor's own loss, which grows with the step-up ratio.

**Simulated efficiency vs available power** (`tools/verify/s3_rectenna.py`; ngspice at 915 MHz, single series HSMS-2850 with its datasheet SPICE model, $C_j$ = 0.18 pF, $R_S$ = 25 Ω, $V_{BR}$ = 3.8 V). The matching network is modelled as a source of resistance $R_g$ with a parallel tank that resonates $C_j$ and shorts the harmonics. $R_g$ and $R_L$ are optimised at each power.

| Available power | −40 dBm | −30 | −20 | −10 | 0 | +10 | +20 dBm |
|---|---|---|---|---|---|---|---|
| Ideal lossless match | 4.5 % | 20 % | 41 % | 61 % | 70 % | 30 % (breakdown) | — |
| Matching inductor $Q_L$ = 50 | **3.2 %** | **16 %** | **31 %** | **51 %** | **58 %** | 30 % | — |
| HSMS-282x class ($V_{BR}$ 15 V, $Q_L$ = 50) | — | — | — | — | 42 % | 57 % | 67 % |

These are upper bounds: no package or PCB loss, no mismatch, perfect harmonic termination, and an optimum load at every power. Measured rectennas sit on or below this curve: tens of % near −20 dBm, a few % or less below −30 dBm, 50–80 % only at 0 to +20 dBm, which is the survey trend of Valenta and Durgin [14] quoted in [08 inductive coupling](../08-antennas/inductive-coupling-rfid-nfc-wpt.md#far-field-rf-energy-harvesting-rectennas--why-ambient-rf-powers-almost-nothing). Three design lessons follow:
- **Pick the diode for the power level.** Zero-bias, low-barrier diodes (HSMS-285x, SMS7630 class) win at µW. They break down early: the reverse peak is ≈ 2 $V_{DC}$, so efficiency collapses above ~0 dBm. Higher-barrier, higher-$V_{BR}$ diodes win at mW to W.
- **The load is part of the match.** The optimum $R_L$ moves from ≈ 10 kΩ at −30 dBm to ≈ 300 Ω at +20 dBm. A harvester feeding a storage capacitor through a boost converter with maximum-power-point tracking holds the optimum.
- **Without harmonic control** (a plain resistive source) a single half-wave rectifier cannot exceed $4/\pi^2$ ≈ 40.5 %. The quasi-static solution peaks at 38–39 % (ngspice spot check 38.1 %). Real high-efficiency designs short or open the harmonics at the diode, the same idea as class-F amplifiers.

**How much power is there?** Friis with a 2 dBi harvesting antenna (script §3; the 915 MHz efficiency curve is used for every case):

| Source | Received | DC (upper bound) |
|---|---|---|
| Singapore LPWAN limit, 100 mW e.r.p. (164 mW EIRP) at 922 MHz, 3 m | −17.1 dBm (19 µW) | ≈ 7 µW |
| same, 10 m | −27.6 dBm (1.7 µW) | ≈ 0.3 µW |
| FCC 15.247 maximum, 4 W EIRP at 915 MHz, 3 m | −3.2 dBm (0.48 mW) | ≈ 0.27 mW |
| E22-400T33D, 33 dBm into a dipole, 433 MHz, 10 m / 100 m | −8.0 / −28.0 dBm | ≈ 80 / 0.3 µW |
| Ambient cellular/TV/Wi-Fi (typical −40 to −60 dBm, from [08](../08-antennas/inductive-coupling-rfid-nfc-wpt.md)) | 100 nW – 1 nW | ≤ 3 nW – 30 pW |

A dedicated nearby transmitter can therefore run a µW sensor tag (UHF RFID works this way). Ambient RF yields nanowatts: less than the leakage of a supercapacitor or the sleep current of most MCUs.

**Why exposure limits cap "charging across the room".** Anywhere a person may stand, the incident power density must stay below the reference level: ICNIRP 2020 general public $f_{MHz}/200$ W/m² for 400–2000 MHz, 10 W/m² above 2 GHz (→ [RF exposure](../19-regulations-safety/rf-exposure-safety.md)). A receiving antenna collects at most $P = SA_e$ with $A_e = G\lambda^2/4\pi$. With a 2 dBi antenna:

| f | $S_{lim}$ (public) | $A_e$ | Max collected power | 5 W phone charge needs |
|---|---|---|---|---|
| 433 MHz | 2.17 W/m² | 605 cm² | 131 mW | 38 × the limit (26 kW EIRP at 5 m) |
| 915 MHz | 4.58 W/m² | 135 cm² | 62 mW | 81 × the limit (116 kW EIRP at 5 m) |
| 2.45 GHz | 10 W/m² | 19 cm² | 19 mW | 265 × the limit (832 kW EIRP at 5 m) |

Even before rectifier losses and licence EIRP limits, far-field charging of a phone-sized load at room scale needs power densities tens to hundreds of times the public limit. The only ways out are a larger aperture (which needs a larger device), a narrow beam aimed only at an unoccupied target (with safety interlocks), or near-field coupling (→ [inductive WPT](../08-antennas/inductive-coupling-rfid-nfc-wpt.md)). For a rocket this rules out "RF-charging the avionics on the pad"; a µW-class "wake-on-RF" tag is feasible.

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical values |
|---|---|---|---|
| Thermal voltage | $V_T = kT/q$ | — | 25.7 mV @ 25 °C |
| Decade slope | $nV_T\ln 10$ | exponential region | 59 mV (n = 1) |
| Incremental resistance | $r_d = nV_T/I$ | below $R_S$-dominated region | 26 Ω @ 1 mA |
| $V_F$ tempco | $(V-E_g/q-XTI\,V_T)/T$ | constant current | −1.8 mV/K Si, −1.5 Schottky |
| Depletion C | $C_{j0}(1+V_R/\phi)^{-\gamma}$ | reverse / small forward | γ = 0.47–0.5 abrupt, 0.75–2 hyperabrupt |
| Diffusion C | $\tau_T I/nV_T$ | forward | 10s–100s pF for slow Si diodes |
| Detector current responsivity | $\beta = 1/(2nV_T)$ | square law | 18–19 A/W |
| Detector voltage responsivity | $\gamma_0 = 1/[2(I_S+I_b)]$ V/W, × $1/(1+\omega^2C_j^2R_SR_v)$ | matched, square law | 10–170 mV/µW |
| Square-law ceiling | $V_{p,junction} \lesssim 40$ mV for 1 dB error | n ≈ 1.06 | −18 dBm (50 Ω-terminated) |
| Video resistance | $R_v = nV_T/(I_S+I_b) + R_S$ | small signal | 8–9 kΩ (HSMS-2850, 0 bias) |
| PIN on-resistance | $W^2/[(\mu_n+\mu_p)I_F\tau]$ | $f \gg 1/2\pi\tau$, $f > 1300/W^2$ MHz | 1–5 Ω @ 10 mA |
| PIN off capacitance | $\varepsilon A/W$ | above relaxation frequency | 0.1–1 pF |
| PIN $T_{FR}$ | $\tau\ln(1+I_F/I_R)$ | — | 0.1τ for $I_R = 10I_F$ |
| Varactor Q | $1/(2\pi fR_SC)$ | — | falls as 1/f |
| Varactor usable limit | $f_{max} \approx Q_{ref}f_{ref}/10$ (VCO), $/100$ (filter) | rule of thumb [2] | — |
| Varactor breakdown margin | $V_{BR} \ge V_{R,max} + 5$ V | rule of thumb [2] | — |
| Leakage vs T | ×2 per 10 °C | rule of thumb [2] | ×50 from 25→125 °C |
| Built-in potential | $V_T\ln(N_AN_D/n_i^2)$ | pn junction | 0.7–0.9 V Si |
| LED $V_F$ floor | $hc/(q\lambda)$ = 1240/λ(nm) V | — | 1.97 V @ 630 nm |
| Rectenna efficiency (HSMS-2850, 915 MHz, ngspice bound) | — | $Q_L$ = 50 match | 3/16/31/51/58 % at −40/−30/−20/−10/0 dBm |
| Half-wave rectifier, no harmonic control | $\eta \le 4/\pi^2$ | resistive source | 40.5 % |
| Harvest cap at exposure limit | $P_{max} = S_{lim}G\lambda^2/4\pi$ | far field | 62 mW @ 915 MHz, 2 dBi |
| Shunt-C on 50 Ω line | $S_{11} = -j\omega CZ_0/(2+j\omega CZ_0)$ | — | 1 pF → RL 12 dB @ 1.575 GHz |

## Worked examples

### 1. Forward-power monitor for a 433 MHz LoRa transmitter (zero-bias Schottky)
Goal: a DC voltage that tracks the output of a 2 W (33 dBm) EBYTE E22-400T33D-class module, read by the flight computer's ADC.

1. Stay in square law with margin: target −25 dBm at a 50 Ω-terminated HSMS-2850 detector. Coupling + padding needed: 33 − (−25) = 58 dB (e.g. a 30 dB coupler + 28 dB of attenuation, or a 40 dB coupler + 18 dB pad).
2. Junction peak voltage: $V_p = \sqrt{2\cdot 50\cdot 10^{-2.5}\ \text{mW}} = \sqrt{100\times3.16\times10^{-6}} = 17.8$ mV (well under the 40 mV 1-dB point).
3. Open-circuit output: $V_p^2/(4nV_T) = (17.8\ \text{mV})^2/(4\times 27.2\ \text{mV}) = 2.90$ mV.
4. Load $R_L = 100$ kΩ, $R_v ≈ 9.1$ kΩ: $V_{out} = 2.90\times100/109 = 2.66$ mV (script §8).
5. Consequence: 2.7 mV full-scale is ~3 LSB of a 12-bit, 3.3 V ADC. You need gain ×300–1000 from a **zero-drift (chopper) op-amp** because a 1 mV offset is 40 % of the signal (→ [op-amps](op-amps-real-limitations.md)); and the output drifts ~−0.34 %/K plus $I_S$ drift — use a dual matched diode with the second diode unexcited as a temperature reference, or use a log detector IC (→ [detectors](../06-rf-circuits/detectors-and-power-meters.md)).

Check with ngspice at −30 dBm (netlist below): 0.809 mV simulated vs 0.842 mV hand estimate; the 4 % difference is diode loading of the 50 Ω node and the small large-signal correction (script §7).

### 2. PIN T/R or antenna-select switch at 433 MHz (BAR64-02V-class)
Data: $R_S = 2.1\ \Omega$ at 10 mA, $C_T = 0.13$ pF, τ = 1.55 µs [11].
- Series diode ON: IL $= 20\log(1+2.1/100) = 0.18$ dB.
- Series diode OFF: isolation $= 10\log[1+(1/(4\pi\cdot433\text{ MHz}\cdot0.13\text{ pF}\cdot50))^2] = 29.0$ dB (script §3). At 2.45 GHz the same diode gives only 14 dB.
- Shunt diode ON: isolation $= 20\log(1+50/4.2) = 22.2$ dB; shunt diode OFF costs only 0.0003 dB at 433 MHz.
- Series-shunt ("L" or "T") combinations add isolation. Package inductance (~0.5–1 nH) and pad capacitance reduce the off-state isolation further — simulate with the vendor S-parameters (→ [package parasitics](../04-real-components-hf/package-parasitics-bondwires.md)).
- Lowest frequency: $1/(2\pi\tau) = 103$ kHz — 433 MHz is 4000× above it: fine.
- Bias: from 3.3 V with $V_F \approx 0.85$ V at 10 mA, $R = (3.3-0.85)/0.01 \approx 240\ \Omega$, fed through an RF choke whose self-resonance is above 433 MHz, with DC-blocking capacitors on the RF ports.
- Switching speed: with 10 mA forward and a driver that sinks 100 mA momentarily (a small capacitor in parallel with the bias resistor is the classic "speed-up" trick), $T_{FR} \approx 0.095\times1.55\ \mu\text{s} = 148$ ns.

### 3. Varactor-tuned 433 MHz VCO tank
Choose $L = 22$ nH. Needed total capacitance at 433 MHz: $C = 1/[(2\pi f)^2L] = 6.14$ pF. An abrupt varactor with $C_{j0} = 10$ pF, φ = 0.7 V, γ = 0.47 swings 6.59 pF (1 V) → 2.78 pF (10 V), a 2.4:1 ratio. Coupling it through $C_c = 3.3$ pF and adding $C_{fix} = 4.1$ pF:

| $V_{tune}$ | $C_{var}$ | series with 3.3 pF | total | $f$ |
|---|---|---|---|---|
| 1 V | 6.59 pF | 2.20 pF | 6.30 pF | 427.5 MHz |
| 2 V | 5.30 pF | 2.03 pF | 6.13 pF | 433.2 MHz |
| 4 V | 4.09 pF | 1.83 pF | 5.93 pF | 440.8 MHz |
| 10 V | 2.78 pF | 1.51 pF | 5.61 pF | 453.1 MHz |

(script §8). A 2.4:1 capacitance ratio became a 6 % tuning range: exactly what you want for a VCO that must cover 430–450 MHz with low $K_V$ (≈ 3–8 MHz/V here), because low $K_V$ means less FM from tuning-line noise. The series $C_c$ also divides the RF voltage across the varactor, reducing the large-signal problems of Level 3. Check Q: with $R_S = 0.8\ \Omega$ at ~5 pF, Q ≈ 92 at 433 MHz — acceptable for a VCO by the Q ≥ 10 rule [2], but the tank Q is shared with the inductor (→ [inductors](../04-real-components-hf/inductors-at-rf.md)).

### 4. ESD protection on a GNSS antenna input (1575.42 MHz)
A shunt capacitance $C$ on a 50 Ω line (script §5):

| C | IL @ 1575 MHz | Return loss @ 1575 MHz |
|---|---|---|
| 0.2 pF (RF-grade TVS [5]) | 0.01 dB | 26 dB |
| 0.5 pF | 0.07 dB | 18 dB |
| 1 pF (typical "low-C" USB ESD array) | 0.26 dB | 12 dB |
| 5 pF | 4.0 dB | 2.2 dB |
| 30 pF | 17.5 dB | 0.1 dB |

Loss ahead of the first LNA adds directly to the noise figure (→ [NF & Friis](../07-noise-linearity/noise-figure-and-friis.md)), so a 1 pF part costs ~0.3 dB of GNSS sensitivity and mistunes the match; a general-purpose SMBJ-class TVS (hundreds of pF or more) is a short at RF. Use a ≤ 0.3 pF RF TVS, or — if the port does not carry DC to an active antenna — a shunt inductor to ground that is high-impedance at 1575 MHz but a DC path for ESD charge. With an active antenna fed through the coax, keep the bias-tee path in mind.

## Practical notes
- **Part families (check current datasheets):** zero-bias detectors — Broadcom HSMS-285x (Is = 3 µA, Rs = 25 Ω, Cj0 = 0.18 pF [3]), Skyworks SMS7630 class; biased/general Schottky detectors and mixers — HSMS-282x/286x, SMS7621 class; generic power Schottky (BAT54, SS14) are *not* RF detectors (large C, low Is). PIN — BAR64/BAP64 class for switches/attenuators, thin-I-region PINs for limiters. Varactors — hyperabrupt SMV12xx / BB8xx class for UHF VCOs.
- **Detector layout:** keep the diode, RF termination and video bypass capacitor tight; the video bypass must be a good short at RF but small enough for the needed video bandwidth ($\tau = R_vC$). Use a matched dual diode for temperature compensation.
- **Detector ADC interface:** mV-level DC with ~9 kΩ source impedance — buffer with a low-bias-current, zero-drift op-amp; filter before the ADC (→ [signal conditioning](analog-signal-conditioning.md)).
- **PIN bias networks:** every RF port needs a DC block; the bias feed needs a choke or λ/4 line; add RC filtering so digital noise on the control line does not modulate $R_S$. Budget DC current: several diodes × 10 mA matters on a 1S battery.
- **Varactor tuning line:** RC-filter it heavily (it is a direct FM input); use a clean, low-noise supply for the tuning DAC or PLL charge pump.
- **Reverse leakage of Schottkys** rises steeply with temperature — a concern for sample-and-hold, peak detectors and "ideal diode" ORing in hot avionics bays.
- **Diode as protection:** clamp diodes to rails (BAT54S, BAV99) protect ADC inputs but inject current into the rail and add capacitance and leakage; see [analog signal conditioning](analog-signal-conditioning.md).

## Common mistakes & misconceptions
- **"A diode drops 0.7 V."** It drops whatever the exponential says at that current and temperature: 0.55 V at 10 µA, 0.75 V at 10 mA for a small Si junction, and a Schottky can be 0.15 V at µA currents.
- **Using $V_T = 26$ mV at any temperature.** At 85 °C it is 30.9 mV (+20 %), which moves bias points and detector outputs.
- **Assuming square law up to −20 dBm regardless of the matching network.** The limit is the junction voltage (~40 mV peak); a high-Q match raises the voltage and lowers the square-law ceiling in dBm (derivation above).
- **Measuring detector sensitivity into a scope's 1 MΩ vs a 10 kΩ ADC input and wondering why they differ.** $V_{out} = V_{oc}R_L/(R_L+R_v)$.
- **Thinking a PIN diode "switches like a transistor" at any frequency.** Below ~$1/(2\pi\tau)$ and the transit frequency it rectifies; at the other extreme, its off-capacitance kills isolation at high GHz.
- **Treating varactor capacitance ratio as frequency ratio.** Frequency goes as the square root and is diluted by strays and fixed capacitors.
- **Forgetting that RF swing adds to the varactor bias.** At low tuning voltage the RF peak can forward-bias it.
- **Putting a general-purpose TVS on an antenna line** (hundreds of pF) or even a 1 pF USB ESD array on a GNSS input (0.3 dB NF, mismatch).
- **Using a Zener as a precision reference.** Low-voltage Zeners have soft knees and tempco; all have avalanche noise. Use a bandgap or buried-Zener reference IC.
- **"Free energy from ambient RF."** Ambient levels are −40 to −60 dBm, and a rectifier at −40 dBm converts a few % at best: nW. Harvesting works only with a dedicated transmitter within metres.
- **Quoting a rectenna's peak efficiency (70–80 % at +10 dBm) for a −30 dBm budget.** Efficiency is a steep function of input power; use the curve at your power.
- **"Wireless charging across the room is just a matter of a bigger transmitter."** Exposure limits cap the power density where people are, so a 2 dBi antenna can collect at most tens of mW.
- **Using a 0.7 V diode drop for an LED or a Schottky** — LEDs are 1.3–3.5 V depending on colour; Schottkys are 0.2–0.45 V.
- **"Schottkys have no capacitance."** They have no *diffusion* (storage) capacitance; junction capacitance is still there and is what limits detectors above a few GHz.

## How to simulate / verify
- **Python:** `tools/verify/analog_diodes.py` checks every number on this page (thermal voltage and tempco; responsivity derivation plus time-domain check; exact Bessel square-law→linear curve; Cj roll-off; PIN $R_S$, switch formulas vs exact S21; varactor tuning table; TVS capacitance vs RL/IL; ngspice detector run).
- **ngspice (bundled with KiCad; run via `tools/verify/analog_ngspice.py`):** zero-bias detector at 433 MHz, −30 dBm available from a 50 Ω source into a 50 Ω termination:
```spice
* HSMS-2850 zero-bias detector at 433 MHz, 50-ohm terminated, -30 dBm available
Vs src 0 SIN(0 20m 433MEG)
Rsrc src in 50
Rterm in 0 50
D1 in out HSMS2850
Cv out 0 100p
RL out 0 100k
.model HSMS2850 D(IS=3e-6 N=1.06 RS=25 CJO=0.18p VJ=0.35 M=0.5 EG=0.69 XTI=2 BV=3.8 IBV=3e-4)
.options temp=25
.tran 0.05n 40u 30u 0.05n
.end
```
  Average `v(out)` over the saved window → 0.81 mV. Sweep the source amplitude: in square law $V_{out} \propto P$ (×10 in DC volts per +10 dB of RF power; slope 1 on a log $V_{out}$ vs log $P$ plot), in linear detection $V_{out} \propto V_p \propto \sqrt P$ (slope 1/2).
- **Primer and rectenna:** `tools/verify/s3_primer.py` (built-in potential, depletion width, LED photon-energy floor, ngspice $V_F$ of 1N4148 / HSMS-282x / HSMS-2850 / LED models) and `tools/verify/s3_rectenna.py` (ngspice 915 MHz rectenna efficiency vs power with ideal and $Q_L$ = 50 matching, HSMS-282x at high power, the $4/\pi^2$ resistive-source ceiling with an ngspice spot check, Friis budgets, exposure cap). Outputs in `*_output.txt`.
- **PIN switch:** model the ON diode as $R_S$ + package L and the OFF diode as $C_T$ ∥ $R_P$ + L; use vendor S-parameters in scikit-rf or Qucs-S for accurate isolation.
- **Varactor:** use `.model` with CJO, VJ, M fitted to the datasheet C–V curve (Skyworks publish SPICE parameters for hyperabrupt parts [2]); simulate the VCO tank with `.ac` across tuning voltages, and a harmonic-balance or long transient for large-signal effects.
- **Bench:** measure a detector's transfer curve with a signal generator and step attenuator; check PIN IL/isolation with a NanoVNA (→ [NanoVNA practical](../17-test-measurement/nanovna-librevna-practical.md)).

## Open questions / gaps
- Noise spec interpretation for zero-bias detectors (datasheet quotes −162 dBV/Hz at 100 Hz, which is below $4kTR_v$ for the stated $R_v$; the measurement conditions were not found). Needs the full AN on detector noise.
- AN969's text did not extract cleanly; its exact sensitivity expression (≈ 0.52/(Is+Ib)) is taken from partially garbled text and agrees with the derivation to 4 %.
- High-injection mobility values for PIN $R_S$ estimates are not tabulated here; the formula is used for scaling, and datasheet $R_S$(I) curves should be used for design.
- Step-recovery comb-generator design detail (drive network, impulse shaping) is left to [frequency multipliers](../06-rf-circuits/frequency-multipliers-dividers.md).

## Sources
1. Skyworks Solutions, *Design With PIN Diodes*, application note 200312E (2021). https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/1-100/Design_With_PIN_Diodes_200312E.pdf — PIN models ($R_S$, $C_T$, transit/relaxation limits), switching times, switch formulas, thermal model. (app note)
2. Skyworks Solutions, *Varactor Diodes*, application note 200824A (2008). https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/1-100/200824A.pdf — γ, φ, Q formula and 1/f scaling, VCO/filter Q limits, breakdown margin, leakage vs temperature, TCC. (app note)
3. Avago/Broadcom, *HSMS-285x Surface Mount Zero Bias Schottky Detector Diodes* datasheet. https://media.digikey.com/pdf/Data%20Sheets/Avago%20PDFs/HSMS-285x.pdf — SPICE parameters, $R_v$ formula, 40 mV/µW and −57 dBm TSS at 915 MHz, small-signal limit ~−20 dBm, 915 MHz matching network. (datasheet)
4. Avago, *The Zero Bias Schottky Detector Diode*, Application Note 969. http://people.ee.ethz.ch/~mzahner/PPS-EMrad/material/literature/RF-Detectors_Receivers/ — role of $I_S$ in video resistance and sensitivity. (app note; text extraction partial)
5. Infineon ESD0P2RF ultra-low-capacitance TVS diode — 0.2 pF, linear to 6 GHz, 20 kV ESD. EDN product announcement https://www.edn.com/infineon-introduces-worlds-smallest-esd-protection-diode-for-rf-antennas/ and Infineon AN178 *ESD Protection for RF Antennas*. (datasheet / app note)
6. Hewlett-Packard, *Pulse and Waveform Generation with Step Recovery Diodes*, Application Note 918 (1967/1984). https://hpmemoryproject.org/an/pdf/an_918.pdf — SRD operation, 100–200 ps pulses. (app note)
7. A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th/8th ed., Oxford — ch. 3–4 (pn junction physics, diode models, Zener). (textbook)
8. P. R. Gray, P. J. Hurst, S. H. Lewis, R. G. Meyer, *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley 2009 — ch. 1 (junction capacitance, diffusion capacitance, breakdown). (textbook)
9. S. M. Sze, K. K. Ng, *Physics of Semiconductor Devices*, 3rd ed., Wiley 2007 — ch. 3 (metal–semiconductor contacts, thermionic emission, Richardson constant). (textbook)
10. Avago, *Square Law and Linear Detection*, Application Note 986. https://www.rf-microwave.com/app/resources/uploads/diodes/AN986.pdf — square-law region up to about −20 dBm. (app note)
11. Infineon, *BAR64-02V* RF PIN diode datasheet. https://www.infineon.com/dgdl/Infineon-BAR64-02V-DS-v01_01-EN.pdf?fileId=5546d462689a790c01690f0247ae38fc — 2.1 Ω @ 10 mA/100 MHz, 0.13 pF, τ = 1.55 µs. (datasheet; values via vendor listing)
12. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 1 (diodes, LEDs, rectifiers), ch. 9 (voltage references, Zener tempco and noise). (textbook)
13. P. P. Altermatt et al., "Reassessment of the intrinsic carrier density in crystalline silicon in view of band-gap narrowing," *J. Appl. Phys.* 93, 1598 (2003) — $n_i$ = 9.65 × 10⁹ cm⁻³ at 300 K. (peer-reviewed)
14. C. R. Valenta, G. D. Durgin, "Harvesting wireless power: survey of energy-harvester conversion efficiency in far-field, wireless power transfer systems," *IEEE Microwave Magazine* 15(4), 108–120, 2014 — measured RF-to-DC efficiency vs input power across published rectennas. (peer-reviewed; cited for the trend, figure not re-read)
15. ICNIRP, "Guidelines for limiting exposure to electromagnetic fields (100 kHz to 300 GHz)," *Health Physics* 118(5), 483–524, 2020 — Table 5 reference levels (via [19/rf-exposure-safety](../19-regulations-safety/rf-exposure-safety.md)). (standard/peer-reviewed)
16. Broadcom (Avago), *HSMS-282x Surface Mount RF Schottky Barrier Diodes* datasheet — SPICE parameters (IS 2.2e-8, N 1.08, RS 6 Ω, CJ0 0.7 pF, BV 15 V). (datasheet)
