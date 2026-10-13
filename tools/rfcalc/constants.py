"""Physical constants (SI, CODATA 2018 exact/recommended values) and KB conventions.

Conventions follow CONVENTIONS.md section 5: noise referenced to T0 = 290 K, powers in dBm
referenced to 1 mW, impedances referenced to 50 ohm unless stated.
"""
import math

C0 = 299_792_458.0                 # speed of light in vacuum [m/s] (exact)
MU0 = 1.25663706212e-6             # vacuum permeability [H/m] (CODATA 2018; ~4*pi*1e-7)
EPS0 = 1.0 / (MU0 * C0 ** 2)       # vacuum permittivity [F/m] ~ 8.8541878128e-12
ETA0 = MU0 * C0                    # free-space wave impedance [ohm] ~ 376.730313
K_B = 1.380649e-23                 # Boltzmann constant [J/K] (exact)
Q_E = 1.602176634e-19              # elementary charge [C] (exact)
H_PLANCK = 6.62607015e-34          # Planck constant [J s] (exact)
T0 = 290.0                         # IEEE standard noise temperature [K]
KT0_DBM_HZ = 10 * math.log10(K_B * T0 / 1e-3)   # -173.975 dBm/Hz ("-174 dBm/Hz")
R_EARTH = 6_371_000.0              # mean Earth radius [m]
SIGMA_CU = 5.8e7                   # annealed copper (100 % IACS) conductivity [S/m]
Z0_REF = 50.0                      # default reference impedance [ohm]
