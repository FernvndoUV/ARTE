import calandigital as calan
import numpy as np
import utils, corr, argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

parser = argparse.ArgumentParser(
    description="Plot spectra from an spectrometer model in ROACH.")
parser.add_argument("-i", "--ip", dest="ip", default=None,
    help="ROACH IP address.")
parser.add_argument("-b", "--bof", dest="boffile",
    help="Boffile to load into the FPGA.")
parser.add_argument("-u", "--upload", dest="upload", action="store_true",
    help="If used, upload .bof from PC memory (ROACH2 only).")
parser.add_argument("-D", "--DM", dest="DMs", nargs="*",
        help="DM values")

def plot_dedispersor(_fpga,  DMs):
    """ fpga        :   katcp wrapper
        DMs         :   list of the DMs of each dedispersor
    """
    global fpga, data, index
    fpga = _fpga
    index = len(DMs)
    y_lim = (50,70)
    data = []
    fig = plt.figure()
    for i in range(index):
        ax = fig.add_subplot(4,3,i+1)
        ax.set_ylim(y_lim)
        ax.set_xlim(0, 1024)
        ax.grid()
        ax.set_title('DM: '+str(DMs[i]))
        dat, = ax.plot([],[])
        thresh, = ax.plot([],[])
        data.append(dat)
        data.append(thresh)
    plt.tight_layout()
    anim = FuncAnimation(fig, animate, interval=50, blit=True)
    plt.show()

def animate(_):
    for i in range(index):
        dedisp_pow = utils.get_dedispersed_power(fpga, i)
        thresh = utils.get_dedispersed_mov_avg(fpga, i)
        dedisp_pow = 10*np.log10(dedisp_pow+1)
        thresh = 10*np.log10(thresh+1)
        data[2*i].set_data(np.arange(2**10), dedisp_pow)
        data[2*i+1].set_data(np.arange(2**10), thresh)
    return data


if __name__ == '__main__':
    args = parser.parse_args()
    roach = corr.katcp_wrapper.FpgaClient(args.ip)
    print(len(args.DMs))
    plot_dedispersor(roach, args.DMs)



