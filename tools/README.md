# tools/ — runnable calculators, verification scripts and index builder

Everything here is plain Python 3 (tested with anaconda Python 3.13 on macOS / Apple Silicon: numpy,
scipy, sympy, matplotlib, scikit-rf 2.0.1, pytest 8). Nothing needs installing beyond that, except where
a script says so (PyNEC, ngspice, openEMS — see
[kb/16-simulation-tools/installing-tools-macos.md](../kb/16-simulation-tools/installing-tools-macos.md)).

```
tools/
  README.md          this file
  build_index.py     regenerates INDEX.md and FAQ.md from tools/taxonomy.md + page front-matter
  taxonomy.md        planned page list per domain (edit this to plan pages)
  rfcalc/            tested RF calculator package + CLI (python3 -m rfcalc ...)
    tests/           pytest suite; expected values come from KB worked examples
  verify/            ~150 verification scripts, one family per KB domain (see below)
```

## rfcalc — the KB's calculators in one package

`rfcalc` consolidates formulas that were derived and verified in `tools/verify/` by the domain agents
(each module's docstring names the script it was ported from and the KB page it serves).

| Module | Contents |
|---|---|
| `units` | dB/dBm/W/V/dBµV conversions, add/subtract powers, field strength ↔ received power, antenna factor, Γ/VSWR/return loss/mismatch loss, wavelength |
| `link` | FSPL, Friis, EIRP/ERP, effective aperture, noise floor, `LinkBudget` (line items, margin, range for a margin) |
| `propagation` | Fresnel radius (paraxial, exact, ITU form), earth bulge, radio horizon, LOS altitude, Fresnel-clear altitude, elevation angle |
| `noise` | kTB, NF ↔ Te, lossy-line NF/Te, antenna temperature through loss, `Stage`/`cascade` (NF, gain, IIP3 coherent & power-sum, IP1dB, OIP3), noise shares, Friis, sensitivity, MDS, SFDR, C/N0, two-tone IIP3/IIP2 helpers |
| `matching` | L-match (complex load, both solutions, component values), real L-match Q, π and T networks, finite-Q loss estimate, quarter-wave transformer, single shunt stub, line input impedance |
| `tline` | microstrip (Hammerstad–Jensen ± thickness, Wheeler-77, simple form, Kirschning–Jansen dispersion, Pozar synthesis, width root-finding, loss), stripline (Cohn, Wheeler-78), CPW and CPWG (Ghione–Naldi), coax (Z0, loss, TE11 cutoff), guided wavelength, L and C per metre |
| `skin` | skin depth, surface resistance, conductivity table, roughness (Hammerstad, Groiss), round-wire AC resistance (exact Bessel and HF asymptote) |
| `resonance` | LC resonance, L or C for a frequency, characteristic reactance, series/parallel Q, bandwidth, loaded Q, resonator insertion loss, group delay |
| `radar` | radar range equation (received power, SNR with bandwidth or integration time, max range), Albersheim, range resolution, unambiguous range, Doppler (one-/two-way), FMCW parameters, beat frequency, RCS of sphere/plate/trihedral |
| `arrays` | ULA array factor (complex/dB), steering phase, HPBW, first null, grating-lobe spacing limit, exact directivity, coherent array gain |
| `lora` | symbol time, LDRO rule, symbol count and time on air (SX127x and SX126x forms), bit rate, sensitivity from the SNR table, processing gain, packet rate |

### Running the CLI
Run from the `tools/` directory (or set `PYTHONPATH=/path/to/RF Physics/tools`). Numbers accept SI
suffixes (`433.125M`, `12p`, `22n`, `125k`, `2.4G`) and lengths accept `mm`, `um`, `cm`, `km`, `mil`.

```bash
cd tools
python3 -m rfcalc --help
python3 -m rfcalc fspl 433.125M 30km                                   # 114.72 dB
python3 -m rfcalc link --f 433.125M --d 30km --pt 33 --tx-loss 0.5 --gr 11 --rx-loss 0.45 --other 4.1 --sf 7 --margin 20
python3 -m rfcalc fresnel 433.125M 30km                                # 72 m mid-path
python3 -m rfcalc horizon 3000 --h2 2                                  # 225.8 km, 231.6 km LOS
python3 -m rfcalc cascade --stage SAW:-1.5 --stage LNA:18:0.7:8 --stage coax:-2.6 --stage module:0:6:-5 --bw 125k --snr -20
python3 -m rfcalc sens --bw 125k --nf 6 --snr -20                      # -137.0 dBm
python3 -m rfcalc lmatch 32.1-18.5j --f 433M                           # 15.61 nH + 5.49 pF (or 67.19 pF + 24.61 nH)
python3 -m rfcalc microstrip --h 1.51mm --er 4.5 --z0 50 --f 915M      # W = 2.797 mm
python3 -m rfcalc cpwg --s 0.2mm --h 1.51mm --er 4.5 --z0 50           # zero-thickness model: see the calculators page
python3 -m rfcalc coax 2.74mm 7.24mm --er 1.384                        # LMR-400: 49.5 ohm
python3 -m rfcalc skin 433M                                            # 3.176 um
python3 -m rfcalc lc --l 22n --c 6.115p                                # 433.9 MHz
python3 -m rfcalc radar --pt 1 --g 20 --f 24G --rcs 1 --r 100 --tint 1e-3
python3 -m rfcalc fmcw --f0 77G --bw 4G --tc 40e-6 --fs 10M            # 3.75 cm resolution
python3 -m rfcalc array 8 0.5 --steer 30                               # HPBW 14.65 deg, 90 deg/element
python3 -m rfcalc lora --sf 9 --pl 32                                  # 246.78 ms
python3 -m rfcalc db vswr 2                                            # RL 9.54 dB, ML 0.512 dB
```

### From Python
```python
import sys; sys.path.insert(0, "tools")
from rfcalc import link, noise, lora, matching, tline
link.fspl_db(433.125e6, 30e3)                     # 114.72
noise.cascade([noise.Stage("cable", -3), noise.Stage("LNA", 20, 0.8), noise.Stage("module", 0, 6)])[-1]["NF_cum_dB"]   # 3.91
lora.time_on_air(32, 12, 125e3)                   # 1.810 s (LDRO on automatically)
tline.microstrip_hj(0.36e-3, 0.2104e-3, 4.4, 35e-6)   # (50.92 ohm, eps_eff)
```

### Tests
```bash
cd tools && python3 -m pytest rfcalc/tests -q      # 142 passed in ~0.1 s (2026-09-29)
```
Expected values are taken from the KB pages' worked examples (the test docstrings name the page) and a
few published references (TI FMCW relations, Albersheim). Where a KB page rounds, the test states the
tolerance; where rfcalc disagreed with a page, the discrepancy was investigated and logged in
`research-logs/W3-C2-simulation-tools.md` rather than papered over.

## verify/ — verification scripts

Each KB domain agent wrote scripts named `<prefix>_<topic>.py` that check the equations and numbers on
its pages numerically (closed forms vs brute force, vs scikit-rf, vs independent solvers). Run any of
them with `python3 tools/verify/<script>.py`; they print `[PASS]`/`[FAIL]` lines (some print `[MISS]` for
pre-registered expectations that were not met — findings, not errors).

| Prefix | Domain (kb folder) |
|---|---|
| `math_` | 00-math-foundations |
| `circuits_` | 01-circuit-theory |
| `em_` | 02-electromagnetics |
| `tline_` | 03-transmission-lines-matching (incl. `tline_fd2d.py`, a 2-D field solver) |
| `components_` | 04-real-components-hf |
| `analog_` | 05-analog-electronics (incl. `analog_ngspice.py`, a runner for KiCad's bundled libngspice) |
| `rfckt_` | 06-rf-circuits |
| `noise_` | 07-noise-linearity |
| `ant_` | 08-antennas (incl. `ant_mom_wire.py`, `ant_mom_general.py`: an independent thin-wire MoM) |
| `prop_` | 09-propagation-link-budget |
| `comms_` | 10-comms-modulation |
| `radar_` | 11-radar |
| `array_` | 12-phased-arrays |
| `pcb_` | 13-pcb-rf-layout-emc |
| `dsp_` | 14-sdr-dsp |
| `lora_` | 15-lora-ism-radios |
| `sim_` | 16-simulation-tools (below) |
| `meas_` | 17-test-measurement |
| `reg_`, `proj_` | 19-regulations-safety, 20-projects-recipes |

### sim_ scripts (domain 16)
| Script | Needs | What it checks | Runtime |
|---|---|---|---|
| `sim_ngspice_examples.py` | `brew install ngspice` (and optionally KiCad) | L-match `.sp`, Butterworth LPF, Colpitts, pad NF, vector-fit → SPICE; KiCad libngspice route | ~1 s |
| `sim_nec_vs_mom.py` | `pip install PyNEC` | NEC-2 vs own MoM: dipoles, DL6WU Yagi, monopole; segmentation study | ~15 s |
| `sim_openems_msl.py` | openEMS (source build) | microstrip Z0/εeff vs H-J and FD solver, 2 meshes | ~20 s |
| `sim_openems_patch.py` | openEMS | 2.45 GHz FR-4 patch: f_res, Z_in, BW, D, efficiency, 3 meshes | ~90 s |
| `sim_harmonic_balance.py` | numpy/scipy | own harmonic-balance solver vs transient (tripler) | ~1 min |

openEMS scripts must be run with the openEMS venv interpreter:
`~/opt/openEMS/venv/bin/python tools/verify/sim_openems_patch.py` (set `RFKB_EXACT_EC=1` for
`sim_openems_msl.py` to make the FDTD stopping step deterministic). Results are appended to
`tools/verify/sim_openems_results.txt`.

## build_index.py
```bash
python3 tools/build_index.py            # rebuild INDEX.md and FAQ.md
python3 tools/build_index.py --check    # also report broken links and missing template sections
```
