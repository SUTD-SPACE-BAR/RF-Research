---
title: Kalman filtering and state estimation — derivation, Q/R tuning, α-β(-γ) trackers, complementary filters, EKF, UKF, NEES/NIS consistency, baro+IMU rocket fusion and GNSS/INS coupling
domain: 00-math-foundations
slug: kalman-filter-and-state-estimation
tags: [kalman-filter, state-estimation, state-space, process-noise, measurement-noise, riccati, dare, joseph-form, innovation, nees, nis, consistency, dwna, cwna, van-loan, alpha-beta, alpha-beta-gamma, tracking-index, kalata, benedict-bordner, complementary-filter, ekf, ukf, sigma-points, sensor-fusion, barometer, accelerometer, apogee-detection, gnss-ins, loosely-coupled, tightly-coupled, deep-integration]
prerequisites: [estimation-theory-ml-map-crb.md, z-transform-and-discrete-time-systems.md, probability-random-processes-and-psd.md, matrices-and-linear-algebra-for-networks.md]
related:
  - ../11-radar/radar-tracking-monopulse-and-trackers.md
  - ../21-gnss/gnss-receiver-architecture-acquisition-tracking.md
  - ../21-gnss/gnss-on-rockets-dynamics-and-limits.md
  - ../21-gnss/gnss-receiver-integration-u-blox.md
  - ../21-gnss/rtk-ppp-and-corrections.md
  - ../21-gnss/gnss-error-sources-dop.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../10-comms-modulation/synchronization-carrier-timing.md
  - ../20-projects-recipes/ground-station-tracking-yagi.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Kalman filtering and state estimation

## Questions this page answers
- What does a Kalman filter actually do, and where do its equations come from?
- How do I choose the process noise Q and measurement noise R, and what happens if I get them wrong?
- How do I know whether my filter is working (NEES, NIS, innovation tests)?
- What is the Joseph form, and why do flight codes use it?
- Is an α-β filter just a Kalman filter, and how do I pick α and β?
- Is a complementary filter a Kalman filter in disguise?
- How do I fuse a barometer and an accelerometer on a rocket to get velocity and detect apogee?
- EKF or UKF — which should I use for a nonlinear problem (drag, ranges and angles)?
- What is the difference between loosely, tightly and deeply coupled GNSS/INS fusion?
- Why did my filter "lock up" and ignore its measurements, or become noisy and jumpy?

## TL;DR
- **Model:** $\mathbf x_k=\mathbf F\mathbf x_{k-1}+\mathbf B\mathbf u_k+\mathbf w_k$, $\mathbf z_k=\mathbf H\mathbf x_k+\mathbf v_k$, $\mathbf w\sim\mathcal N(0,\mathbf Q)$, $\mathbf v\sim\mathcal N(0,\mathbf R)$. **Predict** $\hat{\mathbf x}^-=\mathbf F\hat{\mathbf x}+\mathbf B\mathbf u$, $\mathbf P^-=\mathbf F\mathbf P\mathbf F^T+\mathbf Q$; **update** $\boldsymbol\nu=\mathbf z-\mathbf H\hat{\mathbf x}^-$, $\mathbf S=\mathbf H\mathbf P^-\mathbf H^T+\mathbf R$, $\mathbf K=\mathbf P^-\mathbf H^T\mathbf S^{-1}$, $\hat{\mathbf x}=\hat{\mathbf x}^-+\mathbf K\boldsymbol\nu$, $\mathbf P=(\mathbf I-\mathbf K\mathbf H)\mathbf P^-(\mathbf I-\mathbf K\mathbf H)^T+\mathbf K\mathbf R\mathbf K^T$ (Joseph form). For linear-Gaussian models this is the exact Bayesian posterior; otherwise it is still the best *linear* estimator.
- **Q sets bandwidth.** Q too small → filter trusts its model, lags manoeuvres, NEES explodes (68.8 vs 2 for Q × 0.01); Q too large → noisy, conservative (NEES 1.04). The **innovation lag-1 correlation** shows which without truth: +0.16 when Q is too small, −0.07 when too large, ≈0 when right (verified).
- **Consistency tests:** NEES $\boldsymbol\epsilon=\tilde{\mathbf x}^T\mathbf P^{-1}\tilde{\mathbf x}\sim\chi^2_n$ (needs truth: simulation); NIS $\boldsymbol\nu^T\mathbf S^{-1}\boldsymbol\nu\sim\chi^2_m$ (works on flight logs). Average over M runs → χ²(nM)/M bands, e.g. [1.878, 2.126] for n = 2, M = 1000. Use ≥ several hundred runs — with M = 100 a correct filter showed 2.21 because errors are correlated in time.
- **α-β = steady-state Kalman** for a constant-velocity target with piecewise-constant white acceleration: tracking index $\lambda=\sigma_wT^2/\sigma_v$, $r=\frac{4+\lambda-\sqrt{8\lambda+\lambda^2}}{4}$, $\alpha=1-r^2$, $\beta=2(2-\alpha)-4\sqrt{1-\alpha}$, $\lambda^2=\beta^2/(1-\alpha)$ (exact vs the Riccati solution). Stable for $0<\alpha<2$, $0<\beta<4-2\alpha$. α-β-γ: with gains $[\alpha,\beta/T,\gamma/2T^2]$, $\gamma=\beta^2/\alpha$.
- **Complementary filter = steady-state Kalman** for baro + accelerometer: baro path low-pass $F(s)$, accelerometer path $1-F(s)$, exactly complementary (sum = 1 to 10⁻¹⁴); $F=\frac{\sqrt2\omega_ns+\omega_n^2}{s^2+\sqrt2\omega_ns+\omega_n^2}$, $\omega_n=(q_a/r_b)^{1/4}$.
- **Rocket worked example** (baro 50 Hz, 0.8 m; accel 100 Hz, 0.3 m/s² + 0.4 m/s² bias): fused velocity error **0.09 m/s rms** vs 6 m/s for differenced baro; apogee time **−2 ms** vs +0.49 s for accelerometer dead reckoning; bias estimated 0.401 ± 0.007 m/s². A **20 ms timestamp error on the baro** drives NEES from 2.9 to 329 — consistency tests find timing bugs.
- **EKF vs UKF** (coast, drag coefficient from baro): both consistent (NEES 2.65/2.82, n = 3), drag constant to 0.3 %, apogee predicted 2 s after burnout to ±3.8 m — for mild nonlinearity they tie; the UKF wins for strong nonlinearity or when Jacobians are painful.
- **GNSS/INS:** loosely coupled = GNSS position/velocity as measurements (simple, needs a full fix); tightly coupled = per-satellite pseudoranges/Doppler (works with < 4 satellites, needs raw data); deep = the INS steers the tracking loops (survives boost jerk).

## Intuition (no math)
A Kalman filter is a disciplined way of mixing **prediction** and **measurement**.

Each tick, the filter first *predicts*: "the rocket was at 300 m going up at 120 m/s, and the accelerometer says it decelerated at 15 m/s², so it should now be at 301.1 m going 119.85 m/s." Along with the prediction it carries an honest statement of its uncertainty, which grows every step because the model and the accelerometer are imperfect (that growth is Q).

Then a *measurement* arrives — the barometer says 300.4 m — with its own uncertainty (R). The filter compares the two. The difference, the **innovation**, is the surprise. It corrects the prediction by a fraction of the surprise. That fraction, the **Kalman gain**, is set by relative confidence: if the prediction is much more certain than the baro, nudge a little; if the baro is much more certain, move most of the way. The uncertainty then shrinks, because two independent pieces of information beat one.

Crucially, a measurement of *position* also corrects *velocity* and even the *accelerometer bias*, because the filter knows how they are linked: if the baro keeps reading below the prediction, the velocity estimate must be too high, which in turn means the accelerometer is reading high. Hidden states get estimated through the model's correlations. That is what makes Kalman filtering more than smoothing.

**Three ways to go wrong.** (1) Lie about Q (pretend the model is perfect): the filter becomes stubborn, ignores measurements and lags real manoeuvres — like a navigator who trusts the dead reckoning over the lighthouse. (2) Lie about R (pretend the sensor is perfect): the estimate jumps around with every noisy reading. (3) Get the *timing* or *model* wrong (stale samples, wrong axis, missing gravity): the filter is confidently wrong. The consistency tests on this page detect all three — they ask "are the surprises as big as the filter itself predicted?"

**Special cases you already know.** Averaging a constant is a Kalman filter with no process noise. An exponential moving average is a one-state Kalman filter frozen at its steady-state gain. A radar's α-β tracker is a two-state one. A complementary filter (low-pass the barometer, high-pass the integrated accelerometer, add) is the steady-state Kalman filter for those two sensors. The general filter adds time-varying gains (fast convergence after start-up and after gaps), multiple sensors at different rates, and an honest uncertainty you can test.

## The math

### Level 1 — the scalar filter

One state $x$ (say altitude), random-walk model $x_k=x_{k-1}+w_k$ (variance $q$ per step), measurement $z_k=x_k+v_k$ (variance $r$).
- Predict: $\hat x^-_k=\hat x_{k-1}$, $P^-_k=P_{k-1}+q$.
- Update: $K_k=\dfrac{P^-_k}{P^-_k+r}$, $\hat x_k=\hat x^-_k+K_k(z_k-\hat x^-_k)$, $P_k=(1-K_k)P^-_k$.

$K$ lies between 0 (ignore the measurement) and 1 (believe it entirely). With $q=0$ the filter computes the running mean of all data ($P=r/N$; verified equal to batch least squares). With $q>0$ the gain settles to a constant α satisfying $\alpha^2/(1-\alpha)=q/r$, i.e. $\alpha=\frac{-\lambda^2+\sqrt{\lambda^4+4\lambda^2}}{2}$ with $\lambda^2=q/r$ — the filter becomes the [exponential moving average](z-transform-and-discrete-time-systems.md) $\hat x_k=\hat x_{k-1}+\alpha(z_k-\hat x_{k-1})$. Q and R thus set the EMA's α from physics instead of by guesswork: $q/r=1$ gives α = 0.618; $q/r=0.01$ gives α = 0.095.

### Level 2 — the linear Kalman filter, derived; noise models; tuning

**State-space model** [1], [2 ch. 5], [3 ch. 5].
$$\mathbf x_k=\mathbf F\mathbf x_{k-1}+\mathbf B\mathbf u_k+\mathbf w_k,\qquad\mathbf z_k=\mathbf H\mathbf x_k+\mathbf v_k,$$
$\mathbf x$ ($n\times1$) state, $\mathbf u$ known input (e.g. measured specific force), $\mathbf z$ ($m\times1$) measurement; $\mathbf w_k\sim\mathcal N(\mathbf0,\mathbf Q)$, $\mathbf v_k\sim\mathcal N(\mathbf0,\mathbf R)$, white, mutually independent and independent of the initial state $\mathbf x_0\sim\mathcal N(\hat{\mathbf x}_0,\mathbf P_0)$. $\mathbf F$ comes from exact discretisation of the continuous dynamics, $\mathbf F=e^{\mathbf AT}$ ([z-transform page](z-transform-and-discrete-time-systems.md)).

**Derivation 1 — Bayesian (exact for linear-Gaussian).** Suppose the posterior at $k-1$ is $\mathcal N(\hat{\mathbf x}_{k-1},\mathbf P_{k-1})$. A linear map of a Gaussian plus independent Gaussian noise is Gaussian, so the *prediction* is $\mathcal N(\mathbf F\hat{\mathbf x}_{k-1}+\mathbf B\mathbf u_k,\ \mathbf F\mathbf P_{k-1}\mathbf F^T+\mathbf Q)$. The measurement likelihood is $\mathcal N(\mathbf z_k;\mathbf H\mathbf x_k,\mathbf R)$. Prior × likelihood is the linear-Gaussian Bayes problem solved on the [estimation page](estimation-theory-ml-map-crb.md): posterior mean $\hat{\mathbf x}^-+\mathbf K(\mathbf z-\mathbf H\hat{\mathbf x}^-)$ with $\mathbf K=\mathbf P^-\mathbf H^T(\mathbf H\mathbf P^-\mathbf H^T+\mathbf R)^{-1}$ and covariance $(\mathbf I-\mathbf K\mathbf H)\mathbf P^-$. By induction the posterior stays Gaussian forever and the filter propagates it exactly — Kalman's result [1] (who derived it via orthogonal projection, which also shows it is the best *linear* filter for non-Gaussian noise with the same second moments).

**Derivation 2 — minimum-variance gain (any linear update).** Take an update $\hat{\mathbf x}=\hat{\mathbf x}^-+\mathbf K(\mathbf z-\mathbf H\hat{\mathbf x}^-)$ with arbitrary $\mathbf K$. The error is $\tilde{\mathbf x}=(\mathbf I-\mathbf K\mathbf H)\tilde{\mathbf x}^--\mathbf K\mathbf v$, so
$$\mathbf P(\mathbf K)=(\mathbf I-\mathbf K\mathbf H)\mathbf P^-(\mathbf I-\mathbf K\mathbf H)^T+\mathbf K\mathbf R\mathbf K^T\qquad(\text{Joseph form, valid for any }\mathbf K).$$
Minimise $\mathrm{tr}\,\mathbf P$: $\partial\,\mathrm{tr}\mathbf P/\partial\mathbf K=-2(\mathbf I-\mathbf K\mathbf H)\mathbf P^-\mathbf H^T+2\mathbf K\mathbf R=0$ ⇒ $\mathbf K(\mathbf H\mathbf P^-\mathbf H^T+\mathbf R)=\mathbf P^-\mathbf H^T$ ⇒ the Kalman gain. Substituting it back collapses Joseph to the short form $(\mathbf I-\mathbf K\mathbf H)\mathbf P^-$ — **but only for the optimal gain**. With a suboptimal gain (a fixed gain, a gated or under-relaxed update, rounding), the short form is wrong: for a test gain the Joseph form matched the Monte-Carlo covariance (16.95 vs 17.00) while the short form was off by > 10 % (verified). Joseph also keeps $\mathbf P$ symmetric positive-definite in float32, which is why flight code uses it.

**The innovation sequence.** $\boldsymbol\nu_k=\mathbf z_k-\mathbf H\hat{\mathbf x}^-_k$ has covariance $\mathbf S_k=\mathbf H\mathbf P^-_k\mathbf H^T+\mathbf R$ and, for a correct filter, is **white** — each surprise is unpredictable from the past (otherwise the filter would have used that predictability). Whiteness and the size of ν relative to S are the basis of every real-data health check.

**Riccati recursion and steady state.** Eliminating $\mathbf K$, $\mathbf P^-_{k+1}=\mathbf F\big[\mathbf P^-_k-\mathbf P^-_k\mathbf H^T(\mathbf H\mathbf P^-_k\mathbf H^T+\mathbf R)^{-1}\mathbf H\mathbf P^-_k\big]\mathbf F^T+\mathbf Q$ — independent of the data, so gains can be precomputed. For time-invariant, detectable and stabilisable models it converges to the solution of the **discrete algebraic Riccati equation** (`scipy.linalg.solve_discrete_are`), giving a constant gain: the fixed-gain filters below. The closed-loop error dynamics $(\mathbf I-\mathbf K\mathbf H)\mathbf F$ have all eigenvalues inside the unit circle.

**Process-noise models for kinematics** [2 §6.2–6.3]. For a constant-velocity (CV) state $[p,v]$ with sample period $T$:
- *DWNA* (discrete white-noise acceleration — piecewise-constant acceleration $w$ of variance $\sigma_w^2$ over each interval): $\boldsymbol\Gamma=[T^2/2,\ T]^T$, $\mathbf Q=\boldsymbol\Gamma\boldsymbol\Gamma^T\sigma_w^2=\sigma_w^2\begin{pmatrix}T^4/4&T^3/2\\T^3/2&T^2\end{pmatrix}$.
- *CWNA* (continuous white-noise acceleration, PSD $\tilde q$ m²/s³): $\mathbf Q=\tilde q\begin{pmatrix}T^3/3&T^2/2\\T^2/2&T\end{pmatrix}$, the exact integral $\int_0^Te^{\mathbf A\tau}\mathbf L\tilde q\mathbf L^Te^{\mathbf A^T\tau}d\tau$ (reproduced by Van Loan's matrix-exponential method [9] to 10⁻¹⁸).
- They are *not* interchangeable: with $\sigma_w^2=\tilde q/T$ the velocity terms agree but the position term differs by 3/4 (verified). Use DWNA if your α-β design rules (Kalata) are DWNA-based; CWNA if you start from a sensor noise density.
- Constant-acceleration (CA) analogues add a third state; the "DWPA" model drives the acceleration *increment* with $\boldsymbol\Gamma=[T^2/2,\ T,\ 1]^T$.

**Choosing Q and R (tuning).**
- **R from the sensor**: log the sensor at rest (on the pad, on the bench) and use the measured variance at the filter's sample rate; check the noise is white (autocorrelation, Allan deviation) — if not, it needs its own state (e.g. a first-order Gauss–Markov bias).
- **Q from physics**: for a DWNA tracker, a common starting rule is $\tfrac12a_{\max}\le\sigma_w\le a_{\max}$, with $a_{\max}$ the largest unmodelled acceleration [2]. When an accelerometer drives the prediction (as an input), the process noise *is* the accelerometer noise: $\mathbf Q=\mathbf B\mathbf B^T\sigma_a^2$ plus small bias random-walk terms.
- **What mis-tuning looks like** (CV tracker, $T$ = 0.1 s, σ_w = 2 m/s², σ_v = 5 m, M = 1000 runs; verified):

| Filter Q | avg NEES (n = 2) | avg NIS (m = 1) | innovation lag-1 corr. | Behaviour |
|---|---|---|---|---|
| correct | 2.02 | 1.003 | −0.002 | consistent |
| ×0.01 | 68.8 | 1.29 | **+0.156** | stubborn, lags, overconfident |
| ×100 | 1.04 | 0.93 | **−0.068** | jumpy, conservative |

NIS alone barely moves (1.29, 0.93) because S absorbs part of the error, but the **sign of the innovation autocorrelation** flags the direction of mis-tuning on real data.

**Multi-rate sensors and gaps.** Predict at the fastest rate (the IMU); update whenever a measurement arrives (baro at 50 Hz, GNSS at 5–10 Hz) — sequential updates with the correct timestamps. Missing data is free: just predict (P grows). Out-of-sequence or late measurements must be applied at their true time (buffer and re-propagate, or augment the state); applying a 20 ms-old baro sample "now" is a model error the NEES test catches (worked example).

### Level 3 — fixed-gain trackers, complementary filters, nonlinear filters, consistency, GNSS/INS

**α-β and α-β-γ filters as steady-state Kalman filters** [2 §6.5], [4], [5]. The α-β tracker is
$$\hat p^-=\hat p+T\hat v,\quad\hat v^-=\hat v;\qquad\hat p=\hat p^-+\alpha\,\nu,\quad\hat v=\hat v^-+\frac{\beta}{T}\nu,\qquad\nu=z-\hat p^-,$$
a CV Kalman filter with frozen gain $\mathbf K=[\alpha,\ \beta/T]^T$. For the DWNA model with position measurements, the DARE solution depends on a single number, Kalata's **tracking index** $\lambda=\sigma_wT^2/\sigma_v$ (manoeuvre displacement per step over measurement noise), and is given in closed form by
$$r=\frac{4+\lambda-\sqrt{8\lambda+\lambda^2}}{4},\qquad\alpha=1-r^2,\qquad\beta=2(2-\alpha)-4\sqrt{1-\alpha},\qquad\lambda^2=\frac{\beta^2}{1-\alpha}.$$
Verified against `solve_discrete_are` to 10⁻⁸ for λ = 0.05, 0.5, 2 (α = 0.271, 0.628, 0.854; β = 0.043, 0.305, 0.764). The older **Benedict–Bordner** relation $\beta=\alpha^2/(2-\alpha)$ [5] comes from a different criterion (trading noise variance against the transient error to a ramp) and gives a slightly smaller β (0.288 vs 0.305 at α = 0.628). *Stability*: the error dynamics have characteristic polynomial $z^2-(2-\alpha-\beta)z+(1-\alpha)$, so by the [stability triangle](z-transform-and-discrete-time-systems.md) the filter is stable iff $0<\alpha<2$ and $0<\beta<4-2\alpha$ (checked against eigenvalues); the often-quoted "0 < α < 1, 0 < β ≤ 2" is a conservative design range, not the stability limit. **α-filter** convention trap: for the one-state random-walk model, $\alpha^2/(1-\alpha)=q/r$; the published form $\alpha=(-\Lambda^2+\sqrt{\Lambda^4+16\Lambda^2})/8$ uses $\Lambda=\sigma_wT^2/\sigma_v$ with a per-step position std of $\sigma_wT^2/2$ ($\Lambda^2=4q/r$) — both verified, and they agree only with the right definitions.

**α-β-γ** (CA model, DWPA noise, gains $[\alpha,\ \beta/T,\ \gamma/2T^2]$): the steady-state Kalman gains satisfy $\gamma=\beta^2/\alpha$ and $\lambda^2=\gamma^2/(4(1-\alpha))$ (verified; λ = 0.1 → α, β, γ = 0.605, 0.276, 0.126; λ = 1 → 0.864, 0.798, 0.737). Some texts write the third gain as $\gamma'/T^2$, in which case $\gamma'=\beta^2/2\alpha$ — check the convention before copying gains. Radar use of these trackers (track-while-scan, gating, initiation) is on the [radar tracking page](../11-radar/radar-tracking-monopulse-and-trackers.md).

**Complementary filter as a special case** [6]. Two sensors see the same quantity with complementary error spectra: a barometer (altitude $h+n_b$, noise broadband but no drift) and an accelerometer ($\ddot h+n_a$, whose double integral drifts at low frequency but is clean at high frequency). For any filter $F(s)$,
$$\hat h=F(s)\,(h+n_b)+\big(1-F(s)\big)\,\frac{\ddot h+n_a}{s^2}=h+F(s)\,n_b+\frac{1-F(s)}{s^2}\,n_a ,$$
so the signal passes undistorted whatever $F$ is — only the noises are shaped: choose $F$ low-pass so baro noise is cut at high frequency and the accelerometer's integrated noise and bias are cut at low frequency. The steady-state Kalman filter for state $[h,v]$ with the accelerometer as input and the baro as measurement is exactly such a filter: in continuous time,
$$F(s)=\frac{\sqrt2\,\omega_ns+\omega_n^2}{s^2+\sqrt2\,\omega_ns+\omega_n^2},\qquad\omega_n=\Big(\frac{q_a}{r_b}\Big)^{1/4},$$
with $q_a$ the accelerometer noise PSD (m²/s³) and $r_b$ the baro noise PSD (m²·s), i.e. ζ = 1/√2 and gains $K_1\approx\sqrt2\,\omega_nT$, $K_2\approx\omega_n^2T$. Verified in discrete time (T = 10 ms, σ_a = 0.1 m/s², σ_b = 0.5 m): DARE gains [0.00630, 0.00199] vs continuous-limit [0.00632, 0.00200]; with noiseless consistent inputs the filter reproduces truth to 3×10⁻¹⁴; $H_{baro}+H_{acc}/D_{int}=1$ to 9×10⁻¹⁵ (the discrete complementary identity); and the two paths have equal magnitude at $\omega_n\sqrt{1+\sqrt2}$ = 0.111 Hz. What the Kalman version adds: optimal $\omega_n$ from the noise levels, time-varying gain after start-up, extra states (accelerometer bias), multi-rate handling and a covariance. The same structure underlies gyro + accelerometer/magnetometer attitude complementary filters (gyro high-pass, gravity/field reference low-pass).

**Extended Kalman filter (EKF)** [2 ch. 10], [3 ch. 13]. Nonlinear $\mathbf x_k=\mathbf f(\mathbf x_{k-1},\mathbf u_k)+\mathbf w$, $\mathbf z_k=\mathbf h(\mathbf x_k)+\mathbf v$. Propagate the estimate through the true nonlinear functions, and the covariance through their Jacobians $\mathbf F_k=\partial\mathbf f/\partial\mathbf x|_{\hat{\mathbf x}_{k-1}}$, $\mathbf H_k=\partial\mathbf h/\partial\mathbf x|_{\hat{\mathbf x}^-_k}$. It is first-order accurate: when the nonlinearity is significant over the width of the uncertainty (large initial errors, range–bearing measurements of nearby targets, strong drag nonlinearity), the EKF's covariance is too small and it can diverge. Remedies: iterate the update (IEKF), add stabilising Q, use an **error-state** formulation (estimate small errors of a nominal trajectory computed by a high-rate integrator — the standard INS approach, where the error dynamics are nearly linear), or use the UKF.

**Unscented Kalman filter (UKF)** [7], [8]. Instead of linearising, pass $2n+1$ deterministically chosen **sigma points** $\boldsymbol{\mathcal X}_0=\hat{\mathbf x}$, $\boldsymbol{\mathcal X}_{\pm i}=\hat{\mathbf x}\pm\big(\sqrt{(n+\lambda_u)\mathbf P}\big)_i$ through the nonlinear function and recompute the mean and covariance as weighted sums ($W_0^{(m)}=\lambda_u/(n+\lambda_u)$, $W_i=1/2(n+\lambda_u)$, $\lambda_u=\alpha_u^2(n+\kappa)-n$, with an extra $(1-\alpha_u^2+\beta_u)$ on $W_0^{(c)}$; $\beta_u=2$ is optimal for Gaussians). The measurement update uses the sigma-point cross-covariance $\mathbf P_{xz}$: $\mathbf K=\mathbf P_{xz}\mathbf S^{-1}$. It captures the mean and covariance correctly to second order for any nonlinearity, needs no Jacobians, and costs ~$2n+1$ function evaluations per step. **Worked comparison** (coast after burnout, state $[h,v,k]$ with drag $\dot v=-g-kv|v|$, baro only; 30 MC runs): drag constant error at apogee 3.6×10⁻⁶ (EKF) and 3.8×10⁻⁶ (UKF) on $k$ = 1.2×10⁻³ m⁻¹; NEES 2.65 and 2.82 (n = 3); apogee predicted 2 s after burnout by $h+\ln(1+kv^2/g)/2k$ to +0.34 ± 3.81 m and −0.10 ± 3.80 m. A tie, as expected for this smooth problem; the UKF's advantage appears with larger nonlinearity (bearing-only tracking, large attitude errors). (With a larger Q the same filters were *conservative*, NEES 1.46 — Q is a modelling statement, not a free safety margin.)

**Consistency testing: NEES and NIS** [2 §5.4], [10]. A filter is *consistent* if its errors are zero-mean and match its covariance.
- **NEES** (needs truth → simulation): $\epsilon_k=\tilde{\mathbf x}_k^T\mathbf P_k^{-1}\tilde{\mathbf x}_k\sim\chi^2_n$. Over M independent runs, $\bar\epsilon_k=\frac1M\sum\epsilon_k$ satisfies $M\bar\epsilon_k\sim\chi^2_{nM}$: two-sided 95 % band $[\chi^2_{nM}(0.025),\chi^2_{nM}(0.975)]/M$ — [1.878, 2.126] for n = 2, M = 1000; [2.29, 3.81] for n = 3, M = 40.
- **NIS** (works on real logs): $\boldsymbol\nu_k^T\mathbf S_k^{-1}\boldsymbol\nu_k\sim\chi^2_m$; for a single run, the time average over K steps has $K\bar\epsilon\sim\chi^2_{mK}$ (96.2 % of single runs fell inside their 95 % band — verified).
- **Whiteness**: normalised innovation autocorrelation at lag $\ell\ne0$ should be within $\pm1.96/\sqrt K$.
- **Interpretation**: NEES/NIS high → overconfident (Q or R too small, unmodelled dynamics, *wrong timestamps*, wrong frame/sign); low → conservative (inflated noise); time structure (bursts at burnout, transonic) → model fails in a phase. Passing χ² tests is necessary, not sufficient — a filter can be consistent and still poorly tuned [10].
- **Statistics need many runs.** NEES samples are strongly correlated in time; a correct filter gave a run-averaged NEES of 2.21 with M = 100 but 2.02 with M = 1000. Use fixed seeds and hundreds of runs, as in the team's estimator-validation suites (truth from a different model, sensors at exactly the R the filter claims).

**GNSS/INS integration architectures** [11 ch. 14], [12]. An INS integrates gyro rates (attitude) and accelerometer specific force (velocity, position) at high rate; its errors grow without bound (bias → velocity error ∝ t, position ∝ t²; tilt error couples gravity into horizontal acceleration). GNSS has bounded but noisy, low-rate errors and drops out (high dynamics, [rocket limits](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)). Fusion uses an error-state EKF with typically 15 states (3 position, 3 velocity, 3 attitude errors, 3 accelerometer biases, 3 gyro biases), plus 2 clock states when coupling tightly.

| Architecture | GNSS input to the filter | Pros | Cons |
|---|---|---|---|
| **Loosely coupled** | receiver's position/velocity solution (PVT) | simple; any receiver; small filter | needs ≥ 4 satellites; the receiver's own Kalman filter makes the PVT errors time-correlated (violates "white R") — inflate R or decimate; tuned by the receiver's dynamic model ([u-blox integration](../21-gnss/gnss-receiver-integration-u-blox.md)) |
| **Tightly coupled** | per-satellite pseudorange and Doppler (pseudorange-rate) | uses 1–3 satellites; per-satellite fault detection by NIS gating; better geometry handling | needs raw measurements (e.g. u-blox UBX-RXM-RAWX on the ZED-F9P), ephemeris, clock states; more code |
| **Deep / ultra-tight (vector tracking)** | correlator outputs; the INS predicts code and carrier for the tracking loops | narrower loops survive jerk and low C/N₀; fastest reacquisition | needs receiver-internal access (SDR or special firmware) |

Practical items common to all: lever arm between IMU and antenna; time synchronisation (PPS/timepulse, [GNSS timing](../21-gnss/gnss-timing-1pps.md)); latency compensation; using carrier-phase/RTK only when the fix is valid ([RTK](../21-gnss/rtk-ppp-and-corrections.md)); and quality-weighting R by the receiver's reported accuracy.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\mathbf K=\mathbf P^-\mathbf H^T(\mathbf H\mathbf P^-\mathbf H^T+\mathbf R)^{-1}$ | linear(ised) update | |
| Joseph $\mathbf P=(\mathbf I-\mathbf K\mathbf H)\mathbf P^-(\mathbf I-\mathbf K\mathbf H)^T+\mathbf K\mathbf R\mathbf K^T$ | any gain | always in flight code |
| scalar steady gain $\alpha^2/(1-\alpha)=q/r$ | random walk + direct measurement | q/r = 0.01 → α = 0.095 |
| DWNA $\mathbf Q=\sigma_w^2\begin{psmallmatrix}T^4/4&T^3/2\\T^3/2&T^2\end{psmallmatrix}$ | CV tracker | $\tfrac12a_{\max}\le\sigma_w\le a_{\max}$ |
| CWNA $\mathbf Q=\tilde q\begin{psmallmatrix}T^3/3&T^2/2\\T^2/2&T\end{psmallmatrix}$ | from a noise PSD | |
| $\lambda=\sigma_wT^2/\sigma_v$; α, β from Kalata | α-β (DWNA) | λ = 0.5 → α 0.628, β 0.305 |
| stable: $0<\alpha<2$, $0<\beta<4-2\alpha$ | α-β | |
| $\gamma=\beta^2/\alpha$ (gains $\alpha,\beta/T,\gamma/2T^2$) | α-β-γ (DWPA) | λ = 1 → 0.864, 0.798, 0.737 |
| complementary: $\omega_n=(q_a/r_b)^{1/4}$, ζ = 0.707 | baro + accel | 0.1 m/s², 0.5 m @ 100 Hz → 0.071 Hz; 150 µg/√Hz, 0.5 m → 0.023 Hz |
| NEES band $\chi^2_{nM}(0.025..0.975)/M$ | M MC runs | n 2, M 1000: [1.88, 2.13] |
| NIS band (single run) $\chi^2_{mK}(\cdot)/K$ | K steps | |
| bias-only dead-reckoning apogee error ≈ $b\,t_{apo}/g$ | vertical flight | 0.4 m/s², 11.4 s → 0.47 s |
| α-β lag to constant accel: $aT^2/\beta$ (predicted), $(1-\alpha)aT^2/\beta$ (filtered) | CV α-β | λ 0.004, 4 m/s² → 10.5 / 9.6 m |

## Worked examples

**1. 1-D rocket altitude/velocity estimator fusing barometer and accelerometer** (`est_kalman.py` §7).
*Truth:* net 60 m/s² for 2.5 s, then coast with quadratic drag ($\dot v=-g-kv|v|$, $k$ = 0.0012 m⁻¹) → burnout at 130.9 m/s, apogee 646.0 m at $t$ = 11.409 s. *Sensors:* accelerometer at 100 Hz reporting specific force $f=a+g$ with σ = 0.3 m/s² and a 0.4 m/s² bias (sampled as average acceleration per interval, like an IMU delta-velocity output); barometric altitude at 50 Hz, σ = 0.8 m.
*Filter:* state $\mathbf x=[h,v,b]^T$ (b = accelerometer bias), input $u=f_{meas}-g$,
$$\mathbf F=\begin{pmatrix}1&T&-T^2/2\\0&1&-T\\0&0&1\end{pmatrix},\quad\mathbf B=\begin{pmatrix}T^2/2\\T\\0\end{pmatrix},\quad\mathbf H=(1\ 0\ 0),\quad\mathbf Q=\mathbf B\mathbf B^T\sigma_a^2+\mathrm{diag}(0,0,q_bT),\quad R=\sigma_b^2,$$
predict at 100 Hz, update on every second step (baro), Joseph form.
*Results (one run; consistency over 40):*

| Estimator | velocity rms error | apogee-time error |
|---|---|---|
| Kalman (baro + accel + bias state) | **0.089 m/s** | **−2 ms** |
| Baro EMA (α = 0.1) then differentiate | 6.0 m/s | −980 ms (a noise zero-crossing) |
| Accelerometer dead reckoning (no bias state) | 4.6 m/s at apogee | +492 ms (≈ $bt/g$ = 465 ms) |

Bias estimated as 0.401 ± 0.007 m/s² — the baro makes the bias observable through the $-T$ coupling in $\mathbf F$. Run-averaged NEES = 2.94 (band [2.29, 3.81] for n = 3, M = 40): consistent. Two deliberate faults: point-sampled instead of interval-averaged acceleration → NEES 3.22 (still acceptable at 100 Hz); **baro samples 20 ms stale** (a timestamp bug) → NEES **329**. (A first draft of this simulation had NEES ≈ 28 because of a predict/update indexing slip — found exactly by this test.) Practical additions for a real flight computer: zero-velocity updates on the pad (h, v known) to converge the bias before launch; inflate R or gate the baro by NIS through transonic flight and at ejection (pressure spikes); detect apogee from $\hat v$ crossing zero with a covariance-aware margin rather than from raw baro.

**2. Choosing α-β gains for a 10 Hz ground-station position tracker.** Measured position noise σ_v = 5 m (e.g. telemetry-reported GNSS fixes), worst-case unmodelled acceleration 4 m/s² → σ_w ≈ 2–4 m/s². With σ_w = 2: λ = 2 × 0.1²/5 = 0.004 → $r=(4.004-\sqrt{0.032016})/4=0.9563$, **α = 0.0856, β = 0.00382** (β/T = 0.0382 s⁻¹). Noise reduction is large but the filter is slow: a sustained 4 m/s² acceleration produces a steady-state lag of $aT^2/\beta$ = **10.5 m** in the one-step prediction and $(1-\alpha)aT^2/\beta$ = **9.6 m** in the filtered position (both verified by simulation). Doubling σ_w (λ = 0.008) roughly halves the lag at the cost of more noise. That trade is the whole of α-β design; antenna-pointing use is on the [radar tracking page](../11-radar/radar-tracking-monopulse-and-trackers.md).

**3. Complementary filter design from datasheet numbers.** Convert both sensors to continuous-time noise densities consistent with the sampled model ($q=\sigma^2T$ for white noise of per-sample variance σ² at period T). Accelerometer noise density 150 µg/√Hz (one-sided) = 1.47×10⁻³ m/s²/√Hz; sampled with bandwidth $f_s/2$ its variance is ASD²·f_s/2, so $q_a$ = ASD²/2 = 1.08×10⁻⁶ m²/s³. Baro altitude noise 0.5 m rms at 100 Hz: $r_b=\sigma_b^2T$ = 2.5×10⁻³ m²·s. Then $\omega_n=(q_a/r_b)^{1/4}$ = **0.144 rad/s (0.023 Hz)**: below ~0.02 Hz trust the baro, above it the integrated accelerometer (verified). In practice accelerometer *bias* and vibration (not white noise) dominate, so either add a bias state (example 1) or raise $\omega_n$ — a datasheet-only design is a starting point.

**4. Steady-state Riccati vs Kalata check (by hand).** λ = 0.5: $\sqrt{8(0.5)+0.25}=2.0616$, $r=(4.5-2.0616)/4=0.6096$, α = 1 − 0.3716 = 0.6284, β = 2(1.3716) − 4(0.6096) = 0.3048; $\beta^2/(1-\alpha)=0.0929/0.3716=0.250=\lambda^2$ ✓ (DARE agrees to 10⁻⁸).

## Practical notes
- **Write the model before the code**: states, units, frames (ENU/NED, body/world), signs (specific force includes +g at rest), timestamps. Most "Kalman tuning" problems are model or timing errors. Assert something physical (e.g. positive specific force on the rail).
- **Run the real filter code in simulation with Monte-Carlo NEES before flight**, with truth from a different (richer) model than the filter's; then run NIS and innovation-whiteness on every bench and flight log.
- **Numerics**: use Joseph form; symmetrise P; consider float64 on the host and check float32 on the target; bound P from below to keep the filter alive after long quiet periods; square-root or UD factorised filters if P becomes ill-conditioned.
- **Gating**: reject measurements with NIS above a χ² threshold (e.g. 99.7 % → 9.0 for m = 1) — protects against baro spikes, GNSS multipath jumps and radar clutter, but log every rejection and avoid locking out a correct sensor after a model error (re-initialise if rejections persist).
- **Initialisation**: set $\hat{\mathbf x}_0$ from the first measurements (two-point initialisation for position/velocity) and a P₀ that honestly covers the initial error; a P₀ that is too small makes the first seconds inconsistent.
- **Observability**: a state the measurements cannot see (accelerometer bias with no baro/GNSS; heading with no magnetometer or manoeuvre) has P that never shrinks; check $\mathrm{rank}[\mathbf H;\mathbf H\mathbf F;\dots]$ or watch P.
- **Compute budget**: an n-state filter costs O(n³) per update; 3–9 states at 100–1000 Hz is trivial for a Teensy 4.1 / ESP32-S3; a 15–17-state error-state GNSS/INS EKF at 100 Hz prediction and 5–10 Hz update is also fine.

## Common mistakes & misconceptions
1. **"Q is a tuning knob with no meaning."** It is the variance of what the model leaves out; tune from physics and verify with NEES/NIS, not by eye.
2. **Using the short covariance update with a non-optimal gain** (fixed gains, gated or scaled updates) — use Joseph.
3. **Wrong time alignment** — applying a delayed measurement at the wrong instant; the NEES jumped 2.9 → 329 for 20 ms at 130 m/s.
4. **Forgetting gravity or its sign** in the accelerometer input (specific force reads +1 g on the pad).
5. **Treating GNSS PVT errors as white** in a loosely coupled filter — they are filtered and correlated; inflate R or use pseudoranges.
6. **Believing the EKF covariance after a large initial error** — linearisation makes it overconfident; use larger P₀/Q early, an IEKF/UKF, or an error-state formulation.
7. **Testing consistency with too few runs** — M = 100 was not enough to confirm a correct filter here.
8. **Copying α-β-γ gains or α-filter formulas across texts** — gain and tracking-index conventions differ by factors of 2 (this page states its convention and verifies it).
9. **Assuming a complementary filter is inferior** — for two sensors with white noise it is the steady-state Kalman filter; the Kalman filter's advantages are start-up, biases, multi-rate and a covariance.
10. **Gating so hard that a real manoeuvre is rejected** — the filter then coasts on a wrong model and never recovers; combine gating with manoeuvre detection or multiple models (IMM).

## How to simulate / verify
- `python3 tools/verify/est_kalman.py` (≈ 10 s, **ALL PASS**): (1) KF = batch LS; (2) CV/DWNA tracker NEES/NIS/whiteness with M = 1000 vectorised runs and the mis-tuned cases; (3) Joseph vs short form for a suboptimal gain; (4) DARE vs Kalata α-β, α-filter conventions, stability triangle, α-β-γ relations; (5) CWNA = Van Loan, DWNA vs CWNA; (6) complementary-filter identity, gains and crossover; (7) 1-D rocket baro + accelerometer + bias filter vs baro-only and dead reckoning, apogee timing, NEES with deliberate faults; (8) EKF vs UKF drag-coefficient estimation and apogee prediction; (9) worked-example numbers (α-β lag, datasheet complementary design).
- Tools: `scipy.linalg.solve_discrete_are` (steady-state gains), `scipy.signal.cont2discrete` (F and, via Van Loan, Q), `filterpy` (KF/EKF/UKF reference implementations), `scipy.stats.chi2.ppf` for bands.
- Validation recipe: fixed-seed Monte-Carlo with truth from a higher-fidelity simulator (e.g. a 6-DOF or RocketPy trajectory), synthetic sensors at exactly the filter's R, then deliberate faults (dropouts, stale timestamps, clipping, bias steps) as matched pairs.

## Open questions / gaps
- Interacting multiple-model (IMM) filters for boost/coast/descent phase switching and manoeuvring targets are only mentioned; no simulation.
- Attitude estimation (quaternion error-state EKF, gyro + magnetometer + gravity) is outlined only via the complementary-filter analogy; a dedicated page would be needed.
- The tightly-coupled GNSS/INS description is architectural; no pseudorange-level simulation in the KB yet, and which raw-measurement messages the MAX-M10S exposes was not checked.
- Smoothers (RTS) for post-flight reconstruction are not covered.

## Sources
1. R. E. Kalman, "A new approach to linear filtering and prediction problems," *Trans. ASME J. Basic Eng.* 82(1):35–45 (1960), doi:10.1115/1.3662552. http://eceweb1.rutgers.edu/~gajic/pdffiles/519KalmanFiltering/kalman1960.pdf (peer-reviewed; located)
2. Y. Bar-Shalom, X. R. Li, T. Kirubarajan, *Estimation with Applications to Tracking and Navigation*, Wiley (2001): ch. 5 (linear KF, innovations, consistency tests NEES/NIS §5.4), ch. 6 (DWNA/CWNA/DWPA motion models, α-β and α-β-γ filters, tracking index, σ_w rule of thumb), ch. 10 (EKF). (textbook; section numbers recalled)
3. D. Simon, *Optimal State Estimation: Kalman, H∞, and Nonlinear Approaches*, Wiley (2006): ch. 5 (discrete KF, Joseph form, steady state), ch. 13 (EKF), ch. 14 (UKF). (textbook; recalled)
4. P. R. Kalata, "The tracking index: a generalized parameter for α-β and α-β-γ target trackers," *IEEE Trans. AES* 20(2):174–182 (1984). (peer-reviewed; closed forms cross-checked via the Wikipedia "Alpha beta filter" summary and verified against the Riccati solution here)
5. T. R. Benedict, G. W. Bordner, "Synthesis of an optimal set of radar track-while-scan smoothing equations," *IRE Trans. Automatic Control* 7(4):27–32 (1962). (peer-reviewed; relation β = α²/(2−α) compared numerically)
6. W. T. Higgins, "A comparison of complementary and Kalman filtering," *IEEE Trans. AES* 11(3):321–325 (1975), doi:10.1109/TAES.1975.308081 — tutorial showing complementary filters' relation to Wiener/Kalman filters. (peer-reviewed; abstract read; equivalence verified numerically here)
7. S. J. Julier, J. K. Uhlmann, "Unscented filtering and nonlinear estimation," *Proc. IEEE* 92(3):401–422 (2004). (peer-reviewed; recalled)
8. E. A. Wan, R. van der Merwe, "The unscented Kalman filter for nonlinear estimation," *Proc. IEEE AS-SPCC* (2000) — scaled sigma points (α, β, κ). (peer-reviewed; recalled)
9. C. F. Van Loan, "Computing integrals involving the matrix exponential," *IEEE Trans. Autom. Control* 23(3):395–404 (1978) — discretisation of Q. (peer-reviewed; recalled; method reproduced numerically)
10. Z. Chen, C. Heckman, S. Julier, N. Ahmed, "Weak in the NEES?: Auto-tuning Kalman filters with Bayesian optimization," arXiv:1807.08855 (2018) — NEES/NIS as χ² tests and their limits for tuning. https://arxiv.org/abs/1807.08855 (peer-reviewed conference paper; search summary)
11. P. D. Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*, 2nd ed., Artech House (2013): ch. 3 (Kalman-filter-based estimation), ch. 14 (INS/GNSS integration: loosely, tightly, deep coupling; error-state formulation). (textbook; chapter numbers recalled)
12. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., Artech House (2017), ch. 11 (navigation filtering) and ch. 13 (GNSS/INS integration) — per the KB curriculum check rows (D4). (textbook; not re-read)
13. Space Bar avionics methods notes (internal): estimator validation with truth from a different vehicle, deterministic seeds, sensor σ equal to the filter's R, matched-pair fault cases. (internal practice note)
