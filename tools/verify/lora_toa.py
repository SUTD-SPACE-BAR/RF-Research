#!/usr/bin/env python3
"""
lora_toa.py — LoRa time-on-air (ToA), bit rate and packet-rate calculator + cross-checks.

Used by: kb/15-lora-ism-radios/lora-phy-css-math.md (ToA section, worked examples),
         kb/15-lora-ism-radios/rocket-telemetry-radio-design.md (update-rate budget).

Three independent implementations are compared:
  (A) SX127x form  — Semtech SX1276/77/78/79 datasheet Rev 7 §4.1.1.7 (= AN1200.13):
        n_payload = 8 + max(ceil((8PL - 4SF + 28 + 16CRC - 20IH) / (4(SF - 2DE))) (CR+4), 0)
        T = (n_preamble + 4.25 + n_payload) * 2^SF / BW
  (B) SX126x form  — SX1261/2 datasheet Rev 1.2 §6.1.4 (equations are images; checked on the rendered p.41):
        SF>=7 : N = Npre + 4.25 + 8 + ceil(max(8PL + 16CRC - 4SF + 8 + 20H, 0) / (4(SF-2DE))) (CR+4)
        SF5/6 : N = Npre + 6.25 + 8 + ceil(max(8PL + 16CRC - 4SF      + 20H, 0) / (4SF))      (CR+4)
  (C) Integer replica of Semtech's sx126x_driver (sx126x_get_lora_time_on_air_numerator):
        quarter-symbol integer arithmetic, result rounded up to whole ms.
The script asserts A == B for SF7..12 (the two chip generations are air-compatible there) and
that C == ceil(B) for every case, then prints tables used on the KB pages.

Also derives the payload-symbol formula from the interleaver block structure (first block:
8 symbols at CR4/8 carrying SF-2 bits/symbol; later blocks: (4+CR) symbols carrying SF or SF-2
bits/symbol) and checks it reproduces (A).

Run:  python3 tools/verify/lora_toa.py
"""
import math
import itertools

BW_HZ = {7.8: 7812.5, 10.4: 10416.667, 15.6: 15625.0, 20.8: 20833.333, 31.25: 31250.0,
         41.7: 41666.667, 62.5: 62500.0, 125: 125000.0, 250: 250000.0, 500: 500000.0}
# Semtech driver uses these integer Hz values
BW_HZ_DRIVER = {7.8: 7812, 10.4: 10417, 15.6: 15625, 20.8: 20833, 31.25: 31250,
                41.7: 41667, 62.5: 62500, 125: 125000, 250: 250000, 500: 500000}


def t_sym(sf, bw_hz):
    """Symbol duration [s] = 2^SF / BW."""
    return (2 ** sf) / bw_hz


def ldro_auto(sf, bw_hz, rule="sx126x"):
    """Low-data-rate-optimisation rule of thumb.
    SX127x DS: 'mandated when symbol duration exceeds 16 ms';
    SX126x DS: 'usually recommended when symbol time >= 16.38 ms'.
    Both put the boundary at SF11/125 kHz (16.384 ms)."""
    ts_ms = t_sym(sf, bw_hz) * 1e3
    return ts_ms >= 16.38 if rule == "sx126x" else ts_ms > 16.0


def n_payload_sx127x(pl, sf, cr, crc=True, explicit=True, de=False):
    ih = 0 if explicit else 1
    num = 8 * pl - 4 * sf + 28 + 16 * int(crc) - 20 * ih
    den = 4 * (sf - 2 * int(de))
    return 8 + max(math.ceil(num / den) * (cr + 4), 0)


def toa_sx127x(pl, sf, bw_hz, cr=1, npre=8, crc=True, explicit=True, de=None):
    if de is None:
        de = ldro_auto(sf, bw_hz, "sx127x")
    n = npre + 4.25 + n_payload_sx127x(pl, sf, cr, crc, explicit, de)
    return n * t_sym(sf, bw_hz), n


def nsym_sx126x(pl, sf, cr=1, npre=8, crc=True, explicit=True, de=False):
    h = 20 if explicit else 0
    ncrc = 16 if crc else 0
    if sf in (5, 6):
        num = max(8 * pl + ncrc - 4 * sf + h, 0)
        return npre + 6.25 + 8 + math.ceil(num / (4 * sf)) * (cr + 4)
    num = max(8 * pl + ncrc - 4 * sf + 8 + h, 0)
    den = 4 * (sf - 2 * int(de))
    return npre + 4.25 + 8 + math.ceil(num / den) * (cr + 4)


def toa_sx126x(pl, sf, bw_hz, cr=1, npre=8, crc=True, explicit=True, de=None):
    if de is None:
        de = ldro_auto(sf, bw_hz, "sx126x")
    n = nsym_sx126x(pl, sf, cr, npre, crc, explicit, de)
    return n * t_sym(sf, bw_hz), n


def toa_driver_ms(pl, sf, bw_key, cr=1, npre=8, crc=True, explicit=True, de=False):
    """Integer replica of Semtech sx126x_driver ToA (quarter-symbol arithmetic, ms ceil)."""
    num = (pl << 3) + (16 if crc else 0) - (4 * sf)
    if explicit:
        num += 20
    if sf <= 6:
        den = 4 * sf
    else:
        num += 8
        den = 4 * (sf - 2) if de else 4 * sf
    if num < 0:
        num = 0
    intermed = ((num + den - 1) // den) * (cr + 4) + npre + 12
    if sf <= 6:
        intermed += 2
    numerator = ((4 * intermed + 1) * (1 << (sf - 2)))  # in units of 1/BW seconds
    bw = BW_HZ_DRIVER[bw_key]
    return (1000 * numerator + bw - 1) // bw


def n_payload_from_blocks(pl, sf, cr, crc=True, explicit=True, de=False):
    """Derivation from interleaver structure (see page): first block = 8 symbols at CR4/8
    with SF-2 bits/symbol -> carries 4(SF-2) information bits, of which 20 are the explicit
    header; each later block = (4+CR) symbols carrying 4*(SF-2DE) information bits."""
    first_block_bits = 4 * (sf - 2)
    header_bits = 20 if explicit else 0
    remaining = 8 * pl + 16 * int(crc) - (first_block_bits - header_bits)
    per_block = 4 * (sf - 2 * int(de))
    blocks = max(math.ceil(remaining / per_block), 0)
    return 8 + blocks * (cr + 4)


def bitrate(sf, bw_hz, cr=1, de=False):
    """Nominal (useful) bit rate Rb = (SF-2DE) * BW/2^SF * 4/(4+CR) [bit/s]."""
    return (sf - 2 * int(de)) * bw_hz / 2 ** sf * 4 / (4 + cr)


def self_test():
    n_cases = 0
    for pl, sf, bwk, cr, crc, exp_ in itertools.product(
            [1, 5, 10, 13, 32, 51, 64, 100, 222, 255], range(7, 13),
            [7.8, 20.8, 62.5, 125, 250, 500], [1, 2, 3, 4], [True, False], [True, False]):
        bw = BW_HZ[bwk]
        de = ldro_auto(sf, bw)
        a, na = toa_sx127x(pl, sf, bw, cr, 8, crc, exp_, de)
        b, nb = toa_sx126x(pl, sf, bw, cr, 8, crc, exp_, de)
        assert abs(na - nb) < 1e-9, (pl, sf, bwk, cr, crc, exp_, na, nb)
        # structural derivation reproduces formula A
        assert n_payload_from_blocks(pl, sf, cr, crc, exp_, de) == \
            n_payload_sx127x(pl, sf, cr, crc, exp_, de) or \
            n_payload_sx127x(pl, sf, cr, crc, exp_, de) == 8  # max(…,0) clamp case
        c = toa_driver_ms(pl, sf, bwk, cr, 8, crc, exp_, de)
        b_drv = nb * (2 ** sf) / BW_HZ_DRIVER[bwk] * 1e3
        assert c == math.ceil(b_drv - 1e-9), (pl, sf, bwk, c, b_drv)
        n_cases += 1
    # SF5/6 (SX126x only) driver vs formula B
    for pl, sf, bwk, cr in itertools.product([1, 10, 32, 64, 255], [5, 6], [125, 250, 500], [1, 4]):
        nb = nsym_sx126x(pl, sf, cr, 12, True, True, False)
        c = toa_driver_ms(pl, sf, bwk, cr, 12, True, True, False)
        assert c == math.ceil(nb * 2 ** sf / BW_HZ_DRIVER[bwk] * 1e3 - 1e-9)
        n_cases += 1
    return n_cases


def main():
    n = self_test()
    print(f"Self-test passed: SX127x formula == SX126x formula (SF7-12), driver integer "
          f"replica == ceil(formula), block derivation == formula; {n} cases.\n")

    print("Reference values (8-symbol preamble, explicit header, CRC on, CR4/5, auto-LDRO):")
    for pl, sf, bwk in [(10, 7, 125), (13, 7, 125), (13, 12, 125), (51, 12, 125), (64, 7, 125)]:
        t, nsym = toa_sx126x(pl, sf, BW_HZ[bwk])
        print(f"  PL={pl:3d} B SF{sf:2d} BW{bwk:>5} kHz: {nsym:7.2f} symbols, ToA = {t*1e3:9.3f} ms")
    print()

    print("Symbol time and nominal bit rate (CR4/5):")
    print("   SF |  BW125: Ts[ms]  Rb[bit/s] |  BW250: Ts   Rb     |  BW500: Ts   Rb     | LDRO@125")
    for sf in range(5, 13):
        row = []
        for bwk in (125, 250, 500):
            bw = BW_HZ[bwk]
            de = ldro_auto(sf, bw)
            row.append((t_sym(sf, bw) * 1e3, bitrate(sf, bw, 1, de)))
        print(f"  {sf:3d} | {row[0][0]:8.3f} {row[0][1]:9.0f}     | {row[1][0]:7.3f} {row[1][1]:7.0f} "
              f"   | {row[2][0]:7.3f} {row[2][1]:7.0f}   | {ldro_auto(sf, BW_HZ[125])}")
    print()

    print("ToA [ms] for rocket telemetry payloads (preamble 8, explicit hdr, CRC, CR4/5, auto-LDRO)")
    print("and maximum packet rate if the radio transmitted back-to-back (100% duty):")
    for bwk in (125, 250, 500):
        for pl in (16, 32, 64):
            cells = []
            for sf in range(7, 13):
                t, _ = toa_sx126x(pl, sf, BW_HZ[bwk])
                cells.append(f"SF{sf}:{t*1e3:7.1f} ({1/t:5.1f} Hz)")
            print(f"  BW{bwk:>3} PL{pl:3d}: " + " ".join(cells))
    print()

    print("Effect of options on a 32-byte packet, SF9/BW125:")
    base, _ = toa_sx126x(32, 9, BW_HZ[125])
    for label, kw in [("baseline CR4/5 explicit CRC pre8", {}),
                      ("implicit header", {"explicit": False}),
                      ("no CRC", {"crc": False}),
                      ("CR4/8", {"cr": 4}),
                      ("preamble 16", {"npre": 16}),
                      ("LDRO forced on", {"de": True})]:
        t, _ = toa_sx126x(32, 9, BW_HZ[125], **kw)
        print(f"  {label:34s}: {t*1e3:7.2f} ms ({(t/base-1)*100:+5.1f} %)")


def regulatory_timing():
    """Duty-cycle and dwell-time consequences (used by ism-band-plans-duty-cycle.md)."""
    print("\nRegulatory timing (preamble 8, explicit, CRC, CR4/5):")
    print("  Max PHY payload that fits a 400 ms dwell (FCC 15.247 FHSS / AS923 dwell):")
    for bwk in (125, 500):
        row = []
        for sf in range(7, 13):
            best = 0
            for pl in range(1, 256):
                t, _ = toa_sx126x(pl, sf, BW_HZ[bwk])
                if t <= 0.4:
                    best = pl
            row.append(f"SF{sf}:{best:3d} B")
        print(f"    BW{bwk}: " + "  ".join(row))
    print("  Minimum interval between 32-byte packets under a duty-cycle limit (T_packet / d):")
    for sf, bwk in ((7, 125), (9, 125), (12, 125), (7, 250), (7, 500)):
        t, _ = toa_sx126x(32, sf, BW_HZ[bwk])
        print(f"    SF{sf}/BW{bwk}: ToA {t*1e3:7.1f} ms -> 1 %: {t/0.01:7.2f} s, 10 %: {t/0.1:6.2f} s, "
              f"0.1 %: {t/0.001:8.1f} s")


if __name__ == "__main__":
    main()
    regulatory_timing()
