import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.signal import savgol_filter
import ipdb
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder_name", dest="folder_name", default=None)
parser.add_argument("-l", "--log_per_img", dest="log_per_img", default=1)
parser.add_argument("-c", "--cal_time", dest="cal_time", default=1)
parser.add_argument("-ft", "--file_time", dest="file_time", default=2)
parser.add_argument("-st", "--spect_time", dest="spect_time", default=1e-2)
parser.add_argument("-d", "--decimation", dest="decimation", default=1)
parser.add_argument("-w", "--avg_win", dest="mov_avg_size", default=100)
parser.add_argument("-t", "--tails", dest="tails", default=32)
parser.add_argument("-i", "--img_folder", dest="img_folder", dtype=str)




###
###
###


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
        return ind

    def get_spectra(self, number):
        """
        number  :   requested number of spectrums
        You have to be aware that you have enough data to read in the n_spect
        """
        spect = np.frombuffer(self.f.read(2052*4*number), '>I')
        spect = spect.reshape([-1, 2052])
        self.n_spect -= number
        return spect[:,4:]

    def get_complete(self):
        """
        read the complete data, be carefull on the sizes of your file
        """
        data = self.get_spectra(self.n_spect)
        return data

    def close_file(self):
        self.f.close()

def identify_rfi(sample_spect):
    """
    Get the channels with RFI
    """
    #TODO: in the meanwhile we flag the DC values
    #flags = (np.arange(3)+0).tolist()
    flags = np.arange(20).tolist()
    flags = flags+[1024]
    flags += (np.arange(27)+394).tolist()
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
    base = savgol_filter(sample_spect[mask], 51, 3)
    return mask, base

def moving_average(data, win_size=64):
    out = np.zeros(len(data)-win_size+1)
    for i in range(len(data)-win_size+1):
        out[i] = np.mean(data[i:win_size+i]) 
    return out


def get_image_data(filenames,cal_time=1,spect_time=1e-2,file_time=2 ,decimation=1,
        win_size=100,tails=32):
    """
    filenames   :   list with the names of the plots
    cal_time    :   calibration time at the begining of each file   
    spect_time  :   time between two spectra
    file_time   :   complete time of each file in minutes
    """
    filenames.sort()
    
    sample = read_10gbe_data(filenames[0])
    sample_spect = sample.get_complete()
    sample.close_file()
    #get the first spectras as base line 
    hot_source = sample_spect[2:int(cal_time/spect_time),:]
    flags, baseline = get_baseline(np.median(hot_source,axis=0))
    ##approximated size for one file
    spect_size = int(file_time*60/spect_time-tails)
    baseline = np.tile(baseline, (spect_size,1))
    data = np.zeros([len(filenames)*(spect_size), int(np.sum(flags))])
    data[:spect_size,:] = sample_spect[:spect_size,flags]-baseline
    for i in range(1, len(filenames)):
        sample = read_10gbe_data(filenames[i])
        sample_spect = sample.get_complete()
        sample.close_file()
        #get the first spectras as base line 
        hot_source = sample_spect[2:int(cal_time/spect_time),:]
        flags, baseline = get_baseline(np.median(hot_source,axis=0))
        baseline = np.tile(baseline, (spect_size,1))
        data[i*(spect_size):(i+1)*(spect_size),:] = sample_spect[:spect_size,flags]-baseline
    ##get only the data written
    data = data[:(len(filenames)+1)*spect_size,:]
    #now we decimate
    aux = data.shape[0]//decimation
    data = data[:aux*decimation,:].reshape([-1,decimation,data.shape[1]])
    data = np.mean(data.astype(float),axis=1)
    avg_pow = np.mean(data, axis=1)
    avg_pow = moving_average(avg_pow, win_size=win_size)
    t = np.arange(len(avg_pow))*spect_time/60.*decimation   #time in minutes
    return data, avg_pow, t, flags
        

def get_dm_data(filenames):
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
        mov_avg[0].append(f['mov_avg0'].flatten()/2.**15)
        mov_avg[1].append(f['mov_avg1'].flatten()/2.**15)
        mov_avg[2].append(f['mov_avg2'].flatten()/2.**15)
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


def plot_folder(folder_name, log_per_img=2, cal_time=1, file_time=2,spect_time=1e-2,
        decimation=1, mov_avg_size=100, tails=32, img_folder="log_img"):

    if(not os.path.exists(img_folder)):
        os.mkdir(img_folder)
    _log_names = os.listdir(os.path.join(folder_name, 'logs'))
    ind = np.random.randint(len(_log_names))
    log_names = [os.path.join(folder_name,'logs',log) for log in _log_names]
    misc_names = [os.path.join(folder_name,'misc',log) for log in _log_names] 

    freq = np.linspace(1200,1800, 2048, endpoint=False)
    
    n_img = len(log_names)//log_per_img
    for i in range(n_img):
        print("%i of %i"%(i+1,n_img))
        sublogs = log_names[i*log_per_img:(i+1)*log_per_img]
        data, avg_pow, t, flags = get_image_data(sublogs,cal_time, spect_time,
                file_time, decimation, mov_avg_size, tails)
        hr_i= sublogs[0].split('/')[-1].split('.')[0]
        hr_f= sublogs[-1].split('/')[-1].split('.')[0]
    
        name = os.path.join(img_folder,  hr_i+'_to_'+hr_f)
        print('Making 10Gbe plot')
        fig, axes = plt.subplots(2,1, sharex=True)
        axes[0].plot(t,avg_pow)
        #axes[0].axis(ymin = -1000000, ymax = 1000000)
        axes[0].grid()
        axes[0].set_ylabel('Linear power')
        axes[1].set_title("Spectrogram")
        axes[1].pcolormesh(t,freq[flags], data[:len(t),::-1].T, cmap = 'viridis',vmax = 10**6, vmin = -10**6,shading='auto' )
        axes[1].set_xlabel('minutes')
        axes[1].set_ylabel('MHz')

        plt.savefig(name+'_log.png', dpi=1000)
        ##delete some variables
        fig.clear()
        plt.close(fig)
        del data, avg_pow, flags
        del fig, axes

        print("Making dedispersors plots")
        submisc = misc_names[i*log_per_img:(i+1)*log_per_img]
        dms, mov_avg = get_dm_data(submisc)
        
        tf = t[-1]
        fig, axes = plt.subplots(11,1)
        for i in range(11):
            t = np.linspace(0,tf, len(dms[i][0]))
            axes[i].plot(t,dms[i][0])
            axes[i].plot(t, mov_avg[i][0])
            axes[i].grid()
        plt.savefig(name+'_dms.png', dpi=500)
        fig.clear()
        plt.close(fig)
        del dms, mov_avg, t
        del fig, axes
        

if __name__ == '__main__':
     
    args = parser.parse_args()
    plot_folder(
            folder_name=args.folder_name,
            log_per_img=args.log_per_img,
            cal_time=args.cal_time, 
            file_time=args.file_time,
            spect_time=args.spect_time,
            decimation=args.decimation,
            mov_avg_size=args.mov_avg_size,
            tails=args.tails,
            img_folder=args.img_folder)
