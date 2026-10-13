---
title: Link margin, reliability and availability — how much margin to design for
domain: 09-propagation-link-budget
slug: link-margin-availability
tags: [fade-margin, link-margin, availability, reliability, outage-probability, lognormal-shadowing, suzuki, rayleigh, RSS-margin, packet-repetition, burst-errors, gilbert-elliott, ITU-R-P.530]
prerequisites: [link-budget-methodology.md, multipath-fading-doppler.md, ../00-math-foundations/probability-random-processes-and-psd.md]
related: [empirical-path-loss-models.md, polarization-mismatch-loss.md, two-ray-ground-reflection.md, diffraction-knife-edge.md, ../10-comms-modulation/channel-coding-fec.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md]
level: intermediate
confidence: high
last_updated: 2026-09-27
---

# Link margin, reliability and availability — how much margin to design for

## Questions this page answers
- How much fade margin do I need for 90 %, 99 % or 99.9 % reliability?
- How do I combine shadowing, fading, antenna-pattern and polarisation uncertainties into one margin?
- Why is "add up all the worst cases" the wrong approach — and when is it right?
- Will sending each telemetry packet three times make the link reliable?
- What margin should a rocket telemetry link carry during ascent, descent and after landing?
- What is the difference between availability of a fixed link (99.99 %) and reliability of a flight link?

## TL;DR
- **Margin is a probability statement.** Specify it as "margin $M$ gives outage probability $p$ under model X". Lognormal shadowing with σ: $M = \sigma\,Q^{-1}(p)$ — 90 %: 1.28σ; 95 %: 1.64σ; 99 %: 2.33σ; 99.9 %: 3.09σ (σ = 8 dB → 10.3/13.2/18.6/24.7 dB) (`tools/verify/prop_margin.py`).
- **Rayleigh fading:** 10 dB per decade — 1 %: 20 dB, 0.1 %: 30 dB. **Shadowing + Rayleigh (Suzuki), margin above the model's median:** σ = 6 dB → 1 % needs **24.0 dB**; σ = 8 dB → **26.9 dB** — far less than the naive sum 20 + 2.33·8 = 38.6 dB.
- **Independent Gaussian-in-dB impairments add as RSS of their σ's:** four terms (σ = 6, 5, 3, 1 dB) need 19.6 dB for 99 %, not the 35 dB linear sum (Monte-Carlo confirms 19.6 dB). **Deterministic** effects (antenna null during boost, horizon, a ridge) must be handled explicitly, not statistically.
- **Repetition only helps if fades are independent.** With 20 % average loss in bursts of ~20 packets (Gilbert–Elliott channel), "at least 1 of 5 consecutive packets" still fails 9.9 % of the time, versus 2.5×10⁻⁴ if losses were independent.
- **Rocket practice:** ascent/descent with LOS — nominal margin ~45–52 dB covers a deterministic impairment allocation (~30 dB) plus ~10–20 dB statistical reserve; **landed** — design for ≥ 20–25 dB above the *median* plane-earth/terrain prediction for ~99 % location reliability, and use time/space diversity (repeated beacon + moving receiver).

## Intuition (no math)
A link budget gives the *typical* received power. Reality scatters around it: the ground station might be behind a bush, the rocket antenna might point its null at you for a second, multipath might cancel for a moment. **Margin** is how far below typical the signal can fall before packets are lost. How much you need depends on how widely the signal scatters (the statistics) and how often you can tolerate failure (the reliability target).

Not all uncertainties are alike. Some are **random and independent** — shadowing from unknown terrain, small pointing errors, unknown cable losses. Their standard deviations add in quadrature, so several small uncertainties need much less margin together than the sum of their individual worst cases. Others are **systematic** — the rocket *will* point its tail at a ground station near the pad during boost, the rocket *will* sink below the horizon at landing. Those must be designed around (geometry, antenna choice, operating mode), because margin cannot "average them away".

Repetition is a form of time diversity. It works when successive packets see independent channels. A fade caused by a slow effect (a null that lasts seconds, a hill, a static landed rocket) affects many packets in a row — repeating inside that window buys nothing.

## The math

### Level 1 — the margin formulas
- Margin: $M = \overline{P_r} - S$ (dB), $\overline{P_r}$ = predicted (median) received power, $S$ = sensitivity.
- **Lognormal shadowing** $X\sim\mathcal{N}(0,\sigma^2)$ dB: reliability $1 - p = P(X > -M) = 1 - Q(M/\sigma)$ ⇒ $M = \sigma\,Q^{-1}(p)$.
- **Rayleigh** (unit-mean power): $p = 1 - e^{-10^{-M/10}}$ ≈ $10^{-M/10}$.
- **Rician** (K-factor): $p = 1 - Q_1(\sqrt{2K}, \sqrt{2(K+1)10^{-M/10}})$ ([multipath-fading-doppler](multipath-fading-doppler.md)).
- **Composite (Suzuki)**: $p(M) = \int P_\text{Rayleigh}(M + x)\,f_X(x)\,dx$ — computed by Monte-Carlo here.
- **Independent dB-Gaussian terms**: $\sigma_\text{tot} = \sqrt{\sum\sigma_i^2}$, $M = \sigma_\text{tot}Q^{-1}(p)$.
- **Packet repetition**, independent losses with per-packet loss $q$: $P(\text{all } N \text{ lost}) = q^N$.

### Level 2 — why the naive sum over-designs, and the median-vs-mean trap
**Composite distributions.** The 1 % tail of (shadowing + Rayleigh) is dominated by combinations of *moderate* shadowing and *moderate* fading, not by both being at their 1 % points simultaneously; the required margin (26.9 dB at σ = 8 dB) is well below 20 + 18.6 = 38.6 dB. Monte-Carlo table (margin above the median local mean, dB):

| σ (dB) | 10 % outage | 1 % outage | 0.1 % outage |
|---|---|---|---|
| 0 (Rayleigh only) | 9.8 | 20.0 | 29.9 |
| 4 | 11.3 | 21.8 | 31.8 |
| 6 | 13.0 | 24.0 | 34.1 |
| 8 | 15.0 | 26.9 | 37.4 |

**Median vs mean.** Path-loss models predict the *median* (the mean in dB) of the local-mean power. The linear mean of a lognormal is higher than its median by $\sigma^2\ln10/20$ dB (1.8, 4.1, 7.4 dB for σ = 4, 6, 8 dB). Margins quoted relative to the linear mean are therefore larger by that amount; always state the reference. (An early version of this KB's script used the linear mean; corrected — see research log.)

**RSS of independent impairments.** If the uncertainties are each Gaussian in dB and independent, their sum is Gaussian with variance $\sum\sigma_i^2$. Example: shadowing σ = 6, antenna pattern/attitude σ = 5, polarisation σ = 3, Tx power/temperature σ = 1 dB → σ_tot = 8.4 dB, 99 % margin 19.6 dB (linear sum of 2.33σᵢ: 35.0 dB). Caveats: polarisation loss and antenna-pattern loss are *not* Gaussian (they have hard floors of 0 dB and long one-sided tails into nulls); for them, use their actual distributions or a deterministic worst-case in the geometry where the null is known to occur.

### Level 3 — time structure, fixed-link availability and flight reliability
**Bursty losses.** A two-state (Gilbert–Elliott) channel with loss 1 % in the good state, 90 % in the bad state, bad-state share 20 % and mean bad-dwell 20 packets gives 19 % average loss. The probability that *all* of $N$ consecutive packets are lost is 15.7 % (N = 2), 9.9 % (N = 5), 4.6 % (N = 10) — orders of magnitude worse than the independent model (3.6×10⁻², 2.5×10⁻⁴, 6×10⁻⁸) (script §4). Remedies: spread repeats over longer than the fade duration (interleaving in time), use diversity that decorrelates faster (a second antenna, the second frequency link), or strong FEC across packets (erasure codes) matched to the burst length.

**Fixed links vs flight links.** Terrestrial microwave links are designed for **availability** over a year (e.g. 99.99 % → 53 minutes/year outage) with ITU-R P.530 methods that model multipath-fade depth distributions vs path length, frequency and climate, and rain outages from P.837/P.838. A rocket flight lasts minutes; what matters is the **reliability of specific events**: "receive ≥ 1 position packet per 2 s during descent", "receive the landing position". Budget per phase:
1. *Boost (0–10 s)*: deterministic pattern null toward a near-pad GS, plume at small look angles, Doppler rate ⇒ low SF, GS placed off-axis; accept some loss (the logger has the data).
2. *Coast/apogee/descent*: LOS, large margin; lobing fades of seconds ⇒ packet rate high enough that 1 s of loss is tolerable.
3. *Final descent (< ~1 km altitude at 20–30 km)*: Fresnel clearance lost, then horizon ⇒ margin shrinks by tens of dB within a minute; make sure the last few fixes are sent at robust settings.
4. *Landed*: ground-level link, Suzuki-type statistics with a quasi-static channel ⇒ high SF beacon, repeat over minutes, receiver moves (space diversity) — design for ≥ 20–25 dB above the median prediction.

**Why "margin" at 30 km is not wasted.** The nominal +52 dB at 30 km (433 MHz, 2.4 kb/s) absorbs: antenna null −15, lobing −6, plume −10, detuning −2 (≈ 33 dB deterministic allocation, [link-budget-methodology](link-budget-methodology.md)) and still leaves ~19 dB for random effects (≈ 99 % for σ ≈ 8 dB lognormal). The toy flight model in `prop_margin.py` §5 (end-on dipole null ≈ −23 dB at worst (ψ = 4°), slow lobing up to −10.5 dB, trajectory to 20 km) keeps ≥ 30 dB margin throughout.

## Design equations & rules of thumb

| Situation | Model | Margin (typical) |
|---|---|---|
| LOS air-to-ground, random residuals | lognormal σ 3–6 dB | 99 %: 7–14 dB |
| Rayleigh only | exponential power | 90 %: 10 dB; 99 %: 20 dB; 99.9 %: 30 dB |
| Rician K = 10 dB | Marcum Q | 10 dB margin → 7×10⁻⁴ outage |
| Ground-level link (Suzuki, σ = 6–8 dB) | lognormal × Rayleigh | 90 %: 13–15 dB; 99 %: 24–27 dB |
| Several independent Gaussian-dB terms | RSS | $2.33\sqrt{\sum\sigma_i^2}$ for 99 % |
| Repetition over a bursty channel | Gilbert–Elliott | little gain unless spaced > burst length |
| Fixed microwave link availability | ITU-R P.530 | 99.99 %+; climate- and path-dependent |

## Worked examples
**1 — Landed-rocket beacon, 433 MHz, 5 km, V-pol whip.** Median two-ray prediction $P_r$ = −99.1 dBm (flat medium-dry ground) plus terrain/vegetation uncertainty σ = 6 dB and quasi-static Rayleigh fading: 99 % requires 24.0 dB ⇒ need sensitivity ≤ −123 dBm: SF7/BW125 (−124.5 dBm) is marginal, 2.4 kb/s (−128 dBm) OK with 5 dB spare, SF12 (−137 dBm) comfortable with 14 dB spare. With an H-pol dipole lying flat (−113.6 dBm median), only SF12 meets 99 % (−113.6 − 24 = −137.6 dBm vs −137 dBm: essentially zero spare).

**2 — Combining uncertainties for the 30 km ascent link.** Statistical terms: shadowing near the GS σ = 3 dB (clear site), antenna pattern (random roll/attitude excluding the known end-on null) σ = 5 dB, polarisation with a CP ground antenna σ ≈ 1 dB, Tx power/temperature σ = 1 dB ⇒ σ_tot = 6.0 dB, 99.9 % margin 18.5 dB. Deterministic allocation (plume, lobing, detuning): ~18 dB. Total need ≈ 37 dB < 52 dB available — the link closes with ~15 dB spare at 99.9 %.

**3 — Does triple-sending the GPS packet help?** If losses come from 2–8 s lobing nulls and the packet rate is 2/s, three consecutive copies fall into the same null. Sending the latest fix in *every* packet (so any packet suffices) and ensuring packet spacing is short relative to the fade-free intervals achieves more than repetition. After landing, spread repeats over minutes and move the receiving antenna between attempts.

## Practical notes
- **Measure your σ:** log RSSI vs predicted $P_r$ over a test flight or a drive test; the residual RMS is your σ for the site class.
- **Keep separate budgets per flight phase** (boost, coast, descent, final descent, landed).
- **Log packet loss vs time** on the ground station to distinguish random loss (scattered) from bursty loss (clustered) — the remedy differs.
- **Diversity by design:** two receive antennas (e.g. crossed polarisations or spaced > λ), both links (433 + 915 MHz), and a second ground station near the landing area.

## Common mistakes & misconceptions
- **Quoting a margin without the reliability and model** ("20 dB margin" means nothing on its own).
- **Adding all worst cases linearly** for independent random effects (massive over-design) — or, conversely, **treating a certain deterministic null as random** (under-design).
- **Using the linear mean instead of the median** as the reference for lognormal shadowing (off by σ² ln10/20).
- **Assuming packet repetition gives independent tries** on a slow or static channel.
- **Designing a flight link to "99.99 % availability"** — the relevant question is event reliability during a few minutes, dominated by geometry.

## How to simulate / verify
- `tools/verify/prop_margin.py` — lognormal margins, Suzuki Monte-Carlo (median-referenced), mean-vs-median offset, RSS vs linear combination (with Monte-Carlo check), independent vs Gilbert–Elliott repetition, toy flight time-series.
- `tools/verify/prop_doppler_fading.py` — Rayleigh/Rician outage and diversity.
- Build a flight-phase simulation: trajectory (from the team's 6-DOF sim) → geometry → pattern/polarisation/lobing/horizon → $P_r(t)$ → packet success probability → expected telemetry gaps. Compare with logged flight data.

## Open questions / gaps
- Site-specific σ values for Marcus's launch/landing areas are unknown; the examples use generic 3–8 dB.
- The distribution of antenna-pattern loss for a rolling/pitching rocket should come from the installed pattern (domain 08) and flight attitude logs, not a Gaussian assumption.
- ITU-R P.530's fixed-link fade model was not extracted (cited for scope only).

## Sources
1. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002, §4.9–4.10 (lognormal shadowing, percentage of coverage area), §5.6 (Rayleigh/Rician fade margins). (textbook)
2. A. Goldsmith, *Wireless Communications*, Cambridge 2005, §2.7–2.8 (shadowing, outage), §3.2 (composite fading), ch. 7 (diversity). (textbook)
3. H. Suzuki, "A statistical model for urban radio propagation," *IEEE Trans. Commun.* 25(7), 673–680 (1977). (peer-reviewed) — composite lognormal–Rayleigh.
4. E. N. Gilbert, "Capacity of a burst-noise channel," *Bell Syst. Tech. J.* 39, 1253–1265 (1960); E. O. Elliott, "Estimates of error rates for codes on burst-noise channels," *BSTJ* 42, 1977–1997 (1963). (peer-reviewed)
5. ITU-R Recommendation P.530, *Propagation data and prediction methods required for the design of terrestrial line-of-sight systems* (current revision). https://www.itu.int/rec/R-REC-P.530 (standard — cited for scope)
6. B. Sklar, *Digital Communications*, 2nd ed., 2001, ch. 5 (link margin) and ch. 15 (fading channels). (textbook)
7. `tools/verify/prop_margin.py`, `tools/verify/prop_doppler_fading.py` (this KB).
