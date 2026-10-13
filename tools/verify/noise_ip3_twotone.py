#!/usr/bin/env python3
"""
noise_ip3_twotone.py — verification for kb/07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
and dynamic-range-sfdr-blocking.md.

1. Symbolic (sympy) two-tone expansion of y = a1 x + a2 x^2 + a3 x^3: amplitudes of every product.
2. Closed forms: A_IIP3 = sqrt(4/3 |a1/a3|), A_1dB = sqrt(0.145 |a1/a3|), ratio -> 9.64 dB;
   A_IIP2 = |a1/a2|; HD2, HD3; blocking/desensitisation gain a1 + 3/2 a3 A_b^2; cross-mod.
3. Numerical two-tone FFT "measurement" on
      (a) pure cubic polynomial   (b) tanh (differential-pair-like)   (c) Rapp soft limiter (p=2)
   extracting P1dB (single tone) and IIP3 by small-signal extrapolation -> the IIP3 - P1dB gap.
   Shows that "IIP3 = P1dB + 9.6 dB" holds only for the pure cubic; real devices differ.
4. 3:1 slope check of IM3 vs input power; 2:1 for IM2.

Run: python3 noise_ip3_twotone.py
"""
import numpy as np
import sympy as sp

R = 50.0
def dbm_from_peak(A):          # tone of peak amplitude A volts into R
    return 10*np.log10(A**2/(2*R)/1e-3)
def peak_from_dbm(P):
    return np.sqrt(2*R*1e-3*10**(P/10))

print("=== 1. Symbolic two-tone expansion ===")
a1, a2, a3, A, t, w1, w2 = sp.symbols('a1 a2 a3 A t w1 w2', real=True)
x = A*sp.cos(w1*t) + A*sp.cos(w2*t)
y = sp.expand(a1*x + a2*x**2 + a3*x**3)
y = sp.expand(sp.fu(sp.expand_trig(y)))          # not strictly needed; use rewrite for clarity
yc = sp.expand(sp.simplify(sp.expand((a1*x + a2*x**2 + a3*x**3).rewrite(sp.exp))))
# collect coefficients of exp(j(m w1 + n w2) t)
terms = {}
for term in sp.Add.make_args(yc):
    ex = [f for f in sp.Mul.make_args(term) if f.func == sp.exp]
    arg = sp.expand(sum(sp.log(e).expand(force=True) for e in ex)/(sp.I*t)) if ex else 0
    m = sp.Poly(arg, w1, w2).coeff_monomial(w1) if arg != 0 else 0
    n = sp.Poly(arg, w1, w2).coeff_monomial(w2) if arg != 0 else 0
    coeff = sp.simplify(term/sp.Mul(*ex)) if ex else term
    terms[(m, n)] = sp.simplify(terms.get((m, n), 0) + coeff)
def amp(m, n):
    # real cosine amplitude = 2*|coef| for (m,n) != (0,0)
    c = terms.get((m, n), 0)
    return sp.simplify(2*c) if (m, n) != (0, 0) else sp.simplify(c)
for (m, n), label in [((1, 0), 'fundamental w1'), ((2, -1), 'IM3 2w1-w2'), ((1, -1), 'IM2 w1-w2'),
                      ((1, 1), 'IM2 w1+w2'), ((2, 0), 'HD2 2w1'), ((3, 0), 'HD3 3w1'), ((2, 1), 'IM3 2w1+w2'),
                      ((0, 0), 'DC')]:
    print(f"  {label:16s}: {amp(m, n)}")

print("\n=== 2. Closed forms (pure cubic, a3 < 0 compressive) ===")
A_iip3 = sp.sqrt(sp.Rational(4, 3)*sp.Abs(a1/a3))
A_1db = sp.sqrt((1 - 10**(-sp.Rational(1, 20)))*sp.Rational(4, 3)*sp.Abs(a1/a3))
print("  A_IIP3 = sqrt(4/3 |a1/a3|);  A_1dB = sqrt(4/3 (1-10^(-1/20)) |a1/a3|) = sqrt(%.4f |a1/a3|)"
      % float(sp.Rational(4, 3)*(1 - 10**(-sp.Rational(1, 20)))))
ratio_db = float(20*sp.log(A_iip3/A_1db, 10).subs({a1: 1, a3: -1}))
print(f"  IIP3 - P1dB = {ratio_db:.3f} dB  (single-tone P1dB vs two-tone per-tone IIP3)")
# Two-tone 1 dB compression (both tones equal): fundamental gain a1 + 9/4 a3 A^2 -> A_1dB,2tone^2 = 0.145*(3/4)/(9/4)*...
A1db_2t = sp.sqrt((1 - 10**(-sp.Rational(1, 20)))*sp.Rational(4, 9)*sp.Abs(a1/a3))
print(f"  per-tone amplitude at which a two-tone test compresses 1 dB: {float(20*sp.log(A1db_2t/A_1db,10).subs({a1:1,a3:-1})):.2f} dB "
      "relative to single-tone P1dB (i.e. 4.77 dB lower per tone)")
print("  IIP2 amplitude = |a1/a2| (IM2 at w1-w2 has amplitude a2 A^2)")
print("  HD2/fund = a2 A/(2 a1);  HD3/fund = a3 A^2/(4 a1);  IM3/fund = 3 a3 A^2/(4 a1)  -> IM3 is 9.54 dB above HD3")
print("  Small wanted signal gain with blocker amplitude Ab: a1 + (3/2) a3 Ab^2  -> blocked (gain->0) at Ab^2 = 2/3 |a1/a3|")
print("  Cross-modulation: AM on blocker Ab(1+m cos wm t) transfers to wanted as (3 a3/a1) Ab^2 m cos wm t (small m)")
Ab_block_db = float(10*sp.log((sp.Rational(2, 3))/(sp.Rational(4, 3)), 10))
print(f"  Blocker that fully blocks the gain: {Ab_block_db:.2f} dB relative to A_IIP3 (Ab^2 = A_IIP3^2/2)")
Ab_desense1 = float(10*sp.log((1-10**(-sp.Rational(1,20)))*sp.Rational(2,3)/sp.Rational(4,3),10))
print(f"  Blocker giving 1 dB small-signal gain drop: {Ab_desense1:.2f} dB relative to A_IIP3 "
      f"(= P1dB - 3.0 dB for the pure cubic)")

print("\n=== 3. Numerical measurement on three nonlinearities ===")
fs, N = 4096.0, 1 << 15
tt = np.arange(N)/fs
f1, f2 = 400.0, 420.0
def fb(f): return int(round(f*N/fs))
def spectrum(v):
    return np.fft.rfft(v)/N*2

def models(Vsat=1.0):
    cubic = lambda v: v - (4/3)*v**3/(Vsat**2)*0.0 + v*0   # placeholder, replaced below
    return None

G = 10.0  # small-signal voltage gain for all models
Vsat = 1.0
# (a) cubic with the same small-signal gain and a3 chosen so that A_IIP3 = 1 V (for comparability)
a1n, a3n = G, -4*G/3/1.0**2
cubic = lambda v: a1n*v + a3n*v**3
# (b) tanh with same small-signal gain: y = Vsat*G*tanh(v/Vsat)... Taylor a3 = -G/(3 Vsat^2)
tanh_m = lambda v: G*Vsat*np.tanh(v/Vsat)
# (c) Rapp p=2 AM/AM on instantaneous amplitude (memoryless, real passband approximation):
def rapp(v, p=2.0, Vo=G*Vsat):
    u = G*v
    return u/(1 + np.abs(u/Vo)**(2*p))**(1/(2*p))

def measure(fn, name):
    # single-tone gain compression sweep
    Pins = np.arange(-60.0, 20.0, 0.25)
    gains = []
    for P in Pins:
        Ap = peak_from_dbm(P)
        yv = fn(Ap*np.cos(2*np.pi*f1*tt))
        Y = spectrum(yv)
        gains.append(dbm_from_peak(np.abs(Y[fb(f1)])) - P)
    gains = np.array(gains)
    g0 = gains[0]
    idx = np.where(gains <= g0 - 1.0)[0]
    P1 = np.interp(g0-1.0, gains[idx[0]-1:idx[0]+1][::-1], Pins[idx[0]-1:idx[0]+1][::-1]) if len(idx) else np.nan
    # two-tone small-signal IM3 extrapolation (at -40 dBm per tone and -30 dBm per tone for slope)
    res = []
    for P in (-40.0, -35.0, -30.0):
        Ap = peak_from_dbm(P)
        yv = fn(Ap*np.cos(2*np.pi*f1*tt) + Ap*np.cos(2*np.pi*f2*tt))
        Y = spectrum(yv)
        Pf = dbm_from_peak(np.abs(Y[fb(f1)]))
        Pim = dbm_from_peak(np.abs(Y[fb(2*f1 - f2)]) + 1e-300)
        res.append((P, Pf, Pim))
    slope = (res[2][2] - res[0][2])/(res[2][0] - res[0][0])
    P, Pf, Pim = res[0]
    iip3 = P + (Pf - Pim)/2
    print(f"  {name:12s}: G0={g0:6.2f} dB, IP1dB={P1:7.2f} dBm, IIP3(extrap)={iip3:7.2f} dBm, "
          f"IIP3-IP1dB={iip3-P1:5.2f} dB, IM3 slope={slope:4.2f} dB/dB")
    return P1, iip3

measure(cubic, "pure cubic")
measure(tanh_m, "tanh")
# (c) cubic partially cancelled + compressive quintic ("IM3 sweet spot" device): IIP3 is high while
#     compression (set mostly by a5) stays low -> the gap exceeds 9.6 dB
quint = lambda v: G*(v - (4/3)*0.1*v**3 - 0.5*v**5)
measure(quint, "cubic+quintic")
# (d) Rapp p=2 applied to the instantaneous voltage has NO cubic term (Taylor: u - u^5/(4 Vo^4) ...):
#     IM3 rises 5 dB/dB, so an "IIP3" extrapolated with a 3:1 line is meaningless. Always check the slope.
measure(rapp, "Rapp p=2")

print("\n=== 4. IM2 slope (add a2 term) ===")
a2n = 0.3*G
poly2 = lambda v: a1n*v + a2n*v**2 + a3n*v**3
out = []
for P in (-40.0, -30.0):
    Ap = peak_from_dbm(P)
    yv = poly2(Ap*np.cos(2*np.pi*f1*tt) + Ap*np.cos(2*np.pi*f2*tt))
    Y = spectrum(yv)
    out.append((P, dbm_from_peak(np.abs(Y[fb(f1)])), dbm_from_peak(np.abs(Y[fb(f2 - f1)]))))
s2 = (out[1][2]-out[0][2])/(out[1][0]-out[0][0])
iip2 = out[0][0] + (out[0][1]-out[0][2])
print(f"  IM2 slope = {s2:.2f} dB/dB; IIP2 (extrap) = {iip2:.2f} dBm; theory |a1/a2| -> "
      f"{dbm_from_peak(abs(a1n/a2n)):.2f} dBm")
print("\nDone.")
