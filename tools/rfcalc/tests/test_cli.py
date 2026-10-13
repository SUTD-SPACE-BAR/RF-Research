"""CLI smoke tests: the documented commands in tools/README.md must run and print the KB numbers."""
import pytest

from rfcalc import cli


@pytest.mark.parametrize("s,v", [("433.125M", 433.125e6), ("1.51mm", 1.51e-3), ("30km", 30e3), ("12p", 12e-12),
                                 ("2.4G", 2.4e9), ("35um", 35e-6), ("1e-3", 1e-3), ("125k", 125e3),
                                 ("10mil", 254e-6), ("22n", 22e-9)])
def test_num_parser(s, v):
    assert cli.num(s) == pytest.approx(v)


def run(capsys, *argv):
    assert cli.main(list(argv)) == 0
    return capsys.readouterr().out


def test_fspl(capsys):
    assert "114.72 dB" in run(capsys, "fspl", "433.125M", "30km")


def test_lora(capsys):
    assert "246.78 ms" in run(capsys, "lora", "--sf", "9", "--pl", "32")


def test_lmatch(capsys):
    out = run(capsys, "lmatch", "32.1-18.5j", "--f", "433M")
    assert "15.61 nH" in out and "5.49 pF" in out


def test_cascade(capsys):
    out = run(capsys, "cascade", "--stage", "SAW:-1.5", "--stage", "LNA:18:0.7:8", "--stage", "coax:-2.6",
              "--stage", "module:0:6:-5", "--bw", "125k", "--snr", "-20")
    assert "-140.5 dBm" in out and "SFDR = 67.7 dB" in out


def test_microstrip(capsys):
    assert "2.7970 mm" in run(capsys, "microstrip", "--h", "1.51mm", "--er", "4.5", "--z0", "50")


@pytest.mark.parametrize("argv", [
    ["fresnel", "433.125M", "30km"], ["horizon", "3000", "--h2", "2"], ["sens", "--bw", "125k", "--nf", "6", "--snr", "-20"],
    ["cpwg", "--s", "0.2mm", "--h", "1.51mm", "--er", "4.5", "--z0", "50"], ["coax", "2.74mm", "7.24mm", "--er", "1.384"],
    ["skin", "433M"], ["lc", "--l", "22n", "--c", "6.115p"], ["lc", "--l", "22n", "--f", "433.92M"],
    ["radar", "--pt", "1", "--g", "20", "--f", "24G", "--rcs", "1", "--r", "100", "--tint", "1e-3"],
    ["fmcw", "--f0", "77G", "--bw", "4G", "--tc", "40e-6", "--fs", "10M"], ["array", "8", "0.5", "--steer", "30"],
    ["db", "dbm2w", "33"], ["db", "w2dbm", "2"], ["db", "vswr", "2"], ["db", "rl", "10"],
    ["link", "--f", "433.125M", "--d", "30km", "--pt", "33", "--gr", "11", "--sf", "7", "--margin", "20"],
    ["itm", "--f", "433.125M", "--d", "10km", "--dh", "30"],
])
def test_all_commands_run(capsys, argv):
    assert run(capsys, *argv).strip()


def test_itm_area_matches_ntia_vector(capsys):
    # NTIA area.csv row 1: 10 m / 1 m, 16 km, dh 0, 230 MHz, H-pol, climate 5, N0 301, 87/50/50 % -> 152.5 dB
    out = run(capsys, "itm", "--f", "230M", "--d", "16km", "--htx", "10", "--hrx", "1", "--dh", "0", "--pol", "0",
              "--climate", "5", "--n0", "301", "--er", "15", "--sigma", "0.008", "--mdvar", "0", "--time", "87")
    assert "152.51 dB" in out
