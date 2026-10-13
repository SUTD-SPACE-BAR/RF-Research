---
title: SDR front ends — overload, blocking and spurious responses from nearby transmitters, preselector filters, when an LNA helps or hurts, ESD/over-power/lightning protection, bias tees and host-noise hygiene
domain: 14-sdr-dsp
slug: sdr-front-end-protection-and-filtering
tags: [sdr, front-end, overload, blocking, desensitisation, intermodulation, im3, harmonic-mixing, image, spurious-response, preselector, saw, cavity-filter, fm-bandstop, lna, sfdr, limiter, pin-diode, schottky, tvs, esd, lightning, gas-discharge-tube, static, bias-tee, dc-block, usb-noise, ferrite, rtl-sdr, hackrf, ground-station, launch-site]
prerequisites: [sdr-hardware-survey.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md, ../07-noise-linearity/noise-figure-and-friis.md, ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md]
related: [signal-identification-and-spectrum-survey.md, iq-complex-baseband.md, sampling-aliasing-bandpass-sampling.md, ../06-rf-circuits/lna-design.md, ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md, ../06-rf-circuits/rf-switches-attenuators-limiters.md, ../06-rf-circuits/receiver-architectures.md, ../15-lora-ism-radios/ground-station-design.md, ../18-components-parts/filter-parts-saw-ceramic-ltcc.md, ../18-components-parts/lna-pa-gain-block-mmics.md, ../17-test-measurement/sdr-as-test-equipment.md, ../17-test-measurement/bench-measurement-recipes.md, ../19-regulations-safety/lab-safety-esd-high-power.md]
level: mixed
confidence: medium
last_updated: 2026-10-02
---

# SDR front ends — protection and filtering

## Questions this page answers
- Why do strong FM broadcast stations show up all over my RTL-SDR spectrum — even at 410 MHz?
- How strong are the signals near a broadcast tower, a cell site, or my own uplink transmitter, and can they damage my SDR?
- Does putting an LNA in front of my SDR always help? When does it make things worse?
- Should the filter go before or after the LNA?
- Does a cavity or SAW filter actually help my 915/923 MHz LoRa (Meshtastic) receiver?
- How do I protect an SDR from my own 2 W transmitter, static on the antenna, ESD and lightning?
- Will a limiter save my HackRF? Will a TVS diode hurt my GNSS signal?
- How do I use a bias tee safely, and what happens with a DC-grounded antenna?
- Is this "cheap LNA" oscillating, and how do I get rid of USB noise and spurs?
- How do I feed one antenna to several SDRs (or an SDR and a LoRa module) without losing sensitivity?
- How much rejection does my preselector need near an FM or cellular transmitter?
- Why does my noise floor not drop when I add an attenuator, and what does that tell me?

## TL;DR
- **Strong-signal problems come in four kinds**: (1) *ADC clipping* — the total power in the sampled bandwidth exceeds full scale; (2) *compression/blocking* — a strong signal anywhere the front end passes reduces gain for everything; (3) *intermodulation and harmonics* — products of strong signals land on your frequency (3rd order moves 3 dB per dB, an n-th harmonic n dB per dB); (4) *spurious responses* of the tuner (images, LO-harmonic mixing). The **10 dB pad test** separates them from real signals: a real signal drops 10 dB, an n-th-order product 10n dB (script §9).
- **Levels are higher than people expect** (script §1–2): broadcast FM at 0.1 V/m gives −15 dBm into a dipole (1 V/m near a tower: +5 dBm); a 2 W 433 MHz uplink 5 m away gives ≈ −2 dBm; a cell site (60 dBm EIRP assumed) at 300 m ≈ −22 dBm. HackRF's safe maximum is −5 dBm; RTL-SDR tuners tolerate ≈ +10 dBm at the chip.
- **An LNA trades dynamic range for sensitivity.** At 433 MHz an LNA (NF 0.45 dB, 20 dB) at the antenna takes the system NF from 5.4 dB to ≈ 0.8 dB but drops the system IIP3 by roughly its gain (−10 → −25 dBm with our assumed SDR IIP3) and SFDR from 72 to 64–65 dB (script §3). In a quiet field it wins; next to transmitters it can lose.
- **Filter placement**: LNA first (lowest NF) when the band is quiet; **filter first** when out-of-band blockers would compress or intermodulate the LNA — a 2 dB SAW then costs ≈ 1.9 dB of NF (script §3). Two FM stations at −20 dBm each need ≈ 39 dB of rejection *ahead* of a wideband LNA to keep IM3 below the 125 kHz noise floor (script §4).
- **Skirts matter, not the headline rejection**: a 5-pole Butterworth for 902–928 MHz gives only ≈ 28 dB at 940 MHz; a 917–925 MHz filter only ≈ 18 dB at 927 MHz (script §5). Cavity filters (< 1 dB loss, steep) beat SAWs where the blocker is close.
- **Protection is layered**: DC-grounded antenna or λ/4 shorted stub (static), gas-discharge arrester at the building entry (lightning), **limiter** (VLM-33-class: +12…+30 dBm in → ≈ +9…+13 dBm out — still too much for a HackRF, so follow it with ≥ 21 dB of pad, script §6), low-capacitance TVS for ESD (0.2 pF is invisible at UHF; 1.5 pF costs 9 dB of return loss at 1575 MHz, script §7). Never put a 5 V-working TVS on a 2 W TX line: its peak voltage is 14 V (21 V at VSWR 3).
- **Bias tees** (RTL-SDR Blog: 4.5 V, 180 mA [3]) power masthead LNAs; choke ≥ 10 Z0 reactance (≥ 200 nH at 400 MHz) and DC block ≥ 80 pF (script §8). DC-grounded antennas short them; instruments (VNA, generator) on a biased line get damaged — insert a DC block.

- **Diagnose before you buy filters**: 50 Ω load (internal spurs remain), 10 dB pad (overload products fall 20–40 dB, real signals 10 dB), retune (spurious responses move wrongly), battery-only host (USB/supply noise disappears).

Numbers marked "script" are from `tools/verify/e3_frontend.py` (20/20 PASS). The RTL-SDR IIP3 used in the cascades (−10 dBm) is an *illustrative assumption* — it is not published and depends on the gain setting.

## Intuition (no math)
A receiver front end is a funnel that must let a whisper through while a crowd is shouting nearby. The SDR's tuner and ADC can only handle a certain total loudness; everything the antenna collects in the passband of the front end — not just the signal you are tuned to — counts against that limit. When it is exceeded, the receiver does not simply get "louder": it distorts, and distortion creates new signals (harmonics and intermodulation products) at frequencies where nothing was transmitted. That is why a cheap SDR near FM broadcast towers shows music in odd places, and why an LNA that "boosts everything" can make reception worse: it boosts the crowd as well as the whisper.

Filters are the fix: they stop the crowd from reaching the sensitive stages. But a filter is never free — its loss adds noise if it sits before the LNA, and its rejection close to the passband (its skirts) is often much weaker than the headline number. Protection devices are a separate layer: they do nothing in normal operation and sacrifice themselves, or clamp, when something violent happens — a static discharge, a nearby transmitter keying up, lightning on the mast. They also have side effects (capacitance, their own distortion), so you choose them as carefully as the LNA.

## The math

### Level 1 — the working relations
- **Power from a field** (available power from a matched antenna of gain G, field E in V/m rms):
  $$P=\frac{E^2}{120\pi}\cdot\frac{G\lambda^2}{4\pi}=\frac{E^2\lambda^2G}{480\pi^2}\ \text{W}.$$
  At 100 MHz into a dipole: 1 V/m → +4.9 dBm, 0.1 V/m → −15.1 dBm, 10 mV/m → −35.1 dBm (script §1, matches `rfcalc.units.field_dbuvm_to_dbm`).
- **Power from a nearby transmitter** (far field, d ≫ λ/2π): $P_r = P_t + G_t + G_r - 20\log_{10}(4\pi d/\lambda)$. 2 W at 433 MHz, dipoles: 5 m → −1.9 dBm, 20 m → −13.9 dBm (script §2).
- **Cascade** (Friis noise and IIP3, input-referred, linear units):
  $$F=F_1+\frac{F_2-1}{G_1}+\dots,\qquad \frac{1}{IIP3}=\frac{1}{IIP3_1}+\frac{G_1}{IIP3_2}+\dots$$
  ([cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md)). Noise floor $N=-174+NF+10\log_{10}B$ dBm; third-order SFDR $=\tfrac23(IIP3-N)$ ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).
- **IM3**: two tones of $P$ dBm each produce input-referred products at $3P-2\,IIP3$. They reach the floor when $P_{max}=(2\,IIP3+N)/3$; a preselector must reject blockers by $P_b-P_{max}$.
- **Peak RF voltage** on a line: $V_{pk}=\sqrt{2PZ_0}\,(1+|\Gamma|)$ — the number to compare with a TVS working voltage or a diode's breakdown.

### Level 2 — mechanisms and derivations
**(a) Which strong signal causes which symptom.**
1. *ADC full-scale.* An 8-bit RTL-SDR has ≈ 44–50 dB between the noise in its whole sampled band and clipping ([hardware survey](sdr-hardware-survey.md)). The relevant power is the *total* in the ≈ 2.4 MHz captured plus whatever the tuner's IF filter leaks — one strong local transmitter in the captured span forces the gain down and lifts the effective floor for every weak signal.
2. *Compression/blocking.* A single large signal at offset Δf reduces the small-signal gain once it approaches the stage's P1dB; the receiver's *blocking* spec is the level that costs 3 dB of sensitivity ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). Reciprocal mixing (the blocker multiplied by the LO's phase noise) adds noise $P_b+\mathcal L(\Delta f)+10\log B$ even below compression.
3. *Harmonics and IM.* Expand a memoryless non-linearity $y=a_1x+a_2x^2+a_3x^3+a_4x^4+\dots$. A tone $A\cos\omega t$ produces an n-th harmonic with amplitude ∝ $a_nA^n$ (leading term), so its level in dB moves **n dB per dB** of input; two tones produce $2\omega_1-\omega_2$ etc. with the same rule for their order (script §9: 10 dB pad → 2nd/3rd/4th drop 20.1/30.0/40.0 dB). Broadcast FM at 102.5 MHz → 4th harmonic at **410 MHz** with 4 × 75 = 300 kHz deviation — the "music at 410 MHz" puzzle (D2 #462): wideband, distorted audio, gone with an FM band-stop filter.
4. *Tuner spurious responses.* A mixer driven by a square-ish LO also mixes with odd LO harmonics: tuned with LO $f_{LO}$ and IF $f_{IF}$, it responds to $kf_{LO}\pm f_{IF}$ for k = 1, 3, 5…. Example for a low-IF tuner with $f_{IF}$ = 3.57 MHz (R820T-class [4]) tuned to 145 MHz ($f_{LO}$ ≈ 148.6 MHz): the 3rd-harmonic response lies near 442–449 MHz, so a strong 446 MHz PMR handset can appear on 2 m unless the tuner's tracking filter removes it. The image ($f_{LO}+f_{IF}$ vs $f_{LO}-f_{IF}$, 7.1 MHz apart) is rejected ≈ 65 dB in the tuner datasheet [4] — less in practice for strong signals ([IQ](iq-complex-baseband.md)). Spurious responses move the "wrong" way or by the wrong amount when you retune; IM and harmonics do not depend on the tuning at all.

**(b) LNA in front: the trade, quantified.** With an LNA of gain $G$, noise factor $F_L$ and IIP3 $I_L$ ahead of an SDR ($F_S$, $I_S$):
$$F_{sys}=F_L+\frac{F_S-1}{G},\qquad \frac{1}{I_{sys}}=\frac{1}{I_L}+\frac{G}{I_S}\ \Rightarrow\ I_{sys}\approx\frac{I_S}{G}\ \text{when } I_L\gg G I_S .$$
The floor falls by $10\log(F_S/F_{sys})$ but the IM-limited ceiling falls by ≈ G dB, so SFDR changes by $\tfrac23\big[-G\,\text{dB}+10\log(F_S/F_{sys})\big]$ — negative whenever the gain exceeds the NF improvement. Script §3 at 433 MHz/125 kHz (SDR NF 5.4 dB, IIP3 −10 dBm assumed; LNA 0.45 dB, 19.8 dB, OIP3 +36 dBm; SAW 2 dB; coax 3 dB):

| Chain | NF (dB) | IIP3 (dBm) | Floor (dBm) | SFDR (dB) |
|---|---|---|---|---|
| SDR alone | 5.40 | −10.0 | −117.6 | 71.8 |
| coax → SDR | 8.40 | −7.0 | −114.6 | 71.8 |
| **LNA → SAW → coax → SDR** | **0.84** | −24.8 | −122.2 | 64.9 |
| SAW → LNA → coax → SDR | 2.69 | −24.8 | −120.3 | 63.7 |
| LNA → coax → SDR (no filter) | 0.69 | −26.8 | −122.3 | 63.7 |
| 10 dB pad → SDR | 15.40 | 0.0 | −107.6 | 71.8 |

Two lessons: the LNA buys 4.7 dB of floor but costs ≈ 7 dB of SFDR; and an attenuator never changes SFDR (it slides the whole window up), which is why "add a pad" fixes overload only when you have sensitivity to spare.

**(c) How much preselection.** Keeping IM3 of two equal blockers at the noise floor allows $P_{max}=(2I+N)/3$ per blocker: −45.9 dBm for the bare SDR, −58.6 dBm behind the unfiltered LNA (script §4). Two FM stations at −20 dBm (a few km from a broadcast site) therefore need ≥ 38.6 dB of rejection *before* the LNA — a broadcast band-stop or a 433 MHz band-pass in front of it, not after it.

**(d) Filter skirts.** For a band-pass mapped from a low-pass prototype, the normalised offset is $\Omega=|f/f_0-f_0/f|/(B/f_0)$; Butterworth rejection $10\log(1+\Omega^{2n})$, Chebyshev $10\log(1+\varepsilon^2T_n^2(\Omega))$. Script §5:

| Filter (centre / bandwidth) | Blocker | Butterworth n = 3 / 5 / 7 | Chebyshev 0.1 dB, n = 5 |
|---|---|---|---|
| 915 / 26 MHz (US 902–928) | 940 MHz | 16.8 / 27.8 / 38.9 dB | 32.2 dB |
| 921 / 8 MHz (SG 917–925) | 935 MHz | 32.5 / 54.1 / 75.7 dB | 60.9 dB |
| 921 / 8 MHz (SG 917–925) | 927 MHz | 10.9 / 17.5 / 24.5 dB | 19.3 dB |

Ideal prototypes predict > 100 dB far from the passband (e.g. a 433 MHz filter at 100 MHz), but real SAWs and LC filters flatten out at 40–70 dB because of package feed-through and ground inductance ([filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)); list values from the datasheet *at the blocker frequency*, not the "typical rejection" headline ([filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)).

**(e) Protection devices.**
- *Limiters* (PIN/Schottky): below threshold they are a few tenths of a dB of loss; above it they clamp to a "flat leakage" level. Mini-Circuits VLM-33-S+ (30–3000 MHz): 0.23 dB loss, VSWR 1.05, limits +12 to +30 dBm inputs to ≈ +11.5 dBm typical (9.2 dBm for +12 dBm in, 13.0 dBm for +30 dBm in at 415 MHz), 2 W maximum, 10 ns recovery [5]. That protects an LNA rated for +15–20 dBm input but **not** a HackRF (−5 dBm) — follow it with ≥ 21 dB of pad, or ≥ 16 dB for an RSPdx-R2 (0 dBm) (script §6).
- *Diode clamps* (antiparallel Schottkys, BAV99-type on many dongles): conduct at a few hundred mV, i.e. from roughly 0 to +10 dBm in 50 Ω (RTL-SDR front-end diodes reported to clip from ≈ +7…+12 dBm [6], forum — anecdotal). Near conduction they generate harmonics and IM themselves — a protection diode can *create* the spurs you are chasing when strong signals are present.
- *TVS / ESD diodes*: choose working voltage above the RF peak and capacitance below what the frequency tolerates. A 0.2 pF, ±5.3 V part (Infineon ESD0P2RF class [7]) handles 24.5 dBm matched (21 dBm at VSWR 3) without conducting, with return loss 37/31/26/22 dB at 433/915/1575/2440 MHz; a 1.5 pF part gives only 20/14/9/6 dB (script §7). On a 2 W TX line (14 V peak, 21 V at VSWR 3) a 5 V TVS would clamp every RF cycle.
- *Gas-discharge tubes and λ/4 stubs*: the GDT arrester fires at tens to hundreds of volts and diverts lightning-induced surges (kA, µs) to a ground rod, too slowly to protect semiconductors alone; a shorted quarter-wave stub is a DC (and low-frequency) short across the line with negligible effect at its design frequency — narrowband but excellent for static and surge energy below the band. Station grounding belongs in [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md).

**(f) Bias tees.** DC is injected through a choke (shunt reactance $X_L$) and kept out of the receiver by a series capacitor ($X_C$). A shunt reactance X across $Z_0$ has $S_{21}=2/(2+Z_0/jX)$: $X_L=10Z_0$ costs 0.011 dB and gives 26 dB return loss; $5Z_0$ costs 0.043 dB and 20 dB (script §8). Hence $L\ge 10Z_0/(2\pi f_{min})$ (199 nH at 400 MHz, with self-resonance above $f_{max}$) and $C\ge 10/(2\pi f_{min}Z_0)$ (80 pF). The DC drop over the coax, $I\,\ell\,R_{loop}$, is small for an LNA (50 mA × 20 m × 0.06 Ω/m = 0.06 V; loop resistance assumed for RG-58-class cable), but a bias tee driving a **DC-shorted antenna** (folded dipole, J-pole, many collinears and shunt-fed antennas) is a short circuit.

**(g) Host noise and common-mode current.** USB, display and switching-supply noise reaches the SDR mostly as *common-mode* current on the USB cable and the coax shield, which then couples into the antenna or the dongle's ground. A series common-mode impedance $Z_f$ (a clip-on ferrite) in a loop whose other impedances total $Z_{loop}$ reduces the current by
$$A_{cm}=20\log_{10}\left|1+\frac{Z_f}{Z_{loop}}
ight|\ 	ext{dB}.$$
With a ferrite of ≈ 250 Ω at 100 MHz (typical clip-on order of magnitude, assumed) in a 150 Ω loop, $A_{cm}\approx$ 8.5 dB; two in series ≈ 13 dB — useful, but not a cure for a noisy laptop placed next to the antenna. Distance (a 2–5 m USB extension) and a quieter supply are usually worth more than ferrites. Differential-mode spurs from the dongle's own clock (fixed lines at reference multiples) are unaffected by either.

### Level 3 — architecture limits and the general picture
- **Total-power budgets.** For a wideband receiver the quantity that matters is the *integrated* power of everything inside each stage's passband: the LNA sees the whole antenna bandwidth, the mixer sees the tracking filter's passband, the ADC sees the IF filter's. Draw a "power at each node" diagram for the worst nearby transmitter, compare with each stage's IP1dB and the ADC full scale, and put filtering just before the first stage that would be exceeded. This is the same reasoning as a cellular handset's front-end design ([receiver architectures](../06-rf-circuits/receiver-architectures.md)).
- **Near-field and co-site coupling.** Friis isolation between two antennas (two dipoles, 433 MHz: 26.9 dB at 2 m, 40.9 dB at 10 m; 915 MHz: 33.4/47.4 dB, script §10) assumes main-beam, co-polar, far-field geometry. Vertical stacking of collinear antennas (each in the other's pattern null), cross-polarisation and metal between antennas add isolation; near-field coupling (spacing ≲ λ/2π = 11 cm at 433 MHz) and coupling along coax shields remove it. Measure the isolation with a VNA (S21 between the two antenna ports) rather than trusting the formula ([bench recipes](../17-test-measurement/bench-measurement-recipes.md)).
- **Diode limiters and linearity.** A limiter's threshold must be above the strongest *wanted* signal by more than its IM-free margin; otherwise its own odd-order distortion degrades IIP3 of the whole chain. High-dynamic-range stations use high-threshold limiters plus filters, and accept that the limiter is for survival only.
- **AGC and self-protection.** SDR AGCs act on the digitised band; they cannot see a blocker that the tuner's filter removes before the ADC but that still compresses the LNA. Fix gain for measurements and set it from the worst-case blocker, not from the wanted signal ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

**Worked "power at each node" budget** (433 MHz ground station, own 2 W uplink at 20 m → −13.9 dBm at the connector, plus two FM stations at −20 dBm each; chain SAW → LNA → 3 dB coax → SDR):

| Node | Uplink at 434 MHz (in-band of a wide SAW) | FM pair at ≈ 100 MHz | Limit at that node | Verdict |
|---|---|---|---|---|
| Antenna connector | −13.9 dBm | −20 dBm each | — | — |
| After SAW (IL 2 dB; ≥ 50 dB at 100 MHz assumed) | −15.9 dBm | ≤ −72 dBm | — | FM removed |
| LNA input | −15.9 dBm | ≤ −72 dBm | LNA input P1dB ≈ +3 dBm (OIP3 36, G 19.8, P1dB-out ≈ 22 dBm assumed) | OK |
| LNA output / coax | +3.9 dBm | ≤ −52 dBm | — | — |
| SDR input (after 3 dB coax) | +0.9 dBm | ≤ −55 dBm | SDR clips/compresses near −20…−10 dBm at useful gain (assumed) | **SDR overloaded by the uplink** |

The uplink sits inside the 433 MHz SRD passband, so no band filter can remove it: only time-division (mute or attenuate the RX while transmitting), more antenna separation, or moving the uplink to another band fixes it — exactly Example 2 below.

### Front-end recipes by use case

| Use | Recommended chain (antenna → SDR) | Why |
|---|---|---|
| 433/915 MHz telemetry RX, quiet field | LNA (NF < 1 dB) at the antenna → SAW → coax → SDR | lowest NF; SAW after LNA still stops coax-picked-up and FM overload |
| Same, near broadcast/cellular sites | band-pass (cavity or SAW) → LNA → coax → SDR | protects the LNA from blockers; costs the filter's loss in NF |
| Same, with co-located uplink TX | limiter → band-pass → LNA (bypass/switch) → SDR; TX/RX time-division | survives the TX burst; measure isolation |
| GNSS on a rocket next to a 433/915 MHz downlink | GNSS SAW → LNA (or ceramic filter + LNA in the active antenna) | rejects the downlink harmonic/fundamental before the LNA ([filter parts Example 3](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)) |
| Monitoring your own TX with a HackRF/RTL-SDR | ≥ 40 dB of rated pads (or a coupler) → band-pass → SDR | the TX power must never reach the input ([SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md)) |
| ADS-B 1090 MHz in a city | 1090 SAW → LNA → SDR (or an integrated filtered LNA) | cellular 900 MHz and 1.8 GHz overload broadband LNAs |
| HF direct sampling (RX888-class) | 30–60 MHz low-pass (anti-alias) → step attenuator → ADC | aliases and broadcast overload are the limit, not NF ([sampling](sampling-aliasing-bandpass-sampling.md)) |
| Wideband survey (unknown signals) | no LNA at first; band-stop for the strongest local service; add gain only after the pad test | avoid creating products you then "discover" |

### Protection devices compared

| Device | Protects against | Speed | Side effects | Typical use |
|---|---|---|---|---|
| DC-grounded antenna / λ/4 shorted stub | static build-up, low-frequency surge energy | — (passive DC path) | stub is narrowband | every outdoor receive antenna |
| Gas-discharge tube arrester + ground rod | lightning-induced surges (kA) | µs (slow) | small capacitance; needs a real ground | building/trailer entry |
| PIN/Schottky limiter | RF over-power (nearby TX, T/R failure) | ns | leakage +10…+13 dBm; IMD near threshold; 0.2–0.5 dB IL | in front of LNAs |
| Antiparallel small-signal diodes | moderate over-power, ESD | ns | clip at ≈ 0…+10 dBm, create IMD | inside dongles and modules |
| Low-C TVS (≤ 0.3 pF) | ESD at connectors (kV, ns) | sub-ns | capacitance → RL/NF at GHz | GNSS/2.4 GHz inputs |
| Fixed pad | everything below its power rating | — | adds its loss to NF; SFDR unchanged | test set-ups, very strong sites |
| T/R switch / relay | own TX into own RX | µs–ms | finite isolation (measure it) | half-duplex ground stations |

## Design equations & rules of thumb

| Rule | When valid | Typical values |
|---|---|---|
| $P=E^2\lambda^2G/(480\pi^2)$ | matched antenna, far field | 0.1 V/m @ 100 MHz → −15 dBm |
| $P_r=P_t+G_t+G_r-\text{FSPL}$ | d ≫ λ/2π | 2 W, 433 MHz, 5 m → −2 dBm |
| $IIP3_{sys}\approx IIP3_{SDR}-G_{LNA}$ | LNA much more linear than SDR | 20 dB LNA → −15 dB |
| SFDR change from an LNA ≈ ⅔(ΔNF − G) | SDR-limited IIP3 | −7 dB at 433 MHz example |
| Pad: SFDR unchanged; floor and ceiling both +A dB | any attenuator | use only with sensitivity to spare |
| Required rejection $=P_b-(2IIP3+N)/3$ | two equal blockers, IM3 at floor | 39 dB for two FM stations at −20 dBm |
| n-th-order product moves n dB/dB | weakly non-linear stage | 10 dB pad → 3rd order −30 dB |
| LO-harmonic responses at $kf_{LO}\pm f_{IF}$ | switching mixers, k odd | 145 MHz tune ↔ ≈ 445 MHz |
| Limiter leakage ≈ +10…+13 dBm | VLM-33-class | needs pad for HackRF/RSP |
| TVS: $V_{RWM}>\sqrt{2PZ_0}(1+\lvert\Gamma\rvert)$ | RF line | 2 W @ VSWR 3 → > 21 V |
| Shunt C at UHF: RL ≈ $-20\log(\omega C Z_0/2)$ | ωCZ0 ≪ 2 | 0.2 pF @ 1575 MHz → 26 dB |
| Bias-tee choke $X_L\ge10Z_0$, block $X_C\le Z_0/10$ | lowest frequency | 400 MHz: 200 nH, 80 pF |

## Worked examples

**Example 1 — FM broadcast "everywhere" on an RTL-SDR (D2 #460, #462, #469, #472).** Symptoms: WFM audio near 410 MHz and in the FRS/PMR band, a raised floor across VHF. Diagnosis: (i) tune away by 100 kHz — the mystery signal stays at the same absolute frequency (not a tuner spurious response); (ii) the audio is wide and distorted, deviation ≈ 4 × 75 kHz (4th harmonic of a 102.5 MHz station); (iii) insert a 10 dB pad: it drops ≈ 40 dB. Fix: an 88–108 MHz band-stop filter *at the SDR input*, lower RF gain, and for 433 MHz work a 433 MHz band-pass. If the site is within a few km of the transmitter (fields of 0.1–1 V/m → −15 to +5 dBm), use the band-pass before any LNA.

**Example 2 — ground station next to its own uplink.** Telemetry RX and a 2 W 433 MHz command/uplink TX on the same trailer, 5 m apart, both dipoles: −1.9 dBm reaches the RX connector (script §2). Behind a 20 dB LNA that is +18 dBm — beyond most LNAs' absolute maximum and far above the SDR's. Options, in order of preference:
   1. time-division (never receive while transmitting) *and* a limiter + pad that survive the TX burst;
   2. separate the antennas vertically (collinear stack) and in distance — 20 m gives −13.9 dBm;
   3. frequency separation with filters (uplink on 868/915 MHz, downlink on 433 MHz, each RX with a band-pass that rejects the other band by ≥ 60 dB);
   4. a T/R switch with a known isolation (measure it; many PIN SPDT switches offer 25–40 dB, i.e. +3…−7 dBm leaking at 2 W — still needing a limiter).

   Always measure the real antenna-to-antenna S21 on site.

**Example 3 — does a cavity filter help a 915 MHz Meshtastic/LoRa node? (D2 #139).** It helps only if a *strong out-of-band* signal limits the receiver. In the US the 902–928 MHz band sits between cellular downlinks below 894 MHz (LTE bands 5/26, from general knowledge) and 929–932 MHz paging; a 5-pole filter of the band's width gives ≈ 28 dB at 940 MHz but much less at 929–930 MHz (script §5 shape), so close-in pagers need a narrower cavity. In Singapore, a 917–925 MHz filter must reject band-8 downlinks starting just above 925 MHz: ≈ 18 dB at 927 MHz even for a 5-pole design — steep cavities or keeping the receiver off the band edge are the realistic remedies ([ground station](../15-lora-ism-radios/ground-station-design.md)). Test before buying: log the node's noise floor/RSSI with and without a pad; if a 6 dB pad changes the floor by less than 6 dB, the receiver is interference-limited and a filter (not more gain) is the fix.

**Example 4 — "switching on the LNA" in a LoRa module (D2 #137).** Enabling a front LNA ahead of an SX1262 (NF ≈ 6 dB, IIP3 ≈ −5 dBm in the 07 example) improves NF by several dB but lowers IIP3 by about the LNA gain; the 07 page's cascade shows SFDR falling from 74.7 to 67.7 dB ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). Rural range test: switch it on. Urban rooftop next to cellular sites: measure both settings with the pad test and keep the one with the better floor-to-interference ratio.

**Example 5 — protecting a HackRF used next to transmitters.** Chain: antenna → λ/4 shorted stub (static) → VLM-33-S+ limiter → 20 dB pad → band-pass → HackRF. Worst case +30 dBm at the antenna port → limiter out ≈ +13 dBm → −7 dBm at the HackRF: 2 dB under its −5 dBm limit; with a 23 dB pad, 5 dB margin. Cost: 20–23 dB of sensitivity — acceptable for monitoring your own transmitter at close range, not for weak-signal reception (use an LNA chain with switched protection instead).

**Example 6 — ESD protection on a GNSS antenna input.** The active antenna line carries 3.3 V bias and signals near −130 dBm. A 0.2 pF TVS at the connector costs 0.011 dB and keeps return loss at 26 dB at 1575 MHz (script §7); its ±5.3 V working voltage clears the 3.3 V bias. A general-purpose 1.5 pF ESD diode would cost 0.56 dB and degrade the match to 9 dB RL — a measurable NF penalty before the LNA. Place it at the connector with the shortest possible ground path ([PCB layout](../13-pcb-rf-layout-emc/_index.md)).

**Example 7 — bias tee for a masthead LNA on 20 m of coax.** RTL-SDR Blog V3/V4 bias tee: 4.5 V, up to 180 mA [3]. A 50 mA LNA loses 0.06 V over 20 m of RG-58-class cable (assumed 0.06 Ω/m loop) → 4.44 V at the LNA — check the LNA's minimum supply. Before connecting a NanoVNA or signal generator to the same coax for tests, switch the bias off *and* insert a DC block; before enabling bias, confirm with an ohmmeter that the antenna is not DC-shorted (folded dipoles and J-poles read ≈ 0 Ω).

**Example 8 — choosing a 433 MHz preselector 3 km from an FM transmitter.** A 10 kW ERP station (16.4 kW EIRP) at 3 km produces $E=\sqrt{30\,\text{EIRP}}/d$ = 0.23 V/m, i.e. −7.7 dBm into a resonant 100 MHz dipole (script §1). A 433 MHz antenna is badly mismatched at 100 MHz, which typically removes another 10–20 dB (assumption — measure the antenna's S11 at 100 MHz with a NanoVNA and convert to mismatch loss), so expect ≈ −18 to −28 dBm per strong station at the connector. From Level 2(c), two such stations at −20 dBm need ≥ 39 dB of rejection ahead of a wideband LNA; a 433.92 MHz SAW with ≥ 50 dB listed at 100 MHz (check the datasheet table at that frequency) meets it with ≈ 10 dB margin, at the cost of ≈ 2 dB of NF. If several stations are present, budget the strongest *pair* that can intermodulate into your band (2f₁ − f₂ cannot reach 433 MHz from the FM band, but harmonics and mixer spurious responses can — the pad test tells you which).

## Practical notes

### Ground-station front-end checklist (before every launch campaign)
1. Antenna DC resistance measured (shorted designs noted) and bias-tee setting recorded.
2. Static path in place (DC-grounded antenna or λ/4 stub); arrester and ground at the trailer/building entry.
3. Filter S21 measured with a NanoVNA at the wanted frequency *and* at the worst local blockers (from the [site survey](signal-identification-and-spectrum-survey.md)).
4. Antenna-to-antenna S21 between every TX and RX antenna on site; worst-case power at each RX input computed (node budget above).
5. Limiter and pads sized for the worst case; their insertion loss included in the link budget.
6. Pad test done on the full chain at the site: the wanted signal (or a beacon) drops exactly the pad value; the floor does not drop by more than the pad.
7. Gain settings, firmware and cable set recorded (record-everything); a reference beacon level logged at the start and end of the day.

### Further notes
- **One antenna, several receivers**: a 2-way splitter costs ≈ 3.5 dB (3 dB split + ≈ 0.5 dB excess) on each branch and adds that loss to the NF if it is ahead of the LNA — put the LNA first, then split (the LNA's gain buries the splitter loss). Splitter port-to-port isolation (typically 20–25 dB) also limits how much one receiver's LO leakage or a module's TX reaches the other: never split between a transceiver that can transmit and an SDR.
- **"The floor did not drop with the pad"**: if a 10 dB pad lowers the displayed floor by less than 10 dB, the floor is set by the SDR itself (internal noise/spurs) — you were not antenna-noise-limited and an LNA *will* help; if it drops by exactly 10 dB, external noise or interference dominates and only filtering, antenna placement or a quieter site help.
- **Diagnose before fixing**: 50 Ω load on the input (internal spurs and USB noise remain), 10 dB pad (overload products drop > 10 dB), retune (spurious responses move wrongly), battery-only laptop (supply/ground noise disappears), and a spectrum of the antenna with the LNA unpowered (LNA oscillation disappears). Record the results — they turn a forum question into a diagnosis ([signal ID § artefacts](signal-identification-and-spectrum-survey.md)).
- **Cheap LNA boards** (wideband SPF5189Z-class, 50–4000 MHz) amplify FM, cellular and Wi-Fi along with your signal and can oscillate when their input/output see poor matches or when unshielded (D2 #458): symptoms are a comb of spurs or a raised floor that changes when you touch the board or the cables. Put them in a metal box, filter their supply, terminate unused ports, and add the band-pass in front ([LNA parts](../18-components-parts/lna-pa-gain-block-mmics.md)).
- **Integrated LNA + SAW modules** powered over the coax are convenient for 433/915 MHz, 1090 MHz and GNSS; check their max input and whether the SAW is before or after the LNA.
- **USB and host noise** (D1 #679): use a short USB extension so the dongle is away from the computer, clip-on ferrites at both ends of USB and on the coax near the SDR (common-mode currents on the coax shield also pick up noise), a powered hub with a quiet supply, USB-2 ports instead of USB-3 for 2.4 GHz work, the aluminium-cased dongles, and a battery test to identify the culprit. Switching-supply combs have a constant spacing (the switching frequency) and drift with load.
- **Maximum inputs** (from the vendors via [hardware survey](sdr-hardware-survey.md)): HackRF −5 dBm; SDRplay RSPdx-R2 0 dBm continuous; R820T chip +10 dBm [4]. Treat them as damage limits, not operating levels; for measurements stay ≥ 20 dB lower.
- **Static and weather**: unplug or ground antennas when storms approach (the RTL-SDR datasheets advise disconnecting the antenna in storms [3]); dry wind and dust charge insulated antennas — a DC-grounded design or a bleed resistor/stub prevents discharges into the input.
- **Hot switching**: never connect/disconnect a transmitter's antenna or a limiter path while transmitting; arcs and reflected power damage both ends ([RF switches](../06-rf-circuits/rf-switches-attenuators-limiters.md)).

## Common mistakes & misconceptions
1. **"More gain = more range."** Gain ahead of the SDR lowers IIP3 dB-for-dB; past the point where the SDR's NF is buried (≈ 15–20 dB of LNA gain), extra gain only reduces dynamic range.
2. **Putting the filter after the LNA to "save NF" next to a broadcast site** — the LNA is then the stage that intermodulates. Filter first when blockers dominate.
3. **Trusting headline rejection** — skirts at the actual blocker frequency (and package feed-through far away) decide.
4. **"A limiter protects any SDR."** Its leakage (+10…+13 dBm) exceeds many SDRs' maximum input; add a pad after it.
5. **Using a general-purpose ESD diode on a GNSS or 2.4 GHz input** — its picofarads of capacitance cost return loss and NF; use ≤ 0.3 pF RF TVS parts.
6. **Putting a 5 V TVS on a transmitter output** — it clamps the RF peaks (14 V at 2 W).
7. **Bias tee into a DC-shorted antenna or into test equipment.** Check DC resistance; use DC blocks.
8. **Calling an overload product a real signal** — always do the 10 dB pad test.
9. **Assuming far-field isolation between two antennas on the same mast or trailer** — measure S21.
10. **"My SDR's maximum input is +10 dBm, so −5 dBm is fine for measurements."** Damage limits are not linearity limits; measurements need the strongest signal 20–40 dB below compression.
11. **Fixing USB noise with more RF gain** — host noise enters after the RF stages; ferrites, cable routing and a quieter supply fix it, gain does not.
12. **Leaving the LNA powered while hot-plugging antennas or test leads** — the transient and the momentary open/short can oscillate or damage it; power down first.

## How to simulate / verify
- `python3 tools/verify/e3_frontend.py` (output `tools/verify/e3_frontend_output.txt`): field-to-power vs `rfcalc`; nearby-transmitter levels; cascades with `rfcalc.noise.cascade` (NF, IIP3, SFDR for six chains); IM3 and preselector rejection; Butterworth/Chebyshev skirts; limiter + pad budgets; TVS voltage and capacitance; bias-tee values and DC drop; n-dB-per-dB pad test on a polynomial model; antenna isolation.
- Measure your own chain: two-tone IIP3 of SDR and LNA with two generators and a combiner ([spectrum analyzers Example 6](../17-test-measurement/spectrum-analyzers.md)); filter S21 and antenna-to-antenna S21 with a NanoVNA; blocking with a strong tone at the blocker offset while monitoring a weak test signal's SNR (the RTL-SDR Blog V4 datasheet's desensitisation test is a good template [3]).
- Find common-mode noise paths with a clamp-on RF current probe or a small loop around the USB cable and coax while watching the SDR's floor; add ferrites where the current is largest.
- Simulate filter skirts with scikit-rf or Qucs-S using the vendor S-parameters, not prototypes ([simulation tools](../16-simulation-tools/_index.md)).

## Open questions / gaps
- Measured IIP3/IP1dB of RTL-SDR (R828D/R828S), Airspy and HackRF at 433/915 MHz versus gain setting were not found; the −10 dBm used here is illustrative. A bench campaign (two-tone at several gains) would fix the cascade numbers.
- The behaviour of dongle protection diodes (clipping level, IMD) is from forum reports only.
- Real SAW/cavity rejection at Singapore band-8 offsets (927–935 MHz) needs vendor S-parameters or measurement.
- PIN T/R-switch isolation values quoted are typical ranges, not from a specific datasheet.
- Lightning-arrester selection and station grounding are only summarised here (see domain 19).
- Ferrite common-mode impedances and splitter isolation figures are order-of-magnitude typical values (assumed), not from specific datasheets.
- No measurement yet of how much the team's ground-station LNA degrades IIP3 at the real launch sites; the node budget uses assumed P1dB values.

## Sources
1. This KB: [dynamic range, SFDR, blocking](../07-noise-linearity/dynamic-range-sfdr-blocking.md), [receiver cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md), [SDR hardware survey](sdr-hardware-survey.md) (measured NFs from the Libre Space Foundation evaluation; vendor maximum inputs), [LNA parts](../18-components-parts/lna-pa-gain-block-mmics.md) (TQP3M9036 NF 0.45 dB / 19.8 dB / OIP3 +36 dBm), [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md) (B39431B3710U410 433.92 MHz SAW, IL 2 dB). (internal, each with its own primary sources)
2. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall (2011), ch. 2 (non-linearity, IM, desensitisation, cascades) and ch. 4 (receiver architectures, image and harmonic mixing). (textbook)
3. RTL-SDR Blog, *RTL-SDR Blog V4 Datasheet* v1.0 (2024), https://www.rtl-sdr.com/wp-content/uploads/2024/12/RTLSDR_V4_Datasheet_V_1_0.pdf, and *RTL-SDR Blog V3 Datasheet* (2018) — R828D triplexer + notch, 28–43 dB better out-of-band isolation, two-tone desensitisation method, bias tee 4.5 V/180 mA, storm advice. (manufacturer; V4 read)
4. Rafael Micro, R820T preliminary datasheet (2011; copy on rtl-sdr.com) — 3.57/4.57 MHz IF, 65 dBc image rejection, +10 dBm maximum input. (datasheet, unofficial copy; via the hardware-survey page)
5. Mini-Circuits, *VLM-33-S+ Limiter* datasheet, https://www.minicircuits.com/pdfs/VLM-33-S+.pdf (read 2026-09-29) — 30–3000 MHz, 0.23 dB IL, +12…+30 dBm limiting range, +11.5 dBm typical output, 2 W max, 10 ns recovery, frequency table. (datasheet)
6. rtl-sdr.com forum thread "Can I use the SDR very close to the RF source?" (search summary, 2026-09-29) — R820T +10 dBm, BAV99 diodes clipping from ≈ 7–12 dBm. (forum — anecdotal)
7. Infineon, ESD0P2RF-02LS datasheet (2009) — bi-directional, 0.2 pF, ±5.3 V working, 20 kV ESD, linear to 6 GHz (distributor summary). (datasheet; numbers via search summary)
8. ARRL, *The ARRL Handbook for Radio Communications* (current ed.), chapters on station grounding, lightning protection and receiver performance. (handbook; general practice, not re-read)
9. A. Csete, S. Christiansen (Libre Space Foundation), "Evaluation of SDR Boards and Toolchains" (2020) — measured SDR NFs used in the cascade (RTL-SDR V3 5.4 dB at 437 MHz). (independent measurement; via [hardware survey](sdr-hardware-survey.md))
10. This repository: `tools/verify/e3_frontend.py`, `tools/rfcalc/noise.py`. (verification)
