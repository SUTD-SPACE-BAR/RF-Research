#!/usr/bin/env python3
"""
ant_patch.py -- rectangular microstrip patch design & checks for kb/08-antennas/patch-antennas.md

Design model (transmission-line model, Balanis 4th ed. sec. 14.2; Hammerstad 1975 fringing):
    W     = c / (2 f) * sqrt(2 / (er + 1))
    eeff  = (er + 1)/2 + (er - 1)/2 * (1 + 12 h / W)^(-1/2)
    dL    = 0.412 h (eeff + 0.3)(W/h + 0.264) / ((eeff - 0.258)(W/h + 0.8))
    L     = c / (2 f sqrt(eeff)) - 2 dL
Performance (cavity-model CAD formulas of Jackson & Alexopoulos 1991 / Jackson, Volakis
Antenna Engineering Handbook ch. 7, as given in Jackson's U. Houston notes):
    1/Q = 1/Qd + 1/Qc + 1/Qsp + 1/Qsw,  Qd = 1/tan d,  Qc = (eta0/2)(k0 h)/Rs,
    Qsp = (3/16)(er/(p c1))(L/W)/(h/lam0),  Qsw = Qsp * e_hed/(1 - e_hed),
    e_hed = 1/(1 + (3/4) pi (k0 h)(1/c1)(1 - 1/er)^3),  c1 = 1 - 1/er + 0.4/er^2,
    p = 1 + a2/10 (k0W)^2 + (a2^2 + 2 a4)(3/560)(k0W)^4 + c2/5 (k0L)^2 + a2 c2/70 (k0W)^2 (k0L)^2
    BW(VSWR<2) = 1/(sqrt(2) Q),   e_rad = (1/Qsp)/(1/Q)  [radiated / total]
    R_edge = (4 eta0/pi)(L/W)(h/lam0) / [tan d + Rs/(pi eta0 (h/lam0)) + (16/3)(p c1/er)(W/L)(h/lam0)/e_hed]
    R_in(x0) = R_edge cos^2(pi x0 / L)   (x0 measured from the patch centre for a probe;
                                          for an inset from the edge, use cos^2(pi y0/L) with
                                          y0 = inset depth -- same thing, different origin)
Directivity: numerical integration of the two-slot (magnetic-current) cavity-model pattern over
the upper hemisphere of an infinite ground plane (ignores substrate/surface waves).
CP: two-mode (nearly-square / truncated-corner) model -- two orthogonal parallel-RLC modes;
    axial ratio vs frequency, shows the required mode split f2 - f1 = f0/Q.

Run: python3 tools/verify/ant_patch.py
"""
import numpy as np

C0 = 299792458.0
MU0 = 4e-7 * np.pi
ETA0 = 376.730313668
_trapz = getattr(np, "trapezoid", None) or np.trapz


def design(f, er, h):
    W = C0 / (2 * f) * np.sqrt(2 / (er + 1))
    eeff = (er + 1) / 2 + (er - 1) / 2 / np.sqrt(1 + 12 * h / W)
    dL = 0.412 * h * (eeff + 0.3) * (W / h + 0.264) / ((eeff - 0.258) * (W / h + 0.8))
    L = C0 / (2 * f * np.sqrt(eeff)) - 2 * dL
    return W, L, eeff, dL


def jackson(f, er, h, W, L, tand, sigma=5.8e7, rough=1.0):
    lam0 = C0 / f
    k0 = 2 * np.pi / lam0
    Rs = rough * np.sqrt(2 * np.pi * f * MU0 / (2 * sigma))
    c1 = 1 - 1 / er + 0.4 / er ** 2
    a2, a4, c2 = -0.16605, 0.00761, -0.0914153
    p = (1 + a2 / 10 * (k0 * W) ** 2 + (a2 ** 2 + 2 * a4) * 3 / 560 * (k0 * W) ** 4
         + c2 / 5 * (k0 * L) ** 2 + a2 * c2 / 70 * (k0 * W) ** 2 * (k0 * L) ** 2)
    e_hed = 1 / (1 + 0.75 * np.pi * (k0 * h) / c1 * (1 - 1 / er) ** 3)
    Qd = 1 / tand if tand > 0 else np.inf
    if er <= 1.0:
        e_hed = 1.0 - 1e-12
    Qc = (ETA0 / 2) * (k0 * h) / Rs
    Qsp = 3 / 16 * er / (p * c1) * (L / W) / (h / lam0)
    Qsw = Qsp * e_hed / (1 - e_hed)
    Q = 1 / (1 / Qd + 1 / Qc + 1 / Qsp + 1 / Qsw)
    BW = 1 / (np.sqrt(2) * Q)
    e_rad = (1 / Qsp) / (1 / Q)
    Redge = (4 * ETA0 / np.pi) * (L / W) * (h / lam0) / (
        tand + Rs / (np.pi * ETA0 * (h / lam0)) + 16 / 3 * (p * c1 / er) * (W / L) * (h / lam0) / e_hed)
    return dict(Q=Q, Qd=Qd, Qc=Qc, Qsp=Qsp, Qsw=Qsw, BW=BW, e_rad=e_rad, e_hed=e_hed,
                Redge=Redge, p=p, c1=c1)


def directivity_two_slot(f, W, Leff):
    """Two y-directed magnetic line currents (length W) at x = +/- Leff/2 over infinite ground."""
    k = 2 * np.pi * f / C0
    th = np.linspace(0, np.pi / 2, 721)
    ph = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    X = k * W / 2 * np.sin(TH) * np.sin(PH)
    sinc = np.where(np.abs(X) < 1e-12, 1.0, np.sin(X) / np.where(np.abs(X) < 1e-12, 1, X))
    AF = np.cos(k * Leff / 2 * np.sin(TH) * np.cos(PH))
    U = (np.cos(PH) ** 2 + (np.cos(TH) * np.sin(PH)) ** 2) * sinc ** 2 * AF ** 2
    Prad = _trapz(np.sum(U, axis=1) * (ph[1] - ph[0]) * np.sin(th), th)
    U0 = U[0, 0]
    # E-plane (phi=0) and H-plane (phi=90) half-power beamwidths
    def hpbw(col):
        u = U[:, col] / U[0, col]
        idx = np.where(u < 0.5)[0]
        return 2 * np.degrees(th[idx[0]]) if len(idx) else 180.0
    return 4 * np.pi * U0 / Prad, hpbw(0), hpbw(len(ph) // 4)


def inset_depth(Redge, L, R0=50.0):
    return L / np.pi * np.arccos(np.sqrt(R0 / Redge)) if Redge > R0 else 0.0


def ms_width(Z0, er, h):
    """Microstrip width for Z0 (Hammerstad/Wheeler synthesis, as in Pozar 4th ed. eq. 3.197)."""
    A = Z0 / 60 * np.sqrt((er + 1) / 2) + (er - 1) / (er + 1) * (0.23 + 0.11 / er)
    B = 377 * np.pi / (2 * Z0 * np.sqrt(er))
    wh = 8 * np.exp(A) / (np.exp(2 * A) - 2)
    if wh > 2:
        wh = 2 / np.pi * (B - 1 - np.log(2 * B - 1) + (er - 1) / (2 * er) * (np.log(B - 1) + 0.39 - 0.61 / er))
    return wh * h


def cp_two_mode(f0, Q, split):
    """Axial ratio (dB) vs frequency for two orthogonal modes with resonances f1, f2 = f0(1 -/+ split/2)
    each modelled as a parallel RLC (equal R), fed equally (diagonal / corner-truncated patch)."""
    f = np.linspace(f0 * (1 - 4 / Q), f0 * (1 + 4 / Q), 4001)
    f1, f2 = f0 * (1 - split / 2), f0 * (1 + split / 2)
    V1 = 1 / (1 + 1j * Q * (f / f1 - f1 / f))
    V2 = 1 / (1 + 1j * Q * (f / f2 - f2 / f))
    # field components Ex ~ V1, Ey ~ V2; axial ratio from the polarization ellipse
    ER = np.abs(V1 + 1j * V2) / np.sqrt(2)
    EL = np.abs(V1 - 1j * V2) / np.sqrt(2)
    AR = (ER + EL) / np.maximum(np.abs(ER - EL), 1e-15)
    return f, 20 * np.log10(AR)


def main():
    cases = [
        ("GNSS L1 1575.42 MHz, FR-4 1.6 mm", 1575.42e6, 4.4, 1.6e-3, 0.02),
        ("GNSS L1 1575.42 MHz, RO4003C 1.524 mm", 1575.42e6, 3.55, 1.524e-3, 0.0027),
        ("GNSS L1 1575.42 MHz, ceramic er=20, 4 mm", 1575.42e6, 20.0, 4.0e-3, 0.0005),
        ("2.45 GHz, FR-4 1.6 mm", 2.45e9, 4.4, 1.6e-3, 0.02),
        ("2.45 GHz, RO4003C 1.524 mm", 2.45e9, 3.55, 1.524e-3, 0.0027),
        ("5.8 GHz, FR-4 1.6 mm", 5.8e9, 4.3, 1.6e-3, 0.02),
        ("5.8 GHz, RO4350B 0.762 mm", 5.8e9, 3.66, 0.762e-3, 0.0037),
        ("915 MHz, FR-4 1.6 mm", 915e6, 4.5, 1.6e-3, 0.02),
        ("915 MHz, air/foam 6 mm", 915e6, 1.05, 6.0e-3, 0.0005),
        ("433 MHz, air 10 mm (why patches are rare at 433)", 433e6, 1.0, 10e-3, 0.0),
    ]
    print(f"{'case':46s} {'W mm':>7s} {'L mm':>7s} {'eeff':>6s} {'dL mm':>6s} {'h/lam':>7s} {'BW%':>6s} "
          f"{'e_rad%':>6s} {'D dBi':>6s} {'G dBi':>6s} {'Redge':>6s} {'inset mm':>8s} {'50ohm w':>7s}")
    cad_D = []
    for (name, f, er, h, tand) in cases:
        W, L, eeff, dL = design(f, er, h)
        j = jackson(f, er, h, W, L, tand)
        D, bwE, bwH = directivity_two_slot(f, W, L + 2 * dL)
        G = 10 * np.log10(D * j["e_rad"])
        x_in = inset_depth(j["Redge"], L)
        w50 = ms_width(50, er, h)
        Dj = 3 / (j["p"] * j["c1"]) * er / (er + np.tan(2*np.pi*f/C0*np.sqrt(er)*h) ** 2) * \
            (np.tan(2*np.pi*f/C0*np.sqrt(er)*h) / (2*np.pi*f/C0*np.sqrt(er)*h)) ** 2 if er > 1.0 else 3 / (j["p"] * j["c1"])
        cad_D.append((name, 10*np.log10(D), 10*np.log10(Dj)))
        print(f"{name:46s} {W*1e3:7.2f} {L*1e3:7.2f} {eeff:6.3f} {dL*1e3:6.3f} {h*f/C0:7.4f} "
              f"{100*j['BW']:6.2f} {100*j['e_rad']:6.1f} {10*np.log10(D):6.2f} {G:6.2f} {j['Redge']:6.0f} "
              f"{x_in*1e3:8.2f} {w50*1e3:7.2f}")
    print("\nDirectivity: two-slot pattern integration vs Jackson CAD D = 3/(p c1) * er tanc^2(k1 h)/(er + tan^2(k1 h)):")
    for (n, a, b) in cad_D:
        print(f"   {n:46s} two-slot {a:5.2f} dBi   Jackson CAD {b:5.2f} dBi")
    print("\nNotes: inset depth measured from the radiating edge along L so that R = 50 ohm (cos^2 law);")
    print("       D from the two-slot cavity-model pattern (infinite ground, no substrate); G = D * e_rad.")

    # detail for one case
    f, er, h, tand = 2.45e9, 4.4, 1.6e-3, 0.02
    W, L, eeff, dL = design(f, er, h)
    j = jackson(f, er, h, W, L, tand)
    D, bwE, bwH = directivity_two_slot(f, W, L + 2 * dL)
    print(f"\nDetail 2.45 GHz FR-4 1.6 mm: Qd={j['Qd']:.0f} Qc={j['Qc']:.0f} Qsp={j['Qsp']:.1f} Qsw={j['Qsw']:.0f} "
          f"-> Q={j['Q']:.1f}; e_hed(surface-wave eff.)={j['e_hed']:.3f}; HPBW E/H = {bwE:.0f}/{bwH:.0f} deg")
    # sensitivity: er tolerance on FR-4
    for erx in [4.2, 4.4, 4.6]:
        eeffx = (erx + 1) / 2 + (erx - 1) / 2 / np.sqrt(1 + 12 * h / W)
        dLx = 0.412 * h * (eeffx + 0.3) * (W / h + 0.264) / ((eeffx - 0.258) * (W / h + 0.8))
        fr = C0 / (2 * (L + 2 * dLx) * np.sqrt(eeffx))
        print(f"   same copper, er = {erx}: resonance = {fr/1e6:.0f} MHz ({(fr/f-1)*100:+.1f} %)")
    # thickness sweep: bandwidth and efficiency vs h/lambda for er=2.2 and 10.8 (compare Jackson notes: ~3% at h/lam=0.02, er=2.2)
    print("\nBandwidth (VSWR<2) and radiation efficiency vs h/lambda0 (lossless materials, W=1.5L as in Jackson's plots):")
    for er in [2.2, 10.8]:
        row = []
        for hl in [0.01, 0.02, 0.04, 0.06]:
            lam = C0 / 1e9; h_ = hl * lam
            # choose L from design then set W = 1.5 L (Jackson's convention)
            _, L_, _, _ = design(1e9, er, h_)
            W_ = 1.5 * L_
            jj = jackson(1e9, er, h_, W_, L_, 0.0, sigma=1e30)
            row.append(f"h/lam={hl}: BW={100*jj['BW']:.1f}% e_sw={100*jj['e_rad']:.0f}%")
        print(f"   er={er}: " + "; ".join(row))

    print("\nCP (nearly-square / truncated-corner) two-mode model, Q = 30:")
    Q = 30
    for split_factor in [0.5, 1.0, 1.5]:
        fr, AR = cp_two_mode(1.0, Q, split_factor / Q)
        i0 = np.argmin(AR)
        good = fr[AR < 3]
        bw = (good.max() - good.min()) * 100 if len(good) else 0
        print(f"   mode split (f2-f1)/f0 = {split_factor:.1f}/Q: min AR = {AR[i0]:.2f} dB at f/f0 = {fr[i0]:.4f}, "
              f"3-dB AR bandwidth = {bw:.2f} %  (VSWR-2 impedance BW of one mode = {100/(np.sqrt(2)*Q):.2f} %)")


if __name__ == "__main__":
    main()
