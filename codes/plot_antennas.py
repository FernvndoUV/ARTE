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

def plot_antennas(_fpga, _freq=[1200, 1800]):
    global fpga, data, freq
    fpga = _fpga
    y_lim = (0,100)
    data = []
    axes = []
    freq = np.linspace(_freq[0], _freq[1], 2048, endpoint=0)
    fig = plt.figure()
    for i in range(4):
        ax = fig.add_subplot(2,2,i+1)
        ax.set_ylim(y_lim)
        ax.set_xlim(freq[0], freq[-1])
        ax.grid()
        ax.set_title('Antenna %i' %i)
        line, = ax.plot([],[],lw=2)
        data.append(line)
    anim = FuncAnimation(fig, animate, interval=50, blit=True)
    plt.show()

def animate(i):
    dat = utils.get_antenas(fpga)
    for i in range(4):
        spec = 10*np.log10(dat[i,:]+1)
        data[i].set_data(freq, spec)
    return data

if __name__ == '__main__':
    args = parser.parse_args()
    roach = corr.katcp_wrapper.FpgaClient(args.ip)
    #roach = calan.initialize_roach(args.ip, boffile=args.boffile, upload=args.upload)
    plot_antennas(roach)
