# Research log W1-A3: 02-electromagnetics
Status: complete
Owner scope: kb/02-electromagnetics/ ; research-logs/W1-A3-electromagnetics.md ; tools/verify/em_*.py

## Plan
Order chosen so that later pages can link to earlier ones (constants → Maxwell → waves → ...).
- [x] electromagnetic-units-and-constants — done ([page](../kb/02-electromagnetics/electromagnetic-units-and-constants.md)) — ε0, μ0, c, η0 after 2019 SI; μ0/(4π×10⁻⁷) − 1 quantified; Gaussian vs SI; field-unit conversions
- [x] maxwells-equations — done — integral/differential forms, displacement current, constitutive relations, phasor form, continuity, KVL/KCL from Maxwell and when they fail
- [x] wave-equation-plane-waves-polarization — done — wave eq derivation, γ = α + jβ, η, lossy media (good dielectric / good conductor limits), polarization, axial ratio, IEEE vs optics handedness
- [x] poynting-vector-power-flow — done — instantaneous/average S, E = √(ηS), energy flow in circuits (coax, DC wire), V/m ↔ dBµV/m ↔ W/m², worked 2 W at 1 km
- [x] boundary-conditions-reflection-refraction — done — BCs, normal/oblique incidence, Fresnel TE/TM, Brewster, TIR, multilayer (transfer matrix), radome half-wave/thin-wall, ground/sea reflection
- [x] skin-effect-conductor-loss-roughness — done — δ derivation, table Cu/Al/Ni/Au/Ag 1 MHz–100 GHz (verified), Rs, AC resistance wire/trace, proximity, Hammerstad/Huray/Groisse, ENIG Ni, Litz
- [x] dielectrics-permittivity-loss-tangent — done — complex ε, tanδ, polarization mechanisms, Debye, Djordjevic–Sarkar, glass-weave anisotropy, moisture/temperature, materials table
- [x] magnetic-materials-permeability — done — complex μ, ferrites, Snoek's limit, HF roll-off, gyrotropic ferrites (Polder tensor)
- [x] quasi-static-vs-full-wave — done — electrical length, λ/10 vs λ/20, rise-time criteria, retardation
- [x] radiation-from-currents-hertzian-dipole — done — potentials, Lorenz gauge, retarded potentials, full dipole fields, R_rad = 80π²(l/λ)², Larmor, DM vs CM radiation, small loop dual
- [x] waveguides-and-cavity-resonators — done — rectangular/circular, TE/TM, cutoff, vp/vg, wave impedance, attenuation, cavity Q, SIW intro
- [x] near-field-far-field — done — λ/2π, Fresnel region, 2D²/λ, wave impedance vs distance for E/H sources
- [x] inductance-capacitance-from-fields — done — energy definitions, loop vs partial inductance, mutual, parallel plate / coax / two-wire / wire-over-ground, fringing
- [x] _index.md — done
- [x] _sources.md — done

Verification scripts planned (tools/verify/):
- em_constants.py — CODATA 2018/2022 μ0, ε0, η0, c; deviation from 4π×10⁻⁷
- em_skin_depth.py — skin depth / Rs table for Cu/Al/Ni/Au/Ag; roughness models
- em_plane_waves.py — γ, η for lossy media; polarization/axial ratio; Poynting numbers
- em_fresnel_radome.py — Fresnel coeffs, Brewster, transfer-matrix radome
- em_dielectrics.py — Debye, Djordjevic–Sarkar causal model
- em_hertzian_dipole.py — symbolic check of dipole fields & radiation resistance; wave impedance vs distance
- em_waveguides.py — cutoffs, attenuation, cavity Q
- em_inductance.py — L/C formulas cross-checked (coax, two-wire, wire over ground)
- (added) em_maxwell.py, em_poynting.py, em_magnetics.py, em_quasistatic.py, em_nearfield.py — all 13 scripts pass (2026-09-27)

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md. Created log. Starting with constants page (NIST CODATA).
- 2026-09-27 — NIST CODATA 2022 pages for mu0, eps0, Z0, alpha fetched (values recorded in em_constants.py). BIPM SI Brochure 9th ed. (2019, updated) PDF text: §2.3.1 ampere — mu0 now experimentally determined; eps0, Z0, Y0 share its rel. uncertainty; eps0*mu0=1/c^2 and Z0/mu0=c remain exact; at adoption mu0=4π×1e-7 with rel. unc. 2.3e-10.
- 2026-09-27 — Orfanidis EWA site (rutgers) returns 403/404; Feynman Lectures site 403; MIT OCW redirect loop. Will cite these from knowledge with chapter-level refs only, flagged. Haus & Melcher chapter-1 section list confirmed at web.mit.edu/6.013_book.
- 2026-09-27 — Djordjevic et al. 2001 (IEEE T-EMC 43(4) 662–667) PDF read: FR-4 measured 10 Hz–12 GHz; eps' decays ~0.14 per decade 10 kHz–10 GHz; eps'' ≈ 0.1, tanδ ≈ 0.02 nearly constant; wideband model eps = eps_inf + Δeps'/((m2-m1) ln10) * ln((ω2+jω)/(ω1+jω)) − jσ/(ωε0), fit eps_inf=4.27, σ=80 pS/m(?), ω1=1e4, ω2=1e12 s^-1, Δeps'/(m2−m1)=0.14; eps'' = (π/2)/ln10 × decay-per-decade ≈ 0.682×; single-Debye fit near 300 kHz: eps_inf=4.9, Δ=0.28, ω0=2e6. Measurement error ~0.2 in eps', 0.02 in eps''.
- 2026-09-27 — Huray et al. DesignCon 2010 PDF read: eq (9) Prough/Psmooth ≈ 1 + (3/2)Σ(N_i 4π a_i²/A_hex)/(1+δ/a_i+δ²/2a_i²); max = 1+(3/2)ΣN_i4πa_i²/A_hex; hex base 9.4 µm; fits 79 spheres (12 µm rms, high profile) and 50 spheres (4 µm rms low profile), a=0.5 µm, to 50 GHz; Hammerstad eq(1) K=1+(2/π)atan(1.4(Δ/δ)²) max 2 (Hammerstad & Bekkadal 1975; Morgan 1949 J.Appl.Phys 20:352).
- 2026-09-27 — Shlepnev (Simberian) 2019 'snowballs to cannonballs' app note + EPEPS 2017 'Unified approach' paper read: unified K = 1 + (RF−1)F(SR); Groiss F = exp(−(δ/(2Δ))^1.6), RF=2 gives Groiss exactly (Groiss et al., IEEE Trans. Magn. 32(3):894–897, 1996); Cannonball-Huray = Huray with RF fixed 8.33 (SR ratio 4.887), r = 0.06 Rz (Simonovich DesignCon 2015/2019). Polar AP8155: Hammerstad saturates ~>4 GHz, Groiss useful to ~7–10 GHz, Huray to 40–50 GHz; rule of thumb 0.5 µm spheres, 45–85 (60 nominal).

- 2026-09-27 — Rogers RO4003C/RO4350B datasheet values (via search snippets of datasheet mirrors incl. JLCPCB copy): RO4003C Dk process 3.38±0.05 @10 GHz, design 3.55, Df 0.0027@10 GHz / 0.0021@2.5 GHz; RO4350B process 3.48±0.05, design 3.66, Df 0.0037@10 GHz / 0.0031@2.5 GHz.
- 2026-09-27 — Coonrod (Rogers), PCD&F Mar 2018 'Impact of final plated finishes on insertion loss': ENIG vs bare Cu ≈ +0.38 dB/in (8-mil microstrip) and +0.21 dB/in (20-mil) at 25 GHz; GCPW worse (~1.2 vs 0.5 dB/in at 50 GHz); ImAg & OSP ≈ bare Cu to 40 GHz; ImSn worse; Ni ≈ ¼ σ_Cu. Milad (Uyemura) 2020: EN is the loss driver; thick Ni 3–6 µm; thin-Ni ENEPIG (0.1 µm) and Ni-free EPIG much lower loss. Plating-industry sources: EN 4–13% P, PCB ENIG usually mid-P 6–9%; high-P (>~10–11%) non-magnetic as plated.
- 2026-09-27 — 3D-print dielectrics: Castles et al. Sci. Rep. 2016 (PMC4778131): printed ABS ε'=2.57±0.02, tanδ=0.0047 @15 GHz, printed ≈ bulk within 1%. Kuzmanić et al. Prog. Addit. Manuf. 2023 (PMC9942642): εr 100% infill PLA≈2.81, ABS≈3.00, strong infill dependence (33% infill: 1.98/2.29), freq not stated. Işık et al. arXiv 2607.16937 (2026): 7 PLA colours + 2 SLA resins at 70–110 GHz, ε' 2.45–2.75, tanδ up to >0.02 (silver PLA, black resin). IEEE Xplore 7843900 (CoBCom 2016): printed PLA 0.5–20 GHz + 40/60 GHz, ε' ≈ 2.75 (E), anisotropy 2.74/2.83/2.96 at 60 GHz, tanδ 0.012–0.016.
- 2026-09-27 — ITU-R P.527-6 (09/2021) PDF read: pure/sea water double-Debye model eqs (5)–(27) (implemented in em_dielectrics.py), penetration depth eq (4). Kaatze 1989 J. Chem. Eng. Data 34:371: water τ(25 °C) ≈ 8.27 ps. ITU-R P.368-10 (2022): ground-wave curves sea water avg salinity σ=5 S/m εr=70; low salinity σ=1, εr=80.
- 2026-09-27 — Energy-flow sources: Boulé, Am. J. Phys. 92(1):14 (2024) (arXiv 2305.11827) DC power between two parallel wires; Davis & Kaplan, Am. J. Phys. 79:1155 (2011) (arXiv 1207.2173) Poynting flow in circular circuit. Forum sweep: Veritasium 2021 "Big misconception about electricity" debate; handedness IEEE-RCP = optics-LCP (Thorlabs tutorial 2017; MATLAB phased docs); skin-effect misconception "current flows only on the surface".
- 2026-09-27 — WROTE electromagnetic-units-and-constants.md (+ tools/verify/em_constants.py: mu0 from alpha; CODATA2018 +5.47e-10, CODATA2022 −1.38e-10 vs 4π e-7; dBuV/m conversions).
- 2026-09-27 — WROTE maxwells-equations.md (+ em_maxwell.py: sympy continuity & plane-wave checks, σ/ωε table, loop EMF).
- 2026-09-27 — WROTE wave-equation-plane-waves-polarization.md (+ em_plane_waves.py). em_plane_waves.py initially had the Stokes S3 sign flipped vs the time trace — caught by the assert; fixed (S3 = 2 Im(Ex Ey*) >0 ⇒ IEEE RH for e^{jωt}, +z). RHCP = (x̂ − jŷ)e^{−jkz}.
- 2026-09-27 — em_dielectrics.py written early (ITU-R P.527-6 water model; D-S FR-4). Found: fresh-water loss at 433 MHz is dominated by dipolar relaxation (ε''≈1.9) not conduction (0.42) → corrected example in wave page (≈10 dB/m, not 1.8). P.527 sea water @433 MHz gives σ_eff 4.83 S/m, ε' 71.6 — consistent with P.368 (70, 5 S/m).
- 2026-09-27 — WROTE poynting-vector-power-flow.md (+ em_poynting.py: coax ∫S = VI, DC wire inward flux = I²R, two-wire DC line power-within-radius, complex Poynting vs RLC, exposure numbers). Fixed own error: EIRP→dBµV/m constant is 44.77 (not 104.8).
- 2026-09-27 — WROTE boundary-conditions-reflection-refraction.md (+ em_fresnel_radome.py: Fresnel/Brewster/TIR, transfer matrix, half-wave 75.6 mm @915 MHz fibreglass, thin-wall |Γ|²<1% for t<λd/53, A-sandwich, CFRP −46…−160 dB, sea/ground R_H/R_V, pseudo-Brewster sea 3.9°). CFRP σ from search summaries (TLM arXiv 1502.01227, ResearchGate) — medium.
- 2026-09-27 — CRC 'Electrical resistivity of pure metals' PDF (mirror) read: 293 K ρ (1e-8 Ωm): Al 2.650, Cu 1.678, Au 2.214, Ni 6.93, Ag 1.587, Pd 10.54, Fe 9.61; Sn 11.5 (273 K).
- 2026-09-27 — WROTE skin-effect-conductor-loss-roughness.md (+ em_skin_depth.py: δ/Rs tables, Bessel wire, proximity, roughness model tables, layered Zs for ENIG/ENEPIG/ImAg/ImSn, microstrip loss split, Litz).
- 2026-09-27 — Fair-Rite 43 datasheet page: μi 800, B 3500 G @10 Oe, ρ 1e5 Ω·cm, Tc >130 °C. Palomar mix table: 31 (MnZn 1500), 73 (2500), 75 (5000), 43 (NiZn 800), 52 (250), 61 (125). Snoek limit form fr(μi−1) = |γ|Ms/3π (search; Nakamura JAP 88:348, 2000) — note Ms must be 4πMs (G) with γ in rad/s/Oe, or μ0Ms (T) with γ in rad/s/T.
- 2026-09-27 — WROTE dielectrics-permittivity-loss-tangent.md (+ em_dielectrics.py sections 6–7: Wiener anisotropy bounds ≤ ~11 %, moisture). Several material-table rows (PTFE, alumina, G10, Kapton, RT5880, TCDk) from knowledge, flagged M/L.
- 2026-09-27 — WROTE magnetic-materials-permeability.md (+ em_magnetics.py: Snoek table, bead Z from relaxation/Lorentz μ, Polder μ± identities, Kittel FMR, Faraday rotation, MnZn dimensional resonance).
- 2026-09-27 — WROTE quasi-static-vs-full-wave.md (+ em_quasistatic.py: stub error ≈ (βl)²/3 → 13 % at λ/10, 3.3 % at λ/20; π-section S11; R_rad vs size; electrical-length table; rise-time rules; τ_em² = τ_e τ_m). Fixed own unit bug in script (λ/10 printed ×10 too small).
- 2026-09-27 — Session interrupted by API limit after writing em_hertzian_dipole.py (not yet run). Resumed on coordinator instruction.
- 2026-09-27 — Ran em_hertzian_dipole.py (all pass: sympy fields from A, R_rad = 2πη/3 (l/λ)² = 789.02 vs 80π² 789.57, Larmor ≡ ½I²R, complex power 1 − j/(kr)³, Z_w vs kr, Paul DM/CM constants reproduced 1.3169e-14 / 1.2566e-6; CM 3.6 µA vs DM 34 mA at 100 MHz). WROTE radiation-from-currents-hertzian-dipole.md.
- 2026-09-27 — WROTE near-field-far-field.md (+ em_nearfield.py: region table, 2D²/λ phase π/8 and −0.056 dB on-axis gain error, Z_w convergence 10 % at ~0.5λ / 1 % at 1.6λ, Schelkunoff R for E/H sources, near-field error of far-field law).
- 2026-09-27 — WROTE waveguides-and-cavity-resonators.md (+ em_waveguides.py: WR cutoffs, dispersion with numeric vg, TE10 αc closed form = numeric (WR-90 0.108 dB/m @10 GHz), circular Bessel zeros, below-cutoff 27.3 dB/a & 32 dB/diameter, TE101 Qc closed form = numeric, PCB plane-pair 715 MHz Q≈31, SIW a_eff).
- 2026-09-27 — WROTE inductance-capacitance-from-fields.md (+ em_inductance.py: TEM L'C'=με; Rosa/Grover partials; loop=Σpartials→two-wire limit; rect loop partial-sum vs numeric Neumann (−1.4 %); via partial 0.69 nH vs Johnson&Graham '+1' form 1.30 nH; 2-D FD Laplace microstrip w/ Richardson extrapolation matches Hammerstad–Jensen Z0/ε_eff < 0.4 %; Maxwell coaxial-loop M vs Neumann). First FD attempt was 5 % off (edge-singularity convergence) → fixed by extrapolation.
- 2026-09-27 — WROTE _index.md (reading order, pages table, 27-question FAQ with anchors validated against headings) and _sources.md (27 textbooks, 10 standards/data, 20 papers, 11 app notes/trade, 4 forum/video; status read/abstract/knowledge). Link check: all ../NN/slug.md targets exist or are planned in INDEX.md. All 13 em_*.py scripts pass. Task complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | NIST CODATA 2022 (physics.nist.gov/cuu), Mohr et al. Rev. Mod. Phys. 97, 025002 (2025) | standard | constants | authoritative |
| S2 | BIPM SI Brochure 9th ed. (2019, updated) | standard | SI redefinition, mu0 status | authoritative |
| S3 | Djordjevic, Biljic, Likar-Smiljanic, Sarkar, IEEE T-EMC 43(4):662, 2001 | peer-reviewed | FR-4 wideband model | read full text |
| S4 | Huray, Oluwafemi, Loyer, Bogatin, Ye, DesignCon 2010 | conference | snowball model | read full text |
| S5 | Shlepnev, Simberian app note 2019; EPEPS 2017 unified RCC | app note / conference | roughness model unification, Groiss form | vendor but careful |
| S6 | Polar Instruments AP8155 | app note | roughness model validity ranges | vendor |
| S7 | Rogers RO4000 datasheet | datasheet | Dk/Df | manufacturer |
| S8 | Coonrod, PCD&F 2018; Milad, Uyemura 2020 | trade article | ENIG/finish loss | industry, measured data |
| S9 | Castles 2016 Sci Rep; Kuzmanić 2023; Işık 2026 arXiv; CoBCom 2016 PLA | peer-reviewed/preprint | 3D-print dielectrics | varied |
| S10 | ITU-R P.527-6 (2021); ITU-R P.368-10 (2022); Kaatze 1989 | standard / peer-reviewed | water, sea, ground | authoritative |
| S11 | Boulé AJP 2024; Davis & Kaplan AJP 2011 | peer-reviewed | energy flow in circuits | good |

## Contradictions / discrepancies found
- C9: Lumped-vs-distributed rise-time rules differ: Johnson & Graham l < t_r/(6 t_pd); Bogatin TD < 20 % t_r (t_r/5); 'critical length' t_r/(2 t_pd) answers a different question. Knee freq 0.5/t_r vs BW 0.35/t_r.
- C12: Via inductance: Johnson & Graham formula (as widely quoted) 5.08h[ln(4h/d)+1] nH vs Rosa/Grover partial (μ0h/2π)[ln(4h/d)−1] — ~2× difference; the J&G value is close to a loop value with a distant return. Flagged (J&G text not re-read).
- C11: Popular EMC wave-impedance sketches (monotonic curves meeting at λ/2π) differ from the exact dipole result: E-source |Z| dips to 257 Ω at kr ≈ 1.17 and H-source peaks at 553 Ω before converging to 377 Ω.
- C10: Snoek-limit formula written 'γMs/3π' in papers is unit-ambiguous (Ms must be 4πMs in G with γ in rad/s/Oe, or μ0Ms in T with γ in rad/s/T); using emu/cm³ gives 4π too small.
- C4: Gold resistivity: CRC 293 K = 2.214 µΩ·cm vs widely copied 2.44 µΩ·cm (Wikipedia/hyperphysics style tables) — 10 % difference → 5 % in δ. KB uses CRC.
- C5: Huray 2010 'hexagonal base dimension 9.4 µm' is geometrically ambiguous → SR = 1.1/3.2/4.3 for 79 spheres depending on interpretation (script). Shlepnev: treat Huray params as fit parameters.
- C6: Fresnel TM sign convention differs between texts (r_TM = ±r_TE at normal incidence). Noted in boundary page.
- C7: Polar AP8155 says Hammerstad saturates above ~4 GHz, Groiss useful to 7–10 GHz; Huray paper says Hammerstad fails > ~5 Gbps/10 GHz. Consistent in spirit; exact limits depend on foil.
- C8: Low-quality PCB vendor blogs claim ENIG adds '1–3 dB/inch at 10 GHz' and 'Ni μr ≈ 500'; measured data (Coonrod 2018) show ~0.2–0.4 dB/in at 25 GHz for microstrip. KB follows measured data.
- C1: μ0/(4π×10⁻⁷) − 1 is +5.5e-10 in CODATA 2018 (as quoted in many post-2019 texts/Wikipedia) but −1.4e-10 in CODATA 2022. Not a physics contradiction — new α data — but texts quoting "μ0 slightly larger than 4π×10⁻⁷" are now out of date.
- C2: Circular-polarization handedness: IEEE (thumb along propagation) vs traditional optics (viewed facing oncoming wave) are opposite: IEEE-RHCP = optics-LCP. Plus e^{jωt} vs e^{−iωt} flips the algebraic sign of the imaginary part. Documented in wave-equation page.
- C3: 120π vs 376.73 Ω (0.069 %) — explains 4th-digit disagreements between textbooks (e.g. 80π² vs 789 Ω).

## Knowledge gaps noticed (for later gap-filling)
- G1: Ni-P (ENIG) resistivity vs P content and effective μr(f) of plated nickel 0.1–10 GHz — need peer-reviewed measurement (ECTC/EMC papers).
- G2: Primary datasheets not re-fetched for PTFE, alumina, G10/NEMA LI-1, Kapton, LPI solder mask, RT/duroid 5880, TCDk, moisture uptake — medium confidence rows in dielectrics table.
- G3: Hand-laid rocket fibreglass Dk/Df; measured detuning of 433/915 MHz antennas in nose cones — measurement task (08/17).
- G4: CFRP conductivity (in-plane/transverse) from secondary summaries; anisotropic layup transmission not modelled.
- G5: Johnson & Graham via formula and 1/6 rise-time rule, Bogatin 20 % rule quoted from knowledge (books not re-read).
- G6: IEEE Std 145/211 handedness text not read directly; Orfanidis and Feynman sites blocked (403) — cited at chapter level.
- G7: FR-4 anisotropy numbers are Wiener bounds only; no measured in-plane vs z Dk found.
- G8: ICNIRP 2020 reference levels and FCC Part 15 limits used in examples quoted from knowledge (19-regulations to confirm).
- G9: 3-D pad fringing capacitance only estimated; SIW leakage/radiation loss not covered.

## Cross-domain notes (things other domains should cover/link)
- 03-transmission-lines: microstrip conductor loss (Wheeler incremental inductance), ε_eff filling factor, coax loss tables; link to skin-effect and dielectrics pages; Hammerstad–Jensen implementation exists in em_inductance.py (FD-verified).
- 04-real-components: ferrite-bead page should link magnetic-materials (Snoek, relaxation model); inductors page: proximity effect (Medhurst); via/pad parasitics: use partial vs loop distinction and C12 discrepancy.
- 06-rf-circuits: circulators page should build on Polder tensor/μ± in magnetic-materials.
- 08-antennas: antennas-on-rockets — nose-cone thin-wall numbers, CFRP shielding, near-field detuning (boundary & near-field pages); polarization page must adopt IEEE convention stated in PW page (RHCP = (x̂ − jŷ)e^{−jkz}).
- 09-propagation: two-ray model should use R_H/R_V from BC page (sea: P.527-6 ε at 433 MHz = 71.6 − j200.6; pseudo-Brewster 3.9°); implement P.527 soil model for UHF ground.
- 13-pcb-rf-layout-emc: ENIG vs ImAg/OSP guidance (SK page), plane-pair resonances (WG page: 100×50 mm → 715 MHz), DM/CM radiation numbers (RAD page), near-field shielding (NF page); JLCPCB per-prepreg Dk values needed.
- 16-simulation-tools: openEMS validation exercises suggested in each page (plane-wave slab, microstrip Poynting integral, Veritasium geometry transient).
- 17-test-measurement: far-field range distances (NF page), two-length line loss separation a√f + bf (SK page), dielectric coupon measurement.
- 19-regulations: confirm ICNIRP 2020 f/200 W/m² (400–2000 MHz) and FCC Class B limits used in examples.

## Resume instructions (what the next agent should do if this one is interrupted)
- Task COMPLETE (2026-09-27): 13 topic pages + _index.md + _sources.md in kb/02-electromagnetics/; 13 scripts tools/verify/em_*.py all passing.
- Follow-up work, if any, should address the Knowledge gaps G1–G9 above and the cross-domain notes.
