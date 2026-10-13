---
title: Beginner project ladder — eleven graded first RF projects (RTL-SDR FM/ADS-B, AIS/APRS decoding, Meteor-M weather images, a NanoVNA-tuned 433 MHz dipole, cable loss and velocity factor, a tinySA look at a LoRa transmitter, a LoRa range test, SDR LoRa monitoring, an HB100 Doppler radar, a 2.4 GHz patch on JLC FR-4, and two-channel / KrakenSDR direction finding)
domain: 20-projects-recipes
slug: beginner-project-ladder
tags: [beginner, projects, first-projects, ladder, hello-world, rtl-sdr, fm, ads-b, ais, aprs, weather-satellite, meteor-m, lrpt, noaa-apt, v-dipole, qfh, nanovna, dipole, s11, cable-loss, velocity-factor, tinysa, lora, range-test, gr-lora_sdr, hb100, doppler, patch-antenna, jlcpcb, fr-4, krakensdr, direction-finding, interferometer, pre-registration]
prerequisites: [../00-math-foundations/rf-concepts-for-beginners.md]
related:
  - ../00-math-foundations/rf-learning-roadmap.md
  - ../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md
  - ../17-test-measurement/lab-setup-by-budget.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/bench-measurement-recipes.md
  - ../15-lora-ism-radios/choosing-and-judging-lora-antennas.md
  - lora-rocket-telemetry-link.md
  - sdr-receiver-build.md
  - patch-antenna-design-walkthrough.md
  - phased-array-starter-build.md
level: intro
confidence: medium
last_updated: 2026-10-14
---

# Beginner project ladder — eleven graded first RF projects

Each rung adds one new idea and one new instrument skill, and each ends with a **measurement you can
predict before you build** — the team's pre-registration habit in miniature. The ladder needs three
instruments in total (an RTL-SDR, a NanoVNA and a tinySA, ≈ US$300 in 2026) plus parts. Rungs 1–3
are receive-only; rungs 6–8 transmit, so read the legal notes first. When you finish rung 11 you are
ready for the full recipes in this domain ([LoRa telemetry link](lora-rocket-telemetry-link.md),
[ground station](ground-station-tracking-yagi.md), [SDR receiver](sdr-receiver-build.md)).

## Questions this page answers
- What is a good "hello world" project in RF?
- What should I build first with an RTL-SDR, a NanoVNA and a tinySA?
- Can I still receive NOAA weather-satellite pictures, and what antenna do I need?
- How do I build and tune a 433 MHz dipole, and what should the NanoVNA show?
- How do I measure a cable's loss and velocity factor?
- How do I safely look at my LoRa module's output on a tinySA?
- How do I run a LoRa range test that tells me something, and what range should I expect?
- How do I decode LoRa packets with an SDR?
- How do I make an HB100 Doppler module measure speed?
- Can I make a working 2.4 GHz patch antenna on cheap JLCPCB FR-4?
- How do I try direction finding with a KrakenSDR or two SDRs?
- Which projects are legal to transmit with in Singapore without a licence?

## TL;DR
- **Eleven rungs, three instruments.** 1 RTL-SDR FM + ADS-B → 2 AIS/APRS packets → 3 Meteor-M weather images → 4 NanoVNA 433 MHz dipole → 5 cable loss and velocity factor → 6 tinySA on a LoRa transmitter → 7 LoRa point-to-point range test → 8 SDR LoRa monitor (gr-lora_sdr) → 9 HB100 Doppler radar → 10 2.4 GHz patch on JLC FR-4 → 11 two-channel / KrakenSDR direction finding.
- **NOAA APT is over**: NOAA-19 and NOAA-15 were decommissioned in August 2025 (NOAA-18 in June 2025). The 137 MHz project is now **Meteor-M N2-3/N2-4 LRPT at 137.9 MHz** (QPSK, 72 kBd, ≈ 120 kHz) with a V-dipole or QFH and SatDump.
- **Predictions to beat** (script-checked): ADS-B line of sight from a 10 m mast to aircraft at 35 000 ft ≈ 439 km; 433 MHz dipole resonates at ≈ 328 mm tip-to-tip (R ≈ 72 Ω, VSWR 1.44 on 50 Ω); a 2.000 m PTFE cable shows its quarter-wave dip at ≈ 26 MHz (VF 0.695); an HB100 gives 70.2 Hz per m/s; a 10 mW e.r.p. 433 MHz LoRa link between 1.5 m-high dipoles should reach ≈ 3.3 km at SF9 with 10 dB fade margin on flat open ground.
- **Never transmit into nothing, never into an instrument**: antenna or 50 Ω load first; ≥ 40 dB of power-rated attenuation in front of a tinySA (absolute maximum +6 dBm) for a 1–2 W module.
- **Legal in Singapore without a licence**: receive anything here; transmit at 433.05–434.79 MHz ≤ 10 mW e.r.p. (≤ 10 % duty), 866–869 MHz ≤ 500 mW e.r.p., 917–925 MHz LoRa end devices ≤ 100 mW e.r.p. and ≤ 1 % duty; HB100 at 10.525 GHz falls in the 10.50–10.55 GHz radio-determination allowance. Rated 1–2 W EBYTE modules need a licence or permit ([Singapore rules](../19-regulations-safety/singapore-imda-rules.md)).

Numbers marked "script" are from `tools/verify/e6_beginner_numbers.py` (43/43 PASS); antenna and RSSI-test
numbers from `tools/verify/e6_lora_antennas.py`; SDR gain numbers from `tools/verify/e6_gain_staging.py`.

## Intuition (no math)
A good first project has three properties: it **works on the first evening** (so you stay motivated),
it **produces a number you can compare with a prediction** (so you learn something), and it **leaves
you with a tool** for the next rung. The ladder alternates receiving (cheap, legal, forgiving) with
building passive parts (antennas, cables), then measuring transmitters, then systems.

The early rungs teach you to *see* RF: an SDR waterfall makes bandwidth, noise and overload visible;
a NanoVNA turns "is my antenna good?" into a curve. The middle rungs teach the link: transmit power,
path loss and noise come together in a range test whose result you can predict within a few dB. The
last rungs teach design: a radar, a printed antenna and a direction finder each need you to predict a
number from geometry and then explain why the measurement differs.

## The math

### Level 1 — the numbers the ladder uses
| Idea | Formula | Rungs |
|---|---|---|
| Wavelength, antenna length | $\lambda = c/f$; dipole ≈ 0.47–0.48 λ tip-to-tip in thin wire; λ/4 whip | 1, 3, 4, 10 |
| dB and dBm | $P_\text{dBm} = 10\log_{10}(P/1\,\text{mW})$; gains/losses add | all |
| Radio horizon (4/3 Earth) | $d\,[\text{km}] \approx 4.12(\sqrt{h_1} + \sqrt{h_2})$, heights in m | 1, 2, 7 |
| Reflection | $\Gamma = (Z - 50)/(Z + 50)$, VSWR $=(1+|\Gamma|)/(1-|\Gamma|)$ | 4, 5, 10 |
| Velocity factor | $v_f = 4 L f_{\lambda/4}/c$ from the open-stub dip | 5 |
| Noise floor | −174 dBm/Hz + 10 log B + NF | 1–3, 8 |
| Free-space and two-ray path loss | $L_{fs} = 20\log_{10}(4\pi d f/c)$; beyond the breakpoint $4h_1h_2/\lambda$, $L \approx 40\log_{10}d - 20\log_{10}(h_1h_2)$ | 7 |
| Doppler | $f_d = 2 v f_0 / c$ (radar), $f_d = v_r f/c$ (satellite) | 3, 9 |
| Interferometer phase | $\Delta\phi = 2\pi (d/\lambda)\sin\theta$ | 11 |

### Level 2 — the few derivations you need
- **Quarter-wave dip of an open cable.** An open-ended line of length $L$ looks like a short circuit
  when it is a quarter wavelength long *inside the cable*, $L = v_f c/(4 f)$; solve for $v_f$. The
  open reflects everything, so the measured return loss is twice the one-way loss
  ([NanoVNA Recipe D](../17-test-measurement/nanovna-librevna-practical.md)).
- **Two-ray range.** Over flat ground the direct and ground-reflected rays nearly cancel once the path
  is much longer than $4h_1h_2/\lambda$ (13 m for two 1.5 m-high 433 MHz antennas — script); the
  received power then falls as $1/d^4$ and grows with $(h_1h_2)^2$
  ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)). That is why handheld range
  tests disappoint and why masts help 6 dB per doubling of one height.
- **Homodyne Doppler.** The HB100 multiplies the echo $\cos(2\pi f_0 t - 4\pi R(t)/\lambda)$ by its own
  oscillator; with $R = R_0 - vt$ the product contains a tone at $2v/\lambda$
  ([CW and Doppler radar](../11-radar/cw-and-doppler-radar.md)).
- **Patch resonance.** A rectangular patch resonates when its length is about half a wavelength in the
  substrate, shortened by fringing: $L \approx c/(2f\sqrt{\varepsilon_{eff}}) - 2\Delta L$
  ([patch antennas](../08-antennas/patch-antennas.md)).
- **Two-element direction finding.** A plane wave from angle θ reaches two antennas $d$ apart with a
  path difference $d\sin\theta$; measuring the phase difference gives θ, unambiguously only if
  $d \le \lambda/2$ ([DIY phased arrays](../12-phased-arrays/diy-phased-array-projects.md)).

### Level 3 — where the simple predictions break
- Real ADS-B range is set by buildings, terrain and antenna height, not the horizon; a window-sill
  antenna typically sees one sector only.
- Dipole resonance shifts with wire thickness, feed gap, nearby objects and the feed cable carrying
  common-mode current; a choke balun is part of the antenna.
- Two-ray assumes flat, smooth ground; vegetation, buildings and body blocking add 10–30 dB and turn the
  link into a fading channel ([multipath and fading](../09-propagation-link-budget/multipath-fading-doppler.md)).
- FR-4 εr varies ±5 % and is lossy, so a printed patch can be 2–3 % off in frequency and lose 1–3 dB of
  efficiency ([patch walkthrough](patch-antenna-design-walkthrough.md)).
- DF bearings are limited by calibration and multipath, typically 1–5° in the field, not by noise
  ([phased-array starter](phased-array-starter-build.md)).

## Design equations & rules of thumb
| Rule | Value | Why |
|---|---|---|
| ADS-B ground-plane whip | λ/4 = 68.8 mm at 1090 MHz, 4 radials drooped ~45° | script; [dipoles](../08-antennas/dipoles-and-monopoles.md) |
| 137 MHz V-dipole | two 53.4 cm arms (0.98 λ/4), 120° V, horizontal, axis N–S | 9A4QV design [5]; script |
| 433 MHz dipole (2 mm wire) | 327.9 mm resonant, R ≈ 72 Ω, VSWR-2 bandwidth 8.2 % on 50 Ω | MoM on the [dipoles page](../08-antennas/dipoles-and-monopoles.md) |
| Cut long, trim short | start 3–5 % long; trimming ≈ 1 % of length raises f by ≈ 1 % | resonance ∝ 1/length |
| Pad before a tinySA | ≥ 40 dB, first pad rated ≥ 2× CW power | tinySA Ultra +6 dBm absolute max [8] |
| RTL-SDR gain | the lowest gain at which the noise floor rises 5–10 dB with the antenna connected | [gain staging](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md) |
| A/B antenna comparisons | interleave A and B; ≥ 60 packets each to see 2 dB with 4 dB fading spread | `e6_lora_antennas.py` §6 |
| HB100 IF chain | 70–80 dB audio gain, band-pass ≈ 6–600 Hz for people, ≈ 2.5 kHz for cars | [CW and Doppler](../11-radar/cw-and-doppler-radar.md) |
| Interferometer spacing | ≤ λ/2 for unambiguous bearings (34.5 cm at 433 MHz) | [DIY arrays](../12-phased-arrays/diy-phased-array-projects.md) |

## Worked examples — the ladder
Every rung has the same blocks. **Goal** · **Kit and cost** (2026 snapshot; marketplace prices
unverified unless a KB page cites them) · **Steps** · **Predict, then measure** · **What you learn** ·
**KB links**.

### Rung 0 (optional warm-up) — a first discrete radio: superregen OOK pair, crystal set or Tayloe SDR
- **Goal**: build or wire a receiver whose every stage you can see; meet regeneration, quench and
  selectivity before any SDR hides them.
- **Kit and cost**: FS1000A + XY-MK-5V 433 MHz pair and an Arduino (≈ US$2–5 marketplace, unverified),
  later an RXB6 or CC1101 board for comparison; alternatives are a crystal-set kit (MW AM only) or a
  SoftRock-style 4-path Tayloe/QSD receiver kit with a sound card.
- **Steps and predictions**: follow the beginner steps and Example 7 in
  [receiver architectures: first-radio receivers](../06-rf-circuits/receiver-architectures.md#first-radio-receivers-crystal-sets-superregeneration-and-cheap-ook-modules).
  Predict ≈ 100–300 m ground range for the superregen pair and ≈ 2× that for a CC1101, and see the
  XY-MK-5V's own ≈ 1–2 MHz-wide emission on the rung-1 RTL-SDR. For a QSD, predict the 2 kHz RF bandwidth
  from 0.8 µF and 50 Ω ([mixers: N-path](../06-rf-circuits/mixers.md#level-3--lptv-analysis-conversion-matrices-noise-folding-and-n-path-tayloe-mixers)).
- **Legal note**: 433.05–434.79 MHz in Singapore is 10 mW e.r.p. at ≤ 10 % duty (or 1 mW continuous); do not
  build a broadcast-band FM "bug" without a dummy load ([regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md)).

### Rung 1 — RTL-SDR first light: broadcast FM and aircraft ADS-B
- **Goal**: receive and recognise signals; meet the waterfall, the noise floor and gain; decode
  aircraft positions.
- **Kit and cost**: RTL-SDR Blog V3 or V4L with its dipole kit (≈ US$35–50; the V4 is end-of-life
  [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)); a laptop; SDR++ (or SDR#/GQRX); readsb or
  dump1090 with tar1090 for a map. For ADS-B, a home-made 1090 MHz ground plane from an SMA chassis socket
  and 1.5 mm wire (≈ US$5).
- **Steps**: (1) install the driver and SDR++; tune 88–108 MHz in WFM; set the gain manually.
  (2) Find the DC spike at the centre and offset-tune away from it ([IQ](../14-sdr-dsp/iq-complex-baseband.md)).
  (3) Watch an FM station's ≈ 200 kHz hump, the 19 kHz stereo pilot and RDS in the demodulated
  spectrum. (4) Build the λ/4 whip (68.8 mm) with four radials; mount it as high as you can with a clear
  view of the sky. (5) Run readsb at 1090 MHz; log messages per second and the farthest aircraft.
- **Predict, then measure**: the radio horizon from a 10 m mast to an airliner at 35 000 ft is ≈ 439 km
  (script); from a window sill expect a fraction of that in the open directions. Record messages/s at
  three gain settings and the floor rise for each.
- **What you learn**: λ sets antenna size; line of sight sets range; more gain is not always better.
- **KB links**: [gain staging and reception recipes](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md),
  [radio horizon](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md),
  [signal identification](../14-sdr-dsp/signal-identification-and-spectrum-survey.md).

### Rung 2 — decode packets: ships (AIS) and APRS
- **Goal**: turn bursts on a waterfall into decoded data; see packet radio, GMSK and AFSK.
- **Kit and cost**: the rung-1 SDR; a VHF antenna (a vertical dipole ≈ 0.88–0.90 m tip-to-tip at 162 MHz (λ/2 = 0.925 m before
  end-effect shortening), or a λ/4 ground plane of ≈ 44–46 cm); AIS-catcher (AIS) and Dire Wolf (APRS). Cost ≈ US$5 in wire.
- **Steps**: (1) AIS on 161.975 and 162.025 MHz (GMSK 9.6 kb/s, 25 kHz channels) — tune between the
  two channels (50 kHz apart) with a sample rate that covers both (≥ 250 kS/s) and let AIS-catcher decode; the Singapore Strait is one of the
  busiest AIS areas in the world. (2) APRS on 144.390 MHz (Singapore, Malaysia, North America; 144.800 MHz
  in Europe) — narrow-band FM, 1200 b/s AFSK; feed the audio to Dire Wolf.
- **Predict, then measure**: ship positions should reach roughly the VHF line of sight (a 10 m antenna to a
  20 m ship mast ≈ 31 km by the horizon formula) plus a little beyond; count decodes vs gain and see the
  overload point when a nearby ship transmits.
- **What you learn**: burst signals, channel bandwidth, the noise floor of a 12.5–25 kHz channel
  (−133 dBm kTB at 12.5 kHz, script), the difference between hearing and decoding.
- **KB links**: [reception recipes](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md),
  [software demodulation](../14-sdr-dsp/software-demodulation.md),
  [digital modulation](../10-comms-modulation/digital-modulation-psk-qam-fsk.md).

### Rung 3 — weather-satellite images: Meteor-M LRPT with a V-dipole or QFH
- **Goal**: track a satellite pass, handle Doppler, and decode an image from 830 km away.
- **Status note**: the classic NOAA APT project ended with the decommissioning of NOAA-18 (June 2025),
  NOAA-19 (13 Aug 2025) and NOAA-15 (19 Aug 2025) [3]. Meteor-M N2-3 and N2-4 transmit LRPT on
  **137.9 MHz** (QPSK, 72 kBd, ≈ 120 kHz) [4]; N2-3's antenna only partly deployed, so its signal is weaker [5].
- **Kit and cost**: rung-1 SDR; a **V-dipole** (two 53.4 cm arms at 120°, horizontal, the V's axis
  north–south, ≈ US$5–20) [5] or a home-built **QFH** (≈ US$20–30 in PVC and copper; wider sky coverage,
  circular polarisation, more fiddly to build); optional 137 MHz filtered LNA with bias tee
  (≈ US$30). Software: SatDump (decoding and pass scheduling) or Gpredict for predictions.
- **Steps**: (1) predict passes and pick one above ≈ 30° maximum elevation; (2) put the antenna outside,
  away from walls, ~1–2 m up; (3) record or live-decode at ≥ 1 MS/s centred near 137.9 MHz; (4) let
  SatDump lock the QPSK demodulator and build the image; (5) repeat for several passes, noting maximum
  elevation, SNR and how many image lines decode.
- **Predict, then measure**: Doppler sweeps ≈ ±3.0 kHz over a pass (script) — inside the demodulator's
  pull-in range; a linear antenna on a circularly polarised satellite costs a steady 3 dB, which the
  V-dipole designer accepts in exchange for rejecting vertically polarised terrestrial interference [5].
- **What you learn**: LEO geometry and pass prediction, polarisation, Doppler, why an antenna pattern
  pointed at the sky beats a higher-gain one pointed at the horizon.
- **KB links**: [reception recipes (Meteor)](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md),
  [helical antennas and QFH](../08-antennas/helical-antennas.md),
  [polarisation mismatch](../09-propagation-link-budget/polarization-mismatch-loss.md).

### Rung 4 — build and tune a 433 MHz dipole with a NanoVNA
- **Goal**: make an antenna, measure its impedance and resonance, and learn calibration.
- **Kit and cost**: NanoVNA-H4 (≈ US$110 [6]) with its SOL standards; an SMA chassis socket; 2 mm copper
  or brass wire; two snap-on ferrite cores (≈ US$5); a short RG-316 jumper.
- **Steps**: (1) calibrate SOL **at the end of the jumper** (not at the instrument); (2) solder two arms of
  ≈ 170 mm (≈ 3 % long) to the socket; (3) sweep 380–480 MHz and find the S11 minimum; (4) trim both arms
  equally, 2 mm at a time, recording resonant frequency vs total length; (5) clip the ferrites on the
  cable next to the feed and repeat; (6) do the "grab the cable" test — if the trace moves, common-mode
  current is flowing.
- **Predict, then measure**: resonance at ≈ 327.9 mm tip-to-tip for 2 mm wire, R ≈ 72 Ω, VSWR ≈ 1.44 on
  50 Ω (mismatch loss 0.14 dB), VSWR-2 bandwidth ≈ 8 % (≈ 35 MHz) ([dipoles](../08-antennas/dipoles-and-monopoles.md)).
  Plot f vs 1/length — it should be close to a straight line.
- **What you learn**: resonance, impedance, return loss vs VSWR, calibration planes, baluns and cable
  currents.
- **KB links**: [NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md),
  [antenna measurement](../08-antennas/antenna-measurement.md),
  [antenna matching and baluns](../08-antennas/antenna-matching-and-baluns.md),
  [choosing LoRa antennas](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md).

### Rung 5 — measure cable loss and velocity factor
- **Goal**: see that a cable is a component with loss, delay and its own impedance.
- **Kit and cost**: NanoVNA; 2–10 m each of RG-58, RG-316 and (if you have it) LMR-240; an SMA
  load. (Offcuts are fine.)
- **Steps**: follow [NanoVNA Recipe D](../17-test-measurement/nanovna-librevna-practical.md): open-ended
  cable on CH0; find the first frequency where S11 phase passes −180° (the quarter-wave dip); compute
  $v_f$; read the open-end return loss at 433 and 915 MHz and halve it for one-way loss; try the TDR
  mode to find the open end; then measure your rung-4 dipole through 10 m of RG-58 and watch the cable
  "improve" its SWR.
- **Predict, then measure**: a 2.000 m PTFE cable (v_f 0.695) dips at 26.0 MHz (script); RG-58 (v_f 0.66)
  at 24.7 MHz; one-way loss per 10 m ≈ 2.9 dB (RG-58) and 7.2 dB (RG-316) at 433 MHz
  ([coax and cables](../03-transmission-lines-matching/coax-and-cables.md)). Through 10 m of RG-58, an
  antenna with 11.9 dB return loss reads ≈ 17.7 dB at the radio end.
- **What you learn**: velocity factor, loss rising with frequency, why SWR is measured at the antenna.
- **KB links**: [coax and cables](../03-transmission-lines-matching/coax-and-cables.md),
  [time-domain reflectometry](../03-transmission-lines-matching/time-domain-reflectometry.md),
  [reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md).

### Rung 6 — a tinySA look at a LoRa transmitter (conducted, no antenna)
- **Goal**: measure a real transmitter's power, frequency, bandwidth, time on air and harmonics safely.
- **Kit and cost**: tinySA Ultra (≈ US$120–130 [6]); a 30–40 dB, ≥ 2 W SMA attenuator plus a 10–20 dB
  pad (≈ US$20–60, marketplace); the LoRa module or dev board; short SMA cables.
- **Steps**: (1) connect module → 40 dB power attenuator → tinySA **before** powering the module;
  (2) set the module to a fixed channel and a repeating packet; (3) measure the carrier frequency and
  ppm error (CW or the chirp centre); (4) zero-span, RBW ≥ 300 kHz for power ([bench recipe R6](../17-test-measurement/bench-measurement-recipes.md));
  (5) sweep 125/250/500 kHz bandwidths and SF7–12 and compare the burst length with the time-on-air
  calculator; (6) look for 2f and 3f with **another 20 dB** of attenuation so the analyzer works in its
  linear range.
- **Predict, then measure**: 33 dBm − 40 dB = −7 dBm at the tinySA (safe: absolute max +6 dBm, suggested
  ≤ 0 dBm, best linearity below −25 dBm [8]); time on air for 32 bytes at SF9/125 ≈ 247 ms
  ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)); harmonics after the module's filter should be
  far below the carrier — compare with the spurious limits in the [filter recipe](bandpass-filter-design-walkthrough.md).
- **What you learn**: RBW/VBW, detector modes, attenuator safety, what a chirp looks like, ppm errors.
- **KB links**: [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md),
  [RF power measurement](../17-test-measurement/rf-power-measurement.md),
  [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md).

### Rung 7 — a LoRa point-to-point range test that teaches something
- **Goal**: predict a link, test it, and explain the difference.
- **Kit and cost**: two LoRa boards (e.g. Heltec LoRa 32 V3, RAK4631 or an SX1262 module + MCU; ≈ US$20–40
  each, marketplace) with GNSS or a phone logging position; the rung-4 dipoles; optional step attenuator;
  a 2–6 m mast or a tall tripod.
- **Steps**: (1) choose a **legal** band and power (Singapore exempt: 433 MHz ≤ 10 mW e.r.p.; 866–869 MHz
  ≤ 500 mW e.r.p.; 917–925 MHz ≤ 100 mW e.r.p. and ≤ 1 % duty); (2) write the prediction down;
  (3) fixed transmitter sending a sequence number every few seconds; mobile receiver logging RSSI, SNR,
  sequence and position; (4) walk or drive out along an open road, then repeat with one end on the mast;
  (5) plot packet error rate vs SNR and RSSI vs log-distance. Fit the exponent from the transmitter's sequence numbers *including the lost packets* (censored/Tobit fit): a least-squares fit to received packets alone is biased low — n = 1.7 for a true 3.5 in the KB's simulation ([tool landscape Example 5](../16-simulation-tools/tool-landscape-overview.md)). For a long-range equivalent without
  travelling, insert a known attenuation at the receiver ([bench recipe R8](../17-test-measurement/bench-measurement-recipes.md),
  [telemetry-link range test](lora-rocket-telemetry-link.md)).
- **Predict, then measure** (script §11): two 1.5 m-high dipoles at 433.92 MHz, 10 mW e.r.p., SF9/125
  (sensitivity −129.5 dBm): the two-ray breakpoint is only 13 m, the received power at 1 km ≈ −99 dBm
  (30.8 dB margin) and the range with 10 dB fade margin ≈ **3.3 km**; with one end on a 6 m mast,
  ≈ 6.6 km. The slope beyond the breakpoint should be ≈ 40 dB/decade.
- **What you learn**: link budgets, ground reflection, why height beats power, SNR vs RSSI near
  sensitivity, fading statistics.
- **Caution**: if you use Meshtastic, turn off MQTT uplink/downlink and check the packet's `via_mqtt` flag;
  internet-bridged packets carry a far-away node's position but a nearby gateway's RF reception, which
  produces impossible "ranges" ([LoRa link budget — common mistakes](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).
- **KB links**: [LoRa sensitivity and link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md),
  [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md),
  [band plans and duty cycle](../15-lora-ism-radios/ism-band-plans-duty-cycle.md),
  [choosing LoRa antennas (A/B tests)](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md).

### Rung 8 — monitor your own LoRa link with an SDR (gr-lora_sdr)
- **Goal**: see and decode LoRa in software; measure what the modules do not report.
- **Kit and cost**: the rung-1 SDR (or a Pluto/Airspy), GNU Radio 3.10 with gr-lora_sdr; your rung-7
  transmitter at legal power or through attenuators.
- **Steps**: (1) record IQ (SigMF) around the channel, offset-tuned so the DC spike is outside it;
  (2) view the chirps in a spectrogram and read SF from the chirp duration ($2^{SF}/BW$); (3) decode with
  gr-lora_sdr (SF5–12 supported; SF5–6 are not compatible with SX126x chips) [9]; (4) measure carrier offset
  (ppm), SNR and packet error rate vs attenuation; compare with the module's RSSI/SNR reports.
- **Predict, then measure**: SF7/125 symbols last 1.024 ms, SF12/125 32.8 ms; a 1 ppm SDR clock error is
  433 Hz at 433 MHz — record the transmitter on the bench first as a reference
  ([SDR receiver recipe](sdr-receiver-build.md)).
- **What you learn**: chirp spread spectrum, sample rates and decimation, ppm budgets, IQ recording.
- **KB links**: [reception recipes (LoRa)](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md),
  [GNU Radio stack](../14-sdr-dsp/gnu-radio-and-software-stack.md),
  [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md).

### Rung 9 — an HB100 Doppler speed radar
- **Goal**: build a working microwave sensor; learn Doppler, mixing and low-noise analog gain.
- **Kit and cost**: HB100 module (10.525 GHz, 20 dBm EIRP, single mixer output) (≈ US$5–15, marketplace);
  a two-stage low-noise op-amp IF amplifier (≈ 70–80 dB total, AC-coupled) with a band-pass filter; an
  MCU ADC or a PC sound card; Python for the FFT.
- **Steps**: (1) power the HB100 from a clean 5 V; (2) build the amplifier in two stages so the first
  stage's offset cannot saturate the second; (3) band-pass ≈ 6–600 Hz for people (≈ 2.5 kHz for cars);
  (4) sample at ≥ 2.5 × the highest Doppler; take 0.25 s FFTs (4 Hz bins); (5) calibrate with a reflector
  on a pendulum, then measure walkers and cars, noting the cosine error.
- **Predict, then measure**: 70.2 Hz per m/s = 19.5 Hz per km/h (script): a walker at 1.4 m/s → 98 Hz; a car
  at 50 km/h → 975 Hz. Expect detection of a person out to ≈ 15–20 m with a simple analog detector
  ([CW and Doppler](../11-radar/cw-and-doppler-radar.md)).
- **Legal note**: in Singapore the 10.50–10.55 GHz radio-determination allowance (≤ 117 dBµV/m at 10 m)
  covers an HB100 (≈ 105 dBµV/m); 24 GHz radar *guns* are not allowed under the non-specific SRD item —
  check before building a "speed gun" ([CW and Doppler legal note](../11-radar/cw-and-doppler-radar.md)).
- **What you learn**: homodyne receivers, why a single mixer cannot tell direction, audio-band low-noise
  design, FFT resolution.
- **KB links**: [DIY radar hardware](../11-radar/diy-radar-hardware.md),
  [radar range equation](../11-radar/radar-range-equation.md),
  [low-noise analog design](../05-analog-electronics/low-noise-analog-design.md).

### Rung 10 — a 2.4 GHz patch antenna on JLC FR-4
- **Goal**: design a printed antenna, order it, and close the loop between formula, simulation and
  measurement.
- **Kit and cost**: a JLCPCB 2-layer 1.6 mm FR-4 board (a few US$ for 5 boards plus shipping); SMA edge or
  end-launch connector; a VNA that reaches 2.5 GHz properly — **LiteVNA 64 (≈ US$190) or NanoVNA V2 Plus4**,
  since the NanoVNA-H4 is weak above ~1.5 GHz [6]; optional openEMS.
- **Steps**: (1) size the patch from the closed form for εr ≈ 4.4 (the KB's verified design is
  37.23 × 28.81 mm with a probe 8.3 mm from the edge [7]); (2) put **three variants** on one panel
  (nominal, −2 %, +2 % length) because FR-4 εr and thickness vary; (3) optionally simulate in openEMS;
  (4) measure S11 on the VNA with the board away from the bench; (5) compare the resonance with the
  closed form and the simulation.
- **Predict, then measure**: the KB's 2.45 GHz FR-4 reference resonated 2.2 % low in openEMS
  (2.397 GHz) with ≈ 2.6 % bandwidth and ≈ 40–45 % efficiency [7]; expect your board within ±3 % and
  explain the offset with εr ([JLC manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)).
- **What you learn**: printed antennas, substrate tolerance, the value of fabricating variants, simulation
  validation.
- **KB links**: [patch walkthrough (with the 2.45 GHz reference)](patch-antenna-design-walkthrough.md),
  [patch antennas](../08-antennas/patch-antennas.md),
  [openEMS workflow](../16-simulation-tools/openems-workflow.md),
  [simulation validation](../16-simulation-tools/simulation-validation.md).

### Rung 11 — direction finding: KrakenSDR or two coherent SDR channels
- **Goal**: measure a bearing from phase; meet calibration, ambiguity and multipath.
- **Kit and cost**: **KrakenSDR** (5 coherent channels, built-in noise-source calibration, ≈ US$750) with
  five whips on a uniform circle (radius 23.6 cm at 433 MHz for spacing 0.4 λ); or a cheaper two-channel
  route — Pluto Rev C/D second channel, a B210, or two RTL-SDRs on a shared clock with a noise source
  ([DIY arrays](../12-phased-arrays/diy-phased-array-projects.md)); a legal 433 MHz beacon (rung 7 board at
  10 mW e.r.p.).
- **Steps**: (1) two-channel: place two whips λ/2 apart (34.5 cm at 433 MHz); calibrate the phase offset
  with the beacon at broadside; (2) move the beacon to known bearings (0°, ±30°, ±60°) and compute θ from
  Δφ; (3) KrakenSDR: run the DoA software (MUSIC) and log bearings; (4) repeat near buildings to see
  multipath.
- **Predict, then measure**: with d = λ/2 a 10° phase error is 3.2° of bearing at broadside; with d = λ a
  source at 20° aliases to −41° ([DIY arrays](../12-phased-arrays/diy-phased-array-projects.md)); field
  accuracy 1–5° once calibrated ([phased-array starter](phased-array-starter-build.md)).
- **What you learn**: steering vectors, coherence, calibration, ambiguity, why recovery DF works.
- **KB links**: [adaptive beamforming and DOA](../12-phased-arrays/adaptive-beamforming-doa.md),
  [array calibration](../12-phased-arrays/array-calibration.md),
  [phased-array starter build](phased-array-starter-build.md).

## Practical notes
- **Keep a lab notebook with predictions first.** For each rung write the predicted number, its tolerance
  and what each outcome would mean *before* measuring — the same discipline the full recipes use.
- **Shared accessories** (buy once, ≈ 15–25 % of the instrument budget): 50 Ω load, 30–40 dB / 2 W
  attenuator, 10 dB pad, SMA gender changers (SMA vs RP-SMA!), a torque wrench, ferrite clamp cores, RG-316
  jumpers ([lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md),
  [connectors](../18-components-parts/connectors-and-cables-parts.md)).
- **Safety**: no transmitter without a load; keep hands off transmitting antennas; even 2 W into a Yagi
  needs a ≈ 1 m keep-out ([RF exposure safety](../19-regulations-safety/rf-exposure-safety.md)); ESD-safe
  handling of LNAs and SDR inputs ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).
- **Front-end protection**: near your own transmitter, add a pad or a filter in front of the SDR; strong
  nearby signals cause phantom signals and can damage inputs
  ([SDR front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)).
- **Where next**: after rung 7 → [LoRa telemetry link](lora-rocket-telemetry-link.md); after rung 8 →
  [SDR receiver](sdr-receiver-build.md); after rung 9 → [FMCW radar](fmcw-radar-build.md); after rung 10 →
  [GNSS patch walkthrough](patch-antenna-design-walkthrough.md); after rung 11 →
  [phased-array starter](phased-array-starter-build.md).
- **Also worth a weekend**: rtl_433 on 433.92 MHz to see weather stations and tyre sensors (a template for
  a custom beacon decoder); listening to the ISS on 145.800 MHz during an SSTV event
  ([reception recipes](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md)).

## Common mistakes & misconceptions
- **"Any antenna sold for 868/915 MHz is tuned for my band."** Measure it (rung 4); many cheap antennas are
  off-band or mistuned ([choosing LoRa antennas](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md)).
- **"My NOAA project stopped working, so my SDR is broken."** NOAA-15/18/19 were decommissioned in 2025;
  move to Meteor-M LRPT.
- **"Wavy, slanted weather images mean a bad antenna."** For APT recordings this was usually sample-clock
  (ppm) error or Doppler; for LRPT, dropouts usually mean low elevation, multipath or interference.
- **"Calibrating at the NanoVNA port is fine."** Calibrate at the end of the cable you measure through, or
  the cable's delay and loss end up in the result.
- **"A good SWR proves a good antenna."** A 50 Ω dummy load has a perfect SWR and radiates nothing; S11
  says matched, not efficient (Meshtastic's antenna docs make the same point).
- **"Connect the transmitter straight to the tinySA, it's only 100 mW."** 20 dBm exceeds its +6 dBm absolute
  maximum by 14 dB.
- **"The range test proves the radio's range."** Ground-to-ground at 1.5 m measures ground reflection and
  clutter; a rocket in flight is line of sight with very different numbers
  ([LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).
- **"Meshtastic says I reached 400 km, so LoRa does that."** Check `via_mqtt`; internet bridging produces
  such "records".
- **"The HB100 sees nothing, so it's dead."** Its output is microvolts; it needs 70–80 dB of gain and a
  moving target.

## How to simulate / verify
- `python3 tools/verify/e6_beginner_numbers.py` — wavelengths, whip/dipole/V-dipole lengths, velocity factor
  from the quarter-wave dip, kTB floors, ADS-B horizon, HB100 Doppler, Meteor/ISS Doppler, two-ray range
  prediction for rung 7 (43/43 PASS).
- `python3 tools/verify/e6_lora_antennas.py` — A/B RSSI sample sizes and the interleaving check used in
  rung 7; mismatch and feeder tables (20/20 PASS).
- `python3 tools/verify/e6_gain_staging.py` — SDR gain setting rule used in rungs 1–3 and 8 (27/27 PASS).
- Antenna rungs: NEC/MoM models of the dipole ([NEC modelling](../16-simulation-tools/nec-antenna-modelling.md));
  the patch in openEMS ([openEMS workflow](../16-simulation-tools/openems-workflow.md)).

## Open questions / gaps
- Marketplace prices (HB100, attenuators, LoRa boards, QFH materials) are unverified 2026 snapshots.
- Rung 0 (discrete first radio) was added 2026-10-13 (W5-S14) as a pointer to 06/receiver-architectures; it has
  no measured team result yet, and the module figures it relies on are seller claims.
- Meteor-M operating frequencies and modes change; check a current status page before a session.
- Two-ray predictions assume flat open ground; no Singapore field data have been logged in the KB yet —
  the first team range test should be added here as a measured example.
- The Singapore legality of every rung was taken from the 19 and 11 pages, not re-read against IMDA
  documents for this page.

## Sources
1. This KB: [dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md) (433 MHz MoM resonance 327.9 mm, 72 Ω, 8.2 % bandwidth), [NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md) (Recipe D), [coax and cables](../03-transmission-lines-matching/coax-and-cables.md), [bench recipes R6/R8](../17-test-measurement/bench-measurement-recipes.md), [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md), [CW and Doppler radar](../11-radar/cw-and-doppler-radar.md) and [DIY radar](../11-radar/diy-radar-hardware.md) (HB100 facts and SG legality), [DIY phased arrays](../12-phased-arrays/diy-phased-array-projects.md), [LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md), [Singapore rules](../19-regulations-safety/singapore-imda-rules.md), [signal catalogue](../14-sdr-dsp/signal-identification-and-spectrum-survey.md) (AIS/APRS parameters). (internal)
2. Community demand for a project ladder: [gaps/D2-reddit.md](../../gaps/D2-reddit.md) §2 rank 5 (10 posts), [gaps/D1-stackexchange.md](../../gaps/D1-stackexchange.md) #24, [gaps/D4-curriculum.md](../../gaps/D4-curriculum.md) §4 (no Level-0 project rung). (gap analyses)
3. NOAA OSPO, "Decommissioning of NOAA-15 & NOAA-19" (message, 20 Aug 2025) https://ospo.noaa.gov/data/messages/2025/08/MSG_20250820_1410.html ; NOAA NESDIS, "Suspension of POES data to users after June 16, 2025 and decommissioning" https://www.nesdis.noaa.gov/news/suspension-of-poes-data-users-after-june-16-2025-and-decommissioning (operator notices; search summaries)
4. USRadioguy, "Meteor M series" status page (M2-3 and M2-4 LRPT 137.9 MHz, 72k, active; updates to Sept 2025) https://usradioguy.com/meteor-satellite/ ; Signal Identification Wiki, "Low Rate Picture Transmission (LRPT)" (QPSK, 72 kBd, 120 kHz) https://www.sigidwiki.com/wiki/Low_Rate_Picture_Transmission_(LRPT) (community sites; fetched 2026-10-02)
5. RTL-SDR.com, "Simple NOAA/Meteor weather satellite antenna: a 137 MHz V-dipole" (9A4QV design: 120°, horizontal, N–S, linear vs CP trade, claimed terrestrial rejection) https://www.rtl-sdr.com/simple-noaameteor-weather-satellite-antenna-137-mhz-v-dipole/ ; RTL-SDR.com, "Meteor M2-3 now in orbit…" (antenna deployment issue) (community/manufacturer blog)
6. This KB, [lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md) and [NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md) — NanoVNA-H4 ≈ US$110, LiteVNA ≈ US$190, tinySA Ultra ≈ US$120–130, H4 range limits. (internal, vendor-sourced)
7. This KB, [patch walkthrough §4](patch-antenna-design-walkthrough.md) and [openEMS workflow](../16-simulation-tools/openems-workflow.md) — 2.45 GHz FR-4 reference patch 37.23 × 28.81 mm, openEMS 2.397 GHz, efficiency 40–45 %. (internal, verified by `tools/verify/sim_openems_patch.py`)
8. tinySA Ultra specifications as recorded on the [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md) page — absolute max +6 dBm, suggested ≤ 0 dBm, best linearity below −25 dBm. (manufacturer, via KB)
9. J. Tapparel et al., gr-lora_sdr README (SF5–12; SF5/6 not SX126x-compatible; CR, implicit/explicit header, LDRO) https://github.com/tapparelj/gr-lora_sdr ; Tapparel et al., SPAWC 2020. (software docs; README read 2026-10-02)
10. Meshtastic protobufs, `mesh.proto` (`MeshPacket.via_mqtt`) https://github.com/meshtastic/protobufs (project source; read 2026-10-02)
