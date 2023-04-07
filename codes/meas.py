import numpy as np
import calandigital as calan
from calandigital.instruments.sva1075x import sva1075x
from calandigital.instruments.rigol_dp832 import rigol_dp832
import  matplotlib.pyplot as plt
import time, sys, corr
sys.path.append('..')
import control, utils
import subprocess

roach_ip = '192.168.1.18'
siglent_ip = '192.168.1.64'
rigol_ip = '192.168.1.106'

boffile = '../arte_beamform_with_gain.bof.gz'
gain = 1
integ_time = 1e-2

ENR = (14.85+14.74)/2
T_cold = 293
#T_hot = 10**(ENR/10)*T_cold+T_cold
T_hot = 12*1e3

#configure roach
roach = corr.katcp_wrapper.FpgaClient(roach_ip)
#roach.upload_program_bof(boffile, 3000)
#time.sleep(0.1)
#roach_control.set_snap_trigger()
#roach_control.reset_accumulators()

#gain = calan.float2fixed(np.array(1) nbits=32, binpt=16)
#roach.write_int('gain', gain)
#time.sleep(0.1)

#subprocess.call(['../calibrate.sh'])

#siglent 
integ_time = 1e-2   ##intergration time
res_bw = 3*1e6#1e3#600*1e6/2048
video_bw = 3*1e2#1e2#1./integ_time
pts = 751
span = [1200*1e6,1800*1e6]

siglent = sva1075x('TCPIP::'+siglent_ip+'::INSTR')
siglent.configure_spectrum(span, pts, res_bw, video_bw, 1)

rigol = rigol_dp832(rigol_ip)

beam = utils.get_beam(roach)
antennas = utils.get_antenas(roach)
siglent_spect = siglent.get_spectra()

###start measurement 
#rigol
#ch1:   3V, 1A
#ch2:   28V,1A
#ch3:   5V, 1A
#rigol.set_voltage(1,3)
#rigol.set_current(1,1)
#rigol.set_voltage(2,28)
#rigol.set_current(2,1)
#rigol.set_voltage(3,5)
#rigol.set_current(3,1)


rigol.turn_output_on(1)
rigol.turn_output_on(3)

##cold meas
time.sleep(1)
beam_cold = utils.get_beam(roach)
antennas_cold = utils.get_antenas(roach)
time.sleep(1)
siglent_spect_cold = siglent.get_spectra()

#hot measure
rigol.turn_output_on(2)
time.sleep(1)
beam_hot = utils.get_beam(roach)
antennas_hot = utils.get_antenas(roach)
time.sleep(1)
siglent_spect_hot = siglent.get_spectra()


rigol.turn_output_off(1)
rigol.turn_output_off(2)
rigol.turn_output_off(3)

##calculate noise tempearture
y = antennas_hot/antennas_cold
te_antenna =  (T_hot-y*T_cold)/(y-1)

y = beam_hot/beam_cold
te_beam =  (T_hot-y*T_cold)/(y-1)

siglent_hot = 10**(siglent_spect_hot/10)
siglent_cold = 10**(siglent_spect_cold/10)

y = siglent_hot/siglent_cold
te_siglent =  (T_hot-y*T_cold)/(y-1)

freq = np.linspace(1200,1800, 2048, endpoint=False)

plt.figure()
plt.plot(freq, te_antenna[0,:])
plt.title('Noise Temperature ADC input')
plt.xlabel('MHz')
plt.ylabel('K')
plt.ylim(0,500)
plt.grid()

plt.figure()
plt.plot(freq, te_beam)
plt.title('Noise Temperature synth beam')
plt.xlabel('MHz')
plt.ylabel('K')
plt.ylim(0,500)
plt.grid()


freq = np.linspace(1200, 1800, pts)
plt.title('Noise Temperature synth beam')
plt.figure()
plt.plot(freq, te_siglent)
plt.title('Noise Temperature at Siglent')
plt.xlabel('MHz')
plt.ylabel('K')
plt.ylim(0,500)
plt.grid()

plt.show()

np.savez('data', 
         antennas_cold= antennas_cold,
         antennas_hot = antennas_hot,
         beam_cold = beam_cold,
         beam_hot = beam_hot,
         siglent_cold = siglent_spect_cold,
         siglent_hot = siglent_spect_hot
         )
