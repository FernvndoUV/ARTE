import socket, corr, sys, os
import time, datetime, multiprocessing
import calandigital as calan
import numpy as np
import argparse
from  control import roach_control


parser = argparse.ArgumentParser(
    description="Save data comming from the 10Gbe interface")
parser.add_argument('-f', '--folder', dest='folder', 
        default='log', type=str)
parser.add_argument('-ft', '--filetime', dest='file_time', default=2,
        type=float)
parser.add_argument('-tt', '--totaltime', dest='total_time', default=60,
        type=float)




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


def receive_10gbe_data(folder, file_time,total_time=None,ip_addr='192.168.2.10', port=1234):
    """
    Function to save the 10gbe data in a certain folder, like we dont want a 
    super huge file we write several of them with the cpu timestamp.
    folder      :   where to save the raw_data
    file_time   :   Time per file (minutes)
    total_time  :   Total time to save in minutes, if its none is a while true
    ip_addr     :   10gbe address
    port        :   10gbe port
    """
    #roach = corr.katcp_wrapper.FpgaClient(roach_ip)
    #time.sleep(1)

    pkt_size = 2**18    #256kB

    #create the folder if it doesnt exists
    if(not os.path.exists(folder)):
        os.mkdir(folder)
    os.chdir(folder)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_addr, port))
    
    if(total_time is not None):
        count = int(total_time//file_time)
    ### TODO
    ### Like i am using threads we could save other info too.
    ###
    for i in range(count):
        filename = str(datetime.datetime.now())
        p = multiprocessing.Process(target=write_10gbe_rawdata, name="tge", args=(filename, sock, pkt_size, ))
        p.start()
        start = time.time()
        while(1):
            ex_time = time.time()-start
            if(ex_time>(file_time*60)):
                break
        p.terminate()
        p.join()
    sock.close()
    f.close()

if __name__ == '__main__':
    args = parser.parse_args()
    receive_10gbe_data(folder=args.folder, file_time=args.file_time,total_time=args.total_time,
            ip_addr='192.168.2.10', port=1234)
    
