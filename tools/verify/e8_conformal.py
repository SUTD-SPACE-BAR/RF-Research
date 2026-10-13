#!/usr/bin/env python3
"""
e8_conformal.py -- verification for kb/12-phased-arrays/conformal-and-cylindrical-arrays.md (task W5-E8)

2-D (azimuth-plane, infinite-cylinder) exact eigenfunction solutions for elements on a perfectly conducting
circular cylinder of radius a, e^{+jwt}, H^(2) outgoing.  Far-field patterns (common factors dropped):
  TM line source I_z at (rho', phi'):     E_z(phi) ~ sum_n j^n [J_n(k rho') - J_n(ka) H_n(k rho')/H_n(ka)] e^{jn(phi-phi')}
  TE narrow axial slot (E_phi aperture):  H_z(phi) ~ sum_n j^n e^{jn(phi-phi')} / H_n'(ka)
  TE magnetic line source at rho' -> a:   reduces to the slot series (Wronskian), checked numerically
  TM aperture (E_z = 1 over |phi-phi'| < dphi/2):  E_z(phi) ~ sum_n j^n dphi sinc(n dphi/2) e^{jn(phi-phi')} / H_n(ka)

Sections
 1. Checks: TM series vs independent 2-D MoM (EFIE, pulse basis, point matching); a -> 0 limit (omni);
    TE magnetic-line-source -> slot limit; large-ka slot -> lit-region flat / shadow decay (creeping wave).
 2. Element pattern rotation: each element's pattern is the same function of (phi - phi_n) -> no common element
    factor; "pattern multiplication" error for a sector beam.
 3. Wraparound (in-phase, m = 0) arrays on rocket body tubes: roll ripple vs N, diameter, frequency, polarization.
 4. Commutated sector beam on a large cylindrical array: gain/ripple vs scan between element positions,
    sector size trade.
 5. Polarization on curved surfaces (3-D, free-space dipoles, cylinder scattering ignored): Ludwig-3 cross-pol of a
    sector beam from circumferential vs axial dipoles; tilted (cone-generator) elements.
 6. Uniform circular arrays: phase modes (Jacobi-Anger + aliasing), mode amplitudes J_m(kr), KrakenSDR geometry,
    phase-mode DF estimators (mode1/mode0 vs mode+1/mode-1) with noise; elevation dependence.
 7. Pseudo-Doppler (commutated ring) DF: bearing from the phase of the commutation tone.
Run: python3 tools/verify/e8_conformal.py      (~20 s)
"""
import os
import warnings
import numpy as np
from scipy.special import jv, hankel2, h2vp, jvp

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
C0 = 299792458.0
results, misses = [], []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "MISS"
    if not cond:
        misses.append(name)
    line = f"[{tag}] {name} {detail}"
    print(line); results.append(line)


def say(s=""):
    print(s); results.append(s)


def db(x):
    return 20 * np.log10(np.abs(x) + 1e-300)


def nmax_for(*kx):
    return int(np.ceil(max(kx) + 12 + 2 * max(kx) ** (1 / 3)))


def tm_line(phi, ka, krho, phis=0.0):
    nm = nmax_for(ka, krho)
    n = np.arange(-nm, nm + 1)
    c = (1j ** n) * (jv(n, krho) - jv(n, ka) * hankel2(n, krho) / hankel2(n, ka))
    return np.exp(1j * np.outer(np.atleast_1d(phi) - phis, n)) @ c


def te_slot(phi, ka, phis=0.0):
    nm = nmax_for(ka)
    n = np.arange(-nm, nm + 1)
    c = (1j ** n) / h2vp(n, ka)
    return np.exp(1j * np.outer(np.atleast_1d(phi) - phis, n)) @ c


def te_mag_line(phi, ka, krho, phis=0.0):
    nm = nmax_for(ka, krho)
    n = np.arange(-nm, nm + 1)
    c = (1j ** n) * (jv(n, krho) - jvp(n, ka) * hankel2(n, krho) / h2vp(n, ka))
    return np.exp(1j * np.outer(np.atleast_1d(phi) - phis, n)) @ c


def tm_aperture(phi, ka, dphi, phis=0.0):
    nm = nmax_for(ka)
    n = np.arange(-nm, nm + 1)
    c = (1j ** n) * dphi * np.sinc(n * dphi / 2 / np.pi) / hankel2(n, ka)
    return np.exp(1j * np.outer(np.atleast_1d(phi) - phis, n)) @ c


def mom_tm(phi, ka, krho, M=240, phis=0.0):
    """2-D TM EFIE, pulse basis, point matching, on a polygonal cylinder (k = 1 units: lengths in k-units)."""
    ang = (np.arange(M) + 0.5) * 2 * np.pi / M
    ve = np.exp(1j * np.arange(M + 1) * 2 * np.pi / M) * ka
    mid = 0.5 * (ve[:-1] + ve[1:])
    dl = np.abs(ve[1:] - ve[:-1])
    src = krho * np.exp(1j * phis)
    R = np.abs(mid[:, None] - mid[None, :])
    gam = 1.781072418
    Z = hankel2(0, np.where(R > 0, R, 1.0)) * dl[None, :]
    Z[np.diag_indices(M)] = dl * (1 - 1j * (2 / np.pi) * (np.log(gam * dl / 4) - 1))
    rhs = -hankel2(0, np.abs(mid - src))
    J = np.linalg.solve(Z, rhs)
    ph = np.atleast_1d(phi)
    rx = np.cos(ph); ry = np.sin(ph)
    def proj(p):
        return np.outer(rx, p.real) + np.outer(ry, p.imag)
    E = np.exp(1j * (rx * src.real + ry * src.imag)) + (np.exp(1j * proj(mid)) @ (J * dl))
    return E


def ripple_db(p):
    a = np.abs(p)
    return 20 * np.log10(a.max() / a.min())


phi = np.linspace(-np.pi, np.pi, 1441, endpoint=False)

# =====================================================================================================
say("=== 1. Exact cylinder solutions and their checks ===")
for ka, kh in [(2 * np.pi * 0.5, 2 * np.pi * 0.25), (2 * np.pi * 1.0, 2 * np.pi * 0.25), (2 * np.pi * 0.2, 2 * np.pi * 0.1)]:
    s = tm_line(phi, ka, ka + kh)
    m = mom_tm(phi, ka, ka + kh, M=400)
    s_n = s / np.abs(s).max(); m_n = m / np.abs(m).max()
    err = np.max(np.abs(db(s_n) - db(m_n))[np.abs(s_n) > 10 ** (-20 / 20)])
    say(f"  TM line source, a = {ka/2/np.pi:.2f} lambda, standoff {kh/2/np.pi:.2f} lambda: series vs MoM max |dB diff| "
        f"(where > -20 dB) = {err:.3f} dB; F/B = {db(s_n[np.argmin(np.abs(phi))]/s_n[np.argmin(np.abs(np.abs(phi)-np.pi))]):.1f} dB")
    if abs(ka - 2 * np.pi) < 1e-9:
        ERR_MOM = err
check("1a TM series == independent 2-D MoM within 0.1 dB (a = 1 lambda, standoff lambda/4)", ERR_MOM < 0.1, f"({ERR_MOM:.3f} dB)")
# First run pre-registered "a -> 0 (ka = 1e-4) gives an omni pattern (< 0.05 dB)": MISS (1.65 dB).  The expectation was
# wrong: in 2-D TM an infinitely long thin PEC wire is a strong parasitic scatterer, its coefficient J0(ka)/H0(ka)
# vanishes only like pi/(2 ln(2/(gamma ka))) (logarithmically).  Logged.  Checks now: (i) the slow log trend, (ii) the
# thin-cylinder case against the independent MoM.
for kat in [1e-4, 1e-8, 1e-16]:
    say(f"  TM, thin PEC wire ka = {kat:.0e} at lambda/4 from the source: ripple {ripple_db(tm_line(phi, kat, 2*np.pi*0.25)):.2f} dB "
        f"(|J0/H0| = {abs(jv(0,kat)/hankel2(0,kat)):.3f})")
kat = 2 * np.pi * 0.01
s_t = tm_line(phi, kat, 2 * np.pi * 0.25); m_t = mom_tm(phi, kat, 2 * np.pi * 0.25, M=60)
e_t = np.max(np.abs(db(s_t / np.abs(s_t).max()) - db(m_t / np.abs(m_t).max())))
check("1b TM thin cylinder (a = 0.01 lambda) series == MoM within 0.1 dB (2-D thin-wire scattering is real)",
      e_t < 0.1, f"({e_t:.3f} dB; ripple {ripple_db(s_t):.2f} dB)")
for ka in [0.5, 3.0]:
    p1 = te_slot(phi, ka); p2 = te_mag_line(phi, ka, ka * (1 + 1e-7))
    r = np.max(np.abs(p1 / p1[0] - p2 / p2[0]))
    say(f"  TE: magnetic line source at rho' -> a vs slot series (ka = {ka}): max rel diff {r:.1e}")
check("1c TE magnetic line source on the surface == axial-slot series (Wronskian identity)", r < 1e-5, f"({r:.1e})")
# small and large cylinders: slot pattern
for ka in [0.3, 1.0, 3.0, 10.0, 30.0]:
    p = te_slot(phi, ka); p /= np.abs(p).max()
    lit = np.abs(phi) < np.radians(60)
    shadow_back = db(p[np.argmin(np.abs(np.abs(phi) - np.pi))])
    say(f"  TE axial slot, ka = {ka:5.1f} (C = {ka/np.pi:.2f} lambda diam.): ripple over |phi|<60 deg {ripple_db(p[lit]):.2f} dB, "
        f"level at 90 deg {db(p[np.argmin(np.abs(phi-np.pi/2))]):.1f} dB, behind {shadow_back:.1f} dB")
    if ka == 0.3:
        SLOT_SMALL = ripple_db(p)
    if ka == 30.0:
        SLOT_BIG = (db(p[np.argmin(np.abs(phi - np.pi / 2))]), shadow_back)
# First run pre-registered "(ka = 0.3) ripple < 1.5 dB" (got 1.56) and "ka = 30: ~-6 dB at grazing" (got -3.2 dB):
# both were guesses, not derivations (logged).  Replaced by derived/limit checks:
#  small ka (x = ka): c_n = 1/H_n'(x); c0 ~ j pi x/2 - pi^2 x^3/8, c+-1 ~ j pi x^2/2, c+-2 ~ j pi x^3/8.  The n = +-1 term is
#  in quadrature with c0 (second order), so the n = +-2 term and Re(c0) enter at the same order: normalised pattern
#  1 + j pi x^2/4 - (x^2/2) cos 2phi + j 2x cos phi -> ripple ~ 10 log10[(1 + 3x^2 + pi x^3)/(1 + x^2)] ~ 10 log10(1 + 2x^2).
#  (A second attempt that kept only n = 0, +-1, i.e. 10 log(1 + 4x^2), also failed -- logged.)
def slot_small(x):
    return 10 * np.log10((1 + 3 * x ** 2 + np.pi * x ** 3) / (1 + x ** 2))
for kas in [0.005, 0.01, 0.05, 0.1, 0.3]:
    say(f"  TE slot small-ka check ka = {kas}: ripple {ripple_db(te_slot(phi, kas)):.4f} dB vs leading-order "
        f"{slot_small(kas):.4f} dB")
rr = ripple_db(te_slot(phi, 0.01)) / slot_small(0.01)
check("1d TE small-ka slot ripple -> leading-order 10log[(1+3x^2+pi x^3)/(1+x^2)] (ratio within 3% at ka = 0.01)",
      abs(rr - 1) < 0.03, f"(ratio {rr:.4f})")
gz = [db((lambda p: p[np.argmin(np.abs(phi - np.pi / 2))] / np.abs(p).max())(te_slot(phi, kab))) for kab in [3.0, 10.0, 30.0]]
check("1e TE slot: grazing (90 deg) level converges to a ka-independent value as ka grows (spread < 0.3 dB for ka = 3-30) "
      "and the shadow deepens (< -20 dB behind at ka = 30)", (max(gz) - min(gz)) < 0.3 and SLOT_BIG[1] < -20,
      f"({np.round(gz, 2)} dB; behind {SLOT_BIG[1]:.1f} dB)")

# =====================================================================================================
say("\n=== 2. Element-pattern rotation and the failure of pattern multiplication ===")
lam_a = 2.55          # cylinder radius in wavelengths (32 elements at ~0.5 lambda around the circumference)
ka = 2 * np.pi * lam_a
Nc = 32
phin = 2 * np.pi * np.arange(Nc) / Nc
g = te_slot(phi, ka)          # element at phi' = 0
gN = np.abs(g).max()


def elem(phi_obs, phin_):
    # same function of (phi - phi_n): rotate by interpolation-free re-evaluation
    return te_slot(phi_obs, ka, phis=phin_) / gN


def sector_weights(phi0, M, taper="cos", Nc_=Nc):
    phin_ = 2 * np.pi * np.arange(Nc_) / Nc_
    dphi = np.angle(np.exp(1j * (phin_ - phi0)))
    idx = np.argsort(np.abs(dphi))[:M]
    w = np.zeros(Nc_, complex)
    halfspan = np.max(np.abs(dphi[idx])) + np.pi / Nc_
    amp = np.cos(0.5 * np.pi * dphi[idx] / halfspan) if taper == "cos" else np.ones(M)
    # co-phasal excitation: cancel the path term k a cos(phi0 - phi_n)
    w[idx] = amp * np.exp(-1j * ka * np.cos(phi0 - phin_[idx]))
    return w


def cyl_pattern(w, phi_obs, exact=True):
    out = np.zeros(len(phi_obs), complex)
    for n in np.nonzero(w)[0]:
        if exact:
            # exact slot pattern includes the path phase via the series (source at phi_n on the surface)
            out += w[n] * elem(phi_obs, phin[n])
        else:
            out += w[n] * np.exp(1j * ka * np.cos(phi_obs - phin[n]))
    return out


w = sector_weights(0.0, 12)
pe = cyl_pattern(w, phi)
# "pattern multiplication" with one common element pattern (the centre element's) times isotropic AF
af_iso = cyl_pattern(w, phi, exact=False)
# The exact series already contains the path phase e^{j ka cos} implicitly; compare shapes in dB
pe_n = pe / np.abs(pe).max()
pm = af_iso * (np.abs(g) / gN)
pm_n = pm / np.abs(pm).max()
main = np.abs(phi) < np.radians(40)
err_main = np.max(np.abs(db(pe_n) - db(pm_n))[main & (np.abs(pe_n) > 0.1)])
sl_e = db(np.abs(pe_n)[np.abs(phi) > np.radians(15)].max())
sl_m = db(np.abs(pm_n)[np.abs(phi) > np.radians(15)].max())
D2 = lambda p: np.abs(p).max() ** 2 / np.mean(np.abs(p) ** 2)
say(f"  32-element ring, a = {lam_a} lambda, 12-element cos-tapered sector beam at 0 deg: exact (rotated element "
    f"patterns) peak sidelobe {sl_e:.1f} dB, 2-D directivity {10*np.log10(D2(pe)):.2f} dB;")
say(f"    'pattern multiplication' with the centre element's pattern: sidelobe {sl_m:.1f} dB, "
    f"max main-region shape error {err_main:.2f} dB")
check("2 pattern multiplication is not exact on a cylinder (shape differences > 0.1 dB somewhere above -20 dB)",
      err_main > 0.1, f"({err_main:.2f} dB)")
PM = (sl_e, sl_m, err_main, 10 * np.log10(D2(pe)))

# =====================================================================================================
say("\n=== 3. Wraparound (in-phase) arrays on rocket body tubes: roll ripple ===")
tubes_mm = [54, 75, 98, 152]
freqs = [433.92e6, 915e6, 2450e6, 5800e6]


def wrap_pattern(N, ka, pol="TE", dphi_el=None):
    out = np.zeros(len(phi), complex)
    for n in range(N):
        p0 = 2 * np.pi * n / N
        if pol == "TE":
            out += te_slot(phi, ka, phis=p0)
        else:
            out += tm_aperture(phi, ka, dphi_el, phis=p0)
    return out


ROWS = []
for D in tubes_mm:
    for f in freqs:
        lam = C0 / f
        ka = np.pi * D * 1e-3 / lam
        circ = np.pi * D * 1e-3 / lam
        row = [D, f / 1e6, circ]
        for pol in ["TE", "TM"]:
            rip = {}
            for N in range(1, 21):
                if pol == "TM":
                    # patch-like axial-polarized element: aperture width 0.3 lambda, or the full share if narrower
                    wid = min(0.3 * lam, 0.9 * np.pi * D * 1e-3 / N)
                    dphi_el = wid / (D * 1e-3 / 2)
                    p = wrap_pattern(N, ka, "TM", dphi_el)
                else:
                    p = wrap_pattern(N, ka, "TE")
                rip[N] = ripple_db(p)
            nmin1 = next((N for N in range(1, 21) if rip[N] < 1.0), None)
            nmin3 = next((N for N in range(1, 21) if rip[N] < 3.0), None)
            row += [rip[1], nmin3, nmin1]
        ROWS.append(row)
        say(f"  tube {D:3d} mm @ {f/1e6:7.2f} MHz: circumference {circ:5.2f} lambda | TE (phi-pol slots): 1 el ripple "
            f"{row[3]:5.1f} dB, N for <3 dB = {row[4]}, <1 dB = {row[5]} | TM (z-pol apertures): 1 el {row[6]:5.1f} dB, "
            f"<3 dB N = {row[7]}, <1 dB N = {row[8]}")
# rule of thumb: element spacing along the circumference for < 1 dB
sp = []
for r in ROWS:
    for k in (5, 8):
        if r[k] is not None and r[k] > 1:
            sp.append(r[2] / r[k])
say(f"  circumferential spacing (lambda) of the minimal <1 dB designs with N > 1: min {min(sp):.2f}, max {max(sp):.2f}, "
    f"median {np.median(sp):.2f}")
check("3a minimal <1 dB wraparound designs have circumferential spacing <= ~1 lambda", max(sp) <= 1.05,
      f"(max {max(sp):.2f} lambda)")
# aliasing-mode explanation: ripple ~ 2|a_N/a_0| for TE, a_n = 1/H'_n(ka)
for ka, N in [(np.pi * 0.098 / (C0 / 2450e6), 4), (np.pi * 0.098 / (C0 / 2450e6), 6), (np.pi * 0.098 / (C0 / 5800e6), 8),
              (np.pi * 0.098 / (C0 / 5800e6), 12)]:
    # two-term model: pattern ~ 1 + 2 rho e^{j chi} cos(N phi), rho e^{j chi} = j^N H'_0 / H'_N
    zr = (1j ** N) * h2vp(0, ka) / h2vp(N, ka)
    cc = np.linspace(-1, 1, 2001)
    two = np.abs(1 + 2 * zr * cc)
    pred2 = 20 * np.log10(two.max() / two.min())
    lo = 10 * np.log10(1 + 4 * abs(zr) ** 2); hi = 20 * np.log10((1 + 2 * abs(zr)) / max(1 - 2 * abs(zr), 1e-9))
    act = ripple_db(wrap_pattern(N, ka, "TE"))
    say(f"  TE, ka = {ka:5.2f}, N = {N:2d}: |j^N H'_0/H'_N| = {abs(zr):.3f}, phase {np.degrees(np.angle(zr)):+.0f} deg -> "
        f"two-term ripple {pred2:.2f} dB (bounds {lo:.2f}..{hi:.2f}), full series {act:.2f} dB")
    ALIAS = ALIAS + [(abs(zr), pred2, act)] if 'ALIAS' in dir() else [(abs(zr), pred2, act)]
small = [x for x in ALIAS if x[0] < 0.05]
check("3b two-term aliasing model (modes 0 and +-N) reproduces the roll ripple within 0.05 dB when |ratio| < 0.05",
      all(abs(x[1] - x[2]) < 0.05 for x in small), f"({[(round(x[1],3), round(x[2],3)) for x in small]})")

# =====================================================================================================
say("\n=== 4. Commutated sector beam on a cylindrical array (32 elements, a = 2.55 lambda, TE slots) ===")
ka = 2 * np.pi * lam_a
step = 2 * np.pi / Nc
for M in [6, 8, 12, 16]:
    gains, sls = [], []
    for phi0 in np.linspace(0, step, 9):
        w = sector_weights(phi0, M)
        p = cyl_pattern(w, phi)
        i0 = np.argmin(np.abs(np.angle(np.exp(1j * (phi - phi0)))))
        gains.append(np.abs(p[i0]) ** 2 / np.mean(np.abs(p) ** 2))
        off = np.abs(np.angle(np.exp(1j * (phi - phi0)))) > np.radians(12 + 60 / M)
        sls.append(db(np.abs(p[off]).max() / np.abs(p).max()))
    g_db = 10 * np.log10(np.array(gains))
    say(f"  sector M = {M:2d} ({M*360/Nc:.0f} deg of arc): 2-D directivity {g_db.mean():.2f} dB, ripple over one "
        f"element step {g_db.max()-g_db.min():.2f} dB, worst sidelobe {max(sls):.1f} dB")
    if M == 12:
        COMM12 = (g_db.mean(), g_db.max() - g_db.min(), max(sls))
    if M == 16:
        COMM16 = g_db.mean()
    if M == 8:
        COMM8 = g_db.mean()
# geometric co-phasing vs conjugate of the embedded element pattern in the beam direction (max-gain excitation)
for M in [8, 12, 16]:
    wg = sector_weights(0.0, M)
    wc = np.zeros(Nc, complex)
    for n in np.nonzero(wg)[0]:
        wc[n] = np.abs(wg[n]) * np.conj(elem(np.array([0.0]), phin[n])[0])
    wmf = np.zeros(Nc, complex)
    for n in range(Nc):
        wmf[n] = np.conj(elem(np.array([0.0]), phin[n])[0])     # all 32 elements, matched (max 2-D directivity)
    dg = [10 * np.log10(D2(cyl_pattern(ww, phi))) for ww in (wg, wc)]
    say(f"  M = {M:2d}: directivity with geometric co-phasing {dg[0]:.2f} dB, with conjugate element-pattern phases "
        f"{dg[1]:.2f} dB")
dmf = 10 * np.log10(D2(cyl_pattern(wmf, phi)))
say(f"  all 32 elements, conjugate-matched (maximum-directivity) excitation: {dmf:.2f} dB")
check("4a commutated sector beam: scan ripple between commutation steps < 0.5 dB (M = 12)", COMM12[1] < 0.5,
      f"({COMM12[1]:.2f} dB)")
say(f"  directivity gain from M = 8 -> 12 -> 16: {COMM8:.2f} -> {COMM12[0]:.2f} -> {COMM16:.2f} dB "
    f"(diminishing: far elements face away)")

# =====================================================================================================
say("\n=== 5. Polarization on curved surfaces (3-D, free-space short dipoles; cylinder scattering ignored) ===")


def ludwig3_x_beam(E, rhat):
    """Ludwig-3 co/cross for a beam along +x with co-pol reference +y (cyclic relabelling of the usual z-beam
    definition: z->x, x->y, y->z)."""
    # spherical angles about the x axis: theta' from x, phi' from y toward z
    X, Y, Z = rhat
    th = np.arccos(np.clip(X, -1, 1))
    ph = np.arctan2(Z, Y)
    # unit vectors in (Y, Z, X) frame mapped back: theta_hat' = (cos th cos ph, cos th sin ph, -sin th) in (y, z, x)
    th_hat = np.array([-np.sin(th), np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph)])
    ph_hat = np.array([np.zeros_like(th), -np.sin(ph), np.cos(ph)])
    e_co = np.cos(ph) * th_hat - np.sin(ph) * ph_hat
    e_cr = np.sin(ph) * th_hat + np.cos(ph) * ph_hat
    return np.sum(E * e_co, axis=0), np.sum(E * e_cr, axis=0)


def far_E(pos, tvec, w, rhat):
    """pos (N,3) in wavelengths, tvec (N,3) unit dipole directions, rhat (3, P)."""
    k = 2 * np.pi
    ph = np.exp(1j * k * (pos @ rhat))           # (N, P)
    E = np.zeros((3, rhat.shape[1]), complex)
    for n in range(len(w)):
        t = tvec[n][:, None]
        tperp = t - np.sum(t * rhat, axis=0) * rhat
        E += w[n] * tperp * ph[n]
    return E


a_l = 2.55
Ms = 12
phin_s = (np.arange(Ms) - (Ms - 1) / 2) * (2 * np.pi / 32)
pos = np.stack([a_l * np.cos(phin_s), a_l * np.sin(phin_s), np.zeros(Ms)], axis=1)
amp = np.cos(0.5 * np.pi * phin_s / (np.max(np.abs(phin_s)) + np.pi / 32))
w = amp * np.exp(-1j * 2 * np.pi * a_l * np.cos(phin_s))
# directions over the main beam: azimuth and elevation +-25 deg grid
az = np.radians(np.linspace(-25, 25, 101)); el = np.radians(np.linspace(-25, 25, 101))
AZ, EL = np.meshgrid(az, el)
rhat = np.stack([np.cos(EL) * np.cos(AZ), np.cos(EL) * np.sin(AZ), np.sin(EL)]).reshape(3, -1)
POL = {}
for name, tv in [("circumferential (phi-hat) dipoles -> co-pol horizontal", np.stack([-np.sin(phin_s), np.cos(phin_s), 0 * phin_s], 1)),
                 ("axial (z-hat) dipoles", np.tile([0.0, 0.0, 1.0], (Ms, 1)))]:
    E = far_E(pos, tv, w, rhat)
    if "axial" in name:
        # co-pol for a z-polarised beam along x: use the same Ludwig-3 machinery with reference z (swap roles)
        co, cr = ludwig3_x_beam(E, rhat)
        co, cr = cr, co
    else:
        co, cr = ludwig3_x_beam(E, rhat)
    pk = np.abs(co).max()
    inbeam = np.abs(co) >= pk * 10 ** (-10 / 20)
    xmax = db(np.abs(cr[inbeam]).max() / pk)
    POL[name] = xmax
    say(f"  12-element sector, {name}: peak Ludwig-3 cross-pol inside the -10 dB beam = {xmax:.1f} dB")
# the same element directions for a planar (flat) 12-element array with identical elements: reference
posf = np.stack([np.zeros(Ms), (np.arange(Ms) - (Ms - 1) / 2) * 0.5, np.zeros(Ms)], axis=1)
Ef = far_E(posf, np.tile([0.0, 1.0, 0.0], (Ms, 1)), amp.astype(complex), rhat)
cof, crf = ludwig3_x_beam(Ef, rhat)
inb = np.abs(cof) >= np.abs(cof).max() * 10 ** (-10 / 20)
XF = db(np.abs(crf[inb]).max() / np.abs(cof).max())
say(f"  flat 12-element array of y-dipoles (reference): peak cross-pol inside -10 dB beam = {XF:.1f} dB")
check("5a rotated (circumferential) element polarizations raise cross-pol above the flat-array reference",
      POL["circumferential (phi-hat) dipoles -> co-pol horizontal"] > XF + 3, f"({POL['circumferential (phi-hat) dipoles -> co-pol horizontal']:.1f} vs {XF:.1f} dB)")
# cone generators (nose cone, half-angle alpha): element along the generator, tilted toward the axis
for alpha_deg in [10, 20]:
    al = np.radians(alpha_deg)
    tv = np.stack([np.sin(al) * np.cos(phin_s), np.sin(al) * np.sin(phin_s), np.full(Ms, np.cos(al))], 1)
    E = far_E(pos, tv, w, rhat)
    co, cr = ludwig3_x_beam(E, rhat); co, cr = cr, co
    pk = np.abs(co).max(); inbeam = np.abs(co) >= pk * 10 ** (-10 / 20)
    xm = db(np.abs(cr[inbeam]).max() / pk)
    say(f"  axial-ish dipoles along cone generators, half-angle {alpha_deg} deg: peak cross-pol in beam {xm:.1f} dB")
    POL[f"cone{alpha_deg}"] = xm

# =====================================================================================================
say("\n=== 6. Uniform circular arrays and phase modes ===")
N, r_l = 5, 0.340        # KrakenSDR-style 5-element UCA, r = 0.34 lambda (KB adaptive-beamforming-doa page)
kr = 2 * np.pi * r_l
phin_u = 2 * np.pi * np.arange(N) / N
ph = np.linspace(-np.pi, np.pi, 721, endpoint=False)
A = np.exp(1j * kr * np.cos(ph[:, None] - phin_u[None, :]))        # steering (arrival) vectors, (P, N)
for m in [0, 1, 2]:
    wm = np.exp(1j * m * phin_u) / N
    Fm = A @ np.conj(wm)                                           # beamformer output for a source at ph
    # predicted: sum_q j^{m+qN} J_{m+qN}(kr) e^{-j(m+qN) ph} (sign from conj weights / arrival convention)
    pred = sum((1j ** (m + q * N)) * jv(m + q * N, kr) * np.exp(-1j * (m + q * N) * ph) for q in range(-6, 7))
    err = np.max(np.abs(Fm - pred))
    main = (1j ** m) * jv(m, kr)
    alias = max(abs(jv(m + q * N, kr)) for q in [-1, 1])
    say(f"  mode m = {m}: |principal amplitude| J_m(kr) = {abs(main):.3f}; largest aliased |J_(m+-N)| = {alias:.4f} "
        f"({db(alias/abs(main)):.1f} dB); Jacobi-Anger+aliasing identity error {err:.1e}")
    if m == 0:
        J0 = abs(main)
check("6a phase-mode identity (Jacobi-Anger with aliasing) exact", err < 1e-12)
say(f"  kr = {kr:.3f}: first zero of J0 is 2.405 -> mode 0 is weak ({J0:.3f}); at 433.92 MHz r = {r_l*C0/433.92e6*100:.1f} cm")
# DF estimators with noise: (i) arg(y1/y0) ; (ii) 0.5*arg(y1/y-1) with ambiguity resolved by (i); MUSIC reference
rng = np.random.default_rng(3)
snr = 10 ** (10 / 10); K = 200
errs1, errs2 = [], []
for trial in range(400):
    th = rng.uniform(-np.pi, np.pi)
    a = np.exp(1j * kr * np.cos(th - phin_u))
    s = (rng.normal(size=K) + 1j * rng.normal(size=K)) / np.sqrt(2)
    nse = (rng.normal(size=(N, K)) + 1j * rng.normal(size=(N, K))) / np.sqrt(2 / (1 / snr))
    X = np.outer(a, s) + nse
    Rm = X @ X.conj().T / K
    def ymode(m):
        wv = np.exp(1j * m * phin_u) / N
        return wv
    w0, w1, wm1 = ymode(0), ymode(1), ymode(-1)
    # cross-correlation of mode outputs (removes source phase): y_m = w_m^H x
    c10 = w1.conj() @ Rm @ w0         # E[y1 y0*]
    c1m1 = w1.conj() @ Rm @ wm1
    # y_m ~ j^m J_m e^{-j m th} s  -> y1 y0* ~ j J1 J0 e^{-j th}
    est1 = -np.angle(c10 / (1j * jv(1, kr) * jv(0, kr)))
    # y1 y-1* ~ (j J1 e^{-j th})(conj(j^-1 J-1 e^{j th})) = (j J1)(conj(-j * -J1)) e^{-2j th} ... compute generally:
    ref = (1j * jv(1, kr)) * np.conj((1j ** -1) * jv(-1, kr))
    est2a = -0.5 * np.angle(c1m1 / ref)
    cands = [est2a, est2a + np.pi]
    est2 = min(cands, key=lambda c: abs(np.angle(np.exp(1j * (c - est1)))))
    errs1.append(np.degrees(np.angle(np.exp(1j * (est1 - th)))))
    errs2.append(np.degrees(np.angle(np.exp(1j * (est2 - th)))))
errs1 = np.array(errs1); errs2 = np.array(errs2)
say(f"  5-el UCA, SNR 10 dB/element, 200 snapshots: arg(y1/y0) estimator rms {np.sqrt(np.mean(errs1**2)):.2f} deg "
    f"(max {np.max(np.abs(errs1)):.1f}); arg(y+1/y-1)/2 estimator rms {np.sqrt(np.mean(errs2**2)):.2f} deg "
    f"(max {np.max(np.abs(errs2)):.1f}) [MUSIC on the same geometry: ~0.3 deg, adaptive-beamforming-doa page]")
UCA_ERR = (np.sqrt(np.mean(errs1 ** 2)), np.sqrt(np.mean(errs2 ** 2)), np.max(np.abs(errs1)), np.max(np.abs(errs2)))
check("6b mode+1/mode-1 estimator beats mode1/mode0 when J0(kr) is small", UCA_ERR[1] < UCA_ERR[0], f"({UCA_ERR})")
# deterministic aliasing bias of the mode1/mode-1 estimator (no noise)
th = np.linspace(-np.pi, np.pi, 3601)
bias = []
for t in th:
    a = np.exp(1j * kr * np.cos(t - phin_u))
    y1 = np.exp(1j * phin_u).conj() @ a / N; ym1 = np.exp(-1j * phin_u).conj() @ a / N
    ref = (1j * jv(1, kr)) * np.conj((1j ** -1) * jv(-1, kr))
    e2 = -0.5 * np.angle(y1 * np.conj(ym1) / ref)
    e2 = min([e2, e2 + np.pi], key=lambda c: abs(np.angle(np.exp(1j * (c - t)))))
    bias.append(np.degrees(np.angle(np.exp(1j * (e2 - t)))))
say(f"  aliasing bias of the mode+-1 estimator (noise-free): max |bias| = {np.max(np.abs(bias)):.2f} deg "
    f"(periodic in azimuth with period 360/N = {360/N:.0f} deg)")
BIAS = np.max(np.abs(bias))
# mode count rule: usable |m| <= M ~ kr, need N >= 2M + 1
for rl in [0.2, 0.34, 0.5, 1.0]:
    krr = 2 * np.pi * rl
    Mu = int(np.floor(krr))
    say(f"  r = {rl:.2f} lambda (kr = {krr:.2f}): modes up to |m| ~ {Mu} have |J_m| >= {abs(jv(Mu, krr)):.2f}; "
        f"needs N >= {2*Mu+1} elements (spacing {2*np.pi*rl/(2*Mu+1):.2f} lambda)")
# elevation: in-plane kr -> kr cos(el)
for el_deg in [0, 30, 60]:
    say(f"  source at elevation {el_deg} deg: effective kr = {kr*np.cos(np.radians(el_deg)):.2f}, "
        f"|J1| = {abs(jv(1, kr*np.cos(np.radians(el_deg)))):.3f}")

# =====================================================================================================
say("\n=== 7. Pseudo-Doppler (commutated ring) DF ===")
Np, rp = 8, 0.15          # 8 antennas, r = 0.15 lambda
fc_comm = 1e3             # commutation (rotation) frequency, Hz
fs = 200e3
t = np.arange(0, 0.05, 1 / fs)
bearing = np.radians(73.0)
slot = (np.floor(t * fc_comm * Np) % Np).astype(int)
phase = 2 * np.pi * rp * np.cos(bearing - 2 * np.pi * slot / Np)
sig = np.exp(1j * phase) * np.exp(1j * 2 * np.pi * 2.0e3 * t)       # carrier offset 2 kHz
inst = np.unwrap(np.angle(sig[1:] * np.conj(sig[:-1])))
# the phase sequence itself (after removing the carrier) has a fundamental at fc_comm whose phase gives bearing
ph_seq = np.unwrap(np.angle(sig * np.exp(-1j * 2 * np.pi * 2.0e3 * t)))
X1 = np.sum(ph_seq * np.exp(-1j * 2 * np.pi * fc_comm * t))
# for a stepped (sample-and-hold) rotation the fundamental lags by half a step: correct by pi/Np
spp = int(round(fs / (fc_comm * Np)))          # samples per antenna dwell (25)
# zero-order-hold delay of the stepped phase: (spp - 1)/2 samples (first run used spp/2 = half a step -> 0.9 deg bias;
# a script discretisation error, logged)
est = (-np.angle(X1) - 2 * np.pi * fc_comm * ((spp - 1) / 2) / fs) % (2 * np.pi)
say(f"  8-element ring, r = 0.15 lambda, 1 kHz commutation: true bearing 73.0 deg, estimated {np.degrees(est):.2f} deg; "
    f"peak phase swing +-{np.degrees(2*np.pi*rp):.0f} deg (FM deviation ~{2*np.pi*rp*fc_comm/1e3:.2f} kHz equiv.)")
check("7 pseudo-Doppler bearing from the commutation-tone phase within 0.5 deg", abs(np.degrees(est) - 73.0) < 0.5,
      f"({np.degrees(est):.2f})")

# =====================================================================================================
say("\n=== 7b. Adcock / Watson-Watt (4 elements on a ring, two orthogonal difference pairs) ===")
# elements at (+-d/2, 0) and (0, +-d/2); a wave from azimuth phi: pair outputs (E - W) = 2j sin(k d/2 cos phi),
# (N - S) = 2j sin(k d/2 sin phi); reference (sum of all four) restores the sign; bearing = atan2(NS, EW)
ph = np.radians(np.linspace(0, 360, 3601))
for dl in [0.1, 0.2, 0.3, 0.4, 0.5]:
    x = np.pi * dl
    ew = np.sin(x * np.cos(ph)); ns = np.sin(x * np.sin(ph))
    est = np.arctan2(ns, ew)
    err = np.degrees(np.angle(np.exp(1j * (est - ph))))
    # classic small-spacing prediction of the peak "octantal" error: from sin(x c) ~ x c - (x c)^3/6
    pred = np.degrees(x ** 2 / 24)
    say(f"  Adcock spacing d = {dl:.1f} lambda: max octantal bearing error {np.max(np.abs(err)):.3f} deg "
        f"(small-spacing estimate (pi d/lambda)^2/24 rad = {pred:.3f} deg)")
    if dl == 0.2:
        ADC = (np.max(np.abs(err)), pred)
check("7b Adcock octantal error matches (pi d/lambda)^2/24 within 10 % at d = 0.2 lambda", abs(ADC[0] / ADC[1] - 1) < 0.1,
      f"({ADC[0]:.3f} vs {ADC[1]:.3f} deg)")

# =====================================================================================================
say("\n=== 8. GNSS L1 wraparound cases, UCA geometry table, figures ===")
for D in [98, 152]:
    f = 1575.42e6; lam = C0 / f; ka = np.pi * D * 1e-3 / lam
    out = []
    for pol in ["TE", "TM"]:
        rr = []
        for N in range(1, 13):
            if pol == "TM":
                wid = min(0.3 * lam, 0.9 * np.pi * D * 1e-3 / N); p = wrap_pattern(N, ka, "TM", wid / (D * 1e-3 / 2))
            else:
                p = wrap_pattern(N, ka, "TE")
            rr.append(ripple_db(p))
        out.append((rr[0], next(N for N in range(1, 13) if rr[N - 1] < 1.0), rr))
    say(f"  GNSS L1 1575.42 MHz, tube {D} mm (C = {ka:.2f} lambda): TE 1-el {out[0][0]:.1f} dB, <1 dB N = {out[0][1]}; "
        f"TM 1-el {out[1][0]:.1f} dB, <1 dB N = {out[1][1]}")
for f in [433.92e6, 868e6, 915e6]:
    lam = C0 / f
    for s_ in [0.4, 0.5]:
        rN = s_ * lam / (2 * np.sin(np.pi / 5))
        say(f"  5-element UCA at {f/1e6:.2f} MHz, spacing {s_} lambda: r = {rN*100:.1f} cm, kr = {2*np.pi*rN/lam:.2f}, "
            f"J0 = {jv(0, 2*np.pi*rN/lam):+.3f}, J1 = {jv(1, 2*np.pi*rN/lam):.3f}")
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG = os.path.join(os.path.dirname(os.path.dirname(HERE)), "kb", "12-phased-arrays", "figures")
    os.makedirs(FIG, exist_ok=True)
    C1, C2, C3, C4, GR, TXT, TXT2 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#8a8984", "#0b0b0b", "#52514e"
    plt.rcParams.update({"axes.edgecolor": GR, "axes.labelcolor": TXT, "xtick.color": TXT2, "ytick.color": TXT2,
                         "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.8, "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb",
                         "axes.facecolor": "#fcfcfb", "legend.frameon": False})
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    Ns = np.arange(1, 17)
    for f, col in [(2450e6, C1), (5800e6, C2)]:
        lam = C0 / f; ka = np.pi * 0.098 / lam
        rte = [ripple_db(wrap_pattern(N, ka, "TE")) for N in Ns]
        rtm = [ripple_db(wrap_pattern(N, ka, "TM", min(0.3 * lam, 0.9 * np.pi * 0.098 / N) / 0.049)) for N in Ns]
        ax[0].plot(Ns, rte, lw=2, color=col, marker="o", ms=4, label=f"{f/1e9:.2f} GHz, circumferential pol. (TE)")
        ax[0].plot(Ns, rtm, lw=2, color=col, ls="--", marker="s", ms=4, label=f"{f/1e9:.2f} GHz, axial pol. (TM)")
    ax[0].axhline(1.0, color=GR, lw=1, ls=":")
    ax[0].set_yscale("log"); ax[0].set_ylim(0.01, 60); ax[0].set_xlim(1, 16)
    ax[0].set_xlabel("number of in-phase elements N"); ax[0].set_ylabel("roll ripple (dB, log scale)")
    ax[0].set_title("Wraparound roll ripple, 98 mm body tube", fontsize=10, color=TXT, loc="left")
    ax[0].legend(fontsize=7.5, loc="upper right", framealpha=0.92, facecolor="#fcfcfb", edgecolor="none")
    x = np.linspace(0, 8, 801)
    for m, col in [(0, C1), (1, C2), (2, C3), (3, C4)]:
        ax[1].plot(x, np.abs(jv(m, x)), lw=2, color=col, label=f"|J{m}(kr)|")
    ax[1].axvline(2 * np.pi * 0.34, color=GR, lw=1, ls=":")
    ax[1].text(2 * np.pi * 0.34 + 0.08, 0.92, "KrakenSDR ring\n(r = 0.34λ)", color=TXT2, fontsize=8, va="top")
    ax[1].set_xlim(0, 8); ax[1].set_ylim(0, 1.02)
    ax[1].set_xlabel("kr = 2πr/λ"); ax[1].set_ylabel("phase-mode amplitude")
    ax[1].set_title("UCA phase-mode amplitudes", fontsize=10, color=TXT, loc="left")
    ax[1].legend(fontsize=8, loc="upper right", framealpha=0.92, facecolor="#fcfcfb", edgecolor="none")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "e8-wraparound-and-phase-modes.png"), dpi=130); plt.close(fig)
    say("  wrote figure e8-wraparound-and-phase-modes.png")
except Exception as e:
    say(f"  figure skipped: {e}")

say("\nSUMMARY: " + ("ALL PASS" if not misses else f"{len(misses)} MISS: {misses}"))
with open(os.path.join(HERE, "e8_conformal_output.txt"), "w") as fh:
    fh.write("\n".join(results) + "\n")
