#!/usr/bin/env python3
"""Shared helpers for the W5-E7 verification scripts (tools/verify/rf2_*.py).

check(name, cond)            -> prints PASS/FAIL and accumulates a global flag
finish()                     -> prints ALL PASS / SOME FAILED and sets the exit code
ngspice(netlist, vectors)    -> runs ngspice in batch mode, returns dict of numpy arrays
                                (first column = scale: frequency or time)
"""
import numpy as np, subprocess, tempfile, os, shutil, sys

_ok = [True]


def check(name, cond, detail=""):
    cond = bool(cond)
    _ok[0] &= cond
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
    return cond


def finish():
    print("ALL PASS" if _ok[0] else "SOME FAILED")
    sys.exit(0 if _ok[0] else 1)


def db10(x):
    return 10 * np.log10(np.abs(x))


def db20(x):
    return 20 * np.log10(np.abs(x))


def find_ngspice():
    for p in ("/opt/homebrew/bin/ngspice", "/usr/local/bin/ngspice", shutil.which("ngspice") or "",
              "/Applications/KiCad/KiCad.app/Contents/MacOS/ngspice"):
        if p and os.path.exists(p):
            return p
    return None


def ngspice(netlist_body, analysis, vectors, timeout=300):
    """Run ngspice -b. netlist_body: elements; analysis: e.g. '.ac dec 200 1e6 1e9' or '.tran ...'.
    vectors: list of expressions for wrdata (e.g. ['v(out)', 'i(vdd)']). Returns (scale, [arrays]).
    For AC analyses wrdata writes real and imaginary parts; complex arrays are returned."""
    exe = find_ngspice()
    if exe is None:
        raise RuntimeError("ngspice not found")
    d = tempfile.mkdtemp(prefix="rf2_")
    out = os.path.join(d, "out.txt")
    cir = os.path.join(d, "c.cir")
    is_ac = analysis.strip().lower().startswith(".ac")
    with open(cir, "w") as fh:
        fh.write("* rf2 auto netlist\n" + netlist_body + "\n" + analysis + "\n")
        fh.write(".control\nset wr_singlescale\nset wr_vecnames\nrun\n")
        fh.write("wrdata " + out + " " + " ".join(vectors) + "\n.endc\n.end\n")
    r = subprocess.run([exe, "-b", cir], capture_output=True, text=True, timeout=timeout)
    if not os.path.exists(out):
        raise RuntimeError("ngspice failed:\n" + r.stdout[-2000:] + r.stderr[-2000:])
    data = np.loadtxt(out, skiprows=1)
    shutil.rmtree(d, ignore_errors=True)
    scale = data[:, 0]
    cols = []
    if is_ac:
        for k in range(len(vectors)):
            cols.append(data[:, 1 + 2 * k] + 1j * data[:, 2 + 2 * k])
    else:
        for k in range(len(vectors)):
            cols.append(data[:, 1 + k])
    return scale, cols
