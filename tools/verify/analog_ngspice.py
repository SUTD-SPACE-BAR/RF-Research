#!/usr/bin/env python3
"""Minimal runner for the ngspice shared library bundled with KiCad (macOS).

Used by the 05-analog-electronics verification scripts to run the SPICE netlists printed on the
pages. No separate ngspice install is needed: KiCad ships libngspice in its app bundle.

Usage as a library:
    from analog_ngspice import run_netlist
    vecs = run_netlist(netlist_text, ["v(out)", "time"])   # returns dict name -> numpy array
Usage from the shell:
    python3 tools/verify/analog_ngspice.py file.cir v(out) time
"""
import ctypes
import os
import sys
import numpy as np

_CANDIDATES = [
    os.environ.get("NGSPICE_LIB", ""),
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib",
    "/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.0.dylib",
    "/opt/homebrew/lib/libngspice.dylib",
    "/usr/local/lib/libngspice.dylib",
    "libngspice.so.0",
]

_lib = None
_log = []

SendChar = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
SendStat = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
ControlledExit = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
SendData = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)
SendInitData = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p)
BGThreadRunning = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)


class VectorInfo(ctypes.Structure):
    _fields_ = [("v_name", ctypes.c_char_p), ("v_type", ctypes.c_int), ("v_flags", ctypes.c_short),
                ("v_realdata", ctypes.POINTER(ctypes.c_double)), ("v_compdata", ctypes.c_void_p),
                ("v_length", ctypes.c_int)]


@SendChar
def _send_char(msg, ident, user):
    _log.append(msg.decode(errors="replace"))
    return 0


@SendStat
def _send_stat(msg, ident, user):
    return 0


@ControlledExit
def _exit(status, unload, quit_, ident, user):
    return 0


def _load():
    global _lib
    if _lib is not None:
        return _lib
    for c in _CANDIDATES:
        if not c:
            continue
        try:
            _lib = ctypes.CDLL(c)
            break
        except OSError:
            continue
    if _lib is None:
        raise RuntimeError("libngspice not found; install KiCad or set NGSPICE_LIB")
    _lib.ngSpice_Init(_send_char, _send_stat, _exit, None, None, None, None)
    _lib.ngGet_Vec_Info.restype = ctypes.POINTER(VectorInfo)
    _lib.ngSpice_Command.argtypes = [ctypes.c_char_p]
    return _lib


def run_netlist(text, vectors, complex_ok=True):
    """Run a netlist (string). Returns dict of requested vectors (real or complex numpy arrays)."""
    lib = _load()
    _log.clear()
    lines = [l for l in text.strip().splitlines()]
    arr = (ctypes.c_char_p * (len(lines) + 1))()
    for i, l in enumerate(lines):
        arr[i] = l.encode()
    arr[len(lines)] = None
    lib.ngSpice_Circ(arr)
    lib.ngSpice_Command(b"run")
    out = {}
    for v in vectors:
        p = lib.ngGet_Vec_Info(v.encode())
        if not p:
            raise KeyError(f"vector {v} not found; log tail:\n" + "".join(_log[-20:]))
        info = p.contents
        n = info.v_length
        if info.v_realdata:
            out[v] = np.ctypeslib.as_array(info.v_realdata, shape=(n,)).copy()
        else:
            raw = ctypes.cast(info.v_compdata, ctypes.POINTER(ctypes.c_double))
            a = np.ctypeslib.as_array(raw, shape=(2 * n,)).copy()
            out[v] = a[0::2] + 1j * a[1::2]
    lib.ngSpice_Command(b"destroy all")
    lib.ngSpice_Command(b"remcirc")
    return out


def log_tail(n=30):
    return "".join(_log[-n:])


USAGE = """usage: python3 tools/verify/analog_ngspice.py NETLIST.cir VECTOR [VECTOR ...]
  e.g. python3 tools/verify/analog_ngspice.py rc.cir "v(out)" time
Runs NETLIST.cir in the bundled libngspice and prints the first/last 5 points of each VECTOR.
This file is a helper library for the 05-analog verification scripts, not a check of its own:
run with no arguments it only prints this message (exit 0)."""

if __name__ == "__main__":
    # W6-F5 (2026-10-14, D7 section 4): print usage instead of an IndexError when run without arguments.
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)
    if len(sys.argv) < 3:
        print(USAGE, file=sys.stderr)
        sys.exit(2)
    txt = open(sys.argv[1]).read()
    res = run_netlist(txt, sys.argv[2:])
    for k, v in res.items():
        print(k, v[:5], "...", v[-5:])
