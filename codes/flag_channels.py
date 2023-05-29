import numpy as np
import calandigital as calan

def flag_channels(roach, flags, n_chan=2048, n_streams=4):
    """ n_chan: fft channels
        n_streams = parallel streams (out of the fft)

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
        roach.write_int('control_rfi_flag',val+2**31)
        #roach.write_int('rfi_flag', val)
    roach.write_int('control_rfi_flag',0)

    
