import json,collections
rows=json.load(open('all.json'))
N={('electronics','rf'):60,('electronics','antenna'):50,('electronics','impedance-matching'):25,('electronics','transmission-line'):25,('electronics','radio'):15,('electronics','lora'):25,('electronics','sdr'):15,('electronics','power-amplifier'):12,('electronics','noise+rf'):15,('electronics','noise'):5,('electronics','oscillator'):12,('electronics','pll'):12,('electronics','filter+rf'):15,('electronics','pcb-design+rf'):20,('electronics','emc'):15,('electronics','radar'):20,('electronics','smith-chart'):12,('electronics','vna'):15,('electronics','spectrum-analyzer'):12,('electronics','mixer'):15,('electronics','balun'):12,('electronics','coaxial'):10,('electronics','gps'):12,('electronics','wireless'):10,('electronics','modulation'):12,('electronics','adc'):8,('electronics','operational-amplifier+noise'):8,('electronics','operational-amplifier+stability'):8,('electronics','crystal'):10,('electronics','microstrip'):12,('electronics','433mhz'):10,('electronics','receiver'):8,('electronics','transmitter'):8,('electronics','transceiver'):6,('electronics','dipole'):8,('electronics','lna'):10,('electronics','phase-noise'):8,('electronics','shielding'):8,('electronics','ground-plane'):10,('electronics','frequency-modulation'):6,('electronics','amplitude-modulation'):6,('electronics','ferrite'):8,('electronics','impedance+rf'):10,('electronics','decoupling-capacitor+rf'):4,('electronics','rf-hot'):10,('electronics','antenna-hot'):8,
('ham','ALL'):80,('ham','antenna-theory'):25,('ham','propagation'):15,('ham','coaxial-cable'):12,('ham','feed-line'):10,('ham','impedance-matching'):12,('ham','license'):6,('ham','legal'):6,('ham','software-defined-radio'):12,('ham','rfi'):8,('ham','balun'):10,('ham','yagi'):8,('ham','antenna-tuner'):8,('ham','grounding'):6,('ham','rtl-sdr'):8,('ham','uhf'):6,('ham','satellites'):5,('ham','measurement'):8,('ham','ALL-hot'):8,
('dsp','radar'):25,('dsp','software-defined-radio'):15,('dsp','fft'):10,('dsp','modulation'):10,('dsp','beamforming'):12,('dsp','doa'):10,('dsp','array-signal-processing'):10,('dsp','digital-communications'):10,('dsp','demodulation'):8,('dsp','synchronization'):8,('dsp','chirp'):10,('dsp','gnuradio'):5,('dsp','sampling'):8,('dsp','doppler'):8,('dsp','matched-filter'):8,('dsp','ofdm'):5,('dsp','pll'):6,('dsp','decimation'):5,('dsp','window-functions'):6,('dsp','fsk'):6,('dsp','snr'):5}
sel=[]
for r in rows:
    keep=False
    for s in r['srcs']:
        tag,rank=s.split('#');rank=int(rank)
        # hot sorts have their own key
        k=(r['site'],tag)
        if k in N and rank<=N[k]: keep=True
    sel.append(r) if keep else None
print(len(sel))
json.dump(sel,open('sel.json','w'))
