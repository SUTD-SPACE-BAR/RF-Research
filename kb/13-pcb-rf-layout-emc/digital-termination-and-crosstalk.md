---
title: Digital termination and crosstalk — reflections on fast edges, when to terminate, series/parallel/Thevenin/AC termination, NEXT and FEXT from mutual L and C, the 3W rule, and clocks near RF
domain: 13-pcb-rf-layout-emc
slug: digital-termination-and-crosstalk
tags: [signal-integrity, reflections, ringing, overshoot, rise-time, critical-length, knee-frequency, series-termination, source-termination, parallel-termination, thevenin-termination, ac-termination, rc-termination, crosstalk, next, fext, backward-crosstalk, forward-crosstalk, saturation-length, mutual-inductance, mutual-capacitance, even-odd-mode, 3w-rule, guard-trace, spi, sd-card, clock, esp32, teensy, jlcpcb]
prerequisites:
  - ../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - grounding-and-return-paths.md
related:
  - mixed-signal-layout.md
  - emc-emi-fundamentals.md
  - stackups-and-materials.md
  - rf-layout-rules.md
  - vias-stitching-fencing.md
  - rf-pcb-review-checklist.md
  - ../03-transmission-lines-matching/time-domain-reflectometry.md
  - ../03-transmission-lines-matching/s-parameters.md
  - ../02-electromagnetics/quasi-static-vs-full-wave.md
  - ../17-test-measurement/oscilloscopes-and-probing-for-rf.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Digital termination and crosstalk

## Questions this page answers
- When does a digital trace (SPI clock, SD card, UART, GPIO) need termination on my flight-computer board?
- Why does my 40 MHz SPI clock ring, and what does the 22–33 Ω series resistor actually do?
- What are series, parallel, Thevenin and AC (RC) terminations, and which costs how much power?
- What is the difference between near-end (NEXT) and far-end (FEXT) crosstalk, and where do they come from?
- Why does microstrip have far-end crosstalk but stripline almost none?
- Does the "3W rule" work? How much crosstalk does it really leave on a JLCPCB 4-layer vs a 2-layer board?
- How far should a clock or SPI trace stay from the LoRa or GNSS RF trace?
- Why does crosstalk stop growing beyond a certain parallel length?
- What value of series resistor should I put on an MCU clock pin?
- Do I need termination on I²C or UART?

## TL;DR
- **A digital trace is a transmission line once its delay TD is a sizeable fraction of the edge time $t_r$.**
  - The bandwidth that matters is the knee frequency $f_\text{knee}\approx0.35/t_r$ to $0.5/t_r$, not the clock rate.
  - In the script (25 Ω driver, 50 Ω line, 5 pF receiver), the unterminated far-end overshoot is **5 % at TD = tr/10, 10 % at TD ≈ tr/6, 17 % at tr/4, and 35 % for long lines**.
  - With 1 ns edges on FR-4 microstrip (≈ 6 ps/mm), **lines longer than about 25–30 mm need thought**.
- **Series (source) termination** with $R_s+R_t=Z_0$ (typically 22–33 Ω for MCU pins) removes overshoot completely at **zero DC power**. It needs a single load at the far end: the mid-line voltage sits at V/2 for 2TD.
- **Parallel to ground:** 50 Ω at 3.3 V draws 66 mA and **218 mW** in the high state, and cuts the swing to 2.2 V with a 25 Ω driver. **Thevenin** (100/100 Ω) costs 54 mW. **AC** (50 Ω + C) costs no DC power, but with a weak driver it adds an RC tail: 13.5 ns to settle with 100 pF, against 6.6 ns unterminated. Series termination is almost always the right answer on a flight computer.
- **Crosstalk** comes from mutual inductance $L_m$ and capacitance $C_m$ between traces:
  - $K_b=\tfrac14\left(\frac{L_m}{L}+\frac{C_m}{C}\right)$ is the NEXT that **saturates** once the coupled length exceeds the saturation length $\tfrac12t_rv$;
  - $V_\text{FEXT}=\tfrac12\left(\frac{C_m}{C}-\frac{L_m}{L}\right)\frac{\ell}{v\,t_r}V$ is **negative** in microstrip, grows with length and edge rate, and is **zero in homogeneous stripline**;
  - both are verified against an exact even/odd-mode simulation within 1–5 % (`e11_crosstalk.py`).
- **The 3W rule** (centre spacing ≥ 3 × width):
  - on **JLC04161H-7628** (h 0.21 mm, W 0.2 mm) it gives NEXT **−27.5 dB**;
  - on a **2-layer 1.5 mm** board (W 0.3 mm) it gives only **−15.5 dB**;
  - what really matters is spacing relative to **height above the plane**, D/h. 3W "works" only when W ≈ h.
- **Clock next to the LoRa trace** (7628, 10 mm parallel run, 920 MHz): backward coupling is −26 / −34 / −43 / −54 dB for 0.2 / 0.5 / 1 / 2 mm gaps. Against the ≈ 100 dB isolation the [mixed-signal page](mixed-signal-layout.md) shows is needed for a clock harmonic, **spacing alone is never enough**. Also use ground between the traces, different layers, slower edges and frequency planning.

## Intuition (no math)
A fast edge travels down a trace like a wave down a rope. If the far end is an open circuit (a CMOS input is a few pF, nearly open), the wave reflects and doubles the voltage there, then travels back to the driver. The driver's low output impedance (~25 Ω) reflects it again, and the edge rings up and down until it settles. If the trace is short compared with the edge (the wave makes many round trips during the rise), the reflections blur into the edge and nobody notices. If the trace is long, each bounce is visible as overshoot and ringing. That causes false clocking, extra EMI and stress on the input protection diodes.

**Termination** absorbs the wave at one end.
- A resistor at the driver making the total source resistance equal to $Z_0$ (**series termination**) launches a half-height wave. The open far end doubles it to full height, and the reflection is absorbed when it returns to the matched source. That is clean, and no DC current flows.
- A resistor at the far end equal to $Z_0$ (**parallel termination**) absorbs the wave on arrival, but it draws current whenever the line is high.

**Crosstalk** happens because a signal trace's electric field reaches the neighbouring trace (mutual capacitance) and its magnetic field links the neighbour's current loop (mutual inductance).
- As the aggressor's edge travels along, it continuously injects a little energy into the victim, some heading backward and some forward.
- The backward part arrives at the victim's near end spread over twice the coupled delay, so it looks like a long low pulse, and its height stops growing once the coupled length is longer than about half an edge. This is near-end crosstalk.
- The forward part travels along *with* the aggressor's edge and accumulates over the whole length, but the inductive and capacitive contributions have opposite signs. In a uniform dielectric (stripline) they cancel exactly. In microstrip, part of the field is in air, so the capacitive coupling is weaker, the inductive coupling wins, and a negative spike appears at the far end. This is far-end crosstalk.

## The math

### Level 1 — the numbers you need

| Quantity | Formula | Typical value |
|---|---|---|
| Edge bandwidth | $f_\text{knee}\approx0.35/t_{10-90}$ (to $0.5/t_r$) | 1 ns → 350–500 MHz |
| Propagation delay | $t_{pd}=\sqrt{\varepsilon_\text{eff}}/c$ | microstrip FR-4: 6.0–6.1 ps/mm; stripline: 7.0 ps/mm |
| Reflection coefficient | $\Gamma=\frac{Z_L-Z_0}{Z_L+Z_0}$ | open +1, CMOS driver (25 Ω into 50 Ω) −1/3 |
| Terminate when | $TD\gtrsim t_r/6$ (≈ 10 % overshoot) | 1 ns edge: > 28 mm |
| Series termination | $R_t=Z_0-R_\text{out}$ | 50 − 25 = 25 → use 22–27 Ω |
| Parallel / Thevenin | $R=Z_0$; $R_1\parallel R_2=Z_0$ | DC power $V^2/R$ or $V^2/(R_1+R_2)$ |
| AC termination | $R=Z_0$, $RC\gtrsim3\cdot2TD$ | 50 Ω + 100 pF for TD ≈ 1 ns |
| NEXT (saturated) | $K_b=\frac14\left(\frac{L_m}{L}+\frac{C_m}{C}\right)$ | 7628, 0.2 mm traces at 0.4 mm pitch: 0.092 |
| Saturation length | $\ell_\text{sat}=\tfrac12t_rv$ | 1 ns, microstrip: 83 mm |
| FEXT | $\frac{V_f}{V}=k_f\frac{\ell}{vt_r}$, $k_f=\frac12\left(\frac{C_m}{C}-\frac{L_m}{L}\right)$ | 7628 pair, 10 cm, 0.5 ns: −6 % |

### Level 1½ — the same ideas with only algebra
- **Is my trace "long"?** Multiply its length in mm by 6 ps/mm to get its delay TD. If TD is more than about one sixth of the edge time, expect more than 10 % overshoot. A 1 ns edge allows about 28 mm.
- **What does a series resistor do?** It makes driver resistance plus resistor equal to the trace impedance. The edge goes out at half height, doubles at the open far end, and the echo dies when it gets back to the now-matched driver.
- **How much crosstalk?** If a neighbour trace's NEXT coefficient is 0.04, a 3.3 V edge puts 0.04 × 3.3 = 0.13 V on the quiet trace's near end. Doubling the spacing on a thin prepreg cuts this roughly by 4–5×.

**Choosing a termination (decision table):**

| Situation | Choose | Why |
|---|---|---|
| Point-to-point CMOS (SPI clock, SD, camera clock) | series R at the driver | zero DC power, clean far end |
| Multi-drop bus | slow the edges (drive strength) or keep stubs short | series termination leaves mid-line steps |
| Long clock line to a single load, driver too strong | series R | also slows edges, so less EMI |
| Low-swing / ECL-style or matched-impedance receivers | parallel to $V_{TT}$ | defined by the logic family |
| Bidirectional line, cannot pick an end | AC (RC) at both ends, or slow edges | no DC load |
| Short line (TD < tr/10) | nothing | lumped capacitance only |

### Level 2 — derivations

**1. Lattice (bounce) diagram.** A source $V_s$ with resistance $R_s$ launches $V_1=V_s\frac{Z_0}{R_s+Z_0}$ into a line of delay TD. The wave reflects with $\Gamma_L$ at the load and $\Gamma_S=\frac{R_s-Z_0}{R_s+Z_0}$ at the source, so the load voltage after the k-th arrival is
$$V_L=V_1(1+\Gamma_L)\left[1+\Gamma_S\Gamma_L+(\Gamma_S\Gamma_L)^2+\cdots\right]\to V_s\frac{R_L}{R_s+R_L}.$$
For an open load and a 25 Ω driver on 50 Ω: $V_1$ = 2.2 V, $\Gamma_S=-1/3$, and the first far-end step is 4.4 V (**+33 % overshoot** on 3.3 V). The script's long-line value is 35 %, the extra coming from the 5 pF load's own ringing. With a finite rise time, the reflections overlap the edge. When $2TD\ll t_r$ the round trips are spread across the ramp and the overshoot shrinks roughly in proportion to TD/tr. The script's numbers come from a Bergeron (method-of-characteristics) simulation, with the far-end node $(2a_\text{arr}-v)/Z_0=C_L\,dv/dt+i_\text{term}(v)$ solved each step by backward Euler.

**2. Why a short line looks like a capacitor.** Below the critical length, the line is a lumped capacitance $C=\ell/(Z_0v)$ (≈ 120 pF/m for 50 Ω FR-4 microstrip, so 3.6 pF for 30 mm). The driver then simply charges $C_\text{line}+C_L$ through $R_s$. That is why "add a series resistor" works in two ways: it terminates long lines, and it slows edges on short ones, which reduces EMI.

**3. The termination options.**
- **Series:** $R_s+R_t=Z_0$ makes $\Gamma_S=0$. The launched wave is V/2, the open end doubles it to V, and the reflected V/2 is absorbed at the source. Anywhere *along* the line the voltage sits at V/2 for $2(TD-x/v)$, so a second receiver mid-line sees a stair-step and may double-clock. The script shows the 1.65 V plateau at the near end for 2TD.
- **Parallel to ground or $V_{TT}$:** $R=Z_0$ at the far end makes $\Gamma_L=0$. The steady-state high level is $V\frac{R}{R+R_s}$ (2.2 V with a 25 Ω driver, which is marginal for 3.3 V CMOS thresholds), with DC power $V^2/R$.
- **Thevenin:** $R_1$ to $V_{cc}$ and $R_2$ to ground with $R_1\parallel R_2=Z_0$ presents $Z_0$ to the wave and biases the line at $V_{cc}R_2/(R_1+R_2)$. Power is $V_{cc}^2/(R_1+R_2)$ continuously.
- **AC (RC):** R = Z₀ in series with C. During the edge, C is a short and the edge sees $Z_0$. At DC, C is open and no current flows. C must be large enough that its time constant $Z_0C$ exceeds the round trip ($\gtrsim3\cdot2TD$). It must also be small enough not to load the driver: the driver has to charge C through $R_s+Z_0$, which produces the slow tail the script shows (100 pF: no overshoot, but 13.5 ns to settle within 5 %).
- **Diode clamps** limit overshoot but do not terminate.

**4. Crosstalk from the coupled telegrapher equations.** Two lines over a plane have per-unit-length matrices $\mathbf L=\begin{pmatrix}L&L_m\\L_m&L\end{pmatrix}$ and $\mathbf C=\begin{pmatrix}C&-C_m\\-C_m&C\end{pmatrix}$, with C the total (Maxwell diagonal) capacitance of one line and $C_m>0$:
$$-\partial_x\mathbf V=\mathbf L\,\partial_t\mathbf I,\qquad-\partial_x\mathbf I=\mathbf C\,\partial_t\mathbf V .$$
Assume **weak coupling** (no back-action on the aggressor), with the aggressor carrying a forward wave $V_1=f(t-x/v)$, $I_1=V_1/Z_0$. The victim then sees distributed sources $-L_m\partial_tI_1$ (series voltage) and $+C_m\partial_tV_1$ (shunt current). Split the victim into forward and backward waves $F=\tfrac12(V_2+Z_0I_2)$ and $B=\tfrac12(V_2-Z_0I_2)$:
$$\partial_xF+\tfrac1v\partial_tF=-\tfrac12\left(L_m\,\partial_tI_1-Z_0C_m\,\partial_tV_1\right)=-\frac{1}{2v}\left(\frac{L_m}{L}-\frac{C_m}{C}\right)\partial_tV_1,$$
using $I_1=V_1/Z_0$, $L_m/Z_0=(L_m/L)/v$ and $Z_0C_m=(C_m/C)/v$. Similarly,
$$-\partial_xB+\tfrac1v\partial_tB=-\frac{1}{2v}\left(\frac{L_m}{L}+\frac{C_m}{C}\right)\partial_tV_1 .$$
(Here $Z_0=\sqrt{L/C}$, $v=1/\sqrt{LC}$, and $L_m/Z_0=(L_m/L)/v$, $Z_0C_m=(C_m/C)/v$.)

- **Forward wave:** the source travels with F at the same speed, so the contributions add coherently. Integrating along ℓ gives
$$F(\ell,t)=-\frac{\ell}{2v}\left(\frac{L_m}{L}-\frac{C_m}{C}\right)\frac{dV_1}{dt}(t-\ell/v),$$
a pulse of width $t_r$ and height $k_f\frac{\ell}{vt_r}V$.
- **Backward wave:** each element dx contributes at the near end with delay 2x/v. Integrating gives
$$B(0,t)=\frac14\left(\frac{L_m}{L}+\frac{C_m}{C}\right)\left[V_1(t)-V_1(t-2TD)\right],$$
which saturates at $K_bV$ when $2TD>t_r$. Otherwise its peak is $K_bV\cdot2TD/t_r$.

These equal the textbook results (Hall & Heck; Bogatin; Johnson & Graham) [1][2][3]. In the script, $L_m/L$ and $C_m/C$ come from the 2-D field solver's even/odd solutions:
- $L_{e,o}=Z_{e,o}/v_{e,o}$ and $C_{e,o}=1/(Z_{e,o}v_{e,o})$;
- $L=\frac{L_e+L_o}2$, $L_m=\frac{L_e-L_o}2$, $C=\frac{C_e+C_o}2$, $C_m=\frac{C_o-C_e}2$.

They are checked against an exact frequency-domain even/odd simulation of the matched pair (inverse FFT of a ramp):

| Coupled length, edge | 2TD/tr | NEXT sim / formula | FEXT sim / formula |
|---|---|---|---|
| 100 mm, 0.5 ns | 2.30 | 0.0927 / 0.0916 | −0.0616 / −0.0601 |
| 100 mm, 2 ns | 0.57 | 0.0535 / 0.0527 | −0.0158 / −0.0150 |
| 20 mm, 1 ns | 0.23 | 0.0215 / 0.0211 | −0.0063 / −0.0060 |

**5. Why stripline has no FEXT.** In a homogeneous dielectric the even and odd modes travel at the same speed, $\mathbf L\mathbf C=\mu\varepsilon\mathbf I$, so $L_m/L=C_m/C$ and $k_f=0$. The script confirms that the even and odd εeff are equal to 10⁻³ for an embedded pair. In microstrip the odd mode has more field in air ($\varepsilon_o$ = 2.65 vs $\varepsilon_e$ = 3.29 for the 7628 pair), so $C_m/C<L_m/L$ and FEXT is negative. Soldermask or a dielectric overlay partly equalises the two and reduces FEXT.

### Level 3 — what the simple formulas leave out
- **Strong coupling.** For tight spacing ($K_b\gtrsim0.1$) the aggressor is itself modified, and the even/odd modal solution (as in the script) replaces the weak-coupling formulas. Above about K ≈ 0.3 a "victim" is better analysed as a coupled pair, as in [mixed-mode S-parameters](../03-transmission-lines-matching/s-parameters.md).
- **Terminations of the victim.** The formulas assume a victim matched at both ends. A victim with a CMOS input at the far end (an open) reflects FEXT back toward the near end, and a low-impedance driver at the near end reflects NEXT forward. Real crosstalk can be up to 2× the matched values.
- **Losses and dispersion** round the edges of long lines and reduce FEXT, which depends on dV/dt. A series-terminated aggressor with slowed edges couples less.
- **Return-path discontinuities.** Splits, slots and layer changes without return vias create common return impedance. That gives far more crosstalk (ground bounce) than the uniform-line $L_m$ and $C_m$ ([grounding and return paths](grounding-and-return-paths.md)). The field-solver numbers here assume a solid plane.
- **Guard traces.** A grounded trace between aggressor and victim reduces coupling only if it is stitched to the plane with vias every ≲ λ/10 of the highest frequency of interest (≈ every 5–10 mm for 1 ns edges). Otherwise it resonates and can *increase* coupling at its resonance. On thin prepreg, moving the traces apart by one more trace width is often as good.
- **Frequency-domain view for RF victims.** For a matched pair with weak coupling, the backward coupling coefficient is $|S_{31}|=2K_b|\sin\beta\ell|$, maximal at ℓ = λ/4. For short runs, $\approx2K_b\beta\ell$. This is how a clock harmonic reaches an RF trace (Example 4).

## Design equations & rules of thumb

| Rule | When valid | Value on the reader's boards |
|---|---|---|
| $t_{pd}$ = 6.0 ps/mm (microstrip, εeff 3.3) | FR-4 outer layers | 1 ns edge = 165 mm |
| Terminate if TD > tr/6 (10 % overshoot) | 25 Ω driver, CMOS load | 1 ns: > 28 mm; 3 ns: > 80 mm |
| Series $R_t\approx Z_0-R_\text{out}$ | point-to-point | MCU pin (≈ 20–40 Ω) on 50 Ω: 22–33 Ω |
| Series R within 10 mm of the driver | so the R-to-pin stub is ≪ the edge | — |
| Parallel 50 Ω: $V^2/R$ | high state | 3.3 V: 218 mW |
| $K_b=\frac14(L_m/L+C_m/C)$ | weak coupling | 7628, 0.2 mm traces, 0.6 mm pitch: −27.5 dB |
| NEXT saturates at $\ell_\text{sat}=t_rv/2$ | any | 1 ns: 83 mm |
| FEXT ∝ ℓ/tr, zero in stripline | microstrip only | 10 cm, 0.5 ns on 7628: −6 % |
| Crosstalk falls ≈ as $1/(1+(D/h)^2)$ (J&G) | over a solid plane | thin prepreg ≫ thick 2-layer |
| 3W (centre) rule | only when W ≈ h | 7628: −27.5 dB; 2-layer: −15.5 dB |
| RF victim: $|S_{31}|\approx2K_b\beta\ell$ | short run, weak coupling | 10 mm at 920 MHz, 2 mm gap: −54 dB |

## Worked examples

### Example 1 — the ESP32-S3 SPI clock to the SD card
- **Geometry:** a 40 MHz SPI clock, 60 mm on L1 of a JLC04161H-7628 board (0.2 mm trace, 68 Ω bare by Hammerstad–Jensen), to one SD card. The ESP32 GPIO at its higher drive strengths has edges of roughly 1–2 ns (from knowledge, not datasheet-verified) and an output resistance of roughly 25–40 Ω.
- **Delay:** TD = 60 mm × 6.0 ps/mm = 0.36 ns. With $t_r$ = 1 ns, TD/tr = 0.36, so the script's table predicts **≈ 20–25 % overshoot** and visible ringing at the card.
- **Fix:** a **33–39 Ω resistor within a few mm of the ESP32 pin**: 68 − 30 ≈ 38 Ω, so 33 Ω (slightly under-terminated) or 39 Ω. That gives overshoot ≈ 0. As a bonus, the slower edge cuts high-order harmonics: the 63rd harmonic at 1575 MHz that the [mixed-signal page](mixed-signal-layout.md) worries about drops by several dB.
- **Check** with a 500 MHz+ scope probe at the card, using a short ground spring ([probing](../17-test-measurement/oscilloscopes-and-probing-for-rf.md)).

### Example 2 — a sensor bus with several devices (the multi-drop trap)
A Teensy 4.1 SPI bus runs to an IMU, a barometer and a flash chip in a daisy chain 80 mm long. Series termination at the driver gives the *mid-line* devices a 1.65 V plateau for up to 2TD ≈ 1 ns. Their inputs see a slow, stepped edge, which is usually tolerable at 3.3 V because the CMOS threshold is about 1.65 V, but it is marginal. Better options:
1. Slow the edges (lower drive strength) so that $t_r$ ≫ 2TD, making the bus lumped. At 10 MHz SPI, 3–5 ns edges are fine.
2. Route a short trunk with a series resistor and very short stubs (stub delay < tr/10).
3. Use separate chip-select-timed lines.

Parallel termination at the far end would cost 218 mW and drop the swing. Do not use it on 3.3 V CMOS.

### Example 3 — NEXT between SPI clock and MISO
On JLC-7628 with 0.2 mm traces at 0.6 mm pitch (3W), $K_b$ = 0.042: a 3.3 V clock edge injects about **140 mV** of saturated NEXT into a matched victim, and up to about 2× that into a CMOS-terminated one. FEXT over 60 mm with 1 ns edges is $0.037\times0.36$ ≈ 1.3 %, or 45 mV. Both are fine against CMOS noise margins (≈ 0.8 V). On a 2-layer board with the same traces at the same 0.9 mm pitch, $K_b$ = 0.17 gives **560 mV**, enough to cause glitches on a quiet line that changes state near the clock edge. Spread the traces to ≥ 3 mm (10W: $K_b$ = 0.038) or put a stitched ground pour between them.

### Example 4 — how close can the clock run to the LoRa RF trace?
On JLC-7628, a 0.36 mm 50 Ω RF trace runs 10 mm parallel to a clock trace.
- **Coupling at 920 MHz:** $|S_{31}|$ = −25.6 dB (0.2 mm gap), −34 dB (0.5 mm), −43 dB (1 mm), −54 dB (2 mm).
- **The aggressor:** the [mixed-signal page](mixed-signal-layout.md) estimates a 40 MHz clock's 23rd harmonic at 920 MHz at about −20 dBm (1 ns edges).
- **Result:** even at a 2 mm gap the coupled harmonic is about −74 dBm, which is **63 dB above** a LoRa SF12 sensitivity of about −137 dBm and lands on the SG 920 MHz channel.
- **Conclusion:** spacing helps, but the clock harmonic must *also* be attacked at the source:
  1. move the LoRa channel ≥ 0.5 MHz away from 920.000 MHz;
  2. slow the edges with a series R;
  3. route the clock on an inner layer under a solid plane;
  4. never run it parallel to the RF trace at all (cross at 90° on a different layer).

### Example 5 — when not to bother
A 1 MHz I²C bus has 100–300 ns edges set by the pull-ups. TD for 100 mm is 0.6 ns, so TD/tr < 0.01. It is a lumped RC, and no termination is needed. Crosstalk into it is governed by the large pull-up resistance (a high-impedance victim, so capacitive coupling dominates), not by $Z_0$. Keep it away from switch-node traces of buck converters for that reason.

## Practical notes
- **Placement:** put series resistors within ~5–10 mm of the driver pin, *before* any branch. Use 0402 parts; the pad parasitics (≈ 0.1 pF, 0.5 nH) are negligible at these edge rates.
- **Choosing $R_t$:** measure or estimate the driver's output impedance from the datasheet (V_OH drop at a stated current). For MCU GPIO at full drive it is typically 20–50 Ω. Over-terminating (too large R) slows the edge but is otherwise safe. Under-terminating leaves some ringing.
- **Drive strength settings** (ESP32, STM32, i.MX RT on the Teensy) are the cheapest termination: use the weakest setting that meets timing.
- **Stack-up first:** the [canonical stackup advice](stackups-and-materials.md) (4-layer, thin prepreg to a solid L2 ground) reduces crosstalk more than any spacing rule. On 2-layer boards, flood ground between signal traces and stitch it.
- **Differential pairs** (USB, LVDS camera links) are terminated differentially at the receiver (usually inside the chip). Keep them tightly coupled and symmetric. See [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md) for $Z_\text{diff}$.
- **Measure:** TDR (a VNA in time-domain mode) shows the impedance profile. A fast scope at the receiver shows overshoot. Crosstalk can be measured by driving one trace with a pulse generator (or an MCU toggling) and probing the terminated victim.

- **Scope ringing that is not real:** a long probe ground lead (10–15 cm) forms an LC resonance near 100–300 MHz that looks exactly like line ringing. Verify with a spring-tip ground before adding terminations.
- **Rocket environment:** vibration and temperature do not change Z₀ or crosstalk measurably, but connectors and harnesses between boards are long, uncontrolled lines. Series-terminate every fast signal that leaves the board.

## Common mistakes & misconceptions
- **"Termination depends on the clock frequency."** It depends on the *edge rate* versus line length. A 1 MHz signal with 1 ns edges rings just like a 100 MHz one.
- **Putting the series resistor at the receiver end.** It then does nothing for reflections; it belongs at the driver.
- **Parallel-terminating 3.3 V CMOS to ground.** It halves or thirds the high level and burns hundreds of mW. Use series termination.
- **Series-terminating a multi-drop bus** and expecting clean edges at the middle devices.
- **"The 3W rule guarantees low crosstalk."** It is a W-relative rule. What matters is D/h: on a 1.5 mm 2-layer board, 3W leaves −15 dB.
- **"Longer parallel runs always mean more NEXT."** NEXT saturates beyond $t_rv/2$. FEXT keeps growing with length in microstrip.
- **Unstitched guard traces.** Without vias every few mm they are resonant stubs.
- **Ignoring return-path breaks.** A trace crossing a plane split creates far more coupling than any spacing rule predicts.

## How to simulate / verify
- `python3 tools/verify/e11_crosstalk.py` (≈ 5 s): **12/14 checks**; output in `tools/verify/e11_crosstalk_output.txt`. It covers:
  - the Bergeron transmission-line simulation (overshoot vs TD/tr; series, parallel, Thevenin and AC terminations);
  - field-solver $L_m/L$, $C_m/C$ (via `tline_fd2d.coupled_params`) → NEXT/FEXT formulas vs an exact even/odd modal simulation;
  - stripline FEXT = 0; the 3W rule on both boards; clock-to-RF coupling at 920 MHz.
- **The two misses** (pre-set bounds):
  - overshoot at TD = tr/10 is 5.2 %, against "< 5 %": the 5 pF load adds ringing, so the rule of thumb is TD < tr/10 for ≈ 5 %;
  - the AC termination with 100 pF settled *slower* than unterminated (13.5 vs 6.6 ns), because a weak driver must charge C through $R_s+Z_0$. The expectation was wrong, not the physics.
- **SPICE:** ngspice's lossless `T` element or the lossy `LTRA`, with coupled lines as two T-lines plus mutual L and C sections ([SPICE page](../16-simulation-tools/spice-circuit-simulation.md)). openEMS for full 3-D coupling including vias and plane gaps.
- **KiCad:** set net classes with the trace widths from the [canonical width table](stackups-and-materials.md#canonical-50-ω-width-table), and add courtyards and keep-outs around RF traces. The `pcbreview` skill can flag crosstalk spacing.

## Open questions / gaps
- ESP32-S3 and i.MX RT GPIO edge rates and output impedances per drive-strength setting are quoted from knowledge. A scope measurement on the flight computer would replace them.
- Coupling of a clock trace into a *chip antenna* (radiated, not trace-to-trace) is not computed. An openEMS model is suggested in [mixed-signal layout](mixed-signal-layout.md).
- The soldermask effect on FEXT was not quantified (the field solver supports a mask layer; a future run could tabulate it).
- The guard-trace resonance claim is from the literature (Bogatin), not simulated here.

- Victim-termination effects (CMOS-open far end doubling FEXT) are stated, not simulated; the script's victims are matched at both ends.

## Sources
1. S. H. Hall, H. L. Heck, *Advanced Signal Integrity for High-Speed Digital Designs*, Wiley 2009, ch. 3 (coupled lines: even/odd modes, NEXT/FEXT derivation, saturation length) and ch. 2 (reflections and termination). (textbook)
2. E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., Pearson 2018, ch. 8 (reflections, when to terminate, series/parallel/AC termination; §8.8–8.12) and ch. 10 (cross talk, NEXT/FEXT coefficients, guard traces). (textbook; from knowledge)
3. H. W. Johnson, M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall 1993, ch. 4 (transmission lines, termination), ch. 5 (ground planes, crosstalk ∝ 1/(1+(D/H)²)), ch. 6 (terminations). (textbook; chapter/section numbers checked against the publisher's full ToC, sigcon.com/vault/pdf/HSDD-TOC-full.pdf, by W5-S18 2026-10-13)
4. C. R. Paul, *Analysis of Multiconductor Transmission Lines*, 2nd ed., Wiley 2008, ch. 6–7 (weak-coupling crosstalk, inductive/capacitive coupling, modal decomposition). (textbook; from knowledge)
5. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015, §12.9–12.10 (digital signals on long wires, driving cables, termination). (textbook)
6. This KB: [grounding and return paths](grounding-and-return-paths.md) (Johnson & Graham coupling law and return paths), [mixed-signal layout](mixed-signal-layout.md) (harmonic levels and isolation targets), [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md) (field solver `tools/verify/tline_fd2d.py`). Verification: `tools/verify/e11_crosstalk.py`. (numerical check)
