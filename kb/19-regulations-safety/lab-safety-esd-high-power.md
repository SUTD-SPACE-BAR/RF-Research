---
title: RF lab and station safety — ESD, high-power RF, no-load transmission, lithium batteries, RF-induced e-match ignition (HERO), lightning and station grounding, and other bench hazards (BeO, high voltage, power lines)
domain: 19-regulations-safety
slug: lab-safety-esd-high-power
tags: [esd, hbm, js-001, gaas, phemt, lna, rf-burns, dummy-load, attenuator, pa-protection, vswr, lithium-battery, lipo, hero, mil-std-464, mil-hdbk-240, ime-slp-20, e-match, pyro, igniter, arming, lightning, surge, station-grounding, bonding, single-point-ground, ground-rod, gas-discharge-tube, quarter-wave-stub, arrester, ground-potential-rise, step-voltage, iec-62305, itu-t-k112, nec-810, rooftop, power-line-clearance, beryllium-oxide, beo, magnetron, high-voltage]
prerequisites:
  - rf-exposure-safety.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
related:
  - ../06-rf-circuits/power-amplifiers.md
  - ../06-rf-circuits/lna-design.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../08-antennas/antennas-on-rockets.md
  - ../14-sdr-dsp/sdr-front-end-protection-and-filtering.md
  - ../08-antennas/dipoles-and-monopoles.md
  - ../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md
  - spectrum-allocation-ism-bands.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# RF lab safety — ESD, high power, no-load transmission, batteries, and e-match RF hazards

> **Safety guidance, not a substitute for your institution's safety procedures, the building owner's
> lightning-protection system, a licensed electrician, or the igniter manufacturer's data.** Last verified
> 2026-09-27 (lightning, grounding and hazard sections 2026-10-13).

## Questions this page answers
- How careful do I need to be with ESD when handling an LNA or a GaAs/pHEMT part?
- What happens if my LoRa module transmits without an antenna?
- Can a 2 W transmitter burn me?
- How far should a transmitter be from an e-match or igniter?
- Can the rocket's own 2 W telemetry radio fire the recovery charges?
- What is HERO and what margin do military standards require?
- How do I test that my avionics bay is RF-safe for pyros?
- Why did my ground-station LNA die at the launch pad?
- How should we handle and fly with lithium batteries?
- How do I protect a rooftop LoRa gateway or a ground-station mast from lightning?
- What is a single-point ground (entry) panel, and why must everything be bonded to it?
- Do I need a lightning arrester on the coax, and which type — gas tube or quarter-wave stub?
- How deep and how many ground rods do I need, and why is "low ground resistance" not the main point?
- Is the roof always the best place for an antenna?
- What should a launch-site ground station do when a thunderstorm approaches?
- How far must an antenna mast be from power lines?
- Are beryllium-oxide parts in old RF transistors and attenuators dangerous?
- Is it safe to use a microwave-oven magnetron or transformer for a project?

## TL;DR
- **ESD**: component sensitivity is classified by the Human Body Model (ANSI/ESDA/JEDEC JS-001; Class 0A < 125 V … 3B ≥ 8 kV) [1]. RF LNAs are often at the sensitive end — e.g. Mini-Circuits PSA4-5043+ (pHEMT LNA): **HBM Class 1B (500 to < 1000 V), Machine Model passes only 35 V** [2]. Handle with wrist strap, grounded mat, and ground the coax shield/centre before connecting to an antenna port.
- **Receiver overload**: the same LNA survives only **+17 dBm CW continuous (+23 dBm for 5 min)** [2]. A 2 W transmitter a metre from a receive antenna can deliver about +10 dBm; our EBYTE modules quote a 10 dBm RX damage threshold ([module page](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)). Keep ≥ 40 dB between co-sited transmitters and receivers on the bench; use a limiter/filter at pad-side ground stations.
- **Never transmit into no load**: an open/short reflects all power back into the PA (|Γ| = 1), stressing the output devices and producing harmonics. Always connect a 50 Ω dummy load or attenuator rated for the power (2 W CW ⇒ ≥ 5 W-rated load for margin).
- **RF burns**: 2 W into 50 Ω is 10 V rms (14 V peak) on the line, but at a high-impedance antenna element (end-fed half-wave ~2 kΩ) it is ~63 V rms — enough for a painful localised RF burn on contact. Don't touch radiating elements while keyed.
- **HERO / e-matches**: MIL-STD-464C requires EIDs to keep **16.5 dB margin below the maximum no-fire stimulus (MNFS)** for safety (induced current ≤ 15 % of no-fire current) and 6 dB otherwise; verification per MIL-HDBK-240 [3]. For commercial detonators IME SLP-20 bases distances on a 40 mW no-fire power: **UHF (450–470 MHz) 1 W → 8 ft, 3 W → 14 ft; handheld ≤ 2 W of unknown mode → 11 ft** [4]. A matched-lead Friis bound with a 16.5 dB margin reproduces the SLP-20 UHF column within ~15 % (`tools/verify/reg_hero_distance.py`): **2 W at 433 MHz on a dipole → 4.3 m; on a 12 dBi Yagi → 13 m**.
- **Inside the rocket** the telemetry transmitter is centimetres from the pyro wiring — far-field distances don't apply. Design (shunted/twisted leads, RF bypass at the pyro connector, FET gates held off, provably dead pyro rail until armed) and **test**: transmit continuously at full power with a dummy igniter and monitor its current/temperature.
- **Lightning**: Singapore has ≈ 176 lightning days a year [11]. Stroke currents are tens of kA (design maximum 200 kA, 10/350 µs) and rise at up to 100–200 kA/µs [8]. Nothing on a hobby mast stops a direct strike. The aim is to **give the current a short outside path to earth and keep everything bonded to one point so it rises in potential together**. A 30 kA stroke into a 40 Ω ground rod lifts the "ground" to 1.2 MV, and 10 m of down-conductor drops 150 kV at only 10 kA/µs (`tools/verify/s2_lightning_grounding.py`). Damage comes from *differences* in potential between separately grounded things.
- **Station grounding recipe**: DC-grounded antenna (static), coax shield bonded at the antenna/mast top, at the mast foot and at a **single-point entry panel** where every cable enters through an arrester (GDT type for DC-fed LNAs; a λ/4 shorted stub is a dead short below its band), panel bonded by a short, straight, ≥ 16 mm² Cu (≥ 6 AWG) conductor to ground rods that are **bonded to the building/mains earth**, no solder-only joints [7][9]. Unplug and disconnect in storms. At a launch field: lower the mast and shelter when thunder is heard; keep igniters shunted.
- **Other hazards**: BeO ceramics in old RF power transistors and high-power loads are harmless intact but toxic as dust (US PEL 0.2 µg/m³) [14]; microwave-oven HV circuits are lethal and store charge; keep masts ≥ their height + 3 m from overhead lines (US OSHA minimum clearance 3.05 m up to 50 kV) [13].
- **Lithium batteries**: spare Li-ion cells/packs travel in carry-on only, terminals protected, ≤ 100 Wh each (101–160 Wh: up to two with airline approval) (FAA PackSafe, 49 CFR 175.10(a)(18)) [5]; charge on a fire-safe surface, never unattended.

## Intuition (no math)
RF hazards in the lab come in three flavours: **too much voltage in a tiny place** (ESD punching through a transistor gate junction), **too much power where it shouldn't be** (a PA reflecting into itself, a transmitter frying a nearby receiver, RF energy heating an igniter's bridgewire), and **energy stored in batteries**. The common defence is the same: control where the energy goes — ground paths for charge, matched loads and attenuators for RF power, distance and shielding for radiated fields, and interlocks/arming for pyrotechnics.

## The math
### Level 1 — voltages and powers
- RMS voltage on a matched line: $V = \sqrt{PZ_0}$: 2 W on 50 Ω → 10 V rms; at a 2 kΩ high-impedance feed point → $\sqrt{2\cdot2000} = 63$ V rms.
- Reflected power into a PA: $P_{ref} = |\Gamma|^2 P_{fwd}$ with $\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ — open/short/no antenna ⇒ $|\Gamma| = 1$ ([reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)).
- Power reaching a nearby receiver: Friis $P_r = P_t + G_t + G_r - 20\log_{10}(4\pi R/\lambda)$; at 433 MHz and 1 m the path loss is 25.2 dB, so 33 dBm + 2 + 2 − 25 ≈ +12 dBm (near-field; order-of-magnitude only).

### Level 2 — RF energy into an igniter
Treat the igniter leads as a receiving antenna delivering at most $P = S\,A_e$ to the bridgewire, where $A_e = G\lambda^2/4\pi$ and $S = \mathrm{EIRP}/4\pi R^2$. The worst case is a resonant, matched pair of leads ($G ≈ 1.64$). Requiring $P \le P_{nf}\cdot10^{-M/10}$ ($M$ = margin in dB) gives
$$R_{safe} = \frac{\lambda}{4\pi}\sqrt{\frac{\mathrm{EIRP}\cdot G\cdot 10^{M/10}}{P_{nf}}}.$$
With $P_{nf}$ = 40 mW (SLP-20 basis) and $M$ = 16.5 dB, 1 W at 460 MHz → 2.84 m versus SLP-20's 8 ft = 2.44 m; 3 W → 4.9 m vs 14 ft = 4.27 m [4] — agreement within 15 %, which supports using the formula for other frequencies/powers. Lower frequencies are worse ($R \propto \lambda$) — SLP-20 recommends 450 MHz and above for mobile transmitters near blasting [4].

### Level 3 — why the far-field bound fails inside the airframe
At 5–30 cm from a 433 MHz transmitter the wiring is in the reactive near field ($R < \lambda/2\pi$ = 11 cm) and couples capacitively/inductively; the pickup depends on loop area, lead routing and how the pyro circuit terminates RF (a FET's drain capacitance, the continuity-sense network, TVS diodes). MIL-HDBK-240 therefore relies on **test** (instrumented EIDs, induced current measurement) rather than calculation for installed systems [3]. RF rectification in semiconductor junctions can also *switch* a circuit (e.g. bias a FET gate), a separate mechanism from bridgewire heating.


## Lightning, surge and station grounding

### Intuition — what a strike does to a station
A lightning flash is a current source: tens of kiloamperes are forced into whatever the channel attaches to, for tens to hundreds of microseconds, with several strokes per flash. You cannot insulate against it and you cannot "ground it away". Earth has resistance, so the current lifts the local ground by megavolts. Every conductor has inductance, so the current front drops hundreds of kilovolts along a few metres of wire. Equipment is destroyed when it sits **between two things that rise by different amounts**, for example a radio whose coax shield is tied to the mast ground and whose power plug is tied to the building's mains earth tens of metres away. Current then flows through the radio. The protective idea is therefore:
1. **Divert** most of the current outside, down a short, straight path from the antenna and mast to earth.
2. **Equalise**: bond every conductor entering the equipment (coax shields, LNA DC feeds, rotator and Ethernet cables, mains earth) to **one point** at the entry, so that the whole station rises and falls together, like a bird on a high-voltage line.
3. **Clamp** the cable *centre* conductors to that point with arresters, which do nothing at RF and conduct only during the surge.
4. **Avoid**: disconnect and lower antennas during storms, and do not be there yourself.

Most damage to amateur and student stations is not from direct strikes but from **nearby** strikes (induced surges on long cables and power lines) and **static** charge on undischarged antennas. Those are what cheap measures prevent.

### The numbers (layered)
**Level 1 — magnitudes.** IEC 62305-1 defines lightning protection levels (LPL) I–IV with design maximum first-stroke currents of 200/150/100/100 kA (10/350 µs, 100 C of charge, 10 MJ/Ω specific energy at LPL I), subsequent strokes of 50/37.5/25/25 kA with steepness **200/150/100/100 kA/µs**, and minimum currents of 3/5/10/16 kA used for the rolling-sphere radii [8]. A typical (median) negative first stroke is of order 30 kA (Berger/CIGRE statistics summarised in IEC 62305-1 Annex A; not read directly). Most of the energy is below about 1 MHz, which is why an RF-band short such as a λ/4 stub does not affect UHF but shorts the surge.

**Level 2 — four formulas** (each computed in `tools/verify/s2_lightning_grounding.py`):
- *Where it strikes.* The electrogeometric striking distance is $r \approx 10\,I^{0.65}$ m (I in kA). The rolling-sphere radii of IEC 62305 (20/30/45/60 m for LPL I–IV) are this formula at the minimum currents 3/5/10/16 kA (20.4/28.5/44.7/60.6 m). A 30 kA stroke has $r$ ≈ 91 m, so any mast or person that is the tallest thing within ≈ 90 m on an open field is a likely attachment point.
- *Ground rod resistance* (Dwight [16]): a rod of length $L$ and radius $a$ in soil of resistivity $\rho$ (Ω·m) has
$$R = \frac{\rho}{2\pi L}\left[\ln\frac{4L}{a} - 1\right].$$
A 2.4 m × 16 mm rod in 100 Ω·m soil gives **40 Ω** (the script's independent average-potential solution agrees within 0.1 %). Soils range from 30 Ω·m (loam) to 1000 Ω·m or more (city fill, dry sand) (ITU-T K.112 Table B.1 [7]), giving 12–400 Ω per rod. Two rods spaced at least one rod length apart give ≈ 22–24 Ω, not the ideal 20 Ω, because their potential fields overlap.
- *Ground potential rise and step voltage.* $V_{GPR} = IR$: 30 kA × 40 Ω = **1.2 MV**. Around a hemispherical electrode the surface potential is $V(r) = \rho I/(2\pi r)$, so the voltage across a 1 m stride 10 m from the strike point is $\frac{\rho I}{2\pi}\left(\frac{1}{10} - \frac{1}{11}\right)$ = **4.3 kV** (30 kA, 100 Ω·m), and 80 kV at 2 m. This is why standing near a struck mast, or lying on the ground, is dangerous.
- *Inductive drop.* A straight round conductor of length $l$ and radius $a$ has partial inductance $L \approx \frac{\mu_0 l}{2\pi}\left[\ln\frac{2l}{a} - 1\right]$, i.e. **≈ 1–1.5 µH/m**. 10 m of 8 mm mast or coax shield is 15 µH: at 10 kA/µs it drops **150 kV**, and at 100 kA/µs 1.5 MV. A 50 mm strap is ≈ 1.0 µH/m against 1.4 µH/m for 6 AWG wire. Shortness and directness matter more than the strap.

**Level 3 — induced surges from nearby strikes.** A stroke current $I$ at distance $d$ produces a magnetic field $\mu_0 I/(2\pi d)$. A cable loop of area $A$ picks up $V = \mu_0 A\,(dI/dt)/(2\pi d)$. A 100 m launch-controller firing line with its two leads 0.5 m apart ($A$ = 50 m²) sees **0.5 kV at 200 m and 2 kV at 50 m** for a modest 10 kA/µs. Twisting the leads (residual area ≈ 1 %) cuts this a hundredfold. The same mechanism drives surges into long coax, rotator and mains cables, which is why arresters and bonding are needed at the *entry* even when the mast itself is never struck. Ground-potential differences along buried cables add a resistive component. The real coupling depends on geometry; these are orders of magnitude.

### Protection hierarchy for a student station
| Layer | What | Why / rule | Source |
|---|---|---|---|
| 0. Avoid | Disconnect feeders outside the building and lower portable masts when storms are forecast; switch off and unplug | the only protection against a direct strike that a hobby budget can buy | practice; [15] |
| 1. Static bleed | **DC-grounded antenna** (folded dipole, J-pole, gamma/shunt-fed Yagi) or a **λ/4 shorted stub** across the feed | wind and rain charge an isolated element to kV; the DC path drains it ([dipoles § ground](../08-antennas/dipoles-and-monopoles.md)) | [14 page](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md) |
| 2. Air termination and down-conductor | mast top above the antennas (or within the building's LPS protection zone on a roof), metal mast as down-conductor, connected to earth by the shortest path | K.112: a metallic pole can itself serve as the down-conductor; on a roof bond to the building's LPS at ≥ 2 points | [7] |
| 3. Feeder bonding | bond the coax shield to the mast **at the top**, **at the foot** where it leaves the mast (K.112: also at the bend if the horizontal run is ≥ 10–20 m), and **at the entry panel** | the shield then carries its share of current to earth outside instead of into the shack | [7] |
| 4. Single-point entry panel | one metal bulkhead plate or bar where *every* conductor enters: coax arresters, LNA DC/bias lines, rotator and control cables, Ethernet/PoE surge protector, and the mains SPD as near as practical | everything referenced to one point → no potential difference across equipment | [7][9] |
| 5. Earthing | panel → ground rod(s)/ring by a short, straight conductor (≥ 16 mm² Cu so it does not melt [7]; US NEC 810: ≥ 10 AWG to the discharge unit, ≥ 6 AWG between electrodes); rods bonded to the **building's mains earth**; exothermic, crimped or listed clamps, **no solder-only joints**; bends ≥ 200 mm radius, no hairpins | the bond to mains earth is what prevents a potential difference between "radio ground" and "power ground"; solder melts at stroke current | [7][9] |
| 6. Inside | equipment chassis bonded to the panel by short straps; masthead LNA behind a GDT plus a limiter/low-C TVS ([SDR front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)) | the arrester's let-through (≈ 220 µJ at 3 kA for a GDT protector [10]) still kills an LNA | [10] |

Earth resistance is secondary. ITU-T K.112 asks for "as low as 10 Ω" where feasible, but states the main objective of the earthing network is **equipotential bonding** [7]. A single rod in poor soil (> 100 Ω) with good bonding protects equipment better than a 5 Ω earth with an unbonded second "radio ground".

### Arresters for coax: GDT versus λ/4 stub
| Type | How it works | Good for | Watch out |
|---|---|---|---|
| **Gas-discharge tube (GDT)** coax protector, DC-pass or DC-block | a sealed gap from centre to shield that ionises above its turn-on voltage (e.g. **600 V ± 20 %**) and conducts kA; DC-block versions add a series capacitor | broadband (e.g. 125–1000 MHz, 0.1 dB loss, 50 kA 8/20 µs, 220 µJ let-through for a PolyPhaser IS-50NX-C2 [10]); DC-pass versions carry masthead-LNA bias | slow (µs) and leaves hundreds of volts let-through → follow with a limiter/TVS for an LNA; tubes wear out after large surges, so inspect after storms. Its turn-on must exceed the RF peak: 2 W is 14 V peak (28 V at full mismatch), far below 600 V |
| **λ/4 shorted-stub** protector | a quarter-wave stub from centre to shield is an open circuit at $f_0$ and a short at DC and low frequencies | very high surge rating, nothing to wear out, narrowband: return loss > 30 dB over 420–450 MHz for a 433.92 MHz stub (script); effectively 0 Ω below 1 MHz | **shorts DC**, so no LNA bias through it; it is also a λ/2 short at $2f_0$, so a 433 MHz stub **kills 868 MHz**. Do not share a 433/868 diplexed feed through one |
| Low-capacitance TVS / PIN limiter | clamps residual let-through at the equipment | the last stage before an LNA or SDR | capacitance costs return loss at GHz; see [14 page](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md) |

### Bonding layout, described in words
Antenna (DC-grounded) at the top of a metal mast. The coax runs down the mast and is clamped to it with a shield-bonding kit just below the antenna and again just above the mast foot. The mast foot is bonded to a ground rod at its base. The coax then runs along (not over) the ground or wall to the building, where it enters through a metal **entry panel** mounted on the outside wall at the point of entry. On the panel, each coax passes through a bulkhead arrester. LNA bias, rotator and Ethernet cables pass through their own surge protectors on the same panel. The panel is bonded by a short, straight heavy conductor to a ground rod directly below it. That rod is bonded to the mast-foot rod (and to any others), and the rod system is bonded to the building's main earthing terminal by a licensed electrician. Inside, the radio, PC and power supply chassis are strapped to an indoor bar that is itself bonded to the panel. No cable reaches the radio without passing the panel.

### Rooftop gateways and "the roof is always best"
Height does help a LoRa gateway: horizon and Fresnel clearance grow with mast height ([Fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)). But a roof is not automatically the best spot:
- **It puts the antenna in the strike zone.** The rolling sphere touches roof edges and corners first. Any antenna must sit inside the building's air-termination protection zone or carry its own air terminal bonded to the building's lightning protection system (LPS). K.112 also warns that adding a mast that raises the building may require the LPS risk assessment to be redone, and that cable trays should not run along the roof edge [7]. In Singapore the building's LPS follows **SS 555** (IEC 62305-based; the 2010 edition was the Building Control "deemed-to-satisfy" standard from 1 July 2011) and belongs to the building owner [12]. On campus or an HDB block, get facilities management's written permission and have their electrician bond to their LPS. Do not drill into or clamp onto it yourself.
- **Long feeders cost what the height gained.** 20 m of LMR-240-class cable is ≈ 3.4 dB at 433 MHz and ≈ 5 dB at 868–923 MHz. Mount the radio at the antenna (a weatherproof gateway with PoE) and bring data down on Ethernet through a surge protector, or better on fibre, which carries no surge at all.
- **Rooftops are crowded RF sites**: cellular and paging transmitters a few metres away overload receivers ([SDR front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)).
- **Access and falls**: working at height on a roof edge needs the building's permit-to-work.

Often a 6–10 m mast at ground level in a clear spot, or a window/balcony mount below roof level, gives most of the coverage with a fraction of the lightning exposure.

### Launch-site ground station checklist
- [ ] **Check the forecast and watch the sky.** Lightning strikes more than 10 miles (≈ 16 km) from the rain; if you can hear thunder you are within striking distance; wait **30 minutes after the last thunder** before resuming [15].
- [ ] **When thunder is heard: stop pad work, lower the mast, disconnect the feeder at the radio, and shelter in a building or hard-topped vehicle**, not under the mast, the canopy or a tree. A tent or gazebo is not shelter.
- [ ] **Igniters stay shunted** (shorting plugs) until final arming; firing lines are twisted pairs laid flat on the ground. An unshunted 100 m line can pick up 0.5–2 kV from a strike a few hundred metres away (Level 3 above).
- [ ] **Bond the station as an island.** Mast foot, coax shield, battery negative or chassis, laptop and generator frame all go to one bar or ground stake by short leads. The stake drains static and equalises; it does not make a direct strike survivable.
- [ ] **Static**: on dry, windy days discharge the coax (short centre to shield) before connecting it to the LNA or SDR. Use DC-grounded antennas.
- [ ] **Power lines**: site the mast so that, if it falls, it stays clear of every overhead line by more than the clearance below. Guy and coax swing counts.
- [ ] **Generators**: earth the generator frame per its manual and keep it on the same bonding island.

### Power-line clearance
Contact between an antenna, mast or guy wire and an overhead line is the most lethal antenna-installation hazard. US OSHA requires an unqualified person and any conductive object they handle to stay **≥ 3.05 m (10 ft)** from lines up to 50 kV to ground, plus 0.10 m per 10 kV above that [13]. Siting rule used here: **distance to the nearest overhead line ≥ mast height + 3 m** in every direction the mast could fall. Never raise a mast near lines, and treat "insulated" overhead cables as bare. Power lines are also an RF *noise* source (corona and gap discharges, broadband up to UHF), so moving away pays twice ([thermal and man-made noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).

## Other bench and station hazards
| Hazard | Where you meet it | Why it hurts | Handling rule |
|---|---|---|---|
| **Beryllium oxide (BeO) ceramic** | flange-package RF power transistors (older VHF/UHF/microwave parts), high-power resistive terminations, attenuators and some resistors, some magnetron and tube insulators | harmless as an intact solid; **inhaled dust or fumes** from broken, ground, filed or burnt parts can cause chronic beryllium disease and lung cancer. US OSHA limits are tiny: PEL 0.2 µg/m³ (8 h TWA), STEL 2.0 µg/m³, action level 0.1 µg/m³ [14] | check the datasheet or "BeO" marking (colour is not a reliable indicator); never crush, grind, sand, file or drill; do not heat a part until it cracks; if one breaks, wet-wipe the fragments, bag them and dispose of them as hazardous waste; prefer AlN-substrate parts in new designs |
| **Microwave-oven magnetron and HV supply** | salvaged oven parts, DIY "radar" or heaters | the oven's HV transformer and doubler put kilovolts on the magnetron cathode, and the HV capacitor can hold a lethal charge after unplugging (typically ≈ 2 kV rms secondary, ≈ 4 kV peak; unverified — repair literature). Outside its cavity a magnetron radiates hundreds of watts at 2.45 GHz | do not run an oven magnetron outside the oven; if you open one, unplug it, discharge the capacitor through an insulated resistor and verify with a meter; see [DIY radar hardware](../11-radar/diy-radar-hardware.md) for low-power alternatives |
| **High-voltage PAs** | valve (tube) amplifiers (kV plate supplies), 50 V GaN/LDMOS stages, tuners | DC shock; RF voltages of hundreds of volts at tuner capacitors and high-impedance feed points (§ Level 1) | interlocked covers, bleeder resistors, one hand in the pocket, discharge sticks for kV supplies |
| **RF burns** | touching a radiating element or open-wire line while keyed | localised deep heating at the contact point (63 V rms at a 2 kΩ point for 2 W) | never touch elements while transmitting; key only into a load during adjustment |
| **Eye lens** | looking into a waveguide, horn or along a keyed Yagi boom at short range | the lens has poor blood flow, so it cannot shed heat (the heating mechanism is explained in [RF exposure](rf-exposure-safety.md)) | never look into an energised horn or waveguide; respect the exposure distances on that page |
| **Masts and towers** | raising and guying ground-station masts | falls, a mast toppling onto people or lines | two people for raising, gloves and helmets, guys anchored before climbing; no work in wind or storms |

## Design equations & rules of thumb
| Item | Value / rule | Source |
|---|---|---|
| HBM classes | 0A < 125 V; 0B 125–250; 1A 250–500; 1B 500–1000; 1C 1–2 kV; 2 2–4 kV; 3A 4–8 kV; 3B ≥ 8 kV | JS-001-2011 via [1] |
| Example LNA | PSA4-5043+: HBM 1B, MM 35 V, max RF input +17 dBm CW | [2] |
| EID safety margin | 16.5 dB below MNFS (15 % current); 6 dB reliability | MIL-STD-464C §5.4 [3] |
| SLP-20 basis | 40 mW no-fire (P = 0.999 at 95 % confidence) | [4][6] |
| SLP-20 UHF distances | 1 W 8 ft; 3 W 14 ft; 5 W 18 ft; 10 W 25 ft (450–470 MHz) | [4] Table 3 |
| Handheld unknown ≤ 2 W | 11 ft | [4] §F |
| Dummy load | ≥ 2.5× the CW power rating; check its VSWR at the operating frequency | practice |
| Bench isolation | ≥ 40 dB between transmitter and any receiver input | practice / [module page] |
| Spare Li-ion | carry-on only, ≤ 100 Wh; two of 101–160 Wh with approval | [5] |
| Striking distance | $r ≈ 10 I^{0.65}$ m; rolling sphere 20/30/45/60 m (LPL I–IV) | [8], script |
| Lightning design currents | 200/150/100 kA (10/350 µs); subsequent 200/150/100 kA/µs | IEC 62305-1 via [8] |
| Ground rod | $R = \frac{\rho}{2\pi L}[\ln(4L/a) - 1]$; 2.4 m × 16 mm, 100 Ω·m → 40 Ω | [16], script |
| GPR / step voltage | $IR$; $\rho I/(2\pi)\,(1/r - 1/(r+1))$: 30 kA, 100 Ω·m, 10 m → 4.3 kV | script |
| Conductor inductance | ≈ 1–1.5 µH/m → 10 m at 10 kA/µs = 150 kV | script |
| Loop pickup from a nearby stroke | $\mu_0 A\,(dI/dt)/(2\pi d)$: 50 m², 200 m, 10 kA/µs → 500 V | script |
| Earth target | equipotential first; ≤ 10 Ω "whenever feasible" | K.112 [7] |
| Bonding conductor | ≥ 16 mm² Cu (melting, 10 MJ/Ω); NEC 810: ≥ 10 AWG to arrester, ≥ 6 AWG between electrodes; no solder-only joints | [7][9] |
| GDT coax arrester | 600 V turn-on, 50 kA 8/20, 0.1 dB, 125–1000 MHz, 220 µJ let-through | [10] |
| λ/4 stub arrester | open at $f_0$, short at DC and $2f_0$ | script |
| Power-line clearance | ≥ 3.05 m (≤ 50 kV) + 0.1 m/10 kV; site at ≥ mast height + 3 m | [13] |
| Beryllium | PEL 0.2 µg/m³, STEL 2.0 µg/m³ | [14] |
| Storm rule | thunder audible → stop and shelter; resume 30 min after the last thunder | [15] |

## Worked examples
**1. Pad checkout with the rocket's own 2 W radio.** Team members connect e-matches with the flight computer powered. If the telemetry is transmitting, the e-match leads are within 30 cm of a 2 W source — inside every far-field safe distance (4.3 m with margin). Procedure: **radio silent (TX disabled in firmware) until the pad is cleared and the pyro channels are armed remotely/by switch**, or prove by test (example 3) that the installed configuration has ≥ 16.5 dB margin.

**2. A second team's 5 W transmitter on the next rail at 3 m.** SLP-20 UHF column: 18 ft (5.5 m) for 5 W — closer than recommended for commercial detonators. Coordinate with the range safety officer; hobby e-matches may have lower no-fire ratings than SLP-20's reference detonator.

**3. RF safety test of the avionics bay (recommended, per MIL-HDBK-240 philosophy).** Replace each e-match with a dummy of the same resistance fitted with a fine thermocouple (or use a low-level current probe/diode detector across it), install the bay fully wired in the airframe, transmit continuously at maximum power on each radio and each frequency to be used, and log the induced current. Pass criterion: induced current ≤ 15 % of the e-match manufacturer's no-fire current (16.5 dB). Repeat with pyro channels "disarmed" and "armed but not firing". (Numbers: `tools/verify/reg_hero_distance.py` for the far-field context.)

**4. Ground-station LNA at the pad.** Receive Yagi 3 m from a 2 W transmitter on the same band: path loss at 433 MHz and 3 m ≈ 34.7 dB; received ≈ 33 + 2 + 12 − 34.7 ≈ +12 dBm into the LNA — near the PSA4-5043+ continuous limit (+17 dBm) and far above any receiver's blocking level. Fit a limiter or bypass the LNA until launch; keep the Yagi pointed away from the pad transmitters during checkout.

**5. Rooftop LoRa gateway on a campus block.** Antenna: a 3 dBi fibreglass collinear at 923 MHz on a 2 m pole. The building already has a Class III LPS (rolling sphere 45 m). Plan: place the pole ≥ 2 m back from the parapet, inside the protection zone of an existing air terminal (or add one, bonded to the LPS at two points, by the building's contractor); bond the pole base to the LPS roof conductor; put the gateway in an IP65 box at the pole foot with a 1 m jumper; bring data down over PoE through a PoE surge protector at the roof box and another at the indoor end, both bonded locally. Feeder loss: 1 m of LMR-240 (≈ 0.25 dB) instead of 25 m (≈ 6 dB), which buys ≈ 6 dB, roughly what the extra 10 m of height bought. If facilities refuse roof access, a window-mounted antenna with the gateway indoors loses height but has no strike exposure.

**6. Field ground station, approaching storm.** 5 m aluminium mast with an 11 dBic crossed Yagi, masthead LNA (bias tee), 10 m coax to a table. Bond at a single steel stake at the mast foot: mast, coax shield (via a GDT arrester with DC pass for the LNA bias), laptop/SDR chassis and battery negative, all with short leads. When thunder is heard at the 10:30 launch window: an active strike is within ≈ 16 km. Stop, lower the mast (≈ 2 min), unplug the coax at the SDR, everyone into the cars, and resume no earlier than 30 min after the last thunder. Why not "ride it out" on the bonding? A strike to the mast (a 30 kA stroke has a 91 m striking distance; the mast is the tallest object) would lift the stake by $IR$ ≈ 30 kA × 50 Ω = 1.5 MV and put kilovolts across every stride near it. Bonding saves the equipment from *nearby* strikes, not people from a direct one.

**7. Choosing an arrester for the 433 MHz ground station.** With an LNA powered up the coax: a λ/4 stub would short the 5 V bias, so use a DC-pass GDT protector (or a DC-block GDT plus a bias-tee *after* it, with the bias line given its own protector). Without an LNA: a 433 MHz λ/4 stub is ideal (> 30 dB return loss over 420–450 MHz, nothing to wear out). If the same feed also carries 868 MHz through a diplexer, the stub's 868 MHz short rules it out: use a broadband GDT. In every case follow with the limiter/TVS from the [14 page](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md), because the GDT lets through hundreds of volts for a microsecond.

## Practical notes
- **ESD station**: wrist strap to a common ground point, dissipative mat, ionizer for insulating plastics; store RF parts in shielding bags; touch the connector shell before the centre pin; discharge long coax runs (they charge like capacitors, especially outdoors in dry wind) before mating to an LNA.
- **Antenna ports are exposed ESD entry points**: a DC-grounded antenna (folded dipole, grounded quarter-wave stubs) or a GDT/low-capacitance TVS at the ground-station input protects the LNA.
- **PA protection**: set the EBYTE module to low power for bench work; power up only with load connected; monitor supply current (a module transmitting into an open draws abnormal current or overheats).
- **Attenuator ratings**: 2 W into a 1 W SMA attenuator fails; the first pad in a chain dissipates almost all the power.
- **High voltage in HF amplifiers and tuners** (if you build them): RF voltages of hundreds of volts at tuner capacitors; burns are deep and painful.
- **Pyro/RF board design** (consistent with the Space Bar design lessons: pyro rail must be provably dead unless armed): RF bypass (100 pF + ferrite) at the pyro connector, twisted and shielded igniter leads, shorting shunts until arming, gate pull-downs on firing FETs, and keep the LoRa antenna and its feed away from pyro wiring.
- **Lithium packs**: balance-charge in a LiPo bag on a non-flammable surface; storage at ~50 % charge; inspect for swelling after hard landings; for air travel follow [5] and the airline's stricter limits.
- **Magnetron and pulse-modulator numbers** (energy per pulse, power density near a surplus magnetron): [11 DIY radar § tubes and pulse modulators](../11-radar/diy-radar-hardware.md#microwave-tubes-and-pulse-modulators).

## Common mistakes & misconceptions
- **"LoRa modules are low power, ESD doesn't matter."** The RF front end is the most ESD-sensitive part of the board.
- **"Transmitting briefly without an antenna is fine."** Full reflection for even a packet can damage some PAs and radiates harmonics from the PCB.
- **"The igniter is only 1 Ω, RF can't heat it."** Resonant leads can deliver tens of milliwatts; margins are specified in dB for this reason.
- **"The flight computer isn't armed, so RF can't fire anything."** RF can bias FET gates or couple around an open switch; test the installed system.
- **"A good ground rod makes my station lightning-proof."** Nothing on a hobby budget survives a direct strike, and a low earth resistance matters less than bonding everything to one point (K.112). At 30 kA even a 10 Ω earth rises 300 kV.
- **"A separate 'clean' RF ground rod for the radio is better."** An unbonded second ground is exactly what lets a surge flow through the radio between the two grounds. Bond every rod to the building's mains earth.
- **"The roof is always the best spot."** Height helps coverage, but a roof puts the antenna in the strike zone, ties it to the building's LPS and its owner, often adds a long lossy feeder, and shares the roof with strong transmitters. Mounting the radio at the antenna and avoiding the roof edge usually matter more.
- **"Soldered ground connections are best."** Stroke current melts solder; use clamps, crimps or exothermic welds (NEC 250.70).
- **"Coil the excess ground wire neatly."** A coil is an inductor (≈ µH) at the surge front. Keep ground leads straight and short, with gentle bends.
- **"A gas tube protects my LNA."** It fires at hundreds of volts after microseconds; the LNA needs a limiter or TVS behind it.
- **"A quarter-wave stub protector works on every band through my diplexer."** It is a short at DC and at $2f_0$.
- **"Insulated overhead cables are safe to touch with a mast."** Treat every overhead line as live and bare; keep the mast's fall radius plus 3 m clear.
- **"BeO parts are poisonous to handle."** Intact parts are safe to handle; the danger is dust or fumes from breaking or machining them.
- **"Safe distances from SLP-20 apply to hobby e-matches."** SLP-20 addresses commercial detonators with a specific no-fire rating; use your igniter's data and margin.

## How to simulate / verify
- `python3 tools/verify/reg_hero_distance.py` — matched-lead Friis bound for igniter pickup vs distance with 0/6/16.5 dB margins; SLP-20 comparison.
- `python3 tools/verify/reg_rf_exposure.py` — human-exposure distances for the same transmitters.
- `python3 tools/verify/s2_lightning_grounding.py` covers: striking distance vs rolling-sphere radii; Dwight rod resistance against a numerical average-potential solution, with soil-table values; GPR and step voltage; partial inductance and L·di/dt; loop pickup from a nearby stroke; λ/4-stub return loss and the DC/2f₀ short; GDT turn-on vs RF peak voltage. ALL PASS.
- Measure your earth with a clamp-on earth tester or the fall-of-potential / four-point methods in ITU-T K.112 Annex B. Inspect GDT arresters (DC insulation resistance) after nearby strikes.
- NEC-2 model of the airframe wiring + antenna to estimate coupling (advanced); bench test per worked example 3 is decisive.

## Open questions / gaps
- No-fire current/power ratings for the e-matches the team uses (manufacturer data not collected here).
- MIL-HDBK-240A (2011) test procedures were not read directly (standard summaries and MIL-STD-464C only).
- IEC 62305-1 and NFPA 780 were not read directly (paywalled). LPL values come from a manufacturer guide [8] and a search summary of the IEC table. The ≈ 30 kA median stroke is from Berger/CIGRE as summarised in IEC 62305-1 Annex A (not read). ARRL's *Grounding and Bonding for the Radio Amateur* was not read; ITU-T K.112 and the NEC Article 810 summary [9] were used instead.
- The current SS 555 edition (2010 confirmed; a 2018 edition is cited only by third parties) and the Singapore wiring-code rules for bonding to a building's main earthing terminal were not checked. Have the building's licensed electrical worker do that connection.
- Magnetron/oven HV values are typical repair-literature figures, not from a manufacturer.
- Induced-voltage numbers use a simple infinite-line model; real coupling depends on geometry and the return-stroke channel.
- Newer JS-001 editions' class boundaries (e.g. sub-divisions of Class 0) not verified.

## Sources
1. ANSI/ESDA/JEDEC JS-001-2011 HBM classification table, as reproduced by Desco Industries, "ESD Sensitivity — Classifications — Withstand Voltage" (2013). https://desco.blog/2013/10/15/esd-sensitivity-classifications-withstand-voltage/ (standard via vendor summary)
2. Mini-Circuits, *PSA4-5043+ Monolithic Amplifier* datasheet Rev. D — ESD rating (HBM Class 1B, MM 35 V), absolute maximum input power. https://www.minicircuits.com/pdfs/PSA4-5043+.pdf (datasheet)
3. US DoD, *MIL-STD-464C Electromagnetic Environmental Effects Requirements for Systems* (1 Dec 2010), §5.4 HERO and EID margins (16.5 dB / 6 dB of MNFS; 15 % no-fire current rationale), verification per MIL-HDBK-240. (military standard; copy via acqnotes.com)
4. Institute of Makers of Explosives, *SLP-20 Safety Guide for the Prevention of Radio Frequency Radiation Hazards in the Use of Commercial Electric Detonators* (December 2011) — §F handheld sources, Table 3 distances, 40 mW no-fire basis, precautions (higher frequencies preferred, small wiring loops). (industry safety guide)
5. FAA, "PackSafe — Lithium Batteries" (last updated 11 Aug 2026), citing 49 CFR 175.10(a)(18). https://www.faa.gov/hazmat/packsafe/lithium-batteries (regulator guidance)
6. MSHA Program Policy Letter P13-V-09 (12 Jul 2013) — SLP-20 40 mW no-fire basis, surface-blasting applicability. https://www.msha.gov/compliance-enforcement/compliance-assistance/program-policy-letters/p13-v-09 (regulator)
7. ITU-T, *Recommendation K.112 (05/2021): Lightning protection, earthing and bonding — practical procedures for radio base stations* — §6.1 (equipotential objective; ≤ 10 Ω where feasible; ring electrode), §6.3.3 (feeder bonded at tower top, bending point if ≥ 10/15/20 m, and entry bar; unshielded cables via SPDs at three points), §6.3.4 (welded/crimped joints), conductor table notes (≥ 16 mm² Cu to avoid melting at 10 MJ/Ω), §7 (rooftop sites: share the building LPS, ≥ 2 connection points, no cable tray along the roof edge, re-assess risk if the RBS raises the building), Annex B Table B.1 (soil resistivity). https://www.itu.int/rec/T-REC-K.112 (standard)
8. ABB, *Total Solution to Earthing & Lightning Protection — Technical reference IEC/BS EN 62305-1…4* (9AKK106354A3360) — LPL maximum/minimum currents (200/150/100/100 kA; 3/5/10/16 kA), rolling-sphere radii 20/30/45/60 m, mesh sizes. https://library.e.abb.com/public/ee4d371685e544e09e8d9712fbd716c9/IEC%20BS%20EN%2062305%201%20-%204.pdf (manufacturer guide to the standard). IEC 62305-1:2010 Table 3 values for charge, specific energy and subsequent-stroke steepness taken from a search summary of the standard's table (secondary).
9. W. D. Reeve, "Antenna system bonding and grounding requirements in the National Electrical Code" (Dec 2011) — NEC 810.20 (antenna discharge units), 810.21 (conductor material, straight runs, ≥ 10 AWG Cu, ≥ 6 AWG bond between electrodes, intersystem bonding termination), 250.70 (no solder-only connections). https://reeve.com/Documents/Articles%20Papers/Reeve_AntennaSystemGroundingRequirements.pdf (engineering paper on a US code — practice reference, not Singapore law)
10. PolyPhaser (Infinite Electronics), *IS-50NX-C2-ME Type N coaxial RF surge protector* datasheet rev 1.1 (2020) — gas tube + blocking capacitor, 125–1000 MHz, 0.1 dB, VSWR 1.1, 50 kA (IEC 61000-4-5 8/20 µs), 600 V ± 20 % turn-on, 220 µJ throughput at 3 kA, 375/125/50 W by band. https://www.polyphaser.com (datasheet)
11. Meteorological Service Singapore, "Weather systems" — ≈ 176 lightning days per year (Changi climate station), peak in November then April–May; "one of the highest lightning strike rates in the world". https://www.weather.gov.sg/learn_weather_systems/ (national met service)
12. Singapore Standards Council, *SS 555:2010 Protection against lightning*, Parts 1–4 (based on IEC 62305:2006; replaces CP 33:1996), preview pages; Institution of Engineers Singapore circular on BCA adoption (compliance for plans submitted from 1 July 2011). http://www.singaporestandardseshop.sg ; https://www.ies.org.sg/wp-content/uploads/circulars13Jan11a.pdf (national standard — previews/secondary only)
13. US OSHA, 29 CFR 1910.333(c)(3) — minimum approach to overhead lines 10 ft (305 cm) for ≤ 50 kV, + 4 in per 10 kV above; vehicles/equipment 10 ft. https://www.law.cornell.edu/cfr/text/29/1910.333 (regulation; used as a reference value)
14. US OSHA, 29 CFR 1910.1024 (beryllium): PEL 0.2 µg/m³ 8 h TWA, STEL 2.0 µg/m³ (15 min), action level 0.1 µg/m³; articles not processed by the employer are out of scope; OSHA "Beryllium" topic page (CBD, lung cancer; exposure arises in processing, not use of finished articles). https://www.law.cornell.edu/cfr/text/29/1910.1024 ; https://www.osha.gov/beryllium (regulation / agency)
15. NOAA JetStream, "Lightning safety" (lightning can strike > 10 miles from the rain; if you hear thunder you are within striking distance; wait 30 minutes after the last thunder); OSHA 3863 *Lightning Safety When Working Outdoors*. https://www.noaa.gov/jetstream/lightning/lightning-safety ; https://www.osha.gov/sites/default/files/publications/OSHA3863.pdf (agency guidance)
16. H. B. Dwight, "Calculation of resistances to ground," *Electrical Engineering* 55(12), 1319–1328, Dec 1936 — single-rod formula; also in IEEE Std 142 (Green Book). (peer-reviewed, historical; formula re-derived and checked numerically in the script)
