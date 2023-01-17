import socket, corr, sys, os, structlog
import time, datetime, multiprocessing
import calandigital as calan
import numpy as np
import argparse, subprocess
from  control import roach_control
import utils,control
import read_sensors
from multiprocessing import Process
#from datetime import datetime
import datetime
import time
###
### Author: Sebastian Jorquera
### This code write several files with the data acquired from the 10Gbe port,
### for that it creates a socket that is in charge of that work. In the meanwhile
### you could save other stuffs. The class dms_acquisition check the refresh time
### for each DM and save the data accordingly.
### If you want you could save more data in the while loop.
###


parser = argparse.ArgumentParser(
    description="Save data comming from the 10Gbe interface")
parser.add_argument('-f', '--folder', dest='folder',
        default='log', type=str)
parser.add_argument('-ft', '--filetime', dest='file_time', default=2,
        type=float)
parser.add_argument('-tt', '--totaltime', dest='total_time', default=60,
        type=float)
parser.add_argument('-ri', '--roach_ip', dest='roach_ip', default='10.17.89.91')
parser.add_argument('-dms', '--dms', dest='dms', nargs="*")
parser.add_argument('-cal', '--cal', dest='cal_time', default=1, type=float)
parser.add_argument('-no_temp', '--no_temp', action='store_false')
parser.add_argument('-temp_time', '--temp_time', dest='temp_time', default=30, type=float)



def write_10gbe_rawdata(filename, sock, pkt_size):
    """
    Function to receive data from the sock socket and write it to a file.
    Is meanted to be forked by a main process that could do other stuffs in
    the meanwhile.
    filename:   File where we the data is saved
    sock    :   Socket where the roach is streaming
    pkt_size:   size to read in each iteration
    """
    with open(filename, 'ab') as f:
        while(1):
            try:
                while(1):
                    data = sock.recv(pkt_size)
                    f.write(data[:])
            finally:
                f.close()

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
    finally:
        f.close()

def get_misc_data(filename, dm_acq):
    """
    Get miscellaneous data (antennas, rfi, etc)
    """
    dm_acq.reset_acq(start)
    detections = []
    rfi_data = []
    antennas_data = []
    try:
        while(1):
            dm_acq.check_time(curr_time)
            det = roach_control.read_frb_detection()
            if(det!=0):
                detections.append([det, ex_time])
                roach_control.reset_detection_flag()
            #rfi_data.append(utils.get_rfi_score(roach))
            antennas_data.append(utils.get_antenas(roach))
    finally:
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



def receive_10gbe_data(folder, file_time,total_time=None,ip_addr='192.168.2.10',
        port=1234, roach_ip='10.17.89.91', DMs = [45,90,135,180,225,270,315,360,405,450,495],
        cal_time=1, temp=True, temp_time=30):
    """
    Function to save the 10gbe data in a certain folder, like we dont want a
    super huge file we write several of them with the cpu timestamp.
    folder      :   where to save the raw_data
    file_time   :   Time per file (minutes)
    total_time  :   Total time to save in minutes, if its none is a while true
    ip_addr     :   10gbe address
    port        :   10gbe port
    """
    roach = corr.katcp_wrapper.FpgaClient(roach_ip)
    roach_control = control.roach_control(roach)
    time.sleep(1)

    pkt_size = 2**18    #256kB
    dm_acq = dms_acquisition(roach,DMs)

    #create the folder if it doesnt exists
    if(not os.path.exists(folder)):
        os.mkdir(folder)
        os.mkdir(os.path.join(folder, 'logs'))
        os.mkdir(os.path.join(folder, 'misc'))
    if(temp):
        tn = read_sensors.roach_connect(roach_ip)
        temp_file = os.path.join(folder, 'temperature')
        temp_proc = multiprocessing.Process(target=measure_temperature, name='temp',
                                            args=(tn, temp_file, temp_time))
        temp_proc.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_addr, port))

    if(total_time is not None):
        count = int(total_time//file_time)

    for i in range(count):
        print(i)
        filename = str(datetime.datetime.now())
        tge_filename = os.path.join(folder,'logs', filename)
        misc_filename = os.path.join(folder,'misc', filename)
        tge_process = multiprocessing.Process(target=write_10gbe_rawdata, name="tge", args=(tge_filename, sock, pkt_size, ))
        misc_process = multiprocessing.Process(target=get_misc_data, name="misc", args=(misc_filename, dm_acq, ))
        tge_process.start()
        misc_process.start()
        roach_control.enable_diode()
        time.sleep(cal_time)
        roach_control.disable_diode()
        start = time.time()
        dm_acq.reset_acq(start)
        detections = []
        rfi_data = []
        antennas_data = []
        while(1):
            ##if you want to save something else, put it here
            curr_time = time.time()
            ex_time = curr_time-start
            if(ex_time>(file_time*60)):
                tge_process.terminate()
                tge_process.join()
                misc_process.terminate()
                misc_process.join()
                break
    time.sleep(10)
    sock.close()
    f.close()
    if(temp):
        temp_proc.terminate()
        temp_proc.join()
        tn.close()

if __name__ == '__main__':
    args = parser.parse_args()
    dms = np.array(args.dms).astype(float)
    print("DMs: {:}".format(dms))
    receive_10gbe_data(folder=args.folder, file_time=args.file_time,total_time=args.total_time,
            ip_addr='192.168.2.10', port=1234, roach_ip=args.roach_ip,
            DMs=dms, cal_time=args.cal_time, temp=args.no_temp, temp_time=args.temp_time)
    
