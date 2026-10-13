#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~530 s (8.8 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress.
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""
array_steering.py — verification for kb/12-phased-arrays/beam-steering-grating-lobes.md

Checks:
  1. Grating-lobe positions u_g = u0 + m*lambda/d; onset scan angle for peak at horizon (d = lambda/(1+|sin th0|))
     and for the grating lobe's near-side null at the horizon (d = lambda(1-1/N)/(1+|sin th0|)).
  2. Beam broadening with scan (numeric vs 1/cos th0) — reuses array_factor HPBW logic.
  3. Scan loss: ideal projected aperture cos(th0) and cos^n element patterns.
  4. Beam squint with phase shifters: numeric beam peak vs sin th = (f0/f) sin th0, small-signal -(df/f0) tan th0.
  5. Instantaneous bandwidth: gain loss at band edge vs fractional bandwidth; closed-form criterion
     B/f0 = K * Theta3_broadside / sin th0 with the loss that corresponds to K.
  6. True time delay: no squint; subarray TTD + element phase shifters -> squint of the subarray pattern -> lobes.
  7. Phase quantisation: rms error LSB/sqrt(12), gain loss ~ sigma^2, peak quantisation lobe vs bits
     (worst case over steering angle) for (a) N=100 Hamming taper (ADI's case) and (b) N=8 and 32 uniform;
     compare with 1/2^(2P) (classic periodic-error bound) and ADI's "-7.5 dB at 2 bits, -6 dB/bit".
     Phase randomisation (dither) effect on peak lobe.
  8. Beam pointing resolution with a P-bit phase shifter vs ADI's theta_RES = asin(Phi_LSB/(N pi)).
  9. Random phase error -> beam pointing error sigma_u (least-squares slope) Monte Carlo vs formula.
 10. Worked-example numbers (8-el 5.8 GHz, 2.4 GHz ground station, 10.25 GHz Phaser).
Conventions: theta from broadside, u = sin(theta), lambda=1 unless stated, e^{+j w t}.
"""
import numpy as np
from scipy.optimize import brentq, minimize_scalar

rng = np.random.default_rng(7)
c0 = 299792458.0


def af(w, x, u, k=2 * np.pi):
    return np.exp(1j * k * np.outer(u, x)) @ w


def steer(x, u0, k=2 * np.pi):
    return np.exp(-1j * k * x * u0)


def hpbw_deg(N, d, th0_deg, amp=None, n=200001):
    x = np.arange(N) * d
    a = np.ones(N) if amp is None else amp
    w = a * steer(x, np.sin(np.radians(th0_deg)))
    th = np.linspace(-np.pi / 2, np.pi / 2, n)
    P = np.abs(af(w, x, np.sin(th))) ** 2
    P /= P.max()
    i0 = np.argmax(P)
    ir = i0
    while ir < n - 1 and P[ir] > 0.5:
        ir += 1
    il = i0
    while il > 0 and P[il] > 0.5:
        il -= 1
    return np.degrees(th[ir] - th[il])


print("=" * 78)
print("1. Grating lobes")
for d in (0.5, 0.6, 0.7, 0.8, 1.0):
    th_peak = np.degrees(np.arcsin(min(1, 1 / d - 1))) if 1 / d - 1 <= 1 else 90
    print(f"  d={d:.1f}λ: grating-lobe PEAK reaches horizon when |sinθ0| = λ/d - 1 = {1/d-1:+.3f} -> θ0,max = {th_peak:5.1f}°")
for N in (8, 16, 64):
    for th in (30, 45, 60):
        d1 = 1 / (1 + np.sin(np.radians(th)))
        d2 = (1 - 1 / N) / (1 + np.sin(np.radians(th)))
        print(f"  N={N:2d}, scan ±{th}°: d_max(peak at horizon) = {d1:.3f}λ ; d_max(null at horizon) = {d2:.3f}λ")
# numeric check: N=16, d=0.6, scan 41.8° -> grating lobe peak at u=-1
N, d = 16, 0.6
th0 = np.arcsin(1 / d - 1)
x = np.arange(N) * d
u = np.linspace(-1, 1, 40001)
P = np.abs(af(steer(x, np.sin(th0)), x, u)) / N
print(f"  numeric: N=16 d=0.6λ θ0={np.degrees(th0):.1f}°: |AF| at u=-1 = {P[0]:.3f} (1 = full grating lobe)")

print("=" * 78)
print("2. Beam broadening with scan (uniform)")
for N in (8, 16, 32):
    row = []
    for th in (0, 30, 45, 60):
        h = hpbw_deg(N, 0.5, th)
        row.append(f"{th}°:{h:6.2f} (x{h/hpbw_deg(N,0.5,0):.3f} vs 1/cos {1/np.cos(np.radians(th)):.3f})")
    print(f"  N={N:2d}: " + "  ".join(row))

print("=" * 78)
print("3. Scan loss (dB) relative to broadside")
for th in (15, 30, 45, 60, 70):
    c = np.cos(np.radians(th))
    print(f"  θ0={th:2d}°: cosθ {10*np.log10(c):6.2f}  cos^1.2 {12*np.log10(c):6.2f}  cos^1.5 {15*np.log10(c):6.2f}  cos^2 {20*np.log10(c):6.2f}")

print("=" * 78)
print("4. Beam squint with phase shifters (N=32, d=λ0/2 at f0)")
N = 32
d = 0.5  # in units of lambda0
x = np.arange(N) * d
for th0d in (20, 40, 60):
    th0 = np.radians(th0d)
    w = np.exp(-1j * 2 * np.pi * x * np.sin(th0))  # phases set at f0, then frozen
    for fr in (0.9, 0.95, 1.05, 1.1):
        k = 2 * np.pi * fr
        th = np.linspace(-np.pi / 2, np.pi / 2, 400001)
        P = np.abs(np.exp(1j * k * np.outer(np.sin(th), x)) @ w)
        thp = th[np.argmax(P)]
        pred = np.arcsin(np.sin(th0) / fr)
        small = th0 - (fr - 1) * np.tan(th0)
        print(f"  θ0={th0d}° f/f0={fr:4.2f}: numeric peak {np.degrees(thp):7.3f}°, asin((f0/f)sinθ0) {np.degrees(pred):7.3f}°, small-signal {np.degrees(small):7.3f}°")

print("=" * 78)
print("5. Instantaneous bandwidth (phase-shifter steering): loss at band edge f0(1±B/2)")
# Theory: squint at edge dth = (B/2) tan th0; loss ~ AF^2 at offset dth in a beam of width Theta3/cos th0
for N in (8, 16, 32):
    x = np.arange(N) * 0.5
    Th3bs = np.radians(hpbw_deg(N, 0.5, 0))
    for th0d in (30, 45, 60):
        th0 = np.radians(th0d)
        w = np.exp(-1j * 2 * np.pi * x * np.sin(th0))

        def loss_at(B):
            out = []
            for fr in (1 - B / 2, 1 + B / 2):
                k = 2 * np.pi * fr
                val = np.abs(np.exp(1j * k * x * np.sin(th0)) @ w) / N  # gain toward intended direction
                out.append(20 * np.log10(val))
            return min(out)

        B1 = brentq(lambda B: loss_at(B) + 1.0, 1e-5, 1.0)
        B3 = brentq(lambda B: loss_at(B) + 3.0, 1e-5, 1.5)
        print(f"  N={N:2d} θ0={th0d}°: B(1 dB edge loss) = {100*B1:6.2f}%  B(3 dB) = {100*B3:6.2f}%   "
              f"Θ3bs/sinθ0 = {100*Th3bs/np.sin(th0):6.2f}%   λ/(L sinθ0) = {100/(N*0.5*np.sin(th0)):6.2f}%")
print("  Closed form: edge loss L_dB ≈ 12 (Δθ/Θ3)^2 ... compare 3 dB <-> Δθ_edge = Θ3(θ0)/2  => B/f0 = Θ3bs/sinθ0")

print("=" * 78)
print("6. TTD vs phase; subarray TTD (4 subarrays of 8, phase shifters within subarray)")
N = 32
x = np.arange(N) * 0.5
th0 = np.radians(45)
tau = x * np.sin(th0)  # delay in units of lambda0/c
for fr in (0.9, 1.0, 1.1):
    k = 2 * np.pi * fr
    th = np.linspace(-np.pi / 2, np.pi / 2, 200001)
    # full TTD
    w_ttd = np.exp(-1j * k * tau)
    P = np.abs(np.exp(1j * k * np.outer(np.sin(th), x)) @ w_ttd)
    # subarray TTD: delay at subarray centres, element phases at f0 within subarray
    M = 8
    sub = np.arange(N) // M
    xc = (np.arange(N // M) * M + (M - 1) / 2) * 0.5
    w_sub = np.exp(-1j * k * xc[sub] * np.sin(th0)) * np.exp(-1j * 2 * np.pi * (x - xc[sub]) * np.sin(th0))
    Ps = np.abs(np.exp(1j * k * np.outer(np.sin(th), x)) @ w_sub)
    # pure phase
    w_ph = np.exp(-1j * 2 * np.pi * x * np.sin(th0))
    Pp = np.abs(np.exp(1j * k * np.outer(np.sin(th), x)) @ w_ph)
    def peak_and_sll(P):
        P = P / P.max()
        ip = np.argmax(P)
        # highest lobe outside main lobe (beyond first nulls approx 2/(N d) in u)
        uu = np.sin(th)
        mask = np.abs(uu - uu[ip]) > 1.2 * 1 / (N * 0.5 * fr)
        return np.degrees(th[ip]), 20 * np.log10(P[mask].max())
    a, b = peak_and_sll(P)
    c, dd = peak_and_sll(Ps)
    e, g = peak_and_sll(Pp)
    gain_sub = 20 * np.log10(np.abs(np.exp(1j * k * x * np.sin(th0)) @ w_sub) / N)
    print(f"  f/f0={fr}: TTD peak {a:6.2f}° SLL {b:6.1f} dB | subarray-TTD peak {c:6.2f}° SLL {dd:6.1f} dB (loss toward 45°: {gain_sub:5.2f} dB) | phase-only peak {e:6.2f}° SLL {g:6.1f} dB")

print("=" * 78)
print("7. Phase quantisation")
for P_ in range(2, 8):
    lsb = 2 * np.pi / 2 ** P_
    sig = lsb / np.sqrt(12)
    loss = -10 * np.log10(np.sinc(1 / 2 ** P_) ** 2)  # exact mean loss for uniform error: |E e^{j e}|^2 = sinc^2
    print(f"  {P_} bits: LSB {np.degrees(lsb):7.3f}°, rms err {np.degrees(sig):6.3f}°, gain loss (exact sinc²) {loss:6.3f} dB, σ² approx {10*np.log10(np.e)*sig**2:6.3f} dB, "
          f"1/2^(2P) = {-20*np.log10(2**P_):6.2f} dB, 1/(2^P-1)^2 = {-20*np.log10(2**P_-1):6.2f} dB")


def quantize(ph, bits, offset=None):
    lsb = 2 * np.pi / 2 ** bits
    if offset is None:
        return np.round(ph / lsb) * lsb
    return np.round((ph + offset) / lsb) * lsb - offset  # dither: known per-element offset (e.g. feed-line phase)


def qlobe_fft(N, bits, u0, amp, offset=None, M=16384):
    """d = lambda/2 only. Returns (peak lobe of quantised pattern outside main lobe, peak of the ERROR pattern
    |AF_q - AF_ideal|^2), both in dB relative to the quantised main-beam peak. FFT: AF(u) = sum w_n e^{j pi n u},
    u = 2m/M wrapped into [-1,1)."""
    n = np.arange(N)
    ideal = -np.pi * n * u0
    ph = quantize(ideal, bits, offset)
    wq = amp * np.exp(1j * ph)
    wi = amp * np.exp(1j * ideal)
    # e^{+j pi n u}: use ifft (sign +) times M
    Aq = np.fft.ifft(wq, M) * M
    Ai = np.fft.ifft(wi, M) * M
    u = np.fft.fftfreq(M) * 2  # in [-1,1)
    Pq = np.abs(Aq) ** 2
    Pe = np.abs(Aq - Ai) ** 2
    pk = Pq.max()
    up = u[np.argmax(Pq)]
    du = np.angle(np.exp(1j * np.pi * (u - up))) / np.pi  # wrapped distance in u
    main = np.abs(du) < 2.5 / (N * 0.5)
    return 10 * np.log10(Pq[~main].max() / pk), 10 * np.log10(Pe.max() / pk)


from scipy.signal.windows import taylor
cases = [(100, "hamming", np.hamming(100), 60), (32, "uniform", np.ones(32), 45), (8, "uniform", np.ones(8), 45),
         (8, "taylor-30dB", taylor(8, nbar=4, sll=30), 45), (16, "uniform", np.ones(16), 45)]
for (N, name, amp, thmax) in cases:
    print(f"  N={N} {name}: worst case over steering 0..{thmax}° — total-pattern peak lobe / error-pattern peak (dBc), angle")
    for bits in (2, 3, 4, 5, 6):
        u0s = np.sin(np.radians(np.linspace(0, thmax, 4501)))
        res = np.array([qlobe_fft(N, bits, u0, amp) for u0 in u0s])
        i = int(np.argmax(res[:, 1]))
        j = int(np.argmax(res[:, 0]))
        print(f"    {bits} bits: error-pattern max {res[i,1]:7.2f} dB at θ0={np.degrees(np.arcsin(u0s[i])):5.2f}° ; "
              f"total-pattern worst lobe {res[j,0]:7.2f} dB at θ0={np.degrees(np.arcsin(u0s[j])):5.2f}° ; "
              f"1/2^(2P) {-6.02*bits:6.2f} ; ADI angle sin⁻¹(1/2^B) {np.degrees(np.arcsin(1/2**bits)):5.2f}°")
# dither
N = 100
amp = np.hamming(N)
off = rng.uniform(0, 2 * np.pi, N)
u0s = np.sin(np.radians(np.linspace(0, 60, 4501)))
for bits in (3, 4):
    v0 = max(qlobe_fft(N, bits, u0, amp)[1] for u0 in u0s)
    v1 = max(qlobe_fft(N, bits, u0, amp, offset=off)[1] for u0 in u0s)
    eta = np.sum(amp) ** 2 / (N * np.sum(amp ** 2))
    sig2 = (2 * np.pi / 2 ** bits) ** 2 / 12
    print(f"  N=100 Hamming {bits} bits: worst error-pattern lobe without dither {v0:.2f} dB, with random phase offset (dither) {v1:.2f} dB; "
          f"mean random-error floor σ²/(Nη) = {10*np.log10(sig2/(N*eta)):.1f} dB")

print("=" * 78)
print("8. Beam pointing resolution with P-bit phase shifters (smallest non-zero steer), d = λ/2")
for N in (8, 30, 100):
    for bits in (2, 4, 6):
        lsb = 2 * np.pi / 2 ** bits
        # ADI: half the array at 0, other half at one LSB
        theta_res = np.degrees(np.arcsin(lsb / (N * np.pi)))
        x = np.arange(N) * 0.5
        ph = np.where(np.arange(N) >= N // 2, lsb, 0.0)
        u = np.linspace(-0.2, 0.2, 400001)
        P = np.abs(af(np.exp(1j * ph), x, u))
        print(f"    N={N:3d} {bits} bits: ADI θ_RES={theta_res:6.3f}°, numeric peak of half-array-LSB state {np.degrees(np.arcsin(abs(u[np.argmax(P)]))):6.3f}°, HPBW {hpbw_deg(N,0.5,0):6.2f}°")

print("=" * 78)
print("9. Random phase errors -> pointing error (σ_φ = 10°)")
sigp = np.radians(10)
for N in (8, 16, 64):
    x = np.arange(N) * 0.5
    errs = []
    for _ in range(4000):
        ph = rng.normal(0, sigp, N)
        u = np.linspace(-0.3, 0.3, 6001)
        P = np.abs(af(np.exp(1j * ph), x, u))
        # refine with parabola
        i = np.argmax(P)
        errs.append(u[i])
    su_mc = np.std(errs)
    su_th = sigp / (2 * np.pi * 0.5) * np.sqrt(12 / (N * (N ** 2 - 1)))
    du3 = 0.886 / (N * 0.5)
    print(f"    N={N:2d}: σ_u Monte Carlo {su_mc:.5f}, LS-slope formula {su_th:.5f}; in beamwidths {su_mc/du3:.4f} (formula 0.622σ/√N ≈ {0.622*sigp/np.sqrt(N):.4f})")

print("=" * 78)
print("10. Worked examples")
f = 5.8e9; lam = c0 / f
print(f"  5.8 GHz: λ={lam*1e3:.2f} mm")
for d_mm in (25.84, 28.0, 31.0, 34.0):
    dl = d_mm * 1e-3 / lam
    thm = np.degrees(np.arcsin(min(1, 1 / dl - 1)))
    thm2 = np.degrees(np.arcsin(min(1, (1 - 1 / 8) / dl - 1))) if (1 - 1 / 8) / dl - 1 < 1 else 90
    print(f"    d={d_mm:5.2f} mm ({dl:.3f}λ): max scan (GL peak at horizon) {thm:5.1f}°, (GL null at horizon, N=8) {thm2:5.1f}°")
# squint across 5.725-5.875 and 5.65-5.95 at 45 deg
for f1, f2 in ((5.725e9, 5.875e9), (5.65e9, 5.95e9)):
    f0 = 5.8e9
    for th0d in (30, 45, 60):
        a = np.degrees(np.arcsin(np.sin(np.radians(th0d)) * f0 / f1)) - th0d
        b = np.degrees(np.arcsin(np.sin(np.radians(th0d)) * f0 / f2)) - th0d
        print(f"    band {f1/1e9:.3f}-{f2/1e9:.3f} GHz, θ0={th0d}°: squint {a:+.2f}° / {b:+.2f}° (8-el scanned HPBW {hpbw_deg(8,0.5,th0d):.1f}°)")
# TTD delay needed
for N, dmm, f in ((8, 25.84, 5.8e9), (32, 25.84, 5.8e9), (8, 14.0, 10.25e9)):
    L = (N - 1) * dmm * 1e-3
    print(f"    N={N}, d={dmm} mm: max TTD span at 60° = {L*np.sin(np.radians(60))/c0*1e12:.0f} ps; at f={f/1e9} GHz that's {L*np.sin(np.radians(60))/c0*f:.2f} cycles")
# 2.4 GHz ground station scanning ±60
lam = c0 / 2.44e9
print(f"  2.44 GHz: λ={lam*1e3:.1f} mm; d_max(±60°) = {lam/(1+np.sin(np.radians(60)))*1e3:.1f} mm; with N=8 null margin {lam*(7/8)/(1+np.sin(np.radians(60)))*1e3:.1f} mm")
# Phaser: 14 mm at 10.25 GHz
lam = c0 / 10.25e9
dl = 14e-3 / lam
print(f"  Phaser: d=14 mm = {dl:.3f}λ at 10.25 GHz (<λ/2) -> λ/d-1 = {1/dl-1:.3f} > 1: no grating-lobe peak in visible space for any scan; "
      f"N=8 null-margin limit sin θ0 ≤ (1-1/8)/(d/λ)-1 = {(7/8)/dl-1:.3f} -> {np.degrees(np.arcsin(min(1,(7/8)/dl-1))):.1f}°")
print("=" * 78)
print("11. 8-element worked example: total-pattern peak sidelobe (mask = first null) with P-bit phase shifters, scan 0..45°")
def total_sll(N, bits, u0, amp, M=16384):
    n = np.arange(N)
    ideal = -np.pi * n * u0
    w = amp * np.exp(1j * (quantize(ideal, bits) if bits else ideal))
    A = np.abs(np.fft.ifft(w, M) * M) ** 2
    u = np.fft.fftfreq(M) * 2
    up = u[np.argmax(A)]
    du = np.angle(np.exp(1j * np.pi * (u - up))) / np.pi
    # first-null half-width in u for the actual taper: find where A first drops to a local min
    order = np.argsort(du)
    duo, Ao = du[order], A[order]
    ip = np.argmin(np.abs(duo))
    r = ip
    while r < len(Ao) - 1 and Ao[r + 1] < Ao[r]:
        r += 1
    l = ip
    while l > 0 and Ao[l - 1] < Ao[l]:
        l -= 1
    mask = np.ones_like(Ao, bool); mask[l:r + 1] = False
    return 10 * np.log10(Ao[mask].max() / A.max())
for name, amp in (("uniform", np.ones(8)), ("Taylor 25 dB nbar=3", taylor(8, nbar=3, sll=25))):
    for bits in (0, 3, 4, 5, 6):
        u0s = np.sin(np.radians(np.linspace(0, 45, 2251)))
        v = [total_sll(8, bits, u0, amp) for u0 in u0s]
        print(f"  {name:20s} {('ideal' if bits==0 else str(bits)+' bits'):7s}: worst SLL over 0..45° = {max(v):6.2f} dB, at broadside {v[0]:6.2f} dB")
print("done")
