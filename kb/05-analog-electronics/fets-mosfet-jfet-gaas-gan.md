---
title: FETs — MOSFET, JFET, GaAs MESFET/pHEMT, GaN HEMT, LDMOS (and which device for which job)
domain: 05-analog-electronics
slug: fets-mosfet-jfet-gaas-gan
tags: [mosfet, square-law, velocity-saturation, gm-over-id, subthreshold, jfet, gaas, mesfet, phemt, hemt, 2deg, gan, ldmos, device-selection, gate-bias, bias-sequencing, power-mosfet, rds-on]
prerequisites:
  - bjt-fundamentals-small-signal.md
  - diodes-schottky-pin-varactor.md
related:
  - amplifier-topologies.md
  - low-noise-analog-design.md
  - power-supplies-for-rf-and-analog.md
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../13-pcb-rf-layout-emc/thermal-management-rf.md
  - ../18-components-parts/lna-pa-gain-block-mmics.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# FETs — MOSFET, JFET, GaAs MESFET/pHEMT, GaN HEMT, LDMOS (and which device for which job)

## Questions this page answers
- What is the MOSFET square law, and why does it stop working in modern short-channel transistors?
- What is the $g_m/I_D$ design method and why do analog designers love it?
- Why does a MOSFET give less transconductance per milliamp than a BJT?
- When should I use a JFET instead of a BJT or op-amp input?
- What is a HEMT/pHEMT and why are GaAs pHEMTs the classic lowest-noise LNA device at 0.5–20 GHz?
- Why is everyone using GaN for power amplifiers?
- What does LDMOS do that GaN does not (and vice versa)?
- Why must I apply the negative gate voltage before the drain voltage on GaAs/GaN amplifiers?
- Which transistor technology should I pick for a given frequency, power and noise requirement?
- Will my pyro-channel MOSFET really turn on fully with a 3.3 V GPIO?
- Why does a CMOS op-amp have millivolts of offset, why are voltage references ≈ 1.2 V, and why can't a CMOS radio chip swing many volts into its antenna?

## TL;DR
- **Long-channel MOSFET (saturation):** $I_D = \tfrac12\mu C_{ox}\tfrac WL V_{ov}^2(1+\lambda V_{DS})$, $V_{ov} = V_{GS}-V_{th}$; $g_m = 2I_D/V_{ov}$; $f_T \approx 3\mu V_{ov}/(4\pi L^2)$. Short channels velocity-saturate: $I_D \to WC_{ox}v_{sat}V_{ov}$, $g_m \to WC_{ox}v_{sat}$, $f_T \to \sim v_{sat}/(2\pi L)$. The long-channel formula *over*-predicts at 180 nm (118 vs ≲ 88 GHz, `tools/verify/analog_fet.py` §1).
- **$g_m/I_D$** (S/A = 1/V) summarises the operating point: ≈ $1/(nV_T)$ ≈ 30 /V in weak inversion (efficient, slow), $2/V_{ov}$ ≈ 5–10 /V in strong inversion (fast, power-hungry). A BJT is always $1/V_T$ = 38.7 /V [1][2].
- **JFET:** $I_D = I_{DSS}(1-V_{GS}/V_P)^2$, $g_{m0} = 2I_{DSS}/|V_P|$. Picoamp gate current → negligible current noise → best choice for high-impedance sources. BF862: $I_{DSS}$ 10–25 mA, $y_{fs}$ 35–45 mS, $e_n$ 0.8 nV/√Hz at 100 kHz, $C_{iss}$ 10 pF [3]; square-law estimate 37.5 mS (script §3).
- **HEMT/pHEMT:** electrons travel in an undoped 2-D electron gas at a heterojunction (high mobility, high velocity) → lowest NF at 0.5–20 GHz. ATF-54143 (enhancement-mode, single positive supply): NF 0.3 dB / 23 dB gain at 900 MHz, OIP3 35.5 dBm at 3 V/60 mA [4].
- **GaN HEMT:** 3.4 eV bandgap → ~10× the breakdown field of Si/GaAs, plus a dense 2DEG (~10¹³ cm⁻²) → 6–10 W/mm power density at 28–48 V [5]. High voltage means the optimum load for 10 W at 28 V is ≈ 31 Ω (vs ≈ 1 Ω at 5 V) — easy broadband matching (script §4). Depletion-mode: CGH40010F $V_{GS(th)}$ −3.8…−2.3 V, $V_{GS(Q)}$ ≈ −2.7 V at 28 V/200 mA, $V_{GS}$ limits −10/+2 V [6].
- **LDMOS:** rugged, cheap silicon for 28–50 V PAs from HF to ~3.5 GHz; GaN wins on bandwidth, efficiency and frequency.
- **Bias safely:** depletion-mode devices (JFET, MESFET, D-pHEMT, GaN) are *on* at $V_{GS}$ = 0. Gate negative first, then drain; drain off first, then gate. Threshold spread (1.5 V on the CGH40010F) forces per-device adjustment or an active bias controller.
- **Power MOSFET gate drive:** $V_{GS(th)}$ is specified at ~250 µA, not "on". Use $R_{DS(on)}$ specified at your actual drive: AO3400A is ≤ 48 mΩ at 2.5 V, ≤ 32 mΩ at 4.5 V; a fitted model gives ≈ 38 mΩ at 3.3 V (script §6) [7].

## Intuition (no math)
A FET is a voltage-controlled resistor with a very clever geometry. A conducting channel runs from source to drain; the gate, separated by an insulator (MOSFET), a reverse-biased junction (JFET) or a Schottky barrier (MESFET/HEMT), sets how many carriers are in the channel. Because the gate draws (almost) no DC current, FETs are voltage-driven and ideal for high-impedance inputs and switches.

Current in a FET is *drift*: carriers pushed by the drain field. Doubling the gate overdrive both adds carriers and, near pinch-off, adds more voltage headroom — hence the square law. But carriers can't go faster than a saturation velocity (~10⁵ m/s in Si). In a short channel they hit that limit, so current becomes linear in overdrive and transconductance stops improving with more current. Contrast the BJT, whose current is *diffusion* over a barrier: exponential in voltage, so transconductance per unit current is the thermodynamic maximum $1/V_T$. A MOSFET approaches that only in weak inversion, where it too is a barrier device (subthreshold conduction).

For speed you want carriers that are fast (high mobility and saturation velocity) and a short trip (short gate). Compound semiconductors deliver fast electrons: GaAs electrons are ~5× more mobile than silicon's. A HEMT goes further: it puts the electrons in an undoped layer right next to a doped wider-bandgap layer that donated them, so they move without bumping into the dopant ions — a "2-D electron gas" (2DEG). Low scattering means high speed and low noise.

For power you want to swing large voltage *and* current. Voltage is limited by the field at which the material avalanches — set by bandgap. GaN's bandgap (3.4 eV) is three times silicon's, and its breakdown field about ten times higher, so a GaN transistor the size of a GaAs one can stand off 5–10× the voltage while carrying high current in its dense 2DEG. Higher voltage at the same power also means higher impedance: a 28 V GaN device wants a load near 50 Ω, while a 3.6 V phone PA wants a fraction of an ohm, which is lossy and narrowband to match.

## The math

### Level 1 — the device laws

**MOSFET (n-channel, long channel)**, $V_{ov} = V_{GS}-V_{th}$:
- Triode ($V_{DS} < V_{ov}$): $I_D = \mu C_{ox}\frac WL\left(V_{ov}V_{DS} - \tfrac12V_{DS}^2\right)$; small $V_{DS}$: $R_{DS(on)} = 1/[\mu C_{ox}(W/L)V_{ov}]$.
- Saturation ($V_{DS} \ge V_{ov}$): $I_D = \tfrac12\mu C_{ox}\frac WL V_{ov}^2(1+\lambda V_{DS})$.
- $g_m = \mu C_{ox}\frac WLV_{ov} = \dfrac{2I_D}{V_{ov}} = \sqrt{2\mu C_{ox}\tfrac WL I_D}$, $r_o = 1/(\lambda I_D)$, $g_mr_o = 2/(\lambda V_{ov})$.
- Symbols: µ carrier mobility in the inversion layer (m²/V s; ~0.03–0.05 for electrons in Si), $C_{ox} = \varepsilon_{ox}/t_{ox}$ (F/m²), $W, L$ gate width and length (m), λ channel-length modulation (1/V, ∝ 1/L).

**Weak inversion (subthreshold)** ($V_{GS} < V_{th}$): $I_D \approx I_0\frac WL e^{(V_{GS}-V_{th})/(nV_T)}$, $n$ ≈ 1.2–1.5 → $g_m = I_D/(nV_T)$ and a swing of $nV_T\ln10$ ≈ 70–90 mV/decade.

**JFET** (and depletion-mode MESFET, approximately): $I_D = I_{DSS}\left(1-\dfrac{V_{GS}}{V_P}\right)^2$ for $V_P < V_{GS} \le 0$ (n-channel, $V_P < 0$), $g_m = g_{m0}\sqrt{I_D/I_{DSS}}$, $g_{m0} = 2I_{DSS}/|V_P|$.

**Capacitances:** $C_{gs}$ (≈ $\tfrac23WLC_{ox}$ + overlap in saturation), $C_{gd}$ (overlap; the Miller capacitance), $C_{ds}$/$C_{db}$. Power-MOSFET datasheets give $C_{iss} = C_{gs}+C_{gd}$, $C_{oss} = C_{ds}+C_{gd}$, $C_{rss} = C_{gd}$, and total gate charge $Q_g$ (switching time ≈ $Q_g/I_{drive}$).

**Transition frequency:** $f_T = g_m/[2\pi(C_{gs}+C_{gd})]$.

### Level 2 — derivations

**Square law.** The inversion charge per unit area at position $x$ along the channel is $Q_n(x) = C_{ox}[V_{GS} - V_{th} - V(x)]$. Drift current $I_D = W\mu Q_n(x)\,dV/dx$. Integrating from $V = 0$ at the source to $V_{DS}$ at the drain over length $L$:
$$I_D = \mu C_{ox}\frac WL\left[V_{ov}V_{DS}-\frac{V_{DS}^2}{2}\right].$$
The maximum, at $V_{DS} = V_{ov}$, is where the channel pinches off at the drain; beyond it the current stays at $\tfrac12\mu C_{ox}(W/L)V_{ov}^2$ (the pinched-off region absorbs extra $V_{DS}$ and shortens the effective $L$ slightly → λ).

**Long-channel $f_T$.** With $C_{gs} = \tfrac23WLC_{ox}$ and $g_m = \mu C_{ox}(W/L)V_{ov}$:
$$f_T = \frac{g_m}{2\pi C_{gs}} = \frac{3\mu V_{ov}}{4\pi L^2}.$$
Speed rises as $1/L^2$ and linearly with overdrive (so with $\sqrt{I_D}$). Checked numerically in script §1.

**Velocity saturation.** The drift velocity $v = \mu E$ saturates at $v_{sat}$ ≈ 10⁵ m/s (Si). When $V_{ov}/L$ exceeds roughly $v_{sat}/\mu$ (≈ 2.5 V/µm for µ = 0.04 m²/V s), the channel current becomes $I_D \approx WC_{ox}v_{sat}(V_{GS}-V_{th})$ — *linear* in overdrive — and $g_m \approx WC_{ox}v_{sat}$, independent of current. Then $f_T \approx v_{sat}/(2\pi L)$ (using $C_{gs} \approx WLC_{ox}$): 88 GHz at 180 nm, 245 GHz at 65 nm as intrinsic estimates (script §1). Real devices are lower because of overlap/fringe capacitance and access resistance. The square law, applied at 180 nm with $V_{ov}$ = 0.4 V, would claim 118 GHz — a common over-estimate.

**The $g_m/I_D$ picture.** Define the inversion coefficient $IC = I_D/I_{spec}$ with $I_{spec} = 2n\mu C_{ox}(W/L)V_T^2$. The EKV model interpolates smoothly:
$$\frac{g_m}{I_D} = \frac{1}{nV_T}\cdot\frac{2}{1+\sqrt{1+4\,IC}}$$
→ $1/(nV_T)$ ≈ 30 /V at $IC \ll 1$ (weak inversion); → $1/(nV_T\sqrt{IC}) = 2/V_{ov}$ at $IC \gg 1$ (strong inversion) (script §2) [1][2]. Design flow: choose $g_m/I_D$ for the speed/efficiency trade (high = efficient, low noise per mA, slow, large; low = fast, small), then $I_D = g_m/(g_m/I_D)$, then $W/L$ from a simulated current-density table. It works even where the square law fails.

**Why BJTs beat MOSFETs on $g_m$ per ampere.** A BJT's collector current is diffusion over a barrier, $\propto e^{V_{BE}/V_T}$, so $g_m/I_C = 1/V_T$ — the Boltzmann limit. A MOSFET reaches it only in weak inversion (and only to $1/(nV_T)$ because the gate couples to the channel through a capacitive divider, $n = 1 + C_{dep}/C_{ox}$). For a 50 Ω LNA or a low-noise preamp at fixed current budget, a BJT gives ≈ 4–8× the $g_m$ of a strong-inversion MOSFET.

**JFET noise (why they are quiet at high impedance).** Channel thermal noise referred to the gate is $e_n^2 \approx 4kT(2/3)/g_m$ (long-channel γ = 2/3). For the BF862 at 5 mA ($g_m$ ≈ 22 mS): 0.71 nV/√Hz, close to the 0.8 nV/√Hz datasheet figure (script §3) [3]. Current noise is only the shot noise of the gate leakage, $\sqrt{2qI_G}$ ≈ 1.8 fA/√Hz for 10 pA — versus ≈ 90 pA/√Hz for a BJT at 5 mA (β = 200). Through a 100 kΩ source that is 0.18 nV/√Hz for the JFET vs 9 µV/√Hz for the BJT (→ [low-noise design](low-noise-analog-design.md)).

**HEMT physics.** A wide-bandgap, doped barrier (AlGaAs on GaAs, or AlGaN on GaN) donates electrons into the narrower-gap channel material, where they collect in a triangular quantum well only a few nm thick at the interface — the 2DEG. The donors stay behind in the barrier, so the channel electrons suffer little ionised-impurity scattering: room-temperature mobility is several times that of doped bulk. "Pseudomorphic" (pHEMT) means a thin strained InGaAs channel is used to raise mobility and confinement further. In AlGaN/GaN the 2DEG is induced mainly by *spontaneous and piezoelectric polarisation*, even without doping, reaching ~1–1.2 × 10¹³ cm⁻² [5]. The gate is a Schottky contact, so it conducts if driven positive past ~+0.7 V (GaAs) or ~+1–2 V (GaN).

**Power capability.** An ideal class-A device swings from knee voltage $V_k$ to breakdown $V_{br}$ and from 0 to $I_{max}$; the maximum sinusoidal power is
$$P_{max} = \frac{(V_{br}-V_k)\,I_{max}}{8}.$$
Per mm of gate periphery: GaAs pHEMT (15 V, 0.5 A/mm) ≈ 0.9 W/mm; LDMOS (70 V, 0.25 A/mm) ≈ 2 W/mm; GaN (80 V, 1 A/mm) ≈ 9.4 W/mm — matching measured GaN densities of 6–10 W/mm [5] (script §4; device numbers are representative, not a specific part). The optimum load for power $P$ from supply $V_{DD}$ (class A/B, load-line) is
$$R_{opt} \approx \frac{(V_{DD}-V_k)^2}{2P}$$
— 31 Ω for 10 W at 28 V, 1 Ω for 10 W at 5 V, 0.54 Ω at 3.6 V. Matching a fraction of an ohm to 50 Ω needs a 100:1 transformation with high loaded Q (narrow band, lossy); 31 Ω needs almost none. This, more than raw power density, is why GaN amplifiers are broadband (→ [power amplifiers](../06-rf-circuits/power-amplifiers.md)).

**Johnson limit.** Breakdown needs a critical field $E_c$ over a length; speed needs a short transit length at $v_{sat}$. The product is bounded: $V_{br}f_T \lesssim E_cv_{sat}/(2\pi)$ — ≈ 480 V·GHz for Si, ≈ 640 for GaAs, ≈ 13 000 for GaN with textbook $E_c$, $v_{sat}$ (script §4) [5][8]. It is a scaling law, not a design number, but it explains the landscape: higher frequency means lower voltage in any material, and GaN buys ~20× more headroom.

### Level 3 — second-order effects and limits
- **Short-channel effects:** DIBL (drain-induced barrier lowering, $V_{th}$ falls with $V_{DS}$), mobility degradation with vertical field, hot-carrier ageing, and $g_mr_o$ falling to ~5–20 in nm nodes — hence analog circuits use longer-than-minimum L for gain and cascodes (→ [amplifier topologies](amplifier-topologies.md)).
- **Flicker noise:** MOSFETs have large 1/f noise ($\propto 1/(C_{ox}WL\,f)$, corners from 10s of kHz to MHz in small devices) from oxide traps; JFETs and BJTs are far better. Bad for oscillator phase noise and DC-precision circuits — chopper/auto-zero architectures exist because of it (→ [op-amps](op-amps-real-limitations.md), [shot & flicker noise](../07-noise-linearity/shot-and-flicker-noise.md)).
- **Thermal behaviour of power MOSFETs:** $R_{DS(on)}$ rises with temperature (≈ +0.4–1 %/K) above the zero-temperature-coefficient point, which helps parallel devices share current when switched fully on; but in linear mode below that point current *increases* with temperature, so linear-mode operation (hot-swap, active loads, slow gate drive) can create hot spots and fail within the nominal SOA. Use linear-mode-rated parts and respect the DC SOA curve.
- **GaN trapping and current collapse:** surface and buffer traps make the high-voltage RF current lower than the DC I–V suggests (drain lag); field plates and passivation mitigate it [5]. Gate lag and long thermal/trap time constants matter for pulsed radar PAs (→ [radar hardware](../11-radar/diy-radar-hardware.md)).
- **GaN as an LNA:** noise figure is somewhat worse than GaAs pHEMT, but a GaN LNA survives watts of input without a limiter — attractive behind a T/R switch in radar.
- **Thermal limits:** high power density means high heat flux; GaN-on-SiC uses SiC's high thermal conductivity; plastic-packaged parts need copper-filled via farms and a heatsink (→ [thermal management](../13-pcb-rf-layout-emc/thermal-management-rf.md)).

#### Level 3 — analog-IC building blocks: why the datasheet numbers of ICs are what they are
These are the on-chip ideas behind the offset, reference accuracy and supply limits of the ICs this KB uses: op-amps, LDOs, ADCs and LoRa transceivers. You will not design them on a PCB, but they explain the datasheet numbers. Numbers are checked in `tools/verify/s18_analog_blocks.py`.
- **Mismatch: Pelgrom's law.** Two "identical" transistors differ in threshold by a random $\Delta V_T$, with $\sigma(\Delta V_T) = A_{VT}/\sqrt{WL}$ (plus a small distance term) [11]. The reason is that a bigger gate averages over more random dopant atoms; a Monte-Carlo average of unit cells reproduces the $1/\sqrt{\text{area}}$ law. Pelgrom et al. report $A_{VT}$ falling from about 15 to about 5 mV·µm as oxides thinned from the 1 µm to the 0.25 µm generations [12]. A common rule of thumb, from lecture notes and not checked here, is ≈ 1 mV·µm per nm of oxide. Bipolar $V_{BE}$ matches far better, at ≈ 0.35 mV·µm [12].
  - *Example:* an input pair of 10 µm × 1 µm with $A_{VT}$ = 5 mV·µm has σ = 1.6 mV, so a ±4.7 mV (3σ) offset spread. That is the shape of a cheap CMOS op-amp's offset specification. Halving σ costs 4× the area and 4× the capacitance; this is the speed–precision–power trade-off, and why precision parts trim or chop.
- **Gradients and common-centroid layout.** Process and temperature gradients add a *systematic* difference proportional to the distance between device centroids. Splitting each device into units and placing them ABBA (or cross-coupled quads) puts both centroids at the same point, so a linear gradient cancels exactly. *Illustrative:* with a gradient of 0.5 mV per 100 µm and 20 µm unit pitch, AABB leaves 0.20 mV of offset and ABBA leaves 0. Dummy devices at the ends, the same orientation, and keeping hot devices away do the rest [15].
- **PVT corners.** An IC must meet its specification over process corners (typically SS/SF/TT/FS/FF), supply (±10 %) and temperature (e.g. −40…125 °C). That is 5 × 3 × 3 = 45 corner simulations before Monte-Carlo mismatch is added. Datasheet "min/max" columns are this envelope, and "typ" is TT at 25 °C. That is why the KB quotes min/max for budgets ([canonical values](../00-math-foundations/canonical-values-and-conventions.md), "Datasheet numbers").
- **PTAT and the bandgap reference.** Two bipolar junctions run at a current-density ratio $n$ differ by $\Delta V_{BE} = (kT/q)\ln n$. This is exactly proportional to absolute temperature (PTAT), at +0.179 mV/K for $n$ = 8 (53.8 mV at 300 K). $V_{BE}$ itself falls by about 2 mV/K. Adding $K\Delta V_{BE}$ with $K = 2/0.179 \approx 11$ cancels the slope at the design temperature and gives ≈ 1.25 V, close to the extrapolated silicon bandgap (≈ 1.2 V) [13]. That is why references are ≈ 1.2 V, 2.5 V (a scaled Brokaw cell [14]) or 1.25 V multiples. Residual curvature of the $V_{BE}(T)$ law and mismatch-driven initial error (Brokaw's trimmed cell reached 5 ppm/°C over the military range [14]; untrimmed figures are much worse — typical-range claim, not sourced here) are why LDOs and ADC references specify accuracy in % and tempco in ppm/°C. The same $\Delta V_{BE}$ is the on-chip temperature sensor ([BJT page](bjt-fundamentals-small-signal.md)).
- **Gain boosting.** A single device gives $g_mr_o$ (≈ 20, 26 dB, in modern short-channel processes). A cascode gives ≈ $(g_mr_o)^2$ (≈ 52 dB). Regulating the cascode gate with an auxiliary amplifier of gain $A_b$ multiplies the output resistance again (≈ 78 dB with $A_b$ = 20) without stacking more devices into a low supply. Bult and Geelen reached 90 dB this way in a fast single-stage op-amp [16]. The price is a pole–zero doublet that can add a slow settling tail.
- **CMOS breakdown and RF output.** Thin-oxide core devices tolerate only about their nominal $V_{DD}$, e.g. 1.8 V in a 0.18 µm process and about 1 V in nanometre processes (general knowledge, medium confidence). Beyond that, oxide wear-out (time-dependent breakdown) and hot-carrier ageing set in, and junctions break down at a few volts; thick-oxide I/O devices take 2.5–5 V. An RF output stage therefore cannot swing far, and the matching network must transform 50 Ω down. Example: +22 dBm (158 mW) is 3.98 V peak in 50 Ω. A stage limited to 2 V peak needs $R_{opt} = V^2/2P$ = 12.6 Ω, a 4:1 transformation (→ [power amplifiers](../06-rf-circuits/power-amplifiers.md)). CMOS PAs and T/R switches also stack transistors so each one sees only part of the swing. GaAs, GaN and LDMOS (above) are used where watts are needed.

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical |
|---|---|---|---|
| MOSFET sat. current | $\tfrac12\mu C_{ox}(W/L)V_{ov}^2$ | long channel, $V_{DS} \ge V_{ov}$ | — |
| MOSFET $g_m$ | $2I_D/V_{ov}$ | strong inversion | 5–10 /V × $I_D$ |
| Weak-inversion $g_m$ | $I_D/(nV_T)$ | $V_{GS} < V_{th}$ | ≈ 30 /V × $I_D$ |
| $g_m/I_D$ (EKV) | $\frac{2}{nV_T(1+\sqrt{1+4IC})}$ | all regions | 3–30 /V |
| Long-channel $f_T$ | $3\mu V_{ov}/(4\pi L^2)$ | $V_{ov}/L \ll v_{sat}/\mu$ | — |
| Velocity-sat. $f_T$ | $\sim v_{sat}/(2\pi L)$ | short channel | upper estimate |
| Subthreshold swing | $nV_T\ln10$ | — | 70–90 mV/dec |
| JFET $g_{m0}$ | $2I_{DSS}/|V_P|$ | — | 10–50 mS small JFETs |
| JFET/FET channel noise | $e_n^2 \approx 4kT\gamma/g_m$ | above 1/f corner | γ = 2/3 long channel |
| Class-A power density | $(V_{br}-V_k)I_{max}/8$ | ideal | 0.9 (GaAs) / 2 (LDMOS) / 9 (GaN) W/mm |
| Optimum PA load | $(V_{DD}-V_k)^2/(2P)$ | load-line | 31 Ω @ 10 W, 28 V |
| Johnson limit | $V_{br}f_T \lesssim E_cv_{sat}/2\pi$ | scaling | Si 0.5, GaN 13 kV·GHz |
| Switching time | $\approx Q_g/I_{drive}$ | power MOSFET | nC / A = ns |

**Which device for which job** (representative, 2026; confirm with current datasheets)

| Technology | Sweet-spot frequency | Power | Noise | Supply | Typical use |
|---|---|---|---|---|---|
| Si power MOSFET (trench) | DC–MHz switching | W–kW | — | 12–200 V | pyro channels, load switches, DC-DC |
| Si RF CMOS (in ICs) | to 100+ GHz | mW–1 W | good | ≤ 1.2–3.3 V | complete transceivers (SX126x, nRF, Wi-Fi SoCs) |
| Si BJT | DC–2 GHz | mW–W | good | 3–30 V | general analog, VHF/UHF oscillators |
| SiGe HBT | 0.1–100+ GHz | mW–0.5 W | very good; low 1/f | 2–4 V | LNAs, VCOs, mmWave radar ICs |
| JFET | DC–few 100 MHz | mW | best at high source Z | 5–30 V | sensor/audio/photodiode preamps, VHF oscillators |
| GaAs MESFET | legacy to ~20 GHz | ≤ 1 W | good | 3–8 V | largely replaced by pHEMT |
| GaAs pHEMT (D- and E-mode) | 0.5–40 GHz | mW–few W | lowest at 1–20 GHz | 2–8 V | LNAs, RF switches, gain blocks |
| GaAs/InGaP HBT | 0.5–6 GHz | 0.5–4 W | — | 3–5 V | handset PAs, gain-block MMICs |
| Si LDMOS | 1 MHz–3.8 GHz | 10 W–1.5 kW | — | 28–50 V | broadcast, base station, rugged ham/ISM PAs |
| GaN-on-SiC HEMT | DC–40+ GHz | 1 W–1 kW | fair; survives overload | 28–50 V | broadband and high-efficiency PAs, radar, rugged LNAs |
| InP HEMT/HBT | 30–600 GHz | mW | lowest at mmWave | low | radio astronomy, sub-THz |

## Worked examples

### 1. Pyro-channel MOSFET driven from a 3.3 V MCU pin
A Space Bar lesson: pyro FET gates were driven at 3.3 V without a characterised $R_{DS(on)}$. Take the AO3400A (30 V, SOT-23): $V_{GS(th)}$ 0.9 V typ / 1.4 V max *at 250 µA*; $R_{DS(on)}$ max 26.5 mΩ at 10 V, 32 mΩ at 4.5 V, 48 mΩ at 2.5 V [7].
- Model $R_{DS(on)} = R_0 + K/(V_{GS}-V_{th,max})$ fitted to the 4.5 V and 2.5 V points: $R_0$ = 23.2 mΩ. It predicts 26.4 mΩ at 10 V (datasheet 26.5 mΩ — the model is sound) and **37.6 mΩ at 3.3 V** worst case (script §6).
- Igniter pulse at 3 A: 113 mV drop and 0.34 W for a few ms — fine thermally. At 5 A: 0.94 W; still fine for ms pulses (check the transient thermal impedance curve), but a battery sagging to a 3.0 V GPIO high level adds ~3 mΩ.
- Lesson: pick a part whose $R_{DS(on)}$ is *specified* at or below your minimum gate drive (2.5 V rating for a 3.3 V system), add a gate resistor (10–100 Ω) against ringing and a pull-down (10–100 kΩ) so the gate is defined while the MCU boots.

### 2. JFET vs BJT for a 100 kΩ-source preamp
- BF862 at 5 mA: $e_n$ ≈ 0.8 nV/√Hz, $i_n$ ≈ 2 fA/√Hz (10 pA leakage). Total input noise with $R_s$ = 100 kΩ: resistor 40.7 nV/√Hz dominates; the JFET adds < 0.1 %.
- BJT at 5 mA (β = 200): $i_n = \sqrt{2qI_B}$ = 89 pA/√Hz → 8.9 µV/√Hz across 100 kΩ — 220× the source's own noise. Even at the BJT's optimum current for 100 kΩ ($I_C = V_T\sqrt\beta/R_s$ ≈ 3.7 µA), NF is worse than the JFET's.
- The JFET's weakness is its 10 pF $C_{iss}$ (+ Miller from 1.9 pF $C_{rss}$): with 100 kΩ the input pole is at ~160 kHz unless cascoded or bootstrapped.

### 3. Why a 10 W 433/915 MHz amplifier should be GaN or LDMOS at 28 V
From $R_{opt} = (V_{DD}-V_k)^2/(2P)$ (script §4): at 5 V, 10 W needs ≈ 1.0 Ω (a 50:1 transformation; a two-section L-network with loaded Q ≈ 5 per section, lossy and narrow); at 28 V, ≈ 31 Ω — almost 50 Ω already, broadband and low-loss. A 2 W stage at 5 V needs ≈ 5 Ω (10:1), still practical — which is roughly where integrated 1–2 W LoRa modules sit.

### 4. Biasing a CGH40010F GaN HEMT
Data: $V_{GS(th)}$ −3.8 / −3.0 / −2.3 V (min/typ/max), $V_{GS(Q)}$ ≈ −2.7 V for $I_{DQ}$ = 200 mA at 28 V, $V_{GS}$ abs. max −10/+2 V, $I_{G,max}$ 4 mA, $V_{BR}$ ≥ 84 V [6].
1. Power-up: set the gate supply to −5 V (pinched off), *then* ramp $V_{DD}$ to 28 V, *then* raise $V_{GS}$ until $I_D$ = 200 mA. Power-down in reverse. Loss of the negative rail with drain applied → the device turns fully on (> 2.9 A saturated current) and self-destructs; add a sequencer or a drain switch interlocked to the negative rail.
2. Sensitivity: near threshold $I_D \approx K(V_{GS}-V_{th})^2$; with $V_{GS(Q)}-V_{th}$ ≈ 0.3 V at 200 mA, K ≈ 2.2 A/V², so a +0.1 V bias error gives ≈ 360 mA (+78 %). The 1.5 V threshold spread means a fixed divider cannot work across parts: trim per device, or use an active bias controller that servos $V_{GS}$ to hold $I_{DQ}$.
3. Temperature: $V_{th}$ drifts; the active controller also removes that.
4. Gate network: a series gate resistor (tens of Ω) and RC decoupling on the gate feed are standard stability measures (→ [amplifier stability & biasing](../06-rf-circuits/amplifier-stability-and-biasing.md)).

### 5. LNA device choice at 915 MHz: SiGe HBT vs E-pHEMT
BFP740 at 900 MHz: NF$_{min}$ 0.45 dB (6 mA), OIP3 22.5 dBm at 3 V/15 mA [9]. ATF-54143 at 900 MHz: NF 0.3 dB, gain 23.4 dB, OIP3 35.5 dBm at 3 V/60 mA [4]. Linearity per DC watt: 4.0 (BFP740) vs 19.7 (ATF-54143) (script §5). For a battery-powered ground station in a crowded ISM band, the pHEMT's 13 dB higher OIP3 for 4× the current is often worth it; for a coin-cell node, the SiGe device at a few mA is. Both need careful stability design at UHF where they have 25–30 dB of available gain.

## Practical notes
- **Gate protection:** MOSFET gates are thin oxide (typically ±8 to ±20 V absolute); GaAs/GaN Schottky gates conduct at small positive voltage and have small reverse limits (ATF-54143: −5/+1 V [4]; CGH40010F −10/+2 V [6]). Add series gate resistance, keep ESD discipline, and never leave a gate floating.
- **Negative gate supplies:** charge-pump inverters (e.g. ICL7660/LM2776 class) plus heavy RC filtering; their switching noise appears on the gate and modulates the RF — filter well (→ [power supplies](power-supplies-for-rf-and-analog.md)).
- **E-mode vs D-mode pHEMT:** enhancement-mode (ATF-54143, many LNA MMICs) runs from a single positive supply with $V_{GS}$ ≈ +0.4–0.7 V; depletion-mode needs a negative gate or a source resistor for self-bias (which needs a good bypass capacitor — its ESL causes instability at GHz).
- **Datasheet reading:** use S-parameter and noise-parameter files at your bias; $f_T$ and "NF" headlines are at optimum conditions and with fixture losses removed.
- **Thermal:** SOT-343/SOT-89 pHEMTs and SOT-89 gain blocks dissipate 0.1–0.5 W; the ground paddle *is* the heatsink — via farms under it.
- **Parts search:** for JLCPCB-assembled boards, check stock/basic-part status of small-signal FETs with the parts-search tools before committing.

## Common mistakes & misconceptions
- **"$V_{GS(th)}$ = 1 V, so 3.3 V turns it fully on."** Threshold is defined at a tiny current (µA); full enhancement needs several times $V_{th}$. Read $R_{DS(on)}$ at your actual $V_{GS}$.
- **Using the square law to size short-channel devices.** It over-predicts current and $f_T$; use $g_m/I_D$ with simulated or measured curves.
- **Assuming FETs have no input current noise.** MOSFET gate leakage is tiny, but at RF the gate current noise induced through $C_{gs}$ ($\propto f^2$) matters; and JFET gate leakage doubles every ~10 °C.
- **Powering a depletion-mode amplifier drain-first.** At $V_{GS}$ = 0 it conducts $I_{DSS}$ (amps for power GaN) → instant failure.
- **Thinking GaN is "just a better GaAs".** It needs 28–50 V supplies, negative bias sequencing, careful thermal design and has trapping effects; for sub-watt, low-voltage work GaAs/SiGe/CMOS are simpler.
- **Ignoring Miller capacitance ($C_{rss}$/$C_{gd}$) in switches:** fast $dV_{DS}/dt$ couples back to the gate and can re-turn-on a low-side FET — hold the gate low with a low-impedance driver.
- **Paralleling MOSFETs used in linear mode** and trusting positive $R_{DS(on)}$ tempco to share current — it doesn't in linear mode.

## How to simulate / verify
- **Python:** `tools/verify/analog_fet.py` — square-law and $f_T$ checks, velocity-saturation estimate, EKV $g_m/I_D$ limits, JFET $g_{m0}$ and noise vs BF862, power-density and $R_{opt}$ tables, Johnson limit, OIP3/P$_{DC}$ comparison, $R_{DS(on)}$(V$_{GS}$) fit.
- **ngspice (KiCad-bundled, `tools/verify/analog_ngspice.py`):** plot a JFET transfer curve and compare to the square law:
```spice
* JFET square-law check (BF862-like: IDSS ~ 15 mA, VP ~ -0.8 V)
* ngspice NJF: IDSS = BETA*VTO^2 -> BETA = 15m/0.64 = 23.4m
.model JBF NJF(VTO=-0.8 BETA=23.4m LAMBDA=0.02 CGS=8p CGD=2p IS=1e-14)
VD d 0 DC 5
VG g 0 DC 0
J1 d g 0 JBF
.dc VG -0.8 0 0.01
.end
```
  `-i(VD)` vs `VG` traces $I_{DSS}(1-V_{GS}/V_P)^2$; its derivative at $V_{GS}$ = 0 is $2I_{DSS}/|V_P|$ ≈ 37.5 mS (× (1+λ$V_{DS}$)).
- **MOSFET models:** for discrete power MOSFETs use the vendor SPICE subcircuit (they include $C_{gd}(V)$ and body diode); for IC design use BSIM models from the PDK and $g_m/I_D$ lookup tables (Jespers & Murmann provide scripts [2]).
- **Analog-IC blocks (Level 3):** `tools/verify/s18_analog_blocks.py` — Pelgrom σ and a unit-cell Monte-Carlo of the 1/√area law, AABB vs ABBA gradient offset, PTAT/bandgap arithmetic, gain-boost dB, CMOS swing vs $R_{opt}$.
- **RF devices:** use vendor S2P + noise-parameter files or harmonic-balance models (Modelithics, vendor large-signal models) in Qucs-S/ADS; for GaN load-pull data use the vendor's impedance tables.

## Open questions / gaps
- Representative $V_{br}$, $I_{max}$, $V_k$ in the power-density table are typical literature numbers, not from one datasheet; a table of specific parts (with W/mm) would firm it up.
- Mishra et al.'s material table lists SiC mobility 260 cm²/V s and bandgap 2.9 eV (6H polytype); 4H-SiC, used today, has ~3.26 eV and ~900 cm²/V s (Sze). Not used in calculations here; noted as a source difference.
- Analog-IC block section (W5-S18): the "≈ 1 mV·µm per nm of oxide" rule and the untrimmed-reference accuracy range are not sourced to a primary paper; Pelgrom 1989 was not re-read (its numbers come via the 1998 IEDM overview). No process-specific A_VT for the transceiver ICs the team uses is public.
- GaN LNA noise figures and survivability numbers not yet sourced — see [LNA design](../06-rf-circuits/lna-design.md).

## Sources
1. B. Razavi, *Design of Analog CMOS Integrated Circuits*, 2nd ed., McGraw-Hill 2017 — ch. 2 (MOS physics, square law, subthreshold, short-channel effects), ch. 7 (noise). (textbook)
2. P. G. A. Jespers, B. Murmann, *Systematic Design of Analog CMOS Circuits Using Pre-Computed Lookup Tables*, Cambridge 2017 — $g_m/I_D$ method, EKV-style interpolation. (textbook)
3. NXP Semiconductors, *BF862 N-channel junction FET* datasheet. https://www.nxp.com/docs/en/data-sheet/BF862.pdf — $V_{GSoff}$ 0.3–1.2 V, $I_{DSS}$ 10–25 mA, $y_{fs}$ 35–45 mS, $C_{iss}$ 10 pF, $C_{rss}$ 1.9 pF, $e_n$ 0.8 nV/√Hz @ 100 kHz. (datasheet)
4. Avago Technologies, *ATF-54143 Low Noise Enhancement Mode Pseudomorphic HEMT* datasheet. https://www.modelithics.com/models/Vendor/Avago/ATF-54143.pdf — NF 0.5 dB @ 2 GHz / 0.3 dB @ 900 MHz, OIP3 36.2/35.5 dBm, $V_{th}$ 0.38 V, $V_{GS}$ −5/+1 V, $V_{DS}$ 5 V max. (datasheet)
5. U. K. Mishra, P. Parikh, Y.-F. Wu, "AlGaN/GaN HEMTs — an overview of device operation and applications," *Proc. IEEE* 90(6), 1022–1031, 2002. http://my.ece.ucsb.edu/Mishra/classfiles/overview.pdf — material comparison, 2DEG 1–1.2×10¹³ cm⁻², 6–10 W/mm, trapping. (peer-reviewed)
6. Wolfspeed/MACOM, *CGH40010 10 W, DC–6.0 GHz GaN HEMT* datasheet. https://cdn.macom.com/datasheets/CGH40010.pdf — $V_{GS(th)}$, $V_{GS(Q)}$, limits, 65 % drain efficiency at P$_{SAT}$. (datasheet)
7. Alpha & Omega Semiconductor, *AO3400A 30 V N-Channel MOSFET* datasheet. https://www.aosmd.com/res/datasheets/AO3400A.pdf — $R_{DS(on)}$ at 10/4.5/2.5 V, $V_{GS(th)}$. (datasheet)
8. S. M. Sze, K. K. Ng, *Physics of Semiconductor Devices*, 3rd ed., Wiley 2007 — ch. 6–7 (MESFET/HEMT/MOSFET physics), material constants ($E_c$, $v_{sat}$, mobility). (textbook)
9. Infineon, *BFP740* datasheet (see [BJT page](bjt-fundamentals-small-signal.md) source 1). (datasheet)
10. P. R. Gray et al., *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley 2009 — ch. 1 (MOS models, JFET), ch. 11 (FET noise). (textbook)
11. M. J. M. Pelgrom, A. C. J. Duinmaijer, A. P. G. Welbers, "Matching properties of MOS transistors," *IEEE J. Solid-State Circuits* SC-24(5), 1433–1440, 1989 — σ(ΔV_T) = A_VT/√(WL) plus distance term. (peer-reviewed; citation as given in [12])
12. M. J. M. Pelgrom, H. P. Tuinhout, M. Vertregt, "Transistor matching in analog CMOS applications," *IEDM 1998*, pp. 915–918. https://designers-guide.org/Forum/Attachments/Transistor_matching_in_analog_CMOS_applications_.pdf — A_VT ≈ 15 → 5 mV·µm from 1 µm to 0.25 µm generations (their Fig. 3), improvement with oxide thickness, bipolar A_VBE = 0.35 mV·µm, simulated vs measured bandgap spread. (peer-reviewed; read 2026-10-13)
13. R. J. Widlar, "New developments in IC voltage regulators," *IEEE J. Solid-State Circuits* SC-6(1), 2–7, 1971 — the bandgap reference. (peer-reviewed; bibliographic data confirmed by search)
14. A. P. Brokaw, "A simple three-terminal IC bandgap reference," *IEEE J. Solid-State Circuits* SC-9(6), 388–393, 1974 — Brokaw cell, 2.5 V reference, ≈ 5 ppm/°C over the military range. (peer-reviewed; abstract via search)
15. A. Hastings, *The Art of Analog Layout*, 2nd ed., Prentice Hall, 2006 — matching, common-centroid and dummy devices. (textbook; cited from knowledge)
16. K. Bult, G. J. G. M. Geelen, "A fast-settling CMOS op amp for SC circuits with 90-dB DC gain," *IEEE J. Solid-State Circuits* 25(6), 1379–1384, 1990 — gain boosting. (peer-reviewed; end page given as 1384 in most citations, 1394 in some patents)
