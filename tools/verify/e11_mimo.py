#!/usr/bin/env python3
"""e11_mimo.py — checks for kb/10-comms-modulation/mimo-capacity-and-channel-estimation.md (W5-E11).

1. MIMO capacity: log-det = sum over singular values; water-filling closed form = numerical optimum;
   ergodic 1x1 Rayleigh capacity = log2(e) e^{1/rho} E1(1/rho); high-SNR slope = min(Nt, Nr) b/s/Hz per 3 dB.
2. Diversity: BPSK over Rayleigh with L-branch MRC vs closed form; Alamouti 2x1 = 1x2 MRC minus 3 dB.
3. Channel estimation: LS and MMSE MSE with orthogonal pilots vs theory.
4. OFDM comb pilots: LS + DFT interpolation vs linear interpolation; aliasing when pilot spacing > N/L.
5. Ground-station diversity: selection diversity outage with correlated Rayleigh branches; two-ray
   height-diversity null spacing lambda/(2 sin psi).

Run: python3 tools/verify/e11_mimo.py     (~20 s)
"""
import numpy as np
from scipy import optimize, special

rng = np.random.default_rng(11)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def crandn(*s):
    return (rng.standard_normal(s) + 1j * rng.standard_normal(s)) / np.sqrt(2)


def waterfill(lam, P, N0=1.0):
    """Powers p_i = (mu - N0/lam_i)^+ with sum p_i = P (lam_i = sigma_i^2)."""
    lam = np.sort(lam)[::-1]
    for k in range(len(lam), 0, -1):
        mu = (P + np.sum(N0 / lam[:k])) / k
        p = mu - N0 / lam[:k]
        if p[-1] > 0:
            return np.concatenate([p, np.zeros(len(lam) - k)]), lam
    return None


def part1():
    print("1. MIMO capacity")
    H = crandn(4, 4)
    snr = 10.0
    c_det = np.log2(np.linalg.det(np.eye(4) + snr / 4 * H @ H.conj().T).real)
    s = np.linalg.svd(H, compute_uv=False)
    c_svd = np.sum(np.log2(1 + snr / 4 * s ** 2))
    check("log-det capacity = sum over singular values", abs(c_det - c_svd) < 1e-9, f"{c_det:.4f} b/s/Hz")
    for P in (1.0, 10.0, 100.0):
        p, lam = waterfill(s ** 2, P)
        c_wf = np.sum(np.log2(1 + p * lam))
        cons = {"type": "eq", "fun": lambda q: np.sum(q) - P}
        r = optimize.minimize(lambda q: -np.sum(np.log2(1 + np.maximum(q, 0) * lam)), np.full(4, P / 4),
                              constraints=[cons], bounds=[(0, P)] * 4, method="SLSQP")
        c_eq = np.sum(np.log2(1 + P / 4 * lam))
        print(f"   P/N0 = {10*np.log10(P):4.0f} dB: water-filling {c_wf:.4f} (numerical {-r.fun:.4f}), equal power {c_eq:.4f};"
              f" powers {np.round(p, 3)}")
        check(f"water-filling closed form = numerical optimum (P/N0 {10*np.log10(P):.0f} dB)", abs(c_wf + r.fun) < 1e-3)
    # ergodic 1x1 Rayleigh
    for rho_db in (0, 10, 20):
        rho = 10 ** (rho_db / 10)
        h2 = np.abs(crandn(400000)) ** 2
        mc = np.mean(np.log2(1 + rho * h2))
        cf = np.log2(np.e) * np.exp(1 / rho) * special.exp1(1 / rho)
        print(f"   1x1 Rayleigh {rho_db:2d} dB: Monte Carlo {mc:.4f}, closed form {cf:.4f}, AWGN {np.log2(1+rho):.4f}")
        check(f"ergodic 1x1 Rayleigh capacity closed form ({rho_db} dB)", abs(mc - cf) < 0.01)
    # slopes
    for nt, nr in ((1, 1), (2, 2), (4, 4), (4, 2)):
        cs = []
        for rho_db in (27, 30):
            rho = 10 ** (rho_db / 10)
            Hs = crandn(4000, nr, nt)
            M = np.eye(nr) + rho / nt * Hs @ np.conj(np.transpose(Hs, (0, 2, 1)))
            cs.append(np.mean(np.log2(np.linalg.det(M).real)))
        slope = cs[1] - cs[0]
        print(f"   {nt}x{nr}: ergodic C at 30 dB = {cs[1]:.2f} b/s/Hz, slope per 3 dB = {slope:.2f} (min = {min(nt,nr)})")
        check(f"high-SNR slope ~ min(Nt,Nr) for {nt}x{nr}", abs(slope / min(nt, nr) - 1) < 0.08, f"{slope:.2f}")
    # rank-1 LOS: array gain only
    a = np.ones((2, 1)); b = np.ones((1, 2))
    Hlos = a @ b
    sl = np.linalg.svd(Hlos, compute_uv=False)
    check("rank-1 LOS 2x2: one singular value, sigma^2 = Nt*Nr = 4", abs(sl[0] ** 2 - 4) < 1e-12 and sl[1] < 1e-12)


def part2():
    print("2. Diversity: MRC and Alamouti (BPSK, Rayleigh)")
    n = 400000
    for snr_db in (10, 15):
        g = 10 ** (snr_db / 10)
        for L in (1, 2, 4):
            mu = np.sqrt(g / (1 + g))
            pb = ((1 - mu) / 2) ** L * sum(special.comb(L - 1 + k, k) * ((1 + mu) / 2) ** k for k in range(L))
            bits = rng.integers(0, 2, n); s = 2 * bits - 1
            h = crandn(n, L)
            y = h * s[:, None] + crandn(n, L) / np.sqrt(g)
            z = np.sum(np.conj(h) * y, axis=1).real
            ber = np.mean((z > 0) != (s > 0))
            print(f"   SNR/branch {snr_db} dB, L = {L}: MRC BER sim {ber:.2e}, closed form {pb:.2e}")
            check(f"MRC BER closed form (L = {L}, {snr_db} dB)", abs(ber / pb - 1) < 0.1 if pb > 1e-4 else abs(ber - pb) < 3e-5)
    # Alamouti 2x1 vs MRC 1x2 at same total transmit power
    g = 10 ** (12 / 10)
    nb = 400000
    s = 2 * rng.integers(0, 2, (nb, 2)) - 1.0
    h = crandn(nb, 2)
    n1, n2 = crandn(nb) / np.sqrt(g), crandn(nb) / np.sqrt(g)
    r1 = (h[:, 0] * s[:, 0] + h[:, 1] * s[:, 1]) / np.sqrt(2) + n1
    r2 = (-h[:, 0] * s[:, 1] + h[:, 1] * s[:, 0]) / np.sqrt(2) + n2     # real BPSK: conj(s) = s
    e1 = np.conj(h[:, 0]) * r1 + h[:, 1] * np.conj(r2)
    e2 = np.conj(h[:, 1]) * r1 - h[:, 0] * np.conj(r2)
    ber_al = np.mean(np.concatenate([(e1.real > 0) != (s[:, 0] > 0), (e2.real > 0) != (s[:, 1] > 0)]))
    def pb_mrc(gg, L=2):
        mu = np.sqrt(gg / (1 + gg))
        return ((1 - mu) / 2) ** L * sum(special.comb(L - 1 + k, k) * ((1 + mu) / 2) ** k for k in range(L))
    print(f"   Alamouti 2x1 at 12 dB: BER {ber_al:.2e}; MRC 1x2 at 12 dB {pb_mrc(g):.2e}, at 9 dB {pb_mrc(g/2):.2e}")
    check("Alamouti 2x1 = MRC 1x2 with 3 dB less SNR (same diversity order 2)", abs(ber_al / pb_mrc(g / 2) - 1) < 0.1)


def part3():
    print("3. MIMO channel estimation: LS vs MMSE (2x2, T = 4 orthogonal pilots)")
    nt = nr = 2
    T = 4
    X = np.array([[1, 1, 1, 1], [1, -1, 1, -1]], complex)       # rows orthogonal, X X^H = 4 I
    trials = 50000
    for snr_db in (0, 10):
        sig2 = 10 ** (-snr_db / 10)                              # per-receive-antenna noise, unit pilot power per antenna
        H = crandn(trials, nr, nt)
        N = crandn(trials, nr, T) * np.sqrt(sig2)
        Y = H @ X + N
        XXh = X @ X.conj().T
        Hls = Y @ X.conj().T @ np.linalg.inv(XXh)
        Hmm = Y @ X.conj().T @ np.linalg.inv(XXh + sig2 * np.eye(nt))
        mse_ls = np.mean(np.abs(Hls - H) ** 2)
        mse_mm = np.mean(np.abs(Hmm - H) ** 2)
        th_ls = sig2 / T
        th_mm = 1 / (1 + T / sig2)
        print(f"   SNR {snr_db:2d} dB: LS MSE {mse_ls:.4f} (theory {th_ls:.4f}), MMSE MSE {mse_mm:.4f} (theory {th_mm:.4f})")
        check(f"LS and MMSE MSE match theory ({snr_db} dB)", abs(mse_ls / th_ls - 1) < 0.03 and abs(mse_mm / th_mm - 1) < 0.03)


def part4():
    print("4. OFDM comb pilots (N = 64, 8-tap exponential channel)")
    N, L = 64, 8
    pdp = np.exp(-np.arange(L) / 2.0); pdp /= pdp.sum()
    snr = 10 ** (25 / 10)
    out = {}
    for D in (4, 8, 16):
        mse_dft, mse_lin = [], []
        for _ in range(2000):
            h = crandn(L) * np.sqrt(pdp)
            Hk = np.fft.fft(h, N)
            pil = np.arange(0, N, D)
            Hp = Hk[pil] + crandn(len(pil)) / np.sqrt(snr)
            # DFT interpolation: IDFT of pilot estimates -> keep first min(L', N/D) taps -> FFT
            g = np.fft.ifft(Hp)
            keep = min(len(pil), L)
            Hd = np.fft.fft(np.concatenate([g[:keep], np.zeros(N - keep)]) , N)
            # linear (circular) interpolation
            xp = np.concatenate([pil, [N]]); fp = np.concatenate([Hp, [Hp[0]]])
            Hl = np.interp(np.arange(N), xp, fp.real) + 1j * np.interp(np.arange(N), xp, fp.imag)
            mse_dft.append(np.mean(np.abs(Hd - Hk) ** 2)); mse_lin.append(np.mean(np.abs(Hl - Hk) ** 2))
        out[D] = (np.mean(mse_dft), np.mean(mse_lin))
        print(f"   pilot spacing D = {D:2d} (N/D = {N//D:2d} pilots): MSE DFT-interp {10*np.log10(out[D][0]):6.1f} dB, "
              f"linear {10*np.log10(out[D][1]):6.1f} dB")
    # theory for N/D >= L: noise on Np pilots, keep L of Np taps -> MSE = sigma^2 * L/Np (sigma^2 = 1/snr)
    th = {D: 10 * np.log10(L / (N // D) / snr) for D in (4, 8)}
    check("DFT-interpolation MSE = sigma^2 L/Np when N/D >= L (D = 4, 8; within 0.5 dB)",
          all(abs(10 * np.log10(out[D][0]) - th[D]) < 0.5 for D in (4, 8)), f"theory {th[4]:.1f}, {th[8]:.1f} dB")
    check("DFT interpolation aliases when N/D < L (D = 16: MSE > 10 dB worse than D = 8)",
          10 * np.log10(out[16][0] / out[8][0]) > 10)
    check("DFT interpolation beats linear interpolation at D = 8", out[8][0] < out[8][1])


def part5():
    print("5. Ground-station diversity")
    n = 400000
    thr_db = -10.0            # fade margin: outage if instantaneous SNR < mean - 10 dB
    thr = 10 ** (thr_db / 10)
    single = 1 - np.exp(-thr)
    for rho in (0.0, 0.5, 0.9, 0.99):
        a = crandn(n); b = crandn(n)
        h1 = a
        h2 = rho * a + np.sqrt(1 - rho ** 2) * b                  # complex correlation rho
        sel = np.mean(np.maximum(np.abs(h1) ** 2, np.abs(h2) ** 2) < thr)
        print(f"   envelope corr ~ rho^2 = {rho**2:.2f}: P(fade > 10 dB) single {single:.4f}, selection {sel:.5f} "
              f"(independent theory {single**2:.5f})")
        if rho == 0.0:
            check("independent selection diversity outage = p^2", abs(sel / single ** 2 - 1) < 0.1)
        if rho == 0.99:
            check("highly correlated branches give little gain (outage > 0.25 x single)", sel > 0.25 * single)
    lam = 299792458 / 433e6
    for d_km, alt_km in ((10, 3), (5, 3), (20, 1)):
        psi = np.arctan(alt_km / d_km)
        print(f"   two-ray height-diversity null spacing at 433 MHz, rocket {alt_km} km up at {d_km} km: "
              f"lambda/(2 sin psi) = {lam/(2*np.sin(psi)):.2f} m (elevation {np.degrees(psi):.1f} deg)")
    check("two-ray null spacing at 16.7 deg elevation, 433 MHz ~ 1.2 m",
          abs(lam / (2 * np.sin(np.arctan(0.3))) - 1.21) < 0.03)


if __name__ == "__main__":
    part1(); part2(); part3(); part4(); part5()
    print(f"\nSummary: {sum(RES)}/{len(RES)} checks passed")
