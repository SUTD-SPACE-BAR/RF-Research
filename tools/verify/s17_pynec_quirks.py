#!/usr/bin/env python3
"""
s17_pynec_quirks.py -- W5-S17 orchestrator note (b): demonstrates three PyNEC (NEC2++ 2.3.x) traps
first hit by W5-S12, for kb/16-simulation-tools/nec-antenna-modelling.md (Common mistakes):
 1. without an rp_card (RP) and without xq_card (XQ) nothing is solved: get_input_parameters(0) is None;
 2. a wire touching a ground plane needs geometry_complete(1) (GE 1); with GE 0 the 433 MHz lambda/4
    monopole over perfect ground gives ~43 - j1690 ohm instead of ~36 ohm;
 3. get_e_theta()/get_e_phi() are flat arrays with THETA varying fastest -> reshape(nph, nth).T.
Run: python3 tools/verify/s17_pynec_quirks.py
"""
import numpy as np, PyNEC
def ctx(L=0.3265, ground=False, ge=0):
    c = PyNEC.nec_context(); g = c.get_geometry()
    if ground:   # quarter-wave monopole touching z = 0
        g.wire(1, 21, 0, 0, 0, 0, 0, L/2, 1e-3, 1.0, 1.0)
    else:
        g.wire(1, 41, 0, 0, -L/2, 0, 0, L/2, 1e-3, 1.0, 1.0)
    c.geometry_complete(ge)
    if ground: c.gn_card(1, 0, 0, 0, 0, 0, 0, 0)   # perfect ground
    else: c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, 1, 1 if ground else 21, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, 433.0, 0)
    return c
# quirk 3: no rp_card and no xq -> anything?
c = ctx()
try:
    z = c.get_input_parameters(0).get_impedance(); print("no RP/XQ: impedance", z)
except Exception as e: print("no RP/XQ: exception", type(e).__name__, e)
c = ctx(); c.xq_card(0); print("with XQ:", c.get_input_parameters(0).get_impedance())
# quirk 2: monopole touching perfect ground, GE 0 vs GE 1
for ge in (0, 1):
    c = ctx(ground=True, ge=ge); c.xq_card(0); print(f"monopole GE {ge}:", c.get_input_parameters(0).get_impedance())
# quirk 1: e_theta order
c = ctx(); nth, nph = 5, 3
c.rp_card(0, nth, nph, 0, 0, 0, 0, 10.0, 0.0, 20.0, 45.0, 0.0, 0.0)
rp = c.get_radiation_pattern(0)
et = np.abs(np.array(rp.get_e_theta())); print("len", et.size, "theta", rp.get_theta_angles(), "phi", rp.get_phi_angles())
print("flat |Etheta|:", np.round(et/et.max(), 3))
