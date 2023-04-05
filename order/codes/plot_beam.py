import calandigital as calan
import numpy as np
import utils, corr, yaml
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def plot_beam(_fpga, _freq=[1200, 1800]):
    global fpga, data, freq
    fpga = _fpga
    y_lim = (-90,0)

    data = []
    axes = []
    freq = np.linspace(_freq[0], _freq[1], 2048, endpoint=0)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_ylim(y_lim)
    ax.set_xlim(freq[0], freq[-1])
    ax.grid()
    ax.set_title('Beam')
    data, = ax.plot([],[],lw=2)
    anim = FuncAnimation(fig, animate, interval=50, blit=True)
    plt.show()

def animate(i):
    dat = utils.get_beam(fpga)
    spec = 10*np.log10(dat+1)-111.119
    data.set_data(freq, spec)
    return data,

if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
    plot_beam(roach)

