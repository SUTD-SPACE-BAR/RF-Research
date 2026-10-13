#!/usr/bin/env python3
"""Minimal noisy two-port cascade engine (chain/ABCD noise-correlation matrices).

Method: Hillbrand & Russer, "An efficient method for computer aided noise analysis of
linear amplifier networks", IEEE Trans. Circuits Syst. CAS-23(4), 1976.
Convention: correlation matrices normalised to 2kT (so a resistor R in series has
C_A = [[R, 0], [0, 0]] in these units); noise factor F = 1 + z C_A z^H / Re(Zs), z = [1, Zs].

Elements are stored as (ABCD[nf,2,2], CA[nf,2,2]) tuples.  Build chains with cascade().
Self-test: python3 tools/verify/rfckt_noise2port.py
"""
import numpy as np


def series_z(Z):
    Z = np.atleast_1d(Z).astype(complex)
    n = len(Z)
    A = np.tile(np.eye(2, dtype=complex), (n, 1, 1))
    A[:, 0, 1] = Z
    C = np.zeros((n, 2, 2), complex)
    C[:, 0, 0] = Z.real          # thermal noise of the resistive part (T = T0)
    return A, C


def shunt_y(Y):
    Y = np.atleast_1d(Y).astype(complex)
    n = len(Y)
    A = np.tile(np.eye(2, dtype=complex), (n, 1, 1))
    A[:, 1, 0] = Y
    C = np.zeros((n, 2, 2), complex)
    C[:, 1, 1] = Y.real
    return A, C


def tline(Z0, theta):
    """Lossless line of characteristic impedance Z0 and electrical length theta (rad, array)."""
    theta = np.atleast_1d(theta)
    n = len(theta)
    A = np.zeros((n, 2, 2), complex)
    A[:, 0, 0] = np.cos(theta)
    A[:, 0, 1] = 1j * Z0 * np.sin(theta)
    A[:, 1, 0] = 1j * np.sin(theta) / Z0
    A[:, 1, 1] = np.cos(theta)
    return A, np.zeros((n, 2, 2), complex)


def s_to_abcd(S, z0=50.0):
    S11, S12, S21, S22 = S[:, 0, 0], S[:, 0, 1], S[:, 1, 0], S[:, 1, 1]
    A = np.zeros_like(S)
    A[:, 0, 0] = ((1 + S11) * (1 - S22) + S12 * S21) / (2 * S21)
    A[:, 0, 1] = z0 * ((1 + S11) * (1 + S22) - S12 * S21) / (2 * S21)
    A[:, 1, 0] = ((1 - S11) * (1 - S22) - S12 * S21) / (2 * S21) / z0
    A[:, 1, 1] = ((1 - S11) * (1 + S22) + S12 * S21) / (2 * S21)
    return A


def abcd_to_s(A, z0=50.0):
    a, b, c, d = A[:, 0, 0], A[:, 0, 1] / z0, A[:, 1, 0] * z0, A[:, 1, 1]
    den = a + b + c + d
    S = np.zeros_like(A)
    S[:, 0, 0] = (a + b - c - d) / den
    S[:, 0, 1] = 2 * (a * d - b * c) / den
    S[:, 1, 0] = 2 / den
    S[:, 1, 1] = (-a + b - c + d) / den
    return S


def device(S, fmin_lin, gopt, rn, z0=50.0):
    """Active device from S-parameters + noise parameters (Fmin linear, Gamma_opt, Rn ohm)."""
    A = s_to_abcd(S, z0)
    yopt = (1 - gopt) / (1 + gopt) / z0
    n = len(fmin_lin)
    C = np.zeros((n, 2, 2), complex)
    C[:, 0, 0] = rn
    C[:, 0, 1] = (fmin_lin - 1) / 2 - rn * np.conj(yopt)
    C[:, 1, 0] = np.conj(C[:, 0, 1])
    C[:, 1, 1] = rn * abs(yopt) ** 2
    return A, C


def cascade(*els):
    A, C = els[0]
    A, C = A.copy(), C.copy()
    for A2, C2 in els[1:]:
        C = C + A @ C2 @ np.conj(np.transpose(A, (0, 2, 1)))
        A = A @ A2
    return A, C


def noise_factor(C, Zs=50.0):
    Zs = np.broadcast_to(np.asarray(Zs, complex), (C.shape[0],))
    z = np.stack([np.ones_like(Zs), Zs], axis=1)
    q = np.einsum('ni,nij,nj->n', z, C, np.conj(z)).real
    return 1 + q / Zs.real


def noise_params(C):
    """Return (Fmin, Zopt, Rn) from a chain correlation matrix (2kT units).

    F - 1 = [C11 + 2 Re(C12 Zs*) + C22 |Zs|^2] / Rs.  dF/dXs = 0 -> Xopt = -Im(C12)/C22;
    dF/dRs = 0 -> Ropt = sqrt(C11/C22 - (Im C12 / C22)^2);  Fmin = 1 + 2 (Re C12 + C22 Ropt).
    """
    C11, C12, C22 = C[:, 0, 0].real, C[:, 0, 1], C[:, 1, 1].real
    Rn = C11
    Xopt = -C12.imag / C22
    Ropt = np.sqrt(np.maximum(C11 / C22 - (C12.imag / C22) ** 2, 0))
    Fmin = 1 + 2 * (C12.real + C22 * Ropt)
    return Fmin, Ropt + 1j * Xopt, Rn


def abcd_to_y(A):
    a, b, c, d = A[:, 0, 0], A[:, 0, 1], A[:, 1, 0], A[:, 1, 1]
    Y = np.zeros_like(A)
    Y[:, 0, 0] = d / b
    Y[:, 0, 1] = (b * c - a * d) / b
    Y[:, 1, 0] = -1 / b
    Y[:, 1, 1] = a / b
    return Y


def y_to_abcd(Y):
    y11, y12, y21, y22 = Y[:, 0, 0], Y[:, 0, 1], Y[:, 1, 0], Y[:, 1, 1]
    dY = y11 * y22 - y12 * y21
    A = np.zeros_like(Y)
    A[:, 0, 0] = -y22 / y21
    A[:, 0, 1] = -1 / y21
    A[:, 1, 0] = -dY / y21
    A[:, 1, 1] = -y11 / y21
    return A


def ca_to_cy(A, CA):
    """Chain -> admittance correlation matrix: C_Y = T C_A T^H, T = [[-Y11, 1], [-Y21, 0]]."""
    Y = abcd_to_y(A)
    T = np.zeros_like(A)
    T[:, 0, 0] = -Y[:, 0, 0]; T[:, 0, 1] = 1
    T[:, 1, 0] = -Y[:, 1, 0]
    return Y, T @ CA @ np.conj(np.transpose(T, (0, 2, 1)))


def cy_to_ca(Y, CY):
    """Admittance -> chain: C_A = T C_Y T^H, T = [[0, A12], [1, A22]]."""
    A = y_to_abcd(Y)
    T = np.zeros_like(Y)
    T[:, 0, 1] = A[:, 0, 1]
    T[:, 1, 0] = 1; T[:, 1, 1] = A[:, 1, 1]
    return A, T @ CY @ np.conj(np.transpose(T, (0, 2, 1)))


def parallel_feedback(el, Yfb):
    """Add a passive two-terminal admittance Yfb (array) from port-1 node to port-2 node (shunt-shunt feedback)."""
    A, CA = el
    Y, CY = ca_to_cy(A, CA)
    Yfb = np.asarray(Yfb, complex)
    M = np.array([[1, -1], [-1, 1]], complex)
    Y2 = Y + Yfb[:, None, None] * M
    CY2 = CY + Yfb.real[:, None, None] * M        # thermal noise of the feedback element (2kT units)
    return cy_to_ca(Y2, CY2)


if __name__ == '__main__':
    rng = np.random.default_rng(0)
    ok = True
    # 1. device noise parameters reproduce F = Fmin + Rn/Gs |Ys - Yopt|^2
    n = 200
    fmin = 10 ** (rng.uniform(0.1, 3, n) / 10)
    gopt = rng.uniform(0, 0.8, n) * np.exp(2j * np.pi * rng.random(n))
    rn = rng.uniform(1, 40, n)
    S = np.tile(np.array([[0.5, 0.05], [5.0, 0.4]], complex), (n, 1, 1))
    A, C = device(S, fmin, gopt, rn)
    Gs_ = rng.uniform(0, 0.9, n) * np.exp(2j * np.pi * rng.random(n))
    Zs = 50 * (1 + Gs_) / (1 - Gs_)
    Ys, Yopt = 1 / Zs, (1 - gopt) / (1 + gopt) / 50
    F_ref = fmin + rn / Ys.real * abs(Ys - Yopt) ** 2
    F_ours = noise_factor(C, Zs)
    e1 = np.max(abs(F_ours - F_ref))
    print(f"device F(Zs) vs classical formula: max err {e1:.2e}")
    ok &= e1 < 1e-9
    # 2. extracted Fmin / Zopt round-trip
    Fm, Zo, Rn2 = noise_params(C)
    e2 = max(np.max(abs(Fm - fmin)), np.max(abs(Zo - 50 * (1 + gopt) / (1 - gopt))), np.max(abs(Rn2 - rn)))
    print(f"noise-parameter round trip: max err {e2:.2e}")
    ok &= e2 < 1e-6
    # 3. matched attenuator: F = 1/G (passive network at T0)
    f = np.ones(1)
    R1, R2 = 8.55, 141.9  # ~3 dB T-pad (series, shunt, series) for 50 ohm
    att = cascade(series_z(R1 * f), shunt_y(1 / R2 * f), series_z(R1 * f))
    Sat = abcd_to_s(att[0])
    G = abs(Sat[0, 1, 0]) ** 2
    F = noise_factor(att[1])[0]
    print(f"T-pad: |S21|^2 = {10*np.log10(G):.3f} dB, NF = {10*np.log10(F):.3f} dB (expect equal magnitude)")
    ok &= abs(10 * np.log10(F) + 10 * np.log10(G)) < 0.02
    # 4. Friis check: attenuator (L) + device
    A2, C2 = device(S[:1], fmin[:1], np.zeros(1), rn[:1])
    tot = cascade(att, (A2, C2))
    F_tot = noise_factor(tot[1])[0]
    F_dev = noise_factor(C2)[0]
    print(f"Friis: pad+device NF {10*np.log10(F_tot):.3f} dB vs F1+(F2-1)/G1 = {10*np.log10(F + (F_dev-1)/G):.3f} dB")
    ok &= abs(F_tot - (F + (F_dev - 1) / G)) < 1e-3  # pad output is matched to 50 ohm -> exact Friis
    # 5. chain <-> admittance correlation round trip, and a feedback resistor equals a series resistor
    A3, C3 = device(S[:5], fmin[:5], gopt[:5], rn[:5])
    Yb, CYb = ca_to_cy(A3, C3)
    A4, C4 = cy_to_ca(Yb, CYb)
    e5 = max(np.max(abs(A4 - A3)), np.max(abs(C4 - C3)))
    print(f"C_A -> C_Y -> C_A round trip: max err {e5:.1e}")
    ok &= e5 < 1e-9
    # a 'feedback' admittance around an empty 2-port (ideal thru is singular) -> use a big shunt
    # check instead: resistor Rf between the ports of a 2-port made of two tiny shunt conductances
    g = 1e-9 * np.ones(1)
    base = cascade(shunt_y(g), shunt_y(g))  # effectively open 2-port with ports tied?  not usable
    Rf = 75.0
    el = cascade(shunt_y(1e-12 * np.ones(1)), series_z(1e6 * np.ones(1)), shunt_y(1e-12 * np.ones(1)))
    fb = parallel_feedback(el, np.array([1 / Rf]))
    ser = series_z(np.array([1 / (1 / Rf + 1 / 1e6)]))
    e6 = abs(noise_factor(fb[1])[0] - noise_factor(ser[1])[0])
    print(f"feedback-R vs series-R noise factor: err {e6:.1e}")
    ok &= e6 < 1e-6
    print("ALL PASS" if ok else "FAIL")
