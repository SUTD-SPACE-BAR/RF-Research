#!/usr/bin/env python3
"""Tiny frequency-domain nodal solver for distributed/lumped RF networks + microstrip helpers.

Used by rfckt_couplers.py, rfckt_baluns.py and others.
    c = Circuit(f)                     # f: array of frequencies (Hz)
    c.line('a', 'b', Z=70.7, f0=2.45e9, deg=90)      # TEM line between node a and node b (ground-referenced)
    c.R('b', 'c', 100); c.C('a', 0, 1e-12); c.L(...)
    c.coupled('a1','a2','b1','b2', Ze, Zo, f0, deg)   # coupled-line 4-port (line A: a1->a2, line B: b1->b2)
    S = c.sparams(['p1','p2','p3'], z0=50)            # S-matrix (nf, P, P)
Node 0 (or 'gnd') is ground.  Lines are ideal TEM unless ee_e/ee_o are passed (then electrical
lengths follow each mode's velocity; 'deg' is interpreted at f0 for the mean velocity).
"""
import numpy as np
from scipy.optimize import brentq

c0 = 299792458.0
eps0 = 8.8541878128e-12


class Circuit:
    def __init__(self, f):
        self.f = np.atleast_1d(np.asarray(f, float))
        self.w = 2 * np.pi * self.f
        self.nodes = {}
        self.stamps = []   # (node list, Y-matrix array (nf,k,k))

    def _n(self, name):
        if name in (0, '0', 'gnd', None):
            return None
        if name not in self.nodes:
            self.nodes[name] = len(self.nodes)
        return self.nodes[name]

    def Y2(self, a, b, y):
        """Two-terminal admittance y (array or scalar) between a and b."""
        y = np.broadcast_to(np.asarray(y, complex), self.f.shape)
        Y = np.zeros((len(self.f), 2, 2), complex)
        Y[:, 0, 0] = y; Y[:, 1, 1] = y; Y[:, 0, 1] = -y; Y[:, 1, 0] = -y
        self.stamps.append(([self._n(a), self._n(b)], Y))

    def R(self, a, b, R):
        self.Y2(a, b, 1.0 / R)

    def C(self, a, b, C, Q=None):
        z = 1 / (1j * self.w * C) + ((1 / (self.w * C)) / Q if Q else 0)
        self.Y2(a, b, 1 / z)

    def L(self, a, b, L, Q=None):
        z = 1j * self.w * L + ((self.w * L) / Q if Q else 0)
        self.Y2(a, b, 1 / z)

    def line(self, a, b, Z, f0, deg, alpha_db_per_wl=0.0, ee=None, length=None):
        """Ground-referenced TEM line from node a to node b; electrical length deg at f0."""
        th = np.deg2rad(deg) * self.f / f0
        att = alpha_db_per_wl / 8.686 * (deg / 360.0) * (self.f / f0)   # Np, crude loss option
        g = att + 1j * th
        Y = np.zeros((len(self.f), 2, 2), complex)
        Y[:, 0, 0] = Y[:, 1, 1] = 1 / (Z * np.tanh(g))
        Y[:, 0, 1] = Y[:, 1, 0] = -1 / (Z * np.sinh(g))
        self.stamps.append(([self._n(a), self._n(b)], Y))

    def coupled(self, a1, a2, b1, b2, Ze, Zo, f0, deg, ee_e=None, ee_o=None):
        """Symmetric coupled pair; line A from a1 to a2, line B from b1 to b2 (a1,b1 at the same end).
        Even/odd decomposition; unequal modal velocities if ee_e/ee_o given (length fixed by mean)."""
        if ee_e is None:
            th_e = th_o = np.deg2rad(deg) * self.f / f0
        else:
            eem = (ee_e + ee_o) / 2
            L = np.deg2rad(deg) / (2 * np.pi * f0 * np.sqrt(eem) / c0)
            th_e = 2 * np.pi * self.f * np.sqrt(ee_e) / c0 * L
            th_o = 2 * np.pi * self.f * np.sqrt(ee_o) / c0 * L
        def yline(Z, th):
            return 1 / (1j * Z * np.tan(th)), -1 / (1j * Z * np.sin(th))   # y11, y12 of a line
        ye11, ye12 = yline(Ze, th_e)
        yo11, yo12 = yline(Zo, th_o)
        # node order: a1, a2, b1, b2 ; even/odd: Y_aa = (Ye+Yo)/2, Y_ab = (Ye-Yo)/2
        Y = np.zeros((len(self.f), 4, 4), complex)
        s11, s12 = (ye11 + yo11) / 2, (ye12 + yo12) / 2
        m11, m12 = (ye11 - yo11) / 2, (ye12 - yo12) / 2
        Y[:, 0, 0] = Y[:, 1, 1] = Y[:, 2, 2] = Y[:, 3, 3] = s11
        Y[:, 0, 1] = Y[:, 1, 0] = Y[:, 2, 3] = Y[:, 3, 2] = s12
        Y[:, 0, 2] = Y[:, 2, 0] = Y[:, 1, 3] = Y[:, 3, 1] = m11
        Y[:, 0, 3] = Y[:, 3, 0] = Y[:, 1, 2] = Y[:, 2, 1] = m12
        self.stamps.append(([self._n(a1), self._n(a2), self._n(b1), self._n(b2)], Y))

    def ymatrix(self):
        N = len(self.nodes)
        Y = np.zeros((len(self.f), N, N), complex)
        for nodes, y in self.stamps:
            for i, ni in enumerate(nodes):
                if ni is None:
                    continue
                for j, nj in enumerate(nodes):
                    if nj is None:
                        continue
                    Y[:, ni, nj] += y[:, i, j]
        return Y

    def sparams(self, ports, z0=50.0):
        """S-matrix with every port terminated in z0.  Uses the terminated nodal matrix
        Yt = Y + diag(1/z0 at ports) (always invertible for a passive network), then
        S = (2/z0) [Yt^-1]_pp - I.  (Kron-reducing to port Y fails when port Y does not exist,
        e.g. two cascaded quarter-wave lines exactly at f0.)"""
        Y = self.ymatrix().copy()
        p = [self.nodes[q] for q in ports]
        z = np.broadcast_to(np.asarray(z0, float), (len(p),)).astype(float)
        for i, zi in zip(p, z):
            Y[:, i, i] += 1.0 / zi
        Zt = np.linalg.inv(Y)
        Zpp = Zt[:, p][:, :, p]
        sq = np.sqrt(z)
        return 2.0 * Zpp / np.outer(sq, sq) - np.eye(len(p))

    def tline_float(self, a1, b1, a2, b2, Z, f0, deg):
        """Two-conductor line with floating conductors (transmission-line-transformer winding on an
        ideal core: common-mode current fully choked). Conductor A runs a1->a2, conductor B b1->b2;
        only the differential (line) mode propagates."""
        th = np.deg2rad(deg) * self.f / f0
        y11 = 1 / (1j * Z * np.tan(th)); y12 = -1 / (1j * Z * np.sin(th))
        Y = np.zeros((len(self.f), 4, 4), complex)
        # port-1 voltage = Va1 - Vb1, port-2 voltage = Va2 - Vb2
        M = np.array([[1, -1, 0, 0], [0, 0, 1, -1]], float)           # (2 x 4) incidence
        Yl = np.zeros((len(self.f), 2, 2), complex)
        Yl[:, 0, 0] = Yl[:, 1, 1] = y11; Yl[:, 0, 1] = Yl[:, 1, 0] = y12
        Y = np.einsum('ki,nkl,lj->nij', M, Yl, M)
        self.stamps.append(([self._n(a1), self._n(b1), self._n(a2), self._n(b2)], Y))


# ------------------------------------------------------------------ microstrip helpers
def hj_z0(w, h, er):
    """Hammerstad-Jensen static microstrip (zero thickness): returns (Z0, eeff)."""
    u = w / h
    a = 1 + np.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49 + np.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * b)
    fu = 6 + (2 * np.pi - 6) * np.exp(-(30.666 / u) ** 0.7528)
    z01 = 60 * np.log(fu / u + np.sqrt(1 + (2 / u) ** 2))
    return z01 / np.sqrt(ee), ee


def width_for(Z, h, er):
    return brentq(lambda w: hj_z0(w, h, er)[0] - Z, 1e-6, 100e-3)


def garg_bahl(w, s, h, er):
    """Garg & Bahl (1979) static coupled microstrip: returns (Z0e, Z0o, ee_e, ee_o)."""
    from scipy.special import ellipk
    z0, ee = hj_z0(w, h, er)
    z0a, _ = hj_z0(w, h, 1.0)
    def caps(er_, z0_, ee_):
        Cp = eps0 * er_ * w / h
        Cf = 0.5 * (np.sqrt(ee_) / (c0 * z0_) - Cp)
        A = np.exp(-0.1 * np.exp(2.33 - 2.53 * w / h))
        Cf2 = Cf / (1 + A * (h / s) * np.tanh(8 * s / h)) * np.sqrt(er_ / ee_)
        k = (s / h) / (s / h + 2 * w / h); kp = np.sqrt(1 - k ** 2)
        Cga = eps0 * ellipk(kp ** 2) / ellipk(k ** 2)
        Cgd = eps0 * er_ / np.pi * np.log(1 / np.tanh(np.pi * s / (4 * h))) + 0.65 * Cf * (0.02 * np.sqrt(er_) / (s / h) + 1 - 1 / er_ ** 2)
        return Cp + Cf + Cf2, Cp + Cf + Cga + Cgd
    Ce, Co = caps(er, z0, ee)
    Cea, Coa = caps(1.0, z0a, 1.0)
    return 1 / (c0 * np.sqrt(Ce * Cea)), 1 / (c0 * np.sqrt(Co * Coa)), Ce / Cea, Co / Coa


def coupled_synth(Ze, Zo, h, er, guess=(1.3e-3, 0.3e-3)):
    from scipy.optimize import minimize
    def res(p):
        w_, s_ = np.exp(p)
        ze, zo, _, _ = garg_bahl(w_, s_, h, er)
        return (ze - Ze) ** 2 + (zo - Zo) ** 2
    best = minimize(res, np.log(guess), method='Nelder-Mead', options=dict(xatol=1e-9, fatol=1e-12, maxiter=6000))
    w_, s_ = np.exp(best.x)
    return (w_, s_) + tuple(garg_bahl(w_, s_, h, er))


if __name__ == '__main__':
    # self-test: a lambda/4 line of Z0 = 50 between two 50-ohm ports is transparent; a 70.7-ohm one transforms 100->50
    f0 = 1e9
    c = Circuit([f0])
    c.line('a', 'b', 50, f0, 90)
    S = c.sparams(['a', 'b'])
    ok = abs(S[0, 0, 0]) < 1e-12 and abs(abs(S[0, 1, 0]) - 1) < 1e-12
    c = Circuit([f0]); c.line('a', 'b', 70.7107, f0, 90); c.R('b', 0, 100.0)
    S = c.sparams(['a'])
    ok &= abs(S[0, 0, 0]) < 1e-5
    c = Circuit([f0]); c.line('a', 'x', 100, f0, 90); c.line('x', 'b', 30, f0, 90)
    S = c.sparams(['a', 'b'])[0]
    ok &= np.allclose(S.conj().T @ S, np.eye(2))          # lossless cascade stays unitary exactly at f0
    print("self-test", "PASS" if ok else "FAIL")
