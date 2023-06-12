import numpy as np
import socket, struct, sys,time

class dram_ring():

    def __init__(self, fpga, fpga_addr=('10.0.0.45',1234), sock_addr=('10.0.0.29', 1234), 
            tx_core_name = 'one_GbE', n_pkt=10, timeout=10):
        """sock address = (gbe ip address, port)
        """
        self.fpga = fpga
        self.pkt_sock = 36*220
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(sock_addr)
        self.sock.settimeout(timeout)

        ##gbe ethernet module parameters
        pkt_size = 36*220-2
        idle = 25000
        self.n_pkt = n_pkt

        source_ip = fpga_addr[0].rsplit('.')
        dest_ip = sock_addr[0].rsplit('.')  
        source_ip = int(source_ip[0])*2**24+int(source_ip[1])*2**16+int(source_ip[2])*2**8+int(source_ip[3])
        dest_ip = int(dest_ip[0])*2**24+int(dest_ip[1])*2**16+int(dest_ip[2])*2**8+int(dest_ip[3])
        fabric_port = fpga_addr[1] 
        mac_base=(2<<40) + (2<<32)
        
        ##configure ethernet fpga module
        fpga.tap_start('tx_tap',tx_core_name,mac_base+source_ip,source_ip,fabric_port)
        time.sleep(1)
        #set dest ip address and port
        #fpga.write_int('ip_sel',1)
        #time.sleep(0.1)
        #fpga.write_int('ip_addr',dest_ip)
        #time.sleep(0.1)
        #fpga.write_int('ip_sel',2)
        #time.sleep(0.1)
        #fpga.write_int('ip_addr',fabric_port)
        #time.sleep(0.1)
        #fpga.write_int('ip_sel',0)
        
        
        fpga.write_int('control1',2)
        fpga.write_int('control1',1)
        
        #configure the ring buffer
        fpga.write_int('ring_configuration', 0b101100) #rst everything
        fpga.write_int('ring_n_pkt', self.n_pkt)
        fpga.write_int('ring_gbe_idle', idle)


    def init_ring(self):
        self.fpga.write_int('ring_configuration',0)     
        self.fpga.write_int('ring_configuration',1)     ##start writing
        #self.fpga.write_int('control1',1)    
        self.fpga.write_int('control1',0b101)    


    def reading_dram(self, filename='data', iters=None):
        self.fpga.write_int('control1', 0)
        f = file(filename, 'wb')            ##CHANGE TO APPEND!!
        start = time.time()
        self.fpga.write_int('ring_configuration', 0b110000)
        self.fpga.write_int('ring_configuration', 0b010010) #read 1 burst of 220
        """
        When having npkt=1 we read 15840 bytes per iter, with 2 we have 15840*1.5
        3->15840*2, etc
        """
        base = 15840    ##bytes read with n_pkt=1
        if(iters is None):
            bytes_per_iter = base*(self.n_pkt+1)/2
            iters = int(2**25*288/8/(bytes_per_iter))
        for i in range(iters):
            data = ""
            for j in range(self.n_pkt+1):
                data =data+self.sock.recv(self.pkt_sock)
            f.write(data[:])
            print(str(i)+"\t "+str(len(data)))
            if(i%50==1):
                time.sleep(0.2)
            self.fpga.write_int('ring_configuration', 0b110000)
            self.fpga.write_int('ring_configuration', 0b010010) #read 1 burst of 220 
    #if(i%30==1):
        #time.sleep(1)
        end = time.time()
        print("took %.4f secs read dram" %(end-start))
        f.close()
    
    def open_sock(self, sock_addr=('10.0.0.29', 1234)): 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(sock_addr)

    def close_socket(self):
        self.sock.close()
