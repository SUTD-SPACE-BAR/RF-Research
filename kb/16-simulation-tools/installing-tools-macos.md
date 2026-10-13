---
title: Installing RF simulation tools on macOS (Apple Silicon) — tested commands, what worked, what failed
domain: 16-simulation-tools
slug: installing-tools-macos
tags: [macos, apple-silicon, homebrew, ngspice, kicad, libngspice, openems, csxcad, pynec, nec2, qucs-s, ltspice, xnec2c, wine, gatekeeper, notarization, scikit-rf, install]
prerequisites: [tool-landscape-overview.md]
related: [spice-circuit-simulation.md, openems-workflow.md, nec-antenna-modelling.md, python-rf-toolkit.md, rf-circuit-simulators-harmonic-balance.md, ../08-antennas/antenna-simulation-nec-openems.md]
level: intro
confidence: high
last_updated: 2026-10-02
---

# Installing RF simulation tools on macOS (Apple Silicon)

## Questions this page answers
- How do I install ngspice on a Mac, and do I even need to if KiCad is installed?
- Can I run openEMS on an M-series Mac? Is there a Homebrew formula or a pip/conda package?
- How do I get NEC-2 on macOS without Windows (PyNEC, xnec2c, 4nec2 under Wine)?
- Does LTspice run natively on macOS, and why does its Homebrew install ask for my password?
- Why did macOS warn me that Qucs-S "could not be verified", and is it safe to open?
- Which of these tools were actually installed and tested on this machine, and with what result?
- How do I check that an installed solver gives correct answers before I trust it?

## TL;DR
- **Tested on this machine** (macOS 26.6.2, Apple Silicon arm64, Homebrew 7.0.1, anaconda Python 3.13.9) on 2026-09-27:
  | Tool | How | Result |
  |---|---|---|
  | ngspice 47 CLI | `brew install ngspice` | **works**, batch mode needs no X11 |
  | ngspice 44.2 shared library | already inside KiCad 10 (`/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib`) | **works** via ctypes (`tools/verify/analog_ngspice.py`) — no install needed |
  | PyNEC 2.3.4 (NEC-2 in C++, Python) | `pip install PyNEC` (arm64 wheel on PyPI) | **works** |
  | openEMS v0.37.0-rc3 + CSXCAD + Python | build from the official source with `update_openEMS.sh` (~12 min, no sudo) | **works**; microstrip and patch cases run in 4–54 s |
  | scikit-rf, numpy, scipy, sympy, matplotlib, pytest | anaconda base | present |
  | Qucs-S 26.1.0 | cask from the maintainer's tap `ra3xdh/qucs-s` | installed, **not notarized → Gatekeeper blocks first launch**; not used by anything in this KB |
  | LTspice 26.0.2 | cask is a `.pkg` → needs an administrator password | **not installed** (documented only) |
  | xnec2c, Xyce | no Homebrew formula/cask | not installed |
  | Wine (for 4nec2, MMANA-GAL, Saturn PCB Toolkit) | `wine-stable` cask **disabled 2026-09-01** (fails Gatekeeper) | not installed |
- openEMS is **not** on PyPI or conda-forge, and its old Homebrew formula is marked broken in the official docs — build from source [1].
- Use `HOMEBREW_NO_INSTALL_CLEANUP=1` when installing: Homebrew's automatic `brew cleanup` otherwise deletes old cached bottles/casks of *other* packages.
- After any install, run a **smoke test with a known answer** (below) — an installed tool that silently gives wrong numbers is worse than none.

## Intuition (no math)
Most RF solvers were written for Linux or Windows. On a Mac they arrive by one of four routes, in decreasing order of convenience and trust:
1. **A package manager with signed/verified binaries** (Homebrew core formulae, PyPI wheels). Fast, reversible, versioned.
2. **Something already bundled in an app you trust** (KiCad ships ngspice as a library).
3. **Building from the project's own source** (openEMS). Slower, but you see every step and nothing needs administrator rights if you install into your home folder.
4. **A vendor installer or a third-party tap/app** (LTspice `.pkg`, Qucs-S cask, Wine). These may need your password or may not be notarized by Apple; macOS Gatekeeper will then stop the first launch. That is a decision for the machine's owner, not for a script.

Apple Silicon adds one more wrinkle: x86-only binaries run under Rosetta 2 (present on this machine), but Windows-only tools need Wine, whose Homebrew cask was disabled in September 2026 — so the practical Mac toolbox is ngspice + openEMS + PyNEC + Python (scikit-rf), with Windows tools (4nec2, Sonnet Lite, AWR, HFSS student) on a separate PC or VM.

## The math
Installing is not mathematics, but *checking* an install is. Each solver should reproduce a result whose value is known independently of any solver:

| Solver | Invariant / closed form used as the smoke test | Expected |
|---|---|---|
| SPICE (AC) | first-order RC low-pass, $f_{3\,dB} = 1/(2\pi RC)$ | 1 kΩ, 159.155 nF → 1000.0 Hz |
| SPICE (.sp) | ideal L-match, $Q=\sqrt{R_h/R_l-1}$, $X_s = QR_l$, $X_p = R_h/Q$ | 12.5→50 Ω at 433 MHz: 7.96 nH, 12.73 pF, $|S_{11}|\approx0$ |
| NEC-2 | energy conservation of a lossless wire: average gain = 1 (free space), 2 (over perfect ground) | 1.000 |
| NEC-2 | thin half-wave dipole resonance | ≈ 0.483λ, ≈ 72 Ω |
| openEMS | quasi-TEM microstrip Z0 vs a 2-D field solver / Hammerstad–Jensen | within ~1 % |

These are the same checks used throughout [simulation validation](simulation-validation.md). A "hello world" that merely runs without error is not a check.

## Design equations & rules of thumb (the command reference)

| Goal | Command (tested unless marked) |
|---|---|
| ngspice CLI | `HOMEBREW_NO_INSTALL_CLEANUP=1 brew install ngspice` → `ngspice -b circuit.cir` |
| ngspice plots in a window (optional) | `brew install --cask xquartz` (untested; batch mode + Python plotting needs no X11) |
| ngspice from Python, no install | `from analog_ngspice import run_netlist` (in `tools/verify/`; uses KiCad's libngspice, else `/opt/homebrew/lib/libngspice.dylib`) |
| NEC-2 from Python | `pip install PyNEC` → `import PyNEC` |
| openEMS deps | `HOMEBREW_NO_INSTALL_CLEANUP=1 brew install cmake boost hdf5 cgal vtk qt5compat` |
| openEMS source | `git clone --recursive https://github.com/thliebig/openEMS-Project.git ~/opt/src/openEMS-Project` |
| openEMS build | `cd ~/opt/src/openEMS-Project && ./update_openEMS.sh ~/opt/openEMS --python` |
| openEMS Python | `source ~/opt/openEMS/venv/bin/activate` (or call `~/opt/openEMS/venv/bin/python` directly); add `pip install scipy scikit-rf` |
| openEMS on PATH | `export PATH="$HOME/opt/openEMS/bin:$PATH"` in `~/.zshrc` |
| KB calculators | `cd tools && python3 -m rfcalc --help` ([tools/README.md](../../tools/README.md)) |
| LTspice (not run here) | `brew install --cask ltspice` — the cask is a `.pkg`, macOS asks for an administrator password; or download from analog.com |
| Qucs-S (installed, not used) | `brew tap ra3xdh/qucs-s && brew install --cask ra3xdh/qucs-s/qucs-s` — see the Gatekeeper note below |
| Remove Qucs-S | `brew uninstall --cask qucs-s && brew untap ra3xdh/qucs-s` |

## Worked examples

### 1 — ngspice: install and first run (tested)
```bash
HOMEBREW_NO_INSTALL_CLEANUP=1 brew install ngspice     # ngspice-47, KLU solver, ~15 s from a bottle
cat > rc.cir <<'EOF'
RC lowpass test
V1 in 0 AC 1
R1 in out 1k
C1 out 0 159.155n
.control
ac dec 10 10 100k
meas ac f3db WHEN vdb(out)=-3.0103
print f3db
quit
.endc
.end
EOF
ngspice -b rc.cir          # -> f3db = 9.999996e+02  (expected 1000.0 Hz)
```
The first attempt's side effect: without `HOMEBREW_NO_INSTALL_CLEANUP=1`, Homebrew ran `brew cleanup` and deleted old versions/caches of unrelated packages (harmless here, but surprising).

### 2 — the KiCad route (no install at all)
KiCad 10 bundles **ngspice 44.2** as a shared library. `tools/verify/analog_ngspice.py` (written by W2-B1) loads it with ctypes and returns vectors as numpy arrays; `tools/verify/sim_ngspice_examples.py` shows the same `.sp` S-parameter result from both the CLI (ngspice 47) and the KiCad library (ngspice 44.2): $|S_{11}|$ = 0.1093 / 1.3×10⁻⁷ / 0.1178 at 400 / 433 / 466 MHz for the L-match above. So if KiCad is installed, SPICE is already available to Python scripts.

### 3 — PyNEC (tested)
```bash
pip install PyNEC        # PyNEC 2.3.4, wheel pynec-2.3.4-cp313-cp313-macosx_11_0_arm64.whl
```
```python
import PyNEC
c = PyNEC.nec_context(); g = c.get_geometry()
g.wire(1, 41, 0, 0, -0.164, 0, 0, 0.164, 0.001, 1.0, 1.0)   # 328 mm, 2 mm diameter, 41 segments
c.geometry_complete(0)
c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)                            # free space
c.ex_card(0, 1, 21, 0, 1.0, 0, 0, 0, 0, 0)                    # voltage source on the centre segment
c.fr_card(0, 1, 433.0, 0)
c.rp_card(0, 91, 1, 0, 5, 0, 0, 0, 0, 2, 0, 0, 0)
print(c.get_input_parameters(0).get_impedance())              # [73.06+3.83j]
```
The module name is `PyNEC` (the separate `necpp` PyPI package is the plain C wrapper). Details and traps: [NEC modelling](nec-antenna-modelling.md).

### 4 — openEMS from source (tested, ~25 min total)
1. Dependencies (≈ 10 min from bottles; pulls Qt 6 base libraries and Homebrew's python@3.14 as VTK dependencies):
   `HOMEBREW_NO_INSTALL_CLEANUP=1 brew install cmake boost hdf5 cgal vtk qt5compat`
   (installed: boost 1.92.0, hdf5 2.2.0, cgal 6.2.1, vtk 9.7.0, qt5compat 6.11.2; cmake was already present).
2. `git clone --recursive https://github.com/thliebig/openEMS-Project.git ~/opt/src/openEMS-Project` (master 9f5cdd4, 2026-09-25; openEMS v0.37.0-rc3-16, CSXCAD v0.7.0-rc3-1).
3. `./update_openEMS.sh ~/opt/openEMS --python --python-venv-mode site` → "build successful" after ≈ 12 min on 10 cores. The script's dependency check warned that Homebrew's `python-setuptools cython numpy python-matplotlib` were "missing", but the build creates its own venv and installs them with pip, so the warning is harmless. It also downloads and builds TinyXML automatically (Homebrew dropped TinyXML). Note: `--python-venv-mode site` did **not** give access to anaconda's packages (the venv has `include-system-site-packages = false`), so add `~/opt/openEMS/venv/bin/pip install scipy scikit-rf`.
4. Smoke test: `~/opt/openEMS/bin/openEMS --help` prints `openEMS 64bit -- version v0.37.0-rc3-16-g5b1ecb1` and its libraries (CSXCAD, hdf5, tinyxml, fparser, boost, vtk); `~/opt/openEMS/venv/bin/python -c "import CSXCAD, openEMS"` succeeds.
5. Physics test: `~/opt/openEMS/venv/bin/python tools/verify/sim_openems_msl.py` → Z0 = 50.31 Ω for a line that the Hammerstad–Jensen formula puts at 50.44 Ω and this repository's 2-D field solver at 50.38 Ω (13 s). Full workflow: [openEMS workflow](openems-workflow.md).

### 5 — Qucs-S and Gatekeeper (what happened here)
Qucs-S's project page documents a Homebrew route through the maintainer's own tap. It was installed on 2026-09-27 with `brew tap ra3xdh/qucs-s` and `brew install --cask ra3xdh/qucs-s/qucs-s` (cask version 26.1.0, which downloads `Qucs-S-26.1.0-macOS.dmg` from the project's GitHub releases and depends on the `ngspice` formula). **Homebrew cask available; unsigned and not notarized, so Gatekeeper blocks first launch; the user decides whether to allow it via System Settings → Privacy & Security → Open Anyway.** Running a binary inside the app bundle from a script triggered the macOS "could not verify … is free of malware" dialog on this machine. Nothing in this knowledge base depends on Qucs-S; every circuit example is reproduced with ngspice, scikit-rf or rfcalc. If you do not want it: `brew uninstall --cask qucs-s && brew untap ra3xdh/qucs-s`.

## Practical notes
- **Where things live**: Homebrew in `/opt/homebrew`; openEMS in `~/opt/openEMS` (binaries `bin/openEMS`, `bin/nf2ff`, `bin/AppCSXCAD`, `bin/sar_calc`; Python venv `venv/`); source and build logs in `~/opt/src/openEMS-Project` (`build_YYYYMMDD_HHMMSS.log`).
- **Two Pythons**: anaconda's `python3` (numpy, scipy, scikit-rf 2.0.1, PyNEC, rfcalc tests) and the openEMS venv (scikit-rf 2.1.0 added). Run openEMS scripts with `~/opt/openEMS/venv/bin/python`. Mixing them (e.g. `pip install` into the wrong one) is the commonest "module not found".
- **Rosetta 2** is present, so x86_64-only macOS binaries (e.g. an Intel `.dmg`) will run, more slowly.
- **Windows-only tools** (4nec2, EZNEC, MMANA-GAL, Saturn PCB Toolkit, AppCAD, Sonnet Lite, AWR Microwave Office, HFSS/CST student editions): with the Wine cask disabled, the reliable options are a Windows PC, a Windows-on-ARM virtual machine (UTM/Parallels; not tested here), or a university lab machine. AWR's free 6-month academic licence explicitly does not support Macs [5].
- **Nothing here needs sudo**, except the LTspice `.pkg`. Prefer installs into your home directory; they are easy to delete.
- **Record versions**: solver behaviour changes between versions (see the ngspice `.meas` crash below); write the version into every results file, as `tools/verify/sim_openems_results.txt` does.

### Disk space and clean removal (measured 2026-09-29)

| Item | Size | Remove with |
|---|---|---|
| ngspice (Cellar) | 6 MB | `brew uninstall ngspice` |
| openEMS install `~/opt/openEMS` (incl. venv) | 326 MB | `rm -r ~/opt/openEMS` |
| openEMS source + build tree `~/opt/src/openEMS-Project` | 105 MB | `rm -r ~/opt/src/openEMS-Project` |
| openEMS brew deps: boost 378 MB, vtk 300 MB, qtbase 69 MB, cgal 50 MB, hdf5 23 MB | ≈ 0.8 GB | `brew uninstall vtk cgal boost hdf5 qt5compat` then `brew autoremove` |
| Qucs-S.app | 427 MB | `brew uninstall --cask qucs-s && brew untap ra3xdh/qucs-s` |
| PyNEC | < 1 MB | `pip uninstall PyNEC` |

### Which route for which tool (decision table)

| Tool | Best route on Apple Silicon | Fallback | Avoid |
|---|---|---|---|
| SPICE | brew ngspice, or KiCad's libngspice | LTspice (native macOS app, admin password) | old PSpice/Windows-only demo versions |
| NEC-2 | PyNEC (pip) | build xnec2c; EZNEC/4nec2 on a Windows PC | copying random `.exe` builds |
| FDTD | openEMS from source | MEEP (conda-forge `pymeep`, not tested here) | unmaintained third-party taps |
| Planar MoM | Sonnet Lite on Windows | openEMS with a fine mesh | — |
| Harmonic balance | Qucs-S/QucsatorRF (unsigned; owner decides), Keysight ADS / AWR on Windows with academic licences | Xyce from source | treating SPICE transient as HB |
| Line/matching calculators | `tools/rfcalc`, KiCad PCB Calculator | JLCPCB web calculator | calculators that hide their model |

## Common mistakes & misconceptions
- **"There is a Homebrew formula for openEMS."** The official docs say the old formula is broken and unmaintained; a third-party tap exists, but the supported route is the source build [1].
- **"`pip install openEMS` will work."** Not on macOS: there is no PyPI or conda-forge package (checked 2026-09-27); the Python modules are built against your local C++ build.
- **"If it installed, it works."** The openEMS build's own dependency check printed a scary "did not pass" warning and still produced a correct solver; conversely, brew's ngspice-47 **segfaults** on `meas sp … WHEN …` in `.sp` analyses (tested) — only a known-answer test tells you which.
- **"The Gatekeeper warning means malware."** It means Apple has not notarized the app; it says nothing either way about the code. Whether to allow it is the owner's decision — and a script should never bypass it (no `xattr`/`spctl` tricks).
- **"I need Windows for NEC."** PyNEC gives the NEC-2 engine on macOS directly; only the GUIs (4nec2, EZNEC) are Windows-only.
- **Installing into the anaconda base and the openEMS venv interchangeably** — then wondering why `import openEMS` fails in one and `import skrf` in the other.

## How to simulate / verify
- `python3 tools/verify/sim_ngspice_examples.py` — ngspice CLI and KiCad libngspice on four netlists with closed-form answers (≈ 1 s).
- `python3 tools/verify/sim_nec_vs_mom.py` — PyNEC vs this repository's own MoM (≈ 15 s).
- `~/opt/openEMS/venv/bin/python tools/verify/sim_openems_msl.py` and `sim_openems_patch.py` — openEMS microstrip (≈ 20 s) and patch antenna (≈ 90 s, three meshes).
- `cd tools && python3 -m pytest rfcalc/tests -q` — 142 calculator tests (≈ 0.1 s).

## Open questions / gaps
- The SDR software stack (GNU Radio — e.g. via the radioconda conda distribution or Homebrew — SoapySDR drivers, SDR++, gr-lora_sdr) was **not** installed or tested on this machine; the landscape and choices are in [14 GNU Radio & software stack](../14-sdr-dsp/gnu-radio-and-software-stack.md). Record versions here once tested.
- xnec2c (GTK GUI for NEC-2) could be built from source with Homebrew's gtk+3 (MacPorts also packages it); not attempted.
- A Windows-on-ARM VM route for 4nec2/Sonnet Lite/AWR was not tested.
- Xyce (Sandia; harmonic balance) has no Homebrew formula; building it from source was not attempted.
- LTspice's macOS command-line batch mode was not tested (the `.pkg` needs an administrator password).

## Sources
1. openEMS project documentation source, `doc-src/install/package.rst`, `requirements.rst`, `clone-build-install.rst`, `check.rst`, github.com/thliebig/openEMS-Project (master, 2026-09-25) — macOS deps, broken Homebrew formula, `update_openEMS.sh` options, TinyXML handling. https://docs.openems.de (tool documentation)
2. ngspice User's Manual (version 41+), ch. 15 (analyses incl. `.sp`), ch. 17 (control language: `meas`, `wrdata`); https://ngspice.sourceforge.io/docs.html ; Homebrew formula `ngspice` 47. (tool documentation)
3. T. Molteno, python-necpp / PyNEC, https://github.com/tmolteno/python-necpp ; PyPI `PyNEC` 2.3.4 (arm64 wheels). (tool documentation)
4. Qucs-S project page https://ra3xdh.github.io/ (engines, Homebrew tap instructions) and cask `ra3xdh/homebrew-qucs-s/Casks/qucs-s.rb` (version 26.1.0, GitHub-release dmg, depends on ngspice). (tool documentation)
5. Cadence, "AWR University Program FAQ" (PDF): 6-month free academic Microwave Office licence on a personal Windows PC; Macs not supported. https://awr.cadence.com/support/AWR_University_FAQ.pdf (vendor document)
6. Homebrew casks `ltspice` (26.0.2, pkg artifact) and `wine-stable` (disabled 2026-09-01, Gatekeeper), checked with `brew info` on 2026-09-27. (package metadata)
7. This repository: `tools/verify/analog_ngspice.py` (KiCad libngspice runner, W2-B1), `tools/verify/sim_*.py`, research log `research-logs/W3-C2-simulation-tools.md` (full install record). (verification)
