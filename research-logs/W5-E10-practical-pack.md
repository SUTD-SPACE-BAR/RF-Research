# Research log W5-E10: practical pack (mesh capacity, radar applications, RFI hunting/immunity, ATUs, coax/connector practice, regulatory FAQ)
Status: complete
Owner scope: NEW files only —
kb/15-lora-ism-radios/lora-mesh-capacity-and-congestion.md,
kb/11-radar/radar-applications-gpr-through-wall-sensing.md,
kb/17-test-measurement/interference-hunting-and-rf-immunity.md,
kb/03-transmission-lines-matching/antenna-tuners-and-atus.md,
kb/18-components-parts/coax-and-connector-practicalities.md,
kb/19-regulations-safety/regulatory-faq-misc.md;
plus surgical one-line cross-links from existing pages, _index/_sources of 03/11/15/17/18/19,
tools/taxonomy.md lines for 03/11/15/17/18/19 only, tools/verify/e10_*.py scripts.

## Plan
- [x] Step 0: read CONVENTIONS, INDEX, D3 §2/§3 + relevant §5 rows, D2 §2/§3 + relevant §5 rows (DONE reading), canonical-values page (00 — not present yet in folder listing on 2026-10-02; re-check), load WebSearch/WebFetch
- [x] 15/lora-mesh-capacity-and-congestion (written 2026-10-03) — airtime per packet (Semtech formula), channel utilisation, pure/slotted ALOHA derivation (link 10 multiple-access page by W5-E5), flooding overhead vs hop count, why more hops/power hurts, Meshtastic presets + airtime, duty cycle, launch-day capacity estimate (N rockets + ground stations); script tools/verify/e10_mesh_capacity.py
- [x] 11/radar-applications-gpr-through-wall-sensing (written 2026-10-03) — GPR (soil attenuation, resolution), through-wall (Adib & Katabi), Wi-Fi CSI sensing, harmonic radar/NLJD/RECCO, RCWL-0516 (3.2 GHz self-oscillating Doppler), automotive/short-range, vital-sign radar; possible vs hype; script e10_radar_apps.py
- [x] 17/interference-hunting-and-rf-immunity (written 2026-10-03; 238 lines — pad to ≥250 with substance on resume) — SDR/H-loop/attenuator/DF/body-fade hunting; RCD/GFCI trips, Ethernet CM, audio rectification (GSM 217 Hz), motors/SMPS, ferrites, why throughput tests don't verify; rocket av-bay TX→sensors/pyro (link 13 EMC, 19 HERO); script e10_rfi.py
- [x] 03/antenna-tuners-and-atus (written 2026-10-12) — what a tuner does/doesn't do, L/T/Pi topologies and losses, auto-tuner algorithms, remote tuners, "tuner fixes antenna" myth with numeric line-loss examples; script e10_tuner_loss.py
- [x] 18/coax-and-connector-practicalities (written 2026-10-12) — torque, mating cycles, cleaning, adapter loss, SMA vs RP-SMA, U.FL fragility, weatherproofing, crimp vs solder, bend radius, phase-stable, NanoVNA cable test, fakes, 75 Ω-on-50 Ω number; script e10_coax.py
- [x] 19/regulatory-faq-misc (written 2026-10-12) — NextNav 902–928 MHz status (2026), Baofeng/uncertified HTs (US/SG), hobby radar licensing, other D2/D3 regulatory Qs
- [x] taxonomy lines (03/11/15/17/18/19), _index/_sources updates, one-line cross-links, `python3 tools/build_index.py --check`

## Log (append-only)
- 2026-10-02 — Read CONVENTIONS.md, HANDOFF.md, INDEX.md rows for 03/10/11/13/15/17/18/19, D3 §1–§3 and §5 rows (mesh 296/441–449/457/458/535/654; radar 74/76/79/461/477/498/499/540/581/699; immunity 388/394/396/436/439/473/484/518–520; RFI hunting 43/178/258/359/383/619/625; tuners 4/219/224/345/346/464/492/517/634/673/674; coax 68/69/72/148/150/152/184/187/315; regulatory 77/452/455/462/529/627), D2 §2/§3 and filtered §5 rows (mesh 220/226/228/234/240/243/245/246/254; RFI 18/30/39/77/125/462; regulatory 45/230/481; radar 300/305/307). No pages written yet.
- 2026-10-02 — PAUSE received from coordinator before any research/page writing. Stopped. No background jobs started.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|

## Contradictions / discrepancies found

## Knowledge gaps noticed (for later gap-filling)

## Cross-domain notes (things other domains should cover/link)

## Resume instructions (what the next agent should do if this one is interrupted)
1. Step 0 reading of D2/D3 is done (see Log for row numbers); re-read CONVENTIONS.md §3–§4 quickly and check whether `kb/00-math-foundations/canonical-values-and-conventions.md` now exists (W5-E9 is writing it) and whether W5-E5's multiple-access page exists in kb/10 (`ls kb/10-comms-modulation/`) to get its slug for links.
2. Load WebSearch/WebFetch via ToolSearch `select:WebSearch,WebFetch`.
3. Read the existing pages to link/avoid duplicating: 15/lora-phy-css-math (airtime formula), 15/lorawan-vs-raw-lora, 15/ism-band-plans-duty-cycle, 15/lora-impairments-doppler-drift-timing; 11/diy-radar-hardware, 11/cw-and-doppler-radar; 13/emc-emi-fundamentals, 19/lab-safety-esd-high-power; 03/coax-and-cables, 03/impedance-matching-lumped-and-distributed, 08/wire-antennas-hf-random-wire-fan-dipole; 18/connectors-and-cables-parts, 13/connectors-and-launches; 19/spectrum-allocation-ism-bands, 19/amateur-radio-licensing, 19/singapore-imda-rules.
4. Write the six pages in Plan order (mesh first), each with a tools/verify/e10_*.py check; update this log after each page.
5. Finally add taxonomy lines, _index/_sources rows, cross-links; run `python3 tools/build_index.py --check`.
- 2026-10-03 — RESUMED. canonical-values page not yet on disk (W5-E9 Task 2 pending) → use CONVENTIONS §4 values. W5-E5's planned slug: 10/multiple-access-and-duplexing (not yet on disk).
- 2026-10-03 — Mesh research: Meshtastic docs (presets table SF/BW/CR/link budget; hop limit default 3 max 7; default LONG_FAST; EU 10 % hourly duty; SG_923 917–925 MHz 20 dBm 100 %); mesh-algo page (managed flooding, SNR-weighted contention, ROUTER always rebroadcasts, next-hop DMs since 2.6, >40-node interval scaling); firmware source airtime.h (max CU 40 %, polite 25 %, polite duty 50 % of region; CU window 6×10 s) and RadioInterface.h/.cpp (preamble 16 sym, header 16 B, CWmin 3/CWmax 8, slot = 2.5 Ts + 7.6 ms); device roles/position 900 s/telemetry 1800 s/nodeinfo 10800 s defaults; MeshCore FAQ (flood-then-direct, clients never repeat, 64-hop limit, US 910.525 MHz SF7/62.5 kHz); Bor et al. 2016 accepted PDF (pure-ALOHA DER = exp(−2NTλ) lower bound; capture raises DER 0.51→0.64 at N=200; text says 64 nodes at DER>0.9 for SN3 while Fig. 4 caption + abstract say 120 → contradiction recorded); Georgiou & Raza arXiv:1610.04793 abstract.
- 2026-10-03 — Wrote tools/verify/e10_mesh_capacity.py (ToA per preset, ALOHA MC, CSMA, managed-flood MC, central-node load vs range/hop, p^h, launch-day) → ALL PASS (27 checks); output in e10_mesh_capacity_output.txt.
- 2026-10-03 — WROTE kb/15-lora-ism-radios/lora-mesh-capacity-and-congestion.md. Next: radar applications page.
- 2026-10-03 — Radar research: Davis & Annan 1989 material table via UBC GPG (er, sigma, v); GPG fundamentals (low-loss plateau); Wi-Vi PDF (Adib & Katabi SIGCOMM 2013: 2.4 GHz 20 MHz, 2 TX + 1 RX, MIMO nulling 42 dB mean, walls 8" concrete / 6" hollow / 1.75" wood; counts 0–3 people 100/100/85/90 %; gestures ≤5 m 100 %, 75 % at 8 m, none >9 m; one-way 2.4 GHz losses glass 3, wood door 6, hollow wall 9, 18" concrete 18, reinforced 40 dB; UWB state-of-art needs 2 GHz BW and 2.4 m array); WiTrack PDF (NSDI 2014: FMCW 5.56–7.25 GHz [paper also says 5.46–7.25], 0.75 mW, through-wall median error 13.1/10.25/21 cm); RCWL-0516 (jdesbonnet repo: MMBR941M Colpitts self-oscillating mixer, 3.181 GHz measured, ~7 m, RCWL-9196 ≈ BISS0001); harmonic radar (Maggiora et al. Sci Rep 2019 PMC6700122: 9.4 GHz, 1 kW peak, 45 µs, 7 m res., 500 m tracking, 15 mg J-wire + Schottky tag; Rasilainen et al. IJAP 2015 review: RECCO 0.917 GHz; RECCO R9 quick guide ranges air 120 m / dry snow 20 / wet 10 / water 0.2 m); NLJD 2nd vs 3rd harmonic discrimination (US6057765A patent; Mazzaro et al. IEEE TAES 50(1) 2014); IEEE 802.11bf-2025 published 2025-09-26; HLK-LD2410 24–24.25 GHz FMCW, 0.75 m res., 0.75–6 m; ADE 651 fraud conviction (ABC News 2013-04-24).
- 2026-10-03 — Wrote tools/verify/e10_radar_apps.py → ALL PASS (output e10_radar_apps_output.txt).
- 2026-10-03 — WROTE kb/11-radar/radar-applications-gpr-through-wall-sensing.md (265 lines). Next: 17 interference hunting.
- 2026-10-03 — RFI research: HomingIn (K0OV) equipment page via curl (body fade = null with source behind you; offset attenuator ~4 MHz offset, 20–100 dB, immune to case leakage; resistive attenuators bypassed through HT case; 3rd-harmonic trick ≈ 40–60 dB); BEAMA RCD Handbook (unwanted tripping: transients + capacitance to earth, RFI suppression capacitors; IEC 61009 ring-wave 0.5 µs/100 kHz 200 A no-trip; worked 1 kV/50 µs → 1.6 nF for 50 mA); BS 7671 531.3.2 30 % rule (9 mA for 30 mA RCD) and IEC 61008 50–100 % IΔn window (via IET/BEAMA search); ARRL GFCI/AFCI page (RF upsets imbalance/arc detection; replace with less susceptible unit preferred over filtering); Hackaday ferrites-vs-Ethernet 2024 (NanoVNA: 2 ferrites × 2 turns ≈ 17 dB; iperf showed no change — critics cite K9YC); K9YC "A Ham's Guide to RFI…" Rev 7 2019 (Ethernet trash is CM from poor line drivers; 9 turns on 2.4" #31/#43 ≥ 2 kΩ at 10–30 MHz; threshold effect 300 Ω example; square-law detection doubles dB; ≥500–1000 Ω to make a dent at VHF; kill own router to identify birdies; birdie clusters near 10.107/10.122 MHz); Pololu motor-noise note (0.1 µF across + each terminal to case, twist leads); Aberhosan SHINE story (ISPreview/Irish Times 2020).
- 2026-10-03 — Wrote tools/verify/e10_rfi.py → ALL PASS.
- 2026-10-03 — WROTE kb/17-test-measurement/interference-hunting-and-rf-immunity.md (e10_rfi.py ALL PASS). PAUSE received immediately after; stopped. No background jobs.

### Resume instructions (2026-10-03 second pause — supersede the list below)
Done: 15/lora-mesh-capacity-and-congestion (252 lines, e10_mesh_capacity.py ALL PASS), 11/radar-applications-gpr-through-wall-sensing (265 lines, e10_radar_apps.py ALL PASS), 17/interference-hunting-and-rf-immunity (e10_rfi.py ALL PASS; check `wc -l` ≥ 250, pad with substance if short).
Next, in order:
1. 03/antenna-tuners-and-atus — write tools/verify/e10_tuner_loss.py first (matched-line loss + extra loss at SWR via the standard formula; RG-58/RG-213/ladder line at 7/14/28 MHz with SWR 3/10/20 at the antenna; L/T/Pi loss with inductor Q 100–300 over impedance extremes; tuner-at-rig vs at-antenna comparison). Cover auto-tuner algorithms (SWR bridge, relay L/C banks, binary search/memories, N7DDC clones), remote tuners powered over coax (bias-T), internal-tuner ≈3:1 range, RX-only use, "tuners fix antennas" myth. Sources: ARRL Antenna Book; existing 03/reflections and 08/wire-antennas-hf pages (link, don't duplicate).
2. 18/coax-and-connector-practicalities — e10_coax.py (75 Ω on 50 Ω mismatch loss 0.18 dB; adapter loss; bend radius; phase matching ΔL = Δφ·λ·VF/360; NanoVNA cable loss/VF/TDR). Torque (SMA 0.56–1.1 N·m, typically 0.9 N·m / 8 in-lb), mating cycles (SMA ~500, U.FL ~30), RP-SMA, U.FL retention, weatherproofing, crimp vs solder, fakes. Sources: Amphenol/Hirose U.FL datasheets; link 03/coax-and-cables, 18/connectors-and-cables-parts, 13/connectors-and-launches.
3. 19/regulatory-faq-misc — NextNav FCC docket WT 25-110 status as of 2026 (research), Baofeng/uncertified HTs (FCC Part 90/95 vs 97, 2018 FCC enforcement advisory; Singapore IMDA), hobby radar licensing (FCC 15.245/15.252/Part 97 pulse emissions; SG TS SRD), US §15.247 basis for 250 kHz non-hopping LoRa (open question), MQTT/jammers/home FM TV transmitters/CE self-declaration.
4. Taxonomy lines (03/11/15/17/18/19 only) add the six slugs; _index/_sources rows for the 6 domains; one-line cross-links (15/lorawan-vs-raw-lora → mesh page; 11/diy-radar-hardware → apps page; 13/emc-emi-fundamentals → 17 page; 08/wire-antennas-hf → tuner page; 03/coax-and-cables + 18/connectors → coax page; 19/spectrum-allocation → reg FAQ); run `python3 tools/build_index.py --check`; mark log complete; final report ≤250 words.
- 2026-10-12 — RESUMED (third time). Following second-pause resume list.
- 2026-10-12 — 17 page padded to 253 lines (noise-floor snippet, CM current probe).
- 2026-10-12 — Tuner research: OZ9F/N7DDC ATU-100 extended-board manual (7 L 0.05–4.5 µH uneven steps, max 8.53 µH; 7 C 10 pF–1 nF; C switchable before/after L; retune when SWR > 1.3 and changed; 100 W, 150 W measured max, ≥ 5 W to tune; tunes on any signal incl. speech); Icom IC-7300 internal ATU 16.7–150 Ω (SWR < 3:1) per Icom America/manual. Wrote tools/verify/e10_tuner_loss.py (mismatched-line loss formula vs exact; RG-58/LMR-400/ladder tables; SWR at rig; lossy L/T networks via ABCD; Q_n/Q_u rule; relay state count) → ALL PASS. Note: RG-58 HF loss is extrapolated from the 03 fit (k1√f+k2f) and is ≈ 20 % below commonly quoted Belden 8240 HF figures → loss numbers slightly optimistic (recorded as gap).
- 2026-10-12 — WROTE kb/03-transmission-lines-matching/antenna-tuners-and-atus.md. Next: 18 coax/connector page.
- 2026-10-12 — Coax research: Hirose U.FL datasheet (Digikey PDF): DC–6 GHz, VSWR 1.3 max ≤ 3 GHz / 1.4 (1.13 mm) 3–6 GHz, 30 cycles, vibration 10–100 Hz 59 m/s², shock 735 m/s² 11 ms, cable pull after mating 2/4/2 N (1.13 mm; 1/3/1 N for 0.81 mm), extraction jig U.FL-LP-N-2 pull vertically, "click" confirms mate, U.FL-to-SMA adapter has lower retention (measurement use only); Keysight connector-care help (low-pressure air, IPA 99.5 % on lint-free swab moistened not saturated, keep off the bead, clean threads, turn only the nut); Times WK-U / CommScope 221213 weatherproofing kits (butyl mastic + electrical tape multilayer); onallbands practitioner wrap guide. Wrote tools/verify/e10_coax.py → ALL PASS.
- 2026-10-12 — WROTE kb/18-components-parts/coax-and-connector-practicalities.md. Next: 19 regulatory FAQ.
- 2026-10-12 — Regulatory research: FCC 25-20 NOI (WT 25-110, adopted 27 Mar 2025, released 28 Mar, comments 28 Apr / replies 13 May 2025); rfidnews 2026-09-27 (dockets RM-11989, WT 24-240, WT 25-110; draft NPRM sent to OMB March 2026; SpecTech Alliance 17 Sep 2026; >2000 comments; "nothing decided"; plan 902–907 up / 918–928 down / 907–918 shared); Comms Daily 2026-06 (New Street: NPRM likely, "far from a done deal") and 2026-08-03 (D2D NPRM docket 26-169 may drop 900 MHz) — via search snippets only; no adopted NPRM found as of 2026-10-12. FCC DA 18-980 Enforcement Advisory 2018-03 (read PDF: radios must be authorised before import/ad/sale/use unless capable only of amateur frequencies; Amcrest/Baofengradio.US citation DA 18-801; 12.5 kHz narrowband 90.209). eCFR 97.305 (pulse authorised 33/13/5/1.2 cm and mm bands; not 70/23/3 cm; test emissions brief). eCFR 15.245 (FDS bands/field strengths) and 15.249. IMDA: 2005 IDA release allocating 446.0–446.1 MHz walkie-talkies; IRIS localised network licence 446.325–446.475 MHz ≤ 1 W ERP; WTO import-licensing summary: jammers prohibited in SG. Wrote tools/verify/e10_regulatory.py.
- 2026-10-12 — WROTE kb/19-regulations-safety/regulatory-faq-misc.md (e10_regulatory.py ALL PASS). Next: taxonomy, _index/_sources, cross-links, build_index --check.
- 2026-10-13 — Taxonomy: six slugs added (03, 11, 15, 17, 18, 19). _index rows and _sources sections added for the six domains. One-line cross-links added in 15/lorawan-vs-raw-lora, 11/diy-radar-hardware, 13/emc-emi-fundamentals, 08/wire-antennas-hf-random-wire-fan-dipole, 03/coax-and-cables, 18/connectors-and-cables-parts, 19/spectrum-allocation-ism-bands. `build_index.py --check`: 279 pages; 0 missing sections; 2 broken links, both in another agent's 03/microstrip-discontinuities.md (not mine). All six e10_*.py scripts ALL PASS. TASK COMPLETE.

## Contradictions / discrepancies (summary)
- Bor et al. 2016: the text gives 64 nodes for DER > 0.9 (SN3), while Fig. 4's caption and the abstract give 120 nodes. Neither is used as a design number.
- WiTrack paper: the sweep is stated as 5.56–7.25 GHz in one section and 5.46–7.25 GHz in another.
- Through-wall flash: this KB's estimate is 48–66 dB; Wi-Vi quotes about 36 dB. The assumptions differ.
- RG-58 HF loss: the 03 fit extrapolated to HF is about 20 % below the commonly quoted Belden HF figures, so the tuner-page losses are slightly optimistic.
- 18/connectors-and-cables-parts says plain U.FL retention is "not verified". The Hirose datasheet gives post-mating cable-pull limits of 2/4/2 N (1.13 mm). Now recorded in 18/coax-and-connector-practicalities; the 18 selection page could be updated by its owner.

## Knowledge gaps noticed
- US Part 15 basis for non-hopping 125/250 kHz LoRa at 30 dBm (Meshtastic US preset): unresolved.
- NextNav: whether an NPRM has been adopted rests on trade-press snippets; re-check FCC ECFS (WT 25-110).
- The current Singapore walkie-talkie rule (power/frequency) was not read from a current IMDA document.
- RCWL-0516 radiated power: no reliable source found.
- No measured av-bay field and sensor-upset data, and no measured launch-site ChUtil data.
- RG-6 is missing from the 03 coax fit table.

## Cross-domain notes
- 13/emc-emi-fundamentals and 19/lab-safety now link to 17/interference-hunting (av-bay immunity test procedure).
- 10/multiple-access-and-duplexing (W5-E5) is linked from the mesh page for the launch-day channel plan.
