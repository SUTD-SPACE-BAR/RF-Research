---
title: Telegrapher's equations and characteristic impedance
domain: 03-transmission-lines-matching
slug: telegrapher-equations-characteristic-impedance
tags: [transmission-line, telegrapher, RLGC, characteristic-impedance, propagation-constant, velocity-factor, distortionless-line, skin-effect]
prerequisites:
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/differential-equations-circuits-waves.md
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
related:
  - reflections-vswr-return-loss-mismatch.md
  - input-impedance-stubs-quarter-wave.md
  - coax-and-cables.md
  - planar-lines-microstrip-stripline-cpwg.md
  - time-domain-reflectometry.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../02-electromagnetics/inductance-capacitance-from-fields.md
  - ../02-electromagnetics/quasi-static-vs-full-wave.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Telegrapher's equations and characteristic impedance

## Questions this page answers
- When does a wire or PCB trace stop being "just a wire" and become a transmission line?
- What is characteristic impedance physically, and why is it measured in ohms if nothing dissipates?
- Why does my multimeter read open (or a few ohms) across a 50 Ω coax instead of 50 Ω?
- How do I derive $Z_0$ and the propagation constant $\gamma=\alpha+j\beta$ from the RLGC model?
- What is velocity factor, and how do I compute the physical length of a quarter wave in coax?
- Why is attenuation in dB per metre roughly proportional to $\sqrt{f}$ at low frequency and to $f$ at high frequency?
- What is a distortionless line and why did Heaviside add inductance to telephone cables?
- Is $Z_0$ really constant with frequency? Why is it complex at audio frequencies?
- How do I measure $Z_0$ and velocity factor of an unknown cable with a NanoVNA?

## TL;DR
- Any two-conductor structure whose length is not ≪ wavelength (rule of thumb: $\ell > \lambda/10$, or the one-way delay exceeds ~1/6 of the signal rise time) must be treated as a **transmission line**: voltage and current become waves.
- Per-unit-length model: series $R$ (Ω/m), $L$ (H/m), shunt $G$ (S/m), $C$ (F/m). The **telegrapher's equations** $\partial v/\partial z=-Ri-L\,\partial i/\partial t$, $\partial i/\partial z=-Gv-C\,\partial v/\partial t$ follow from KVL/KCL on a slice.
- **Characteristic impedance** $Z_0=\sqrt{(R+j\omega L)/(G+j\omega C)}$ is the voltage-to-current ratio of *one travelling wave*; for a low-loss line $Z_0\approx\sqrt{L/C}$ (real). It is *not* a resistance you can measure at DC.
- **Propagation constant** $\gamma=\sqrt{(R+j\omega L)(G+j\omega C)}=\alpha+j\beta$. Low loss: $\alpha\approx R/(2Z_0)+GZ_0/2$ (Np/m; ×8.686 for dB/m), $\beta\approx\omega\sqrt{LC}$.
- **Phase velocity** $v_p=\omega/\beta=1/\sqrt{LC}$; for a TEM line in a homogeneous dielectric $v_p=c/\sqrt{\varepsilon_r}$, so **velocity factor** $VF=1/\sqrt{\varepsilon_r}$ (solid PE 0.66, PTFE 0.69–0.70, foam PE 0.80–0.85). For microstrip use $\varepsilon_\text{eff}$.
- Conductor loss grows as $\sqrt{f}$ (skin effect), dielectric loss as $f$; real braided cables lose 10–30 % more than smooth-copper theory (RG-58 at 1 GHz: 11.5 dB/100 ft theory vs 14.5 datasheet).
- **Heaviside's distortionless condition** $R/L=G/C$ makes $\alpha$ and $v_p$ frequency-independent and $Z_0$ exactly real.
- Measure an unknown line: $Z_0=\sqrt{Z_\text{open}Z_\text{short}}$; velocity factor from the frequency of the first $\lambda/4$ resonance of an open stub.

## Intuition (no math)

**Why wires become waves.** A signal cannot appear at the far end of a cable instantly; it travels at a finite speed (about two-thirds of the speed of light in a typical coax). If the cable is short compared with how fast the signal changes, the whole wire is at "the same voltage" and lumped circuit theory works. Once the cable is long enough that the voltage at one end differs noticeably from the other at the same instant, you must track the *wave*. At 433 MHz a wavelength in RG-58 is only 46 cm, so a 1 m antenna lead is more than two wavelengths long — definitely a transmission line. At 50 Hz the wavelength is 4000 km, so mains wiring in a house is not.

**The ladder picture.** Chop the line into tiny slices. Each slice has a little series inductance (the magnetic field around the current loop formed by the two conductors) and a little shunt capacitance (the electric field between them), plus small losses: series resistance of the metal and shunt leakage through the dielectric. A long line is an infinite ladder of these L–C slices.

**What $Z_0$ really is.** Launch a voltage step into an infinitely long line. The step front advances, and as it advances it must charge the capacitance of each new slice and build up the magnetic field in its inductance. That requires a steady current flowing from the source, and the ratio of the step voltage to that current is a fixed number set by $L$ and $C$ per metre — the characteristic impedance. Energy leaves the source not to be burned but to fill fields that are moving away. So $Z_0$ behaves like a resistor to the source *while the wave is travelling away and nothing comes back*. A 50 Ω line terminated in 50 Ω is indistinguishable, from the source, from an infinitely long line: the terminating resistor simply absorbs the wave as if the line went on forever.

**Why the ohmmeter lies.** A multimeter applies DC. It launches a tiny step: for the first few nanoseconds (twice the transit time) the cable does draw current as if it were 50 Ω, but then the wave reflects from the open far end, comes back, and the current settles to zero — the line has simply charged up like a capacitor. The meter reads open (unshorted far end) or the DC resistance of the copper (shorted far end). $Z_0$ is a property of *waves*, visible only with a time-domain reflectometer, a VNA, or on a fast oscilloscope.

**Velocity.** In a TEM line (coax, stripline) the wave is a plane-wave-like field guided between conductors, so it travels at the speed of light in the dielectric, $c/\sqrt{\varepsilon_r}$. Filling a coax with polyethylene ($\varepsilon_r\approx2.3$) slows the wave to 0.66 c. Foam dielectrics have more air and are faster (0.80–0.88 c). In microstrip part of the field is in air and part in the board, so the wave sees an *effective* permittivity between 1 and $\varepsilon_r$.

**Loss.** Two independent mechanisms. The current crowds into a thin skin at the conductor surface (skin depth ≈ 3 µm in copper at 433 MHz), so the series resistance grows as $\sqrt{f}$. The dielectric also absorbs a fraction of each cycle's energy ($\tan\delta$), which gives a loss growing linearly with $f$. At low GHz in good cable the conductor term dominates; on FR-4 PCBs above ~1–2 GHz the dielectric term takes over.

## The math

### Level 1 — the results and what the symbols mean

| Symbol | Meaning | Unit |
|---|---|---|
| $R$ | series resistance per unit length (both conductors) | Ω/m |
| $L$ | series inductance per unit length | H/m |
| $G$ | shunt conductance per unit length (dielectric loss) | S/m |
| $C$ | shunt capacitance per unit length | F/m |
| $\omega=2\pi f$ | angular frequency | rad/s |
| $Z_0$ | characteristic impedance | Ω |
| $\gamma=\alpha+j\beta$ | propagation constant | 1/m |
| $\alpha$ | attenuation constant | Np/m (1 Np = 8.686 dB) |
| $\beta=2\pi/\lambda$ | phase constant | rad/m |
| $v_p$ | phase velocity | m/s |

Lossless line ($R=G=0$):
$$Z_0=\sqrt{\frac{L}{C}},\qquad v_p=\frac{1}{\sqrt{LC}},\qquad \beta=\omega\sqrt{LC}=\frac{2\pi}{\lambda},\qquad \lambda=\frac{v_p}{f}.$$

Two handy corollaries (lossless): $L=Z_0/v_p$ and $C=1/(Z_0v_p)$. A 50 Ω cable with $VF=0.66$ has $C=1/(50\times0.66\times3\times10^8)=101$ pF/m and $L=253$ nH/m.

Velocity factor for a TEM line with a homogeneous dielectric: $VF=v_p/c=1/\sqrt{\varepsilon_r}$. For quasi-TEM planar lines, $VF=1/\sqrt{\varepsilon_\text{eff}}$ (see [planar lines](planar-lines-microstrip-stripline-cpwg.md)).

Electrical length: $\theta=\beta\ell=2\pi\ell/\lambda$ (radians) or $360°\,\ell/\lambda$. Physical length for a given electrical length: $\ell=\dfrac{\theta}{360°}\dfrac{VF\cdot c}{f}$.

### Level 2 — derivation from the RLGC ladder

**Assumptions.** (i) The line is uniform along $z$. (ii) The fields are TEM or quasi-TEM, so a unique voltage between conductors and a current on them can be defined at each $z$ ([why this matters](../02-electromagnetics/quasi-static-vs-full-wave.md)). (iii) Linear, time-invariant materials.

Take a slice of length $\Delta z$ with series $R\Delta z$, $L\Delta z$ and shunt $G\Delta z$, $C\Delta z$. KVL around the slice:
$$v(z,t)-R\Delta z\, i(z,t)-L\Delta z\,\frac{\partial i(z,t)}{\partial t}-v(z+\Delta z,t)=0.$$
KCL at the node $z+\Delta z$:
$$i(z,t)-G\Delta z\, v(z+\Delta z,t)-C\Delta z\,\frac{\partial v(z+\Delta z,t)}{\partial t}-i(z+\Delta z,t)=0.$$
Divide by $\Delta z$ and let $\Delta z\to0$ — the **telegrapher's equations** (Heaviside, 1876–1880s):
$$\boxed{\frac{\partial v}{\partial z}=-Ri-L\frac{\partial i}{\partial t},\qquad \frac{\partial i}{\partial z}=-Gv-C\frac{\partial v}{\partial t}}$$

**Phasor form.** With $v(z,t)=\mathrm{Re}\{V(z)e^{j\omega t}\}$ (engineering convention, [phasors](../00-math-foundations/complex-numbers-and-phasors.md)), $\partial/\partial t\to j\omega$. Define the series impedance and shunt admittance per metre $Z'=R+j\omega L$, $Y'=G+j\omega C$:
$$\frac{dV}{dz}=-Z'I,\qquad \frac{dI}{dz}=-Y'V.$$
Differentiate the first and substitute the second:
$$\frac{d^2V}{dz^2}=\gamma^2V,\qquad \gamma=\sqrt{Z'Y'}=\sqrt{(R+j\omega L)(G+j\omega C)},$$
with the branch of the square root chosen so that $\mathrm{Re}\,\gamma\ge0$. The general solution is a superposition of a forward wave and a backward wave:
$$V(z)=V_0^+e^{-\gamma z}+V_0^-e^{+\gamma z}.$$
Put this into $dV/dz=-Z'I$:
$$I(z)=\frac{\gamma}{Z'}\left(V_0^+e^{-\gamma z}-V_0^-e^{\gamma z}\right)=\frac{1}{Z_0}\left(V_0^+e^{-\gamma z}-V_0^-e^{\gamma z}\right),$$
$$\boxed{Z_0=\frac{Z'}{\gamma}=\sqrt{\frac{R+j\omega L}{G+j\omega C}}}$$
So $Z_0$ is the ratio $V^+/I^+$ of the forward wave (and $-V^-/I^-$ of the backward wave). The minus sign for the backward wave is why reflections change the total $V/I$ ratio; that is the subject of [reflections](reflections-vswr-return-loss-mismatch.md). Verified symbolically and numerically (sympy + scikit-rf) in `tools/verify/tline_telegrapher.py`.

**Time domain, lossless.** With $R=G=0$ the telegrapher's equations combine into the 1-D wave equation $\partial^2v/\partial z^2=LC\,\partial^2v/\partial t^2$, whose d'Alembert solution $v=f^+(t-z/v_p)+f^-(t+z/v_p)$, $i=[f^+-f^-]/Z_0$, shows any waveform shape travels undistorted at $v_p=1/\sqrt{LC}$.

**Low-loss approximation.** Write $\gamma=j\omega\sqrt{LC}\sqrt{(1+R/j\omega L)(1+G/j\omega C)}$. For $R\ll\omega L$ and $G\ll\omega C$, expand to first order:
$$\gamma\approx j\omega\sqrt{LC}\left[1+\frac{1}{2}\left(\frac{R}{j\omega L}+\frac{G}{j\omega C}\right)\right]
\;\Rightarrow\;
\alpha\approx\frac{R}{2Z_0}+\frac{GZ_0}{2}=\alpha_c+\alpha_d,\qquad \beta\approx\omega\sqrt{LC}.$$
Carrying the expansion to second order gives the first dispersion correction
$$\beta\approx\omega\sqrt{LC}\left[1+\frac{1}{8}\left(\frac{R}{\omega L}-\frac{G}{\omega C}\right)^2\right],$$
and similarly $Z_0\approx\sqrt{L/C}\,[1-\tfrac{j}{2\omega}(R/L-G/C)]$. The numerical check shows the first-order formulas are accurate to 2×10⁻⁵ above 100 MHz for a coax-like line, while near the $R=\omega L$ corner (≈1.3 MHz for $R=2$ Ω/m) the second-order term cuts the error in $\beta$ by ~8–50×.

**Where $G$ comes from.** A dielectric with loss tangent $\tan\delta$ gives $G=\omega C\tan\delta$ (see [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)). Then $\alpha_d=GZ_0/2=\tfrac{1}{2}\omega\sqrt{LC}\tan\delta=\pi\tan\delta/\lambda$ for a homogeneous TEM line — the dielectric loss per wavelength is fixed by $\tan\delta$ alone: $\alpha_d\lambda=27.3\tan\delta$ dB per wavelength.

**Where $R$ comes from.** At RF the current flows within a skin depth $\delta_s=\sqrt{2/(\omega\mu\sigma)}$ of the surface (copper: 66 µm/√(f/1 MHz) … 3.1 µm at 433 MHz, 1.3 µm at 2.45 GHz). The surface resistance is $R_s=1/(\sigma\delta_s)=\sqrt{\pi f\mu/\sigma}$ and $R\approx R_s/(\text{effective current-carrying perimeter})$. For coax, $R=\dfrac{R_s}{2\pi}\left(\dfrac1a+\dfrac1b\right)$ ([skin effect](../02-electromagnetics/skin-effect-conductor-loss-roughness.md)). Hence $\alpha_c\propto\sqrt f$ and $\alpha_d\propto f$ — the classic cable loss law $\alpha(f)=k_1\sqrt f+k_2f$ used on every coax datasheet.

**Distortionless line.** If $R/L=G/C$ (Heaviside's condition), then
$$\gamma=\sqrt{LC}\,\sqrt{(R/L+j\omega)(G/C+j\omega)}=\sqrt{LC}\,(R/L+j\omega)\;\Rightarrow\;\alpha=\sqrt{RG},\;\beta=\omega\sqrt{LC},\;Z_0=\sqrt{L/C}.$$
Attenuation and velocity are the same at all frequencies: a pulse is attenuated but not smeared. Real telephone pairs had $R/L\gg G/C$ (too little inductance), which smeared speech; Heaviside proposed, and Pupin and Campbell (c. 1900) implemented, *loading coils* every ~1.8 km to raise $L$. Verified in the script: $\alpha$ constant to 10⁻⁹ and $Z_0$ exactly real.

### Level 3 — where RLGC comes from, and where the model breaks

**RLGC from fields.** For a TEM line, $L$ and $C$ follow from 2-D electrostatics and magnetostatics of the cross-section ([inductance/capacitance from fields](../02-electromagnetics/inductance-capacitance-from-fields.md)). Because the transverse fields of a TEM mode obey the 2-D Laplace equation, the external inductance and capacitance of a line in a homogeneous medium satisfy $LC=\mu\varepsilon$ exactly, so $v_p=1/\sqrt{\mu\varepsilon}$ regardless of the conductor shape. Only $Z_0$ depends on geometry. For coax:
$$L=\frac{\mu}{2\pi}\ln\frac ba,\qquad C=\frac{2\pi\varepsilon}{\ln(b/a)},\qquad Z_0=\frac{1}{2\pi}\sqrt{\frac\mu\varepsilon}\ln\frac ba=\frac{60}{\sqrt{\varepsilon_r}}\ln\frac ba\ \Omega.$$
A useful general identity: if $C_\text{air}$ is the capacitance with the dielectric removed, $Z_0=1/(c\sqrt{C\,C_\text{air}})$ and $\varepsilon_\text{eff}=C/C_\text{air}$. This is exactly how quasi-static field solvers (and `tools/verify/tline_fd2d.py`, used by the planar-lines page) compute microstrip.

**Frequency dependence of the parameters.** $L$ has an external part (fields outside the metal, constant) plus an internal part from field penetrating the conductor. At DC the internal inductance of a round wire is $\mu/8\pi$ = 50 nH/m; at RF it falls as $1/\sqrt f$ and equals $R/\omega$ (the skin-effect surface impedance is $(1+j)R_s$). So both $R$ and $L$ vary with frequency, and causality links them (Kramers–Kronig). Likewise $\varepsilon_r$ and $\tan\delta$ of FR-4 drift with frequency; a causal wideband model such as Djordjevic–Sarkar is needed for time-domain simulation of digital channels.

**Low-frequency behaviour.** Below the corner $f_c=R/(2\pi L)$ (≈1 MHz for small coax, ~kHz for telephone twisted pair), $R$ dominates $j\omega L$ and $Z_0\to\sqrt{R/(j\omega C)}$: magnitude large and phase −45° ("RC line", diffusion rather than waves). The script shows a 50 Ω RF cable has $Z_0\approx1784\,\angle{-45°}$ Ω at 1 kHz. This is why audio/telephone engineers speak of 600 Ω or complex line impedances, and why "$Z_0$ is a constant" is an RF-only statement.

**Where the transmission-line model breaks.**
1. *Higher-order modes*: when the cross-section approaches $\lambda/2$ in the medium, waveguide modes can propagate (coax TE₁₁ cutoff ≈ $c/[\pi\sqrt{\varepsilon_r}\,(a+b)]$ with $a,b$ the conductor radii, e.g. 16.3 GHz for LMR-400, whose datasheet quotes 16.2 GHz; see [coax](coax-and-cables.md)). The single-$V$, single-$I$ picture then fails.
2. *Quasi-TEM dispersion*: microstrip, CPW — $\varepsilon_\text{eff}$ and $Z_0$ vary with frequency ([planar lines](planar-lines-microstrip-stripline-cpwg.md)).
3. *Radiation*: open structures (microstrip bends, unbalanced twin-lead, CPW without backing) radiate at discontinuities; this appears as extra loss not captured by $R$ and $G$.
4. *Non-uniform or coupled lines*: tapers, differential pairs, crosstalk — need multiconductor telegrapher equations with $\mathbf{L}$, $\mathbf{C}$ matrices (modal decomposition; see [s-parameters mixed-mode section](s-parameters.md)).
5. *Common-mode current on the shield outside*: coax has a third "conductor" — the outer surface of the shield. Currents there are not described by the coax $Z_0$ at all (see [reflections page on SWR myths](reflections-vswr-return-loss-mismatch.md)).

**Is the transmission-line treatment needed? — criteria.** For sinusoids, significant phase shift along the line matters when $\ell\gtrsim\lambda/10$ (36° of phase; some authors use $\lambda/20$ for precise work). For digital edges, a common criterion is one-way delay $t_d>t_r/6$ (some use $t_r/4$ or $t_r/2$) — thresholds are conventions, not physics; the real question is whether the reflection from a mismatch arrives while the edge is still rising.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $Z_0=\sqrt{(R+j\omega L)/(G+j\omega C)}$ | any uniform TEM/quasi-TEM line | — |
| $Z_0\approx\sqrt{L/C}$ | $R\ll\omega L$, $G\ll\omega C$ (RF) | 50 Ω coax: L ≈ 250 nH/m, C ≈ 100 pF/m |
| $\gamma=\sqrt{(R+j\omega L)(G+j\omega C)}$ | any | — |
| $\alpha\approx R/(2Z_0)+GZ_0/2$ Np/m | low loss | ×8.686 → dB/m |
| $\beta=\omega\sqrt{LC}=2\pi f\sqrt{\varepsilon_\text{eff}}/c$ | low loss | 433 MHz, VF 0.66: 13.7 rad/m |
| $VF=1/\sqrt{\varepsilon_r}$ | TEM, homogeneous | PE 0.66, PTFE 0.695, foam 0.80–0.88, air 1 |
| $L=Z_0/v_p$, $C=1/(Z_0v_p)$ | lossless | — |
| $\alpha_d\lambda=27.3\tan\delta$ dB | homogeneous TEM | FR-4 ($\tan\delta$≈0.02): 0.55 dB per wavelength |
| $\alpha(f)=k_1\sqrt f+k_2 f$ | cable datasheet fits | LMR-400: see [coax](coax-and-cables.md) |
| $R/L=G/C$ ⇒ distortionless | Heaviside | — |
| $Z_0=\sqrt{Z_\text{oc}Z_\text{sc}}$, $\tanh\gamma\ell=\sqrt{Z_\text{sc}/Z_\text{oc}}$ | measurement of unknown line | — |
| TL treatment needed if $\ell>\lambda/10$ or $t_d>t_r/6$ | rule of thumb | 433 MHz on FR-4 microstrip: λ/10 ≈ 38 mm |

## Worked examples

### Example 1 — RG-58 from its geometry
Belden 8240 (RG-58): solid copper centre 0.033 in (0.838 mm, $a=0.419$ mm), PE insulation OD 2.95 mm ($b=1.475$ mm), stated VF 0.66 [5].
- $\varepsilon_r=1/0.66^2=2.30$.
- $Z_0=\dfrac{60}{\sqrt{2.30}}\ln\dfrac{1.475}{0.419}=39.6\times1.259=49.8$ Ω. Datasheet: 52 Ω nominal (51.5 ± 1.5 Ω). The braid's effective radius is larger than the insulation radius, which pushes the real $Z_0$ up.
- $L=\dfrac{\mu_0}{2\pi}\ln\dfrac ba=2\times10^{-7}\times1.259=252$ nH/m; $C=\dfrac{2\pi\varepsilon_0\varepsilon_r}{\ln(b/a)}=101.5$ pF/m (datasheet 93.5 pF/m).
- Note: the datasheet's *own* numbers imply $Z_0=1/(v_pC)=1/(0.66\,c\times93.5\,\text{pF/m})=54$ Ω, not 52 Ω. Nominal values on cable datasheets are mutually consistent only to ~5 %. Trust a measurement ([TDR](time-domain-reflectometry.md)) over arithmetic on datasheet nominals.
- Conductor loss at 433 MHz: $R_s=\sqrt{\pi\times433\times10^6\times4\pi\times10^{-7}/5.8\times10^7}=5.43$ mΩ; $R=\dfrac{R_s}{2\pi}(1/a+1/b)=\dfrac{5.43\times10^{-3}}{2\pi}(2387+678)=2.65$ Ω/m; $\alpha_c=R/(2Z_0)=0.0266$ Np/m = 0.231 dB/m = 7.0 dB/100 ft. Add PE dielectric loss ($\tan\delta\approx2\times10^{-4}$): $\alpha_d=\pi\sqrt{\varepsilon_r}\tan\delta/\lambda_0=0.0014$ Np/m — small (0.37 dB/100 ft). The script's theory total at 400 MHz is 7.1 dB/100 ft vs the datasheet's 8.4 dB/100 ft. The script tabulates 1–1000 MHz: the datasheet exceeds smooth-solid-copper theory by 10 % at 100 MHz, rising to 26 % at 1 GHz — tinned braid, braid weave and roughness add loss.

### Example 2 — quarter wave of RG-58 and of LMR-400 at 433 MHz
$\lambda_0=c/f=692.3$ mm. RG-58 (VF 0.66): $\lambda/4=0.66\times692.3/4=114.2$ mm. LMR-400 (VF 0.85): 147.1 mm. A stub cut with the wrong VF is off by 29 % — at 433 MHz that shifts its resonance to ~560 MHz.

### Example 3 — is my PCB trace a transmission line?
A 25 mm trace on 1.6 mm FR-4 ($\varepsilon_r=4.5$) feeding a 433 MHz LoRa module. A 50 Ω microstrip here is 3.0 mm wide with $\varepsilon_\text{eff}\approx3.4$ (model with h = 1.6 mm, bare; the JLC0216A calculator width to order is 2.69 mm masked — [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)) ([planar lines](planar-lines-microstrip-stripline-cpwg.md)): $\lambda=c/(f\sqrt{3.4})=375$ mm, so $\ell/\lambda=0.067$ (24° of phase). Borderline: if the trace is 50 Ω, its length only adds 24° of phase and a little loss. But if it is drawn as a "normal" 0.5 mm signal trace, Hammerstad–Jensen gives $Z_0\approx108$ Ω, $\varepsilon_\text{eff}\approx3.0$, so the 25 mm is 22.6° of 108 Ω line, which transforms a perfect 50 Ω antenna into $Z_\text{in}\approx56.5+j33.9$ Ω ($|\Gamma|=0.31$, VSWR 1.9) at the module pin — computed with the formula in [input impedance](input-impedance-stubs-quarter-wave.md) and scikit-rf `MLine`. At 2.45 GHz the same trace is ≈130° long: definitely a transmission line.

### Example 4 — the ohmmeter step
A 10 m open-ended 50 Ω cable (VF 0.66, one-way delay 50.5 ns) is connected to a source with 1 kΩ internal resistance and a 1 V step. For the first $2t_d=101$ ns, the current is $1/(1000+50)=0.952$ mA — the cable looks like 50 Ω. The reflection from the open end then returns, and after many round trips the current dies out; total delivered charge = $C_\text{line}V=10\times101\text{ pF}\times1\text{ V}=1.01$ nC, i.e. the line has charged like a 1 nF capacitor (script: 1010.8 pC both ways). A multimeter, integrating over milliseconds, sees an open.

### Example 5 — measuring $Z_0$ and VF of an unknown cable with a NanoVNA
Measure the same cable with the far end open ($Z_\text{oc}$) then shorted ($Z_\text{sc}$) at a frequency where it is *not* near $\lambda/4$ multiples (where one of the two blows up). Then
$$Z_0=\sqrt{Z_\text{oc}Z_\text{sc}},\qquad \tanh\gamma\ell=\sqrt{Z_\text{sc}/Z_\text{oc}}.$$
Proof: $Z_\text{oc}=Z_0\coth\gamma\ell$ and $Z_\text{sc}=Z_0\tanh\gamma\ell$ (from the input-impedance formula), so their product is $Z_0^2$ and their ratio $\tanh^2\gamma\ell$. For VF: sweep the open cable and find the lowest frequency $f_1$ where $Z_\text{in}$ crosses zero reactance with a low value (the $\lambda/4$ series resonance): $VF=4\ell f_1/c$. Example: a 1.000 m cable resonating at $f_1=49.5$ MHz has $VF=4\times1\times49.5\times10^6/3\times10^8=0.660$. Include connector length in $\ell$.

## Practical notes
- **Where it bites Marcus's hardware**: the EBYTE E22-400T33D and E220-900T30D modules have a 50 Ω RF port; everything between the module pad (or its U.FL/SMA) and the antenna — PCB trace, U.FL pigtail, SMA bulkhead, coax to the fin/nose-cone antenna — is a transmission line at 433 and 915 MHz. At 1575 MHz (GNSS) even a 10 mm trace is 37° long on FR-4.
- **Velocity factor matters only when length matters**: in a well-matched system (everything 50 Ω) cable length changes phase and loss but not impedance. Length becomes critical for stubs, phasing lines in arrays, λ/4 transformers, and Wilkinson/branch-line designs.
- **Datasheet VF and $Z_0$ are nominal**: ±1–3 Ω and ±1–2 % VF are common; phased-array feed harnesses must be trimmed by measurement, not by length.
- **Temperature**: PTFE has a phase discontinuity near 19 °C (crystal transition) — relevant to phase-matched cables in outdoor arrays (see [coax](coax-and-cables.md)).
- **Loss rises fast with frequency on thin cable**: U.FL 1.13 mm micro-coax is ~3.7 dB/m at 3 GHz [6]; keep pigtails to a few centimetres, especially for GNSS where every 0.1 dB before the LNA adds directly to the noise figure ([noise figure](../07-noise-linearity/noise-figure-and-friis.md)).

## Common mistakes & misconceptions
- **"A 50 Ω cable is a 50 Ω resistor."** No; it stores and transports energy and dissipates only its small $\alpha$. It *looks* like 50 Ω to a source only when terminated in 50 Ω (or for the round-trip time before reflections return).
- **"I measured my coax with a multimeter and it isn't 50 Ω, so it's faulty."** The multimeter measures DC continuity only. Use a TDR/VNA.
- **"Characteristic impedance depends on length."** It doesn't; $Z_0$ is per-cross-section. *Input* impedance depends on length and load.
- **"Velocity factor is the same for all coax."** It depends on the dielectric: 0.66 (solid PE: RG-58, RG-174, RG-213), 0.69–0.70 (PTFE: RG-316, RG-402/405), 0.80–0.88 (foam: LMR series).
- **"Z0 is always real."** Only approximately, at RF, for low-loss lines. At audio frequencies it is large and ~−45°; lossy lines have a small imaginary part even at RF, which matters for precise VNA calibration standards (see [s-parameters](s-parameters.md) on pseudo-waves).
- **"Doubling frequency doubles the loss in dB."** Only for dielectric loss. Conductor loss scales as $\sqrt f$; the total follows $k_1\sqrt f+k_2f$.
- **"Microstrip VF = 1/√εr of the board."** No — use $\varepsilon_\text{eff}$ (≈3.3–3.5 for FR-4 microstrip, not 4.5).
- **"Low-loss approximation formulas for α hold down to DC."** They fail below $f=R/(2\pi L)$.

## How to simulate / verify
- `tools/verify/tline_telegrapher.py` — checks the closed-form $Z_0$, $\gamma$ and $Z_\text{in}$ of a lossy RLGC line against scikit-rf, low-loss approximations, the distortionless line, RG-58 from geometry vs Belden data, the step-into-open-line (ohmmeter) bounce calculation, and the telegrapher PDE solution with sympy. All checks pass.
- scikit-rf snippet — build any line from RLGC:

```python
import numpy as np, skrf as rf
f = rf.Frequency(1, 3000, 301, unit='MHz')
w = 2*np.pi*f.f
R, L, G, C = 2.0, 250e-9, 1e-5, 100e-12          # per metre
Zp, Yp = R + 1j*w*L, G + 1j*w*C
med = rf.media.DefinedGammaZ0(frequency=f, gamma=np.sqrt(Zp*Yp), z0=np.sqrt(Zp/Yp), z0_port=50)
line = med.line(1.0, unit='m')                    # 1 m two-port referenced to 50 ohm
print(line.s21.s_db[::100, 0, 0])                 # insertion loss vs frequency
```
- For coax use `rf.media.Coaxial(frequency, Dint, Dout, epsilon_r, tan_delta, sigma)`; for microstrip `rf.media.MLine`; for CPW `rf.media.CPW`.
- SPICE: ngspice's lossy `LTRA` or the ideal `T` element; a 100-section RLGC ladder reproduces the distributed behaviour up to ~(sections/10) wavelengths.

## Open questions / gaps
- Wideband causal dielectric models (Djordjevic–Sarkar) and conductor-roughness models (Huray, Groiss) are only mentioned; they belong with [skin effect/roughness](../02-electromagnetics/skin-effect-conductor-loss-roughness.md) and [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md).
- Multiconductor telegrapher equations (matrix $\mathbf{L},\mathbf{C}$, modal decomposition) are sketched only in [s-parameters](s-parameters.md) and [planar lines](planar-lines-microstrip-stripline-cpwg.md); crosstalk belongs to 13-pcb-rf-layout-emc.
- Braid-shield loss increment (10–30 % over theory for RG-58) is shown from one datasheet; a proper braid model (e.g. Kley's transfer-impedance model) is not included.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §2.1 (lumped-element model, telegrapher equations), §2.2 (field analysis, coax L, C), §2.7 (lossy lines, low-loss approximation, distortionless line, perturbation method). (textbook)
2. R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., McGraw-Hill 1992 / IEEE Press 2001 — ch. 3 (TEM lines, $LC=\mu\varepsilon$, losses). (textbook)
3. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online, rev. 2016), chapter "Transmission Lines" (chapter number differs between revisions) — https://eceweb1.rutgers.edu/~orfanidi/ewa/ — lossy line, $Z_0$ and $\gamma$ derivations, coax. (textbook, free)
4. M. Steer, *Microwave and RF Design, Vol. II: Transmission Lines*, 3rd ed., NC State University Libraries, 2019 (open access; mirrored on LibreTexts) — RLGC model, low-frequency behaviour, dispersion. (textbook, free)
5. Belden, "8240 RG-58 50 Ω coax" technical data sheet, rev. 0.541, 2026 — https://catalog.belden.com/techdata/EN/8240_techdata.pdf — dimensions, VF, capacitance, attenuation table 1–1000 MHz. (datasheet)
6. Hirose Electric, "U.FL Series" catalog, 2020 — micro-coax attenuation (1.13 mm: 3.73 dB/m at 3 GHz). (datasheet)
7. P. J. Nahin, *Oliver Heaviside: The Life, Work, and Times of an Electrical Genius of the Victorian Age*, Johns Hopkins, 2002 — history of the telegrapher equations, distortionless condition, loading coils. (book)
8. EE Stack Exchange / ResearchGate Q&A threads on "why does a 50 Ω coax read open on a multimeter" (e.g. researchgate.net/post/Why-is-the-cable-impedance-of-50-ohm-cable-is-considered-to-be-real…) — used only to identify the common confusion. (forum — anecdotal)
9. Verification: `tools/verify/tline_telegrapher.py` (this KB), scikit-rf 2.0.1 `DefinedGammaZ0`. (numerical check)
