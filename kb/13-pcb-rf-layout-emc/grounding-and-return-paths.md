---
title: Grounding and return paths — where RF return current really flows, and why splits, slots and "star grounds" fail
domain: 13-pcb-rf-layout-emc
slug: grounding-and-return-paths
tags: [return-current, ground-plane, reference-plane, image-theory, current-spreading, split-plane, slot, moat, stitching-via, stitching-capacitor, layer-change, star-ground, AGND, DGND, mixed-signal, 20-H-rule, crosstalk, loop-inductance]
prerequisites:
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - ../02-electromagnetics/inductance-capacitance-from-fields.md
  - stackups-and-materials.md
related:
  - vias-stitching-fencing.md
  - mixed-signal-layout.md
  - emc-emi-fundamentals.md
  - power-distribution-decoupling-for-rf.md
  - rf-layout-rules.md
  - ../02-electromagnetics/radiation-from-currents-hertzian-dipole.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Grounding and return paths

## Questions this page answers
- Where does the return current of an RF trace flow in the ground plane?
- How wide is the "shadow" of return current under a microstrip on a 4-layer vs a 2-layer board?
- At what frequency does return current stop taking the shortest path and start following the trace?
- Why is routing a trace across a split or slot in the ground plane so bad, even at low frequency?
- Should I split my ground plane into analog, digital and RF grounds?
- What do I do with an ADC's AGND and DGND pins?
- Does a "star ground" work at RF?
- What happens to the return current when my signal changes layers through a via?
- How close must a stitching via or capacitor be to a layer-change via?
- Is the "20-H rule" for power planes worth following?
- Why does my 2-layer board have more crosstalk than the same layout on 4 layers?
- Is a cross-hatched ground plane as good as a solid one?
- Does the ground plane itself have to be "50 Ω"?
- How do I avoid ground loops between boards, batteries and cables?

## TL;DR
- **At RF the return current flows in the plane directly under the trace**, with density $K(x)=\frac{I}{\pi}\frac{h}{h^2+x^2}$ (image theory; verified with an FD field solution, script §2). **50 % flows within ±h, 80 % within ±3h, 90 % within ±6.3h.** On JLC04161H-7628 (h = 0.21 mm) 90 % of the return lies within ±1.3 mm of the trace centreline; on a 2-layer 1.6 mm board, within ±9.5 mm.
- **Crossover from "lowest resistance" to "lowest inductance"** happens at $f_c\approx\Delta R/(2\pi\Delta L)$ — a few kHz to ≈ 100 kHz on real boards (script §4). Everything RF, every clock edge and every switching-regulator harmonic is far above it: **the return follows the signal**.
- **Never route a signal across a gap, slot or split in its reference plane.** A 20 mm slot adds ≈ 2.7 nH by the closed form with an assumed Z_slot = 100 Ω (16 Ω at 915 MHz, RL 16 dB for a 50 Ω line); openEMS on the JLC 2-layer board fits **Z_slot ≈ 70–94 Ω** and 1.95 nH for 20 mm (RL ≈ 19 dB), so the table below is ≈ 1–3 dB pessimistic for short slots and, worse, turns the two plane halves into a slot/dipole antenna: a 10 mA, 100 MHz digital harmonic crossing it can drive a 1 m cable 24–30 dB over the FCC Class B limit (script §6, order-of-magnitude).
- **Use one solid, continuous ground plane and partition the layout**, not the plane (Ott; ADI) [1][2][3]. Tie a converter's AGND and DGND pins together to the same plane at the part — the names describe the chip's internal circuits, not your system grounds [2].
- **"Star grounds" are a low-frequency (audio/DC) technique.** A 30 mm ground trace is ≈ 30 nH = 172 Ω at 915 MHz — not a ground. At RF, "ground" means a low-inductance plane plus many short vias.
- **Layer changes need a return path next to the via**: a GND-to-GND stitching via 1 mm away through the JLC 1.065 mm core adds ≈ 0.8 nH (4.7 Ω at 915 MHz); 10 mm away, 1.8 nH. If the two reference planes are at different nets (GND/PWR), the return must go through a decoupling capacitor — keep one within a few mm, or better, make both references GND.
- **The 20-H rule does not reduce far-field emissions** (Shim & Hubing measurements) [4]; stitch plane edges with vias instead ([vias, stitching and fencing](vias-stitching-fencing.md)).
- **Thin dielectric to the plane cuts crosstalk**: coupling ∝ $1/(1+(D/h)^2)$ — the same 1 mm trace spacing couples ≈ 24 dB less on 0.21 mm prepreg than on a 1.5 mm 2-layer board (script §5) [5].

## Intuition (no math)
Every current flows in a loop. A signal "trace" is only half the circuit; the other half is the **return path**, and at high frequency the energy actually travels in the electric and magnetic fields in the dielectric *between* the trace and its return (Hartley's framing: the copper only guides the fields) [6]. Whatever shape that field region has, the return current in the plane is its footprint.

Why under the trace? The current distribution that nature picks at high frequency is the one with the **lowest inductance**, which is the one with the **smallest loop area** — i.e. the return hugging the signal. (At DC it is the one with the lowest *resistance*, which spreads out and takes the shortest geometric path.) Think of the ground plane as a mirror: the trace sees its own mirror image a distance h below the plane, and the return current is concentrated where the mirror image is. Move the plane closer (thin prepreg) and the image — and the return — become tighter.

"Ground" is therefore not a bottomless sink at 0 V. It is the **return conductor of every signal on the board**, and any obstacle in that conductor — a slot, a split, a missing plane under a connector, a via to a different layer without a nearby return via — forces the return to detour. The detour is a larger loop: more inductance (impedance mismatch, ground bounce), more magnetic coupling to neighbours (crosstalk), and a voltage across the obstacle that drives the plane halves and any attached cables as an antenna (radiation, susceptibility).

For mixed-signal boards the historical advice was to **split** the ground into analog and digital halves joined at one point, to stop digital return current flowing through the analog area. That works only when *no signal crosses the split* and the return currents actually stay in their halves. Modern practice (Ott, ADI, Bogatin) keeps one solid plane and gets separation by **placement and routing discipline**: digital return currents stay under digital traces (because they follow them at HF), so if you don't route digital through the analog area, its currents don't go there either [1][2][7].

## The math

### Level 1 — the return-current footprint
For a thin trace at height h above an infinite ground plane carrying current I, the surface current density in the plane at lateral offset x is
$$K(x)=\frac{I}{\pi}\,\frac{h}{h^2+x^2}\quad[\mathrm{A/m}],\qquad \int_{-\infty}^{\infty}K\,dx=I .$$
The fraction within ±x is $F(x)=\frac{2}{\pi}\arctan\frac{x}{h}$:

| within | ±0.5h | ±h | ±2h | ±3h | ±5h | ±10h | ±20h |
|---|---|---|---|---|---|---|---|
| fraction | 29.5 % | 50 % | 70.5 % | 79.5 % | 87.4 % | 93.7 % | 96.8 % |

Tails fall slowly (∝ 1/x²): a ground-plane cut 5h away from a trace still interrupts ≈ 6 % of its return current each side.

| Stackup | h | 90 % within | 99 % within |
|---|---|---|---|
| JLC04161H-7628 L1/L2 | 0.2104 mm | ±1.33 mm | ±13.4 mm |
| JLC04161H-3313 L1/L2 | 0.0994 mm | ±0.63 mm | ±6.3 mm |
| 2-layer 1.6 mm | ≈ 1.43–1.51 mm (JLC0216A core 1.43 mm; 1.51 mm used here) | ±9.5 mm | ±96 mm |

A real 50 Ω microstrip (W ≈ 1.8h on FR-4) broadens the centre of the distribution (peak 0.25/h instead of 1/πh = 0.32/h) but the tails are the filament's: 82 % within ±3h (FD field solution, script §2).

### Level 2 — derivation, resistance of the return, and the crossover frequency
**Image theory.** The plane (a perfect conductor for the tangential magnetic field at frequencies where the skin depth ≪ plane thickness) is replaced by an image current −I at depth −h. The tangential H at the plane surface from the pair is $H_x=\frac{I}{2\pi}\frac{2h}{h^2+x^2}$, and the surface current equals the tangential H: $K=H_x$, which gives the formula above. The script checks it against a 2-D finite-difference solution of the air-filled strip (the TEM current distribution follows the charge distribution): a thin strip matches within 0.8 percentage points; $K(h)/K(0)=0.500$ exactly as predicted.

**Effective width of the return.** The plane's contribution to the line resistance is $R'_{plane}=R_\square\int K^2dx/I^2=R_\square/(2\pi h)$ — the return behaves like a strip of width **2πh** (1.3 mm on JLC-7628, 9.5 mm on a 2-layer board). Thin prepreg concentrates the return and raises plane loss (the JLC inner planes are also only 15 µm), one reason the thin-prepreg line has higher conductor loss ([stackups](stackups-and-materials.md)).

**When does the return follow the trace?** Two candidate return paths: under the trace (resistance $R_1$, loop inductance $L_1$) and a geometric short-cut ($R_2<R_1$, $L_2>L_1$). The current divides by impedance; the change-over occurs near
$$f_c\approx\frac{R_1-R_2}{2\pi\,(L_2-L_1)} .$$
For a U-shaped trace 3 × 50 mm whose ends are 50 mm apart (script §4): on JLC-7628 (15 µm inner plane) $f_c\approx$ 120 kHz; on a 2-layer 1 oz board ≈ 6 kHz. So below ~kHz (audio, DC power) return current takes the shortest path and **does** spread across the board; above ~100 kHz it follows the trace. (This lumped two-branch estimate cannot give the exact high-frequency split because it neglects mutual inductance; the field solution shows the concentration.)

**Crosstalk.** Johnson & Graham's classical result for two traces over a solid plane: the mutual coupling (inductive and capacitive) between parallel traces falls as $k\approx\frac{K}{1+(D/h)^2}$, $D$ = centre spacing [5]. With D = 1 mm: −27.5 dB (relative) on h = 0.21 mm vs −3.2 dB on h = 1.5 mm — the dominant reason 2-layer RF boards have isolation problems (script §5).
NEXT/FEXT derivation from mutual L and C, saturation length and the 3W rule: [digital termination and crosstalk](digital-termination-and-crosstalk.md).

### Level 3 — obstacles: slots, splits, layer changes and plane edges
**Slot or split under a trace.** A trace crossing a slot of length $\ell_s$ at its middle sees two shorted slotline stubs in series: $Z\approx j\frac{Z_{slot}}{2}\tan\!\left(\beta_s\frac{\ell_s}{2}\right)$ ([04 page](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)); for short slots $L\approx Z_{slot}\ell_s/(4v_s)$ (≈ 2.7 nH for 20 mm with $Z_{slot}$ ≈ 100 Ω). Script §6:

| Slot length | 100 MHz | 915 MHz | 2.45 GHz |
|---|---|---|---|
| 5 mm | X 0.4 Ω, RL 47 dB | 4.0 Ω, 28 dB | 10.7 Ω, 19.5 dB |
| 10 mm | 0.9 Ω, 41 dB | 7.9 Ω, 22 dB | 22 Ω, 13 dB |
| 20 mm | 1.7 Ω, 35 dB | 16 Ω, 16 dB | 56 Ω, 6 dB |
| 40 mm | 3.5 Ω, 29 dB | 36 Ω, 9 dB | resonant |

**openEMS check (W5-S11, 2026-10-13; `tools/verify/sim2_openems_pcb.py`, [openEMS workflow Run 4a](../16-simulation-tools/openems-workflow.md)).** 50 Ω microstrip on the JLC 2-layer core (1.43 mm, εr 4.5) crossing a 1 mm slot at its centre; L fitted to $|S_{21}|^2$ below the first resonance, then inverted through the formula above:

| Slot length | L fit | **Z_slot** | S21 at 915 MHz | S21 at 1575 MHz | First resonance |
|---|---|---|---|---|---|
| 10 mm | 1.20 nH | 87 Ω | −0.01 dB | −0.03 dB | > 3 GHz |
| 20 mm | 1.95 nH | 70 Ω | −0.05 dB | −0.18 dB | > 3 GHz |
| 40 mm | 4.35 nH | 79 Ω | −0.29 dB | −1.46 dB | 2.573 GHz (S21 −19.6 dB) |
| 60 mm | 7.63 nH (7.82 on mesh 2) | 92 Ω (94) | −0.97 dB | **−10.0 dB** | 1.741 GHz (1.758) |

So the assumed **100 Ω is ≈ 10–30 % high; use 70–94 Ω** (≈ 80 Ω) for a 1 mm slot on a 1.43 mm 2-layer board. The slot also sees a lower effective permittivity than the (εr + 1)/2 = 2.75 used for $v_s$: **εeff ≈ 2.06–2.12**, so the λ_s/2 resonance sits ≈ 14–16 % *higher* than the closed form (a thin board's slot field fringes mostly into air). The direction of the conclusion is unchanged: a slot is mild while short against λ_s/2 and destructive near resonance — a 60 mm split notches GNSS L1 by 10 dB, and at 915 MHz costs ≈ 1 dB plus radiation. These are simulation results (mesh-checked, ±1 % on resonance); they have not been measured on a board.

The impedance mismatch is the lesser problem. The voltage $V=I\,j\omega L$ across the slot (17 mV for a 10 mA harmonic at 100 MHz across 20 mm) appears **between the two halves of the plane** — a common-mode source that drives the board halves and every cable attached to them. With 1 m of cable (CM impedance 150–300 Ω) that is 57–115 µA of common-mode current, giving 2.4–4.8 mV/m at 3 m by Ott's cable formula — 24–30 dB over the FCC Class B limit ([EMC fundamentals](emc-emi-fundamentals.md)). This is why "don't cross splits" is an EMC rule even for slow-looking signals: their *edges* have 100 MHz content.

**Layer change.** When a signal goes from L1 (referenced to L2) to L4 (referenced to L3) through a via, its return must go from L2 to L3. If both are GND, a **stitching via** carries it; the added loop is the go/return via pair through the core, $L\approx\frac{\mu_0}{\pi}h_{core}\ln(s/r)$ (Johnson; [04 page](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)). On JLC-7628 (core 1.065 mm, r = 0.15 mm): s = 0.6/1/2/5/10 mm → 0.59/0.81/1.10/1.49/1.79 nH (script §7). If L3 is a power plane, the return must jump through the **plane-pair capacitance or a decoupling capacitor** (ESL + mounting ≈ 0.7–1.5 nH plus the spreading inductance to reach it) and it also **excites the plane-pair cavity** (resonances at $f_{mn}=\frac{c}{2\sqrt{\varepsilon_r}}\sqrt{(m/A)^2+(n/B)^2}$, e.g. 715 MHz for a 100 × 50 mm board — [cavity page](../02-electromagnetics/waveguides-and-cavity-resonators.md)). For RF signals: **keep them on one layer; if they must change layers, reference GND on both sides and put a GND via within ≈ 1 mm (or a ring of 2–4).**

**Plane edges and the 20-H rule.** Fringing fields at a power/ground plane edge radiate; the "20-H rule" recesses the power plane by 20× the plane spacing. Shim and Hubing's modelling and measurements found that it contains the near field slightly but **does not reduce, and at plane resonances slightly increases, far-field radiation** [4]. Effective measures: GND planes on both sides of power planes, **edge via stitching** of GND planes at ≤ λ/20 pitch, decoupling to damp plane resonances ([PDN](power-distribution-decoupling-for-rf.md)).

**Cross-hatched planes.** Hatching (a copper grid instead of a solid pour) exists for mechanical reasons — flex circuits that must bend, and copper balance against warp on thin rigid boards. Electrically it is a perforated reference: the return current must follow the grid, so loop inductance rises and Z0 depends on where the trace sits over the grid. A 2-D field solution for a 0.2 mm trace on 0.1 mm polyimide (εr 3.3, 52.7 Ω over a solid plane) with 0.2 mm hatch lines running parallel to the trace (worst case) gives **58 Ω over a hatch line and 87 Ω over a gap at 0.6 mm pitch; 59 Ω and 120 Ω at 1.0 mm pitch** (script §9). With 45° hatching the impedance alternates along the line at the hatch period — a periodic discontinuity that becomes resonant when the period approaches λ/2. **Use solid planes for RF and any controlled-impedance line**; on flex, use a solid plane under RF/impedance traces and hatch only elsewhere, and get the fab to compute Z0 for the hatch geometry if you must use it.

**"The ground must be 50 Ω too."** It is not a separate part with its own impedance: Z0 is a property of the *pair* — signal conductor plus reference — and their geometry (width, height, εr). The plane is the return conductor of that line; what matters is that it is continuous under the trace (so the geometry, and therefore Z0, stays constant) and that its own impedance is small compared with the circuit's (ground vias, plane resistance, slots — all covered above).

**Where the "ground is not equipotential" argument ends.** At RF even a solid plane has a voltage gradient wherever current flows through it; a plane of sheet impedance $Z_\square\approx(1+j)R_s$ (skin effect, ≈ 8 mΩ/□ at 1 GHz) plus the loop inductance of the current path. The plane's virtue is not that it is "0 V everywhere" but that it offers every signal a return path with minimum loop area — so the voltages it develops are small and local.

## Design equations & rules of thumb

| Rule | Equation / value | Notes |
|---|---|---|
| Return footprint | $K=\frac{I}{\pi}\frac{h}{h^2+x^2}$; 50 % in ±h, 90 % in ±6.3h | keep plane intact ≥ ±3–5h each side of RF traces |
| Plane resistance of return | $R_\square/(2\pi h)$ | JLC-7628 L2 (15 µm): 0.86 Ω/m DC |
| Crossover to "follows trace" | $f_c\approx\Delta R/(2\pi\Delta L)$ | ≈ 5–120 kHz |
| Crosstalk | ∝ $1/(1+(D/h)^2)$ | 3h spacing ≈ −20 dB relative |
| Slot under a trace | $L\approx Z_{slot}\ell_s/(4v)$, resonant at $\ell_s\approx\lambda_s/2$; Z_slot ≈ 70–94 Ω and εeff ≈ 2.1 on a 1.43 mm 2-layer board (openEMS) | never; if unavoidable, bridge it with a 0 Ω/cap *under the trace* |
| Layer-change return via | $L\approx\frac{\mu_0}{\pi}h\ln(s/r)$ | ≤ 1 mm: < 0.8 nH through 1 mm core |
| Ground trace instead of plane | ≈ 1 nH/mm | 30 mm = 172 Ω @ 915 MHz |
| Stitching GND pours / edges | pitch ≤ λ/20 of highest frequency of concern | [vias page](vias-stitching-fencing.md) |

## Worked examples

### 1. Keep-out around a 915 MHz feed on JLC04161H-7628
Where can a cut in L2 (e.g. an antenna keep-out, a split for a module outline) go without disturbing the feed? The return within ±3h = ±0.63 mm carries 80 %; ±1.33 mm carries 90 %; ±2.7 mm carries 95 %. Rule: **no L2 voids within ≈ 2.5 mm (≈ 12h) of the RF trace**, and L3 below should also be solid under RF sections so any via transition has a nearby reference. For the U.FL/SMA pad where L2 is intentionally voided to reduce pad capacitance, the return transitions to L3 — put GND vias around the void so the L2 and L3 grounds are tied at the void edge ([connectors and launches](connectors-and-launches.md)).

### 2. Why the 2-layer LoRa board "works on the bench but fails EMC"
Same schematic, 2-layer 1.6 mm board, bottom-layer ground pour broken by a few control traces. A 40 MHz MCU clock trace crosses one 20 mm gap in the pour. Its 3rd–25th harmonics (120 MHz–1 GHz) see ≈ 2.7 nH across the gap; with 1–3 mA per harmonic the gap develops 2–40 mV, which drives the battery lead and the antenna coax braid as a dipole. Result: harmonics radiated at tens of dB over Class B limits and — more important for Marcus — **re-received by the LoRa or GNSS antenna a few centimetres away** (desense). Fix: move the control traces to the top layer, stitch the pour; or go 4-layer with an unbroken L2.

### 3. An ESP32-S3 USB pair that dives to L4
USB D+/D− go from the connector on L1 to L4 (reference L3 = +3V3 plane). Their return has to cross from L2 (GND) to L3 (3V3): if the nearest decoupling capacitor is 15 mm away, the return loop is ≈ several nH and the USB edge energy spreads into the L2/L3 cavity (radiating at its resonances, which for a 60 × 40 mm board start near 1.3 GHz — close to GNSS L1). Fix: keep USB on L1; or make L3 GND under the USB route; or place a 100 nF + stitching GND via pair right at the via transition.

### 4. How far is "far enough" for crosstalk between an SPI clock and a GNSS RF trace?
On JLC-7628 (h = 0.21 mm), relative coupling at D = 2 mm is −39 dB, at D = 5 mm −55 dB; on 2-layer 1.6 mm board, −9 dB and −22 dB. With an SPI clock of 3.3 V edges, its 1575 MHz spectral content might be ≈ −40 dBm at the trace; the GNSS signal is −130 dBm. You need > 90 dB isolation — geometry alone won't give that on 2-layer; on 4-layer use D ≥ 5 mm **plus** a GND guard/via fence, plus routing on opposite sides of a solid plane ([mixed-signal layout](mixed-signal-layout.md), [vias](vias-stitching-fencing.md)).

## Practical notes
- **Stackup philosophy (Hartley)**: every signal and power layer one dielectric away from a ground plane; for 4-layer RF boards, **L1 signal/RF – L2 GND – L3 GND or power pour – L4 signal** [6]. Two GND planes (L2, L3) stitched together give every layer change a GND-to-GND return.
- **Pour GND on L1 around RF sections and stitch it to L2** — but don't leave floating or single-via copper islands (they resonate and couple) ([vias](vias-stitching-fencing.md)).
- **Components with ground pins** (LoRa modules, RF switches, PAs): one via per ground pad minimum, next to the pad; the module's ground is the antenna's counterpoise return ([rf-layout-rules](rf-layout-rules.md)).
- **Where current *enters* the board matters**: battery and pyro returns carry amps; keep their path from connector to regulator short and away from RF and sensor areas. At DC and ~kHz the return *does* spread (script §4) — a heavy low-frequency current crossing the sensor area produces µV–mV offsets on single-ended sensor signals.
- **System-level ground loops (boards, batteries, cables).** Every connection between two subsystems that carries both a signal and a ground creates a loop with any *other* ground path between them (a second cable, a shared battery return, a metal bulkhead, a USB lead to the laptop on the bench). At low frequency a changing magnetic field through that loop, or a voltage difference between the two grounds driven by large return currents (servo, pyro, motor-driver), adds noise to single-ended signals; at RF the same loops carry common-mode current and radiate or pick up ([EMC](emc-emi-fundamentals.md)). Rules: (1) route each high-current return with its supply (twisted pair) back to its source, never through another board's ground; (2) give inter-board links **one** low-impedance ground path (a solid connector ground with many pins, or board-to-board connectors) and avoid parallel ground wires through other harnesses; (3) use differential or current-mode signalling (CAN, RS-485, LVDS) for long links; (4) bond cable shields at the connector, 360° where possible, at both ends for RF shielding (accepting the LF loop), or at one end only when LF hum on an audio-band analog signal is the larger problem; (5) on the bench, beware the laptop USB ground in parallel with the battery ground — measure with the board on battery.
- **Chassis / airframe**: on a rocket there is often no chassis. The battery pack, harness and antenna coax are the "chassis". Keep one board ground, bond shields at the connector, and manage CM currents on cables ([EMC](emc-emi-fundamentals.md)).
- **Measure**: a return-path problem shows up as (a) S11 ripple at the discontinuity on a VNA/TDR, (b) a near-field H-probe hot spot at the slot/split, (c) CM current on cables measured with a clamp-on current probe.

## Common mistakes & misconceptions
- **"Current returns via the shortest path to the power supply."** Only at DC/low kHz. At RF it returns under the trace.
- **"Split AGND/DGND planes with a single tie point"** — correct only if nothing crosses the split and the two sides really have no shared return currents; with SPI/UART/clock lines crossing, a split makes things worse [1][2].
- **"Ground is 0 V everywhere."** Ground has impedance; a plane is good because loops are small, not because it is equipotential.
- **Stitching vias as decoration.** Their job is to give specific return currents a path (layer changes, pour-to-plane, edges) — place them where the currents are.
- **Using a thermal-relief spoke connection for RF ground pads/vias** — adds ≈ 1 nH-class inductance. Use solid connections for RF grounds (accept the soldering heat penalty or use thermal vias).
- **Assuming the 20-H rule reduces emissions** [4].
- **Guard traces grounded at one end** — a λ/4-ish guard trace resonates and couples *more*. Guards must be stitched to GND at ≤ λ/20 intervals or omitted.
- **"A hatched ground plane is as good as a solid one."** Z0 rises by 10–130 % depending on hatch pitch and trace position (script §9) and the return path is broken into a grid — solid planes for RF.
- **"RF ground must be 50 Ω."** Z0 belongs to the trace + reference geometry; the plane must be continuous and low-impedance, not "50 Ω".

## How to simulate / verify
- `python3 tools/verify/pcb_return_current.py` (≈ 30 s): image-theory distribution; independent FD check for thin and 50 Ω strips; 2πh effective width; crossover estimate; crosstalk; slot impedance/return loss and the slot's CM-radiation estimate; return-via inductance; star-ground wire reactance; Z0 over a cross-hatched reference (FD, §9).
- **openEMS / Sonnet**: model a microstrip crossing a slot and a via transition with and without stitching vias; plot surface current on the ground plane to see the detour ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)). A ready slot model: `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_pcb.py slot` (10–60 mm slots, Z_slot fit; [openEMS workflow Run 4a](../16-simulation-tools/openems-workflow.md)).
- **KiCad**: DRC cannot see return paths; review each RF/fast net on the plane layers visually ("View → Layers" with the net highlighted), or use the `pcbreview` return-path checks where available.
- **Bench**: near-field H-probe scan over the plane while the board runs; a hot slot edge is unmistakable ([test & measurement](../17-test-measurement/_index.md)).

## Open questions / gaps
- The closed-form table uses an assumed slotline $Z_{slot}$ ≈ 100 Ω. The openEMS slot study (2026-10-13) gives 70–94 Ω and εeff ≈ 2.1 on the 2-layer core; the table has not been recomputed with these, and the 4-layer JLC04161H-7628 stack (slot in L2 under a 0.21 mm prepreg) has not been simulated. Neither has been measured.
- The crossover model is lumped (no mutual inductance) — a PEEC/FastHenry run of the U-shaped trace would give the actual split vs frequency.

## Sources
1. H. W. Ott, "Partitioning and layout of a mixed-signal PCB," *Printed Circuit Design*, June 2001, and "Grounding of mixed signal PCBs" tech tip, Henry Ott Consultants, https://hott.shielddigitaldesign.com/techtips/split-gnd-plane.html — one solid plane, partition the layout; splits only with a single bridge and no traces crossing. (expert article)
2. H. Zumbahlen, "Staying well grounded," *Analog Dialogue* 46-06, June 2012, Analog Devices, https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html — AGND/DGND pin naming, tie at the converter. (app note)
3. Analog Devices, MT-031 "Grounding data converters and solving the mystery of AGND and DGND" (W. Kester), https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf — (cited from knowledge; fetch timed out). (app note)
4. H. W. Shim, T. H. Hubing, "20-H rule modeling and measurements," *Proc. IEEE Int. Symp. EMC*, 2001, https://cecas.clemson.edu/cvel/pdf/EMCS01-939.pdf — 20-H rule does not reduce radiated emissions; slightly higher at resonances. (peer-reviewed conference)
5. H. W. Johnson, M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall, 1993, ch. 5 "Ground Planes and Layer Stacking" (return current distribution, §5.2 crosstalk in solid ground planes ∝ 1/(1+(D/H)²)). (textbook; chapter/section numbers checked against the publisher's full ToC, sigcon.com/vault/pdf/HSDD-TOC-full.pdf, by W5-S18 2026-10-13)
6. R. Hartley, "How grounding controls noise and EMI in a PCB," Sierra Circuits article/video, https://www.protoexpress.com/blog/how-grounding-controls-noise-and-emi-by-rick-hartley/ ; AltiumLive talks on grounding and return paths. (talk)
7. E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., Pearson, 2018, ch. 6–10 (return paths, reference-plane changes, crosstalk). (textbook; from knowledge)
8. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009, ch. 3 (grounding), ch. 10–12 (PCB layout, return paths, digital radiation). (textbook; from knowledge)
9. TI, SWRA640H, *CC13xx/CC26xx Hardware Configuration and PCB Design Considerations*, 2024 — solid ground under the RF path back to the exposed-pad vias; no traces under the RF path. (app note)
10. Verification script `tools/verify/pcb_return_current.py` (this page); via formulas from [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md).
