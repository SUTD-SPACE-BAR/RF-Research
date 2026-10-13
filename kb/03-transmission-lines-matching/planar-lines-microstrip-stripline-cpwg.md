---
title: Planar lines — microstrip, stripline, CPW/CPWG and differential pairs
domain: 03-transmission-lines-matching
slug: planar-lines-microstrip-stripline-cpwg
tags: [microstrip, stripline, coplanar-waveguide, cpwg, grounded-coplanar, differential-pair, coupled-microstrip, offset-stripline, hammerstad-jensen, kirschning-jansen, wheeler, conformal-mapping, jlcpcb, stackup, pcb-impedance, soldermask, trapezoidal-etch, field-solver, power-handling, trace-heating, ipc-2152]
prerequisites:
  - telegrapher-equations-characteristic-impedance.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
related:
  - s-parameters.md
  - impedance-matching-lumped-and-distributed.md
  - input-impedance-stubs-quarter-wave.md
  - time-domain-reflectometry.md
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
  - ../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md
  - ../13-pcb-rf-layout-emc/vias-stitching-fencing.md
  - ../16-simulation-tools/impedance-and-rf-calculators.md
  - microstrip-discontinuities.md
  - ../13-pcb-rf-layout-emc/thermal-management-rf.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Planar lines — microstrip, stripline, CPW/CPWG and differential pairs

## Questions this page answers
- How wide should a 50 Ω trace be on a JLCPCB 2-layer 1.6 mm board, and on the 4-layer JLC04161H-7628 stackup?
- What are the Hammerstad–Jensen, Wheeler and Kirschning–Jansen formulas, and how accurate are they?
- Why is microstrip "quasi-TEM" and what is effective permittivity?
- When should I use grounded coplanar waveguide (CPWG) instead of microstrip?
- How much do copper thickness and soldermask change the impedance?
- How do I design a 100 Ω differential pair? Is the IPC-2141 formula good enough?
- How lossy is a trace on FR-4 at 433 MHz, 915 MHz, 2.45 GHz and 5.8 GHz?
- At what frequency do microstrip lines start to misbehave (dispersion, surface waves, radiation)?
- Why does my impedance calculator disagree with another one?
- Which closed form should I use for coupled microstrip (even/odd mode), and how good is it?
- What 50 Ω width do I need for an inner-layer (offset) stripline on a JLC 6-layer board?
- How much does the trapezoidal etch profile change the impedance?
- How much RF power can a PCB trace carry? Will the 2 W trace from my E22 module get hot? Can I use IPC-2152 for RF?
- Does an RF ground plane have to be "50 Ω" too?
- Where do I find models for open ends, gaps, steps, bends and T-junctions?

## TL;DR
- **Microstrip** 50 Ω widths (verified with the Hammerstad–Jensen formulas *and* an independent 2-D field solver written for this KB):
  - JLCPCB 2-layer 1.6 mm FR-4 modelled as h = 1.51 mm (board minus copper; εr ≈ 4.5) — 1.6 mm is the finished board thickness, not the dielectric, and JLC's own stackup has a 1.43 mm core (below): **2.80 mm** (2.71–2.90 mm for εr 4.7–4.3), $\varepsilon_\text{eff}\approx3.36$. (Taking h = 1.6 mm, as other pages of this KB do for round numbers, gives 2.97 mm, εeff 3.37.) **To order:** JLC's calculator for its JLC0216A 2-layer template (1.43 mm core, εr 4.5, 30 µm Cu, mask) gives **2.69 mm** masked ([canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)); 1.51 mm and 1.6 mm here are model inputs, not JLC's stated dielectric.
  - JLC04161H-7628 (L1→L2 prepreg 0.2104 mm, εr 4.4): **0.372 mm** bare, ≈ **0.34–0.35 mm** with soldermask; $\varepsilon_\text{eff}\approx3.2$–3.35. (JLC's calculator, trapezoid + conformal mask: **0.359 mm masked / 0.377 mm bare** — order with the fab value, [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table).)
  - JLC04161H-2116 (0.1164 mm, 4.16): 0.206 mm; -3313 (0.0994 mm, 4.1): 0.175 mm; -1080 (0.0764 mm, 3.91): 0.135 mm (bare).
- **CPWG** on the 2-layer 1.6 mm board (35 µm copper, bottom ground, via-stitched top ground): gap 0.15 / 0.20 / 0.25 / 0.30 mm → trace **0.76 / 1.01 / 1.22 / 1.39 mm** for 50 Ω (bare, h = 1.51 mm, εr 4.5; JLC calculator on JLC0216A at a 0.203 mm gap: 0.918 mm masked / 1.089 mm bare) — a pad-sized trace instead of a 2.8 mm microstrip. This is the main reason to use CPWG on thin-layer-count boards.
- **Accuracy**: Hammerstad–Jensen agrees with the field solver to ≤ 0.4 % (W/h 0.1–10, εr 2.2–10); its thickness correction to 0.2 %; Wheeler-77 and the simple Hammerstad-75 (Pozar) forms to ~1 %; Ghione–Naldi CPWG to ≤ 1 % for gaps < 2h (but it fails as the gap → ∞).
- **Second-order effects are several ohms**: 35 µm copper lowers Z0 by 2–5 Ω on thin prepregs; soldermask (εr ≈ 3.8) lowers microstrip by ~1–2.5 Ω and CPWG/differential pairs by 3–10 Ω. Published JLC-stackup designs (JITX, JLC calculator) only reconcile with field solutions *including* soldermask.
- **Dispersion** is negligible at 433–915 MHz and small at 2.45 GHz (εeff +1.5 % on 1.6 mm FR-4, +0.08 % on 0.21 mm prepreg); it matters at 24 GHz on thick boards (+20 %).
- **Loss** (50 Ω, tanδ 0.02): 1.6 mm FR-4 microstrip 0.016 / 0.032 / 0.082 / 0.19 dB/cm at 0.433 / 0.915 / 2.45 / 5.8 GHz (dielectric-dominated); on the thin 0.21 mm prepreg the narrow trace roughly doubles it at UHF (conductor loss 0.02–0.03 dB/cm).
- **Differential pairs**: JLC04161H-7628 0.172/0.15 mm (W/s) is 109 Ω bare, ≈ 98 Ω with soldermask; the IPC-2141 approximation is within 1 % of the field solver for these bare geometries. The **Kirschning–Jansen (1984) coupled-microstrip closed form** agrees with the field solver to **≤ 0.6 %** in all four mode parameters (u 0.3–3, g 0.2–2, t = 0); the Hammerstad–Jensen coupled branch as coded in Qucs is off by up to 19 % in impedance — use K-J.
- **Inner layers on JLC 6-layer** (L3 between L2/L4 planes, offset stripline, field solver, 15 µm Cu): 50 Ω is **0.136 mm** on JLC06161H-3313 and **0.241 mm** on JLC06161H-1080 — the near plane (0.11 / 0.21 mm prepreg) sets the width. **Trapezoidal etch** (JLC: top 0.5 mil narrower) raises Z0 by only 0.27 Ω on a 0.377 mm trace; a rectangle at the mean width reproduces it.
- **Power handling** ([§ below](#level-3--power-handling-of-rf-traces)): RF current crowds into the skin and edges, so a trace's RF resistance is **15–55× its DC resistance** at 0.43–2.45 GHz; feed a DC rule (IPC-2221/2152) the *DC-equivalent* current $\sqrt{p'/R'_{DC}}$, not the RF current. The E22's 2 W at 433 MHz on JLC-7628 heats even an infinitely long trace by only ≈ 3 K (a 3 cm trace dissipates 45 mW). 25 W at 2.45 GHz on the same 0.36 mm trace is a real limit (≈ 150 K for a long line; 3.6 W in 5 cm). Peak voltage (50 V at 25 W, 75 V at VSWR 3) is far below air's ≈ 327 V Paschen minimum.
- **Ground planes are not "50 Ω"**: Z0 belongs to the signal-plus-return cross-section; the plane is the return conductor and should have the *lowest* possible impedance (≈ 5–13 mΩ/□ surface resistance at 0.43–2.45 GHz) and be continuous under the trace.
- **Discontinuities** (open end, gap, step, bend, T, via): see [microstrip discontinuities](microstrip-discontinuities.md).

## Intuition (no math)
A microstrip is a strip on top of a dielectric sheet with a ground plane below. Most of the electric field runs straight down through the board, but some fringes out of the strip edges and through the air above. Because part of the energy is in air ($\varepsilon_r=1$) and part in the board, the wave can't be purely TEM (it would need a single speed); it is **quasi-TEM**, travelling at a speed set by an *effective* permittivity somewhere between 1 and $\varepsilon_r$. Wider strips put more of the field in the board: $\varepsilon_\text{eff}$ rises and $Z_0$ falls (more capacitance, less inductance per metre). A thinner board brings the ground closer: again more capacitance, so for the same 50 Ω you need a narrower strip — 2.8 mm on a 1.6 mm board, 0.37 mm on a 0.21 mm prepreg.

**Stripline** buries the strip between two ground planes in a homogeneous dielectric: it is truly TEM, non-dispersive, well shielded, but slower (full $\varepsilon_r$) and needs vias to reach components. **Coplanar waveguide** puts ground metal beside the strip on the same layer; with a ground plane underneath too (CPWG, "grounded coplanar"), the fields split between the side gaps and the plane below. Narrow gaps pull a lot of capacitance into the side walls, so a 50 Ω CPWG trace can be much narrower than a microstrip on the same board. The cost is sensitivity to the gap (etching tolerance, soldermask filling the gap) and the need for via fences to keep the side grounds at the same potential as the bottom plane.

## The math

### Level 1 — what to compute and with which formula

| Line | Quantity | Recommended closed form | Accuracy (checked here) |
|---|---|---|---|
| Microstrip | $Z_0$, $\varepsilon_\text{eff}$ (static) | Hammerstad–Jensen 1980 (+ thickness) | ≤ 0.4 % vs field solver |
| Microstrip | dispersion $\varepsilon_\text{eff}(f)$, $Z_0(f)$ | Kirschning–Jansen 1982 / Jansen–Kirschning 1983 | stated ≤ 0.6 % to 60 GHz·mm [4] |
| Microstrip | quick estimate | Hammerstad-75 (Pozar §3.8), Wheeler 1977 | ~1 % |
| Microstrip | synthesis W from Z0 | Pozar eq. 3.197 closed form, or root-find H-J | ≤ 0.25 % vs H-J |
| Stripline (centred) | $Z_0$ | Cohn 1954 exact (t = 0); Wheeler 1978 (t > 0) | exact / ≈ 1 % |
| CPW / CPWG | $Z_0$, $\varepsilon_\text{eff}$ | conformal mapping (Ghione–Naldi 1984; Simons 2001) | ≤ 1 % for gap < 2h, t = 0 |
| Coupled microstrip | $Z_e$, $Z_o$, $\varepsilon_{\text{eff},e/o}$ | Kirschning–Jansen 1984 | ≤ 0.6 % vs field solver (u 0.3–3, g 0.2–2) |
| Offset (asymmetric) stripline, mixed dielectrics | $Z_0$ | 2-D field solver (closed forms are rough) | — |
| Open ends, gaps, steps, bends, T-junctions | equivalent circuits | Kirschning–Jansen–Koster, Hammerstad, Gupta → [discontinuities page](microstrip-discontinuities.md) | see that page |
| Anything else (thick Cu, mask, asymmetric) | — | 2-D field solver | reference |

All symbols: $W$ strip width, $h$ dielectric height (strip to ground), $t$ copper thickness, $u=W/h$, $\varepsilon_r$ substrate permittivity, $\eta_0=376.73$ Ω.

### Level 2 — the formulas

**Why a capacitance ratio gives everything (quasi-static).** With $C$ the capacitance per metre with the dielectric and $C_a$ with the dielectric replaced by air (the inductance does not depend on a non-magnetic dielectric, so $L=1/(c^2C_a)$):
$$Z_0=\frac{1}{c\sqrt{CC_a}},\qquad\varepsilon_\text{eff}=\frac{C}{C_a},\qquad v_p=\frac{c}{\sqrt{\varepsilon_\text{eff}}}.$$
This is exactly what the field solver `tools/verify/tline_fd2d.py` computes (finite-volume Laplace solution on a graded mesh, capacitance from stored energy, Richardson extrapolation over three meshes; it reproduces Cohn's exact stripline to ≤ 0.13 % and agrees within 0.1–0.2 % with the separate uniform-grid solver written by the electromagnetics agent in `tools/verify/em_inductance.py`).

**Hammerstad & Jensen (1980), zero thickness.**
$$Z_{01}(u)=\frac{\eta_0}{2\pi}\ln\!\left[\frac{f(u)}{u}+\sqrt{1+\frac{4}{u^2}}\right],\qquad f(u)=6+(2\pi-6)\exp\!\left[-\left(\frac{30.666}{u}\right)^{0.7528}\right],$$
$$\varepsilon_\text{eff}=\frac{\varepsilon_r+1}{2}+\frac{\varepsilon_r-1}{2}\left(1+\frac{10}{u}\right)^{-ab},\quad a=1+\frac1{49}\ln\frac{u^4+(u/52)^2}{u^4+0.432}+\frac1{18.7}\ln\!\left[1+\left(\frac u{18.1}\right)^3\right],\quad b=0.564\left(\frac{\varepsilon_r-0.9}{\varepsilon_r+3}\right)^{0.053},$$
$$Z_0=Z_{01}(u)/\sqrt{\varepsilon_\text{eff}}.$$
**Thickness correction** (normalised $t_n=t/h$): $\Delta u_1=\dfrac{t_n}{\pi}\ln\!\left[1+\dfrac{4e}{t_n\coth^2\sqrt{6.517u}}\right]$, $\Delta u_r=\tfrac12\left[1+\mathrm{sech}\sqrt{\varepsilon_r-1}\right]\Delta u_1$; then $Z_0=Z_{01}(u+\Delta u_r)/\sqrt{\varepsilon_\text{eff}(u+\Delta u_r)}$ and $\varepsilon_\text{eff}=\varepsilon_\text{eff}(u+\Delta u_r)\,[Z_{01}(u+\Delta u_1)/Z_{01}(u+\Delta u_r)]^2$. (A web summary of the Qucs documentation garbled the $a(u)$ term; the form above is the one in scikit-rf's source and the one that matches the field solver.)

**Simple forms (Hammerstad 1975, as in Pozar):** $\varepsilon_\text{eff}=\frac{\varepsilon_r+1}2+\frac{\varepsilon_r-1}{2\sqrt{1+12/u}}$; $Z_0=\frac{60}{\sqrt{\varepsilon_\text{eff}}}\ln(8/u+u/4)$ for $u\le1$, $Z_0=\frac{120\pi}{\sqrt{\varepsilon_\text{eff}}\,[u+1.393+0.667\ln(u+1.444)]}$ for $u\ge1$. Synthesis: with $A=\frac{Z_0}{60}\sqrt{\frac{\varepsilon_r+1}2}+\frac{\varepsilon_r-1}{\varepsilon_r+1}\left(0.23+\frac{0.11}{\varepsilon_r}\right)$ and $B=\frac{377\pi}{2Z_0\sqrt{\varepsilon_r}}$: $u=\frac{8e^A}{e^{2A}-2}$ if that is < 2, else $u=\frac2\pi\left[B-1-\ln(2B-1)+\frac{\varepsilon_r-1}{2\varepsilon_r}\left(\ln(B-1)+0.39-\frac{0.61}{\varepsilon_r}\right)\right]$.

**Wheeler (1977)**: $Z_0=\dfrac{\eta_0}{2\pi\sqrt{2(1+\varepsilon_r)}}\ln\!\left\{1+\dfrac{4h}{W'}\left[\kappa+\sqrt{\kappa^2+\frac{\pi^2}{2}\left(1+\frac1{\varepsilon_r}\right)}\right]\right\}$, $\kappa=\dfrac{14+8/\varepsilon_r}{11}\dfrac{4h}{W'}$, with $W'$ the thickness-corrected width. Wheeler derived it by conformal mapping plus curve fitting; it is the basis of many online calculators (and of IPC-2141's older formulas' successors).

**Kirschning–Jansen dispersion (1982).** With $f_n=f\,[\text{GHz}]\cdot h\,[\text{mm}]$:
$$\varepsilon_\text{eff}(f)=\varepsilon_r-\frac{\varepsilon_r-\varepsilon_\text{eff}(0)}{1+P(f)},\qquad P=P_1P_2\left[(0.1844+P_3P_4)f_n\right]^{1.5763},$$
$P_1=0.27488+\left[0.6315+\frac{0.525}{(1+0.0157f_n)^{20}}\right]u-0.065683e^{-8.7513u}$, $P_2=0.33622(1-e^{-0.03442\varepsilon_r})$, $P_3=0.0363e^{-4.6u}\left[1-e^{-(f_n/38.7)^{4.97}}\right]$, $P_4=1+2.751\left[1-e^{-(\varepsilon_r/15.916)^8}\right]$. The companion $Z_0(f)=Z_0(0)(R_{13}/R_{14})^{R_{17}}$ uses 17 fitted coefficients (Jansen & Kirschning 1983) — implemented in `tools/verify/tline_microstrip.py` (`ms_kj`), identical to scikit-rf's `MLine(disp='kirschningjansen')` to 10⁻⁹. Kobayashi and Yamashita models agree to < 1 % below 6 GHz for the boards here.

**Stripline.** Centred strip, zero thickness, ground spacing $b$ (Cohn, exact conformal map):
$$Z_0=\frac{30\pi}{\sqrt{\varepsilon_r}}\frac{K(k)}{K(k')},\quad k=\mathrm{sech}\frac{\pi W}{2b},\ k'=\sqrt{1-k^2}.$$
Finite thickness (Wheeler 1978): $Z_0=\frac{30}{\sqrt{\varepsilon_r}}\ln\left\{1+\frac4\pi\frac{b-t}{W'}\left[\frac8\pi\frac{b-t}{W'}+\sqrt{\left(\frac8\pi\frac{b-t}{W'}\right)^2+6.27}\right]\right\}$ with $W'=W+\Delta W$, $\frac{\Delta W}{b-t}=\frac{x}{\pi}\left\{1-\frac12\ln\left[\left(\frac{x}{2-x}\right)^2+\left(\frac{0.0796x}{W/b+1.1x}\right)^m\right]\right\}$, $x=t/b$, $m=2/[1+\frac23x/(1-x)]$. Checked: within 0.2 % (t = 17.5 µm) and 1.0 % (t = 35 µm, b = 0.4 mm) of the field solver. $\varepsilon_\text{eff}=\varepsilon_r$ exactly (TEM), so stripline λ is shorter than microstrip λ by $\sqrt{\varepsilon_r/\varepsilon_\text{eff}}$ ≈ 1.15 on FR-4.

**CPW and CPWG (conformal mapping).** Half-widths $a=W/2$, $b=W/2+S$ (S = gap), $K(k)$ the complete elliptic integral:
- CPW on a substrate of thickness $h$, no backside metal: $k_0=a/b$, $k_1=\dfrac{\sinh(\pi a/2h)}{\sinh(\pi b/2h)}$, $\varepsilon_\text{eff}=1+\dfrac{\varepsilon_r-1}2\dfrac{K(k_1)K(k_0')}{K(k_1')K(k_0)}$, $Z_0=\dfrac{30\pi}{\sqrt{\varepsilon_\text{eff}}}\dfrac{K(k_0')}{K(k_0)}$.
- CPWG (conductor-backed): $k_3=\dfrac{\tanh(\pi a/2h)}{\tanh(\pi b/2h)}$, $q=\dfrac{K(k_3)/K(k_3')}{K(k_0)/K(k_0')}$, $\varepsilon_\text{eff}=\dfrac{1+\varepsilon_rq}{1+q}$, $Z_0=\dfrac{60\pi}{\sqrt{\varepsilon_\text{eff}}}\dfrac{1}{K(k_0)/K(k_0')+K(k_3)/K(k_3')}$.
These assume zero thickness and infinitely wide top grounds. Field-solver checks (script `tline_cpwg.py`): ≤ 1 % error for S < 2h; for larger gaps the CPWG formula keeps rising while the true impedance saturates at the microstrip value (W = 3 mm on 1.51 mm: formula 51.0 Ω at S = 6 mm vs field 48.1 Ω, microstrip 48.4 Ω). With 35 µm copper and narrow gaps the formula is 3–4 Ω high (the gap side walls add capacitance) — use a solver for S ≲ 0.3 mm.

**Edge-coupled microstrip (differential pairs).** Two modes: even (both strips +1 V, common mode) and odd (±1 V, differential). $Z_\text{diff}=2Z_\text{odd}$, $Z_\text{comm}=Z_\text{even}/2$; odd mode has more field in air (lower $\varepsilon_\text{eff}$). Closed forms exist; the one to use is Kirschning–Jansen (below), checked here against the field solver. The widely quoted IPC-2141 approximation $Z_\text{diff}\approx2Z_0(1-0.48e^{-0.96s/h})$ happened to be within 1 % of the solver for the bare JLC-7628 geometries tested, but it contains no dependence on εr or W beyond $Z_0$ and should be treated as an estimate.

**Coupled microstrip in closed form (Kirschning & Jansen 1984).** Write $u=W/h$, $g=s/h$ (s = edge gap), and let $\varepsilon_\text{eff}(x)$ and $Z_L(x)=Z_{01}(x)/\sqrt{\varepsilon_\text{eff}(x)}$ be the single-line Hammerstad–Jensen functions above evaluated at normalised width $x$. The quasi-static mode permittivities are
$$\varepsilon_{\text{eff},e}=\varepsilon_\text{eff}(v),\qquad v=u\,\frac{20+g^2}{10+g^2}+g\,e^{-g}$$
(the even mode behaves like one wider strip), and
$$\varepsilon_{\text{eff},o}=\Big[\tfrac{\varepsilon_r+1}{2}+a_o-\varepsilon_\text{eff}(u)\Big]e^{-c_og^{d_o}}+\varepsilon_\text{eff}(u),$$
with $a_o=0.7287\,[\varepsilon_\text{eff}(u)-\tfrac{\varepsilon_r+1}2](1-e^{-0.179u})$, $b_o=0.747\varepsilon_r/(0.15+\varepsilon_r)$, $c_o=b_o-(b_o-0.207)e^{-0.414u}$, $d_o=0.593+0.694e^{-0.562u}$. The impedances are the single-line value corrected by a coupling term,
$$Z_{e}=\frac{Z_L(u)\sqrt{\varepsilon_\text{eff}(u)/\varepsilon_{\text{eff},e}}}{1-\frac{Z_L(u)}{\eta_0}\sqrt{\varepsilon_\text{eff}(u)}\,Q_4},\qquad Z_{o}=\frac{Z_L(u)\sqrt{\varepsilon_\text{eff}(u)/\varepsilon_{\text{eff},o}}}{1-\frac{Z_L(u)}{\eta_0}\sqrt{\varepsilon_\text{eff}(u)}\,Q_{10}},$$
where $Q_4=\dfrac{2Q_1/Q_2}{e^{-g}u^{Q_3}+(2-e^{-g})u^{-Q_3}}$, $Q_1=0.8695u^{0.194}$, $Q_2=1+0.7519g+0.189g^{2.31}$, $Q_3=0.1975+(16.6+(8.4/g)^6)^{-0.387}+\tfrac{1}{241}\ln\frac{g^{10}}{1+(g/3.4)^{10}}$, and $Q_{10}$ is built from five more fitted terms $Q_5$–$Q_9$ (all in `tools/verify/s6_coupled_offset.py`). The paper also gives dispersion and a thickness correction (Jansen's even/odd width increments). **Check** (t = 0, εr 4.4, 12 geometries u 0.3–3 × g 0.2–2): all four quantities within **0.54 %** of the field solver; on the JLC-7628 pair (0.1722/0.15 mm, t = 0) K-J gives $Z_\text{diff}$ 124.0 Ω vs 124.1 Ω (FD); copper thickness then lowers it to the 109 Ω quoted above. The older Hammerstad–Jensen (1980) coupled-line equations, *as implemented in qucsator's `mscoupled.cpp`* (whose authors flag one term as uncertain), reproduce the mode permittivities to 0.3 % but the impedances only to 19 % — so either that coding or our transcription of it is off; use K-J or the solver.

### Level 3 — losses, dispersion limits, higher-order modes
**Conductor loss (Hammerstad/Wheeler incremental-inductance style)**: $\alpha_c\approx\frac{R_s}{Z_0W}K_iK_r$ Np/m with current-distribution factor $K_i=e^{-1.2(Z_0/\eta_0)^{0.7}}$ and Hammerstad roughness factor $K_r=1+\frac2\pi\arctan[1.4(\Delta/\delta_s)^2]$ ($\Delta$ = rms roughness, $\delta_s$ skin depth; JLC-type ED copper has Δ ≈ 1–2 µm, comparable to δ at GHz, so roughness can add up to ~2× conductor loss). **Dielectric loss**: $\alpha_d=\pi\frac{\varepsilon_r}{\sqrt{\varepsilon_\text{eff}}}\frac{\varepsilon_\text{eff}-1}{\varepsilon_r-1}\frac{\tan\delta}{\lambda_0}$ (the "filling-factor" weighted form). Our implementation equals scikit-rf's `MLine.alpha` (0.0799 dB/cm at 2.45 GHz on 1.6 mm FR-4). Rougher/modern models (Huray snowball, Groiss) and causal wideband dielectric models (Djordjevic–Sarkar, which scikit-rf applies by default via `diel='djordjevicsvensson'`) → [skin effect & roughness](../02-electromagnetics/skin-effect-conductor-loss-roughness.md).

**Loss table (dB/cm, 50 Ω line; smooth / 1 µm-rms rough conductor + dielectric at tanδ = 0.02):**

| Board | 433 MHz | 915 MHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|
| 2-layer 1.6 mm, W 2.80 mm | 0.0025/0.0027 + 0.0131 = **0.016** | 0.0037/0.0043 + 0.0276 = **0.032** | 0.0060/0.0085 + 0.0739 = **0.082** | 0.0092/0.0155 + 0.175 = **0.19** |
| JLC 7628 (0.21 mm), W 0.372 mm | 0.019/0.021 + 0.0125 = **0.033** | 0.028/0.033 + 0.026 = **0.059** | 0.045/0.064 + 0.071 = **0.135** | 0.069/0.117 + 0.167 = **0.28** |

So a 30 mm RF trace on the thin-prepreg board costs ≈ 0.1 dB at 915 MHz, 0.4 dB at 2.45 GHz — negligible for LoRa, noticeable for GNSS-L1 before the LNA only if long.

**Dispersion onset.** Kirschning–Jansen shows εeff rising by 0.12 % (433 MHz), 1.5 % (2.45 GHz), 4.8 % (5.8 GHz), 20 % (24 GHz) on 1.6 mm FR-4, but only 0.08 % at 2.45 GHz on the 0.21 mm prepreg — dispersion scales with $f\cdot h$.

**Higher-order modes and radiation.** Two practical limits (approximate): the lowest TE surface-wave mode of the grounded slab starts at $f_{TE1}\approx\dfrac{c}{4h\sqrt{\varepsilon_r-1}}$ (1.6 mm FR-4: 26 GHz; 0.21 mm: 190 GHz), and the transverse resonance of a wide strip at $f_T\approx\dfrac{c}{\sqrt{\varepsilon_r}(2W+0.8h)}$ (1.6 mm, 2.8 mm strip: 21 GHz). Well below these, radiation from *discontinuities* (open ends, bends, T-junctions, via transitions) is the practical issue on thick low-εr boards; it grows with $(h/\lambda)^2$ — another reason RF designs above a few GHz prefer thin dielectrics. CPWG with poorly stitched top grounds supports a parallel-plate (and slotline) mode between top and bottom grounds; via fences at < λ/10 spacing suppress it (layout details → [vias & fencing](../13-pcb-rf-layout-emc/vias-stitching-fencing.md)).

**Trapezoidal etch.** Etching undercuts the copper, so a trace has a wider foot $W_1$ than top $W_2$; JLC's calculator assumes $W_2=W_1-0.5$ mil (12.7 µm). Field solver with a staircased trapezoid on JLC04161H-7628 (35 µm, bare): $W_1$ = 0.377 mm gives 49.86 Ω vs 49.59 Ω for a rectangle of width $W_1$ (+0.27 Ω), and a rectangle at the mean width $(W_1+W_2)/2$ gives 50.06 Ω. Rule: **model a trapezoid as a rectangle at its mean width**; the effect is a fraction of an ohm on 1 oz copper and grows only for thick copper on very narrow traces. This is one of the reasons JLC's 0.377 mm bare width differs from the 0.372 mm rectangle value above.

**Offset (asymmetric) stripline on JLC 6-layer boards.** On a JLC06161H stack (layer data from JLC's impedance page: L1 – prepreg – L2 – 0.55 mm core – L3 – prepreg – L4 – 0.55 mm core – L5 – prepreg – L6; inner Cu 15.2 µm) a trace on L3 with L2 and L4 as grounds sees the **core** (0.55 mm, εr 4.6) on one side and the **prepreg** (JLC06161H-3313: 2116, 0.1088 mm, εr 4.16; JLC06161H-1080: 7628, 0.2104 mm, εr 4.4) on the other. The near plane dominates. Field solver (trace embedded in the prepreg, planes at the copper faces): **50 Ω = 0.136 mm (−3313; εeff 4.30) and 0.241 mm (−1080; εeff 4.47)**. The same trace treated as a microstrip over the near plane alone would read 62–64 Ω — the far plane still adds ~25 % capacitance. Because the dielectrics differ, the line is not pure TEM ($\varepsilon_\text{eff}$ lies between the two εr), but dispersion is negligible at UHF. Inner layers suit shielded RF routing between two planes on 6-layer flight boards; the 0.136 mm width on -3313 is near JLC's minimum track, so prefer -1080 (0.24 mm) for RF. Order the width JLC's own calculator gives for the chosen stack.

### Level 3 — power handling of RF traces
**Level 1: what limits power.** Two things: **heating** (the line's loss turns into heat in the copper and the dielectric) and **voltage** (breakdown or corona between the trace and nearby copper). In a matched 50 Ω line, $V_\text{pk}=\sqrt{2PZ_0}$ and $I_\text{rms}=\sqrt{P/Z_0}$: 2 W → 14.1 V, 0.20 A; 25 W → 50 V, 0.71 A. At VSWR $S$ the standing-wave maxima are $(1+|\Gamma|)$ times higher (VSWR 3: ×1.5).

**Level 2: heat per metre and the DC-equivalent current.** A line with attenuation α (Np/m) carrying power $P$ dissipates $p'=2\alpha P$ W/m, split into conductor heat $p'_c=2\alpha_cP$ (in the trace and, to a lesser extent, the plane) and dielectric heat $p'_d=2\alpha_dP$ (in the substrate under the trace). Over a length ℓ the total is $P(1-e^{-2\alpha\ell})$. Since $\alpha_c=R'/(2Z_0)$, the trace's **RF resistance** is $R'_{RF}=2Z_0\alpha_c$ — skin effect plus current crowding at the strip edges — which is 15–55× the DC value $R'_{DC}=\rho/(Wt)$ at 0.43–2.45 GHz on JLC stackups. DC trace-heating rules (IPC-2221's $I=kΔT^{0.44}A^{0.725}$, k = 0.048 for outer layers, A in mil²; the IPC-2152 charts) relate temperature rise to a *uniform DC* current. To use them at RF, feed them the **DC-equivalent current** that produces the same heat: $I_{eq}=\sqrt{p'/R'_{DC}}$ — about 5× the RF current at 433 MHz and 10× at 2.45 GHz on JLC-7628.

**Temperature rise model.** For a long trace, heat flows through the dielectric to the nearest plane ($R'_d\approx h/[k_d(W+h)]$ K·m/W, 45° spreading, $k_{FR4}$ ≈ 0.3 W/m·K) and then spreads in the copper planes and convects from both faces of the board, which acts as a fin ($R'_b=1/[2\sqrt{2h_c\sum kt}\,\tanh(mL)]$, $m=\sqrt{2h_c/\sum kt}$, L = half board width). Dielectric heat is generated through the depth, so it sees about $R'_d/2$:
$$\Delta T\approx p'_c\,(R'_d+R'_b)+p'_d\,(R'_d/2+R'_b).$$
With $h_c$ = 12 W/m²K per face (still air plus radiation; an assumption) and a 50 mm wide board, $R'_d$ ≈ 1.2 K·m/W on both JLC stackups and $R'_b$ ≈ 1.0–1.2 K·m/W. A 2-D finite-volume conduction model of the full cross-section (`tools/verify/s6_trace_heating.py`) agrees with this two-resistor estimate within 22 %:

| Trace (KB canonical width, 1 µm rough Cu, tanδ 0.02) | f | $p'_c+p'_d$ per W (W/m) | $R'_{RF}/R'_{DC}$ | ΔT long line, 2 W | ΔT long line, 25 W | IPC-2221 at $I_{eq}$, 25 W |
|---|---|---|---|---|---|---|
| JLC04161H-7628, 0.359 mm | 433 MHz | 0.48 + 0.29 | 18 | **3.3 K** | 41 K | 149 K |
| | 915 MHz | 0.76 + 0.61 | 28 | 5.6 K | 70 K | 287 K |
| | 2.45 GHz | 1.49 + 1.62 | 55 | 12.5 K | **156 K** | 734 K |
| JLC0216A 2-layer, 2.692 mm | 433 MHz | 0.07 + 0.30 | 15 | 1.1 K | 14 K | 25 K |
| | 915 MHz | 0.10 + 0.64 | 24 | 2.2 K | 28 K | 55 K |
| | 2.45 GHz | 0.21 + 1.70 | 48 | 5.6 K | 71 K | 163 K |

Three lessons. (i) **Thin-prepreg traces are conductor-loss heated; thick-board traces are dielectric-loss heated** — the 2.7 mm trace's copper loss is 7× lower, but FR-4's tanδ still heats it. (ii) **IPC-2221 fed with $I_{eq}$ is 2–5× pessimistic here**: its empirical data are for traces without a plane 0.2 mm below; IPC-2152 accounts for planes and board size and is the better DC reference, but it is still a DC chart. (iii) **The "infinitely long" numbers are worst cases.** Real RF traces are 1–5 cm long and end on pads, modules and connectors that sink heat: a 3 cm, 2 W, 433 MHz trace on JLC-7628 dissipates only 45 mW in total. The cases that need care are tens of watts at GHz on thin, narrow FR-4 lines (25 W, 2.45 GHz, 5 cm: 3.6 W in the trace) — widen the trace (thicker dielectric or CPWG), use a low-loss laminate, or keep high-power runs short. Board-level thermal design (PA dissipation, vias, enclosures) is in [thermal management](../13-pcb-rf-layout-emc/thermal-management-rf.md).

**Level 3: voltage limits and altitude.** In air, no gap of any size breaks down below the **Paschen minimum, ≈ 327 V** (at p·d ≈ 0.75 Pa·m), so a 50 Ω trace is voltage-safe until $V_\text{pk}$ approaches that: 1.07 kW matched, ≈ 475 W at VSWR 3. At 25 W (75 V peak at VSWR 3) the margin is > 4×. Paschen's curve is for DC and uniform fields; sharp copper edges, contamination and RF (where electrons are not swept out each cycle) lower the threshold, and at reduced pressure the minimum moves to larger gaps — so keep IPC clearance rules, keep soldermask on high-voltage nodes and treat high-Q matching nodes (whose voltage is Q times the line voltage) as the real hot spots. Altitude also reduces natural convection (lower air density), so a trace that is marginal on the bench runs hotter in a high-altitude avionics bay. (RF breakdown versus pressure for PCB geometries is not quantified in the sources read — see open questions.)

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $Z_0=1/(c\sqrt{CC_a})$, $\varepsilon_\text{eff}=C/C_a$ | any quasi-TEM line | field-solver definition |
| Hammerstad–Jensen (above) | microstrip, $0.01\le u\le100$, $\varepsilon_r\le128$ | ≤ 0.4 % |
| 50 Ω microstrip: $W/h\approx1.85$ (εr 4.5), 1.77 (εr 4.4, t 35 µm on 0.21 mm) | FR-4 | 1.6 mm board: 2.8 mm |
| $\varepsilon_\text{eff}\approx3.3$–3.4 for 50 Ω on FR-4 | microstrip | λ/4 at 915 MHz ≈ 44 mm |
| Cohn: $Z_0=\frac{30\pi}{\sqrt{\varepsilon_r}}K(k)/K(k')$, $k=\mathrm{sech}(\pi W/2b)$ | centred stripline, t = 0 | exact |
| CPWG (Ghione–Naldi) | gap < 2h, thin Cu | narrow gaps → narrow 50 Ω trace |
| Copper 35 µm: −2…−5 Ω (thin prepreg), −0.3 Ω (1.6 mm microstrip) | thickness | use H-J thickness correction |
| Soldermask εr 3.8: −1…−2.5 Ω microstrip, −3…−10 Ω CPWG / diff pairs | coated outer layers | mask thickness varies |
| $Z_\text{diff}=2Z_\text{odd}$, $Z_\text{comm}=Z_\text{even}/2$ | coupled pair | JLC7628 0.172/0.15 mm: 109 Ω bare |
| $f_{TE1}\approx c/(4h\sqrt{\varepsilon_r-1})$ | microstrip surface waves | 1.6 mm FR-4: 26 GHz |
| Kirschning–Jansen coupled microstrip | u 0.3–3, g 0.2–2 checked | ≤ 0.6 % vs field solver |
| Trapezoid ≈ rectangle at mean width | etched outer traces | JLC 0.5 mil etch-back: +0.27 Ω |
| Offset stripline L3 on JLC 6-layer, 50 Ω | L2/L4 grounds, 15 µm Cu | 0.136 mm (-3313), 0.241 mm (-1080) |
| $V_\text{pk}=\sqrt{2PZ_0}(1+\lvert\Gamma\rvert)$, $I_\text{rms}=\sqrt{P/Z_0}(1+\lvert\Gamma\rvert)$ | standing-wave maxima | 25 W, VSWR 3: 75 V, 1.06 A |
| $p'=2\alpha P$; $R'_{RF}=2Z_0\alpha_c$; $I_{eq}=\sqrt{p'/R'_{DC}}$ | trace heating; DC rules need $I_{eq}$ | $R'_{RF}/R'_{DC}$ 15–55 at 0.43–2.45 GHz |
| $\Delta T\approx p'_c(R'_d+R'_b)+p'_d(R'_d/2+R'_b)$ | long trace, still air | JLC-7628, 2 W @ 433 MHz: 3 K |
| Paschen minimum ≈ 327 V (air, any pressure, DC) | voltage limit | ≈ 1 kW matched in 50 Ω |

## Worked examples

### Example 1 — the 50 Ω antenna feed on Marcus's two board types
*2-layer, 1.6 mm FR-4 (JLCPCB default)*: microstrip 2.80 mm wide (h = 1.51 mm, εr 4.5, bare model; JLC's calculator for JLC0216A gives 2.69 mm masked — order that, [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)) — wider than a U.FL (≈ 1 mm signal pad) or an 0402 pad. The 2.8 mm → 0.5 mm neck-down at the connector is itself a discontinuity (a short high-Z section ≈ series inductance; at 433 MHz a 2 mm neck is harmless, at 2.45 GHz it costs a few dB of return loss). **CPWG** with a 0.2 mm gap needs a 1.01 mm trace (35 µm Cu, field solver), ≈ 0.9 mm once soldermask (≈ −3 Ω) is included (JLC calculator: 0.918 mm masked at a 0.203 mm gap) — matching connector and component pads. Stitch the side grounds to the bottom plane with a via row every few mm (< λ/10 ≈ 18 mm at 915 MHz in FR-4; much tighter is customary).

*4-layer JLC04161H-7628*: plain microstrip on L1 over the L2 ground: 0.372 mm bare, ≈0.343 mm with a gap-filling soldermask model (JLC's calculator, trapezoid + conformal mask: **0.359 mm masked / 0.377 mm bare** — the width to order) — an 0402-pad-width trace; CPWG is optional (use it for isolation, e.g. with a 0.3 mm gap: W 0.36 mm gives 49.1 Ω bare / 46.6 Ω masked). Published designs for this stackup: JITX's 0.3244 mm (our model: 51.4–53.9 Ω depending on mask model) and a CPWG 0.34/0.20 mm from Saturn PCB Toolkit (our solver: 48.7 Ω bare, 45.7 Ω with mask); the LibreCAL hardware uses 0.30/0.18 mm "with good experimental results" (51.1 Ω bare / 47.6 Ω masked). **Different calculators disagree by several ohms mainly through soldermask and copper-thickness assumptions** — the fab's own calculator (which knows its process) and a TDR coupon are the arbiters.

### Example 2 — synthesis by hand
50 Ω on εr 4.5, h = 1.51 mm with Pozar's closed form: $A=\frac{50}{60}\sqrt{2.75}+\frac{3.5}{5.5}(0.23+0.0244)=1.382+0.162=1.544$; $u=8e^{1.544}/(e^{3.088}-2)=37.5/19.93=1.88<2$ ✓ → W = 2.84 mm (H-J root-find with t = 35 µm: 2.80 mm; the difference is the copper thickness).

### Example 3 — 100 Ω differential pair for a balanced 2.4 GHz antenna or USB on JLC04161H-7628
Field solver, 35 µm copper: W = 0.1722 mm, s = 0.15 mm → $Z_\text{odd}=54.5$, $Z_\text{even}=87.8$ Ω → **$Z_\text{diff}=109$ Ω** bare, **98.4 Ω** with gap-filling soldermask; W = 0.2332/s = 0.15 mm → 97.3 bare / 88.9 Ω masked (JITX lists these as its 100 Ω and 90 Ω structures — consistent only with the masked values). IPC-2141 estimate: 109.7 Ω and 96.1 Ω (bare), within 1.2 %.

### Example 4 — quarter-wave lengths for stubs and transformers
915 MHz on 1.6 mm FR-4 50 Ω microstrip: $\lambda_g/4=c/(4f\sqrt{3.36})=44.7$ mm. On JLC-7628 (εeff ≈ 3.19 bare, 3.35 masked) ≈ 45.8/44.7 mm. The ~2.5 % difference from soldermask moves a λ/4 resonator by ~2.5 % in frequency (23 MHz at 915 MHz) — trim-on-board territory.

### Example 5 — will the E22's 2 W, 433 MHz trace get hot (and what about 25 W)?
JLC04161H-7628, 0.359 mm, 1 oz: $\alpha_c$ = 2.08 dB/m, $\alpha_d$ = 1.25 dB/m (1 µm rough copper, tanδ 0.02) → α = 0.383 Np/m. At 2 W, $p'=2\alpha P$ = 1.53 W/m (0.96 W/m in the copper, 0.57 W/m in the FR-4). The trace's RF resistance is $2Z_0\alpha_c$ = 24.5 Ω/m vs 1.37 Ω/m at DC (18×), so the DC-equivalent current is $\sqrt{1.53/1.37}$ = 1.06 A, not the 0.20 A that flows. Two-resistor model: $0.96(1.23+0.98)+0.57(0.62+0.98)$ = 3.0 K; field solver 3.3 K for an infinitely long line. A real 3 cm feed loses 0.10 dB and dissipates 45 mW: **no thermal issue**; the module and its LDO are the heat sources ([thermal management](../13-pcb-rf-layout-emc/thermal-management-rf.md)). Scale to a 25 W, 2.45 GHz amplifier on the same trace: α_c + α_d = 13.5 dB/m, 78 W/m, 156 K for a long line and 3.6 W in a 5 cm run — redesign with a wider line on a thicker dielectric (the 2.7 mm 2-layer trace: 71 K long-line) or a low-loss laminate. Voltage is never the limit at these powers: 75 V peak at VSWR 3 vs the ≈ 327 V Paschen minimum.

### Example 6 — a shielded 50 Ω RF route on a JLC 6-layer flight board
Route the 433/915 MHz line on L3 between the L2 and L4 ground planes of JLC06161H-1080 (L3–L4 7628 prepreg 0.2104 mm, L2–L3 core 0.55 mm): field-solver 50 Ω width **0.241 mm** (εeff 4.47, so λ/4 at 915 MHz = 38.7 mm vs 45 mm on the surface). Stitch both planes with vias along the route, and model each layer-change via as a discontinuity ([discontinuities](microstrip-discontinuities.md), [vias & fencing](../13-pcb-rf-layout-emc/vias-stitching-fencing.md)). On JLC06161H-3313 the same line would be 0.136 mm — close to the minimum track, so ±15 µm of etch is ±11 % of width (≈ ±3 Ω).

## Practical notes
- **Specify impedance control** with the fab (JLCPCB offers standard 4/6-layer impedance stackups; its calculator assumes a soldermask of εr 3.8 and outer copper 1.6 mil finished; 2-layer boards are standard FR-4 with Dk ≈ 4.5 and no guaranteed impedance). Put a test coupon on the panel if you care, and verify with [TDR](time-domain-reflectometry.md).
- **FR-4 εr is not one number**: 4.1–4.6 across prepreg/core styles and resin content (JLC lists 3.91–4.6), falling slowly with frequency; a ±0.2 change in εr shifts a 50 Ω microstrip by ≈ ±1 Ω or its width by ≈ ±3.5 %.
- **Etch tolerance**: finished widths typically vary by ±10–20 µm; for a 0.135 mm trace (JLC-1080) that is ±10 %; for CPWG gaps of 0.15 mm the gap tolerance dominates.
- **Discontinuities** (open ends, gaps, steps, bends/mitres, T-junctions, vias), with models and an openEMS check: [microstrip discontinuities](microstrip-discontinuities.md).
- **Keep the reference plane solid** under RF traces (no splits); for CPWG, no ground-pour islands without vias. Layout rules belong to [13-pcb-rf-layout-emc](../13-pcb-rf-layout-emc/rf-layout-rules.md).
- **Tools**: KiCad's built-in calculator (Wheeler/H-J microstrip, CPWG), Saturn PCB Toolkit, JLCPCB's online calculator, and field solvers (this KB's `tline_fd2d.py`, openEMS for 3-D). Expect ±1–3 Ω differences between them from model assumptions.

## Common mistakes & misconceptions
- **Using the full board thickness as h on a multilayer board** — h is the distance to the *nearest reference plane* (0.21 mm on JLC-7628, not 1.6 mm).
- **Using microstrip formulas for a trace with ground pour close beside it** — if the pour is within ~2–3 h it is a CPWG; the impedance can drop by 10+ Ω.
- **Forgetting soldermask and copper thickness** — 2–10 Ω errors on thin stackups.
- **Using CPWG formulas outside their range** — for gaps ≳ 2h the (zero-thickness) formula is wrong; the line is effectively microstrip.
- **Assuming the calculator is exact** — they differ by model; closed forms are accurate to ~0.5 % *for their idealised geometry*, and the real geometry (trapezoidal etch, mask, roughness, εr) is the bigger error.
- **"Dispersion ruins my 2.4 GHz design"** — on thin boards it is < 0.1 %; on 1.6 mm boards ~1.5 %.
- **"RF ground planes must be 50 Ω too."** A ground plane has no characteristic impedance of its own. $Z_0$ is a property of the *two-conductor cross-section* — signal strip plus its return conductor (the plane) and the dielectric between them; the plane's job is to carry the return current (concentrated in a band a few h wide directly under the trace) with as little impedance as possible. A 35 µm copper plane is 0.49 mΩ/□ at DC and 5.4 / 7.9 / 12.9 mΩ/□ surface resistance at 433 / 915 / 2450 MHz — four orders of magnitude below 50 Ω, and that is what you want. What *does* matter: the plane is continuous under the whole route (a slot or split forces the return current around it and adds inductance and radiation), the distance h is what the width was designed for, and the plane is tied to the connector and component grounds with short vias ([grounding and return paths](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- **Using IPC-2152 (or IPC-2221) with the RF current.** These are DC charts. RF current flows in the skin and crowds to the strip edges, so the same current heats 15–55× more; enter the DC-equivalent current $\sqrt{p'/R'_{DC}}$ (Example 5), and add the dielectric heat, which DC rules ignore.
- **Assuming "low power" means "no trace heating" at any frequency** — at 2.45 GHz and 25 W, a 0.36 mm FR-4 line dissipates ≈ 0.8 W per cm.
- **Using a Hammerstad–Jensen coupled-line implementation without checking it** — the qucsator version reproduced here is 19 % off in impedance; Kirschning–Jansen is within 0.6 %.
- **Differential pair = two 50 Ω lines** — only if uncoupled (then 100 Ω); tight coupling lowers Zdiff, and asymmetry converts differential to common mode ([mixed-mode S-parameters](s-parameters.md)).

## How to simulate / verify
- `tools/verify/tline_fd2d.py` — the 2-D quasi-static field solver (self-test vs Cohn's exact stripline).
- `tools/verify/tline_microstrip.py` — H-J (±t), Wheeler-77, simple forms, K-J dispersion, Pozar synthesis, stripline (Cohn, Wheeler-78), edge-coupled pairs, JLC stackup widths with/without mask, losses, higher-order-mode estimates; all compared with the FD solver and/or scikit-rf (runtime ≈ 3–5 min).
- `tools/verify/tline_cpwg.py` — CPW/CPWG conformal mapping vs FD and scikit-rf; thickness/mask effects; 2-layer and JLC-7628 CPWG designs.
- `tools/verify/s6_coupled_offset.py` — Kirschning–Jansen and Hammerstad–Jensen coupled microstrip vs FD (12 geometries + JLC pair), trapezoidal etch, offset stripline on JLC 6-layer (≈ 3 min). All pass.
- `tools/verify/s6_trace_heating.py` — power-handling numbers of Example 5 and the Level-3 table: loss split, RF/DC resistance, 2-D finite-volume thermal model vs the two-resistor estimate, IPC-2221 at the DC-equivalent current, Paschen margin, plane surface resistance. All pass.
- scikit-rf models for circuit simulation: `rf.media.MLine(frequency, w, h, t, ep_r, tand, rough, disp='kirschningjansen', diel='frequencyinvariant')`, `rf.media.CPW(..., has_metal_backside=True)`. Note that scikit-rf's default `diel='djordjevicsvensson'` treats `ep_r` as the value at `f_epr_tand` (1 GHz) and makes it frequency-dependent.

```python
import sys; sys.path.insert(0, 'tools/verify')
from tline_microstrip import ms_hj, width_for
from tline_cpwg import cpwg
w50 = width_for(50, lambda w: ms_hj(w, 0.2104e-3, 4.4, 35e-6)[0])   # JLC04161H-7628
print(w50*1e3, 'mm;', cpwg(1.0e-3, 0.2e-3, 1.51e-3, 4.5))           # CPWG on 2-layer (t = 0)
```

## Open questions / gaps
- Measured TDR data on JLCPCB coupons to settle the ±3 Ω calculator spread (soldermask thickness over copper vs in gaps is not published per stackup in the sources read).
- Done 2026-10-13 (W5-S6): Kirschning–Jansen coupled microstrip (static, t = 0) implemented and checked; trapezoidal etch quantified; offset stripline widths for JLC06161H-3313/-1080 L3 tabulated. Still open: K-J dispersion and thickness corrections for coupled lines are not checked; the 6-layer layer data came from a page summary of jlcpcb.com/impedance and should be re-read from the page; the Hammerstad–Jensen coupled discrepancy (19 %) is unresolved (Qucs coding vs the 1980 paper not compared).
- Trace heating: the thermal model is 2-D (infinitely long trace) with an assumed 12 W/m²K per face; short traces with pad/via heat sinking, soldermask, and reduced-pressure convection in a rocket bay are not modelled, and no measured trace-temperature data were found. RF breakdown versus pressure for PCB gap geometries is not quantified.
- The JITX RS_50 width (0.3244 mm) remains ~5–10 % narrower than our masked solution. W4-D6/W5-E9 (2026-10-03): the spread between 0.343 (our rectangular strip + gap-filling mask), 0.359 (JLC calculator, trapezoid + conformal mask, confirmed by 13's field solver within 1 %) and 0.3244 mm (JITX) comes from mask/etch model inputs, not formula accuracy; the KB canonical value is the fab calculator's ([canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)). Likewise the 2-layer 2.80/2.97 mm figures assume h = 1.51/1.6 mm, while JLC's JLC0216A template uses a 1.43 mm core (2.69 mm masked); the source of the 1.43 mm figure is cited in 13.

## Sources
1. E. Hammerstad and Ø. Jensen, "Accurate models for microstrip computer-aided design," *IEEE MTT-S Int. Microwave Symp. Digest*, 1980, pp. 407–409. (peer-reviewed conference; formulas via [6], [7])
2. H. A. Wheeler, "Transmission-line properties of a strip on a dielectric sheet on a plane," *IEEE Trans. MTT*, vol. 25, no. 8, pp. 631–647, Aug. 1977; and "Transmission-line properties of a strip line between parallel planes," *IEEE Trans. MTT*, vol. 26, no. 11, pp. 866–876, Nov. 1978. (peer-reviewed)
3. M. Kirschning and R. H. Jansen, "Accurate model for effective dielectric constant of microstrip with validity up to millimetre-wave frequencies," *Electronics Letters*, vol. 18, no. 6, pp. 272–273, 1982; R. H. Jansen and M. Kirschning, "Arguments and an accurate model for the power-current formulation of microstrip characteristic impedance," *AEÜ*, vol. 37, pp. 108–112, 1983. (peer-reviewed)
4. S. B. Cohn, "Characteristic impedance of the shielded-strip transmission line," *IRE Trans. MTT*, vol. 2, pp. 52–57, 1954. (peer-reviewed)
5. G. Ghione and C. Naldi, "Analytical formulas for coplanar lines in hybrid and monolithic MICs," *Electronics Letters*, vol. 20, no. 4, pp. 179–181, 1984; R. N. Simons, *Coplanar Waveguide Circuits, Components, and Systems*, Wiley 2001; C. P. Wen, "Coplanar waveguide…," *IEEE Trans. MTT*, vol. 17, pp. 1087–1090, 1969. (peer-reviewed / textbook)
6. S. Jahn, M. Margraf et al., *Qucs Technical Papers* — microstrip (quasi-static, dispersion, losses), coplanar sections — https://qucs.sourceforge.net/tech/node75.html. (documentation of open-source simulator)
7. scikit-rf 2.0.1 source: `skrf.media.mline`, `skrf.media.cpw` — https://scikit-rf.readthedocs.io/. (software)
8. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — §3.7 (stripline), §3.8 (microstrip, synthesis eq. 3.197). (textbook)
9. B. C. Wadell, *Transmission Line Design Handbook*, Artech House 1991; K. C. Gupta, R. Garg, I. Bahl, P. Bhartia, *Microstrip Lines and Slotlines*, 2nd ed., Artech 1996 — surveys of the formulas, surface-wave and higher-order mode limits. (textbooks)
10. IPC-2141A, *Design Guide for High-Speed Controlled Impedance Circuit Boards*, IPC 2004 — edge-coupled approximation (as widely quoted). (standard, via secondary sources)
11. JLCPCB, "Controlled impedance PCB layer stackup" — https://jlcpcb.com/impedance (stackup thicknesses/Dk); "User guide to the JLCPCB impedance calculator" (outer Cu 1.6 mil, mask 1.2 mil, εr 3.8); JLCPCB standard 2-layer stackup page (FR-4 Dk ≈ 4.5, Df ≈ 0.02). Accessed 2026-09-27. (manufacturer)
12. JITX documentation, `jitxlib.jlcpcb.JLC04161H_7628` routing structures — https://docs.jitx.com/en/latest/jitxlib/jitxlib.jlcpcb.JLC04161H_7628.html. (software documentation)
13. LibreCAL GitHub pull request #8 (jankae/LibreCAL) — CPWG 0.34/0.20 mm on JLC04161H-7628 per Saturn PCB Toolkit vs as-built 0.30/0.18 mm. (forum/engineering discussion — anecdotal)
14. Verification: `tools/verify/tline_fd2d.py`, `tline_microstrip.py`, `tline_cpwg.py`; cross-check with `tools/verify/em_inductance.py` (W1-A3). (numerical check)
15. M. Kirschning and R. H. Jansen, "Accurate wide-range design equations for the frequency-dependent characteristic of parallel coupled microstrip lines," *IEEE Trans. MTT*, vol. 32, no. 1, pp. 83–90, Jan. 1984 (correction: vol. 33, p. 288, 1985) — coupled-line even/odd static and dispersion model; equations as coded in qucsator `src/components/microstrip/mscoupled.cpp` (GPL, S. Jahn), re-implemented and verified against the FD solver. (peer-reviewed; via open-source implementation)
16. IPC-2221B, *Generic Standard on Printed Board Design*, 2012 — conductor current formula $I=k\Delta T^{0.44}A^{0.725}$ (k 0.048 external, 0.024 internal); IPC-2152, *Standard for Determining Current Carrying Capacity in Printed Board Design*, 2009 — DC charts including plane and board effects. (standard; formula as widely reproduced)
17. Paschen's law and the air minimum ≈ 327 V near p·d ≈ 0.75 Pa·m — e.g. M. A. Lieberman and A. J. Lichtenberg, *Principles of Plasma Discharges and Materials Processing*, 2nd ed., Wiley 2005, ch. 14; Wikipedia "Paschen's law" (consulted 2026-10-13). (textbook / secondary)
18. JLCPCB, "Controlled impedance PCB layer stackup" — 6-layer JLC06161H-3313 / -1080 layer thicknesses and Dk, https://jlcpcb.com/impedance, read 2026-10-13 via a page summary (re-check before ordering). (manufacturer)
19. Verification: `tools/verify/s6_coupled_offset.py` (coupled closed forms vs FD, trapezoid, offset stripline) and `tools/verify/s6_trace_heating.py` (loss split, RF/DC resistance, 2-D thermal FV model, IPC-2221, Paschen margin, plane surface resistance); outputs in `*_output.txt`. (numerical check)
