import calandigital as calan
import numpy as np
import utils, corr, yaml
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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
    f = open('../configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
    plot_antennas(roach)

