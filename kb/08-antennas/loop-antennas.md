---
title: Loop antennas — small loops, magnetic (transmitting) loops, full-wave loops, ferrite rods, receive-only loops
domain: 08-antennas
slug: loop-antennas
tags: [loop, small-loop, magnetic-loop, ferrite-rod, full-wave-loop, quad, radiation-resistance, efficiency, direction-finding, active-loop, active-whip, mini-whip, receive-only, p372, sense-antenna, lf-time-signal, mla-30]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, ../02-electromagnetics/skin-effect-conductor-loss-roughness.md, ../02-electromagnetics/magnetic-materials-permeability.md]
related: [small-antenna-limits.md, pcb-and-chip-antennas.md, antenna-measurement.md, ../04-real-components-hf/ferrites-and-beads.md, inductive-coupling-rfid-nfc-wpt.md, multiband-and-wideband-antennas.md, wire-antennas-hf-random-wire-fan-dipole.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Loop antennas

## Questions this page answers
- How does a small loop radiate, and why is its radiation resistance so tiny?
- Why is a small loop's efficiency so sensitive to conductor size?
- What is a "magnetic loop" (small transmitting loop) and why does it need a huge-voltage capacitor?
- How is a full-wavelength loop different from a small loop?
- Why do AM radios use ferrite rods, and why are they receive-only?
- When is a small loop a good receive antenna despite terrible efficiency?
- Are PCB loop antennas at 433 MHz (key fobs) any good?
- Is my active loop or mini-whip limited by the sky noise or by its own amplifier?
- Why does my cheap active loop (MLA-30) show ghost stations, hum or a high noise floor?
- How long must an active whip be at a quiet site?
- How does a sense antenna turn a loop's figure-8 into a cardioid?
- Can I receive LF time signals (DCF77, JJY, BPC) in Singapore, and with what antenna?

## TL;DR
- A **small loop** (circumference C ≲ λ/10) with uniform current I is a magnetic dipole of moment m = NIA. It has the same doughnut pattern as a short electric dipole (D = 1.5, 1.76 dBi) but with E and H swapped: maximum in the plane of the loop, null along its axis.
- **Radiation resistance**: R_r = 20π²(C/λ)⁴·N² = 31 171·(NA/λ²)² Ω — it scales as the *fourth* power of size. A 30 mm loop at 433 MHz has R_r ≈ 0.068 Ω (formula; our MoM 0.084 Ω) against ≈ 0.16 Ω of copper skin-effect loss for 1 mm wire → **≈ 29 % efficient** (`tools/verify/ant_small_limits.py`).
- The formula is accurate only for C ≲ 0.07λ (MoM within ~5 %); at C = 0.14λ the MoM R_r is 24 % higher, at 0.23λ about 2× (current no longer uniform) — `tools/verify/ant_mom_general.py`.
- **Magnetic (small transmitting) loops**: fat tubing and a high-Q capacitor give usable efficiency (1 m, 22 mm copper at 14.2 MHz: ≈ 68 % from conductor loss alone, falling to ≈ 16 % at 7.1 MHz) with a very narrow bandwidth (≈ 9 kHz) and kilovolts across the capacitor at 100 W.
- A **full-wave loop** (C ≈ λ) is a different antenna: resonant near C ≈ 1.05λ at ≈ 130–140 Ω, maximum radiation *along the loop axis* (broadside to its plane), D ≈ 3.5 dBi (MoM) — the element of a quad beam.
- **Receive-only antennas are judged against ITU-R P.372 noise**, not by efficiency. At 7 MHz residential noise (Fa ≈ 49 dB) swamps a 1 m active whip's 3 nV/√Hz buffer by +12 dB. At a quiet-rural site (Fa ≈ 29 dB) the same whip is buffer-limited (−8 dB). A 1 m broadband loop into a 1 nV/√Hz amplifier is limited by the amplifier at a quiet site below ≈ 14 MHz (`s12_rx_antennas.py`).
- **Ferrite rods** multiply R_r by μ_eff² but μ_eff is limited by rod shape (demagnetization) and ferrite loss; they are for reception at LF/MF/HF where external noise dominates and efficiency doesn't matter.

## Intuition (no math)
A small loop of wire carrying current makes a tiny magnet whose magnetism oscillates. An oscillating magnetic dipole radiates exactly like an oscillating electric dipole with E and H interchanged: the radiated electric field circles around the loop's axis (it is parallel to the plane of the loop), the maximum is in the plane of the loop, and there is a null along the axis. So a loop lying flat (axis vertical) radiates horizontally polarized waves toward the horizon, and a loop standing upright radiates, in the directions within its plane, with E parallel to that plane. The reason it radiates so weakly is cancellation: current on one side of the loop flows opposite to current on the other side. Only the tiny path difference across the loop (∝ C/λ) keeps them from cancelling completely, and power goes as the square of that residue *squared again* because the loop area already involves two dimensions — hence R_r ∝ (C/λ)⁴.

Because R_r is minuscule, the loop's own copper resistance competes directly. Doubling the conductor diameter halves the loss resistance; doubling the loop diameter multiplies R_r by 16. That is why transmitting loops are made of thick copper pipe and why tiny PCB loops are inefficient.

When the loop grows to a full wavelength in circumference, the current reverses around it and the opposite sides now carry currents that add in the broadside direction. The pattern flips: now the loop radiates best *perpendicular* to its plane.

## The math

### Level 1 — formulas
Symbols: N turns, A loop area (m²), C = circumference, b = loop radius, a = wire radius, σ = conductivity, R_s = √(πfμ₀/σ) surface resistance, μ_eff = effective permeability of a core.

| Quantity | Formula | Notes |
|---|---|---|
| Radiation resistance | R_r = 20π²(C/λ)⁴N² = 31 171 (NA/λ²)² Ω | C ≲ 0.1λ, uniform current |
| With core | R_r × μ_eff² | ferrite rod, receive |
| Ohmic (skin-effect) loss | R_loss ≈ N·(C/2πa)·R_s × (1 + proximity factor) | proximity effect raises loss for close-wound turns |
| Inductance (1 turn, circular) | L ≈ μ₀b[ln(8b/a) − 2] | b ≫ a |
| Efficiency | η = R_r/(R_r + R_loss + R_cap) | capacitor ESR matters |
| Loop Q (loaded) | Q = ωL/(R_r + R_loss) | BW(3 dB) = f/Q |
| Capacitor voltage (tuned STL) | V_C ≈ √(2PQωL) (peak) | kV at 100 W |
| Receive open-circuit voltage | V = jωμ_eff N A B = (2π N A μ_eff/λ)·E | effective height h_e = 2πNAμ_eff/λ |
| Directivity | 1.5 (1.76 dBi), null on axis | same as short dipole |

### Level 2 — derivation of R_r by duality
A small loop of area A carrying I is equivalent to a magnetic dipole m = IA (A·m²). Its far field is E_φ = (η k² m /4πr) sinθ e^{−jkr}, where θ is measured from the loop axis (Balanis ch. 5 [1]). Compare the Hertzian electric dipole E_θ = j(η k I l/4πr) sinθ e^{−jkr}: the loop is equivalent to an electric dipole with I l ↔ j k m = j k I A. The electric dipole's R_r = (η/6π)(kl)² therefore maps to
$$R_r=\frac{\eta}{6\pi}k^4A^2=\frac{\eta}{6\pi}\Big(\frac{2\pi}{\lambda}\Big)^4A^2=\frac{8\pi^3\eta}{3}\Big(\frac{A}{\lambda^2}\Big)^2\approx 31\,171\Big(\frac{A}{\lambda^2}\Big)^2 ,$$
and with A = C²/4π, R_r = 20π²(C/λ)⁴. N turns multiply m by N, hence R_r by N². (Our script confirms the two forms agree: 1.97392×10⁻² Ω for C = 0.1λ.)

**Loss.** At RF the current flows within one skin depth δ = √(2/ωμ₀σ) of the surface, so a round wire of radius a and length C has R ≈ C·R_s/(2πa). For copper at 433 MHz, R_s = 5.43 mΩ. For a 30 mm loop of 1 mm wire: C = 94.2 mm → R_loss = 0.0942/(2π·0.0005)·0.00543 = 0.163 Ω; R_r = 0.068 Ω → η = 29 %. Multi-turn loops suffer an extra *proximity effect* (current crowding between adjacent turns) that can raise the loss severalfold for close spacing.

**Validity check (our MoM).** For 1 mm wire at 433 MHz: D = 10 mm (C = 0.045λ): MoM R_r = 0.00085 Ω vs formula 0.00084 Ω; D = 15 mm (0.068λ): 0.0044 vs 0.0042 Ω; D = 30 mm (0.136λ): 0.084 vs 0.068 Ω (+24 %); D = 50 mm (0.227λ): 1.01 vs 0.52 Ω; D = 80 mm (0.363λ): 29.9 vs 3.4 Ω. The formula rapidly fails above C ≈ 0.1λ because the current stops being uniform around the loop.

### Level 3 — full-wave loops, ferrite cores, and noise-limited reception
- **Full-wave loop (C ≈ λ).** The current distribution is roughly cos(φ) around the loop with maxima at the feed and opposite side; radiation is maximal along the axis. Our MoM (circular loop, wire radius 5×10⁻⁴λ at 433 MHz): C = 0.9λ: 97 − j276 Ω; 1.0λ: 120 − j97 Ω; **1.05λ: 138 − j9 Ω (≈ resonant), D = 3.6 dBi**; 1.1λ: 164 + j85 Ω. Square loops (quad elements) behave similarly (≈ 100–125 Ω, ≈ 3.1–3.4 dBi; Balanis/ARRL [1], [4]).
- **Ferrite rods.** A rod of relative permeability μ_r concentrates flux; its effective permeability is limited by the demagnetization factor N_d of the rod shape: μ_eff = μ_r/[1 + N_d(μ_r − 1)] → ≈ 1/N_d for μ_r ≫ 1/N_d. Long thin rods (length/diameter 10–20) reach μ_eff ≈ 50–150. R_r scales by μ_eff²; our example (1 MHz, 10 mm rod, 50 turns, μ_eff = 100) gives R_r ≈ 6×10⁻⁷ Ω — useless for transmitting, fine for receiving. Ferrite loss (μ'') and the core's frequency limits (see [ferrites](../04-real-components-hf/ferrites-and-beads.md)) restrict rods to below a few tens of MHz.
- **Why an inefficient receive antenna can be fine.** Below ~30 MHz, atmospheric and man-made noise received by *any* antenna is tens of dB above kT₀B (ITU-R P.372). An antenna with efficiency η reduces signal and external noise equally; as long as η·T_ext ≫ T_receiver, the SNR is unchanged. A 1 % efficient loop at 1 MHz (T_ext ~ 10⁶–10⁸ K) still delivers noise-limited reception. At UHF (433 MHz, T_ext ~ hundreds of K), antenna inefficiency directly degrades SNR — so small loops are a poor choice for a LoRa ground station. See [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md).
- **Chu–McLean.** A small loop is a TE₁ (magnetic dipole) radiator; its radiation Q is bounded by 1/(ka)³ + 1/(ka). Our 30 mm 433 MHz loop: X_L ≈ 193 Ω (MoM), R_r ≈ 0.084 Ω → Q_rad ≈ 2300 vs the bound ≈ 400 (ka = 0.136) — about 6× above the bound, typical for a thin-wire loop ([small-antenna limits](small-antenna-limits.md)).

## Receive-only antennas: active loops, E-field whips and the external-noise test

**The test.** A receive antenna is good enough when the external noise it collects is well above everything added after it: its own loss, the amplifier, the receiver. Below ≈ 30 MHz external noise is large. ITU-R P.372 gives the median noise factor $F_a$ (dB above $kT_0b$) as straight lines in log f:
- **man-made noise:** $F_a = c - d\log f_\text{MHz}$ with c/d = 76.8/27.7 (city), 72.5/27.7 (residential), 67.2/27.7 (rural) and 53.6/28.6 (quiet rural), valid 0.3–250 MHz;
- **galactic noise:** $52-23\log f$, which reaches the ground only above the ionospheric cut-off (≈ 10–20 MHz);
- **atmospheric noise** (lightning), which dominates at LF–MF and at night, is given only as charts in P.372.

| f (MHz) | Residential | Rural | Quiet rural | Galactic |
|---|---|---|---|---|
| 1 | 72.5 dB (5.2×10⁹ K) | 67.2 | 53.6 (6.6×10⁷ K) | 52.0 |
| 3.5 | 57.4 | 52.1 | 38.0 | 39.5 |
| 7 | 49.1 (2.4×10⁷ K) | 43.8 | 29.4 (2.5×10⁵ K) | 32.6 |
| 14 | 40.8 | 35.5 | 20.8 | 25.6 |
| 28 | 32.4 | 27.1 | 12.2 | 18.7 |

Measured man-made noise is often lower than the 1970s-based P.372 residential and rural lines (FFI 2016 survey [8]).

**Field-strength form.** P.372 converts $F_a$ to the vertical noise field of a short monopole over perfect ground:
$$E_n=F_a+20\log f_\text{MHz}+B-95.5\ \text{dB(µV/m)},\qquad B=10\log b .$$
Re-derived here: a short monopole over a PEC ground delivers $E^2\lambda^2/(640\pi^2)$ into a matched load, where E is the *local* field at the ground (twice the incident field). Setting this equal to $kT_0b$ gives −95.51 dB. The same calculation for a free-space λ/2 dipole gives P.372's −99.0 (`tools/verify/s12_rx_antennas.py` §1).

**Active E-field whip ("mini-whip") — high-impedance buffer.** A short whip of height h is a voltage source $E\,h/2$ (effective height h/2) behind its capacitance $C_a\approx 2\pi\varepsilon_0h/[\ln(2h/a)-1]$. The buffer's input capacitance $C_\text{in}$ divides that voltage. The external-noise margin over the buffer's noise $e_n$ is
$$M=20\log\frac{E_n\,(h/2)\,C_a/(C_a+C_\text{in})}{e_n}.$$
For $e_n$ = 3 nV/√Hz and $C_\text{in}$ = 5 pF (§2), using man-made noise only:

| Whip | C_a | Quiet rural, 1 / 7 / 14 / 28 MHz | Residential, 7 / 28 MHz |
|---|---|---|---|
| 0.10 m | 2.1 pF | −28 / −35 / −38 / −41 dB | −16 / −20 dB |
| 0.5 m | 6.5 pF | −9 / −16 / −18 / −21 | +4 / −1 |
| 1.0 m | 11.1 pF | −1 / −8 / −11 / −13 | +12 / +7 |
| 2.0 m | 19.6 pF | +7 / −1 / −3 / −6 | +19 / +14 |

A 1 m whip with a 0.8 nV/√Hz (BF862-class) buffer gets +3.5 dB at 7 MHz quiet rural. At quiet sites above ≈ 10 MHz the galactic floor helps by a few dB. Conclusions:
- **Mini-whips are for noisy sites:** a 10 cm whip is 20–40 dB under the noise floor at a quiet rural one.
- **In town, ≈ 1 m is enough** to be externally limited at HF.
- **A buffer limited by its own noise** raises the floor without improving SNR. A pre-registered "1 m is externally limited by 10 dB even at a quiet site" failed (−7.9 dB).

**Active (broadband) loop — low-impedance amplifier.** The loop's open-circuit external noise is $\sqrt{4kT_aR_r}$. Its reactance ωL dominates, so a transimpedance (current) amplifier compares that voltage with its own $e_n$. A tuned and matched loop is different: its loss noise matters only through the efficiency, $\Delta SNR=10\log[(\eta T_a+(1-\eta)T_0+T_{rx})/(\eta T_a)]$. NEC-free estimate (§3) for a 1 m, 10 mm copper loop, with T_a = man-made + galactic:

| f | R_r | R_loss | η | Tuned-loop penalty (quiet rural / residential) | Broadband loop, 1 nV/√Hz amplifier: margin |
|---|---|---|---|---|---|
| 1 MHz | 2.4 µΩ | 26 mΩ | −40 dB | 0.24 / 0.01 dB | −18 / −2 dB |
| 3.5 | 0.36 mΩ | 49 mΩ | −21 dB | 0.08 / 0.00 | −11 / +5 |
| 7 | 5.7 mΩ | 69 mΩ | −11 dB | 0.04 / 0.00 | −6 / +9 |
| 14 | 91 mΩ | 98 mΩ | −3 dB | 0.03 / 0.00 | −1.5 / +12.5 |

The loop's own copper loss costs almost nothing: even at −40 dB efficiency, the external noise exceeds T₀ by 40+ dB. My pre-registered expectation that it would cost > 3 dB at 28 MHz was wrong (0.3 dB). The **amplifier** sets the floor of an untuned active loop at quiet sites, which is why good commercial loops (Wellbrook-class) use very low-noise push-pull amplifiers and larger loops. The galactic term is included at all f in this table; below ≈ 10 MHz that overstates T_a in daytime, but atmospheric noise usually takes its place at night.

**Why cheap active loops misbehave** (MLA-30-class; user reports and one teardown — anecdotal [9]):
- **Overload and intermodulation.** A broadband amplifier with modest IIP3 sees every broadcast station at once. Reviewers report MF/SW stations "obliterated by IMD" when switching from a better loop. The fix is a band-pass or high-pass filter at the amplifier input, lower gain, or a higher-IIP3 amplifier ([intermodulation](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
- **Supply noise and hum.** The supplied bias-tee and DC-DC converter inject switching noise. Owners lowered the noise floor by ≈ 10–20 dB with a linear 12 V supply and a better bias-tee. Hum or 100 Hz modulation on signals usually means ripple on the bias supply, or rectification in an overloaded stage, or a mains ground loop through the feeder.
- **Feeder common-mode noise.** The loop amplifier's ground and the coax shield are part of the antenna's "other side", especially for whips. House noise conducted along the outside of the shield then appears as signal. Put a CM choke at the antenna and another where the coax enters the building, and ground the shield to a rod at the mast foot ([baluns](antenna-matching-and-baluns.md#where-to-put-chokes-a-placement-rule-from-nec)).
- **Location matters most.** Mount the loop or whip high and away from the house wiring. Its advantage over a wire is only that it is small enough to put where the noise is low. See also [receive-only SDR antennas](multiband-and-wideband-antennas.md#receive-only-sdr-antennas-does-length-matter) and the Beverage/RDF discussion on the [HF wire page](wire-antennas-hf-random-wire-fan-dipole.md#receive-only-wires-beverage-rdf-and-stealth-long-wires).

**Sense antenna: making a loop directional one way.** A small loop's open-circuit voltage is ∝ cos φ (a figure-8) and is in quadrature with the field. A whip's voltage is omnidirectional and in phase with the field. Shift the loop by 90° and add equal amplitudes: the sum is ∝ 1 + cos φ, a **cardioid** with a single null behind. Classic RDF uses it to resolve the loop's 180° ambiguity. Errors fill the null (§5): a 10 % amplitude error leaves 26 dB front/back, a 10° phase error 21 dB, and 20 % with 20° together 14 dB. Sense first, with the cardioid, then take bearings on the sharp loop nulls.

**LF/VLF time-signal reception.** Time stations at 40–77.5 kHz use ground-wave and, at night, ionospheric paths; the receive antenna is a tuned ferrite rod (small loop). At LF the external (atmospheric) noise is enormous, so rod efficiency is irrelevant; Q and the null orientation are what matter, as for example 4 above. The stations [10]:
- DCF77 77.5 kHz, Mainflingen, 50 kW (≈ 30 kW ERP)
- MSF 60 kHz, Anthorn, 15 kW ERP
- WWVB 60 kHz, Fort Collins, 50–70 kW ERP (sources differ)
- JJY 40 kHz (Otakadoya) and 60 kHz (Hagane-yama)
- BPC 68.5 kHz, Shangqiu

From Singapore the nearest are BPC (≈ 3900 km) and JJY 60 kHz (≈ 4500 km). Reception there is a night-time, sky-wave affair at best, and radio-controlled clocks set for Europe or the USA will not work. For time on a flight computer or ground station use GNSS 1 PPS instead ([GNSS timing](../21-gnss/gnss-timing-1pps.md)). This is a design judgement, not measured.

## Design equations & rules of thumb

| Item | Value / rule |
|---|---|
| Small-loop regime | C < 0.1λ (MoM: formula within 5 % below 0.07λ) |
| R_r scaling | ∝ D⁴f⁴N²μ_eff² |
| Loss scaling | ∝ D·√f / d_wire |
| Efficiency improves with | larger D (strongly), fatter conductor, fewer joints, low-ESR (vacuum/air) capacitor |
| STL practical range | ≈ λ/10 > C > λ/30; below that efficiency collapses |
| STL bandwidth | f/Q, a few kHz at HF |
| Full-wave loop | resonant at C ≈ 1.03–1.05λ, 100–140 Ω, 3.1–3.6 dBi |
| Loop pattern | small: null on axis; full-wave: maximum on axis |
| External noise field | E_n = Fa + 20 log f_MHz + B − 95.5 dB(µV/m) | P.372, short monopole over ground |
| Active whip margin | 20 log[E_n (h/2) C_a/(C_a+C_in)/e_n] | 1 m: +12 dB residential, −8 dB quiet rural @ 7 MHz |
| Loop + sense whip | 1 + cos φ cardioid; 10 % / 10° error → 26 / 21 dB F/B | — |

## Worked examples

**Example 1 — PCB loop at 433 MHz (key-fob style).** A 30 × 20 mm rectangular trace loop (A = 6×10⁻⁴ m², C = 0.10 m = 0.144λ), 1 mm trace width (equivalent round radius ≈ 0.25 mm). R_r = 31 171·(6×10⁻⁴/0.4794)² = 0.049 Ω. Loss: R_s = 5.43 mΩ; a trace of width w and length C has R ≈ C·R_s/(2w) ≈ 0.10·0.00543/0.002 ≈ 0.27 Ω plus the tuning capacitor ESR (~0.1–0.3 Ω for a good C0G at 433 MHz). η ≈ 0.049/(0.049 + 0.27 + 0.2) ≈ **9 % (−10 dB)** (C = 0.144λ is already past the small-loop regime, so the true R_r is ≈ 25 % higher per our MoM trend — ≈ 11 %; current crowding at the trace edges raises the loss — the conclusion stands). That is why key fobs work to tens of metres only, and why a flight computer should not use a PCB loop for telemetry.

**Example 2 — Small transmitting loop for 14 MHz.** 1.0 m diameter, 22 mm copper tube: R_r = 0.097 Ω, R_loss = 0.045 Ω → η ≈ 68 % (−1.6 dB) before capacitor and joint losses; L ≈ 2.45 µH → X_L = 218 Ω; loaded Q ≈ 1540; BW ≈ 9.2 kHz. At 100 W: V_C ≈ √(2·100·1540·218) ≈ **8.2 kV peak** — use a vacuum-variable or a wide-spaced air capacitor, and treat it as a high-voltage hazard (RF burns). At 7.1 MHz the same loop is ≈ 16 % efficient.

**Example 3 — Full-wave loop for 915 MHz.** C = 1.05λ = 344 mm (D ≈ 110 mm), 1.5 mm wire: Z ≈ 130–140 Ω (quarter-wave 75 Ω matching section: √(50·137) ≈ 83 Ω; 75 Ω coax gives VSWR ≈ 1.2), D ≈ 3.5 dBi along the axis. Two such loops make a 2-element quad (≈ 7 dBi).

**Example 4 — AM ferrite-rod receive antenna.** 1 MHz, rod 10 mm × 100 mm (μ_eff ≈ 100), 50 turns: R_r ≈ 6×10⁻⁷ Ω, but the effective height h_e = 2π·50·7.85×10⁻⁵·100/300 = 8.2 mm — a 1 mV/m broadcast signal gives ≈ 8 µV open-circuit, multiplied by the tuned circuit's Q (≈ 100) at the receiver input. Signal and atmospheric noise are both collected; the receiver works.

## Practical notes
- **Loops for direction finding**: the sharp axial null (tens of dB) is used for RDF. For recovering a rocket transmitting at 433 MHz, a small 3-element Yagi (front lobe) plus attenuator is easier to use than a loop null at UHF; loops are the classic choice at HF/LF.
- **Shielded loops** (coax-built loop with a gap in the shield at the top) balance the loop and suppress the electric-field (dipole-mode) pickup of an unbalanced loop; they do not "reject electric fields" in the far field (far-field E and H are inseparable) — they reduce common-mode and near-field capacitive coupling.
- **Feed**: small loops are low-impedance; couple with a smaller "Faraday" coupling loop (≈ 1/5 the diameter) or a gamma match; tune with a series/parallel capacitor.
- **Near-field sensitivity**: small loops couple to nearby metal via their magnetic near field (eddy currents); keep ≥ one diameter from metal.
- **Safety**: tuned small loops concentrate RF current and voltage; observe RF exposure distances ([RF exposure](../19-regulations-safety/rf-exposure-safety.md)).

## Common mistakes & misconceptions
- **"Magnetic loops are 'magnetic antennas' that radiate a different kind of wave."** Far away the wave is an ordinary EM wave; the loop just has a magnetic-dominated near field.
- **"A small loop is less affected by ground/noise because it receives the magnetic field."** In the far field |E| = η|H|; a loop receives the same wave. Balanced/shielded loops *can* reduce local common-mode noise pickup, which is a real but different effect.
- **"R_r = 20π²(C/λ)⁴ holds for any loop."** Only for C ≲ λ/10; our MoM shows the formula is 24 % low at 0.136λ and 2× low at 0.23λ.
- **"More turns always help a transmitting loop."** N turns raise R_r by N² but loss by ~N (more with proximity effect) and push the self-resonance down; single-turn STLs are usually best.
- **"A mini-whip is as good as a big antenna anywhere."** Only where man-made noise is high. At a quiet site a 10–25 cm whip with a 3 nV/√Hz buffer is 20–40 dB below the sky noise at HF.
- **"My active loop's noise floor is the band noise."** Check: disconnect the loop element (or terminate the amplifier input). If the floor barely drops, you are hearing the amplifier, its power supply or feeder CM noise.
- **"An inefficient receive loop loses SNR."** Not when external noise dominates: a 1 m loop at −40 dB efficiency loses < 0.3 dB of SNR (tuned).
- **"A full-wave loop is just a big small loop."** Its pattern maximum is on the axis, the opposite of a small loop.

## How to simulate / verify
- `python3 tools/verify/ant_small_limits.py` — R_r, loss, efficiency, inductance, Q, bandwidth for small loops; ferrite rod numbers.
- `python3 tools/verify/ant_mom_general.py` (`small_loop()`) — MoM loop impedance and pattern; use it to see where the small-loop formula breaks and to model full-wave loops.
- `python3 tools/verify/s12_rx_antennas.py` (≈ 1 min): P.372 tables and the −95.5/−99.0 constants re-derived; active whip and active loop noise margins; Beverage RDF (NEC); sense cardioid errors.
- NEC-2: loops need ≥ 12–36 segments; very small loops (C < 0.01λ) and very short segments (Δ < 10⁻³λ) are numerically inaccurate in NEC-2 ([simulation](antenna-simulation-nec-openems.md)).
- Measure small-loop efficiency with a Wheeler cap ([antenna measurement](antenna-measurement.md)).

## Open questions / gaps
- Proximity-effect factor for multi-turn loops (Smith 1972 / Butterworth) not quantified here.
- The active-antenna margins assume ideal buffers (fixed e_n, no current noise, no input filter) and P.372 medians; real sites vary by ± 10 dB. A local noise survey (GAP_REGISTER R13) settles it.
- Ferrite rod μ_eff vs length/diameter curve should be sourced from a ferrite manufacturer (Fair-Rite rod data) — domain 04.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — ch. 5 (loop antennas: small loop fields, R_r = 20π²(C/λ)⁴, ferrite-loaded loops, circular loops of arbitrary size). (textbook)
2. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — ch. 7 (loop antennas, effective height, directivity). (textbook)
3. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, 2016 — ch. 17 "Linear and Loop Antennas" (§17.8–17.10 loop, circular and square loops). [chapter numbers checked against the 2016 edition's table of contents, W5-S18 2026-10-13; the 2010 edition numbers ch. 11–18 one lower, with Aperture Antennas as ch. 18 and Currents on Linear Antennas as ch. 21]. https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook)
4. ARRL, *The ARRL Antenna Book*, 24th ed. — small transmitting loops, quad loops. (handbook)
5. ITU-R Recommendation P.372, *Radio noise* — external noise levels vs frequency (why inefficient receive loops work at MF/HF). (standard; cited, not read in this pass)
6. This repository: `tools/verify/ant_small_limits.py`, `tools/verify/ant_mom_general.py`, `tools/verify/s12_rx_antennas.py`. (verification)
7. ITU-R Recommendation P.372-6 (1994) and later revisions, *Radio noise* — Fa lines (Table 1 constants via the ITU/IEEE 802.18-12-0057 PLT table), E_n = Fa + 20 log f + B − 95.5 (monopole) / −99.0 (dipole). https://itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.372-6-199408-S!!PDF-E.pdf (standard; formula verified by search excerpt and by derivation)
8. FFI report 16/00869, *External man-made radio noise measurements* (Norway, 2013–14) — measured residential/rural noise below the P.372 lines. https://www.ffi.no/no/Rapporter/16-00869.pdf (government report; abstract level)
9. MLA-30 user reports: D. Day (N1DAY) comparison review (swling.com, 2019; IMD vs Wellbrook ALA1530); EEVblog forum thread "MLA-30 active loop antenna" (bias-tee/DC-DC noise, linear supply fix); G8JNJ teardown summarised at rtl-sdr.com (input-filter mismatch). (forum/review — anecdotal)
10. M. Kuhn, "Low-frequency radio time signals," Univ. of Cambridge, https://www.cl.cam.ac.uk/~mgk25/time/lf-clocks/ — station frequencies, powers and locations (expert list; WWVB power differs from NIST's commonly quoted 70 kW ERP).
