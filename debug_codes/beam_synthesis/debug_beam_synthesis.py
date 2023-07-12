import numpy as np
import matplotlib.pyplot as plt
import sys, time, corr
sys.path.append('../codes')
import control
import calandigital as calan
from calandigital.instruments.rigol_dp832 import rigol_dp832

roach_ip = '192.168.0.168'
rigol_ip = '192.168.0.38'
boffile = "fpg_files/arte_timestamp.fpg" 
iterations = 2048

roach = corr.katcp_wrapper.FpgaClient(roach_ip)
time.sleep(0.1)
rigol = rigol_dp832(rigol_ip)
ctrl = control.roach_control(roach)



print("Making cold measurement")
ctrl.enable_diode()
rigol.turn_output_off(2)

cold_data = np.zeros((2, 4096, iterations))
for i in range(iterations):
    print("cold "+str(i))
    cold_data[:,:,i] = ctrl.get_sync_snapshots(['adcsnap0', 'adcsnap1'], addr_width=12)


print("Making hot measurement")
rigol.turn_output_on(2)

hot_data = np.zeros((2, 4096, iterations))
for i in range(iterations):
    print("hot "+str(i))
    hot_data[:,:,i] = ctrl.get_sync_snapshots(['adcsnap0', 'adcsnap1'], addr_width=12)


ctrl.disable_diode()
rigol.turn_output_off(2)


hot_spect = np.fft.fft(hot_data, axis=1)
cold_spect = np.fft.fft(cold_data, axis=1)

hot_beam = np.sum(hot_spect, axis=0)
cold_beam = np.sum(cold_spect, axis=0)


hot_acc_beam = np.sum(hot_beam*np.conj(hot_beam), axis=1)
cold_acc_beam = np.sum(cold_beam*np.conj(cold_beam), axis=1)

hot_acc = np.sum(hot_spect*np.conj(hot_spect), axis=2)
cold_acc = np.sum(cold_spect*np.conj(cold_spect), axis=2)


np.savez('synth_adc.npz', 
        hot_data = hot_data,
        cold_data = cold_data)

