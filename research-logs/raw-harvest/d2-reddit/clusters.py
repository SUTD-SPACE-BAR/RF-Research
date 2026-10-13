#!/usr/bin/env python3
"""Group partial/missing rows into topic clusters and rank them. Prints a markdown table + unmatched rows."""
import json, glob, os, re, math, collections, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:1]
exec(open(D + "/gen.py").read().split("STN = ")[0])  # reuse loading of rows/meta

# (key, title, relevance 1-3, regex over q+page+note, target, needs, D1 relation)
C = [
 ("learn", "RF learning roadmap: books, courses, videos by level", 3, r"\bLRN\b|rf-learning-roadmap",
  "NEW 00/rf-learning-roadmap (companion to 00/math-roadmap-for-rf)",
  "Graded path (absolute beginner → hobby builder → EE student → RF/microwave → specialisms) with 1–2 books, one free course/video series and one bench tool per stage; which book for whom (Bowick/ARRL/EMRFD first, Pozar/Lee as the core, Balanis/Stutzman for antennas, Razavi for RFIC, Skolnik/Richards for radar, Lyons/PySDR for DSP); how to read Pozar; map each chapter to KB pages; physics- and CS-background entry points.",
  "NEW (extends D1 #24)"),
 ("projects", "Beginner project ladder (\"hello world\" of RF)", 3, r"first-rf-projects|sdr-receiver-build",
  "NEW 20/first-rf-projects (+ planned 20/sdr-receiver-build)",
  "Five to eight graded builds with bill of materials and a pass/fail measurement each: RTL-SDR + dipole; NanoVNA-tuned 433/915 MHz dipole; LoRa link range test; crystal/AM radio; LC filter measured on a NanoVNA; FM receiver in GNU Radio; HB100 Doppler radar; small LNA board. Include what is legal to transmit.",
  "reinforces D1 #24"),
 ("antid", "Antenna identification field guide (\"what is this antenna?\")", 2, r"antenna-identification|visual ID|small-cell|photo ID",
  "NEW 08/antenna-identification-field-guide",
  "Photo-free text guide to recognising common antennas by shape/size → band → service: cellular sector panels and small cells, microwave backhaul dishes/radomes, DAS, HF beams/log-periodics, HF DF rings, VHF/UHF collinears, ADS-B/AIS/GNSS pucks, trunked-radio and paging sites, satellite dishes; how to estimate the band from element length; where to look up licences.",
  "NEW"),
 ("sigid", "Signal identification workflow (unknown signals, HD Radio, HF modes)", 2, r"signal-identification|signal-ID|encoding|bitstream|rtl_433|URH",
  "NEW 14/signal-identification (or section in 14/software-demodulation)",
  "Procedure: note frequency → band plan/allocation → bandwidth and shape → modulation clues (constant envelope, tones, symbol rate via FFT of |x|² or cyclostationarity) → databases (Signal Identification Wiki) → tools (inspectrum, URH, rtl_433); worked IDs: HD Radio/IBOC sidebands, LTE/NR carriers, DVB-T, POCSAG, OTH radar and HF MFSK modems; line coding (NRZ/Manchester/PWM).",
  "reinforces D1 #16"),
 ("mesh", "Meshtastic / LoRa-mesh network operation", 2, r"Meshtastic roles|mesh routing|MQTT|MeshCore|preset|capacity|asymmetric|node range-troubleshooting|high-power mesh",
  "15/lorawan-vs-raw-lora (expand) or NEW 15/lora-mesh-networks",
  "Roles (client, router, client_mute) and why routers belong on high sites only; flooding and hop limit vs airtime; preset choice as sensitivity vs capacity (airtime per packet, collisions vs node count); why MQTT-bridged nodes show impossible ranges; loud 1 W nodes and asymmetric links; a node range-troubleshooting checklist (band/region, antenna on the right connector, SWR, placement, TX power).",
  "NEW"),
 ("loraant", "Choosing and judging LoRa/ISM antennas (stock, commercial, placement)", 3, r"stock|commercial LoRa antennas|elevation pattern|down-tilt|urban|window placement|site height|mistuned",
  "08/antenna-fundamentals + 08/antenna-measurement (new section) or 15/ground-station-design",
  "Why cheap stock/stubby antennas are often mistuned (measure with a NanoVNA); what \"3/5/8 dBi\" means for elevation coverage; choosing antennas for rooftop, hilltop, urban and indoor nodes; A/B testing method with RSSI statistics; red flags in listings (length vs band, missing ground plane).",
  "NEW (extends 08/antenna-fundamentals forum note)"),
 ("sdrspur", "SDR/analyzer spurious responses, artefacts and gain staging", 3, r"harmonic mixing|overload|spurious|LO-harmonic|images/spurs|gain staging|broadband LNA overload|spur checks|LO feedthrough",
  "17/sdr-as-test-equipment + 14/sdr-hardware-survey (add)",
  "Why stations appear at wrong frequencies (tuner LO-harmonic mixing, images, IMD from overload, ADC aliasing in direct-sampling mode); how to set RF/IF gain (raise until the noise floor lifts a few dB, back off when spurs appear; AGC off); when an LNA or FM-band notch helps vs hurts.",
  "reinforces D1 #12"),
 ("otherant", "Antenna types not yet in the KB (RFID/NFC, slot, lens, random wire, sector, collinear, harmonic)", 2, r"other-antenna-types|irises|tuning stubs|RFID|NFC|slot|lens|random-wire|sector|collinear phasing|harmonic \(3|V/inverted-V|off-band|antennas vs frequency|RF-to-optics|optics",
  "NEW 08/other-antenna-types (+ sections in 08/dipoles-and-monopoles)",
  "UHF RFID tag antennas (T-match dipoles) and HF/NFC coils with matching; slot/Babinet and slots in metal enclosures; slotted-waveguide arrays; lens antennas (3-D printed); random-wire/end-fed with unun; sector/panel antennas; collinear phasing coils; harmonic operation (3λ/2) and off-band reception; how antenna concepts continue to optical frequencies.",
  "reinforces D1 #8"),
 ("layout", "RF PCB layout rules, vias/fencing, launches and review", 3, r"rf-layout-rules|rf-pcb-review-checklist|vias-stitching-fencing|connectors-and-launches|floating|exposed ground|tuning pads|power trace|chassis|loop area",
  "13/rf-layout-rules, 13/vias-stitching-fencing, 13/connectors-and-launches, 13/rf-pcb-review-checklist (planned)",
  "Layout checklist for first RF boards (keep-outs, ground pours with stitching, no floating copper, via fences — not around radiators, U.FL/SMA launches, routing power under RF on inner layers, why RF areas look empty), >10 GHz specifics, and a reviewer's checklist.",
  "reinforces D1 #1, #3, #9"),
 ("shield", "Shielding: Faraday cages, fabrics, shield cans, room shielding", 2, r"shielding-and-isolation|Faraday|fabric|shield can|shield-can|shield cans",
  "13/shielding-and-isolation (planned)",
  "Shielding effectiveness (absorption + reflection + apertures), seams/doors/gaskets, why meshes and fabrics fail at high frequency, shield-can hole patterns, how to test a DIY cage with a phone/SDR, room shielding at Ku band.",
  "reinforces D1 #10"),
 ("emc", "RF immunity and interference hunting (audio pickup, lights blinking, noisy HF)", 2, r"emc-emi|immunity|rectification|\bRFI\b|interference to|CE certification|\bTEM\b|noise source|hunt RFI|picks up RF|GSM phones buzz",
  "13/emc-emi-fundamentals (planned) + 07/thermal-noise (man-made noise) + 19/certification",
  "Audio rectification (GSM 217 Hz buzz, FM in amplifiers), fixes (RC at inputs, ferrites, shielded/twisted leads); RF upsetting LED drivers/dimmers; hunting HF noise sources (inverters, LED supplies) with a portable receiver; DIY TEM/GTEM pre-compliance.",
  "reinforces D1 #7, #29"),
 ("simple", "Simple discrete radios (crystal/foxhole, AM, FM transmitter, superregen)", 2, r"crystal/foxhole|foxhole|crystal radio|AM-radio|one-transistor FM|FM transmitter|slope detection|SAW-resonator|discrete AM|simple discrete|Donald|dental",
  "06/receiver-architectures (add) + NEW 20/first-rf-projects",
  "How a crystal/foxhole radio works and fails (antenna/ground, detector bias, earphone impedance); why simple AM receivers pick up FM (slope detection); one-transistor FM transmitter analysis and legality; SAW-resonator OOK transmitters.",
  "reinforces D1 #11"),
 ("sat", "SDR reception recipes: weather satellites, ADS-B, airband, ISS, dishes/LNBs", 2, r"satellite|\bLNB\b|HRPT|LRPT|Gpredict|\bISS\b|TV dish|satellite-TV|\bAPT\b|NOAA|QFH|ADS-B|airband|\bATC\b|GOES|dish",
  "NEW 20/satellite-reception-recipe (+ 06/receiver-architectures LNB section)",
  "NOAA/Meteor/MetOp LRPT/HRPT chains (QFH/helix/dish, LNA+SAW, Doppler correction, decoders); ISS/amateur satellites; tracking software; Ku-band LNB internals (DRO/PLL LO, HEMT LNA) and re-using TV dishes.",
  "NEW (+ D1 tail LNB item)"),
 ("safety", "Station safety: lightning, grounding, BeO", 2, r"lightning|BeO|beryllium|grounding absent",
  "19/lab-safety-esd-high-power (add)",
  "Lightning protection and station grounding for masts/rooftop nodes (arrestors, single-point ground, bonding), DC-grounded antennas, hazards of BeO ceramics in magnetrons, power transistors and attenuators.",
  "reinforces D1 #15"),
 ("cell", "Cellular, Wi-Fi and consumer-system specifics (5G NR, LTE, Wi-Fi spectra, mm-wave)", 1, r"\b5G\b|\bLTE\b|Wi-Fi signal|mm-wave Wi-Fi|cellular-specific|SINR|Bluetooth car|phone detectors|remote starter|rolling-code|relay attack|NR numerology",
  "10/ofdm + 10/modulation-choice-guide (add worked system examples)",
  "5G NR numerology and CP-OFDM/DFT-s-OFDM in one table; why LTE/Wi-Fi spectra look the way they do on an analyzer (resource-block loading, DC null, averaging); why mm-wave Wi-Fi never took off; external antennas for 4G/5G routers (MIMO, cross-pol, SINR vs RSRP); key-fob rolling codes and relay attacks (one paragraph).",
  "NEW"),
 ("df", "Direction finding in practice (fox hunting, jammers, rocket beepers)", 2, r"fox-hunting|direction-finding|\bjammer\b|beeper",
  "12/adaptive-beamforming-doa (add a practical section) or NEW 17/radio-direction-finding",
  "Handheld DF: Yagi + body-shield null, offset attenuator/active attenuator near the source, time-difference and pseudo-Doppler DF, KrakenSDR in practice; finding a jammer or a landed rocket's beacon; legality of jammers.",
  "reinforces D1 #2"),
 ("track", "Rocket trackers, recovery aids and hobby telemetry protocols", 2, r"tracker|AirTag|Com-Spec|telemetry/tracker|recovery",
  "15/rocket-telemetry-radio-design (add)",
  "Landscape of commercial trackers/telemetry (Featherweight, Eggtimer, Big Red Bee, Altus Metrum, RDF beepers, BLE tags) with band, power, protocol and typical range; which can be received with an SDR; why BLE/UWB tags fail for field recovery.",
  "NEW"),
 ("filters", "Duplexers, cavity filters and front-end filtering against strong neighbours", 2, r"duplexer|cavity filter|canisters|tubular|US 902–928|filter helps|combline|filters sold|TX noise",
  "06/rf-filters-lc-saw-baw-cavity-microstrip (add) + 07/dynamic-range-sfdr-blocking",
  "Repeater duplexers (band-pass/band-reject cavities), tubular/combline filters, when a LoRa/Meshtastic node needs a cavity/SAW filter (US LTE B5/B26, 929 MHz paging; Singapore 900 MHz GSM/LTE), insertion-loss cost.",
  "reinforces D1 #23"),
 ("hfant", "HF antenna practice (EFHW/unun construction, V/inverted-V, compact HF, HT whips)", 1, r"EFHW|unun|ground plane size covered|HT whip|improvised|stealth|attic|compact HF|V-dipole|combining/switching",
  "08/dipoles-and-monopoles + 08/antenna-matching-and-baluns (add)",
  "EFHW 49:1/64:1 transformer design (core mix, turns, compensation capacitor, heating), inverted-V/V patterns, stealth/attic HF options, HT whip vs external antenna, improvised ground planes and mag mounts.",
  "reinforces D1 #39, #40"),
 ("case", "Worked system case studies (Starlink, Voyager/DSN)", 1, r"Starlink|\bDSN\b|Voyager|case study",
  "12/beamforming-architectures, 09/link-budget-methodology (add worked examples)",
  "Starlink user terminal as a phased-array case study (dual-pol stacked patches, hybrid beamforming ICs, scan range); Voyager/DSN link budget with 70 m dish, cryogenic LNA, 160 bit/s and concatenated coding.",
  "NEW"),
 ("radar", "Radar practice gaps (displays/terms, radar detectors/RWR, weather radar, FMCW vs pulsed choice)", 1, r"A-scope|PPI|display|radar detectors|radar warning|weather-radar|pulse-pair|pulsed-vs-FMCW|look-down|image frequency|GPR|magnetron/duplexer",
  "11/pulsed-radar-and-pulse-compression, 11/diy-radar-hardware, 11/clutter-and-mti (add); GLOSSARY",
  "Radar display formats and vocabulary (A-scope, PPI, B-scope, video, fast/slow time); how radar detectors and RWRs work; weather-radar velocity (pulse-pair) and dual-pol; when to choose pulsed vs FMCW; real vs complex IF in FMCW.",
  "reinforces D1 #32, #37"),
 ("sim", "Simulation practicalities (openEMS meshing/field dumps, solver artefacts, commercial-tool learning)", 1, r"openems-workflow|simulation-validation|HFSS|field dump|mesh",
  "16/openems-workflow, 16/simulation-validation (add)",
  "Field dump boxes and ParaView animation; importing STL/curved geometry and graded meshes; diagnosing spikes in simulated S11 (box resonances, port setup); where to learn HFSS/CST/ADS.",
  "extends D1 #31"),
 ("wpt", "Wireless power transfer and RF harvesting", 2, r"wireless-power",
  "NEW 09/wireless-power-and-energy-harvesting", "Near-field vs far-field power transfer limits, rectenna efficiency vs input power, why 'charging across the room' is limited by exposure rules and aperture.",
  "reinforces D1 #38"),
 ("analogdet", "Analog detector/discriminator circuits (FM, AM) explained", 1, r"discriminator|FM detector|envelope detection|analog video",
  "10/analog-modulation-am-fm-pm-ssb (add)", "Circuit-level explanation of slope, Foster–Seeley, ratio, quadrature and PLL FM detectors and diode envelope detectors, with component roles.",
  "NEW"),
 ("gnss", "GNSS receiver operation and front-end design", 2, r"^21|GNSS|GPS|gps-sdr-sim|CRPA",
  "NEW 21-gnss (domain folder exists, empty) + 20/gnss-front-end-design (planned)",
  "Receiver anatomy (module parts: SAW, LNA, TCXO), front-end schematic review, anti-jam (CRPA nulling), GNSS signal structure and simulation (never radiate).",
  "reinforces D1 #4"),
 ("parts", "Parts odds and ends (magnetic cores, SMP/test connectors, clone synthesizer boards, crystal packages)", 1, r"SMP|test connectors|LMX2595|pinout|air variables|YIG|susceptor|probing|AL/µ|iron powder",
  "18/connectors-and-cables-parts, 18/mixers-plls-vcos-parts, 04/crystals-and-resonators (add)", "SMP/SMPM and RF switch connectors; LMX2595 clone boards; crystal package pinouts; niche items.",
  "partly reinforces D1 #20, #21"),
 ("bulk", "Bulk data (images, voice) over sub-GHz links: LoRa vs FLRC vs HaLow vs FSK", 3, r"image transfer|kB image|images in the field|FLRC|HaLow|voice audio|Codec2|carry video|15 kB",
  "10/modulation-choice-guide + 15/other-ism-radios-fsk-2g4 (add a throughput section)",
  "Throughput vs range for sending a 10–600 kB image: LoRa SF/BW air time, GFSK/FLRC (SX1280, LR2021), 802.11ah HaLow, fragmentation + FEC + ARQ, duty-cycle limits; codecs for voice (Codec2) and why video needs Mb/s. Directly relevant to rocket camera/thumbnail downlinks.",
  "NEW"),
 ("chipint", "Chip-level radio integration (reference matching networks, bare-chip boards)", 3, r"reference-design|vendor class-E|bare-chip|Si446x",
  "NEW 20/lora-rocket-telemetry-link hardware section + 15/semtech-chip-family + 18/rf-transceiver-ics",
  "Walk-through of a vendor reference design (SX1262/SX1276/Si4463): PA match and harmonic filter, RF switch control (DIO2), TCXO supply, layout; why a custom board transmits 50 dB low (switch polarity, wrong match, PA_BOOST vs RFO), and how to bring it up.",
  "reinforces D1 #18"),
 ("bband", "Broadband splitters, multicouplers and broadband PAs", 1, r"ferrite-transformer|multicoupler|20:1|lumped couplers|broadband PAs|cost drivers|amplitude-and-phase weight",
  "06/couplers-dividers-combiners, 06/power-amplifiers (add)",
  "Transformer (0°/180°) hybrid splitters as used in Mini-Circuits parts; receiver multicouplers (LNA then split); multi-octave splitters; distributed/feedback/transformer-coupled broadband PAs and why they cost more.",
  "NEW"),
 ("ampfail", "Amplifier bring-up and failure modes", 2, r"why amps die|generic bring-up|bring-up covered|why cascaded high-gain|0 Ω/series jumper",
  "17/rf-bring-up-debug-playbook, 06/rf-switches-attenuators-limiters (add)",
  "Checklist for 'my amplifier does not amplify / died': bias, oscillation, ESD, overdrive, missing DC blocks, hot switching, mismatch; how to test safely with attenuators; why high-gain blocks are cascaded.",
  "reinforces D1 #35"),
 ("concept", "Beginner conceptual explainers (superposition, balanced vs differential, why not just add a wire)", 2, r"superposition|balanced \(impedance\)|adding a wire|isotropic single-polarisation|history not|element spacing vs",
  "07/dynamic-range-sfdr-blocking, 06/baluns-and-rf-transformers, 08/antenna-fundamentals (add plain-language boxes)",
  "Why billions of signals coexist (linear superposition + selective filtering); differential vs balanced; why soldering a wire to a PCB antenna detunes it; why no single-polarisation antenna is isotropic; short history notes (Smith chart).",
  "reinforces D1 #29"),
 ("legal", "Legality of consumer-band and homebrew transmitters (FRS/PMR, TV/FM, jammers)", 1, r"FRS|PMR|unlicensed TV|legality",
  "19/spectrum-allocation-ism-bands (add)", "Which services require type-approved radios (FRS/PMR446, CB), why a ham HT may not transmit there, home FM/TV transmitter rules, jammer prohibition.",
  "reinforces D1 #5"),
 ("sdrhw", "SDR hardware practicalities (hosts, clones, dongle heat/ppm drift, sample-rate limits)", 1, r"SBC-specific|clone B210",
  "14/sdr-hardware-survey (add)", "Host CPU/USB limits for Raspberry Pi-class stations; quality of B210/Pluto clones.", "reinforces D1 #12"),
]
PRIO = ["learn","projects","bulk","chipint","track","mesh","loraant","sigid","antid","sdrspur","sdrhw","case","df","sat","gnss","wpt","safety","legal","filters","df","shield","emc","layout","otherant","simple","analogdet","bband","ampfail","concept","radar","sim","case","hfant","parts","cell"]
C.sort(key=lambda c: PRIO.index(c[0]) if c[0] in PRIO else 99)
comp = [(k, t, r, re.compile(p, re.I), tg, nd, d1) for k, t, r, p, tg, nd, d1 in C]
assign = collections.defaultdict(list); unmatched = []
OVR = {"1ileuy7": "antid", "ufknk8": "sdrhw", "lumlx5": "sdrhw", "mm7a0k": "sdrhw", "rxqlzz": "sdrspur", "olhemk": "sdrspur", "10da8zd": "sdrspur", "1l8d5yg": "bband", "gfyuw9": "emc", "ovjt4m": "emc", "fzq9cc": "otherant", "hf2k4d": "otherant", "1nhmku3": "mesh", "knixio": "parts", "1mm3bog": "legal", "141441x": "ampfail", "a91891": "df", "17gvnfp": "df", "1ld0gbb": "track", "17bxe34": "bulk", "r5ukxg": "parts", "1o783j3": "layout"}
ckey = {c[0]: c for c in comp}
for r in rows:
    if r["st"] not in ("P", "M"):
        continue
    blob = " ".join([r["dom"], r["q"], r["page"], r["note"]])
    if r["id"] in OVR:
        assign[OVR[r["id"]]].append(r); continue
    for k, t, rel, rx, tg, nd, d1 in comp:
        if rx.search(blob):
            assign[k].append(r); break
    else:
        unmatched.append(r)
res = []
for k, t, rel, rx, tg, nd, d1 in comp:
    L = assign[k]
    if not L:
        continue
    n = len(L); nm = sum(1 for r in L if r["st"] == "M")
    ssum = sum(r["score"] for r in L if isinstance(r["score"], int))
    csum = sum(r["com"] for r in L if isinstance(r["com"], int))
    subs = collections.Counter(r["sub"] for r in L)
    score = rel * (math.log10(ssum + 1) + math.log10(csum + 1)) * (1 + 0.15 * n) * (1 + 0.3 * nm / n)
    res.append((score, k, t, n, nm, ssum, csum, subs, tg, nd, d1, L))
res.sort(key=lambda x: -x[0])
mode = os.environ.get("MODE", "summary")
if mode == "summary":
    for s, k, t, n, nm, ssum, csum, subs, tg, nd, d1, L in res:
        print(f"{s:7.1f} {k:10s} n={n:3d} miss={nm:2d} score={ssum:5d} com={csum:5d} {dict(subs.most_common(3))}")
    print("unmatched", len(unmatched))
    if os.environ.get("SHOW"):
        for k in assign:
            if k == os.environ["SHOW"]:
                for r in assign[k]: print("   ", k, r["id"], r["st"], r["q"][:80])
    for r in unmatched:
        print("  ", r["id"], r["st"], r["dom"], r["q"][:70], "|", r["page"][:40], "|", r["note"][:50])
else:
    # markdown for §2; row refs are ids
    idx = {}
    out = ["| Rank | Topic cluster | n (missing) | Σscore / Σcomments | Subreddits | Example posts | Target | What the answer needs | vs D1 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for i, (s, k, t, n, nm, ssum, csum, subs, tg, nd, d1, L) in enumerate(res, 1):
        ex = sorted(L, key=lambda r: -(r["score"] if isinstance(r["score"], int) else 0))[:3]
        exs = ", ".join(f"[{r['id']}](https://www.reddit.com/r/{r['sub']}/comments/{r['id']}/)" for r in ex)
        sb = ", ".join(f"{a} {b}" for a, b in subs.most_common(3))
        out.append(f"| {i} | {t} | {n} ({nm}) | {ssum} / {csum} | {sb} | {exs} | {tg} | {nd} | {d1} |")
    print("\n".join(out))
    print("\nUNMATCHED:", len(unmatched))
