import numpy as np
import calandigital as calan
from calandigital.instruments import generator
import time
from utils import *
from dram_class import dram_ring

#TODO: change the adc_deay1 register for status!!!

"""
-the control_control register has the following bit fields:
    0    :  cnt_rst         :reset the accumulators
    1    :  rst_detection   :reset the detection flag
    2    :  snap_trig       :triggers the aqcuisition of the snapshots
    3    :  tge_en          :enable the 10Gbe
    4    :  rst_tge         :reset the 10Gbe
    5-6  :  adc_lat_sel     :select to which snapshot write the delay
    7:11 :  acc_len_sel     :select which accumulator set   
    12   :  reset_dedisp    :reset dedispersors and mov avg
    13   :  en_dedisp       :enable dedispersor accumulation. Enable this accumulation after setting the accumultions.
    14   :  rfi_en          :enable the rfi subsystem (if not on, there is no rfi block signal for the detection)
    15   :  diode_en        :connected to the gpio0 that enable the noise diode measure


-the control_adc_delay writes the delay to sync the ADCs inputs.

-control_rfi_flag:  
    0-4:    rfi flag        :like we have 4 inputs we select which one we flag
    4-10:   rfi num         :select the "channel" to flag (really is channels/4 and
                             the rfi flag field tell us which one we are flagging)
    32:     flag en         :enable write the flag 

-control_gain:  gain of the ADC before bit reduction for the DRAM   

-control_status inform the status of the system:
    0   :   frb_detection 
    1   :   rfi_detected
"""


class roach_control():
    def __init__(self, roach):
        self.roach = roach
        self.dram = None

    def reset_accumulators(self):
        """reset all the accumulators in the model
        """
        curr_state = self.roach.read_int('control_control')
        data = set_bit(curr_state,0)
        self.roach.write_int('control_control', data)
        time.sleep(0.2)
        data = clear_bit(curr_state, 0)
        self.roach.write_int('control_control', data)

    def reset_detection_flag(self):
        """reset the frb detection flag
        """
        curr_state = self.roach.read_int('control_control')
        data = set_bit(curr_state,1)
        self.roach.write_int('control_control', data)
        time.sleep(0.2)
        data = clear_bit(curr_state, 1)
        self.roach.write_int('control_control', data)

    def enable_diode(self):
        """enable the noise diode
        """
        curr_state = self.roach.read_int('control_control')
        data = set_bit(curr_state,15)
        self.roach.write_int('control_control', data)

    def disable_diode(self):
        """disable noise diode
        """
        curr_state = self.roach.read_int('control_control')
        data = clear_bit(curr_state,15)
        self.roach.write_int('control_control', data)

    def reset_10gbe(self):
        """reset the 10Gbe module
        """
        curr_state = self.roach.read_int('control_control')
        data = set_bit(curr_state, 4)
        self.roach.write_int('control_control', data)
        time.sleep(0.2)
        data = clear_bit(curr_state, 4)
        self.roach.write_int('control_control', data)


    def enable_10gbe(self):
        """Enable the 10Gbe transmition
        """
        curr_state = self.roach.read_int('control_control')
        data = set_bit(curr_state, 3)
        self.roach.write_int('control_control', data)


    def enable_rfi_subsystem(self):
        """ Enable RFI subsystem
            If the subsystem is off then the RFI flag is not considered for the
            FRB detection
        """
        curr_state = self.roach.read_int('control_control')
        data = set_bit(curr_state, 14)
        self.roach.write_int('control_control', data)

    def flag_frequencies(self, frequencies ,near=None, channels=2048, bw_edges=[1200,1800]):
        """
            frequencies : list of frequencies to flag in Mhz
            near        : if is not None and one frequency falls in the middle of
                          two channels then we flag both. Otherwise only flags the
                          nearest one
            channels    : number of channels of the spectrum
            bw_edges    : the start and end frequencies in the bw (in Mhz)
        """
        print(frequencies)
        flags = []
        bw = float(bw_edges[1]-bw_edges[0])
        for freq in frequencies:
            channel = ((freq-bw_edges[0])/bw)*channels
            if(near is not None):
                #TODO
                if(channel ==0.0):
                    flags.append(int(round(channel)))
                    flags.append(int(round(channel)+1))
                else:
                    flags.append(int(round(channel)))
                    flags.append(int(round(channel+1)))
                    flags.append(int(round(channel-1)))
            else:
                flags.append(int(round(channel)))
        self.flag_channels(flags, n_chan=channels, n_streams=4)
        return 1

    
    def flag_channels(self, flags, n_chan=2048, n_streams=4):
        """ 
            flags:      array with the channels to flag
            n_chan:     fft channels
            n_streams:  parallel streams (out of the fft)

            #model reg name control_rfi_flag:
                0-4: rfi_flag
                4-10: rfi_num
                32: rfi_enable
        """
        chan_flag = np.zeros(n_chan)
        chan_flag[flags] = 1
        chan_flag = chan_flag.reshape([-1, n_streams])
        aux = np.zeros([n_chan/n_streams, 8-n_streams])
        chan_flags = np.hstack([chan_flag, aux])
        vals = np.packbits(chan_flags[:,::-1].astype(np.uint8))
        ind = np.where(vals!=0)[0]
        for i in range(len(ind)):
            val = vals[ind[i]]+(ind[i]*2**4)
            self.roach.write_int('control_rfi_flag',val+2**31)
        self.roach.write_int('control_rfi_flag',0)
    ##snapshots and sync the adcs

    def set_snap_trigger(self):
        """ Enable the capture of the snapshot block
        """
        curr_state = self.roach.read_int('control_control')
        state = set_bit(curr_state,2)
        self.roach.write_int('control_control', state)

    def unset_snap_trigger(self):
        """Disable captures of the snapshots
        """
        curr_state = self.roach.read_int('control_control')
        state = clear_bit(curr_state,2)
        self.roach.write_int('control_control', state)


    def set_adc_latencies(self, adc_num, lat):
        """ Set a delay for a given adc
            adc_num:    0,1,2 to select an adc to write to
            lat:        latency
        """
        if(adc_num>3):
            raise Exception("adc_num should be less than 3!")
        curr_state = self.roach.read_int('control_control')
        data = write_bitfield(curr_state, adc_num, [5,6])
        self.roach.write_int('control_control', data)
        time.sleep(0.1)
        self.roach.write_int('control_adc_delay', lat)

    def get_sync_snapshots(self, snap_names, addr_width=11):
        """Configure the snapshots for an external trigger
           generate the trigger and take the data
           snap_names   :   list with the snap names
        """
        ##prepare snashot capture
        self.unset_snap_trigger()
        for snap in snap_names:
            self.roach.write_int(snap+'_ctrl',0)
            self.roach.write_int(snap+'_ctrl',1)
        time.sleep(0.1)
        self.set_snap_trigger()
        time.sleep(0.1)
        self.unset_snap_trigger()
        adc_data = np.zeros([len(snap_names), 2**addr_width])
        for i in range(len(snap_names)):
            adc_data[i,:] = calan.read_data(self.roach, snap_names[i]+'_bram',
                    addr_width, 8, '>i1')
        return adc_data


    
    def get_adcs_delay(self, test_freq):
        """ 
        TODO!!!
        """
        return 1



    def set_accumulation(self, acc, num=0, thresh=None, thresh_pt=20):
        """
        Set the accumulation of the model and also the threshold for the
        dedispersor.
        num     :    select where to write the accumulation
                     0      :   10gbe and antennas
                     1-n    :   dedispersors accs
                     30     :   rfi holding time
                     31     :   rfi accumulation
        acc     :    accumulation to set
        thresh  :    threshold for the dedispersors and num=31 is threshold
        """
        curr_state = self.roach.read_int('control_control')
        data = write_bitfield(curr_state, num, [7,12])
        self.roach.write_int('control_control', data)
        time.sleep(0.1)
        self.roach.write_int('control_acc_len', acc)
        time.sleep(0.1)
        if(thresh is not None):
            data = int(thresh*2**thresh_pt)
            self.roach.write_int('control_theta', data)


    def initialize_10gbe(self, integ_time=10**-2):
        """
            Initialize the 10Gbe 
            integ_time  :integration time between two frames, in seconds
        """
        tx_core='ten_Gbe_v2'
        source=([192,168,2,3], 1234)
        dest=([192,168,2,10], 1234)
        dest_ip = (dest[0][0]*(2**24)+dest[0][1]*(2**16)+dest[0][2]*(2**8)+dest[0][3])
        source_ip = (source[0][0]*(2**24)+source[0][1]*(2**16)+source[0][2]*(2**8)+source[0][3])
        port = source[1]
        mac_base = (2<<40)+(2<<32)
        nchnls  = 2048/4   ##number of channels/parallel streams
        fpga_clk = 150.*10**6
        acc = int(round(integ_time/nchnls*fpga_clk))
        self.set_accumulation(acc, 0)
        self.roach.tap_start('tx_tap',tx_core,mac_base+source_ip,source_ip,port)

    def enable_dedispersor_acc(self):
        """
        Enable the accumulators for the dedispersion. This should be done just one
        time, after setting the accumulations.
        """
        curr_state = self.roach.read_int('control_control')
        state = set_bit(curr_state, 13)
        self.roach.write_int('control_control', state)
        time.sleep(0.1)
        
    def reset_dedispersor(self):
        """ Reset the dedispersors
        """
        curr_state = self.roach.read_int('control_control')
        state = set_bit(curr_state, 12)
        self.roach.write_int('control_control', state)
        time.sleep(0.1)
        state = clear_bit(state, 12)
        self.roach.write_int('control_control', state)

    def read_frb_detection(self):
        #dat = self.roach.read_int('control_adc_delay1') ##change this name!!
        #dat = dat & 1
        dat = self.roach.read_int('control_status')
        return dat

    def set_ring_buffer_gain(self, gain):
        """
        For the DRAM ring buffer the adc samples are reduced to 4 bits. To adjust 
        that 4 bits into a given range we multiply the samples by a gain.
        The gain uses 32_10 UFix data type.
        """
        gain_bin = calan.float2fixed(np.array(gain), 32,10, signed=False)
        self.roach.write_int('control_gain', gain_bin)


    def initialize_dram(self, addr=('10.0.0.29', 1234), n_pkt=10):
        """
        Creates the DRAM object to control arte ring buffer
        addr:   (computer recv ip, destination port)
        n_pkt:  number of frames send in one packet
        """
        if(self.dram is not None):
            raise Exception('There is already one dram object')
        self.dram = dram_ring(self.roach, sock_addr=addr, n_pkt=n_pkt)
    
    def write_dram(self):
        """
        Enable the write of the DRAM ring buffer
        """
        if(self.dram is None):
            raise Exception("There is no dram object, call initialize_dram")
        self.dram.init_ring()

    def read_dram(self, filename='data'):
        """Stop the writing procedure and start reading the saved data in the DRAM.
        It should take like 3 minutes
        """
        if(self.dram is None):
            raise Exception("There is no dram object, call initialize_dram")
        self.dram.reading_dram()


