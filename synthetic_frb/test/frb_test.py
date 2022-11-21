from upload_curve import *
from att_ali import *

###
### Author:Sebastian Jorquera
###

DMs = [45,90,135,180,225,270,315,360,405,450,495]
atts = [0, 5, 10, 15, 20, 25, 30]

att_dev = '/dev/ttyUSB1'
gen_name = 'TCPIP::192.168.1.45::INSTR'

freqs = [1200,1800]
vmin = 3
vmax = 8
npts = 16384

trigger = 0 #1 to have a single burst, 0 to have continous

###
###

#connect to devices
gen = arbitrary_generator(gen_name)
gen.turn_output_off()
gen.turn_burst_off()
gen.set_termination('inf') ##set the termination to HIZ

att = attenuator(dev=att_dev)

#calculate the period for each DM
periods = np.zeros(len(DMs))
for i in range(len(DMs)-1,-1,-1):
    t,f = frb_curve(DMs[i],freqs[0], freqs[1])
    periods[i] = t[0]

#upload the curve to the generator

#f_norm = (f-(f[-1]+f[0])/2)/((f[-1]-f[0])/2)
#f_norm = f_norm/np.max(np.abs(f_norm))
#gen.set_arbitrary_waveform(f_norm[::-1])
#time.sleep(1)

#gen.instr.write('volt:high '+str(vmax))
#gen.instr.write('volt:low '+str(vmin))
#gen.set_waveform('user')

gen.set_freq_hz(1./t[0])
if(trigger):
    gen.burst_config(1)
    gen.turn_burst_on()
    gen.turn_output_on()

gen.turn_output_on()

##TODO: make the single burst option.. also think how to connect to the roach
## pc and make the measurement automatic 
for t in periods[::-1]:
    gen.set_freq_hz(1./t)
    for att_val in atts:
        print("period:%.3f \t att:%.3f"%(t,att_val))
        att.set_attenuation(att_val)
        time.sleep(1)
        raw_input("press enter when you  are ready ;)") 
        

    
    

