import calandigital as calan
import numpy as np
import utils, corr, yaml, time
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
import ipdb


def plot_bits(_fpga):
    global fpga, data, freq, axes
    fpga = _fpga
    y_lim = (0,35)
    freq = np.linspace(1200, 1800,4096, endpoint=False)
    data = []
    axes = []
    plt.ion()
    fig, axes = plt.subplots(2,2)
    ##
    init_data = np.random.random(size=8192)
    _,_,patches = axes[0,0].hist(init_data*8, bins=np.arange(8))
    #data.append(patches)
    _,_,line = axes[0,1].hist(init_data*4, bins=np.arange(4))
    #data.append(patches)
    #data.append(axes[0,1])

    for i in range(2):
        axes[0,i].set_ylim(0,1)
        axes[0,i].grid()
        axes[1,i].set_ylim(0,50)
        axes[1,i].set_xlim(freq[0], freq[-1])
        #data.append(line)
        axes[1,i].grid()
        line, = axes[1,i].plot([],[])
        data.append(line)
    #init_data 
    #axes[0,0].set_xlim(0,8)
    #axes[0,1].set_xlim(0,4)
    while(1):
        snap_data = calan.read_snapshots(fpga, ['adcsnap0', 'snapshot'])
        snap_data = np.array(snap_data)
        spec_data = np.fft.fft(snap_data, axis=1)
        #bits0 = bit_usage(snap_data[0,:], nbits=8)
        #bits1 = bit_usage(snap_data[1,:], nbits=4)
        bits0 = snap_data[0,:]
        bits1 = snap_data[1,:]
        counts = [bits0, bits1]
        for i in range(2):
            axes[0,i].cla()
            axes[1,i].cla()
            axes[0,i].set_ylim(0,1)
            axes[1,i].set_ylim(0,50)
            #axes[0,i].hist(counts[i], np.arange(8-4*i+1), density=True, color='blue')
            bits = 8-4*i
            axes[0,i].hist(counts[i], np.linspace(-2**bits, 2**bits-1, 2**bits), density=True, color='blue')
            axes[1,i].plot(freq, 10*np.log10(np.abs(spec_data[i,:len(freq)]+1)))
            axes[0,i].grid()
            axes[1,i].grid()
        fig.canvas.draw()
        #time.sleep(0.5)
    #anim = FuncAnimation(fig, animate, interval=50, blit=True)
    #plt.show()

def animate(a):
    snap_data = calan.read_snapshots(fpga, ['adcsnap0', 'snapshot'])
    snap_data = np.array(snap_data)
    spec_data = np.fft.fft(snap_data, axis=1)

    #bits0,_ = np.histogram(bit_usage(snap_data[0,:], nbits=8), np.arange(8), density=True)
    #bits1,_ = np.histogram(bit_usage(snap_data[1,:], nbits=4), np.arange(4), density=True)
    bits0 = bit_usage(snap_data[0,:], nbits=8)
    bits1 = bit_usage(snap_data[1,:], nbits=4)
    counts = [bits0, bits1]
    for i in range(2):
        data[i].set_data(freq, 10*np.log10(np.abs(spec_data[i,:len(freq)]+1)))
        ##clear the patches 
        children = axes[0,i].get_children()
        #ipdb.set_trace()
        print(len(children))
        for ind,child in enumerate(children):
            #ipdb.set_trace()
            rect = type(child) is matplotlib.patches.Rectangle
            spine = type(child) is matplotlib.spines.Spine
            if(rect and (ind!=(len(children)-1))):
                print(child)
                child.remove()
        axes[0,i].hist(counts[i], np.arange(4+4*i+1), density=True, color='blue')
    return data


def bit_usage(data, nbits=4):
    dat = np.copy(data)
    ##convert from 2complement to unsigned
    mask = np.where(data<0)
    dat[mask] = dat[mask]+2**(nbits)
    bits_usage = np.log2(dat+1)
    return bits_usage

if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
    time.sleep(1)
    plot_bits(roach)



