#!/usr/bin/env python3
"""Verification for kb/11-radar/radar-cross-section.md

Run:  python3 tools/verify/radar_rcs.py        (~20 s)

Checks:
  1. Mie series (Bohren & Huffman coefficients) for a sphere, backscatter:
       - PEC limit (m -> large, or explicit PEC coefficients): Rayleigh 9 pi a^2 (ka)^4 for ka << 1,
         optical limit pi a^2 for ka >> 1, first resonance peak ~3.65 pi a^2 near ka ~ 1.
       - Dielectric Rayleigh limit sigma = (pi^5 D^6 / lambda^4) |K|^2, K = (m^2-1)/(m^2+2).
       - "Water-sphere bird" (100 g) at 2.4 / 10 / 24 / 77 GHz with liquid-water permittivity from
         the double-Debye model of ITU-R P.840 (Liebe et al. 1991).
  2. Physical-optics (PO) integrals, sigma = (4 pi/lambda^2)|int_lit (n.k) exp(j 2 k.r) dS|^2:
       - flat plate at normal incidence -> 4 pi A^2 / lambda^2 ; off-normal pattern sinc^2 cos^2.
       - cylinder broadside -> 2 pi a L^2 / lambda (stationary phase).
       - sphere -> pi a^2 (large ka).
  3. Ray-traced (geometric optics) effective area of corner reflectors along their symmetry axis:
       - triangular trihedral: A_eff = a^2/sqrt(3) => sigma = 4 pi a^4 / (3 lambda^2)
       - square trihedral:     A_eff = sqrt(3) a^2  => sigma = 12 pi a^4 / lambda^2
       - dihedral (fold length a, plate width b), symmetric incidence: A_eff = sqrt(2) a b
         => sigma = 8 pi a^2 b^2 / lambda^2
     and the angular falloff of the triangular trihedral's A_eff (its wide acceptance).
  4. Statistical RCS: many random scatterers -> exponential (Swerling 1/2) power pdf, std/mean = 1;
     one dominant (power ratio 1) + many small -> close to chi-square 4 dof (std/mean = 1/sqrt 2).
  5. Corner-reflector design table (printed) for 2.4 / 10.525 / 24.125 / 60 / 77 GHz.
"""
import numpy as np
from scipy import special, integrate

c = 299_792_458.0
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


db = lambda x: 10 * np.log10(x)


# ----------------------------------------------------------------------------- Mie
def riccati(n, z):
    """psi_n(z)=z j_n(z), xi_n(z)=z h_n^(1)(z) and derivatives (complex z allowed for psi)."""
    jn = special.spherical_jn(n, z)
    jnp = special.spherical_jn(n, z, derivative=True)
    psi = z * jn
    dpsi = jn + z * jnp
    return psi, dpsi


def mie_backscatter_eff(x, m, nmax=None):
    """Backscatter efficiency Q_b = sigma/(pi a^2) for sphere size parameter x=ka, relative index m.
    m = None -> perfect electric conductor."""
    if nmax is None:
        nmax = int(x + 4 * x ** (1 / 3) + 10)
    n = np.arange(1, nmax + 1)
    psi_x, dpsi_x = riccati(n, x)
    yn = special.spherical_yn(n, x)
    ynp = special.spherical_yn(n, x, derivative=True)
    jn = special.spherical_jn(n, x)
    jnp = special.spherical_jn(n, x, derivative=True)
    xi = x * (jn + 1j * yn)
    dxi = (jn + 1j * yn) + x * (jnp + 1j * ynp)
    if m is None:
        a = psi_x / xi                      # TM (electric) PEC
        b = dpsi_x / dxi                    # TE (magnetic) PEC
        # Bohren-Huffman convention for PEC: a_n = dpsi/dxi, b_n = psi/xi
        a, b = dpsi_x / dxi, psi_x / xi
    else:
        mx = m * x
        psi_mx, dpsi_mx = riccati(n, mx)
        a = (m * psi_mx * dpsi_x - psi_x * dpsi_mx) / (m * psi_mx * dxi - xi * dpsi_mx)
        b = (psi_mx * dpsi_x - m * psi_x * dpsi_mx) / (psi_mx * dxi - m * xi * dpsi_mx)
    s = np.sum((2 * n + 1) * (-1.0) ** n * (a - b))
    return np.abs(s) ** 2 / x ** 2


print("=" * 78)
print("1. Sphere (Mie series)")
for x in (0.05, 0.1):
    check(f"PEC Rayleigh ka={x}: Qb vs 9(ka)^4", mie_backscatter_eff(x, None), 9 * x ** 4, 0.02, rel=True)
for x in (50.0, 200.0):
    check(f"PEC optical ka={x}: Qb -> 1", mie_backscatter_eff(x, None), 1.0, 0.05)
xs = np.linspace(0.3, 3, 2701)
q = np.array([mie_backscatter_eff(x, None) for x in xs])
ipk = np.argmax(q)
check("PEC first resonance peak Qb (~3.65)", q[ipk], 3.65, 0.05)
check("PEC first resonance at ka (~1.0)", xs[ipk], 1.0, 0.06)
print(f"    PEC sphere: peak sigma/(pi a^2) = {q[ipk]:.3f} at ka = {xs[ipk]:.3f} (circumference = {xs[ipk]:.2f} lambda)")
# large-index dielectric approaches PEC in the optical region only loosely; check Rayleigh dielectric
m = 1.5 + 0.0j
x = 0.02
K = (m ** 2 - 1) / (m ** 2 + 2)
lam = 1.0
a = x * lam / (2 * np.pi)
sig_ray = np.pi ** 5 * (2 * a) ** 6 / lam ** 4 * abs(K) ** 2
check("dielectric Rayleigh sigma = pi^5 D^6 |K|^2/lambda^4", mie_backscatter_eff(x, m) * np.pi * a ** 2, sig_ray, 0.01, rel=True)


def water_eps(f_ghz, T_c=25.0):
    """Double-Debye liquid-water permittivity (ITU-R P.840 / Liebe 1991), e^{j wt}: eps = eps' - j eps''."""
    T = T_c + 273.15
    th = 300.0 / T
    e0 = 77.66 + 103.3 * (th - 1)
    e1 = 0.0671 * e0
    e2 = 3.52
    fp = 20.20 - 146.0 * (th - 1) + 316.0 * (th - 1) ** 2
    fs = 39.8 * fp
    f = f_ghz
    epp = f * (e0 - e1) / (fp * (1 + (f / fp) ** 2)) + f * (e1 - e2) / (fs * (1 + (f / fs) ** 2))
    ep = (e0 - e1) / (1 + (f / fp) ** 2) + (e1 - e2) / (1 + (f / fs) ** 2) + e2
    return ep - 1j * epp


print("    Liquid water permittivity (25 C, P.840 double Debye): "
      + ", ".join(f"{f} GHz: {water_eps(f).real:.1f}-j{-water_eps(f).imag:.1f}" for f in (2.4, 10, 24, 77)))
check("water eps' at 10 GHz, 25 C (~60-64)", water_eps(10).real, 62.5, 2.5)
mass_g = 100.0
a_bird = (3 * mass_g * 1e-6 / (4 * np.pi)) ** (1 / 3)
print(f"    100 g water sphere: radius {a_bird*100:.2f} cm, pi a^2 = {np.pi*a_bird**2*1e4:.1f} cm^2")
bird = {}
for f in (2.4, 5.6, 10.0, 24.125, 77.0):
    lam = c / (f * 1e9)
    x = 2 * np.pi * a_bird / lam
    m_w = np.sqrt(water_eps(f))
    m_w = m_w.real - 1j * m_w.imag       # to exp(-iwt) (Bohren-Huffman) convention: m = n + i k
    m_bh = np.conj(np.sqrt(water_eps(f)))
    sig = mie_backscatter_eff(x, m_bh) * np.pi * a_bird ** 2
    bird[f] = sig
    print(f"    f = {f:6.2f} GHz: ka = {x:5.2f}, sigma = {sig*1e4:7.1f} cm^2 ({db(sig):.1f} dBsm)")
check("100 g water-sphere bird at 10 GHz within 1e-3..1e-2 m^2", float(1e-3 < bird[10.0] < 1e-2), 1.0, 0)

print("=" * 78)
print("2. Physical optics integrals")
lam = 0.0039   # 77 GHz
k = 2 * np.pi / lam
# flat square plate side b at normal incidence: integral = A
b = 0.10
A = b * b
check("plate normal: 4 pi A^2/lambda^2 (dBsm)", db(4 * np.pi * A ** 2 / lam ** 2), db(4 * np.pi * (b * b) ** 2 / lam ** 2), 1e-12)
# off-normal in one principal plane, numerical PO: I = cos(th) * int_-b/2^b/2 exp(j 2 k x sin th) dx * b
for th_deg in (0.5, 1.0, 2.0):
    th = np.radians(th_deg)
    xg = np.linspace(-b / 2, b / 2, 20001)
    I = np.cos(th) * b * np.trapezoid(np.exp(1j * 2 * k * xg * np.sin(th)), xg)
    sig_num = 4 * np.pi / lam ** 2 * abs(I) ** 2
    sig_th = 4 * np.pi * A ** 2 / lam ** 2 * np.cos(th) ** 2 * np.sinc(2 * b * np.sin(th) / lam) ** 2
    check(f"plate PO pattern at {th_deg} deg (sinc^2 cos^2)", sig_num, sig_th, 1e-4, rel=True)
th3 = np.degrees(np.arcsin(0.443 * lam / b))
print(f"    10 cm plate at 77 GHz: peak {db(4*np.pi*A**2/lam**2):.1f} dBsm; two-way -3 dB half-width ~ {th3:.2f} deg (0.443 lambda/b)")
# cylinder broadside, radius ac, length L: I = L ac int_{-pi/2}^{pi/2} cos(phi) exp(j 2 k ac cos phi) dphi
ac, L = 0.05, 1.0
lam_c = c / 24.125e9
kc = 2 * np.pi / lam_c
ph = np.linspace(-np.pi / 2, np.pi / 2, 400001)
I = L * ac * np.trapezoid(np.cos(ph) * np.exp(1j * 2 * kc * ac * np.cos(ph)), ph)
sig_cyl = 4 * np.pi / lam_c ** 2 * abs(I) ** 2
check("cylinder broadside PO vs 2 pi a L^2/lambda", sig_cyl, 2 * np.pi * ac * L ** 2 / lam_c, 0.05, rel=True)
print(f"    100 mm dia x 1 m cylinder broadside at 24.125 GHz: {db(2*np.pi*ac*L**2/lam_c):.1f} dBsm (PO {db(sig_cyl):.1f})")
# sphere PO (large ka): I = 2 pi a^2 int_0^{pi/2} cos(t) sin(t) exp(j 2 k a cos t) dt
asp = 0.1
tt = np.linspace(0, np.pi / 2, 400001)
Isp = 2 * np.pi * asp ** 2 * np.trapezoid(np.cos(tt) * np.sin(tt) * np.exp(1j * 2 * k * asp * np.cos(tt)), tt)
check("sphere PO -> pi a^2 (ka >> 1)", 4 * np.pi / lam ** 2 * abs(Isp) ** 2, np.pi * asp ** 2, 0.02, rel=True)

print("=" * 78)
print("3. Corner reflectors by ray tracing (geometric optics)")
rng = np.random.default_rng(1)


def trace(origin, d, faces, max_bounce=4):
    """faces: list of (axis index, predicate(p) -> bool). Planes are x_i = 0. Returns bounces, final dir."""
    p = origin.copy()
    d = d.copy()
    nb = 0
    last = -1
    for _ in range(max_bounce):
        best_t, best_i = np.inf, -1
        for i, (ax, inside) in enumerate(faces):
            if i == last or abs(d[ax]) < 1e-15:
                continue
            t = -p[ax] / d[ax]
            if t > 1e-12 and t < best_t:
                q = p + t * d
                if inside(q):
                    best_t, best_i = t, i
        if best_i < 0:
            break
        p = p + best_t * d
        d[faces[best_i][0]] *= -1
        last = best_i
        nb += 1
    return nb, d


def eff_area(faces, direction, box, nrays=60000):
    """Fraction of rays (launched over a plane perpendicular to direction, covering 'box' extent) that
    return anti-parallel -> effective area."""
    d = direction / np.linalg.norm(direction)
    # orthonormal basis on the launch plane
    u = np.cross(d, [0.0, 0.0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [0.0, 1.0, 0.0])
    u /= np.linalg.norm(u)
    v = np.cross(d, u)
    center = np.array(box) / 2
    ext = np.linalg.norm(box) * 1.1
    s1 = rng.uniform(-ext, ext, nrays)
    s2 = rng.uniform(-ext, ext, nrays)
    hits = 0
    for i in range(nrays):
        o = center + s1[i] * u + s2[i] * v - 5 * ext * d
        nb, dout = trace(o, d, faces)
        if nb >= 2 and np.dot(dout, -d) > 1 - 1e-9:
            hits += 1
    return hits / nrays * (2 * ext) ** 2


a = 1.0
tri = [(0, lambda q: q[1] >= 0 and q[2] >= 0 and q[1] + q[2] <= a),
       (1, lambda q: q[0] >= 0 and q[2] >= 0 and q[0] + q[2] <= a),
       (2, lambda q: q[0] >= 0 and q[1] >= 0 and q[0] + q[1] <= a)]
sq = [(0, lambda q: 0 <= q[1] <= a and 0 <= q[2] <= a),
      (1, lambda q: 0 <= q[0] <= a and 0 <= q[2] <= a),
      (2, lambda q: 0 <= q[0] <= a and 0 <= q[1] <= a)]
axis = -np.array([1.0, 1.0, 1.0])     # incoming towards the corner along the symmetry axis
Aeff_tri = eff_area(tri, axis, [a, a, a])
Aeff_sq = eff_area(sq, axis, [a, a, a])
check("triangular trihedral A_eff = a^2/sqrt3", Aeff_tri, 1 / np.sqrt(3), 0.03, rel=True)
check("square trihedral A_eff = sqrt3 a^2", Aeff_sq, np.sqrt(3), 0.03, rel=True)
# dihedral: faces x=0 (0<=y<=bw, 0<=z<=af) and y=0 (0<=x<=bw, 0<=z<=af); incidence in xy-plane at 45 deg
af, bw = 1.0, 0.5
dih = [(0, lambda q: 0 <= q[1] <= bw and 0 <= q[2] <= af),
       (1, lambda q: 0 <= q[0] <= bw and 0 <= q[2] <= af)]
Aeff_dih = eff_area(dih, -np.array([1.0, 1.0, 0.0]), [bw, bw, af])
check("dihedral A_eff = sqrt2 a b", Aeff_dih, np.sqrt(2) * af * bw, 0.03, rel=True)
# off-axis falloff of triangular trihedral (rotate about the vertical diagonal)
print("    triangular trihedral effective area vs azimuth offset from symmetry axis (PO sigma ~ A_eff^2):")
base = 1 / np.sqrt(3)            # theoretical on-axis A_eff (MC noise ~1-3 %)
res = []
for off in (0, 10, 20, 30):
    ang = np.radians(off)
    # rotate axis direction about z by 'off'
    R = np.array([[np.cos(ang), -np.sin(ang), 0], [np.sin(ang), np.cos(ang), 0], [0, 0, 1]])
    Ae = eff_area(tri, R @ axis, [a, a, a], nrays=30000)
    res.append((off, Ae))
    print(f"      {off:2d} deg: A_eff/A_eff(0) = {Ae/base:.3f} -> sigma change {20*np.log10(max(Ae,1e-9)/base):6.2f} dB")
check("triangular trihedral still within 3 dB at 10 deg off-axis", float(20 * np.log10(res[1][1] / base) > -3), 1.0, 0)

print("=" * 78)
print("4. Statistics of complex targets (random-phase scatterers)")
rng2 = np.random.default_rng(3)
Ns, trials = 30, 200000
amp = rng2.uniform(0.5, 1.5, Ns)
ph = rng2.uniform(0, 2 * np.pi, (trials, Ns))
sig = np.abs(np.sum(amp * np.exp(1j * ph), axis=1)) ** 2
check("many scatterers: std/mean of RCS -> 1 (exponential, Swerling 1/2)", sig.std() / sig.mean(), 1.0, 0.03)
check("many scatterers: P(sigma < 0.1 mean) -> 1-e^-0.1", np.mean(sig < 0.1 * sig.mean()), 1 - np.exp(-0.1), 0.005)
dom = np.sqrt(np.sum(amp ** 2))          # dominant scatterer with power equal to the rest combined
sig2 = np.abs(dom + np.sum(amp * np.exp(1j * ph), axis=1)) ** 2
print(f"    dominant + many (power ratio 1): std/mean = {sig2.std()/sig2.mean():.3f} (chi2-4dof: {1/np.sqrt(2):.3f}; Rice K=1 exact: {np.sqrt(3)/2:.3f})")
check("dominant+many std/mean between chi2-4 (0.707) and Rice-K1 (0.866)", float(0.69 < sig2.std() / sig2.mean() < 0.9), 1.0, 0)

print("=" * 78)
print("5. Corner-reflector design table (triangular trihedral sigma = 4 pi a^4/(3 lambda^2))")
print("    edge a (cm) | " + " | ".join(f"{f:>7.3f} GHz" for f in (2.4, 10.525, 24.125, 60.0, 77.0)))
for acm in (5, 10, 20, 30):
    aa = acm / 100
    row = [db(4 * np.pi * aa ** 4 / (3 * (c / (f * 1e9)) ** 2)) for f in (2.4, 10.525, 24.125, 60.0, 77.0)]
    print(f"    {acm:11d} | " + " | ".join(f"{v:7.1f} dBsm" for v in row))
tab = 4 * np.pi * 0.1 ** 4 / (3 * (c / 24.125e9) ** 2)
check("10 cm triangular trihedral at 24.125 GHz (dBsm) = 10log(4pi 1e-4/(3 lambda^2))", db(tab), db(4*np.pi*1e-4/(3*(c/24.125e9)**2)), 1e-9)
check("10 cm triangular trihedral at 24.125 GHz ~ 4.3 dBsm", db(tab), 4.33, 0.02)
print(f"    diffraction beamwidth of the returned bundle ~ lambda/a: a=10 cm -> {np.degrees((c/77e9)/0.1):.2f} deg @77 GHz, {np.degrees((c/24.125e9)/0.1):.2f} deg @24 GHz; plate-angle errors must be << this")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
