import socket, corr, sys, os
import time, datetime, multiprocessing
import calandigital as calan
import numpy as np
import argparse, subprocess
from  control import roach_control
import utils,control, yaml
import read_sensors
from multiprocessing import Process
#from datetime import datetime
import datetime
import time
from calandigital.instruments.rigol_dp832 import *

###
### Author: Sebastian Jorquera
### This code write several files with the data acquired from the 10Gbe port,
### for that it creates a socket that is in charge of that work. In the meanwhile
### you could save other stuffs. The class dms_acquisition check the refresh time
### for each DM and save the data accordingly.
### If you want you could save more data in the while loop.
###


def write_10gbe_rawdata(filename, sock, pkt_size,run):
    """
    Function to receive data from the sock socket and write it to a file.
    Is meanted to be forked by a main process that could do other stuffs in
    the meanwhile.
    filename:   File where we the data is saved
    sock    :   Socket where the roach is streaming
    pkt_size:   size to read in each iteration
    """
    with open(filename, 'ab') as f:
        while(run.is_set()):
            data = sock.recv(pkt_size)
            f.write(data[:])


class dms_acquisition():
    def __init__(self, roach,DMs):
        self.roach = roach
        self.dm_update = np.array(utils.compute_accs(1500., 600., 2048.,DMs))//2*(512/(150*1e6))*1024
        self.indices = np.arange(len(self.dm_update))

    def reset_acq(self, curr_time):
        self.dedisp_data = []
        self.mov_avg = []
        for i in range(len(self.dm_update)):
            self.dedisp_data.append([])
            self.mov_avg.append([])
        self.timers = np.ones(len(self.dm_update))*curr_time

    def check_time(self, curr_time):
        test_time = (curr_time-self.timers)*np.ones(len(self.dm_update))
        mask =  (test_time>self.dm_update)
        self.timers[mask] = curr_time
        self.get_dm_data(self.indices[mask])

    def get_dm_data(self, indices):
        for ind in indices:
            dm_data = utils.get_dedispersed_power(self.roach, ind)
            mov_avg = utils.get_dedispersed_mov_avg(self.roach, ind)
            self.dedisp_data[ind].append(dm_data)
            self.mov_avg[ind].append(mov_avg)

def measure_temperature(tn,temp_filename, temp_time):
    """
    Save the temperature in one folder
    TODO: add the external sensors
    """
    f = open(str(temp_filename), 'a')
    try:
        while(1):
            time.sleep(temp_time)
            ambient, ppc, fpga, inlet, outlet = read_sensors.read_temperatures(tn)
            ##add the other sensors here!!
            # stamp = datetime.timestamp(datetime.now())
            stamp = time.mktime(datetime.datetime.now().timetuple())
            packet = np.array((stamp, ambient,ppc,fpga,inlet, outlet))
            np.savetxt(f, packet)
    #finally:
    except:
        f.close()

def dram_download(roach_ip, dram_addr, n_frames, measure_on):
    roach = corr.katcp_wrapper.FpgaClient(roach_ip)
    roach_control = control.roach_control(roach)
    roach_control.initialize_dram(addr=dram_addr, n_pkt=dram_frames)
    roach_control.write_dram()
    while(measure_on.is_set()):
        det = roach_control.read_frb_detection()
        if(det!=0):
            filename=datetime.now().strftime("d-%m-%Y:%H:%M:%S")
            roach_control.read_dram(filename) 
            roach_control.reset_detection_flag()
            roach_control.write_dram()
    roach_control.dram.close_socket()
    roach_control.dram = None
            

def get_misc_data(misc_filename, dm_acq, roach_ip, DMs,i, run, dram_dump):
    """
    Get miscellaneous data (antennas, rfi, etc)
    """
    roach = corr.katcp_wrapper.FpgaClient(roach_ip)
    roach_control = control.roach_control(roach)
    time.sleep(1)
    dm_acq = dms_acquisition(roach,DMs)

    start = time.time()
    dm_acq.reset_acq(start)
    detections = []
    rfi_data = []
    antennas_data = []
    # a = 0
    while(run.is_set()):
        curr_time = time.time()
        ex_time = curr_time-start
        dm_acq.check_time(curr_time)
        if(not dram_dump):
            det = roach_control.read_frb_detection()
            if(det!=0):
                detections.append([det, ex_time])
                roach_control.reset_detection_flag()
        #rfi_data.append(utils.get_rfi_score(roach))
        antennas_data.append(utils.get_antenas(roach))
    print('saving misc: %i'%i)
    np.savez(misc_filename,
             dm0=dm_acq.dedisp_data[0],
             dm1=dm_acq.dedisp_data[1],
             dm2=dm_acq.dedisp_data[2],
             dm3=dm_acq.dedisp_data[3],
             dm4=dm_acq.dedisp_data[4],
             dm5=dm_acq.dedisp_data[5],
             dm6=dm_acq.dedisp_data[6],
             dm7=dm_acq.dedisp_data[7],
             dm8=dm_acq.dedisp_data[8],
             dm9=dm_acq.dedisp_data[9],
             dm10=dm_acq.dedisp_data[10],
             mov_avg0=dm_acq.mov_avg[0],
             mov_avg1=dm_acq.mov_avg[1],
             mov_avg2=dm_acq.mov_avg[2],
             mov_avg3=dm_acq.mov_avg[3],
             mov_avg4=dm_acq.mov_avg[4],
             mov_avg5=dm_acq.mov_avg[5],
             mov_avg6=dm_acq.mov_avg[6],
             mov_avg7=dm_acq.mov_avg[7],
             mov_avg8=dm_acq.mov_avg[8],
             mov_avg9=dm_acq.mov_avg[9],
             mov_avg10=dm_acq.mov_avg[10],
             detections=detections,
             #rfi_data = rfi_data,
             antennas = antennas_data
         )
    roach.stop()


def receive_10gbe_data(folder, file_time,total_time=None,ip_addr='192.168.2.10',
        port=1234, roach_ip='192.168.0.168', DMs = [45,90,135,180,225,270,315,360,405,450,495],
        dram_dump=False,dram_addr=('10.0.0.29',1234), dram_frames=10,cal_time=1, temp=True, 
        temp_time=30, rigol_ip='192.168.0.38',noise_params=[2,28,1]):
    """
    Function to save the 10gbe data in a certain folder, like we dont want a
    super huge file we write several of them with the cpu timestamp.
    folder      :   where to save the raw_data
    file_time   :   Time per file (minutes)
    total_time  :   Total time to save in minutes, if its none is a while true
    ip_addr     :   10gbe address
    port        :   10gbe port
    noise_params: [channel, voltage, current]
    """
    roach = corr.katcp_wrapper.FpgaClient(roach_ip)
    roach_control = control.roach_control(roach)
    time.sleep(1)
    roach_control.reset_detection_flag()

    pkt_size = 2**18    #256kB
    dm_acq = dms_acquisition(roach,DMs)
    rigol = rigol_dp832(rigol_ip)
    rigol.set_voltage(noise_params[0], noise_params[1])
    rigol.set_current(noise_params[0], noise_params[2])

    #create the folder if it doesnt exists
    if(not os.path.exists(folder)):
        os.mkdir(folder)
        os.mkdir(os.path.join(folder, 'logs'))
        os.mkdir(os.path.join(folder, 'misc'))
        os.mkdir(os.path.join(folder, 'hw_detections'))
    if(temp):
        tn = read_sensors.roach_connect(roach_ip)
        temp_file = os.path.join(folder, 'temperature')
        temp_proc = multiprocessing.Process(target=measure_temperature, name='temp',args=(tn, temp_file, temp_time))
        temp_proc.start()
    
    ##make file to store the timestamps of the calibrations
    cal_file = open(os.path.join(folder, 'calibrations'), 'a')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_addr, port))

    if(total_time is not None):
        count = int(total_time//file_time)

    ###start dram process
    if(dram_dump):
        measure_on = multiprocessing.Event()
        measure_on.set()
        dram_proc = multiprocessing.Process(target=dram_download, name='dram_read',
                                               args=(roach_ip, dram_addr,
                                                     dram_frames, measure_on))
        dram_proc.start()

    for i in range(count):
        filename = str(datetime.datetime.now())
        tge_filename = os.path.join(folder,'logs', filename)
        misc_filename = os.path.join(folder,'misc', filename)
        run = multiprocessing.Event()
        run.set()
        tge_process = multiprocessing.Process(target=write_10gbe_rawdata, name="tge", args=(tge_filename, sock, pkt_size, run,))
        misc_process = multiprocessing.Process(target=get_misc_data, name="misc",
                                    args=(misc_filename, dm_acq, roach_ip, 
                                          DMs,i, run, dram_dump))
        tge_process.start()
        misc_process.start()
        ##change switch
        cal_file.write(str(time.time())+'\n')
        roach_control.enable_diode()
        #hot measure
        rigol.turn_output_on(noise_params[0])
        if(not rigol.get_status(noise_params[0])):
            raise Exception('Channel %i doesnt turn on!'%noise_params[2])
        time.sleep(cal_time//2)
        cold measure
        #rigol.turn_output_off(noise_params[0])
        if(rigol.get_status(noise_params[0])):
            raise Exception('Channel %i doesnt turn off!'%noise_params[2])
        time.sleep(cal_time//2)
        roach_control.disable_diode()
        
        ##starting measurement
        start = time.time()
        dm_acq.reset_acq(start)
        while(1):
            ##if you want to save something else, put it here
            curr_time = time.time()
            ex_time = curr_time-start
            if(ex_time>(file_time*60)):
                run.clear()
                #tge_process.terminate()
                tge_process.join()
                #misc_process.terminate()
                misc_process.join()
                print("misc %i, tge %i"%(tge_process.is_alive(), misc_process.is_alive()))
                break
    time.sleep(10)
    sock.close()
    f.close()
    cal_time.close()
    if(temp):
        temp_proc.terminate()
        temp_proc.join()
        tn.close()
    if(dram_dump):
        measure_on.unset()
        dram_proc.terminate()
        dram_proc.join()
        

if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()

    ##configure the network interface 
    ##enable jumbo frames
    cmd = ['sudo','ip', 'link' ,'set' ,config['tengbe_log']['interface'], 'mtu', '9000']
    subprocess.call(cmd)
    ##kernel configs
    cmd = ['sudo', 'sysctl', '-w', 'net.core.rmem_max=26214400']
    subprocess.call(cmd)
    cmd = ['sudo', 'sysctl', '-w', 'net.core.rmem_default=26214400']
    subprocess.call(cmd)
    cmd = ['sudo', 'sysctl', '-w', 'net.core.optmem_max=26214400']
    subprocess.call(cmd)
    cmd = ['sudo', 'sysctl', '-w', 'net.core.netdev_max_backlog=300000']
    subprocess.call(cmd)
    #increase kernel buffers
    cmd = ['sudo', 'ethtool', '-G', config['tengbe_log']['interface'], 'rx', '4096']
    subprocess.call(cmd)
    #increase pci mmrbc (this depend on the pci address of your nic)
    cmd = ['sudo', 'setpci', '-v', '-d' '8086:10fb', 'e6.b=2e']
    subprocess.call(cmd)

    time.sleep(1)
    
    dram_frames = config['dram_frames']

    log_info = config['tengbe_log']
    receive_10gbe_data(folder=log_info['log_folder'], 
                       file_time=log_info['filetime'],
                       total_time=log_info['totaltime'],
                       ip_addr=log_info['ip'],
                       port=log_info['port'],
                       roach_ip=config['roach_ip'],
                       DMs=config['DMs'],
                       cal_time=log_info['calibration_time'],
                       dram_dump=config['dram_dump'],
                       dram_addr=(config['dram_socket']['ip'], config['dram_socket']['port']),
                       dram_frames=config['dram_frames'],
                       temp=log_info['temp'],
                       temp_time=log_info['temp_time'],
                       rigol_ip=config['supply_ip']
                       )

