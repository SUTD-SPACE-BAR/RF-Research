"""ITM (Longley-Rice v1.2.2) port: NTIA reference vectors + internal unit tests.

Reference vectors re-typed from https://github.com/NTIA/itm (area.csv, p2p.csv, pfls.csv). NTIA prints
A__db to 0.1 dB (area) and 0.01 dB (p2p), so the tolerance is 0.06 / 0.01 dB (rounding + float noise).
p2p row 1 (a 3679-interval profile) was not transcribed; rows 2-5 cover line-of-sight and diffraction,
the area rows cover line-of-sight and troposcatter. Page: kb/16-simulation-tools/tool-landscape-overview.md.
"""
import csv
import math
import os

import pytest

from rfcalc import itm

DATA = os.path.join(os.path.dirname(__file__), "data")


def _rows(name):
    with open(os.path.join(DATA, name)) as fh:
        return list(csv.DictReader(fh))


def _profiles():
    out = []
    with open(os.path.join(DATA, "itm_pfls.csv")) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            out.append([float(v) for v in line.split(",")])
    return out


AREA = _rows("itm_area.csv")
P2P = _rows("itm_p2p.csv")
PFLS = _profiles()                     # profiles for p2p rows 2..5


@pytest.mark.parametrize("r", AREA, ids=[f"area{i+1}" for i in range(len(AREA))])
def test_area_vectors(r):
    g = lambda k: float(r[k])          # noqa: E731
    out = itm.itm_area_tls(g("h_tx__meter"), g("h_rx__meter"), int(g("tx_siting_criteria")),
                           int(g("rx_siting_criteria")), g("d__km"), g("delta_h__meter"), int(g("climate")),
                           g("N_0"), g("f__mhz"), int(g("pol")), g("epsilon"), g("sigma"), int(g("mdvar")),
                           g("time"), g("location"), g("situation"))
    assert out["A_db"] == pytest.approx(g("A__db"), abs=0.06)


@pytest.mark.parametrize("k", range(len(PFLS)), ids=[f"p2p{k+2}" for k in range(len(PFLS))])
def test_p2p_vectors(k):
    r = P2P[k + 1]
    pfl = PFLS[k]
    assert len(pfl) == int(pfl[0]) + 3                       # transcription completeness check
    g = lambda key: float(r[key])      # noqa: E731
    out = itm.itm_p2p_tls(g("h_tx__meter"), g("h_rx__meter"), pfl, int(g("climate")), g("N_0"), g("f__mhz"),
                          int(g("pol")), g("epsilon"), g("sigma"), int(g("mdvar")), g("time"), g("location"),
                          g("situation"))
    assert out["A_db"] == pytest.approx(g("A__db"), abs=0.01)


def test_vectors_cover_all_three_modes():
    modes = set()
    for r in AREA:
        g = lambda k: float(r[k])      # noqa: E731
        modes.add(itm.itm_area_tls(g("h_tx__meter"), g("h_rx__meter"), int(g("tx_siting_criteria")),
                                   int(g("rx_siting_criteria")), g("d__km"), g("delta_h__meter"), int(g("climate")),
                                   g("N_0"), g("f__mhz"), int(g("pol")), g("epsilon"), g("sigma"), int(g("mdvar")),
                                   g("time"), g("location"), g("situation"))["mode"])
    for k, pfl in enumerate(PFLS):
        r = P2P[k + 1]
        g = lambda key: float(r[key])  # noqa: E731
        modes.add(itm.itm_p2p_tls(g("h_tx__meter"), g("h_rx__meter"), pfl, int(g("climate")), g("N_0"),
                                  g("f__mhz"), int(g("pol")), g("epsilon"), g("sigma"), int(g("mdvar")), g("time"),
                                  g("location"), g("situation"))["mode"])
    assert modes == {1, 2, 3}


def test_free_space_loss_matches_kb_constant():
    # 32.45 + 20 log f_MHz + 20 log d_km (canonical FSPL form, 00/canonical-values)
    assert itm.free_space_loss(30e3, 433.0) == pytest.approx(32.45 + 20 * math.log10(433) + 20 * math.log10(30))


def test_inverse_ccdf():
    assert itm.inverse_ccdf(0.1) == pytest.approx(1.2816, abs=4.5e-4)
    assert itm.inverse_ccdf(0.5) == pytest.approx(0.0, abs=4.5e-4)
    assert itm.inverse_ccdf(0.9) == pytest.approx(-1.2816, abs=4.5e-4)


def test_fresnel_integral_knife_edge():
    # v = 0 (grazing): 6.02 dB; continuity at v^2 = 5.76 within 0.05 dB
    assert itm.fresnel_integral(0.0) == pytest.approx(6.02)
    assert itm.fresnel_integral(5.759999) == pytest.approx(itm.fresnel_integral(5.76), abs=0.05)


def test_profile_builder_and_errors():
    pfl = itm.profile_from_elevations([10, 12, 15, 11], 100.0)
    assert pfl == [3.0, 100.0, 10.0, 12.0, 15.0, 11.0]
    with pytest.raises(ValueError):
        itm.profile_from_elevations([1.0], 100.0)
    flat = itm.profile_from_elevations([0.0] * 51, 200.0)
    with pytest.raises(ValueError):                              # TX height below 0.5 m is a hard error
        itm.itm_p2p_tls(0.1, 2, flat, 5, 301, 433, 1, 15, 0.005, 12, 50, 50, 50)
    with pytest.raises(ValueError):                              # climate 9 does not exist
        itm.itm_p2p_tls(2, 2, flat, 9, 301, 433, 1, 15, 0.005, 12, 50, 50, 50)


def test_area_loss_monotonic_in_distance():
    a = [itm.itm_area_tls(5, 2, 0, 0, d, 30, 5, 301, 433, 1, 15, 0.005, 12, 50, 50, 50)["A_db"]
         for d in (2, 5, 10, 20, 40, 80)]
    assert all(b > a_ for a_, b in zip(a, a[1:]))
