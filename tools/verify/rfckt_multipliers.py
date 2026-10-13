#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/frequency-multipliers-dividers.md

 A. Transistor (class-C) multiplier: optimum conduction angle and harmonic content for n = 2, 3, 4
 B. Push-push doubler: antiphase drive cancels odd harmonics
 C. Phase-noise multiplication by N: +20 log N (small index) and carrier collapse (Bessel J0(N beta))
 D. Divider: -20 log M, floor-limited; a x240 OCXO multiplication example
 E. Dual-modulus prescaler P/P+1: N = P*B + A, contiguous for N >= P(P-1)
 F. Pulse/comb generator: harmonic envelope ~ sinc(n f0 tau) for an SRD-like impulse train
 G. Varactor vs resistive multiplier efficiency limits (Manley-Rowe vs Page 1/n^2) - arithmetic
 H. Anti-parallel diode pair tripler: only odd harmonics; APDP current spectrum
Run: python3 tools/verify/rfckt_multipliers.py
"""
import numpy as np, sys
from scipy.special import jv
from scipy.optimize import minimize_scalar

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- A. conduction angle for harmonics
def harm(alpha, n, N=1 << 14):
    th = np.linspace(-np.pi, np.pi, N, endpoint=False)
    h = alpha / 2
    i = np.clip((np.cos(th) - np.cos(h)) / (1 - np.cos(h)), 0, None)
    return 2 * np.mean(i * np.cos(n * th)), np.mean(i)


def In_closed(alpha, n):
    """Closed form In/Imax for a truncated cosine (n >= 2)."""
    h = alpha / 2
    return (2 / np.pi) * (np.sin(n * h) * np.cos(h) - n * np.cos(n * h) * np.sin(h)) / (n * (n ** 2 - 1) * (1 - np.cos(h)))


print("A: n   optimum conduction angle   In/Imax   In/I1(class-B ref)   eta_n = In/(2 Idc)")
opt = {}
for n in (2, 3, 4):
    grid = np.linspace(0.05, 2 * np.pi - 0.05, 721)
    a0 = grid[np.argmax([harm(g, n)[0] for g in grid])]
    r = minimize_scalar(lambda a: -harm(a, n)[0], bounds=(max(a0 - 0.05, 0.01), a0 + 0.05), method='bounded')
    a = r.x; In, Idc = harm(a, n)
    opt[n] = (np.degrees(a), In)
    print(f"   {n}      {np.degrees(a):6.1f} deg              {In:.4f}      {20*np.log10(In/0.5):+6.1f} dB             {In/(2*Idc)*100:5.1f} %")
    check(f"A1 closed-form In matches FFT for n={n}", abs(In_closed(a, n) - In) < 1e-4)
check("A2 optimum angle ~ 120 deg (n=2), ~ 80 deg (n=3), ~ 60 deg (n=4): roughly 240/n deg",
      abs(opt[2][0] - 120) < 3 and abs(opt[3][0] - 80) < 3 and abs(opt[4][0] - 60) < 3)

# ---------------------------------------------------------------- B. push-push
th = np.linspace(-np.pi, np.pi, 1 << 14, endpoint=False)
def ic(theta, alpha):
    h = alpha / 2
    return np.clip((np.cos(theta) - np.cos(h)) / (1 - np.cos(h)), 0, None)
a = np.deg2rad(120)
single = ic(th, a)
pp = ic(th, a) + ic(th + np.pi, a)        # two devices driven in antiphase, outputs summed
def hk(x, k):
    return abs(2 * np.mean(x * np.exp(-1j * k * th)))
print("B: harmonic currents (relative to Imax):  k=1     k=2     k=3     k=4")
print(f"   single device                         {hk(single,1):.4f}  {hk(single,2):.4f}  {hk(single,3):.4f}  {hk(single,4):.4f}")
print(f"   push-push pair                        {hk(pp,1):.1e}  {hk(pp,2):.4f}  {hk(pp,3):.1e}  {hk(pp,4):.4f}")
check("B1 push-push cancels odd harmonics and doubles the even ones", hk(pp, 1) < 1e-9 and hk(pp, 3) < 1e-9 and abs(hk(pp, 2) - 2 * hk(single, 2)) < 1e-9)

# ---------------------------------------------------------------- C. phase-noise multiplication
fs, Nn = 1.0, 1 << 16
t = np.arange(Nn)
beta, fm = 0.01, 200 / Nn
for Nmul in (2, 10, 100):
    phi = beta * np.sin(2 * np.pi * fm * t)
    x = np.exp(1j * Nmul * phi)                    # ideal multiplier: phase multiplied by N
    X = np.abs(np.fft.fft(x)) / Nn
    sb = 20 * np.log10(X[200] / X[0])
    th_ = 20 * np.log10(jv(1, Nmul * beta) / jv(0, Nmul * beta))
    base = 20 * np.log10(jv(1, beta) / jv(0, beta))
    print(f"C: x{Nmul:3d}: first PM sideband {sb:7.2f} dBc (Bessel {th_:7.2f}); increase vs x1 {sb-base:+6.2f} dB, 20logN = {20*np.log10(Nmul):.2f}")
    if Nmul == 10:
        check("C1 sideband level rises by 20 log N for small indices", abs((sb - base) - 20 * np.log10(Nmul)) < 0.1)
print(f"   carrier collapse: J0(N*beta) = 0 at N*beta = 2.405 -> for beta = 0.01 rad at N = {2.405/0.01:.0f}; "
      "for broadband phase noise the carrier collapses when the integrated N*phi_rms approaches ~1 rad")
# broadband noise example: 100 MHz OCXO at -150 dBc/Hz multiplied to 24 GHz
L0 = -150.0; N24 = 24e9 / 100e6
print(f"   100 MHz OCXO floor {L0} dBc/Hz multiplied x{N24:.0f} to 24 GHz: {L0 + 20*np.log10(N24):.1f} dBc/Hz")
check("C2 20logN arithmetic (x240 = +47.6 dB)", abs(20 * np.log10(240) - 47.6) < 0.05)

# ---------------------------------------------------------------- D. divider
for M, Lin, floor in ((8, -134, -155), (64, -134, -155), (2, -110, -160)):
    Lout = 10 * np.log10(10 ** ((Lin - 20 * np.log10(M)) / 10) + 10 ** (floor / 10))
    print(f"D: /{M:2d}: input {Lin} dBc/Hz -> ideal {Lin-20*np.log10(M):.1f}, with a {floor} dBc/Hz divider floor {Lout:.1f} dBc/Hz")
check("D1 division reduces phase noise by 20logM until the floor", abs(10 * np.log10(10 ** ((-134 - 18.06) / 10) + 10 ** (-155 / 10)) + 150.3) < 0.3)

# ---------------------------------------------------------------- E. dual-modulus prescaler
for P in (4, 8, 16):
    reach = set()
    for B in range(0, 400):
        for A in range(0, P):
            if A <= B:
                reach.add(P * B + A)
    Nmax = 300
    gaps = [k for k in range(1, Nmax) if k not in reach]
    cont = max(gaps) + 1 if gaps else 1
    print(f"E: prescaler {P}/{P+1}: every N >= {cont} reachable (theory P(P-1) = {P*(P-1)}); largest gap {max(gaps) if gaps else None}")
    check(f"E1 P/P+1 contiguous from P(P-1) for P={P}", cont == P * (P - 1))
print("   (ADF4351 specifies INT >= 23 for 4/5 and >= 75 for 8/9 - above these theoretical minima)")

# ---------------------------------------------------------------- F. comb generator envelope
f0 = 100e6
for tau in (100e-12, 300e-12):
    # rectangular pulses of width tau at rate f0: harmonic n amplitude = 2 f0 tau |sinc(n f0 tau)|
    n = np.array([1, 10, 30, 50, 100])
    amp = 2 * f0 * tau * np.abs(np.sinc(n * f0 * tau))
    print(f"F: {tau*1e12:.0f} ps pulses at 100 MHz: harmonics n = 1/10/30/50/100 at "
          + "/".join(f"{20*np.log10(a):.1f}" for a in amp) + f" dB (re pulse amplitude); first null at {1/tau/1e9:.1f} GHz")
Mp = 1 << 16
pulse = np.zeros(Mp); w_ = 33; pulse[:w_] = 1.0     # period Mp samples, width w_
P_ = np.abs(np.fft.rfft(pulse)) / Mp * 2
k = 40
check("F1 comb harmonic envelope = 2 f0 tau sinc(n f0 tau)", abs(P_[k] - 2 * (w_ / Mp) * abs(np.sinc(k * w_ / Mp))) < 1e-3)

# ---------------------------------------------------------------- G. efficiency limits
for n in (2, 3, 4):
    print(f"G: resistive (Page) multiplier efficiency limit 1/n^2 for n={n}: {100/n**2:.1f} % ({10*np.log10(1/n**2):.1f} dB); "
          f"ideal lossless varactor (Manley-Rowe): 100 %")
check("G1 Page bound arithmetic", abs(10 * np.log10(1 / 9) + 9.54) < 0.01)

# ---------------------------------------------------------------- H. APDP tripler
VT = 0.0275
v = 0.4 * np.cos(th)
i = np.sinh(v / VT)
print(f"H: APDP current harmonics (rel. fundamental): 2nd {20*np.log10(hk(i,2)/hk(i,1)+1e-300):.0f} dB, "
      f"3rd {20*np.log10(hk(i,3)/hk(i,1)):.1f} dB, 5th {20*np.log10(hk(i,5)/hk(i,1)):.1f} dB")
check("H1 APDP generates only odd harmonics (tripler without a balun)", hk(i, 2) < 1e-9 * hk(i, 1))

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
