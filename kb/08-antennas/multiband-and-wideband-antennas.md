---
title: Multiband and wideband antennas — biconical, discone, bow-tie, Vivaldi/tapered slot, spirals, LPDA, sleeve monopoles, traps and parasitics, wideband SDR receive antennas
domain: 08-antennas
slug: multiband-and-wideband-antennas
tags: [wideband, ultra-wideband, uwb, multiband, biconical, monocone, discone, bow-tie, vivaldi, tapered-slot, spiral, frequency-independent, self-complementary, mushiake, rumsey, lpda, sleeve-monopole, traps, parasitic, sdr, scanner, noise-limited]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, slot-antennas.md, small-antenna-limits.md]
related: [yagi-uda-and-log-periodic.md, wire-antennas-hf-random-wire-fan-dipole.md, helical-antennas.md, horn-reflector-aperture-antennas.md, pcb-and-chip-antennas.md, ../03-transmission-lines-matching/broadband-matching-bode-fano.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../14-sdr-dsp/sdr-hardware-survey.md, ../17-test-measurement/sdr-as-test-equipment.md, ../11-radar/diy-radar-hardware.md]
level: mixed
confidence: medium
last_updated: 2026-10-02
---

# Multiband and wideband antennas

## Questions this page answers
- What makes an antenna wideband, and what is a "frequency-independent" antenna?
- What is the difference between a multiband antenna and a wideband one?
- How does a discone work, how do I dimension one, and is it really 25–1300 MHz?
- Why does my discone receive well at some frequencies and poorly at others?
- What impedance does a biconical or bow-tie antenna have, and why are self-complementary antennas 188 Ω?
- How does a Vivaldi (tapered-slot) antenna work, and how big must it be for 1–10 GHz?
- What sets the band of a spiral antenna?
- When should I use an LPDA instead of a discone or a Yagi?
- How do traps, parallel elements and parasitic resonators make an antenna multiband?
- For receive-only SDR, does antenna length or efficiency matter?
- What is a good wideband antenna for an RTL-SDR?
- Can I use one antenna for 433 MHz and 915 MHz?

## TL;DR
- **Wide bandwidth needs either a smooth, scale-free geometry** (cones, bow-ties, spirals, tapered slots, log-periodic structures: Rumsey's principle — if a structure is defined only by angles it looks the same at every frequency) **or loss** (resistive loading, "wideband" cheap antennas that are really attenuators). Check efficiency, not just VSWR.
- **Conical antennas**: an infinite cone pair is a transmission line of $Z_0=120\ln\cot(\theta/2)$ Ω (bicone), $60\ln\cot(\theta/2)$ (monocone over ground); **50 Ω monocone at θ = 47°** (verified, `tools/verify/ant2_wideband.py`), 50 Ω bicone at 66.8°. Finite cones are wideband above their first resonance.
- **Discone** (Kandoian 1945): put the first resonance at ≈ 0.7 × the lowest operating frequency, make disc radius + cone slant ≈ λ/2 there, disc/cone ≈ 0.72 sin θ (Nail) [2]. NEC of a 16 + 16-rod discone for a 100 MHz design: **VSWR < 2.5 from 60 to 700 MHz (> 11:1)** — but the **horizon gain swings from +2.9 to −9 dBi** and the beam tilts 20–70° below the horizon above ≈ 150 MHz. A discone is *not* frequency independent [2]; it is a fat, multi-resonant dipole.
- **Self-complementary antennas** (spirals, 90° bow-tie) have $Z=\eta_0/2=188.4\ \Omega$ at all frequencies (Babinet; [slot-antennas](slot-antennas.md)). Infinite planar bow-tie: 188 Ω at 90° flare, 147 Ω at 120°, 109 Ω at 150°, 50 Ω only at 179° (verified: η₀K(k)/K(k′)) — bow-ties are naturally 100–200 Ω and need a balun/taper.
- **Spirals**: circularly polarized, ≈ constant pattern and 188 Ω (free space); band from f_low ≈ c/(πD_out) to f_high ≈ c/(πd_in): a 15 cm spiral with a 1 cm feed region covers ≈ 0.64–9.5 GHz.
- **Vivaldi (Gibson 1979)**: an exponentially flared slot; ≈ 10 dBi end-fire, demonstrated from below 2 to above 40 GHz [6]; lowest frequency set by aperture width ≈ λ₀/2 (≈ 75 mm for 2 GHz in air, 53–61 mm on FR-4).
- **LPDA**: the directional wideband choice (≈ 6–8 dBi over a decade with the right τ, σ) — design on [yagi-uda-and-log-periodic](yagi-uda-and-log-periodic.md#example-5--lpda-for-4001000-mhz-covers-433-and-868915).
- **Multiband tricks** (narrowband on several bands): traps, fan/parallel elements, harmonic resonance (EFHW, λ/4 ↔ 3λ/4), parasitic or coupled resonators, dual-resonance PCB antennas — see [HF wire antennas](wire-antennas-hf-random-wire-fan-dipole.md) for NEC-checked fan and trap dipoles.
- **Receive-only SDR**: at HF, external noise is 20–50 dB above kT₀, so even a −30 dB-efficient wire costs only 0.5 dB SNR (7 MHz, residential); at UHF the sky is cold and the receiver dominates: −3 dB efficiency costs ≈ 2 dB at 433 MHz, 4.5 dB at 915 MHz and 6 dB at GNSS L1 (P.372 noise, `ant2_wideband.py` §4). **"Any wire works" is true at HF and false at UHF.**

## Intuition (no math)
An ordinary dipole is narrowband because it is a resonator: a standing wave fits on it at one frequency, and its stored reactive energy is large compared with what it radiates per cycle (Q ≈ 8–10). Two ways around that:

1. **Make it a gradual transition rather than a resonator.** Open a two-wire line out slowly into a pair of cones, flaring plates or a widening slot. A wave launched at the feed travels outward along the structure, which slowly becomes wide enough to radiate, without a sharp end to reflect from. Each frequency radiates from the part of the structure where it "fits" (where the width or circumference is about half a wavelength) and the rest is just transmission line. That is how bicones, discones, Vivaldis and horns work.
2. **Make the shape scale-free.** If the geometry is defined only by angles (an infinite cone, an infinite bow-tie, an equiangular spiral), then scaling the frequency is the same as scaling the antenna — and a scaled infinite antenna is the same antenna. Truncating it sets the lowest frequency (the biggest part must still be about a wavelength) and the feed region sets the highest (Rumsey [5]).

Multiband antennas are different: they are narrowband at several separated frequencies (e.g., 433 and 915 MHz, or 7 and 14 MHz) and achieve that with resonators — two elements on one feed, a trap that switches part of the element out, or a structure with two resonant modes.

## The math

### Level 1 — formulas and numbers
| Antenna | Key relation | Typical numbers |
|---|---|---|
| Infinite biconical | $Z_0=120\ln\cot(\theta/2)$ Ω (θ = half-angle from axis) | 50 Ω at 66.8°, 100 Ω at 47°, 300 Ω at 9.4° |
| Infinite monocone / discone limit | $Z_0=60\ln\cot(\theta/2)$ | 50 Ω at 47.0°, 79 Ω at 30° |
| Discone sizing (Stearns/Nail [2]) | first resonance f_r ≈ 0.7 f_low; R_disc + L_slant ≈ λ_r/2; R/L ≈ 0.72 sin θ | θ = 25–40° |
| Infinite planar bow-tie | $Z=\eta_0K(k)/K(k')$, $k=\tan^2(\pi/4-\alpha/4)$, α = full flare | 90°: 188 Ω; 150°: 109 Ω |
| Self-complementary | $Z=\eta_0/2$ | 188.4 Ω |
| Spiral band | f_low ≈ c/(πD_out), f_high ≈ c/(πd_in) | 15 cm / 1 cm: 0.64–9.5 GHz |
| Vivaldi | taper $y=\pm\tfrac{w}{2}e^{Rx}$; aperture W ≈ λ_low/2 | W = 75 mm → f_low ≈ 2 GHz (air) |
| LPDA | τ = L_{n+1}/L_n, σ = d/(2L) | τ 0.85–0.95 |
| Receive SNR penalty | $\Delta=10\log\frac{f_a+(l_c-1)+l_c(f_r-1)}{f_a+f_r-1}$ | see table in §SDR |

### Level 2 — derivations
**(a) Biconical transmission line.** Two coaxial cones of half-angle θ with apexes at the origin guide a TEM spherical wave $E_\theta\propto e^{-jkr}/(r\sin\theta)$ (the field must be ∝ 1/sinθ to satisfy ∇·E = 0 in the gap). The voltage between the cones at radius r is $V=\int_\theta^{\pi-\theta}E_\theta r\,d\theta'$ and the current on one cone is $I=2\pi r\sin\theta' H_\phi$ with $H_\phi=E_\theta/\eta_0$. Integrating $\int d\theta'/\sin\theta'=2\ln\cot(\theta/2)$ gives
$$Z_0=\frac{V}{I}=\frac{\eta_0}{\pi}\ln\cot\frac{\theta}{2}\approx 120\ln\cot\frac{\theta}{2}\ \Omega .$$
For one cone over a ground plane (image theory) the voltage halves: $Z_0=60\ln\cot(\theta/2)$; 50 Ω ⇒ θ = 2 arctan e^{−5/6} = 47.0°, the value used for 50 Ω discones and monocones [2]. A *finite* cone is this line terminated by the radiation impedance of its open end (Schelkunoff): the input impedance oscillates around Z₀ with a decreasing swing as frequency rises — the "scalloped" SWR of real discones [2].

**(b) Self-complementary impedance (Mushiake).** For a planar structure and its complement in an infinite sheet, Babinet–Booker gives $Z\,Z_c=\eta_0^2/4$ ([derivation](slot-antennas.md#level-2--derivation-bookers-duality-argument)). If the structure *is* its own complement (rotating it maps metal onto gaps), $Z=Z_c$, hence $Z=\eta_0/2=188.4$ Ω for every frequency. The infinite bow-tie of flare angle α maps to its complement at 180° − α; conformal mapping gives $Z=\eta_0K(k)/K(k')$ with $k=\tan^2(\pi/4-\alpha/4)$, which our script checks satisfies $Z(90°)=188.37$ Ω and $Z(60°)Z(120°)=\eta_0^2/4$.

**(c) Rumsey's angle principle and active regions.** If a structure's shape depends only on angles, its impedance and pattern are frequency independent; real antennas must be truncated, and work if current decays rapidly beyond an "active region" whose size is ~λ (so truncation does not matter) [5]. For a two-arm spiral the active region is the ring where the circumference ≈ λ (adjacent arms' currents come into phase there and radiate a CP wave along the axis), hence f_low ≈ c/(πD_out); the feed region of diameter d_in sets f_high. The same idea gives the LPDA (active region = the dipoles ≈ λ/2 long) and the Vivaldi (active region where the slot width ≈ λ/2).

**(d) Receive-only: when does efficiency matter?** Following ITU-R P.372, refer all noise to the terminals of an equivalent *lossless* antenna. With external noise factor $f_a$, antenna (and feed) loss factor $l_c=1/\eta$ at temperature T₀ and receiver noise factor $f_r$, the system noise factor is
$$f=f_a+(l_c-1)+l_c(f_r-1),$$
while the signal at that reference point is unchanged. So the SNR penalty of an inefficient antenna relative to a lossless one is $\Delta=10\log[f/(f_a+f_r-1)]$. If $f_a\gg l_c f_r$ the loss is invisible (HF); if $f_a\lesssim1$ the loss counts in full (UHF, cold sky). External-noise values from P.372 are tabulated on [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md#external-noise-itu-r-p372).

### Level 3 — limits
- **Bode–Fano and Chu.** A small antenna cannot be made wideband by matching alone; the bandwidth–efficiency–size trade is fundamental ([small-antenna limits](small-antenna-limits.md), [Bode–Fano](../03-transmission-lines-matching/broadband-matching-bode-fano.md)). Wideband antennas are always *large* at their lowest frequency (discone ≈ λ/4 tall, spiral ≈ λ/π across, Vivaldi aperture ≈ λ/2).
- **Pattern bandwidth vs impedance bandwidth.** A discone's VSWR stays low over > 10:1 but its pattern breaks up; an LPDA keeps both over its design band; a spiral keeps its pattern but its polarization degrades outside the band. Specify both.
- **Dispersion.** Frequency-independent antennas whose active region moves with frequency (LPDA, spiral) have a frequency-dependent phase centre → they distort UWB pulses (chirp). Vivaldis, bicones and TEM horns are preferred for impulse/UWB radar.
- **Resistive loading.** Wu–King loaded dipoles and terminated "wideband" antennas buy bandwidth with resistive loss (efficiency often −6 to −20 dB). Acceptable for HF receive (see Level 2d), not for transmitting or UHF receive.

## Antenna-by-antenna notes

### Discone (and why "25–1300 MHz" needs care)
Construction: a disc (or 8–16 radial rods) on top, the coax centre conductor to the disc, the shield to the apex of a cone below; rods ≥ 8 per element [2]. Our NEC design for f_low = 100 MHz (θ = 30°, R/L = 0.36): cone slant 1.575 m, disc radius 0.567 m, cone base 1.58 m across, height 1.38 m (`ant2_wideband.py` §3):
| f (MHz) | 50 | 60 | 70 | 100 | 180 | 300 | 500 | 700 |
|---|---|---|---|---|---|---|---|---|
| VSWR(50) | 4.6 | 2.25 | 1.55 | 1.23 | 2.67 | 1.93 | 1.86 | 2.18 |
| horizon gain (dBi) | — | — | — | +2.9 | — | −9.1 | +1.2 | +1.4 |
| beam peak elevation | — | — | — | −19° | — | −69° | −52° | −44° |
Impedance-wise it covers 60–700 MHz (11.7:1) and would continue higher if the rods were modelled finer; pattern-wise it is a good omni only up to ≈ 1.5 × f_low, after which the main lobe points *down* along the cone and the horizon gain swings by ≈ 12 dB (−9 to +3 dBi across 100–700 MHz). Commercial "25–1300 MHz" receive discones add a loaded whip on top to extend the low end (manufacturer claims — not verified here); below the first resonance VSWR rises fast (4.6 at 50 MHz). For **receive** at VHF (noise-limited near cities) this is fine; for **transmit** use the SWR valleys [2]; for UHF weak-signal work (433/915 MHz telemetry) a discone typically has 0–5 dB less gain toward the horizon than a dedicated vertical dipole or ground plane — and much less than a Yagi.

### Biconical and bow-tie
EMC test labs use biconical antennas (≈ 30–300 MHz) because of their smooth impedance; TV "bow-tie" arrays use the planar version. A planar bow-tie's impedance (109–188 Ω for 90–150° flares) suits a 4:1 or 2:1 balun. Printed bow-ties are popular for GPR/UWB and for 2.4/5.8 GHz dual-band boards.

### Vivaldi / tapered-slot (TSA)
A slotline (the slot dual of a twin-lead line, see [slot antennas](slot-antennas.md)) is flared exponentially, $y=\pm(w/2)e^{Rx}$, from a narrow slot (w ≈ 0.3–0.5 mm, high impedance) at the feed to a wide aperture W ≈ λ_low/2. The wave travels along the flare and detaches end-fire where the width ≈ λ/2 → nearly constant beamwidth and gain over the band [6]. Example: w = 0.5 mm → W = 75 mm over 100 mm with R = 50 m⁻¹ (half-widths 0.25, 0.68, 1.86, 5.05, 13.8, 37.5 mm at x = 0…100 mm). Feeding uses a microstrip-to-slotline balun (radial stub + slot cavity) or the *antipodal* form (flares on opposite faces of the board, fed from microstrip). Uses: UWB radar, wideband array elements (tightly coupled arrays), EMC probes, 1–10 GHz SDR/test antennas. Pre-built PCB Vivaldis covering ≈ 1–10 GHz are common lab tools (not characterised here).

### Spirals
Archimedean ($r=r_0+a\phi$) and equiangular ($r=r_0e^{a\phi}$, Dyson [7]) two-arm spirals radiate CP broadside on both sides; one side is usually suppressed with an absorber-lined cavity (costs ≈ 3 dB efficiency) or a reflector at λ/4 (narrows the band). Needs a wideband balun (tapered microstrip–twin-line). Used for direction-finding, ESM receivers and wideband CP links. Our band estimate: D_out 15 cm, d_in 1 cm → 0.64–9.5 GHz (15:1).

### Log-periodic dipole array
Directional, linearly polarized, 6–8 dBi over 2:1–10:1 — the standard wideband "beam" for SDR/scanners and EMC, with 2–5 dB less gain than a Yagi of the same boom length ([Yagi/LPDA](yagi-uda-and-log-periodic.md)). For a ground station that must hear 433 and 915 MHz with one antenna, a 400–1000 MHz LPDA is the simplest choice ([example 5 there](yagi-uda-and-log-periodic.md#example-5--lpda-for-4001000-mhz-covers-433-and-868915)).

### Sleeve and open-sleeve monopoles
A sleeve (a tube or parasitic wires around the base of a monopole) adds a second resonance, broadening a monopole from ≈ 10 % to 2:1–3:1 bandwidth; open-sleeve dipoles (parasitic wires beside a dipole) give dual resonances in one compact element [1]. The coaxial "sleeve dipole" in [dipoles](dipoles-and-monopoles.md#sleeve-coaxial-dipole) is a narrowband cousin (the sleeve is a choke).

### Multiband (several narrow bands)
| Technique | How | Typical use | Caveat |
|---|---|---|---|
| Parallel/fan elements | one resonant element per band on one feed | HF fan dipoles; 433/915 dual whips | elements interact (+2–4 % shift when close, NEC) |
| Traps | parallel LC "switch" that isolates outer sections on the upper band | HF trap dipoles/verticals, dual-band VHF/UHF whips | trap loss 2–8 % (Q 200, NEC); narrower bandwidth |
| Harmonic operation | use odd/even resonances of one element | EFHW (all harmonics), λ/4 whip at 3× (3λ/4) | pattern changes on harmonics (lobes) |
| Coupled/parasitic resonator | second resonant element near the driven one | dual-band PCB IFAs, open-sleeve | tuning interacts |
| Dual-mode PCB antenna | two branches of an IFA/meander or a slot+monopole | 2.4/5 GHz Wi-Fi, 868/2400 | ground-plane dependent; tune on the real board |
| Matching-network diplexing | antenna wideband-ish; LC network creates two matched bands | 315/433 MHz OOK boards, 433/868 modules | efficiency of the small antenna still limits |

**One antenna for 433 and 915 MHz?** A 433 MHz λ/4 whip is close to 3λ/4 at 1300 MHz, *not* at 915 MHz (915/433 = 2.11), so it is badly mismatched at 915 MHz (≈ 0.53λ: a high-impedance point). Options: a dual-band whip with a trap or coil (commercial 433/868-915 dual-band whips), two whips on a diplexer, or an LPDA/discone on the ground station.

## Receive-only SDR antennas: does length matter?
SNR penalty (dB) of an antenna with radiation efficiency η, relative to a lossless antenna, from ITU-R P.372 external noise (`ant2_wideband.py` §4):
| Band / environment | F_a | Receiver NF | η = −1 dB | −3 dB | −10 dB | −20 dB | −30 dB |
|---|---|---|---|---|---|---|---|
| 7 MHz, residential | 49.1 dB | 10 dB | 0.0 | 0.0 | 0.0 | 0.1 | 0.5 |
| 14 MHz, quiet rural | 20.8 dB | 10 dB | 0.1 | 0.3 | 2.3 | 9.4 | 18.9 |
| 100 MHz, residential | 17.1 dB | 6 dB | 0.1 | 0.3 | 2.2 | 9.2 | 18.7 |
| 144 MHz, rural | 7.4 dB | 3 dB | 0.3 | 1.2 | 5.8 | 15.0 | 24.9 |
| 433 MHz, residential (P.372 Tab. 3) | 4 dB | 3 dB | 0.6 | 1.9 | 7.9 | 17.6 | 27.6 |
| 915 MHz, sky (assumed) | −10 dB | 3 dB | 1.7 | 4.5 | 12.4 | 22.6 | 32.6 |
| 1575 MHz GNSS, sky (assumed) | −16 dB | 1.5 dB | 2.6 | 6.2 | 14.8 | 25.1 | 35.1 |
So: at HF a short wire, a small active whip or a compromise loop is fine (but a *quiet* location matters more than the antenna); at VHF the antenna starts to matter; at UHF and above, the antenna's efficiency, gain and the feedline loss count dB-for-dB — the reason a ground station for 433/915 MHz telemetry uses a proper Yagi/LPDA and a mast-head LNA ([ground-station design](../15-lora-ism-radios/ground-station-design.md)). An RTL-SDR's telescopic dipole set to λ/4 per arm for the band of interest beats a "wideband" mag-mount whip at UHF; a discone is a convenient all-rounder for VHF scanning.

## Design equations & rules of thumb
| Quantity | Value / equation | Valid | Typical |
|---|---|---|---|
| 50 Ω monocone / discone angle | θ = 47° (narrow band) → 39° (5 octaves) [2] | infinite-cone theory + optimisation | 25–40° in practice |
| Discone first resonance | 0.7 × f_low; R + L = λ_r/2; R/L = 0.72 sin θ | Nail/Stearns [2] | NEC: VSWR < 2.5 from 0.6 f_low upward |
| Discone pattern | omni ≈ to 1.5 f_low, then tilts down 20–70° | NEC, 16 + 16 rods | horizon gain −9…+3 dBi |
| Self-complementary Z | 188.4 Ω | planar, infinite | spirals ~120–188 Ω with cavity/substrate |
| Planar bow-tie Z | 109–188 Ω for 150–90° flare | infinite | 4:1 balun to 50 Ω |
| Spiral f_low | ≈ c/(πD_out) | two-arm | 15 cm → 640 MHz |
| Vivaldi f_low | aperture ≈ λ/2 | — | 75 mm → 2 GHz |
| HF receive | efficiency nearly irrelevant if F_a ≫ NF + loss | P.372 | −30 dB costs 0.5 dB at 7 MHz |
| UHF receive | efficiency loss ≈ SNR loss | F_a ≲ NF | −3 dB costs 2–6 dB |

## Worked examples

**Example 1 — A VHF/UHF scanner discone for the roof.** Lowest frequency 100 MHz: f_r = 70 MHz → λ_r = 4.28 m → R + L = 2.14 m; θ = 30° → R/L = 0.36 → L = 1.575 m, R = 0.567 m (cone base 1.58 m). Use 16 rods each (3 mm aluminium), cone apex 15 mm below the disc. NEC: VSWR ≤ 2.25 from 60 MHz upward (except 2.67 near 180 MHz) to the 700 MHz model limit. Expect good omni coverage on 2 m (144 MHz) and degraded, downward-tilted patterns on 70 cm (430 MHz: horizon ≈ +2 dBi but peak 48° below the horizon) — fine for a scanner, not optimal for a fixed UHF link.

**Example 2 — Is a −10 dB-efficient mini-whip OK for a 7 MHz receive-only SDR?** Residential F_a = 72.5 − 27.7 log 7 = 49.1 dB. With NF 10 dB: penalty = 10 log[(81 000 + 9 + 10 × 9)/(81 000 + 9)] ≈ **0.005 dB**. Yes — at HF the location (man-made noise) and common-mode noise on the feedline dominate, not efficiency. The same −10 dB antenna on 915 MHz costs **12.4 dB**.

**Example 3 — UWB/GPR front end, 0.5–3 GHz.** A planar bow-tie of 90° flare (≈ 188 Ω theoretical, infinite) with arm length ≈ λ_low/4 = 150 mm and a 4:1 balun, or a Vivaldi with W ≈ 300 mm (λ/2 at 500 MHz) — the bow-tie is smaller but radiates both ways (put absorber behind it); the Vivaldi is directional (≈ 6–10 dBi) and pulse-friendly.

**Example 4 — 433/915 MHz ground-station receive with one antenna.** Options ranked by gain toward a rocket at low elevation: 400–1000 MHz LPDA (≈ 6–7 dBi, must be pointed), two separate Yagis (11 dBi each), a discone (−5 to +2 dBi at the horizon at UHF, no pointing). The P.372 table says each dB of antenna gain is ≈ 1 dB of SNR at these frequencies, so a pointed LPDA is worth ≈ 5–10 dB over a discone.

## Practical notes
- **Check "wideband" claims with a gain measurement**, not an SWR plot: a 50 Ω resistor has a perfect wideband SWR ([antenna-measurement](antenna-measurement.md)).
- **Discone construction**: rods are easier to tune (bend in/out to adjust impedance [2]); keep the coax running up inside the cone axis; add a common-mode choke at the base.
- **Wideband baluns** limit spirals, bow-ties and Vivaldis as often as the radiator does.
- **Strong out-of-band signals**: a wideband antenna delivers FM broadcast, cellular and pager signals to the SDR front end — add filters (FM notch, band-pass) before the LNA ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

## Common mistakes & misconceptions
- **"A discone is frequency independent."** It is a multi-resonant fat dipole with a scalloped SWR [2] and a pattern that tilts down at high frequency (NEC: horizon gain −9…+3 dBi).
- **"Low SWR over a wide band = good wideband antenna."** Many cheap wideband antennas are lossy; check gain/efficiency.
- **"A 25–1300 MHz discone works equally well across the band."** Impedance maybe; pattern and horizon gain no.
- **"For SDR the antenna doesn't matter."** True at HF (noise-limited), false at UHF/GNSS where every dB of loss or gain is ≈ a dB of SNR.
- **"Longer wire = better at all frequencies."** At UHF, a wire many λ long has a lobed pattern with nulls; a resonant element of the right polarization usually wins.
- **"My 433 MHz whip also works at 915 MHz (≈ 2×)."** 915/433 = 2.11 puts the whip at ≈ 0.53λ, a high-impedance point; use a dual-band design.
- **"Spirals are 50 Ω."** Self-complementary spirals are ≈ 188 Ω in free space (less on a substrate/cavity) and need a balun/transformer.
- **"Bow-ties are 50 Ω."** Planar bow-ties are 100–190 Ω for practical flare angles.

## How to simulate / verify
- `python3 tools/verify/ant2_wideband.py` — conical and bow-tie impedances (analytic, Babinet check), NEC-2 discone (16 + 16 rods: VSWR sweep 40–700 MHz, horizon gain and beam tilt), P.372-based receive SNR penalty table, spiral and Vivaldi size rules. Output in `tools/verify/ant2_wideband_output.txt`.
- NEC segment budget for discones: ≥ 80 f₂/f₁ segments (Stearns [2]); our model uses ≈ 1600.
- Vivaldis, spirals and printed bow-ties need a full-wave solver (openEMS; see [openEMS workflow](../16-simulation-tools/openems-workflow.md)) — not done here.

## Open questions / gaps
- No openEMS model of a Vivaldi, spiral or printed bow-tie yet; their numbers here are textbook rules.
- Discone NEC model stops at 700 MHz (segmentation); behaviour to 1.3 GHz and the effect of a top-loading whip (commercial "25 MHz" claims) are unverified.
- Sleeve-monopole bandwidth figures are cited, not computed.
- P.372 noise above 250 MHz is from its Table 3 (1970s European data) and assumed sky values; local measurements with an SDR would be better.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016 — ch. 9 (broadband dipoles: biconical, bow-tie, discone, sleeve), ch. 11 (frequency-independent antennas, spirals, LPDA). (textbook; cited)
2. S. Stearns (K6OIK), "All about the discone antenna," *QEX*, Jan/Feb 2007, 36–43 — history (Kandoian 1943/45, Nail), Schelkunoff monocone Z₀ = 60 ln cot(θ/2), optimum angle 47° → 39° vs bandwidth, discone not frequency independent, first resonance at 0.7 f_low, R/L = 0.72 sin θ (Nail), ≥ 8 rods, NEC segment rule. https://antena.fe.uni-lj.si/literatura/Razno/Antene/knjige/All_About_the_Discone_Antenna,_QEX,_Jan-Feb-2007.pdf (expert article; READ via pdftotext)
3. S. A. Schelkunoff, "Theory of antennas of arbitrary size and shape," *Proc. IRE* 29, 1941; *Advanced Antenna Theory*, 1952 — biconical antenna theory. (peer-reviewed/textbook; cited via [1], [2])
4. Y. Mushiake, "Self-complementary antennas," *IEEE APM* 34(6), 23–29, 1992. (peer-reviewed; cited)
5. V. H. Rumsey, *Frequency Independent Antennas*, Academic Press, 1966 (and "Frequency independent antennas," IRE Natl. Conv. Rec., 1957). (book; cited)
6. P. J. Gibson, "The Vivaldi aerial," *Proc. 9th European Microwave Conf.*, 101–105, 1979 — exponentially tapered slot; ≈ 10 dBi from below 2 to above 40 GHz (peer-reviewed; abstract read).
7. J. D. Dyson, "The equiangular spiral antenna," *IRE Trans. Antennas Propag.* 7(2), 181–187, 1959. (peer-reviewed; cited)
8. ITU-R P.372 (*Radio noise*), via this KB's [thermal-noise page](../07-noise-linearity/thermal-noise-and-noise-temperature.md) — external noise factors F_a. (standard)
9. J. L. Volakis (ed.), *Antenna Engineering Handbook*, 5th ed., 2019 — wideband and UWB antennas, Vivaldi feeds. (handbook; cited)
10. This repository: `tools/verify/ant2_wideband.py` (+ `_output.txt`); `tools/verify/ant2_slot.py` (Babinet). (verification)
