#!/usr/bin/env python3
"""What LoRa's coding rates CR 4/5 ... 4/8 buy, under an idealised model.
Used by kb/10-comms-modulation/channel-coding-fec.md (and cross-referenced for domain 15).

Run:  python3 tools/verify/comms_lora_cr.py      (~20 s)

Model (stated on the page; NOT a bit-exact LoRa PHY):
  * Each LoRa symbol is non-coherent 2^SF-ary orthogonal signalling in AWGN; symbol error
    probability Ps(Es/N0) from the exact integral (tools/verify/comms_ber_awgn.py).
  * A symbol error lands on a uniformly random wrong symbol (noise-limited regime), so each of
    its SF bits is wrong with probability ~1/2.
  * LoRa's diagonal interleaver puts one bit of each of SF codewords into each symbol, so a
    block of (4+CR) symbols carries SF Hamming-type codewords of length 4+CR, and a symbol error
    corrupts at most one bit of any given codeword.
  * CR 4/5: single parity (detect only).  CR 4/6: d_min = 2 (detect only).
    CR 4/7: Hamming(7,4), corrects 1.  CR 4/8: extended Hamming(8,4), corrects 1 (detects 2).
  * Packet: 32 information bytes (payload incl. CRC) -> blocks of SF*4 information bits.
  * Energy accounting: Eb = energy per information bit; Es = SF * (4/(4+CR)) * Eb.
Monte-Carlo at the bit level with real Hamming syndrome decoding, then PER vs Eb/N0.
"""
import numpy as np
from scipy import special, integrate, optimize

rng = np.random.default_rng(99)
ok_all = True


def ps_mfsk_nc(M, es):
    a = np.sqrt(es)
    f = lambda r: 2 * r * np.exp(-(r - a) ** 2) * special.i0e(2 * r * a) * np.exp((M - 1) * np.log1p(-np.exp(-r * r) + 1e-300))
    pc = integrate.quad(f, 0, a + 12, limit=400, points=[a])[0]
    return max(1 - pc, 1e-300)


G7 = np.array([[1, 0, 0, 0, 1, 1, 0], [0, 1, 0, 0, 1, 0, 1], [0, 0, 1, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]])
H7 = np.hstack([G7[:, 4:].T, np.eye(3, dtype=int)])
syn7 = {tuple(H7[:, i]): i for i in range(7)}


def decode_block(err, cr):
    """err: (ncw, 4+cr) bit-error pattern (1 = flipped); returns True if all data bits correct
    (for detect-only codes, a detected error counts as a packet failure)."""
    n = 4 + cr
    if cr in (1, 2):
        return not err.any()
    ok = True
    for e in err:
        if not e.any():
            continue
        if cr == 3:
            s = tuple(H7 @ e[:7] % 2)
            if s == (0, 0, 0):
                return False          # undetected codeword error (weight>=3) -> CRC fails
            e2 = e.copy()
            e2[syn7[s]] ^= 1
            if e2[:4].any():
                return False
        else:  # cr == 4, extended Hamming: overall parity bit
            s = tuple(H7 @ e[:7] % 2)
            par = e.sum() % 2
            if s == (0, 0, 0) and par == 0:
                return False
            if par == 1 and s != (0, 0, 0):
                e2 = e.copy()
                e2[syn7[s]] ^= 1
                if e2[:4].any():
                    return False
            elif par == 1 and s == (0, 0, 0):
                continue               # error only in overall parity bit
            else:
                return False           # double error detected
    return ok


def per(sf, cr, ebn0_db, payload_bytes=32, npkt=4000):
    g = 10 ** (ebn0_db / 10)
    es = sf * 4 / (4 + cr) * g
    ps = ps_mfsk_nc(2 ** sf, es)
    nblocks = int(np.ceil(payload_bytes * 8 / (4 * sf)))
    n = 4 + cr
    fails = 0
    for _ in range(npkt):
        bad = False
        for _b in range(nblocks):
            sym_err = rng.random(n) < ps
            if not sym_err.any():
                continue
            # each erroneous symbol flips each of the SF codewords' bit at its position w.p. 1/2
            err = np.zeros((sf, n), dtype=int)
            for j in np.nonzero(sym_err)[0]:
                err[:, j] = rng.integers(0, 2, sf)
            if not decode_block(err, cr):
                bad = True
                break
        fails += bad
    return fails / npkt, ps


def req_ebn0(sf, cr, target=0.01):
    xs = np.arange(2.0, 12.01, 0.5)
    pers = []
    for x in xs:
        p, _ = per(sf, cr, x, npkt=1500)
        pers.append(max(p, 1e-4))
        if p < target / 3:
            break
    pers = np.array(pers)
    xs = xs[:len(pers)]
    return float(np.interp(np.log(target), np.log(pers[::-1]), xs[::-1]))


results = {}
for sf in (7, 12):
    print(f"SF{sf}, 32-byte packet, PER target 1 %:")
    for cr in (1, 2, 3, 4):
        r = req_ebn0(sf, cr)
        results[(sf, cr)] = r
        print(f"   CR 4/{4+cr}: required Eb/N0 ~ {r:5.2f} dB   (air time x{(4+cr)/5:.2f} vs CR 4/5)")
    print(f"   net gain of CR 4/8 over CR 4/5: {results[(sf,1)] - results[(sf,4)]:.2f} dB;"
          f" CR 4/7 over 4/5: {results[(sf,1)] - results[(sf,3)]:.2f} dB")

g7 = results[(7, 1)] - results[(7, 3)]
g8 = results[(7, 1)] - results[(7, 4)]
ok = (0.0 < g7 < 3.0) and (results[(7, 2)] > results[(7, 1)] - 0.2)
ok_all &= ok
print(f"[{'PASS' if ok else 'FAIL'}] CR 4/7 gives a modest positive gain (0-3 dB) at SF7; CR 4/6 gives none")
print("\nOVERALL:", "PASS" if ok_all else "FAIL")
