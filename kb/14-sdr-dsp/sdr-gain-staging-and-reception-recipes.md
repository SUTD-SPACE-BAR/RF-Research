---
title: SDR gain staging and reception recipes — setting LNA/mixer/VGA gain, AGC, overload signs, phantom signals, bias-tee LNAs, a dynamic-range demonstration, and step-by-step recipes for ADS-B, AIS, APRS, Meteor-M weather satellites, the ISS, LoRa (gr-lora_sdr) and rtl_433
domain: 14-sdr-dsp
slug: sdr-gain-staging-and-reception-recipes
tags: [sdr, rtl-sdr, gain, gain-staging, r820t, r828d, lna-gain, mixer-gain, vga, agc, rtl2832u, noise-floor, floor-lift, overload, clipping, adc, dynamic-range, phantom-signals, harmonics, image, lo-harmonic, bias-tee, masthead-lna, itu-r-p372, ads-b, readsb, dump1090, ais, ais-catcher, aprs, direwolf, meteor-m, lrpt, satdump, noaa-apt, iss, ariss, sstv, lora, gr-lora_sdr, rtl_433, beginner]
prerequisites: [sdr-hardware-survey.md, iq-complex-baseband.md, ../00-math-foundations/rf-concepts-for-beginners.md]
related:
  - sdr-front-end-protection-and-filtering.md
  - signal-identification-and-spectrum-survey.md
  - software-demodulation.md
  - gnu-radio-and-software-stack.md
  - sampling-aliasing-bandpass-sampling.md
  - fft-spectral-analysis-windows.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../17-test-measurement/sdr-as-test-equipment.md
  - ../20-projects-recipes/sdr-receiver-build.md
  - ../20-projects-recipes/beginner-project-ladder.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# SDR gain staging and reception recipes

How to set an SDR's gain so weak signals are heard and strong ones do not break the receiver, how to
tell a real signal from one your receiver invented, when a bias-tee LNA helps, and step-by-step
recipes for the signals every new SDR owner tries first. Strong-signal physics (blocking,
intermodulation, preselectors, protection) is derived on
[SDR front-end protection and filtering](sdr-front-end-protection-and-filtering.md), and the full
catalogue of signal fingerprints is on [signal identification](signal-identification-and-spectrum-survey.md);
this page links to them rather than repeating them. The rocket ground-station case (LNA + SAW + SDR pair)
is worked in [20/sdr-receiver-build](../20-projects-recipes/sdr-receiver-build.md).

## Questions this page answers
- How should I set the RF gain on my RTL-SDR — is more gain always better?
- What do the LNA, mixer and VGA gain settings of the R820T/R828D tuner do?
- Should I turn on AGC (tuner AGC or RTL AGC)?
- What does overload look like on the waterfall, and how do I fix it?
- Why do I hear FM stations at 410 MHz, or a 446 MHz handset while tuned to 2 m?
- Does a bias-tee LNA help, and when does it make things worse?
- How much dynamic range does an 8-bit SDR really have, and how can I see it for myself?
- How do I receive ADS-B, AIS and APRS with an RTL-SDR?
- Can I still receive NOAA weather satellites? How do I decode Meteor-M LRPT?
- How do I hear the ISS?
- How do I decode LoRa packets with gr-lora_sdr, and 433 MHz sensors with rtl_433?
- Does a higher sample rate give better sensitivity?

## TL;DR
- **Gain staging = placing a fixed window.** An 8-bit RTL-SDR's ADC holds ≈ 44 dB over its full 2.4 MHz band (ENOB ≈ 7), ≈ 57 dB in a 125 kHz channel and ≈ 67 dB in 12.5 kHz. Gain slides that window up or down in absolute power; it does not make it bigger.
- **The rule**: raise the gain until the noise floor, with the antenna connected, sits **≈ 5–10 dB above the floor you see at minimum gain or with a 50 Ω load** — then stop. At a 6 dB "floor lift" the ADC costs only ≈ 1 dB of sensitivity; at 10 dB, 0.4 dB; every extra dB of gain after that only lowers the clipping point by 1 dB (script §1; the [SDR receiver recipe](../20-projects-recipes/sdr-receiver-build.md) uses the same 6–10 dB rule).
- **…unless a strong signal sets the limit first.** Monte-Carlo (script §2): with a −75 dBm neighbour, the weak −115 dBm tone reaches within 0.6 dB of its analog limit at a floor lift of ≈ 9 dB; with a −45 dBm neighbour in the passband, the ADC clips before the floor lifts at all, and the best achievable SNR is ≈ 20 dB worse. Fix that with **filtering or attenuation ahead of the SDR**, not with gain.
- **R820T/R828D gain** (osmocom librtlsdr source): 29 settings from 0 to 49.6 dB built by alternating LNA (≤ 33.5 dB) and mixer (≤ 15.3 dB) steps, with the VGA fixed at 16.3 dB in manual mode (26.5 dB with tuner AGC). The numbers are relative steps measured at 928 MHz, not calibrated gain.
- **AGC off** for anything you want to measure or decode in bursts; set gain manually ([hardware survey](sdr-hardware-survey.md)).
- **Phantom signals** are mostly receiver products: FM harmonics (102.5 MHz × 4 = 410 MHz), tuner LO-harmonic responses (tuned to 145 MHz, a 446 MHz handset appears; tuned to Meteor's 137.9 MHz, 421–428 MHz signals can leak in), IQ images, clock spurs. **The 10 dB pad test** sorts them: real signals drop 10 dB, an n-th-order product 10n dB ([front-end page](sdr-front-end-protection-and-filtering.md)).
- **A masthead LNA helps where the receiver's noise dominates**, not where the environment's does: ≈ +14 dB SNR for ADS-B at 1090 MHz (RTL NF ≈ 12 dB, 2.5 dB of cable), but only ≈ 0.2–1.7 dB for 137 MHz weather satellites in city to rural man-made noise (≈ 4 dB at a galactic-noise-limited site) (script §5, ITU-R P.372) — while adding overload risk.
- **Recipes** (below): ADS-B 1090 MHz (readsb/dump1090); AIS 161.975/162.025 MHz (AIS-catcher); APRS 144.390 MHz in Singapore/Malaysia (Dire Wolf); **Meteor-M LRPT 137.9 MHz** (SatDump; NOAA APT ended in 2025); ISS 145.800 / 145.825 / 437.800 MHz; LoRa with gr-lora_sdr; 433.92 MHz sensors with rtl_433.

Numbers marked "script" are from `tools/verify/e6_gain_staging.py` (27/27 PASS).

## Intuition (no math)
Picture the receiver's usable range as a **window** of fixed height on a ladder of signal levels. The
bottom of the window is the noise floor; the top is where the ADC clips. Turning the gain knob does not
make the window taller — it moves the ladder. Too little gain and weak signals sit below the bottom of
the window, buried in the ADC's own quantisation noise. Too much gain and the strongest signal on the
band hits the top, the ADC clips, and the clipping smears junk over everything.

The right setting is therefore "just enough": enough that the antenna's noise (amplified) sits clearly
above the ADC's noise — you see the floor rise when you connect the antenna — and no more. Past that
point the receiver is as sensitive as its analog front end allows, and any further gain only throws away
headroom. If a strong signal shares the band, you may never reach that point; then the cure is to remove
the strong signal before the ADC (a filter, a notch, a different antenna, an attenuator), because no
gain setting can fit both into one window.

Phantom signals are the other half of the story. An overloaded amplifier or a mixer driven by a
square-wave oscillator creates new frequencies that were never transmitted. They behave differently from
real signals when you add attenuation or retune, which is how you catch them.

## The math

### Level 1 — the window, the floor lift and the gain table
**Noise floor and clip level, referred to the antenna.** With a total analog gain $G$ (dB) from antenna
to ADC, an ADC full scale $P_{FS}$ (dBm at the ADC input) and an analog noise figure NF:

$$N_{in}\,[\text{dBm/Hz}] = 10\log_{10}\!\left(10^{(-174+NF)/10} + 10^{(N_{ADC} + P_{FS} - G)/10}\right), \qquad P_{clip} \approx P_{FS} - G - \text{crest margin}.$$

The first term is the antenna/front-end noise; the second is the ADC's own floor
$N_{ADC} = -(6.02\,\text{ENOB} + 1.76) - 10\log_{10} f_s$ dBFS/Hz referred back through the gain. Their
ratio, seen on screen as the **floor lift** $X$ (how far the floor rises above the low-gain/50 Ω floor),
sets the sensitivity penalty the ADC still causes:

$$\Delta_{NF} = 10\log_{10}\!\left(1 + 10^{-X/10}\right).$$

| Floor lift X | 0 dB | 3 dB | 5 dB | 6 dB | 10 dB | 15 dB | 20 dB |
|---|---|---|---|---|---|---|---|
| Sensitivity penalty | 3.0 dB | 1.8 dB | 1.2 dB | 1.0 dB | 0.4 dB | 0.14 dB | 0.04 dB |

So the useful range of the gain knob ends around X ≈ 6–10 dB (script §1).

**The window.** In a channel of bandwidth $B$ the ADC-limited dynamic range is
$6.02\,\text{ENOB} + 1.76 + 10\log_{10}(f_s/B)$ dB: 43.9 dB over 2.4 MHz for ENOB ≈ 7, 56.7 dB in
125 kHz, 66.7 dB in 12.5 kHz ([hardware survey](sdr-hardware-survey.md), script). A 12-bit SDR adds
≈ 26 dB.

**The RTL-SDR tuner gain table** (osmocom librtlsdr, `tuner_r82xx.c` and `librtlsdr.c` [1]):

| Setting | What happens |
|---|---|
| Manual gain value 0 … 49.6 dB (29 steps: 0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6) | the driver alternately steps the **LNA** (16 steps totalling 33.5 dB) and the **mixer** (15.3 dB) until the requested sum is reached; tuner AGC off |
| VGA (IF amplifier) | fixed at **16.3 dB** in manual mode; **26.5 dB** when tuner AGC is on |
| Tuner AGC ("auto gain") | the R820T's own loops set LNA and mixer gain from the signal it sees |
| RTL2832U digital AGC (`rtlsdr_set_agc_mode`) | a separate digital gain inside the demodulator chip, designed for DVB-T |

The step sizes were measured by the driver authors at 928 MHz with −60 dBm input [1]; treat the
displayed number as a relative index. The *absolute* antenna-referred clip level and noise floor must be
measured (a signal generator and a step attenuator, or the noise-rise test in the
[SDR receiver recipe](../20-projects-recipes/sdr-receiver-build.md)).

### Level 2 — the dynamic-range demonstration (Monte-Carlo, script §2)
A complex 8-bit ADC (ENOB 7 at 2.4 MS/s, extra converter noise added to match), an analog NF of 4.5 dB,
a weak −115 dBm tone and a stronger in-band neighbour. "Total gain" is antenna → ADC, referenced so
that 0 dBm at the ADC is full scale; analog noise equals the ADC floor at G = 61.8 dB in this model.

| Total gain G (dB) | 30 | 50 | 62 | 66 | 70 | 74 | 78 |
|---|---|---|---|---|---|---|---|
| **A — neighbour at −75 dBm**: weak-tone SNR in 12.5 kHz (dB) | −22.0 | 1.4 | 10.6 | 12.1 | 12.9 | 13.2 | −5.5 (clipped) |
| floor lift over the low-gain floor (dB) | 0 | 0.3 | 3.1 | 5.6 | 8.8 | 12.5 | — |
| **B — neighbour at −45 dBm**: weak-tone SNR (dB) | −18.8 | lost (ADC clips from G = 46) | lost | lost | lost | lost | lost |

The analog-only limit for the weak tone is 13.5 dB. In A, SNR rises dB-for-dB while the ADC dominates,
reaches within 0.6 dB of the limit at a 9 dB floor lift, and collapses when the −75 dBm neighbour clips
(clipping spurs at −18 dBc). Going from 62 to 70 dB of gain (floor lift 3 → 9 dB) buys only 2.3 dB. In
B the strong neighbour reaches full scale at G ≈ 45 dB, so the best usable setting (G = 42 dB) gives
−6.4 dB — about 20 dB short — because the 70 dB spread plus 10 dB SNR (80 dB) exceeds the 66.7 dB window.

**Does a masthead LNA help? (script §5)** System temperature $T_{sys} = T_a + T_{LNA} + (T_{cable} + L\,T_{SDR})/G_{LNA}$,
with the antenna temperature $T_a$ from ITU-R P.372 man-made noise lines
($F_{am} = c - 27.7\log_{10}f_{MHz}$) and the measured RTL-SDR V3 noise figures (5.8 dB at 145 MHz, 11.9 dB
at 1280 MHz [2]):

| Case | $T_a$ | 5 m RG-58 | SNR gain from a 1 dB / 20 dB masthead LNA |
|---|---|---|---|
| Meteor 137.9 MHz, city (Fam 17.5 dB) | 16 400 K | 0.74 dB | 0.2 dB |
| Meteor 137.9 MHz, residential (13.2 dB) | 6 100 K | 0.74 dB | 0.6 dB |
| Meteor 137.9 MHz, rural (7.9 dB) | 1 800 K | 0.74 dB | 1.7 dB |
| Meteor 137.9 MHz, galactic noise only | 550 K | 0.74 dB | 3.9 dB |
| ADS-B 1090 MHz, sky/ground ≈ 150 K | 150 K | 2.5 dB | 14.2 dB |

At VHF in towns the environment, not the SDR, sets the floor; an LNA there mainly helps by allowing a long
feeder and by carrying a filter. At L-band the SDR's own noise dominates and an LNA is a large win
([thermal noise and P.372](../07-noise-linearity/thermal-noise-and-noise-temperature.md),
[noise figure and Friis](../07-noise-linearity/noise-figure-and-friis.md)).

### Level 3 — where the simple rule breaks
- **Out-of-band blockers.** A strong signal that the tuner's IF filter removes never reaches the ADC, so
  neither the waterfall nor any AGC sees it — but it can still compress the LNA or mixer and raise the
  floor everywhere. Symptom: the floor rises and weak signals vanish when a nearby transmitter keys up,
  although nothing is visible in the span ([front-end page](sdr-front-end-protection-and-filtering.md)).
- **Gain-dependent NF and linearity.** On a real tuner the noise figure improves at high LNA gain and
  linearity worsens; the best setting can be a few steps away from the "floor lift" point. Measure SNR or
  decode rate, not only the floor.
- **AGC dynamics.** AGC loops act on the average power: a bursty signal (ADS-B, AIS, LoRa) arrives
  before the loop reacts, and a strong burst can pump the gain down and lose the next weak one.
- **Quantisation without noise.** At very low gain the ADC sees less than one LSB of noise and creates
  harmonically related spurs from strong tones (the −40 dBc spur at G = 30 dB in scenario A); real dongles
  hide this with their own noise, but it is why "minimum gain" is not "cleanest".
- **Sample rate does not buy sensitivity.** The noise in a channel depends on the channel bandwidth, not
  on $f_s$; a higher rate only spreads the same ADC window over more spectrum (processing gain falls back
  in each narrowband channel). Above ≈ 2.4–2.56 MS/s an RTL-SDR also drops samples over USB
  ([hardware survey](sdr-hardware-survey.md), [FFT scaling](fft-spectral-analysis-windows.md)).
- **Direct-sampling (HF) mode** on V3 dongles bypasses the tuner: signals above 14.4 MHz alias in from
  other Nyquist zones unless low-pass filtered ([sampling](sampling-aliasing-bandpass-sampling.md)).

## Design equations & rules of thumb
| Rule | Value | Source |
|---|---|---|
| Set gain by floor lift | 5–10 dB above the 50 Ω / minimum-gain floor; ≤ 1 dB sensitivity penalty at ≥ 6 dB | script §1–2; [SDR receiver](../20-projects-recipes/sdr-receiver-build.md) |
| Strong signal present | highest gain that keeps the strongest in-band signal ≤ −6 dBFS peak; otherwise filter it out | script §2 B |
| 8-bit window | ≈ 44 dB full band; 57 dB in 125 kHz; 67 dB in 12.5 kHz | [hardware survey](sdr-hardware-survey.md); script |
| AGC | off for measurement, bursts and decoding; manual gain | [1], [hardware survey](sdr-hardware-survey.md) |
| Pad test | real signal −10 dB; n-th-order product −10n dB | [front-end page](sdr-front-end-protection-and-filtering.md) |
| Retune test | real signal stays at its absolute frequency; IQ image moves the other way; LO-harmonic response moves by k× | [front-end page](sdr-front-end-protection-and-filtering.md), [signal ID](signal-identification-and-spectrum-survey.md) |
| 50 Ω test | anything still present with a load on the input is internal (clock spurs at 28.8 MHz multiples, USB noise) | [signal ID](signal-identification-and-spectrum-survey.md) |
| LNA worth it? | big win at ≥ 1 GHz or behind long feeders; small at VHF in towns | script §5 |
| Bias tee | RTL-SDR Blog: 4.5 V, ≤ 180 mA; never into a DC-shorted antenna or an instrument | [front-end page](sdr-front-end-protection-and-filtering.md) |
| Max input | R820T chip +10 dBm; HackRF −5 dBm: damage limits, stay ≥ 20 dB below | [front-end page](sdr-front-end-protection-and-filtering.md) |

## Worked examples
**1. Setting gain for ADS-B in a city.** Connect the 1090 MHz antenna, start at the lowest gain and note
the floor in the readsb/SDR++ display; step up until the floor rises ≈ 6–10 dB (on many dongles this is in
the upper third of the table, 33–44 dB). Then watch messages per second at that setting and one or two
steps either side: the maximum message rate, not the maximum gain, is the answer. If messages *drop* at
high gain while the floor jumps, a strong out-of-band signal (cellular downlinks near 900 MHz, broadcast
TV) is compressing the tuner: add a 1090 MHz band-pass or a filtered ADS-B LNA at the antenna (≈ +14 dB SNR
from the LNA alone, script §5).

**2. Weak satellite, strong pager.** A Meteor pass at −115 dBm in 120 kHz while a 2 m-band pager or
land-mobile transmitter delivers −45 dBm into the antenna inside the 2.4 MHz capture: the 70 dB spread plus
the decoder's SNR exceeds the RTL's window, as in scenario B. Fixes in order: narrow the capture (1 MS/s
centred on 137.9 MHz keeps more signals out of the ADC), add a 137 MHz band-pass at the SDR, use a
horizontally polarised antenna (V-dipole) to reject vertical land-mobile signals, or move the antenna.
Turning the gain up makes it worse.

**3. Is that FM station at 410 MHz real?** Tune away by 100 kHz: it stays at 410.0 MHz (not an image or
LO response). Its audio is distorted and wide (≈ 4 × 75 kHz deviation). Insert a 10 dB pad: it drops
≈ 40 dB. Verdict: the 4th harmonic of a 102.5 MHz station generated in your tuner; fix with an FM band-stop
filter and less gain ([front-end Example 1](sdr-front-end-protection-and-filtering.md)).

**4. A 446 MHz handset on 2 m.** Tuned to 145 MHz (LO ≈ 148.6 MHz with a 3.57 MHz IF), the tuner's
3rd-LO-harmonic response sits at ≈ 442–449 MHz (script §4), so a nearby PMR446 radio appears on the 2 m
display; retune by 1 MHz and it moves by ≈ 3 MHz. The cure is a 2 m band-pass filter.

**5. See your own dynamic range on the bench.** With a signal generator (or a strong local signal) and a
step attenuator: (i) fix the gain; (ii) record the floor with a 50 Ω load and with the antenna; (iii) step
the generator up in 5 dB steps until the ADC clips (spurs spray across the span, the floor jumps); (iv) the
difference between the clip level and the floor in your channel is your window — compare with 57 dB in
125 kHz; (v) repeat at three gains and plot both lines; they move together.

## Practical notes — reception recipes

### Common set-up for every recipe
1. Manual gain, AGC off, PPM correction set (measure against a known carrier; a 1 ppm error is 1.09 kHz
   at 1090 MHz).
2. Offset-tune so the DC spike is outside the channel ([IQ](iq-complex-baseband.md)).
3. Start with a 50 Ω load to learn your internal spurs, then connect the antenna and do the floor-lift
   check.
4. Record IQ (SigMF) when something interesting happens ([software stack](gnu-radio-and-software-stack.md)).
5. Receiving is unrestricted in most places; check local rules before *sharing* decoded content.

| Signal | Frequency | Modulation / bandwidth | Antenna | Sample rate | Software | Gain hint |
|---|---|---|---|---|---|---|
| ADS-B | 1090 MHz | PPM, 1 Mb/s, ≈ 2 MHz | λ/4 ground plane 68.8 mm, or a collinear; high, clear sky | 2.0–2.4 MS/s | readsb / dump1090 + tar1090 | high; filtered LNA at the antenna is a big win |
| AIS | 161.975 / 162.025 MHz | GMSK 9.6 kb/s, 25 kHz channels | vertical λ/2 ≈ 0.9 m or λ/4 ≈ 45 cm | ≥ 250 kS/s spanning both | AIS-catcher, rtl_ais | moderate; ships near you are strong |
| APRS | 144.390 MHz (SG, MY, N. America), 144.800 (Europe), 145.175 (Australia) | AFSK 1200 b/s on NFM, ≈ 12.5 kHz | vertical 2 m antenna | 24–48 kS/s audio after demod | Dire Wolf, multimon-ng | moderate |
| Meteor-M LRPT | 137.9 MHz (N2-3, N2-4) | QPSK 72 kBd, ≈ 120 kHz | V-dipole (53.4 cm arms, 120°, horizontal, N–S) or QFH | ≈ 1 MS/s | SatDump | floor-lift rule; filter first in towns |
| ISS | 145.800 (voice/SSTV down), 145.825 (APRS/packet), 437.800 MHz (repeater down) | NFM | vertical or small Yagi | 48–250 kS/s | SDR++ + SSTV decoder; Dire Wolf | moderate; Doppler ±3.5 kHz at VHF, ±10.5 kHz at 437.8 MHz |
| LoRa | 433/868/915/923 MHz | CSS, 125–500 kHz | band dipole | 4 × BW after decimation | gr-lora_sdr | floor-lift; beware your own TX |
| 433 MHz sensors | 433.92 MHz (also 315/345/868/915) | OOK/FSK, PWM/Manchester | λ/4 whip ≈ 17 cm | 250 kS/s (default) | rtl_433 | low–moderate |

### Recipe — ADS-B (aircraft)
- **What**: Mode S extended squitter replies at 1090 MHz from aircraft transponders (position, altitude,
  identity) ([signal catalogue](signal-identification-and-spectrum-survey.md)).
- **Steps**: build the 1090 MHz ground plane (68.8 mm whip, four radials); mount it outdoors or high;
  run readsb (or dump1090) at 2.4 MS/s; open the tar1090 map; set gain by message rate (worked example 1).
- **Check**: maximum range in clear directions vs the radio horizon (≈ 439 km from 10 m to 35 000 ft,
  [beginner numbers](../../tools/verify/e6_beginner_numbers.py)); messages/s vs gain.
- **Pitfalls**: loss in thin coax at 1090 MHz (RG-174 ≈ 1.06 dB/m, log-log interpolated between 1.00 dB/m at 1000 MHz and 1.39 at 1575 MHz from the [coax table](../03-transmission-lines-matching/coax-and-cables.md)); cell-band overload — the V4-class
  dongles' input filtering and a 1090 MHz SAW help ([hardware survey](sdr-hardware-survey.md)).

### Recipe — AIS (ships)
- **What**: two 25 kHz channels at 161.975 (AIS 1) and 162.025 MHz (AIS 2), GMSK 9.6 kb/s, short TDMA
  bursts.
- **Steps**: centre between the channels; run AIS-catcher (it decodes both); log positions; compare with
  a public ship map.
- **Check**: VHF line-of-sight range (a 10 m antenna to a 20 m mast ≈ 31 km by the 4/3-Earth formula).
- **Pitfalls**: marine VHF voice and pagers nearby can overload — add a VHF marine band-pass if the floor
  jumps.

### Recipe — APRS (amateur packet)
- **What**: 1200 b/s Bell-202 AFSK packets on narrow-band FM (positions, weather, messages); the regional
  frequency matters — 144.390 MHz in Singapore and Malaysia per community frequency lists [6].
- **Steps**: NFM demodulate in SDR++ (or rtl_fm) and pipe audio into Dire Wolf; or run Dire Wolf on the
  SDR directly; decode packets and paths.
- **Check**: decoded packets per hour vs gain; compare the ISS digipeater (145.825 MHz) during passes.
- **Pitfalls**: audio levels into the decoder matter more than RF gain once the signal is above the floor.

### Recipe — Meteor-M LRPT weather images (NOAA APT is gone)
- **Status**: NOAA-18 (June 2025), NOAA-19 (13 Aug 2025) and NOAA-15 (19 Aug 2025) were decommissioned
  [3], ending 137 MHz APT. Meteor-M N2-3 and N2-4 transmit LRPT on **137.9 MHz** (QPSK, 72 kBd, ≈ 120 kHz)
  and HRPT near 1.7 GHz [4]; N2-3's antenna only partly deployed, so it is weaker [5].
- **Steps**: predict passes (SatDump or Gpredict) and choose ones above ≈ 30° elevation; put a V-dipole
  or QFH outside, away from walls; capture ≈ 1 MS/s around 137.9 MHz; let SatDump's LRPT pipeline lock and
  build the composite; repeat over several passes and compare antennas.
- **Check**: SNR and decoded lines vs elevation; Doppler sweep ≈ ±3.0 kHz over the pass (script in
  [beginner numbers](../../tools/verify/e6_beginner_numbers.py)) — inside the demodulator's pull-in range.
- **Pitfalls**: land-mobile and pager signals in 138–175 MHz overload broadband LNAs — use a filtered
  137 MHz LNA, or none in town (script §5: < 1 dB benefit in city noise); a linear antenna on the CP
  satellite costs 3 dB.
- **Myth**: "wavy or slanted lines mean a bad antenna" — on APT recordings this was usually sample-clock
  (ppm) error or Doppler; on LRPT, gaps usually mean low elevation, multipath or interference.

### Recipe — hearing the ISS
- **Frequencies** (ARISS/AMSAT [7]): 145.800 MHz FM voice and SSTV downlink (worldwide), 145.825 MHz APRS
  and packet, cross-band repeater 437.800 MHz down / 145.990 MHz up (67 Hz tone).
- **Steps**: predict a pass; NFM at 145.800 MHz; for SSTV events, pipe audio into an SSTV decoder; for APRS,
  Dire Wolf on 145.825 MHz.
- **Check**: Doppler is ≈ ±3.5 kHz at 145.8 MHz and ≈ ±10.5 kHz at 437.8 MHz (script) — retune during the
  pass at UHF.
- **Pitfalls**: a vertical antenna has a null overhead; a small hand-held Yagi tracked by hand works best.

### Recipe — monitoring LoRa with gr-lora_sdr
- **What**: decode raw LoRa (including your own rocket telemetry) in GNU Radio; gr-lora_sdr supports SF5–12,
  coding rates, implicit/explicit headers, CRC and low-data-rate optimisation; SF5–6 are not compatible
  with SX126x chips [8].
- **Steps**: offset-tune by $f_s/4$; decimate to an integer multiple of the bandwidth (e.g. 4 × 125 kHz);
  set SF, BW, CR and sync word; record SigMF; compare decoded SNR and carrier offset with the module's
  reports. The full ground-station chain — LNA, SAW, splitter, "high" and "low" SDRs, pad-referenced
  Doppler — is the [SDR receiver recipe](../20-projects-recipes/sdr-receiver-build.md).
- **Pitfalls**: your own transmitter nearby clips the ADC (pad the SDR during bench tests); 1 ppm SDR error
  is 433 Hz at 433 MHz — measure a reference carrier.

### Recipe — rtl_433 (433 MHz sensors and remotes)
- **What**: a generic receiver for ISM-band devices (433.92 MHz by default; also 315, 345, 868 and 915 MHz);
  its README lists about 380 device protocols (Oct 2026) [9].
- **Steps**: `rtl_433` (default 433.92 MHz, 250 kS/s); add `-F json` or `-F csv:log.csv` to log; use
  `-R 0` with the analyzer to study an unknown device's pulses.
- **Use**: survey your launch site's 433 MHz band for bursts before choosing a telemetry channel; a
  template for a custom beacon decoder ([software demodulation](software-demodulation.md)).

### Bias-tee LNAs in practice
Power a masthead LNA over the coax from the SDR's bias tee only after checking: the LNA's current (RTL-SDR
Blog: ≤ 180 mA), that the antenna is not a DC short (folded dipoles, many loops, DC-grounded verticals),
and that no instrument (VNA, generator) is on the same line without a DC block. Choose an LNA with a
**filter built in** for VHF and for any site near transmitters; a wideband 20 dB LNA in front of an RTL-SDR
lowers the strong-signal limit by ≈ 20 dB ([front-end page](sdr-front-end-protection-and-filtering.md)).

## Common mistakes & misconceptions
- **"More gain is always better" / "an SDR can't be overloaded."** Past a 6–10 dB floor lift, gain only
  removes headroom; with a strong in-band signal it destroys reception (script §2) — D2 §3c myth, now
  addressed here.
- **"Auto gain is safest."** Tuner and RTL AGCs are tuned for continuous DVB-T, react slowly to bursts and
  cannot see out-of-band blockers; use manual gain.
- **"A station heard at the wrong frequency is really transmitting there."** Harmonics, LO-harmonic
  responses, images and clock spurs are receiver-made; use the pad, retune and 50 Ω tests.
- **"A higher sample rate gives better sensitivity."** Channel noise depends on channel bandwidth;
  sample rate only sets the span (and RTL-SDRs drop samples above ≈ 2.56 MS/s).
- **"Switching on an LNA always improves reception."** It helps when the receiver's own noise dominates
  (L-band, long feeders, quiet sites); at VHF in towns external noise dominates and the LNA mainly adds
  overload risk (script §5).
- **"NOAA weather pictures stopped, so my set-up is broken."** NOAA-15/18/19 were decommissioned in 2025;
  use Meteor-M LRPT.
- **"Wavy NOAA images mean a bad antenna."** Usually sample-clock/ppm error or Doppler handling.
- **"The centre spike is a signal."** It is the zero-IF DC offset; offset-tune ([IQ](iq-complex-baseband.md)).
- **"Powering an LNA through the bias tee is harmless."** Into a DC-shorted antenna it shorts the supply; into
  a VNA port it can damage the instrument.

## How to simulate / verify
- `python3 tools/verify/e6_gain_staging.py` — floor-lift penalty, antenna-referred window vs gain, the
  8-bit Monte-Carlo dynamic-range demonstration (scenarios A and B), the librtlsdr gain-table algorithm,
  FM-harmonic and LO-harmonic landing table, masthead-LNA benefit vs ITU-R P.372 environment (27/27 PASS).
- `python3 tools/verify/e3_frontend.py` — the strong-signal derivations used by the front-end page.
- `python3 tools/verify/proj_sdr_receiver.py` — the ground-station SDR noise-rise and clip levels (domain 20).
- Bench: worked example 5 above; the noise-rise test R2 in the [SDR receiver recipe](../20-projects-recipes/sdr-receiver-build.md).

## Open questions / gaps
- Measured R820T/R828D noise figure and IIP3 versus gain index at 137/433/1090 MHz are not in the KB; the
  Monte-Carlo uses a fixed NF (4.5 dB) and an ENOB-7 ADC as illustrations.
- The P.372 man-made noise lines date from the 1970s and assume an omnidirectional antenna near the
  ground; a sky-pointing V-dipole sees less of it. A Singapore 137 MHz noise measurement would settle
  the LNA question for the team.
- Meteor-M frequencies and active satellites change; re-check a status page before a campaign.
- rtl_433 decoder count: the current README lists ≈ 380 (now also on [software demodulation](software-demodulation.md),
  updated 2026-10-03 by W5-E9).
- AIS-catcher, Dire Wolf and SatDump option details were not re-read for this page; follow their current
  documentation.

## Sources
1. Osmocom, *rtl-sdr* (librtlsdr) source: `src/tuner_r82xx.c` (LNA/mixer/VGA step tables, VGA 16.3 dB manual / 26.5 dB auto, gains measured at 928 MHz with −60 dBm) and `src/librtlsdr.c` (29-value R82xx gain list, `rtlsdr_set_agc_mode` for the RTL2832 digital AGC). https://github.com/osmocom/rtl-sdr (software source; read 2026-10-02); RTL-SDR.com, "New R820T driver with LNA/mixer/VGA gain settings" (2014) — independent stage control. (community blog)
2. This KB: [SDR hardware survey](sdr-hardware-survey.md) — RTL-SDR V3 measured NF 5.8/5.4/11.9 dB at 145/437/1280 MHz (Libre Space Foundation evaluation), ENOB ≈ 7, 56.7 dB in 125 kHz, manual-gain advice, bias-tee limits; [SDR front-end protection](sdr-front-end-protection-and-filtering.md) — overload kinds, pad test, LO-harmonic responses, 410 MHz example, protection; [signal identification](signal-identification-and-spectrum-survey.md) — AIS/APRS/ADS-B/LRPT parameters and receiver-made artefacts; [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md) — ITU-R P.372-13 Table 1 lines; [SDR receiver recipe](../20-projects-recipes/sdr-receiver-build.md) — noise-rise gain rule. (internal)
3. NOAA OSPO, "Decommissioning of NOAA-15 & NOAA-19" (20 Aug 2025) https://ospo.noaa.gov/data/messages/2025/08/MSG_20250820_1410.html ; NOAA NESDIS, "Suspension of POES data to users after June 16, 2025 and decommissioning". (operator notices; search summaries)
4. USRadioguy, "Meteor M series" (status of M2-3/M2-4: LRPT 137.9 MHz 72k, HRPT 1700 MHz; M2-2 failed) https://usradioguy.com/meteor-satellite/ ; Signal Identification Wiki, "LRPT" (QPSK, 72 kBd, 120 kHz). (community sites; fetched 2026-10-02)
5. RTL-SDR.com, "Simple NOAA/Meteor weather satellite antenna: a 137 MHz V-dipole" (9A4QV) and "Meteor M2-3 now in orbit and transmitting weather images" (partial antenna deployment). (community/manufacturer blog)
6. APRS frequency lists: aprs.world, "APRS frequencies by country — 2026 reference"; hamradio.my, "Understanding emission designators for APRS…" (144.390 MHz in Malaysia/Singapore). (community references — anecdotal)
7. AMSAT, "Amateur radio on the ISS" https://www.amsat.org/amateur-radio-on-the-iss/ ; ARISS operations notices (437.800 down / 145.990 up, PL 67 Hz; 145.825 APRS). (amateur-satellite organisations)
8. J. Tapparel et al., gr-lora_sdr README and "An open-source LoRa physical layer prototype on GNU Radio", IEEE SPAWC 2020. https://github.com/tapparelj/gr-lora_sdr (software docs + peer-reviewed)
9. B. Larsson et al., rtl_433 README (bands, default 433.92 MHz, options, protocol list). https://github.com/merbanan/rtl_433 (software docs; read 2026-10-02)
10. ITU-R P.372-13 (2016), *Radio noise* — via the 07 page. (standard)
