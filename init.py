import yaml, time, sys
import calandigital as calan
sys.path.append('codes')
import numpy as np
import matplotlib.pyplot as plt
import utils, control
import corr, subprocess, time
import ipdb

##
##  Getting hyperparameters
##
f = open('configuration.yml', 'r')
config = yaml.load(f, Loader=yaml.loader.SafeLoader)
f.close()

##flags
flags = np.arange(87).tolist()
flags = flags+[1024]
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

##
##  Programming FPGA and set the parameters
##
roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
time.sleep(1)
roach.upload_program_bof(bof_file=config['boffile'], port=3000, timeout=10)
time.sleep(1)

roach_control = control.roach_control(roach)
time.sleep(1)
roach_control.set_snap_trigger()
time.sleep(0.2)

roach_control.flag_channels(flags)

###compute the necessary accumulations
dedisp_acc = utils.compute_accs(
        config['start_freq']+config['bandwidth']/2, float(config['bandwidth']),
        config['channels'], config['DMs'])
dedisp_acc = np.array(dedisp_acc)//2

##dedispersor accumulation
thresh = config['thresholds']
for i in range(len(dedisp_acc)):
    roach_control.set_accumulation(dedisp_acc[i], thresh=thresh[i], num=1+i)

##rfi accumulation
roach_control.set_accumulation(config['rfi_acc_len'], thresh=config['rfi_threshold'],
                               num=31)
roach_control.set_accumulation(config['rfi_holding_time'], thresh=0, num=30)

#intialize the timestamp
roach.write_int('timestamp', time.time())

##intialize 10Gbe subsystem
roach_control.initialize_10gbe(integ_time=config['tengbe_log']['log_time']*1e-3)
roach_control.enable_10gbe()

#set dram interface address
cmd = ['sudo', 'ip', 'addr', 'add', config['dram_socket']['ip']+'/24','dev',
        config['dram_socket']['interface']]
subprocess.call(cmd)
cmd = ['sudo', 'ip', 'link', 'set', 'up', 'dev', config['dram_socket']['interface']]
subprocess.call(cmd)

#initialize ring buffer subsystem
dram_gain = utils.ring_buffer_calibration(roach_control)
#roach_control.set_ring_buffer_gain(config['dram_gain'])
dram_addr = (config['dram_socket']['ip'], config['dram_socket']['port'])
roach_control.initialize_dram(addr=dram_addr, n_pkt=config['dram_frames'])
##TODO: auto gain algorithm!!
#utils.ring_buffer_digital_gain(roach_cotrol)
roach_control.write_dram()

#enable rfi subsytem
roach_control.enable_rfi_subsystem()

roach_control.reset_accumulators()
roach_control.enable_dedispersor_acc()

###close dram socket 
#roach_control.dram.close_socket()
#roach_control.dram = None
roach_control.reset_detection_flag()


###calibrate 
if(config['cal_info']['calibrate']):
    cmd = ['calibrate_adc5g.py',
            '-i', config['roach_ip'],
            '-gf', str(config['cal_info']['gen_freq']),
            '-gp', str(config['cal_info']['gen_power']),
            '--zdok0snap', 'adcsnap0', 'adcsnap1',
            '--zdok1snap', 'adcsnap2', 'adcsnap3',
            '--ns', '128',
            '-bw', str(config['bandwidth'])]
    if(config['cal_info']['do_mmcm']):
        cmd.append('-dm')
    if(config['cal_info']['do_ogp']):
        cmd.append('-do')
    if(config['cal_info']['do_inl']):
        cmd.append('-di')
    if(config['cal_info']['plot_snap']):
        cmd.append('-psn')
    if(config['cal_info']['plot_spect']):
        cmd.append('-psp')

    subprocess.call(cmd)

if(config['sync_info']['sync_adcs']):
   cmd = ['python2', 'codes/sync_adcs.py',
          '--ip', config['roach_ip'],
          '--bof', config['boffile'],
          '--genname', str(config['sync_info']['gen_info']),
          '--genpow', str(config['sync_info']['gen_power']),
          '--bandwidth', str(config['bandwidth']),
          '--points', str(config['sync_info']['points']),
          '--nyquist_zone', '3',
          '--snapname', 'adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3' 
           ]
   subprocess.call(cmd)

