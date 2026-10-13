"""Expected values: kb/09-propagation-link-budget/friis-free-space-path-loss.md and
link-budget-methodology.md (Example A, range table)."""
import pytest

from rfcalc import link, lora


def test_fspl_constant():
    # 32.45 dB constant (d km, f MHz)
    assert float(link.fspl_db(1e6, 1e3)) == pytest.approx(32.45, abs=0.01)


def test_fspl_433_30km():
    assert float(link.fspl_db(433.125e6, 30e3)) == pytest.approx(114.7, abs=0.05)


def test_fspl_915_30km():
    assert float(link.fspl_db(915e6, 30e3)) == pytest.approx(121.2, abs=0.05)


def test_friis_example1():
    # 33 - 0.5 + 0 + 11 - 114.7 = -71.2 dBm
    pr = link.friis_pr_dbm(33.0, 0.0, 11.0, 433.125e6, 30e3, other_losses_db=0.5)
    assert pr == pytest.approx(-71.2, abs=0.05)


def test_link_budget_example_a():
    lb = link.LinkBudget(f_hz=433.125e6, d_m=30e3)
    for name, v in [("Tx", 33.0), ("Tx feeder", -0.5), ("Rocket ant", 0.0), ("Gases", -0.1),
                    ("Pol", -3.0), ("Pointing", -1.0), ("GS ant", 11.0), ("Rx feeder", -0.45)]:
        lb.add(name, v)
    assert lb.received_dbm() == pytest.approx(-75.8, abs=0.05)
    assert lb.margin_db(-127.75) == pytest.approx(52.0, abs=0.3)


@pytest.mark.parametrize("sf,bw,km", [(7, 125e3, 820), (12, 125e3, 3458), (7, 500e3, 410), (12, 62.5e3, 4890)])
def test_range_table(sf, bw, km):
    lb = link.LinkBudget(f_hz=433.125e6, d_m=30e3)
    for v in (33.0, -0.5, 0.0, -0.1, -3.0, -1.0, 11.0, -0.45):
        lb.add("x", v)
    r = lb.range_for_margin_m(lora.sensitivity_dbm(sf, bw, 6.0), 20.0) / 1e3
    assert r == pytest.approx(km, rel=0.01)


def test_balloon_record_fspl():
    # 832 km at 868 MHz -> 149.6 dB (friis page Example 4)
    assert float(link.fspl_db(868e6, 832e3)) == pytest.approx(149.6, abs=0.1)


def test_aperture_gain():
    # 0.5 m^2 aperture: 11.2 dBi at 433 MHz, 17.7 dBi at 915 MHz (friis page Example 3)
    assert float(link.gain_from_aperture_dbi(0.5, 433e6)) == pytest.approx(11.2, abs=0.05)
    assert float(link.gain_from_aperture_dbi(0.5, 915e6)) == pytest.approx(17.7, abs=0.05)


def test_noise_floor():
    # decibels page Example 2: 125 kHz, NF 6 dB -> -117.0 dBm
    assert float(link.noise_floor_dbm(125e3, 6.0)) == pytest.approx(-117.0, abs=0.05)


def test_erp():
    assert link.erp_dbm(33.8) == pytest.approx(31.65)
