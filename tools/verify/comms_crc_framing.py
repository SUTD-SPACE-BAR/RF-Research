#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/packet-framing-protocols.md

Run:  python3 tools/verify/comms_crc_framing.py      (~20 s)

Checks:
  1. CRC implementations against the standard "123456789" check values:
     CRC-8 (0x07) = 0xF4, CRC-16/CCITT-FALSE (0x1021, init 0xFFFF) = 0x29B1,
     CRC-16/ARC (0x8005 reflected) = 0xBB3D, CRC-16/KERMIT (0x1021 reflected) = 0x2189,
     CRC-32 (IEEE 802.3) = 0xCBF43926, CRC-32C (Castagnoli) = 0xE3069283.
  2. Error-detection properties of CRC-16/CCITT: detects all odd-weight errors (x+1 factor),
     all bursts <= 16 bits, and all 2-bit errors for codeword lengths up to the order of x modulo
     the primitive factor (32767) -> HD >= 4 up to 32751 data bits (matches Koopman's CRC zoo).
  3. Undetected-error probability for heavily corrupted frames ~ 2^-r (CRC-8 by Monte-Carlo).
  4. PER = 1 - (1 - p)^N for independent bit errors (Monte-Carlo), and the frame-length trade.
  5. Sync-word detection with <= E bit errors allowed: miss probability at channel BER p and
     false-alarm probability per position in random data, for a 32-bit word.
  6. PN9 whitening (x^9 + x^5 + 1): period 511, and whitening an all-zeros payload leaves no run
     longer than 9 bits.
  7. ARQ: expected transmissions 1/(1-PER); stop-and-wait efficiency.
"""
import numpy as np
from scipy import special

rng = np.random.default_rng(31)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    g = f"0x{got:X}" if isinstance(got, int) and not rel and tol == 0 and got > 9 else f"{got:.5g}"
    w = f"0x{want:X}" if isinstance(want, int) and not rel and tol == 0 and want > 9 else f"{want:.5g}"
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {g}, expected {w} (tol {tol}{' rel' if rel else ''})")


def reflect(x, w):
    return int(bin(x)[2:].zfill(w)[::-1], 2)


def crc(data, width, poly, init, refin, refout, xorout):
    top = 1 << (width - 1)
    mask = (1 << width) - 1
    reg = init
    for byte in data:
        if refin:
            byte = reflect(byte, 8)
        reg ^= byte << (width - 8)
        for _ in range(8):
            reg = ((reg << 1) ^ poly) & mask if reg & top else (reg << 1) & mask
    if refout:
        reg = reflect(reg, width)
    return reg ^ xorout


msg = b"123456789"
check("CRC-8 (0x07)", crc(msg, 8, 0x07, 0x00, False, False, 0x00), 0xF4, 0)
check("CRC-16/CCITT-FALSE", crc(msg, 16, 0x1021, 0xFFFF, False, False, 0x0000), 0x29B1, 0)
check("CRC-16/ARC (IBM)", crc(msg, 16, 0x8005, 0x0000, True, True, 0x0000), 0xBB3D, 0)
check("CRC-16/KERMIT", crc(msg, 16, 0x1021, 0x0000, True, True, 0x0000), 0x2189, 0)
check("CRC-32 (IEEE 802.3)", crc(msg, 32, 0x04C11DB7, 0xFFFFFFFF, True, True, 0xFFFFFFFF), 0xCBF43926, 0)
check("CRC-32C (Castagnoli)", crc(msg, 32, 0x1EDC6F41, 0xFFFFFFFF, True, True, 0xFFFFFFFF), 0xE3069283, 0)

# ------------------------------------------------------------------------------ 2
# polynomial arithmetic over GF(2) with Python ints (bit i = coefficient of x^i)
G = (1 << 16) | 0x1021        # x^16 + x^12 + x^5 + 1


def pmod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pdiv(a, m):
    q = 0
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        s = a.bit_length() - 1 - dm
        q |= 1 << s
        a ^= m << s
    return q, a


q, rem = pdiv(G, 0b11)
check("CCITT-16 divisible by (x+1)", rem, 0, 0)
prim = q                        # degree-15 factor
order = None
xk = 1
for k in range(1, 40000):
    xk = pmod(xk << 1, prim)
    if xk == 1:
        order = k
        break
check("order of x modulo degree-15 factor (primitive -> 2^15-1)", order, 32767, 0)
check("CCITT-16 HD>=4 max data length [bits] = order - 16", order - 16, 32751, 0)
# every burst of length <= 16 is detected: burst polynomial x^i * b(x), b of degree < 16 with b(0)=1
det_all = True
for blen in range(1, 17):
    for trial in range(200):
        b = (1 << (blen - 1)) | 1 | (int(rng.integers(0, 1 << 16)) & ((1 << max(blen - 1, 1)) - 1))
        b &= (1 << blen) - 1
        b |= 1 | (1 << (blen - 1))
        shift = int(rng.integers(0, 500))
        if pmod(b << shift, G) == 0:
            det_all = False
check("CCITT-16 detects all sampled bursts <= 16 bits", float(det_all), 1.0, 0)
odd_ok = all(pmod(int(e), G) != 0 for e in (rng.integers(1, 1 << 62, 2000) | 1) if bin(int(e)).count("1") % 2 == 1)
check("CCITT-16 detects sampled odd-weight errors", float(odd_ok), 1.0, 0)

# ------------------------------------------------------------------------------ 3
ntr = 200_000
frames = rng.integers(0, 256, (ntr, 20), dtype=np.uint8)
# CRC-8 table
tab = []
for i in range(256):
    r = i
    for _ in range(8):
        r = ((r << 1) ^ 0x07) & 0xFF if r & 0x80 else (r << 1) & 0xFF
    tab.append(r)
tab = np.array(tab, dtype=np.uint8)
reg = np.zeros(ntr, dtype=np.uint8)
for j in range(frames.shape[1]):
    reg = tab[reg ^ frames[:, j]]
claimed = rng.integers(0, 256, ntr, dtype=np.uint8)       # garbage frame + garbage CRC byte
p_und = np.mean(reg == claimed)
check("CRC-8 undetected fraction for random garbage ~ 2^-8", p_und, 2 ** -8, 0.08, rel=True)
print(f"  implied: CRC-16 ~ {2**-16:.2e}, CRC-32 ~ {2**-32:.2e} per corrupted frame (random-garbage model)")

# ------------------------------------------------------------------------------ 4
for p, Nb in ((1e-3, 256), (1e-4, 2048)):
    e = rng.random((50_000, Nb)) < p
    per_mc = np.mean(e.any(axis=1))
    check(f"PER = 1-(1-p)^N, p={p}, N={Nb}", per_mc, 1 - (1 - p) ** Nb, 0.05, rel=True)
print("  PER at p = 1e-4 for frame lengths (bits):", {N: round(1 - (1 - 1e-4) ** N, 4) for N in (64, 256, 1024, 4096)})

# ------------------------------------------------------------------------------ 5
Nsw = 32
print("  32-bit sync word, accept if <= E bit errors:")
for E in (0, 1, 2, 3, 4, 6):
    pfa = sum(special.comb(Nsw, i) for i in range(E + 1)) / 2 ** Nsw
    miss = {p: 1 - sum(special.comb(Nsw, i) * p ** i * (1 - p) ** (Nsw - i) for i in range(E + 1)) for p in (1e-2, 5e-2)}
    print(f"    E={E}: P_FA/position = {pfa:.2e}; P_miss @BER 1e-2 = {miss[1e-2]:.2e}, @5e-2 = {miss[5e-2]:.2e}")
check("P_FA per position, E=3, 32-bit word", sum(special.comb(32, i) for i in range(4)) / 2 ** 32, 1.278e-6, 0.01, rel=True)
check("P_miss E=0 at BER 1e-2 = 1-(0.99)^32", 1 - 0.99 ** 32, 0.2750, 0.001)

# ------------------------------------------------------------------------------ 6
def pn9(n, seed=0x1FF):
    s = seed
    out = []
    for _ in range(n):
        out.append(s & 1)
        fb = (s ^ (s >> 5)) & 1       # taps x^9 + x^5 + 1 (Fibonacci form)
        s = (s >> 1) | (fb << 8)
    return np.array(out)


seq = pn9(1022)
check("PN9 period 511", float(np.array_equal(seq[:511], seq[511:])), 1.0, 0)
payload = np.zeros(4000, dtype=int)
wh = payload ^ np.resize(pn9(511), 4000)
runs = np.diff(np.flatnonzero(np.diff(np.r_[-1, wh, -1]) != 0))
check("longest run after whitening all-zeros payload <= 9", int(runs.max()), 9, 0)
check("PN9 ones per period (balance)", int(pn9(511).sum()), 256, 0)

# ------------------------------------------------------------------------------ 7
per = 0.1
check("expected transmissions with ARQ = 1/(1-PER)", 1 / (1 - per), 1.111, 0.001)
Tf, Tack, Tprop = 50e-3, 10e-3, 0.1e-3
eff = (1 - per) * Tf / (Tf + Tack + 2 * Tprop)
print(f"  stop-and-wait efficiency (Tf 50 ms, ACK 10 ms, PER 10 %) = {eff:.3f}")

# ------------------------------------------------------------------------------ 8
# Optimal payload length L for throughput eta = L/(L+H) * (1-p)^(L+H)
H, p = 80, 1e-4
Ls = np.arange(8, 20000)
eta = Ls / (Ls + H) * (1 - p) ** (Ls + H)
L_num = Ls[np.argmax(eta)]
L_approx = -H / 2 + np.sqrt(H ** 2 / 4 - H / np.log(1 - p))
print(f"  optimal payload (H = {H} bits, BER {p}): numerical {L_num} bits, closed form {L_approx:.0f}, sqrt(H/p) = {np.sqrt(H/p):.0f}; peak throughput {eta.max():.3f}")
check("optimal frame payload length closed form vs numerical [bits]", L_approx, L_num, 1.0)

# ------------------------------------------------------------------------------ 9
# Downlink-only erasure coding across frames: systematic (n=10, k=8) MDS code, i.i.d. frame loss q
from itertools import combinations
q = 0.10
n_, k_ = 10, 8
lost_data = 0.0
for i in range(n_ + 1):
    pi = special.comb(n_, i) * q ** i * (1 - q) ** (n_ - i)
    if i > n_ - k_:
        # decoding fails; received systematic frames still usable. expected lost data frames = i*k/n
        lost_data += pi * i * k_ / n_
fail = sum(special.comb(n_, i) * q ** i * (1 - q) ** (n_ - i) for i in range(n_ - k_ + 1, n_ + 1))
resid = lost_data / k_
print(f"  (10,8) erasure code, frame loss 10 %: block decode failure {fail:.3f}, residual data-frame loss {resid:.4f} (uncoded 0.100), overhead 25 %")
check("(10,8) MDS erasure block failure at 10 % loss", fail, 0.0702, 0.001)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
