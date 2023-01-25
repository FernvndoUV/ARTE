#!/usr/bin/python3
import socket
import sys, os, logging, time
import numpy as np
#import ipdb
import re, subprocess
from config import *

#SERVER_ADDR = './uds_socket'
#RECV_LEN = 128

class calan_python3():
    def __init__(self, server_addr, roach_ip, python2_interpreter):
        ##star the python2 server
        self.python2 =  subprocess.Popen([python2_interpreter, 'calan_python2.py' ,'--ip', roach_ip, 
            '--server_addr', server_addr])
        time.sleep(2)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.sock.connect(server_addr)
        except socket.error as msg:
            logging.error(msg)
            sys.exit()
    
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
        logging.info(b'Message: '+msg)
        #self.connection.sendall(msg.encode())
        self.sock.sendall(msg)
        """
        msg = cmd+';'
        if(params is not None):
            msg += params
        msg +=';'
        if(data is not None):
            msg += data
        length = len(msg)
        length += len(str(length))+1
        msg = str(length)+';'+msg 
        logging.info('Message: '+msg)
        self.sock.sendall(msg.encode())
        """
    
    def recv_msg(self, recv_len=RECV_LEN):
        msg = self.sock.recv(recv_len)
        split = msg.split(b';')
        length = int(split[0].decode())
        if(length>recv_len):
            for i in range(length//recv_len):
                msg += self.sock.recv(recv_len)
        return msg

    def parse_msg(self,msg):
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


    ###this are the current available commands
    def initialize_roach(self, ip, boffile):
        """
        """
        cmd = 'initialize_roach'
        params = ip+','+boffile
        self.send_msg(cmd, params)
        ans = self.sock.recv(128)
        logging.debug(ans)
        return ans
    
    def float2fixed(self, data, nbits, binpt, signed=True, warn=False):
        return 1

    def read_data(self, bram, awidth, dwidth, dtype):
        cmd = 'read_data'
        params = bram+','+str(awidth)+','+str(dwidth)+','+dtype
        self.send_msg(cmd, params)
        time.sleep(0.1)
        msg = self.recv_msg()
        cmd,params,data = self.parse_msg(msg)
        ##the calan digital converts the data to float..
        data = np.frombuffer(data, float)
        logging.debug(data)
        return data
    
    def read_interleave_data(self, brams, awidth, dwidth, dtype):
        cmd = 'read_interleave_data'
        #we need to encode the brams bcs they are in
        #brams = np.array(brams).tobytes()   ##check here bcs there are some commas and dont know how they are converted
        bram = ''
        for b in brams:
            bram +=b+' '
        bram = bram[:-1]
        params = bram+','+str(awidth)+','+str(dwidth)+','+dtype
        self.send_msg(cmd, params)
        time.sleep(0.1)
        msg = self.recv_msg()
        cmd,params,data = self.parse_msg(msg)
        ##the calan digital converts the data to float..
        data = np.frombuffer(data, float)
        logging.debug(data)
        return data

    def read_deinterleave_data(self,bram, dfactor, awidth, dwidth, dtype):
        ##TODO!!
        cmd = 'read_deinterleave_data'
        params = bram+','+str(awidth)+','+str(dwidth)+','+dtype
        self.send_msg(cmd, params)
        time.sleep(0.1)
        msg = self.recv_msg()
        cmd,params,data = self.parse_msg(msg)
        ##the calan digital converts the data to float..
        data = np.frombuffer(data, float)
        logging.debug(data)
        ##we need to reshape this!
        return data


    def read_snapshots(self, snapshots, samples, dtype='>i1'):
        cmd = 'read_snapshots'
        snap = ''
        for s in snapshots:
            snap +=s+' '
        snap = snap[:-1]
        params = snap+','+str(samples)+','+dtype   
        self.send_msg(cmd, params)
        time.sleep(0.1)
        msg = self.recv_msg()
        cmd, params, data = self.parse_msg(msg)
        data = np.frombuffer(data, dtype)
        data = data.reshape((4,-1)) ##check!
        logging.debug(data)
        return data

    def write(self, name, values, offset=0):
        cmd = "write"
        params = name+','+str(offset)
        self.send_msg(cmd, params,values)
        ans = self.sock.recv(128)
        logging.debug(ans)
        return ans

    def write_interleaved_data(self,brams, data):
        return 1

    def close(self):
        self.python2.kill()
        self.sock.close()
        
        
    



