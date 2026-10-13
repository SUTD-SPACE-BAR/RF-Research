#!/usr/bin/env python3
"""
s2_speech_crest.py — speech crest factor, SSB peak-to-average power ratio (PEP/average), and what
clipping / compression does to it (gap slice S2, W5-S2; G-10-04).

Used by: kb/10-comms-modulation/analog-modulation-am-fm-pm-ssb.md (SSB practice section).

Test signals
  1. Recorded *synthetic* speech from the macOS text-to-speech engine (`say`, 16 kHz, 16-bit), several
     voices. If `say` is unavailable the script skips this part. TTS speech is smoother than a live
     talker into a microphone, so treat its numbers as a lower bound on the natural crest factor.
  2. A source–filter speech model built here: glottal pulse train (f0 100–140 Hz with jitter) through
     four formant resonators, syllabic envelope ~4 Hz and pauses. Independent of (1).
  3. Single tone (PEP/avg = 1, 0 dB) and two tones (2, 3.01 dB) as sanity checks.

Method
  Audio band-limited to 300–2700 Hz (the SSB filter). For SSB the RF envelope is |m + j·m̂| (m̂ = Hilbert
  transform), so PEP/average = max|a|² / mean|a|². "Average" is reported two ways: over the whole
  recording (pauses included — what an average-reading wattmeter sees over a sentence) and over
  "talk" frames only (20 ms frames within 30 dB of the loudest frame).
  Processing: (a) envelope ("RF") clipping of the analytic signal to c dB below its peak, then
  re-filtering to 300–2700 Hz; (b) a fast feed-forward compressor (attack 1 ms, release 100 ms,
  ratio 10:1 above a threshold 20 dB below peak). Results are normalised to equal PEP, so the gain in
  average power is the "talk power" a processor buys for a PEP-limited transmitter.

Run:  python3 tools/verify/s2_speech_crest.py      (≈ 10 s)
"""
import os
import shutil
import subprocess
import tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import firwin, filtfilt, hilbert, lfilter

FS = 16000
FAILS = []
TEXT = ("The rocket cleared the rail at forty metres per second. Telemetry shows a clean boost, "
        "apogee at three thousand one hundred metres, and the drogue fired on time. "
        "Recovery team, head north east, about two kilometres, past the tree line.")


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name} {detail}")
    if not ok:
        FAILS.append(name)


def db(x):
    return 10 * np.log10(x)


BP = firwin(801, [300, 2700], pass_zero=False, fs=FS)


def bandlimit(x):
    return filtfilt(BP, [1.0], x)


def stats(x):
    """Return audio crest factor (dB), SSB PEP/avg over all samples and over talk frames (dB)."""
    a = hilbert(x)
    p = np.abs(a) ** 2
    cf = 20 * np.log10(np.max(np.abs(x)) / np.sqrt(np.mean(x ** 2)))
    pep_avg_all = db(np.max(p) / np.mean(p))
    fr = int(0.02 * FS)
    nfr = len(p) // fr
    e = p[:nfr * fr].reshape(nfr, fr).mean(axis=1)
    talk = e > np.max(e) * 10 ** (-30 / 10)
    pep_avg_talk = db(np.max(p) / np.mean(p[:nfr * fr].reshape(nfr, fr)[talk]))
    return cf, pep_avg_all, pep_avg_talk, talk.mean()


def env_clip(x, clip_db):
    a = hilbert(x)
    c = np.max(np.abs(a)) * 10 ** (-clip_db / 20)
    mag = np.abs(a)
    g = np.minimum(1.0, c / np.maximum(mag, 1e-12))
    return bandlimit(np.real(a * g))


def compress(x, thr_db=-20, ratio=10.0, att=1e-3, rel=0.1, lookahead=True):
    """Feed-forward compressor on the analytic envelope. With lookahead=True the detector sees the
    envelope `att` seconds early (a delay line in the signal path), so the gain is already down when a
    syllable onset arrives; without it, onsets pass at full gain and set the PEP."""
    a = np.abs(hilbert(x))
    d = int(att * FS)
    det = np.concatenate([a[d:], np.zeros(d)]) if lookahead else a
    det = np.maximum(det, a) if lookahead else det
    ka, kr = np.exp(-1 / (att * FS)), np.exp(-1 / (rel * FS))
    env = np.empty_like(a)
    e = 0.0
    for i, v in enumerate(det):
        k = 0.0 if (lookahead and v > e) else (ka if v > e else kr)
        e = k * e + (1 - k) * v
        env[i] = e
    thr = np.max(a) * 10 ** (thr_db / 20)
    over = np.maximum(env / thr, 1.0)
    gain = over ** (1 / ratio - 1)
    return bandlimit(x * gain)


def report(label, x):
    cf, all_, talk, frac = stats(x)
    print(f"   {label:34s} audio crest {cf:5.1f} dB | SSB PEP/avg: whole {all_:5.1f} dB ({10**(all_/10):5.1f}:1), "
          f"talk-only {talk:5.1f} dB ({10**(talk/10):4.1f}:1) | talk {100*frac:4.0f} %")
    return cf, all_, talk


def processing_table(x, label):
    print(f"   processing on {label} (normalised to equal PEP):")
    base = stats(x)
    out = {}
    for name, y in [("none", x), ("RF clip 6 dB", env_clip(x, 6)), ("RF clip 12 dB", env_clip(x, 12)),
                    ("RF clip 18 dB", env_clip(x, 18)), ("compressor 10:1, no look-ahead", compress(x, lookahead=False)),
                    ("compressor 10:1, look-ahead", compress(x))]:
        s = stats(y)
        gain = base[1] - s[1]   # equal PEP -> average power rises by the drop in PEP/avg
        out[name] = (s, gain)
        print(f"     {name:26s} PEP/avg whole {s[1]:5.1f} dB, talk {s[2]:5.1f} dB -> average (talk) power +{gain:4.1f} dB")
    return out


print("1. Sanity: tones")
t = np.arange(FS) / FS
one = np.cos(2 * np.pi * 1000 * t)
two = np.cos(2 * np.pi * 700 * t) + np.cos(2 * np.pi * 1900 * t)
s1, s2 = stats(one), stats(two)
check("single tone PEP/avg = 0 dB", abs(s1[1]) < 0.05, f"({s1[1]:.3f} dB)")
check("two-tone PEP/avg = 3.01 dB", abs(s2[1] - 3.01) < 0.05, f"({s2[1]:.3f} dB)")

print("\n2. macOS TTS speech (several voices)")
results = []
if shutil.which("say"):
    tmp = tempfile.mkdtemp()
    for voice in ["Daniel", "Samantha", "Karen", "Fred"]:
        f = os.path.join(tmp, f"{voice}.wav")
        r = subprocess.run(["say", "-v", voice, "-o", f, "--data-format=LEI16@16000", TEXT], capture_output=True)
        if r.returncode != 0 or not os.path.exists(f):
            continue
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fs, d = wavfile.read(f)
        x = bandlimit(d.astype(float) / 32768.0)
        results.append((voice, x, report(f"TTS {voice}", x)))
    shutil.rmtree(tmp, ignore_errors=True)
else:
    print("   `say` not found — TTS part skipped")

print("\n3. Source-filter speech model (independent)")
rng = np.random.default_rng(7)


def model_speech(dur=12.0):
    n = int(dur * FS)
    src = np.zeros(n)
    tpos = 0.0
    while tpos < dur:
        f0 = 120 + 20 * np.sin(2 * np.pi * 0.3 * tpos) + rng.normal(0, 3)
        idx = int(tpos * FS)
        if idx < n:
            src[idx] = 1.0
        tpos += 1.0 / f0
    # glottal shaping (two-pole low-pass) + formants
    x = lfilter([1.0], [1, -1.8, 0.81], src)
    y = np.zeros(n)
    for fmt, bwf, g in [(700, 90, 1.0), (1220, 110, 0.6), (2600, 160, 0.3), (3300, 200, 0.15)]:
        r = np.exp(-np.pi * bwf / FS)
        th = 2 * np.pi * fmt / FS
        y += g * lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x)
    # syllabic envelope with random syllable strengths and pauses
    tt = np.arange(n) / FS
    syl = np.clip(np.sin(2 * np.pi * 4.0 * tt + rng.uniform(0, 6.28)), 0, None) ** 1.5
    strength = np.repeat(rng.uniform(0.3, 1.0, int(dur * 4) + 2), FS // 4)[:n]
    pause = np.repeat(rng.uniform(0, 1, int(dur * 1.0) + 2) > 0.25, FS)[:n]
    noise = 0.02 * rng.normal(size=n) * syl          # fricative-like noise component
    return (y * syl * strength + noise) * pause


xm = bandlimit(model_speech())
model_stats = report("source-filter model", xm)

print("\n4. Speech processing (equal PEP)")
proc = processing_table(results[0][1] if results else xm, results[0][0] + " TTS" if results else "model")
proc_m = processing_table(xm, "model")

print("\n5. Consequences for a PEP-limited transmitter (100 W PEP)")
talks = [r[2][2] for r in results] + [model_stats[2]]
for name, (s, g) in proc.items():
    print(f"     {name:26s} average talk power ≈ {100/10**(s[2]/10):5.1f} W of 100 W PEP")

print("\n6. Checks against the literature")
alls = [r[2][1] for r in results] + [model_stats[1]]
check("unprocessed SSB speech PEP/avg (whole recording) ≥ 4 dB (exam's 2.5:1 = 4.0 dB is a lower bound)",
      min(alls) >= 4.0, f"(range {min(alls):.1f}–{max(alls):.1f} dB)")
check("unprocessed talk-only PEP/avg is 6–16 dB", all(6 <= v <= 16 for v in talks), f"(range {min(talks):.1f}–{max(talks):.1f} dB)")
check("12 dB RF clipping buys ≥ 4 dB average power", proc["RF clip 12 dB"][1] >= 4.0, f"(+{proc['RF clip 12 dB'][1]:.1f} dB)")
check("processing ordering: 6 < 12 < 18 dB clip gain", proc["RF clip 6 dB"][1] < proc["RF clip 12 dB"][1] < proc["RF clip 18 dB"][1])
check("compression without look-ahead buys little (< 3 dB)", proc["compressor 10:1, no look-ahead"][1] < 3.0,
      f"({proc['compressor 10:1, no look-ahead'][1]:+.1f} dB)")
check("look-ahead compression beats no look-ahead", proc["compressor 10:1, look-ahead"][1] > proc["compressor 10:1, no look-ahead"][1])

print("\nALL PASS" if not FAILS else f"\nFAILED: {FAILS}")
