---
title: GNSS error sources and DOP — satellite clock/orbit (SISRE), ionosphere incl. equatorial scintillation over Singapore, troposphere, multipath, receiver noise, UERE budgets and dilution of precision
domain: 21-gnss
slug: gnss-error-sources-dop
tags: [gnss, error-budget, uere, sisre, broadcast-ephemeris, satellite-clock, ionosphere, klobuchar, nequick, tec, iono-free, scintillation, s4, equatorial-plasma-bubble, singapore, troposphere, saastamoinen, mapping-function, multipath, narrow-correlator, receiver-noise, dop, gdop, pdop, hdop, vdop, tdop, elevation-mask, multi-gnss, ecef, geodetic, wgs84, enu, azimuth-elevation, broadcast-ephemeris-kepler, satellite-clock-relativistic, sagnac, raim, fde, protection-level]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, ../09-propagation-link-budget/ionospheric-hf-propagation.md, ../00-math-foundations/probability-random-processes-and-psd.md]
related: [gnss-signals-and-codes.md, rtk-ppp-and-corrections.md, gnss-on-rockets-dynamics-and-limits.md, ../08-antennas/gnss-antennas.md, ../09-propagation-link-budget/multipath-fading-doppler.md, ../09-propagation-link-budget/atmospheric-rain-attenuation.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# GNSS error sources and dilution of precision

## Questions this page answers
- Where does the few-metre error of a standalone GNSS fix come from?
- How good are the broadcast orbits and clocks of GPS, Galileo, BeiDou and GLONASS?
- How big is the ionospheric error in Singapore, and what is equatorial scintillation?
- How much does the troposphere delay the signal in a hot, humid climate?
- What is multipath and why do narrow correlators help?
- What are GDOP, PDOP, HDOP and VDOP, how are they derived, and why is vertical worse?
- How much does multi-constellation reception improve DOP over Singapore?
- What happens to DOP when the rocket's antenna points sideways?
- How do I convert latitude/longitude/height to ECEF and to local east-north-up, and get a satellite's azimuth and elevation?
- How do I compute where a GPS or Galileo satellite is from the broadcast ephemeris (RINEX navigation file)?
- How accurate is the broadcast orbit compared with the IGS precise orbit?
- What is RAIM, how does a receiver detect a bad satellite, and what is a protection level?

## TL;DR
- **Position error ≈ DOP × σ_UERE** (verified by Monte Carlo: ratio 1.00 within 5 %, `tools/verify/gnss_dop_errors.py`). Typical single-frequency σ_UERE ≈ 1–5 m, dominated by the ionosphere at low latitudes.
- **Satellite orbit + clock (SISRE)**, global RMS for 2017: Galileo ≈ 0.2 m, GPS ≈ 0.6 m, BeiDou-2 ≈ 1 m, GLONASS ≈ 2 m [1]; BDS-3 MEO ≈ 0.5 m (later study) [2].
- **Ionosphere**: 0.162 m per TECU at L1; Singapore lies between the geomagnetic dip equator (≈ 9–11°N at 100–106°E, where SE-Asian scintillation stations sit [3]) and the southern equatorial-anomaly crest, so daytime TEC of 50–100 TECU (8–16 m vertical at L1) is plausible; broadcast models remove only ~half. Dual-frequency (F9P L1/L2) removes the first-order term at ×2.98 noise ([ionosphere page](../09-propagation-link-budget/ionospheric-hf-propagation.md)).
- **Scintillation** from post-sunset equatorial plasma bubbles: strongest 19:00–02:00 local time around the equinoxes (Mar–Apr, Sep–Oct) and at high solar activity — Solar Cycle 25 is at/after maximum (2020–2025 observations) [3]. Effects: C/N₀ fades, cycle slips, loss of lock, RTK float. **Daytime launches are rarely affected; night-time tests and RTK surveys around the equinoxes are.**
- **Troposphere**: Saastamoinen zenith delay for Singapore-like air (1010 hPa, 28 °C, 80 % RH) = 2.31 m hydrostatic + 0.29 m wet (script); ×5.8 at 10° elevation. Models leave ≈ 0.1–0.2 m (wet part). Irrelevant above ~10–15 km altitude.
- **Multipath** (code): with a reflection at −6 dB, a wide (d = 1) correlator errs by up to ≈ 49 m (in-phase) / 73 m (out-of-phase); a narrow (d = 0.1) correlator by ≤ 7.3 m (script). Carrier-phase multipath is ≤ λ/4 (≈ 5 cm).
- **Coordinates and orbits** (new Level 3b): WGS-84 geodetic ↔ ECEF ↔ ENU, satellite ECEF from the 16-parameter Kepler ephemeris, satellite clock with the relativistic term (≈ 23 ns per 0.01 of eccentricity), light time + Sagnac (±36 m if ignored). Real data, 2026-10-05: **GPS broadcast orbit − IGS rapid orbit RMS 1.46 m radial (mostly the constant antenna-offset), 1.09 m along, 0.49 m cross, 1.89 m 3-D** (`tools/verify/s13_gnss_ephemeris.py`).
- **RAIM**: least-squares residuals $\mathbf r=\mathbf S\boldsymbol\rho$ give $\mathbf r^T\mathbf r/\sigma^2\sim\chi^2_{n-4}$; ≥ 5 satellites to detect, ≥ 6 to exclude. 8 satellites, σ = 3 m, $P_{fa}$ 3.3×10⁻⁷, $P_{md}$ 10⁻³ → **HPL ≈ 21 m** (script).
- **DOP over Singapore** (synthetic constellations, 10° mask, 24 h median): GPS only ≈ 7.8 satellites, HDOP 0.89 / VDOP 1.70; GPS+GAL 15.8, 0.64/1.17; GPS+GAL+BDS 29.7, 0.49/0.80; all five systems 40.5, 0.43/0.70 (script). An antenna tilted 90° (under a chute) sees ≈ 12 satellites, HDOP ≈ 2.0. **Real broadcast constellation, 2026-10-05:** GPS 10 satellites (min 8), HDOP 0.81 / VDOP 1.45; GPS+Galileo 20 (min 15), 0.58/1.05 — about 10 % better than the synthetic model, as expected.

## Intuition (no math)
Each pseudorange is a range measurement corrupted by a stack of small errors: the satellite is not quite where its broadcast orbit says and its clock is a little off; the signal is slowed by the ionosphere (by an amount that changes with time of day, season, solar activity and latitude) and by water vapour and dry air near the ground; it may bounce off nearby surfaces before arriving; and the receiver's tracking loops add noise. Add these in quadrature → the user-equivalent range error (UERE), typically a few metres.

The position is then found by intersecting spheres. If all satellites are bunched in one part of the sky, the spheres intersect at shallow angles and small range errors become large position errors — that amplification is the dilution of precision (DOP). Because all satellites are above you (none below the horizon), the vertical is always worse determined than the horizontal, and the receiver clock trades off against height.

## The math

### Level 1 — the UERE budget
$$\sigma_{UERE} = \sqrt{\sigma_{SISRE}^2 + \sigma_{iono}^2 + \sigma_{tropo}^2 + \sigma_{mp}^2 + \sigma_{rx}^2},\qquad \sigma_{pos} = \text{DOP}\cdot\sigma_{UERE}$$

| Source | Single-frequency, open sky (1σ, m) | Dual-frequency | RTK (short baseline) | Notes |
|---|---|---|---|---|
| Satellite orbit + clock | 0.2 (GAL) – 0.6 (GPS) – 2 (GLO) [1] | same | cancels | clocks dominate SISRE [1] |
| Ionosphere (residual) | 1–5 (low latitude, Klobuchar/NeQuick removes ~50 %) | ≈ 0.1 (higher-order) | cancels (≤ 1 ppm) | 0.162 m/TECU at L1 |
| Troposphere (residual) | 0.1–0.5 (elevation-dependent) | same | cancels | 2.6 m zenith before model |
| Multipath (code) | 0.2–2 (site-dependent) | 0.2–2 | phase: mm–cm | narrow correlators help |
| Receiver noise (code) | 0.1–0.5 | ×2–3 (iono-free) | phase: mm | C/N₀ and loop BW |
| **UERE** | **≈ 1.5–5** | **≈ 0.5–2** | **≈ 0.01** | |

With HDOP ≈ 0.5–1 multi-GNSS this gives the datasheet "1.5 m CEP" (24-h static) of both u-blox modules [6][7].

### Level 2 — DOP derivation
Linearised pseudorange model ([receiver page](gnss-receiver-architecture-acquisition-tracking.md#level-2--acquisition-statistics-loop-noise-the-navigation-equations)): $\Delta\boldsymbol\rho = \mathbf G\Delta\mathbf x + \boldsymbol\varepsilon$, rows $\mathbf g_i = [-\cos E_i\sin A_i,\ -\cos E_i\cos A_i,\ -\sin E_i,\ 1]$ in local East-North-Up (azimuth $A_i$, elevation $E_i$). For i.i.d. errors of variance $\sigma^2$, least squares gives
$$\operatorname{cov}(\Delta\hat{\mathbf x}) = \sigma^2\mathbf H,\quad \mathbf H = (\mathbf G^T\mathbf G)^{-1}$$
$$\text{GDOP}=\sqrt{\operatorname{tr}\mathbf H},\ \ \text{PDOP}=\sqrt{H_{11}+H_{22}+H_{33}},\ \ \text{HDOP}=\sqrt{H_{11}+H_{22}},\ \ \text{VDOP}=\sqrt{H_{33}},\ \ \text{TDOP}=\sqrt{H_{44}}.$$
**Analytic example** (one satellite at zenith + three at elevation $e$, 120° apart): $\mathbf G^T\mathbf G$ = diag(1.5cos²e, 1.5cos²e) for E,N and a 2 × 2 Up/clock block $\begin{bmatrix}1+3\sin^2 e & -(1+3\sin e)\\ -(1+3\sin e) & 4\end{bmatrix}$. Hence $\text{HDOP} = 1.1547/\cos e$ and VDOP from the 2 × 2 inverse: e = 10°: HDOP 1.17, VDOP 1.40; e = 30°: 1.33, 2.31; e = 60°: 2.31, 8.62 (verified numerically). Lesson: **low-elevation satellites are what make the vertical observable** — raising the elevation mask (to cut multipath and atmosphere) costs VDOP.

**Why vertical is worse:** the Up component and the clock column are correlated (every satellite above the horizon has $-\sin E < 0$ while the clock coefficient is +1); with satellites only above you, height and clock bias can trade off. A satellite below the horizon (impossible on the ground, possible for a high-altitude vehicle with a downward antenna) would break the correlation.

### Level 3 — the error sources in detail
**Broadcast ephemeris and clock.** Navigation messages give Keplerian elements + corrections (GPS, Galileo, BeiDou) or ECEF state + accelerations (GLONASS) valid for ~2–4 h (GLONASS 30 min); the SISRE is the projection of orbit and clock errors on the user's line of sight, dominated by the clock [1]. Galileo's passive hydrogen masers and frequent uploads give the smallest SISRE.

**Ionosphere.** Group delay $40.3\,\text{TEC}/f^2$ (m), phase advance of equal magnitude ([derivation](../09-propagation-link-budget/ionospheric-hf-propagation.md)); slant factor ≈ 1.75 at 30° elevation, ≈ 3 near the horizon. GPS broadcasts the Klobuchar model (8 coefficients; removes ≈ 50 % RMS globally, less effectively at the equator), Galileo NeQuick-G, BeiDou its own Klobuchar-like model; u-blox applies them in standalone mode. Dual-frequency combination $P_{IF} = 2.546P_1 - 1.546P_2$ (L1/L2) removes the first-order term with ×2.98 noise; L1/L5 ×2.59 (script).

**Equatorial ionosphere and Singapore.** The geomagnetic dip equator over Southeast Asia passes ≈ 9–11°N (the SEALION stations Bac Lieu 9.3°N and Chumphon 10.7°N are "at geomagnetic equatorial latitudes" [3]); Singapore at 1.3°N is ≈ 8–10° south of it, i.e. between the dip equator and the southern crest of the equatorial ionization anomaly (≈ ±15° magnetic) — a high-TEC, high-gradient, high-scintillation region. After sunset the eastward electric field's pre-reversal enhancement lifts the F layer and Rayleigh–Taylor instability grows **equatorial plasma bubbles** (EPBs): depleted plumes with km-to-m-scale irregularities that diffract L-band signals. Andoh et al. (2026) report, for 2020–2025 in Southeast Asia, scintillation intensifying from evening to post-midnight, mostly in March–April and September–October, lasting later into the night at higher solar activity, enhanced when a geomagnetic storm's main phase starts in the evening and suppressed for 1–2 days after the recovery phase begins [3]. Amplitude scintillation index $S_4 = \sqrt{\langle I^2\rangle - \langle I\rangle^2}/\langle I\rangle$; weak < 0.3, moderate 0.3–0.6, strong > 0.6; $S_4 \propto f^{-1.5}$ in weak scattering ([ionosphere page](../09-propagation-link-budget/ionospheric-hf-propagation.md)). Strong amplitude fades (> 10–20 dB) and rapid phase fluctuations cause cycle slips and loss of PLL lock — the same mechanism that rocket dynamics exploit, but without warning.

**Troposphere.** Neutral atmosphere delay is non-dispersive (same on all frequencies). Saastamoinen zenith hydrostatic delay $\text{ZHD} = 0.0022768\,P/(1-0.00266\cos2\varphi-0.00028h)$ (m, P in hPa, h in km) and wet $\text{ZWD} = 0.002277\,(1255/T + 0.05)\,e$ (e water-vapour pressure hPa) [8]: Singapore-like values 2.306 m + 0.288 m (script; tropical ZWD is among the largest anywhere). Slant delay ≈ zenith / sin E for E > 15° (better mapping functions — Niell, VMF — below that): 5.2 m at 30°, 14.9 m at 10°. On a rocket above ~10 km most of the troposphere is below and the receiver's model (which assumes a ground-level user) may over-correct slightly — a minor effect next to dynamics.

**Multipath.** A reflection with relative amplitude α and extra delay δ distorts the correlation triangle; the early–late discriminator's zero moves (error envelope). For α = 0.5 (−6 dB) (script, 1 chip = 293 m):

| δ (chips) | d = 1, in-phase | d = 1, out-of-phase | d = 0.1, in-phase | d = 0.1, out-of-phase |
|---|---|---|---|---|
| 0.05 | 4.9 m | −14.7 m | 4.9 m | −7.3 m |
| 0.25 | 24.4 | −73.3 | 7.3 | −7.3 |
| 0.5 | 48.8 | −58.6 | 7.3 | −7.3 |
| 1.0 | 48.8 | −29.3 | 4.9 | −2.9 |
| 1.2 | 29.3 | −17.6 | 0 | 0 |

The narrow-correlator plateau is $\alpha d/2$ chips (= 7.3 m); reflections delayed more than $1 + d/2$ chips cause no error. Higher chip rates (L5/E5, 29 m chips) shrink everything tenfold. Antenna-side defences: RHCP (a single reflection is mostly LHCP), large ground planes and choke rings for low-elevation rejection ([GNSS antennas](../08-antennas/gnss-antennas.md)). On a launch pad, the rail, tower and support equipment are multipath sources: survey the pad position away from them or use a mast.

**Receiver noise.** Code noise ∝ √(B_n d / (C/N₀)) — 0.37 m at 45 dB-Hz with a carrier-aided 0.5 Hz, d = 0.2 DLL; carrier noise ≈ λ/(2π) × σ_PLL ≈ 1 mm ([receiver page](gnss-receiver-architecture-acquisition-tracking.md#worked-examples)).

**Other effects receivers already model**: satellite relativistic clock term, Sagnac (Earth rotation during signal flight, up to ≈ 30 m), satellite antenna phase-centre offsets (precise work), solid-Earth tides (cm, PPP only).

### Level 3b — coordinate frames, satellite positions from the broadcast ephemeris, and integrity (RAIM)

**(a) Frames.** Three frames appear in every GNSS calculation. *ECEF* (Earth-centred, Earth-fixed; x through 0° latitude/0° longitude, z through the north pole) is where satellites and receivers are computed; GPS broadcast orbits are in WGS-84 and Galileo's in GTRF, both aligned with ITRF to a few centimetres [10][11]. *Geodetic* coordinates (latitude φ, longitude λ, height h above the WGS-84 ellipsoid with a = 6 378 137 m, f = 1/298.257223563, $e^2=f(2-f)=6.694\times10^{-3}$) are what the receiver reports. *Local ENU* (east, north, up at the receiver) is where azimuth, elevation and the DOP geometry live.

Forward: with the prime-vertical radius $N(\varphi)=a/\sqrt{1-e^2\sin^2\varphi}$,
$$x=(N+h)\cos\varphi\cos\lambda,\quad y=(N+h)\cos\varphi\sin\lambda,\quad z=\big(N(1-e^2)+h\big)\sin\varphi .$$
Inverse: $\lambda=\operatorname{atan2}(y,x)$, $p=\sqrt{x^2+y^2}$; start from $\varphi=\operatorname{atan2}(z,p(1-e^2))$ and iterate $h=p/\cos\varphi-N$, $\varphi=\operatorname{atan2}\!\big(z,\ p(1-e^2N/(N+h))\big)$ — 3–5 iterations reach sub-millimetre accuracy from −100 m to GNSS-orbit heights (script: worst 1×10⁻⁵ mm; agrees with astropy's WGS-84 conversion to < 1 µm). Closed forms (Bowring, Vermeille) exist but are not needed on a flight computer. Note that $h$ is the **ellipsoidal** height; height above mean sea level is $h-N_g$ with $N_g$ the geoid undulation (u-blox NAV-PVT reports both `height` and `hMSL`; NMEA GGA gives the separation) — mixing them is a metres-level error in an altitude comparison with the barometer.

ENU: $\mathbf d=\mathbf R(\mathbf r_s-\mathbf r_r)$ with
$$\mathbf R=\begin{bmatrix}-\sin\lambda & \cos\lambda & 0\\ -\sin\varphi\cos\lambda & -\sin\varphi\sin\lambda & \cos\varphi\\ \cos\varphi\cos\lambda & \cos\varphi\sin\lambda & \sin\varphi\end{bmatrix},\qquad A=\operatorname{atan2}(d_E,d_N),\quad E=\arcsin(d_U/\lVert\mathbf d\rVert).$$
The geometry rows $\mathbf g_i$ of Level 2 are just $[-\hat{\mathbf d}_i^T,\ 1]$ in this frame.

**(b) Satellite position from the broadcast Kepler ephemeris** (GPS LNAV per IS-GPS-200 Table 20-IV [10]; Galileo [11], BeiDou MEO/IGSO and QZSS use the same algorithm with their own constants). The message gives a reference time $t_{oe}$, $\sqrt A$, $e$, $M_0$, ω, $i_0$, $\Omega_0$, the rates $\Delta n$, $\dot\Omega$, IDOT, and six harmonic corrections $C_{uc},C_{us},C_{rc},C_{rs},C_{ic},C_{is}$. For a time $t$ (GPS seconds of week):
1. $t_k=t-t_{oe}$ (± 604 800 s at a week crossover; stay inside the fit interval, normally $|t_k|\le 2$ h).
2. $n=\sqrt{\mu/A^3}+\Delta n$, $M_k=M_0+nt_k$; solve Kepler's equation $M_k=E_k-e\sin E_k$ by Newton iteration (3–4 steps for $e<0.03$).
3. True anomaly $\nu_k=\operatorname{atan2}(\sqrt{1-e^2}\sin E_k,\ \cos E_k-e)$; argument of latitude $\Phi_k=\nu_k+\omega$.
4. Corrections: $u_k=\Phi_k+C_{us}\sin2\Phi_k+C_{uc}\cos2\Phi_k$, $r_k=A(1-e\cos E_k)+C_{rs}\sin2\Phi_k+C_{rc}\cos2\Phi_k$, $i_k=i_0+\text{IDOT}\,t_k+C_{is}\sin2\Phi_k+C_{ic}\cos2\Phi_k$.
5. In-plane position $x'=r_k\cos u_k$, $y'=r_k\sin u_k$; corrected node longitude $\Omega_k=\Omega_0+(\dot\Omega-\dot\Omega_E)t_k-\dot\Omega_Et_{oe}$ (this term converts the inertial node into the rotating ECEF frame).
6. $x=x'\cos\Omega_k-y'\cos i_k\sin\Omega_k$, $y=x'\sin\Omega_k+y'\cos i_k\cos\Omega_k$, $z=y'\sin i_k$.

Constants: $\mu$ = 3.986005×10¹⁴ m³/s² (GPS) but 3.986004418×10¹⁴ (Galileo, BeiDou) — using the wrong one moves a satellite by metres after a few hours; $\dot\Omega_E$ = 7.2921151467×10⁻⁵ rad/s. The **satellite clock** is $\Delta t_{sv}=a_{f0}+a_{f1}(t-t_{oc})+a_{f2}(t-t_{oc})^2+F e\sqrt A\sin E_k$ with $F=-4.442807633\times10^{-10}$ s/√m; the last (relativistic) term is ≈ 23 ns ≈ 7 m peak per 0.01 of eccentricity, so it must not be forgotten. Single-frequency users also subtract the group-delay term ($T_{GD}$ for GPS L1, $BGD$ for Galileo). GLONASS is different: it broadcasts a PZ-90 position, velocity and luni-solar acceleration every 30 min, and the user integrates the equations of motion with the $J_2$ term (Runge–Kutta) — not scripted here. BeiDou GEO satellites need one extra −5° rotation in step 6 (also not scripted).

**(c) Transmit time and Earth rotation.** The satellite position is needed at transmission, $t_{tx}=t_{rx}-\tau$ with $\tau=\rho/c$ ≈ 67–86 ms; iterate twice. During τ the Earth turns by $\dot\Omega_E\tau$, so the satellite ECEF vector must be rotated by that angle about z before forming the range (the Sagnac correction). Ignoring it gives range errors of up to ≈ ±36 m in the script's geometry from Singapore — it shows up as a metres-to-tens-of-metres position bias, not as noise. The script simulates pseudoranges this way for a receiver at 3 km altitude and the least-squares solution from the Earth's centre recovers position and clock exactly.

**(d) How good is the broadcast orbit?** Comparing a full day of real GPS broadcast ephemerides (BKG merged BRDC file, 2026-10-05) with the IGS rapid orbit every 15 min [12]: RMS radial 1.46 m, along-track 1.09 m, cross-track 0.49 m, 3-D 1.89 m over 3072 satellite-epochs. The radial difference is mostly a constant −1.42 m: the broadcast orbit refers to the satellite antenna phase centre and the IGS orbit to the centre of mass, offset towards the Earth; about each satellite's daily mean the radial scatter is only 0.15 m. (Projected onto a user's line of sight and combined with the clock error, this is the SISRE of Level 1; the clock part was not checked here.) The Galileo comparison was not possible with this product (the IGS rapid orbit is GPS-only; a multi-GNSS MGEX orbit is needed).

**(e) Integrity — receiver autonomous integrity monitoring (RAIM).** DOP tells you how errors are *amplified*; RAIM asks whether one measurement is *wrong* (a satellite clock jump, a multipath or spoofing outlier). With $n>4$ satellites the least-squares residuals are $\mathbf r=\mathbf S\boldsymbol\varepsilon$, $\mathbf S=\mathbf I-\mathbf G(\mathbf G^T\mathbf G)^{-1}\mathbf G^T$ (rank $n-4$). Without a fault, $T=\mathbf r^T\mathbf r/\sigma^2$ follows a χ² law with $n-4$ degrees of freedom, so a threshold $T_D$ fixes the false-alarm probability. A bias $b$ on satellite $i$ makes $T$ non-central with $\lambda=b^2S_{ii}/\sigma^2$ and moves the horizontal position by $b\sqrt{A_{1i}^2+A_{2i}^2}$ ($\mathbf A=(\mathbf G^T\mathbf G)^{-1}\mathbf G^T$). The ratio of the two is the satellite's **slope**, $\text{slope}_i=\sqrt{(A_{1i}^2+A_{2i}^2)/S_{ii}}$; the **horizontal protection level** is $\text{HPL}=\max_i\text{slope}_i\cdot\sigma\sqrt{\lambda_{det}}$, where $\lambda_{det}$ gives the allowed missed-detection probability [13][14]. Detection needs ≥ 5 satellites; identifying and excluding the bad one (FDE) needs ≥ 6, and works only when the residuals of different satellites are not too correlated. Advanced RAIM (ARAIM) extends this to dual-frequency multi-constellation receivers. For a rocket the practical use is in post-flight log analysis (`RXM-RAWX`) or as an extra consistency check in flight software — reject the fix and fall back to IMU/baro when T exceeds the threshold.


## Design equations & rules of thumb

| Quantity | Value | Source |
|---|---|---|
| σ_pos | DOP × σ_UERE | derivation, script |
| SISRE (RMS) | GAL 0.2, GPS 0.6, BDS-2 1, GLO 2 m (2017); BDS-3 ≈ 0.5 m | [1][2] |
| Iono L1 | 0.162 m/TECU; 50 TECU vertical ≈ 8 m | [ionosphere page] |
| Iono-free noise | ×2.98 (L1/L2), ×2.59 (L1/L5) | script |
| ZHD / ZWD (Singapore) | 2.31 / 0.29 m | script, [8] |
| Narrow-correlator multipath plateau | α d/2 chips | script |
| HDOP (zenith + 3 at e) | 1.1547/cos e | derivation |
| Typical DOP, multi-GNSS (SG) | HDOP ≈ 0.5, VDOP ≈ 0.8 | script (synthetic) |
| Scintillation season (SG) | equinox months, 19:00–02:00 LT, solar max | [3] |
| WGS-84 | a = 6 378 137 m, 1/f = 298.257223563, e² = 6.694×10⁻³ | [10] |
| Kepler solve | $M=E-e\sin E$, Newton, 3–4 iterations | [10] |
| Relativistic clock term | $Fe\sqrt A\sin E$, ≈ 23 ns per 0.01 of e | [10] |
| Sagnac (if ignored) | up to ≈ ±36 m range | script |
| Broadcast − IGS orbit (GPS, 2026-10-05) | 1.46 / 1.09 / 0.49 m radial/along/cross RMS | script, [12] |
| RAIM | $T=\mathbf r^T\mathbf r/\sigma^2\sim\chi^2_{n-4}$; HPL = max slope · σ√λ | [13][14] |

## Worked examples
**1 — Standalone accuracy of the MAX-M10S in Singapore at 14:00.** σ_SISRE ≈ 0.5 m (GPS+GAL+BDS weighted), iono residual ≈ 3 m (TEC 60 TECU vertical, Klobuchar removes half → 4.9 m vertical-equivalent, partly common to all satellites and absorbed into the clock; take 3 m effective), tropo 0.2 m, multipath 0.5 m, noise 0.3 m → σ_UERE ≈ 3.1 m. HDOP 0.5, VDOP 0.8 → σ_H ≈ 1.6 m, σ_V ≈ 2.5 m. Consistent with the datasheet 1.5 m CEP (24 h static; diurnal ionosphere averages lower) [7].

**2 — GNSS altitude vs barometer at apogee.** VDOP 0.8 × UERE 3 m ≈ 2.5 m (1σ) standalone — far better than a barometer's absolute altitude (hundreds of metres of weather-dependent offset) but noisier sample-to-sample. Fuse: barometer for short-term apogee detection, GNSS for absolute altitude and drift correction.

**3 — Equinox night RTK survey of the launch pad.** Scheduled 21:00 local time in late March near solar maximum: high probability of EPB scintillation; expect RTK fixes to drop to float intermittently and GLONASS/L1 C/A to lose lock first. Move the survey to daytime or accept a longer survey-in (u-blox survey-in averages standalone fixes anyway) [6].

**5 — Where is G01, seen from Singapore? (real ephemeris).** Broadcast record G01, $t_{oe}$ = 2026-10-05 12:00:00 GPST (20:00 SGT): $\sqrt A$ = 5153.75 √m → a = 26 561.1 km, e = 0.00203, $i_0$ = 54.79°. At $t=t_{oe}$ ($t_k$ = 0): $E_k$ = −26.41°, ECEF = (−14 880.983, 20 963.731, −6 481.975) km, |r| = 26 513.0 km. From Singapore (1.3521° N, 103.8198° E, h = 15 m → ECEF (−1 523 121.7, 6 191 803.0, 149 494.2) m): azimuth 126.7°, elevation 55.9°, range 20 991 km. Satellite clock offset 156.633 µs, of which the relativistic term is 2.07 ns (0.62 m). The IGS rapid orbit puts the satellite 2.58 m away from the broadcast position at that epoch. The Galileo record E19 at the same time gives azimuth 194.0°, elevation 62.7° (script §3).

**6 — Protection level for an 8-satellite fix.** Satellites at elevations 15–85°, σ = 3 m, $P_{fa}$ = 3.33×10⁻⁷ and $P_{md}$ = 10⁻³ (aviation-style allocations): $T_D$ = 35.7 (χ², 4 degrees of freedom), $\lambda_{det}$ = 78.5, largest slope 0.80 → **HPL = 0.80 × 3 × √78.5 ≈ 21 m** (HDOP 0.95). A 41 m bias on the worst-slope satellite is detected 90 % of the time in Monte Carlo (theory 0.900); the largest *undetected* horizontal error in 40 000 trials was 24 m, close to the HPL as intended. The largest normalised residual points at the faulty satellite 99.7 % of the time at that bias, but residual correlations reach 0.76, so with a weaker geometry exclusion can pick the wrong satellite.

**4 — DOP under the parachute.** Boresight tilted 60°: ≈ 19 satellites, HDOP 1.07, VDOP 1.39; 90°: ≈ 12, HDOP 2.04, VDOP 1.76 (script, GPS+GAL+BDS). With σ_UERE 3 m, the horizontal error rises from ≈ 1.5 m to ≈ 6 m — still fine for recovery.

## Practical notes
- **Elevation mask**: u-blox `CFG-NAVSPG-INFIL_MINELEV` (default a few degrees) — raise to 10–15° only if low satellites are visibly bad (multipath, scintillation) [6].
- **Use the receiver's own accuracy estimates** (`hAcc`, `vAcc`, `sAcc` in NAV-PVT) as EKF measurement noise rather than DOP alone; they include C/N₀ and residual information.
- **Record `NAV-SAT`/`RXM-RAWX`** to diagnose: scintillation shows as C/N₀ fades on some satellites and not others; multipath as elevation-dependent noise; interference as all satellites dropping together ([interference page](gnss-interference-jamming-spoofing.md)).
- **Space weather**: check Kp/Dst and local EPB forecasts before night tests; geomagnetic storms in the evening can intensify bubbles [3].

## Common mistakes & misconceptions
- **"More satellites = proportionally better accuracy."** DOP improves roughly as 1/√N only while geometry improves; UERE (ionosphere!) then dominates.
- **"HDOP 1 means 1 m error."** It means 1 × σ_UERE.
- **"The ionosphere is negligible at the equator because it's warm."** The opposite: equatorial TEC and scintillation are among the largest on Earth.
- **"Dual-frequency removes all ionosphere error."** First order only; scintillation and higher-order terms remain, and noise grows ×2.6–3.
- **"Multipath only matters in cities."** A launch rail, tower or car roof beside the antenna is enough.
- **"The GNSS altitude is height above sea level."** The raw solution is height above the WGS-84 ellipsoid; mean-sea-level height subtracts the geoid undulation. Compare like with like (u-blox `height` vs `hMSL`).
- **"Satellite position = Kepler orbit at the receive time."** Use the transmit time and rotate for Earth rotation; skipping the Sagnac step costs up to tens of metres, and skipping the relativistic clock term up to several metres.
- **"Low DOP means the fix is trustworthy."** DOP ignores faults; one bad satellite can pull a low-DOP solution far away. That is what RAIM checks.

## How to simulate / verify
- `python3 tools/verify/gnss_dop_errors.py` — analytic vs numeric DOP, LSQ solution and DOP×UERE Monte Carlo, synthetic multi-GNSS constellations over Singapore (24 h), antenna-tilt sky masks, Saastamoinen delays, iono-free amplification, multipath error envelopes. ALL PASS.
- `python3 tools/verify/s13_gnss_ephemeris.py [BRDC.rnx IGS.SP3]` — WGS-84 geodetic↔ECEF (round trip, astropy cross-check), ENU look angles, Kepler ephemeris for real GPS/Galileo records, a full day of broadcast vs IGS rapid orbits (radial/along/cross), real-sky DOP over Singapore, light-time + Sagnac least squares, RAIM (χ² test, slopes, HPL, Monte Carlo P_d, exclusion) and the Wi-Fi/LoRa IMD frequency check for the [interference page](gnss-interference-jamming-spoofing.md). Pre-registered expectations P1–P5 all met; the Galileo orbit comparison was not testable with the GPS-only IGS rapid product. ALL PASS (output in `s13_gnss_ephemeris_output.txt`; data files from https://igs.bkg.bund.de/root_ftp/IGS/).
- Real constellations: download a current almanac/RINEX navigation file and use RTKLIB `rtkplot` / GNSS planning tools (e.g. Trimble GNSS Planning) for the launch date and site.

## Open questions / gaps
- No quantitative TEC/S4 climatology for Singapore itself was extracted (the nearest stations in [3] are in Vietnam/Thailand at the dip equator); NTU/regional datasets would close this.
- The DOP numbers use idealised Walker constellations; one real day (2026-10-05, GPS and Galileo) gives ≈ 10 % lower HDOP/VDOP. BeiDou, GLONASS and QZSS were not propagated from real ephemerides (GLONASS needs numerical integration, BeiDou GEO an extra rotation).
- Broadcast-orbit accuracy was checked for GPS only, and the clock part of the SISRE was not checked.
- Dip-equator latitude at Singapore's longitude was inferred from [3], not computed with IGRF.

## Sources
1. O. Montenbruck, P. Steigenberger, A. Hauschild, "Multi-GNSS signal-in-space range error assessment – Methodology and results," *Advances in Space Research* 61(12):3020–3038, 2018 — global RMS SISRE 2017: Galileo 0.2 m, GPS 0.6 m, BeiDou-2 1 m, GLONASS 2 m; clock dominates (via search summary of abstract). https://www.researchgate.net/publication/324402343 (peer-reviewed)
2. "Signal-in-space range error and positioning accuracy of BDS-3," *Scientific Reports* 12, 2022 — BDS-3 MEO SISRE ≈ 0.52 m vs Galileo 0.4, GPS 0.59, GLONASS 2.33 m (via search summary). https://www.nature.com/articles/s41598-022-12012-y (peer-reviewed)
3. S. Andoh, S. Perwitasari, M. Nishioka, T. Naoi, T. Tsugawa, L. T. Thanh, P. Supnithi, "Ionospheric scintillations associated with equatorial plasma bubbles in Southeast Asia during the ascending and maximum phases of Solar Cycle 25," *Earth, Planets and Space* 78:199, 2026 — SEALION stations at the geomagnetic equator, seasonal/local-time/solar/storm dependence. https://link.springer.com/article/10.1186/s40623-026-02527-3 (peer-reviewed, open access)
4. ITU-R Recommendation P.531, *Ionospheric propagation data and prediction methods required for the design of satellite services and systems* — TEC range, group delay, S4 and frequency scaling (via [ionosphere page](../09-propagation-link-budget/ionospheric-hf-propagation.md)). https://www.itu.int/rec/R-REC-P.531/en (standard)
5. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., 2017 — ch. 10–11 (error sources, UERE budgets, DOP, multipath error envelopes). (textbook)
6. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — navigation input filters (min elevation), survey-in. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
7. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — 1.5 m CEP (24 h static, −130 dBm, > 6 SVs per system). https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
8. J. Saastamoinen, "Atmospheric correction for the troposphere and stratosphere in radio ranging of satellites," in *The Use of Artificial Satellites for Geodesy*, AGU Geophys. Monogr. 15, 1972 — zenith hydrostatic and wet delay formulas (as reproduced in Misra & Enge ch. 5 and Teunissen & Montenbruck ch. 6). (peer-reviewed/monograph; formulas cross-checked numerically)
9. P. Misra, P. Enge, *Global Positioning System*, 2nd ed., 2006 — ch. 5 (ionosphere, troposphere, multipath), ch. 6 (DOP). (textbook)
10. *IS-GPS-200* (Navstar GPS Space Segment/Navigation User Interfaces), current revision — Table 20-IV user algorithm for ephemeris, satellite clock and relativistic correction (F constant), μ and Ω̇E values; WGS-84 constants per NGA TR8350.2. https://www.gps.gov/technical/icwg/ (standard)
11. European Union, *Galileo OS SIS ICD*, issue 2.x — §5.1 ephemeris algorithm and constants (μ = 3.986004418×10¹⁴), GST, BGD. https://www.gsc-europa.eu/electronic-library/programme-reference-documents (standard)
12. International GNSS Service: BKG merged broadcast file BRDC00WRD_S_20262780000_01D_MN.rnx and IGS rapid orbit IGS0OPSRAP_20262780000_01D_15M_ORB.SP3 (2026-10-05), https://igs.bkg.bund.de/root_ftp/IGS/ — used in s13_gnss_ephemeris.py. (data product)
13. R. G. Brown, "A baseline GPS RAIM scheme and a note on the equivalence of three RAIM methods," *Navigation (J. ION)* 39(3):301–316, 1992 — least-squares residual, parity and range-comparison RAIM; slope and protection level. (peer-reviewed; cited from general knowledge, equations re-derived and checked by Monte Carlo)
14. B. W. Parkinson, P. Axelrad, "Autonomous GPS integrity monitoring using the pseudorange residual," *Navigation* 35(2):255–274, 1988; RTCA DO-229 (SBAS/RAIM MOPS) for the P_fa/P_md allocations. (peer-reviewed / standard; allocations used as illustration)
