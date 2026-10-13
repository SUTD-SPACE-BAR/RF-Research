---
title: Friis transmission equation and free-space path loss
domain: 09-propagation-link-budget
slug: friis-free-space-path-loss
tags: [friis, free-space-path-loss, FSPL, effective-aperture, EIRP, ERP, power-flux-density, field-strength, far-field, ITU-R-P.525]
prerequisites: [../00-math-foundations/decibels-and-log-units.md, ../08-antennas/antenna-fundamentals.md, ../02-electromagnetics/poynting-vector-power-flow.md]
related: [link-budget-methodology.md, fresnel-zones-los-radio-horizon.md, two-ray-ground-reflection.md, polarization-mismatch-loss.md, ../02-electromagnetics/near-field-far-field.md, ../11-radar/radar-range-equation.md, ../08-antennas/yagi-uda-and-log-periodic.md]
level: mixed
confidence: high
last_updated: 2026-09-29
---

# Friis transmission equation and free-space path loss

## Questions this page answers
- How much power does a receiving antenna collect from a transmitter a known distance away?
- Where does the free-space path loss formula come from, and what are the constants 32.45, 92.45 and −147.55?
- Do higher frequencies really "attenuate more" in free space?
- Is 433 MHz or 915 MHz better for range, all else equal?
- What are EIRP and ERP, and how do they convert?
- How do I convert between received power, power flux density and field strength (dBµV/m)?
- When is the Friis equation not valid (near field, ground, obstructions)?

## TL;DR
- **Friis (1946):** $P_r = P_t\,G_t\,G_r\left(\dfrac{\lambda}{4\pi d}\right)^2$, or in dB $P_r = P_t + G_t + G_r - L_\text{FS}$ with **$L_\text{FS} = 20\log_{10}(4\pi d/\lambda)$**.
- Practical forms: $L_\text{FS} = 32.45 + 20\log_{10}f_\text{MHz} + 20\log_{10}d_\text{km}$ dB (ITU-R P.525 writes 32.4); = $92.45 + 20\log f_\text{GHz} + 20\log d_\text{km}$; = $-147.55 + 20\log f_\text{Hz} + 20\log d_\text{m}$; = $-27.55 + 20\log f_\text{MHz} + 20\log d_\text{m}$ (`tools/verify/prop_fspl.py`).
- **Numbers for Marcus:** at 30 km, 433.125 MHz → **114.7 dB**; 915 MHz → **121.2 dB**; GPS L1 → 125.9 dB. Each doubling of distance adds 6.02 dB.
- **Myth-buster:** space does not absorb high frequencies. The $f^2$ in FSPL is the shrinking **effective aperture** of an antenna of fixed *gain* ($A_e = G\lambda^2/4\pi$). With a fixed-size receive aperture, received power is frequency-independent; with fixed apertures at both ends it *rises* as $f^2$ (+6.5 dB going 433 → 915 MHz).
- For equal antenna **gains** (e.g. dipole-to-dipole, or omni on the rocket), 433 MHz has a 6.5 dB path advantage over 915 MHz; the E22's 3 dB extra power widens it to 9.5 dB vs the E220.
- **EIRP** = $P_t - L_\text{feed} + G_t$ (dBm, dBi); **ERP** = EIRP − 2.15 dB (dipole reference). Flux density $S = \text{EIRP}/4\pi d^2$; field $E = \sqrt{30\,\text{EIRP}}/d$: 33 dBm EIRP at 30 km gives −67.5 dBm/m² and 48.2 dBµV/m.
- Valid only in the **far field** ($d \gtrsim 2D^2/\lambda$), with a clear first Fresnel zone and no ground reflection. Near the ground the loss is higher (two-ray, 40 dB/decade); see [two-ray-ground-reflection](two-ray-ground-reflection.md).

## Intuition (no math)
A transmitter's power spreads out over the surface of an ever-growing sphere. At distance $d$ the sphere's area is $4\pi d^2$, so the power per square metre falls as $1/d^2$ — the inverse-square law. Nothing is absorbed; it is just spread thinner. A directional transmitting antenna concentrates the power into part of the sphere (gain $G_t$), multiplying the flux density in that direction.

The receiving antenna acts like a net of a certain *area* (its effective aperture $A_e$) catching some of that flux. Here is the subtle part: an antenna of a given **gain** has an effective area proportional to the wavelength squared. A half-wave dipole at 433 MHz is 35 cm long and catches flux over an area of ≈ 0.063 m²; a 915 MHz dipole is half the size and catches a quarter of the area. So with two dipoles, the higher frequency link receives less power — not because space ate it, but because the higher-frequency antenna is a smaller net. If instead you keep the antenna **size** fixed (a dish or a Yagi of fixed boom length), its gain rises with frequency and it catches the same area: then frequency does not matter at the receiver, and if both ends have fixed-size antennas, higher frequency *wins*.

That is why satellites and radars use high frequencies with dishes, while small handheld and rocket radios, stuck with small, low-gain antennas on at least one end, prefer lower frequencies.

## The math

### Level 1 — the formulas
Symbols: $P_t$ transmit power (W) delivered to the antenna; $G_t, G_r$ antenna gains (linear, relative to isotropic) in the direction of the other antenna; $\lambda = c/f$ wavelength (m); $d$ separation (m); $A_{e}$ effective aperture (m²).
- Power flux density at the receiver: $S = \dfrac{P_tG_t}{4\pi d^2}$ W/m².
- Received power: $P_r = S\,A_{er}$ with $A_{er} = \dfrac{G_r\lambda^2}{4\pi}$.
- Hence **Friis**: $P_r = P_tG_tG_r\left(\dfrac{\lambda}{4\pi d}\right)^2 = \dfrac{P_tA_{et}A_{er}}{\lambda^2d^2}$.
- **Free-space (basic transmission) loss between isotropic antennas**: $L_\text{FS} = \left(\dfrac{4\pi d}{\lambda}\right)^2$, $L_\text{FS,dB} = 20\log_{10}\dfrac{4\pi df}{c}$.
- dB constants (from $20\log_{10}(4\pi/c)$ with unit scalings): **32.45** (MHz, km), 92.45 (GHz, km), −147.55 (Hz, m), −27.55 (MHz, m), 36.58 (MHz, statute miles). ITU-R P.525 rounds to 32.4 [2].

### Level 2 — derivation of the effective aperture $A_e = G\lambda^2/4\pi$
The aperture–gain relation is what turns an inverse-square law into the Friis equation. It follows from reciprocity plus thermodynamics:
1. Put a matched antenna inside a black-body enclosure at temperature $T$. The antenna's terminals then deliver $kTB$ into a matched resistor (it is in equilibrium — see [07-noise-linearity/thermal-noise-and-noise-temperature](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).
2. The power it receives from black-body radiation, in one polarisation, is $\tfrac12\oint A_e(\Omega)B_f\,d\Omega$ with Rayleigh–Jeans spectral brightness $B_f = 2kT/\lambda^2$ per unit bandwidth per steradian. So $kTB = \tfrac{kTB}{\lambda^2}\oint A_e(\Omega)d\Omega$, giving $\oint A_e\,d\Omega = \lambda^2$.
3. Directivity is defined so that $\oint D\,d\Omega = 4\pi$. By reciprocity the receiving and transmitting patterns have the same shape, $A_e(\Omega) \propto D(\Omega)$. Combining: $A_e(\Omega) = \dfrac{\lambda^2}{4\pi}D(\Omega)$ (and with ohmic efficiency $\eta$, $A_e = G\lambda^2/4\pi$).
The derivation also shows that an **isotropic** antenna has $A_e = \lambda^2/4\pi$: 381 cm² at 433 MHz, 85 cm² at 915 MHz, 28.8 cm² at GPS L1 (script).

### Level 3 — generalisations and limits of validity
- **Full Friis with mismatch and polarisation:** $P_r = P_tG_t(\theta_t,\phi_t)G_r(\theta_r,\phi_r)\left(\frac{\lambda}{4\pi d}\right)^2(1-|\Gamma_t|^2)(1-|\Gamma_r|^2)\,|\hat{\rho}_t\cdot\hat{\rho}_r^*|^2$ — the last factor is the polarisation loss factor ([polarization-mismatch-loss](polarization-mismatch-loss.md)).
- **Far-field condition.** The derivation assumes each antenna is in the other's far field: $d \gtrsim 2D^2/\lambda$ (and $d \gg \lambda$, $d \gg D$), where $D$ is the largest antenna dimension. A 2.5 m 433 MHz Yagi has $2D^2/\lambda$ ≈ 18 m; a 1.2 m dish at 10 GHz ≈ 96 m (script). Closer than this, gain is not yet fully formed ([02-electromagnetics/near-field-far-field](../02-electromagnetics/near-field-far-field.md)).
- **Free space means:** no ground reflection, no obstacles in the first Fresnel zone ([fresnel-zones-los-radio-horizon](fresnel-zones-los-radio-horizon.md)), no absorbing medium ([atmospheric-rain-attenuation](atmospheric-rain-attenuation.md)), no refraction/ducting. For an elevated rocket seen from a ground station at moderate elevation these are all good approximations; for a rocket on the ground they are all wrong.
- **Wideband signals:** $\lambda$ varies across the band; for an ultra-wideband link FSPL is evaluated per frequency (the "path loss" of a pulse depends on the antennas' frequency dependence). Irrelevant for LoRa (125 kHz at 433 MHz).
- **Relation to the radar equation:** a radar path is two Friis links joined by a scatterer (target RCS $\sigma$): $P_r = \frac{P_tG_tG_r\lambda^2\sigma}{(4\pi)^3d^4}$ — see [11-radar/radar-range-equation](../11-radar/radar-range-equation.md).
- **Field-strength forms:** $E_\text{rms} = \sqrt{\eta_0 S} = \sqrt{30\,\text{EIRP}}/d$ (V/m, W, m), using $\eta_0 = 120\pi$ Ω. In dB: $E\,[\text{dB}\mu\text{V/m}] = \text{EIRP}\,[\text{dBm}] - 20\log_{10}d_\text{km} + 44.77$ (check: 33 dBm at 30 km → 48.2 dBµV/m, as the script computes from $\sqrt{\eta_0S}$). Regulatory limits are often given as field strength at a distance.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $L_\text{FS} = 32.45 + 20\log f_\text{MHz} + 20\log d_\text{km}$ | far field, free space | 433 MHz: 85.2 (1 km), 105.2 (10 km), 114.7 (30 km), 119.2 (50 km) dB |
| same | | 915 MHz: 91.7 / 111.7 / 121.2 / 125.7 dB |
| $+6.02$ dB per doubling of $d$; +20 dB per decade | free space | |
| $A_e = G\lambda^2/4\pi$ | any antenna | 0 dBi at 433 MHz: 381 cm² |
| EIRP = $P_t - L_f + G_t$; ERP = EIRP − 2.15 | | E22 + 0 dBi antenna: ≈ 32.5 dBm EIRP |
| $S = \text{EIRP} - 10\log(4\pi d^2)$ | | 33 dBm, 30 km: −67.5 dBm/m² |
| $E = \text{EIRP}_\text{dBm} - 20\log d_\text{km} + 44.77$ dBµV/m | | 33 dBm, 30 km: 48.2 dBµV/m |
| $d_\text{ff} = 2D^2/\lambda$ | antenna far field | 2.5 m Yagi at 433 MHz: 18 m |

FSPL table (dB), from `prop_fspl.py`:

| d | 433.1 MHz | 868 MHz | 915 MHz | 1575.4 MHz | 2450 MHz | 5800 MHz | 24 GHz | 77 GHz |
|---|---|---|---|---|---|---|---|---|
| 100 m | 65.2 | 71.2 | 71.7 | 76.4 | 80.2 | 87.7 | 100.1 | 110.2 |
| 1 km | 85.2 | 91.2 | 91.7 | 96.4 | 100.2 | 107.7 | 120.1 | 130.2 |
| 5 km | 99.2 | 105.2 | 105.7 | 110.4 | 114.2 | 121.7 | 134.0 | 144.2 |
| 10 km | 105.2 | 111.2 | 111.7 | 116.4 | 120.2 | 127.7 | 140.1 | 150.2 |
| 30 km | 114.7 | 120.8 | 121.2 | 125.9 | 129.8 | 137.3 | 149.6 | 159.7 |
| 50 km | 119.2 | 125.2 | 125.7 | 130.4 | 134.2 | 141.7 | 154.0 | 164.2 |
| 100 km | 125.2 | 131.2 | 131.7 | 136.4 | 140.2 | 147.7 | 160.1 | 170.2 |

## Worked examples
**1 — Received power from the rocket at 30 km (433 MHz).** $P_t$ = 33 dBm (E22-400T33D), rocket feeder 0.5 dB, rocket antenna 0 dBi toward the ground station, ground Yagi 11 dBi: $P_r = 33 - 0.5 + 0 + 11 - 114.7 = -71.2$ dBm before polarisation, pointing and feeder losses. The full budget (−75.8 dBm with 3 dB polarisation, 1 dB pointing, 0.45 dB feeder, 0.1 dB gases) is in [link-budget-methodology](link-budget-methodology.md). *Licence note:* 33 dBm at 433 MHz is the licensed (amateur/permit) case in Singapore; at the licence-exempt 10 mW e.r.p. (12.15 dBm EIRP) the same geometry gives $P_r$ ≈ −91.6 dBm ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)).

**2 — 433 vs 915 MHz, fair comparison.** Same antennas by **gain** (0 dBi rocket, 11–12 dBi Yagi): FSPL difference 6.5 dB in favour of 433 MHz; the E22 transmits 3 dB more than the E220 → 433 MHz link ≈ 9.5 dB stronger. Same antennas by **size** (a Yagi of fixed boom length has ~6.5 dB more gain at 915 MHz): the ground-side advantage cancels the FSPL difference, leaving the rocket end (where the antenna size is constrained by the airframe and a dipole is ~0 dBi at either frequency) to decide. For a rocket-to-ground link the 433 MHz choice is sound; ground-station Yagis at 915 MHz are smaller for the same gain.

**3 — The frequency myth in numbers (script §3).** Going from 433 to 915 MHz at 30 km with a 1 W transmitter: isotropic antennas at both ends: −6.50 dB; isotropic Tx and a fixed 0.5 m² receive aperture: +0.00 dB; fixed apertures at both ends (0.1 m² and 0.5 m²): **+6.50 dB**. A 0.5 m² aperture is 11.2 dBi at 433 MHz and 17.7 dBi at 915 MHz.

**4 — Sanity check against a record.** The 832 km LoRaWAN balloon record used 25 mW (14 dBm) at 868 MHz from 38 km altitude [4]. FSPL = 149.6 dB; with a 0 dBi balloon antenna and a 2–8 dBi gateway antenna, $P_r$ = −133.6 to −127.6 dBm, versus ≈ −137 dBm for SF12/BW125: a 3–9 dB margin. Free-space Friis plus a datasheet sensitivity predicts that the record is *just possible* — reassuring evidence that elevated LoRa links behave as free space (spreading factor was not stated in the report; SF12 assumed).

**5 — Field strength for an EMC/regulatory check.** 30 dBm EIRP at 3 m: $E = 30 - 20\log_{10}(0.003) + 44.77 = 125.2$ dBµV/m (= $\sqrt{30\cdot1}/3$ = 1.8 V/m) — relevant to susceptibility of the flight computer's own electronics near its 1–2 W antenna (see [19-regulations-safety/rf-exposure-safety](../19-regulations-safety/rf-exposure-safety.md) and [13-pcb-rf-layout-emc/emc-emi-fundamentals](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)). (3 m is near the edge of the far field for small antennas; indicative only.)

## Practical notes
- **Gain is directional.** Use the gain *toward the other antenna*, not the peak gain. A rocket dipole has 2.15 dBi broadside but a deep null along its axis; a ground Yagi loses gain off boresight (pointing loss).
- **Use dBi consistently.** Datasheets quoting dBd are 2.15 dB lower than dBi for the same antenna; mixing them up is a common 2 dB error.
- **EIRP limits** in ISM bands are regulatory (see [19-regulations-safety/spectrum-allocation-ism-bands](../19-regulations-safety/spectrum-allocation-ism-bands.md) and [singapore-imda-rules](../19-regulations-safety/singapore-imda-rules.md)); a 2 W module on a gain antenna may exceed an ERP/EIRP limit even if the module itself is "legal".
- **Mismatch** $(1-|\Gamma|^2)$ at each end: VSWR 2 costs 0.51 dB; VSWR 3 costs 1.25 dB ([03-transmission-lines-matching/reflections-vswr-return-loss-mismatch](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)).

## Common mistakes & misconceptions
- **"High frequencies attenuate faster in free space."** The $f^2$ term belongs to antennas of fixed gain; space itself is lossless and dispersionless. Real frequency-dependent *attenuation* (dB/km) comes from gases, rain, foliage and buildings, and is tiny at 433/915 MHz ([atmospheric-rain-attenuation](atmospheric-rain-attenuation.md)).
- **Using 32.45 with d in metres or f in GHz.** Keep units matched to the constant.
- **Applying Friis to a link near the ground.** Two ground-level antennas beyond the breakpoint distance see ~40 dB/decade, not 20 — FSPL underestimates loss by tens of dB ([two-ray-ground-reflection](two-ray-ground-reflection.md)).
- **Adding the gains of both antennas "as if pointed" when neither is.** Pattern values toward each other, polarisation, mismatch and cable loss are all separate budget lines.
- **Confusing EIRP and ERP** (2.15 dB).
- **Forum myth: "LoRa range scales with SF, so any SF12 link reaches 15 km."** Range is a link-budget outcome: SF buys sensitivity (≈ 2.5 dB/step), which in free space buys range as $10^{\Delta/20}$ (×1.33 per step), but on the ground the loss grows as $d^4$ or faster, so each SF step buys only ×1.15 in range.

## How to simulate / verify
- `tools/verify/prop_fspl.py` — dB constants, FSPL table, the aperture argument (three cases), flux density/field strength, ERP/EIRP, far-field distances, balloon-record sanity check.
- `tools/verify/prop_link_budget.py` — the `Link` class uses the same FSPL function.
- Antenna-to-antenna coupling at short range (near field) should be simulated with an EM solver (openEMS, NEC) rather than Friis ([08-antennas/antenna-simulation-nec-openems](../08-antennas/antenna-simulation-nec-openems.md)).
- Field test: measure RSSI vs distance on a clear elevated path (e.g. hilltop to hilltop, or drone-lifted transmitter) and fit $P_r = A - 20n\log d$; $n \approx 1$ confirms free space.

## Open questions / gaps
- Record-attempt reports rarely give SF, antenna gains and RSSI; a better-documented long-range LoRa experiment would tighten the sanity check.

## Sources
1. H. T. Friis, "A note on a simple transmission formula," *Proc. IRE* 34(5), 254–256 (1946). (peer-reviewed) — the transmission formula in aperture form.
2. ITU-R Recommendation P.525-5 (11/2024), *Calculation of free-space attenuation*: $L_{bf} = 32.4 + 20\log f + 20\log d$ (MHz, km), point-to-point and point-to-area forms. https://www.itu.int/rec/R-REC-P.525/en (standard)
3. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley 2016, §2.14–2.18 (effective aperture, Friis equation, polarisation, radar equation). (textbook)
4. The Things Network, "LoRa world record broken: 832 km / 517 mi using 25 mW" (2020) and "LoRaWAN packet received at 702 km" (2017). https://www.thethingsnetwork.org/article/lorawan-world-record-broken-twice-in-single-experiment-1 (news — anecdotal; SF and antenna details not stated)
5. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §14.2 (Friis formula, EIRP, antenna noise temperature). (textbook)
6. J. D. Kraus, R. J. Marhefka, *Antennas for All Applications*, 3rd ed., McGraw-Hill 2002, ch. 2 (aperture–directivity relation from thermodynamics). (textbook)
7. `tools/verify/prop_fspl.py` (this KB).
