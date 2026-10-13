---
title: Antenna identification guide — recognising antenna types in the wild, estimating the band from element length, and why stock antennas should be measured
domain: 08-antennas
slug: antenna-identification-guide
tags: [identification, field-guide, rubber-duck, whip, dipole, yagi, lpda, discone, patch, helix, qfh, collinear, j-pole, chip-antenna, cellular-panel, sector-antenna, dish, horn, mag-mount, element-length, nanovna, stock-antenna]
prerequisites: [antenna-fundamentals.md]
related: [dipoles-and-monopoles.md, yagi-uda-and-log-periodic.md, multiband-and-wideband-antennas.md, helical-antennas.md, patch-antennas.md, pcb-and-chip-antennas.md, horn-reflector-aperture-antennas.md, slot-antennas.md, antenna-measurement.md, ../15-lora-ism-radios/choosing-and-judging-lora-antennas.md, ../17-test-measurement/nanovna-librevna-practical.md, ../19-regulations-safety/rf-exposure-safety.md, ../19-regulations-safety/spectrum-allocation-ism-bands.md]
level: intro
confidence: medium
last_updated: 2026-10-02
---

# Antenna identification guide

## Questions this page answers
- What is that antenna on the roof / mast / tower / device, and what is it for?
- How can I tell an antenna's frequency band from its size?
- What do rubber ducks, whips, dipoles, Yagis, LPDAs, discones, patches, helices, QFHs, collinears, J-poles, chip antennas, cellular panels, dishes, horns and mag-mounts look like, and what gain and pattern do they have?
- Why is a "6 dBi" omni a long fibreglass stick?
- What is the box with rectangular panels on a cell tower (and is it safe near my window)?
- Is the antenna that came with my LoRa/Meshtastic/radio module actually tuned to the right band?
- What SWR is "good enough" for a stock antenna, and how much does a bad one cost?

## TL;DR
- **Size gives the band.** A resonant element is ≈ λ/4 (monopole/whip) or ≈ λ/2 (dipole, Yagi element) long: $f[\text{MHz}]\approx 71/L_{\lambda/4}[\text{m}]\approx 142/L_{\lambda/2}[\text{m}]$ (0.95 end-effect factor). 433 MHz: λ/4 ≈ 164–173 mm; 915 MHz ≈ 78–82 mm; 2.45 GHz ≈ 29–31 mm (`tools/verify/ant2_ident.py`).
- **Exceptions that fool people**: rubber ducks and stubbies hide a coil (normal-mode helix) — physically short, electrically λ/4, lossy; PCB/chip antennas are shortened by the substrate and by meandering; fibreglass radomes hide collinear arrays several λ long.
- **Shape gives the job**: omni vertical (whip, collinear, J-pole, discone) → coverage all round; directional (Yagi, LPDA, panel, dish, horn, helix) → point-to-point or tracking; CP (helix, QFH, crossed Yagi, patch with a corner cut) → satellites and rolling targets.
- **Gain is length or area**: collinear omni ≈ 10 log(2L/λ) dBi with elevation beamwidth ≈ 51λ/L degrees (2 λ → 6 dBi/25°, 4 λ → 9 dBi/13°); dish/horn ≈ 10 log(e·(πD/λ)²) (60 cm at 11.7 GHz ≈ 35 dBi).
- **Stock antennas are often mistuned or mislabelled.** NanoVNA tests of antennas bundled with mesh-radio kits found best-match frequencies of **852, 892 and 808 MHz**, i.e. SWR at 915 MHz of **2.0, 2.0 and 4.0** (mismatch loss 0.5–1.9 dB) [6]; club testers report "915 MHz" antennas that were relabelled 868 MHz parts [7]. A good S11 does not prove efficiency — but a bad one proves a problem. **Measure, on the radio or a representative ground** (see [choosing and judging LoRa antennas](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md)).

## Intuition (no math)
Antennas are built to the size of the wave they handle. A half-wave dipole for FM radio (100 MHz, λ = 3 m) is about 1.5 m tip to tip; for Wi-Fi (2.45 GHz) it is 6 cm. So the first clue is size, the second is shape: rods mean wire antennas (dipoles, monopoles, Yagis), flat squares mean patches, cones or discs mean wideband, spirals and coils mean circular polarization or shortening, and dishes and horns mean very high frequencies and narrow beams. The third clue is orientation: vertical rods are vertically polarized; a Yagi whose elements are horizontal is horizontally polarized; rectangular panels on cell towers are dual-slant (±45°) arrays.

What you cannot see is how well it is tuned. A plastic stick labelled "915 MHz 5 dBi" may contain an 868 MHz whip, or a 433 MHz spring. The only way to know is to measure its match on the device (or on a ground plane like the device's), and ideally compare its received signal against a known reference antenna.

## The math

### Level 1 — size to frequency
| Band | f (MHz) | λ/4 (mm) | 0.95 λ/4 (mm) | λ/2 (mm) |
|---|---|---|---|---|
| CB | 27.2 | 2757 | 2619 | 5514 |
| FM broadcast | 98 | 765 | 727 | 1530 |
| Airband | 127 | 590 | 561 | 1180 |
| NOAA APT / 2 m | 137.5 | 545 | 518 | 1090 |
| 2 m amateur | 146 | 513 | 488 | 1027 |
| Marine VHF | 158 | 474 | 451 | 949 |
| 315 MHz SRD | 315 | 238 | 226 | 476 |
| 433 MHz ISM / 70 cm | 433 | 173 | 164 | 346 |
| 446 MHz PMR | 446 | 168 | 160 | 336 |
| UHF TV | 600 | 125 | 119 | 250 |
| 868 MHz SRD | 868 | 86 | 82 | 173 |
| 915 MHz ISM | 915 | 82 | 78 | 164 |
| ADS-B | 1090 | 69 | 65 | 138 |
| GNSS L1 | 1575 | 48 | 45 | 95 |
| Cellular 1.8–2.1 GHz | 1950 | 38 | 37 | 77 |
| 2.4 GHz ISM | 2450 | 31 | 29 | 61 |
| 3.5 GHz (5G n78) | 3500 | 21 | 20 | 43 |
| 5.8 GHz ISM | 5800 | 13 | 12 | 26 |
Inverse rules: $f\approx 71.2/L_{\lambda/4}$, $f\approx 142.4/L_{\lambda/2}$ (MHz, m); thicker elements resonate shorter still ([dipoles](dipoles-and-monopoles.md#level-1--the-numbers-you-use)).

### Level 2 — gain from size
- **Omni collinears** (a stack of in-phase λ/2 sections, see [collinears](dipoles-and-monopoles.md#collinear-arrays-and-phasing-coils)): a uniform line source of length L ≥ λ has directivity ≈ 2L/λ and elevation half-power beamwidth ≈ 50.8 λ/L degrees: 1 λ ≈ 3 dBi/51°, 2 λ ≈ 6 dBi/25°, 3 λ ≈ 7.8 dBi/17°, 4 λ ≈ 9 dBi/13°. A "6 dBi" 915 MHz omni therefore has ≈ 0.65 m of radiating length; a "6 dBi" 433 MHz omni ≈ 1.4 m. A 6 dBi omni that is 20 cm long is not 6 dBi.
- **Apertures** (dish, horn, panel, patch array): $G\approx e_{ap}(\pi D/\lambda)^2$ (e ≈ 0.5–0.7): 60 cm satellite-TV dish at 11.7 GHz ≈ 35 dBi (3° beam); 1.2 m dish at 1.7 GHz ≈ 24 dBi (HRPT weather satellites); 45 cm at 5.8 GHz ≈ 26.5 dBi ([apertures](horn-reflector-aperture-antennas.md)).
- **Yagis/LPDAs**: gain grows with boom length (≈ ln), not element count ([Yagi](yagi-uda-and-log-periodic.md)).

## Field guide
| Type | What you see | Typical bands | Gain / pattern | Polarization | Where |
|---|---|---|---|---|---|
| **Rubber duck / stubby** | flexible black rubber sleeve 5–20 cm, on SMA/BNC | 136–174, 400–520 MHz (HTs), 433/868/915 (modules), 2.4 GHz | −10 to 0 dBi; omni (donut); efficiency often 10–50 % | vertical | handheld radios, LoRa modules, routers |
| **λ/4 whip** | single straight rod ≈ λ/4, needs ground (body/radials) | everything 27 MHz–6 GHz | ≈ 2–5 dBi over a good ground, 0–2 dBi on a small device | vertical | cars, modules, rockets |
| **5/8 λ whip** | rod ≈ 0.6 λ with a base coil | VHF/UHF mobile | ≈ 3 dB over λ/4 at low angles — only over a large ground | vertical | vehicles |
| **Ground plane** | vertical λ/4 + 3–4 drooping radials | VHF/UHF base | ≈ 2 dBi, horizon-peaked | vertical | base stations, ground stations |
| **Dipole** | two collinear arms, centre feed (often a T-shaped bracket) | HF wires to 6 GHz printed | 2.15 dBi, donut | along the arms | everywhere; FM/TV, HF ham |
| **Yagi-Uda** | boom with parallel rods: one driven (fed, often folded), one longer reflector behind, shorter directors in front | 50 MHz–2.4 GHz (TV, ham, LoRa ground stations) | 7–17 dBi, single forward beam | along the elements (horizontal or vertical) | rooftops, tracking stations |
| **LPDA (log-periodic)** | boom of many rods shrinking steadily toward the front, criss-cross feed | 2:1–10:1 bands: TV, EMC, scanner, cellular | 6–8 dBi, constant over band | along the elements | TV, EMC labs, wideband links |
| **Discone** | horizontal disc (or rods) on top of a cone of rods | 25–1300 MHz (rx), 60–700 MHz in our NEC example | −9 … +3 dBi at the horizon, beam tilts down at high f | vertical | scanners, SDR, monitoring |
| **Patch** | flat square/rectangle on a ground plane (often under a plastic radome) | 1.2–6 GHz, mm-wave arrays | 5–9 dBi per patch, broadside hemisphere | linear or CP (corner cut, two feeds) | GNSS pucks, Wi-Fi panels, radar modules |
| **Axial-mode helix** | coil of wire ≈ λ circumference, pitch ≈ λ/4, on a ground disc | 435 MHz–10 GHz (satellite, tracking) | 8–15 dBic, end-fire beam | circular (winding sense) | satellite ground stations, rocket tracking |
| **QFH (quadrifilar helix)** | four wires twisted round a tube in a "cage" | 137 MHz (NOAA/Meteor), 400 MHz, L-band GNSS | ≈ 2–5 dBic, cardioid hemisphere, no zenith null | circular | weather-satellite rx, GNSS |
| **Collinear omni** | white fibreglass tube 0.5–6 m, no visible elements | 144/430 MHz, 868/915 (LoRa gateways), 2.4 GHz | 3–11 dBi, flat "pancake" beam (13–51°) | vertical | gateways, repeaters, marine |
| **J-pole / slim-Jim** | λ/2 rod on a λ/4 parallel-wire stub (looks like a "J"), often 300 Ω twin-lead | 144/430 MHz | ≈ 2 dBi omni, no ground needed | vertical | hobby base stations |
| **Chip / PCB antenna** | small ceramic chip at a board edge, or a meandered/F-shaped copper trace with a clear copper keep-out | 315 MHz–6 GHz | −10 to +3 dBi, board-dependent | messy | IoT, Wi-Fi/BLE modules, phones |
| **Cellular panel (sector) antenna** | tall grey rectangular boxes (≈ 0.3 × 1.3–2.6 m) in groups of three facing different ways | 700–2700 MHz, 3.5 GHz massive-MIMO boxes | 15–18 dBi, ≈ 65° azimuth, 6–8° elevation, electrical down-tilt | dual slant ±45° | cell towers, rooftops (typical vendor data) |
| **Microwave backhaul dish** | round drum with a flat white radome, 0.3–1.8 m | 6–80 GHz | 30–50 dBi pencil beam | linear (H/V) | towers, point-to-point links |
| **Satellite-TV dish** | offset reflector + LNB on an arm | 10.7–12.75 GHz | 35–39 dBi (60–90 cm) | linear (LNB skew) | homes |
| **Horn** | flared metal mouth | 1–100 GHz | 10–25 dBi | linear | radar, test ranges, dish feeds |
| **Magnetic-mount whip** | whip on a round magnet base, coax out of the side | 27 MHz–6 GHz (vehicles) | as λ/4 whip, roof = ground; base couples capacitively | vertical | temporary vehicle installs |
| **Slotted waveguide / slot array** | metal bar or tube with rows of slots (ship radar "bar") | 3 and 9 GHz radar, 10 GHz | 10–30 dBi fan beam | across the slots | ships, airports ([slots](slot-antennas.md)) |
| **Loop / ferrite rod** | ring (small loop) or rod with a coil | LF–HF receive, RFID | inefficient but low-noise pickup | depends | AM radios, RFID readers ([loops](loop-antennas.md)) |
(Gains and dimensions follow the linked KB pages; cellular-panel numbers are typical vendor datasheet values, not individually verified.)

## Telling look-alikes apart
- **Rubber duck vs whip**: if it is flexible and much shorter than the λ/4 table value for its band, it contains a coil (normal-mode helix) — expect several dB less than a full λ/4 whip ([small-antenna limits](small-antenna-limits.md)).
- **Yagi vs LPDA**: Yagi elements are nearly equal in length with one longer at the back; LPDA elements shrink steadily (constant ratio τ) and the feed line zig-zags between them.
- **Collinear vs plain whip**: a collinear is several λ long (or hidden in a tube); a whip is λ/4 or 5/8 λ. Coils or sleeves at intervals along an exposed vertical are collinear phasing sections (D2 #73).
- **Discone vs ground-plane**: discones have many rods in both a disc and a cone; ground-planes have one vertical and 3–4 radials.
- **Panel vs dish**: panels are flat rectangles with a dipole/patch array inside (sector coverage); dishes are round and very directional.
- **Band from a Yagi**: measure the driven element (≈ λ/2): 345 mm ≈ 433 MHz; 160 mm ≈ 915 MHz; 1 m ≈ 146 MHz.

## Stock antennas are often not well tuned — measure them
Evidence collected for this page:
| Source | Antennas | Best-match frequency | SWR at target | Mismatch loss |
|---|---|---|---|---|
| myembeddedstuff.com (June 2026, NanoVNA) [6] | antenna A bundled with a mesh kit | 852 MHz (SWR 1.30) | 1.32 at 868; 2.02 at 915 | 0.07 / 0.53 dB |
| same | antenna B | 892 MHz (1.29) | 1.98 at 868; 2.02 at 915 | 0.5 dB |
| same | antenna C | 808 MHz (1.20) | 2.9 at 868; 4.0 at 915 | 1.2 / 1.9 dB |
| Nodak Mesh club guide (2026) [7] | several "915 MHz" units | — | some turned out to be relabelled 868 MHz parts (no numbers given) | — |
| Meshtastic documentation [8] | general | — | notes that cheap antennas often carry incorrect frequency labels | — |
| "Testing LoRa antennas at 915 MHz" (Medium, via search snippet only — unverified) [9] | folding stub with/without ground plane | 980 MHz (no ground) / 830 MHz (with ground) | 4.0 / 2.3 at 916 MHz | 1.9 / 0.7 dB |
Lessons:
1. **A mistuned stock antenna typically costs 0.5–2 dB of mismatch loss** (SWR 2–4) — noticeable but not catastrophic; a *mislabelled band* (433 MHz antenna on 868 MHz) costs far more.
2. **The ground matters.** The same stub moved its best match from 980 to 830 MHz when a ground plane was added [9] — a monopole-type antenna must be measured on the device or a representative ground ([dipoles](dipoles-and-monopoles.md#finite-ground-planes-and-small-boards), [PCB antennas](pcb-and-chip-antennas.md)).
3. **Good SWR ≠ good antenna.** A lossy antenna (or a dummy load) can show SWR 1.2; compare received signal strength against a reference dipole on the same link ([antenna measurement](antenna-measurement.md)).
4. **How to measure**: NanoVNA calibrated at the end of the cable you will use (SOL at the antenna connector), antenna mounted as used, hands and metal away, sweep ±20 % around the band; read the frequency of minimum |S11| and the SWR at your band ([NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md)). For LoRa-specific buying and judging advice see [choosing and judging LoRa antennas](../15-lora-ism-radios/choosing-and-judging-lora-antennas.md).

## Design equations & rules of thumb
| Quantity | Rule | Notes |
|---|---|---|
| Band from λ/4 element | f(MHz) ≈ 71.2 / L(m) | thin rod, 0.95 factor |
| Band from λ/2 element | f(MHz) ≈ 142.4 / L(m) | dipole / Yagi driven element |
| Collinear gain | ≈ 10 log(2L/λ) dBi, HPBW ≈ 51λ/L ° | L ≥ λ |
| Aperture gain | 10 log(e_ap(πD/λ)²) | e 0.5–0.7 |
| Mismatch loss | −10 log(1 − Γ²), Γ = (S − 1)/(S + 1) | SWR 2 → 0.51 dB; 3 → 1.25 dB; 4 → 1.94 dB |

## Worked examples
**Example 1 — The white stick on a LoRa gateway.** A 1.3 m fibreglass omni labelled "915 MHz 9 dBi": 1.3 m = 4 λ at 915 MHz → D ≈ 10 log 8 = 9 dBi, elevation beamwidth ≈ 13° — plausible. At a hilltop gateway it covers the horizon well but under-serves nodes close below it (outside the 13° beam); a 3 dBi antenna can serve nearby low nodes better (TTN forum experience [10], anecdotal; physics as above).

**Example 2 — What band is this Yagi?** Driven element (folded dipole) 330 mm, 10 elements on a 1.5 m boom: f ≈ 142.4/0.33 ≈ 430 MHz → 70 cm amateur / 433 MHz ISM; gain ≈ 12–13 dBi for a 2.2 λ boom ([DL6WU designs](yagi-uda-and-log-periodic.md#worked-examples)).

**Example 3 — The panels outside a bedroom window** (D2 #17). Three tall rectangular panels on a pole: cellular sector antennas, ≈ 15–18 dBi with a 65° × 7° beam pointing *outward and slightly down*; a window beside or behind the panel is well outside the main beam. Exposure is regulated by distance-based compliance zones ([RF exposure](../19-regulations-safety/rf-exposure-safety.md)).

**Example 4 — Is the stock "433 MHz" spring antenna right?** Measure: if the S11 minimum sits at, e.g., 470 MHz with SWR 2.5 at 433 MHz, the mismatch loss is 0.9 dB; stretching the spring (lengthening) lowers the resonance. A proper λ/4 wire (164–173 mm) on the board's ground is usually better and costs nothing ([dipoles](dipoles-and-monopoles.md)).

## Practical notes
- Photograph the antenna with a scale reference (a coin or ruler); estimate the longest element; use the table.
- Look at the connector/feed: N or 7/16 DIN on towers (high power), SMA/RP-SMA on modules (RP-SMA is common on Wi-Fi — a mismatch of connector gender is not an RF problem but a mating one; see [connectors](../18-components-parts/connectors-and-cables-parts.md)).
- Labels can be wrong; datasheets with measured S11 and gain patterns are a good sign; "gain" claims without patterns are not.

## Common mistakes & misconceptions
- **"A longer antenna always has more gain."** Only collinear/array structures convert length into (elevation) directivity, and a long *single wire* beyond 1.25 λ splits into lobes ([dipoles](dipoles-and-monopoles.md#level-3--thickness-bandwidth-and-the-limits-of-the-thin-wire-picture)).
- **"The label is the band."** Measure — mislabelled or mistuned stock antennas are common [6]–[8].
- **"Low SWR proves a good antenna."** It proves a match only.
- **"High-gain omnis are better everywhere."** Their flat beam can miss nearby users above or below.
- **"A short rubber duck performs like a whip."** The loading coil and short length cost several dB.

## How to simulate / verify
- `python3 tools/verify/ant2_ident.py` — length table, mismatch-loss table, collinear and dish gain rules (output in `tools/verify/ant2_ident_output.txt`).
- Measure stock antennas with a NanoVNA as described above; compare against a reference dipole via received signal strength.

## Open questions / gaps
- Photo-based identification (images) is not included — text descriptions only.
- Cellular panel and backhaul numbers are generic vendor values, not tied to a datasheet.
- The Medium 915 MHz stub measurements are known only through a search-engine snippet (page blocked); treat as unverified.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — dipoles, Yagis, LPDAs, helices, apertures. (textbook; cited)
2. This KB's antenna pages linked above (dipoles, Yagi/LPDA, helical, patch, PCB, aperture, slot, wideband). (KB)
3. ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — practical antenna types and collinears. (handbook; cited)
4. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — line-source directivity, helices. (textbook; cited)
5. Hackaday, "Identify that antenna by sight," 2022. https://hackaday.com/2022/11/01/identify-that-antenna-by-sight/ — the size-from-wavelength approach (article; search summary).
6. MyEmbeddedStuff, "How to evaluate antennas for Meshtastic / MeshCore using a NanoVNA," June 2026. https://myembeddedstuff.com/how-to-evaluate-antennas-for-meshtastic — three bundled antennas: best match 852/892/808 MHz, SWR at 868/915 MHz (blog measurement — anecdotal; numbers via WebFetch summary, cross-checked for internal consistency).
7. Nodak Mesh, "NanoVNA antenna testing for 915 MHz LoRa mesh nodes," 2026. https://nodakmesh.org/blog/nanovna-antenna-testing-guide — some "915 MHz" antennas found to be relabelled 868 MHz parts (club blog — anecdotal).
8. Meshtastic documentation, "Antenna testing." https://meshtastic.org/docs/hardware/antennas/antenna-testing/ — "A lot of cheap antennas come labeled with an incorrect working frequency" (project documentation).
9. "Testing LoRa antennas at 915 MHz," Medium (home-wireless), https://medium.com/home-wireless/testing-lora-antennas-at-915mhz-6d6b41ac8f1d — stub antenna SWR with/without ground plane (page blocked; numbers from search snippet only — unverified).
10. The Things Network forum, "Using high-gain Yagi (11–23 dBi) antennas for LoRa gateway — don't," https://www.thethingsnetwork.org/forum/t/using-high-gain-yagi-11-23dbi-antennas-for-lora-gateway-don-t/36095 (forum — anecdotal).
11. This repository: `tools/verify/ant2_ident.py` (+ `_output.txt`). (verification)
