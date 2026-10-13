## 3. Misconceptions in the wild, and whether the KB addresses them

✅ = explicitly corrected in a page's "Common mistakes" (or main text); ◐ = the physics is there but the
myth is not called out; ✗ = not addressed. Examples are Reddit post URLs (titles paraphrased in §5).

### 3a. LoRa / Meshtastic range and antenna myths

| Misconception (as it shows up in posts) | Examples | KB | Where / what to add |
|---|---|---|---|
| A higher-dBi omni always gives more range | https://www.reddit.com/r/meshtastic/comments/1pr10y0/ , https://www.reddit.com/r/meshtastic/comments/1sz036v/ | ✅ | 08/antenna-fundamentals (collinear vs overhead/nearby node, a forum-observed note); add the elevation-pattern picture for hilltop vs valley nodes |
| The stock/stubby antenna that came with the board is fine, and anything sold "for 868/915" is tuned to it | https://www.reddit.com/r/meshtastic/comments/1ststnd/ (paper-clip dipole "doubled" range), https://www.reddit.com/r/meshtastic/comments/1vgrasw/ , https://www.reddit.com/r/meshtastic/comments/1qdjrg2/ | ◐ | 08/antenna-measurement explains S11 but never says cheap stock antennas are often mistuned or mis-banded; add "measure before trusting" with a NanoVNA recipe link |
| A node heard 400–5 500 miles away proves an RF record | https://www.reddit.com/r/meshtastic/comments/1jlbuj9/ , https://www.reddit.com/r/meshtastic/comments/1luhjva/ | ✗ | MQTT/internet bridging makes impossible "receptions" appear; genuine long hops need elevated LOS or ducting (09/fresnel covers ducting). Add to 15/lorawan-vs-raw-lora |
| A louder 1 W node fixes a mesh's range | https://www.reddit.com/r/meshtastic/comments/1pqwwlx/ , https://www.reddit.com/r/meshtastic/comments/1ujkxzv/ | ◐ | 15/lora-sensitivity ("2 W doubles range" is corrected: +3 dB = ×1.41); missing: the link is only as good as the weaker direction (same receiver), plus legality |
| "LoRa range is X km" / SF12 always means more range | https://www.reddit.com/r/Lora/comments/1ugy0ix/ , https://www.reddit.com/r/meshtastic/comments/1q1wohs/ | ✅ | 15/lora-sensitivity-and-link-budget (range is geometry; SF12 fragility) |
| Switching the LNA on always improves reception | https://www.reddit.com/r/meshtastic/comments/1w6wbs0/ , https://www.reddit.com/r/sdr/comments/sdlwxu/ | ◐ | 06/lna-design and 14/sdr-hardware-survey say when an LNA helps; the urban-blocking / overload trade-off is not stated as a myth |
| LoRa decoding below the noise floor "breaks physics" | https://www.reddit.com/r/Lora/comments/dy62h7/ , https://www.reddit.com/r/rfelectronics/comments/uh9oge/ | ✅ | 07/sensitivity-and-mds, 10/ber-ebn0-and-shannon |
| A roof/flagpole is always the best spot, no other concerns | https://www.reddit.com/r/meshtastic/comments/1my7fu9/ | ◐ | 09/fresnel covers height; lightning/bonding absent (D1 #15) |

### 3b. Antenna and feedline myths

| Misconception | Examples | KB | Where / what to add |
|---|---|---|---|
| A tiny/compact "miracle" antenna performs like a full-size one | https://www.reddit.com/r/HamRadio/comments/1uf2ofq/ | ✅ | 08/small-antenna-limits (Chu, crowdfunded "tiny long-range" claims) |
| The small antenna on a toy/remote is "just for show" (the inverse myth) | https://www.reddit.com/r/AskElectronics/comments/1gi6ug7/ | ✅ | 08/small-antenna-limits + 09/link-budget: short links need very little efficiency |
| An antenna cut for one band cannot receive another; a "directional" antenna is deaf off-axis | https://www.reddit.com/r/HamRadio/comments/1eh1g88/ , https://www.reddit.com/r/HamRadio/comments/11m5gic/ | ◐ | Add off-band/harmonic response and "receivers are selective, antennas mostly aren't" to 08/dipoles-and-monopoles |
| Coax impedance depends on length; a multimeter should read 50 Ω | https://www.reddit.com/r/rfelectronics/comments/1k1wror/ , https://www.reddit.com/r/HamRadio/comments/1ppna66/ | ✅ | 03/telegrapher-equations-characteristic-impedance |
| A splitter only works one way | https://www.reddit.com/r/HamRadio/comments/16wu8wt/ | ✅ | 06/couplers-dividers-combiners (reciprocity) |
| Soldering a wire onto a PCB/Bluetooth antenna extends its range | https://www.reddit.com/r/AskElectronics/comments/giiiid/ | ◐ | 08/pcb-and-chip-antennas explains ground/keep-out dependence but not this specific trap |
| Antennas "stop working" above some frequency; RF and light are different things | https://www.reddit.com/r/rfelectronics/comments/lipbt1/ , https://www.reddit.com/r/rfelectronics/comments/ilgnkt/ | ◐ | Add an "RF to optics" continuum paragraph (conductor loss, plasmonics, why optical antennas are nano-scale) |
| Any metal mesh box or "RF-blocking" fabric is a Faraday cage | https://www.reddit.com/r/rfelectronics/comments/1p7puxl/ , https://www.reddit.com/r/rfelectronics/comments/1o46jv2/ | ◐ | 02/waveguides (apertures below cutoff) only; 13/shielding-and-isolation (planned) should cover seams, doors, fabrics |

### 3c. SDR gain, sample-rate and "phantom signal" confusion

| Misconception | Examples | KB | Where / what to add |
|---|---|---|---|
| A station heard at the "wrong" frequency is really transmitting there | https://www.reddit.com/r/sdr/comments/1nu0vj8/ (music at 410 MHz), https://www.reddit.com/r/sdr/comments/knxqwm/ , https://www.reddit.com/r/sdr/comments/142c7sj/ , https://www.reddit.com/r/sdr/comments/1nkgofn/ | ◐ | 17/sdr-as-test-equipment asks "are the spikes and mirrors real?" and covers image/DC; add tuner LO-harmonic mixing (e.g. FM ×4 ≈ 410 MHz) and overload IMD |
| More gain is always better / an SDR can't be overloaded | https://www.reddit.com/r/RTLSDR/comments/10da8zd/ , https://www.reddit.com/r/RTLSDR/comments/olhemk/ | ✗ | No gain-staging procedure anywhere (raise gain until the noise floor lifts ~3–5 dB, back off at spurs, AGC off, pre-filter first). Add to 14/sdr-hardware-survey |
| A higher sample rate gives better sensitivity / more usable bandwidth | https://www.reddit.com/r/RTLSDR/comments/mm7a0k/ | ◐ | 14/sampling (span = fs, ~80 % flat) and 14/fft (noise per bin) cover it; state the myth and the RTL2832 USB limits explicitly |
| The centre spike / mirror image is a real signal | (covered pattern) | ✅ | 14/iq-complex-baseband (DC spike, image, offset tuning) |
| Wavy/diagonal-lined NOAA images mean a bad antenna | https://www.reddit.com/r/RTLSDR/comments/fhsee6/ , https://www.reddit.com/r/RTLSDR/comments/jajlhl/ | ✗ | Sample-clock/ppm error and Doppler in APT decoding; add to a satellite-reception recipe |

### 3d. General RF myths

| Misconception | Examples | KB | Where / what to add |
|---|---|---|---|
| RF from 5G/small cells/rooftop sites is dangerous like ionising radiation | https://www.reddit.com/r/rfelectronics/comments/1ik7am5/ , https://www.reddit.com/r/rfelectronics/comments/17wxqs0/ , https://www.reddit.com/r/HamRadio/comments/1kp7074/ | ◐ | 19/rf-exposure-safety gives limits and distances but never says RF is non-ionising (no page contains "ionising"); add one paragraph (photon energy, heating as the established mechanism) |
| Matching means making the impedance as small as possible | https://www.reddit.com/r/rfelectronics/comments/1jvznka/ | ✅ | 01/network-theorems-max-power-transfer |
| "0 dBm Wi-Fi" means 1 mW is received; dB and dBm add alike | https://www.reddit.com/r/rfelectronics/comments/uoszuv/ , https://www.reddit.com/r/rfelectronics/comments/nt616h/ | ✅ | 00/decibels-and-log-units |
| With every frequency in the air at once, signals must all interfere | https://www.reddit.com/r/rfelectronics/comments/ltnvrp/ | ◐ | Plain-language superposition + selectivity box (reinforces D1 #29) |
| Dental fillings can receive radio stations | https://www.reddit.com/r/rfelectronics/comments/oh4zpy/ | ◐ | 05/diodes covers rectifying junctions; add the myth with the physics of why it is (almost always) folklore |
| You need an expensive lab to learn RF | https://www.reddit.com/r/rfelectronics/comments/o2pgid/ | ✅ | 17/lab-setup-by-budget |
| You must master Pozar (and all the maths) before building anything | https://www.reddit.com/r/rfelectronics/comments/i3j3qb/ , https://www.reddit.com/r/rfelectronics/comments/1qlybi1/ | ◐ | 00/math-roadmap-for-rf is maths-first; commenters converge on build-and-measure early (see §4) |
