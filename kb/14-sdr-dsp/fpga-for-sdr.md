---
title: FPGAs for SDR — when to use one, DSP slices, fixed point, CORDIC, Zynq + AD9361, RFSoC, open-source gateware and latency
domain: 14-sdr-dsp
slug: fpga-for-sdr
tags: [fpga, zynq, ad9361, rfsoc, dsp48, fixed-point, rounding, bit-true, cordic, pipelining, time-sharing, rfnoc, adi-hdl, openwifi, maia-sdr, litex, amaranth, hackrf-pro, latency, hls]
prerequisites: [digital-filters-fir-iir.md, multirate-dsp-decimation-cic.md, nco-ddc-duc.md, gnu-radio-and-software-stack.md]
related: [sdr-hardware-survey.md, software-demodulation.md, fft-spectral-analysis-windows.md, ../05-analog-electronics/data-converters-adc-dac.md, ../18-components-parts/adcs-dacs-for-sdr.md, ../12-phased-arrays/beamforming-architectures.md, ../11-radar/fmcw-radar.md, ../11-radar/diy-radar-hardware.md, ../13-pcb-rf-layout-emc/mixed-signal-layout.md]
level: mixed
confidence: medium
last_updated: 2026-09-29
---

# FPGAs for SDR

## Questions this page answers
- When do I actually need an FPGA in an SDR, and when is a PC or microcontroller enough?
- What is a DSP slice, and how many do I need for a given filter at a given sample rate?
- How do I plan fixed-point word lengths, and which rounding mode should I use?
- How is CORDIC used in FPGA radios (NCOs, FM discriminators, magnitude/phase)?
- What do the Pluto's Zynq-7010, an AntSDR's Zynq-7020 or an RFSoC give me?
- Which open-source FPGA SDR projects can I learn from (ADI HDL, RFNoC, openwifi, Maia SDR, HackRF Pro gateware, LiteX)?
- How much latency does an FPGA path have compared with USB + PC?
- How do I verify FPGA DSP (bit-true models)?

## TL;DR
- **Use an FPGA when**: the sample rate is too high for the host link (≥ ~10–60 MS/s continuous, multichannel), the latency budget is µs (radar gating, TDD/Wi-Fi turnaround, loop control), you need deterministic timing across channels (phased arrays, MIMO), or you want to cut data before it hits USB (DDC, FFT, detection). Otherwise, do it on the host ([software stack](gnu-radio-and-software-stack.md)).
- **DSP slice** = hardened multiply–accumulate (Xilinx 7-series DSP48E1: 25×18 multiplier, 25-bit pre-adder, 48-bit accumulator; UltraScale DSP48E2: 27×18) [1]. **Slices needed ≈ (folded MACs per second) / f_clk**: a 255-tap complex FIR at 61.44 MS/s needs ≈ 79 slices at 200 MHz — essentially all 80 of the Pluto's XC7Z010; the XC7Z020 has 220 [2]. An 83-tap LoRa channel filter at 500 kS/s fits in *one* time-shared slice (script).
- **Word lengths**: accumulator ≥ data + coefficient bits + $\lceil\log_2(\sum|h|/\max|h|)\rceil$ … worst case $\log_2N$ — 16 × 18-bit with 83 taps needs 36 bits (≤ 41 by the naive rule) and fits the 48-bit accumulator; the bit-true model matched float to 93 dB SNR (script).
- **Rounding**: truncation biases by −½ LSB (a DC spike at −96 dBFS for a 16-bit output — visible after long FFT averaging); round-half-up is nearly unbiased; convergent (round-half-even) is unbiased (script).
- **CORDIC**: shift-add rotation/vectoring, ≈ 1 bit per iteration, gain 1.64676 ([NCO](nco-ddc-duc.md)); a 16-iteration integer CORDIC FM discriminator matched the float result to 0.1 % of deviation (script).
- **Platforms**: Zynq-7000 + AD936x (Pluto XC7Z010, AntSDR/E310 XC7Z020, E320 XC7Z045) [3], [4]; RFSoC (direct RF sampling with integrated DDC/NCO, e.g. RFSoC 4x2: XCZU48DR, 4 × 5 GS/s ADC, 2 × 9.85 GS/s DAC, US$2,499 academic) [5]; USRP X410 uses an RFSoC ZU28DR [6].
- **Latency**: FPGA FIR ≈ group delay + pipeline (255 taps at 61.44 MS/s ≈ 2.2 µs) vs ≈ 75–160 µs minimum round trip through PCIe/USB 3 to a host [7].

Verified by `tools/verify/dsp_fpga_fixed.py` (all PASS).

## Intuition (no math)
A CPU is one very fast worker doing tasks one after another; an FPGA is a factory floor where you lay out hundreds of small workers (multipliers, adders, memories) and wire them into an assembly line. Each worker is slow compared with a CPU core (100–500 MHz), but they all work every clock cycle, in parallel, with exact timing. That makes FPGAs ideal for the first stages of an SDR — mixing, filtering and decimating tens to thousands of millions of samples per second — and for anything that must happen within a microsecond. The cost: you design the assembly line yourself, in fixed-point arithmetic, and debugging means simulation, not print statements.

The common pattern is a *split*: the FPGA does the high-rate, regular work (DDC, FIR, FFT, detection, timestamping) and hands a much smaller stream to a processor (the Zynq's ARM cores or a PC) for the irregular, low-rate work (decoding, protocols, GUI).

## The math

### Level 1 — throughput and resources
- **MAC rate**: an $N$-tap real FIR at output rate $f_{out}$ needs $N f_{out}$ MAC/s; complex data with real taps needs 2×; symmetric taps halve it (pre-adder folds pairs).
- **Slices**: one DSP slice does one MAC per clock, so slices ≈ MAC/s ÷ $f_{clk}$. If $f_{clk}\gg f_s$, one slice can be **time-shared** over $f_{clk}/f_s$ taps (a "serial" or "semi-parallel" FIR).
- Script §4 at $f_{clk}$ = 200 MHz: LoRa channel FIR (83 taps, complex, 500 kS/s): 0.042 G folded MAC/s → **1 slice**; 31-tap half-band (17 non-zero taps, complex, 30.72 MS/s): 0.55 G → **3 slices**; 255-tap complex FIR at 61.44 MS/s: 15.7 G → **79 slices**.
- **Device budgets** (7-series Zynq): XC7Z010 80 DSP48E1, XC7Z020 220 [2]. Block RAMs hold FIR delay lines, NCO tables, FFT buffers; LUTs/flip-flops hold CICs, CORDICs, control.
- **Multiplier-free blocks**: CIC decimators (adders/registers only), half-band zeros, $f_s/4$ mixers and CORDIC save DSP slices ([multirate](multirate-dsp-decimation-cic.md), [NCO](nco-ddc-duc.md)).

### Level 2 — fixed-point design
**Formats.** Q notation: a signed $B$-bit word with $F$ fractional bits (Q$(B-F)$.$F$) represents integers × $2^{-F}$. Multiply adds word lengths ($B_1 + B_2$) and fractional bits; add needs one extra bit per doubling of the number of terms.

**Accumulator sizing.** For an FIR with integer taps $h_q$ and inputs bounded by $|x|\le X$, the output is bounded by $X\sum|h_q|$ — the tight bound. The naive bound $B_x + B_h + \lceil\log_2N\rceil$ assumes all taps are full-scale. Script §1: an 83-tap channel filter, 16-bit data, 18-bit taps: tight bound 36 bits, naive 41 bits — both fit the DSP48's 48-bit accumulator, so a single cascaded slice chain handles it without intermediate rounding. The bit-true integer output, rounded back to 16 bits, matches the floating-point filter to **93 dB SNR** — i.e. the 16-bit output quantisation is the only visible error.

**Rounding when discarding LSBs** (script §2, dropping 6 bits of random data):
- *Truncation* (just drop bits = floor): mean error −0.49 LSB → a DC offset. At a 16-bit output that is −96 dBFS — invisible in a single FFT, but after heavy averaging it becomes a centre spike indistinguishable from LO leakage ([IQ](iq-complex-baseband.md)).
- *Round half up* (add ½ LSB then truncate — one adder, or free via the DSP48's rounding constant): mean +0.008 LSB.
- *Convergent* (round half to even): unbiased; available in DSP48 pattern-detect logic and in vendor IP.
- In recursive structures (IIR, loop filters, NCO accumulators) bias accumulates — always round, and saturate rather than wrap except where wrap is intended (CIC integrators, phase accumulators) ([filters](digital-filters-fir-iir.md), [multirate](multirate-dsp-decimation-cic.md)).

**Scaling for dynamic range.** Keep signals near full scale at every node (left-justify after each decimation, since filtering out noise lowers the RMS), but leave headroom for peaks: complex Gaussian signals have ≈ 10–12 dB peak-to-average at 10⁻⁴–10⁻⁵ probability; design for overflow probability, then saturate.

**CORDIC in hardware** ([NCO](nco-ddc-duc.md) for the derivation): a pipelined CORDIC has one stage per iteration — two adders, shifts, and a small arctan constant per stage — and produces one result per clock with latency = number of stages. Uses: NCO sine/cosine (rotation mode), magnitude and phase (vectoring mode) for AM/FM/PM demodulation, polar-to-rectangular conversion for phase shifters in beamformers. Script §3: 16 iterations, 18-bit datapath, FM discriminator on $x[n]x^*[n-1]$ — maximum error 5.3 Hz on a 5 kHz deviation (0.1 %), set by the 14-fraction-bit angle and the product rescaling [8].

### Level 3 — platforms, projects and design flow
**Zynq-7000 + AD936x** (ADI HDL reference designs [9]): the AD936x streams 12-bit I/Q over a parallel LVDS/CMOS interface to the FPGA fabric; the ADI HDL provides the interface core, DMA to the ARM's DDR, and optional FIR/DDS blocks; Linux (IIO drivers) runs on the ARM and serves samples over USB/Ethernet (libiio). Examples: **ADALM-Pluto** (AD9363 + XC7Z010, 512 MB DDR), **AntSDR E200/E310** (AD9361/AD9363 + XC7Z020, Gigabit Ethernet, Pluto-compatible or UHD firmware [4]), **USRP E310/E320** (XC7Z020 / XC7Z045 [3]), **LibreSDR** and Pluto+ clones. Because the Pluto's XC7Z010 is small (80 DSP slices), heavy processing there must use multiplier-light structures — **Maia SDR** (Daniel Estévez) fits a low-resource FFT in Amaranth HDL into the Pluto and serves a real-time waterfall up to 61.44 MS/s plus SigMF recording to a browser, sidestepping the USB 2 bottleneck [10].

**RFSoC** (AMD Zynq UltraScale+ RFSoC): multi-GS/s RF ADCs and DACs on the same die as the FPGA and ARM cores; each converter tile includes a digital mixer with a 48-bit NCO and decimation/interpolation filters (vendor documentation as summarised; not re-read) [11]. The **RFSoC 4x2** academic board (XCZU48DR; 4 × 5 GS/s ADC, 2 × 9.85 GS/s DAC; PYNQ Python framework; US$2,499, universities only) [5] and the **USRP X410** (ZU28DR, 4 × 400 MHz channels, 1 MHz–7.2 GHz) [6] are the accessible entry points. Direct RF sampling needs ps-level clock jitter ([sampling](sampling-aliasing-bandpass-sampling.md), [phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**Ettus RFNoC** (UHD 4): FPGA blocks (DDC/DUC, FFT, FIR, Replay/DRAM buffering, custom) connected by a network-on-chip inside X3x0/N3xx/E320/X410 USRPs and controlled from UHD/GNU Radio [12].

**openwifi** (UGent, AGPL): a full 802.11a/g/n PHY and low-MAC with CSMA/CA in FPGA on Zynq + AD9361 boards (ZC706/ZedBoard + FMCOMMS2, ADRV9361-Z7035, AntSDR…) meeting the 10 µs SIFS turnaround — the canonical example of latency that a host-based SDR cannot achieve [13].

**Lattice/LiteX/Amaranth open toolchains**: **HackRF Pro** replaces HackRF One's CoolRunner-II CPLD with a Lattice iCE40UP5K (5280 LUTs, 8 DSP blocks) whose Amaranth-HDL gateware, built with the open icestorm tools, implements a DC blocker, an $f_s/4$ shifter and 1–32× decimation/interpolation [14]. **LiteX-M2SDR** (Enjoy-Digital; Artix-7 XC7A200T + AD9361, PCIe Gen2 ×4, 61.44 MS/s, SoapySDR) and **LimeSDR XTRX** (XC7A50T) show PCIe-attached designs [15].

**Latency.** A measured minimum round trip (UHD latency test, 20 MS/s, small buffers): B210 over USB 3 ≈ 160 µs, X300 over PCIe ≈ 75 µs [7]; GNU Radio buffering typically adds ms. In fabric, a 255-tap FIR at 61.44 MS/s has 127 samples of group delay + ~20 pipeline clocks at 200 MHz ≈ **2.2 µs** (script §5); a CORDIC adds ~16 clocks. Radar range gating, TDD switching, AGC and fast frequency hopping belong in the FPGA.

**Design flow.**
1. *Floating-point reference* (Python/MATLAB) of the chain.
2. *Bit-true model* in Python with integers — exact word lengths, rounding and saturation (as in `tools/verify/dsp_fpga_fixed.py`, `dsp_nco.py`, `dsp_multirate_cic.py`); measure SNR/SFDR against the float reference.
3. *HDL* (Verilog/VHDL, Amaranth/Migen, or HLS from C++) using vendor IP (FIR Compiler, CIC Compiler, DDS Compiler, FFT) where sensible.
4. *Simulation* with test vectors from the bit-true model; compare sample-for-sample (cocotb makes this Python-driven).
5. *Timing closure* (pipelining registers, DSP-slice cascades), then on-hardware tests with injected tones and ILA/logic-analyser captures.

## Design equations & rules of thumb

| Rule | When valid | Typical values |
|---|---|---|
| Slices ≈ folded MAC/s ÷ $f_{clk}$ | FIR in DSP slices | 255 taps @ 61.44 MS/s complex: 79 @ 200 MHz |
| Time-share when $f_{clk}/f_s$ ≥ taps | low-rate filters | 83 taps @ 500 kS/s: 1 slice |
| Accumulator: $B_x + \lceil\log_2(\max|x|\cdot\sum|h_q|)\rceil$ bits | fixed-point FIR | 36 bits (naive 41) — fits 48 |
| Coefficient bits ≈ $A/6 + 2$ | FIR stop-band $A$ dB | 18 bits → ~100 dB floor |
| Truncation bias −½ LSB; round or use convergent | discarding LSBs | −96 dBFS DC at 16 bits |
| CORDIC ≈ 1 bit/stage, latency = stages | pipelined | 16 stages ≈ 16 bits |
| FPGA latency µs; host path ≥ ~0.1 ms | round-trip | 2.2 µs vs 75–160 µs |
| XC7Z010 80, XC7Z020 220 DSP48E1 | 7-series Zynq | Pluto vs AntSDR |

## Worked examples

**1 — Can a Pluto's FPGA decimate 61.44 MS/s to a LoRa channel on-chip?** Plan: NCO (quarter-wave LUT in one BRAM + 2 multipliers, or CORDIC in LUTs) → CIC ÷32, N = 5 (adders only; 12-bit in → 12 + 25 = 37-bit registers) → 1.92 MS/s → compensating FIR ÷4 (≈ 40 taps folded, complex: 40 × 480 kS/s × 2 ≈ 38 M MAC/s → 1 slice time-shared) → 480 kS/s → channel FIR (83 taps: 1 slice). Total ≈ 4–6 DSP slices of 80 and a few thousand LUTs — easily fits; the USB 2 link then carries 480 kS/s × 4 B = 1.9 MB/s instead of 246 MB/s. This is the rationale for on-device DDCs (and for Maia SDR-style firmware).

**2 — Why not run the same 255-tap filter at the full rate?** 79 DSP slices at 200 MHz: the whole XC7Z010 — and the AD936x interface, DMA and NCO also need resources. Decimate first ([multirate](multirate-dsp-decimation-cic.md)).

**3 — FM/FSK discriminator in fabric.** Complex multiply $x[n]x^*[n-1]$ (3–4 DSP slices, or 2 with the Karatsuba 3-multiplier trick time-shared), then a 16-stage pipelined CORDIC in vectoring mode (≈ 16 × 2 adders of 18–20 bits in LUTs) → phase difference = frequency, one output per clock. Script: 0.1 % error vs float. For LoRa, the equivalent FPGA kernel is dechirp (complex multiply by an NCO-generated chirp) + FFT ([demodulation](software-demodulation.md)).

**4 — FMCW radar on a Zynq + AD9361 board.** TX: DDS-generated chirp from a phase accumulator whose FTW ramps each clock ([NCO](nco-ddc-duc.md)) or a replay buffer; RX: dechirp (mixer), decimate, range FFT per chirp in the fabric, then Doppler FFT across chirps on the ARM. Deterministic chirp–ADC alignment (same clock, synchronous start) is the FPGA's key contribution ([FMCW radar](../11-radar/fmcw-radar.md), [DIY radar](../11-radar/diy-radar-hardware.md)).

## Practical notes
- **Start from a reference design** (ADI HDL `projects/pluto`, Ettus RFNoC examples, openwifi, Maia SDR) rather than from scratch; toolchain versions matter (Vivado version pinned per HDL release).
- **Keep a bit-true model under version control** and regenerate test vectors whenever word lengths change.
- **Clock-domain crossings** (ADC interface clock ↔ processing clock ↔ DMA clock) need FIFOs; most FPGA SDR bugs are CDC or reset bugs, not DSP bugs.
- **Measure SFDR on hardware** with an injected tone after every major change; digital spurs (NCO truncation, rounding bias, overflow) are easy to see in a long averaged FFT ([FFT](fft-spectral-analysis-windows.md)).
- **Power and heat**: RFSoC and large FPGAs need real cooling; the Pluto's Zynq runs warm and its XO drifts with temperature ([hardware survey](sdr-hardware-survey.md)).

## Common mistakes & misconceptions
1. **"FPGA = faster, so always better."** For ≤ a few MS/s a laptop (numpy/GNU Radio) is simpler and fast enough ([software stack](gnu-radio-and-software-stack.md) script: ~100 MS/s FIR).
2. **Sizing accumulators by guesswork** — use the $\sum|h|$ bound; overflow in a FIR is a burst of garbage, in an IIR a limit cycle or instability.
3. **Truncating everywhere** — DC bias spikes and, in loops, frequency drift.
4. **Saturating CIC integrators** — they must wrap ([multirate](multirate-dsp-decimation-cic.md)).
5. **Ignoring pipeline latency in feedback loops** (Costas/PLL in fabric) — each register adds loop delay, reducing phase margin.
6. **Testing only with floats** — the HDL will differ from the float model; only a bit-true model predicts it.
7. **Expecting an RFSoC board to be plug-and-play for hobby projects** — powerful, but the toolchain, clocking and thermal design are professional-level work.

## How to simulate / verify
- `python3 tools/verify/dsp_fpga_fixed.py` (< 1 s): bit-true FIR with DSP48-style word lengths vs float (93 dB SNR), accumulator bounds, rounding-mode biases, integer CORDIC FM discriminator, DSP-slice resource estimates, latency. All PASS.
- Related bit-true models: `dsp_nco.py` (NCO truncation/dither, integer CIC DDC), `dsp_multirate_cic.py` (wrap-around CIC).
- For HDL: cocotb (Python test benches driving Verilator/Icarus/GHDL or vendor simulators) with vectors from these models.

## Open questions / gaps
- RFSoC converter-tile details (NCO width, decimation options per generation, ZCU111/ZCU216 specs), DSP48E2 widths and the RFNoC device list are from search summaries, not re-read documents.
- No resource/timing results from an actual synthesis run are included; slice counts are arithmetic estimates.
- HLS (Vitis HLS, hls4ml-style) flows and GPU alternatives (e.g. cuSignal, Holoscan) not covered.

## Sources
1. AMD/Xilinx, *7 Series DSP48E1 Slice User Guide* UG479 (25×18 multiplier, 25-bit pre-adder, 48-bit ALU/accumulator, pattern detect, cascade) — as summarised by controlpaths.com, "Using DSP48E1 slice" (2021), https://www.controlpaths.com/2021/01/11/using-dsp48e1-slice/; *UltraScale DSP48E2* UG579 (27×18). (manufacturer docs via blog; DSP48E2 width unverified)
2. AMD/Xilinx, *Zynq-7000 SoC Product Selection Guide* (XMP097), https://docs.amd.com/v/u/en-US/zynq-7000-product-selection-guide — XC7Z010 80 DSP slices, XC7Z020 220. (manufacturer; via search summary 2026-09-29)
3. Ettus Research, UHD manual, USRP E3xx page, https://files.ettus.com/manual/page_usrp_e3xx.html — E310 XC7Z020, E320 XC7Z045. (manufacturer docs)
4. MicroPhase, AntSDR (antsdr_uhd firmware), https://github.com/MicroPhase/antsdr_uhd; PySDR Pluto chapter (Pluto = AD9363 + Zynq 7010), https://pysdr.org/content/pluto.html. (manufacturer/online textbook)
5. AMD/Xilinx RFSoC-PYNQ, "RFSoC 4x2 overview," https://github.com/Xilinx/RFSoC-PYNQ/blob/master/docs/rfsoc_4x2_overview.md — XCZU48DR, 4 × 5 GS/s ADC, 2 × 9.85 GS/s DAC, US$2,499 (academic). (manufacturer docs)
6. Ettus Research, USRP X410 product page (ZU28DR RFSoC, 4 × 400 MHz, 1 MHz–7.2 GHz). (manufacturer)
7. S. Kumar, F. Kaltenberger, "Latency measurements of USRP-based SDR platforms," EURECOM (2018 preprint), https://sumiteurecom.github.io/latency-measurements-usrp.pdf. (preprint)
8. J. E. Volder, "The CORDIC trigonometric computing technique," *IRE Trans. Electronic Computers* EC-8(3):330–334 (1959); R. Andraka, "A survey of CORDIC algorithms for FPGA based computers," *FPGA '98*, pp. 191–200. (peer-reviewed)
9. Analog Devices, HDL reference designs, https://github.com/analogdevicesinc/hdl (incl. `projects/pluto`). (manufacturer code/docs)
10. D. Estévez, Maia SDR, https://maia-sdr.org/ — Pluto firmware with Amaranth FPGA FFT, real-time waterfall to 61.44 MS/s, SigMF recording (docs).
11. AMD/Xilinx, *Zynq UltraScale+ RFSoC RF Data Converter* LogiCORE product guide PG269 (NCO frequency conversion, decimation). (manufacturer docs — *search summary only, unverified*)
12. Ettus Research, "Getting started with RFNoC in UHD 4.0," https://kb.ettus.com/Getting_Started_with_RFNoC_in_UHD_4.0, and UHD manual. (manufacturer docs)
13. open-sdr, openwifi, https://github.com/open-sdr/openwifi — 802.11a/g/n FPGA PHY/low-MAC, 10 µs SIFS, supported boards. (project docs)
14. Great Scott Gadgets, HackRF documentation "gateware," https://github.com/greatscottgadgets/hackrf/blob/main/docs/source/gateware.rst — HackRF Pro iCE40UP5K Amaranth gateware. (manufacturer docs)
15. Enjoy-Digital, LiteX-M2SDR, https://github.com/enjoy-digital/litex_m2sdr; Lime Microsystems / MyriadRF, LimeSDR XTRX, https://github.com/myriadrf/LimeSDR-XTRX. (project docs)
16. f. j. harris, *Multirate Signal Processing for Communication Systems* (2004/2021) — hardware-efficient polyphase/CIC structures; U. Meyer-Baese, *Digital Signal Processing with Field Programmable Gate Arrays*, 4th ed., Springer (2014) — fixed-point FIR/CIC/CORDIC on FPGAs. (textbooks)
