import numpy as np
from astropy import units as u
from astropy import constants as cte
import matplotlib.pyplot as plt
from calandigital.instruments.arbitrary_generator import arbitrary_generator
import argparse, time


parser = argparse.ArgumentParser(
    description="Upload the FRB curve into an AWG")
parser.add_argument("-u", "--upload", dest="upload", action="store_true",
        help="If used, upload .bof from PC memory (ROACH2 only).")
parser.add_argument("-d", "--dm", dest="dm", default=500,
        help="DM of the signal")
parser.add_argument("-t", "--trigger", dest="trigger", action="store_true",
        help="If used trigger an single FRB after upload it")
parser.add_argument("-min", "--v_min", dest="v_min", default=5,
        help="Min voltage of the curve")
parser.add_argument("-max", "--v_max", dest="v_max", default=10,
        help="Max voltage of the curve")
parser.add_argument("-f","--freq", dest="freq", nargs="*", default=None,
        help="Low and High frequency (in MHz) to calculate the FRB curve"
        )
parser.add_argument("-g","--genname", dest="genname", default=None,
        help="Generator name (as a VISA string). Simulated if not given.\
    See https://pyvisa.readthedocs.io/en/latest/introduction/names.html")
parser.add_argument("-n", "--npts", dest="npts", default=2**13,
        help="Number of points of the AWG")
parser.add_argument("-on", "--turn_on", dest="turn_on",action="store_true",
        help="Turn the output on")

def frb_curve(DM, f1, f2, n_samp=8192):
    """
     inputs:
        DM in pc*cm**3
        f1, f2 in mhz
     outputs:
        f in MHz
        t in seconds 
    """
    ##wrong!!! the t must be linear!
    ti = 4.149*10**3*DM*f1**(-2)
    tf = 4.149*10**3*DM*f2**(-2)
    t = np.linspace(ti,tf,n_samp)
    f = np.sqrt(4.149*10**3*DM/t)
    #t = 4.149*10**3*DM*f**(-2)
    return [t-t[-1],f]

def main():
    args = parser.parse_args()
    if((args.freq is None) or (args.genname is None)):
        raise Exception("You should give the Generator visa name and the frequency to calculate the FRB curve")
    
    gen = arbitrary_generator(args.genname)
    gen.turn_output_off()
    gen.turn_burst_off()
    gen.set_termination('inf') ##set the termination to HIZ
    t,f = frb_curve(float(args.dm), float(args.freq[0]), float(args.freq[1])) 
    if(args.upload):
        f_norm = (f-(f[-1]+f[0])/2)/((f[-1]-f[0])/2)
        f_norm = f_norm/np.max(np.abs(f_norm))
        gen.set_arbitrary_waveform(f_norm[::-1])
        time.sleep(1)
    gen.instr.write('volt:high '+str(args.v_max))
    gen.instr.write('volt:low '+str(args.v_min))
    #gen.set_amplitude_vpp(args.vpp)
    #gen.set_offset_volt(args.offset)
    T = t[0]
    gen.set_freq_hz(1./T)
    gen.set_waveform('user')
    if(args.trigger):
        gen.burst_config(1)
        gen.turn_burst_on()
        gen.turn_output_on()
        #gen.send_sw_trigger()
    elif(args.turn_on):
        gen.turn_output_on()
    gen.instr.close()

if __name__ == '__main__':
    main()
