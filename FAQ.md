# FAQ — every question the knowledge base answers

Auto-generated from each page's "Questions this page answers" section by `tools/build_index.py`. Grouped by domain → page.

## 00-math-foundations — the maths toolkit

### [RF concepts for beginners — a Level-1 tour with high-school maths (what RF is, frequency and wavelength, dB, impedance and 50 Ω, antennas, modulation and bandwidth, noise, sharing the air, penetration, and why RF is non-ionising)](kb/00-math-foundations/rf-concepts-for-beginners.md)
- What actually is "RF", and how is a radio wave related to light?
- How do I get the wavelength from the frequency, and why does it matter for antenna size?
- What is a decibel, and why do RF people add dB instead of multiplying?
- What does dBm mean, and how many watts is 33 dBm?
- What is impedance, and why is almost everything in RF 50 Ω?
- What does an antenna really do — does a bigger antenna "amplify" the signal?
- What is bandwidth, and why does a faster data rate need more of it?
- What is noise, and why can't a receiver hear an arbitrarily weak signal?
- With millions of radio signals in the air at once, why don't they all interfere?
- Do higher frequencies penetrate walls better?
- Is radio-frequency radiation "radiation" like X-rays? Can my LoRa radio or a 5G mast damage DNA?
- What is the one-paragraph intuition behind each of these that I should keep in my head?

### [RF learning roadmap — from zero to graduate level for radios, radars, LoRa links and antennas (stages, books by audience, free courses, video channels, first instruments, what to build, and the KB reading order)](kb/00-math-foundations/rf-learning-roadmap.md)
- Where do I start learning RF if I want to build radios, radars, LoRa links and antennas?
- Should I read Pozar first, or build something first?
- Which RF book is right for me — Pozar, Balanis, the ARRL Handbook, EMRFD, Bowick, Razavi, Lee, Skolnik, Richards, Mailloux, Lyons or PySDR?
- Which chapters of Pozar should a builder read first, and which can wait?
- Are there good free RF courses and free textbooks?
- Which YouTube channels are worth watching for RF and test equipment?
- What instruments should I buy first, and in what order?
- I come from physics / software / ham radio / embedded avionics — where is my entry point?
- In what order should I read this knowledge base's domains?
- How do I know I am ready to move to the next stage? Is there a "LeetCode for RF"?

### [Maths roadmap for RF, antennas, radar and analog design](kb/00-math-foundations/math-roadmap-for-rf.md)
- What maths do I actually need to design radios, antennas, radars, phased arrays and analog circuits?
- In what order should I learn it, starting from high-school algebra?
- Which maths does each RF topic depend on (link budgets, matching, filters, LNAs, antennas, arrays, FMCW radar, LoRa)?
- How can I check whether I'm ready for a given topic?
- What free courses and books cover each stage?
- What can I skip (for now)?

### [Decibels and logarithmic units](kb/00-math-foundations/decibels-and-log-units.md)
- Why do we use 10 log for power but 20 log for voltage?
- What exactly is a dBm, and how many volts is 0 dBm (or 33 dBm) into 50 Ω?
- Is 30 dBm + 30 dBm = 60 dBm? How do I add two signals given in dBm?
- When do two signals add to +3 dB and when to +6 dB?
- What is the difference between dB, dBm, dBW, dBi, dBd, dBic, dBc, dBc/Hz, dBFS, dB-Hz, dBsm and dBK?
- How do I convert dBµV/m field strength into received power in dBm?
- Why is thermal noise −174 dBm/Hz, and why does the spectrum-analyser noise floor move when I change RBW but my carrier does not?
- Why does 1 % sometimes mean −40 dB and sometimes 0.04 dB?
- What is a neper and why does it appear in transmission-line attenuation?
- How can I do dB arithmetic in my head?

### [Complex numbers and phasors](kb/00-math-foundations/complex-numbers-and-phasors.md)
- What is $j$, and why do engineers use $j$ instead of $i$?
- What does Euler's formula $e^{j\theta}=\cos\theta+j\sin\theta$ actually mean, and why is it everywhere in RF?
- What is a phasor, and why can I replace $d/dt$ with $j\omega$?
- Why is impedance a complex number? Is the imaginary part "not real"?
- What is the difference between RMS, peak, peak-to-peak, average power and PEP?
- Why is there a ½ in $P=\tfrac12\mathrm{Re}\{VI^*\}$ in some books but not in others?
- What is reactive power and does it heat anything?
- What is an analytic signal and a complex envelope?
- What is a negative frequency, and why does my SDR's FFT show signals at negative frequencies?
- Why does `atan(y/x)` give the wrong phase angle?

### [Fourier series and the Fourier transform](kb/00-math-foundations/fourier-series-and-transform.md)
- What does it mean that "every signal is a sum of sine waves"?
- Why does a square wave contain only odd harmonics, and how big are they?
- Why do fast clock edges cause EMI hundreds of MHz above the clock frequency?
- Could my flight computer's 24 MHz or 40 MHz clock interfere with my 433/900 MHz LoRa receiver?
- What is a sinc function and why does it appear everywhere?
- What is the time–bandwidth product, and why can't a signal be both short and narrowband?
- What do Parseval's theorem, the convolution theorem and the modulation theorem say, in plain words?
- What does the spectrum of a radar pulse train look like?
- What does the spectrum of a chirp (radar or LoRa) look like, and why is its bandwidth B regardless of length?
- How is the DFT/FFT related to the "real" Fourier transform?
- Why is an antenna's far-field pattern the Fourier transform of its aperture?

### [Laplace transform, transfer functions and Bode plots](kb/00-math-foundations/laplace-transfer-functions-bode.md)
- What is the Laplace variable $s$, and how is it related to $j\omega$?
- What are poles and zeros *physically*, and why does their position tell me whether a circuit rings, decays or oscillates?
- How do I sketch a Bode plot by hand?
- What are damping ratio, natural frequency and Q, and how do they relate to overshoot and peaking?
- What do phase margin and gain margin mean, and why do amplifiers and PLLs oscillate?
- What is a minimum-phase system, and why does a delay or a right-half-plane zero make control harder?
- What is group delay, and why does a narrow filter delay my signal?
- Why is rise time × bandwidth ≈ 0.35?

### [Linear systems, convolution, causality and Kramers–Kronig](kb/00-math-foundations/linear-systems-convolution.md)
- What makes a system "linear" and "time-invariant", and why do we care?
- What is an impulse response, and what does convolution actually compute?
- Why is filtering a multiplication in frequency but a convolution in time?
- What does "causal" mean mathematically, and why can't I build an ideal brick-wall filter?
- What is the Hilbert transform and where does it show up in RF?
- What are the Kramers–Kronig relations, and why must a lossy PCB dielectric have a frequency-dependent εr?
- Why does my EM or SI simulator ask for a "Djordjevic–Sarkar" or "wideband Debye" material model instead of just εr and tan δ?
- What is the difference between phase delay and group delay, and what is dispersion?
- Is a mixer a linear system?

### [Vector calculus for electromagnetics](kb/00-math-foundations/vector-calculus-for-em.md)
- What do gradient, divergence, curl and the Laplacian mean physically?
- How do I read Maxwell's equations in words?
- What do the divergence (Gauss) theorem and Stokes' theorem let me do in practice?
- Why do antenna books use spherical coordinates, and why do the formulas look so messy there?
- Why can't I take the Laplacian of each component of a vector in spherical coordinates?
- What is a "phasor vector field", and why does $\nabla\times\mathbf E=-j\omega\mu\mathbf H$ have a $j$ in it?
- Where does $e^{-jkr}/r$ come from, and what is the Helmholtz equation?
- How far from an antenna does the near field stop mattering?

### [Probability, random processes and power spectral density](kb/00-math-foundations/probability-random-processes-and-psd.md)
- Why is thermal noise Gaussian?
- Why do noise *powers* add but noise *voltages* don't?
- What does "nV/√Hz" mean, and how do I turn a noise density into an rms voltage?
- What is a power spectral density, and what does the Wiener–Khinchin theorem say?
- What is "white" noise and why is it an idealisation?
- What is equivalent noise bandwidth (ENBW), and why is it not the −3 dB bandwidth?
- What are the Rayleigh and Rician distributions, and how much fade margin does my link need?
- What is the Q-function / erfc, and how does it give bit-error rates?
- Why does averaging make a spectrum-analyser noise trace smoother, and by how much?
- How do I set a detection threshold for a given false-alarm rate?
- Where does shot noise's $2qI$ come from?

### [Differential equations for circuits and waves](kb/00-math-foundations/differential-equations-circuits-waves.md)
- What is a time constant, and why do we say a capacitor is "charged" after 5τ?
- Why does charging a capacitor from a fixed voltage always waste half the energy, whatever the resistance?
- How do I tell whether an RLC circuit will ring, and how fast the ringing dies?
- What are damping ratio ζ, natural frequency ωₙ and Q, and how are they related?
- Why do my power rails ring after a load step, and how do I damp them?
- Where does the wave equation come from, and why is $f(x-vt)$ a solution?
- How do telegrapher's equations turn into waves on a cable?
- What is separation of variables, and how does it give waveguide modes and cutoff frequencies?
- Why is skin depth a "diffusion" length?

### [Special functions in RF — sinc, Bessel, jinc, Fresnel, erf, Chebyshev, Legendre](kb/00-math-foundations/special-functions-bessel-sinc.md)
- What is a sinc function and why does it keep appearing (pulses, apertures, FFT bins)?
- Why does an FM signal have sidebands with Bessel-function amplitudes, and what is Carson's rule?
- How can I calibrate FM deviation with a spectrum analyser (the "Bessel null" method)?
- Why is a dish antenna's beam described by a "jinc"/Airy pattern with −17.6 dB sidelobes?
- What are Fresnel integrals and how do they give knife-edge diffraction loss (6 dB at grazing)?
- What is the Q-function/erfc and where does it appear?
- Why do Chebyshev polynomials appear in both filters and antenna arrays?
- What are Legendre functions and spherical Bessel functions used for?
- Where does the modified Bessel function $I_0$ show up (Rician fading, Kaiser windows)?

### [Numerical methods overview — from root-finding to FDTD, MoM and FEM](kb/00-math-foundations/numerical-methods-overview.md)
- How do calculators and simulators solve equations that have no closed form?
- When should I use bisection, Newton or Brent's method?
- Which numerical integration rule should I use, and why is Gauss–Legendre so accurate?
- Why is the FFT fast, and what does it actually compute?
- Why does my transient simulation blow up or need tiny time steps (stiffness, stability)?
- What are FDTD, MoM and FEM, how do they differ, and which one fits antennas, PCBs, cavities?
- What is the Courant (CFL) condition and "cells per wavelength"?
- How do I know a simulation result is right (convergence and validation)?

### [Matrices and linear algebra for networks, arrays and calibration](kb/00-math-foundations/matrices-and-linear-algebra-for-networks.md)
- How does a circuit simulator actually solve a circuit (nodal analysis, MNA)?
- What do Z, Y, ABCD and S matrices mean, and how do I convert between them?
- Why is a reciprocal network's S-matrix symmetric, and a lossless one's unitary?
- What do eigenvalues tell me about a circuit (natural frequencies, coupled resonators)?
- Why does MIMO capacity involve the singular value decomposition?
- How do adaptive beamformers use covariance matrices and eigenvectors?
- How does VNA calibration become a linear-equation solve?
- What is least squares, and why do calibration fits go numerically wrong (conditioning)?

### [The z-transform and discrete-time systems — ROC, poles and zeros, stability, Laplace↔z mappings, difference equations](kb/00-math-foundations/z-transform-and-discrete-time-systems.md)
- What is the z-transform, and what does $z^{-1}$ mean physically?
- How do I turn a difference equation (the code in my firmware loop) into a transfer function, and back?
- What is the region of convergence (ROC), and why can two different sequences have the same $X(z)$?
- Why must the poles of a digital filter be inside the unit circle?
- How do I get the frequency response of a digital filter from $H(z)$?
- How is the z-plane related to the s-plane, and what is $z=e^{sT}$?
- Bilinear transform or impulse invariance — which should I use to digitise an analogue filter, and why does the bilinear transform need prewarping?
- How do I compute the inverse z-transform (partial fractions)?
- How much lag and how much noise reduction does a simple exponential moving average give my barometer?
- How do I model a digital PLL, a sigma-delta modulator or a CIC filter with $H(z)$?
- How can I tell quickly whether a second-order recursion is stable?

### [Estimation theory — bias, variance, least squares, ML, MAP/MMSE, Fisher information and the Cramér–Rao bound (with frequency, phase and time-delay CRBs)](kb/00-math-foundations/estimation-theory-ml-map-crb.md)
- What makes an estimator "good" — bias, variance, MSE, consistency, efficiency?
- Why is the "unbiased" variance estimator (divide by N−1) not the one with the smallest error?
- What is least squares, and when is it the best possible estimator?
- What is maximum likelihood, and how is it related to least squares and to a matched filter?
- What is the difference between MAP and MMSE, and how does a prior change the answer?
- What is the Fisher information and the Cramér–Rao bound (CRB), and how do I derive it?
- What is the best possible accuracy for estimating a tone's frequency or phase in noise?
- What sets the best possible ranging accuracy for a radar, a GNSS receiver or a LoRa timestamp, and what is "rms bandwidth"?
- Why does carrier-phase GNSS reach millimetres when code ranging gives metres?
- Why do estimators suddenly get much worse than the CRB at low SNR (the threshold effect)?
- How well can I estimate vertical velocity from barometer samples alone?

### [Kalman filtering and state estimation — derivation, Q/R tuning, α-β(-γ) trackers, complementary filters, EKF, UKF, NEES/NIS consistency, baro+IMU rocket fusion and GNSS/INS coupling](kb/00-math-foundations/kalman-filter-and-state-estimation.md)
- What does a Kalman filter actually do, and where do its equations come from?
- How do I choose the process noise Q and measurement noise R, and what happens if I get them wrong?
- How do I know whether my filter is working (NEES, NIS, innovation tests)?
- What is the Joseph form, and why do flight codes use it?
- Is an α-β filter just a Kalman filter, and how do I pick α and β?
- Is a complementary filter a Kalman filter in disguise?
- How do I fuse a barometer and an accelerometer on a rocket to get velocity and detect apogee?
- EKF or UKF — which should I use for a nonlinear problem (drag, ranges and angles)?
- What is the difference between loosely, tightly and deeply coupled GNSS/INS fusion?
- Why did my filter "lock up" and ignore its measurements, or become noisy and jumpy?

### [Canonical values and conventions — the numbers and sign/unit choices every KB page must agree on](kb/00-math-foundations/canonical-values-and-conventions.md)
- Which value of kT, η0, skin depth or FSPL constant should I use so that my answer matches the rest of the knowledge base?
- Why do two pages give answers 3 dB apart for the same thing, and which one is right?
- Is "SNR" in a link or radar budget E/N0 or 2E/N0?
- Is ADC processing gain 10 log(fs/2B) or 10 log(fs/B)?
- What sign convention does the KB use for phasors and for right-hand circular polarisation?
- Is a gain figure in dBi, dBd or dBic, and is a Singapore power limit ERP or EIRP?
- When do I use 10 log and when 20 log, and are the phasors peak or RMS?
- What are the Singapore licence-exempt limits for 433, 868 and 920 MHz LoRa?
- Which E22 channel is legal in Singapore at 250 kHz bandwidth?
- How much inductance does a ground via have, and how wide is a 50 Ω trace on a JLCPCB board?
- How far can a landed rocket be heard, and why do pages disagree?

## 01-circuit-theory — lumped circuits

### [Lumped elements, impedance and admittance](kb/01-circuit-theory/lumped-elements-impedance-admittance.md)
- What are Ohm's law and electrical power, and how do I size a resistor for an LED or a divider?
- What do the prefixes p, n, µ, m, k, M and G mean, and how do I convert between them?
- How much power does a resistor dissipate, and when will it burn?
- What is impedance, and how is it different from resistance?
- Why does a capacitor's impedance fall with frequency while an inductor's rises?
- What is the reactance of 10 nH or 10 pF at 433 MHz, 915 MHz and 2.4 GHz?
- What is admittance, and when is it easier to use than impedance?
- How do I combine impedances in series and in parallel?
- How do I turn a series R + jX into an equivalent parallel R ∥ X (and why is that only true at one frequency)?
- Why is a capacitor's reactance negative?
- When can I treat a component or a PCB trace as "lumped"?
- What value of L or C gives 50 Ω of reactance at my frequency?
- Is a 100 nF capacitor a "short circuit" at 433 MHz?

### [Network theorems and maximum power transfer](kb/01-circuit-theory/network-theorems-max-power-transfer.md)
- How do KCL and KVL turn a circuit into equations I can solve?
- What is nodal analysis and why do simulators use it?
- What are the Thévenin and Norton equivalents and how do I find them?
- When can I use superposition (and why can't I superpose powers)?
- What is the maximum power transfer theorem, and what is "available power"?
- Why is the load impedance for maximum power the *complex conjugate* of the source impedance?
- Does conjugate matching really waste half the power? Is a matched system only 50 % efficient?
- Why isn't a power amplifier conjugate-matched to its transistor? What is a load-line match?
- Why isn't an LNA conjugate-matched either — what is noise matching?
- If my LoRa module wants 50 Ω, is it "conjugate matched" to the antenna?

### [Resonance and Q](kb/01-circuit-theory/resonance-and-q.md)
- What happens at resonance in a series and in a parallel LC circuit?
- What exactly is Q, and why are there so many definitions (energy, bandwidth, X/R)?
- What is the difference between unloaded Q, loaded Q and external Q?
- How is bandwidth related to Q?
- How do I convert a series-loss model to a parallel-loss model of a resonator?
- If my inductor has Q = 50 and my capacitor Q = 500, what is the Q of the tank?
- Why does a narrow filter made from chip inductors have so much insertion loss?
- What is the Q of an L-matching network and why does it set the match bandwidth?
- Why is the voltage across a resonant capacitor so much bigger than the input voltage?
- What is the group delay of a resonator?

### [Passive LC filter design from low-pass prototypes](kb/01-circuit-theory/passive-filter-design-prototypes.md)
- How do I design an LC low-pass, high-pass, band-pass or band-stop filter from tables?
- What are the g-values in filter tables and how do I scale them to 50 Ω and my frequency?
- Butterworth, Chebyshev, elliptic or Bessel — which should I use?
- What filter order do I need for a given attenuation?
- How do I design a harmonic filter for a 433 MHz LoRa power amplifier?
- Can I build a 902–928 MHz band-pass filter from chip inductors and capacitors? Why is the insertion loss so high?
- Why do the textbook band-pass element values come out as 0.3 pF and 100 nH?
- How much loss will component Q add to my filter?
- What is group delay and why does a sharp filter distort pulses?
- Why is my Bessel filter's cutoff in the wrong place?
- What are constant-k and m-derived filters, and should I still design with the image-parameter method?

### [Two-port networks — Z, Y, h, ABCD and T parameters](kb/01-circuit-theory/two-port-networks-zyh-abcd.md)
- What is a two-port network and why describe circuits that way?
- What do Z, Y, h and ABCD parameters mean physically, and how are they measured?
- Which parameter set should I use for series, parallel or cascaded connections?
- How do I convert between Z, Y, h, ABCD (and S)?
- How do I find the input impedance and voltage gain of a two-port with a load?
- How can I tell from the matrix whether a network is reciprocal, symmetric or lossless?
- Why are ABCD matrices so convenient for ladder filters and transmission lines?
- What are T-parameters and why do different textbooks disagree on them?
- Why are transistor data given as h-parameters (low frequency) but S-parameters (RF)?

### [Transformers and coupled inductors](kb/01-circuit-theory/transformers-coupled-inductors.md)
- What is mutual inductance, and what does the coupling coefficient k mean?
- How does an ideal transformer transform impedance (and why by the turns ratio squared)?
- What are leakage and magnetising inductance, and how do they limit a real transformer's bandwidth?
- How do I model two coupled inductors in a circuit simulator?
- How does a tapped inductor or a capacitive divider act as an impedance transformer in a tank?
- How do I measure k from the frequency splitting of two coupled resonators?
- Why does a transmission-line (Guanella/Ruthroff) transformer work at much higher frequencies than a conventional one?
- Why is |k| always ≤ 1?

### [Transient and step response (RC, RL, RLC)](kb/01-circuit-theory/transient-and-step-response.md)
- What is a time constant and how long does an RC or RL circuit take to settle?
- Where does the "rise time × bandwidth ≈ 0.35" rule come from, and when is it 0.4 or 0.45?
- What do damping ratio ζ and Q have to do with overshoot and ringing?
- Why does my scope show ringing at ~100 MHz on every fast edge?
- Why does a decoupling capacitor ring when the load current steps?
- How long does a narrowband filter or resonator take to respond to a burst (e.g. a LoRa or radar pulse)?
- How do rise times of cascaded stages combine?
- What is the difference between the time-domain view and the frequency-domain view of the same circuit?

### [Energy storage and reactive power](kb/01-circuit-theory/energy-storage-and-reactive-power.md)
- What are real, reactive and apparent power, and what does "var" mean?
- What is power factor, and does it matter in RF circuits?
- How much energy is stored in an inductor or capacitor, and how does that relate to reactive power?
- Why can the voltage across a capacitor in a matching network be much higher than the RF voltage on the 50 Ω line?
- How do I check capacitor voltage and inductor current ratings for a 2 W LoRa transmitter's matching network or filter?
- Why does a small tuned loop antenna need a high-voltage capacitor?
- Where does reactive power "go"? Does it heat anything?

## 02-electromagnetics — fields and waves

### [Maxwell's equations — integral, differential and phasor forms, and where circuit laws come from](kb/02-electromagnetics/maxwells-equations.md)
- What do each of Maxwell's four equations actually say, in plain words?
- What is displacement current, is it "real", and why is it essential for radio waves to exist?
- How do the integral and differential forms relate, and when should I use which?
- What are constitutive relations (D = εE, B = μH, J = σE) and when do they break down?
- How do I write Maxwell's equations for sinusoidal signals (phasor / time-harmonic form)?
- Where do KVL and KCL come from, and exactly when do they stop being true?
- Why does my oscilloscope show different voltages depending on how I route the probe ground lead?
- Is a conductor a conductor at all frequencies? (σ/ωε and charge relaxation time)

### [Wave equation, plane waves, lossy media and polarization](kb/02-electromagnetics/wave-equation-plane-waves-polarization.md)
- How does the wave equation fall out of Maxwell's equations?
- What are the propagation constant γ = α + jβ and the intrinsic impedance η, and how do I compute them for any material?
- What is the wavelength and speed of a wave inside FR-4, water or fibreglass?
- How fast does a 433 MHz signal die in sea water, fresh water or a lossy radome?
- What is the difference between linear, circular and elliptical polarization, and what is axial ratio?
- Which way does a "right-hand circularly polarized" wave rotate — and why do physics/optics books say the opposite?
- How much signal do I lose receiving a circularly polarized GNSS signal with a linear antenna?

### [Poynting vector, energy flow and field strength](kb/02-electromagnetics/poynting-vector-power-flow.md)
- What is the Poynting vector and what does it physically represent?
- How do I convert between transmitted power, power density (W/m²) and field strength (V/m, dBµV/m)?
- What field strength does my 2 W 433 MHz transmitter produce at 1 km, 10 km or 30 km?
- Does electrical energy flow *inside* the copper wire or in the space around it?
- In a coax cable, where exactly is the power flowing?
- What is reactive power in field terms, and how does the "complex Poynting theorem" relate to impedance?
- Why can't I use S = E²/377 right next to my antenna?

### [Boundary conditions, reflection and refraction (Fresnel, Brewster, TIR, radomes, ground and sea)](kb/02-electromagnetics/boundary-conditions-reflection-refraction.md)
- What conditions must E, H, D and B satisfy at an interface between two materials or at a metal surface?
- How much of a wave reflects off a dielectric, the ground or the sea, and how does this depend on angle and polarization?
- What is the Brewster angle and why does vertical polarization over ground have a reflection "dip"?
- What is total internal reflection and what is an evanescent wave?
- How thick can a fibreglass nose cone be before it hurts my 433/915 MHz link? What is a half-wave radome wall?
- Can I put an antenna inside a carbon-fibre airframe?
- Why is the ground-reflected wave in a two-ray model nearly −1 at low grazing angles?
- Does a metal film thinner than the skin depth (a space blanket, a crisp packet, metallic paint, low-e window glass) let radio through?
- Do antennas still work at optical frequencies?

### [Skin effect, conductor loss, surface roughness and plating](kb/02-electromagnetics/skin-effect-conductor-loss-roughness.md)
- Why does RF current flow near the surface of a conductor, and how deep does it go?
- What is the skin depth of copper, silver, gold, aluminium and nickel at 433 MHz, 915 MHz, 2.4 GHz, 10 GHz, 77 GHz?
- What is surface resistance (Ω per square) and how do I get the AC resistance of a wire or a PCB trace from it?
- What is the proximity effect and when does it matter?
- How much does copper foil roughness increase loss, and which model (Hammerstad, Groiss, Huray, "cannonball") should I use?
- Is ENIG bad for RF? Why do people recommend immersion silver, OSP or bare copper?
- Does silver plating help? Does gold? When is Litz wire useful?
- If foil or a sputtered film is thinner than the skin depth, does radio pass through it?
- Does the skin depth keep shrinking at infrared and optical frequencies?
- Can dental fillings really pick up radio stations?

### [Dielectrics — complex permittivity, loss tangent, dispersion and material values](kb/02-electromagnetics/dielectrics-permittivity-loss-tangent.md)
- What do Dk, Df, εr, ε', ε'' and tanδ mean and how are they related?
- Why do materials polarise, and why does that cause loss?
- What is a Debye relaxation, and why does FR-4's permittivity drift slowly with frequency?
- What is the Djordjevic–Sarkar (wideband Debye) model and why do simulators insist on it?
- Why does a Rogers datasheet give two different Dk values ("process" and "design")?
- What εr and tanδ should I use for FR-4, RO4003C, RO4350B, PTFE, alumina, fibreglass, water, PLA/ABS 3D-printed parts?
- How much do glass weave, moisture and temperature change the numbers?
- Is carbon fibre a dielectric?

### [Magnetic materials — complex permeability, ferrites, Snoek's limit and gyrotropic media](kb/02-electromagnetics/magnetic-materials-permeability.md)
- What do μ', μ'' and "complex permeability" mean on a ferrite datasheet?
- Why does a ferrite's permeability collapse above some frequency, and why can't I have high μ *and* high frequency (Snoek's limit)?
- Why is a ferrite bead a resistor at 100 MHz rather than an inductor?
- Which ferrite mix (31, 43, 61, 67…) for 433 MHz or 915 MHz? Do ferrites work at 2.4 GHz?
- What makes a magnetised ferrite "gyrotropic", and how does that give circulators and isolators?
- Why does nickel (e.g. in ENIG or connector plating) behave strangely at RF?
- Why does an iron-powder toroid have μ ≈ 10 when iron itself has μ in the thousands, and why is it so stable and low-loss?
- What does an air gap do to a core's permeability, temperature drift and Q?
- Do magnets affect radio waves or antennas?

### [Quasi-static vs full-wave — when is a circuit "lumped"?](kb/02-electromagnetics/quasi-static-vs-full-wave.md)
- When can I treat a PCB trace as just a wire, and when must I treat it as a transmission line?
- Where do the "λ/10" and "λ/20" rules come from, and how wrong is a lumped model at those sizes?
- How do I decide from a digital signal's rise time rather than its clock frequency?
- What exactly "breaks" when a circuit gets electrically large: phase, impedance, radiation, KVL?
- What are electroquasistatic (EQS) and magnetoquasistatic (MQS) approximations?
- How big is "small" at 433 MHz, 915 MHz, 2.4 GHz on FR-4?

### [Radiation from currents — potentials, the Hertzian dipole, small loops and why circuits radiate](kb/02-electromagnetics/radiation-from-currents-hertzian-dipole.md)
- How do currents produce radiated waves, step by step from Maxwell's equations?
- What are the scalar and vector potentials, the Lorenz gauge and "retarded" potentials?
- What are the complete fields of a Hertzian (infinitesimal) dipole, including the near-field terms?
- Where does R_rad = 80π²(l/λ)² come from, and why do some books get 789 Ω and others 790 Ω?
- Why do accelerating charges radiate but steady currents don't?
- How much does a small loop radiate, and why is a small loop antenna so inefficient?
- Why do cables (common-mode) radiate far more than PCB loops (differential-mode)?

### [Waveguides and cavity resonators (rectangular, circular, parallel-plate, SIW, PCB plane cavities; transverse resonance, modal V/I, probe and loop excitation)](kb/02-electromagnetics/waveguides-and-cavity-resonators.md)
- How does a hollow metal pipe carry microwaves, and why does it have a cutoff frequency?
- What are TE, TM and TEM modes, and why can't a hollow waveguide carry TEM?
- What waveguide size would I need at 433 MHz, 915 MHz, 2.45 GHz or 10 GHz?
- Phase velocity is faster than light in a waveguide — doesn't that break relativity?
- How lossy is a waveguide compared with coax?
- How do cavity resonators work, and what limits their Q?
- Why does a small hole or a honeycomb vent block RF (waveguide beyond cutoff)?
- What is a substrate-integrated waveguide (SIW)?
- Why does my PCB's power/ground plane pair resonate at a few hundred MHz?
- Why does a circular waveguide (a can) have such a narrow single-mode band, and what does its TE11 mode look like?
- What is the transverse-resonance method, and how does it find surface waves on a PCB?
- What is "the impedance" of a waveguide when there are several definitions?
- How long should the probe in a cantenna be, and where should it go?
- How do probes, loops and small holes couple energy into a waveguide?

### [Near field and far field — reactive, radiating (Fresnel) and Fraunhofer regions](kb/02-electromagnetics/near-field-far-field.md)
- Where does an antenna's near field end and its far field begin?
- What do λ/2π, 0.62√(D³/λ) and 2D²/λ mean, and which applies to my antenna?
- How far away must I be to measure an antenna's gain or pattern correctly?
- What is "wave impedance", and why are magnetic near fields hard to shield?
- Why does Friis' formula fail when two antennas are close?
- Why does my radio detune when I put it near the rocket body or my hand?

### [Inductance and capacitance from fields — loop vs partial inductance, mutual inductance, standard geometries](kb/02-electromagnetics/inductance-capacitance-from-fields.md)
- What *is* inductance and capacitance in terms of fields and stored energy?
- What is the inductance of a PCB trace, a via or a bond wire — and why do experts say that question is incomplete?
- What is the difference between loop inductance and partial inductance (Ruehli, Clayton Paul)?
- How do I compute mutual inductance between two loops or two wires?
- What are L and C per unit length of coax, a two-wire line, a wire over ground, a microstrip?
- How big is fringing capacitance, and when does the parallel-plate formula fail?
- Why does "1 nH/mm" come up so often, and when is it wrong?

### [Electromagnetic units and constants (ε0, μ0, c, η0 after the 2019 SI)](kb/02-electromagnetics/electromagnetic-units-and-constants.md)
- What are the exact values of ε0, μ0, c and the impedance of free space today?
- Is μ0 still exactly 4π×10⁻⁷ H/m after the 2019 SI redefinition, and does it matter for RF work?
- Why is the impedance of free space 376.73 Ω and not exactly 120π Ω?
- How do I convert between V/m, dBµV/m, W/m² and dBm/m²?
- How do I convert a received power in dBm into a field strength in dBµV/m?
- What goes wrong when I mix Gaussian (CGS) and SI formulas from old physics books?
- What are the units of E, H, D, B, J, ρ, σ, ε, μ and how do they fit together?

### [Green's functions and integral equations — scalar and dyadic Green's functions, EFIE/MFIE, Pocklington and Hallén, layered media, the method of moments, equivalence, reciprocity and aperture radiation](kb/02-electromagnetics/greens-functions-and-integral-equations.md)
- What is a Green's function, and why is exp(−jkR)/(4πR) the one for free space?
- How do I get the field of an *arbitrary* current distribution from the Green's function?
- What is the dyadic Green's function, and how does it contain the Hertzian dipole's near and far fields?
- What are the EFIE and MFIE, and why does the MFIE only work on closed bodies?
- Where do the Pocklington and Hallén equations for wire antennas come from, and what is the "reduced kernel" problem?
- How does the method of moments (NEC, FEKO, my own MoM script) turn an integral equation into a matrix?
- Why do planar EM solvers (Sonnet, Momentum, AXIEM) only mesh the copper, and what are Sommerfeld integrals?
- What are surface-wave poles, and why do they make layered-media Green's functions hard?
- How small must NEC segments be, and why does making them too short break the model?
- What is image theory, and how does it relate to a monopole over a ground plane?
- What is a magnetic current, and why do antenna books use one when no such thing exists?
- What does the equivalence principle actually say, and how does it give the far field of a horn or an open waveguide from the field in its mouth?
- Why is an antenna's receive pattern the same as its transmit pattern, and when does reciprocity fail?
- How much does an open-ended waveguide radiate, and how well is it matched?
- How much RF leaks through a small hole or a slot in a metal enclosure?

## 03-transmission-lines-matching — 

### [Telegrapher's equations and characteristic impedance](kb/03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md)
- When does a wire or PCB trace stop being "just a wire" and become a transmission line?
- What is characteristic impedance physically, and why is it measured in ohms if nothing dissipates?
- Why does my multimeter read open (or a few ohms) across a 50 Ω coax instead of 50 Ω?
- How do I derive $Z_0$ and the propagation constant $\gamma=\alpha+j\beta$ from the RLGC model?
- What is velocity factor, and how do I compute the physical length of a quarter wave in coax?
- Why is attenuation in dB per metre roughly proportional to $\sqrt{f}$ at low frequency and to $f$ at high frequency?
- What is a distortionless line and why did Heaviside add inductance to telephone cables?
- Is $Z_0$ really constant with frequency? Why is it complex at audio frequencies?
- How do I measure $Z_0$ and velocity factor of an unknown cable with a NanoVNA?

### [Reflections, VSWR, return loss and mismatch loss](kb/03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)
- What is the reflection coefficient Γ and how is it related to VSWR, return loss and mismatch loss?
- My antenna has a VSWR of 2:1 — how much power am I actually losing?
- Does "reflected power" burn out my transmitter / LoRa module?
- Why does the SWR reading change when I change the length of my coax?
- Why does a long, lossy cable make a bad antenna look well matched?
- Is return loss positive or negative? Is S11 = −10 dB the same as a return loss of 10 dB?
- Does low SWR mean my antenna is good?
- How high does the voltage on the line get when the load is mismatched?
- Where are the voltage maxima and minima of a standing wave?

### [Input impedance, stubs, quarter-wave and half-wave lines](kb/03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md)
- What impedance do I see looking into a length of line terminated in some load?
- Why does a quarter-wave line turn a short into an open (and 12.5 Ω into 200 Ω)?
- How long must a piece of coax be to act as a quarter wave at 433 MHz?
- How can a piece of open or shorted line replace an inductor or capacitor?
- What is a resonant stub, what is its Q, and how is it used as a bias feed or harmonic trap?
- How much bandwidth does a quarter-wave transformer have?
- Why is a half-wave line "transparent", and when is it not?
- How do I convert electrical length (degrees) to millimetres on coax or PCB?
- What is a radial (fan) or butterfly stub, how do I size one, and is it really broadband?
- How accurate are the radial-stub design formulas on ordinary FR-4?
- What do stepped-impedance, hairpin, interdigital, spurline, Lange, Wilkinson and tuning-pad structures do, and where are they covered?

### [The Smith chart](kb/03-transmission-lines-matching/smith-chart.md)
- What exactly is the Smith chart — why are the grid lines circles?
- How do I read impedance, admittance, VSWR and Q off it?
- Which way do I move when I add a series inductor, a shunt capacitor, or a length of line?
- How do I read my NanoVNA's Smith display (markers, loops, spirals)?
- Why does the trace always go clockwise as frequency increases?
- What are constant-Q circles and why do they matter for bandwidth?
- What are noise, gain and stability circles (preview)?
- What does "negative resistance / outside the chart" mean?

### [Impedance matching — lumped and distributed](kb/03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)
- How do I design an L-network, and where does $Q=\sqrt{R_h/R_l-1}$ come from?
- How do I match a complex load such as a chip antenna measured as 18 − j35 Ω?
- When should I use a Pi or T network instead of an L, and how do I pick Q?
- How much bandwidth do I get, and how much loss do real 0402 inductors add?
- How do single-stub, quarter-wave, binomial, Chebyshev and Klopfenstein matching work, and when do they beat lumped parts?
- What is the practical procedure for tuning a pi pad on my PCB with a NanoVNA?
- Is the best match always the conjugate match? (Not for PAs and LNAs.)
- Why did my perfect simulated match fail on the real board?
- If a matching network "just moves the reflection", where does the reflected power go?
- Why does my extracted component model contain a negative inductance?
- How do I use the S11 or impedance table in an RF IC's datasheet — do I conjugate it or not?
- How do I match a differential (balanced) IC input?
- How do I match a diode detector whose impedance is several kilohms?
- How do I match one transistor stage to the next without going through 50 Ω?
- Why can't a double-stub tuner match every load?

### [Broadband matching and the Bode–Fano limit](kb/03-transmission-lines-matching/broadband-matching-bode-fano.md)
- Is there a fundamental limit to how wideband I can match a reactive load such as a small antenna?
- What does the Bode–Fano integral say, in plain words and in numbers?
- How much can a cleverer matching network improve on a simple one? (At most ≈ 4× for VSWR 2.)
- Why is my small 433 MHz chip/helical antenna so narrowband and so sensitive to its surroundings?
- Can a 1 cm 915 MHz antenna cover the whole 902–928 MHz band?
- How do I estimate an antenna's Q from a NanoVNA sweep, and then its best achievable bandwidth?
- Can resistive loading, active (non-Foster) or time-varying networks beat the limit?

### [S-parameters](kb/03-transmission-lines-matching/s-parameters.md)
- What exactly are S-parameters, and why do we use waves instead of voltages and currents at RF?
- What do $S_{11}$, $S_{21}$, $S_{12}$, $S_{22}$ mean physically, and what does "referenced to 50 Ω" mean?
- What is the difference between Kurokawa power waves and Marks–Williams pseudo-waves, and when does it matter?
- How do I convert S to Z, Y or ABCD, change the reference impedance, or cascade networks (T-parameters)?
- How do I check that a measured S-matrix is physical (reciprocal, lossless, passive)?
- What are mixed-mode (differential/common) S-parameters?
- How do I read a Touchstone (.s2p) file, and why is the column order S11 S21 S12 S22?
- How do I get group delay from S21? What are K and μ?

### [Planar lines — microstrip, stripline, CPW/CPWG and differential pairs](kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)
- How wide should a 50 Ω trace be on a JLCPCB 2-layer 1.6 mm board, and on the 4-layer JLC04161H-7628 stackup?
- What are the Hammerstad–Jensen, Wheeler and Kirschning–Jansen formulas, and how accurate are they?
- Why is microstrip "quasi-TEM" and what is effective permittivity?
- When should I use grounded coplanar waveguide (CPWG) instead of microstrip?
- How much do copper thickness and soldermask change the impedance?
- How do I design a 100 Ω differential pair? Is the IPC-2141 formula good enough?
- How lossy is a trace on FR-4 at 433 MHz, 915 MHz, 2.45 GHz and 5.8 GHz?
- At what frequency do microstrip lines start to misbehave (dispersion, surface waves, radiation)?
- Why does my impedance calculator disagree with another one?
- Which closed form should I use for coupled microstrip (even/odd mode), and how good is it?
- What 50 Ω width do I need for an inner-layer (offset) stripline on a JLC 6-layer board?
- How much does the trapezoidal etch profile change the impedance?
- How much RF power can a PCB trace carry? Will the 2 W trace from my E22 module get hot? Can I use IPC-2152 for RF?
- Does an RF ground plane have to be "50 Ω" too?
- Where do I find models for open ends, gaps, steps, bends and T-junctions?

### [Coaxial lines and RF cables](kb/03-transmission-lines-matching/coax-and-cables.md)
- How is the characteristic impedance of coax calculated from its dimensions?
- Why is 50 Ω the standard (and why is TV cable 75 Ω)?
- How much loss do RG-58, RG-174, RG-316, RG-402/405, LMR-195/240/400 and U.FL micro-coax have at 433, 915, 1575 and 2450 MHz?
- Which cable should I use for a LoRa ground station, and how much range does cable loss cost?
- How much power can a cable carry, and why does the rating fall with frequency?
- What limits the maximum frequency of a coax?
- Which cables are phase-stable (for arrays and interferometry)?
- How long can a U.FL pigtail be before it hurts a GNSS receiver?
- What is the impedance of ladder line or open-wire line, and why is it so low-loss at HF?
- How does ladder line compare with coax when the SWR is high?
- Does balanced line need a choke or balun?
- Can I use twisted pair or Ethernet cable as an RF feeder?

### [Time-domain reflectometry (TDR) and VNA time-domain analysis](kb/03-transmission-lines-matching/time-domain-reflectometry.md)
- How does a TDR show the impedance along a cable or PCB trace?
- How do I tell a capacitive from an inductive discontinuity on a TDR trace, and how big is it?
- How can a VNA (or NanoVNA) produce a TDR plot from frequency data?
- What sets the spatial resolution and the maximum distance ("alias-free range")?
- What do the minimum / normal / maximum windows do?
- What are low-pass vs band-pass modes, and gating?
- How do I find a bad connector or a kink in a long antenna feed?
- How do I draw a lattice (bounce) diagram, and what does it look like for a capacitive or inductive load?
- Why does a fast logic edge ring and overshoot at the end of a long trace, and how big is the overshoot?
- Why is the second step on my TDR trace smaller than the first, and what are the small "ghost" steps after it?

### [Signal-flow graphs, Mason's rule and mismatch uncertainty](kb/03-transmission-lines-matching/signal-flow-graphs-mason.md)
- What is a signal-flow graph and how do I draw one for a two-port between a source and a load?
- How does Mason's gain rule work, step by step?
- Where do $\Gamma_\text{in}=S_{11}+S_{12}S_{21}\Gamma_L/(1-S_{22}\Gamma_L)$ and the transducer-gain formula come from?
- Why can't I measure RF power more accurately than about ±0.1–0.6 dB even with a perfect power sensor?
- How much does a mismatched source (like a LoRa module) and a mismatched antenna reduce delivered power, and can a mismatch ever *increase* it?
- Why does my SWR meter read 1.2 on a perfect dummy load?
- Where do the periodic ripples in a cable's insertion loss come from?

### [Antenna tuners and ATUs — what a tuner does and does not do, L/T/Pi topologies and their losses, auto-tuner algorithms, remote and at-antenna tuners, and the "tuners fix antennas" myth in numbers](kb/03-transmission-lines-matching/antenna-tuners-and-atus.md)
- What does an antenna tuner actually do, and what does it not do?
- Does a tuner at the radio fix the SWR on my feedline?
- How much power do I lose using a tuner at the rig with high SWR on coax?
- Why is a tuner better at the antenna end, and how is a remote tuner powered and controlled?
- How do L, T and Pi tuners differ, and why can a T tuner waste power?
- How does an automatic antenna tuner find a match, and why do cheap (N7DDC-style) ones fail?
- Are ordinary relays good enough inside an RF tuner?
- Which antennas will my radio's internal tuner match?
- Does a tuner help a receive-only shortwave setup?
- What should I consider when choosing a tuner?

### [Microstrip discontinuities — open ends, gaps, steps, bends and mitres, T-junctions and vias](kb/03-transmission-lines-matching/microstrip-discontinuities.md)
- Why is my open-circuit stub resonating low, and how much shorter should I cut it?
- What is an "excess capacitance" and why do discontinuities look like little L and C networks?
- Why does a 75 % mitre perform worse than a 57 % one?
- What is the Kirschning–Jansen–Koster open-end formula, and how accurate is it?
- Does a 90° corner in a 50 Ω trace matter at 433 MHz, 915 MHz, 2.4 GHz or 5.8 GHz?
- How much should I mitre a bend? Is 45° chamfering always right?
- Can a gap in a microstrip work as a DC block?
- How big is the parasitic of a step in width (for example a 2.8 mm trace necking down to an SMA or U.FL pad)?
- How do I model a microstrip T-junction in a power splitter or stub filter?
- How much inductance does a ground via add to a shorted stub?
- When do the closed-form models stop working and I have to run an EM simulation?

### [Periodic structures — Floquet/Bloch waves, slow-wave and Bragg lines, surface and leaky waves, EBG/mushroom surfaces and metamaterial basics (with a hype check)](kb/03-transmission-lines-matching/periodic-structures-ebg.md)
- What happens to a wave on a transmission line loaded with identical capacitors every few millimetres?
- What are Floquet's theorem, Bloch waves and a k–β (Brillouin) diagram, and how do I read one?
- What is the Bloch impedance, and why does a periodic line have stop bands?
- How do slow-wave lines and stepped-impedance (Bragg, "PBG") lines work, and are they any use at 433 MHz?
- What are surface waves on a PCB, and how much power does a patch or printed dipole lose to them?
- How does a leaky-wave antenna steer its beam with frequency?
- What is a mushroom EBG or "artificial magnetic conductor", and can it let me mount an antenna flat on a metal airframe?
- What is a metamaterial, what is a left-handed (CRLH) line, and which metamaterial claims are hype?

## 04-real-components-hf — real parts at RF

### [Resistors at RF — thin vs thick film, parasitics, terminations, attenuators and derating](kb/04-real-components-hf/resistors-at-rf.md)
- Does a chip resistor still behave like a resistor at 433 MHz, 915 MHz or 2.4 GHz?
- Why are low-value resistors inductive and high-value resistors capacitive at RF?
- Is there a resistor value that stays flat to the highest frequency?
- Thin film or thick film — which for RF?
- How do I make a good 50 Ω termination on a PCB?
- What resistor values do I need for a 3/6/10/20 dB 50 Ω attenuator, and can chip resistors take my transmitter's power?
- How do I derate a chip resistor's power with temperature?
- Why does a 10 kΩ bias resistor on an RF line not isolate as well as I expected?

### [Capacitors at RF — MLCC dielectrics, ESR, ESL, SRF and selection](kb/04-real-components-hf/capacitors-at-rf-mlcc.md)
- What is the difference between C0G/NP0, X7R, X5R and Y5V, and which do I use in an RF path?
- Why does my "10 µF" ceramic capacitor measure 3 µF on the 5 V rail?
- What are ESR, ESL and self-resonant frequency (SRF), and how do I get them for a part?
- What value DC-blocking capacitor should I use at 433 MHz, 915 MHz and 2.4 GHz?
- Can I use a capacitor above its self-resonant frequency?
- Why do people put 100 nF and 100 pF (or 10 nF) in parallel — does it help or hurt?
- What is the Q of a chip capacitor and does it matter in a matching network?
- What are "RF-grade" or "high-Q" capacitors (Murata GJM, ATC, Johanson), and are they worth it?
- What voltage rating do I need in a PA matching network or a tuned antenna?
- Does capacitor orientation on the board matter?
- Why don't electrolytic or tantalum capacitors work at RF, and what are they good for?
- How do aluminium, tantalum and polymer capacitors compare in impedance, and what happens to them in the cold?
- Why use polypropylene, mica or porcelain capacitors, and what is the main RF loss in a film capacitor?
- Which capacitor family should I use for bulk decoupling, a filter, a PA tank or an HF transmitter?

### [Inductors at RF — types, Q, SRF, saturation and air-coil design](kb/04-real-components-hf/inductors-at-rf.md)
- What kinds of RF inductors exist (air-core, wirewound ceramic, multilayer, thin-film, ferrite-core) and when do I use each?
- How do inductance and Q change with frequency, and why does inductance "rise" near the self-resonant frequency?
- How far below SRF should I operate a chip inductor?
- Why do multilayer inductors have lower Q than wirewound ones, and how much does it matter?
- How do I calculate the inductance of an air-wound coil (Wheeler, Nagaoka, Lundin)? How accurate are these formulas?
- Do RF inductors saturate?
- What inductor should I use for an RF choke / bias-T at 433 or 915 MHz?
- Why doesn't my measured inductor match the datasheet?

### [Ferrites and ferrite beads — impedance, DC bias, resonance pitfalls and core materials](kb/04-real-components-hf/ferrites-and-beads.md)
- What does a ferrite bead actually do — is it an inductor or a resistor?
- What does "600 Ω at 100 MHz" on a bead datasheet mean, and what is it at 433 or 915 MHz?
- Why does my bead stop working when the load draws current?
- Can a bead plus a capacitor make supply noise *worse*? How do I damp it?
- Which bead should I put on the supply of a LoRa module or a GNSS receiver?
- What are Fair-Rite 31, 43, 61 (and 73) materials and which do I use on a cable?
- How does a common-mode choke differ from a bead?
- When does a ferrite bead hurt rather than help?
- Iron powder or ferrite — which toroid (T50-2, T68-6, FT240-43, FT240-61) for a filter, a trap, a balun or a 49:1 EFHW transformer?
- How many turns do I need from the A_L value, and why does my ferrite inductor measure less than A_L predicts at HF?
- How hot will my EFHW transformer get at 100 W, and do I need two stacked cores?
- What does the capacitor across the 50 Ω side of an EFHW transformer do, and what rating does it need?
- Which ferrite bead works on a 433 MHz coax, and will it heat up at 2 W?
- Why do modern cables rarely have a ferrite lump on them?

### [PCB parasitics — traces, vias, pads, plane gaps and ground-return inductance](kb/04-real-components-hf/pcb-parasitics-traces-vias-pads.md)
- How much inductance does a PCB trace have — is "1 nH per mm" right?
- What is the difference between partial inductance and loop inductance, and which one matters?
- How much inductance does a via have on a 1.6 mm 2-layer board vs a 4-layer JLCPCB board?
- Does putting more ground vias in parallel keep reducing inductance?
- How much capacitance does a component pad add, and why cut the ground plane under an SMA pad?
- What happens when a trace crosses a gap or slot in the ground plane?
- Why should my shunt capacitor's ground via be right at the pad?
- When can I treat a short trace as a lumped inductor?

### [Crystals and resonators — BVD model, load capacitance, pulling, XO/TCXO/OCXO and LoRa frequency budgets](kb/04-real-components-hf/crystals-and-resonators.md)
- What is inside a quartz crystal electrically (motional R, L, C and C0)?
- What are series and parallel (anti-)resonance, and what does "load capacitance" on the datasheet mean?
- How do I pick the two load capacitors for a crystal?
- How many ppm does 1 pF of extra stray capacitance pull my crystal?
- What is ESR, negative resistance and gain margin in a Pierce oscillator, and what is drive level?
- What is the difference between XO, TCXO, VCXO, OCXO and MEMS oscillators?
- How big is a 10 ppm error at 433 MHz and 915 MHz?
- When does LoRa need a TCXO? Why do narrow bandwidths and high spreading factors care about crystal drift?
- Does rocket acceleration or vibration shift my radio's frequency?
- Why are watch/RTC crystals 32.768 kHz, and why do they drift so much in the cold?
- How many seconds per day will my flight computer's RTC lose at a cold launch site?
- Is the MCU's internal RC oscillator good enough, or do I need a crystal (UART, CAN, USB, RTC)?

### [Package parasitics — bondwires, leads, exposed pads and ground pins](kb/04-real-components-hf/package-parasitics-bondwires.md)
- How much inductance does a bondwire have? Is "1 nH per mm" right?
- How much lead inductance do SOIC, TSSOP and QFN packages have?
- Why do RF ICs (LoRa transceivers, LNAs, PAs) have so many ground pins and a big exposed pad?
- How should I connect a QFN exposed pad to ground, and how many vias does it need?
- What does ground inductance do to an amplifier's gain and stability?
- Why is a PA's ground connection so critical?
- Why do RF parts come in QFN/BGA/flip-chip rather than SOIC?

### [Component models — vendor S-parameter files, equivalent circuits and how to use them](kb/04-real-components-hf/component-models-s2p-spice.md)
- Where do I get accurate RF models for capacitors, inductors, beads and resistors?
- What is in a vendor `.s2p` file, and was it measured in series or shunt?
- Should I use the S-parameter file or the SPICE/equivalent-circuit model?
- Why doesn't my simulation with vendor models match my board?
- How do I include pads, vias and the PCB in a simulation that uses de-embedded part models?
- How can I tell if an S-parameter file is bad (non-passive, non-causal)?
- How do I use `.s2p` files in scikit-rf, QUCS-S, LTspice or a harmonic-balance simulator?
- Can S-parameter models show DC bias, saturation or temperature effects?

## 05-analog-electronics — 

### [Diodes for analog and RF — pn junction, Schottky, PIN, varactor, step-recovery, Zener/TVS](kb/05-analog-electronics/diodes-schottky-pin-varactor.md)
- What do n-type, p-type and "depletion region" mean, and why does a junction have a built-in voltage?
- What forward voltage should I expect from a silicon, germanium, Schottky or LED diode?
- How do diodes fail?
- How efficient is an RF energy harvester (rectenna) at −30, −10 or 0 dBm?
- Can I power a sensor from ambient RF, or charge a phone across a room with radio waves?
- What does the diode equation actually say, and where do 26 mV and "60 mV per decade" come from?
- Why does a diode's forward voltage drop by about 2 mV per °C?
- Why is a Schottky diode fast and low-drop, and why is it the default RF detector and mixer diode?
- How much DC voltage will a Schottky detector give me for a given RF power, and where does square-law detection stop?
- Why does my zero-bias detector read differently when it gets hot?
- How does a PIN diode act as a current-controlled resistor at RF but a rectifier at low frequency?
- How do I estimate insertion loss and isolation of a series or shunt PIN switch?
- What is the C–V law of a varactor, what is gamma, and how much can I tune a VCO with one?
- Why does a varactor VCO get noisy or distorted when the RF swing is large?
- What is a step-recovery (snap-off) diode and what are comb generators used for?
- Can I put an ordinary TVS or ESD diode on an antenna line?
- Why are Zener diodes noisy, and which voltage has the lowest temperature coefficient?

### [BJT fundamentals and small-signal models (gm, hybrid-π, fT, fmax, noise, SiGe HBT)](kb/05-analog-electronics/bjt-fundamentals-small-signal.md)
- Why is $V_{BE}$ "about 0.6–0.7 V", and how much does it change with current?
- What is the difference between $f_\beta$, $f_\alpha$ and $f_T$?
- How do BJTs fail?
- Why is a BJT's transconductance exactly $I_C/V_T$, whatever the transistor?
- What are $r_\pi$, $r_e$, $r_o$ and the Early voltage, and how do I get them from the bias point?
- What do $f_T$ and $f_{max}$ really mean, and why is $f_T$ not "the highest frequency the transistor works at"?
- Why does a common-emitter stage's bandwidth collapse when its gain is high (Miller effect)?
- Why should I never design a bias circuit that depends on β?
- What sets a BJT's noise, what is the optimum source resistance, and why are RF LNA transistors run at several mA?
- What's special about SiGe HBTs and why are they used for LNAs up to tens of GHz?
- Why is $BV_{CEO}$ so much lower than $BV_{CBO}$, and why do RF transistors die from 1–2 V of reverse base-emitter voltage?
- How does saturation work, and what sets $V_{CE(sat)}$?

### [FETs — MOSFET, JFET, GaAs MESFET/pHEMT, GaN HEMT, LDMOS (and which device for which job)](kb/05-analog-electronics/fets-mosfet-jfet-gaas-gan.md)
- What is the MOSFET square law, and why does it stop working in modern short-channel transistors?
- What is the $g_m/I_D$ design method and why do analog designers love it?
- Why does a MOSFET give less transconductance per milliamp than a BJT?
- When should I use a JFET instead of a BJT or op-amp input?
- What is a HEMT/pHEMT and why are GaAs pHEMTs the classic lowest-noise LNA device at 0.5–20 GHz?
- Why is everyone using GaN for power amplifiers?
- What does LDMOS do that GaN does not (and vice versa)?
- Why must I apply the negative gate voltage before the drain voltage on GaAs/GaN amplifiers?
- Which transistor technology should I pick for a given frequency, power and noise requirement?
- Will my pyro-channel MOSFET really turn on fully with a 3.3 V GPIO?
- Why does a CMOS op-amp have millivolts of offset, why are voltage references ≈ 1.2 V, and why can't a CMOS radio chip swing many volts into its antenna?

### [Amplifier topologies — CE/CS, CB/CG, CC/CD, cascode, differential pair, Darlington, mirrors, feedback amplifiers, RF gain blocks](kb/05-analog-electronics/amplifier-topologies.md)
- What do the three basic single-transistor stages (common emitter/source, base/gate, collector/drain) each do well?
- Why does a common-base stage make a good wideband 50 Ω input, and what noise figure does that cost?
- Why is the cascode everywhere, from op-amp input stages to LNAs?
- How does a differential pair reject common-mode noise and why is it more linear than a single transistor?
- Why do MMIC gain blocks (ERA, MAR, Gali, PGA class) have a Darlington pair and two resistors, and why do I bias them through a resistor and choke?
- How do the four feedback-amplifier types change input and output impedance?
- How can I estimate the bandwidth of a multi-capacitor amplifier without solving a big polynomial?
- How much does emitter degeneration improve linearity (IIP3)?
- What is a current mirror, and how accurate is it?
- How do shunt peaking, series peaking and T-coils extend bandwidth, and by how much?
- How does a distributed (travelling-wave) amplifier get DC–20 GHz bandwidth?
- Why do balanced amplifiers with 90° hybrids have a good input match even when each amplifier is badly matched?
- What noise figure does a resistive-feedback wideband LNA have?
- Why can't I use an LNA to drive a power amplifier?
- What is crossover distortion, and why are output stages class AB?

### [Feedback and stability — loop gain, Bode and Nyquist, phase margin, compensation, capacitive loads, parasitic oscillation](kb/05-analog-electronics/feedback-and-stability.md)
- What exactly is "loop gain", and how do I find it in a real circuit?
- What do phase margin and gain margin mean, and how much do I need?
- How does phase margin relate to overshoot and ringing on a step response?
- When is the simple Bode test not enough and I need the Nyquist criterion?
- How do op-amps stay stable (dominant-pole and Miller compensation, pole splitting, the right-half-plane zero)?
- Why does my op-amp ring or oscillate when I hang a capacitor (or a long cable, or an ADC input) on its output — and how do $R_{ISO}$ and in-loop compensation fix it?
- Why does a transimpedance amplifier or a high-value feedback resistor need a small feedback capacitor, and how big?
- Why does an emitter follower oscillate at hundreds of MHz, and why does a 100 Ω base resistor cure it?
- How do I track down and cure a parasitic oscillation on a real board?

### [Op-amps — real limitations (GBW, slew, noise, offsets, CMRR/PSRR, output drive, RRIO, CFA, FDA) and how to choose one](kb/05-analog-electronics/op-amps-real-limitations.md)
- Why is my gain-of-10 amplifier's bandwidth only a tenth of the op-amp's GBW — and why does an inverting gain of −1 only get half?
- What is the difference between small-signal bandwidth and full-power bandwidth?
- How do I add up $e_n$, $i_n$ and resistor noise, and what does the 1/f corner do to low-frequency noise?
- How big is the DC error of my circuit (offset, drift, bias current, CMRR, PSRR), and when do I need a zero-drift op-amp?
- Why does supply ripple from a switching regulator show up at the op-amp output?
- What does "rail-to-rail" really mean, and why is there distortion near the positive rail on some RRIO parts?
- Why can't I put a capacitor across the feedback resistor of a current-feedback amplifier?
- How do fully differential amplifiers drive ADCs, and what input impedance does a single-ended source see?
- Why does my sensor amplifier's output shift when the LoRa transmitter keys up?
- How do I choose an op-amp?
- What resistor values should I use for a given gain — 1 kΩ or 1 MΩ?
- Why does my AC-coupled non-inverting amplifier drift to a rail, and where does the bias resistor go on a single supply?
- Is an op-amp stable as an attenuator (gain below 1)?
- How do I stop an op-amp + MOSFET current sink from oscillating?
- Why is a summing amplifier noisier and slower than its gain suggests?

### [Oscillators — Barkhausen and negative resistance, Colpitts/Clapp/Hartley/Pierce/crystal/VCO, start-up and amplitude, phase-noise basics, ring and relaxation](kb/05-analog-electronics/oscillators.md)
- What really makes a circuit oscillate, and why is "loop gain = 1 at 0°" not the whole story?
- How do I view an oscillator as a negative resistance cancelling a resonator's loss?
- How do Colpitts, Clapp, Hartley and Pierce oscillators work, and what sets their frequency?
- How do I pick the load capacitors for a crystal, and how much will a wrong value pull my LoRa radio's frequency?
- What is $g_{m,crit}$ and gain margin for a crystal oscillator, and why do some crystal circuits fail to start in the cold?
- What limits the amplitude of an oscillator, and how big does it get?
- What is Leeson's model and why does resonator Q dominate phase noise?
- How do VCOs, ring oscillators and RC relaxation oscillators differ?
- How does a cross-coupled LC VCO start, what sets its amplitude, and how much tail current does it need?
- How wide can a varactor VCO tune, and why do synthesiser chips use switched capacitor banks?
- How does a quadrature VCO produce I and Q, and how accurate is its 90°?

### [Data converters — ADC and DAC fundamentals (quantisation, ENOB, SFDR, jitter, aliasing, architectures, DAC sinc, drivers, references)](kb/05-analog-electronics/data-converters-adc-dac.md)
- Where does SNR = 6.02N + 1.76 dB come from, and when is it wrong?
- What are SINAD, ENOB, SFDR, THD and noise spectral density (dBFS/Hz), and how do I read them off a datasheet?
- Why does clock jitter limit SNR at high input frequency, and how much jitter can I afford?
- Where will a 433 MHz or 915 MHz signal land if I sample it at 61.44 or 125 MSPS?
- How do flash, SAR, pipeline, sigma-delta and time-interleaved ADCs differ, and which suits sensors, SDR or radar?
- Why do DAC outputs droop and have images, and what is the sinc correction?
- How much does oversampling and decimation improve SNR?
- Why does my SAR ADC read wrong unless I put a capacitor at its input (charge kickback), and how do I size the RC?
- What is an ADC's noise figure, and how much gain do I need in front of it in an SDR?
- How does reference noise limit an ADC?

### [Power supplies for RF and analog — LDO PSRR and noise, switcher ripple and spurs, LC/ferrite post-filters, ground bounce, sequencing, battery-powered bursts, references](kb/05-analog-electronics/power-supplies-for-rf-and-analog.md)
- How much switching-regulator ripple gets through an LDO at 1–2 MHz, and why does PSRR fall with frequency?
- How noisy is an LDO (µV rms), and does it matter for my ADC, VCO or sensor?
- How big is a buck converter's output ripple, and why is it often larger than the formula says?
- How do supply ripple and noise show up as spurs next to my LO or transmitter carrier?
- How do I design an LC or ferrite-bead post-filter that does not resonate and make things worse?
- What happens to a 1S LiPo when a 2 W LoRa module draws 1 A+ bursts through a buck-boost — and to my sensor readings?
- What is ground bounce, and how big is it?
- Why must some RF amplifiers be powered up in a particular order?
- What makes a good voltage reference?
- How big a reservoir capacitor does my rectifier need, and why is a bridge better than a half-wave rectifier?
- What is the difference between a series and a shunt (Zener) regulator, and what does the capacitor across the Zener do?
- Should a transmitter run from a switching or a linear supply?
- How do I build a bench supply for a 2 W LoRa module?
- Which battery chemistry should I use, and how long will it last?
- Why does my flight computer reset when the radio transmits on a cold morning?

### [Active filters — Sallen-Key, MFB, state-variable/biquads, design tables, sensitivity, op-amp requirements, anti-alias design](kb/05-analog-electronics/active-filters.md)
- How do I design a 2nd-order low-pass with an op-amp, and what sets its $f_0$ and Q?
- Sallen-Key or multiple-feedback (MFB) — which should I use?
- How do I build a 4th-, 5th- or 6th-order Butterworth, Bessel or Chebyshev filter from 2nd-order sections?
- How sensitive is my filter to 1 % resistors and 5 % capacitors?
- How fast must the op-amp be (GBW) for a given filter?
- Why does my Sallen-Key low-pass "stop filtering" at high frequency?
- What order of anti-alias filter do I need in front of an ADC?
- When should I use a state-variable or biquad filter?

### [Low-noise analog design — the en–in model, optimum source resistance, noise figure of op-amp circuits, resistor and 1/f noise, noise bandwidth](kb/05-analog-electronics/low-noise-analog-design.md)
- How do I predict the noise of an amplifier from its $e_n$ and $i_n$ and the source resistance?
- What is the optimum source resistance, and can I "noise-match" by adding a resistor? (No — why?)
- What noise figure does an op-amp give with a 50 Ω source, and how do transformers or paralleled devices improve it?
- Why do my thick-film resistors make low-frequency noise when there is DC across them?
- What is kT/C noise and why does it limit sampling circuits?
- What is noise bandwidth and how do I convert a filter's −3 dB bandwidth into it?
- Why is a photodiode transimpedance amplifier's noise dominated by the op-amp's voltage noise, not the feedback resistor?
- Which amplifier (bipolar, JFET, CMOS) should I use for a 50 Ω, 1 kΩ, 100 kΩ or 10 MΩ source?

### [Analog signal conditioning — instrumentation amplifiers, bridges, level shifting, ADC front ends, input protection, sensor-line filtering, current sensing, isolation](kb/05-analog-electronics/analog-signal-conditioning.md)
- When do I need an instrumentation amplifier instead of an op-amp difference amplifier?
- How much CMRR do I get from 1 % or 0.1 % resistors?
- How much voltage does a strain-gauge or pressure bridge give, and why measure ratiometrically?
- How do I scale and shift a ±2.5 V (or 0–8.4 V battery) signal into a 3.3 V ADC?
- Why does my voltage divider read wrong on the MCU's ADC, and what capacitor fixes it?
- How do I protect an analog input from ESD, reverse voltage and over-voltage — and how can the protection diodes *back-power* my board?
- How should I pick a TVS for a battery or pyro rail?
- How do I filter RF out of long sensor wires without ruining the INA's CMRR?
- How do I measure pyro-channel current and igniter continuity reliably?
- When is galvanic isolation needed?
- How do I read a 4–20 mA sensor with a 3.3 V ADC, and how long can the cable be?
- Why does a remote sensor read wrong when the pyro or servo current flows, and how do differential lines fix it?
- What is the difference between a comparator and an op-amp, and when do I need hysteresis?
- How do I calculate Schmitt-trigger thresholds for a battery-low detector?
- How does a 555 timer set its frequency?

## 06-rf-circuits — RF building blocks

### [Low-noise amplifier (LNA) design](kb/06-rf-circuits/lna-design.md)
- What is the difference between transducer, available, operating and maximum available gain?
- What are noise parameters (Fmin, Γopt, Rn) and how do I use them?
- Why can't I have minimum noise figure and a perfect input match at the same time — and how do people get both?
- How do I draw noise circles and gain circles and choose a source impedance?
- How does inductive source degeneration give a real 50 Ω input without a noisy resistor?
- How do I design a discrete pHEMT LNA for 433 MHz or for GPS L1 (1575.42 MHz), step by step?
- Why does my LNA need a resistor or feedback if I want it stable?
- How much does inductor Q matter for LNA noise figure?
- Should the LNA go before or after the SAW filter?
- Does my LoRa ground station actually benefit from an LNA, and where should it go?
- Which ready-made LNA MMICs are good at 433 MHz and at GNSS L1?
- How much power will destroy an LNA, and how close can the rocket's transmitter be?
- What is induced gate noise, and why does a MOSFET have a nonzero minimum noise figure?
- How wide should the transistor in a CMOS LNA be for a given current budget?
- How do noise-cancelling (CG–CS / balun) wideband LNAs beat the 1 + γ/α limit of a common-gate input?

### [RF power amplifiers (classes A–F, load line, load-pull, Doherty, ET, DPD, thermal, ruggedness)](kb/06-rf-circuits/power-amplifiers.md)
- Why can a class A amplifier never exceed 50 % efficiency, and where does class B's 78.5 % come from?
- What do the class letters A, AB, B, C, D, E, F and inverse-F actually mean?
- Why is a PA not conjugately matched? What is the Cripps load line?
- What is load-pull, and why are the contours shaped like that?
- How do I pick the output matching network and harmonic filter for a 2 W 433 MHz transmitter?
- How do broadband (multi-octave) PAs work: resistive feedback gain blocks and transformer-coupled push-pull?
- What collector-to-collector load and transformer ratio does a push-pull HF PA need, and why does push-pull cancel even harmonics?
- How much harmonic suppression does a LoRa transmitter need to be legal?
- What is back-off, PAPR, and why does a QAM/OFDM PA run so inefficiently?
- How does a Doherty amplifier keep its efficiency at 6 dB back-off?
- What are envelope tracking and digital predistortion?
- Can a LoRa PA run saturated? (Yes — constant envelope.)
- How hot will my PA get, and what happens when the antenna breaks off (VSWR)?
- What sets the class-E component values, and why does the switch see 3.6 × Vcc?
- What is a Doherty offset line, and what happens if I get it wrong?
- What is class J, and why does it give class-B efficiency over an octave?
- How do I do load-pull on the bench without an automatic tuner?
- How do AM/AM and AM/PM turn into EVM, and why are my upper and lower IM3 products different?
- How much emitter ballast does a BJT PA need to avoid thermal runaway, and why does LDMOS quiescent current drift with temperature?
- What does neutralisation actually do to the transistor's two-port (stability, U)?
- Besides DPD, how else can a PA be linearised (feedforward, Cartesian feedback, LINC/outphasing, EER, envelope feedback), and when does each make sense?

### [Mixers (diode, Gilbert, passive FET, spurs, image rejection, IQ, harmonic and subsampling mixers)](kb/06-rf-circuits/mixers.md)
- How does multiplying two sine waves shift a signal in frequency, and why do I get both sum and difference?
- Why is a diode double-balanced mixer's conversion loss about 6 dB, and what is the theoretical minimum?
- What do "Level 7", LO drive, isolation and IP3 mean on a Mini-Circuits mixer data sheet?
- What is a spur chart, and which m × n products hurt a 433 MHz receiver with a 10.7 MHz IF?
- What is the image frequency and the half-IF spur?
- How does an image-reject (Hartley) or IQ mixer cancel the image, and how much imbalance can I tolerate?
- What is a Gilbert cell, and what limits its linearity?
- What are passive FET mixers and why are they used in modern CMOS radios?
- What is a harmonic mixer, and why does an anti-parallel diode pair mix with 2 × LO?
- Can I "mix" by sampling (subsampling), and what does it cost in noise?
- What is a conversion matrix, and why is a mixer a linear periodically time-varying (LPTV) circuit?
- Why does a passive switching mixer fold noise from 3·LO, 5·LO … into its output?
- How does a Tayloe (quadrature sampling) detector reach < 1 dB conversion loss, and what sets its bandwidth?
- Why does a 4-path mixer respond at 3·LO with the sidebands swapped?

### [RF filters — technologies (LC, helical, cavity, ceramic, SAW, BAW, LTCC) and microstrip/coupled-resonator design](kb/06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)
- Should my filter be LC, SAW, BAW, ceramic, helical, cavity or microstrip?
- Why can't I build a 1.7 MHz-wide 433 MHz filter from chip inductors?
- How does unloaded Q set a band-pass filter's insertion loss?
- How do Richards' transformation and the Kuroda identities turn a lumped filter into stubs and lines?
- How do I design a stepped-impedance microstrip low-pass or a parallel-coupled-line band-pass filter?
- Why does my microstrip coupled-line filter have a spurious passband at twice the centre frequency?
- What are coupling coefficients and external Q, and how do I extract them from an EM simulation?
- What is a coupling matrix and how do cross-couplings create transmission zeros?
- Why is my 2.45 GHz microstrip filter on FR-4 so lossy?
- What SAW filter should go in front of a GNSS or 433 MHz receiver, and what insertion loss should I expect?
- How do I get a coupling matrix from a specification with prescribed transmission zeros (Cameron's method)?
- Why do I have to re-synthesise all the couplings when I add a cross-coupling?
- Can a filter put a notch on Iridium right next to the GNSS band, and how much does resonator Q matter?
- What is an extracted-pole filter?
- How do I make a filter with flat group delay (linear phase)?
- Why does my SAW filter have ripple in its passband and group delay (triple-transit echo)?
- How does a YIG tunable filter work, and why does it not go below ~2 GHz?

### [Couplers, power dividers and combiners (Wilkinson, branch-line, rat-race, Lange, coupled-line, resistive)](kb/06-rf-circuits/couplers-dividers-combiners.md)
- How does a Wilkinson divider work, and why does it need a resistor between the outputs?
- Why can't a three-port be lossless, matched and reciprocal at the same time?
- How do I design a Wilkinson for 2.45 GHz in microstrip, or with lumped L and C at 433 MHz?
- How do I make an unequal (e.g. 2:1) power split?
- What are branch-line (90°) and rat-race (180°) hybrids used for?
- How do I feed a circularly polarised GNSS patch with a quadrature hybrid, and how good will the axial ratio be?
- What are coupling, directivity and isolation, and why is my microstrip coupler's directivity so poor?
- How do I sample a PA's output power with a directional coupler?
- What is a Lange coupler?
- When should I use a resistive splitter instead?
- How much power do I lose when combining two PAs that are not perfectly in phase — or when one fails?
- If the Wilkinson's lines are lossy, what resistor gives the best isolation?
- What happens if the two outputs see different loads, or are tied together into 25 Ω or 50 Ω?
- What happens when I combine two *uncorrelated* signals or noise sources in a Wilkinson? Does the resistor waste half?
- Does a Wilkinson combiner protect my PAs from a bad antenna?
- How does a Mini-Circuits-style transformer splitter work, and what sets its frequency range?
- What is a 180° hybrid transformer, and how is it related to the 0° splitter's resistor?
- Should a transmission-line-transformer hybrid be wound as a 25, 50 or 100 Ω pair, and how long can it be?
- How do I feed several receivers from one antenna without losing sensitivity (multicoupler)?
- Which splitter covers several octaves?

### [Baluns and RF transformers (lattice LC, Marchand, Guanella/Ruthroff TLTs, ferrite, chip baluns)](kb/06-rf-circuits/baluns-and-rf-transformers.md)
- Why does my transceiver (CC1101, SX126x RX input, AD9361, many mixers) have differential RF pins, and how do I connect it to a 50 Ω antenna?
- How do I design a lumped LC ("lattice") balun, and how wide is it?
- How does a Marchand balun work and what coupling does it need?
- What is the difference between a Guanella and a Ruthroff transformer, and why does one work to higher frequency?
- What do amplitude and phase imbalance specs mean for my system?
- What sets the low- and high-frequency limits of a ferrite transformer?
- Should I use a chip balun (e.g. Johanson) or discrete parts?
- What are mixed-mode S-parameters (Sdd, Scs, Sds)?
- Can I leave a balun footprint empty and bridge it with 0 Ω for a single-ended build?
- What do the dots on a transformer or balun mean, and what happens if I reverse one?
- Where should the balun sit relative to the chip?
- How do I feed an SA612/NE602: single-ended, through a balun, and how much LO?

### [RF switches, attenuators and limiters (PIN, FET/SOI, T/R switching, Pi/T pads, DSAs, LNA protection)](kb/06-rf-circuits/rf-switches-attenuators-limiters.md)
- How does a PIN diode act as an RF switch, and why does it need milliamps of bias?
- Series or shunt switch — which gives better isolation, and at what cost?
- What does "Ron × Coff" mean for a CMOS/SOI switch, and how does it set insertion loss and isolation?
- How does a quarter-wave T/R switch protect a receiver when transmitting?
- Which switch should go between a LoRa transceiver's PA and LNA and the antenna?
- How do I calculate Pi and T attenuator resistor values, and how much power does each resistor take?
- Why does an attenuator improve return loss?
- What is a digital step attenuator (DSA) good for?
- How do I protect an LNA from a nearby transmitter, and what are flat leakage and spike leakage?
- Why is an anti-parallel diode pair a poor limiter for a 0 dBm-rated GNSS LNA?

### [VCOs and PLL frequency synthesizers (integer-N, fractional-N, loop filters, phase noise, spurs, DDS)](kb/06-rf-circuits/vco-and-pll-synthesizers.md)
- How does a phase-locked loop turn a 25 MHz crystal into a clean 433.92 MHz or 3.5 GHz signal?
- What are Kvco, Kφ (charge-pump gain) and N, and how do they set the loop bandwidth?
- How do I design a passive loop filter for a given bandwidth and phase margin?
- Which noise sources dominate close to the carrier and far out, and what is the best loop bandwidth?
- What is the "normalised phase-noise floor" (PN_SYNTH, figure of merit) on a PLL data sheet?
- How does fractional-N work, and where does sigma-delta noise go?
- Where do reference spurs come from and how do I suppress them?
- How long does a PLL take to lock or hop?
- When should I use a DDS or a clock generator like the Si5351 instead?
- How does a VCO's resonator Q set its phase noise (Leeson)?
- What is the difference between a PLL and a DLL, and why do FPGAs have both?
- How fast can the loop be relative to the reference before the PFD's sampling makes it unstable (Gardner limit)?
- Why does a big frequency hop take much longer to lock than the linear model says (cycle slips)?
- How do I measure my PLL's loop bandwidth on the bench?
- How does two-point modulation let a PLL send FSK faster than its loop bandwidth?
- How well does a PLL follow an FMCW chirp, and what happens at the start of the ramp?
- What is an offset (translation) PLL and why is it quieter?
- Why does charge-pump mismatch raise in-band noise in a fractional-N PLL, and what does a bleed current do?

### [Receiver architectures (superheterodyne, dual conversion, zero-IF, low-IF, digital IF, direct RF sampling)](kb/06-rf-circuits/receiver-architectures.md)
- What is a superheterodyne receiver and how do I choose its IF?
- Why does a low IF make the image and the half-IF spur hard to filter?
- When is dual conversion worth it?
- What goes wrong in a zero-IF (direct-conversion) receiver — DC offset, flicker noise, LO leakage, IQ imbalance, second-order distortion?
- Why do LoRa chips (SX126x) and RTL-SDR tuners use a low IF?
- What does direct RF sampling require from the ADC and its clock?
- How do I check a frequency plan for spurs?
- What is reciprocal mixing and why does a strong nearby signal raise my noise floor?
- How does a superregenerative receiver (the XY-MK-5V 433 MHz module) work, and why is it so unselective?
- How far will a cheap FS1000A / XY-MK-5V OOK pair reach, and what do I gain with an RXB6 or CC1101?
- What should my first home-built radio be: crystal set, superregen, or a Tayloe SDR?
- What is inside a satellite-TV LNB, and can I use one (or the dish) with my SDR?
- Why does an offset dish look as if it points at the ground?
- How much power does a receiver need, and how do LoRa chips listen on microamps?
- Do receivers transmit? Can a transmitter tell whether anyone is listening?

### [Transmitter architectures (direct up-conversion, two-step, polar, IQ-modulator impairments, masks, spurs)](kb/06-rf-circuits/transmitter-architectures.md)
- How does an IQ (direct up-conversion) transmitter work, and what limits its spectral purity?
- What causes carrier (LO) leakage and the unwanted sideband, and how good must I and Q be?
- Why do direct-conversion transmitters get "pulled" by their own PA, and how is the VCO frequency planned to avoid it?
- When is a two-step (IF) transmitter better?
- How do polar (envelope-and-phase) and outphasing transmitters work, and what is hard about them?
- How does a LoRa/FSK transmitter differ from a QAM/OFDM one?
- What masks and spurious limits apply, and where do harmonics and spurs come from?

### [RF detectors and power meters (diode square-law detectors, log amps, RMS detectors, temperature effects)](kb/06-rf-circuits/detectors-and-power-meters.md)
- How does a Schottky diode turn RF into a DC voltage, and why is it "square-law" at low power?
- What is voltage sensitivity (mV/µW) and tangential signal sensitivity (TSS)?
- Where does the detector change from square-law to linear (peak) detection?
- How do log amplifiers (AD8307, AD8318) and RMS detectors (LTC5582) differ, and which should I use for a PA power/VSWR monitor?
- Why does my detector read differently for QPSK, 16-QAM or noise than for a CW tone of the same power?
- Why do diode detectors drift with temperature, and how are they compensated?

### [Frequency multipliers and dividers (class-C multipliers, push-push, diode/varactor/SRD, 20 log N, prescalers)](kb/06-rf-circuits/frequency-multipliers-dividers.md)
- How does a transistor or diode multiply a frequency, and how efficient can it be?
- What conduction angle maximises the 2nd or 3rd harmonic of a class-C multiplier?
- Why does a push-push doubler cancel the fundamental?
- Why does multiplying a frequency by N raise phase noise by 20 log N, and what is "carrier collapse"?
- Why does dividing a frequency lower phase noise, and where does it stop?
- How does a dual-modulus prescaler reach every divide ratio, and why do PLLs have a minimum N?
- What are step-recovery-diode comb generators, varactor multipliers and injection-locked dividers used for?

### [Circulators and isolators (ferrite gyrotropy, junction circulators, isolators, non-magnetic alternatives)](kb/06-rf-circuits/circulators-isolators.md)
- What does a circulator do, and why does it need a magnet?
- How can a circulator be lossless and matched when a lossless matched three-port is "impossible"?
- What is gyrotropy, the Polder tensor and Faraday rotation?
- How does a junction circulator work, and why are UHF circulators lumped-element?
- What does an isolator actually protect a PA from — and what VSWR does the PA still see if the antenna breaks?
- Can a circulator replace a T/R switch in a radar or a half-duplex radio?
- What are magnet-free (active or time-modulated) circulators?

### [Amplifier stability and biasing (K, Δ, μ, stability circles, bias networks, sequencing)](kb/06-rf-circuits/amplifier-stability-and-biasing.md)
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

### [AGC loops and receiver gain control — loop dynamics, attack/decay, digital AGC, gain plans, RSSI, and receiver DSP features (noise blanker, noise reduction, auto-notch)](kb/06-rf-circuits/agc-loops-and-receiver-gain-control.md)
- How does an AGC loop work, and how do I choose its attack and decay times?
- Why do AGC designs use "linear-in-dB" VGAs and log detectors?
- Why does my AGC oscillate or "pump", and how do I make it stable?
- How fast must an AGC be to catch a LoRa preamble?
- In a receiver with an LNA step and an IF VGA, which gain should I turn down first?
- How does a digital AGC in an SDR work, and how large can its step size be?
- How do AD9361, RTL-SDR and SX127x/SX126x chips control gain?
- How do I turn SX1276/SX1262 RSSI and SNR registers into a signal level in dBm, and how accurate is it?
- What do a noise blanker, noise reduction (NR) and an auto-notch (ANF) actually do, and why must the blanker come before the narrow filter?

### [PA control, protection and sequencing — ALC loops, ramping and key clicks, VSWR foldback, mismatch stress, T/R and bias sequencing, thermal limits, and class-D switching PAs](kb/06-rf-circuits/pa-control-protection-and-sequencing.md)
- What does ALC do on a transmitter, and why should it be idle for AFSK and other data modes?
- How do I design a power-control (ALC) loop, and why does it get slow or misbehave near saturation?
- Why does a transmitter "splatter" when it keys up, and what ramp time should I pick on an SX126x?
- How does VSWR protection (foldback) work, and how much does coupler directivity spoil the measurement?
- What actually happens inside a PA when the antenna breaks off or shorts: voltage, current, heat?
- Why must RF be delayed after keying an external amplifier or T/R relay (sequencing), and by how much?
- In what order do I bias a GaN or GaAs PA?
- How hot does a duty-cycled LoRa transmitter get, and when does thermal shutdown matter?
- What is a class-D RF amplifier (voltage-mode vs current-mode), and why is it rare at UHF?
- Why do old VHF amplifiers have an "SSB/FM" switch?

### [Duplexers, diplexers and crystal/ceramic IF filters — cavity and SAW/BAW duplexers, 433 + 915 MHz antenna sharing, crystal ladder design from motional parameters (Dishal/Cohn), monolithic and ceramic filters](kb/06-rf-circuits/duplexers-diplexers-and-crystal-filters.md)
- What is the difference between a duplexer and a diplexer, and when do I need either?
- How does a repeater's cavity duplexer get 70–80 dB of isolation with only 5 MHz between transmit and receive?
- Can a cavity notch filter knock out another team's transmitter 600 kHz from my channel?
- How do I share one antenna between a 433 MHz and a 915 MHz LoRa radio on the rocket or at the ground station?
- What is a crystal ladder filter, and how do I design one from cheap microprocessor crystals?
- How do I measure a crystal's motional capacitance and inductance without a crystal tester?
- Why does my crystal filter come out narrower than designed, and why are its skirts lopsided?
- What are shape factor and ultimate rejection?
- When do I use a monolithic crystal filter or a ceramic 10.7 MHz / 455 kHz filter instead?

### [Co-site interference and transmitter intermodulation — reverse IMD, desense by nearby transmitters, antenna isolation, launch-site frequency planning, and on-board 433/915 MHz + GNSS + Wi-Fi coexistence](kb/06-rf-circuits/co-site-interference-and-transmitter-intermod.md)
- Why does a transmitter produce intermodulation products when another transmitter is nearby ("reverse" or transmitter IMD)?
- How does a circulator or isolator at the transmitter output reduce that intermodulation?
- How far apart must two antennas be for a given isolation, horizontally and vertically?
- Another team at the launch site is transmitting 1 W a few hundred kHz from my channel. How far away must they be, and what can I do?
- Why can't a filter at my receiver remove a nearby transmitter's noise?
- How should several teams choose LoRa channels so that their intermodulation products don't land on each other?
- On one rocket with a 433 MHz LoRa, a 915 MHz LoRa, GNSS and an ESP32 with Wi-Fi, which combinations are dangerous?

### [Oscillator phase noise beyond Leeson — the Hajimiri–Lee ISF (LTV) theory, flicker up-conversion, AM–PM, microphonics and g-sensitivity](kb/06-rf-circuits/oscillator-phase-noise-ltv-isf.md)
- What does Leeson's formula leave out, and why are its F and flicker corner only "fitting parameters"?
- What is the impulse sensitivity function (ISF), and how does it predict phase noise from each noise source?
- Why is the 1/f³ corner of an oscillator's phase noise usually lower than the transistor's 1/f noise corner?
- Why do symmetric waveforms (matched rise and fall times) give lower close-in phase noise?
- Why is a Colpitts oscillator quieter than its transistor noise suggests (cyclostationary noise)?
- Why do some sources write Leeson with FkT/(2Ps) and others with 2FkT/Ps, and which should I use?
- How does amplitude noise turn into phase noise in a varactor-tuned VCO (AM–PM)?
- What are microphonics, and how do I keep my oscillator from "singing" on a vibrating rocket?
- How much phase noise does a crystal's g-sensitivity add under rocket vibration, at 433 MHz, 915 MHz, GPS L1 and 24 GHz?
- Does a PLL remove vibration-induced phase noise?

### [Modulator and detector circuits — varactor and reactance FM, PM modulators, balanced modulators and SSB, envelope and product detectors, synchronous AM, and FM discriminators (slope, Foster–Seeley, ratio, quadrature, PLL)](kb/06-rf-circuits/modulator-and-detector-circuits.md)
- How does a varactor or a "reactance modulator" make FM, and how linear is it?
- How do I make phase modulation, and what is the difference from FM in hardware?
- What is a balanced modulator, and how do the filter and phasing methods turn DSB into SSB?
- How do I choose R and C for a diode envelope detector, and what is diagonal clipping?
- What is a product detector and a BFO, and why does SSB need one?
- Why does synchronous AM detection survive selective fading when an envelope detector doesn't?
- How do Foster–Seeley, ratio, quadrature and PLL FM detectors work, and which rejects AM?
- How do these analog circuits map onto the one-line DSP demodulators in an SDR?

## 07-noise-linearity — 

### [Thermal noise and noise temperature](kb/07-noise-linearity/thermal-noise-and-noise-temperature.md)
- Where does the "−174 dBm/Hz" noise floor come from, and is it a law of nature?
- Why does a resistor make noise at all, and why does the available noise power not depend on its resistance?
- What is kTB and how much noise is there in a 125 kHz LoRa channel?
- What is "noise temperature", and why do people describe an amplifier with a temperature in kelvin?
- What is antenna noise temperature, and is my antenna noisier pointed at the ground or the sky?
- Why do HF radios not care about receiver noise figure but GNSS receivers care a lot?
- Why does a 3 dB cable in front of my receiver add exactly 3 dB of noise figure?
- When does the quantum (Planck) correction to thermal noise matter?
- Why does my spectrum analyzer show the noise floor 2.5 dB too low in log-average mode?
- How precisely can I measure an antenna temperature with an SDR, and how long do I need to integrate?
- What is a Dicke radiometer, and why switch between the antenna and a load?
- Can I see the Sun with a 433 MHz Yagi and an RTL-SDR, and how do I get G/T from it?
- How does a radio interferometer get fine resolution from small antennas?

### [Noise figure, noise temperature and the Friis cascade formula](kb/07-noise-linearity/noise-figure-and-friis.md)
- What exactly is noise figure, and how is it different from noise factor and noise temperature?
- Why must the LNA go first, right at the antenna?
- Why does 3 dB of cable in front of my LNA cost me 3 dB, but 3 dB of cable after it costs almost nothing?
- How do I compute the noise figure of a chain of amplifiers, filters, cables and mixers?
- Why does my mixer datasheet quote a "DSB" noise figure and why is the "SSB" one 3 dB worse?
- What are Fmin, Rn and Γopt, and why is the input match for lowest noise not the match for highest gain?
- What are noise circles?
- Can a noise figure be negative, or can a cascade be quieter than its first stage?

### [Phase noise and jitter](kb/07-noise-linearity/phase-noise-and-jitter.md)
- What does "−120 dBc/Hz at 100 kHz offset" actually mean?
- How do I convert an oscillator's phase-noise plot into RMS jitter in femtoseconds?
- What limits the SNR of an ADC sampling a 70 MHz or 433 MHz signal — and why is clock jitter the culprit?
- What is Leeson's model, and why does oscillator phase noise fall at 30, then 20 dB/decade, then flatten?
- What is reciprocal mixing, and how does a strong nearby transmitter "deafen" my LoRa receiver through the LO?
- Why does multiplying a frequency by N raise phase noise by 20 log N?
- How does a PLL shape phase noise?
- How much does phase noise hurt OFDM EVM and FMCW radar?

### [Nonlinearity — harmonics, compression (P1dB), intercept points (IP2/IP3) and intermodulation](kb/07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)
- What is the 1 dB compression point, and why does gain drop at high input power?
- What is IP3 (third-order intercept point), and why do IM3 products rise 3 dB for every 1 dB of input?
- Is IIP3 always P1dB + 9.6 dB? Why do datasheets disagree with that rule?
- What is the difference between input-referred (IIP3) and output-referred (OIP3) figures?
- Which frequencies do intermodulation products land on — and can two other teams' transmitters create a signal on *my* channel?
- How do I compute the IIP3 of a chain of LNA + filter + mixer + ADC?
- What are IP2, cross-modulation and AM–PM conversion, and when do they matter?
- How do I measure IP3 without measuring my test setup instead?
- Why does IM3 change with tone spacing, and why are the lower and upper IM3 products sometimes different?
- What is a Volterra series, and how is the DPD memory polynomial related to it?

### [Dynamic range, SFDR, blocking, desensitisation, selectivity and AGC](kb/07-noise-linearity/dynamic-range-sfdr-blocking.md)
- What is spurious-free dynamic range (SFDR) and why is it "two-thirds of IIP3 minus the noise floor"?
- What is the difference between blocking, desensitisation, adjacent-channel rejection and selectivity?
- Why can a transmitter on the same mast stop my receiver even though it is on a different channel?
- How does an ADC's SNR translate into a noise figure, and how much gain do I need in front of an SDR's ADC?
- What does "processing gain" of an oversampling ADC mean?
- What is AGC for, and what does it cost?
- How do I read the SX1262 blocking and ACR numbers?
- How can billions of radio signals share the air without interfering with each other?
- Why does a nearby transmitter on a completely different frequency still knock out my receiver?
- What does a classic communications receiver have that a cheap SDR does not?

### [Receiver cascade analysis (gain, NF, IIP3, P1dB budget)](kb/07-noise-linearity/receiver-cascade-analysis.md)
- How do I build a stage-by-stage budget for a receiver (gain, noise figure, IIP3, compression)?
- Where should the LNA, the SAW filter and the long cable go on a LoRa ground station?
- How much does each stage contribute to the total noise, and which stage limits linearity?
- What does a "level diagram" show, and how do I check headroom for a strong interferer?
- How does a GNSS active antenna chain work out, and what C/N0 should I expect?
- Is there a script I can reuse for my own chains?

### [Shot noise, flicker (1/f) noise and other non-thermal noise](kb/07-noise-linearity/shot-and-flicker-noise.md)
- What is shot noise and why is it $2qI$?
- Does a resistor carrying DC have shot noise?
- What is 1/f (flicker) noise, and what is a "flicker corner frequency"?
- Why do zero-IF (direct-conversion) receivers struggle with narrow channels like LoRa?
- Why does an oscillator's phase noise get steeper (1/f³) close to the carrier?
- Why does integrated 1/f noise never "settle", and what is the link to the bias-instability floor of an IMU?
- What are popcorn (burst) noise and generation–recombination noise?

### [Receiver sensitivity and minimum detectable signal (MDS)](kb/07-noise-linearity/sensitivity-and-mds.md)
- How do I calculate a receiver's sensitivity from its noise figure and bandwidth?
- What is the difference between sensitivity, noise floor and MDS?
- How can LoRa receive signals *below* the noise (negative SNR)? Doesn't that break physics?
- Why does each LoRa spreading-factor step give ~2.5 dB more sensitivity?
- Is the EBYTE datasheet's "−147 dBm at 2.4 kbps" believable?
- What sensitivity does my ground station really have at the antenna connector?
- How do GNSS sensitivity figures like "−167 dBm tracking" relate to C/N0?
- What does S9 mean in dBm and microvolts, and how many dB is one S-unit?

### [Volterra series and weakly nonlinear analysis — kernels, the method of nonlinear currents, IIP3 with memory, AM–PM, behavioural PA models and DPD](kb/07-noise-linearity/volterra-series-and-nonlinear-analysis.md)
- What is a Volterra series, and how is it different from the power series $y=a_1x+a_2x^2+a_3x^3$?
- How do I compute IM3 and IIP3 of a circuit with capacitors, inductors and feedback, where the "coefficients" depend on frequency?
- What is the method of nonlinear currents?
- Why does an amplifier's IM3 change with tone spacing, and why are the lower and upper IM3 products sometimes unequal?
- Why can emitter or source degeneration make IM3 almost vanish (a "sweet spot")?
- When does the power-series / Volterra model stop being valid?
- What is AM–PM conversion physically, and how does it come out of the Volterra kernels?
- What are the Saleh, Rapp and memory-polynomial models, and how do they relate to digital predistortion?
- Why does my two-tone IIP3 measurement change when I change the tone spacing?
- Does a constant-envelope LoRa transmitter need any of this?

## 08-antennas — 

### [Antenna fundamentals — pattern, directivity, gain, efficiency, aperture, impedance, bandwidth](kb/08-antennas/antenna-fundamentals.md)
- What does an antenna actually do, physically?
- What is the difference between directivity, gain, and realized gain?
- If an antenna has "5 dBi gain", does it amplify my signal?
- What is dBi, dBd, dBic, and how do I convert between them?
- Why does a half-wave dipole have 2.15 dBi and a short dipole 1.76 dBi?
- What is effective aperture, and why is it λ²G/4π for every antenna?
- Why do bigger antennas at low frequency "catch more signal"?
- What is radiation resistance and how is it different from input impedance?
- What are radiation efficiency, mismatch efficiency and total efficiency?
- How do I estimate gain from a beamwidth on a datasheet?
- What does "antenna bandwidth" mean — VSWR, gain, axial ratio, pattern?
- Is an antenna's receive pattern the same as its transmit pattern (reciprocity)?
- How do I calculate EIRP and ERP for my LoRa transmitter?
- Does a good SWR mean my antenna is efficient?
- Does a longer antenna always mean more gain?
- Can I use a 2.4 GHz antenna at 900 MHz (or a 433 MHz antenna at 868/915 MHz)?
- Must an antenna be resonant to radiate well?
- For a receive-only SDR, does the antenna matter?

### [Dipoles and monopoles — current distribution, impedance, shortening, ground planes, practical variants](kb/08-antennas/dipoles-and-monopoles.md)
- Why is a half-wave dipole 73 Ω, and where does the +j42.5 Ω come from?
- How long should I actually cut a 433 MHz or 915 MHz dipole, and why is it shorter than λ/2?
- Does wire thickness change the resonant length and bandwidth?
- Why is a quarter-wave monopole 36.5 Ω, and why does mine measure something else?
- What happens to a λ/4 whip on a small flight-computer board with no real ground plane?
- Why do ground-plane antennas use drooping radials, and what angle gives 50 Ω?
- What is a folded dipole and why is it ~300 Ω? What if the two conductors are different diameters?
- What are sleeve dipoles, J-poles and end-fed half-waves (EFHW), and why a 49:1 transformer?
- How do loading coils and top hats shorten a monopole, and what does it cost in efficiency?
- Why does my dipole's SWR change when I move the coax?
- Does the metal (copper, aluminium, steel, copper tape, conductive filament) change the resonant length or the efficiency?
- How high is the voltage at the tips of a dipole at a given power?
- How does the feed-point impedance change if I move the feed along the antenna (OCF)?
- What happens if I bend or fold the tips of the elements?
- Can an antenna be modelled as an R, L, C circuit?
- How do collinear antennas work, and what are the coils along a vertical for?
- Is a longer whip or a full-wave antenna always better?
- How do handheld radio antennas work without a ground plane, and are aftermarket HT antennas better?
- How does a mag-mount antenna get a ground plane through the paint?
- Why do some antennas have a DC path to ground and some not?
- How do I calculate the mutual impedance between two parallel dipoles, and what does it do to their feed impedance?
- Where should the loading coil go on a short whip: base, centre or top?
- How much bandwidth does a fatter element buy?

### [Loop antennas — small loops, magnetic (transmitting) loops, full-wave loops, ferrite rods, receive-only loops](kb/08-antennas/loop-antennas.md)
- How does a small loop radiate, and why is its radiation resistance so tiny?
- Why is a small loop's efficiency so sensitive to conductor size?
- What is a "magnetic loop" (small transmitting loop) and why does it need a huge-voltage capacitor?
- How is a full-wavelength loop different from a small loop?
- Why do AM radios use ferrite rods, and why are they receive-only?
- When is a small loop a good receive antenna despite terrible efficiency?
- Are PCB loop antennas at 433 MHz (key fobs) any good?
- Is my active loop or mini-whip limited by the sky noise or by its own amplifier?
- Why does my cheap active loop (MLA-30) show ghost stations, hum or a high noise floor?
- How long must an active whip be at a quiet site?
- How does a sense antenna turn a loop's figure-8 into a cardioid?
- Can I receive LF time signals (DCF77, JJY, BPC) in Singapore, and with what antenna?

### [Microstrip patch antennas — models, design equations, feeds, bandwidth, efficiency, circular polarization](kb/08-antennas/patch-antennas.md)
- How does a flat square of copper over a ground plane radiate?
- How do I calculate the width and length of a patch for 2.45 GHz on FR-4, or for GNSS L1 on Rogers?
- Why is my FR-4 patch's gain only ~2 dBi when the textbooks say 6–7 dBi?
- Why is patch bandwidth only 1–3 %, and how do I widen it?
- Where do I put the feed so it is 50 Ω (inset depth, probe position)?
- What are surface waves and why do thick, high-εr substrates lose efficiency?
- How do truncated-corner patches make circular polarization, and how big should the truncation be?
- What is the difference between probe, inset, aperture-coupled and proximity-coupled feeds?
- Can I make a 915 MHz or 433 MHz patch for a ground station or a rocket?
- How do I verify a patch design in openEMS before ordering boards?

### [Helical antennas — normal and axial mode, realistic axial-mode gain (Kraus vs King & Wong vs Emerson), quadrifilar helix](kb/08-antennas/helical-antennas.md)
- What is the difference between a normal-mode and an axial-mode helix?
- How do I design an axial-mode helix for 435 MHz or 2.4 GHz?
- Why do calculators say my 10-turn helix has 16–17 dBi when it measures ~13 dBic?
- Which formula for helix gain should I trust — Kraus, King & Wong, or Emerson?
- How big a ground plane does a helix need?
- How do I match a helix (≈100–150 Ω) to 50 Ω?
- Which winding direction gives RHCP?
- What is a quadrifilar helix (QFH) and why is it used for weather satellites and some GNSS antennas?
- Is a helix a good ground-station antenna for a rolling rocket?

### [Yagi-Uda and log-periodic dipole antennas — how parasitic arrays work, DL6WU design, 433/915 MHz ground-station Yagis, LPDA design](kb/08-antennas/yagi-uda-and-log-periodic.md)
- How can un-driven metal rods (directors, reflector) make an antenna directional?
- Why is the reflector longer and the directors shorter than the driven element?
- How much gain do I get per metre of boom, and why does it grow so slowly?
- How do I design a 433 MHz or 915 MHz Yagi for a rocket ground station (DL6WU method)?
- Does a metal boom change the element lengths? By how much?
- Why is a 3-element Yagi's feed impedance so low and how do I match it?
- How accurately must I cut the elements?
- How do I stack two Yagis, or make a circularly polarized crossed Yagi?
- What is a log-periodic dipole array (LPDA), and how do I choose τ and σ?
- Should I use a Yagi or an LPDA for a ground station?
- How does a corner reflector work, and is it a better ground-station antenna than a Yagi?
- In a 2-element Yagi, is the parasitic element better as a reflector or a director?
- What are front-to-back, front-to-rear and front-to-side ratios?
- Which stacking distance is right: 51/HPBW or λ/(2 sin(B/2))?

### [Horn, reflector and aperture antennas — aperture efficiency, optimum pyramidal horn, parabolic dish gain, taper vs spillover, feeds](kb/08-antennas/horn-reflector-aperture-antennas.md)
- Why is the gain of a big aperture antenna ≈ 4πA/λ² times an efficiency?
- What is aperture efficiency, and why is a dish only 55–70 % efficient?
- How do I design an optimum-gain pyramidal horn for 5.8 or 10 GHz?
- How much gain does a 1.2 m dish give at 2.45 or 5.8 GHz?
- What is the trade-off between illumination taper and spillover, and what edge taper is optimum?
- How do f/D and the feed pattern go together?
- How big must a "cantenna" (circular waveguide feed) be for 2.4 GHz?
- How much does surface roughness of a dish cost (Ruze)?
- Why does a prime-focus dish reverse circular polarization?
- What are waveguide irises and cross-shaped irises, how does a horn polariser make circular polarisation, and how is a patch antenna trimmed after etching?

### [PCB and chip antennas — IFA, PIFA, meandered monopoles, chip antennas, ground-plane dependence, matching, module placement](kb/08-antennas/pcb-and-chip-antennas.md)
- How does an inverted-F (IFA) antenna work, and why is there a short to ground next to the feed?
- Can I just copy TI's 2.4 GHz or 868/915 MHz PCB antenna? What must match?
- Why does my chip antenna perform far worse than its datasheet?
- How big must the ground plane be, and what is the "keep-out" area?
- How do I design the pi-matching network, and what do I measure to tune it?
- Where should an ESP32 module (with PCB antenna) go on my board?
- Is a PCB antenna viable at 433 MHz on a flight computer?
- PIFA vs IFA vs meandered monopole vs chip — which do I choose?
- How close can an antenna be to metal (an enclosure, a battery, a carbon-fibre tube)?
- Which antennas work on or inside metal?
- How do I make one PCB antenna cover 315 and 433 MHz?

### [GNSS antennas — RHCP patches and helices, active antennas, ground planes, axial ratio, phase centre, multipath, and GNSS on rockets](kb/08-antennas/gnss-antennas.md)
- Why are GNSS antennas right-hand circularly polarized?
- Patch or helix — which should I use for GPS/Galileo on a flight computer or a rocket?
- What does an "active antenna" add, and how much LNA gain do the ZED-F9P and MAX-M10S want?
- Why does my GNSS patch perform badly on a small board, or inside a rocket body?
- How big should the ground plane be?
- What are axial ratio and phase-centre variation, and why do RTK users care?
- What bands do L1/L2/L5 and E1/E5b/B1/B2 occupy, and does my antenna cover them?
- Why does my GNSS lose satellites when the LoRa transmitter keys up?
- Is a chip antenna good enough for GNSS?

### [Antenna matching and baluns — common-mode current, chokes, sleeve and coax baluns, Guanella/Ruthroff, ferrite mixes, measuring CM current](kb/08-antennas/antenna-matching-and-baluns.md)
- Why does my antenna's SWR change when I touch or move the coax?
- What is common-mode current on a coax, and where does it come from?
- Do I need a balun on a dipole? On a Yagi? On a monopole?
- Current balun vs voltage balun — what is the difference, and which is better?
- How does a λ/4 sleeve ("bazooka") balun work, and how long should it be at 433 or 915 MHz?
- How does a λ/2 coax 4:1 balun match a folded dipole?
- Which ferrite mix should I use (31, 43, 61) and how much choking impedance is "enough"?
- How do I measure common-mode current or the impedance of a choke?
- How are Yagi driven elements matched (gamma, hairpin, T-match)?
- Can I use an SMD common-mode choke (USB-type) on a 433/915 MHz antenna feed?
- Coax wound on a toroid, bifilar wire on a toroid, or coiled coax in air: which choke is best?
- Where along the feeder should the choke(s) go?

### [Antenna measurement — S11 and what it hides, far-field distance, ranges, gain (comparison and three-antenna), efficiency (Wheeler cap), polarization, DIY SDR pattern measurement](kb/08-antennas/antenna-measurement.md)
- What does an S11/SWR measurement tell me about my antenna, and what can it not tell me?
- How far away must the test antenna be for a valid gain or pattern measurement?
- How do I measure gain without a calibrated reference antenna (three-antenna method)?
- How do I measure radiation efficiency of a small antenna (Wheeler cap)?
- How do I measure axial ratio and polarization sense?
- Can I measure a pattern in my backyard with an SDR, and how accurate is it?
- Why do my range-test RSSI numbers jump around by ±5 dB?
- How do I avoid the test cable becoming part of the antenna?
- What is my ground-station Yagi's antenna temperature, and how does it change with elevation?
- Does pointing the Yagi up at the rocket lower the noise, and does it matter without an LNA?

### [Antennas on rockets — placement, airframe materials, axial nulls, roll, plume attenuation, recovery phase, ground-station choices](kb/08-antennas/antennas-on-rockets.md)
- Where should I put the 433/915 MHz telemetry antenna on my rocket?
- Can I put the antenna inside a fibreglass nose cone? Inside a carbon-fibre or aluminium body tube?
- Why do I lose telemetry near apogee when the rocket is straight above the ground station?
- Why does the signal fade periodically when the rocket rolls?
- Should the ground station use a Yagi, a helix, or a crossed Yagi, and which polarization?
- Does the motor plume block the signal during boost?
- What happens to the link under the parachute and after landing?
- How much does a nose cone detune the antenna?
- What do professional sounding rockets use (wraparound, blade, quadraloop)?
- How do I keep the 2 W LoRa transmitter from deafening the GNSS receiver?

### [Electrically small antennas — Wheeler, Chu, McLean limits; efficiency–bandwidth trade-off; fractal and "tiny antenna" claims](kb/08-antennas/small-antenna-limits.md)
- Why can't I make a tiny 433 MHz antenna that is efficient *and* wideband?
- What is the Chu limit, and what exactly does "ka" measure?
- What is the difference between Chu's, Hansen's and McLean's Q formulas?
- How much bandwidth can a chip antenna at 915 MHz possibly have?
- Why does a lossy small antenna look "wideband"?
- What is Wheeler's radiansphere?
- Do fractal antennas beat the limit? What about "nano" or crowdfunded "tiny long-range" antennas?
- Can a small antenna be directional (superdirective)?
- Does a matching network fix a small antenna's bandwidth?

### [Antenna polarization and circular polarization — axial ratio, IEEE handedness, generating CP, polarization loss factor](kb/08-antennas/antenna-polarization-and-circular-polarization.md)
- What is the polarization of an antenna, and how is it defined when receiving?
- What does RHCP actually mean — clockwise from where?
- What is axial ratio, and how does it relate to cross-polarization?
- How much signal do I lose with a linear antenna receiving a circularly polarized signal, or two linear antennas at an angle?
- Why does reflection turn RHCP into LHCP, and why does that help GNSS reject multipath?
- How do I make circular polarization (crossed dipoles, patches, helices)?
- My rocket rolls — should the ground station be circularly polarized?
- What is "spin Doppler"?
- Is a truly isotropic antenna possible, and what does the hairy-ball theorem have to do with it?
- Which fixed circularly polarized antenna covers a rocket overhead without tracking: turnstile, eggbeater or Lindenblad?
- When is an omni-CP antenna better than a crossed Yagi for a ground station?

### [Antenna simulation — NEC-2/MoM for wire antennas, openEMS/FDTD for patches and PCB antennas, modelling rules and verification](kb/08-antennas/antenna-simulation-nec-openems.md)
- Which tool should I use for a Yagi, a whip, a patch, a PCB antenna, or an antenna inside a nose cone?
- How does NEC work, and what are its segmentation rules?
- What can NEC-2 not model (dielectrics, PCBs, stepped-diameter elements)?
- What is the average gain test and why should I always check it?
- How do I set up a patch or PCB antenna in openEMS (mesh, ports, boundaries, NF2FF)?
- How do I know my simulation is right (convergence, cross-checks)?
- What do 4nec2, xnec2c, NEC2++/PyNEC, MMANA-GAL and EZNEC differ in?
- Why does my 433 MHz antenna resonate at a completely different frequency (e.g. 1.4 GHz) in simulation?
- What are Pocklington's and Hallén's equations, and how do they become a MoM matrix?
- Why does the dipole current come out as a sine wave, and when does that fail?
- Why do short-dipole impedances change when I use very short segments?

### [Slot antennas — Babinet's principle, slots in ground planes, cavity-backed and microstrip-fed slots, slotted-waveguide arrays, PCB slots at 2.4/5.8 GHz](kb/08-antennas/slot-antennas.md)
- What is a slot antenna and how can a hole in metal radiate?
- What is Babinet's principle, and why is a slot's impedance η²/(4·Z_dipole)?
- Why is a resonant half-wave slot about 500 Ω instead of 73 Ω, and how do I feed it with 50 Ω?
- Is a slot horizontally or vertically polarized?
- How does Wi-Fi work in a full-metal laptop (or through a metal rocket airframe)?
- How long should a 2.45 GHz slot in the copper of an FR-4 board be?
- How does a microstrip-fed slot work, and what is aperture coupling in a patch antenna?
- What does cavity-backing a slot do to its impedance and pattern?
- Why are the slots in a slotted-waveguide array offset alternately either side of the centreline?
- How do I design a slotted-waveguide omni for 10 GHz, and how critical are the dimensions?
- Why can a seam or cooling slot in my shielded enclosure leak RF?
- Can I make a 915 MHz antenna on my flight-computer board without a copper keep-out area?
- Is a slot antenna wideband?
- Can I simulate a slot antenna in NEC?

### [HF wire antennas — random/long wires and ununs, EFHW, fan and trap dipoles, inverted-V, G5RV and OCF, NVIS, verticals and ground loss](kb/08-antennas/wire-antennas-hf-random-wire-fan-dipole.md)
- What is a "random wire" or long-wire antenna, and why does it need a tuner or a 9:1 unun?
- Which random-wire lengths should I avoid, and do the published "magic lengths" really work?
- What is the difference between an end-fed half-wave (EFHW) and a random wire?
- Will dipoles of different lengths joined at one feed (fan dipole) work on several bands? What if they are at right angles?
- How does a trap dipole work, and how lossy are the traps?
- What happens to the impedance when I droop a dipole into an inverted-V?
- What is a G5RV, and is it really a multiband antenna without a tuner?
- How does moving the feed point off-centre (OCF/Windom) change the impedance, and why do OCFs skip some bands?
- What is NVIS, and how high should a dipole be for it?
- How much power does a vertical lose to the ground, and do radials help?
- Can I turn a metal clothesline into an antenna?
- Why does an antenna tuner not make a bad antenna good?
- How does a linked dipole work, and do the open links really disconnect the outer wires?
- Can I feed an OCF with ladder line and a tuner, and why is there RF on the feeder?
- How does a shortened (loaded) EFHW work, and what does the coil cost on 80 m?
- What do EFHW patterns look like on the harmonic bands?
- Why is there RF in the shack with my end-fed, and where do the chokes go?
- What is a Beverage, what is RDF, and why is a receive antenna judged by directivity, not gain?
- Can a hidden thin wire work as a receive antenna?

### [Inductive coupling — mutual inductance, coupling coefficient, resonant links and the k²Q₁Q₂ limit; RFID (LF/HF/UHF), NFC antenna design and matching, Qi wireless power](kb/08-antennas/inductive-coupling-rfid-nfc-wpt.md)
- How do two coils "talk" or transfer power without radiating, and why is this not an antenna in the usual sense?
- How do I calculate the mutual inductance of two coils (Neumann formula, coaxial loops)?
- What is the coupling coefficient k, and how fast does it fall with distance?
- Why does making both coils resonant help so much, and what is the maximum link efficiency?
- Where does η_max = U²/(1+√(1+U²))² with U = k√(Q₁Q₂) come from?
- How did the MIT "WiTricity" experiment get 40 % efficiency at 2 m?
- How do I design and match a 13.56 MHz NFC/RFID reader antenna (inductance, Q, damping resistor, EMC filter, C1/C2)?
- Why must an NFC antenna's Q be limited to about 20–35?
- How far can an NFC reader read, and what coil size is best for a given distance?
- How do 125 kHz LF tags and 860–960 MHz UHF RFID tags differ from NFC?
- How does a Qi wireless charger work, and what are its coil values?
- Does metal or a ferrite sheet behind an NFC antenna help or hurt?
- How do I build my own RFID reader?
- Can I harvest useful power from ambient RF or from a far-away transmitter?

### [Lens, reflectarray and transmitarray antennas — dielectric lenses for mm-wave radar, Luneburg lenses, zoning, phase quantisation, why lenses are rare below mm-wave](kb/08-antennas/lens-and-reflectarray-antennas.md)
- Why don't we use lenses for RF the way we do for light?
- Can I put a 3D-printed lens in front of my 24 GHz or 77 GHz radar module, and how much gain does it add?
- How is a dielectric lens shaped, and how thick is it?
- What is a Luneburg lens and why is it used for radar reflectors?
- What are zoned (Fresnel) lenses and zone plates?
- What is a reflectarray / transmitarray and how does it differ from a dish or a phased array?
- How much gain do I lose with 1-bit or 2-bit element phases?
- What limits the bandwidth of a reflectarray?

### [Multiband and wideband antennas — biconical, discone, bow-tie, Vivaldi/tapered slot, spirals, LPDA, sleeve monopoles, traps and parasitics, wideband SDR receive antennas](kb/08-antennas/multiband-and-wideband-antennas.md)
- What makes an antenna wideband, and what is a "frequency-independent" antenna?
- What is the difference between a multiband antenna and a wideband one?
- How does a discone work, how do I dimension one, and is it really 25–1300 MHz?
- Why does my discone receive well at some frequencies and poorly at others?
- What impedance does a biconical or bow-tie antenna have, and why are self-complementary antennas 188 Ω?
- How does a Vivaldi (tapered-slot) antenna work, and how big must it be for 1–10 GHz?
- What sets the band of a spiral antenna?
- When should I use an LPDA instead of a discone or a Yagi?
- How do traps, parallel elements and parasitic resonators make an antenna multiband?
- For receive-only SDR, does antenna length or efficiency matter?
- What is a good wideband antenna for an RTL-SDR?
- Can I use one antenna for 433 MHz and 915 MHz?

### [Antenna identification guide — recognising antenna types in the wild, estimating the band from element length, and why stock antennas should be measured](kb/08-antennas/antenna-identification-guide.md)
- What is that antenna on the roof / mast / tower / device, and what is it for?
- How can I tell an antenna's frequency band from its size?
- What do rubber ducks, whips, dipoles, Yagis, LPDAs, discones, patches, helices, QFHs, collinears, J-poles, chip antennas, cellular panels, dishes, horns and mag-mounts look like, and what gain and pattern do they have?
- Why is a "6 dBi" omni a long fibreglass stick?
- What is the box with rectangular panels on a cell tower (and is it safe near my window)?
- Is the antenna that came with my LoRa/Meshtastic/radio module actually tuned to the right band?
- What SWR is "good enough" for a stock antenna, and how much does a bad one cost?

## 09-propagation-link-budget — 

### [Friis transmission equation and free-space path loss](kb/09-propagation-link-budget/friis-free-space-path-loss.md)
- How much power does a receiving antenna collect from a transmitter a known distance away?
- Where does the free-space path loss formula come from, and what are the constants 32.45, 92.45 and −147.55?
- Do higher frequencies really "attenuate more" in free space?
- Is 433 MHz or 915 MHz better for range, all else equal?
- What are EIRP and ERP, and how do they convert?
- How do I convert between received power, power flux density and field strength (dBµV/m)?
- When is the Friis equation not valid (near field, ground, obstructions)?

### [Link budget methodology (with the 433 MHz and 915 MHz rocket downlinks)](kb/09-propagation-link-budget/link-budget-methodology.md)
- How do I write a link budget line by line, and what belongs in each line?
- How far will my E22-400T33D (433 MHz, 2 W) downlink reach to a ground Yagi at 30 km?
- How does the 915 MHz 1 W E220-900T30D secondary link compare?
- What is G/T and how does the C/N0 / Eb/N0 form relate to the dBm form?
- How much fade margin should I leave, and for what?
- Why do my "10 000 km" free-space ranges not match reality?
- Does the rocket's exhaust plume block the signal?

### [Fresnel zones, line of sight, earth curvature and the radio horizon](kb/09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)
- What is a Fresnel zone, and why does "I can see the other antenna" not guarantee a free-space link?
- How big is the first Fresnel zone on a 433 MHz or 915 MHz link?
- What is the "60 % clearance" rule and where does it come from?
- How far is the radio horizon, and what is the 4/3-earth (k-factor) model?
- At what altitude will my descending rocket drop below the horizon or below Fresnel clearance?
- How high must my ground-level LoRa antennas be for a clear path?
- What are super-refraction and ducting, and do they matter in Singapore?
- Why is the VHF/UHF radio horizon farther than the visual horizon?

### [Two-ray ground reflection, plane-earth loss and antenna-height effects](kb/09-propagation-link-budget/two-ray-ground-reflection.md)
- Why does path loss near the ground grow at 40 dB per decade instead of 20?
- What is the breakpoint (critical) distance, and why does raising an antenna help so much?
- Why does the signal from a climbing rocket fade in and out every few seconds at the ground station?
- Does polarisation matter for ground reflection? What is the Brewster angle?
- Why is a landed rocket so hard to hear, and does it matter which way it is lying?
- What is the "minimum effective antenna height"?
- How rough does the ground have to be before the reflection stops mattering?

### [Empirical and semi-empirical path-loss models (log-distance, Hata, COST-231, Egli, ITU-R P.528/P.1546/P.1812/P.1411/P.452, Longley–Rice)](kb/09-propagation-link-budget/empirical-path-loss-models.md)
- When should I use free space, plane earth, Hata, Egli, Longley–Rice or an ITU-R method?
- What model applies to a rocket-to-ground link (air-to-ground)?
- What model applies to ground-level LoRa between two people or nodes?
- What is the log-distance model with shadowing, and what path-loss exponents are typical?
- Why do different "calculators" give answers 20 dB apart for the same link?
- What are the validity limits of Okumura–Hata, and what happens when I use it for 2 m antennas?

### [Multipath fading, delay spread and Doppler (including rocket Doppler vs LoRa)](kb/09-propagation-link-budget/multipath-fading-doppler.md)
- What are Rayleigh and Rician fading, and what is the K-factor?
- How much fade margin do I need for 99 % or 99.9 % reliability?
- What are delay spread and coherence bandwidth, and is LoRa affected by multipath?
- What Doppler shift does a Mach 3 rocket produce at 433 MHz, and can LoRa handle it?
- Why can the *rate of change* of Doppler during boost break a LoRa link even when the shift itself is fine?
- How often do fades happen and how long do they last?
- How much does diversity (two antennas, two frequencies, two polarisations) help?
- What is "picket fencing" on a mobile VHF signal, and why does moving the antenna a few feet change the signal so much?

### [Atmospheric gases, rain, fog, vegetation and building attenuation](kb/09-propagation-link-budget/atmospheric-rain-attenuation.md)
- Does the atmosphere or rain attenuate my 433/915 MHz telemetry?
- Why are 22 GHz and 60 GHz "bad" frequencies for long links, and why is 60 GHz used for short-range radios?
- How much does heavy tropical rain attenuate a 24 GHz or 77 GHz radar?
- Does fog or cloud matter?
- How much loss do trees add if the rocket lands in a forest?
- How much signal do I lose if my ground station is indoors?
- Do higher frequencies penetrate walls better than lower ones?

### [The ionosphere — HF skywave, MUF, NVIS, Faraday rotation, scintillation and GNSS delay](kb/09-propagation-link-budget/ionospheric-hf-propagation.md)
- Does the ionosphere affect my rocket's 433/915 MHz telemetry?
- Why does HF (3–30 MHz) travel thousands of km while UHF does not?
- What are the critical frequency, the MUF and the skip zone?
- What is NVIS and when is it used?
- What is Faraday rotation, and why do satellite links at VHF/UHF use circular polarisation?
- What is ionospheric scintillation, and is Singapore affected?
- How much ionospheric error does GNSS see, and how do dual-frequency receivers remove it?
- What are the ordinary and extraordinary waves, and why does a vertical or a horizontal antenna both work for HF skywave?
- What is the "critical angle"?

### [Diffraction — knife-edge, rounded obstacles and multiple edges (Deygout, Epstein–Peterson, Bullington)](kb/09-propagation-link-budget/diffraction-knife-edge.md)
- How much signal do I lose when a hill or building blocks the line of sight?
- What is the Fresnel–Kirchhoff parameter $v$, and how do I compute it?
- Why is there 6 dB of loss even when the obstacle just grazes the line of sight?
- How good is the ITU-R P.526 approximation to the exact knife-edge loss?
- How do I handle two or more ridges (Deygout, Epstein–Peterson, Bullington), and why do they disagree?
- My rocket landed behind a ridge — can I still hear it, and does 433 or 915 MHz do better?

### [Link margin, reliability and availability — how much margin to design for](kb/09-propagation-link-budget/link-margin-availability.md)
- How much fade margin do I need for 90 %, 99 % or 99.9 % reliability?
- How do I combine shadowing, fading, antenna-pattern and polarisation uncertainties into one margin?
- Why is "add up all the worst cases" the wrong approach — and when is it right?
- Will sending each telemetry packet three times make the link reliable?
- What margin should a rocket telemetry link carry during ascent, descent and after landing?
- What is the difference between availability of a fixed link (99.99 %) and reliability of a flight link?

### [Polarisation mismatch loss (PLF), axial-ratio mismatch and rocket attitude effects](kb/09-propagation-link-budget/polarization-mismatch-loss.md)
- How much signal do I lose when the transmit and receive antennas are not polarised the same way?
- Why does a circularly polarised ground antenna cost exactly 3 dB with a linear rocket antenna, and why is that often a good deal?
- What does a CP antenna's axial ratio do to the mismatch loss?
- What happens to my link as the rocket pitches over, rolls, and swings under the parachute?
- Why is the signal weakest when the rocket flies straight away from (or toward) the ground station?
- Which way should the ground antenna be polarised for a landed rocket?

### [Solar activity and space weather — sunspot cycle, solar flux, K/A indices, flares, storms and what they do to HF, VHF and GNSS](kb/09-propagation-link-budget/solar-activity-and-space-weather.md)
- What is the sunspot cycle, and where is Solar Cycle 25 in 2026?
- What is the solar flux index (SFI, F10.7), and how does it relate to the sunspot number and to usable HF frequencies?
- What do the K-index, A-index, Kp and Ap measure, and how do I read them?
- What is a solar flare, what do the A/B/C/M/X classes mean, and why does a flare black out HF for an hour?
- Why does a sudden ionospheric disturbance hurt 80 m more than 15 m?
- What is a coronal mass ejection (CME), how long does it take to reach Earth, and what is Bz?
- What do the NOAA R, S and G scales (e.g. "G5", "R3") mean?
- What is polar cap absorption, and why do auroral paths fade when the K-index is high?
- Why does HF noise suddenly rise across the whole band?
- Does space weather affect my 433/915 MHz rocket telemetry or my GNSS receiver in Singapore?
- What are the equatorial anomaly and plasma bubbles, and why does GNSS degrade after sunset near the equinoxes in Singapore?
- Where do I get live space-weather data (NOAA SWPC), and what should I check before a launch or an HF contact?

### [HF propagation modes and prediction — MUF/LUF/FOT, skip, multihop, grey line, long path, NVIS, scatter and how to predict a path (VOACAP, ITU-R P.533, WSPR/RBN/PSKReporter)](kb/09-propagation-link-budget/hf-propagation-modes-and-prediction.md)
- What are the MUF, the LUF and the FOT, and why should I operate just below the MUF?
- What happens to a signal above the MUF, between the LUF and MUF, and below the LUF? What if the LUF is above the MUF?
- What is the critical angle, and why does a lower take-off angle give a longer hop?
- How far does one hop reach via the E layer and via the F2 layer?
- What is the skip zone, and how can I hear stations inside it (scatter)?
- What are chordal hop, grey-line, long-path and NVIS propagation?
- What are the ordinary and extraordinary waves, and why can either a horizontal or a vertical antenna receive skywave?
- Why is 160 m DX only possible when the whole path is dark, and why is low HF so noisy in summer?
- How do VOACAP and ITU-R P.533 predict a path? What do WSPR, the Reverse Beacon Network and PSKReporter tell me?
- Which HF frequencies would link Singapore to Perth or Sydney in October 2026, at noon and at night?
- How do I do an HF link budget (field strength, absorption, noise, SNR)?

### [VHF/UHF anomalous propagation — tropospheric ducting, super-refraction, sporadic-E, meteor scatter, aurora, TEP, aircraft scatter and EME](kb/09-propagation-link-budget/vhf-uhf-anomalous-propagation.md)
- Why is the VHF/UHF radio horizon about 15 % farther than the visual horizon?
- What is tropospheric ducting? What causes it (temperature inversions, evaporation over water), and how far can it carry signals?
- Where does the "−157 N/km" ducting threshold come from, and what are M-units?
- Which frequencies can a given duct trap? Can a duct carry my 433/915 MHz LoRa signal hundreds of km or bring in interference?
- What is sporadic-E? When does it happen (season, time of day), and how high in frequency does it work?
- How does meteor-scatter communication work, and why is 6 m the best band for it?
- What causes auroral propagation, why does it sound raspy, and why is CW best?
- What is transequatorial propagation (TEP), when does it occur, and how far does it reach? Is Singapore a good place for it?
- What is aircraft scatter, and what limits its range?
- How much path loss does an EME (moon-bounce) path have, and what are libration fading and the perigee advantage?
- Why do VHF/UHF weak-signal operators use horizontal polarisation?
- My Meshtastic node "heard" a station 400 km away. Is that ducting or the internet?

### [Ground-wave and LF/MF propagation — Sommerfeld–Norton surface wave, ITU-R P.368, ground conductivity, MF broadcast and why HF ground wave dies quickly](kb/09-propagation-link-budget/ground-wave-and-lf-mf-propagation.md)
- What is the ground wave (surface wave), and how is it different from line-of-sight and skywave?
- Why does ground-wave range shrink as frequency rises, and why is HF ground wave limited to tens of km over land?
- Why does ground wave need vertical polarisation?
- How much do sea water, wet ground and dry ground change coverage?
- How do I compute ground-wave field strength (ITU-R P.368, Norton's numerical distance, LFMF/GRWAVE)?
- Why can I hear far-away AM (MW) stations only at night, and why do they fade?
- What happens on a mixed land–sea path (Millington method, recovery effect)?
- What are LF/VLF used for (time signals, navigation, submarines), and why do they reach so far?
- Does ground wave help my landed rocket's 433 MHz beacon? (No — and why.)

### [Satellite links — orbits, pass geometry, Doppler and Doppler rate, G/T, link budgets and tracking (Gpredict/hamlib)](kb/09-propagation-link-budget/satellite-links-doppler-tracking.md)
- How high are LEO, MEO and GEO satellites, how fast do they move, and how long is a pass?
- How far away is a satellite at 10° elevation, and how much path loss is that at 137 MHz or 437 MHz?
- Why does the Doppler shift sweep from + to − during a pass, and where is it changing fastest?
- Can a LoRa receiver decode a CubeSat without Doppler correction? Which spreading factors fail near zenith?
- What is G/T, and why does my 137 MHz weather-satellite antenna not improve with a better LNA in town?
- How do I do a link budget for a 437 MHz CubeSat or a Meteor-M weather satellite?
- What is a TLE, what does SGP4 do, and how does Gpredict steer a radio and a rotator through hamlib?
- Why can't my az/el rotator follow an overhead pass (the "keyhole")?
- Why do linear transponders invert the passband?
- Can I see QO-100 (the amateur geostationary transponder) from Singapore?

## 10-comms-modulation — 

### [Analog modulation — AM, DSB, SSB, VSB, FM and PM](kb/10-comms-modulation/analog-modulation-am-fm-pm-ssb.md)
- How much of an AM signal's power actually carries the message?
- What is the difference between AM, DSB-SC, SSB and VSB, and when does each need a coherent receiver?
- What is the FM modulation index, and how do Bessel functions give the FM spectrum?
- How wide is an FM signal (Carson's rule), and how good is that rule?
- Why does FM give better audio SNR than AM, and what is the "FM threshold"?
- What is the capture effect, and why can two FM stations not be heard at once while two AM aircraft can?
- What are pre-emphasis and de-emphasis (75 µs / 50 µs), and how many dB do they buy?
- How is APRS / 1200-baud packet sent over an NBFM radio, and what bandwidth does it use?
- How do I calibrate FM deviation with a spectrum analyser?
- Why is LSB used below 10 MHz and USB above, and where must the dial be relative to a band edge?
- How wide is an SSB voice signal, and why is the audio cut at about 300 Hz and 2.7–3 kHz?
- What is the PEP-to-average ratio of SSB speech, and why does it matter for the power amplifier?
- What does a speech processor (compressor or RF clipper) do, and what goes wrong when it or the mic gain is set too high?
- What is ALC on an SSB transmitter, and what is "flat-topping"?
- What is the necessary bandwidth of CW, AM, SSB and FM, and why is Morse code so power-efficient?
- Can I put AM and FM on the same carrier to send two signals at once — is that just QAM?

### [Digital modulation — OOK, FSK/MSK/GMSK, PSK, QAM, APSK](kb/10-comms-modulation/digital-modulation-psk-qam-fsk.md)
- What is the difference between bit rate, symbol rate and baud?
- What does a constellation diagram actually represent?
- How wide is an FSK signal — is it just twice the deviation?
- What is the modulation index of FSK, and why are h = 0.5 (MSK) and h = 1 special?
- What are MSK, GFSK and GMSK, and what does "BT = 0.3" mean?
- Why do satellites use OQPSK or π/4-QPSK instead of plain QPSK?
- How many bits per second per hertz can BPSK, QPSK, 16-QAM or 64-QAM deliver?
- What is PAPR, and why does 16-QAM force me to run my PA backed off?
- What is EVM, and how does it relate to SNR?
- Which modulations can be demodulated without recovering the carrier phase?
- Why do cheap 433 MHz remotes use OOK and most ISM data radios use GFSK?

### [Bit error rate, Eb/N0 and the Shannon limit](kb/10-comms-modulation/ber-ebn0-and-shannon.md)
- What is Eb/N0, and why do communications engineers use it instead of plain SNR?
- How do I convert between Eb/N0, Es/N0, SNR, C/N and C/N0 without losing (or gaining) 3 dB?
- Where does BER = Q(√(2Eb/N0)) for BPSK come from, and how is Q related to erfc?
- Why does QPSK have the same bit error rate as BPSK even though it sends twice as many bits?
- What Eb/N0 do I need for a BER of 1e-5 with BPSK, FSK, DPSK, 8-PSK, 16-QAM or 64-QAM?
- How much worse is non-coherent FSK than coherent BPSK, and why?
- How do I turn a required Eb/N0 into a receiver sensitivity in dBm for my 10 kbps rocket link?
- What is the Shannon limit, and why is it −1.59 dB?
- LoRa works at −20 dB SNR — does it beat Shannon?
- How much does a short packet (100–300 bits) cost compared with Shannon's infinite-block limit?
- Why is my simulated BER curve exactly 3 dB away from the textbook curve?
- How bad is Rayleigh fading for BER, and why does the curve become a straight line on a log plot?
- What are entropy and mutual information, and why are soft decisions worth about 2 dB?
- How close can QPSK, 8-PSK or 16-QAM get to Shannon, and what is BICM?
- What is the difference between ergodic and outage capacity, and which applies to a short telemetry packet?
- How much does adaptive modulation (or LoRa spreading-factor adaptation) recover in a fading channel?

### [Pulse shaping, intersymbol interference and equalisation](kb/10-comms-modulation/pulse-shaping-isi.md)
- Why can't I just send rectangular pulses?
- What is intersymbol interference (ISI) and where does it come from?
- What is the Nyquist ISI criterion, and what is the minimum bandwidth for a given symbol rate?
- What is the difference between a raised-cosine and a root-raised-cosine filter, and why do we split it between TX and RX?
- How does the roll-off factor β trade bandwidth against timing sensitivity and PAPR?
- How long should my RRC FIR filter be?
- How do I read an eye diagram?
- Does my rocket telemetry link need an equaliser?
- What are zero-forcing, MMSE and decision-feedback equalisers, and which should I use?

### [Spread spectrum — DSSS, FHSS, chirp spread spectrum and CDMA](kb/10-comms-modulation/spread-spectrum-dsss-fhss-css.md)
- What is spread spectrum, and what is "processing gain"?
- Does spreading improve performance against ordinary thermal noise?
- What is jamming margin, and how do I compute it?
- What are m-sequences and Gold codes, and how are GPS C/A codes generated?
- How does frequency hopping differ from direct sequence, and what does it protect against?
- How does chirp spread spectrum (LoRa) work, and why is it equivalent to M-ary FSK?
- Why does a frequency offset look like a timing offset in LoRa, and what does rocket Doppler do to it?
- How can GPS signals be received when they are ~18 dB below the thermal noise floor?
- How does CDMA let many users share a channel, and what is the near–far problem?

### [OFDM — orthogonal frequency-division multiplexing](kb/10-comms-modulation/ofdm.md)
- What is OFDM, and why do Wi-Fi, LTE/5G and DVB-T all use it?
- Why are the subcarriers "orthogonal" even though their spectra overlap?
- How does an inverse FFT generate OFDM, and what does the cyclic prefix do?
- How long must the cyclic prefix be?
- Why does OFDM have such a high peak-to-average power ratio, and what does that do to my PA?
- Why is OFDM so sensitive to frequency offset and phase noise?
- How are timing and frequency synchronised (Schmidl–Cox), and what are pilots for?
- Should I use OFDM for a custom rocket telemetry or video link?
- What are the 5G NR numerologies (15/30/60/120 kHz…), and why does NR scale the subcarrier spacing?
- What do LTE and Wi-Fi signals look like on a spectrum analyser (DC null, idle cell, resource-block loading, bursts)?
- How are MIMO antennas on a Wi-Fi router spaced and oriented?

### [Channel coding and forward error correction (FEC)](kb/10-comms-modulation/channel-coding-fec.md)
- What does forward error correction actually buy me in dB, and why is "coding gain" quoted at a specific BER?
- What do (n, k), code rate, minimum distance and "corrects t errors" mean?
- How do Hamming, Golay, BCH and Reed–Solomon block codes differ, and when is each appropriate?
- How does a convolutional code and the Viterbi decoder work, and what is the K = 7, rate-½ "NASA standard" code?
- Why is soft-decision decoding about 2 dB better than hard-decision?
- What are turbo, LDPC and polar codes, and are they practical on a microcontroller?
- What is interleaving, and how deep must it be for my fading or spinning-rocket channel?
- What does LoRa's coding rate CR 4/5 … 4/8 really do for me?
- Which FEC libraries can I use for a custom radio?
- For short telemetry packets, how close to Shannon can any code get?
- What are trellis-coded modulation (TCM) and bit-interleaved coded modulation (BICM), and why did BICM win?
- How does belief-propagation decoding of an LDPC code actually work?

### [Synchronisation — carrier, frequency, symbol timing and frame](kb/10-comms-modulation/synchronization-carrier-timing.md)
- What has to be synchronised in a digital receiver, and in what order?
- How does a Costas loop recover the carrier of a BPSK/QPSK signal that has no carrier component?
- How do I choose the loop bandwidth and damping, and compute the loop-filter gains?
- How much phase jitter does a carrier loop add, and how much does that cost in BER?
- How do I estimate a frequency offset, and what is the best possible accuracy (Cramér–Rao bound)?
- How do Gardner and Mueller–Müller timing recovery work, and which needs what?
- How do I find the start of a packet (preamble, sync word), and what threshold do I use?
- How big is the Doppler shift on a rocket, how fast does it change, and how do I handle it?
- Why is a ±10 ppm crystal a bigger problem than Mach-3 Doppler at 433 MHz?
- Should I estimate carrier phase with a block (feed-forward) estimator or a Costas loop?
- What is residual-carrier PSK and why do deep-space links use it?
- How does polyphase-filterbank timing recovery work, and how many arms do I need?
- Can I get symbol timing in one shot with an FFT?
- How accurately can cross-correlation measure a time delay, and why normalise it?

### [Matched filter and signal detection](kb/10-comms-modulation/matched-filter-detection.md)
- What is a matched filter and why is it "optimal"?
- Why is the best possible output SNR 2E/N0 no matter what shape the pulse has?
- Is a matched filter the same thing as a correlator?
- Why does my receiver need a root-raised-cosine filter if the transmitter already has one?
- How much do I lose if I use a plain RC or crystal IF filter instead of a true matched filter?
- How does a radar compress a long chirp into a short pulse, and what does that have to do with LoRa?
- How do I set a threshold to detect a preamble or sync word with a given false-alarm rate?
- Why does a small frequency offset destroy my sync-word correlator on a fast rocket?
- What changes when the noise is not white?

### [Packet framing and link protocols — preambles, sync words, CRC, whitening, ARQ vs FEC](kb/10-comms-modulation/packet-framing-protocols.md)
- What goes into a radio packet, and why each part?
- How long should my preamble be, and what makes a good sync word?
- How do I set the sync-word error tolerance for a given false-alarm rate?
- Which CRC polynomial should I use, what does "HD = 4 up to 32 751 bits" mean, and what is the chance a corrupted frame passes the CRC?
- Why do FSK radios "whiten" data, and how does PN9 whitening work?
- How does packet error rate relate to bit error rate, and what frame length maximises throughput?
- When should I use ARQ (retransmission) versus FEC — and what can a downlink-only rocket link do instead of ARQ?
- How should I design a rocket telemetry frame (headers, counters, versions), and what can I borrow from CCSDS?

### [Choosing a modulation and coding scheme — a decision guide](kb/10-comms-modulation/modulation-choice-guide.md)
- For a given range, data rate, power and bandwidth, which modulation and FEC should I use?
- How do LoRa, GFSK, BPSK+FEC, QPSK+LDPC and OFDM compare in required Eb/N0, bandwidth and hardware complexity?
- Is LoRa actually more sensitive than FSK or PSK *at the same data rate*, or only because it is slower?
- What changes for a fast rocket (Doppler, antenna nulls, near-pad dynamic range)?
- When is a coherent PSK design worth the extra receiver complexity?
- When is OFDM or high-order QAM justified?
- What should I pick for a custom 433/915 MHz telemetry radio, and for a video downlink?
- Which modulation should I use to send a camera image or voice from a rocket, and how long will it take?

### [Multiple access and duplexing — FDMA, TDMA, CDMA, OFDMA, ALOHA and slotted-ALOHA throughput, CSMA/LBT, FDD vs TDD, duplexers vs T/R switches, and a launch-day channel plan](kb/10-comms-modulation/multiple-access-and-duplexing.md)
- How do many radios share one band — FDMA, TDMA, CDMA, OFDMA and space division?
- What is ALOHA, and why is its maximum throughput only 18 % (37 % slotted)?
- If six rockets share one LoRa channel, what fraction of packets survive?
- Does the LoRa capture effect or using different spreading factors save me?
- What are CSMA and listen-before-talk, and why do hidden terminals break them?
- How long must the guard time be in a TDMA schedule, and can GNSS time synchronise it?
- What is the difference between FDD and TDD, and when do I need a duplexer rather than a T/R switch?
- How much isolation must a duplexer give, and what is receiver desensitisation?
- Why can another team's transmitter on the next pad wipe out my ground station?
- How should several teams and vehicles share frequencies on a launch day?

### [MIMO — channel model, capacity by SVD and water-filling, diversity vs multiplexing, Alamouti, channel estimation (LS/MMSE, OFDM pilots), and diversity for a rocket ground station](kb/10-comms-modulation/mimo-capacity-and-channel-estimation.md)
- What does "MIMO" actually buy: more range, more speed, or both?
- How do you derive MIMO capacity, and where do the SVD and water-filling come from?
- Why does capacity grow with min(Nt, Nr) at high SNR, and why does a line-of-sight rocket link get no multiplexing gain?
- What is the difference between diversity and multiplexing, and what is the diversity–multiplexing trade-off?
- How does the Alamouti code work, and why is it 3 dB worse than receive diversity?
- How do least-squares and MMSE channel estimation work, and how many pilots do I need?
- How should pilots be spaced in an OFDM system, and what goes wrong if they are too sparse?
- What is water-filling, and when is it worth knowing the channel at the transmitter?
- Can two antennas on the rocket help more than two at the ground station?
- Should my LoRa ground station use two antennas, and how far apart?
- What are zero-forcing, MMSE and V-BLAST detectors?
- Why does the condition number of the channel matrix matter?
- What space-time codes exist beyond Alamouti, and why is there no rate-1 code for four antennas?
- How much better is ML than zero-forcing or LMMSE detection, and what is the LMMSE output SINR?
- If the transmitter knows the channel, how much better than Alamouti can it do?
- How do Wi-Fi and LTE get channel state information to the transmitter (sounding, feedback, reciprocity)?
- Should two antennas on a rocket be fed the same signal or an Alamouti pair?

### [Weak-signal digital modes — FT8, FT4, WSPR, JT65, JT9, Q65, FST4, PSK31, RTTY, APRS, DMR/D-STAR — and what they teach about low-rate telemetry](kb/10-comms-modulation/weak-signal-digital-modes.md)
- How can FT8 decode a signal 21 dB below the noise? Does it beat Shannon?
- What does "SNR −21 dB in 2500 Hz" mean, and how do I turn it into Eb/N0 or a received power in dBm?
- What modulation and coding do FT8, FT4, WSPR, JT65, JT9, Q65 and FST4 use?
- How close are these modes to the theoretical limit, and why are they so much better than RTTY or PSK31?
- Is FT8 better or worse than LoRa SF12 at the same bit rate?
- Why does FT8 fail on auroral (high-Doppler-spread) paths while FT4 survives?
- What are a-priori (AP) decoding and ordered-statistics decoding, and are they fair?
- What do PSK31/Varicode, RTTY, APRS, DMR and D-STAR actually send over the air?
- Could I use an FT8- or WSPR-style waveform for a rocket recovery beacon?

## 11-radar — 

### [The radar range equation — monostatic, bistatic, pulsed, FMCW, search and track forms, losses and worked examples](kb/11-radar/radar-range-equation.md)
- How far can my radar see a given target, and how do I derive the radar equation from scratch?
- Why does radar range grow only as the fourth root of transmit power?
- How does the radar equation differ from the Friis equation for a communication link?
- What is the "energy" form of the radar equation, and why do pulsed and FMCW radars obey the same law?
- How do I write the radar equation for a TI mmWave FMCW chip (the SWRA553 form)?
- What losses should I budget (window, straddle, beam shape, CFAR, atmosphere, rain), and how big are they?
- What is the search-radar (power–aperture) equation, and when do I use it instead of the track form?
- How does the bistatic / passive-radar equation work?
- How far can a 24 GHz HB100/CDM324-type module see a person, and why does an FFT extend it?
- Can a DIY S-band radar track a small rocket to apogee?
- Why does a 60 GHz radar lose range outdoors, and how much does tropical rain hurt 77 GHz?

### [Radar cross section (RCS) — definition, canonical shapes, corner-reflector calibration targets, real targets, Swerling statistics](kb/11-radar/radar-cross-section.md)
- What exactly is radar cross section, and why is it not the physical area of the target?
- What is a dBsm?
- Why does a small metal sphere reflect so weakly at low frequency, and why does RCS oscillate near one wavelength?
- What are the RCS formulas for a sphere, flat plate, cylinder, dihedral and trihedral corner reflector?
- How do I build a corner-reflector calibration target for my 24/60/77 GHz radar, and how big should it be?
- What RCS should I assume for a person, a drone, a car, a bird, or a hobby rocket?
- Why does the echo from a drone or a car jump around by 10–20 dB when it turns slightly?
- Which Swerling model fits which target?
- How do stealth shaping and radar-absorbing materials reduce RCS?
- How do I measure the RCS of my own target (e.g. a rocket airframe)?

### [Pulsed radar and pulse compression — resolution, PRF and ambiguities, duty cycle, LFM, Barker and polyphase codes, sidelobes and Doppler tolerance](kb/11-radar/pulsed-radar-and-pulse-compression.md)
- What sets a pulsed radar's range resolution — the pulse length or the bandwidth?
- How do I choose the PRF, and why can't I have both unambiguous range and unambiguous velocity?
- What are duty cycle, average power and blind (eclipsed) range?
- What is pulse compression and why do solid-state radars need it?
- Why does a matched-filtered chirp have −13 dB sidelobes, and what does a Hamming or Taylor window cost?
- What are Barker codes, and why is 13 the longest?
- Frank, P4, polyphase codes — when do I use them instead of a chirp?
- What is "range–Doppler coupling" and why is a chirp called Doppler-tolerant?
- How does stretch processing relate to FMCW radar?
- How many samples per resolution cell do I need to avoid straddle loss?

### [CW and Doppler radar — the Doppler equation, homodyne I/Q receivers, micro-Doppler, HB100/CDM324 modules, speed guns and rocket-velocity measurement](kb/11-radar/cw-and-doppler-radar.md)
- Where does the two-way Doppler shift $2v/\lambda$ come from, and when is it not accurate?
- How many hertz of Doppler do I get per km/h at 10.525, 24 and 77 GHz?
- How does a CW homodyne radar work, and why do I need I and Q to know if a target approaches or recedes?
- How much I/Q imbalance can I tolerate?
- Why does my HB100 "see nothing" on the oscilloscope?
- What is micro-Doppler, and how can a radar see propellers, walking legs, breathing and heartbeats?
- Can I measure my rocket's velocity off the pad with a 24 GHz Doppler module? For how long and how far?
- Why can't a CW radar measure range, and how does two-frequency (FSK) CW fix that?
- What limits the dynamic range of a CW radar (leakage, phase noise, 1/f noise)?
- What is the "cosine error" of a speed gun?
- Which Doppler frequencies and powers are legal in Singapore?

### [FMCW radar — beat frequency, range/velocity/angle resolution, chirp design, range–Doppler processing, phase noise and leakage, VCO nonlinearity, TI/Infineon/ADI devices](kb/11-radar/fmcw-radar.md)
- How does an FMCW radar turn distance into a frequency, and where does $f_b = 2SR/c$ come from?
- What sets range resolution, maximum range, velocity resolution and maximum velocity?
- Why is maximum range limited by the IF bandwidth / ADC rate as well as by SNR?
- How do I design a chirp (bandwidth, slope, ramp time, idle time, number of chirps) for a given job?
- How do the range FFT, Doppler FFT and angle FFT build a range–Doppler map and a point cloud?
- Why do approaching targets show up at *negative* Doppler bins in TI data?
- How are TI's AWR/IWR chirp parameters (idle time, ADC start, ramp end, slope) chosen?
- Why does TX leakage raise the noise floor near zero range, and what is the range-correlation effect?
- What does VCO chirp nonlinearity do to the range profile, and how do I fix it?
- What do the Infineon BGT60TR13C and the ADI Phaser (CN0566) offer?
- Can I build an FMCW radar with a sound card like the MIT coffee-can radar?
- Should my radar be pulsed or FMCW?
- Why does a complex (I/Q) IF give up to 3 dB better SNR than a real IF, and what does I/Q imbalance do?
- Can FMCW work bistatically, with the transmitter and receiver in different places?
- How accurate is an FMCW radar altimeter, and what are the step (fixed) error and the Doppler bias?
- What do fast time, slow time, A-scope, B-scope, PPI and "video" mean?

### [Radar detection theory and CFAR — Pd, Pfa, Swerling targets, Albersheim/Shnidman, integration gain, CA/OS/GO/SO-CFAR](kb/11-radar/detection-theory-cfar.md)
- What SNR does a radar actually need to "see" a target, and where do numbers like 13 dB come from?
- What are probability of detection (Pd) and probability of false alarm (Pfa), and how are they traded?
- What is the Neyman–Pearson criterion and why does it lead to "compare the magnitude with a threshold"?
- Why does a fluctuating target (a drone, a person) need so much more SNR than a steel sphere?
- What are the Swerling I–IV models and which one should I use for my target?
- How accurate are Albersheim's and Shnidman's equations?
- Is non-coherent integration gain really √N? (No — it is closer to N^0.7–N^0.85.)
- What is CFAR, why does my FMCW radar need it, and how do I set the threshold multiplier?
- CA-CFAR vs OS-CFAR vs GO/SO-CFAR — which one should I use and what do they cost?
- How many false alarms per second will my range–Doppler map produce at Pfa = 10⁻⁶?
- What is CFAR loss and how many reference cells do I need?

### [The ambiguity function and radar waveform choice — definition, properties, rectangular pulse, LFM, codes, pulse trains, accuracy vs resolution](kb/11-radar/ambiguity-function-waveforms.md)
- What is the radar ambiguity function and what does it tell me about a waveform?
- Why can't a waveform have perfect range and Doppler resolution at the same time?
- Why does a chirp show a diagonal ridge, and what does that mean physically?
- What do "thumbtack", "ridge" and "bed of nails" ambiguity functions look like, and which waveforms produce them?
- How does a coherent pulse train get its fine Doppler resolution, and where do its ambiguities come from?
- What is a Costas code?
- How accurately can a radar measure range compared with its resolution?
- What is the cross-ambiguity function used in passive radar?
- Which waveform should I pick for my radar?

### [Clutter and MTI — surface and volume clutter, σ⁰ and rain reflectivity, MTI cancellers, blind speeds, staggered PRF, pulse-Doppler, STAP overview](kb/11-radar/clutter-and-mti.md)
- What is clutter, and why does it scale differently with range than a point target?
- What is σ⁰ (sigma-zero), and how big is ground and sea clutter at low grazing angles?
- How strong is rain as a radar "target" at 3, 10, 24 and 77 GHz, and does the weather-radar dBZ formula work at mm-wave?
- How does an MTI (moving-target indicator) canceller work, and what is a blind speed?
- How much clutter suppression (improvement factor) can a two- or three-pulse canceller give?
- How does staggering the PRF remove blind speeds?
- How is pulse-Doppler processing different from MTI?
- What is "static clutter removal" in an FMCW radar, and what does it cost?
- What is STAP and why do airborne/drone-mounted radars need it?

### [SAR and radar imaging — synthetic aperture principle, stripmap D/2 resolution, range–Doppler and backprojection algorithms, ISAR, DIY SAR, mmWave near-field imaging](kb/11-radar/sar-and-imaging.md)
- How can a small moving antenna produce images as sharp as a huge one?
- Why is stripmap SAR cross-range resolution D/2, independent of range and wavelength?
- What limits range and cross-range resolution in a rail or drone SAR?
- How far apart can the measurement positions be along the track (and what happens if they are too far)?
- What are backprojection, range–Doppler and ω-k (range-migration) image formation, and which should I use?
- What is range migration and why does it matter at short range?
- What is ISAR and how does target rotation give cross-range resolution?
- How did the MIT coffee-can radar and Henrik Forstén's projects do DIY SAR?
- Can I image objects with a TI mmWave board on a scanner?
- What is Doppler beam sharpening and how much does it sharpen a real beam?
- How sharp can an "RF camera" or Wi-Fi imaging radar ever be?
- How many hits per scan does a rotating radar get?
- Why are big phased arrays octagonal or circular rather than square?

### [MIMO radar and virtual arrays — virtual-array construction, TDM/BPM/DDM multiplexing, angle resolution, TI cascade radars, calibration](kb/11-radar/mimo-radar-virtual-arrays.md)
- What is a MIMO radar "virtual array", and why does 3 TX × 4 RX behave like 12 receivers?
- How are the virtual element positions computed, and how do I get elevation as well as azimuth?
- What angle resolution does an N-element virtual array give?
- What are TDM, BPM and DDM MIMO, and what does each cost (velocity range, SNR, complexity)?
- Why is my angle estimate wrong for fast targets in TDM-MIMO, and how do I fix it?
- How do TI's 4-chip cascade radars reach ~1.4° azimuth resolution?
- Why do I need to calibrate the channels, and how?
- Where does MIMO radar stop and phased-array beamforming begin?

### [DIY radar hardware — coffee-can radar, HB100/CDM324, TI mmWave EVMs, Infineon BGT60, ADI Phaser, Acconeer, SDR radar, passive radar, rocket tracking, legal bands](kb/11-radar/diy-radar-hardware.md)
- What is the cheapest way to start building radars, and what can each option actually do?
- What is the MIT coffee-can radar and how does it work?
- HB100 vs CDM324 vs an I/Q Doppler module — which should I buy?
- Which TI mmWave board (IWR6843, AWR1843, AWR2944) should I use, and how do I get raw data?
- What are the Infineon BGT60TR13C, the ADI Phaser (CN0566) and the Acconeer A121 good for?
- Can I build a radar with an SDR (Pluto, B210, HackRF)? What limits it?
- How does passive radar with a KrakenSDR or RTL-SDRs and FM/DVB-T transmitters work, and what does it need?
- Can a DIY radar track my rocket? What are the geometry, range and pointing problems?
- Which radar frequencies and powers are legal in Singapore?
- How do magnetrons, klystrons and TWTs work, and what is a pulse-forming-network modulator?
- Is it safe to use a microwave-oven magnetron (or a surplus marine radar) for a radar project?

### [Radar tracking — sequential lobing, conical scan, amplitude/phase monopulse, range and Doppler gates, α-β/Kalman trackers, gating and data association, and tracking a rocket (radar or GNSS-cued antenna)](kb/11-radar/radar-tracking-monopulse-and-trackers.md)
- How does a tracking radar measure angle more finely than its beamwidth?
- What are sequential lobing, conical scan and monopulse, and why did monopulse win?
- How do sum and difference (Σ/Δ) beams work, and what is the "monopulse slope"?
- How accurate is monopulse angle measurement for a given SNR and beamwidth?
- What is the difference between amplitude-comparison and phase-comparison monopulse?
- How does a split-gate (early–late) range tracker work?
- How do α-β and Kalman trackers fit into a radar, and how do I convert range/azimuth to x/y?
- What is gating, and what are nearest-neighbour, PDA, JPDA and MHT association?
- Can I track my rocket with a ground radar or an antenna tracker, and how fast must it slew?
- How do I point a telemetry Yagi at a rocket from its downlinked GNSS, and how much does latency matter?
- Is RSSI-based "step tracking" of a LoRa signal good enough to point an antenna?

### [Pulse-Doppler processing — the radar data cube, range–Doppler maps, low/medium/high PRF regimes, eclipsing and blind zones, Chinese-remainder and multiple-PRF ambiguity resolution, Doppler filter banks (MTD), CFAR on the range–Doppler map, CPI limits, and a DIY pulse-Doppler design](kb/11-radar/pulse-doppler-data-cube-and-prf-regimes.md)
- What is the radar "data cube", and what are fast time and slow time?
- How do I turn a stack of received pulses into a range–Doppler map?
- How much SNR do pulse compression, the Doppler FFT and the antenna channels each give me?
- What are low-, medium- and high-PRF radars, and why does each one exist?
- What are eclipsing and blind zones, and how much do they cost?
- How does a radar with several PRFs resolve range and velocity ambiguities (Chinese remainder theorem)?
- Why does exact CRT fail with noisy measurements, and what do real radars do instead?
- What is a moving-target detector (MTD) and which Doppler window should it use?
- How do I run CFAR on a range–Doppler map, and does windowing upset the false-alarm rate?
- How long can I integrate coherently on an accelerating rocket?
- Can I build a pulse-Doppler radar with an SDR, and what would it see?
- How big is the data cube and how much processing does it take?
- Is an FMCW chirp-sequence radar a pulse-Doppler radar?

### [Radar applications people ask about — ground-penetrating radar, through-wall radar, Wi-Fi/CSI sensing, harmonic radar and junction detectors, cheap motion modules (RCWL-0516, LD2410), automotive and vital-sign radar — what is physically possible and what is hype](kb/11-radar/radar-applications-gpr-through-wall-sensing.md)
- How does a ground-penetrating radar work, and how deep can it see in sand, clay or rock?
- Why does GPR fail in wet clay, and why do low frequencies go deeper?
- What limits GPR resolution?
- How can a radar "see through walls", and what stops it?
- How does Wi-Fi motion sensing (CSI) work, and can my router really count people or read breathing?
- What is harmonic radar, how do RECCO reflectors and insect tags work, and how does a non-linear junction detector find hidden electronics?
- What is the RCWL-0516 "microwave radar" module really, and how is it different from an HB100 or an LD2410?
- Why can't I turn a CDM324 Doppler module into an FMCW radar by wiggling its supply?
- Could a hobby Doppler radar see rain like a weather radar?
- Which radar claims are physics and which are hype?

## 12-phased-arrays — 

### [Array factor and linear arrays — pattern multiplication, beamwidth, nulls, directivity, array gain](kb/12-phased-arrays/array-factor-linear-arrays.md)
- What is an "array factor" and where does the sin(Nx)/sin(x) formula come from?
- Why is the pattern of an array "element pattern × array factor", and when is that wrong?
- How narrow is the beam of an N-element array with half-wavelength spacing?
- Where are the nulls and how high is the first sidelobe of a uniform array?
- What is the difference between a broadside and an endfire array, and what is the Hansen–Woodyard trick?
- How do I calculate the directivity of an array — is it just 10·log10(N) + element gain?
- If I combine N receivers coherently, how much does my SNR improve, and why?
- Why does a transmit array's EIRP grow as N² but its receive G/T only as N?
- How far away do I need to be to measure an array's far-field pattern?
- Is an array of 4 dipoles better than a Yagi for my ground station?
- What is the connection between an array pattern and a Fourier transform / an FIR filter?
- Why does array directivity stay the same when I scan a λ/2-spaced array of isotropic elements, even though the beam gets wider?

### [Beam steering and grating lobes — visible space, scan loss, beam broadening, squint vs true time delay, phase-quantisation lobes](kb/12-phased-arrays/beam-steering-grating-lobes.md)
- What phase do I put on each element to point the beam at 40°?
- What is a grating lobe and why is it "spatial aliasing"?
- What element spacing can I use if I only need to scan ±30° (or ±60°)?
- Is λ/2 spacing always safe?
- Why does the beam get wider and the gain drop as I steer away from broadside?
- What is beam squint, and when do I need true-time delay instead of phase shifters?
- How much bandwidth can a phase-shifter-steered array handle?
- How many phase-shifter bits do I need? Do more bits give finer beam pointing?
- What are quantisation lobes and how high are they with a 4-bit phase shifter?
- Why does my beam point at the wrong angle when I change frequency?
- How accurately can I point the beam if my element phases have random errors?
- What is "visible space" and "u-space"?

### [Planar arrays, element patterns and mutual coupling — lattices, active element pattern, active reflection coefficient, scan blindness, embedded element efficiency](kb/12-phased-arrays/planar-arrays-element-pattern-coupling.md)
- How do I steer a 2-D (planar) array in azimuth and elevation?
- Should I put the elements on a square grid or a triangular grid?
- My patch is perfectly matched on its own — why is it mismatched once it's in the array, and why does the match change as I steer?
- What is the difference between the isolated element pattern, the embedded (active) element pattern and the array factor?
- What is "active reflection coefficient" (scan impedance) and how do I measure it with an ordinary 2-port VNA?
- What is scan blindness, and will my FR-4 patch array suffer from it?
- Why is the gain of an array less than N × the gain of one element (the element-gain paradox)?
- What is the maximum gain one element can contribute in a big array?
- Do edge elements behave differently? What changes for a small (4–16 element) array?
- How strong is the coupling between two λ/2 dipoles or patches half a wavelength apart?
- Is closer spacing always safer?
- How does coupling affect a direction-finding array?

### [Tapering and sidelobe control — uniform, binomial, Dolph–Chebyshev, Taylor n̄, cosine-on-pedestal, taper efficiency, random-error floors, monopulse](kb/12-phased-arrays/tapering-sidelobe-control.md)
- Why does a uniformly weighted array have −13 dB sidelobes, and how do I get lower ones?
- What do Dolph–Chebyshev and Taylor tapers actually do, and which should I use?
- How much gain and beamwidth do I lose by tapering?
- Is an array taper the same thing as an FFT window?
- What is n̄ in a Taylor taper and how do I choose it?
- How accurately must I set the element amplitudes and phases to actually achieve −30 dB sidelobes?
- What happens to the sidelobes if a few elements fail?
- How do I calculate the sidelobe "floor" caused by random errors?
- Why do transmit arrays often stay uniform while receive arrays are tapered?
- What is a monopulse (sum/difference) pattern and why does it need its own taper (Bayliss)?
- Can I get zero sidelobes (binomial array)? Why doesn't everyone do that?
- How do I put a null on an interferer with a fixed taper?

### [Beamforming architectures — analog RF/IF/LO phase shifting, digital, hybrid/subarrays, Butler matrix, Rotman lens, dynamic range and synchronisation](kb/12-phased-arrays/beamforming-architectures.md)
- What are the different ways to build a phased array — RF, IF, LO, digital, hybrid — and what does each cost me?
- Where should the phase shifting happen?
- Do I need a separate receiver (ADC) behind every antenna?
- How many beams can I form at once with each architecture?
- What is a Butler matrix or a Rotman lens and when would I use one?
- Why does "10·log N" dynamic-range improvement apply to noise and some spurs but not others?
- Does a strong interferer in a sidelobe still hit every ADC at full strength in a digital array?
- Why must all channels share an LO/reference? Are two SDRs locked to the same 10 MHz reference coherent?
- Does LO phase noise average out across the channels?
- What data rate does a digital array generate, and where must the beamforming be done?
- Why do I need an LNA *before* the beamformer?
- What is the right architecture for a student DOA array, a tracking ground station, or a small radar?
- How is a Starlink user terminal built (elements, lattice, beamformer chips), and do its published numbers add up?

### [Phase shifters, true-time-delay units and beamformer ICs — switched-line, loaded-line, reflection-type, vector modulator, TTD, T/R modules, cost per element](kb/12-phased-arrays/phase-shifters-ttd-components.md)
- How does a phase shifter actually shift phase — what's inside?
- What's the difference between a switched-line, loaded-line, reflection-type and vector-modulator phase shifter?
- Is a switched-line phase shifter a phase shifter or a time delay?
- Can I build my own phase shifter at 2.4 or 5.8 GHz from switches, varactors or a hybrid coupler?
- What does a beamformer IC like the ADAR1000 contain, and what are its real specs?
- How much loss and noise does a phase shifter add, and where must the LNA go?
- How many bits and how much delay range do I need for a true-time-delay (TTD) unit?
- What's in a T/R module?
- Why does a phase shifter's gain change with its phase setting (and vice versa)?
- What does a phased-array channel cost at hobby/student scale?
- Which parts exist for 433 MHz, 915 MHz, 2.4 GHz, 5.8 GHz and 10 GHz?

### [Array calibration — error sources, REV, mutual-coupling self-calibration, near-field and far-field methods, coherent-SDR noise-source calibration](kb/12-phased-arrays/array-calibration.md)
- Why does a phased array need calibration at all, if every channel is "identical"?
- What errors does calibration remove, and which does it not?
- How accurately must I calibrate to get −25 dB (or −30 dB) sidelobes?
- How can I calibrate an analog phased array with only a power meter or spectrum analyser (REV method)?
- How does KrakenSDR make five RTL-SDR tuners phase-coherent, and why do the antenna cables still have to be equal?
- Can an array calibrate itself using coupling between its own elements?
- What is near-field probe calibration and when is it worth it?
- How do I calibrate a digital (SDR) array with a beacon in the far field?
- How often must I recalibrate — after every retune? Every temperature change?
- How do I measure the delay between two SDR channels to a fraction of a sample?
- What calibration does a DOA array need beyond receiver phase and gain?

### [Adaptive beamforming and direction finding — delay-and-sum, MVDR/Capon, LCMV, diagonal loading, MUSIC, Root-MUSIC, ESPRIT, spatial smoothing, CRB](kb/12-phased-arrays/adaptive-beamforming-doa.md)
- How do I find the direction of a transmitter with an array of antennas and a coherent SDR?
- What is the difference between delay-and-sum (Bartlett), Capon/MVDR and MUSIC?
- Can MUSIC really resolve two sources closer than the beamwidth? At what SNR?
- Why does MUSIC fail with multipath (coherent sources), and what is spatial smoothing?
- What is the best possible bearing accuracy (Cramér–Rao bound) for my array, SNR and number of samples?
- How many snapshots do I need for adaptive beamforming?
- Why does my MVDR beamformer cancel the very signal I'm trying to receive, and how does diagonal loading fix it?
- How does an adaptive array null a jammer?
- How do I estimate how many signals are present?
- Why does a linear array confuse front and back, and why does KrakenSDR use a circular array?
- What are ESPRIT and Root-MUSIC good for?
- Which algorithm should I use in practice?
- How do I find a landed rocket's beacon with a handheld Yagi, and should I use the peak or the null?
- What is "body fade", and what is an offset attenuator for?
- How does a pseudo-Doppler or Watson–Watt direction finder work, and how accurate is it?
- How far off will my position fix be if I take bearings from two places?
- Why does my receiver show full scale everywhere when I get close to the transmitter?

### [DIY phased-array projects — ADI Phaser, KrakenSDR/KerberosSDR, coherent RTL-SDR and Pluto/B210 arrays, FR-4 patch arrays, switched-array radar, rocket ground-station tracking](kb/12-phased-arrays/diy-phased-array-projects.md)
- What is the cheapest way to start experimenting with phased arrays?
- What can I learn with the ADI Phaser (CN0566), and what does it cost?
- How do KrakenSDR and KerberosSDR achieve phase coherence, and what are their limits?
- Can I make two RTL-SDRs, two Plutos, or one Pluto/B210 into a coherent array?
- Could a KrakenSDR find our landed rocket from its 433 MHz beacon? How accurately?
- Should our ground station use a phased array or a tracking Yagi?
- How big would a 433 MHz, 915 MHz, 2.4 GHz or 5.8 GHz array be for 15 or 20 dBi?
- How fast must a tracking antenna steer to follow a rocket off the pad?
- How do I build a 2.4/5.8 GHz patch array on FR-4 (JLCPCB), and how do I feed and steer it?
- What is a switched-array (MIT/Charvat-style) radar?
- What is realistic on a student budget, and in what order should I do things?
- How do the series-fed patch and comb-line antennas on 24/60/77 GHz radar boards work, and how much does their beam squint with frequency?

### [Array pattern synthesis — Schelkunoff zero placement, Fourier and Woodward–Lawson shaped beams, least-squares and min-max (LP) synthesis, Bayliss difference patterns, null steering](kb/12-phased-arrays/array-pattern-synthesis.md)
- How do I design array weights that give a pattern I choose, rather than just a narrow beam?
- What is the Schelkunoff polynomial method, and how do I put nulls exactly where I want them?
- How do I make a two-element cardioid (endfire) array, and what feed phase does it need at 433 MHz?
- How do I get a flat-topped sector beam or a cosecant-squared beam from an array?
- What is Woodward–Lawson synthesis and how is it different from Fourier synthesis?
- Why does my "ideal" flat-top pattern always ripple by about 1–2 dB at the edges (Gibbs)?
- How do I use least squares or linear programming (convex optimisation) to synthesise a pattern with nulls?
- Is Dolph–Chebyshev really optimal, and how can I check that with an optimiser?
- What is a Bayliss taper and why can't I just flip the sign of half a Taylor taper for monopulse?
- How do I steer a null onto an interferer without wrecking my main beam, and how deep will the null really be?
- How does deterministic null steering relate to adaptive (MVDR) nulling?

### [Conformal and cylindrical arrays — element-pattern rotation, wraparound arrays on rocket airframes, commutated cylindrical arrays, polarization on curved surfaces, uniform circular arrays and phase modes for direction finding](kb/12-phased-arrays/conformal-and-cylindrical-arrays.md)
- What changes when array elements sit on a curved surface instead of a flat panel?
- Why doesn't "element pattern × array factor" work on a cylinder?
- How many antennas do I need around my rocket's body tube for a roll-omnidirectional (wraparound) pattern at 433 MHz, 915 MHz, 2.4 GHz or 5.8 GHz?
- Should a wraparound telemetry array be polarized along the rocket axis or around it?
- How does a cylindrical array scan 360° by switching (commutating) which elements are active?
- Why do conformal arrays have high cross-polarization, and what about a nose cone?
- What are "phase modes" of a circular array, and why does a KrakenSDR use a circle?
- Why does a simple phase-mode bearing estimate fail on a KrakenSDR-sized ring at 433 MHz while MUSIC works?
- How does a pseudo-Doppler direction finder work?
- How many elements does a GNSS (L1) wraparound need on a 4-inch or 6-inch airframe?
- What radius should a 5-element direction-finding ring have at 433, 868 or 915 MHz?

### [Stacking and arraying Yagis — stacking distance from effective aperture and mutual resistance, the 2- and 4-Yagi gain increment, phasing harnesses and power dividers, H vs V stacking, NEC study of 433 MHz DL6WU stacks, ground-station trade-offs vs a longer Yagi or a crossed (CP) Yagi](kb/12-phased-arrays/stacking-and-arraying-yagis.md)
- How much gain do I really get from stacking two (or four) identical Yagis — is it 3 dB?
- How far apart should stacked Yagis be, and where does the λ/(2 sin(B/2)) formula come from?
- Why do different books give different stacking distances (51/HPBW, λ/(2 sin(B/2)), "capture areas just touching")?
- Can a stack ever give more than 3 dB?
- Should I stack side by side or one above the other, and what changes with vertical vs horizontal polarization?
- How do I build a phasing harness from 75 Ω coax, and how accurately must the cable lengths match?
- What happens if one Yagi is fed upside down (reversed polarity)?
- Can I tilt a stacked pair's beam upward with a cable delay instead of tilting the booms?
- Does stacking three or four Yagis in a line give 4.8 and 6 dB?
- T-connector harness or Wilkinson power divider?
- For a rocket ground station: two stacked Yagis, one longer Yagi, or a crossed Yagi for circular polarization?
- How narrow does the beam get, and how accurately must I then point it?
- How do I scale a 433 MHz stack to 915 MHz?
- How do I measure the velocity factor of my coax to cut the harness?

## 13-pcb-rf-layout-emc — 

### [PCB stackups and laminate materials for RF — FR-4 grades, glass styles, Rogers/PTFE/Megtron, and JLCPCB's stackups with 50 Ω geometries](kb/13-pcb-rf-layout-emc/stackups-and-materials.md)
- What is the difference between a core and a prepreg, and what do 7628, 3313, 2116, 1080 and 106 mean?
- Why does JLCPCB list a different dielectric constant for each prepreg type?
- How wide is a 50 Ω trace on each JLCPCB stackup, and what does JLCPCB's own calculator say?
- Why do different impedance calculators give different widths for the same JLCPCB stackup?
- Is FR-4 good enough for 433 MHz, 915 MHz, GNSS, 2.4 GHz and 5.8 GHz, or do I need Rogers?
- What do Tg, Td, CTE and moisture absorption mean for an RF board that goes on a rocket?
- What is the fibre-weave effect and does it matter for RF (phased arrays, filters)?
- Which 4-layer or 6-layer stackup should I pick for a LoRa / GNSS / ESP32 flight computer?
- Can I get a hybrid Rogers + FR-4 stackup at JLCPCB, and what does Rogers cost?
- Should I put the soldermask over my RF traces, and how much does it change the impedance?
- Why should I order "FR-4 TG155" rather than the default material when I ask for impedance control?

### [Grounding and return paths — where RF return current really flows, and why splits, slots and "star grounds" fail](kb/13-pcb-rf-layout-emc/grounding-and-return-paths.md)
- Where does the return current of an RF trace flow in the ground plane?
- How wide is the "shadow" of return current under a microstrip on a 4-layer vs a 2-layer board?
- At what frequency does return current stop taking the shortest path and start following the trace?
- Why is routing a trace across a split or slot in the ground plane so bad, even at low frequency?
- Should I split my ground plane into analog, digital and RF grounds?
- What do I do with an ADC's AGND and DGND pins?
- Does a "star ground" work at RF?
- What happens to the return current when my signal changes layers through a via?
- How close must a stitching via or capacitor be to a layer-change via?
- Is the "20-H rule" for power planes worth following?
- Why does my 2-layer board have more crosstalk than the same layout on 4 layers?
- Is a cross-hatched ground plane as good as a solid one?
- Does the ground plane itself have to be "50 Ω"?
- How do I avoid ground loops between boards, batteries and cables?

### [Vias, ground stitching and via fences — inductance, stitching pitch (λ/10–λ/20 and why), CPWG fences, stubs and backdrilling, via-in-pad, thermal vias](kb/13-pcb-rf-layout-emc/vias-stitching-fencing.md)
- How much inductance does a via have on a JLCPCB 4-layer board, and when does it matter?
- Where does the "stitch ground every λ/10 (or λ/20)" rule come from, and how much isolation does a via row really give?
- How far apart should via-fence vias be along a grounded coplanar waveguide at 915 MHz, 2.4 GHz and 5.8 GHz?
- Why do floating or single-via copper islands cause trouble?
- Do I need back-drilling or blind vias for RF on a 1.6 mm board?
- Should I put vias in the exposed pad of a QFN (PA, SX1262, ESP32-S3), and will solder wick into them?
- How much heat does one thermal via carry?

### [RF PCB layout rules — placement order, matching at the pin, component sizes, keep-outs, crystals, isolation, reference layouts and KiCad practice](kb/13-pcb-rf-layout-emc/rf-layout-rules.md)
- In what order should I place parts on an RF board?
- How close to the chip pin must the matching network be, and in what orientation?
- Is 0402 good enough at 2.4 GHz, or do I need 0201? When is 0603 too big?
- Why does my 2.2 pF matching capacitor behave like 3 pF at 2.4 GHz?
- Where should the trace inductance go in an LC filter or match?
- Do microstrip bends need to be mitred or curved?
- How much keep-out does a chip or PCB antenna need, and can there be copper under it?
- Where do I put the crystal or TCXO for an SX1262, and why does my LoRa frequency drift during long packets?
- How do I keep PA energy out of the LNA / receive path?
- How closely must I copy a reference layout (Semtech, TI, Espressif, u-blox)?
- What KiCad features help with RF layout (rule areas, net ties, custom pads, via-fence plugins)?
- Should I put a via fence or ground pour around my antenna to "shield" it?
- What is the exposed (unmasked) ground copper next to RF sections for?
- What changes when I lay out above 10 GHz?

### [RF connectors and board launches — SMA edge launch, U.FL/IPEX, coax-to-microstrip transitions and return-loss budgets](kb/13-pcb-rf-layout-emc/connectors-and-launches.md)
- Why does my SMA edge connector show bad return loss at 2.4 GHz even though the trace is 50 Ω?
- Should I cut the ground plane under the SMA or U.FL signal pad, and on which layers?
- How good is a U.FL, how many times can I plug it, and up to what frequency?
- What is a return-loss budget and how do connector, launch, trace and pads add up?
- Why do vertical (through-hole) SMAs perform worse than edge-launch ones above a few GHz?
- How much loss does a U.FL pigtail add at 433 MHz, 915 MHz, GNSS L1, 2.4 and 5.8 GHz?
- How should I place ground vias around an RF connector footprint?
- Is it better to use an SMA on the board or a U.FL-to-SMA bulkhead pigtail in a rocket?
- Can I rotate the antenna connector footprint 90° (or 45°) without ruining the signal?

### [Shielding and isolation on RF boards — shield cans and their cavity resonances, seams and apertures, absorbers, compartments, filtering at can walls, isolation budgets, and shielding beyond the board (enclosure doors and gaskets, wire meshes and RF fabrics vs frequency, Faraday boxes, testing a DIY cage with an SDR)](kb/13-pcb-rf-layout-emc/shielding-and-isolation.md)
- When do I need a shield can on an RF board, and what does it really buy me?
- At what frequency does my shield can resonate, and why can a can make coupling worse?
- How many solder points does a can fence need, and how big can holes/slots be?
- What do RF absorber sheets do inside a can?
- How do I get signals and power in and out of a shielded compartment without leaking RF?
- How much isolation do I need between a PA and an LNA, or between my LoRa transmitter and my GNSS receiver?
- Do any LoRa harmonics land in the GNSS L1 band?
- How much does a window screen, hardware cloth or chicken wire shield at 433 MHz, 915 MHz or 2.4 GHz?
- Are RF-shielding fabrics and Faraday bags as good as metal?
- Why does a phone still ring inside my home-made Faraday box (or a microwave oven)?
- How do I gasket an enclosure door or lid, and how many screws does it need?
- How do I measure the shielding of a DIY cage or box with an SDR?

### [EMC/EMI fundamentals for RF boards and rocket avionics — DM vs CM radiation, cables, filtering, spread-spectrum clocks, edge rates, pre-compliance (near-field, LISN, LPDA), susceptibility (sensors, pyro), ESD, MIL-STD-461/DO-160 test families, EFT/surge, snubbers and inductive-load clamps](kb/13-pcb-rf-layout-emc/emc-emi-fundamentals.md)
- Why do cables radiate so much more than the PCB traces that drive them?
- How many microamps of common-mode current on a cable is enough to fail FCC/CISPR limits?
- What are Ott's differential-mode and common-mode radiation formulas, and where do the constants come from?
- Which MCU/SD/USB clock harmonics land in my 433 MHz, 915/920 MHz LoRa or GNSS L1 band?
- Does spread-spectrum clocking help my own receiver, or only the EMC test?
- How much does slowing edges with a series resistor help?
- How do I do pre-compliance testing with a near-field probe and a tinySA?
- Can my 2 W telemetry transmitter upset the barometer, IMU or — worse — fire a pyro channel?
- How do I protect RF and sensor ports against ESD without ruining RF performance?
- Why does an audio amplifier buzz when a phone or my telemetry radio transmits, and how do I fix it?
- What do MIL-STD-461 and DO-160 actually test, and which of those tests are worth copying for a rocket flight computer?
- What are EFT, surge and CS115/CS116 transients, and how much energy does my TVS have to absorb?
- How do I design an RC snubber, and do I need a flyback diode on pyro and servo outputs?
- Why did my regulator die when I flipped the arming switch on a LiPo?
- How do I measure conducted emissions with a LISN, and which LISN (50 µH or 5 µH) do I need?
- How do I turn a spectrum-analyser reading from a log-periodic antenna into dBµV/m, and how trustworthy is a home pre-scan?
- We failed a radiated-emission test — what is the fastest way to find and fix the cause?

### [Power distribution and decoupling for RF — target impedance, anti-resonances, bead + capacitor filters, PA burst current, supply isolation for PAs/VCOs/LNAs, star vs daisy-chain feeding](kb/13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)
- What is "target impedance", and what does it mean for a 2 W LoRa module's supply?
- Why can adding a 100 pF "RF capacitor" next to a 100 nF make decoupling worse at UHF?
- Why does my ferrite bead + capacitor supply filter amplify noise at some frequency, and how do I damp it?
- How much bulk capacitance does an EBYTE E22-400T33D need so its 1.2 A TX bursts don't brown out the board?
- Should the PA, LNA and VCO share a supply trace, or be fed in a star?
- How much supply ripple can a VCO or PLL tolerate before it shows spurs?
- How do I filter a buck converter's ripple for an RF front end?

### [Mixed-signal layout for radio boards — ADC grounding, digital noise into LoRa and GNSS (desense), clock and bus routing, keeping USB/SD/switchers away from receivers, SPI/clock termination and crosstalk budgets (NEXT/FEXT, saturation length, guard traces)](kb/13-pcb-rf-layout-emc/mixed-signal-layout.md)
- Should my flight computer have separate analog, digital and RF ground planes?
- How do I connect an ADC's AGND and DGND pins, and where does the converter go?
- Which digital clocks and buses put harmonics into 433 MHz, 915/920 MHz or GNSS L1?
- How weak does a spur have to be to not desensitise my LoRa or GNSS receiver?
- How much isolation do I need between a clock trace and the receiver, and how do I get it?
- How should SPI/UART lines to a radio module be routed?
- Where should USB, the SD card and switching regulators go relative to the GNSS antenna?
- How do I tell if my GNSS is being jammed by my own board?
- Does my SPI clock need a termination resistor, and what value?
- Why does my SPI bus double-clock when I add a second sensor on the same SCK line?
- How much crosstalk does an SPI clock put on the trace next to it, and what is "saturation length"?
- Do guard traces actually help, and does the 3W rule hold on a 4-layer JLC board?

### [Making RF boards at JLCPCB — impedance control, tolerances, minimum features, via-in-pad, surface finishes, Rogers/PTFE service, assembly of RF parts, and what can't be done cheaply](kb/13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)
- Does JLCPCB do impedance control on 2-layer boards, and what tolerance do I actually get?
- Which JLCPCB stackup and material should I select for a 4-layer RF board?
- What are the minimum trace, space, drill and via sizes, and do they limit CPWG gaps?
- Should I choose HASL, ENIG or OSP for an RF board?
- Can JLCPCB make Rogers or PTFE boards, and with how many layers?
- Can JLCPCB assemble 0201 parts, QFNs with exposed pads, U.FL connectors and shield cans?
- How do I check that what came back has the impedance I asked for?
- What RF board features are not available cheaply at JLCPCB?

### [Thermal management for RF boards — PA dissipation, exposed pads and thermal vias, copper spreading, junction temperature, and a 2 W LoRa module in a sealed rocket av-bay](kb/13-pcb-rf-layout-emc/thermal-management-rf.md)
- How much heat does my 2 W LoRa module or my PA chip produce while transmitting?
- How do I estimate a PA's junction temperature from θJA/θJC?
- How much do thermal vias under an exposed pad really help?
- Why is copper area (spreading) more important than via count once there are a few vias?
- Will an EBYTE E22-400T33D overheat in a sealed av-bay sitting on a hot launch pad?
- Why does my LoRa frequency drift during long packets, and how does layout fix it?
- When does a single packet heat the die appreciably?

### [RF PCB review checklist — schematic, stackup, layout, EMC, thermal, manufacturing and bring-up checks for LoRa/GNSS/2.4 GHz boards](kb/13-pcb-rf-layout-emc/rf-pcb-review-checklist.md)
- What should I check before sending an RF board (LoRa, GNSS, 2.4/5.8 GHz) to fabrication?
- What schematic items commonly break RF boards?
- What layout checks catch the most common RF and EMC failures?
- What should the fab notes and the as-built record contain?
- What do I measure first when the boards arrive?

### [Digital termination and crosstalk — reflections on fast edges, when to terminate, series/parallel/Thevenin/AC termination, NEXT and FEXT from mutual L and C, the 3W rule, and clocks near RF](kb/13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md)
- When does a digital trace (SPI clock, SD card, UART, GPIO) need termination on my flight-computer board?
- Why does my 40 MHz SPI clock ring, and what does the 22–33 Ω series resistor actually do?
- What are series, parallel, Thevenin and AC (RC) terminations, and which costs how much power?
- What is the difference between near-end (NEXT) and far-end (FEXT) crosstalk, and where do they come from?
- Why does microstrip have far-end crosstalk but stripline almost none?
- Does the "3W rule" work? How much crosstalk does it really leave on a JLCPCB 4-layer vs a 2-layer board?
- How far should a clock or SPI trace stay from the LoRa or GNSS RF trace?
- Why does crosstalk stop growing beyond a certain parallel length?
- What value of series resistor should I put on an MCU clock pin?
- Do I need termination on I²C or UART?

## 14-sdr-dsp — 

### [Sampling, aliasing and bandpass (under-)sampling](kb/14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)
- What does the Nyquist–Shannon sampling theorem actually say, and where does the factor of 2 come from?
- Why does a 1.1 MHz tone show up at 100 kHz when I sample at 1 MS/s?
- What is a Nyquist zone, and why is a signal in the second zone "upside down"?
- Can I sample a 70 MHz IF (or even 433 MHz directly) with an ADC running far below twice the carrier? Which sample rates are allowed?
- Why does an SDR with a 2.4 MS/s sample rate show 2.4 MHz of spectrum, not 1.2 MHz?
- How steep does my anti-alias filter have to be?
- Why does undersampling make my noise floor worse?
- How much clock jitter can I tolerate if I sample a 433 MHz signal directly?
- Why can't I use the whole ±fs/2 span of my SDR's display?
- What sample rate should I pick to receive a 125 kHz LoRa channel?

### [IQ signals and complex baseband in SDRs — quadrature mixing, negative frequencies, IQ imbalance, DC spike and offset tuning](kb/14-sdr-dsp/iq-complex-baseband.md)
- Why do SDRs deliver *complex* samples (I and Q) instead of ordinary real numbers?
- What is a "negative frequency" on my SDR's waterfall?
- How does a quadrature (IQ) mixer turn an RF signal into I and Q, and how does a transmitter go back?
- What is that spike right in the middle of my SDR spectrum, and how do I get rid of it?
- Why do I see a faint mirror copy of a strong signal on the opposite side of the centre frequency (HackRF, Pluto, LimeSDR)?
- How much image rejection does 0.1 dB of gain error and 1° of phase error give me?
- What is "offset tuning", and what does it *not* protect me from?
- Is the RTL-SDR a zero-IF receiver?
- How do I correct IQ imbalance in software?
- What are analytic signals and the Hilbert transform used for in practice?
- How many Hz off will my 433.92 MHz signal appear for a given ppm error?

### [Digital filters — FIR and IIR design, linear phase, length estimates, stability and fixed-point effects](kb/14-sdr-dsp/digital-filters-fir-iir.md)
- What is the difference between an FIR and an IIR filter, and which should I use in an SDR?
- How many taps does my FIR need for a given transition band and stop-band attenuation?
- Window method, least-squares or Parks–McClellan (remez) — which and why?
- What is linear phase / group delay, and why do demodulators care?
- How do I turn an analogue Butterworth/Chebyshev/elliptic design into a digital IIR, and what is prewarping?
- Why did my high-order IIR blow up when I put it in fixed point (or even float32)?
- How many coefficient bits do I need for 80 dB of stop-band?
- How many accumulator bits does a fixed-point FIR need?
- How expensive (multiplies per second) is a channel filter for a LoRa channel?
- Why is my filter's output delayed, and by how much?
- Can I filter by taking an FFT, zeroing the unwanted bins and taking the inverse FFT?

### [Multirate DSP — decimation, interpolation, polyphase and half-band filters, CIC filters, channelisers](kb/14-sdr-dsp/multirate-dsp-decimation-cic.md)
- How do I get from my SDR's 2.4 MS/s down to the ~500 kS/s a LoRa decoder wants, cheaply and without aliasing?
- What is decimation vs downsampling, and interpolation vs upsampling?
- What is a polyphase filter and why does it save a factor of M?
- Why are half-band filters everywhere (AD936x, FPGAs), and what makes them cheap?
- How does a CIC filter work, why does it need no multipliers, how many bits does it need, and what is "droop"?
- How do I compensate CIC droop?
- How do I resample by a non-integer ratio like 5/24?
- How should I split a big decimation factor into stages?
- How can one FFT receive 8 or 64 channels at once (polyphase filter bank channeliser)?
- What is the $f_s/4$ trick for turning real samples into complex ones?

### [FFT spectral analysis — DFT, windows, scaling to dBFS/Hz, averaging and spectrograms](kb/14-sdr-dsp/fft-spectral-analysis-windows.md)
- What exactly does an FFT bin represent, and how wide is it?
- Why does my SDR's noise floor drop when I increase the FFT size, while the signal stays put?
- Which window should I use — Hann, Blackman–Harris, flat-top, Kaiser — and what do ENBW and scalloping loss mean?
- How do I convert FFT output to dBFS, dBFS/Hz, or (with calibration) dBm/Hz?
- Why does a tone's level change by up to ~4 dB depending on its exact frequency?
- Does zero-padding increase resolution?
- Why is a single FFT of noise so "grassy", and how much averaging do I need?
- Why does averaging in dB give a noise floor that's 2.5 dB too low?
- How do I measure the noise figure of my SDR setup with an FFT?
- What FFT length should a spectrogram use to show a LoRa chirp clearly?
- What is the FFT's processing gain for finding weak tones?
- How do I estimate a tone's frequency to a fraction of a bin, and which 3-bin estimator gets closest to the Cramér–Rao bound?
- What are a zoom FFT and a sliding DFT, and when do I use them?
- How do I estimate the SNR of a recorded signal?
- Why does a random-data ASK/OOK spectrum look triangular in dB instead of like a sinc?
- Do wavelets help for RF signal analysis?

### [NCOs, digital down-conversion (DDC) and up-conversion (DUC) — phase accumulators, spurs, CORDIC and real SDR chains](kb/14-sdr-dsp/nco-ddc-duc.md)
- How does a numerically controlled oscillator (NCO / DDS) make a sine wave from a counter?
- What frequency resolution does a 32-bit or 48-bit phase accumulator give?
- Why does an NCO have spurs, and how many phase and amplitude bits do I need for a given SFDR?
- Is it really "6 dB per phase bit"?
- What does dithering do for an NCO?
- What is CORDIC and why do FPGAs use it?
- What is inside the digital down-converter of an RTL-SDR, an AD9361, an RFSoC or an FPGA SDR?
- How do I build a DDC for a direct-sampling HF receiver, and a DUC for a transmitter?
- How do I correct ppm error or rocket Doppler with an NCO?
- How do I generate phase-continuous FSK digitally?

### [SDR hardware survey — RTL-SDR, Airspy, SDRplay, HackRF, Pluto, LimeSDR, bladeRF, USRP, KrakenSDR, AntSDR, RX888 — and how to choose](kb/14-sdr-dsp/sdr-hardware-survey.md)
- Which SDR should I buy to monitor my rocket's 433 MHz LoRa telemetry, record a flight, or build a ground station?
- What do the specs mean — "14-bit", "10 MHz bandwidth", "NF 3.5 dB" — and which ones are marketing?
- Which SDRs can transmit, which are full duplex, and which have phase-coherent multiple channels?
- Can a Pluto really do 70 MHz–6 GHz? Is the hack safe?
- What SDR do I need for an FMCW radar, direction finding (DOA), or a small phased array?
- Why is my RTL-SDR V4 hard to buy now, and what replaced it?
- How much USB bandwidth / disk do I need for recording?
- Does the SDR's noise figure matter if I put an LNA in front?

### [GNU Radio and the SDR software stack — drivers (UHD, libiio, SoapySDR), applications, libraries, SigMF recording and host performance](kb/14-sdr-dsp/gnu-radio-and-software-stack.md)
- What is GNU Radio, how does a flowgraph work, and what are blocks, stream tags and messages?
- GNU Radio 3.10 or 4.0 — which should I use in 2026?
- What is the difference between UHD, libiio, SoapySDR and gr-osmosdr, and which one does my SDR need?
- Which application should I use to just *look* at the spectrum (SDR++, SDR#, GQRX, SDRangel…)?
- How do I decode LoRa with an SDR (gr-lora_sdr)?
- How should I record IQ so I (and my tools) can read it later — what is SigMF?
- What do "O" and "U" mean in my terminal, and why am I dropping samples?
- Is Python fast enough, or do I need C++ / GNU Radio / an FPGA?
- Where do I start if I've never written SDR code?

### [Software demodulation — FM, AM, SSB, FSK/GFSK, PSK, LoRa and a complete packet pipeline in DSP](kb/14-sdr-dsp/software-demodulation.md)
- How do I demodulate FM from IQ samples in one line of code?
- What sample rates and filters does a broadcast-FM or NBFM receiver chain need, and what is de-emphasis?
- How do I demodulate AM and SSB (USB/LSB) from complex baseband?
- What is the best way to demodulate FSK/GFSK telemetry — discriminator or matched filters — and how much does the cheap way lose?
- How does a software QPSK receiver lock onto carrier and symbol timing (Costas loop, Gardner)?
- How is LoRa demodulated in software, and why is its error rate exactly that of M-ary FSK?
- How do I go from IQ samples to verified packets (preamble, sync word, length, CRC)?
- How would I decode APRS (AX.25 AFSK) or 433 MHz OOK sensors with an SDR?
- Why does my demodulated SSB sound like Donald Duck, or my FSK decode with inverted bits?
- What does a noise blanker do, and where must it go in an SDR receiver chain?
- Does DSP noise reduction improve weak-signal sensitivity?
- What are IF shift, passband tuning and roofing filters, and can an SDR have a digital roofing filter?

### [FPGAs for SDR — when to use one, DSP slices, fixed point, CORDIC, Zynq + AD9361, RFSoC, open-source gateware and latency](kb/14-sdr-dsp/fpga-for-sdr.md)
- When do I actually need an FPGA in an SDR, and when is a PC or microcontroller enough?
- What is a DSP slice, and how many do I need for a given filter at a given sample rate?
- How do I plan fixed-point word lengths, and which rounding mode should I use?
- How is CORDIC used in FPGA radios (NCOs, FM discriminators, magnitude/phase)?
- What do the Pluto's Zynq-7010, an AntSDR's Zynq-7020 or an RFSoC give me?
- Which open-source FPGA SDR projects can I learn from (ADI HDL, RFNoC, openwifi, Maia SDR, HackRF Pro gateware, LiteX)?
- How much latency does an FPGA path have compared with USB + PC?
- How do I verify FPGA DSP (bit-true models)?

### [Signal identification and spectrum surveys — identifying unknown signals (bandwidth, modulation fingerprints, cyclostationary symbol-rate estimation, burst timing), a catalogue of common signals, and surveying 433/868/915 MHz at a launch site](kb/14-sdr-dsp/signal-identification-and-spectrum-survey.md)
- What is this signal on my waterfall, and how do I work out what it is?
- How do I measure the bandwidth, symbol rate (baud) and modulation of an unknown signal?
- How does "cyclostationary" processing find a symbol rate, and why does squaring a signal reveal its carrier?
- What do FM broadcast, ADS-B, AIS, APRS, POCSAG, LoRa, Wi-Fi, Bluetooth, LTE, GNSS and radar look like, and where are they?
- What are the flat square blocks either side of FM broadcast stations?
- Is that signal real, or is my SDR making it (DC spike, image, overload, USB noise)?
- How do I tell the spreading factor of a LoRa signal from a waterfall?
- How do I survey 433 / 868 / 915 MHz at a launch site before flight day, and how long must I listen?
- How do I use rtl_power, heatmap.py, SDR++, inspectrum, URH and rtl_433 for this?
- rtl_433 cannot decode my 433 MHz signal — what next?
- What does the "dBm" column in rtl_power output actually mean?

### [SDR front ends — overload, blocking and spurious responses from nearby transmitters, preselector filters, when an LNA helps or hurts, ESD/over-power/lightning protection, bias tees and host-noise hygiene](kb/14-sdr-dsp/sdr-front-end-protection-and-filtering.md)
- Why do strong FM broadcast stations show up all over my RTL-SDR spectrum — even at 410 MHz?
- How strong are the signals near a broadcast tower, a cell site, or my own uplink transmitter, and can they damage my SDR?
- Does putting an LNA in front of my SDR always help? When does it make things worse?
- Should the filter go before or after the LNA?
- Does a cavity or SAW filter actually help my 915/923 MHz LoRa (Meshtastic) receiver?
- How do I protect an SDR from my own 2 W transmitter, static on the antenna, ESD and lightning?
- Will a limiter save my HackRF? Will a TVS diode hurt my GNSS signal?
- How do I use a bias tee safely, and what happens with a DC-grounded antenna?
- Is this "cheap LNA" oscillating, and how do I get rid of USB noise and spurs?
- How do I feed one antenna to several SDRs (or an SDR and a LoRa module) without losing sensitivity?
- How much rejection does my preselector need near an FM or cellular transmitter?
- Why does my noise floor not drop when I add an attenuator, and what does that tell me?

### [SDR gain staging and reception recipes — setting LNA/mixer/VGA gain, AGC, overload signs, phantom signals, bias-tee LNAs, a dynamic-range demonstration, and step-by-step recipes for ADS-B, AIS, APRS, Meteor-M weather satellites, the ISS, LoRa (gr-lora_sdr) and rtl_433](kb/14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md)
- How should I set the RF gain on my RTL-SDR — is more gain always better?
- What do the LNA, mixer and VGA gain settings of the R820T/R828D tuner do?
- Should I turn on AGC (tuner AGC or RTL AGC)?
- What does overload look like on the waterfall, and how do I fix it?
- Why do I hear FM stations at 410 MHz, or a 446 MHz handset while tuned to 2 m?
- Does a bias-tee LNA help, and when does it make things worse?
- How much dynamic range does an 8-bit SDR really have, and how can I see it for myself?
- How do I receive ADS-B, AIS and APRS with an RTL-SDR?
- Can I still receive NOAA weather satellites? How do I decode Meteor-M LRPT?
- How do I hear the ISS?
- How do I decode LoRa packets with gr-lora_sdr, and 433 MHz sensors with rtl_433?
- Does a higher sample rate give better sensitivity?

## 15-lora-ism-radios — 

### [LoRa physical layer — chirp spread spectrum from first principles](kb/15-lora-ism-radios/lora-phy-css-math.md)
- What exactly is a LoRa chirp, and how does a chirp carry bits?
- What do spreading factor (SF), bandwidth (BW) and coding rate (CR) actually change?
- Why is the LoRa symbol time $2^{SF}/BW$, and what is a "chip"?
- How do I calculate the LoRa bit rate for a given SF, BW and CR?
- How does a LoRa receiver demodulate — why "de-chirp and FFT"?
- Where does LoRa's "processing gain" come from and how big is it?
- How long is my packet on the air (time-on-air), and why do SX127x and SX126x formulas look different?
- What are the preamble, sync word, header, CRC and low-data-rate optimisation (LDRO)?
- Why does each SF step only buy ~2.5 dB of sensitivity instead of 3 dB?
- What do the 4.25 symbols and the "+8" in the time-on-air formula mean?
- Why can't my SX1262 talk to my SX1276 at SF6?

### [LoRa sensitivity, link budget and realistic range](kb/15-lora-ism-radios/lora-sensitivity-and-link-budget.md)
- How do I calculate the sensitivity of a LoRa receiver for a given SF and bandwidth?
- Why does LoRa work below the noise floor, and what SNR does each SF need?
- What noise figure do Semtech chips really have?
- Is EBYTE's "−147 dBm sensitivity at 2.4 kbps" believable?
- What range can my E22-400T33D (433 MHz, 2 W) or E220-900T30D (900 MHz, 1 W) actually reach from a rocket?
- If LoRa's link budget is 160+ dB, why do rockets lose telemetry after landing?
- Would a Singapore-legal 10 mW (433 MHz) or 100 mW (920 MHz) radio still reach 10–30 km?
- Are the "LoRa world records" (700–1300 km) real, and what do they mean for me?
- How much does urban noise and interference in Singapore cost me?

### [LoRa impairments — frequency offset, Doppler, drift, timing, capture and interference](kb/15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)
- How much frequency error between transmitter and receiver can LoRa tolerate?
- Does a Mach 3–5 rocket's Doppler shift break a LoRa link at 433 or 915 MHz?
- Why can acceleration (Doppler *rate*) break LoRa even when the Doppler shift is small?
- Why does a ground station close to the pad see more "acceleration" than the rocket's accelerometer reports?
- Which SF/BW settings survive the boost phase of a high-power rocket?
- Do I need a TCXO, or is a ±10–20 ppm crystal fine?
- What does low-data-rate optimisation (LDRO) protect against, and can I force it on?
- What is the LoRa capture effect, and what happens when two packets collide?
- Are different spreading factors really orthogonal?
- How does multipath affect LoRa?
- Can my 433 MHz radio interfere with my 900 MHz radio on the same rocket?

### [Semtech LoRa chip family — SX127x, SX126x, LLCC68, LR11xx, LR2021, SX128x, STM32WL](kb/15-lora-ism-radios/semtech-chip-family.md)
- Which LoRa chip is inside my E22 / E220 / RFM95 / Heltec board, and does it matter?
- What is the difference between SX1276, SX1278, SX1262, SX1268 and LLCC68?
- Why can't an LLCC68 run SF12?
- Which chip should I use for a new 433 MHz or 920 MHz rocket radio?
- What do PA_BOOST, OCP, paDutyCycle/hpMax, DIO2 RF-switch and DIO3 TCXO settings do?
- What SX126x errata/known limitations must firmware work around?
- What are LR1110/LR1120/LR1121/LR2021 and SX1280, and when are they worth it?
- Why must I run image calibration for 433 MHz on an SX126x?
- What does the Semtech SX1262 reference design contain (matching, harmonic filter, balun, RF switch, TCXO)?
- Why does my custom LoRa board transmit 30–50 dB low?
- How do I bring up a bare SX126x/SX127x board step by step?
- Can I find a landed rocket by RSSI, by time of flight (SX1280 ranging) or by LoRa TDOA, and how accurate is each?

### [LoRa modules — EBYTE E22/E220/E32/E19, HopeRF RFM9x, Heltec, RAK, Seeed, LilyGo](kb/15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)
- What is inside an EBYTE E22-400T33D and E220-900T30D, and what do the part-number letters mean?
- How do the EBYTE M0/M1 modes, AUX pin and configuration registers work?
- What SF/BW/CR does an EBYTE "air data rate" of 2.4k or 19.2k correspond to?
- How do I read RSSI from an EBYTE module, and what are LBT, WOR and the "encryption key"?
- How much current and heat does a 2 W module need, and what supply should I design?
- Can an EBYTE UART module talk to a bare SX1262 running RadioLib?
- Which dev boards (Heltec, RAK4631, T-Beam, Wio-E5, RFM95) use which chip?
- Should I use a UART module or a bare chip with my own firmware for the next flight computer?

### [LoRaWAN vs raw LoRa (and Meshtastic, Reticulum) — what each is for, and why rockets use raw LoRa](kb/15-lora-ism-radios/lorawan-vs-raw-lora.md)
- What is the difference between LoRa and LoRaWAN?
- What are LoRaWAN Class A, B and C devices?
- What does ADR do, and why is it bad for moving devices?
- Could I send rocket telemetry through The Things Network or a LoRaWAN gateway?
- What are Meshtastic and Reticulum, and are they useful for a launch site?
- Which should I use for a rocket downlink, an RTK-correction link, or a recovery beacon?

### [Other ISM radios — FSK/GFSK sub-GHz, SiK/RFD900x, XBee, 2.4 GHz (nRF, BLE coded, ESP-NOW LR, SX1280 FLRC) — and when they beat LoRa](kb/15-lora-ism-radios/other-ism-radios-fsk-2g4.md)
- How does LoRa compare with plain FSK/GFSK radios (CC1101, Si4463, SX126x FSK) at the same data rate?
- What are SiK/RFD900x telemetry radios, and why do UAV and rocketry people use them?
- Is an XBee-PRO 900HP better than LoRa?
- What can 2.4 GHz options (nRF24L01+, nRF52840 BLE long range, ESP-NOW LR, SX1280 FLRC) do?
- When should I choose FSK over LoRa for rocket telemetry?
- How does ExpressLRS work (packet rates, hopping, telemetry ratio), and are its range claims believable?
- How do I recognise an ExpressLRS or drone link, or a jammer, on an SDR waterfall?
- Can I send a camera image or voice from a rocket over LoRa, and how long does a 600 kB photo take?
- What is Wi-Fi HaLow (802.11ah), and is it better than LoRa for images?

### [Rocket telemetry radio design — requirements, packets, FEC, Doppler, antennas, redundancy, what teams flew](kb/15-lora-ism-radios/rocket-telemetry-radio-design.md)
- How do I choose SF, bandwidth and packet size so my rocket telemetry keeps up with the flight?
- What should a telemetry packet contain, and how do I make packet loss measurable?
- Is LoRa's built-in coding enough, or do I need extra FEC?
- Which radio settings survive boost (Doppler rate), and which are best after landing?
- Why does telemetry drop out near apogee or right above the pad, and how do antenna placement and roll matter?
- Does the motor plume block the signal?
- How do I run a 433 MHz and a 900 MHz radio on the same vehicle without them interfering?
- Should my rocket accept commands over the radio, and if so how do I make that safe?
- Can I send RTK corrections to the rocket over LoRa while it is also transmitting telemetry?
- What have amateur and university rocket teams actually flown for telemetry?
- Which commercial rocket GPS trackers and RDF beepers exist, on which bands and at what power, and can I receive them with an SDR?
- Why won't an AirTag or a Bluetooth tag find my rocket in a field?

### [LoRa ground-station design for rocket telemetry — antennas, LNA/filter chain, tracking, diversity, SDR recording](kb/15-lora-ism-radios/ground-station-design.md)
- Should my ground station use an omni, a Yagi or a helix?
- Where do the LNA and the SAW filter go, and in which order?
- How much does coax loss before the receiver cost me?
- How fast must I track the rocket, and can I do it by hand?
- Is it worth running two receivers (diversity)?
- How do I record the raw LoRa signal with an SDR and decode it later?
- How high must my antenna be for a ground-to-ground or post-landing link?
- What should the ground station log so a flight can be analysed afterwards?
- Why might a 923 MHz receiver in Singapore be desensitised by nearby cellular sites?
- Why does my ground station hear the rocket but the rocket never hears my uplink (or the ACK)?
- Will a louder 1 W node fix my LoRa mesh?
- Why does my receiver stop working when the transmitter is right next to it?
- What does LoRaWAN "TXPower 3" mean in dBm at the antenna port?
- What do I do with the RF port I'm not using?

### [ISM/SRD band plans, power limits, duty cycle and dwell time for LoRa (433, 868, 915, 923 MHz)](kb/15-lora-ism-radios/ism-band-plans-duty-cycle.md)
- Which frequencies and power levels may a LoRa radio use in Singapore?
- Is my 2 W E22-400T33D at 433 MHz or 1 W E220-900T30D at 900 MHz legal in Singapore?
- What are the EU 868 MHz sub-bands and duty-cycle limits (ETSI EN 300 220)?
- What do the US FCC §15.247 rules (hopping, 400 ms dwell, 1 W, 6 dBi) mean for LoRa?
- What is AS923 and why does Singapore use it?
- What is the difference between e.r.p., e.i.r.p. and conducted power?
- How often may I transmit a telemetry packet under a 1 % or 10 % duty cycle?
- Why can't SF11/SF12 at 125 kHz be used in 400 ms-dwell regions?
- Can we use amateur 33 cm (902–928 MHz) LoRa at Spaceport America?
- What are Australia's LIPD limits for LoRa at 433 and 915–928 MHz?
- Which licence lets us run 1–2 W LoRa telemetry in Singapore?

### [Choosing and judging LoRa antennas — gain vs pattern (why a high-gain omni is bad for a rocket overhead), spotting fake gain claims, measuring with a NanoVNA and comparative RSSI tests, ground planes, connectors, cable loss and mounting, and what to use on the airframe and at the ground station](kb/15-lora-ism-radios/choosing-and-judging-lora-antennas.md)
- Will a higher-dBi antenna give my LoRa / Meshtastic node more range?
- Why did my "10 dBi" fibreglass omni do worse than the stock whip?
- Is a high-gain omni good for receiving a rocket's telemetry?
- How can I tell whether an antenna's gain claim is plausible?
- My board came with a stubby antenna — is it any good, and is it even for my band?
- How do I test an antenna with a NanoVNA, and what SWR is good enough?
- How do I compare two antennas with RSSI properly — how many packets do I need?
- Does a quarter-wave whip need a ground plane?
- SMA or RP-SMA? Why doesn't my antenna fit?
- How much does the cable between the radio and the antenna cost me?
- Where and how should I mount a LoRa antenna?
- What antenna should go on the rocket, and what at the ground station?

### [LoRa mesh capacity and congestion — airtime, ALOHA collisions, flooding overhead, Meshtastic presets and a launch-day estimate](kb/15-lora-ism-radios/lora-mesh-capacity-and-congestion.md)
- How much airtime does one Meshtastic message cost, and how much more does flooding add per hop?
- What happens when a LoRa mesh channel gets congested, and why do big events overload Meshtastic?
- What is the ALOHA collision probability, and where does the famous 18 % come from?
- Are 6–7 mesh hops useful or harmful?
- Why can more transmit power or more ROUTER nodes make a mesh worse?
- Why can a high-power node be heard but not hear others?
- Should a busy mesh move from LongFast to a faster preset?
- How does MeshCore's routing differ from Meshtastic's flooding?
- How many LoRa links can share an area before they collide?
- How many rockets and ground stations can share a channel on launch day?
- My node "heard" something 5 000 km away. Is that an RF record?

## 16-simulation-tools — 

### [RF simulation tool landscape — which tool for which problem (circuits, lines, antennas, EM, links, radar), free vs commercial, fidelity, learning curve, macOS support](kb/16-simulation-tools/tool-landscape-overview.md)
- I want to simulate X (a matching network, a filter, a PCB antenna, a Yagi, a link, a radar) — which tool should I use?
- Which free tools run natively on my Mac, and which need Windows?
- How accurate is each kind of tool, and how long does it take to learn?
- When is a closed-form calculator enough and when do I need a full-wave EM solver?
- What does this knowledge base already provide (scripts, calculators) so I don't start from zero?
- How do I predict coverage over real terrain (the landing area, a hill between me and the rocket), and how far can I trust it?
- Why does a TTN-Mapper-style coverage map show the link working much further away than it really does?

### [SPICE circuit simulation for RF — ngspice, LTspice, Qucs-S, Xyce; AC, noise, transient, .four, S-parameters; vendor models and RF limits](kb/16-simulation-tools/spice-circuit-simulation.md)
- Can I simulate an RF matching network or filter in SPICE, and how do I get S-parameters out of it?
- What is the difference between AC, noise, transient and `.four` analyses, and which one answers my question?
- How do I run ngspice from the command line or from Python on a Mac (with or without KiCad)?
- Why does my SPICE noise figure come out wrong by a fraction of a dB (or by 3 dB)?
- How do I use a vendor's SPICE model or S-parameter file for an LNA or transistor?
- Where does SPICE stop being trustworthy at RF (distributed effects, parasitics, harmonic balance)?
- How do I simulate an oscillator start-up, and why does my oscillator not start in simulation?

### [RF circuit simulators and harmonic balance — HB vs transient, Qucs-S/QucsatorRF, Xyce, QucsStudio, Keysight ADS, Cadence AWR Microwave Office, Sonnet Lite, SimSmith, RFSim99; what each costs and does](kb/16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)
- What is harmonic balance, and when is it better than a SPICE transient + FFT?
- Can I simulate PA compression, IP3, mixer conversion gain or oscillator phase noise with free tools?
- What do Keysight ADS and Cadence AWR Microwave Office do that SPICE doesn't, and can a student get them free?
- Which free RF tools run on macOS (Qucs-S, SimSmith) and which need Windows (QucsStudio, RFSim99, Sonnet Lite, AWR, ADS)?
- What is circuit envelope, load-pull, X-parameters — do I need them for a LoRa/GNSS front end?
- Can I get an oscillator's phase noise from a transient simulation, and does it agree with Leeson's formula?
- Is Leeson's $P_s$ the power in the tank or something else (why do two phase-noise formulas differ by 6 dB)?

### [EM solvers compared — FDTD, FIT, MoM, FEM and 2.5-D planar methods; openEMS, MEEP, gprMax, Elmer, Palace, OpenParEM, Sonnet, HFSS, CST, FEKO, EMPro; accuracy pitfalls](kb/16-simulation-tools/em-solvers-fdtd-mom-fem.md)
- What is the difference between FDTD, FEM and the method of moments, and which should I use for a PCB antenna, a filter, a connector launch or a nose-cone radome?
- What does "2.5-D planar" (Sonnet, Momentum, AXIEM) mean?
- Which free solvers exist (openEMS, MEEP, gprMax, Elmer, Palace, OpenParEM) and what do the commercial ones (HFSS, CST, FEKO, EMPro) add?
- What do the free student editions limit (mesh size, platform)?
- Why do two solvers disagree on my antenna, and which pitfalls (mesh, ports, boundaries, convergence) cause most errors?
- How big a model can I afford — cells, unknowns, run time?

### [NEC antenna modelling in practice — NEC-2/4 on macOS (PyNEC, xnec2c, 4nec2, EZNEC, MMANA-GAL), card decks, segmentation, ground models, 433 MHz dipole and Yagi decks cross-checked against an independent MoM](kb/16-simulation-tools/nec-antenna-modelling.md)
- How do I run NEC-2 on a Mac without Windows?
- What do the GW, GE, GN, EK, EX, FR, RP cards mean, and what does a minimal deck look like?
- How do I model a 433 MHz dipole and a DL6WU Yagi, and what numbers should I expect?
- Which ground model should I use (free space, perfect, reflection-coefficient, Sommerfeld)?
- My NEC average-gain test says 0.96 for a lossless Yagi — is my model wrong?
- Does NEC agree with another independent code, and by how much?
- When should I stop using NEC and switch to openEMS?
- Can an optimiser (Nelder–Mead, genetic/differential evolution, particle swarm) design my Yagi, and which one should I use?
- Why did my optimiser find a 10 dBi 3-element Yagi with a 4 Ω feed?

### [openEMS workflow — installing on Apple Silicon, Python interface, meshing (λ/20, thirds rule), ports, boundaries, NF2FF, and two worked runs (microstrip line, 2.45 GHz patch)](kb/16-simulation-tools/openems-workflow.md)
- How do I install openEMS and its Python interface on an M-series Mac?
- What does an openEMS Python script consist of (geometry, materials, mesh, excitation, ports, boundaries, NF2FF)?
- How fine must the mesh be, what is the "thirds rule", and how many cells through a 1.6 mm substrate?
- Lumped port or microstrip (MSL) port — which, and how do I get S11, Z_in, Z0 and εeff out?
- How long should the simulation run (end criterion), and why do two identical runs stop at different time steps?
- Does openEMS actually give the right answer for a microstrip line and a patch antenna on FR-4?
- How do I get directivity, gain and radiation efficiency from the near-to-far-field (NF2FF) box?
- How much does a fibreglass nose cone detune my 433/915 MHz whip?
- How much does a slot in the ground plane under a trace, or a connector pad on thin prepreg, cost me?
- Can openEMS simulate a scanned phased-array unit cell (Floquet), and if not, how do I see scan blindness?
- How do I dump fields and animate them in ParaView, import STL or curved parts, and avoid tiny mesh cells?
- My simulated S11 has spikes, sits at 0 dB, or is nonsense — what did I set up wrong?

### [Python RF toolkit — scikit-rf (networks, Touchstone, media, calibration, time domain, circuits, vector fitting), numpy/scipy signal, PyNEC, openEMS, radar/DOA/comms libraries, and this KB's rfcalc](kb/16-simulation-tools/python-rf-toolkit.md)
- How do I load, plot, cascade and de-embed Touchstone (.s1p/.s2p) files in Python?
- Can Python replace a circuit simulator for matching networks and filters?
- How do I calibrate or de-embed NanoVNA data in Python (SOL, fixtures)?
- How do I get a TDR (impedance vs distance) plot from S-parameters?
- How do I turn a measured S-parameter file into a SPICE model?
- Which Python packages exist for NEC, FDTD, radar simulation, direction finding, comms and SDR?
- What does this KB's `tools/rfcalc` package do, and how do I call it?

### [Impedance and RF calculators — KiCad PCB Calculator, Qucs transcalc, Saturn PCB Toolkit, AppCAD, JLCPCB calculator, online tools and rfcalc, compared against a 2-D field solver](kb/16-simulation-tools/impedance-and-rf-calculators.md)
- Which impedance calculator should I trust for a 50 Ω trace on a JLCPCB board?
- Why do KiCad, Saturn, JLCPCB and online calculators give different widths for the same 50 Ω line?
- How accurate is the IPC-2141 microstrip formula?
- How much do copper thickness and soldermask change Z0 on a 2-layer vs a 4-layer board?
- What other RF calculators are worth having (link budget, matching, noise, skin depth, LoRa air time)?
- How do I use this KB's `rfcalc` calculators from the command line?

### [Simulation verification and validation for RF — independent truth, pre-registration, convergence studies (Richardson, GCI), analytic benchmarks, cross-solver comparison, correlation to measurement, port de-embedding, faithful reporting](kb/16-simulation-tools/simulation-validation.md)
- How do I know my simulation is right, not just converged?
- What is the difference between verification and validation?
- How do I do a mesh-convergence study and put an uncertainty on the result (Richardson extrapolation, GCI)?
- Which analytic benchmarks should every RF solver reproduce before I trust it?
- Two solvers disagree — how do I find out which one (or which set-up) is wrong?
- How do I compare a simulation with a NanoVNA measurement fairly (reference planes, de-embedding)?
- What does "pre-register the expected result" mean for an antenna simulation, and why bother?
- How often do honest pre-registered predictions actually miss, and what do the misses teach?
- My simulated S11 shows spikes, a flat floor or 0 dB — how do I find the set-up error?
- When is the model itself the uncertainty, so that no mesh study helps?

### [Installing RF simulation tools on macOS (Apple Silicon) — tested commands, what worked, what failed](kb/16-simulation-tools/installing-tools-macos.md)
- How do I install ngspice on a Mac, and do I even need to if KiCad is installed?
- Can I run openEMS on an M-series Mac? Is there a Homebrew formula or a pip/conda package?
- How do I get NEC-2 on macOS without Windows (PyNEC, xnec2c, 4nec2 under Wine)?
- Does LTspice run natively on macOS, and why does its Homebrew install ask for my password?
- Why did macOS warn me that Qucs-S "could not be verified", and is it safe to open?
- Which of these tools were actually installed and tested on this machine, and with what result?
- How do I check that an installed solver gives correct answers before I trust it?

## 17-test-measurement — 

### [VNA fundamentals and calibration — architecture, error models (3-, 8-, 12-term), SOL/SOLT/SOLR/TRL/LRM, cal-kit definitions, port extension, dynamic range and uncertainty](kb/17-test-measurement/vna-fundamentals-calibration.md)
- What is inside a vector network analyzer and what does "directivity" or "source match" mean for it?
- Why does a VNA need calibration at all, and why exactly three standards for a one-port?
- How do you derive the open-short-load (SOL) calibration equations?
- What are the 12-term and 8-term error models, and which one does my NanoVNA/LibreVNA use?
- SOLT, SOLR (unknown thru), TRL, LRM — which calibration should I use and why?
- What are "offset delay", "C0…C3" and "L0…L3" in a calibration-kit definition, and do they matter below 1 GHz?
- What is the difference between port extension and de-embedding?
- Why does my calibration go bad when I add an SMA-to-U.FL adapter after calibrating?
- How do IF bandwidth and averaging change dynamic range and sweep time?
- How accurate is a return-loss number from a low-cost VNA?
- Is a home-made SOL kit good enough, and how do I characterise it?
- What are ECal and LibreCAL, and can I trust them?
- How do I calibrate when my DUT has a UHF, BNC, MMCX or U.FL connector?
- Should I "calibrate with a 73 Ω resistor" to measure a dipole, or set the VNA to 75 Ω?
- Does my VNA's frequency accuracy matter?

### [NanoVNA, LiteVNA and LibreVNA in practice — models, firmware, accuracy vs frequency, software, and step-by-step recipes (antenna S11 in situ, matching, filters, cables, TDR, SMD parts)](kb/17-test-measurement/nanovna-librevna-practical.md)
- Which low-cost VNA should I buy (NanoVNA-H4, NanoVNA V2 Plus4, LiteVNA, LibreVNA) for 433 MHz, 915 MHz and GNSS work?
- Why does my NanoVNA get noisy above 300 MHz, and how far can I trust it at 915 MHz and 1.5 GHz?
- Which firmware and PC software should I use?
- How do I measure my rocket's antenna S11 in its final position without the cable lying to me?
- How do I tune a pi-match footprint on my board with a NanoVNA?
- How do I measure a filter's S21, a cable's loss and velocity factor, or find a fault with TDR?
- How do I measure an SMD inductor, capacitor or ferrite bead with a NanoVNA?
- Why does the SWR change when I touch the cable, and how do I stop it?
- Can I connect an LNA or a transmitter directly to the NanoVNA?
- How do I build and characterise my own SMA calibration kit, and is LibreCAL worth it?
- How do I calibrate through a UHF, BNC, MMCX or U.FL adapter?
- Can I set the NanoVNA to 73 Ω or 75 Ω to measure a dipole or TV coax?

### [Spectrum analyzers — superheterodyne architecture, RBW/VBW, sweep time, DANL, detectors and the −2.51 dB log-averaging bias, noise and channel power, internal distortion checks, tinySA and budget analyzers, and measuring a LoRa transmitter safely](kb/17-test-measurement/spectrum-analyzers.md)
- How does a swept spectrum analyzer work, and what do RBW and VBW actually do?
- Why does the noise floor drop 10 dB when I reduce RBW by 10×, but my CW signal stays the same?
- Why does the analyzer read noise 2.5 dB too low, and which detector should I use for noise, LoRa and CW?
- How do I measure channel power and occupied bandwidth correctly?
- Is that spur real, or is my analyzer making it?
- How do I measure a 1 W LoRa module's power and harmonics without destroying my tinySA?
- What can a tinySA / tinySA Ultra do, and when do I need a Siglent/Rigol-class analyzer?
- Why does my SA say −60 dBc/Hz phase noise when the TCXO datasheet says −130?
- Why does the noise floor jump up at certain frequencies (band edges) on a microwave analyzer?
- What is the big signal at 0 Hz, and why can't I measure low frequencies with my SA?
- How do I measure gain and phase below 100 kHz, and why are my milliohm PDN readings wrong there?

### [Oscilloscopes and probing for RF — bandwidth and rise time, sample rate and ENOB, passive-probe loading, low-Z (Z0) and active probes, ground-lead ringing, near-field H/E probes, and the scope FFT](kb/17-test-measurement/oscilloscopes-and-probing-for-rf.md)
- What scope bandwidth do I need to see a 433 MHz or 915 MHz signal, or a fast edge?
- Why does my 10× probe make a 100 MHz signal disappear or ring?
- What is a Z0 (low-impedance, resistive-divider) probe and how do I build one?
- How long can the probe's ground lead be?
- How do I find which part of my board is radiating a spur (near-field probes)?
- Is a scope's FFT a substitute for a spectrum analyzer?
- How do I look at the LoRa module's supply current burst and PA ramp?

### [RF power measurement — thermal and diode sensors, average/peak/burst power of LoRa packets, directional couplers and wattmeters, attenuators and their ratings, mismatch uncertainty, and cheap AD8307/AD8318 log-detector meters](kb/17-test-measurement/rf-power-measurement.md)
- What is the most accurate way to measure my LoRa module's output power on a student budget?
- Thermistor, thermocouple, diode — what is the difference, and why do diode sensors misread some signals?
- My power meter shows +8 dBm but the module is set to +22 dBm — why?
- How much uncertainty does mismatch add to a power reading?
- How do I choose attenuators and dummy loads (power rating, frequency, accuracy)?
- How do I use a directional coupler or a through-line wattmeter, and how far can I trust its SWR reading?
- How good are the cheap AD8307/AD8318 log-detector power meter modules, and how do I calibrate one?

### [Noise-figure measurement — Y-factor method (derived), ENR and noise sources, second-stage correction, cold-source/gain method with a spectrum analyzer, SDR-based NF, hot/cold loads, and conducted LoRa sensitivity testing with a step attenuator](kb/17-test-measurement/noise-figure-measurement.md)
- How does the Y-factor method work, and how do I derive the noise figure from "noise source on / off"?
- What is ENR, and should I use a 6 dB or a 15 dB ENR noise source?
- Why must I "calibrate" the noise-figure setup before inserting the LNA (second-stage correction)?
- Can I measure an LNA's noise figure with a tinySA, a Siglent analyzer or an SDR — and how accurately?
- What are the cheap noise sources on AliExpress good for?
- How do I measure my LoRa ground-station receiver's real sensitivity with a step attenuator, and why does my receiver look better than the datasheet?
- How many packets do I need to count to claim "1 % PER at −137 dBm"?

### [Phase-noise measurement — direct spectrum-analyzer method and its corrections, phase-detector (PLL/quadrature) method, delay-line discriminator, two-channel cross-correlation, and low-cost setups](kb/17-test-measurement/phase-noise-measurement.md)
- How do I measure an oscillator's phase noise L(f) with a spectrum analyzer, and which corrections apply?
- Why does every TCXO I measure look like −98 dBc/Hz at 10 kHz?
- What is the phase-detector (PLL) method, and how do I calibrate it?
- When is a delay-line discriminator useful?
- How does cross-correlation measure noise below the instrument's own floor, and how long does it take?
- What can I do on a student budget (tinySA, SDR, sound card, mixer)?
- How does a 32 MHz TCXO's phase noise show up at 915 MHz?
- How much phase noise does an amplifier add to a clean carrier, and how do I measure it?
- Can I average phase noise away?

### [Antenna ranges and over-the-air (OTA) testing — DIY far-field and ground-reflection ranges, reference antennas, SDR/turntable patterns, TRP/TIS, and field-testing a rocket telemetry link (drone/kite tests, range test by attenuation)](kb/17-test-measurement/antenna-range-ota-testing.md)
- How do I set up a backyard/field antenna range at 433/915 MHz, and at what heights?
- What is a ground-reflection range, and why would I *want* the ground reflection?
- What reference antenna should I use for gain measurements?
- What do TRP and TIS mean, and can I estimate them without a chamber?
- My ground-level range test only reached 1.5 km — will the rocket link really work at 10 km?
- How does a "range test by attenuation" work, and how do I turn it into a link margin?
- How many packets/RSSI readings do I need for a meaningful field-test number?

### [SDRs as test equipment — RTL-SDR, HackRF, ADALM-Pluto (and Airspy/SDRplay) as spectrum analyzer, power meter, signal generator and noise-figure meter; calibration and accuracy limits](kb/17-test-measurement/sdr-as-test-equipment.md)
- Can an RTL-SDR, HackRF or Pluto replace a spectrum analyzer for my LoRa and GNSS work?
- How do I turn "dBFS" into dBm, and how accurate is it?
- What are the spikes and mirror signals I see on SDR spectra — are they real?
- Can I use a HackRF or Pluto as a signal generator for receiver testing?
- Can an SDR measure noise figure?
- What SDR setup do I need to log antenna patterns or range-test RSSI?

### [Signal generators and sources — lab generators, ADF4351/MAX2870 synthesiser boards (harmonics, spurs, phase noise, filtering), Si5351 clocks, tinySA as a generator, noise sources, calibrated and step attenuators](kb/17-test-measurement/signal-generators-and-sources.md)
- What signal source do I need to test a LoRa receiver, a filter or an LNA?
- Are the cheap ADF4351 / MAX2870 boards usable as signal generators, and what must I add?
- Why does my Si5351 "sine" have strong harmonics?
- Can a tinySA or HackRF be my signal generator?
- How do I make an accurate −130 dBm signal?
- How do I pick and calibrate attenuators and step attenuators?

### [RF lab setup by budget — what to buy first for a student rocketry team (≈S$300, S$2 000, S$15 000), accessories that matter, and how to buy used HP/Agilent gear safely](kb/17-test-measurement/lab-setup-by-budget.md)
- What is the minimum RF test kit a student rocketry team needs for 433/915 MHz LoRa and GNSS?
- What should we buy first: VNA, spectrum analyzer, or power meter?
- What does S$2 000 or S$15 000 buy, new or used?
- Which cheap accessories (attenuators, loads, cables, torque wrench) actually matter?
- How do we buy used HP/Agilent equipment without getting a broken one?

### [Test fixtures and de-embedding — SMD component fixtures, TRL/LRM calibration kits on JLCPCB boards, 2x-thru (IEEE P370) and AFR, open/short compensation, reference-plane management, and measuring chip antennas on small boards](kb/17-test-measurement/fixtures-and-deembedding.md)
- How do I measure a 0402 inductor, capacitor or filter that has no connectors?
- What is the difference between port extension, open/short compensation, 2x-thru de-embedding and TRL?
- How do I design TRL standards on a cheap JLCPCB board, and how long should the lines be?
- When does 2x-thru de-embedding go wrong?
- Where exactly is my reference plane when I measure a chip antenna through a U.FL pigtail?
- How do I stop the test cable from becoming part of a small-board antenna?
- Can the same fixture panel measure the permittivity of my FR-4 or nose-cone material?

### [RF board bring-up and debug playbook — step-by-step bring-up of a new radio/GNSS board (power, clocks, conducted TX, RX sensitivity, antenna match, OTA, integration) with symptom → cause → test tables, stage-by-stage receiver signal tracing and IF alignment, and amplifier/RF-switch failure modes with a safe test set-up](kb/17-test-measurement/rf-bring-up-debug-playbook.md)
- In what order should I bring up a new LoRa/GNSS flight board so that a fault is found at the cheapest step?
- What should I measure, with which instrument, and what are the pass criteria?
- My telemetry range is 10× shorter than the link budget — what do I check first?
- GNSS loses fix only when the flight computer is running — how do I find the culprit?
- The radio resets or drops packets when transmitting — why?
- How do I prove the fix worked?
- How do I trace a weak signal stage by stage through a receiver, and what level should I see at each stage?
- How do I align the IF of a superhet, and why does peaking the IF cans seem to do nothing?
- How do I know my SDR's LNA is actually working?
- Why do amplifiers and RF switches die on the bench, and how do I set up a safe test?
- Why do people split 40 dB of gain into two stages with a pad between them?

### [Bench measurement recipes — is it transmitting, output/source impedance (two-load, four-load, load-pull-lite), SWR-meter calibration and directivity, shield boxes and conducted vs radiated tests, EBYTE module power and harmonics, antenna efficiency on a budget, attenuator range tests, pulsed signals on an SA, ferrite cores, coupled-loop resonance and Q (dip-meter substitute), LCR meter vs VNA, return-loss bridge + SA/TG, resistive taps vs couplers, the NanoVNA as a receiver, why WSPR/RBN antenna comparisons mislead, and RF prototyping (Manhattan, dead-bug, ugly, copper-clad, enclosures)](kb/17-test-measurement/bench-measurement-recipes.md)
- How can I tell quickly whether my transmitter is actually transmitting?
- How do I measure the output impedance of an amplifier, signal generator or radio module?
- Why is a power amplifier's "output impedance" not 50 Ω, and does that matter?
- How do I calibrate an SWR meter, and how far can I trust its 1.1:1?
- How do I read R, X and SWR on an antenna analyser when it doesn't tell me the sign of X?
- How do I build and check a shield box, and when do I test conducted rather than radiated?
- How do I simulate bad reception or long range in the lab?
- How do I measure my EBYTE 2 W module's true output power and harmonics without destroying anything?
- How do I measure an antenna's efficiency without an anechoic chamber?
- How do I turn an attenuator range test into a range prediction, and how accurate is it?
- Why does a pulsed signal read lower on a spectrum analyser than its peak power?
- How do I measure a ferrite core's permeability or A_L?
- How do I find the resonance and Q of a tank, trap or resonator with a NanoVNA instead of a dip meter?
- Should I use an LCR meter or a VNA to measure an RF inductor or capacitor?
- Can I measure return loss with a spectrum analyzer, tracking generator and a return-loss bridge?
- When is a resistor "tap" good enough instead of a directional coupler?
- Can a NanoVNA be used as a receiver or spectrum analyzer?
- Why are WSPR or Reverse Beacon Network comparisons of two antennas so unreliable?
- Should I prototype a 433 MHz circuit Manhattan-style, dead-bug, or just order a JLC board?

### [Interference hunting and RF immunity — finding noise sources (portable SDR, H-field loop, attenuators, DF, body fade), why RCDs/GFCIs trip and Ethernet, audio and sensors get upset, motors and switch-mode supplies as noise sources, ferrites and how to prove a fix, and transmitter RF inside a rocket av-bay](kb/17-test-measurement/interference-hunting-and-rf-immunity.md)
- How do I systematically find what is making noise in my receiver (QRM, "RFI")?
- Can I hunt RFI with a tinySA or an RTL-SDR, and what else do I need?
- What is the "body fade" trick, and why do attenuators stop working when I get close to a transmitter?
- How do I find power-line, PLC, switch-mode-supply or LED noise?
- Why does my RCD/GFCI trip, and can radio interference cause it?
- Ethernet is transformer-coupled, so can ferrites even matter? Where along the cable should the ferrite go?
- Does an iperf throughput test prove that a ferrite fixed my RFI?
- How do I stop a brushed motor or an ignition system from upsetting my electronics?
- Why did my Arduino reset next to a microwave oven, and why did GSM phones buzz in speakers?
- How can one faulty TV knock out a village's broadband?
- Will my own 2 W telemetry transmitter upset the barometer, IMU, magnetometer or pyro channels in the av-bay, and how do I test for that?

### [Basic bench instruments — frequency counters (gate time, ±1 count, reciprocal counting, prescalers, time-base error), multimeters (Ω/V loading, true RMS, crest factor, DMMs at RF and diode RF probes), scope triggering and probe compensation, and dip meters](kb/17-test-measurement/basic-bench-instruments.md)
- My frequency counter shows nine digits — how many of them are true?
- What is gate time, and why does a cheap counter show only "433.920 0 MHz" after one second?
- What is the difference between a direct counter and a reciprocal counter, and what does a prescaler cost me?
- How accurate is the frequency of my 433 MHz transmitter as read on a counter with a plain crystal time base?
- Why does my analogue meter read a lower voltage than my DMM on the same bias node?
- What is "true RMS", and why does my cheap meter read a square wave 11 % high?
- Can I measure RF with a multimeter?
- How do I trigger a scope reliably on a LoRa packet?
- How do I compensate a 10× probe, and what happens if I don't?
- What is a dip meter, and how do I use one (or a NanoVNA instead) to find a resonance?

### [Measuring εr and tanδ — cavity perturbation, split-post/split-cylinder, ring and two-line methods, resonator coupling and Q₀ (DIY with a NanoVNA)](kb/17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md)
- How do I measure the dielectric constant and loss tangent of FR-4 (or my JLCPCB stack-up) with a NanoVNA?
- What is cavity perturbation, and where do the frequency-shift and Q formulas come from?
- What are split-post and split-cylinder resonators, and why do labs use them?
- How does a microstrip ring resonator give εeff, and how do I turn that into εr?
- What is the two-line method, and why do the connectors cancel out?
- What do under-coupled, critically coupled and over-coupled mean, and how do I get the unloaded Q from a measured loaded Q?
- What is the εr of my rocket's fibreglass nose cone, and how do I measure it?
- Why do different labs and datasheets quote different Dk for the "same" FR-4?

## 18-components-parts — 

### [RF transceiver ICs — sub-GHz packet radios, radio SoCs, IQ/SDR transceivers and GNSS front-ends (selection guide)](kb/18-components-parts/rf-transceiver-ics.md)
- Which radio chip should I put on my next rocket flight computer or ground station, other than a LoRa chip?
- How do I compare a CC1101, CC1200, Si4463 and SX1262 fairly when their datasheets quote sensitivity at different data rates?
- Is there a cheap chip that gives me raw I/Q samples so I can run my own waveform, like a mini SDR?
- What is the difference between the AD9361, AD9363 and AD9364, and are the "AD9361" Pluto clones real?
- Which of these chips can JLCPCB actually assemble from LCSC stock, and roughly what do they cost?
- Do I need an external LNA or PA (range extender) in front of the chip, and how much does it buy me?
- Should I design in a bare GNSS front-end IC (MAX2769) or just use a GNSS module?

### [LNAs, PAs, gain blocks and front-end modules — part selection guide (sub-GHz, GNSS, 2.4 GHz, microwave)](kb/18-components-parts/lna-pa-gain-block-mmics.md)
- Which LNA should I put in front of my 433/915 MHz LoRa ground station or my GNSS patch?
- Are the cheap SPF5189Z "LNA 50–4000 MHz" boards any good, and what replaced the SPF5189Z?
- What is the difference between an "LNA", a "gain block" (GALI/ERA/MAR) and a "driver amplifier"?
- How do NF, gain, OIP3 and P1dB of a candidate LNA feed into my receiver cascade?
- Which front-end module gives +27/+30 dBm at 868/915 MHz, and what does it need around it (filter, supply)?
- What do I use for 1–15 W at 433 MHz (LDMOS) or several watts at microwave (GaN)?
- Which of these can JLCPCB assemble from LCSC stock, and roughly what do they cost?

### [Mixers, IQ modulators/demodulators, PLL synthesizers, VCOs, clock generators, TCXOs and DDS — part selection guide](kb/18-components-parts/mixers-plls-vcos-parts.md)
- Which synthesizer should I use as the LO for a home-made 433 MHz / 2.4 GHz / 5.8 GHz / 24 GHz radio or radar?
- Which PLL can generate FMCW chirps (ramps) by itself?
- Is the ADF4351 board from AliExpress good enough, and why does its spectrum look dirty?
- Should I use a passive diode mixer (ADE-1) or an active Gilbert-cell mixer (ADL5801, LTC5562)?
- What IQ modulator/demodulator gives me a direct-conversion transmitter or receiver without an AD9361?
- Si5351 vs a "real" clock chip: how much jitter can my ADC clock tolerate?
- Which TCXO part numbers work with SX126x/AT86RF215/CC1200 and are in LCSC stock?
- When is a DDS (AD9850/AD9910) better than a PLL?

### [RF switches, digital step attenuators, fixed pads, limiters and T/R switching — part selection guide](kb/18-components-parts/rf-switches-attenuator-parts.md)
- Which SPDT switch should I use to share one antenna between a LoRa radio and a GNSS/second radio, or between TX and RX?
- Can a tiny 1 × 1 mm switch handle +30 dBm from my 1 W PA? What about when the antenna is damaged on landing?
- What is the difference between reflective and absorptive switches, and when does it matter?
- Which digital step attenuator (DSA) should I use for an AGC loop, an array calibration or a bench fixture?
- How do I make a 3/6/10 dB attenuator pad out of JLCPCB basic resistors?
- How do I protect an LNA at a ground station from my own transmitter?
- Which parts should I avoid (75 Ω lookalikes, last-time-buy parts)?

### [Filter parts — SAW, LTCC/ceramic, chip low-pass, baluns-with-filter, cavity and lumped filters for 433/868/915 MHz, GNSS and 2.4 GHz (selection guide)](kb/18-components-parts/filter-parts-saw-ceramic-ltcc.md)
- Which SAW filter do I put in front of my 433 / 868 / 915 MHz receiver or my GNSS LNA, and which are in LCSC stock?
- Which low-pass filter kills the harmonics of a 1 W PA well enough to be legal?
- Are Mini-Circuits LTCC filters (LFCN/HFCN/BFCN) worth US$2–5 when a TDK chip filter costs US$0.07?
- Can I put a SAW filter after my PA?
- When should I buy a cavity or helical filter for the ground station instead of a SAW?
- When is designing my own LC filter better than any off-the-shelf part?

### [RF connectors and cable assemblies — SMA, SMB, MCX, MMCX, U.FL/MHF, W.FL, N, BNC, 3.5/2.92 mm; pigtails, semi-rigid and sourcing (selection guide)](kb/18-components-parts/connectors-and-cables-parts.md)
- Which RF connector should I put on a rocket flight computer, and which on the ground station and test fixtures?
- How high in frequency can SMA, SMB, MCX, MMCX, U.FL, BNC and N connectors go?
- Why did my U.FL pigtail fall off (or wear out), and what should I use in a vibrating airframe?
- What is RP-SMA, and why doesn't my Wi-Fi antenna fit my LoRa module?
- How tight should an SMA be, and do I need a torque wrench?
- Which edge-launch SMA is good to 6 GHz on a JLC 1.6 mm board, and which LCSC parts are genuine brand-name?
- Which cable (RG-316, RG-174, 1.13 mm, semi-rigid) for pigtails and short jumpers?

### [PCB substrates for RF — what JLCPCB, PCBWay, OSH Park and Aisler actually offer (FR-4 grades, RO4350B, PTFE), cost, lead time and when low-loss laminate is worth it](kb/18-components-parts/pcb-substrates-parts.md)
- Can I get Rogers or PTFE boards from JLCPCB, in how many layers and thicknesses, and what does it cost?
- What do PCBWay, OSH Park and Aisler offer for RF work?
- Is plain FR-4 good enough for 433 MHz, 915 MHz, GNSS, 2.4 GHz, 5.8 GHz, 24 GHz?
- Which Dk do I type into my calculator when the fab says "RO4350B, Dk 3.48"?
- What should I tick on the JLC order form for an impedance-controlled RF board?

### [ADCs, DACs and audio codecs for DIY SDRs and radars — LTC2208, AD9226, ADS42LB69, ADS4249, ADC3664, AD9680/AD9208, ADC12DJ3200, MAX19506, AD9708/AD9767, PCM1808, ADAR7251, RFSoC (selection guide)](kb/18-components-parts/adcs-dacs-for-sdr.md)
- Which ADC should I use for a direct-sampling HF/VHF receiver, an IF-sampling SDR, or an FMCW radar's beat signal?
- How do SNR, ENOB, SFDR and noise spectral density (NSD) of a converter translate into receiver dynamic range?
- Can I use an audio codec as the ADC for a radar? When is that enough?
- What are the cheap AD9226/AD9280/AD9708 FPGA modules good for?
- When does a GSPS JESD204B converter or an RFSoC make sense, and what does it cost?
- Which of these converters are in LCSC stock, and what clock/driver do they need?

### [Phased-array and radar parts — beamformer ICs, phase shifters, mmWave radar SoCs (TI, Infineon, Acconeer), ADI 24 GHz chipset and radar modules (procurement guide)](kb/18-components-parts/phased-array-and-radar-parts.md)
- Which radar chip or module should I buy to measure rail-exit velocity or range near the pad?
- Which mmWave radar SoCs (TI IWR/AWR, Infineon BGT60, Acconeer A121) are in LCSC stock, and are their bands legal in Singapore?
- What is in the ADI 24 GHz FMCW chipset (ADF4159 + ADF5901 + ADF5904 + ADAR7251)?
- Which beamformer or phase-shifter IC fits a 2.4/5.8/10 GHz array, and what does a channel cost?
- Are ADAR2001/ADAR2004 beamformers? (No — see below.)
- Which cheap radar modules (HB100, CDM324/IPM-165, HLK-LD2410) are worth playing with?

### [Sourcing RF parts and evaluation boards from Singapore — distributors, LCSC/JLC basic vs extended vs global-sourcing parts, eval boards, samples, marketplace modules and counterfeit pitfalls](kb/18-components-parts/sourcing-and-eval-boards.md)
- Where should I buy RF parts in Singapore — Mouser, Digikey, element14, LCSC, AliExpress?
- What do JLCPCB "basic", "preferred extended", "extended" and "global sourcing" parts mean for my assembly bill?
- Which RF parts are realistically stocked at LCSC for JLC assembly?
- When should I buy an evaluation board instead of designing my own PCB, and what do they cost?
- Can I get free samples as a student?
- Which marketplace modules are commonly fake or mis-specified, and how do I check?

### [RF modules — GNSS (u-blox, Quectel, Unicore, ZHONGKEWEI), Wi-Fi/BLE (ESP32, nRF52), LoRa and telemetry modems, video transmitters and SDR modules; certification and antenna rules (selection guide)](kb/18-components-parts/rf-modules.md)
- Which GNSS module should go on the flight computer (single-band, dual-band, RTK), and what are its altitude/velocity/acceleration limits on a rocket?
- Will my GNSS stop working above 500 m/s or 18/50/80 km?
- Which ESP32 or nRF52840 module variant (PCB antenna vs U.FL) should I use, and does its certification still apply?
- Which LoRa/telemetry modules are in LCSC stock for JLC assembly?
- What about video transmitters and SDR modules?
- What antenna rules come with a certified module?

### [Coax and connector practicalities — torque, mating cycles, cleaning, adapter loss, SMA vs RP-SMA, U.FL fragility and retention, weatherproofing, crimp vs solder, bend radius, phase-stable and phase-matched cables, NanoVNA cable testing, 75 Ω on 50 Ω, and fake or poor connectors](kb/18-components-parts/coax-and-connector-practicalities.md)
- How tight should an SMA be, and do I really need a torque wrench?
- How many times can I plug a U.FL or an SMA before it wears out?
- How do I clean RF connectors without damaging them?
- How much do adapters cost me?
- Why doesn't my Wi-Fi antenna work on my LoRa module (SMA vs RP-SMA)?
- Why did my U.FL fall off, and how do I keep it on in a rocket?
- How do I waterproof an outdoor SMA or N connection?
- Crimp or solder: which is better for RF connectors? How do I fit an SMA to semi-rigid coax?
- How tightly can I bend coax?
- How do I make two cables phase-matched with a VNA?
- How do I test a cable (loss, velocity factor, faults) with a NanoVNA?
- Can I use 75 Ω TV coax (RG-6) for a 50 Ω scanner or SDR?
- How do I tell good coax and connectors from bad or fake ones?
- How do I mount a LoRa module in a weatherproof box with the antenna outside?

### [RF passives and support parts — C0G capacitors, RF inductors, pads, terminations, DC blocks, bias tees, ESD, low-noise LDOs, zero-drift op-amps, ferrites, shields, couplers, splitters, circulators and DBM spur tables (JLC/LCSC stock)](kb/18-components-parts/rf-passives-and-support-parts.md)
- Which C0G capacitors and RF inductors can JLCPCB actually place, and which are "basic" or "preferred"?
- Is a multilayer chip inductor good enough for my 433 MHz filter, or do I need a wire-wound or air-core one?
- What value should a DC block be at 433 MHz, 915 MHz or GNSS L1?
- How do I make a 50 Ω termination or a bias tee from stocked parts?
- Which ESD diode can I put on an antenna port without wrecking the match?
- Which LDO is quiet enough for a VCO or LNA supply, and which op-amp has no drift for a detector or sensor?
- Can I buy shield cans, ferrite toroids, couplers or splitters through JLC?
- Where do I get a 433 MHz or 915 MHz circulator or isolator, and how big is it?
- What is a mixer spur table, and how do I read the Mini-Circuits ADE-1 one?

## 19-regulations-safety — 

### [Spectrum allocation, ITU regions, ISM vs SRD bands, radar and protected bands, band names, emission designators and unwanted-emission domains](kb/19-regulations-safety/spectrum-allocation-ism-bands.md)
- What is the difference between an ISM band and a licence-free (SRD) band?
- Is 433 MHz an ISM band in Singapore?
- Why is 915 MHz used in the USA but 868 MHz in Europe and 920 MHz in Singapore?
- What do "primary" and "secondary" allocation mean for a hobby transmitter?
- Which bands can I use for a hobby radar (24, 60, 77 GHz)?
- Which bands must I never transmit in (GNSS, radio astronomy, passive sensing)?
- Why does IMDA need to consent to each amateur frequency at 430–440 MHz?
- What are HF, VHF, UHF and SHF exactly, and what frequencies are the L, S, C, X, Ku, K and Ka bands?
- What does an emission designator such as 16K0F3E, 2K70J3E or 125KF1D mean?
- What emission designator should I put on a licence or permit application for LoRa?
- What is "necessary bandwidth", and how is it calculated for CW, AM, SSB, FM and FSK?
- Where does "out-of-band" end and "spurious" begin, and which limit applies to my LoRa signal's skirts and harmonics?

### [Singapore radio rules (IMDA) — short-range devices, licences, equipment registration, and whether our LoRa radios are legal](kb/19-regulations-safety/singapore-imda-rules.md)
- Is my 2 W EBYTE E22-400T33D (433 MHz) legal to use in Singapore?
- Is my 1 W EBYTE E220-900T30D (900 MHz band) legal in Singapore, and on which channel?
- What power and duty cycle does IMDA allow for LoRa at 433 MHz, 866–869 MHz and 917–925 MHz?
- What law actually makes low-power radios licence-free in Singapore?
- Is it illegal just to *own* a 2 W radio module in Singapore?
- Does antenna gain count towards the IMDA power limit?
- What is the difference between e.r.p. and e.i.r.p. in IMDA documents?
- What licences can a student rocketry team get to transmit at higher power (amateur, experimental, temporary permit)?
- How much does an IMDA temporary frequency permit cost and how long does it take?
- Do I need to register equipment with IMDA if I build my own radio?
- What should our rocket and ground station comply with before we switch them on in Singapore?
- Can I use a 24 GHz, 60 GHz or 77–81 GHz radar module in Singapore?

### [Amateur radio licensing for rocket telemetry — Singapore (IMDA) and USA (FCC Part 97)](kb/19-regulations-safety/amateur-radio-licensing.md)
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

### [RF exposure safety — ICNIRP 2020, FCC MPE, SAR, and safe distances for our 433/915 MHz transmitters](kb/19-regulations-safety/rf-exposure-safety.md)
- How close can I stand to a 2 W 433 MHz transmitter feeding a 12 dBi Yagi?
- What are the ICNIRP 2020 and FCC exposure limits at 433, 868/915 MHz and 2.4 GHz?
- What is SAR and why do limits switch from SAR to power density?
- Does the duty cycle of my telemetry reduce the exposure?
- Is the far-field formula valid a metre from a Yagi?
- Is it safe to hold a rocket while its 2 W radio is transmitting?
- Does an amateur station need an RF exposure evaluation?
- Are the US and ICNIRP limits the same?
- Is RF "radiation" like X-rays? Can a LoRa radio, Wi-Fi or a 5G mast ionise atoms or damage DNA?
- Why is the eye the organ most often mentioned for microwave heating?
- Why are the exposure limits strictest between about 30 and 300 MHz?
- With two transmitters on one rocket or one mast, how do I add up the exposure, and who is responsible at a shared site?
- Is my HF station exempt from an RF-exposure evaluation?

### [Radio equipment certification — FCC ID and modular approval, CE/RED, IMDA registration, antennas, pre-compliance](kb/19-regulations-safety/certification-fcc-ce-imda.md)
- If I buy a "FCC/CE certified" LoRa module, is my flight computer certified?
- What does an FCC modular approval cover, and what breaks it?
- Can I change the antenna on a certified module?
- Do I need to certify a radio I built myself for our team?
- What is the EU Radio Equipment Directive (RED) and does it apply to amateur or student-built radios?
- Does IMDA require our flight computer to be registered?
- What pre-compliance tests should we do before a competition?
- Why does a module with an SMA connector usually not have a US modular grant?
- What "test mode" firmware does a test lab need from us, and how do I put an SX1262 into continuous-wave transmission?
- What should we bring to a test-lab day, and what do we do if the product fails?

### [Radio rules at launches abroad — USA (FCC Part 15/97, IREC/Spaceport America Cup), EU/Portugal (EuRoC), Australia (ACMA LIPD)](kb/19-regulations-safety/international-rules-for-competitions.md)
- Which radios can a Singapore team legally fly at the Spaceport America Cup (IREC)?
- What does the IREC 2026 Student Band Plan require for 433 MHz and 915 MHz telemetry?
- Is a fixed-channel LoRa link legal under FCC Part 15 at 915 MHz?
- Can we use our 2 W 433 MHz module in the USA without a ham licence?
- What are the EU 433 and 868 MHz limits that apply at EuRoC in Portugal?
- What radio does EuRoC require on board?
- What are Australia's LIPD class-licence limits at 433 and 915–928 MHz?
- How do we pack, declare and configure radios when travelling to a launch?
- Why can't we use amateur 33 cm (902–928 MHz) at Spaceport America?

### [RF lab and station safety — ESD, high-power RF, no-load transmission, lithium batteries, RF-induced e-match ignition (HERO), lightning and station grounding, and other bench hazards (BeO, high voltage, power lines)](kb/19-regulations-safety/lab-safety-esd-high-power.md)
- How careful do I need to be with ESD when handling an LNA or a GaAs/pHEMT part?
- What happens if my LoRa module transmits without an antenna?
- Can a 2 W transmitter burn me?
- How far should a transmitter be from an e-match or igniter?
- Can the rocket's own 2 W telemetry radio fire the recovery charges?
- What is HERO and what margin do military standards require?
- How do I test that my avionics bay is RF-safe for pyros?
- Why did my ground-station LNA die at the launch pad?
- How should we handle and fly with lithium batteries?
- How do I protect a rooftop LoRa gateway or a ground-station mast from lightning?
- What is a single-point ground (entry) panel, and why must everything be bonded to it?
- Do I need a lightning arrester on the coax, and which type — gas tube or quarter-wave stub?
- How deep and how many ground rods do I need, and why is "low ground resistance" not the main point?
- Is the roof always the best place for an antenna?
- What should a launch-site ground station do when a thunderstorm approaches?
- How far must an antenna mast be from power lines?
- Are beryllium-oxide parts in old RF transistors and attenuators dangerous?
- Is it safe to use a microwave-oven magnetron or transformer for a project?

### [Regulatory FAQ (miscellaneous) — the NextNav 902–928 MHz proposal (status 2026), Baofeng and uncertified handhelds (US and Singapore), radar licensing for hobbyists, jammers, home FM/TV transmitters, GNSS simulators, 1 W mesh nodes, Part 15 questions about LoRa, and why noisy products carry a CE mark](kb/19-regulations-safety/regulatory-faq-misc.md)
- What is the NextNav proposal for 902–928 MHz, why does it threaten LoRa, and where does it stand in 2026?
- Will proposed FCC changes to 902–928 MHz break LoRa meshes and US rocket telemetry?
- Are Baofeng UV-5R radios illegal? Can I use one in the US or in Singapore?
- Why can a ham handheld not be used on FRS/GMRS/PMR channels even though it can tune there?
- Can an amateur licence make a home-built radar legal? Is a 20 km hobby radar legal to operate?
- Can I build a 2.4 GHz radar from Wi-Fi parts, and is it legal?
- Are signal jammers legal for testing, or for finding who is jamming us?
- Can I run a small home FM or analog TV transmitter?
- Can I transmit a simulated GPS signal (gps-sdr-sim) to test our GNSS receiver?
- Is a 1 W LilyGO T-Beam (or a PA board) legal on a Meshtastic mesh?
- Under which US rule does non-hopping 250 kHz LoRa at 30 dBm operate?
- How did an obviously noisy product pass CE certification?
- Which licence does each of our team's radios need in Singapore and the USA?
- Is encryption allowed on our telemetry link?
- Where do I report interference, and what evidence should I collect first?

## 20-projects-recipes — end-to-end worked designs

### [Beginner project ladder — eleven graded first RF projects (RTL-SDR FM/ADS-B, AIS/APRS decoding, Meteor-M weather images, a NanoVNA-tuned 433 MHz dipole, cable loss and velocity factor, a tinySA look at a LoRa transmitter, a LoRa range test, SDR LoRa monitoring, an HB100 Doppler radar, a 2.4 GHz patch on JLC FR-4, and two-channel / KrakenSDR direction finding)](kb/20-projects-recipes/beginner-project-ladder.md)
- What is a good "hello world" project in RF?
- What should I build first with an RTL-SDR, a NanoVNA and a tinySA?
- Can I still receive NOAA weather-satellite pictures, and what antenna do I need?
- How do I build and tune a 433 MHz dipole, and what should the NanoVNA show?
- How do I measure a cable's loss and velocity factor?
- How do I safely look at my LoRa module's output on a tinySA?
- How do I run a LoRa range test that tells me something, and what range should I expect?
- How do I decode LoRa packets with an SDR?
- How do I make an HB100 Doppler module measure speed?
- Can I make a working 2.4 GHz patch antenna on cheap JLCPCB FR-4?
- How do I try direction finding with a KrakenSDR or two SDRs?
- Which projects are legal to transmit with in Singapore without a licence?

### [Recipe — LoRa rocket telemetry downlink (433 + 900 MHz) for a 10 km apogee, 15 km slant-range flight](kb/20-projects-recipes/lora-rocket-telemetry-link.md)
- How do I design a complete LoRa telemetry downlink for a rocket that goes to 10 km?
- Which spreading factor and bandwidth survive the boost of a 10 km rocket at 433 MHz and at 900 MHz?
- Will the EBYTE default "2.4k" air rate lose packets during boost?
- Where should the ground station stand so the rocket's tail null doesn't blank the link near apogee?
- How much link margin do I really have at 15 km with a Singapore-legal 10 mW, and with a licensed 2 W?
- Does 10 Hz telemetry fit inside a 10 % or 1 % duty-cycle rule?
- How do I run the 433 MHz primary and the 900 MHz secondary without one interfering with the other?
- How do I range-test the link in Singapore without breaking the power limit?
- Why does a conducted attenuator test of a 2 W module not work on a bench?
- What should I predict *before* the flight so the flight can prove me right or wrong?
- How much does the whole telemetry system cost?

### [Recipe — Tracking ground station for rocket telemetry (433 / 868–915 MHz DL6WU crossed Yagis, masthead LNA + SAW, tracking, diversity, SDR recording)](kb/20-projects-recipes/ground-station-tracking-yagi.md)
- What Yagi should I build for a 433 MHz and a 868/915 MHz rocket ground station, and with what dimensions?
- How big a beam can I still point by hand, and do I need a rotator?
- How do I make a crossed Yagi circularly polarised, and why can the phasing harness look perfectly matched while the CP is bad?
- Where do the LNA, SAW filter and limiter go, and how much gain is too much?
- Which coax, and how much does 15 or 30 m of it cost me at 433 vs 905 MHz?
- Will my own rocket on the pad, another team's radio or a phone next to me overload the receiver?
- Can a Yaesu-class rotator keep up with a rocket?
- Is a second station worth it, and where should it go?
- How do I record the raw signal with an SDR, and how much disk do I need?

### [Recipe — GNSS L1 RHCP patch antenna on JLCPCB FR-4 (TL model → openEMS → fabrication → NanoVNA tuning), with the 2.45 GHz linear reference](kb/20-projects-recipes/patch-antenna-design-walkthrough.md)
- How big is a GPS L1 patch on JLCPCB FR-4, and how much gain will it really have?
- How do I make a single-feed patch circularly polarised, and how big should the cut corners be?
- Which corners do I cut to get RHCP rather than LHCP?
- Why does an FR-4 GNSS patch need tuning after fabrication, and how do I tune it?
- How well do the transmission-line model and openEMS agree?
- What axial ratio and bandwidth can I expect, and is it enough for GPS, Galileo and BeiDou?
- Is a home-made FR-4 patch good enough for a ZED-F9P or MAX-M10S on a rocket, compared with a ceramic patch?
- How do I measure axial ratio and handedness without an anechoic chamber?

### [Recipe — FMCW radar build with a TI mmWave EVM (60 / 77 GHz), with 24 GHz and ADI Phaser alternatives — chirp design, processing chain, corner-reflector calibration, rail-exit velocity of a rocket](kb/20-projects-recipes/fmcw-radar-build.md)
- Which radar should I buy first — TI IWR6843 / AWR1843, a 24 GHz module or the ADI Phaser?
- How do I design a chirp for a given range, resolution and maximum velocity, and what limits the device imposes?
- Why does TDM-MIMO cut my maximum velocity by the number of transmitters?
- Can a mmWave radar beside the pad measure my rocket's rail-exit velocity?
- How strong a return will a person, a drone, a rocket and a corner reflector give?
- How do I build and use a corner reflector to calibrate range and RCS?
- Is a 77–81 GHz radar legal in Singapore, and why does my chirp bandwidth matter for that?
- How much raw data does the radar produce, and how do I process it?

### [Recipe — Phased-array starter build (KrakenSDR 5-element UCA for rocket-recovery direction finding at 433/868 MHz, ADI Phaser 8-element 10 GHz beamforming lab) and an honest array-vs-Yagi verdict](kb/20-projects-recipes/phased-array-starter-build.md)
- What is the simplest coherent array I can build, and what does it teach?
- How big must a 5-element circular array be at 433 MHz and 868 MHz?
- How accurate are KrakenSDR bearings, and what limits them in the field — SNR, calibration or multipath?
- How precisely must the antenna cables match?
- How well can two direction-finding stations locate a landed rocket?
- Does a single LoRa packet give enough samples for DOA?
- What will I see when I steer and taper the ADI Phaser?
- Should my telemetry ground station be a phased array instead of a tracked Yagi?

### [Recipe — GNSS L1 low-noise amplifier for a rocket active antenna (BGA524N6 MMIC vs ATF-54143 pHEMT): stability, noise match, bias, layout and measurement](kb/20-projects-recipes/lna-design-walkthrough.md)
- Should my GNSS LNA be a tiny MMIC (BGA524N6) or a discrete pHEMT (ATF-54143)?
- Why is a bare pHEMT potentially unstable, and how does a real design become unconditionally stable?
- Where does the noise match sit compared with the conjugate match?
- Should the SAW filter go before or after the first LNA on a rocket that carries a 2 W LoRa transmitter?
- How much does a SAW in front cost in C/N0?
- Which datasheet linearity number do I believe when the datasheet disagrees with itself?
- How do I bias it through the coax, and how much power does it take?
- How do I measure gain and a 0.5 dB noise figure with hobby equipment?
- What layout mistakes make an LNA oscillate?

### [Recipe — SDR ground receiver, recorder and spectrum monitor for LoRa rocket telemetry (RTL-SDR / Pluto, gr-lora_sdr, front-end filtering, gain staging)](kb/20-projects-recipes/sdr-receiver-build.md)
- Which SDR should record my LoRa telemetry, and is an RTL-SDR good enough?
- Where should I tune so the DC spike and the IQ image don't sit on my signal?
- What sample rate does gr-lora_sdr need, and how do I decimate to it?
- How much SDR gain should I use behind a masthead LNA?
- Why does a single RTL-SDR clip on the pad and early in the flight, and what do I do about it?
- How big are the recordings, and how do I timestamp them well enough to line up with the flight log?
- Can I measure the rocket's Doppler with an SDR whose own clock is off by 1 ppm?
- How do I find the SF/BW/CR hidden behind the EBYTE "air data rate" setting?
- How do I run a spectrum monitor for interference on launch day?

### [Recipe — Harmonic low-pass and band-pass filters for 433 / 905–920 MHz LoRa links (prototype → real parts → layout → measurement)](kb/20-projects-recipes/bandpass-filter-design-walkthrough.md)
- How much harmonic suppression does my 2 W 433 MHz LoRa transmitter need to be legal in Singapore?
- Should I use a Chebyshev or an elliptic low-pass, and how many poles?
- How do I turn ideal g-values into parts I can actually buy, and what do inductor Q, self-resonance and capacitor ESL do to the response?
- Why does my "60 dB" elliptic filter pass 4–6 GHz almost unattenuated?
- Does a 2-layer board ruin a filter compared with a 4-layer one?
- How much do ±2 % parts move a trap that sits on the 2nd harmonic?
- Will 0603 inductors survive 2 W, and how hot do they get?
- Can I buy a ready-made filter instead (Mini-Circuits LFCN)?
- Can I put a SAW filter after the PA?
- How do I measure 60–80 dB of rejection with a NanoVNA or tinySA without fooling myself?

### [Recipe — GNSS front end on a rocket with onboard LoRa transmitters (ZED-F9P / MAX-M10S, active antenna chain, SAW/LNA budget, desense and harmonic coexistence)](kb/20-projects-recipes/gnss-front-end-design.md)
- How much isolation do I need between my 2 W LoRa antenna and my GNSS antenna?
- Should the SAW go in front of the GNSS LNA on a rocket?
- Can my LoRa transmitter's own noise desense GPS even with no harmonics in the band?
- Which E22 channels must I never use with a ZED-F9P on board, and why is "legal harmonic level" not good enough?
- What active-antenna gain does the ZED-F9P want, and what does the MAX-M10S want?
- Do my MCU clocks (Teensy 24 MHz, ESP32 40 MHz) interfere with GNSS?
- How do I test GNSS coexistence on the bench and on the pad?
- What should I log so I can tell jamming from dynamics after a flight?

### [Recipe — RF design-review checklists (schematic, layout, bring-up, pre-flight) for Space Bar radios, GNSS and ground stations](kb/20-projects-recipes/design-review-checklists.md)
- What should an RF schematic review of a flight computer check?
- What layout mistakes make a LoRa or GNSS board fail?
- In what order should I bring up a new RF board, and what must each step show?
- What must be measured and on file before a rocket with two radios and GNSS flies?
- How do I check the frequency plan against other teams and the venue's rules?
- How do I record review findings so they are not lost or re-argued?

### [Validation test campaign — a pre-registered bench, field and HIL programme that turns the KB's predictions into measurements (antennas, transmit, receive, link, rocket-specific, materials/PCB, environment)](kb/20-projects-recipes/validation-test-campaign.md)
- How do we test the KB's predictions with a NanoVNA, a tinySA, SDRs and our own flight hardware?
- Which tests should we run first to learn the most for the least money and time?
- What exactly counts as a pass, a fail, or "the test could not tell"?
- How wide should the acceptance band be, and how do I combine the prediction's and the measurement's uncertainty?
- How do I record a measurement so that someone else can trust it, or redo it, a year later?
- Where do measured values go in the KB, and how do I mark a prediction confirmed or refuted?
- Which of these tests are legal in Singapore as described, and which need a shielded enclosure, conducted set-up or licence?
- How can a 10 mW legal test say anything about a 2 W flight?
- How do I find out which SF/BW the EBYTE "2.4k" air rate really is?
- How do I measure FR-4 εr myself before trusting a patch-antenna simulation?

## 21-gnss — satellite navigation receivers and their use on rockets

### [GNSS signals and codes — GPS, Galileo, BeiDou, GLONASS, QZSS, NavIC; BPSK vs BOC; received power and processing gain](kb/21-gnss/gnss-signals-and-codes.md)
- What signals do GPS, Galileo, BeiDou, GLONASS, QZSS and NavIC actually transmit, and on which frequencies?
- What is the difference between L1 C/A, L1C, L2C and L5, and which ones do the ZED-F9P and MAX-M10S use?
- Why is the GPS signal "below the noise floor" and how can a receiver still use it?
- What is a C/A code, and why is it 1023 chips long at 1.023 Mcps?
- What are BOC, CBOC and TMBOC modulations, and why did Galileo and modern GPS adopt them?
- How strong is a GNSS signal at the antenna, and what C/N0 should I expect?
- Why does GLONASS use different frequencies for each satellite?
- Which regional systems (QZSS, NavIC, SBAS) are useful in Singapore?
- What is in the navigation message and how fast is it sent?

### [GNSS receiver architecture — front end, acquisition, tracking loops (DLL/PLL/FLL), measurements and the navigation solution](kb/21-gnss/gnss-receiver-architecture-acquisition-tracking.md)
- What is inside a GNSS receiver chip, from antenna to position?
- Why can GNSS receivers use 1- or 2-bit ADCs, and how much does that cost?
- How does acquisition work, and why does a cold start take seconds just to find satellites?
- What are coherent and non-coherent integration, and why can't you integrate forever?
- What do the DLL, PLL and FLL do, and what loop bandwidths are used?
- What C/N0 does a receiver need to keep tracking, and why is that different from acquisition sensitivity?
- How does a receiver turn pseudoranges into a position, and why does it need four satellites?
- What is the receiver clock bias and why does it not matter (much)?
- What does a Kalman filter add, and why do update rates vary with constellations?

### [Time to first fix, almanac and ephemeris, cold/warm/hot starts and assisted GNSS (u-blox AssistNow) — and how to get a fast, reliable fix on the launch pad](kb/21-gnss/ttff-agps-almanac-ephemeris.md)
- Why does a GNSS receiver take ~30 s to get its first fix from cold?
- What is the difference between almanac and ephemeris, and how long are they valid?
- What do cold, warm, hot and aided start mean, and what does the receiver need for each?
- What is A-GNSS / u-blox AssistNow (Live Orbits, Predictive Orbits, Autonomous)?
- How do I make sure my rocket has a good fix before launch and gets it back quickly after landing?
- Why did my GPS cold-start after I reset it?

### [GNSS timing and the 1PPS time pulse — accuracy, quantisation sawtooth (qErr), time bases and leap seconds, disciplining oscillators, and timestamping flight data](kb/21-gnss/gnss-timing-1pps.md)
- How accurate is the u-blox time pulse, and what is the "sawtooth" error?
- What is qErr in UBX-TIM-TP and how do I use it?
- Which time does the pulse mark — GPS time, UTC, Galileo time? What about leap seconds?
- How do I use the PPS to timestamp IMU/baro data on my flight computer to microseconds?
- What happens to timing when the GNSS loses its fix during boost?
- How do I discipline a local oscillator (GPSDO) and how fast should the loop be?
- Can the GNSS timestamp events (launch detect, pyro fire) for me?

### [RTK, PPP and corrections — carrier phase, integer ambiguities, RTCM 3 MSM messages and bandwidth, sizing a LoRa corrections link, NTRIP, SBAS, PPP/PPP-RTK, moving base, PPK and RTK under high dynamics](kb/21-gnss/rtk-ppp-and-corrections.md)
- How does RTK get centimetre accuracy when GNSS code ranges are good to metres?
- What is an integer ambiguity, "float" vs "fixed", and why does dual frequency make fixing faster?
- Which RTCM 3 messages does a ZED-F9P base send, and how many bytes per second is that?
- Can a LoRa link (E22/E220) carry RTK corrections to a rocket? At which air rate?
- What happens when corrections arrive late or get lost?
- What are NTRIP, SBAS, PPP, PPP-RTK (SPARTN/CLAS), Galileo HAS and MADOCA, and which are usable in Singapore?
- What is moving-base RTK?
- Does RTK work on a rocket during boost? Is post-processed kinematic (PPK) better?

### [GNSS error sources and DOP — satellite clock/orbit (SISRE), ionosphere incl. equatorial scintillation over Singapore, troposphere, multipath, receiver noise, UERE budgets and dilution of precision](kb/21-gnss/gnss-error-sources-dop.md)
- Where does the few-metre error of a standalone GNSS fix come from?
- How good are the broadcast orbits and clocks of GPS, Galileo, BeiDou and GLONASS?
- How big is the ionospheric error in Singapore, and what is equatorial scintillation?
- How much does the troposphere delay the signal in a hot, humid climate?
- What is multipath and why do narrow correlators help?
- What are GDOP, PDOP, HDOP and VDOP, how are they derived, and why is vertical worse?
- How much does multi-constellation reception improve DOP over Singapore?
- What happens to DOP when the rocket's antenna points sideways?
- How do I convert latitude/longitude/height to ECEF and to local east-north-up, and get a satellite's azimuth and elevation?
- How do I compute where a GPS or Galileo satellite is from the broadcast ephemeris (RINEX navigation file)?
- How accurate is the broadcast orbit compared with the IGS precise orbit?
- What is RAIM, how does a receiver detect a bad satellite, and what is a protection level?

### [GNSS interference, jamming and spoofing — in-band vs out-of-band, self-interference from on-board radios and clocks, J/S tolerance, detection and mitigation](kb/21-gnss/gnss-interference-jamming-spoofing.md)
- Why does my GNSS lose satellites when the LoRa transmitter keys up?
- Can harmonics of my 433/868/915 MHz radio, or my MCU's crystal, land in a GNSS band?
- How strong does an interferer have to be to break GNSS tracking?
- What is the difference between in-band and out-of-band interference, blocking and desensitisation?
- How much isolation do I need between a 2 W telemetry antenna and a MAX-M10S?
- What is spoofing, how do receivers detect it, and does u-blox report jamming/spoofing?
- Are GNSS jammers or repeaters legal? Can I test with one?
- Why do sounding rockets see jamming at high altitude?

### [GNSS on rockets — export/COCOM limits and how u-blox implements them, dynamic models, tracking loss under boost (acceleration, jerk, oscillator g-sensitivity), antennas, roll and re-acquisition](kb/21-gnss/gnss-on-rockets-dynamics-and-limits.md)
- Will my u-blox GNSS stop working above 500 m/s, 18 km, 50 km or 80 km? Is it "speed AND altitude" or "speed OR altitude"?
- What do the export rules (COCOM, EAR 7A105, MTCR, ITAR) actually say today?
- Which u-blox dynamic platform model should a rocket use, and what does "Airborne <4g" really limit?
- Why do GNSS receivers lose lock during motor boost and regain it after burnout?
- How much acceleration and jerk can a tracking loop take? Is it the acceleration or the jerk that kills it?
- Does the receiver's crystal oscillator care about 15 g?
- Where should the GNSS antenna go on a rocket, and what happens when the rocket rolls or hangs under a parachute?
- How quickly does the receiver re-acquire after losing lock, and how do I make that faster?
- What have amateur and professional rocket flights actually observed?

### [SDR GNSS and DIY receivers — GNSS-SDR, SoftGNSS, Pocket SDR, RTL-SDR/HackRF reception, MAX2769/MAX2771 front ends, gps-sdr-sim (conducted only — never radiate) and a learning path to your own receiver](kb/21-gnss/sdr-gnss-and-diy-receivers.md)
- Can I receive GPS with an RTL-SDR or HackRF, and what else do I need?
- What software turns recorded samples into a position (GNSS-SDR, SoftGNSS, Pocket SDR, RTKLIB)?
- How do dedicated GNSS front-end chips (MAX2769B, MAX2771) differ from a general-purpose SDR?
- How would I build my own GNSS receiver for learning — what are the steps?
- Is it legal to transmit simulated GPS signals with gps-sdr-sim? How do I test a receiver safely?
- What sample rate, bit depth and oscillator accuracy do I need?
- Could a software receiver be better than a u-blox on a rocket?

### [Integrating u-blox ZED-F9P and MAX-M10S — UBX vs NMEA, CFG-VALSET, update rate vs constellations, UART/I²C/SPI throughput, antenna supervision, backup power, resets and layout](kb/21-gnss/gnss-receiver-integration-u-blox.md)
- Should I use UBX or NMEA, and which messages should a flight computer read?
- How do I configure a u-blox F9/M10 receiver (CFG-VALSET, layers, key IDs) and make it survive power cycles?
- How fast can it update, and why does the rate drop when I enable more constellations?
- What baud rate / I²C speed / SPI do I need, and why did my GPS stop talking after a baud-rate change?
- Why does u-blox say its I²C does not support Standard mode — is 100 kHz wrong?
- How do I power an active antenna and use the antenna supervisor?
- What does V_BCKP do, and why does RESET_N give me a cold start?
- What are the layout rules for the RF input?
