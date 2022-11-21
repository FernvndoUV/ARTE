import time
import calandigital as calan
import numpy as np
import matplotlib.pyplot as plt
#import control
##
time_step = 0.5

total_time = 50


##
def reset_ovf(roach):
    roach.write_int('ovf_rst',1)
    roach.write_int('adcsnap0_ctrl', 0b1010)
    roach.write_int('adcsnap1_ctrl', 0b1010)
    roach.write_int('adcsnap2_ctrl', 0b1010)
    roach.write_int('adcsnap3_ctrl', 0b1010)

    roach.write_int('adcsnap0_ctrl', 0b1011)
    roach.write_int('adcsnap1_ctrl', 0b1011)
    roach.write_int('adcsnap2_ctrl', 0b1011)
    roach.write_int('adcsnap3_ctrl', 0b1011)
    roach.write_int('ovf_rst',0)
    #roach.write_int('snap_trig',0)
    roach.write_int('snap_trig',1)

roach_ip ='10.17.89.91'
boffile = 'clip_test3.bof.gz'#'test_clipping2.fpg'

roach = calan.initialize_roach(roach_ip, boffile=boffile, upload=1)
#setup measurement
roach.write_int('ovf_rst',1)
roach.write_int('snap_trig',1)

##configure the snapshots
roach.write_int('adcsnap0_ctrl', 0b10)
roach.write_int('adcsnap1_ctrl', 0b10)
roach.write_int('adcsnap2_ctrl', 0b10)
roach.write_int('adcsnap3_ctrl', 0b10)

roach.write_int('adcsnap0_ctrl', 0b11)
roach.write_int('adcsnap1_ctrl', 0b11)
roach.write_int('adcsnap2_ctrl', 0b11)
roach.write_int('adcsnap3_ctrl', 0b11)


roach.write_int('diode',1)
time.sleep(1)
#roach_control.enable_diode()
steps = int(total_time/time_step)
counters = np.zeros([8, steps])
overflows = np.zeros(steps)
snaps = np.zeros([4,steps, 2**13])

#x_0 --> simulink ons
#x_1 --> verilog


for i in range(steps):
    reset_ovf(roach)
    time.sleep(time_step) #cada cuanto tiempo se resetea el contador
    counters[0,i] = roach.read_int('counter_0_0')
    counters[1,i] = roach.read_int('counter_0_1')
    counters[2,i] = roach.read_int('counter_1_0')
    counters[3,i] = roach.read_int('counter_1_1')
    counters[4,i] = roach.read_int('counter_2_0')
    counters[5,i] = roach.read_int('counter_2_1')
    counters[6,i] = roach.read_int('counter_3_0')
    counters[7,i] = roach.read_int('counter_3_1')
    overflows[i] = roach.read_int('overflow')
    snaps[0,i,:] = calan.read_data(roach, 'adcsnap0_bram', 10, 64,'>i1')
    snaps[1,i,:] = calan.read_data(roach, 'adcsnap1_bram', 10, 64,'>i1')
    snaps[2,i,:] = calan.read_data(roach, 'adcsnap2_bram', 10, 64,'>i1')
    snaps[3,i,:] = calan.read_data(roach, 'adcsnap3_bram', 10, 64,'>i1')

roach.write_int('diode',0)

###this are the simulink ones
overflows = overflows.astype(int)
clip0_0 = np.bitwise_and(overflows, 1)
clip1_0 = np.right_shift(np.bitwise_and(overflows, 2),1)
clip2_0 = np.right_shift(np.bitwise_and(overflows, 4),2)
clip3_0 = np.right_shift(np.bitwise_and(overflows, 8),3)

clip0_1 = np.right_shift(np.bitwise_and(overflows, 16),4)
clip1_1 = np.right_shift(np.bitwise_and(overflows, 32),5)
clip2_1 = np.right_shift(np.bitwise_and(overflows, 64),6)
clip3_1 = np.right_shift(np.bitwise_and(overflows, 128),7)
    
'''
fig, axes = plt.subplots(2,2)
axes[0,0].hist(counters[1,:]/(150*1e3), bins=20)
axes[1,0].hist(counters[3,:]/(150*1e3), bins=20)
axes[0,1].hist(counters[5,:]/(150*1e3), bins=20)
axes[1,1].hist(counters[7,:]/(150*1e3), bins=20)
axes[1,1].set_xlabel('s')
axes[1,0].set_xlabel('s')
axes[0,0].set_title('ADC0')
axes[1,0].set_title('ADC1')
axes[0,1].set_title('ADC2')
axes[1,1].set_title('ADC3')
plt.tight_layout()
plt.show()

'''

fig, axes = plt.subplots(2,2)

axes[0,0].plot(clip0_0,label = 'clip0')
axes[1,0].plot(clip1_0,label = 'clip1')
axes[0,1].plot(clip2_0,label = 'clip2')
axes[1,1].plot(clip3_0,label = 'clip3')

axes[0,0].set_title('Antenna 1')
axes[1,0].set_title('Antenna 2')
axes[0,1].set_title('Antenna 3')
axes[1,1].set_title('Antenna ref')


axes[1,1].set_xlabel('s')
axes[1,0].set_xlabel('s')

axes[1,0].set_ylabel('sat')
axes[0,0].set_ylabel('sat')

axes[1,1].grid()
axes[0,1].grid()
axes[0,0].grid()
axes[1,0].grid()

axes[1,1].legend()
axes[0,1].legend()
axes[0,0].legend()
axes[1,0].legend()

#plt.tight_layout()
plt.show()



#fig, axes = plt.subplots(2,2)

#axes[0,0].plot(sample[1831,:])
#axes[1,0].plot(sample[3052,:])
#axes[0,1].plot(sample[3540,:])
#axes[1,1].plot(sample[4883,:])

#axes[0,0].set_title('Espectro min 0.3')
#axes[1,0].set_title('Espectro min 0.5')
#axes[0,1].set_title('Epectro min 0.58')
#axes[1,1].set_title('Espectro min 0.8')


#axes[1,1].set_xlabel('ch')
#axes[1,0].set_xlabel('ch')

#axes[1,0].set_ylabel('Linear Power')
#axes[0,0].set_ylabel('Linear Power')

#axes[1,1].grid()
#axes[0,1].grid()
#axes[0,0].grid()
#axes[1,0].grid()

#axes[1,1].legend()
#axes[0,1].legend()
#axes[0,0].legend()
#axes[1,0].legend()

##plt.tight_layout()
#plt.show()
