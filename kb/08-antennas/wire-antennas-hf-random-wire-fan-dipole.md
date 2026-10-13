---
title: HF wire antennas — random/long wires and ununs, EFHW, fan and trap dipoles, inverted-V, G5RV and OCF, NVIS, verticals and ground loss
domain: 08-antennas
slug: wire-antennas-hf-random-wire-fan-dipole
tags: [hf, random-wire, long-wire, unun, 9-to-1, efhw, 49-to-1, fan-dipole, trap-dipole, w3dzz, inverted-v, g5rv, ocf, windom, nvis, vertical, radials, ground-loss, counterpoise, antenna-tuner, multiband, linked-dipole, shortened-efhw, efhw-harmonics, rf-in-the-shack, beverage, rdf, receive-antenna, stealth-antenna]
prerequisites: [dipoles-and-monopoles.md, antenna-matching-and-baluns.md, ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md]
related: [../09-propagation-link-budget/ionospheric-hf-propagation.md, multiband-and-wideband-antennas.md, loop-antennas.md, ../06-rf-circuits/baluns-and-rf-transformers.md, ../03-transmission-lines-matching/coax-and-cables.md, ../16-simulation-tools/nec-antenna-modelling.md, ../19-regulations-safety/amateur-radio-licensing.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# HF wire antennas: random wires, fan and trap dipoles, inverted-V, G5RV/OCF, NVIS

## Questions this page answers
- What is a "random wire" or long-wire antenna, and why does it need a tuner or a 9:1 unun?
- Which random-wire lengths should I avoid, and do the published "magic lengths" really work?
- What is the difference between an end-fed half-wave (EFHW) and a random wire?
- Will dipoles of different lengths joined at one feed (fan dipole) work on several bands? What if they are at right angles?
- How does a trap dipole work, and how lossy are the traps?
- What happens to the impedance when I droop a dipole into an inverted-V?
- What is a G5RV, and is it really a multiband antenna without a tuner?
- How does moving the feed point off-centre (OCF/Windom) change the impedance, and why do OCFs skip some bands?
- What is NVIS, and how high should a dipole be for it?
- How much power does a vertical lose to the ground, and do radials help?
- Can I turn a metal clothesline into an antenna?
- Why does an antenna tuner not make a bad antenna good?
- How does a linked dipole work, and do the open links really disconnect the outer wires?
- Can I feed an OCF with ladder line and a tuner, and why is there RF on the feeder?
- How does a shortened (loaded) EFHW work, and what does the coil cost on 80 m?
- What do EFHW patterns look like on the harmonic bands?
- Why is there RF in the shack with my end-fed, and where do the chokes go?
- What is a Beverage, what is RDF, and why is a receive antenna judged by directivity, not gain?
- Can a hidden thin wire work as a receive antenna?

## TL;DR
- **A random wire is an end-fed wire of non-resonant length** fed against a ground or counterpoise through a tuner (often after a 9:1 unun, 50 → 450 Ω). Its feed impedance swings from tens of ohms (near odd λ/4) to several kΩ (near multiples of λ/2), so you need a tuner on every band. NEC: a 20 m wire has |Z| > 1.5 kΩ over **±13 %** around its first antiresonance (peak ≈ 4 kΩ) (`tools/verify/ant2_hf_wire.py`).
- **"Magic lengths"** (e.g., 29, 35.5, 41, 58, 71, 84, 107, 119 ft [7]) avoid half-wave multiples only by a few percent and **only for one installation**: the counterpoise, downlead and coax are part of the antenna. NEC over 40–10 m: with an ideal ground, 41/58/84/119 ft avoid every > 2 kΩ point but 71 ft has 4; with a 7.5 m counterpoise in free space, *only 3 % of all lengths* avoid > 2 kΩ points. Behind a 9:1 unun **no length gave worst-band VSWR below 5.7** — a tuner is always needed; the length rule just keeps you out of the worst kΩ spots.
- **EFHW ≠ random wire**: an EFHW is deliberately λ/2 (or its harmonics) and is fed at its ≈ 2–3 kΩ end with a 49:1 transformer ([dipoles](dipoles-and-monopoles.md#end-fed-half-wave-efhw)).
- **Fan dipole** (40 + 20 m on one feed): both bands work, but the shorter dipole is pulled **+2 to +4 %** in frequency and its R drops to ≈ 36 Ω when the wires run close together; at **90° (crossed)** the interaction is small (−0.9 %, R ≈ 70 Ω). Re-trim the shorter element in place.
- **Trap dipole** (W3DZZ-style 80/40 m, 8.2 µH ∥ 62 pF traps at 7.05 MHz): NEC resonances 3.71 and 7.10 MHz; with Q = 200 coils the traps cost ≈ 2–8 % of the power.
- **Inverted-V**: drooping the arms lowers R — free space 68 → 55 → 40 Ω for 180°/120°/90° apex (over ground at 12 m: 81 → 66 → 49 Ω) — which is why a 90–120° inverted-V matches 50 Ω coax nicely.
- **OCF**: at the fundamental $R\approx R_c/\cos^2(kz)$ (z = offset from centre) — NEC 94 Ω at the 1/3 point vs 97 Ω predicted. At the 1/3 point the feed is reasonable on f₁, 2f₁, 4f₁ (≈ 80–140 Ω) but **≈ 4 kΩ on 3f₁** (the 1/3 point is a current node) — why OCFs "skip" bands.
- **G5RV** (31.1 m top + 10.36 m of ladder line): designed as a 3λ/2 antenna on 20 m [5]; NEC (10.4 m over average ground) gives VSWR 2.3–7 across 20 m, 3.7 on 12 m and 9–63 on the other bands → it **needs a tuner on most bands**; Varney's "≈ 1.8 on 20 m" was not reproduced.
- **NVIS**: a horizontal dipole at **0.1–0.25 λ** over average ground puts its maximum straight up (zenith gain 4.8–6.1 dBi); at 0.5 λ the zenith gain falls to −6 dBi. Use frequencies below foF2 (≈ 2–10 MHz) — see [ionospheric propagation](../09-propagation-link-budget/ionospheric-hf-propagation.md).
- **Linked dipole** (40/20 m): open links are not perfect breaks. 1 pF (0.3 pF) of link capacitance pulls the 20 m resonance down 3.4 % (1.6 %), because the link sits at a voltage maximum and the 5 m outer wire is ≈ λ/4 at 14 MHz. Trim the inner dipole with the links open, in place.
- **OCF on twin feeder** drives common-mode current by itself. Feeder CM relative to DM is −8/+4.5/−6 dB at f₁/2f₁/4f₁ even with a floating balanced tuner, against −56 dB for a centre-fed dipole on the same feeder. Choke it, or accept a radiating feeder.
- **Shortened EFHW** (110 µH coil 21.6 m out, 2.2 m tail, 24 m total): works on 80/40/20/15/10 m. The coil costs 2.45 dB on 80 m (Q 200) and < 0.1 dB above, and the harmonic high-Z points sit 1–3 % low.
- **EFHW on its harmonics**: lobes at 53/42/36° from the wire on 2/3/4 × f₁ (peak 3.9/4.9/5.8 dBi). The harmonic high-Z points drift 1.3–2.1 % above n·f₁, so one wire is not perfectly multiband.
- **RF in the shack**: an end-fed wire's feed current is its counterpoise current. A choke at the transformer does nothing, and a choke 0.05λ down helps only if its impedance is ≫ that short counterpoise's (kΩ). An inductive choke can make it worse (+4.5 dB). A 5 kΩ resistive choke where the coax enters the building cuts radio-end CM by ≈ 24 dB.
- **Beverage** (NEC, 1.83 MHz, 2.5 m high, 500 Ω termination): RDF 7.7/10.2/11.7/12.8 dB for 0.5/1/1.5/2λ against 5.1 dB for a λ/4 vertical, with gain only −10 dBi (1λ). At MF/HF the SNR comes from directivity, not gain ([receive-only antennas](loop-antennas.md#receive-only-antennas-active-loops-e-field-whips-and-the-external-noise-test)).
- **Ground loss**: a λ/4 vertical with 4–8 elevated radials over average ground sends only **≈ 28 %** of its input power into the sky hemisphere (NEC) vs 77 % for a horizontal dipole at λ/2 — near-field loss is fixed by radials, far-field reflection loss is not. Buried-radial fields need ≈ 120 radials for a near-perfect ground (Brown, Lewis & Epstein 1937 [6]).

## Intuition (no math)
At HF (3–30 MHz, λ = 10–100 m) antennas are wires strung between supports, and the same wire is usually asked to work on several bands. A wire has a fixed physical length but the wavelength changes from band to band, so the *standing-wave pattern* on the wire changes: on one band the feed point sits at a current maximum (low impedance, tens of ohms), on another at a voltage maximum (high impedance, kΩ). Every multiband HF trick is a way of managing that:
- **accept it and tune it out** at the feed point (random wire + tuner, ladder line + tuner);
- **give each band its own resonant wire** (fan dipole), or **switch wire length electrically** (traps: parallel resonant circuits that look like an open circuit on the upper band and a loading coil on the lower band);
- **feed where the impedance is similar on several bands** (OCF at the 1/3 point; EFHW at the end, which is high-Z on all harmonics);
- **transform the impedance with a line section** (G5RV's ladder-line "matching section").

A wire low over the ground also *images* in the ground: a horizontal dipole low down sends its energy upward (NVIS), and a vertical's return currents flow through lossy soil unless radials give them a copper path.

An antenna tuner is a matching network. It makes the transmitter see 50 Ω; it does not change what the antenna radiates, and it cannot recover power lost in the feedline (high SWR on lossy coax) or in the ground.

## The math

### Level 1 — the numbers you use
Symbols: L wire length (m), λ = c/f, h height above ground, n integer, Z₀ characteristic impedance of a feedline (Ω), z offset from a dipole's centre.

| Item | Rule | Notes |
|---|---|---|
| Half-wave resonances of a wire | $f_n\approx nK\,c/(2L)$, K ≈ 0.95–0.97 | end effect; thin HF wire |
| High-Z (antiresonant) points of an end-fed wire | L ≈ n·λ/2 | |Z| 1–4 kΩ (NEC) |
| Low-Z points of an end-fed wire (good ground) | L ≈ (2n−1)·λ/4 | tens of Ω |
| Classic dipole cutting rule | L(m) ≈ 142.6/f(MHz) | K ≈ 0.951 ([dipoles](dipoles-and-monopoles.md)) |
| OCF feed resistance (fundamental) | $R\approx R_c/\cos^2(kz)$ | R_c ≈ 70 Ω; 1/3 point ≈ 95 Ω |
| Line transformation (G5RV) | $Z_\text{in}=Z_0\frac{Z_L+jZ_0\tan\beta l}{Z_0+jZ_L\tan\beta l}$ | lossless line |
| Trap resonance | $f_t=1/(2\pi\sqrt{L_tC_t})$ | trap ≈ open at f_t |
| NVIS height | h ≈ 0.1–0.25 λ | maximum at zenith |
| Unun ratios | 9:1 → 450 Ω, 49:1 → 2450 Ω, 4:1 → 200 Ω | turns ratio = √(impedance ratio) |

### Level 2 — why the impedance swings, and the derivations
**(a) The end-fed wire as a transmission line.** Treat each half of a wire antenna as a lossy, radiating transmission line of average characteristic impedance $Z_a\approx120[\ln(L/2a)-1]$ Ω (Schelkunoff; ≈ 900–1100 Ω for 1–2 mm HF wire) terminated by its open end. Seen from the feed, an open-ended line of length L presents $Z=-jZ_a\cot(\beta L)$ plus a radiation resistance: zero reactance and low R at L = (2n−1)λ/4, an infinite (in practice kΩ, limited by radiation) impedance at L = nλ/2. The counterpoise is a second, shorter "line" in series with the first: a short counterpoise adds a large capacitive reactance ($-jZ_c\cot\beta L_c$), which is why the same wire against a 2.5 m counterpoise has worst-band VSWR of 30–200 behind a 9:1 unun, but 8–20 against a 7.5 m counterpoise (NEC, below).

**(b) Width of the "forbidden" region.** Near an antiresonance the impedance behaves like a parallel RLC with a low Q (heavily loaded by radiation), so the kΩ region is wide: for a 20 m wire NEC gives |Z| > 1.5 kΩ from 6.95 to 8.85 MHz (± 13 % around the 7.43 MHz peak of 3.97 kΩ). Clearing every band by ± 13 % is impossible on 80–10 m (the bands are too dense), so the length lists aim for a few percent clearance (our own band-clearance search with K = 0.97 finds local optima at 29, 36, 41, 55, 61 and 72 ft with 3.9–9.7 % clearance; the VE3EED list scores 0–9 % on the same metric). The real protection comes from the tuner.

**(c) Feed-point impedance vs position (OCF).** For a λ/2 wire carrying $I(z)=I_0\cos kz$, the radiated power is fixed by $I_0$; a feed at z sees current $I_0\cos kz$, so $R(z)=2P/|I(z)|^2=R_c/\cos^2 kz$. At the 1/3 point (z = L/6, kz = π/6): R = R_c/0.75 ≈ 97 Ω (NEC: 94 Ω). On the second harmonic the wire is a full wave with a current node at the centre; the 1/3 point is near a current maximum again → moderate R (NEC 122 − j47 Ω). On the third harmonic the 1/3 point *is* a current node → kΩ (NEC 4.2 kΩ). On the fourth, moderate again (127 − j134 Ω). This is the mechanism behind "OCF works on 80/40/20/10 but not 30/15". The slot dual of this formula is $R_c\cos^2 kx$ ([slot antennas](slot-antennas.md#level-2--derivation-bookers-duality-argument)).

**(d) Inverted-V.** Bending the arms down by angle α from horizontal brings the two halves' currents partly into anti-alignment (vertical components cancel broadside) and closer together, reducing the radiation resistance; the resonant arm length *increases* slightly in our NEC runs (10.17 → 10.36 m from flat to 90° apex at 7.1 MHz, free space), because mutual coupling between the arms reduces the effective inductance. Near the ground the tips also load capacitively, pulling the other way; build long and trim.

**(e) Traps.** A parallel L_t–C_t trap at f_t = 1/(2π√(L_tC_t)) has very high impedance at f_t: on the upper band it disconnects the outer wires, so the inner section is a λ/2 dipole. Below f_t the trap is inductive ($X=\omega L_t/(1-\omega^2L_tC_t)$), acting as a loading coil, so the whole wire resonates on the lower band with *less* total length than a full λ/2. The trap's coil loss appears both as a series R on the lower band and as a parallel loss on the upper band, where the trap carries a large circulating current.

**(f) G5RV.** Varney designed the 31.1 m (102 ft) top as a 3λ/2 centre-fed wire on 14 MHz, where its feed R is ≈ 90 Ω at λ/2 height, and the 10.36 m (34 ft) open-wire section as a *half-wave repeater* on 14 MHz, presenting ≈ 90 Ω to 75–80 Ω coax (VSWR ≈ 1.8 on 50 Ω) [5]. On the other bands the line transforms whatever the top presents to something the tuner can handle; Varney himself specifies a tuner [5]. NEC (top at 10.4 m over average ground, 1.6 mm wire, 450 Ω line, 10.36 m electrical): VSWR(50) on 20 m = 7.0/3.6/2.3 at 14.0/14.175/14.35 MHz (minimum 2.3 at 14.35 MHz; 300 Ω line: 6.1/3.3/2.3), 3.7 on 12 m, and 8.9–63 on 80, 40, 30, 17, 15 and 10 m (table below). The 20 m match depends on height, wire diameter and ground (top Z = 108 − j53 Ω in our model, not Varney's resistive 90 Ω).

**NEC per-band numbers** (`ant2_hf_wire.py`). End-fed wire against a 2.5 m counterpoise in free space — feed |Z| (Ω) and VSWR(50) behind an ideal 9:1 unun at band centre:
| Band | 20.1 m (66 ft, "bad") | 21.6 m (71 ft, "good") | 12.5 m (41 ft, "good") |
|---|---|---|---|
| 80 m | 2160 Ω / 490 | 2103 / 376 | 2477 / 1880 |
| 40 m | 2931 / 6.6 | 3290 / 16 | 924 / 53 |
| 30 m | 931 / 43 | 771 / 34 | 390 / 1.7 |
| 20 m | 1119 / 3.4 | 2292 / 8.8 | 1122 / 21 |
| 17 m | 386 / 10 | 150 / 4.5 | 267 / 8.8 |
| 15 m | 728 / 3.3 | 1827 / 6.5 | 394 / 3.2 |
| 12 m | 337 / 6.6 | 139 / 3.7 | 1594 / 6.8 |
| 10 m | 962 / 4.0 | 835 / 5.3 | 154 / 4.9 |
The "good" 71 ft wire is *worse* than the "bad" 66 ft one on 40 and 20 m in this installation; the large capacitive reactance on 80/30 m comes from the too-short counterpoise.

G5RV (top 10.4 m over average ground, 450 Ω line 10.36 m electrical):
| Band | 80 | 40 | 30 | 20 | 17 | 15 | 12 | 10 |
|---|---|---|---|---|---|---|---|---|
| Z at coax (Ω) | 20+j77 | 64−j151 | 76+j417 | 110−j81 | 136−j540 | 48+j132 | 126−j82 | 3026−j656 |
| VSWR(50) | 8.9 | 9.0 | 48 | 3.6 | 46 | 9.1 | 3.7 | 63 |

### Level 3 — ground, height and pattern
- **Image theory over real ground.** A horizontal dipole at height h over a good conductor has an image of opposite sign at −h; the vertical-incidence field is $\propto 2\sin(kh)$, maximal at h = λ/4 and near zero at h = λ/2 (kh = π). Over real ground the reflection coefficient is less than 1 and the null fills in. NEC at 5.3 MHz over average ground (εr 13, σ 5 mS/m): zenith gain **0.8, 4.8, 6.1, 5.9, −6.4 dBi** at h = 0.05, 0.10, 0.15, 0.25, 0.5 λ; at 0.5 λ the main lobe is at 28° elevation (7.7 dBi). The impedance also varies with height (50 → 60 → 82 → 63 − j34 Ω over the same heights).
- **Vertical antennas over real ground.** A vertical's return current flows radially in the ground near its base; with few or no radials that current flows through soil and dissipates (near-field ground loss). Brown, Lewis and Epstein (1937) measured broadcast verticals over buried radial systems and found that ≈ 120 λ/2-long radials are needed to approach a perfect ground; with few radials the ground loss resistance can rival the radiation resistance [6]. *Elevated* radials (a few at ≥ 0.05 λ height) remove most near-field loss; NEC with the base 2 m up at 7.1 MHz: 1/2/4/8 radials → Z = 50/35/33/32 Ω and **24/27/28/28.5 %** of input power radiated into the sky hemisphere. The rest of the deficit (vs 100 % over a perfect ground) is **far-field reflection loss** in the ground several wavelengths out (the pseudo-Brewster effect for vertical polarization), which no radial field fixes; a horizontal dipole at λ/2 over the same ground reaches 77 %.
- **Long wires (several λ).** A wire many wavelengths long radiates in cones of lobes tilting toward the wire axis. Terminated versions (Beverage, rhombic) are travelling-wave antennas; the Beverage is treated below under [receive-only wires](#receive-only-wires-beverage-rdf-and-stealth-long-wires).
- **NEC caveats.** NEC-2 Sommerfeld ground needs wires above ground; buried radials and ground rods need NEC-4 or measurements. Our models use 1.6 mm wire, ≥ 10 segments per half-wave at the highest frequency, and are cross-checked against this KB's own MoM for free-space dipoles ([NEC modelling](../16-simulation-tools/nec-antenna-modelling.md)).

## More HF wire antennas: linked dipoles, OCF on twin feeder, shortened and harmonic EFHWs

All numbers are from `tools/verify/s12_hf_wire_chokes.py` (PyNEC, 1.6 mm wire).

**Linked dipole.** A dipole cut for the highest band has insulated "links" (jumpers) at its ends. Closing the links adds outer sections for a lower band. Model: 40/20 m in free space, inner dipole 10.25 m (resonant at 14.2 MHz alone), links closed giving 20.56 m resonant at 7.1 MHz with Z = 67 Ω. An open link is a 0.1 m insulator with stray capacitance C across it:
- **C = 1 pF:** the 20 m resonance moves to 13.72 MHz (−3.4 %).
- **C = 0.3 pF:** it moves to 13.97 MHz (−1.6 %); R is 71–74 Ω in both cases.

The capacitance looks small (X_C = 11–37 kΩ), but the link sits at the dipole's voltage maximum. Each 5 m outer section is ≈ λ/4 at 14 MHz and presents a low impedance at its near end. A pre-registered "< 2.5 % shift" failed at 1 pF. **Practice:** cut the inner dipole, open the links, and trim it in place. Keep the link hardware small, and do not leave a dangling outer section near λ/4 on the upper band. Linked dipoles beat traps on efficiency (no trap loss), but you must change bands at the antenna.

**OCF on twin feeder (with a balanced tuner).** Model: a 41 m wire fed at the 1/3 point through 10 m of vertical 25 mm-spaced twin feeder (≈ 410 Ω) over average ground; a centre-fed 41 m dipole on the same feeder for comparison. The table gives the impedance at the feeder bottom and the peak feeder common-mode current relative to the differential current:

| Band | Centre-fed, floating tuner | Centre-fed, tuner grounded | OCF, floating tuner | OCF, tuner grounded |
|---|---|---|---|---|
| f₁ = 3.48 MHz | 51 + j315 Ω, −56 dB | −13 dB | 174 + j557 Ω, −8 dB | −4 dB |
| 2f₁ | 45 − j62, −44 dB | −24 dB | 206 − j254, +4.5 dB | −7 dB |
| 4f₁ | 348 + j737, −35 dB | −0.7 dB | 255 − j567, −6 dB | −6 dB |

An off-centre feed is not a balanced load: the two halves present different impedances to the feeder. The OCF therefore drives the feeder in common mode however good the tuner is. Twin feeder makes the impedances easy for a tuner (lower SWR loss than coax), but the feeder radiates and brings RF to the operating position. Two fixes: a current balun at the feed point (the usual 4:1 coax-fed OCF), or a CM choke where the twin line meets the tuner. A grounded (unbalanced) tuner also puts CM current on a centre-fed dipole's feeder, especially on 4f₁, where the feeder plus ground lead resonates. This complements the [OCF feed-resistance derivation](#level-2--why-the-impedance-swings-and-the-derivations).

**Shortened 80/40 m EFHW (loading coil).** An inner wire is λ/2 on 40 m; a series coil plus a short tail then makes the whole wire resonate (high-Z) on 80 m. On 40 m and up, the coil's reactance (110 µH → 4.9 kΩ at 7.1 MHz) isolates the tail, as a trap would. Model: free space, 2 m counterpoise, coil Q 200, fed at the end through an ideal transformer. Solving for high-Z points at 3.6 and 7.1 MHz gives 21.6 m + 110 µH + 2.2 m tail = **24.0 m** (a full 80 m EFHW is ≈ 40 m).

| Band | Z at the feed | Coil-loss efficiency | Nearest high-Z point |
|---|---|---|---|
| 3.6 MHz | 988 − j5140 Ω | **56.9 % (−2.45 dB)** | 3.56 MHz (R ≈ 6.0 kΩ) |
| 7.1 MHz | 3081 − j2442 | 99.4 % | 7.00 MHz (−1.4 %) |
| 14.2 | 1111 − j1874 | 99.9 % | 13.77 (−3.0 %) |
| 21.2 | 890 − j1404 | 99.9 % | 20.65 (−2.6 %) |
| 28.4 | 525 − j1013 | 99.9 % | 27.60 (−2.8 %) |

On 80 m the coil carries the full antenna current, so its loss is large (a pre-registered "< 1.5 dB" failed: −2.45 dB at Q 200). Halving Q roughly doubles the loss resistance. The upper bands are almost lossless, but they are ≈ 3 % off the band centres. Commercial designs trim this with the wire length, the coil value and a small capacitor across the transformer primary (vendor practice). A 49:1 transformer sees 1–6 kΩ; check the coil's voltage and temperature rating at the power you run.

**EFHW on its harmonics: patterns and drift.** Model: a 20.3 m EFHW with a 1 m counterpoise in free space, f₁ = 7.160 MHz. The standing-wave pattern of an n-half-wave wire with current nodes at the ends is $F(\psi)=\cos(\tfrac{n\pi}{2}\cos\psi)/\sin\psi$ for odd n and $\sin(\tfrac{n\pi}{2}\cos\psi)/\sin\psi$ for even n, with ψ measured from the wire.

| n | High-Z point (n·f₁) | Drift | R_peak | Peak gain | Main lobe from the wire: NEC / formula |
|---|---|---|---|---|---|
| 1 | 7.160 MHz | 0 | 2575 Ω | 2.99 dBi | 87° / 90° |
| 2 | 14.506 (14.320) | +1.3 % | 1894 | 3.88 | 53° / 54° |
| 3 | 21.888 (21.480) | +1.9 % | 1621 | 4.94 | 42° / 43° |
| 4 | 29.241 (28.640) | +2.1 % | 1463 | 5.78 | 36° / 36° |

On the harmonics the EFHW is a long wire, not a dipole. Its broadside response splits into lobes tilting toward the wire ends, so the "40 m EFHW on 10 m" covers four cones and has nulls broadside. The harmonic resonances fall above n·f₁ (the end effect matters less on a longer electrical length), so a wire trimmed for 7.1 MHz is high on 21 and 28 MHz. That is why EFHW kits accept a compromise SWR on the upper bands.

## RF in the shack and where the chokes go (end-fed wires)

Model: a 40 m EFHW (20.3 m at 10 m height) with no separate counterpoise. The coax shield runs 10 m down and 5 m along to a grounded radio, so the shield **is** the counterpoise. The table gives the CM current at the radio relative to the antenna feed current, at 7.1 / 14.2 MHz:

| Choke | 7.1 MHz | 14.2 MHz |
|---|---|---|
| none | +3.9 dB | +4.5 dB |
| 5 kΩ resistive at the transformer | +4.5 | +4.0 |
| 1 kΩ resistive 2 m (0.05λ) down | +1.4 | −1.1 |
| 5 kΩ resistive 2 m down | −3.5 | −8.4 |
| 1 kΩ inductive (j1 kΩ) 2 m down | **+8.4** | +4.7 |
| 5 kΩ resistive at the building entry | **−19.9** | −18.3 |

Two pre-registered expectations failed, and both are worth knowing:
1. **A choke at the feed does nothing.** For an end-fed antenna the current into the radiator *equals* the current returning on the counterpoise. Choking it only removes the counterpoise and raises the feed impedance.
2. **A 5 kΩ choke 2 m down gives only 7.4 dB, not > 15 dB.** 2 m of shield is a capacitive counterpoise of several kΩ at 7 MHz, so the choke shares the current instead of blocking it. An **inductive** choke there resonates with that capacitance and makes things worse, which is G3TXQ's warning about reactive chokes ([baluns](antenna-matching-and-baluns.md#where-to-put-chokes-a-placement-rule-from-nec)).

The rule for end-feds:
- Give the antenna a **defined counterpoise**: a wire of 0.05–0.1λ, or the coax section above a choke.
- Put a **high-impedance resistive choke** (≥ 5–10 kΩ, ferrite) where that counterpoise should end.
- Add a **second choke where the coax enters the building**. That is the one that actually keeps RF off the radio, the mains and the USB leads.

Symptoms of RF in the shack are a "hot" microphone, RF burns on metal, and the SWR or the PC/USB link changing with power or hand position. The physics is the same as the UHF case on the [baluns page](antenna-matching-and-baluns.md).

## Receive-only wires: Beverage, RDF and stealth long wires

**Why receive antennas are judged differently.** Below ≈ 20 MHz the external noise is 20–60 dB above kT₀ ([P.372 table](loop-antennas.md#receive-only-antennas-active-loops-e-field-whips-and-the-external-noise-test)). An antenna's efficiency scales signal and noise equally, so what improves SNR is *rejecting noise from other directions*. W8JI's **receiving directivity factor** captures this. RDF is the forward gain in the wanted direction over the gain averaged over the whole sphere; for an antenna over ground, the average counts zero below the horizon. It is the directivity of the sky pattern, independent of efficiency.

**Beverage.** A long, low (2–3 m) wire, one end fed against a ground rod and the far end terminated in ≈ its characteristic impedance (400–600 Ω) to ground. A wave arriving from the terminated end tilts its field forward over the lossy ground. It induces a current wave that travels with it and builds up toward the receiver, while waves from behind are absorbed in the termination. NEC (1.83 MHz, 2.5 m high, 500 Ω, average ground; `tools/verify/s12_rx_antennas.py` §4):

| Antenna | Peak gain (elevation) | F/B | RDF |
|---|---|---|---|
| λ/4 vertical, no radials | −3.6 dBi (22°) | 0 dB | 5.1 dB |
| Beverage 0.5λ (82 m) | −14.9 dBi (64°) | 5.5 | 7.7 |
| Beverage 1.0λ (164 m) | −10.0 dBi (38°) | 12.3 | 10.2 |
| Beverage 1.5λ (246 m) | −7.9 dBi (29°) | 11.8 | 11.7 |
| Beverage 2.0λ (328 m) | −5.4 dBi (24°) | 9.9 | 12.8 |

These agree with the usual amateur figures (W8JI/ON4UN: vertical ≈ 5 dB, 1–2λ Beverages ≈ 10–12 dB). The pre-registered vertical value first came out 3 dB low, because the script averaged over 2π instead of 4π sr; that is fixed. Gain of −10 dBi or less is fine at MF: the external noise still dominates the receiver after the loss. If it does not, add a preamplifier. Practical points: terminate to a good ground rod, transform the ≈ 500 Ω feed with a 9:1 transformer, choke the coax, and run the wire in a straight line. Beverages need long runs (≥ 1λ = 164 m on 160 m), so small lots use flags, pennants, K9AY loops and small phased arrays instead. These are compact terminated loops with RDF ≈ 7–9 dB (vendor and amateur comparisons — anecdotal, not modelled here).

**Stealth long-wire receive.** A thin wire (0.2–0.5 mm enamelled, 10–20 m, under eaves or along a fence) is a perfectly good *receive* antenna at HF. A 1 m active whip in residential noise is already externally noise-limited at 7 MHz ([loop page](loop-antennas.md#receive-only-antennas-active-loops-e-field-whips-and-the-external-noise-test)), so the length matters less than *where* the wire is and what it is connected to. What matters:
- **Distance from the house wiring.** Local noise is a near field that falls quickly with distance.
- **A feed that does not collect CM noise.** Use a 9:1 transformer with a separate ground rod or counterpoise, and a CM choke or isolating transformer on the coax.
- **No conductive path back into the house's noisy ground.**

An indoor wire usually hears mostly the house. As a transmit antenna the same wire is lossy and unpredictable, so use a tuner at its base and observe RF exposure distances ([19](../19-regulations-safety/rf-exposure-safety.md)).

## Design equations & rules of thumb
| Quantity | Value | Valid | Source |
|---|---|---|---|
| Random wire: |Z| > 1.5 kΩ region | ± 13 % around each n λ/2 point | thin wire, NEC | `ant2_hf_wire.py` |
| Random wire + 9:1 unun, best worst-band VSWR (40–10 m) | 5.7–11.6 depending on ground | NEC, ideal unun | `ant2_hf_wire.py` |
| Shortest all-band (160–10 m) random wire | ≈ 143 ft electrical (λ/4 at 1.72 MHz); 74 ft without 160 m | tuner at the feed, good ground | Sprott [8] |
| Inverted-V R (free space / 12 m over ground) | 68/55/40 Ω and 81/66/49 Ω at 180/120/90° | 7.1 MHz | NEC |
| OCF at 1/3 | ≈ 80–140 Ω on f₁, 2f₁, 4f₁; ≈ 4 kΩ on 3f₁ | 41 m wire, 0–20 m height | NEC |
| Fan dipole interaction | shorter element +2…+4 % (close), −1 % (crossed) | 40/20 m | NEC |
| Trap loss (Q_L = 200) | ≈ 2 % (lower band), ≈ 8 % (trap band) | W3DZZ-like | NEC |
| NVIS dipole height | 0.1–0.25 λ | average ground | NEC |
| Vertical, elevated radials | ≥ 2–4 radials ≈ saturates (28 % to sky) | 0.05 λ base height | NEC |
| Buried radials for "perfect" ground | ≈ 120 × λ/2 | broadcast practice | BLE 1937 [6] |
| Linked-dipole open link | 0.3–1 pF → upper-band resonance −1.6 to −3.4 % | 40/20 m | `s12_hf_wire_chokes.py` |
| Shortened EFHW 80/40 | 21.6 m + 110 µH + 2.2 m; −2.45 dB on 80 m (Q 200) | free space | `s12_hf_wire_chokes.py` |
| EFHW harmonic drift | +1.3/+1.9/+2.1 % at 2/3/4 f₁; lobes 53/42/36° from the wire | 20.3 m wire | `s12_hf_wire_chokes.py` |
| Beverage RDF | ≈ 10 dB (1λ), 12–13 dB (2λ); vertical ≈ 5 dB | 1.83 MHz, average ground | `s12_rx_antennas.py` |

## Worked examples

**Example 1 — Random wire for a portable HF station.** A 17.7 m (58 ft) wire sloping from a tree to an auto-tuner with a 9:1 unun at its base, plus a 7.5 m counterpoise on the ground. NEC (free-space analogue): worst VSWR behind the 9:1 ≈ 10 on 40–10 m with one band point above 2 kΩ — within the range of an external auto-tuner (typically ≤ 10:1–30:1 — check its spec) but not a radio's internal tuner (≈ 3:1). If one band refuses to tune, change the wire (or counterpoise) by ≈ 1 m rather than hunting for "the" magic length; put a common-mode choke on the coax at the unun so the shield does not become the counterpoise ([baluns](antenna-matching-and-baluns.md)).

**Example 2 — Two-band fan dipole, 40 + 20 m.** Cut a 40 m dipole (20.30 m tip-to-tip, NEC resonance 7.184 MHz alone) and a 20 m dipole (10.10 m, 14.404 MHz alone) and join them at one balun. Spaced as a vertical fan with the 20 m arms drooping 30° below the 40 m arms: resonances 7.164 and 14.672 MHz (+1.9 %), R 60 and 37 Ω. Trim the 20 m element ≈ 2 % longer (to ≈ 10.3 m) after installation. If space allows, **cross the dipoles at 90°** instead: 7.196 and 14.277 MHz (−0.9 %), R 73/70 Ω — almost no interaction. (Answers D1 #628: yes, joined dipoles at right angles behave as a multiband antenna with minimal interaction; close spacing works but shifts and loads the shorter one.)

**Example 3 — Inverted-V on a single mast.** A 40 m dipole with its centre on a 12 m mast and the ends tied down to give a 90–120° apex angle: NEC R = 49–66 Ω at resonance over average ground → VSWR ≤ 1.3 on 50 Ω coax with a 1:1 current balun, no matching network. Arms ≈ 10.2–10.3 m each at 7.1 MHz; leave 0.3 m extra and trim.

**Example 4 — NVIS for a field-day or recovery-team link (0–300 km).** At 5.3 MHz (λ = 56.6 m) a dipole at 8.5 m (0.15 λ) gives 6.1 dBi at the zenith and 2.1 dBi at 30° elevation; at 28 m (0.5 λ) it would put a null-ish −6.4 dBi upward. Pick a frequency below the current foF2 (daytime 5–10 MHz, night 2–5 MHz at mid-latitudes, higher near the equator — Singapore — see [ionospheric](../09-propagation-link-budget/ionospheric-hf-propagation.md)). Note: amateur HF requires a licence ([19](../19-regulations-safety/amateur-radio-licensing.md)).

**Example 5 — Can a metal clothesline be an antenna?** (D2 #141) Yes: a 15 m steel line ≈ 2 m up is a low random wire. Expect: (i) high losses — steel's resistivity and μ raise its RF resistance ≈ 10–40× over copper at HF (see the conductor-material section of [dipoles](dipoles-and-monopoles.md#conductor-material-length-and-loss)); (ii) at 2 m height most of its HF radiation goes upward (NVIS-like) and into the ground; (iii) any metal post or ground contact becomes part of the antenna. Fine for receive (HF is noise-limited — see [multiband-and-wideband](multiband-and-wideband-antennas.md#receive-only-sdr-antennas-does-length-matter)); a poor transmitting antenna, and never transmit on a line people touch.

## Practical notes
- **Unun and choke.** A 9:1 unun is an autotransformer; with a random wire it sees impedances from tens of ohms to kΩ, so its losses (core heating) vary widely by band. Put a common-mode choke on the coax near the feed; otherwise the coax shield is the counterpoise and RF appears in the shack.
- **Tuner location.** A tuner at the antenna (remote auto-tuner) is better than one in the shack: high SWR on the coax between them adds loss (coax loss multiplies with SWR — [coax](../03-transmission-lines-matching/coax-and-cables.md)). Ladder line (open-wire, low loss at high SWR) is the alternative.
- Tuner topologies, losses, auto-tuner operation and the at-rig vs at-antenna numbers: [antenna tuners and ATUs](../03-transmission-lines-matching/antenna-tuners-and-atus.md).
- **Voltage at the ends.** End-fed and EFHW feed points and all wire tips carry kV at 100 W — insulate, keep out of reach (see [dipoles tip-voltage note](dipoles-and-monopoles.md#tip-voltage-and-safe-power)).
- **Measure on site.** Height, nearby metal, ground and the feedline change resonances by several percent; trim with an antenna analyser (NanoVNA/RigExpert) at the feed point.
- **Lightning and static.** Long wires accumulate static; a DC path to ground (an RF choke or the unun's DC continuity) bleeds it; disconnect and ground antennas when not in use ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).

## Common mistakes & misconceptions
- **"There is a magic random-wire length that tunes everywhere."** The lists clear half-wave multiples by only a few percent, while the kΩ region is ± 13 % wide; the counterpoise and coax change the electrical length. NEC shows the same "good" length (71 ft) is clean in one installation and bad in two others.
- **"A 9:1 unun matches a random wire to 50 Ω."** It moves the average impedance toward 50 Ω; worst-band VSWR behind it was ≥ 5.7 for every length tried (40–10 m) — you still need a tuner.
- **"A random wire doesn't need a ground."** The other terminal of the feed must connect to something: a counterpoise, radials, a ground rod, or (by default) the coax shield. A 2.5 m counterpoise made the worst-band VSWR 3–10× worse than a 7.5 m one in NEC.
- **"An EFHW is a random wire."** An EFHW is resonant (λ/2 and harmonics) and transformer-matched at a high-impedance end; a random wire is deliberately non-resonant and tuner-matched.
- **"A G5RV is a no-tuner multiband antenna."** Only 20 m is near 50 Ω (and even that depends on height/ground); Varney himself used a tuner on the other bands [5].
- **"OCF works on all bands."** At the 1/3 point the third harmonic sees a current node (≈ 4 kΩ).
- **"An antenna tuner fixes a bad antenna."** It matches the transmitter; it does not improve radiation efficiency or feedline loss.
- **"Fan-dipole elements don't interact."** Close-spaced elements shift each other (here +2–4 %) and lower R; crossed elements interact least.
- **"More radials always help a vertical."** Elevated radials saturate after 2–4; buried radials need tens to 120; the far-field ground-reflection loss remains in either case.
- **"An open link disconnects the outer wire."** Its pF-level capacitance sits at a voltage maximum and can move the upper band by 2–3 %.
- **"Ladder line makes an OCF balanced."** The OCF itself is unbalanced; the feeder carries CM current with any tuner (−8 to +4.5 dB re DM in NEC).
- **"Put the EFHW choke right at the transformer."** Then there is no counterpoise. Place a resistive choke a defined counterpoise length down the coax, and another at the building entry.
- **"A Beverage is a high-gain antenna."** Its gain is −10 dBi or less; it wins on RDF (directivity), which is what sets the SNR at MF/low HF.
- **"Higher is always better for HF."** For DX (low angles) yes; for NVIS, a low dipole (0.1–0.25 λ) is what you want.

## How to simulate / verify
- `python3 tools/verify/ant2_hf_wire.py` (≈ 40 s; PyNEC/NEC-2): end-fed impedance per band for 20.1/21.6/12.5 m wires, band-clearance length search, NEC check of the VE3EED lengths under three groundings, fan and crossed dipoles, inverted-V vs apex angle (free space and Sommerfeld ground), OCF impedance vs feed position (free space and over ground), G5RV with an analytic line transformation, NVIS gain vs height, trap dipole with lossy traps, vertical with elevated radials and the sky-hemisphere power fraction. Output saved in `tools/verify/ant2_hf_wire_output.txt`.
- `python3 tools/verify/s12_hf_wire_chokes.py` (≈ 10 min): linked dipole, OCF and dipole on twin feeder, shortened EFHW, EFHW harmonics, RF-in-the-shack choke placement, UHF choke placement. Note: in PyNEC a wire that touches a Sommerfeld ground is connected only with `geometry_complete(1)`; with 0 the end floats.
- `python3 tools/verify/s12_rx_antennas.py`: Beverage/vertical RDF and the P.372 receive-noise analysis.
- NEC practice and PyNEC traps (EK flag order, φ-grid averaging): [NEC antenna modelling](../16-simulation-tools/nec-antenna-modelling.md).
- Measure with an antenna analyser at the feed point, with the choke installed; sweep each band and record R, X.

## Open questions / gaps
- The random-wire NEC study uses idealised groundings (free-space counterpoise or perfect ground); a Sommerfeld-ground model with a sloping wire and the real coax would be closer to practice.
- G5RV: Varney's 1.8:1 on 20 m was not reproduced (NEC: 2.3–7 across the band); height/ground/wire sensitivity not explored systematically.
- OCF: NEC gives ≈ 80–140 Ω at the 1/3 point (supports a 2:1 balun), while commercial OCFs commonly use 4:1 or 6:1 baluns (vendor/forum practice — anecdotal); unresolved.
- Shortened-EFHW and RF-in-the-shack models use ideal transformers and free space or a single coax geometry; real kits (coil Q, transformer loss, the station ground) will differ. Measure the CM current with a clamp-on probe.
- Ground-loss numbers for ground-mounted verticals with buried radials (Brown–Lewis–Epstein curves, Sevick's measurements) are cited, not reproduced (NEC-2 cannot model buried wires).

## Sources
1. ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — random wires and tuners, fan/trap dipoles, inverted-V, OCF, G5RV, NVIS, verticals and radials. (handbook; cited)
2. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — ch. 4 (dipoles over ground, image theory, height effects), ch. 9 (traveling-wave long wires). (textbook; cited)
3. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — long-wire patterns, ground effects. (textbook; cited)
4. S. A. Schelkunoff, *Advanced Antenna Theory*, Wiley 1952 — antennas as transmission lines, average characteristic impedance. (textbook; cited via Balanis)
5. L. Varney (G5RV), "The G5RV multiband antenna... up-to-date," RSGB, reprinted at http://www.popular-hifi.com/shack/ant_g5rv/g5rv.pdf — 102 ft/31.1 m top, 34 ft/10.36 m matching section, 3λ/2 on 14 MHz, ≈ 90 Ω, 1.8:1 on 50 Ω, tuner on other bands (expert article; READ via pdftotext).
6. G. H. Brown, R. F. Lewis, J. Epstein, "Ground systems as a factor in antenna efficiency," *Proc. IRE* 25(6), 753–787, 1937 — buried radial systems, ≈ 120 radials (peer-reviewed; cited via secondary summaries).
7. J. VE3EED (SK), "The 'best' random wire antenna lengths" (list of 29, 35.5, 41, 58, 71, 84, 107, 119, 148… ft), reproduced at https://ve3ips.wordpress.com/2021/11/02/ (forum/club — anecdotal; evaluated numerically here).
8. J. C. Sprott, "Optimal length of random wire antenna," Univ. of Wisconsin technote, 2012/2022. https://sprott.physics.wisc.edu/technote/randwire.htm — computed gaps; 143 ft (λ/4 at 1.72 MHz) or 74 ft without 160 m (technote; READ).
9. W3DZZ trap dipole (C. L. Buchanan, *QST* 1955) — trap concept and typical 80/40 m dimensions (cited via [1]).
10. T. Molteno et al., PyNEC / NEC2++ (https://github.com/tmolteno/python-necpp); G. J. Burke, A. J. Poggio, *NEC — Method of Moments*, LLNL 1981 (tool documentation).
11. This repository: `tools/verify/ant2_hf_wire.py` (+ `_output.txt`), `tools/verify/s12_hf_wire_chokes.py`, `tools/verify/s12_rx_antennas.py`. (verification)
12. H. H. Beverage, C. W. Rice, E. W. Kellogg, "The wave antenna — a new type of highly directive antenna," *Trans. AIEE* 42, 1923; J. Devoldere (ON4UN), *ON4UN's Low-Band DXing*, 5th ed., ARRL, 2010 — Beverages, flags and the RDF figure of merit (introduced by T. Donoghue, W8JI); summarised via the Hi-Z Antennas comparison chart. (peer-reviewed historical / handbook; cited)
13. S. Hunt (G3TXQ), "Common-mode chokes" — measured choke impedance chart, resistive vs reactive chokes (PDF mirror hellschreiber.com/radio/pdf-ant/article-G3TXQ-chokes.pdf; READ). (expert measurement)
