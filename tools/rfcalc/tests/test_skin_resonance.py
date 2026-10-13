"""Expected values: kb/02-electromagnetics/skin-effect-conductor-loss-roughness.md (Examples 1-3) and
kb/01-circuit-theory/resonance-and-q.md (Examples 1-3)."""
import pytest

from rfcalc import resonance as r
from rfcalc import skin as s


def test_skin_depth_433():
    assert float(s.skin_depth(433e6, 5.8e7)) * 1e6 == pytest.approx(3.18, abs=0.01)
    assert float(s.surface_resistance(433e6, 5.8e7)) * 1e3 == pytest.approx(5.43, abs=0.01)


def test_wire_resistance_433():
    # 1 mm copper wire at 433 MHz: R' = 1.73 ohm/m (asymptote and exact Bessel agree)
    assert s.wire_resistance_hf_per_m(433e6, 0.5e-3) == pytest.approx(1.73, abs=0.01)
    assert s.wire_resistance_per_m(433e6, 0.5e-3) == pytest.approx(1.73, abs=0.01)


def test_wire_resistance_dc_limit():
    assert s.wire_resistance_per_m(10.0, 0.5e-3) == pytest.approx(s.dc_resistance_per_m(0.5e-3), rel=1e-3)


def test_silver_gold_5g8():
    # Rs(Ag) = 19.1 mohm, Rs(Au) = 22.5 mohm at 5.8 GHz
    assert float(s.surface_resistance(5.8e9, s.CONDUCTIVITY["silver"])) * 1e3 == pytest.approx(19.1, abs=0.1)
    assert float(s.surface_resistance(5.8e9, s.CONDUCTIVITY["gold"])) * 1e3 == pytest.approx(22.5, abs=0.1)


def test_roughness_limits():
    assert float(s.roughness_hammerstad(1e6, 1e-6)) == pytest.approx(1.0, abs=0.01)
    assert float(s.roughness_hammerstad(100e9, 3e-6)) == pytest.approx(2.0, abs=0.02)


def test_series_trap_433():
    L, C = 22e-9, 6.115e-12
    assert r.f_res(L, C) / 1e6 == pytest.approx(433.92, abs=0.05)
    assert r.char_reactance(L, C) == pytest.approx(59.98, abs=0.02)
    rs = r.esr_from_q(r.char_reactance(L, C), 50)
    assert rs == pytest.approx(1.20, abs=0.01)
    assert r.bandwidth_3db(433.92e6, 50) / 1e6 == pytest.approx(8.68, abs=0.01)


def test_bandpass_tank_433():
    # Q_L = 7.14 -> IL 1.34 dB, group delay 5.24 ns; Q_L = 43 of Qu 50 -> IL 17.6 dB
    assert r.resonator_il_db(7.14, 50) == pytest.approx(1.34, abs=0.01)
    assert r.group_delay_s(7.14, 433.92e6) * 1e9 == pytest.approx(5.24, abs=0.01)
    assert r.resonator_il_db(43.5, 50) == pytest.approx(17.7, abs=0.3)


def test_q_combination():
    assert r.q_combined(45, 500) == pytest.approx(41.3, abs=0.1)


def test_lc_inverse():
    c = r.c_for_f(433.92e6, 22e-9)
    assert c * 1e12 == pytest.approx(6.115, abs=0.002)
    assert r.l_for_f(433.92e6, c) == pytest.approx(22e-9)
