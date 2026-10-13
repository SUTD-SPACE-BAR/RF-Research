"""Expected values: kb/00-math-foundations/decibels-and-log-units.md (Worked examples 1-8)."""
import math

import pytest

from rfcalc import units as u
from rfcalc.constants import KT0_DBM_HZ


def test_kt0():
    assert KT0_DBM_HZ == pytest.approx(-173.975, abs=1e-3)


def test_dbm_watts_roundtrip():
    assert float(u.dbm_to_w(30)) == pytest.approx(1.0)
    assert float(u.w_to_dbm(2.0)) == pytest.approx(33.0103, abs=1e-4)


def test_example1_eirp_voltage():
    # 32.3 dBm at antenna -> 1.70 W; 2 W into 50 ohm -> 10.0 V rms, 14.1 V peak
    assert float(u.dbm_to_w(32.3)) == pytest.approx(1.70, abs=0.005)
    assert float(u.dbm_to_vrms(u.w_to_dbm(2.0))) == pytest.approx(10.0, abs=1e-6)
    assert float(u.dbm_to_vpk(u.w_to_dbm(2.0))) == pytest.approx(14.14, abs=0.01)


def test_example2_noise_floor_and_voltage():
    # -137 dBm in 50 ohm = 31.6 nV rms
    assert float(u.dbm_to_vrms(-137.0)) == pytest.approx(31.6e-9, rel=3e-3)


def test_example3_adding_interferers():
    assert float(u.add_powers_dbm(-95.0, -101.0)) == pytest.approx(-94.03, abs=0.01)


def test_example5_field_to_power():
    # 40 dBuV/m at 433 MHz into a 0 dBi antenna -> -89.9 dBm; AF = 22.96 dB/m
    assert float(u.field_dbuvm_to_dbm(40.0, 433e6, 0.0)) == pytest.approx(-89.9, abs=0.1)
    assert float(u.antenna_factor_db(433e6, 0.0)) == pytest.approx(22.96, abs=0.03)


def test_example6_mismatch():
    assert float(u.return_loss_db(0.01)) == pytest.approx(40.0)
    assert float(u.mismatch_loss_db(0.01)) == pytest.approx(0.0004, abs=5e-5)
    assert float(u.mismatch_loss_db(0.1)) == pytest.approx(0.044, abs=1e-3)
    assert float(u.mismatch_loss_db(u.gamma_from_vswr(2.0))) == pytest.approx(0.51, abs=0.01)
    assert float(u.vswr_to_rl(2.0)) == pytest.approx(9.54, abs=0.01)


def test_example8_subtract_noise():
    assert float(u.subtract_power_dbm(-95.5, -98.0)) == pytest.approx(-99.1, abs=0.05)


def test_dbuv_50ohm_offset():
    # 0 dBm into 50 ohm = 106.99 dBuV
    assert float(u.dbm_to_dbuv(0.0)) == pytest.approx(106.99, abs=0.01)
    assert float(u.dbuv_to_dbm(106.99)) == pytest.approx(0.0, abs=0.01)


def test_field_from_eirp():
    # friis-free-space-path-loss.md Example 5: 30 dBm EIRP at 3 m -> 1.8 V/m (sqrt(30*1)/3 = 1.826)
    assert float(u.eirp_to_field_vpm(1.0, 3.0)) == pytest.approx(math.sqrt(30) / 3, rel=2e-3)


def test_gamma_z_roundtrip():
    z = 32.1 - 18.5j
    assert complex(u.z_from_gamma(u.gamma_from_z(z))) == pytest.approx(z)
