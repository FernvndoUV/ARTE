import calandigital as calan
import numpy as np
import utils, corr, yaml
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def plot_dedispersor(_fpga,  DMs):
    """ fpga        :   katcp wrapper
        DMs         :   list of the DMs of each dedispersor
    """
    global fpga, data, index
    fpga = _fpga
    index = len(DMs)
    y_lim = (58,80)
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
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
    plot_dedispersor(roach, config['DMs'])



