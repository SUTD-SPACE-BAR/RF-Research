#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/gnu-radio-and-software-stack.md

Checks (PASS/FAIL) and measurements (machine-specific, printed):
 1. RTL-SDR cu8 -> complex64 conversion: (u8 - 127.5)/127.5, interleaved I,Q; the classic
    "subtract 128" mistake leaves a DC offset of 0.5 LSB on I and Q (~ -45 dBFS spike).
 2. SigMF: write a .sigmf-meta/.sigmf-data pair (ci16_le) with the required core fields
    (core:datatype, core:version) plus sample_rate, captures, annotations; read back and check.
 3. Host throughput on this machine: complex FIR (overlap-add), FFT, frequency-shift, polyphase
    resample -- expressed as MS/s, to compare with SDR sample rates.
"""
import json
import os
import tempfile
import time

import numpy as np
from scipy import signal

rng = np.random.default_rng(0)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# ------------------------------------------------------------ 1. cu8 conversion
N = 2 ** 20
iq = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) * 0.2
raw = np.empty(2 * N, dtype=np.uint8)
raw[0::2] = np.clip(np.round(iq.real * 127.5 + 127.5), 0, 255).astype(np.uint8)
raw[1::2] = np.clip(np.round(iq.imag * 127.5 + 127.5), 0, 255).astype(np.uint8)
good = (raw.astype(np.float32) - 127.5) / 127.5
x = good[0::2] + 1j * good[1::2]
bad = (raw.astype(np.float32) - 128.0) / 128.0
xb = bad[0::2] + 1j * bad[1::2]
dc_good = np.abs(np.mean(x))
dc_bad = np.abs(np.mean(xb))
check("cu8 conversion with 127.5 offset has no DC", dc_good < 1e-3, f"|mean| {dc_good:.1e}")
check("subtracting 128 leaves a DC spike ~ -45 dBFS", abs(20 * np.log10(dc_bad) - 20 * np.log10(np.sqrt(2) * 0.5 / 128)) < 0.5,
      f"{20*np.log10(dc_bad):.1f} dBFS")

# ------------------------------------------------------------ 2. SigMF round trip
tmp = tempfile.mkdtemp(prefix="sigmf_")
base = os.path.join(tmp, "lora_433_test")
fs = 1e6
sig16 = np.empty(2 * 4096, dtype="<i2")
z = (x[:4096] * 2 ** 14)
sig16[0::2] = np.round(z.real)
sig16[1::2] = np.round(z.imag)
sig16.tofile(base + ".sigmf-data")
meta = {
    "global": {
        "core:datatype": "ci16_le",
        "core:version": "1.2.0",
        "core:sample_rate": fs,
        "core:description": "test capture, 433 MHz ISM",
        "core:recorder": "dsp_host_stack.py",
    },
    "captures": [{"core:sample_start": 0, "core:frequency": 433.52e6, "core:datetime": "2026-09-29T00:00:00Z"}],
    "annotations": [{"core:sample_start": 100, "core:sample_count": 2048,
                     "core:freq_lower_edge": 433.8575e6, "core:freq_upper_edge": 433.9825e6, "core:label": "LoRa BW125"}],
}
with open(base + ".sigmf-meta", "w") as fh:
    json.dump(meta, fh, indent=2)
m2 = json.load(open(base + ".sigmf-meta"))
d2 = np.fromfile(base + ".sigmf-data", dtype="<i2")
x2 = (d2[0::2] + 1j * d2[1::2]) / 2 ** 14
import re
dt_ok = re.fullmatch(r"(c|r)(f32|f64|i32|i16|u32|u16|i8|u8)(_le|_be)?", m2["global"]["core:datatype"]) is not None
check("SigMF required globals present and datatype valid", dt_ok and "core:version" in m2["global"])
check("SigMF data round-trips (ci16_le interleaved I,Q)", np.max(np.abs(x2 - x[:4096])) < 1 / 2 ** 13)
print(f"      wrote and re-read a SigMF pair ({os.path.getsize(base + '.sigmf-data')} data bytes)")
import shutil
shutil.rmtree(tmp)


# ------------------------------------------------------------ 3. host throughput
def rate(fn, nsamp, reps=3):
    fn()  # warm up
    t0 = time.perf_counter()
    for _ in range(reps):
        fn()
    dt = (time.perf_counter() - t0) / reps
    return nsamp / dt / 1e6


Nb = 2 ** 21
xb = (rng.standard_normal(Nb) + 1j * rng.standard_normal(Nb)).astype(np.complex64)
h = signal.firwin(255, 0.1).astype(np.float32)
nco = np.exp(-2j * np.pi * 0.1 * np.arange(Nb)).astype(np.complex64)
r_fir = rate(lambda: signal.oaconvolve(xb, h, mode="same"), Nb)
r_fir_direct = rate(lambda: signal.lfilter(h, 1, xb[: Nb // 8]), Nb // 8)
r_fft = rate(lambda: np.fft.fft(xb.reshape(-1, 2048), axis=1), Nb)
r_mix = rate(lambda: xb * nco, Nb)
r_rs = rate(lambda: signal.resample_poly(xb, 5, 24), Nb)
print(f"      this machine: 255-tap complex FIR (overlap-add) {r_fir:7.1f} MS/s; same FIR via lfilter {r_fir_direct:6.1f} MS/s;")
print(f"                    2048-pt FFT frames {r_fft:7.1f} MS/s; NCO mix {r_mix:7.1f} MS/s; resample_poly 5/24 {r_rs:6.1f} MS/s (input)")
check("numpy/scipy chain keeps up with an RTL-SDR (2.4 MS/s) with large margin", min(r_fir, r_fft, r_mix, r_rs) > 10 * 2.4)

print("\nALL PASS" if ok_all else "\nSOME FAIL")
