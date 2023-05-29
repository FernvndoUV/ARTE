import sys
sys.path.append('../codes')
import control
import corr, argparse, time


###
### Author: Sebastian Jorquera
### Code to read the dram data from the roach using the 1Gbe interface
###


parser = argparse.ArgumentParser(
    description="read dram data")

parser.add_argument("-i", "--ip", dest="ip", default=None,
    help="ROACH IP address.")
parser.add_argument("-f", "--filename", dest="filename",
    help="Filename of the dump")

def read_dram(roach, filename):
    roach_control = control.roach_control(roach)
    try:
        roach_control.initialize_dram(configure=False)
        time.sleep(0.5)
        start = time.time()
        print('Saving DRAM data to '+filename)
        roach_control.read_dram(filename)
        read_time = time.time()-start
        print('DRAM read in %.3f minutes' %(read_time/60))
        roach_control.reset_detection_flag()
        roach_control.write_dram()
        roach_control.dram.close_socket()
    except Exception as e:
        print("Exception reading DRAM!!!")
        print(e)
        if(roach_control.dram is not None):
            roach_control.dram.close_socket()
    
if __name__ == '__main__':
    socket_used = True
    try:
        #check if the socket is available
        sock_addr = ('10.0.0.45',1234)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(sock_addr)
        sock.close()
        socket_used = False
    except:
        #print('Address already in use')
        #(98, 'Address already in use')
        socket_used = True
    if(not socket_used):
        args = parser.parse_args()
        roach = corr.katcp_wrapper.FpgaClient(args.ip)
        time.sleep(0.5)
        read_dram(roach, args.filename)
        roach.stop() 
