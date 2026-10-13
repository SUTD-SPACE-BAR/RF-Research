---
title: Amplifier stability and biasing (K, Δ, μ, stability circles, bias networks, sequencing)
domain: 06-rf-circuits
slug: amplifier-stability-and-biasing
tags: [stability, rollett, k-factor, mu-factor, stability-circles, msg, mag, bias-tee, bias-network, phemt, gan, sequencing, oscillation]
prerequisites:
  - ../03-transmission-lines-matching/s-parameters.md
  - ../03-transmission-lines-matching/smith-chart.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../05-analog-electronics/bjt-fundamentals-small-signal.md
  - ../05-analog-electronics/fets-mosfet-jfet-gaas-gan.md
related:
  - lna-design.md
  - power-amplifiers.md
  - rf-switches-attenuators-limiters.md
  - ../05-analog-electronics/feedback-and-stability.md
  - ../05-analog-electronics/oscillators.md
  - ../05-analog-electronics/power-supplies-for-rf-and-analog.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - ../13-pcb-rf-layout-emc/shielding-and-isolation.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
  - ../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Amplifier stability and biasing

## Questions this page answers
- What does "unconditionally stable" actually mean for an RF amplifier?
- How do I compute the Rollett K factor, |Δ| and the μ factor from S-parameters, and which test should I trust?
- Why is K > 1 not enough on its own?
- What is a stability circle and how do I read it on a Smith chart?
- My LNA simulates fine but oscillates on the bench — where do I look?
- Why is my transistor unstable at 100 MHz when I designed it for 1.5 GHz?
- Can a matching network make an unstable transistor stable?
- How big a resistor do I need to stabilise a transistor, and what does it cost in noise figure and gain?
- What is MSG vs MAG and why does the datasheet curve have a kink?
- How do I design a bias tee (choke and blocking capacitor values) for 433 MHz?
- How do I bias a BJT, an enhancement-mode pHEMT, or a depletion-mode GaAs/GaN FET?
- In what order must I apply gate and drain voltage to a GaN HEMT, and why?
- Why does a source via's inductance change stability and input match?

## TL;DR
- A linear two-port is **unconditionally stable** if no passive source ($|\Gamma_S|<1$) and no passive load ($|\Gamma_L|<1$) can make $|\Gamma_{in}|\ge1$ or $|\Gamma_{out}|\ge1$. Otherwise it is **conditionally (potentially) unstable**; it only oscillates if the actual terminations fall in the unstable region.
- Tests, all using $\Delta=S_{11}S_{22}-S_{12}S_{21}$: Rollett $K=\dfrac{1-|S_{11}|^2-|S_{22}|^2+|\Delta|^2}{2|S_{12}S_{21}|}>1$ **plus** $|\Delta|<1$ (or $B_1>0$); or the single Edwards–Sinsky test $\mu=\dfrac{1-|S_{11}|^2}{|S_{22}-\Delta S_{11}^*|+|S_{12}S_{21}|}>1$ [1][2][3]. $\mu$ is also a *margin*: it is the distance from the Smith-chart centre to the nearest load that causes instability. Verified numerically (all equivalent on 2×10⁵ random 2-ports) by `tools/verify/rfckt_stability.py`.
- **K > 1 alone is insufficient** (about 15 % of random gainy 2-ports in the check have K>1 yet are unstable). Also, all two-port tests assume the network has no hidden internal instability (no right-half-plane poles with its ports terminated) — multi-stage amplifiers can oscillate internally with K>1 at the terminals [4].
- Transistors are usually most unstable **below** the design band, where gain is highest: the ATF-54143 pHEMT (3 V, 60 mA) has μ = 0.04 at 100 MHz and 0.29 at 500 MHz, and only reaches μ>1 above ≈ 3.7 GHz (data-sheet S-parameters). Design stability from ≈ f/10 (or the lowest frequency with gain) up to $f_{max}$.
- **Lossless matching networks cannot change K** (Rollett invariant), and no reciprocal embedding changes MSG $=|S_{21}/S_{12}|$. Only **loss** (resistors, lossy ferrites) or **feedback** stabilises. Put resistive loading where it does least harm: out-of-band (RC/RL networks in the bias feeds) and at the output rather than the input of an LNA.
- A stabilising series gate resistor of 40 Ω raises the ATF-54143's NF_min at 1575 MHz from 0.35 dB to 1.7 dB; a frequency-selective network (gate 100 Ω + 100 nH shunt, drain 22 Ω series + 47 Ω/10 nH + 220 Ω/2 pF shunts) makes it unconditionally stable 0.1–10 GHz for only +0.08 dB NF_min at 1575 MHz (verified).
- Bias tee rules: choke reactance ≥ 5–10 × Z₀ (0.04–0.01 dB loss), block-cap reactance ≤ Z₀/10, both used **below their self-resonant frequency**; damp the choke–bypass resonance with a resistor.
- Depletion-mode GaAs pHEMT (pinch-off ≈ −1 V) and GaN HEMT (≈ −4 V) must have the **gate pinched off before drain voltage is applied**, and drain removed before gate on shutdown [5][6]. Enhancement-mode pHEMTs (ATF-54143, ≈ +0.6 V gate) bias like BJTs [7].

## Intuition (no math)
An amplifier is a machine that takes power from the DC supply and gives it to the signal. If a little of the output finds its way back to the input *in phase*, the amplifier re-amplifies it, and the loop runs away into an oscillation limited only by the transistor saturating. The feedback path does not have to be a wire you drew: it is the transistor's own internal capacitance (gate–drain, base–collector), the inductance of the via that grounds the source, the shared supply rail, radiation inside a shielding can, or simply a reflection from a mismatched load that bounces back through the device.

In S-parameter language, "re-amplified reflection" means a port reflection coefficient with magnitude greater than one: the port *returns more power than it receives*. That is a negative resistance. Connect a negative resistance to a resonator with less positive loss and you have an oscillator — which is exactly how microwave oscillators are designed on purpose (see [oscillators](../05-analog-electronics/oscillators.md)). Amplifier stability analysis is therefore the art of proving that no combination of source and load impedances you could ever connect makes either port look like a negative resistance.

Why are amplifiers usually unstable at *low* frequency? Because a transistor's gain rises as frequency falls (roughly 6 dB/octave for a BJT above its beta cutoff), while the matching networks you designed for 1.5 GHz are nearly transparent or wildly mismatched at 100 MHz. You end up with 30 dB of gain and random terminations — the perfect oscillator. At the other end, near $f_{max}$, small parasitic inductances (especially in the source/emitter lead) create feedback that turns the input into a negative resistance.

Two things cannot stabilise an amplifier: good intentions and lossless matching networks. A lossless network only *moves* impedances around the Smith chart; it cannot absorb the excess power. Resistance can. The engineering is to add resistance at frequencies and places where it hurts least — outside the band, on the output side of an LNA, in the bias feed.

Biasing is the other half of the page because the bias network is part of the RF circuit whether you like it or not. The choke that feeds the drain is a resonator at some frequency; the bypass capacitor becomes an inductor above its SRF; the gate bias resistor sets the input termination at low frequency. A good bias design fixes the DC operating point against temperature and part spread *and* presents benign (resistive) terminations at every frequency where the device has gain.

## The math

### Level 1 — definitions and the tests
Let the two-port have S-parameters $S_{ij}$ referenced to $Z_0=50\ \Omega$. With a load reflection coefficient $\Gamma_L$ on port 2 and a source $\Gamma_S$ on port 1 (see [s-parameters](../03-transmission-lines-matching/s-parameters.md)):
$$\Gamma_{in}=S_{11}+\frac{S_{12}S_{21}\Gamma_L}{1-S_{22}\Gamma_L}=\frac{S_{11}-\Delta\Gamma_L}{1-S_{22}\Gamma_L},\qquad
\Gamma_{out}=S_{22}+\frac{S_{12}S_{21}\Gamma_S}{1-S_{11}\Gamma_S}=\frac{S_{22}-\Delta\Gamma_S}{1-S_{11}\Gamma_S}$$
with the determinant $\Delta=S_{11}S_{22}-S_{12}S_{21}$ (dimensionless).

- **Unconditional stability:** $|\Gamma_{in}|<1$ and $|\Gamma_{out}|<1$ for *all* $|\Gamma_S|<1,\ |\Gamma_L|<1$.
- **Rollett stability factor** [1]: $K=\dfrac{1-|S_{11}|^2-|S_{22}|^2+|\Delta|^2}{2|S_{12}S_{21}|}$.
- **Necessary and sufficient pair:** $K>1$ and $|\Delta|<1$. Equivalent auxiliary conditions (any one suffices with $K>1$ [2, App. I]): $B_1=1+|S_{11}|^2-|S_{22}|^2-|\Delta|^2>0$, $B_2=1-|S_{11}|^2+|S_{22}|^2-|\Delta|^2>0$, $1-|S_{11}|^2>|S_{12}S_{21}|$, $1-|S_{22}|^2>|S_{12}S_{21}|$.
- **Edwards–Sinsky single tests** [2]:
$$\mu=\frac{1-|S_{11}|^2}{|S_{22}-\Delta S_{11}^*|+|S_{12}S_{21}|}>1\quad\Longleftrightarrow\quad \mu'=\frac{1-|S_{22}|^2}{|S_{11}-\Delta S_{22}^*|+|S_{12}S_{21}|}>1$$
- **Maximum stable gain** $\text{MSG}=|S_{21}|/|S_{12}|$ (used where $K<1$) and **maximum available gain** $\text{MAG}=\dfrac{|S_{21}|}{|S_{12}|}\left(K-\sqrt{K^2-1}\right)$ (defined only where $K>1$, sign of the root taken with $B_1>0$) [3 §12.3][8]. On data-sheet plots the "MSG/MAG" curve has a kink where $K$ crosses 1.

### Level 2 — derivations

**(a) Where $\Gamma_{in}$ comes from.** Write incident/reflected waves $a_i, b_i$ with $b=Sa$ and the load condition $a_2=\Gamma_L b_2$. Then $b_2=S_{21}a_1+S_{22}\Gamma_Lb_2\Rightarrow b_2=S_{21}a_1/(1-S_{22}\Gamma_L)$ and $b_1=S_{11}a_1+S_{12}\Gamma_Lb_2$, so $\Gamma_{in}=b_1/a_1$ as above. Instability at the input means $|\Gamma_{in}|>1$: the port reflects more power than is incident. For a source $\Gamma_S$ the loop gain around the input is $\Gamma_S\Gamma_{in}$; oscillation requires $\Gamma_S\Gamma_{in}=1$, which is only possible with $|\Gamma_S|<1$ if $|\Gamma_{in}|>1$.

**(b) The stability circle.** Set $|\Gamma_{in}|=1$: $|S_{11}-\Delta\Gamma_L|^2=|1-S_{22}\Gamma_L|^2$. Expanding,
$$\left(|S_{22}|^2-|\Delta|^2\right)|\Gamma_L|^2-2\,\mathrm{Re}\!\left[(S_{22}-\Delta S_{11}^*)\Gamma_L\right]+\left(1-|S_{11}|^2\right)=0 .$$
Dividing by $D_2=|S_{22}|^2-|\Delta|^2$ and completing the square gives a circle $|\Gamma_L-C_L|=r_L$ with
$$C_L=\frac{(S_{22}-\Delta S_{11}^*)^*}{|S_{22}|^2-|\Delta|^2},\qquad r_L=\frac{|S_{12}S_{21}|}{\big||S_{22}|^2-|\Delta|^2\big|}$$
where the radius simplifies using the identity (verify by expanding both sides)
$$|S_{22}-\Delta S_{11}^*|^2=|S_{12}S_{21}|^2+\left(1-|S_{11}|^2\right)\left(|S_{22}|^2-|\Delta|^2\right).$$
The source-plane circle follows by swapping indices 1↔2: $C_S=(S_{11}-\Delta S_{22}^*)^*/(|S_{11}|^2-|\Delta|^2)$, $r_S=|S_{12}S_{21}|/\big||S_{11}|^2-|\Delta|^2\big|$ [3 §12.2][8 §3.3]. The circle is only the *boundary*; to know which side is unstable test one point — $\Gamma_L=0$ gives $|\Gamma_{in}|=|S_{11}|$, so if $|S_{11}|<1$ the side containing the chart centre is stable.

**(c) Why K>1 and |Δ|<1.** Unconditional stability in the load plane means the unit disk lies entirely in the stable region: either the circle lies wholly outside the unit disk ($|C_L|-r_L>1$, when $D_2>0$) or it encloses the whole disk with the stable region inside ($r_L-|C_L|>1$, when $D_2<0$). Squaring $||C_L|-r_L|>1$ and substituting the identity above reduces, after algebra, to $1-|S_{11}|^2-|S_{22}|^2+|\Delta|^2>2|S_{12}S_{21}|$, i.e. $K>1$. But the squaring step loses the information about *which* of the two geometries applies (and whether the stable side is the disk side). $K>1$ says only "the circles do not cut the unit circle" — the unit disk might be entirely *unstable*. The auxiliary condition ($|\Delta|<1$ or $B_1>0$) resolves that ambiguity [2 §V].

**(d) μ as a geometric distance.** Edwards and Sinsky define $\mu$ as the distance from the origin of the $\Gamma_L$ plane to the nearest unstable point [2 §II]. Take $D_2>0$ with $|S_{11}|<1$ (origin stable, unstable region = inside the circle). The distance is $|C_L|-r_L=\dfrac{|S_{22}-\Delta S_{11}^*|-|S_{12}S_{21}|}{D_2}$. Multiply top and bottom by $|S_{22}-\Delta S_{11}^*|+|S_{12}S_{21}|$ and use the identity:
$$|C_L|-r_L=\frac{(1-|S_{11}|^2)D_2}{D_2\left(|S_{22}-\Delta S_{11}^*|+|S_{12}S_{21}|\right)}=\mu .$$
The case $D_2<0$ (unstable region outside the circle) gives $r_L-|C_L|$ and the same closed form. So **$\mu>1$ iff the unit disk contains no unstable load** — a single, unambiguous test — and $\mu$ is a margin: $\mu=1.2$ means even a load with $|\Gamma_L|=1.2$ (impossible passively) would be needed to cause input instability. A negative $\mu$ means even $\Gamma_L=0$ is unstable ($|S_{11}|>1$). The verification script confirms $\mu$ equals the brute-force distance to $10^{-12}$.

**(e) MAG and why it needs K>1.** A simultaneous conjugate match ($\Gamma_S=\Gamma_{in}^*$, $\Gamma_L=\Gamma_{out}^*$) has a passive solution only when $K>1$ and $|\Delta|<1$; substituting it into the transducer gain yields $\text{MAG}=|S_{21}/S_{12}|(K-\sqrt{K^2-1})$ (derivation in [lna-design](lna-design.md)). As $K\to1^+$, MAG → MSG $=|S_{21}/S_{12}|$. For $K<1$ there is no finite maximum — the gain can be made arbitrarily large near the stability circle, which is another way of saying "it will oscillate". MSG is then quoted as the gain obtainable after adding just enough resistive loading to bring K to 1.

### Level 3 — invariants, hidden instabilities and limits of the two-port view

**Rollett invariants.** Rollett showed that $K$ is invariant under lossless reciprocal embedding of the ports, and that $|S_{21}/S_{12}|$ (equivalently $|Y_{21}/Y_{12}|$ or $|Z_{21}/Z_{12}|$) is invariant under any reciprocal port embedding [1]. Consequences, confirmed numerically (checks I1–I3):
1. A lossless matching network changes the gain you *get* but not $K$: matching can never cure a conditionally stable device.
2. Resistive loading moves $K$ up but leaves MSG unchanged. When you stabilise exactly to $K=1$ with a resistor, MAG equals the unchanged MSG; the practical cost appears because you must stabilise at the *worst* frequency, leaving $K\gg1$ (low MAG) elsewhere, plus the resistor's noise and power loss.
3. Feedback (series or shunt, e.g. source inductance or a drain–gate RC) is not a port embedding — it changes the two-port itself and can raise or lower $K$.

**Hidden (internal) instability.** The $K/\mu$ tests assume the two-port is stable when its ports are terminated in the reference impedance, i.e. $S(s)$ has no right-half-plane poles. That is guaranteed for a measured single transistor (it was measured without oscillating) but not for a simulated multi-stage amplifier or MMIC, which can have internal loops (stage-to-stage, bias lines, odd-mode loops between paralleled devices). Platzker, Struble and Hetzler showed amplifiers and a ring oscillator that satisfy $K>1,|\Delta|<1$ at the external ports yet oscillate strongly [4]. Rigorous tools: the normalised determinant function (NDF) and return ratios of every active source; checking $K/\mu$ at *every* interstage reference plane; loop-gain (Middlebrook/Tian "stb") analysis in SPICE; pole–zero identification of the closed-loop response (e.g. STAN-type methods) [9].

**Paralleled devices** (PA combining, large-periphery transistors) have odd-mode instabilities: two halves oscillate in anti-phase, which is invisible at the combined ports because the combiner cancels it. Cure: odd-mode resistors between the halves (the same resistor that makes a Wilkinson isolated; see [couplers-dividers-combiners](couplers-dividers-combiners.md)).

**Large-signal instability.** S-parameters describe small signals around the quiescent point. Under drive, the operating point swings and new oscillations appear: parametric (sub-harmonic, $f_0/2$) oscillations in PAs and frequency multipliers, bias-line oscillations excited by rectified gate current, and "spurious under drive" [9]. These need harmonic-balance analysis with stability probing (see [harmonic balance](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)) and are one reason PAs get a separate treatment in [power-amplifiers](power-amplifiers.md).

**N-port generalisations** exist (structured-singular-value methods) for circuits where several ports can see arbitrary passive terminations [10].

**Frequency range of validity.** A stability check is only as good as the data: data-sheet tables often start at 100 MHz or 500 MHz, but the device has even more gain below. Extend with a device model (the ATF-54143 data sheet includes a Curtice model [7]) or measure. Above the last data point, parasitic package resonances dominate.

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical / note |
|---|---|---|---|
| Determinant | $\Delta=S_{11}S_{22}-S_{12}S_{21}$ | always | |
| Rollett K | $\frac{1-\lvert S_{11}\rvert^2-\lvert S_{22}\rvert^2+\lvert\Delta\rvert^2}{2\lvert S_{12}S_{21}\rvert}$ | linear 2-port, no RHP poles | need K>1 **and** $\lvert\Delta\rvert<1$ |
| μ (load plane) | $\frac{1-\lvert S_{11}\rvert^2}{\lvert S_{22}-\Delta S_{11}^*\rvert+\lvert S_{12}S_{21}\rvert}$ | same | μ>1 alone suffices; μ is a margin; target μ ≥ 1.05–1.2 over all frequencies with gain |
| Load stability circle | $C_L=\frac{(S_{22}-\Delta S_{11}^*)^*}{\lvert S_{22}\rvert^2-\lvert\Delta\rvert^2}$, $r_L=\frac{\lvert S_{12}S_{21}\rvert}{\lvert\lvert S_{22}\rvert^2-\lvert\Delta\rvert^2\rvert}$ | | locus of $\lvert\Gamma_{in}\rvert=1$ |
| Source stability circle | swap 1↔2 | | locus of $\lvert\Gamma_{out}\rvert=1$ |
| MSG | $\lvert S_{21}/S_{12}\rvert$ | K<1 | invariant to reciprocal embedding |
| MAG | $\lvert S_{21}/S_{12}\rvert(K-\sqrt{K^2-1})$ | K>1, B₁>0 | |
| Shunt choke loss | $\lvert S_{21}\rvert^2=\frac{4X^2}{4X^2+Z_0^2}$ | ideal L | X = 5 Z₀ → 0.043 dB, RL 20 dB; X = 10 Z₀ → 0.011 dB, RL 26 dB |
| Series block cap loss | $\lvert S_{21}\rvert^2=\frac{4}{4+(X/Z_0)^2}$ | ideal C | X = Z₀/10 → 0.011 dB |
| Choke–bypass resonance | $f=1/(2\pi\sqrt{LC})$ | | 100 nH + 100 nF → 1.6 MHz: damp it |
| Enclosure lowest mode | $f_{101}=\frac{c}{2}\sqrt{a^{-2}+b^{-2}}$ | empty metal box a×b (height smallest) | 50×30 mm can → 5.8 GHz; absorber or smaller cavities if near band [11] |
| Collector-feedback bias | $I_C=\frac{\beta(V_{CC}-V_{BE})}{R_B+(\beta+1)R_C}$ | BJT | 4:1 β spread → ≈ 2:1 Ic spread |
| Vbe tempco | ≈ −2 to −2.5 mV/°C | Si BJT | β rises ≈ +0.5 %/°C [12] |

Rules of thumb:
- Check stability from the lowest frequency where the device has gain (often < 50 MHz) up to $f_{max}$, **including all bias, matching and layout parasitics**, not just in band.
- For an LNA, stabilise on the output side and out-of-band; resistance at the input adds noise one-for-one. For a PA, stabilise on the input side (a series gate/base resistor or RC), because output resistance wastes output power.
- MSG/MAG plots are for the *device*; your amplifier's gain with a practical, stable, broadband-benign design is typically several dB lower.
- Every RF choke should be lossy (resistor or ferrite) at frequencies where it is not needed as a choke.

## Worked examples

### Example 1 — Is the ATF-54143 stable? (real data-sheet S-parameters)
Data: ATF-54143 enhancement-mode pHEMT at $V_{DS}=3$ V, $I_{DS}=60$ mA, reference planes at the leads, source grounded through four 0.5 mm vias [7]. At 500 MHz: $S_{11}=0.81\angle{-80.8°}$, $S_{21}=20.05\angle128.0°$, $S_{12}=0.03\angle52.4°$, $S_{22}=0.40\angle{-58.8°}$.

1. $S_{11}S_{22}=0.324\angle{-139.6°}=-0.2468-j0.2100$; $S_{12}S_{21}=0.6015\angle180.4°=-0.6015-j0.0042$.
2. $\Delta=(-0.2468+0.6015)+j(-0.2100+0.0042)=0.3547-j0.2058$, $|\Delta|=0.410$.
3. $K=\dfrac{1-0.6561-0.16+0.168}{2\times0.6015}=\dfrac{0.352}{1.203}=0.293$ → **potentially unstable**.
4. $\mu=0.286$: a load only 0.29 from the chart centre — e.g. $|\Gamma_L|\approx0.3$, a 1.9:1 VSWR in the wrong phase — can make the input oscillate.
5. MSG $=20.05/0.03=668$ → 28.25 dB, matching the data-sheet MSG/MAG column exactly.

The verification script repeats this for every row (0.1–10 GHz) and reproduces the data-sheet MSG/MAG column to 0.00 dB, which also proves the transcription. Summary:

| f (GHz) | K | μ | |Δ| | MSG/MAG (dB) |
|---|---|---|---|---|
| 0.1 | 0.066 | 0.036 | 0.555 | 34.4 (MSG) |
| 0.5 | 0.293 | 0.286 | 0.410 | 28.3 (MSG) |
| 1.0 | 0.513 | 0.424 | 0.462 | 24.1 (MSG) |
| 1.5 | 0.709 | 0.666 | 0.341 | 22.7 (MSG) |
| 2.0 | 0.811 | 0.766 | 0.354 | 20.9 (MSG) |
| 3.0 | 0.948 | 0.924 | 0.381 | 18.0 (MSG) |
| 4.0 | 1.060 | 1.098 | 0.372 | 14.9 (MAG) |
| 8.0 | 1.144 | 1.322 | 0.424 | 9.0 (MAG) |

Lesson: a device you want at 433 MHz or 1575 MHz is at its *least* stable in and below those bands.

### Example 2 — Stabilising it with a single resistor (and why you shouldn't)
Search (script section F) for the smallest resistive loading that gives $\mu>1$ everywhere from 0.4 to 10 GHz:

| Stabiliser | Value needed (0.4–10 GHz) | 0.1–10 GHz | Cost |
|---|---|---|---|
| Shunt R at drain | ≤ 19 Ω | impossible alone | MAG at 1575 MHz 22.4 → 16.6 dB; burns DC unless AC-coupled |
| Series R at drain | ≥ 159 Ω | impossible alone | 22.4 → 15.4 dB; drops output P1dB |
| Series R at gate | ≥ 40 Ω | ≥ 268 Ω | NF_min at 1575 MHz 0.35 → 1.72 dB, at 433 MHz 0.15 → 0.94 dB |

The gate resistor wrecks the noise figure because a series resistor at the input adds its thermal noise directly to the source's. The drain options avoid the noise but waste gain and power at all frequencies.

### Example 3 — Frequency-selective stabilisation
Instead, load the device only where it is dangerous (below ≈ 1 GHz and at high frequency):
- Gate: 100 Ω in series with 100 nH to RF ground — at 433 MHz this branch is $100+j272\ \Omega$ (light loading), at 50 MHz it is ≈ 100 Ω (heavy loading). In a real board this is the gate bias feed (choke + resistor + bypass).
- Drain: 22 Ω series; 47 Ω + 10 nH shunt (the drain bias feed with a damping resistor); 220 Ω + 2 pF shunt (high-frequency loading).

Result (noise-correlation-matrix analysis, script section F): μ_min = 1.20 over 0.1–10 GHz; MAG 25.7 dB at 433 MHz and 18.3 dB at 1575 MHz; NF_min 0.15 → 0.46 dB at 433 MHz and 0.35 → 0.43 dB at 1575 MHz. Compare the 40 Ω gate resistor (1.72 dB at 1575 MHz). This is the pattern used in the data-sheet application circuit, whose bias resistors (R3, R4) are described as the low-frequency termination that improves low-frequency stability [7].

### Example 4 — The source via you forgot
Adding series inductance in the common-source lead (script section G):

| Extra source L | μ_min (3–10 GHz) | |S₁₁| at 1575 MHz |
|---|---|---|
| 0 | 0.92 | 0.64 |
| 0.2 nH | 0.82 | 0.42 |
| 0.5 nH | 0.40 | 0.23 |
| 1.0 nH | −0.09 | 0.23 |

One 1.6 mm, 0.3 mm via to the bottom ground plane is ≈ 0.54 nH (Goldfarb–Pucel; up to ≈ 1 nH once pad and trace stubs are added; see [pcb parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)). Source inductance is double-edged: it improves the input match (the basis of inductive source degeneration in [lna-design](lna-design.md)) but pushes the high-frequency region toward instability. Use multiple vias right at the source pads (the data-sheet fixture uses four), and simulate the inductance you actually have.

### Example 5 — Bias tee for a 433 MHz amplifier
Target choke reactance 5 Z₀ = 250 Ω → $L=250/(2\pi\cdot433\text{ MHz})=92$ nH; choose 100 nH (272 Ω; shunt loss ≈ 0.036 dB). Check the inductor's SRF is well above 433 MHz and that its current rating exceeds the drain current: e.g. Coilcraft 0603CS-R10 (100 nH, SRF 1.4 GHz, DCR ≤ 0.58 Ω) [16] — the 0.58 Ω drops only 35 mV at 60 mA. Blocking capacitor for $X=5\ \Omega$: $C=1/(2\pi\cdot433\text{ MHz}\cdot5)=74$ pF; choose 100 pF C0G. With 0.3–0.5 nH ESL an 0402 100 pF part self-resonates around 0.7–0.9 GHz; below SRF its impedance is lower than the ideal value, so it is fine at 433 MHz. Bypass at the cold end of the choke: 100 pF (RF) in parallel with 100 nF (LF), with a 10 Ω resistor in series with the choke or with the 100 nF to damp the 100 nH–100 nF resonance at 1.6 MHz, where the transistor has > 30 dB gain.

### Example 6 — Biasing the enhancement-mode pHEMT from 5 V
Data-sheet passive bias [7]: gate divider fed *from the drain node* (so it is negative feedback), $V_{DD}=5$ V, $V_{DS}=3$ V, $I_{DS}=60$ mA, $V_{GS}=0.59$ V, divider current $I_{BB}=2$ mA:
$R_1=V_{GS}/I_{BB}=295\ \Omega$, $R_2=(V_{DS}-V_{GS})R_1/V_{GS}=1205\ \Omega$, $R_3=(V_{DD}-V_{DS})/(I_{DS}+I_{BB})=32.3\ \Omega$. A 10 kΩ gate series resistor limits gate current under overdrive.
Why the feedback matters: with $g_m\approx0.41$ S, a fixed gate voltage converts a 0.1 V threshold shift (the data sheet allows $V_{GS}$ 0.4–0.75 V for 60 mA) into ≈ 41 mA of drain-current change; the drain-fed divider cuts that to ≈ 11 mA, because $dI_D/dV_{th}=-g_m/(1+g_mR_3R_1/(R_1+R_2))$. For tighter control use the data sheet's PNP active bias (constant voltage across $R_3$), a current mirror, or an active bias controller.

### Example 7 — BJT collector-feedback bias
RF BJT at $V_{CE}=3$ V, $I_C=10$ mA from 5 V, $\beta=100$, $V_{BE}\approx0.8$ V: $R_C=(5-3)/(10.1\text{ mA})=198\ \Omega$ (use 200 Ω), $R_B=(3-0.8)/0.1\text{ mA}=22$ kΩ. For β = 50/100/200, $I_C$ = 6.5/10.0/13.6 mA; a plain base resistor from $V_{CC}$ would give 5/10/20 mA. RF BJT hFE spreads up to 3:1 between parts, and hFE differences do not show up in RF performance *if* $I_C$ and $V_{CE}$ are held constant — which is the job of the bias network [12].

### Example 8 — GaN HEMT turn-on / turn-off sequence
For a 28 V GaN-on-SiC HEMT PA (e.g. a 10–30 W discrete for 433 MHz or L-band):
1. With drain at 0 V, apply gate ≈ −5 V (beyond pinch-off, typically ≈ −4 V for GaN, ≈ −1 V for GaAs pHEMT [5]).
2. Apply $V_{DD}$ (28 V). Drain current stays near zero (device pinched off).
3. Raise $V_G$ slowly toward ≈ −3 V until $I_{DQ}$ reaches the target (e.g. Class AB). Expect slow drift from charge trapping for minutes after turn-on [5].
4. Apply RF.
Shutdown: RF off → gate back to pinch-off → drain off → gate to 0 V.
Why: a depletion-mode device at $V_{GS}=0$ is fully *on*; applying 28 V with no gate bias puts $I_{DSS}\times28$ V (tens of watts) into a small die — destroyed in milliseconds. The bias source must sink and source gate current (rectification under drive reverses it) and remain stable with large gate decoupling capacitance [6]. Controllers such as ADI's HMC920 integrate a negative charge pump (−2.5 V default), closed-loop $I_{DQ}$ regulation with ±4 mA gate drive, and power-up/down sequencing with over/under-current alarms [13].

## Practical notes
- **Where amplifiers really oscillate on the bench** (in rough order of frequency):
  1. *Bias/supply loops* (kHz–MHz): the transistor, choke, bypass and the regulator form a loop through the supply; oscillation shows as a fuzzy supply rail and sidebands around the carrier. Fix: series R or ferrite in the feed, electrolytic/tantalum with some ESR at the cold end, separate supplies/regulators per stage [12].
  2. *Low-frequency gain* (10–300 MHz): out-of-band terminations are random (a SAW filter or antenna is highly reflective out of band). Fix: resistive LF terminations in gate/drain feeds; high-pass matching networks (series C, shunt L) which reduce LF gain [7].
  3. *Bias-choke SRF* (0.5–3 GHz for SMD chokes): above SRF the "choke" is a capacitor and the bias line becomes a resonant stub. Fix: lossy chokes, λ/4 lines with a resistor at the cold end, or two chokes in series (small high-SRF one near the device).
  4. *High-frequency parasitics* (several GHz): source/emitter via inductance, package resonances. Fix: many vias, short ground returns, small resistive loading at the drain with a small capacitor.
  5. *Enclosure feedback*: the shield lid couples output to input; oscillation appears or changes when you touch or close the lid. Fix: partition walls, absorber, keep box modes out of band, reduce gain per compartment.
  6. *Test setup*: a spectrum analyser or VNA input is not 50 Ω far out of band; unterminated SMA ports; long DC leads. Always terminate unused ports and view 10 MHz–(3×f) on a spectrum analyser with no input signal.
- **Detecting oscillation:** DC current differing from expected; gain that changes when you touch the board; spurs in a spectrum-analyser sweep with no input; noise figure measurement that makes no sense. A near-field probe around the board finds the culprit quickly.
- **Gain blocks** (e.g. Mini-Circuits PGA-103+, 0.05–4 GHz, NF 0.5 dB at 0.4 GHz, 5 V at 97 mA [14]) are designed to be unconditionally stable in 50 Ω; the most common failure is layout (poor ground under the SOT-89, bias choke resonance).
- **Temperature:** a BJT at fixed $V_{BE}$ runs away (Vbe falls ≈ 2–2.5 mV/°C); GaN at fixed $V_G$ can drift either way depending on current density [5][6]. Use feedback or temperature-compensated bias for linear amplifiers.
- **Negative supplies:** a charge-pump inverter (e.g. an LTC1983 or TPS60403-class part) can generate −3 to −5 V for small GaAs/GaN devices; filter its switching ripple (tens–hundreds of kHz) thoroughly or it modulates the carrier.
- **Protection:** put a hardware interlock so the drain switch (a P-MOSFET load switch) cannot close unless the negative gate rail is present and below pinch-off. A fuse or current limit on the drain protects against a gate-open fault.
- **Bench bring-up of an amplifier** (failure modes and a safe test set-up with pads): [17 bring-up playbook § G](../17-test-measurement/rf-bring-up-debug-playbook.md#g-amplifier-and-rf-switch-bring-up-failure-modes-and-a-safe-test-set-up).

## Common mistakes & misconceptions
- *"K > 1 means stable."* No — also need $|\Delta|<1$ (or $B_1>0$), or use μ>1 [2]. The script finds many K>1 counter-examples.
- *"It is stable in band, so it is stable."* Most bench oscillations are out of band, especially below the band where device gain is highest.
- *"My matching network will stabilise it."* Lossless networks leave K unchanged (Rollett invariance); only loss or feedback changes stability.
- *"The amplifier passed the K test in simulation, so a 3-stage MMIC is stable."* Terminal K cannot see internal loops [4]; check each interstage, or use NDF/loop-gain/pole-zero analysis.
- *"The stability circle is the unstable region."* It is only the boundary; which side is unstable must be tested (e.g. with $|S_{11}|$ at $\Gamma_L=0$).
- *"The choke is 1 µH so it blocks RF."* Above its SRF it is a capacitor: a Coilcraft 0805CS-102 (1 µH) has SRF ≈ 180 MHz [16], so at 433 MHz it is a ≈ capacitive shunt. Bigger is not better for chokes.
- *"Apply drain voltage and then adjust the gate"* on a depletion-mode GaN/GaAs device — destroys it. Gate first (pinched off), then drain.
- *"MSG is the gain I will get."* MSG is an upper bound after ideal stabilisation to K=1; practical, broadband-stable designs give less.
- *"S-parameter stability also covers large-signal operation."* It does not; PAs can oscillate parametrically under drive [9].
- *"A resistor anywhere will do."* A series input resistor on an LNA adds NF almost dB-for-dB of its loss; put stabilisation at the output or out of band.

## How to simulate / verify
- **scikit-rf:** `Network.stability` gives K; `Network.stability_circle(target_port)` gives circles; `Network.max_stable_gain`, `max_gain`. The script `tools/verify/rfckt_stability.py` implements K, μ, μ', B₁, circles, MSG/MAG from scratch, checks them against brute force and skrf, reproduces the ATF-54143 data-sheet MSG/MAG column, and runs the stabilisation, via-inductance and bias examples above. Noise impacts use `tools/verify/rfckt_noise2port.py` (Hillbrand–Russer chain noise-correlation matrices, self-tested).
- **Load the real file:** most vendors supply Touchstone `.s2p` files (the ATF-54143 data is typed into `tools/verify/rfckt_atf54143_data.py`). Always sweep from the lowest frequency available to beyond $f_{max}$.
- **SPICE / Qucs-S:** loop-gain (Tian/Middlebrook) probes for bias-loop stability; transient start-up simulation with a kick to see whether oscillation builds up. See [SPICE](../16-simulation-tools/spice-circuit-simulation.md).
- **Harmonic balance** for large-signal stability of PAs.
- **Bench:** NanoVNA/LibreVNA to measure S-parameters of the built amplifier (use an attenuator on port 2 if the output could overload the VNA) and compute μ in Python; spectrum analyser with input terminated to hunt oscillations; vary source/load with a "stub stretcher" or random cable lengths to probe conditional stability.

## Open questions / gaps
- Gonzalez and Pozar present the unconditional-stability derivation slightly differently (Pozar uses $K>1,|\Delta|<1$; Gonzalez also discusses $B_1$); both are equivalent to μ>1 per Edwards–Sinsky, confirmed numerically here. No real contradiction, only presentation.
- Edwards–Sinsky state K>1 is "only a necessary condition"; strictly K>1 is necessary *and* insufficient — consistent with this page.
- Large-signal (parametric) stability is only outlined; a dedicated page on nonlinear stability analysis (Suárez & Quéré) would be valuable.
- The frequency-selective stabiliser in Example 3 was found by a coarse grid search, not optimised; it demonstrates the method rather than a production design. Real designs must include component parasitics (inductor SRF, capacitor ESL).

## Sources
1. J. M. Rollett, "Stability and power-gain invariants of linear twoports," *IRE Trans. Circuit Theory*, CT-9, pp. 29–32, Mar. 1962. Origin of K and of the embedding invariants. (peer-reviewed; cited via [2] and [3])
2. M. L. Edwards, J. H. Sinsky, "A new criterion for linear 2-port stability using a single geometrically derived parameter," *IEEE Trans. MTT*, 40(12), pp. 2303–2311, Dec. 1992. μ, μ′ definitions and proofs; auxiliary-condition equivalence (App. I); K geometry (§V). Read in full. (peer-reviewed)
3. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012, §12.1–12.3 (two-port power gains, stability circles, K–Δ test, μ test, MAG). (textbook)
4. M. Platzker, W. Struble, K. T. Hetzler, "Instabilities diagnosis and the role of K in microwave circuits," *IEEE MTT-S International Microwave Symposium Digest*, Atlanta, June 1993. K test rigorous only without RHP poles; counter-examples; NDF. (peer-reviewed; abstract-level via Semantic Scholar/IEEE listing)
5. TriQuint Semiconductor (now Qorvo), "Biasing GaN on SiC HEMT devices," application note. Pinch-off ≈ −1 V pHEMT / ≈ −4 V GaN, gate-leakage targets, 3 W/mm dissipation, current drift. https://www.rfmw.com/data/triquint_biasing_gan_on_sic_hemt_devices.pdf (app note)
6. J. Bellantoni, "Bias techniques for GaN and pHEMT depletion mode devices," TriQuint, rev. 3, 2014. Bias-circuit requirements (bilateral gate current, capacitive-load stability, temperature slope). (app note)
7. Avago Technologies, *ATF-54143 Low Noise Enhancement Mode Pseudomorphic HEMT* data sheet (S- and noise-parameter tables at 3 V/60 mA; absolute maximum ratings; passive/active bias equations; LF termination resistors; Curtice model). https://www.modelithics.com/models/Vendor/Avago/ATF-54143.pdf (datasheet)
8. G. Gonzalez, *Microwave Transistor Amplifiers: Analysis and Design*, 2nd ed., Prentice Hall, 1997, ch. 3 (stability, circles, MAG). (textbook)
9. A. Suárez, R. Quéré, *Stability Analysis of Nonlinear Microwave Circuits*, Artech House, 2003 (large-signal and parametric instability, pole–zero identification). (textbook; cited for scope)
10. "Unconditional stability analysis of N-port networks based on structured singular value computation," arXiv:2406.19342, 2024. (preprint)
11. Rectangular cavity TE₁₀₁ resonance: Pozar [3] §6.3. (textbook)
12. I. Rosu (VA3IUL), "Bias circuits for RF devices," qsl.net/va3iul. Vbe and β temperature coefficients, hFE spread, BJT/FET bias topologies, bias-loop oscillation. (compiled engineering notes — secondary)
13. Analog Devices, *HMC920LP5E Active Bias Controller* data sheet and AN-1363. https://www.analog.com/media/en/technical-documentation/data-sheets/hmc920.pdf (datasheet; features via vendor summaries)
14. Mini-Circuits, *PGA-103+* data sheet rev. C. https://www.minicircuits.com/pdfs/PGA-103+.pdf (datasheet)
15. Mini-Circuits blog, "RF/microwave bias tees from theory to practice" (choke ≥ 10×50 Ω, block ≤ 50/10 Ω, SRF rules). https://blog.minicircuits.com/rf-microwave-bias-tee-basics/ (app note)
16. Coilcraft 0603CS and 0805CS ceramic chip inductor data (0603CS-R10: 100 nH, SRF 1.4 GHz, DCR 0.58 Ω max; 0805CS-102: 1 µH, SRF 180 MHz). https://www.coilcraft.com/en-us/products/rf/ceramic-core-chip-inductors/ (datasheet; values via vendor product pages)
