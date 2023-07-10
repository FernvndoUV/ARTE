import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr
from calandigital.instruments import generator
import sys

boffile = 'corr4in_arte.gz'
roach_ip = '192.168.0.168'
genname = 'TCPIP::192.168.0.33::INSTR'
bw = 600
channels = 2048

gen_power = -90


corr01_re_bram = ['dout_0a0c_re0','dout_0a0c_re1', 'dout_0a0c_re2', 'dout_0a0c_re3']
corr01_im_bram = ['dout_0a0c_im0','dout_0a0c_im1', 'dout_0a0c_im2', 'dout_0a0c_im3']
corr02_re_bram = ['dout_0a1a_re0','dout_0a1a_re1', 'dout_0a1a_re2', 'dout_0a1a_re3']
corr02_im_bram = ['dout_0a1a_im0','dout_0a1a_im1', 'dout_0a1a_im2', 'dout_0a1a_im3']
corr03_re_bram = ['dout_0a1c_re0','dout_0a1c_re1', 'dout_0a1c_re2', 'dout_0a1c_re3']
corr03_im_bram = ['dout_0a1c_im0','dout_0a1c_im1', 'dout_0a1c_im2', 'dout_0a1c_im3']

bram_re = [corr01_re_bram, corr02_re_bram, corr03_re_bram]
bram_im = [corr01_im_bram, corr02_im_bram, corr03_im_bram]

pow0 = ['dout_0a2_0', 'dout_0a2_1', 'dout_0a2_2', 'dout_0a2_3']
pow1 = ['dout_0c2_0', 'dout_0c2_1', 'dout_0c2_2', 'dout_0c2_3']
pow2 = ['dout_1a2_0', 'dout_1a2_1', 'dout_1a2_2', 'dout_1a2_3']
pow3 = ['dout_1c2_0', 'dout_1c2_1', 'dout_1c2_2', 'dout_1c2_3']

pows = [pow0,pow1,pow2,pow3]

##
roach = corr.katcp_wrapper.FpgaClient(roach_ip)
time.sleep(0.5)
#roach.upload_program_bof(boffile, 3000)
time.sleep(0.5)
roach.write_int('acc_len', 1024)
roach.write_int('cnt_rst',1)
roach.write_int('cnt_rst',0)

#roach.write_int('diode',1)

def get_power():
    power_data = np.zeros((4,2048))
    for i in range(4):
        data = calan.read_interleave_data(roach, pows[i], 9, 64, '>Q')
        power_data[i,:] = data
    return power_data

def get_correlation():
    corr_data = np.zeros((3,2048), dtype=complex)
    for i in range(3):
        corr_re = calan.read_interleave_data(roach, bram_re[i], 9, 64, '>q')
        corr_im = calan.read_interleave_data(roach, bram_im[i], 9, 64, '>q')
        corr_data[i,:] = corr_re+1j*corr_im
    return corr_data


####
gen_info = {'type':'visa', 'connection':genname, 'def_freq':1000, 'def_power':gen_power}
gen = generator.create_generator(gen_info)

freq = np.linspace(1200,1800, channels, endpoint=False)
freq = freq[1:-1]

powers = np.zeros((4, channels, len(freq)))
correlations = np.zeros((3, channels, len(freq)), dtype=complex)
data = np.zeros((7, len(freq)), dtype=complex)

##get the power
gen_pow = float(gen.instr.query('pow?'))
if(gen_pow != gen_power):
    raise Exception('Carefull the power is not set correctly')
else:
    gen.turn_output_on()

for i in range(len(freq)):
    print(i)
    gen.set_freq_mhz(freq[i])
    time.sleep(0.5)
    powers[:,:,i] = get_power()
    correlations[:,:,i] = get_correlation()
    data[:4,i] = powers[:,i+1,i]
    data[4:,i] = correlations[:,i+1,i]
    
gen.turn_output_off()

np.savez('arte_data.npz',
         powers = powers,
         correlations = correlations,
         data = data
         )
