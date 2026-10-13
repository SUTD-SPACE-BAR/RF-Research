"""Expected values: kb/11-radar/detection-theory-cfar.md (Albersheim numbers), TI SPYY005 FMCW relations
(Iovescu & Rao 2017: B = 4 GHz -> 3.75 cm), and hand calculations shown in the comments."""
import math

import pytest

from rfcalc import radar as r


def test_albersheim_single_pulse():
    # Pd 0.9, Pfa 1e-6: exact Swerling-0 13.2 dB; Albersheim within 0.3 dB
    assert r.albersheim_snr_db(0.9, 1e-6, 1) == pytest.approx(13.2, abs=0.3)
    assert r.albersheim_snr_db(0.9, 1e-6, 1) == pytest.approx(13.11, abs=0.02)


def test_albersheim_n10():
    # detection-theory-cfar.md: N = 10, Pfa 1e-4, Pd 0.9 -> Albersheim 3.89 dB
    assert r.albersheim_snr_db(0.9, 1e-4, 10) == pytest.approx(3.89, abs=0.01)


def test_received_power_hand_calc():
    # Pt 1 W, G 20 dBi both, 24 GHz, sigma 1 m^2, R 100 m:
    # Pr = 30 + 20 + 20 + 20log10(lambda) - 30log10(4 pi) - 40log10(R) [dBm] = -81.04 dBm
    pr = r.radar_received_power_w(1.0, 20.0, 20.0, 24e9, 1.0, 100.0)
    assert 10 * math.log10(pr / 1e-3) == pytest.approx(-81.04, abs=0.01)


def test_r4_law():
    a = r.radar_snr_db(1.0, 20, 20, 24e9, 1.0, 100.0, 10.0, t_int_s=1e-3)
    b = r.radar_snr_db(1.0, 20, 20, 24e9, 1.0, 200.0, 10.0, t_int_s=1e-3)
    assert a - b == pytest.approx(40 * math.log10(2), abs=1e-9)


def test_max_range_inverse():
    rmax = r.radar_max_range_m(1.0, 20, 20, 24e9, 1.0, 13.0, 10.0, t_int_s=1e-3)
    assert r.radar_snr_db(1.0, 20, 20, 24e9, 1.0, rmax, 10.0, t_int_s=1e-3) == pytest.approx(13.0, abs=1e-9)


def test_snr_bw_vs_tint_equivalent():
    a = r.radar_snr_db(1.0, 20, 20, 24e9, 1.0, 100.0, 10.0, bw_hz=1e3)
    b = r.radar_snr_db(1.0, 20, 20, 24e9, 1.0, 100.0, 10.0, t_int_s=1e-3)
    assert a == pytest.approx(b)
    with pytest.raises(ValueError):
        r.radar_snr_db(1.0, 20, 20, 24e9, 1.0, 100.0, 10.0)


def test_fmcw_ti_relations():
    p = r.fmcw_params(77e9, 4e9, 40e-6, 10e6, n_chirps=128)
    assert p["range_resolution_m"] == pytest.approx(0.0375, abs=1e-4)      # TI: 4 GHz -> 3.75 cm
    lam = 299_792_458.0 / 77e9
    assert p["v_max_mps"] == pytest.approx(lam / (4 * 40e-6))
    assert p["v_resolution_mps"] == pytest.approx(lam / (2 * 128 * 40e-6))
    # beat frequency of a 10 m target: 2 S R / c
    assert r.fmcw_beat_frequency_hz(10.0, 4e9, 40e-6) == pytest.approx(2 * 1e14 * 10 / 299_792_458.0)
    assert p["max_range_m"] == pytest.approx(10e6 * 299_792_458.0 / (2 * 1e14))


def test_pulse_relations():
    assert r.unambiguous_range_m(1e3) == pytest.approx(149_896.229)
    assert r.range_resolution_m(1e6) == pytest.approx(149.896229)


def test_doppler():
    # 300 m/s rocket at 433 MHz: one-way 433.3 Hz, two-way 866.6 Hz
    assert r.one_way_doppler_hz(300, 433e6) == pytest.approx(433.3, abs=0.1)
    assert r.doppler_shift_hz(300, 433e6) == pytest.approx(866.6, abs=0.1)


def test_rcs_canonical():
    assert r.rcs_sphere_m2(0.1) == pytest.approx(math.pi * 0.01)
    # triangular trihedral a = 0.1 m at 24 GHz: 4 pi a^4 / (3 lambda^2) = 2.685 m^2 = 4.29 dBsm
    assert r.dbsm(r.rcs_trihedral_m2(0.1, 24e9)) == pytest.approx(4.29, abs=0.01)
