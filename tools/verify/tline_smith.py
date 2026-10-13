#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/smith-chart.md

Checks:
  1. The map Gamma = (z-1)/(z+1) sends constant-r lines to circles centre (r/(1+r),0), radius 1/(1+r),
     and constant-x lines to circles centre (1, 1/x), radius 1/|x|.
  2. Admittance chart = impedance chart rotated 180 deg: Gamma(y-plane) = -Gamma.
  3. Constant-Q contours |x|/r = Q are arcs of circles through (+-1, 0) with centre (0, -+1/Q), radius sqrt(1+1/Q^2)
     (upper/inductive arc: centre (0, -1/Q)).
  4. Moving a distance d toward the generator rotates Gamma clockwise by 2*beta*d.
  5. Direction rules: series L / shunt C move clockwise on their constant-r / constant-g circle;
     series C / shunt L anticlockwise.
  6. Foster: the Gamma locus of any lossless (and of typical passive) one-port rotates clockwise with frequency.
  7. Conformality: the map preserves angles (derivative non-zero, Cauchy-Riemann).
  8. NanoVNA-style readout conversions (R+jX -> equivalent series L or C, and parallel form).
  9. Stability-circle formula (preview) matches brute-force |Gamma_in| = 1 boundary for an illustrative S-matrix.
  Also writes kb/03-transmission-lines-matching/figures/smith-chart-anatomy.png

Run: python3 tools/verify/tline_smith.py
"""
import os
import numpy as np

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def G(z):
    return (z - 1) / (z + 1)


# ---------------------------------------------------------------- 1. circles
x = np.linspace(-50, 50, 20001)
for r in [0, 0.2, 0.5, 1, 2, 5]:
    g = G(r + 1j * x)
    cen, rad = r / (1 + r), 1 / (1 + r)
    check(f"constant r = {r} -> circle c = {cen:.3f}, R = {rad:.3f}", np.max(np.abs(np.abs(g - cen) - rad)) < 1e-12)
rr = np.linspace(0, 100, 20001)
for xx in [-2, -0.5, 0.5, 1, 3]:
    g = G(rr + 1j * xx)
    check(f"constant x = {xx} -> circle c = (1, {1/xx:.3f}), R = {1/abs(xx):.3f}",
          np.max(np.abs(np.abs(g - (1 + 1j / xx)) - 1 / abs(xx))) < 1e-12)

# ---------------------------------------------------------------- 2. admittance chart
z = 0.3 + 0.8j
check("Gamma of y = 1/z equals -Gamma of z", abs(G(1 / z) + G(z)) < 1e-15)

# ---------------------------------------------------------------- 3. constant-Q circles
for Q in [0.5, 1, 2, 5]:
    rq = np.linspace(1e-4, 100, 20001)
    g = G(rq + 1j * Q * rq)
    # the inductive (upper) arc belongs to a circle centred BELOW the real axis
    check(f"constant Q = {Q} (upper arc) -> circle c = (0, {-1/Q:.3f}), R = {np.sqrt(1+1/Q**2):.3f}",
          np.max(np.abs(np.abs(g + 1j / Q) - np.sqrt(1 + 1 / Q**2))) < 1e-12)

# ---------------------------------------------------------------- 4. line rotation
zl = 0.4 - 0.7j
bd = np.linspace(0, np.pi, 1000)     # beta*d
gd = G(zl) * np.exp(-2j * bd)
ang = np.unwrap(np.angle(gd))
check("moving toward generator: Gamma angle decreases (clockwise) by 2*beta*d", np.allclose(ang[0] - ang, 2 * bd))


# ---------------------------------------------------------------- 5. direction rules
def sense(path, centre):
    """+1 anticlockwise, -1 clockwise (about centre)"""
    a = np.unwrap(np.angle(path - centre))
    return np.sign(a[-1] - a[0])


z0 = 0.5 + 0.3j
s_ = np.linspace(0, 0.5, 200)
r0 = z0.real
y0 = 1 / z0
g0 = y0.real
cz = r0 / (1 + r0)                # constant-r circle centre
cy = -g0 / (1 + g0)               # constant-g circle centre on the impedance-Gamma plane
check("series L (x increasing) -> clockwise on constant-r circle", sense(G(z0 + 1j * s_), cz) < 0)
check("series C (x decreasing) -> anticlockwise on constant-r circle", sense(G(z0 - 1j * s_), cz) > 0)
check("shunt C (b increasing) -> clockwise on constant-g circle", sense(G(1 / (y0 + 1j * s_)), cy) < 0)
check("shunt L (b decreasing) -> anticlockwise on constant-g circle", sense(G(1 / (y0 - 1j * s_)), cy) > 0)

# ---------------------------------------------------------------- 6. Foster / frequency direction
f = np.linspace(100e6, 3e9, 3000)
w = 2 * np.pi * f
Z0 = 50
nets = {
    "series RLC (R=5, L=20 nH, C=3 pF)": 5 + 1j * w * 20e-9 + 1 / (1j * w * 3e-12),
    "parallel LC (lossless 10 nH || 4 pF)": 1 / (1 / (1j * w * 10e-9) + 1j * w * 4e-12),
    "0.1 lambda@1GHz open stub": -1j * 50 / np.tan(2 * np.pi * f / 1e9 * 0.1 + 1e-12),
}
for name, Z in nets.items():
    g = (Z - Z0) / (Z + Z0)
    a = np.unwrap(np.angle(g))
    check(f"Gamma locus rotates clockwise with frequency: {name}", np.all(np.diff(a) < 1e-12))

# ---------------------------------------------------------------- 7. conformality
zz = 0.7 + 0.2j
h = 1e-6
d1 = (G(zz + h) - G(zz)) / h
d2 = (G(zz + 1j * h) - G(zz)) / (1j * h)
check("dGamma/dz independent of direction (analytic => conformal)", abs(d1 - d2) < 1e-5 and abs(d1) > 0)

# ---------------------------------------------------------------- 8. readout conversions
fm = 433e6
Zm = 32.1 - 18.5j
Cser = -1 / (2 * np.pi * fm * Zm.imag)
Ym = 1 / Zm
Rp, Cp = 1 / Ym.real, Ym.imag / (2 * np.pi * fm)
print(f"      marker 433 MHz: Z = {Zm} -> series {Zm.real} ohm + {Cser*1e12:.2f} pF; "
      f"parallel {Rp:.1f} ohm || {Cp*1e12:.2f} pF; Q = {abs(Zm.imag)/Zm.real:.2f}; |Gamma| = {abs((Zm-50)/(Zm+50)):.3f}")
check("series-C readout for 32.1 - j18.5 ohm at 433 MHz = 19.9 pF", abs(Cser * 1e12 - 19.87) < 0.05)
check("series and parallel forms have equal Q", abs(abs(Zm.imag) / Zm.real - Rp * 2 * np.pi * fm * Cp) < 1e-12)

# ---------------------------------------------------------------- 9. stability-circle preview
S11, S12, S21, S22 = 0.6 * np.exp(-1j * np.radians(160)), 0.08 * np.exp(1j * np.radians(30)), \
    4.0 * np.exp(1j * np.radians(70)), 0.5 * np.exp(-1j * np.radians(40))   # illustrative, not a real part
D = S11 * S22 - S12 * S21
CL = np.conj(S22 - D * np.conj(S11)) / (abs(S22) ** 2 - abs(D) ** 2)
RL = abs(S12 * S21 / (abs(S22) ** 2 - abs(D) ** 2))
th = np.linspace(0, 2 * np.pi, 721)
GLc = CL + RL * np.exp(1j * th)
Gin = S11 + S12 * S21 * GLc / (1 - S22 * GLc)
check("output stability circle: |Gamma_in| = 1 on the circle", np.max(np.abs(np.abs(Gin) - 1)) < 1e-9,
      f"(centre {CL:.3f}, radius {RL:.3f})")
K = (1 - abs(S11) ** 2 - abs(S22) ** 2 + abs(D) ** 2) / (2 * abs(S12 * S21))
mu = (1 - abs(S11) ** 2) / (abs(S22 - D * np.conj(S11)) + abs(S12 * S21))
print(f"      illustrative device: K = {K:.3f}, |Delta| = {abs(D):.3f}, mu = {mu:.3f} "
      f"({'unconditionally stable' if mu > 1 else 'potentially unstable'})")
check("K>1 & |Delta|<1  <=>  mu>1 (consistency of the two tests)", ((K > 1) and (abs(D) < 1)) == (mu > 1))

# ---------------------------------------------------------------- 10. lossless networks are disk automorphisms
# Mismatch factor M = (1-|GS|^2)(1-|GL|^2)/|1-GS GL|^2 is the same at every reference plane of a
# lossless network (power is conserved) -> a lossless match can move any point to the centre,
# and the "pseudo-hyperbolic distance" |(GL - GS*)/(1 - GS GL)| is invariant.
def abcd_series(Z):
    return np.array([[1, Z], [0, 1]], dtype=complex)


def abcd_shunt(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)


def abcd_line(Zc, th):
    return np.array([[np.cos(th), 1j * Zc * np.sin(th)], [1j * np.sin(th) / Zc, np.cos(th)]])


def zin(A, ZL):
    return (A[0, 0] * ZL + A[0, 1]) / (A[1, 0] * ZL + A[1, 1])


def zout(A, ZS):
    # impedance looking back into port 2 with ZS on port 1
    return (A[1, 1] * ZS + A[0, 1]) / (A[1, 0] * ZS + A[0, 0])


rng = np.random.default_rng(1)
maxdev = 0
for _ in range(200):
    A = abcd_series(1j * rng.uniform(-80, 80)) @ abcd_shunt(1j * rng.uniform(-0.05, 0.05)) @ \
        abcd_line(rng.uniform(20, 120), rng.uniform(0, np.pi)) @ abcd_series(1j * rng.uniform(-80, 80))
    ZS = rng.uniform(5, 200) + 1j * rng.uniform(-100, 100)
    ZL = rng.uniform(5, 200) + 1j * rng.uniform(-100, 100)
    g = lambda Z: (Z - 50) / (Z + 50)
    GS1, GL1 = g(ZS), g(zin(A, ZL))          # at port 1 plane
    GS2, GL2 = g(zout(A, ZS)), g(ZL)         # at port 2 plane
    M1 = (1 - abs(GS1) ** 2) * (1 - abs(GL1) ** 2) / abs(1 - GS1 * GL1) ** 2
    M2 = (1 - abs(GS2) ** 2) * (1 - abs(GL2) ** 2) / abs(1 - GS2 * GL2) ** 2
    maxdev = max(maxdev, abs(M1 - M2))
check("mismatch factor invariant through 200 random lossless ladder networks", maxdev < 1e-10,
      f"(max |M1-M2| = {maxdev:.1e})")

# ---------------------------------------------------------------- 11. worked example: 25 ohm through lambda/8 of 50 ohm
g25 = G(0.5)
g_in = g25 * np.exp(-2j * np.pi / 4)
z_in = 50 * (1 + g_in) / (1 - g_in)
check("25 ohm load via lambda/8 of 50 ohm line -> 40 + j30 ohm (90 deg clockwise rotation)",
      abs(z_in - (40 + 30j)) < 1e-9, f"({z_in:.2f})")
fL = 915e6
print(f"      figure L-network at 915 MHz: series L = {14.4949/(2*np.pi*fL)*1e9:.2f} nH, "
      f"shunt C = {24.4949e-3/(2*np.pi*fL)*1e12:.2f} pF")

# ---------------------------------------------------------------- figure
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, "..", "..", "kb", "03-transmission-lines-matching", "figures")
    os.makedirs(outdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    t = np.linspace(0, 2 * np.pi, 721)
    ax.plot(np.cos(t), np.sin(t), "k", lw=1.2)
    for r in [0.2, 0.5, 1, 2, 5]:
        c, R = r / (1 + r), 1 / (1 + r)
        ax.plot(c + R * np.cos(t), R * np.sin(t), color="0.6", lw=0.7)
        ax.text(c - R + 0.01, 0.02, f"r={r}", fontsize=7, color="0.3")
    for xx in [0.2, 0.5, 1, 2, 5]:
        for sgn in [1, -1]:
            gg = G(np.linspace(0, 200, 4000) + 1j * sgn * xx)
            ax.plot(gg.real, gg.imag, color="0.6", lw=0.7)
        gtop = G(1j * xx)
        ax.text(gtop.real * 1.07, gtop.imag * 1.07, f"x={xx}", fontsize=7, color="0.3", ha="center")
        ax.text(gtop.real * 1.07, -gtop.imag * 1.07, f"x=-{xx}", fontsize=7, color="0.3", ha="center")
    ax.plot([-1, 1], [0, 0], color="0.6", lw=0.7)
    for Q in [1, 3]:
        rq = np.logspace(-4, 4, 4000)
        for sgn in [1, -1]:
            gg = G(rq + 1j * sgn * Q * rq)
            ax.plot(gg.real, gg.imag, "--", color="tab:purple", lw=1)
        ax.text(0.0, (np.sqrt(1 + 1 / Q**2) - 1 / Q) + 0.02,
                f"Q={Q}", color="tab:purple", fontsize=8, ha="center")
    gv = 1 / 3
    ax.plot(gv * np.cos(t), gv * np.sin(t), color="tab:green", lw=1.2)
    ax.text(0.0, -gv - 0.06, "VSWR = 2 circle", color="tab:green", fontsize=8, ha="center")
    # L-network path: z = 0.4 + 0.2j (20+j10 ohm) -> series L -> shunt C -> centre
    zL = (20 + 10j) / 50
    # solve: shunt C at the 50-ohm side, series element at load side (load R < 50)
    RLd, XLd = 20.0, 10.0
    Qn = np.sqrt(50 / RLd - 1)
    Xs_total = Qn * RLd            # series reactance needed (inductive)
    Xs_add = Xs_total - XLd
    Bsh = Qn / 50
    p1 = G(zL + 1j * np.linspace(0, Xs_add / 50, 200))
    zmid = zL + 1j * Xs_add / 50
    ymid = 1 / zmid
    p2 = G(1 / (ymid + 1j * np.linspace(0, Bsh * 50, 200)))
    ax.plot(p1.real, p1.imag, color="tab:red", lw=2.2, label=f"series L (+j{Xs_add:.1f} ohm)")
    ax.plot(p2.real, p2.imag, color="tab:blue", lw=2.2, label=f"shunt C (+j{Bsh*1e3:.1f} mS)")
    ax.plot(G(zL).real, G(zL).imag, "o", color="tab:red")
    ax.text(G(zL).real + 0.03, G(zL).imag - 0.07, "load 20+j10 ohm", fontsize=8, color="tab:red")
    ax.plot(0, 0, "ko", ms=4)
    # clockwise arrow along the rim = moving toward the generator (and increasing frequency)
    ta = np.radians(np.linspace(-20, -70, 50))
    ax.plot(1.07 * np.cos(ta), 1.07 * np.sin(ta), color="k", lw=1)
    ax.annotate("", xy=(1.07 * np.cos(ta[-1]), 1.07 * np.sin(ta[-1])),
                xytext=(1.07 * np.cos(ta[-2]), 1.07 * np.sin(ta[-2])), arrowprops=dict(arrowstyle="->"))
    ax.text(0.80, -0.98, "toward generator /\nincreasing f: clockwise", fontsize=8)
    ax.text(-1.0, 0.03, "short", fontsize=8)
    ax.text(0.93, 0.03, "open", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.axis("off")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    ax.set_title("Smith chart (impedance, Z0 = 50 ohm): r and x circles, constant-Q arcs,\n"
                 "VSWR circle, and an L-network match of 20+j10 ohm", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "smith-chart-anatomy.png"), dpi=130)
    print(f"      wrote figure {os.path.normpath(os.path.join(outdir, 'smith-chart-anatomy.png'))}")
    print(f"      L-network numbers: Q = {Qn:.3f}, series X added = {Xs_add:.2f} ohm, shunt B = {Bsh*1e3:.3f} mS")
except Exception as e:
    print("      (figure not written:", e, ")")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
