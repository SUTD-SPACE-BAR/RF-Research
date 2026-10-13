---
title: Amateur radio licensing for rocket telemetry — Singapore (IMDA) and USA (FCC Part 97)
domain: 19-regulations-safety
slug: amateur-radio-licensing
tags: [amateur-radio, ham-licence, imda, sarts, rae, 9v1, fcc-part-97, technician, 70cm, 433-mhz, telemetry, callsign, encryption, spread-spectrum, lora, space-station, spaceport-america]
prerequisites:
  - singapore-imda-rules.md
  - spectrum-allocation-ism-bands.md
related:
  - international-rules-for-competitions.md
  - certification-fcc-ce-imda.md
  - rf-exposure-safety.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../10-comms-modulation/packet-framing-protocols.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Amateur radio licensing for rocket telemetry — Singapore and USA

> **Not legal advice.** Summarises Singapore and US amateur rules as read on **2026-09-27**
> (last verified). Re-read the cited clause before relying on it; where a point is an
> interpretation it is labelled as one.

## Questions this page answers
- Can I legally run my 2 W 433 MHz LoRa telemetry under a ham licence in Singapore?
- How do I get a Singapore amateur licence, what does the exam cover and what does it cost?
- What is the difference between the Singapore Restricted and General class licences?
- What power may a Singapore amateur use on 70 cm, and does the Yagi gain count?
- Is encryption allowed on amateur radio? Is the EBYTE "encryption key" a problem?
- How often must a telemetry transmitter send its callsign?
- Is one-way telemetry from a rocket or balloon allowed on amateur bands?
- Can a Singapore ham transmit in the USA at Spaceport America, or do I need a US licence?
- Is LoRa "spread spectrum" under FCC Part 97, and why does it matter?
- Can I use 902–928 MHz (33 cm) amateur privileges at Spaceport America?
- What happens legally if my rocket goes above 50 km?
- When is licence-exempt (SRD/Part 15) better than amateur operation for 433 MHz telemetry?

## TL;DR
- **Singapore**: the Amateur Station Licence (Telecommunications (Radio-communication) Regulations regs 37–44 [1]; IMDA Amateur Radio Handbook 5th ed., Nov 2025 [2]) allows **430–440 MHz at ≤ 10 W ERP**, on a **secondary, shared basis, with IMDA's prior written consent** stating power and conditions (Appendix 1 footnotes 1, 2, 5). Restricted class (VHF/UHF only) needs 60 % in Section I of the RAE; General needs 60 % in Sections I and II. Fees: exam S$20 (students) / S$40; licence S$50 (Restricted) or S$100 (General) for 5 years. Age ≥ 16; 16–21 must be supervised.
- **Singapore conditions that bite telemetry**: plain language only and **no encryption devices** (reg 41, 42(a)); **no third-party messages**, only to other amateur stations unless IMDA permits (reg 42(b)–(d)); **callsign at the beginning and end of each transmission** (reg 40(d)); no uninterrupted transmission > 10 minutes (Handbook §4.7.1); logbook kept (12 months per reg 40(g); 2 years per Handbook §4.10.2 — keep 2 years); **IMDA-approved equipment** at **approved locations**; portable/mobile ≤ 10 W ERP and only in Singapore (§4.13).
- **ERP counts antenna gain**: 2 W into a 12 dBi Yagi = 17 W ERP > 10 W. A rocket dipole at 2 W is 1.8 W ERP (OK).
- **Open question (Singapore)**: Appendix 1 lists AM/FM/PM telegraphy and telephony emission classes (A1A…J3E, F1A–F3E, G3E) but no data ("D") classes; LoRa is a data emission. Because every 70 cm frequency already needs written consent (footnote 5), **ask IMDA explicitly to authorise "LoRa (chirp spread spectrum) data telemetry, 125 kHz, F1D/X-class" on your frequency**.
- **USA (47 CFR Part 97)** [3]: one-way **telemetry is an authorised transmission** (97.111(b)(7)); data stations may be **automatically controlled on 6 m and shorter** (97.221(b)); ID every 10 min and at the end of each communication (97.119); **no messages encoded to obscure meaning** (97.113(a)(4)); Technician class (35-question Element 2, pass 26) has full 70 cm privileges (97.301(a)).
- **LoRa under Part 97**: if treated as **SS** (bandwidth-expansion modulation, 97.3), it is allowed on 70 cm but **≤ 10 W PEP** (97.313(j)) and only between FCC-regulated points (97.311(a)); if treated as a **data** emission, 70 cm allows **100 kHz authorised bandwidth** (97.307(f)(6)) — a 125 kHz LoRa signal exceeds that, 62.5 kHz fits. At 2 W both readings are satisfied if you use SS; the classification is not settled by the rules.
- **Spaceport America specifics**: New Mexico is a **50 W PEP** area for 70 cm (97.313(f), US270); and **no amateur transmissions at all on 33 cm (902–928 MHz)** from the Texas/New Mexico box 31°41′–34°30′ N, 104°11′–107°30′ W (97.303(n)(2)) — Spaceport America (≈ 32°59′ N, 106°58′ W) is inside it. So the E220-900 can only run under Part 15 there.
- **Singapore hams in the US**: Singapore is **not** on the US bilateral reciprocal list [4], so a 9V1 licence does not authorise operation in the US (97.107) — sit the US Technician exam (any non-government person may qualify, 97.5(b)(1)) or have a US-licensed team member be control operator.
- **Above 50 km** an amateur station is a **space station** (97.3): only 435–438 MHz in 70 cm (97.207(c)), telecommand shutdown capability and FCC pre-space notification ≥ 90 days before integration (97.207(b),(g)).

## Intuition (no math)
The amateur service is a licensed hobby service: in exchange for passing an exam, you get far more power and spectrum than licence-exempt users, but you give up commercial use, secrecy and third-party traffic, and you must identify yourself. A rocket telemetry downlink is a natural fit — it is an experiment, one-way telemetry is explicitly allowed (US) or at least consistent with "the licensee's experiments" (Singapore), and 433 MHz sits inside the 70 cm amateur band. The friction points are (i) the licence is **personal**, so the licensed person must be responsible for the transmitter; (ii) **no encryption** — telemetry must be decodable by anyone; (iii) **identification** — the callsign has to go out on air; and (iv) in Singapore, **each frequency needs IMDA's written consent**, and the emission list was written for voice and Morse, not LoRa.

## The math
### Level 1 — ERP for the amateur limit
Both IMDA and the FCC compute ERP as transmitter PEP × antenna gain relative to a half-wave dipole ($G_{dBd} = G_{dBi} - 2.15$) [2 §4.5.3][3 97.313(i)]. For constant-envelope LoRa, PEP = average power.
$$\mathrm{ERP_{dBm}} = P_{dBm} - L_{cable} + G_{dBi} - 2.15, \qquad \mathrm{ERP_W} = 10^{(\mathrm{ERP_{dBm}}-30)/10}.$$

### Level 2 — callsign overhead in a telemetry stream
Putting the callsign (e.g. `9V1ABC`, 6 bytes; ~8 bytes with a separator/SSID) in every packet adds 8 bytes to an $N$-byte payload. For a 48-byte frame at SF7/125 kHz that is 48 → 56 bytes, which raises the time-on-air from 97.5 to 107.8 ms, about +10 % (`tools/verify/lora_toa.py`, SX126x formula; the preamble and header are fixed overhead, so the relative cost falls as $N$ grows). Sending it only every few seconds saves little and makes "beginning and end of each transmission" (Singapore) harder to argue, so **a callsign in every packet is the safe design**.

### Level 3 — which Part 97 emission class is LoRa?
Part 97 defines SS as "bandwidth-expansion modulation" with ITU emission designators whose 2nd and 3rd symbols are X (97.3). LoRa spreads each symbol over a bandwidth $BW$ much larger than its symbol rate $BW/2^{SF}$ (spreading factor $2^{SF}$, see [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)), so it is physically a bandwidth-expansion modulation → SS. Equipment certifications of LoRa devices often use frequency-modulation data designators (e.g. "F1D"-type), which would make it a data emission with the 100 kHz 70 cm cap. The rules do not resolve this; the practical consequence is: **≤ 10 W PEP if SS; ≤ 100 kHz occupied bandwidth if data**. Designing for both (≤ 10 W and BW 62.5 kHz) removes the question; 125 kHz at ≤ 10 W relies on the SS reading.

## Singapore amateur licence in detail
| Item | Rule | Source |
|---|---|---|
| Classes | General; Restricted (VHF/UHF bands only); Temporary (visitors, 3 months, callsign 9V1/homecall, apply 3 weeks ahead) | reg 37 [1]; Handbook §3.3 [2] |
| Who | natural persons only; not for employees' use; age ≥ 16; applicants < 21 countersigned; licensees 16–21 supervised by an IMDA-approved qualified person | regs 37(2), 38 [1] |
| Exam (RAE) | run by SARTS for IMDA. Section I: 35 MCQ, 1 h (operating rules, procedures, interference, propagation/antennas). Section II: 60 MCQ, 1 h 45 min (theory, receivers, transmitters, propagation, measurements, digital modes incl. APRS, SDR, duty cycle). Pass mark 60 % per section. Section I alone → Restricted; I + II → General | Handbook §2.6–2.7, §3.3 [2] |
| Exemption | holders of a valid foreign amateur licence or acceptable qualification may be exempted from the exam | reg 39(1)(b); Handbook §2.3 [2] |
| Fees | exam S$20 (full-time students) / S$40; licence S$50 Restricted / S$100 General per 5 years; temporary S$25 / S$50; frequency fees waived | reg 39(2); Handbook §2.5, §3.5, §4.4 [2] |
| Equipment | must be approved by IMDA — do not buy/install before approval; changes of location, equipment, mast or antenna need prior approval | Handbook §3.4.1(d); reg 40(e) [1][2] |
| Callsign | prefix 9V1; sent at beginning and end of each transmission/period of transmission | reg 40(d); Handbook §4.8 [2] |
| Content | plain language; licensee's experiments or personal (non-business) affairs; no news, advertising, business, pecuniary or third-party messages; only to amateur stations unless IMDA permits in writing | reg 42 [1]; Handbook §4.7 [2] |
| Encryption | prohibited | reg 41 [1]; Handbook §4.6.1(g) [2] |
| Operation | only at approved locations; by the licensee, or other IMDA-licensed amateurs in the licensee's presence, or (training institution) members in the licensee's presence; listen before transmitting; no uninterrupted transmission > 10 min | reg 40; Handbook §4.6.1(b), §4.7.1, §4.7.6 [2] |
| Logbook | date/time, callsigns, test transmissions, band and emission; signed; kept 2 years (Handbook) — Regulations say 12 months | Handbook §4.10; reg 40(g) |
| Interference | adjust into a dummy load; suppress harmonics/spurious; test and log that the station causes no harmful interference | Handbook §4.11 [2] |
| Portable/mobile | /P or /M suffix; ≤ 10 W ERP; only in Singapore; not simultaneously with the home station | Handbook §4.13 [2] |

**Band and power table (Handbook Appendix 1 [2])** — VHF/UHF/microwave rows:

| Band (MHz) | Power | Footnotes |
|---|---|---|
| 144–146 | 25 W PEP | 2 (shared), 5 (prior written consent) |
| **430–440** | **10 W ERP** | **1 (secondary), 2 (shared), 5 (prior written consent)** |
| 1240–1300, 2400–2450, 5650–5850, 10000–10500 | subject to licensing conditions | 1, 2, 3 (spot frequencies on written application), 5 |
| 24000–24050 | subject to licensing conditions | 2, 5 |
| 24050–24250 | subject to licensing conditions | 1, 2, 3, 5 |
| 5700–5800, 10050–10450 (pulse emissions K1A, K2A, L2A, K2E, L3E) | subject to licensing conditions | 1, 2, 3, 5 |

Note that Singapore's 70 cm allocation (430–440 MHz) **contains the whole 433.05–434.79 MHz SRD band** and the E22-400T33D's default 433.125 MHz. The Restricted-class limit is stated as 10 W ERP (§4.5.3); for General class the Appendix 1 figure for 430–440 MHz is also 10 W ERP.

**Is rocket/balloon telemetry permitted in Singapore?** No clause addresses telemetry directly. It is consistent with "the licensee's experiments" (reg 42(a)) and the syllabus includes APRS and digital modes; SARTS reports members organise radio balloon launches [5]. But three conditions need care: (1) the payload must be plain (published format, no encryption or scrambling); (2) the data must be the licensee's own experiment — a **team** project is fine if a licensed member is the responsible operator, but data sent on behalf of a company/sponsor would be "business" or "third-party"; (3) emission-class consent (see TL;DR). This is an interpretation; get IMDA's consent letter to say "telemetry from an experimental rocket/balloon".

## US amateur rules (47 CFR Part 97) for rocket telemetry
| Topic | Rule (current eCFR, amended through 91 FR 1431, 14 Jan 2026) [3] |
|---|---|
| Licence classes | Technician = Element 2 (35 Q, pass 26); General = 2 + 3; Extra = 2 + 3 + 4 (97.501, 97.503). Any person except a foreign-government representative may qualify (97.5(b)(1)); licence shows name, mailing and email address (97.23); 10-year term (97.25). |
| 70 cm privileges | Technician and above: 420–450 MHz in Region 2 (97.301(a)); secondary to US Government radiolocation (97.303(b)); no TX north of Line A in 420–430 MHz (97.303(m)). |
| Power | minimum necessary (97.313(a)); ≤ 1.5 kW PEP (97.313(b)); ≤ **50 W PEP on 70 cm in US270 areas incl. all of New Mexico, Arizona, Florida** (97.313(f)); **SS ≤ 10 W PEP** (97.313(j)). |
| 33 cm (902–928 MHz) | secondary to US Government, LMS (97.303(n)(1)); **no amateur TX in the White Sands box** 31°41′–34°30′ N, 104°11′–107°30′ W, nor from outside the US and its Region 2 insular areas (97.303(n)(2)); ≤ 50 W PEP within 241 km of WSMR (97.313(g)). |
| Emissions on 70 cm | MCW, phone, image, RTTY, data, SS, test (97.305(c)); data: specified codes ≤ 56 kbaud, unspecified codes allowed, **authorised bandwidth 100 kHz** (97.307(f)(6)); unspecified codes must not obscure meaning (97.309(b)); publicly documented techniques allowed (97.309(a)(4)). |
| SS | only between FCC-regulated points (or foreign stations where permitted); must not obscure meaning; must accept interference from other emissions; keep records convertible to the original information if a Regional Director requires (97.311). |
| One-way telemetry | authorised (97.111(b)(7)); broadcasting and other one-way traffic forbidden (97.113(b)). |
| Automatic control | allowed for RTTY/data on 6 m and shorter (97.221(b)) — a flight computer beacon qualifies when it transmits data. |
| Identification | callsign at the end of each communication and at least every 10 min, by CW, English phone, a RTTY emission using a specified digital code (when the traffic is RTTY/data), or image (97.119(a)–(b)). Space and telecommand stations exempt. |
| Content | no pecuniary interest/for hire; no messages encoded to obscure meaning; no false identification (97.113(a)). |
| Model craft telecommand | ≤ 1 W; no on-air ID needed if a label with callsign, name and address is on the transmitter; control signals are not "codes to obscure" (97.215). |
| Aircraft | amateur station aboard an aircraft needs the pilot-in-command's approval (97.11). |
| Space station | > 50 km altitude (97.3). Any licence class may be control operator; must be able to cease transmissions by telecommand; bands include 144–146 and **435–438 MHz**; written pre-space notification to the FCC Space Bureau within 30 days of launch-vehicle determination and ≥ 90 days before integration (97.207). |
| Foreign licensees | only if their government has a reciprocal arrangement with the US (97.107) — Singapore is not on the ARRL May 2023 bilateral list; Australia and Portugal are [4]. |

**Callsign ID with LoRa in practice.** Put the ASCII callsign in each packet (ASCII is a "specified digital code", 97.309(a)(3)) and document the packet format publicly (e.g. on the team website). Whether an ASCII field inside a LoRa SS emission satisfies 97.119(b)(3) literally is not settled; many teams add a periodic FSK/CW ID from a second transmitter. Choose the conservative option if the radio can do it (SX126x chips can transmit FSK/OOK; the EBYTE UART firmware cannot).

## Licensed (amateur) vs licence-exempt use for 433 MHz telemetry
| Aspect | Licence-exempt SRD (SG TS SRD 26a) | Amateur, Singapore | Amateur, USA |
|---|---|---|---|
| Power at 433 MHz | 10 mW e.r.p. | 10 W ERP (consent) | 1.5 kW PEP; 50 W in NM/AZ/FL; 10 W if SS |
| Duty cycle | ≤ 10 % | none stated (≤ 10 min continuous) | none |
| Who may operate | anyone | licensee (or licensees in his presence) | control operator with licence |
| Encryption | allowed | forbidden | forbidden (obscuring meaning) |
| ID | none | callsign start/end | every 10 min + end |
| Protection | none, accept interference | secondary, accept interference from primary | secondary to US Gov radiolocation |
| Equipment | must meet TS SRD | IMDA approval | no type approval for amateur gear |
| Paperwork | none | exam + licence + frequency consent | exam + licence |

**Rule of thumb**: licence-exempt 10 mW is technically enough for most line-of-sight flights ([Singapore page](singapore-imda-rules.md) worked example 2); the amateur route is worth it for margin (recovery after landing, polarisation nulls), for high-rate modes that break a 10 % duty cycle, and for learning.

## Worked examples
**1. Singapore ground uplink check.** E22-400T33D at 33 dBm, 1 dB feeder loss, 12 dBi Yagi: ERP = 33 − 1 + 12 − 2.15 = 41.85 dBm = 15.3 W > 10 W. Step down to 30 dBm → 7.7 W ERP (OK). (`tools/verify/reg_erp_compliance.py` reports 17.2 W / 8.6 W with 0.5 dB feeder.)

**2. Singapore rocket downlink.** 33 dBm, 0.5 dB loss, dipole: 32.5 dBm = 1.78 W ERP ≤ 10 W. Needs: licensee responsible, consent letter for the frequency (e.g. 433.125 MHz or IMDA's choice) and emission, callsign in each packet, CRYPT key = 0, logbook entry per flight/test.

**3. Spaceport America downlink, US Technician control operator.** 433.125 MHz, LoRa SF9/125 kHz, 2 W, dipole. As SS: 2 W ≤ 10 W PEP ✔ (97.313(j)); New Mexico 50 W PEP ✔ (97.313(f)); telemetry one-way ✔ (97.111(b)(7)); automatic control of data ✔ (97.221(b)); ID in every packet + end ✔ (97.119). As data: 125 kHz > 100 kHz ✘ → if you want to be safe under both readings, use 62.5 kHz bandwidth (halving BW improves sensitivity by ~3 dB but doubles time-on-air).

**4. The E220-900T30D at Spaceport America under Part 97?** Prohibited — 97.303(n)(2) bars amateur 33 cm transmissions in the WSMR box. Use Part 15 rules instead ([international rules](international-rules-for-competitions.md)).

**5. A space shot.** A student rocket designed to exceed 50 km carrying a 433 MHz amateur transmitter becomes a space station at 50 km: 433 MHz is outside the 435–438 MHz space segment (97.207(c)) → either switch to 435–438 MHz, stop transmitting above 50 km, or use a non-amateur authorisation; and file the pre-space notification ≥ 90 days before integration.

## Practical notes
- Get **at least two** team members licensed (Restricted class needs only Section I) so a licensee is always present.
- Keep a one-page **"station card"** in the ground-station box: licence copy, IMDA consent letter, frequencies/powers/antenna gains, logbook.
- Write the **packet format** up publicly (field list, scaling, CRC) — satisfies "publicly documented" (US) and "plain language" intent (SG).
- **Disable the EBYTE CRYPT scrambler** (registers 07H/08H = 0) under amateur operation; LoRa whitening/CRC are standard, published techniques and do not obscure meaning.
- Remember the licence covers **operation in Singapore at approved locations** — a Singapore licence is irrelevant at launches abroad.
- SARTS offers study guides and practice exams, and advice for visiting operators [5].

## Common mistakes & misconceptions
- **"A ham licence makes my 2 W module legal anywhere in 433 MHz."** Only inside the amateur band, under the licensee's control, at approved locations, with IMDA's written consent (SG), without encryption, with ID.
- **"Yagi gain doesn't count, the limit is transmitter power."** Singapore's 70 cm limit is ERP.
- **"The EBYTE 'encryption key' is fine because it's weak."** Any scheme intended to obscure meaning is prohibited on amateur bands (SG reg 41; US 97.113(a)(4)). Turn it off.
- **"Telemetry is one-way so it's broadcasting."** US 97.111(b)(7) explicitly authorises one-way telemetry; broadcasting (to the public, programme content) is different.
- **"My Singapore licence is valid at Spaceport America."** No US–Singapore reciprocal arrangement is listed [4]; get a US licence or use a US-licensed control operator.
- **"33 cm is a US ham band, so the 900 MHz module is covered at Spaceport America."** Not in the WSMR box (97.303(n)(2)).
- **"LoRa is just FSK."** Under Part 97 it is plausibly SS (10 W cap), and as data its 125 kHz bandwidth exceeds the 70 cm 100 kHz authorisation.

## How to simulate / verify
- `python3 tools/verify/reg_erp_compliance.py` — ERP of each power step with dipole/collinear/Yagi against 10 W ERP.
- Measure occupied bandwidth of the LoRa signal (99 % power bandwidth) with a spectrum analyser or SDR to know whether it is < 100 kHz.
- Decode your own downlink with an SDR (gr-lora_sdr) and a non-team receiver to confirm the payload is readable by third parties ("not obscured").

## Open questions / gaps
- IMDA's position on LoRa (data/chirp) emission on 70 cm and on callsign-in-packet as identification — not published; ask.
- Whether IMDA's "prior written consent" for 430–440 MHz is granted per frequency, per emission, per location (portable use at a field site) — procedure not documented beyond footnote 5.
- The authoritative FCC public notice listing reciprocal countries (ARRL's 2023 list used).
- FCC position on LoRa as SS vs data — no ruling found.

## Sources
1. *Telecommunications (Radio-communication) Regulations* (Rg 5), regs 2, 25, 37–46, 56–58 — Singapore Statutes Online, current as at 2026-09-27. https://sso.agc.gov.sg/SL/323-RG5 (legislation)
2. IMDA, *Amateur Radio Handbook*, Fifth Edition (21 November 2025), Parts B–D and Appendix 1. https://www.imda.gov.sg/-/media/imda/files/regulations-and-licensing/licensing/telecommunication/amateur-station/amateur-handbook.pdf (regulator handbook)
3. *47 CFR Part 97 — Amateur Radio Service*, eCFR current text (amendments through 91 FR 1431, 14 Jan 2026): §§97.3, 97.5, 97.11, 97.23, 97.25, 97.107, 97.109, 97.111, 97.113, 97.119, 97.207, 97.215, 97.221, 97.301, 97.303, 97.305, 97.307, 97.309, 97.311, 97.313, 97.501, 97.503. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97 (regulation)
4. ARRL, *Information for US Amateurs Traveling Abroad* (updated May 2023) — bilateral reciprocal list (includes Australia, Portugal; not Singapore); CEPT T/R 61-01 participants. https://www.arrl.org/files/file/VEs/International%20Operating%20May%202023.pdf (society guide)
5. SARTS, "Frequency Bands, Power and Classes of Emission" (Dec 2025) and Handbook Part E (contributed by SARTS). https://www.sarts.org.sg/frequency-bands-power-and-classes-of-emission/ (society web)
6. ARRL, "US270" (2026) — list of 50 W PEP 70 cm areas from 47 CFR 2.106 footnote US270. https://www.arrl.org/us270 (society summary of regulation)
7. Spaceport America location ≈ 32°59′ N, 106°58′ W (public geographic data; approximate). (reference)
