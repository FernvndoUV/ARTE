import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime, timedelta
from scipy.signal import savgol_filter, medfilt, find_peaks
import ipdb


class read_10gbe_data():
    """Class to read the data comming from the 10Gbe
    """
    def __init__(self, filename):
        """ Filename: name of the file to read from
        """
        self.f = open(filename, 'rb')
        ind = self.find_first_header()
        self.f.seek(ind*4)
        size = os.path.getsize(filename)
        self.n_spect = (size-ind*4)//(2052*4)


    def find_first_header(self):
        """ Find the first header in the file bacause after the header is the first
        FFT channel.
        """
        data = np.frombuffer(self.f.read(2052*4), '>I')
        ind = np.where(data==0xaabbccdd)[0][0]
        return (ind-2)

    def get_spectra(self, number):
        """
        number  :   requested number of spectrums
        You have to be aware that you have enough data to read in the n_spect
        """
        spect = np.frombuffer(self.f.read(2052*4*number), '>I')
        spect = spect.reshape([-1, 2052])
        self.n_spect -= number
        spectra = spect[:,4:]
        header = spect[:,:4]
        ##change even and odd channels (bug from the fpga..)
        even = spectra[:,::2]
        odd = spectra[:,1::2]
        spectra = np.array((odd, even))
        spectra = np.swapaxes(spectra.T, 0,1)
        spectra = spectra.reshape((-1,2048))
        spectra = spectra.astype(float)
        return spectra, header

    def get_complete(self):
        """
        read the complete data, be carefull on the sizes of your file
        """
        data, header = self.get_spectra(self.n_spect)
        return data, header

    def close_file(self):
        self.f.close()


def identify_rfi(sample_spect):
    """
    Get the channels with RFI
    """
    #TODO: in the meanwhile we flag the DC values
    flags = np.arange(20).tolist()
    flags = flags+[1024]
    #flags += np.arange(85).tolist()
    #flags += np.arange(1792,2048,1).tolist()
    flags += (np.arange(27)+394).tolist()
    flags += (np.arange(8)+1020).tolist()
    flags += (np.arange(5)+1155).tolist()
    flags += (np.arange(12)+1175).tolist()
    flags += (np.arange(21)+1220).tolist()
    flags += (np.arange(16)+1275).tolist()
    flags += (np.arange(18)+1325).tolist()
    flags += (np.arange(10)+1367).tolist()
    flags += (np.arange(16)+1439).tolist()
    flags += (np.arange(2)+1830).tolist()
    flags += (np.arange(3)+2045).tolist()
    return flags


def get_baseline(sample_spect):
    """
    Obtain the base line for the receiver
    """
    flags = identify_rfi(sample_spect)
    mask = np.ones(2048, dtype=bool)
    mask[flags] = False
    base = savgol_filter(sample_spect, 9, 3) #window 9 points, local pol order 3
    base = base*mask
    return mask, base

def moving_average(data, win_size=64):
    out = np.zeros(len(data)-win_size+1)
    for i in range(len(data)-win_size+1):
        out[i] = np.mean(data[i:win_size+i])
    return out


def get_log_data(filenames,cal_time=2,spect_time=1e-2,file_time=5 ,decimation=15,
        win_size=15,tails=32, temperature=True, substract_median=True):
    """
    filenames   :   list with the names of the plots
    cal_time    :   calibration time at the begining of each file
    spect_time  :   time between two spectra
    file_time   :   complete time of each file in minutes
    tails       :
    temperature :   Return the data in temperature relative to the hot source
    """
    sample = read_10gbe_data(filenames[0])
    sample_spect, header = sample.get_complete()
    sample.close_file()

    if(temperature):
        #get the first spectras as baseline
        hot_source = sample_spect[2:int(cal_time/spect_time),:]
        flags, baseline = get_baseline(np.median(hot_source,axis=0))

    else:
        flags = np.ones(2048, dtype=bool)

    ##approximated size for one file
    spect_size = int(file_time*60/spect_time-tails)


    data = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])
    clip01 = np.zeros(len(filenames)*spect_size//decimation, dtype=bool)  #antenna0 and 1
    clip2 = np.zeros(len(filenames)*spect_size//decimation, dtype=bool)  #antenna2
    clip3 = np.zeros(len(filenames)*spect_size//decimation, dtype=bool)  #antenna3 (reference)
    bases = np.zeros((len(filenames), 2048))

    #nueva linea fran
    data_new = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])
    ### fin fran

    if(temperature):
         for i in range(0, len(filenames)):
            sample = read_10gbe_data(filenames[i])
            sample_spect, header = sample.get_complete()
            sample.close_file()

            base, temp_data = hot_cold_calibration(sample_spect, cal_time, spect_time, decimation, spect_size, substract_median=substract_median)
            data[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags] = temp_data
            bases[i,:] = base
            #now we look at clipping

            sat01, sat2,sat3 = saturation_search(header, spect_size, decimation)
            clip01[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat01
            clip2[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat2
            clip3[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat3
    else:
         for i in range(0, len(filenames)):
            sample = read_10gbe_data(filenames[i])
            sample_spect, header = sample.get_complete()
            sample.close_file()
            aux = sample_spect[:spect_size,:]
            #accumulate, see that could be data that is discarted depending on the
            #decimation value.
            dec_size = aux.shape[0]//decimation
            aux = aux[:dec_size*decimation,:].reshape([-1, decimation, aux.shape[1]])
            aux = np.mean(aux.astype(float), axis=1)
            data[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags] = 10*np.log10(aux+1)-111.119
            sat01, sat2,sat3 = saturation_search(header, spect_size, decimation)
            clip01[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat01
            clip2[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat2
            clip3[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat3

    ## fran edicion
    avg_pow = np.mean(data[:,flags], axis=1)
    avg_pow = moving_average(avg_pow, win_size=win_size)
    t = np.arange(len(avg_pow))*spect_time/60.*decimation #time in
    ## fin fran edicion

    # avg = np.mean(data[:, flags], axis=1)
    # avg = moving_average(avg, win_size=win_size)
    clip01 = moving_average(clip01, win_size=win_size)
    clip01 = np.invert(clip01==0)
    t = np.arange(len(avg))*spect_time/60.*decimation   #time in minutes
    return data, avg, (clip01, clip2, clip3), t, bases, flags





def hot_cold_calibration(sample_spect, cal_time, spect_time, decimation, spect_size, plot=False,substract_median = True):
    """
    Make the calibration steps into one file to obtain the absolute temperature
    """

    P = np.median(sample_spect,axis = 1)
    gradiente = np.abs(np.gradient(P))
    peaks,_ = find_peaks(gradiente,height = 1e6)

    hot_index = peaks[0]+20
    P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
    P_hot = savgol_filter(P_hot, 9, 3)

    load_index = peaks[1] + 20
    P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
    P_load = savgol_filter(P_load, 9, 3)

    aux_index = peaks[1]+200

    P_aux = (np.mean(sample_spect[aux_index:aux_index+5,:],axis=0))
    P_aux = savgol_filter(P_aux, 9, 3)


    flags, baseline_load = get_baseline(P_load)
    bases[i,:] = baseline_load

    t_load = 290 #temp amb
    ENR_ns = (14.85+14.74)/2. #dB
    t_hot = 10**((ENR_ns-8.5)/10.)*t_load+t_load #temp ns on

    t_rx = (t_hot*P_load -t_load*P_hot)/(P_hot-P_load)
    aux = sample_spect[:spect_size,:]
    aux = (aux/P_load)*(t_rx+t_load)-t_rx
    if(plot):
        fig, axes = plt.subplots(2,2)
        axes[0,0].plot(peaks,label = 'Peaks gradiente')
        axes[1,0].plot(P_hot,label = 'Hot baseline')
        axes[1,0].plot(P_load,label = 'Load baseline')
        axes[0,1].plot(t_rx,label = 'Receiver noise temperature')

        axes[1,1].plot(P_aux,label = 'Sky power')
        axes[1,1].plot(P_load,label = 'Load power')

        axes[0,0].set_title('Peaks gradiente')
        axes[1,0].set_title('Hot and load baseline')
        axes[0,1].set_title('Receiver noise temperature')
        axes[1,1].set_title('Sky and load power')

        axes[1,1].set_xlabel('samples')
        axes[1,0].set_xlabel('samples')

        axes[1,0].set_ylabel('Power linear')
        axes[0,0].set_ylabel('Power linear')
        for ax in axes.flatten():
            ax.grid()
            ax.legend()
        plt.show()

    dec_size = aux.shape[0]//decimation
    dec_data = aux[:dec_size*decimation,:].reshape([-1, decimation, aux.shape[1]])
    dec_data = np.mean(dec_data.astype(float), axis=1)

    if(substract_median):
        mediana = (np.median(dec_data[:,:],axis=0))
        data_without_median = np.subtract(dec_data,mediana)
        data_without_median[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags] =data_without_median[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags]
        #Fin editado fran
        return bases, data_without_median
    else:
        return bases, dec_data


def saturation_search(header, spect_size, decimation):
    dec_size = spect_size//decimation
    sat = np.bitwise_and(header[:spect_size,1],2**2-1) #just take the cliping values of antennas0,1
    sat = sat[:dec_size*decimation].reshape([-1, decimation])
    sat = np.sum(sat, axis=1)
    sat = np.invert(sat==0)
    clip01 = sat
    sat = np.bitwise_and(header[:spect_size,1],2**3) #just take the cliping value of antena2
    sat = sat[:dec_size*decimation].reshape([-1, decimation])
    sat = np.sum(sat, axis=1)
    sat = np.invert(sat==0)
    clip2 = sat
    sat = np.bitwise_and(header[:spect_size,1],2**4) #just take the cliping value of antena2
    sat = sat[:dec_size*decimation].reshape([-1, decimation])
    sat = np.sum(sat, axis=1)
    sat = np.invert(sat==0)
    clip3 = sat
    return clip01, clip2, clip3


def get_dm_data(filenames):
    """
    get the dedispersors data from the misc file
    """
    dms = []
    mov_avg = []
    for i in range(11):
        dms.append([])
        mov_avg.append([])
    for filename in filenames:
        f = np.load(filename+'.npz', allow_pickle=True)
        dms[0].append(f['dm0'].flatten()/2.**15)
        dms[1].append(f['dm1'].flatten()/2.**15)
        dms[2].append(f['dm2'].flatten()/2.**15)
        dms[3].append(f['dm3'].flatten()/2.**15)
        dms[4].append(f['dm4'].flatten()/2.**15)
        dms[5].append(f['dm5'].flatten()/2.**15)
        dms[6].append(f['dm6'].flatten()/2.**15)
        dms[7].append(f['dm7'].flatten()/2.**15)
        dms[8].append(f['dm8'].flatten()/2.**15)
        dms[9].append(f['dm9'].flatten()/2.**15)
        dms[10].append(f['dm10'].flatten()/2.**15)
        mov_avg[0].append((f['mov_avg0'].flatten()/2.**15))
        mov_avg[1].append((f['mov_avg1'].flatten()/2.**15))
        mov_avg[2].append((f['mov_avg2'].flatten()/2.**15))
        mov_avg[3].append(f['mov_avg3'].flatten()/2.**15)
        mov_avg[4].append(f['mov_avg4'].flatten()/2.**15)
        mov_avg[5].append(f['mov_avg5'].flatten()/2.**15)
        mov_avg[6].append(f['mov_avg6'].flatten()/2.**15)
        mov_avg[7].append(f['mov_avg7'].flatten()/2.**15)
        mov_avg[8].append(f['mov_avg8'].flatten()/2.**15)
        mov_avg[9].append(f['mov_avg9'].flatten()/2.**15)
        mov_avg[10].append(f['mov_avg10'].flatten()/2.**15)
        f.close()
    return dms, mov_avg



