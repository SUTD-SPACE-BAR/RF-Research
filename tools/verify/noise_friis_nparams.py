#!/usr/bin/env python3
"""
noise_friis_nparams.py — verification for kb/07-noise-linearity/noise-figure-and-friis.md

1. Friis cascade: stage noise temperatures injected at each stage input (algebraic check of
   F = F1 + (F2-1)/G1 + ... and Te = Te1 + Te2/G1 + ...), lossy line before an amplifier F = L*F_amp.
2. Two-port noise from first principles: input-referred noise voltage vn and current in with
   correlation coefficient; F(Zs) = 1 + |vn + in Zs|^2 / (4 k T0 Rs B) averaged.
   Extract Fmin, Rn, Yopt numerically and check the standard forms
       F = Fmin + (Rn/Gs) |Ys - Yopt|^2
       F = Fmin + 4 rn |Gs - Gopt|^2 / ((1 - |Gs|^2) |1 + Gopt|^2)      (Gamma form, rn = Rn/Z0)
   and the noise-circle centre/radius formulas.
3. Noise match vs conjugate (gain) match example.
4. SSB vs DSB mixer noise figure.
"""
import numpy as np
k = 1.380649e-23; T0 = 290.0; Z0 = 50.0

print("=== 1. Friis ===")
def friis(F, G):
    tot = F[0]; g = G[0]
    for Fi, Gi in zip(F[1:], G[1:]):
        tot += (Fi - 1)/g; g *= Gi
    return tot
F = [10**(x/10) for x in (1.0, 6.0, 4.0)]; G = [10**(x/10) for x in (15.0, -6.0, 20.0)]
Ft = friis(F, G)
Te = [T0*(f - 1) for f in F]
Te_tot = Te[0] + Te[1]/G[0] + Te[2]/(G[0]*G[1])
print(f"  LNA(1 dB,15 dB) + passive mixer(6 dB loss, NF 6) + IF amp(4 dB, 20 dB): NF = {10*np.log10(Ft):.3f} dB; "
      f"via Te: {10*np.log10(1 + Te_tot/T0):.3f} dB")
for L_db in (1.0, 3.0):
    L = 10**(L_db/10); Fa = 10**(1.0/10)
    print(f"  {L_db} dB loss then NF 1 dB amp: F_tot = L*F_amp -> {10*np.log10(L*Fa):.2f} dB (Friis {10*np.log10(friis([L, Fa], [1/L, 100])):.2f} dB)")

print("\n=== 2. Two-port noise parameters from vn, in, correlation ===")
rng = np.random.default_rng(2)
# choose en (V/rtHz), in (A/rtHz), complex correlation c
en = 0.6e-9; inn = 6e-12; c = 0.4*np.exp(1j*np.radians(50))
def F_of_Zs(Zs):
    Rs = Zs.real
    # |vn + in Zs|^2 expectation with correlation: en^2 + |Zs|^2 in^2 + 2 Re(c* en in Zs*)...
    # model: vn = en*a, in = inn*(c*a + sqrt(1-|c|^2) b), a,b unit complex Gaussians -> E[vn in*] = en inn c*
    s = en**2 + (abs(Zs)**2)*inn**2 + 2*np.real(np.conj(c)*en*inn*np.conj(Zs))
    return 1 + s/(4*k*T0*Rs)
# analytic optimum via the correlation admittance: in = iu + Yc vn, Yc = E[in vn*]/en^2 = inn*c/en
Yc = inn*c/en
Gu = (inn**2*(1 - abs(c)**2))/(4*k*T0)
Rn = en**2/(4*k*T0)
Gopt_y = np.sqrt(Gu/Rn + Yc.real**2); Bopt_y = -Yc.imag
Yopt = Gopt_y + 1j*Bopt_y
Fmin = 1 + 2*Rn*(Gopt_y + Yc.real)
Zopt = 1/Yopt
# brute-force cross-check of the optimum on a grid
R = np.linspace(1, 400, 800); X = np.linspace(-400, 400, 1601)
RR, XX = np.meshgrid(R, X)
FF = F_of_Zs(RR + 1j*XX)
i = np.unravel_index(np.argmin(FF), FF.shape)
print(f"  analytic: Zopt = {Zopt.real:.2f} {Zopt.imag:+.2f}j ohm, Fmin = {10*np.log10(Fmin):.4f} dB, Rn = {Rn:.2f} ohm; "
      f"grid search: Zopt = {RR[i]:.1f} {XX[i]:+.1f}j, Fmin = {10*np.log10(FF[i]):.4f} dB")
# check admittance form on random Zs
errs = []
for _ in range(2000):
    Zs = rng.uniform(5, 300) + 1j*rng.uniform(-300, 300)
    Ys = 1/Zs
    F_form = Fmin + Rn/Ys.real*abs(Ys - Yopt)**2
    errs.append(abs(F_form - F_of_Zs(Zs)))
print(f"  max |F(admittance form) - F(first principles)| = {max(errs):.2e}")
G = lambda Z: (Z - Z0)/(Z + Z0)
Gopt = G(Zopt); rn = Rn/Z0
errs = []
for _ in range(2000):
    Zs = rng.uniform(5, 300) + 1j*rng.uniform(-300, 300)
    Gs = G(Zs)
    F_g = Fmin + 4*rn*abs(Gs - Gopt)**2/((1 - abs(Gs)**2)*abs(1 + Gopt)**2)
    errs.append(abs(F_g - F_of_Zs(Zs)))
print(f"  max |F(Gamma form) - F(first principles)| = {max(errs):.2e}")
print(f"  Gamma_opt = {abs(Gopt):.3f} at {np.degrees(np.angle(Gopt)):.1f} deg, rn = {rn:.3f}")
# noise circle check
Ftarget = Fmin*10**(0.5/10)
N = (Ftarget - Fmin)/(4*rn)*abs(1 + Gopt)**2
C = Gopt/(N + 1); Rad = np.sqrt(N*(N + 1 - abs(Gopt)**2))/(N + 1)
pts = C + Rad*np.exp(1j*np.linspace(0, 2*np.pi, 9)[:-1])
Fs = [Fmin + 4*rn*abs(g - Gopt)**2/((1 - abs(g)**2)*abs(1 + Gopt)**2) for g in pts]
print(f"  0.5 dB noise circle: centre {abs(C):.3f}@{np.degrees(np.angle(C)):.1f} deg, radius {Rad:.3f}; "
      f"F on circle = {min(10*np.log10(Fs)):.4f}..{max(10*np.log10(Fs)):.4f} dB (target {10*np.log10(Ftarget):.4f})")

print("\n=== 3. Noise match vs conjugate match (illustrative pHEMT noise parameters) ===")
Fmin_db, Gopt2, rn2 = 0.5, 0.5*np.exp(1j*np.radians(60)), 0.10
Fm = 10**(Fmin_db/10)
def Fgam(Gs):
    return Fm + 4*rn2*abs(Gs - Gopt2)**2/((1 - abs(Gs)**2)*abs(1 + Gopt2)**2)
for name, Gs in (("noise match Gs = Gopt", Gopt2), ("50 ohm source Gs = 0", 0.0),
                 ("conjugate match to S11 = 0.6@120 deg -> Gs = 0.6@-120", 0.6*np.exp(-1j*np.radians(120)))):
    print(f"  {name:55s}: NF = {10*np.log10(Fgam(Gs)):.2f} dB")

print("\n=== 4. SSB vs DSB mixer NF ===")
for dsb in (5.0, 7.0, 10.0):
    print(f"  DSB NF {dsb:.1f} dB -> SSB NF {10*np.log10(2*10**(dsb/10)):.2f} dB (equal RF and image conversion gain)")
