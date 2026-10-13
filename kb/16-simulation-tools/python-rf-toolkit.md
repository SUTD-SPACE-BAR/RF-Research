---
title: Python RF toolkit — scikit-rf (networks, Touchstone, media, calibration, time domain, circuits, vector fitting), numpy/scipy signal, PyNEC, openEMS, radar/DOA/comms libraries, and this KB's rfcalc
domain: 16-simulation-tools
slug: python-rf-toolkit
tags: [python, scikit-rf, skrf, touchstone, s-parameters, calibration, sol, tdr, time-domain, circuit, vector-fitting, spice-export, numpy, scipy-signal, pynec, openems, radarsimpy, pyargus, commpy, gnu-radio, rfcalc]
prerequisites: [../03-transmission-lines-matching/s-parameters.md, ../00-math-foundations/fourier-series-and-transform.md]
related: [spice-circuit-simulation.md, nec-antenna-modelling.md, openems-workflow.md, impedance-and-rf-calculators.md, simulation-validation.md, ../14-sdr-dsp/_index.md, ../11-radar/_index.md, ../17-test-measurement/_index.md]
level: mixed
confidence: high
last_updated: 2026-09-29
---

# Python RF toolkit

## Questions this page answers
- How do I load, plot, cascade and de-embed Touchstone (.s1p/.s2p) files in Python?
- Can Python replace a circuit simulator for matching networks and filters?
- How do I calibrate or de-embed NanoVNA data in Python (SOL, fixtures)?
- How do I get a TDR (impedance vs distance) plot from S-parameters?
- How do I turn a measured S-parameter file into a SPICE model?
- Which Python packages exist for NEC, FDTD, radar simulation, direction finding, comms and SDR?
- What does this KB's `tools/rfcalc` package do, and how do I call it?

## TL;DR
- **scikit-rf (`skrf`)** is the core: `Network` (Touchstone I/O, S/Z/Y/ABCD, plotting, Smith charts), `**` cascading, `media` (lumped elements, `MLine` microstrip, `CPW`, `Coaxial`, `RectangularWaveguide`, `DefinedGammaZ0`), `calibration` (OnePort SOL, TwoPort SOLT/TRL/TRM, 8-/12-term), time domain (`step_response`, gating), `circuit.Circuit` (arbitrary netlists of networks), `vectorFitting.VectorFitting` (rational fits → SPICE subcircuits) [1], [2].
- **Tested here** (skrf 2.0.1): an L-match cascade gives $|S_{11}| = 1.7\times10^{-5}$ at 433 MHz and the same RL ≥ 10 dB band (323–520 MHz) as ngspice; `MLine` (Kirschning–Jansen) Z0 = 50.44 Ω, εeff 3.391 for the JLCPCB 2-layer 50 Ω line (= H-J); a OnePort SOL calibration removes a fixture to 7×10⁻¹⁶; a TDR of a 60 Ω line section reads 59.3 Ω; a vector-fitted LPF exported with `write_spice_subcircuit_s` reproduces the network in ngspice to < 0.001 dB.
- **API traps in skrf 2.0.1**: `Circuit` and `VectorFitting` are **not** top-level (`from skrf.circuit import Circuit`, `from skrf.vectorFitting import VectorFitting`); `DefinedGammaZ0`'s default `gamma` is `1j` rad/m (not free space — set it); `MLine`'s default `diel='djordjevicsvensson'` makes εr frequency-dependent from the value at 1 GHz; an ideal lossless network fails `is_passive()` (it sits on the boundary) — call passivity enforcement before transient use.
- **numpy/scipy** do the rest of RF DSP: FFT spectra, windows, `scipy.signal` filters (`butter`, `cheby1`, `firwin`, `freqz`), `chirp`, `hilbert`, `resample_poly`, CFAR-style statistics (`scipy.stats`, `scipy.special.marcumq`-like via `ncx2`) — see [SDR & DSP](../14-sdr-dsp/_index.md).
- **Solvers with Python front ends**: PyNEC (NEC-2), openEMS/CSXCAD (FDTD), MEEP (FDTD, conda-forge `pymeep`, not tested), ngspice via ctypes (`tools/verify/analog_ngspice.py`).
- **Domain libraries** (not installed here; checked on PyPI 2026-09-27): `scikit-commpy` 0.8.0 (modulation, channel coding), `pyargus` 1.1 (array signal processing / DOA), `pyadi-iio` 0.0.21 (ADI Pluto/SDR hardware), `pyrtlsdr` 0.5.0 (RTL-SDR); RadarSimPy (GPL-3.0, pre-built modules from its own site, free tier limited in targets/channels) [5]; GNU Radio 3.10 has a Homebrew formula but it is deprecated (Qt5, disable date 2027-05-19).
- **`tools/rfcalc`** — this KB's own tested calculators (dB, link budget, Fresnel/horizon, noise cascade, matching, line impedances, skin depth, resonance, radar/FMCW, arrays, LoRa); 142 pytest tests with expected values from the KB's worked examples; CLI `python3 -m rfcalc …` ([tools/README.md](../../tools/README.md)).

## Intuition (no math)
Think of an S-parameter file as a black-box "fingerprint" of a component at each frequency — how much of a wave bounces back and how much gets through, with phase. scikit-rf lets you treat those fingerprints like Lego: snap a measured SMA connector onto a simulated microstrip line onto a vendor's filter file, and read off the combined fingerprint. Because everything is linear and per-frequency, this is exact (for the linear, time-invariant parts) and fast — no meshing, no time stepping. It is the natural glue between measurement (NanoVNA files), circuit simulation (SPICE) and field simulation (openEMS exports Touchstone too).

The time-domain view is the same data seen differently: an inverse FFT of S11 is the reflection you would see if you launched a step down the line — a poor man's TDR. Vector fitting goes the other way: it finds a sum of poles that reproduces the fingerprint, which a SPICE simulator can then run in the time domain.

## The math

### Level 1 — cascading
Two-ports cascade by multiplying their transfer (T) or ABCD matrices; skrf's `a ** b` connects port 2 of `a` to port 1 of `b` (general `rf.connect` for any ports). For S-parameters directly, cascading two 2-ports gives
$$S_{11} = S^a_{11} + \frac{S^a_{12}S^a_{21}S^b_{11}}{1 - S^a_{22}S^b_{11}},\qquad S_{21} = \frac{S^a_{21}S^b_{21}}{1-S^a_{22}S^b_{11}}$$
(same $Z_0$ at the junction) — the denominator is the multiple-reflection sum, the source of "ripple" in cascaded mismatched parts [3].

### Level 2 — one-port calibration (SOL)
A reflectometer with an unknown linear error box measures $\Gamma_m = e_{00} + \frac{e_{01}e_{10}\Gamma}{1 - e_{11}\Gamma}$. Three known standards (short $\Gamma=-1$, open $+1$, load $0$, or their characterised models) give three equations for the three unknowns $e_{00}$ (directivity), $e_{11}$ (source match), $e_{01}e_{10}$ (tracking); inverting the bilinear map corrects any DUT [4]. skrf's `OnePort(ideals, measured)` solves this per frequency (least squares if more standards are given). The same algebra de-embeds a *fixture* if you can measure standards at the DUT plane — or, if you have the fixture's S-parameters (from openEMS or a 2x-thru), `fixture.inv ** measured` removes it.

### Level 3 — time domain and vector fitting
- **TDR from S11**: the step response is $\rho(t) = \mathcal F^{-1}\{S_{11}(f)/(j2\pi f)\}$ ≈ cumulative sum of the impulse response; the impedance profile is $Z(t) = Z_0\frac{1+\rho(t)}{1-\rho(t)}$ (accurate for the first discontinuity; later ones are masked by multiple reflections and loss). Resolution ≈ $1/(2 f_{max})$ in round-trip time, so a 6 GHz sweep resolves ≈ 25 mm in εeff 3.4 microstrip; windowing (Hamming, Kaiser) trades resolution for ringing [2].
- **Vector fitting** (Gustavsen & Semlyen [6]): approximate $H(s) \approx \sum_k \frac{r_k}{s - p_k} + d + se$ by iteratively relocating poles $p_k$ with a linear least-squares step. The rational form maps to an RLC/controlled-source network (skrf writes it as a SPICE subcircuit). A fitted model can be slightly non-passive (eigenvalues of $S^HS$ > 1 somewhere), which makes transient simulations blow up — enforce passivity before use.

## Design equations & rules of thumb

| Task | skrf call | Notes |
|---|---|---|
| Load / save | `n = rf.Network('dut.s2p')`, `n.write_touchstone('out')` | check `n.z0` (NanoVNA files are 50 Ω) |
| Plot | `n.plot_s_db()`, `n.plot_s_smith()` | `n['400-500MHz']` slices by frequency |
| Cascade | `a ** b`; `rf.connect(a, 1, b, 0)` | same frequency grid (`.interpolate()` first) |
| Lumped parts | `m = rf.media.DefinedGammaZ0(frequency=f, z0_port=50)`; `m.inductor(L)`, `m.shunt_capacitor(C)`, `m.resistor(R)` | set `gamma=` for a real line |
| Microstrip | `rf.media.MLine(frequency=f, w=, h=, t=, ep_r=, tand=, rough=, disp='kirschningjansen', diel='frequencyinvariant')` | `.line(length, 'm', embed=True, z0=50)` |
| CPWG | `rf.media.CPW(frequency=f, w=, s=, h=, ep_r=, t=, has_metal_backside=True)` | conformal mapping |
| One-port cal | `from skrf.calibration import OnePort`; `cal = OnePort(ideals=[s,o,l], measured=[...]); cal.run(); cal.apply_cal(raw)` | ideal or characterised standards |
| De-embed a fixture | `dut = fixture_left.inv ** meas ** fixture_right.inv` | fixture from EM sim or 2x-thru |
| TDR | `t, step = n.s11.step_response(window='hamming')`, `Z = 50*(1+step)/(1-step)` | needs a DC-extrapolated, uniformly spaced sweep |
| Netlist of networks | `from skrf.circuit import Circuit` | ports via `Circuit.Port`, ground via `Circuit.Ground` |
| Rational fit | `from skrf.vectorFitting import VectorFitting`; `vf.auto_fit()`; `vf.passivity_enforce()`; `vf.write_spice_subcircuit_s('x.sp')` | subcircuit name `s_equivalent` |

## Worked examples
All snippets were run with scikit-rf 2.0.1 / Python 3.13 on this machine.

### 1 — the 433 MHz L-match, as an S-parameter cascade
```python
import numpy as np, skrf as rf
f = rf.Frequency(300, 566, 267, unit='MHz')
m = rf.media.DefinedGammaZ0(frequency=f, z0_port=50)
load = rf.Network(frequency=f, s=np.full((f.npoints, 1, 1), (12.5 - 50) / (12.5 + 50)), z0=50)
net = m.shunt_capacitor(12.733e-12) ** m.inductor(7.958e-9) ** load
band = f.f[net.s_db[:, 0, 0] <= -10]          # 323 ... 520 MHz, same as ngspice
```
$|S_{11}(433\text{ MHz})| = 1.7\times10^{-5}$ (−95 dB); the RL ≥ 10 dB band matches ngspice's `.sp` analysis exactly ([SPICE page](spice-circuit-simulation.md#worked-examples)) — two independent network solvers agreeing.

### 2 — microstrip model and a line
```python
f2 = rf.Frequency(0.1, 3, 30, unit='GHz')
ms = rf.media.MLine(frequency=f2, w=2.8e-3, h=1.51e-3, t=0.0, ep_r=4.5, tand=0.0, rough=0.0,
                    disp='kirschningjansen', diel='frequencyinvariant')
ms.z0_characteristic[0]      # 50.44 ohm  (rfcalc.tline.microstrip_hj: 50.44; openEMS: 50.31; FD: 50.38)
ms.ep_reff_f[0]              # 3.391
line = ms.line(0.1, 'm', embed=True, z0=50)     # 100 mm of line in a 50-ohm system
```

### 3 — removing a fixture with a one-port SOL calibration
```python
from skrf.calibration import OnePort
f = rf.Frequency(100, 1000, 91, unit='MHz'); m = rf.media.DefinedGammaZ0(frequency=f, z0_port=50)
ideals = [m.short(), m.open(), m.match()]
fixture = m.shunt_capacitor(0.5e-12) ** m.line(30, 'deg')         # "unknown" test fixture
cal = OnePort(ideals=ideals, measured=[fixture ** s for s in ideals]); cal.run()
dut = m.load(0.3 + 0.2j)
np.max(abs(cal.apply_cal(fixture ** dut).s - dut.s))               # 7e-16
```
With real NanoVNA data the standards are imperfect (open capacitance, short inductance, load not exactly 50 Ω); give their models as `ideals` — see [VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md).

### 4 — TDR from S-parameters
A 50 Ω / 60 Ω (20 mm) / 50 Ω line, εeff 3.4, swept 1 MHz–6 GHz:
```python
t, step = dut.s11.step_response(window='hamming', pad=0)
z = 50 * (1 + step) / (1 - step)      # peak 59.3 ohm in the 60-ohm section
```
The 0.7 Ω under-read is the window's resolution limit (a 20 mm section at 6 GHz bandwidth); widen the sweep or use a Kaiser window with smaller β to sharpen it ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).

### 5 — Touchstone → SPICE (vector fitting), checked in ngspice
```python
from skrf.vectorFitting import VectorFitting
vf = VectorFitting(lpf)          # lpf: any rf.Network, e.g. rf.Network('saw_filter.s2p')
vf.auto_fit()                    # 5 poles, rms error 2e-15 for the ideal 5th-order LPF
vf.write_spice_subcircuit_s('lpf_vf.sp')      # .SUBCKT s_equivalent p1 p2
```
In ngspice (`.include lpf_vf.sp`, `X1 a b s_equivalent`, two `.sp` ports) the subcircuit gives −0.167 / −16.136 / −33.640 dB at 433.92 / 867.84 / 1301.76 MHz — identical to the Butterworth formula (`tools/verify/sim_ngspice_examples.py` example E). For measured files, fit over the full band you will simulate and **enforce passivity** (`vf.passivity_enforce()`) — the ideal LPF already fails `is_passive()` because a lossless network sits exactly on the boundary.

### 6 — rfcalc from Python
```python
import sys; sys.path.insert(0, 'tools')
from rfcalc import noise, link, lora, matching, tline
st = [noise.Stage('SAW', -1.5), noise.Stage('LNA', 18, 0.7, iip3=8), noise.Stage('coax', -2.6),
      noise.Stage('SX1262', 0, 6.0, iip3=-5)]
noise.cascade(st)[-1]['NF_cum_dB']                 # 2.55 dB  (receiver-cascade-analysis Example A2)
lora.time_on_air(32, 9, 125e3)                     # 0.2468 s
link.fspl_db(433.125e6, 30e3)                      # 114.72 dB
matching.l_match(32.1 - 18.5j, 50, 433e6)[0].components()   # 15.61 nH series, 5.49 pF shunt
tline.microstrip_width(50, 1.51e-3, 4.5, 35e-6)   # 2.797e-3 m
```

## Practical notes
- **Frequency grids**: cascading needs identical grids — `n.interpolate(new_freq)` (complex interpolation; fine for smooth data, dangerous across sharp resonances with coarse data).
- **NanoVNA exports** are .s1p (S11) or .s2p with only S11/S21 filled — treat the missing S12/S22 as unknown, not zero, when de-embedding.
- **Touchstone details**: check the option line (`# MHz S MA R 50`); version-2 files and non-50 Ω references are supported by skrf.
- **Noise parameters**: skrf reads noise data in .s2p files (`n.nfmin`, `n.g_opt`, `n.rn`) and can compute NF for a source impedance — useful for LNA design with vendor files ([LNA design](../06-rf-circuits/_index.md)).
- **Plotting**: `rf.stylely()` for publication-ish plots; Smith charts with `plot_s_smith(draw_labels=True)`.
- **Two environments on this Mac**: anaconda (`python3`, skrf 2.0.1) and the openEMS venv (`~/opt/openEMS/venv/bin/python`, skrf 2.1.0) — pin versions in results files.
- **SDR in Python** (not tested here): `pyrtlsdr` for RTL-SDR, `pyadi-iio` for ADALM-Pluto, SoapySDR bindings; GNU Radio for streaming flowgraphs — see [14-sdr-dsp](../14-sdr-dsp/_index.md).

## Common mistakes & misconceptions
- **`DefinedGammaZ0` without `gamma`** — its default propagation constant is 1j rad/m, so a "line of 30 mm" has almost no phase; pass `gamma=1j*2*np.pi*f/v`.
- **Using `MLine` defaults unknowingly** — Djordjevic–Svensson dielectric dispersion makes εr vary with frequency around its 1 GHz value; for comparisons with closed forms use `diel='frequencyinvariant'`.
- **Cascading files with different reference impedances** without renormalising (`n.renormalize(50)`).
- **TDR from a sweep that starts at a few MHz without DC extrapolation** — the step response drifts; use `n.extrapolate_to_dc()`.
- **Trusting a vector fit outside its fitted band** or using a non-passive fit in a transient simulation.
- **Assuming scikit-rf "simulates layout"** — it cascades models; discontinuities (pads, vias, launches) need EM data or measurement.

## How to simulate / verify
- Every snippet above has an independent twin: ngspice (`sim_ngspice_examples.py`), closed forms (`rfcalc` tests), the 2-D FD solver (`tline_fd2d.py`) or openEMS (`sim_openems_msl.py`).
- `cd tools && python3 -m pytest rfcalc/tests -q` — 142 tests (values from KB worked examples).
- Existing skrf-based verification scripts: `tools/verify/tline_matching.py`, `tline_sparams.py`, `tline_tdr.py`, `components_s2p_models.py`.

## Open questions / gaps
- `pymeep`, RadarSimPy, pyargus and scikit-commpy were not installed or tested; their descriptions are from PyPI/documentation.
- A NanoVNA SOL calibration with *characterised* (non-ideal) standards in skrf, compared against the NanoVNA's internal calibration, would be a useful measured example (domain 17).

## Sources
1. A. Arsenovic et al., "scikit-rf: An Open Source Python Package for Microwave Network Creation, Analysis, and Calibration," *IEEE Microwave Magazine*, 23(1):98–105, 2022. (peer-reviewed)
2. scikit-rf documentation (v2.x): Network, Media (MLine, CPW, Coaxial, DefinedGammaZ0), Calibration, Time Domain, Circuit, VectorFitting tutorials. https://scikit-rf.readthedocs.io/ (tool documentation)
3. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — sec. 4.3–4.4 (S- and ABCD matrices, cascading), sec. 4.5 (signal-flow graphs, TRL). (textbook)
4. Keysight (Agilent) Application Note 1287-3, "Applying Error Correction to Network Analyzer Measurements" — 3-term one-port model; D. Rytting, "Network analyzer error models and calibration methods," ARFTG short course. (app note / lecture notes)
5. RadarSimPy documentation, https://radarsimx.github.io/radarsimpy/ (installation: pre-built modules, free tier limits); PyPI pages for scikit-commpy 0.8.0, pyargus 1.1, pyadi-iio 0.0.21, pyrtlsdr 0.5.0 (checked 2026-09-27). (tool documentation)
6. B. Gustavsen and A. Semlyen, "Rational approximation of frequency domain responses by vector fitting," *IEEE Trans. Power Delivery*, 14(3):1052–1061, 1999. (peer-reviewed)
7. This repository: `tools/rfcalc/` (W3-C2), `tools/verify/sim_ngspice_examples.py` (example E), `tools/verify/tline_*.py` (W1-A4). (verification)
