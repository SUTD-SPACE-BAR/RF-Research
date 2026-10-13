---
title: Radar applications people ask about — ground-penetrating radar, through-wall radar, Wi-Fi/CSI sensing, harmonic radar and junction detectors, cheap motion modules (RCWL-0516, LD2410), automotive and vital-sign radar — what is physically possible and what is hype
domain: 11-radar
slug: radar-applications-gpr-through-wall-sensing
tags: [gpr, ground-penetrating-radar, soil-attenuation, through-wall-radar, flash-effect, mimo-nulling, wi-vi, witrack, wifi-sensing, csi, 802.11bf, harmonic-radar, recco, nljd, nonlinear-junction-detector, rcwl-0516, self-oscillating-mixer, autodyne, ld2410, automotive-radar, vital-signs, weather-radar, hype]
prerequisites:
  - radar-range-equation.md
  - cw-and-doppler-radar.md
  - fmcw-radar.md
related:
  - diy-radar-hardware.md
  - radar-cross-section.md
  - clutter-and-mti.md
  - sar-and-imaging.md
  - mimo-radar-virtual-arrays.md
  - ../02-electromagnetics/wave-equation-plane-waves-polarization.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../09-propagation-link-budget/atmospheric-rain-attenuation.md
  - ../10-comms-modulation/ofdm.md
  - ../19-regulations-safety/regulatory-faq-misc.md
  - ../19-regulations-safety/singapore-imda-rules.md
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# Radar applications: GPR, through-wall, Wi-Fi sensing, harmonic radar and cheap motion modules

## Questions this page answers
- How does a ground-penetrating radar work, and how deep can it see in sand, clay or rock?
- Why does GPR fail in wet clay, and why do low frequencies go deeper?
- What limits GPR resolution?
- How can a radar "see through walls", and what stops it?
- How does Wi-Fi motion sensing (CSI) work, and can my router really count people or read breathing?
- What is harmonic radar, how do RECCO reflectors and insect tags work, and how does a non-linear junction detector find hidden electronics?
- What is the RCWL-0516 "microwave radar" module really, and how is it different from an HB100 or an LD2410?
- Why can't I turn a CDM324 Doppler module into an FMCW radar by wiggling its supply?
- Could a hobby Doppler radar see rain like a weather radar?
- Which radar claims are physics and which are hype?

## TL;DR
- **GPR is limited by soil conductivity, not transmit power.**
  - Conduction loss is $A \approx 1636\,\sigma/\sqrt{\varepsilon_r}$ dB/m: about 0.01 dB/m in dry sand, 0.7 dB/m in limestone, ≈ 18 dB/m in moist clay (50 mS/m) and ≈ 140 dB/m in wet saline clay (`e10_radar_apps.py`).
  - With 100 dB of system performance at 400 MHz, a planar reflector is visible tens of metres down in dry sand or ice, ≈ 2 m in moist clay and **≈ 0.3 m in wet saline clay**.
  - Water's dielectric relaxation adds a loss that rises as f² (7 dB/m in water at 400 MHz, 44 dB/m at 1 GHz). This is one reason low frequencies go deeper.
- **GPR resolution** is ≈ $v/(2B)$ vertically and about the first-Fresnel radius $\sqrt{\lambda d/2}$ laterally. A 400 MHz antenna in soil with εr = 9 gives ≈ 12 cm vertical and ≈ 35 cm lateral resolution at 1 m depth.
- **Through-wall radar** fights the **flash**: the wall echo is 50–65 dB stronger than a person behind it (estimate here; Wi-Vi quotes ≈ 36 dB). Remove it with time gating (needs about 2 GHz of bandwidth), MIMO nulling (Wi-Vi: 42 dB with 20 MHz at 2.4 GHz [3]), or by keeping only *moving* echoes. Walls cost (one way, 2.4 GHz [3]): glass 3 dB, hollow wall 9 dB, 18-inch concrete 18 dB, reinforced concrete about 40 dB. Through reinforced concrete it is essentially impossible for hobby hardware.
- **Wi-Fi/CSI sensing** detects *changes* in multipath across OFDM subcarriers. Presence, gross motion and (with a still subject) breathing are realistic. Imaging and identification are not, at Wi-Fi bandwidths: path resolution is c/B = 15 m at 20 MHz and 1.9 m at 160 MHz. IEEE 802.11bf-2025 now standardises WLAN sensing [5].
- **Harmonic radar** sends at f and listens at 2f. Natural clutter does not double frequency, so a diode tag stands out. Received power goes as $P_t^2/R^6$ in the diode's square-law regime, so 10× the power buys only 2.15× the range. Examples: RECCO 917 MHz → 1834 MHz, tens of metres in air [7]; insect radar 9.4 → 18.8 GHz, 1 kW peak, 15 mg tags tracked to 500 m [6]. **Non-linear junction detectors** compare the 2nd and 3rd harmonics to tell semiconductors from corroded metal [8].
- **The RCWL-0516 is a 3.2 GHz self-oscillating Doppler sensor.** One MMBR941M transistor is both the oscillator and the mixer (measured 3.181 GHz), followed by a PIR-style detector IC; it has ≈ 7 m range and no range information [9]. The **LD2410** is a real 24 GHz FMCW presence radar (0.75 m resolution, ≈ 200 MHz sweep) that can detect a *stationary* breathing person [10].
- **Hype checklist.** Be sceptical of:
  - "metres into wet ground" from any GPR;
  - "imaging through reinforced concrete" with Wi-Fi;
  - "heart rate of a person across a room through walls" without a still subject and line-of-sight-like geometry;
  - "long-range gold/bomb detectors" (the ADE 651 seller was convicted of fraud [12]);
  - any radar claim that never states bandwidth, power and antenna size.

## Intuition (no math)
All of these devices are radars: send a wave, listen for what comes back, and use *time* (range), *phase* (motion) or *frequency* (Doppler, harmonics) to separate what you want from everything else. What differs is **what is in the way**, and **what makes the target different from its surroundings**.

- **GPR**: the "air" is soil, which is a lossy dielectric. Every metre of wet clay eats tens of dB each way, so depth is set by the ground's conductivity. Shorter wavelengths give sharper pictures but die sooner, because water's molecular relaxation and scattering grow with frequency. Every GPR is a compromise between depth and detail.
- **Through-wall**: the wall in front of you reflects far more than the person behind it, like looking through a window at night with the room lights on. The radar must cancel or ignore the wall's echo (the "flash") to see the weak echo from behind. People move and walls do not, so motion is the main discriminator.
- **Wi-Fi sensing**: your access point already measures the channel on every subcarrier, many times a second, in order to equalise it. A walking person changes the multipath, so the channel estimate wiggles. That is enough to detect "someone moved". Telling *who* or *where* precisely needs bandwidth and antennas that Wi-Fi hardware rarely has.
- **Harmonic radar**: make the target different by giving it a diode. Rocks, trees and snow echo the transmitted frequency, but almost nothing in nature re-radiates at twice that frequency. The tag's echo is then alone in its frequency band, at the price of a very steep range law.
- **Cheap motion modules**: these are Doppler radars with no range resolution. They report "something moved". The RCWL-0516 is the extreme version: a single transistor oscillates, and the reflected wave pulls it slightly, which shows up as a low-frequency wobble (self-mixing).

## The math

### Level 1 — the four numbers that decide feasibility
- **Wave speed** in a medium: $v = c/\sqrt{\varepsilon_r}$ (m/s). Dry sand (εr ≈ 4): 0.15 m/ns; water (80): 0.033 m/ns.
- **Attenuation** (low-loss medium): $A \approx 1636\,\sigma/\sqrt{\varepsilon_r}$ dB/m, with σ in S/m. The constant is $8.686\,\eta_0/2$ = 1636.
- **Range resolution**: $\Delta R = v/(2B)$ for monostatic radar, where $B$ is the swept or occupied bandwidth (Hz). For a bistatic path-length measurement the resolution is $c/B$.
- **Doppler and phase**: $f_D = 2v_r/\lambda$, and phase $\phi = 4\pi d/\lambda$ for a displacement $d$ ([CW/Doppler](cw-and-doppler-radar.md)).

### Level 2 — derivations

**Lossy-medium propagation (GPR).** For $e^{j\omega t}$ fields in a medium with permittivity ε and conductivity σ, the propagation constant is $\gamma = \alpha + j\beta = \sqrt{j\omega\mu(\sigma + j\omega\varepsilon)}$ ([plane waves](../02-electromagnetics/wave-equation-plane-waves-polarization.md)). Separating real and imaginary parts:
$$\alpha = \omega\sqrt{\frac{\mu\varepsilon}{2}}\left[\sqrt{1+\left(\frac{\sigma}{\omega\varepsilon}\right)^2}-1\right]^{1/2}\ \text{Np/m}.$$
When $\sigma \ll \omega\varepsilon$, expand $\sqrt{1+x^2} \approx 1 + x^2/2$:
$$\alpha \approx \frac{\sigma}{2}\sqrt{\frac{\mu_0}{\varepsilon}} = \frac{\sigma\,\eta_0}{2\sqrt{\varepsilon_r}}\ \text{Np/m},$$
which is **independent of frequency**. This is the "plateau" that makes GPR possible at all. In dB/m, $A = 8.686\alpha = 1636\,\sigma/\sqrt{\varepsilon_r}$. The script checks this against the exact formula: they agree to < 1 % for dry sand, while for sea water at 100 MHz the shortcut over-states the loss by 2× because the medium is no longer low-loss.

Real soils add two losses that grow with frequency:
- **Water relaxation.** A single Debye relaxation at ≈ 17 GHz gives $\varepsilon'' = \Delta\varepsilon\,\omega\tau/(1+\omega^2\tau^2)$, equivalent to a conductivity $\sigma_{eff} = \omega\varepsilon_0\varepsilon''$ that grows as $f^2$ well below 17 GHz. For pure water: 2.4 mS/m at 100 MHz, 39 mS/m at 400 MHz, 240 mS/m at 1 GHz, i.e. 0.44, 7.1 and 44 dB/m ([dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)).
- **Scattering** from stones, roots and voids comparable to λ.

So the conduction-only depths below are *upper bounds* for wet materials at ≥ 400 MHz.

**GPR depth equation.** Model the target as a large planar interface, such as a water table or a bedrock surface. By the image method, its echo spreads as if from a source at distance $2d$. The two-way loss is then
$$L(d) = \underbrace{2Ad}_{\text{absorption}} + \underbrace{20\log_{10}(2d/1\,\text{m})}_{\text{spreading}} + \underbrace{20\log_{10}(1/|\Gamma|)}_{\text{reflection}} + L_{coupling}.$$
The maximum depth is where $L(d)$ equals the **system performance** $Q$, which is the ratio of transmitted power to the minimum detectable received power (typically 100–160 dB for commercial units; treat as a planning value). With $Q$ = 100 dB at 400 MHz, |Γ| = 0.3 and 10 dB coupling loss:

| Material (εr, σ) [2] | v (m/ns) | A (dB/m), conduction only | Depth, 400 MHz, Q = 100 dB | Depth, 100 MHz, Q = 120 dB |
|---|---|---|---|---|
| Ice (3.5, 0.01 mS/m) | 0.16 | 0.009 | > 200 m | > 200 m |
| Dry sand (4, 0.01 mS/m) | 0.15 | 0.008 | > 200 m | > 200 m |
| Granite (5, 0.1 mS/m) | 0.13 | 0.07 | ≈ 190 m | > 200 m |
| Limestone (6, 1 mS/m) | 0.12 | 0.67 | 32 m | 45 m |
| Silt (15, 10 mS/m) | 0.077 | 4.2 | 6.7 m | 8.8 m |
| Moist clay (20, 50 mS/m) | 0.067 | 18 | 1.9 m | 2.4 m |
| Wet saline clay (30, 500 mS/m) | 0.055 | 140 (100 MHz: 104) | 0.3 m | 0.5 m |
| Sea water (80, 3 S/m) | 0.034 | 280–450 | — | — |

The "> 200 m" entries are artefacts of a model that has only conduction loss. Real systems in dry sand or ice are limited by scattering, layering, antenna ringing and dynamic range, typically to some tens of metres in ice and dry rock (medium confidence; [1]). The table still makes the main point: **σ sets the depth to within an order of magnitude**, and in conductive clay no amount of power helps. Every extra dB/m costs twice per metre of depth.

**GPR resolution.**
- *Vertical*: two reflectors separated by $\Delta z$ produce echoes $2\Delta z/v$ apart. A pulse of bandwidth $B$ separates them when $2\Delta z/v \gtrsim 1/B$, so $\Delta z = v/(2B)$. Impulse GPR antennas typically have $B \approx f_c$. At 400 MHz in εr = 9 (v = 0.1 m/ns) that gives 0.125 m; the λ/4 rule of thumb gives 6 cm.
- *Lateral*: the first Fresnel zone of a reflector at depth $d$ satisfies $\sqrt{d^2+r^2} - d = \lambda/4$, so $r \approx \sqrt{\lambda d/2}$. That is 0.35 m at 1 m depth for 400 MHz in εr = 9.
- *Migration* (synthetic-aperture focusing, [SAR](sar-and-imaging.md)) collapses the hyperbolas that point targets draw in a B-scan. Its result depends on knowing $v$, which the hyperbola's shape itself provides.

**Ground-coupled antennas.** A GPR antenna on the ground radiates mostly *into* the ground: the higher-εr half-space pulls the pattern down, with a peak near the critical angle $\theta_c = \arcsin(1/\sqrt{\varepsilon_r})$. Lifting the antenna by more than ≈ λ/4 loses that coupling and adds a strong surface echo. The antenna's own ringing and the direct TX→RX coupling form the "early-time" problem: they swamp shallow targets unless the antennas are resistively loaded (bow-tie, Wu–King) and time-gated. These are well-known GPR design themes [1].

**Through-wall radar link.** The wall at distance $R_w$ acts as a mirror with reflection coefficient Γ, so the flash power is $P_{flash} \approx P_tG_tG_r\lambda^2|\Gamma|^2/(4\pi\cdot 2R_w)^2$. A person of RCS σ at range R behind a wall with one-way loss $L_w$ returns $P_h = P_tG_tG_r\lambda^2\sigma/((4\pi)^3R^4 L_w^2)$. With $R_w$ = 1 m, |Γ|² = −6 dB, σ = 0.5 m² and R = 5 m at 2.4 GHz, the flash exceeds the person by 48 dB (hollow wall), 66 dB (18-inch concrete) and about 110 dB (reinforced concrete). That decides the method:
- **Time gating** separates the wall echo from echoes 1–5 m behind it only if $\Delta R \ll$ 1 m, which needs **B of order 1–2 GHz**. Commercial UWB systems use ≈ 2 GHz of bandwidth and a 2.4 m array [3].
- **MIMO nulling** (Wi-Vi): two TX antennas are driven with weights that cancel at the receiver for all *static* reflections. Wi-Vi achieves 42 dB mean nulling with a 20 MHz Wi-Fi channel [3], so that only *changes* (moving people) remain. It then uses the person's own motion as a synthetic aperture (inverse SAR) for angle.
- **FMCW with background subtraction** (WiTrack): a 5.56–7.25 GHz sweep at 0.75 mW, with frames subtracted from each other to remove static echoes. It tracked a person through a wall with a median error of about 10–21 cm [4].

**Wi-Fi channel-state sensing.** OFDM receivers estimate the channel on each subcarrier $k$ ([OFDM](../10-comms-modulation/ofdm.md)):
$$H_k(t) = \sum_i a_i(t)\,e^{-j2\pi f_k\tau_i(t)} + \text{noise}.$$
Static paths give constant terms. A path off a moving person has delay $\tau_i(t) = \ell_i(t)/c$, so its phase turns at $2\pi\dot\ell_i/\lambda$: a body Doppler of a few Hz to tens of Hz at 2.4–5 GHz. Breathing changes $\ell$ by millimetres, giving about 0.2–0.4 rad of phase at 5 GHz.
- **Problems.** Transmitter and receiver have independent oscillators, so every packet carries a random CFO/SFO phase. Practical systems use amplitude only, or the *ratio* of CSI between two receive antennas, which cancels the common phase.
- **Resolution.** Delay resolution is $1/B$, i.e. 15 m of path at 20 MHz and 1.9 m at 160 MHz, so Wi-Fi cannot resolve where in a room someone is from delay alone.
- **What works.** Robust results are binary or coarse: presence, motion intensity, a slow periodic breathing component from a still person. Fine-grained claims such as gesture vocabularies, identity and keystrokes come from machine-learning classifiers trained in one room. They generalise poorly when furniture or people change (survey [5]).

**Harmonic radar range law.** Let the tag receive $P_{inc} = S A_{e1}$ with $S = P_tG_t/(4\pi R^2)$. In the small-signal (square-law) regime a diode's second-harmonic output is $P_2 = k_2 P_{inc}^2$. Re-radiated and received at 2f:
$$P_r = k_2\left(\frac{P_tG_tA_{e1}}{4\pi R^2}\right)^2 \frac{G_{tag,2}A_{r2}}{4\pi R^2} \;\propto\; \frac{P_t^2}{R^6}.$$
Doubling the range costs 18 dB (verified), and range scales as $P_t^{1/3}$. When the tag is strongly driven (near the radar), conversion saturates, $P_2 \propto P_{inc}$, and the law relaxes towards $R^{-4}$. The payoff is that clutter at 2f is essentially zero: the radar's own 2nd harmonic must be filtered out by tens of dB, and the receiver must be linear enough not to make its own 2f, so that detection is noise-limited even in vegetation or snow.

**Non-linear junction detection (NLJD).** Any junction with a curved I–V characteristic produces harmonics. A p–n or Schottky junction is asymmetric and gives a strong *even* (2nd) harmonic. A metal–oxide–metal contact, such as rusty bolts or corroded wires, behaves more symmetrically and gives a relatively stronger *odd* (3rd) harmonic. An NLJD transmits at f and compares the received 2f and 3f: 2f ≫ 3f suggests electronics, 3f ≳ 2f suggests corroded metal [8]. Multitone versions also look at intermodulation products [8].

**Self-oscillating mixer (RCWL-0516, autodyne).** An oscillator radiating at $f_0$ receives its own echo, delayed by $2R/c$. Injection pulls the oscillator's amplitude and phase by an amount proportional to the echo amplitude and to $\cos(4\pi R(t)/\lambda + \phi_0)$. A non-linear device biased in its oscillating region therefore produces a baseband (bias-current) component at $f_D = 2v_r/\lambda$. At 3.181 GHz that is **21.2 Hz per m/s** (walking about 20–30 Hz). The same transistor is oscillator, antenna driver and mixer [9]. There is no I/Q (so no direction), no range gate and no frequency stability to speak of. Detection is a threshold on the filtered Doppler energy, done by the RCWL-9196, a BISS0001-like PIR controller [9].

### Level 3 — limits and subtleties
- **GPR clutter is the ground itself.** Stones, roots and layering produce hyperbolas everywhere. Detection is clutter-limited, not noise-limited, so more power does not help but better antennas, polarisation and migration do. Stepped-frequency (SFCW) and FMCW GPRs reach large dynamic range with low peak power, but their own TX→RX leakage and phase noise set the floor ([FMCW leakage](fmcw-radar.md)). This is the issue behind DIY 800–1600 MHz FMCW GPR front-end questions.
- **Through-wall angle resolution** needs an aperture $D \gtrsim \lambda R/\Delta x$: about 1.2 m at 2.4 GHz for 0.5 m cross-range at 5 m. Hence Wi-Vi's use of the target's own motion (about 4λ ≈ 50 cm of movement) as an inverse-SAR aperture [3].
- **Wi-Fi sensing at 60 GHz** (802.11ad/ay, and 802.11bf's >45 GHz mode [5]) has 2 GHz channels (7.5 cm range resolution) and steerable arrays: real radar capability, but with poor wall penetration.
- **Harmonic-radar tag design** sets the diode's junction capacitance and the antenna lengths for both f and 2f; tag orientation causes deep fades. Insect tags are J-shaped wires with arms of ≈ 4 and 12 mm and a Schottky diode at the bend, 15 mg in total [6].
- **Vital signs** need body motion other than the chest to stay well below λ/(4π), the displacement that turns the phase by 1 rad (2.4 mm at 10 GHz, 1.0 mm at 24 GHz, 0.4 mm at 60 GHz). They also need a dominant reflection from the chest, and phase (not amplitude) demodulation: see the arctangent method on the [CW/Doppler page](cw-and-doppler-radar.md). Several people in one range bin, or any body motion, break it.

## Design equations & rules of thumb

| Quantity | Equation | Typical value |
|---|---|---|
| Soil wave speed | $v = c/\sqrt{\varepsilon_r}$ | 0.06–0.15 m/ns |
| Soil attenuation (low loss) | $1636\,\sigma/\sqrt{\varepsilon_r}$ dB/m | dry sand 0.01; clay 18–140 |
| Water relaxation loss | $\sigma_{eff} = \omega\varepsilon_0\varepsilon''$, grows ∝ f² | water: 7 dB/m at 400 MHz |
| GPR vertical resolution | $v/(2B)$ (≈ λ/4 in practice) | 400 MHz, εr 9: 6–12 cm |
| GPR lateral resolution | $\sqrt{\lambda d/2}$ | 0.35 m at 1 m, 400 MHz |
| Depth budget | $2Ad + 20\log(2d) + 20\log(1/|\Gamma|) + L_c = Q$ | Q 100–160 dB |
| Through-wall time gating | needs $c/(2B) \ll$ wall-to-target gap | B ≈ 1–2 GHz |
| Wall loss, one way, 2.4 GHz [3] | — | glass 3, hollow 9, 18″ concrete 18, reinforced 40 dB |
| Wi-Fi path resolution | $c/B$ | 15 m (20 MHz), 1.9 m (160 MHz) |
| Harmonic radar | $P_r \propto P_t^2/R^6$ (square law) | ×10 power → ×2.15 range |
| Doppler | $2v/\lambda$ | 21.2 (3.18 GHz), 70.2 (10.525 GHz), 161 (24.125 GHz) Hz per m/s |
| FMCW resolution | $c/(2B)$ | LD2410 0.75 m ⇒ 200 MHz; 77–81 GHz: 3.75 cm |

**Physically possible vs hype**:

| Claim | Verdict | Why (number) |
|---|---|---|
| GPR finds utilities at 0.5–2 m in typical soil | ✔ possible | 18 dB/m clay still leaves margin at 1–2 m |
| GPR maps bedrock tens of metres down in dry sand, ice or rock | ✔ possible | < 0.1 dB/m conduction loss |
| GPR sees 10 m into wet clay or salt marsh | ✘ hype | 18–140 dB/m one way, × 2 × 10 m |
| Detect a moving person behind a plasterboard or brick wall with Wi-Fi or SDR hardware | ✔ possible | 9 dB per pass; motion survives nulling |
| Image a still person through reinforced concrete with Wi-Fi | ✘ hype | ≈ 40 dB per pass at 2.4 GHz, and no motion to separate from the flash |
| Room-level presence or breathing from Wi-Fi CSI | ◐ in controlled settings | needs a still subject; classifiers are room-specific |
| Wi-Fi CSI localises people to 10 cm | ✘ at 20–160 MHz | path resolution 1.9–15 m; needs arrays or 60 GHz |
| Harmonic tag found at tens to ~100 m | ✔ possible | RECCO 80–120 m in air [7] |
| Harmonic tag found at kilometres with a hand-held unit | ✘ hype | $R \propto P_t^{1/3}$ |
| RCWL-0516 measures distance | ✘ | single-channel Doppler, no sweep [9] |
| 24 GHz FMCW module detects a sitting, still person | ✔ possible | range-binned micro-motion (LD2410) [10] |
| "Long-range" gold, water or bomb locators | ✘ fraud | no transmitter, bandwidth or aperture; ADE 651 conviction [12] |

## Worked examples

**1. Finding a buried pipe in a Singapore garden.** The soil is wet lateritic clay; take εr 20 and σ 50 mS/m.
- Loss: ≈ 18 dB/m one way. A pipe at 1 m costs 36 dB of absorption plus spreading.
- A 400 MHz GPR with $Q$ = 100 dB and |Γ| = 0.3 reaches about 1.9 m (table), so the pipe at 1 m is visible.
- Resolution: v = 0.067 m/ns, λ = 0.17 m, vertical ≈ 4–8 cm, lateral ≈ 0.29 m.
- At 1.6 GHz the resolution is 4× better but water relaxation adds several dB/m. Expect well under 1 m depth in the same clay.

**2. The same GPR on a beach.** Dry sand gives ≈ 0.01 dB/m, so the limit is dynamic range and scattering, not absorption. The wet sand below the water table (εr 25, and salt raises σ) acts as a strong reflector and the effective floor: it is easy to see, and hard to see past.

**3. Could Wi-Vi-style sensing find a person behind the av-bay-test room's wall?** At 2.4 GHz a hollow plasterboard wall costs 9 dB one way, giving a flash ≈ 48 dB above the person (this page's estimate). With ≥ 42 dB of nulling or motion filtering, a walking person is detectable a few metres behind it. A seated, still person is not, except through breathing with long integration. Through 18-inch concrete add 18 dB more; through reinforced concrete add another ≈ 44 dB, which no hobby system has.

**4. RCWL-0516 vs HB100 vs LD2410 for "is someone in the room?"**

| | Frequency | What it measures | Static person? | Range info |
|---|---|---|---|---|
| RCWL-0516 | ≈ 3.18 GHz, free-running [9] | Doppler energy above a threshold | no | none (≈ 7 m sensitivity) |
| HB100 | 10.525 GHz DRO ([CW/Doppler](cw-and-doppler-radar.md)) | single-channel Doppler (no direction) | no | none |
| LD2410 | 24.0–24.25 GHz FMCW [10] | range bins (0.75 m) plus micro-motion energy per bin | **yes** (breathing) | 0.75–6 m |

For an occupancy sensor that must not switch off a light while someone sits still, only the FMCW module works. For "a door opened" the RCWL-0516 is enough. It also triggers through plastic enclosures and thin walls, which can be a feature or a false alarm.

**5. Why a CDM324/IPM-165 cannot be swept for FMCW.** The module's oscillator is a fixed-frequency resonator design with no tuning port. Changing the supply moves the frequency only by "pushing", which is small, non-linear, temperature-dependent and not specified. Amplitude also changes, which an FMCW receiver sees as a huge spurious beat. FMCW needs a VCO with a tuning input and a linear sweep, ideally PLL-controlled: see [FMCW](fmcw-radar.md) and InnoSenT modules with a VCO input, or the TI/Infineon chips on [DIY radar hardware](diy-radar-hardware.md).

**6. Harmonic radar for finding a landed rocket?** Assume a diode tag in the nosecone, a hand-held transmitter at 2.45 GHz and a receiver at 4.9 GHz. Benchmarks: RECCO's 917/1834 MHz system finds reflectors at up to 120 m in air and 80 m in practice [7]. Because $R \propto P_t^{1/3}$, 10× the power buys only 2.15× the range. In a 1–2 km landing zone a harmonic tag is a final-metres tool. Use the [GNSS + LoRa beacon](../15-lora-ism-radios/rocket-telemetry-radio-design.md) to get within about 100 m, and a harmonic tag or audible beacon after that. Check the licensing of the transmitter ([regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md)).

**7. Could a hobby 10 GHz radar see rain?** Take an FMCW at 20 dBm with a 0.6 m dish (33 dBi, 3.5° beam), 30 m range bins, 100 ms dwell and NF 6 dB. For 10 mm/h rain (η ≈ −55 dB m⁻¹ at 10 GHz from the [clutter page](clutter-and-mti.md)), the resolution volume at 5 km is 1.6 × 10⁶ m³, so σ ≈ +7 dBsm and the SNR is about 40 dB (`e10_radar_apps.py`). Yes: precipitation is a big volume target. What hobby radars lack is the calibration needed to turn power into rain rate (dBZ), the clutter handling, and, at 10 GHz, protection from rain *attenuation* along the path. A wide-beam HB100 sees rain as Doppler "noise" a few tens of metres out.

## Practical notes
- **GPR antennas** must be shielded on top and resistively loaded, and kept within a few cm of the ground. Calibrate $v$ on site from the hyperbola of a known target, or from a common-midpoint survey. Open-source modelling: gprMax (FDTD) ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).
- **Mains cables, rebar and water pipes** dominate urban GPR records. Rebar spacing finders are a niche where cheap GPR works very well, because the target is metal at a few cm depth.
- **Wi-Fi sensing on ESP32**: ESP32 chips expose CSI. They are good for presence and motion experiments, and for learning OFDM channel estimation; do not expect localisation better than a room.
- **RCWL-0516 practicalities**:
  - Keep metal 1 cm or more from the back of the board, where the antenna is, and do not mount it behind metal.
  - The detection axis is broad.
  - Supply noise and Wi-Fi bursts can false-trigger it; add an RC filter and keep the ESP32 antenna away.
  - Its frequency is outside the SRD bands (see [regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md)).
- **Automotive radar sensors** fail from radome contamination (water films, ice, mud attenuate strongly at 77 GHz) and from misalignment: 1° of yaw error is 1.7 m of lateral error at 100 m.
- **Vital-sign demos** on TI IWR6843 or Infineon BGT60 kits work at 0.5–2 m with a seated, still subject facing the radar. Treat published "through-wall heart rate at 8 m" claims as laboratory results under ideal geometry.

## Common mistakes & misconceptions
- **"More power makes GPR see deeper."** Absorption costs $2Ad$ dB and conductive soil can be 20–140 dB/m. Each extra metre needs tens of dB, so system performance and frequency choice matter far more than power (D3 #74/#477; D2 #305).
- **"A buried radar could watch people on the surface"** (D2 #305). It is possible only through dry, low-loss ground with little cover. Through moist soil the two-way loss exceeds any practical budget within a metre or two.
- **"Wi-Fi can image through walls like X-ray vision."** At 20–160 MHz Wi-Fi resolves paths of 2–15 m. What is demonstrated is motion detection, counting a few people and coarse tracking, after nulling the static flash. Through reinforced concrete (≈ 40 dB each way at 2.4 GHz [3]) little survives (D3 #461/#498).
- **"The RCWL-0516 is a tiny 'microwave radar' with a range reading."** It is a single-transistor self-oscillating Doppler detector with a PIR-style controller; it has no range, no direction and no stable frequency [9] (D3 #581).
- **"I can sweep a CDM324 by changing its supply."** It has no tuning port. Supply pushing is small and uncontrolled, and it modulates amplitude too (D3 #76).
- **"Harmonic radar finds tags kilometres away if I add power."** $R \propto P_t^{1/3}$ in the square-law regime: ×1000 power for ×10 range.
- **"An NLJD only finds electronics."** Corroded metal joints also make harmonics; the 2nd/3rd-harmonic comparison is how the two are told apart [8] (D3 #499).
- **"Long-range locators find gold, water or explosives at tens of metres."** Devices with no transmitter of meaningful bandwidth, power or aperture cannot do this. The ADE 651 "bomb detector" was a golf-ball finder, and its seller was convicted of fraud [12].
- **"Radar vital-sign sensing works on anyone, anywhere."** It needs a still subject, a dominant chest reflection, and phase demodulation at mm-wave.

## How to simulate / verify
- `python3 tools/verify/e10_radar_apps.py` (output `tools/verify/e10_radar_apps_output.txt`, all checks pass). It covers material speeds and attenuations (exact vs low-loss), water relaxation as an effective conductivity, the GPR depth budget, resolution, the through-wall flash-to-target ratio, the harmonic-radar $R^{-6}$ and $P_t^2$ laws, Doppler and phase per module, FMCW resolution checks (LD2410, automotive, Wi-Fi), and a hobby weather-radar SNR.
- Quick GPR depth estimate for your own soil (same model as the script):

```python
import math
def depth(Q_db, er, sigma, gamma=0.3, coupling_db=10):
    A = 1636 * sigma / math.sqrt(er)               # dB/m one way (low-loss, conduction only)
    f = lambda d: 2*A*d + 20*math.log10(2*d) + 20*math.log10(1/gamma) + coupling_db - Q_db
    lo, hi = 0.01, 500.0
    for _ in range(60):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return lo
print(depth(100, 20, 0.05))   # moist clay -> ~1.9 m
```

- GPR modelling: gprMax (open-source FDTD for GPR) with a soil model containing Debye water and random stones; compare B-scans with and without migration.
- Through-wall: an FMCW or SDR radar plus a static-background-subtraction script (see [FMCW](fmcw-radar.md)); measure the wall loss with two antennas and a NanoVNA or SDR, either side of the wall.
- Wi-Fi CSI: ESP32 CSI tools, logging the amplitude per subcarrier while someone walks.

## Open questions / gaps
- The GPR material table uses mid-range values of wide spreads (Davis & Annan via the UBC GPG site [2]); a site's actual σ can differ 10×. Daniels [1] was not read page-by-page for this pass; the depth and antenna statements are textbook-level background.
- The radiated power of the RCWL-0516 was not found in any reliable source, nor was the exact frequency spread between units ("varies device to device" [9]).
- The through-wall flash estimate here (48–66 dB) is higher than Wi-Vi's "≈ 36 dB" [3]. The assumptions differ (wall distance, RCS, antenna gain); both are order-of-magnitude figures.
- The WiTrack paper states the sweep as both 5.56–7.25 GHz and 5.46–7.25 GHz in different sections [4].
- Radar ECM/jamming (D3 #699) is not covered here; see [spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md).

## Sources
1. D. J. Daniels (ed.), *Ground Penetrating Radar*, 2nd ed., IET, 2004 — GPR systems, antennas (resistively loaded bow-ties), propagation in lossy media, system performance; also H. M. Jol (ed.), *Ground Penetrating Radar: Theory and Applications*, Elsevier, 2009. (textbook; background, not quoted)
2. J. L. Davis, A. P. Annan, "Ground-penetrating radar for high-resolution mapping of soil and rock stratigraphy," *Geophysical Prospecting* 37(5), 531–551, 1989 — material εr/σ/v table, as reproduced by UBC Geophysics for Practising Geoscientists: https://gpg.geosci.xyz/content/GPR/table_velocity.html and attenuation/skin-depth notes https://gpg.geosci.xyz/content/GPR/GPR_fundamental_principles.html (peer-reviewed via course notes)
3. F. Adib, D. Katabi, "See Through Walls with WiFi!", ACM SIGCOMM 2013 — 2.4 GHz, 20 MHz, MIMO nulling (42 dB mean), wall-loss table, counting and gesture results, UWB comparison. https://people.csail.mit.edu/fadel/papers/wivi-paper.pdf (peer-reviewed)
4. F. Adib, Z. Kabelac, D. Katabi, R. C. Miller, "3D Tracking via Body Radio Reflections" (WiTrack), USENIX NSDI 2014 — FMCW 5.56–7.25 GHz, 0.75 mW, through-wall median errors 13.1/10.25/21.0 cm. https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-adib.pdf (peer-reviewed)
5. Y. Ma, G. Zhou, S. Wang, "WiFi Sensing with Channel State Information: A Survey," *ACM Computing Surveys* 52(3), 2019 (peer-reviewed; background on CSI models and limits); IEEE Std 802.11bf-2025 (approved 2025-05-28, published 2025-09-26), WLAN sensing, 1–7.125 GHz and > 45 GHz. https://standards.ieee.org/ieee/802.11bf/11574/ (standard; scope from the IEEE SA page)
6. R. Maggiora, M. Saccani, D. Milanesio, M. Porporato, "An Innovative Harmonic Radar to Track Flying Insects: the Case of *Vespa velutina*," *Scientific Reports* 9, 11964, 2019 — 9.4 GHz, 1 kW peak, 45 µs pulses, 7 m resolution, 500 m tracking, 15 mg J-wire Schottky tag. PMC6700122 (peer-reviewed)
7. K. Rasilainen, V. Viikari, "Transponder Designs for Harmonic Radar Applications," *Int. J. Antennas Propag.* 2015, 565734 — survey of harmonic-radar frequencies (9.4 GHz insect radars, RECCO 0.917 GHz). https://onlinelibrary.wiley.com/doi/full/10.1155/2015/565734 (peer-reviewed); RECCO R9 detector quick guide (2017) — range up to 120 m air, 20 m dry snow, 10 m wet snow, 0.2 m water; "80+ m with reflector 1.5 m above ground". https://beaconreviews.com/manuals/RECCO-R9-quick-guide-v01_ENG_v05-2017-12-28.pdf (manufacturer manual)
8. G. J. Mazzaro, A. F. Martone, D. M. McNamara, "Detection of RF Electronics by Multitone Harmonic Radar," *IEEE Trans. Aerosp. Electron. Syst.* 50(1), 477–490, 2014 (peer-reviewed; abstract-level); US Patent 6,057,765, "Non-linear junction detector" — 2nd-vs-3rd-harmonic discrimination of semiconductor vs corroded-metal junctions. https://patents.google.com/patent/US6057765A/en (patent)
9. J. Desbonnet, "RCWL-0516 information," GitHub, 2017– — MMBR941M Colpitts oscillator acting as self-oscillating mixer, 3.181 GHz measured (varies by unit), RCWL-9196 (≈ BISS0001), ≈ 7 m default range. https://github.com/jdesbonnet/RCWL-0516 (community reverse engineering — anecdotal but measured)
10. Hi-Link, *HLK-LD2410 Human Presence Sensing Module* manual V1.03 (2022) — 24–24.25 GHz FMCW, 0.75–6 m, 0.75 m resolution, ±60°, 5 V 80 mA. https://seengreat.com/upload/file/86/HLK+LD2410+Life+Presence+Sensor+Module+Manual+V1.03(220629).pdf (datasheet)
11. ITU-R P.527-6 (water/sea permittivity; Debye relaxation ≈ 17 GHz at 20 °C), as used on the KB [dielectrics page](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md). (standard)
12. ABC News (Australia), "Businessman convicted over bomb detector scam," 24 Apr 2013 — ADE 651 seller convicted of fraud at the Old Bailey; devices based on a novelty golf-ball finder. https://www.abc.net.au/news/2013-04-24/businessman-convicted-over-bomb-detector-scam/4647628 (news)
13. Forum demand: EEVblog (DIY FMCW GPR front end; CDM324 FMCW; automotive radar failures), Hackaday (MIT garage through-wall radar 2015; GPR for the masses 2019; Wi-Fi bulbs as motion sensors 2025; harmonic radar finds hidden electronics 2026), Andreas Spiess video on RCWL-0516/HB100/PIR; r/Radar (buried radar) — `gaps/D3-forums-youtube.md` rows 74, 76, 79, 461, 477, 498, 499, 540, 581; `gaps/D2-reddit.md` row 305. (forum — anecdotal)
