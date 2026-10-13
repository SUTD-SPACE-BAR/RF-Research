"""Expected values: kb/03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
(Examples 1-4) and kb/01-circuit-theory/resonance-and-q.md (Example 4)."""
import math

import pytest

from rfcalc import matching as m


def test_example1_real_lmatch_433():
    q, xs, xp = m.l_match_real(50.0, 12.5)
    assert q == pytest.approx(1.732, abs=1e-3)
    kind, L = m.x_to_component(xs, 433e6)
    assert kind == "L" and L * 1e9 == pytest.approx(7.96, abs=0.01)
    kind, C = m.x_to_component(xp, 433e6)
    assert kind == "C" and C * 1e12 == pytest.approx(12.73, abs=0.01)
    # page: ~0.21 dB with a Q = 40 inductor (verify script uses capacitor Q = 300)
    assert m.l_match_loss_db(q, 40, 300) == pytest.approx(0.21, abs=0.01)


def test_example2_chip_antenna_433():
    sols = m.l_match(32.1 - 18.5j, 50.0, 433e6)
    comps = [s.components() for s in sols]
    # (A) 15.6 nH series + 5.49 pF shunt; (B) 67 pF series + 24.6 nH shunt
    a = [c for c in comps if c["series"][0] == "L"][0]
    b = [c for c in comps if c["series"][0] == "C"][0]
    assert a["series"][1] * 1e9 == pytest.approx(15.6, abs=0.05)
    assert a["shunt"][1] * 1e12 == pytest.approx(5.49, abs=0.01)
    assert b["series"][1] * 1e12 == pytest.approx(67.2, abs=0.2)
    assert b["shunt"][1] * 1e9 == pytest.approx(24.6, abs=0.05)
    for s in sols:
        assert s.zin(32.1 - 18.5j) == pytest.approx(50.0 + 0j, abs=1e-9)


def test_example3_chip_antenna_915():
    sols = m.l_match(18 - 35j, 50.0, 915e6)
    xs = sorted(s.x_series for s in sols)
    assert xs == pytest.approx([11.0, 59.0], abs=0.05)
    assert sorted(abs(s.b_shunt) * 1e3 for s in sols) == pytest.approx([26.7, 26.7], abs=0.05)
    big = [s for s in sols if s.x_series > 30][0].components()
    assert big["series"][1] * 1e9 == pytest.approx(10.26, abs=0.02)
    assert big["shunt"][1] * 1e12 == pytest.approx(4.64, abs=0.01)


def test_high_load_topology():
    for zl in (200 - 100j, 100 + 80j):
        for s in m.l_match(zl):
            assert s.topology == "shunt-at-load"
            assert s.zin(zl) == pytest.approx(50 + 0j, abs=1e-9)


def test_pi_and_t_match_exact():
    for q in (3, 5, 8):
        p = m.pi_match(50.0, 10.0, q)
        # build input impedance: shunt(src) || [ series + (shunt(load) || RL) ]
        zload = 1 / (1 / 10.0 + 1 / (1j * p["X_shunt_load"]))
        z = 1 / (1 / (zload + 1j * p["X_series"]) + 1 / (1j * p["X_shunt_src"]))
        assert z == pytest.approx(50 + 0j, abs=1e-9)
    t = m.t_match(50.0, 10.0, 5.0)
    assert t["Rv"] == pytest.approx(260.0)
    z = 1j * t["X_series_load"] + 10.0
    z = 1 / (1 / z + 1 / (1j * t["X_shunt"]))
    z = z + 1j * t["X_series_src"]
    assert z == pytest.approx(50 + 0j, abs=1e-9)


def test_pi_rejects_low_q():
    with pytest.raises(ValueError):
        m.pi_match(50.0, 10.0, 1.5)


def test_example4_single_stub():
    sols = m.shunt_stub(60 - 80j, 50.0)
    ds = sorted(s["d_lambda"] for s in sols)
    assert ds[0] == pytest.approx(0.1104, abs=2e-4)
    s1 = [s for s in sols if abs(s["d_lambda"] - 0.1104) < 1e-3][0]
    assert s1["short_lambda"] == pytest.approx(0.0950, abs=2e-4)
    s2 = [s for s in sols if s is not s1][0]
    assert s2["open_lambda"] == pytest.approx(0.155, abs=1e-3)


def test_resonance_page_example4_q():
    assert m.l_match_real(50.0, 5.0)[0] == pytest.approx(3.0)


def test_quarter_wave():
    assert m.quarter_wave_z(50.0, 12.5) == pytest.approx(25.0)
    # lambda/4 of 25 ohm line transforms 12.5 -> 50
    assert m.zin_line(12.5, 25.0, math.pi / 2) == pytest.approx(50.0 + 0j, rel=1e-9)
