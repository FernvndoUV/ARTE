import calandigital as calan
import numpy as np
import utils, corr, yaml
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def plot_rfi_signals(_fpga, _freq=[1200,1800]):
    global fpga, data, freq
    fpga = _fpga
    y_lim = (0,100)
    data = []
    axes = []
    freq = np.linspace(_freq[0], _freq[1], 2048, endpoint=0)
    #fig = plt.figure()
    names = ['RFI corr', 'RFI pow', 'SW score', 'HW score']
    fig, axes = plt.subplots(2,2)
    axes = axes.flatten()
    for i in range(len(axes)):
        #ax = fig.add_subplot(2,2,i+1)
        ax = axes[i]
        ax.set_ylim(y_lim)
        ax.set_xlim(freq[0], freq[-1])
        ax.grid()
        ax.set_title(names[i])
        line, = ax.plot([],[],lw=2)
        data.append(line)
    axes[2].set_ylim(0,1)
    axes[3].set_ylim(0,1)
    anim = FuncAnimation(fig, animate, interval=50, blit=True)
    plt.show()


def animate(i):
    dat = utils.get_rfi_signals(fpga)
    for i in range(2):
        spec = 10*np.log10(dat[i]+1)
        data[i].set_data(freq, spec)
    dat[1][dat[0]==0] = 1
    sw_data = (dat[0])/(dat[1])
    hw_data = utils.get_rfi_score(roach)
    data[2].set_data(freq,sw_data)
    data[3].set_data(freq,hw_data)
    return data

if __name__ == '__main__':
    f = open('../configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
    plot_rfi_signals(roach)
