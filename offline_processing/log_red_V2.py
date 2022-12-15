import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.signal import savgol_filter, medfilt
import ipdb #ipdb.set_trace()
import argparse
from mpl_toolkits.axes_grid1 import make_axes_locatable



parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder_name", dest="folder_name", default=None)
parser.add_argument("-l", "--log_per_img", dest="log_per_img", default=1, type=int)
parser.add_argument("-c", "--cal_time", dest="cal_time", default=1, type=float)
parser.add_argument("-ft", "--file_time", dest="file_time", default=5, type=float)
parser.add_argument("-st", "--spect_time", dest="spect_time", default=1e-2)
parser.add_argument("-d", "--decimation", dest="decimation", default=10, type=int)
parser.add_argument("-w", "--avg_win", dest="mov_avg_size", default=15, type=int)
parser.add_argument("-t", "--tails", dest="tails", default=32, type=int)
parser.add_argument("-i", "--img_folder", dest="img_folder", type=str)
parser.add_argument("-m", "--plot_misc", dest="plot_misc", action="store_true")
parser.add_argument("-pc", "--plot_clip", dest="plot_clip", action="store_true")



##
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
        spectra = spect[:,4:]
        header = spect[:,:4]
        ##change even and odd channels (bug from the fpga..)
        even = spectra[:,::2]
        odd = spectra[:,1::2]
        spectra = np.array((odd, even))
        spectra = np.swapaxes(spectra.T, 0,1)
        spectra = spectra.reshape((-1,2048))
        return spectra, header




    def get_complete(self):
        """
        read the complete data, be carefull on the sizes of your file
        """
        data, header = self.get_spectra(self.n_spect)
        return data, header

    def close_file(self):
        self.f.close()

# ipdb.set_trace()

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

#ipdb.set_trace()

def get_image_data_temperature(filenames,cal_time=1,spect_time=1e-2,file_time=1 ,decimation=15,
        win_size=15,tails=32, temperature=True):
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

    #get the first spectras as baseline
    hot_source = sample_spect[2:int(cal_time/spect_time),:]
    flags, baseline = get_baseline(np.median(hot_source,axis=0))

    ##approximated size for one file
    spect_size = int(file_time*60/spect_time-tails)
    data = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])
    clip = np.zeros(len(filenames)*spect_size//decimation, dtype=bool)
    bases = np.zeros((len(filenames), 2048))

    for i in range(0, len(filenames)):
        sample = read_10gbe_data(filenames[i])
        sample_spect, header = sample.get_complete()
        sample.close_file()

        #get the first spectras as base line
        hot_source = sample_spect[2:int(cal_time/spect_time*3),:]
        ##at hot source there is an increase in the amount of power
        hot_pow = np.sum(hot_source, axis=1)
        hot_pow = medfilt(hot_pow, 5)
        thresh = (np.max(hot_pow)+np.min(hot_pow))/2
        index = (hot_pow>thresh)
        #ipdb.set_trace()
        #
        flags, baseline = get_baseline(np.median(hot_source[index,:],axis=0))
        bases[i,:] = baseline

        aux = sample_spect[:spect_size,:]
        aux = (aux[:, flags]*380./baseline[flags])-90
        #accumulate, see that could be data that is discarted depending on the
        #decimation value.
        dec_size = aux.shape[0]//decimation
        aux = aux[:dec_size*decimation,:].reshape([-1, decimation, aux.shape[1]])
        aux = np.mean(aux.astype(float), axis=1)
        data[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags] = aux

       #now we look at the clipping
        #ipdb.set_trace()
        sat = np.bitwise_and(header[:spect_size,1],2**4-1) #just take the cliping values
        sat = sat[:dec_size*decimation].reshape([-1, decimation])
        sat = np.sum(sat, axis=1)
        sat = np.invert(sat==0)
        clip[i*(spect_size//decimation):(i+1)*(spect_size//decimation)] = sat

    avg_pow = np.mean(data[:,flags], axis=1)
    avg_pow = moving_average(avg_pow, win_size=win_size)
    clip = moving_average(clip, win_size=win_size)
    clip = np.invert(clip==0)
    #print(clip)
    t = np.arange(len(avg_pow))*spect_time/60.*decimation   #time in minutes
    #plt.plot(data[100,:])
    #plt.grid()
    #plt.show()

    return data, avg_pow, clip, t, bases,flags

# savitzky_golay(y, 51, 3)

def get_dm_data(filenames):
    dms = []
    mov_avg = []
    for i in range(11):
        dms.append([])
        mov_avg.append([])
    for filename in filenames:
        f = np.load(filename+'.npz', allow_pickle=True)
        # dms[0].append(savgol_filter(f['dm0'].flatten()/2.**15,51,3))
        # dms[1].append(savgol_filter(f['dm1'].flatten()/2.**15,51,3))
        # dms[2].append(savgol_filter(f['dm2'].flatten()/2.**15,51,3))
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
        mov_avg[0].append((f['mov_avg0'].flatten()/2.**15) -31.8)
        mov_avg[1].append((f['mov_avg1'].flatten()/2.**15)-31.8)
        mov_avg[2].append((f['mov_avg2'].flatten()/2.**15)-31.8)
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



def plot_folder(folder_name, log_per_img=1, cal_time=1, file_time=2,spect_time=1e-2,
        plot_misc=True, decimation=1, mov_avg_size=32, tails=32, img_folder="log_img",
        plot_clip=True):

    if(not os.path.exists(img_folder)):
        os.mkdir(img_folder)
    _log_names = os.listdir(os.path.join(folder_name, 'logs'))
    _log_names.sort()
    log_names = [os.path.join(folder_name,'logs',log) for log in _log_names]
    misc_names = [os.path.join(folder_name,'misc',log) for log in _log_names]
    freq = np.linspace(1200,1800, 2048, endpoint=False)

    n_img = len(log_names)//log_per_img
    for i in range(n_img):
        print("%i of %i"%(i+1,n_img))
        sublogs = log_names[i*log_per_img:(i+1)*log_per_img]
        data, avg_pow, clip, t, bases,flags = get_image_data_temperature(sublogs,cal_time, spect_time,
                file_time, decimation, mov_avg_size, tails)
        hr_i= sublogs[0].split('/')[-1].split('.')[0]
        hr_f= sublogs[-1].split('/')[-1].split('.')[0]

        name = os.path.join(img_folder,  hr_i+'_to_'+hr_f)
        print('Making 10Gbe plot')
        fig, axes = plt.subplots(2,1, sharex=True, gridspec_kw={'height_ratios': [0.15,0.85]})
        axes[0].set_title('Average power',fontsize=20)
        axes[0].plot(t,avg_pow,linewidth=1.5)
        # axes[0].axis(ymin =  np.mean(avg_pow)-5 , ymax = np.mean(avg_pow)+5 )
        # axes[0].vlines([1,2,3,4,6,7,8,9],  np.mean(avg_pow)-5 ,np.mean(avg_pow)+5 , linestyles='dashed',linewidth= 0.1, colors='grey')
        #,2,3,4]
        axes[0].grid()
        axes[0].set_ylabel('Temperature K',fontsize=15)
        axes[0].tick_params(axis= 'y', labelsize=15)


        if(plot_clip):
            #find rising/falling edges
            ind = np.diff(clip.astype(int))
            ris = np.where(ind==1)[0]
            fall = np.where(ind==-1)[0]
            ##check weird cases
            if(clip[0]):
                #the first sample is already clipped
                ris = np.insert(ris,0,0)
            if(clip[-1]):
                #the last sample is clipped
                fall = np.insert(fall, len(fall), len(clip)-1)
            print("Clipping: \nrising edges: {:} , falling edges: {:}".format(len(ris), len(fall)))
            for up, down in zip(ris, fall):
                axes[0].axvspan(t[up], t[down], color='r', alpha=0.3, lw=0)

        graph = axes[1].pcolormesh(t,freq , data[:len(t),::].T, cmap = 'viridis',vmax = 290,vmin =  200,shading='auto' )
        # axes[1].vlines([1,2,3,4,6,7,8,9],freq[0], freq[2047], linestyles='dashed', linewidth= 0.1, colors='grey')
         #,6,7,8,9,11,12,13,14,16,17,18,19]

        axes[1].set_xlabel('Minutes',fontsize=15)
        axes[1].set_ylabel('MHz',fontsize=15)
        plt.tick_params(axis='both', labelsize=15)
        cax = fig.add_axes([axes[1].get_position().x1+0.01,axes[1].get_position().y0,0.02,axes[1].get_position().height])
        plt.tick_params(axis='both', labelsize=15)
        plt.colorbar(graph, cax=cax)
        fig.set_size_inches(15,12)
        plt.savefig(name+'_log.png',dpi=1000)
        plt.close()

        del data, avg_pow, bases,flags,clip
        del fig, axes   ##maybe its faster to clean the canvas and keep the figure

        if(plot_misc):
            print("Making dedispersors plots")
            submisc = misc_names[i*log_per_img:(i+1)*log_per_img]
            dms, mov_avg = get_dm_data(submisc)

            tf = t[-1]
            DMs = [45,90,135]
            fig, axes = plt.subplots(3,1)
            for i in range(3):
                t = np.linspace(0,tf, len(dms[i][0]))
                axes[i].plot(t,dms[i][0])
                axes[i].plot(t, mov_avg[i][0])
                axes[0].set_title('Dedispersed power',fontsize=10)
                axes[0].set_ylabel('DM 45',fontsize=8)
                axes[1].set_ylabel('DM 90',fontsize=8)
                axes[2].set_ylabel('DM 135',fontsize=8)
                axes[i-1].set_xlabel('Minutes',fontsize=8)
                axes[i].grid()
            plt.savefig(name+'_dms.png', dpi=500)
            plt.show()
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
            plot_misc=args.plot_misc,
            plot_clip=args.plot_clip,
            decimation=args.decimation,
            mov_avg_size=args.mov_avg_size,
            tails=args.tails,
            img_folder=args.img_folder)

