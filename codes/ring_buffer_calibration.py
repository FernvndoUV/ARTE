import numpy as np
import matplotlib.pyplot as plt
import calandigital as calan
import ipdb
import time

###
### The idea is change the gain, calculate the similarity between the two spectras
### that should be a concave function so we search for the maximum
###
def ring_buffer_calibration(roach_ctrl, percentage=0.5,iters=16, plot=False):
    """
    The full scale data is represented 8_7 fix, then is multiply by a gain of
    32_10 ufix and the convertion finally is 4_0fix.
    """
    ##
    gains = np.zeros(iters)
    for i in range(iters):
        snap_data = get_dram_snapshot(roach_ctrl.roach)
        snap_data = snap_data.astype(float)
        gain = np.max(snap_data[0,:])*2**7/2**3*percentage
        gains[i] = gain
    gain = np.median(gains)
    print("Computed gain: {:.2f}".format(gain))
    roach_ctrl.set_ring_buffer_gain(gain)
    time.sleep(0.5)
    snap_data = get_dram_snapshot(roach_ctrl.roach)
    spectra = get_integrated_spectra(roach_ctrl.roach)
    if(plot):
        fig, axes = plt.subplots(2,3)
        axes[0,0].plot(snap_data[0,:])
        axes[1,0].plot(snap_data[1,:])
        axes[0,1].plot(10*np.log10(spectra[0,:]+1))
        axes[1,1].plot(10*np.log10(spectra[1,:]+1))
        ##
        axes[0,2].hist(snap_data[0,:], bins=np.linspace(-2**7,2**7-1,2**8))
        axes[1,2].hist(snap_data[0,:], bins=np.linspace(-2**3,2**3-1,2**3))
        for ax in axes.flatten():
            ax.grid()
        axes[0,0].set_ylim((-2**7-0.5,2**7+0.5))
        axes[1,0].set_ylim((-2**3-0.5,2**3+0.5))
        plt.show() 
     


def ring_buffer_gain_spectra_test(roach_control, gain_test=2**7+np.linspace(-2**6,2**6,8), 
        integ_spectra=32,fit_order=13, debug_plot=False):
    """
    roach_control:  
    steps:  how many steps try before keeping a result
    """
    similarity = np.zeros(len(gain_test)) 
    reduced_spectra = np.zeros((len(gain_test), 4096))
    roach_control.set_ring_buffer_gain(gain_test[0])
    full_spectra, red_spectra = get_integrated_spectra(roach_control.roach, integ_spectra=integ_spectra)
    reduced_spectra[0,:] = red_spectra
    coeff = np.polyfit(np.arange(4096), 10*np.log10(full_spectra), fit_order)
    pol_full = np.poly1d(coeff)
    coeff = np.polyfit(np.arange(4096), 10*np.log10(red_spectra), fit_order)
    pol_red = np.poly1d(coeff)
    similarity[0] = np.sum(np.abs(pol_full(np.arange(4096))-pol_red(np.arange(4096))))
    for i,gain in enumerate(gain_test[1:]):
        print('testing gain: {:.2f}'.format(gain))
        roach_control.set_ring_buffer_gain(gain)
        red_spectra = get_integrated_spectra(roach_control.roach, 
                integ_spectra=integ_spectra,
                single=True)
        reduced_spectra[i+1,:] = red_spectra
        coeff = np.polyfit(np.arange(4096), 10*np.log10(red_spectra), fit_order)
        pol_red = np.poly1d(coeff)
        similarity[i+1] = np.sum(np.abs(pol_full(np.arange(4096))-pol_red(np.arange(4096))))
    if(debug_plot):
        fig, axes = plt.subplots(2,1)
        axes[1].plot(similarity)
        axes[0].plot(10*np.log10(full_spectra), label='full')
        for i in range(len(gain_test)):
            axes[0].plot(10*np.log10(reduced_spectra[i,:]), label='{:.2f}'.format(gain_test[i]))
        axes[1].grid()
        axes[0].grid()
        axes[0].legend()
        plt.show()
    ##search for a change of sign in the derivative
    sim_ind = np.argmin(similarity)
    most_sim = gain_test[sim_ind]
    debug = [reduced_spectra, full_spectra]
    return most_sim, similarity, debug



def get_dram_snapshot(roach):
    snap_data = calan.read_snapshots(roach, ['adcsnap0', 'snapshot'])
    snap_data = np.array(snap_data)
    return snap_data

def bit_usage(data, nbits=4):
    dat = np.copy(data)
    ##convert from 2complement to unsigned
    mask = np.where(data<0)
    dat[mask] = dat[mask]+2**(nbits)
    bits_usage = np.log2(dat+1)
    return bits_usage

def get_integrated_spectra(roach, integ_spectra=32, single=False):
    if(not single):
        data = np.zeros((2,4096))
        for i in range(integ_spectra):
            snap_data = get_dram_snapshot(roach)
            spec_data = np.fft.fft(snap_data, axis=1)
            data = data+np.abs(spec_data[:,:4096])
    else:
        data = np.zeros(4096)
        for i in range(integ_spectra):
            snap_data = np.array(calan.read_snapshots(roach,['snapshot']))[0]
            spec_data = np.fft.fft(snap_data)
            data = data+np.abs(spec_data[:4096])
    return data


        
