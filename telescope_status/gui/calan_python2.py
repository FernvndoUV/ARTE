#!/usr/bin/python2
import socket
import corr, os, logging, time
import calandigital as calan
import re
import argparse
from config import *
import numpy as np


parser = argparse.ArgumentParser(
    description="Server running python2 codes to control the roach")
parser.add_argument("-i", "--ip", dest="ip", default=None,
    help="ROACH IP address.")
parser.add_argument("-s", "--server_addr", dest="server_addr", default="./uds_socket",
        type=str, help="UNIX file")



SERVER_ADDR = './uds_socket'    ##unix domain socket
RECV_LEN = 128

class calan_python2():
    """
    This code creates a server that accepts commands to have access to the old
    corr and calandigital codes that runs in python2.
    """
    def __init__(self, roach_ip, server_addr, debug=True):
        logging.getLogger().setLevel(logging.INFO)
        try:
            os.unlink(server_addr)
        except OSError:
            if(os.path.exists(server_addr)):
                raise 
        #create the socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        logging.info('connecting socket')
        self.sock.bind(server_addr)
        ##start listening 
        self.sock.listen(1)

        ##create a connection with the roach
        if(debug):
            self.roach = calan.DummyRoach(roach_ip)
        else:
            self.roach = corr.katcp_wrapper.FpgaClient(roach_ip)

        while 1:
            self.connection, client_addr = self.sock.accept()
            try:
                logging.info("client connected")
                while(1):
                    msg = self.recv_msg(self.connection)
                    if msg:
                        logging.info(msg)
                        cmd, params, data = self.parse_msg(msg)
                        self.cmds(cmd, params, data)
            finally:
                self.connection.close()
    
    def send_msg(self,cmd,params=None,data=None):
        """
        The prefix of each message is the length of the command itself
        if the command requires an extra 

        length;cmd;parameters;data
        the parameters are separated by simple commas
        """
        msg = cmd+';'
        if(params is not None):
            msg += params
        msg +=';'
        msg = msg.encode()
        if(data is not None):
            msg += data
        length = len(msg)
        length += len(str(length))+1
        msg = (str(length)+';').encode()+msg 
        logging.info('Message: '+msg)
        #self.connection.sendall(msg.encode())
        self.connection.sendall(msg)
    
    def recv_msg(self, connection, recv_len=RECV_LEN):
        msg = connection.recv(recv_len)
        if(msg):
            split = msg.decode().split(';')
            lenght = int(split[0])
            if(lenght>recv_len):
                for i in range(lenght//recv_len):
                    msg += connection.recv(recv_len)
            return msg
        

    def parse_msg(self, msg):
        ##first we search for the b; to have the fields
        ind = [r.start() for r in re.finditer(b';', msg)]
        length = msg[0:ind[0]]
        cmd = msg[ind[0]+1:ind[1]]
        params = msg[ind[1]+1:ind[2]]
        data = msg[ind[2]+1:]
        #length,cmd,params,data = msg.split(b';')
        if(params!=''):
            params = params.decode().split(',')
        return cmd,params,data
        """
        length,cmd,params,data = msg.decode().split(';')
        if(params!=''):
            params = params.split(',')
        if(data!=''):
            data = data.encode()
        return cmd,params,data
        """
    
    def cmds(self, cmd, params,data):
        logging.debug(cmd)
        if(cmd=='initialize_roach'):
            ans = self.initialize_roach(params[0], params[1])
            self.connection.sendall(ans.encode()) 

        elif(cmd=='read_data'):
            ans = self.read_data(params[0], params[1], params[2], params[3])

        elif(cmd=='read_interleave_data'):
            brams = params[0].split(' ')
            ans = self.read_interleave_data(brams, params[1],params[2], params[3])
        
        elif(cmd=='write'):
            ans = self.write(params[0], data, offset=params[1])
            self.connection.sendall(ans.encode()) 
        elif(cmd=='read_snapshots'):
            brams = params[0].split(' ')
            ans = self.read_snapshots(brams, int(params[1]), dtype=params[2])
             
            

    ##current cmds 
    def initialize_roach(self, ip, boffile):
        """
        """
        logging.info("programming FPGA")
        try:
            self.roach.upload_program_bof(boffile, port=3000)
            return "ok"
        except Exception as err:
            logging.error("Error")
            return str(err)
    
    def ans_read_cmd(self,data):
        cmd = 'read_resp'
        self.send_msg(cmd, data=data)

        

    def read_data(self, bram, awidth, dwidth, dtype):
        data = calan.read_data(self.roach, bram, int(awidth), int(dwidth), dtype)
        logging.debug(data)
        data = data.tobytes()
        self.ans_read_cmd(data) 
        return 1

    def read_deinterleave_data(self,bram, dfactor, awidth, dwidth, dtype):
        data = calan.read_deinterleave_data(self.roach, bram, dfactor, awidth, dwidth, dtype)
        logging.debug(data)
        data = data.tobytes()
        self.ans_read_cmd(data)
        return 1

    def read_interleave_data(self, brams, awidth, dwidth, dtype):
        data = calan.read_interleave_data(self.roach, brams, int(awidth), int(dwidth), dtype)
        logging.debug(data)
        data = data.tobytes()
        self.ans_read_cmd(data)
        return 1

    def read_snapshots(self, snapshots,  samples, dtype='>i1'):
        data = calan.read_snapshots(self.roach, snapshots, dtype=dtype)
        data = np.array(data).flatten()
        data = data.tobytes()
        self.ans_read_cmd(data)
        return 1

    def write(self, name, data, offset=0):
        try:
            self.roach.write(name, data, offset=offset) 
            return "ok"
        except Exception as err:
            logging.error("Error")
            return str(err)

    def write_interleaved_data(self,brams, data):
        return 1
        



if __name__ == '__main__':
    args = parser.parse_args()
    calan_python2(args.ip, args.server_addr)
