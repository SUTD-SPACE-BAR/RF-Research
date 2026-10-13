#!/usr/bin/env python3
"""Verification + worked-example calculator for kb/11-radar/radar-range-equation.md

Run:  python3 tools/verify/radar_range_equation.py      (~5 s)

Checks / computes:
  1. Equivalence of the three common forms of the monostatic radar equation:
       pulsed (peak power x pulse width x N pulses), FMCW/CW (Pt x T_meas, TI SWRA553 Eq.2 and the
       Rao form), and the "energy" form SNR = E_total G_t G_r lambda^2 sigma / ((4 pi)^3 R^4 k T_s L).
  2. dB-domain budget == linear computation.
  3. Window processing losses and scalloping (straddle) losses (Harris 1978 values):
       rect / Hann / Hamming / Blackman: coherent gain, ENBW, SNR loss, worst-case scalloping.
  4. Beam-shape (scanning) loss for a Gaussian beam, many pulses across the 3-dB beamwidth: ~1.6 dB
     one-dimensional (Blake).
  5. System noise temperature cascade: Ts = Ta + T0 (L-1) + L Te.
  6. Worked examples (printed, used on the page):
       A. 24 GHz IPM-165/CDM324 Doppler module vs a person (back-out of the effective noise figure
          implied by the vendor's "15-20 m" claim; FFT narrowing).
       B. TI AWR1843-class 77 GHz FMCW: car / person / drone / small rocket, single virtual channel
          and with 12-channel coherent beamforming gain.
       C. MIT coffee-can 2.4 GHz FMCW (audio-rate IF) SNR and IF-limited max range.
       D. DIY S-band CW/FMCW rocket-tracking radar with 1.2 m dishes.
       E. Search-radar (power-aperture) form: drone surveillance.
       F. Bistatic passive radar with an FM broadcast illuminator (range-product form).
  7. R^4 scaling: +12.04 dB per range doubling.
"""
import numpy as np
from scipy import integrate, optimize

c = 299_792_458.0
k = 1.380649e-23
T0 = 290.0
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


db = lambda x: 10 * np.log10(x)
undb = lambda x: 10 ** (x / 10)


def snr_mono(Pt, Gt, Gr, lam, sigma, R, Tcoh, F=1.0, Ts=None, L=1.0):
    """SNR after coherent integration over Tcoh (s) (matched filter / FFT), noise kTsF per Hz."""
    Tsys = T0 * F if Ts is None else Ts
    return Pt * Gt * Gr * lam ** 2 * sigma * Tcoh / ((4 * np.pi) ** 3 * R ** 4 * k * Tsys * L)


def rmax_mono(Pt, Gt, Gr, lam, sigma, Tcoh, snr_req, F=1.0, Ts=None, L=1.0):
    Tsys = T0 * F if Ts is None else Ts
    return (Pt * Gt * Gr * lam ** 2 * sigma * Tcoh / ((4 * np.pi) ** 3 * k * Tsys * L * snr_req)) ** 0.25


print("=" * 78)
print("1. Equivalence of forms")
fc = 77e9
lam = c / fc
Pt, Gt, Gr, sigma, F = 10 ** (12 / 10) / 1000, undb(10), undb(10), 1.0, undb(15)
N, Tr = 128, 40e-6
R = 50.0
snr_energy = snr_mono(Pt, Gt, Gr, lam, sigma, R, N * Tr, F)
# TI SWRA553 Eq.(2) in its SNR form: Pt G G c^2 sigma N Tr / (fc^2 (4pi)^3 R^4 k T NF)
snr_ti = Pt * Gt * Gr * c ** 2 * sigma * N * Tr / (fc ** 2 * (4 * np.pi) ** 3 * R ** 4 * k * T0 * F)
check("TI SWRA553 Eq.2 form == energy form", snr_ti, snr_energy, 1e-12, rel=True)
# Pulsed form: peak power Pp, pulse width tau, N pulses; matched filter B ~ 1/tau
Pp, tau = 100.0, 1e-6
snr_pulse_1 = Pp * Gt * Gr * lam ** 2 * sigma / ((4 * np.pi) ** 3 * R ** 4 * k * T0 * F * (1 / tau))
check("pulsed peak-power/(kTFB) with B=1/tau == energy form", snr_pulse_1, snr_mono(Pp, Gt, Gr, lam, sigma, R, tau, F), 1e-12, rel=True)
check("N coherent pulses multiply SNR by N", N * snr_pulse_1, snr_mono(Pp, Gt, Gr, lam, sigma, R, N * tau, F), 1e-12, rel=True)

print("=" * 78)
print("2. dB budget == linear")
budget = (db(Pt * 1000) - 30) + db(Gt) + db(Gr) + 2 * db(lam) + db(sigma) + db(N * Tr) - 3 * db(4 * np.pi) - 4 * db(R) - db(k * T0) - db(F)
check("dB-sum SNR", budget, db(snr_energy), 1e-9)
check("kT0 in dBm/Hz", db(k * T0 * 1000), -173.98, 0.01)
check("(4 pi)^3 in dB", 3 * db(4 * np.pi), 32.98, 0.01)
check("R^4: SNR change per range doubling (dB)", db(snr_mono(1, 1, 1, 1, 1, 1, 1) / snr_mono(1, 1, 1, 1, 1, 2, 1)), 12.04, 0.01)

print("=" * 78)
print("3. Window losses (Harris 1978)")
M = 4096
n = np.arange(M)
wins = {
    "rect": np.ones(M),
    "hann": 0.5 - 0.5 * np.cos(2 * np.pi * n / M),
    "hamming": 0.54 - 0.46 * np.cos(2 * np.pi * n / M),
    "blackman": 0.42 - 0.5 * np.cos(2 * np.pi * n / M) + 0.08 * np.cos(4 * np.pi * n / M),
}
harris = {  # (ENBW bins, processing loss dB, scalloping dB)
    "rect": (1.00, 0.00, 3.92), "hann": (1.50, 1.76, 1.42), "hamming": (1.36, 1.34, 1.78), "blackman": (1.73, 2.37, 1.10)}
for name, w in wins.items():
    cg = w.sum() / M
    enbw = M * np.sum(w ** 2) / w.sum() ** 2
    pl = db(enbw)                       # SNR loss vs rectangular (tone in white noise)
    # scalloping: response to a tone half-way between bins relative to on-bin
    half = np.abs(np.sum(w * np.exp(1j * np.pi * n / M))) / w.sum()
    sl = -20 * np.log10(half)
    print(f"    {name:8s}: coherent gain {cg:.3f}, ENBW {enbw:.3f} bins, SNR (processing) loss {pl:.2f} dB, scalloping {sl:.2f} dB")
    check(f"{name} ENBW", enbw, harris[name][0], 0.01)
    check(f"{name} processing loss dB", pl, harris[name][1], 0.02)
    # NOTE: Harris' table lists 1.78 dB for Hamming; exact computation of 0.54/0.46 gives 1.75 dB
    check(f"{name} scalloping loss dB", sl, harris[name][2], 0.04 if name == "hamming" else 0.02)
# average straddle loss for a uniformly distributed tone frequency (Hann): mean of |W(f)|^2 over +-0.5 bin
off = np.linspace(-0.5, 0.5, 201)
resp = np.array([np.abs(np.sum(wins['hann'] * np.exp(2j * np.pi * d * n / M))) / wins['hann'].sum() for d in off])
avg_straddle = -db(np.mean(resp ** 2))
print(f"    Hann: average (not worst) straddle loss for random target position = {avg_straddle:.2f} dB")

print("=" * 78)
print("4. Beam-shape loss, Gaussian beam, pulses uniformly across the 3-dB beamwidth (1-D)")
# one-way power pattern G(th) = exp(-4 ln2 (th/thB)^2); two-way = G^2
g2 = lambda x: np.exp(-8 * np.log(2) * x ** 2)
avg, _ = integrate.quad(g2, -0.5, 0.5)
Lbs = -db(avg)
check("beam-shape loss (dB), Blake ~1.6 dB", Lbs, 1.6, 0.1)
print(f"    two-dimensional (az & el scanning) ~ {2*Lbs:.2f} dB")

print("=" * 78)
print("5. System noise temperature")
Ta, Lr_dB, NF_dB = 100.0, 1.0, 3.0
Lr = undb(Lr_dB)
Te = T0 * (undb(NF_dB) - 1)
Ts = Ta + T0 * (Lr - 1) + Lr * Te
print(f"    Ta={Ta} K, line loss {Lr_dB} dB, receiver NF {NF_dB} dB (Te={Te:.1f} K) -> Ts = {Ts:.1f} K")
check("Ts cascade example (K)", Ts, 100 + 290 * (Lr - 1) + Lr * 288.626, 0.01)

print("=" * 78)
print("6. Worked examples")
# ---------------- A. 24 GHz Doppler module
print("A. 24.125 GHz IPM-165 / CDM324 class Doppler module, person sigma = 0.3 m^2")
fA = 24.125e9
lamA = c / fA
EIRP = undb(16) / 1000          # 16 dBm typ (datasheet)
GrA = undb(9.5)
sigA = 0.3
snr_req = undb(13)
B600 = 600.0                     # 6-600 Hz LF filter recommended by InnoSenT
# Back out the effective noise figure that makes Rmax = 17.5 m (vendor says 15-20 m for a person)
def rA(F, B):
    return (EIRP * GrA * lamA ** 2 * sigA / ((4 * np.pi) ** 3 * k * T0 * F * B * snr_req)) ** 0.25
Feff = optimize.brentq(lambda FdB: rA(undb(FdB), B600) - 17.5, 0, 80)
print(f"    lambda = {lamA*1000:.2f} mm; vendor range 15-20 m in 6-600 Hz band implies effective NF ~ {Feff:.1f} dB "
      f"(15 m -> {optimize.brentq(lambda FdB: rA(undb(FdB), B600)-15, 0, 80):.1f} dB, 20 m -> {optimize.brentq(lambda FdB: rA(undb(FdB), B600)-20, 0, 80):.1f} dB)")
for Tobs in (0.1, 0.25, 1.0):
    print(f"    FFT with {Tobs} s window (bin {1/Tobs:.0f} Hz), same NF: Rmax = {rA(undb(Feff), 1/Tobs):.1f} m")
print(f"    Doppler per km/h at 24.125 GHz: {2*fA*(1/3.6)/c:.2f} Hz ; at 10.525 GHz: {2*10.525e9*(1/3.6)/c:.2f} Hz")
check("Doppler per km/h @24.125 GHz ~44 Hz (InnoSenT rule)", 2 * fA / 3.6 / c, 44.7, 0.1)
check("Doppler per km/h @10.525 GHz", 2 * 10.525e9 / 3.6 / c, 19.5, 0.05)

# ---------------- B. 77 GHz TI class
print("B. 77 GHz AWR1843-class FMCW: Pt 12 dBm, NF 15 dB, Gt=Gr=10 dBi (assumed), 128 chirps x 40 us sampled")
fB = 77e9
lamB = c / fB
PtB = undb(12) / 1000
FB = undb(15)
TmeasB = 128 * 40e-6
LB = undb(3.0)                  # window + misc processing losses (assumed)
snr_reqB = undb(15)             # Rao: 15-20 dB typical
targets = {"car (10 dBsm)": 10.0, "person (-5 dBsm)": 10 ** -0.5, "small drone (-15 dBsm)": 10 ** -1.5,
           "hobby rocket tail-on (-20 dBsm, assumed)": 0.01, "corner reflector 10 cm (triangular, see RCS page)": None}
res_B = {}
for name, sg in targets.items():
    if sg is None:
        a = 0.10
        sg = 4 * np.pi * a ** 4 / (3 * lamB ** 2)
        name = name + f" = {db(sg):.1f} dBsm"
    r1 = rmax_mono(PtB, undb(10), undb(10), lamB, sg, TmeasB, snr_reqB, F=FB, L=LB)
    r12 = rmax_mono(PtB, undb(10), undb(10), lamB, sg, TmeasB * 12, snr_reqB, F=FB, L=LB)
    res_B[name] = (r1, r12)
    print(f"    {name:48s}: Rmax 1 virtual ch {r1:7.1f} m ; 12-ch coherent (+10.8 dB) {r12:7.1f} m")
print(f"    (12-channel coherent gain multiplies range by 12^0.25 = {12**0.25:.3f})")

# ---------------- C. MIT coffee-can radar
print("C. Coffee-can FMCW, 2.4 GHz: Pt 10 dBm (assumed), cans ~7 dBi (estimate), NF 6 dB (assumed), 20 ms ramp")
fC = 2.44e9
lamC = c / fC
PtC = undb(10) / 1000
GC = undb(7)
for name, sg in {"car 10 m^2": 10.0, "person 0.5 m^2": 0.5}.items():
    rC = rmax_mono(PtC, GC, GC, lamC, sg, 20e-3, undb(13), F=undb(6), L=undb(3))
    print(f"    {name}: SNR-limited Rmax ~ {rC:.0f} m")
Bsw = 90e6
Tr = 20e-3
S = Bsw / Tr
fbmax = 22.05e3
Rif = fbmax * c / (2 * S)
print(f"    IF-limited Rmax with 44.1 kHz audio card (22.05 kHz) and ~{Bsw/1e6:.0f} MHz/20 ms ramp: {Rif:.0f} m; range res c/2B = {c/(2*Bsw):.2f} m")

# ---------------- D. DIY S-band rocket tracker
print("D. DIY 3 GHz CW/FMCW tracker: Pt 1 W, two 1.2 m dishes (eta 0.55), NF 2 dB, 10 ms CPI, SNR 15 dB, L 3 dB")
fD = 3.0e9
lamD = c / fD
GD = 0.55 * (np.pi * 1.2 / lamD) ** 2
bwD = np.degrees(70 * lamD / 1.2) if False else 70 * lamD / 1.2   # 70 lambda/D degrees (rule of thumb)
print(f"    dish gain {db(GD):.1f} dBi, beamwidth ~ {70*lamD/1.2:.1f} deg")
for sg in (0.01, 0.1, 1.0):
    print(f"    sigma {sg:5.2f} m^2 -> Rmax {rmax_mono(1.0, GD, GD, lamD, sg, 10e-3, undb(15), F=undb(2), L=undb(3))/1000:.2f} km")

# ---------------- E. Search radar
print("E. Search radar (power-aperture): X-band drone surveillance")
Pav, Ae, ts = 10.0, 0.1, 1.0
Omega = np.radians(90) * np.radians(20)
TsE, LE = 500.0, undb(6)
sgE = 0.01
snrE = undb(13)
RE = (Pav * Ae * ts * sgE / (4 * np.pi * Omega * k * TsE * LE * snrE)) ** 0.25
print(f"    Pav {Pav} W, Ae {Ae} m^2, frame {ts} s, Omega {Omega:.3f} sr, Ts {TsE} K, L 6 dB, sigma {sgE} m^2, SNR 13 dB -> R = {RE:.0f} m")
# consistency: search form == track form when the beam dwell t_d = ts * (beam solid angle / Omega)
GE = 4 * np.pi * Ae / (c / 10e9) ** 2
omega_b = 4 * np.pi / GE
td = ts * omega_b / Omega
RE_track = rmax_mono(Pav, GE, GE, c / 10e9, sgE, td, snrE, Ts=TsE, L=LE) * (4 * np.pi * Ae / (GE * (c / 10e9) ** 2)) ** 0.25
check("search form == track form with t_d = t_s*Omega_beam/Omega", RE_track, RE, 1e-9, rel=True)

# ---------------- F. Passive bistatic
print("F. Passive bistatic, FM 98 MHz: ERP 10 kW (assumed), Rx 5 dBi, sigma_b 10 m^2, CAF 1 s, Fa 15 dB (assumed), SNR 13 dB, L 6 dB")
fF = 98e6
lamF = c / fF
ERP = 1e4 * undb(2.15)          # ERP is re dipole -> EIRP
RtRr = (ERP * undb(5) * lamF ** 2 * 10 * 1.0 / ((4 * np.pi) ** 3 * k * T0 * undb(15) * undb(13) * undb(6))) ** 0.5
print(f"    Rt*Rr = {RtRr/1e6:.0f} km^2 ; e.g. Rt = 20 km -> Rr up to {RtRr/20e3/1000:.0f} km (thermal-noise limit; DPI usually dominates)")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
