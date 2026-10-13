#!/usr/bin/env python3
"""Tiny batch-mode ngspice helper for the W5-S3 scripts (tools/verify/s3_*.py).

run(netlist_body, analysis, exprs) writes the netlist with a .control block that runs `analysis`
and `wrdata`s every real-valued expression in `exprs` (e.g. "vdb(out)", "v(out)", "i(vcc)", "vp(out)"),
then returns (x, {expr: y}) as numpy arrays. Uses the Homebrew ngspice CLI (or $NGSPICE).
"""
import os
import subprocess
import tempfile
import numpy as np

NGSPICE = os.environ.get("NGSPICE", "/opt/homebrew/bin/ngspice")


def run(body, analysis, exprs, options=""):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.txt")
        cir = os.path.join(d, "c.cir")
        lets = []
        names = []
        for i, e in enumerate(exprs):
            lets.append(f"let s3v{i} = {e}")
            names.append(f"s3v{i}")
        txt = ("* s3 netlist\n" + body.strip() + "\n" + (options + "\n" if options else "") +
               ".control\nset wr_singlescale\nset wr_vecnames\n" + analysis + "\n" + "\n".join(lets) +
               f"\nwrdata {out} " + " ".join(names) + "\n.endc\n.end\n")
        open(cir, "w").write(txt)
        r = subprocess.run([NGSPICE, "-b", cir], capture_output=True, text=True, timeout=600)
        if not os.path.exists(out):
            raise RuntimeError("ngspice failed:\n" + r.stdout[-3000:] + r.stderr[-3000:])
        data = np.loadtxt(out, skiprows=1)
        if data.ndim == 1:
            data = data[None, :]
        x = data[:, 0]
        return x, {e: data[:, i + 1] for i, e in enumerate(exprs)}


def op(body, exprs):
    """DC operating point: returns {expr: value}."""
    x, d = run(body, "op", exprs)
    return {k: float(v[0]) for k, v in d.items()}


def first_cross(x, y, level, rising=None):
    """Linear-interpolated first crossing of y through level."""
    for i in range(1, len(y)):
        a, b = y[i - 1] - level, y[i] - level
        if a == 0:
            return x[i - 1]
        if a * b < 0 and (rising is None or (rising and b > 0) or (rising is False and b < 0)):
            return x[i - 1] + (x[i] - x[i - 1]) * (-a) / (b - a)
    return None
