# Taxonomy (planned pages per domain). Edit THIS file to plan pages; tools/build_index.py regenerates INDEX.md and FAQ.md.


## 00-math-foundations — the maths toolkit
rf-concepts-for-beginners · rf-learning-roadmap · math-roadmap-for-rf ·
decibels-and-log-units · complex-numbers-and-phasors · fourier-series-and-transform ·
laplace-transfer-functions-bode · linear-systems-convolution · vector-calculus-for-em ·
probability-random-processes-and-psd · differential-equations-circuits-waves ·
special-functions-bessel-sinc · numerical-methods-overview · matrices-and-linear-algebra-for-networks ·
z-transform-and-discrete-time-systems · estimation-theory-ml-map-crb · kalman-filter-and-state-estimation ·
canonical-values-and-conventions

## 01-circuit-theory — lumped circuits
lumped-elements-impedance-admittance · network-theorems-max-power-transfer · resonance-and-q ·
passive-filter-design-prototypes · two-port-networks-zyh-abcd · transformers-coupled-inductors ·
transient-and-step-response · energy-storage-and-reactive-power

## 02-electromagnetics — fields and waves
maxwells-equations · wave-equation-plane-waves-polarization · poynting-vector-power-flow ·
boundary-conditions-reflection-refraction · skin-effect-conductor-loss-roughness ·
dielectrics-permittivity-loss-tangent · magnetic-materials-permeability · quasi-static-vs-full-wave ·
radiation-from-currents-hertzian-dipole · waveguides-and-cavity-resonators · near-field-far-field ·
inductance-capacitance-from-fields · electromagnetic-units-and-constants ·
greens-functions-and-integral-equations

## 03-transmission-lines-matching
telegrapher-equations-characteristic-impedance · reflections-vswr-return-loss-mismatch ·
input-impedance-stubs-quarter-wave · smith-chart · impedance-matching-lumped-and-distributed ·
broadband-matching-bode-fano · s-parameters · planar-lines-microstrip-stripline-cpwg ·
coax-and-cables · time-domain-reflectometry · signal-flow-graphs-mason ·
antenna-tuners-and-atus · microstrip-discontinuities · periodic-structures-ebg

## 04-real-components-hf — real parts at RF
resistors-at-rf · capacitors-at-rf-mlcc · inductors-at-rf · ferrites-and-beads ·
pcb-parasitics-traces-vias-pads · crystals-and-resonators · package-parasitics-bondwires ·
component-models-s2p-spice

## 05-analog-electronics
diodes-schottky-pin-varactor · bjt-fundamentals-small-signal · fets-mosfet-jfet-gaas-gan ·
amplifier-topologies · feedback-and-stability · op-amps-real-limitations · oscillators ·
data-converters-adc-dac · power-supplies-for-rf-and-analog · active-filters ·
low-noise-analog-design · analog-signal-conditioning

## 06-rf-circuits — RF building blocks
lna-design · power-amplifiers · mixers · rf-filters-lc-saw-baw-cavity-microstrip ·
couplers-dividers-combiners · baluns-and-rf-transformers · rf-switches-attenuators-limiters ·
vco-and-pll-synthesizers · receiver-architectures · transmitter-architectures ·
detectors-and-power-meters · frequency-multipliers-dividers · circulators-isolators ·
amplifier-stability-and-biasing · agc-loops-and-receiver-gain-control ·
pa-control-protection-and-sequencing · duplexers-diplexers-and-crystal-filters ·
co-site-interference-and-transmitter-intermod · oscillator-phase-noise-ltv-isf ·
modulator-and-detector-circuits

## 07-noise-linearity
thermal-noise-and-noise-temperature · noise-figure-and-friis · phase-noise-and-jitter ·
nonlinearity-p1db-ip3-intermod · dynamic-range-sfdr-blocking · receiver-cascade-analysis ·
shot-and-flicker-noise · sensitivity-and-mds · volterra-series-and-nonlinear-analysis

## 08-antennas
antenna-fundamentals · dipoles-and-monopoles · loop-antennas · patch-antennas ·
helical-antennas · yagi-uda-and-log-periodic · horn-reflector-aperture-antennas ·
pcb-and-chip-antennas · gnss-antennas · antenna-matching-and-baluns · antenna-measurement ·
antennas-on-rockets · small-antenna-limits · antenna-polarization-and-circular-polarization ·
antenna-simulation-nec-openems · slot-antennas ·
wire-antennas-hf-random-wire-fan-dipole · inductive-coupling-rfid-nfc-wpt ·
lens-and-reflectarray-antennas · multiband-and-wideband-antennas · antenna-identification-guide

## 09-propagation-link-budget
friis-free-space-path-loss · link-budget-methodology · fresnel-zones-los-radio-horizon ·
two-ray-ground-reflection · empirical-path-loss-models · multipath-fading-doppler ·
atmospheric-rain-attenuation · ionospheric-hf-propagation · diffraction-knife-edge ·
link-margin-availability · polarization-mismatch-loss · solar-activity-and-space-weather ·
hf-propagation-modes-and-prediction · vhf-uhf-anomalous-propagation · ground-wave-and-lf-mf-propagation ·
satellite-links-doppler-tracking

## 10-comms-modulation
analog-modulation-am-fm-pm-ssb · digital-modulation-psk-qam-fsk · ber-ebn0-and-shannon ·
pulse-shaping-isi · spread-spectrum-dsss-fhss-css · ofdm · channel-coding-fec ·
synchronization-carrier-timing · matched-filter-detection · packet-framing-protocols · modulation-choice-guide ·
multiple-access-and-duplexing · mimo-capacity-and-channel-estimation · weak-signal-digital-modes

## 11-radar
radar-range-equation · radar-cross-section · pulsed-radar-and-pulse-compression ·
cw-and-doppler-radar · fmcw-radar · detection-theory-cfar · ambiguity-function-waveforms ·
clutter-and-mti · sar-and-imaging · mimo-radar-virtual-arrays · diy-radar-hardware ·
radar-tracking-monopulse-and-trackers · pulse-doppler-data-cube-and-prf-regimes ·
radar-applications-gpr-through-wall-sensing

## 12-phased-arrays
array-factor-linear-arrays · beam-steering-grating-lobes · planar-arrays-element-pattern-coupling ·
tapering-sidelobe-control · beamforming-architectures · phase-shifters-ttd-components ·
array-calibration · adaptive-beamforming-doa · diy-phased-array-projects ·
array-pattern-synthesis · conformal-and-cylindrical-arrays · stacking-and-arraying-yagis

## 13-pcb-rf-layout-emc
stackups-and-materials · grounding-and-return-paths · vias-stitching-fencing · rf-layout-rules ·
connectors-and-launches · shielding-and-isolation · emc-emi-fundamentals ·
power-distribution-decoupling-for-rf · mixed-signal-layout · jlcpcb-rf-manufacturing ·
thermal-management-rf · rf-pcb-review-checklist · digital-termination-and-crosstalk

## 14-sdr-dsp
sampling-aliasing-bandpass-sampling · iq-complex-baseband · digital-filters-fir-iir ·
multirate-dsp-decimation-cic · fft-spectral-analysis-windows · nco-ddc-duc ·
sdr-hardware-survey · gnu-radio-and-software-stack · software-demodulation · fpga-for-sdr ·
signal-identification-and-spectrum-survey · sdr-front-end-protection-and-filtering ·
sdr-gain-staging-and-reception-recipes

## 15-lora-ism-radios
lora-phy-css-math · lora-sensitivity-and-link-budget · lora-impairments-doppler-drift-timing · semtech-chip-family ·
lora-modules-ebyte-rfm-heltec · lorawan-vs-raw-lora · other-ism-radios-fsk-2g4 ·
rocket-telemetry-radio-design · ground-station-design · ism-band-plans-duty-cycle ·
choosing-and-judging-lora-antennas · lora-mesh-capacity-and-congestion

## 16-simulation-tools
tool-landscape-overview · spice-circuit-simulation · rf-circuit-simulators-harmonic-balance ·
em-solvers-fdtd-mom-fem · nec-antenna-modelling · openems-workflow · python-rf-toolkit ·
impedance-and-rf-calculators · simulation-validation · installing-tools-macos

## 17-test-measurement
vna-fundamentals-calibration · nanovna-librevna-practical · spectrum-analyzers ·
oscilloscopes-and-probing-for-rf · rf-power-measurement · noise-figure-measurement ·
phase-noise-measurement · antenna-range-ota-testing · sdr-as-test-equipment ·
signal-generators-and-sources · lab-setup-by-budget · fixtures-and-deembedding · rf-bring-up-debug-playbook ·
bench-measurement-recipes · interference-hunting-and-rf-immunity · basic-bench-instruments ·
resonator-and-cavity-perturbation-permittivity-measurement

## 18-components-parts
rf-transceiver-ics · lna-pa-gain-block-mmics · mixers-plls-vcos-parts · rf-switches-attenuator-parts ·
filter-parts-saw-ceramic-ltcc · connectors-and-cables-parts · pcb-substrates-parts ·
adcs-dacs-for-sdr · phased-array-and-radar-parts · sourcing-and-eval-boards · rf-modules ·
coax-and-connector-practicalities · rf-passives-and-support-parts

## 19-regulations-safety
spectrum-allocation-ism-bands · singapore-imda-rules · amateur-radio-licensing ·
rf-exposure-safety · certification-fcc-ce-imda · international-rules-for-competitions · lab-safety-esd-high-power ·
regulatory-faq-misc

## 20-projects-recipes — end-to-end worked designs
beginner-project-ladder · lora-rocket-telemetry-link · ground-station-tracking-yagi · patch-antenna-design-walkthrough ·
fmcw-radar-build · phased-array-starter-build · lna-design-walkthrough · sdr-receiver-build ·
bandpass-filter-design-walkthrough · gnss-front-end-design · design-review-checklists · validation-test-campaign

## 21-gnss — satellite navigation receivers and their use on rockets
gnss-signals-and-codes · gnss-receiver-architecture-acquisition-tracking ·
ttff-agps-almanac-ephemeris · gnss-timing-1pps · rtk-ppp-and-corrections · gnss-error-sources-dop ·
gnss-interference-jamming-spoofing · gnss-on-rockets-dynamics-and-limits · sdr-gnss-and-diy-receivers ·
gnss-receiver-integration-u-blox
