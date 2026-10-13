---
title: Circulators and isolators (ferrite gyrotropy, junction circulators, isolators, non-magnetic alternatives)
domain: 06-rf-circuits
slug: circulators-isolators
tags: [circulator, isolator, ferrite, yig, polder-tensor, gyrotropy, faraday-rotation, junction-circulator, lumped-element-circulator, non-reciprocity, pa-protection, radar-duplexer, magnet-free-circulator]
prerequisites:
  - ../02-electromagnetics/magnetic-materials-permeability.md
  - ../03-transmission-lines-matching/s-parameters.md
  - couplers-dividers-combiners.md
related:
  - power-amplifiers.md
  - rf-switches-attenuators-limiters.md
  - receiver-architectures.md
  - ../11-radar/cw-and-doppler-radar.md
  - ../11-radar/fmcw-radar.md
  - ../02-electromagnetics/wave-equation-plane-waves-polarization.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Circulators and isolators

## Questions this page answers
- What does a circulator do, and why does it need a magnet?
- How can a circulator be lossless and matched when a lossless matched three-port is "impossible"?
- What is gyrotropy, the Polder tensor and Faraday rotation?
- How does a junction circulator work, and why are UHF circulators lumped-element?
- What does an isolator actually protect a PA from — and what VSWR does the PA still see if the antenna breaks?
- Can a circulator replace a T/R switch in a radar or a half-duplex radio?
- What are magnet-free (active or time-modulated) circulators?

## TL;DR
- A **circulator** routes power 1 → 2 → 3 → 1: ideal $S=\begin{bmatrix}0&0&1\\1&0&0\\0&1&0\end{bmatrix}$ — lossless (unitary) and matched, which is allowed only because it is **non-reciprocal** ($S\neq S^T$); the three-port theorem (no lossless, matched, reciprocal three-port) is side-stepped by breaking reciprocity (verified). An **isolator** is a circulator with a load on port 3: forward transmission, reverse absorption.
- Non-reciprocity comes from a **magnetised ferrite**: its permeability is a tensor (Polder) with off-diagonal $\pm j\kappa$, so left- and right-circularly polarised waves see different permeabilities $\mu\pm\kappa$ and travel at different speeds (**gyrotropy**). With $\omega_0=\gamma\mu_0H_0$, $\omega_m=\gamma\mu_0M_s$, $\gamma/2\pi$ = 28.0 GHz/T: $\mu=1+\frac{\omega_0\omega_m}{\omega_0^2-\omega^2}$, $\kappa=\frac{\omega\omega_m}{\omega_0^2-\omega^2}$ (relative).
- **Faraday rotation** in a weakly biased, saturated ferrite approaches the frequency-independent limit $\theta/L=\sqrt{\varepsilon_r}\,\omega_m/(2c)$ — 11.6 °/mm for YIG ($\mu_0M_s$ = 0.178 T, εr 15); computed 12.1 °/mm at 10 GHz, 11.7 °/mm at 20 GHz. Below $f\approx\gamma\mu_0M_s/2\pi$ (5 GHz for YIG) one polarisation is cut off / lossy ("low-field loss") → low-$M_s$ garnets for UHF.
- **Junction (Y) circulators** use a ferrite disk whose two counter-rotating resonant modes are split by the bias; the first circulation mode needs $kR\approx1.84$ → disk radius ≈ 52 mm at 433 MHz, 25 mm at 915 MHz, 9 mm at 2.45 GHz, 2.3 mm at 10 GHz (εf 15) — why **lumped-element** circulators are used at UHF.
- Typical parts: drop-in UHF circulators ≈ 0.25–0.5 dB IL, ≈ 20 dB isolation (e.g. a 420–450 MHz drop-in: 0.25 dB, 21 dB, 400 W [6]). Bandwidth typically 5–20 %.
- **Protection is finite**: with 0.4 dB IL, 20 dB isolation, 20 dB port RL, a PA feeding an **open** antenna through the circulator sees VSWR 1.63 (30 dB-RL termination) or 2.36 (15 dB-RL termination), and the port-3 load must absorb ≈ the full PA power (1.5 W of 2 W).
- **T/R duplexing**: leakage into the receiver is dominated by the **antenna reflection**, not the circulator isolation: 33 dBm TX, antenna RL 15 dB → up to +21.5 dBm at the RX port (worst-case phase) — a circulator never replaces a limiter/T/R switch for a sensitive LNA.
- **Magnet-free** non-reciprocity: active (transistor) circulators, and spatio-temporally modulated or staggered-commutation (N-path) circulators in CMOS [7][8] — compact, integrable, but limited in power handling, noise and linearity.

## Intuition (no math)
In most circuits, if A can send a signal to B, then B can send the same signal back to A (reciprocity). A circulator breaks this symmetry: it is a roundabout with one-way traffic. That needs something with a built-in sense of rotation — a magnetised ferrite. Electrons' spins in the ferrite precess around the bias magnetic field in one direction only (like a spinning top); a circularly polarised RF field rotating in the same direction as the precession interacts strongly with it, one rotating the other way hardly at all. So the two rotation senses see different materials — different speeds.

In a junction circulator, a ferrite disk between three ports supports two resonances rotating in opposite directions. Without bias they are identical and the field pattern from port 1 splits evenly to ports 2 and 3 (and reflects). With the right bias, the two rotating modes are detuned just enough that their combination has a null at port 3 and a maximum at port 2 — a standing pattern rotated by 30°. Energy entering port 2 is similarly steered to port 3, and so on.

Because the steering depends on a resonance, circulators are narrowband (a few to tens of percent) and their size scales with wavelength inside the ferrite — at 433 MHz the disk would be ≈ 10 cm across, so UHF circulators replace the disk resonance with lumped inductors and capacitors around a small ferrite.

## The math

### Level 1 — definitions
- Circulator S-matrix (clockwise): $S_{21}=S_{32}=S_{13}=1$, all others 0. Insertion loss $-20\log|S_{21}|$, isolation $-20\log|S_{12}|$, return loss $-20\log|S_{11}|$.
- Isolator: circulator + matched termination on port 3 → $|S_{21}|\approx1$, $|S_{12}|\approx0$.

### Level 2 — derivations

**(a) Why non-reciprocity is essential.** For a matched three-port, $S=\begin{bmatrix}0&S_{12}&S_{13}\\S_{21}&0&S_{23}\\S_{31}&S_{32}&0\end{bmatrix}$. Losslessness ($S^HS=I$) requires orthogonal unit columns. The reciprocal case ($S_{ij}=S_{ji}$) leads to a contradiction ([couplers](couplers-dividers-combiners.md#level-2--derivations)). Dropping reciprocity, the equations admit exactly two solutions: $S_{21}=S_{32}=S_{13}=e^{j\phi}$, others zero (clockwise), or the counter-clockwise transpose — the ideal circulators [1 §9.6]. Check C verifies unitarity and $S\neq S^T$.

**(b) The Polder tensor.** The magnetisation $\mathbf M$ of a saturated ferrite obeys $\frac{d\mathbf M}{dt}=-\gamma\mu_0\,\mathbf M\times\mathbf H$. Linearising about the bias ($\mathbf H=H_0\hat z+\mathbf h e^{j\omega t}$, $\mathbf M=M_s\hat z+\mathbf m e^{j\omega t}$) gives $\mathbf b=\mu_0(\mathbf h+\mathbf m)=[\mu]\mathbf h$ with
$$[\mu]=\mu_0\begin{bmatrix}\mu_r&-j\kappa_r&0\\j\kappa_r&\mu_r&0\\0&0&1\end{bmatrix},\quad \mu_r=1+\frac{\omega_0\omega_m}{\omega_0^2-\omega^2},\quad\kappa_r=\frac{\omega\,\omega_m}{\omega_0^2-\omega^2}$$
[1 §9.1]. Circularly polarised fields $h_x\pm jh_y$ are eigenvectors with permeabilities $\mu_r\mp\kappa_r$ (sign depends on convention and propagation direction). Near $\omega=\omega_0$ (ferromagnetic resonance) the response is resonant (and lossy in reality, with linewidth ΔH); devices operate either above or below resonance.

**(c) Faraday rotation.** A linearly polarised wave along the bias = equal RHCP and LHCP components with propagation constants $\beta_\pm=k_0\sqrt{\varepsilon_r(\mu_r\pm\kappa_r)}$; after length $L$ the polarisation plane rotates by $\theta=(\beta_+-\beta_-)L/2$ — in the same absolute sense whichever way the wave travels (non-reciprocal: a round trip doubles rather than cancels it). For $\omega\gg\omega_0,\omega_m$: $\kappa_r\approx-\omega_m/\omega$, $\mu_r\approx1$, so $\theta/L\approx\sqrt{\varepsilon_r}\,\omega_m/(2c)$, independent of frequency (check B: 11.6 °/mm limit for YIG).

**(d) Junction circulator (Bosma; Fay & Comstock).** A ferrite disk of radius $R$ between ground planes supports modes $J_{\pm1}(kR)e^{\pm j\phi}$ with $k=\omega\sqrt{\varepsilon\mu_{eff}}$, $\mu_{eff}=\mu_0(\mu_r^2-\kappa_r^2)/\mu_r$. Unbiased, the ±1 modes are degenerate at $kR=1.84$ (first zero of $J_1'$). The bias splits them in frequency by an amount ∝ $\kappa_r/\mu_r$; circulation occurs when the operating frequency sits between them such that their phasor sum cancels at the isolated port — a 30° rotation of the standing-wave pattern [2][3]. The ports' coupling (via matching sections) sets bandwidth. Check F gives the disk radii above (first-mode estimate, $\mu_{eff}\approx1$).

**(e) Isolator VSWR protection.** With non-ideal S-parameters (transmission $a$, leakage $b$, match $r$), terminating port 3 with $\Gamma_T$ and the antenna port with $\Gamma_A$, the PA sees $\Gamma_{in}$ from the reduced two-port (script D). For $|\Gamma_A|=1$ the reflected wave is routed to port 3, reflected by the termination ($\Gamma_T$), partially returned; added to the direct port match and the leakage path, the PA sees roughly $|r|+|b|+|\Gamma_T|$ (worst-case phases): 0.24 (VSWR 1.63) with a 30 dB-RL load, 0.41 (VSWR 2.36) with a 15 dB-RL load.

### Level 3 — materials, power, and magnet-free non-reciprocity
- **Materials**: YIG (4πMs ≈ 1780 G) and doped garnets (lower Ms for UHF, e.g. Al- or Gd-doped), spinels and hexaferrites (self-biased, mm-wave). Below-resonance devices must keep $\omega>\omega_m$ roughly to avoid low-field losses; above-resonance devices need large bias fields [1].
- **Power handling and nonlinearity**: high RF fields excite spin waves (Suhl instabilities) → loss increase at high peak power; temperature changes Ms (circulator frequency shifts); magnets must be kept away from other magnetic parts (and from the rocket's magnetometer!).
- **Lumped-element circulators**: small ferrite with windings/capacitors forming the resonances; 100 MHz–2 GHz, compact.
- **Magnet-free circulators**: active circulators (three amplifiers in a ring) have limited linearity and add noise; **temporally modulated** (parametric) structures — coupled resonators whose capacitances are modulated in a rotating phase sequence — emulate angular momentum bias [7]; **staggered-commutation N-path** circulators in CMOS achieve non-reciprocity with switches clocked in quadrature and enable full-duplex radios [8]. Trade-offs: clock feedthrough, noise, limited power (tens of dBm at best), bandwidth set by the modulation.

## Design equations & rules of thumb

| Quantity | Equation / value | Notes |
|---|---|---|
| Ideal circulator | $S_{21}=S_{32}=S_{13}=1$ | lossless, matched, non-reciprocal |
| Gyromagnetic ratio | $\gamma/2\pi$ = 28.0 GHz/T = 2.80 MHz/Oe | FMR $f_0=\gamma\mu_0H_{int}/2\pi$ |
| Polder | $\mu_r=1+\frac{\omega_0\omega_m}{\omega_0^2-\omega^2}$, $\kappa_r=\frac{\omega\omega_m}{\omega_0^2-\omega^2}$ | lossless |
| Faraday rotation (HF limit) | $\sqrt{\varepsilon_r}\,\omega_m/(2c)$ | YIG ≈ 11.6 °/mm |
| Low-field-loss limit | $f\gtrsim\gamma\mu_0M_s/2\pi$ | YIG: 5 GHz → low-Ms garnets at UHF |
| Junction disk | $kR\approx1.84$, $k=\omega\sqrt{\varepsilon\mu_{eff}}$ | 433 MHz: ≈ 52 mm (εf 15) |
| Typical UHF drop-in | 0.25–0.5 dB IL, ≈ 20 dB isolation | 5–20 % BW |
| PA protection | PA $|\Gamma|$ ≈ port RL + isolation + termination RL (worst case) | size the load for full power |
| T/R leakage | ≈ max(P_TX − isolation, P_TX − RL_ant) (+ coherent addition) | antenna RL dominates |

## Worked examples

### Example 1 — Protecting a 2 W 433 MHz PA from a broken antenna
Rocket antennas can break or be shorted at separation. Without protection a 2 W PA into an open sees total reflection (the AFT05MS003N survives > 65:1 [5], many modules do not). A 433 MHz isolator (≈ 0.3 dB IL, 20 dB isolation) with a good 50 Ω termination keeps the PA's VSWR ≤ 1.63 even with an open antenna (script D) at the cost of 0.3 dB TX power; the termination must be rated for the full 2 W (the script puts 1.5 W into it). On a small rocket the isolator's magnet (and mass) matter — place it away from the magnetometer and check the compass calibration.

### Example 2 — Circulator as a radar or half-duplex duplexer
A CW Doppler radar at 24 GHz or a pulsed radar uses a circulator to connect TX → antenna → RX. With 30 dB circulator isolation and an antenna RL of 20 dB, +33 dBm TX leaks ≈ +15 dBm into the RX port (script E) — the antenna reflection path dominates. For CW/FMCW radar this leakage must be cancelled or handled by the mixer; for pulsed radar a limiter/T/R switch protects the LNA during the pulse ([switches & limiters](rf-switches-attenuators-limiters.md)).

### Example 3 — Why no one builds a 433 MHz stripline junction circulator
Disk radius ≈ 52 mm with εf = 15, plus magnet and ground planes → a 10 cm-class component. Lumped-element designs (small ferrite + LC resonators) or drop-in parts (e.g. a 420–450 MHz drop-in circulator: 0.25 dB IL, 21 dB isolation, VSWR 1.2, 400 W [6]) are used instead.

### Example 4 — Faraday-rotation isolator at X-band
YIG rod in circular waveguide: 45° rotation needs ≈ 45/11.6 ≈ 3.9 mm of fully saturated YIG in the high-frequency limit (εr 15; real devices use lower filling factors and longer rods); input and output rectangular ports at 45° plus resistive cards absorb the returning wave (rotated to 90°).

## Practical notes
- **Temperature:** Ms falls with temperature → centre frequency and isolation drift; specify the operating temperature range (rocket electronics bays can exceed 60 °C).
- **Magnetic environment:** permanent magnets detune near steel and disturb magnetometers/compasses; keep ≥ several cm away or shield.
- **Power:** check average and peak power ratings; the load on an isolator's port 3 must handle full reflected power.
- **Bandwidth:** isolation peaks at the design frequency and drops to ≈ 15 dB at band edges.
- **Measurement:** 3-port measurements (or 2-port with the third port terminated); isolation depends on the termination quality.
- **Alternatives:** for PA protection at low cost, a directional coupler + detector with power foldback ([detectors](detectors-and-power-meters.md)), or a rugged PA device; for T/R, a switch.
- **Isolators against transmitter intermodulation:** how much an isolator reduces reverse IMD between nearby transmitters is derived in [co-site interference § Level 2 (c)](co-site-interference-and-transmitter-intermod.md#level-2--derivations) (−I_iso on one product, −2 I_iso on the other).

## Common mistakes & misconceptions
- *"An isolator makes the PA immune to any load."* It limits the reflected wave to isolation + port mismatch + termination quality: VSWR 1.6–2.4 in the examples.
- *"A circulator isolates TX from RX in a radar."* The antenna's own reflection goes straight to the RX port.
- *"Ferrite devices are broadband."* They rely on resonances or specific bias conditions; bandwidths of 5–20 % are typical for junction types.
- *"The three-port theorem forbids circulators."* It forbids lossless, matched, *reciprocal* three-ports; circulators are non-reciprocal.
- *"Magnet-free circulators are drop-in replacements."* They have limited power handling and add noise/spurs from their modulation clocks.

## How to simulate / verify
- `tools/verify/rfckt_circulators.py`: Polder tensor, Faraday rotation vs the high-frequency limit, ideal circulator S-matrix properties, non-ideal circulator + load/antenna mismatch (PA VSWR), T/R leakage, junction-disk size estimate.
- EM simulation (openEMS supports gyrotropic media in some builds; commercial HFSS/CST) for ferrite devices; circuit models of lumped circulators with ideal gyrators.
- Bench: VNA with the third port terminated; power test into a mismatched load (stub tuner) to check PA protection.

## Open questions / gaps
- Only first-order junction theory (degenerate-mode radius, qualitative splitting) is given; Fay–Comstock design equations for bias field and matching are not implemented.
- The quoted drop-in part is from a trade-press summary [6], not a data sheet read; a table of real UHF/L-band circulators and isolators (IL, isolation, power, size, temperature) belongs in domain 18.
- Ferrite loss (linewidth ΔH) is not modelled; all tensor results are lossless.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012, ch. 9 (theory and design of ferrimagnetic components: Polder tensor, plane waves and Faraday rotation, isolators, circulators, §9.6 junction circulator). (textbook)
2. H. Bosma, "On stripline Y-circulation at UHF," *IEEE Trans. MTT*, 12(1), pp. 61–72, Jan. 1964. (peer-reviewed)
3. C. E. Fay, R. L. Comstock, "Operation of the ferrite junction circulator," *IEEE Trans. MTT*, 13(1), pp. 15–27, Jan. 1965. (peer-reviewed)
4. D. Polder, "On the theory of ferromagnetic resonance," *Phil. Mag.*, 40, pp. 99–115, 1949. (peer-reviewed; origin of the tensor)
5. NXP/Freescale, *AFT05MS003N* data sheet (ruggedness > 65:1 VSWR at 9 V). (datasheet)
6. Microwaves & RF product news, "Drop-in circulator passes 420 to 450 MHz" (VidaRF VDC-04200450-3: 0.25 dB IL, 21 dB isolation, VSWR 1.20, 400 W). https://mwrf.com/technologies/passive-components/article/21844104/dropin-circulator-passes-420-to-450-mhz (trade press — vendor claim)
7. N. A. Estep, D. L. Sounas, J. Soric, A. Alù, "Magnetic-free non-reciprocity and isolation based on parametrically modulated coupled-resonator loops," *Nature Physics*, 10, pp. 923–927, 2014. (peer-reviewed)
8. N. Reiskarimian, H. Krishnaswamy, "Magnetic-free non-reciprocity based on staggered commutation," *Nature Communications*, 7, 11217, 2016. (peer-reviewed)
