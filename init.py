import calandigital as calan
import numpy as np
import sys, time
sys.path.append('codes')
import utils, control
import corr

###
### hyperparameters
###
roach_ip ='10.17.89.91'
boffile = 'arte_headers2.fpg' #'arte_gpio.fpg'#'arte_new2.fpg'

##harcoded parameters
fpga_clk = 150.*10**6
bw = 600.
flow = 1200.
nchannels = 2048.

##dedispersors
##(the dedispersor output and the treshold is a 20_10UFix)
DMs = [45,90,135,180,225,270,315,360,405,450,495]
thresh = thresh = [0.22034862053885101,
0.47419230300761206,
0.6387031656561817,
0.7033368416103863,
0.8564752217732761,
1.1021449829662753,
0.8593363770297829,
0.9177729007016765,
0.5887623494333615,
0.6419021505738306,
0.8205032423095127]

# np.ones(11)*32#[4,4,4,4, 4, 4]     ## for each DM the detection threshold is

                                        ## mov avg+thresh
#10Gbe log
log_time = 10.**-2                       ##10Gbe frame rate

#rfi detection
rfi_acc_len = 1024#256                       ##rfi subsystem accumulation

rfi_thresh = 0.4                        ##over rfi_thresh is considered as rfi event
rfi_hold = 0.5                          ##if an rfi event is detected we dont allow an FRB 
                                        ##detection for rfi_hold seconds
#ring buffer parameters
adc_gain = 2**5                            ##the ADC samples are reduced to 4 bits per sample, this parameter
                                        ##multiplies each ADC sample to modify its range
sock_addr = ('10.0.0.29',1234)         ##ip, port of the computers
                                        ##roach will transmit from  10.0.0.45, 1234
                                        ##('10.0.0.29',1234) ('192.168.2.10',1234)CAMBIO POR FRAN
dram_frames = 10
#channels to flag



flags = np.arange(87).tolist()
# flags = np.arange(20).tolist()
flags = flags+[1024]
# flags += np.arange(85).tolist()
# flags += np.arange(1792,2048,1).tolist()
flags += (np.arange(27)+394).tolist()
flags += (np.arange(5)+455).tolist()
flags += (np.arange(4)+1024).tolist()
flags += (np.arange(25)+1135).tolist()
flags += (np.arange(15)+1155).tolist()
flags += (np.arange(12)+1175).tolist()
flags += (np.arange(30)+1210).tolist()
flags += (np.arange(16)+1275).tolist()

flags += (np.arange(18)+1325).tolist()
flags += (np.arange(10)+1367).tolist()
flags += (np.arange(5)+1381).tolist()
flags += (np.arange(40)+1420).tolist() # 1439
flags += (np.arange(256)+1792).tolist()





# flags incompletos
#channels to flag
# flags = np.arange(20).tolist()
# #flags = flags+[1024]
# flags += (np.arange(170)+20).tolist()
# flags += (np.arange(30)+300).tolist()
# flags += (np.arange(41)+380).tolist()
# flags += (np.arange(5)+1155).tolist()
# flags += (np.arange(12)+1175).tolist()
# flags += (np.arange(21)+1220).tolist()
# flags += (np.arange(16)+1275).tolist()
# flags += (np.arange(18)+1325).tolist()
# flags += (np.arange(10)+1367).tolist()
# flags += (np.arange(16)+1439).tolist()
# flags += (np.arange(2)+1830).tolist()
# flags += (np.arange(136)+1911).tolist()
# ###
###
###

roach = corr.katcp_wrapper.FpgaClient(roach_ip)
time.sleep(1)
roach.upload_program_bof(bof_file=boffile, port=3000, timeout=10)

#roach = calan.initialize_roach(roach_ip, boffile=boffile, upload=1)
#roach = calan.initialize_roach(roach_ip, upload=0)
time.sleep(1)

roach_control = control.roach_control(roach)
time.sleep(0.2)
roach_control.set_snap_trigger()
time.sleep(0.2)

roach_control.flag_channels(flags)

###compute the necessary accumulations
dedisp_acc = utils.compute_accs(flow+bw/2, bw, nchannels, DMs)
dedisp_acc = np.array(dedisp_acc)//2

##dedispersor accumulation
for i in range(len(dedisp_acc)):
    roach_control.set_accumulation(dedisp_acc[i], thresh=thresh[i], num=1+i)


##rfi accumulation
roach_control.set_accumulation(rfi_acc_len, thresh=rfi_thresh, num=31)
roach_control.set_accumulation(rfi_hold, thresh=0, num=30)

#initialize subsystem
roach_control.initialize_10gbe(integ_time=log_time)
roach_control.enable_10gbe()

#initialize ring buffer subsystem
roach_control.set_ring_buffer_gain(adc_gain)
roach_control.initialize_dram(addr=sock_addr, n_pkt=dram_frames)
roach_control.write_dram()

#enable rfi subsytem
roach_control.enable_rfi_subsystem()

roach_control.reset_accumulators()
roach_control.enable_dedispersor_acc()

###close dram socket 
roach_control.dram.close_socket()
roach_control.dram = None

