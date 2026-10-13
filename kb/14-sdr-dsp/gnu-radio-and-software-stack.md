---
title: GNU Radio and the SDR software stack — drivers (UHD, libiio, SoapySDR), applications, libraries, SigMF recording and host performance
domain: 14-sdr-dsp
slug: gnu-radio-and-software-stack
tags: [gnu-radio, grc, flowgraph, blocks, stream-tags, message-passing, pmt, oot, gr_modtool, volk, gnuradio4, uhd, libiio, soapysdr, gr-osmosdr, sdr++, sdrsharp, gqrx, sdrangel, inspectrum, urh, liquid-dsp, pysdr, pyadi-iio, pyrtlsdr, gr-lora_sdr, sigmf, overflow, throughput]
prerequisites: [iq-complex-baseband.md, multirate-dsp-decimation-cic.md, software-demodulation.md]
related: [sdr-hardware-survey.md, fpga-for-sdr.md, fft-spectral-analysis-windows.md, digital-filters-fir-iir.md, nco-ddc-duc.md, ../15-lora-ism-radios/ground-station-design.md, ../16-simulation-tools/python-rf-toolkit.md, ../16-simulation-tools/installing-tools-macos.md, ../17-test-measurement/sdr-as-test-equipment.md]
level: mixed
confidence: medium
last_updated: 2026-09-29
---

# GNU Radio and the SDR software stack

## Questions this page answers
- What is GNU Radio, how does a flowgraph work, and what are blocks, stream tags and messages?
- GNU Radio 3.10 or 4.0 — which should I use in 2026?
- What is the difference between UHD, libiio, SoapySDR and gr-osmosdr, and which one does my SDR need?
- Which application should I use to just *look* at the spectrum (SDR++, SDR#, GQRX, SDRangel…)?
- How do I decode LoRa with an SDR (gr-lora_sdr)?
- How should I record IQ so I (and my tools) can read it later — what is SigMF?
- What do "O" and "U" mean in my terminal, and why am I dropping samples?
- Is Python fast enough, or do I need C++ / GNU Radio / an FPGA?
- Where do I start if I've never written SDR code?

## TL;DR
- **Layers**: hardware → *driver/API* (UHD for Ettus USRPs; libiio for ADI devices such as Pluto; librtlsdr, libhackrf, libairspy, SDRplay API, bladeRF, LimeSuite; **SoapySDR** as a vendor-neutral wrapper over all of them) → *framework or library* (GNU Radio, liquid-dsp, numpy/scipy, pyadi-iio) → *application* (SDR++, SDR#, GQRX, SDRangel, direwolf, rtl_433, gr-lora_sdr flowgraphs).
- **GNU Radio**: the latest stable is **3.10.12.0 (2025-02-20)**; **GNU Radio 4.0** is at release-candidate stage (**RC3, 2026-09-22**, pre-release: "core intended to be stable", with breaking API changes vs 3.10) [1], [2]. For projects in 2026, use 3.10 (all OOT modules, gr-lora_sdr, tutorials); watch 4.0.
- **Flowgraph model**: blocks connected by typed sample streams (buffers), scheduled by the runtime; *sync* (1:1), *decimator*, *interpolator* and *general* blocks; **stream tags** carry metadata attached to a sample index (e.g. `rx_time`, `rx_freq`, packet length); **message ports** carry asynchronous PMT messages (PDUs, control) [3].
- **Throughput reality**: a Python/numpy chain on an Apple M1 Max runs a 255-tap complex FIR at ~117 MS/s (overlap-add) but only ~7 MS/s with a naive `lfilter`; FFT frames ~171 MS/s; polyphase 5/24 resampling ~64 MS/s (script, machine-specific). An RTL-SDR (2.4 MS/s) is easy; a 61.44 MS/s AD9361 stream needs C++/VOLK, careful buffering — or FPGA processing ([FPGA](fpga-for-sdr.md)).
- **Dropped samples**: UHD prints **O** (overflow: host too slow to consume RX samples; "D" on network devices for dropped packets) and **U** (underflow: host too slow to supply TX samples) [4]. Fixes: decimate early, reduce rate, avoid GUI sinks at full rate, write to fast disks, bigger buffers.
- **Record in SigMF** (spec 1.2.x): a `.sigmf-data` binary file of interleaved I/Q plus a `.sigmf-meta` JSON with required `core:datatype` (e.g. `ci16_le`, `cf32_le`, `cu8`) and `core:version`, plus sample rate, centre frequency, start time and annotations [5] (round-trip verified in the script).
- **RTL-SDR raw samples are unsigned 8-bit offset binary**: convert with $(u-127.5)/127.5$; subtracting 128 leaves a ≈ −45 dBFS DC spike that looks like a hardware artefact (script).

Verified by `tools/verify/dsp_host_stack.py` (all PASS; throughput numbers are for the machine it ran on).

## Intuition (no math)
Think of GNU Radio as plumbing for sample streams. Each block is a machine that takes samples in, does one job (filter, mix, demodulate, display), and pushes samples out. You connect machines with pipes (buffers); the scheduler keeps every machine busy as long as its input pipe has data and its output pipe has room. The SDR source at the start sets the pace: it produces samples at the hardware rate whether or not the rest of the plant keeps up. If a later machine is too slow, pipes fill up, the source has nowhere to put new samples, and the driver has to throw some away — that's an overflow, and it silently corrupts anything timing-sensitive (a LoRa packet, a radar sweep).

Drivers are the translators between the SDR's USB/Ethernet protocol and your program. Because every vendor speaks a different dialect, SoapySDR (and gr-osmosdr before it) offers a common phrasebook so the same program can talk to an RTL-SDR, a HackRF or a Pluto.

## The math

### Level 1 — the stack, layer by layer
| Layer | Examples | What it does |
|---|---|---|
| Hardware | RTL-SDR, HackRF, Pluto, USRP, LimeSDR, bladeRF | RF + ADC/DAC + USB/Ethernet |
| Vendor driver / API | librtlsdr (RTL-SDR Blog fork for V4/V4L), libhackrf, libairspy, SDRplay API, libbladeRF, LimeSuite(NG), **UHD** (Ettus), **libiio** (ADI) | tune, set gain/rate, stream sample buffers |
| Abstraction | **SoapySDR** (+ per-device modules), gr-osmosdr, gr-soapy, gr-uhd, gr-iio | one API for many devices |
| DSP framework / library | **GNU Radio**, liquid-dsp, numpy/scipy, VOLK | filters, NCOs, demodulators, sync |
| Applications | SDR++, SDR#, GQRX, SDRangel, SDR Console, CubicSDR; rtl_433, direwolf, gr-lora_sdr; inspectrum, URH | receive, decode, analyse |
| Files | SigMF; raw `.cu8/.cs16/.cf32`; WAV-IQ | recording, sharing, replay |

**Sample formats and sizes** (bytes per complex sample): `cu8`/`ci8` 2 (RTL-SDR, HackRF), `ci16` 4 (Pluto, USRP `sc16` on the wire), `cf32` 8 (GNU Radio's `gr_complex`, numpy `complex64`). Data rate = $f_s\times$ bytes: 2.4 MS/s cu8 = 4.8 MB/s; 20 MS/s ci8 = 40 MB/s (the practical USB 2 ceiling); 61.44 MS/s ci16 = 246 MB/s ([hardware survey](sdr-hardware-survey.md)).

### Level 2 — how GNU Radio works
**Blocks and scheduling (3.x)** [3], [6]:
- A **general block** implements `general_work()` and `forecast()` (how many input items it needs to produce N outputs) and calls `consume()` explicitly — for variable-rate blocks such as packet decoders.
- A **sync block** implements `work()` with one output item per input item; `sync_decimator`/`sync_interpolator` handle fixed ratios; the scheduler handles consumption.
- **Hier blocks** wrap sub-flowgraphs (GRC saves them as a Python file plus `.block.yml`); the **Embedded Python Block** lets you write a block inline in GRC without building a module.
- **Buffers**: by default each connection is a circular buffer (≈ 32 KiB × 2 per the runtime source, configurable via `buffer_size` in the preferences); `set_max_noutput_items()` and `set_output_multiple()` tune chunking — relevant for latency and for blocks that need whole FFT frames.
- The 3.x scheduler runs each block in its own thread ("thread-per-block"); throughput scales across cores but latency accumulates in buffers.

**Stream tags** attach key/value metadata (PMTs) to an absolute sample offset: the UHD source emits `rx_time`, `rx_rate`, `rx_freq` tags after tuning or overflow; packet blocks emit `packet_len`; tags propagate through blocks according to a policy (don't propagate / all-to-all / one-to-one) with offsets rescaled by rate changes [3].

**Message passing** is asynchronous: blocks exchange PMT messages (dictionaries, PDUs = metadata + vector) through named message ports — the natural representation for packets once bits are framed, and for control (retune on a message, e.g. frequency hopping).

**Out-of-tree (OOT) modules**: `gr_modtool newmod <name>` then `gr_modtool add` generates C++/Python block skeletons, YAML block definitions for GRC and CMake glue; this is how gr-lora_sdr, gr-osmosdr and gr-satellites are packaged. **GRC** files (`.grc`) and block definitions are YAML since 3.8.

**VOLK** (Vector-Optimized Library of Kernels) provides SIMD kernels (SSE/AVX/NEON; RISC-V experimental) with run-time dispatch; `volk_profile` picks the fastest per machine [7]. Most of GNU Radio's filter/mixer throughput comes from VOLK.

**Throttle**: only for flowgraphs with *no* hardware clock (e.g. file → GUI) — with an SDR or audio device the hardware sets the rate, and adding Throttle just causes problems [8].

**3.10 highlights**: gr-pdu, gr-iio (ADI devices) and gr-soapy in-tree; logging via spdlog; C++17; custom buffers for accelerators [9]. gr-uhd includes `uhd_fft`, `uhd_rx_cfile` and `uhd_siggen`. gr-osmosdr (Osmocom) remains out-of-tree and supports RTL-SDR, HackRF, bladeRF, Airspy, SDRplay, UHD and rtl_tcp through one source block [10].

**GNU Radio 4.0** (RC3, 2026-09-22) is a new modern-C++ runtime (reorganised into core/library/blocks/control-plane/studio), not a continuation of the 3.10 API; flowgraphs and OOT code will need porting [2].

### Level 3 — drivers, devices and performance engineering
**UHD** (Ettus/NI; v4.11.0.0 as of 2026-09): `uhd_find_devices`, `uhd_usrp_probe --args=...`; `set_clock_source("external")` (10 MHz) and `set_time_source("external")` (PPS) with `set_time_next_pps()` to align multiple devices; CPU formats `fc32/sc16/sc8`, wire formats `sc16/sc12/sc8` (sc8 halves bandwidth at the cost of dynamic range) [4]. RFNoC (UHD 4) runs DSP blocks inside the USRP's FPGA ([FPGA](fpga-for-sdr.md)).
**libiio** (ADI; **v1.0.0 released 2026-09-22**, which breaks the v0.x API/ABI but ships a compatibility layer) exposes IIO devices locally or over USB/Ethernet (Pluto's default URI `ip:192.168.2.1`); command-line `iio_info`, `iio_attr`, `iio_rwdev` [11]. **pyadi-iio** (`adi.Pluto()`) is the easiest Python route to a Pluto [12].
**SoapySDR** (latest tag 0.8.1): C/C++ API with run-time device modules (RTL, HackRF, bladeRF, Lime, Airspy, Pluto, UHD and more), bindings for Python and other languages; used by SDR++, CubicSDR, SDRangel and GNU Radio's gr-soapy [13].

**Why overflows happen and how to avoid them.** The source produces $f_s$ samples/s irrespective of downstream speed. If any block's sustained throughput is below the rate it sees, buffers fill and the driver drops data. Engineering rules:
1. *Decimate as early as possible* — the first block after the source should be a `Frequency Xlating FIR Filter` or a polyphase decimator so everything after runs at the channel rate ([multirate](multirate-dsp-decimation-cic.md)).
2. *Measure each block's cost*: script example — the same 255-tap complex FIR runs at ≈ 117 MS/s with FFT-based overlap-add but ≈ 7 MS/s with a direct-form `lfilter` in scipy on one core (M1 Max); GNU Radio's `FIR Filter`/`FFT Filter` with VOLK is in the same league as the fast figure.
3. *GUI sinks at full rate* (waterfalls at 60 fps of 61 MS/s) and *Python blocks in the high-rate path* are the usual culprits; Python blocks cost per call, so give them large chunks.
4. *Disk*: 61.44 MS/s ci16 = 246 MB/s sustained — an NVMe SSD, not a USB stick; 2 MS/s cu8 (4 MB/s) is fine anywhere.
5. *USB*: use USB 3 ports for USB 3 devices, one high-rate device per controller; USB 2 devices top out near 35–40 MB/s.
6. *Check*: count samples received vs expected ($f_s\times$ elapsed time) — PySDR notes that receiving fewer samples than the configured rate means you are dropping [12].

**Latency.** USB and host buffering add hundreds of µs to ms: a UHD round-trip test measured ≈ 160 µs minimum for a B210 over USB 3 and ≈ 75 µs for an X300 over PCIe at 20 MS/s with small buffers [14]; GNU Radio buffers add more. Protocols with tight turnaround (Wi-Fi SIFS 10 µs) must be done in FPGA (openwifi) ([FPGA](fpga-for-sdr.md)).

## Design equations & rules of thumb

| Rule | When valid | Typical values |
|---|---|---|
| Data rate = $f_s\times$ bytes/sample | streaming, recording | cu8 2, ci16 4, cf32 8 B |
| Decimate in the first block after the source | any high-rate flowgraph | ÷10–÷100 |
| No Throttle with hardware sources/sinks | GNU Radio | Throttle only for file/sim |
| "O"/"D" = RX overflow/drop; "U" = TX underflow | UHD | host too slow |
| Samples received ≈ $f_s\times t$ | sanity check | else dropping |
| RTL-SDR cu8: $(u-127.5)/127.5$ | raw rtl_sdr files | −128 → ≈ −45 dBFS DC |
| Use 3.10 for projects; evaluate 4.0 RC | 2026 | [1], [2] |

## Worked examples

**1 — A GNU Radio flowgraph to record and live-decode rocket LoRa (433.92 MHz, SF9/BW125).**
`osmocom Source` (or `Soapy RTLSDR Source`; 2.0 MS/s, centre 433.52 MHz, manual gain) → branch A: `File Sink` (cu8 or cf32) + a SigMF `.sigmf-meta` written by a small Python script with `core:sample_rate` = 2e6, `core:frequency` = 433.52e6, `core:datetime` = launch time → branch B: `Frequency Xlating FIR Filter` (shift +400 kHz → 0, 23-tap decimate ÷4 → 500 kS/s) → gr-lora_sdr receiver hier block (SF 9, BW 125 kHz, CR per flight config, `os_factor` 4) → `Message Debug`/PDU to file. Branch C: `QT GUI Waterfall Sink` after decimation (not at 2 MS/s). gr-lora_sdr supports SF5–12 (SF5/6 not SX126x-compatible), CR 4/5–4/8, explicit/implicit header, 1–255-byte payloads, CRC, low-data-rate optimisation and soft decoding, tested against RFM95/SX1276/SX1262 [15]. See [ground station](../15-lora-ism-radios/ground-station-design.md) and [multirate Example 1](multirate-dsp-decimation-cic.md).

**2 — Python-only receiver with a Pluto (pyadi-iio).**
```python
import adi, numpy as np
sdr = adi.Pluto("ip:192.168.2.1")
sdr.sample_rate = int(2e6); sdr.rx_lo = int(433.52e6)
sdr.rx_rf_bandwidth = int(1.5e6); sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = 40; sdr.rx_buffer_size = 2**18
x = sdr.rx() / 2**11          # complex, ~±1 full scale (12-bit data in int16)
```
Then NCO shift, `scipy.signal.resample_poly` / FIR decimation, and the demodulators from [software demodulation](software-demodulation.md). At 2 MS/s, Python on a laptop keeps up comfortably (script throughput figures); beyond ~10 MS/s use GNU Radio/C++ or on-device processing.

**3 — Signal archaeology on an unknown 433 MHz burst.** Record with `rtl_sdr -f 433.92e6 -s 1e6 capture.cu8` (write a SigMF meta alongside), open in **inspectrum** (reads SigMF/cf32/cu8) to measure symbol rate and deviation with its cursors, then in **URH** to demodulate, auto-detect parameters and split into messages; finally write a decoder or an rtl_433 flex decoder. Keep the recording and annotations — SigMF annotations (`core:sample_start`, `core:sample_count`, `core:freq_lower_edge/upper_edge`, `core:label`) make the dataset reusable [5].

**4 — Choosing an application.** Just looking/listening on macOS: **SDR++** (cross-platform, fast, SoapySDR-like device support) or **GQRX** (GNU Radio + Qt, via gr-osmosdr). Windows: **SDR#** (Airspy), **SDR Console**, SDRuno (SDRplay). Many radios and TX support: **SDRangel**. Analysis: **inspectrum**, **URH**. Decoding: **rtl_433**, **direwolf** (APRS), **dump1090** (ADS-B), **gr-satellites**, **gr-lora_sdr**. Development: GNU Radio Companion, PySDR examples [12], liquid-dsp (C, MIT-licensed, no dependencies) [16].

## Practical notes
- **Installing on macOS**: radioconda (conda-forge GNU Radio distribution) or Homebrew/MacPorts; SDR++ has native builds ([installing tools](../16-simulation-tools/installing-tools-macos.md)). RTL-SDR V4/V4L need the RTL-SDR Blog librtlsdr fork (or recent Osmocom).
- **Keep driver calibrations on** (DC/IQ correction, AD936x tracking) and **set gains manually** ([IQ](iq-complex-baseband.md), [hardware survey](sdr-hardware-survey.md)).
- **Timestamp recordings**: SigMF `core:datetime` in each capture; for multi-receiver work lock to a GPSDO/PPS and use UHD's `rx_time` tags.
- **Version pinning**: OOT modules are built against a specific GNU Radio minor version; record the versions in your project README.
- **Test with files first**: develop flowgraphs on recorded IQ (with Throttle), then switch to live hardware.

## Common mistakes & misconceptions
1. **Adding a Throttle block to a hardware flowgraph** — two clocks fighting; remove it [8].
2. **Ignoring "O"/"U"** — the flowgraph "works" but packets are corrupted; fix throughput first.
3. **Running every block at the SDR rate** — decimate first.
4. **Saving cf32 when cu8/ci16 suffices** — 4×/2× the disk for no information gain (the ADC had 8 or 12 bits).
5. **Raw files without metadata** — six months later nobody knows the rate, centre frequency or sample format. Use SigMF.
6. **Wrong RTL-SDR offset (128 instead of 127.5)** — fake DC spike (script).
7. **Mixing GNU Radio versions and OOT builds** — import errors or crashes; rebuild OOTs per version.
8. **Assuming Python is too slow for anything** — vectorised numpy/scipy handles several MS/s; per-sample Python loops do not.

## How to simulate / verify
- `python3 tools/verify/dsp_host_stack.py` (≈ 1 s): cu8 conversion and the DC pitfall; SigMF write/read with required fields; host throughput of FIR/FFT/mixing/resampling on the current machine. All PASS.
- Overflow test on real hardware: stream for 60 s, count samples, compare with $f_s\times60$; repeat with GUI sinks off/on to see their cost.
- PySDR's chapters (IQ files and SigMF, RTL-SDR, Pluto, USRP) give runnable Python for each device [12].

## Open questions / gaps
- GNU Radio wiki pages (stream tags, message passing, YAML GRC, OOT tutorials) were not directly reachable (Cloudflare); details are from GNU Radio source headers and search summaries — marked medium confidence.
- GNU Radio 4.0's scheduler, block API and migration path are not described in depth (still RC).
- No measured GNU Radio (VOLK) throughput numbers on this machine; only numpy/scipy figures.

## Sources
1. GNU Radio project, releases, https://github.com/gnuradio/gnuradio/releases (fetched 2026-09-29) — v3.10.12.0 (2025-02-20), v3.10.11.0 (2024-07-24), v3.10.10.0 (2024-04-22). (docs)
2. GNU Radio project, GNU Radio 4.0 releases, https://github.com/gnuradio/gnuradio4/releases (fetched 2026-09-29) — 4.0.0 RC3 (2026-09-22), pre-release for evaluation and API feedback; core intended stable; breaking API changes. (docs)
3. GNU Radio source headers `gnuradio-runtime/include/gnuradio/block.h`, `sync_block.h`, `tags.h` and `lib/block.cc`, https://github.com/gnuradio/gnuradio; wiki pages "Stream Tags", "Message Passing", "Hier Blocks and Parameters", "Embedded Python Block", "OutOfTreeModules", "YAML GRC", https://wiki.gnuradio.org (docs; wiki content via search summaries) — via helper research 2026-09-27.
4. Ettus Research, UHD manual: general (overflow "O"/"D", underflow "U"), identification, synchronisation, stream args, https://files.ettus.com/manual/ ; UHD releases (v4.11.0.0, 2026-09-09). (docs)
5. SigMF specification v1.2.x and JSON schema, https://github.com/sigmf/SigMF (docs) — required globals `core:datatype`, `core:version`; datatype pattern; captures and annotations fields.
6. E. Blossom, "GNU Radio: tools for exploring the radio frequency spectrum," *Linux Journal* (2004); GNU Radio project documentation. (magazine/docs) — history and architecture. *Cited from general knowledge.*
7. VOLK, https://github.com/gnuradio/volk (docs) — SIMD kernels, `volk_profile`; v3.3.0 (2026-02-08).
8. GNU Radio `gr-blocks/include/gnuradio/blocks/throttle.h` (docs) — Throttle only where no other rate-limiting block exists.
9. GNU Radio news, "GNU Radio v3.10.0.0 release" (2022-01-17), https://www.gnuradio.org/news/ (docs).
10. Osmocom, gr-osmosdr, https://github.com/osmocom/gr-osmosdr (docs).
11. Analog Devices, libiio (README, tools migration notes; v1.0.0 release 2026-09-22), https://github.com/analogdevicesinc/libiio (docs).
12. M. Lichtman, *PySDR*, chapters "PlutoSDR in Python", "RTL-SDR in Python", "USRP in Python", "IQ Files and SigMF", https://pysdr.org (online textbook) — Pluto URI, throughput notes, dropped-sample check.
13. Pothosware, SoapySDR wiki, https://github.com/pothosware/SoapySDR/wiki (docs).
14. S. Kumar, F. Kaltenberger (EURECOM), "Latency measurements of USRP-based SDR platforms" (2018 preprint), https://sumiteurecom.github.io/latency-measurements-usrp.pdf (preprint) — B210 ≈ 160 µs, X300 ≈ 75 µs minimum round trip.
15. J. Tapparel et al., gr-lora_sdr README and SPAWC 2020 paper (arXiv:2002.08208), https://github.com/tapparelj/gr-lora_sdr (peer-reviewed + code).
16. J. D. Gaeddert, liquid-dsp, https://github.com/jgaeddert/liquid-dsp and https://liquidsdr.org (docs) — v1.8.3 (2026-09-26), MIT licence.
17. Application repositories: SDR++ https://github.com/AlexandreRouma/SDRPlusPlus; GQRX https://github.com/gqrx-sdr/gqrx; SDRangel https://github.com/f4exb/sdrangel; inspectrum https://github.com/miek/inspectrum; URH https://github.com/jopohl/urh; Airspy SDR# https://airspy.com/download/; SDR Console https://www.sdr-radio.com (docs; via helper research).
