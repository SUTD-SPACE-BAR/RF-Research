#!/usr/bin/env python3
"""s8_alamouti_mimo.py — checks for the S8 extension of
kb/10-comms-modulation/mimo-capacity-and-channel-estimation.md (space-time coding, detectors, CSI).

1. Alamouti BER, BPSK, quasi-static Rayleigh: 2x1 = 2-branch MRC at half SNR; 2x2 = 4-branch MRC at half SNR.
2. Orthogonal designs: rate-3/4 complex code for 4 (and 3) Tx satisfies G^H G = (sum|s|^2) I.
3. MRT (transmit beamforming with CSI at the transmitter), 2x1 = 1x2 MRC; Alamouti is 3 dB behind.
4. 2x2 spatial multiplexing, QPSK: ZF, LMMSE and ML BER; diversity slopes ~1 (ZF/MMSE) and ~2 (ML);
   LMMSE output SINR formula 1/[(I + rho/Nt H^H H)^-1]_kk - 1 vs measured.
5. Fixed rate 4 b/s/Hz on 2x2: Alamouti + 16-QAM vs spatial-multiplexing QPSK (ML): SM wins at low SNR,
   Alamouti (diversity 4) wins at high SNR — the diversity-multiplexing trade-off in one plot.
6. Imperfect CSI: Alamouti with LS pilot estimates (T pilots per antenna) -> SNR loss ~ 10log(1+1/T) at high SNR;
   channel change between the two Alamouti slots (correlation r) -> error floor.
7. Cyclic delay diversity on OFDM: uncoded per-subcarrier BER = 1x1 Rayleigh (no diversity without coding).
8. MIMO-OFDM pilot / sounding bookkeeping numbers used on the page.

Run: python3 tools/verify/s8_alamouti_mimo.py    (~40 s)
"""
import numpy as np
from scipy import special

rng = np.random.default_rng(88)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def crandn(*s):
    return (rng.standard_normal(s) + 1j * rng.standard_normal(s)) / np.sqrt(2)


def mrc_bpsk(gbar, L):
    """Closed-form BPSK BER, L-branch MRC, i.i.d. Rayleigh, mean SNR per branch gbar."""
    mu = np.sqrt(gbar / (1 + gbar))
    return ((1 - mu) / 2) ** L * sum(special.comb(L - 1 + k, k) * ((1 + mu) / 2) ** k for k in range(L))


db = lambda x: 10 * np.log10(x)
un = lambda d: 10 ** (d / 10)

# ------------------------------------------------------------------ 1. Alamouti 2xNr
print("1. Alamouti BPSK")


def alamouti_ber(rho, Nr, n=400_000, H_est_err=0.0, r_time=1.0):
    """rho = total transmit SNR (Es/N0 summed over both antennas). Each antenna sends at half power."""
    s = rng.choice([-1.0, 1.0], size=(n, 2))
    h1 = crandn(n, 2, Nr)                          # slot-1 channel [tx, rx]
    h2 = r_time * h1 + np.sqrt(1 - r_time ** 2) * crandn(n, 2, Nr)   # slot-2 channel
    N0 = 1 / rho
    w1, w2 = np.sqrt(N0) * crandn(n, Nr), np.sqrt(N0) * crandn(n, Nr)
    a = 1 / np.sqrt(2)
    r1 = a * (h1[:, 0] * s[:, [0]] + h1[:, 1] * s[:, [1]]) + w1
    r2 = a * (-h2[:, 0] * np.conj(s[:, [1]]) + h2[:, 1] * np.conj(s[:, [0]])) + w2
    he = h1 + np.sqrt(H_est_err) * crandn(n, 2, Nr) if H_est_err > 0 else h1   # receiver's estimate
    s1 = np.sum(np.conj(he[:, 0]) * r1 + he[:, 1] * np.conj(r2), axis=1)
    s2 = np.sum(np.conj(he[:, 1]) * r1 - he[:, 0] * np.conj(r2), axis=1)
    return np.mean(np.sign(np.c_[s1.real, s2.real]) != s)


for Nr, L in [(1, 2), (2, 4)]:
    for rdb in (6, 12):
        mc = alamouti_ber(un(rdb), Nr)
        cf = mrc_bpsk(un(rdb) / 2, L)
        check(f"Alamouti 2x{Nr} at {rdb} dB = {L}-branch MRC at {rdb - 3} dB", abs(mc / cf - 1) < 0.1,
              f"MC {mc:.3e} vs CF {cf:.3e}")
b22 = alamouti_ber(un(10), 2)
check("2x2 Alamouti at 10 dB beats 1x2 MRC at 10 dB (diversity 4 vs 2)", b22 < mrc_bpsk(un(10), 2),
      f"{b22:.2e} vs {mrc_bpsk(un(10), 2):.2e}")

# ------------------------------------------------------------------ 2. orthogonal designs
print("\n2. Orthogonal space-time block codes")


def G34(s):
    s1, s2, s3 = s
    # Tarokh et al. 1999-style rate-3/4 code for 4 Tx (rows = time slots, columns = antennas)
    return np.array([[s1, s2, s3, 0],
                     [-np.conj(s2), np.conj(s1), 0, s3],
                     [-np.conj(s3), 0, np.conj(s1), -s2],
                     [0, -np.conj(s3), np.conj(s2), s1]])


ok4 = ok3 = True
for _ in range(200):
    s = crandn(3)
    G = G34(s)
    e = np.sum(np.abs(s) ** 2)
    ok4 &= np.allclose(G.conj().T @ G, e * np.eye(4))
    ok3 &= np.allclose(G[:, :3].conj().T @ G[:, :3], e * np.eye(3))
check("rate-3/4 code: G^H G = (|s1|^2+|s2|^2+|s3|^2) I for 4 Tx", ok4)
check("dropping one column gives a rate-3/4 code for 3 Tx", ok3)
A = lambda s: np.array([[s[0], s[1]], [-np.conj(s[1]), np.conj(s[0])]])
s = crandn(2)
check("Alamouti matrix is orthogonal: A^H A = (|s1|^2+|s2|^2) I", np.allclose(A(s).conj().T @ A(s), np.sum(np.abs(s) ** 2) * np.eye(2)))

# ------------------------------------------------------------------ 3. MRT vs Alamouti vs MRC
print("\n3. Transmit CSI (MRT) vs Alamouti, 2x1")
n = 400_000
rho = un(10)
h = crandn(n, 2)
sym = rng.choice([-1.0, 1.0], n)
w = np.conj(h) / np.linalg.norm(h, axis=1, keepdims=True)        # unit-norm MRT precoder
y = np.sum(h * w, axis=1) * sym + np.sqrt(1 / rho) * crandn(n)
ber_mrt = np.mean(np.sign(y.real) != sym)
check("MRT 2x1 at 10 dB = 1x2 MRC at 10 dB (array gain 2 needs CSI at Tx)", abs(ber_mrt / mrc_bpsk(rho, 2) - 1) < 0.1,
      f"{ber_mrt:.3e} vs {mrc_bpsk(rho, 2):.3e}")
check("Alamouti 2x1 at 10 dB = MRT at 7 dB (3 dB array-gain penalty)", abs(alamouti_ber(rho, 1) / mrc_bpsk(rho / 2, 2) - 1) < 0.1)

# ------------------------------------------------------------------ 4. spatial multiplexing detectors
print("\n4. 2x2 spatial multiplexing, QPSK (rho = total SNR, Es per antenna = 1/2)")
Q = np.array([1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j]) / np.sqrt(2)
cands = np.array([[a, b] for a in Q for b in Q])                  # 16 x 2


def bits_qpsk(x):
    return np.c_[x.real > 0, x.imag > 0]


def sm_ber(rdb, n=200_000):
    rho = un(rdb)
    Nt = 2
    H = crandn(n, 2, 2)
    xi = rng.integers(0, 4, (n, 2))
    x = Q[xi] / np.sqrt(Nt)                                       # total power 1
    N0 = 1 / rho
    y = np.einsum("nij,nj->ni", H, x) + np.sqrt(N0) * crandn(n, 2)
    Hh = np.conj(np.transpose(H, (0, 2, 1)))
    G = Hh @ H
    zf = np.linalg.solve(G, np.einsum("nij,nj->ni", Hh, y)[..., None])[..., 0]
    mm = np.linalg.solve(G + N0 * Nt * np.eye(2), np.einsum("nij,nj->ni", Hh, y)[..., None])[..., 0]
    d = np.abs(y[:, None, :] - np.einsum("nij,kj->nki", H, cands / np.sqrt(Nt))) ** 2
    ml = cands[np.argmin(d.sum(-1), axis=1)]
    true = np.c_[bits_qpsk(Q[xi[:, 0]]), bits_qpsk(Q[xi[:, 1]])]
    out = {}
    for nm, est in (("ZF", zf), ("MMSE", mm), ("ML", ml)):
        out[nm] = np.mean(np.c_[bits_qpsk(est[:, 0]), bits_qpsk(est[:, 1])] != true)
    # MMSE SINR check (stream 0), formula vs measured on the unbiased estimate
    A = np.linalg.inv(np.eye(2) + rho / Nt * G)
    sinr_f = np.mean(1 / A[:, 0, 0].real - 1)
    return out, sinr_f


res = {}
for rdb in (10, 20, 30):
    res[rdb], _ = sm_ber(rdb)
    print(f"   {rdb} dB: " + ", ".join(f"{k} {v:.2e}" for k, v in res[rdb].items()))
check("ML <= MMSE <= ZF at every SNR", all(res[r]["ML"] <= res[r]["MMSE"] <= res[r]["ZF"] for r in res))
slope = lambda nm: (np.log10(res[20][nm]) - np.log10(res[30][nm]))
check("ZF diversity slope ~1 (Nr-Nt+1) per decade of SNR", 0.8 < slope("ZF") < 1.2, f"{slope('ZF'):.2f}")
check("ML diversity slope ~2 (Nr)", 1.6 < slope("ML") < 2.4, f"{slope('ML'):.2f}")
# ZF closed form: post-ZF SNR of stream k = (rho/Nt)/[(H^H H)^-1]_kk ~ (rho/Nt) x Gamma(Nr-Nt+1); QPSK bit SNR = half
zf_cf = mrc_bpsk(un(20) / 4, 1)
check("ZF at 20 dB = 1-branch Rayleigh, bit SNR rho/(2 Nt) (Nr-Nt+1 = 1 branch)", abs(res[20]["ZF"] / zf_cf - 1) < 0.1,
      f"{res[20]['ZF']:.3e} vs {zf_cf:.3e}")

# measured MMSE SINR vs formula (separate small run)
rho = un(15); Nt = 2; n = 200_000
H = crandn(n, 2, 2); x = crandn(n, 2) / np.sqrt(Nt); N0 = 1 / rho
y = np.einsum("nij,nj->ni", H, x) + np.sqrt(N0) * crandn(n, 2)
Hh = np.conj(np.transpose(H, (0, 2, 1)))
W = np.linalg.solve(Hh @ H + N0 * Nt * np.eye(2), Hh)            # n x 2 x 2
xh = np.einsum("nij,nj->ni", W, y) * np.sqrt(Nt)
g = np.einsum("nij,nji->ni", W, H)[:, 0]                          # bias of stream 0
A = np.linalg.inv(np.eye(2) + rho / Nt * (Hh @ H))
sinr_formula = 1 / A[:, 0, 0].real - 1
err = xh[:, 0] / g - x[:, 0] * np.sqrt(Nt)                        # unbiased error
sinr_meas = np.mean(1 / np.mean(np.abs(err) ** 2))
# per-realisation check on a few fixed channels
okf = True
for _ in range(5):
    Hf = crandn(2, 2)
    xs = crandn(200_000, 2) / np.sqrt(Nt)
    ys = xs @ Hf.T + np.sqrt(N0) * crandn(200_000, 2)
    Wf = np.linalg.solve(Hf.conj().T @ Hf + N0 * Nt * np.eye(2), Hf.conj().T)
    est = ys @ Wf.T
    gf = (Wf @ Hf)[0, 0]
    e = est[:, 0] / gf - xs[:, 0]
    meas = np.mean(np.abs(xs[:, 0]) ** 2) / np.mean(np.abs(e) ** 2)
    Af = np.linalg.inv(np.eye(2) + rho / Nt * Hf.conj().T @ Hf)
    okf &= abs(db(meas) - db(1 / Af[0, 0].real - 1)) < 0.1
check("LMMSE output SINR formula matches measurement on 5 fixed channels (< 0.1 dB)", okf)

# ------------------------------------------------------------------ 5. fixed rate 4 b/s/Hz
print("\n5. 4 b/s/Hz on 2x2: Alamouti+16QAM vs SM-QPSK (ML)")
L16 = np.array([-3, -1, 1, 3])
QAM16 = (L16[:, None] + 1j * L16[None, :]).ravel() / np.sqrt(10)


def alam16_ser_bits(rdb, n=300_000):
    rho = un(rdb)
    si = rng.integers(0, 16, (n, 2)); s = QAM16[si]
    h = crandn(n, 2, 2); N0 = 1 / rho; a = 1 / np.sqrt(2)
    r1 = a * (h[:, 0] * s[:, [0]] + h[:, 1] * s[:, [1]]) + np.sqrt(N0) * crandn(n, 2)
    r2 = a * (-h[:, 0] * np.conj(s[:, [1]]) + h[:, 1] * np.conj(s[:, [0]])) + np.sqrt(N0) * crandn(n, 2)
    nrm = np.sum(np.abs(h) ** 2, axis=(1, 2))[:, None] * a
    z = np.c_[np.sum(np.conj(h[:, 0]) * r1 + h[:, 1] * np.conj(r2), 1),
              np.sum(np.conj(h[:, 1]) * r1 - h[:, 0] * np.conj(r2), 1)] / nrm
    dec = np.argmin(np.abs(z[..., None] - QAM16[None, None, :]), axis=-1)
    return np.mean(dec != si)


def sm_qpsk_ser(rdb, n=200_000):
    rho = un(rdb); Nt = 2
    H = crandn(n, 2, 2); xi = rng.integers(0, 4, (n, 2)); x = Q[xi] / np.sqrt(Nt)
    y = np.einsum("nij,nj->ni", H, x) + np.sqrt(1 / rho) * crandn(n, 2)
    d = np.abs(y[:, None, :] - np.einsum("nij,kj->nki", H, cands / np.sqrt(Nt))) ** 2
    k = np.argmin(d.sum(-1), axis=1)
    est = np.c_[k // 4, k % 4]
    return np.mean(est != xi)


tab = {r: (alam16_ser_bits(r), sm_qpsk_ser(r)) for r in (10, 20, 30)}
for r, (a16, smq) in tab.items():
    print(f"   {r} dB: Alamouti-16QAM SER {a16:.2e}   SM-QPSK-ML SER {smq:.2e}")
check("SM-QPSK beats Alamouti-16QAM at 10 dB", tab[10][1] < tab[10][0])
check("Alamouti-16QAM beats SM-QPSK at 30 dB (diversity 4 vs 2 wins at high SNR)", tab[30][0] < tab[30][1])

# ------------------------------------------------------------------ 6. imperfect CSI
print("\n6. Imperfect CSI for Alamouti 2x1")
for T in (1, 4):
    rdb = 20; rho = un(rdb)
    # LS estimate with T pilots per antenna at per-antenna pilot SNR rho/2: error var = (1/rho)/(T*(1/2))
    ev = (1 / rho) / (T / 2)
    b_est = alamouti_ber(rho, 1, H_est_err=ev)
    lo_b, hi_b = db(1 + 1 / T), db(1 + 2 / T)     # bracket for half-power pilots on each antenna
    # find equivalent perfect-CSI SNR
    grid = np.arange(rdb - 6, rdb + 0.01, 0.05)
    bers = np.array([mrc_bpsk(un(g) / 2, 2) for g in grid])
    eq = grid[np.argmin(np.abs(np.log(bers) - np.log(b_est)))]
    print(f"   T={T}: BER {b_est:.3e}; equivalent perfect-CSI SNR {eq:.2f} dB -> loss {rdb - eq:.2f} dB (bracket {lo_b:.2f}-{hi_b:.2f})")
    check(f"T={T} pilots: loss between 10log(1+1/T) and 10log(1+2/T) dB", lo_b - 0.1 < rdb - eq < hi_b + 0.1)
fl = [alamouti_ber(un(40), 1, r_time=r) for r in (1.0, 0.99, 0.95)]
check("channel change between slots creates an error floor (BER at 40 dB rises with 1-r)", fl[0] < fl[1] < fl[2],
      f"r=1: {fl[0]:.1e}, 0.99: {fl[1]:.1e}, 0.95: {fl[2]:.1e}")
fD = 433e6 * 300 / 3e8
r_10k = special.j0(2 * np.pi * fD / 10e3)
check("Jakes correlation over one symbol at 10 kbaud, f_D = 433 Hz: J0 = 0.98", abs(r_10k - 0.982) < 0.002, f"{r_10k:.4f}")

# ------------------------------------------------------------------ 7. CDD
print("\n7. Cyclic delay diversity, uncoded OFDM")
N, dly, nsym = 64, 4, 4000
ber = []
for _ in range(nsym):
    h1, h2 = crandn(2)
    k = np.arange(N)
    Hk = (h1 + h2 * np.exp(-2j * np.pi * k * dly / N)) / np.sqrt(2)
    b = rng.choice([-1.0, 1.0], N)
    yk = Hk * b + np.sqrt(1 / un(15)) * crandn(N)
    ber.append(np.mean(np.sign((np.conj(Hk) * yk).real) != b))
check("CDD uncoded BER at 15 dB = 1x1 Rayleigh (diversity only appears with coding across subcarriers)",
      abs(np.mean(ber) / mrc_bpsk(un(15), 1) - 1) < 0.1, f"{np.mean(ber):.3e} vs {mrc_bpsk(un(15), 1):.3e}")

# ------------------------------------------------------------------ 8. bookkeeping
print("\n8. Numbers quoted on the page")
coh_time = 0.423 / 433.0          # Clarke 50 % coherence time ~0.423/f_D
check("coherence time at f_D = 433 Hz ~ 1 ms (0.423/f_D)", abs(coh_time * 1e3 - 0.98) < 0.02, f"{coh_time * 1e3:.2f} ms")
check("802.11a 20 MHz symbol 4 us: an Alamouti pair spans 8 us", 2 * 4e-6 == 8e-6)
check("rate-3/4 4-Tx code: 3 symbols / 4 slots", 3 / 4 == 0.75)

# two antennas on an airframe: coherent (same signal on both) vs Alamouti (orthogonal) far-field power
phi = np.linspace(0, 2 * np.pi, 3601)                  # relative path phase k d sin(theta) + feed phase
coh = np.abs((1 + np.exp(1j * phi)) / np.sqrt(2)) ** 2  # half power per element, amplitudes add
alam = (np.abs(1 / np.sqrt(2)) ** 2 + np.abs(np.exp(1j * phi) / np.sqrt(2)) ** 2) * np.ones_like(phi)
check("same signal on two antennas: power ripples +3 dB ... null; Alamouti: flat 0 dB (= one antenna)",
      abs(db(coh.max()) - 3.01) < 0.01 and coh.min() < 1e-6 and np.allclose(alam, 1.0))
lam433, lam24 = 3e8 / 433e6, 3e8 / 2.44e9
d = 0.10
check("10 cm airframe: max path difference 0.14 lambda at 433 MHz (52 deg, no null) but 0.81 lambda at 2.44 GHz",
      abs(d / lam433 - 0.144) < 0.002 and abs(d / lam24 - 0.813) < 0.002, f"{d / lam433:.3f}, {d / lam24:.3f}")
ripple433 = db(np.abs((1 + np.exp(1j * 2 * np.pi * d / lam433)) / np.sqrt(2)) ** 2)
check("in-phase pair at 433 MHz, 10 cm apart: +3.0 dB broadside, +2.1 dB endfire (no deep null)",
      abs(ripple433 - 2.08) < 0.05, f"{ripple433:.2f} dB")

print(f"\n{sum(RES)}/{len(RES)} checks PASS")
