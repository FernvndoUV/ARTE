from utils import get_log_data, get_dm_data
import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.signal import savgol_filter, medfilt
import ipdb 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder_name", dest="folder_name", default=None)
parser.add_argument("-sta", "--start", dest="start", default=None,
        help="starting time, with format Y/M/D/H/MIN/S/microS")
parser.add_argument("-sto", "--stop", dest="stop", default=None,
        help="stop time, with format Y/M/D/H:MIN:S:microS")

parser.add_argument("-staf", "--startf", dest="start_freq", default=1200,
        help="start frequency to plot ", type=float)
parser.add_argument("-stof", "--stopf", dest="stop_freq", default=1800,
        help="stop frequency to plot ", type=float)
parser.add_argument("-c", "--cal_time", dest="cal_time", default=1, type=float)
parser.add_argument("-ft", "--file_time", dest="file_time", default=5, type=float)
parser.add_argument("-st", "--spect_time", dest="spect_time", default=1e-2, type=float)
parser.add_argument("-d", "--decimation", dest="decimation", default=1, type=int)
parser.add_argument("-w", "--avg_win", dest="mov_avg_size", default=100, type=int)
parser.add_argument("-t", "--tails", dest="tails", default=32, type=int)

parser.add_argument("-pow", "--power", dest="power", action="store_true")
parser.add_argument("-base", "--baseline", dest="baseline", action="store_true")

parser.add_argument("-dm", "--plot_dm", dest="plot_dm", action="store_true")


def zoom_plot(folder_name, start, stop=None,
            start_freq=1200, stop_freq=1800,
            cal_time=1,
            spect_time=1e-2,
            file_time=5,
            decimation=1,
            mov_avg_size=100,
            tails=32,
            temperature=True,
            plot_baseline=False):
    """
    folder_name : folder where are the logs
    start       : start time to look at in th format Year/month/day/hour:min:sec:microsec
                  eg: 2022/10/05/19:18:0:100
    stop        : stop time to look, if its None plot the spectra at the start time.
    start_freq  : start frequncy to look at
    stop_freq   : stop frequency to look at, if its negative the function plot the
                  start_freq channel evolution in time
    cal_time    : calibration time at the begining of the measure
    spect_time  : period between two sucesive spectrums
    file_time   : time saved in each file
    decimation  : downsampling the data accumulating
    mov_avg_size: mov avg window for the accumulated power (non implemented here)
    tails       : discard last frames to keep sizes
    temperature : if False plot the power instead the temperature (not implemented yet)
    """
    if(temperature):
        unit = "K"
    else:
        unit = "dB"

    dirs_name = os.listdir(folder_name)
    dirs_name.sort()
    dirs = [os.path.join(folder_name, x) for x in dirs_name]

    ##search for the starting file and starting index of the desired start
    start = datetime.strptime(start, "%Y/%m/%d/%H:%M:%S:%f")
    date = datetime.strptime(dirs_name[-1].split('.')[0], "%Y-%m-%d %H:%M:%S")
    if(start>date):
        start_ind = len(dirs_name)-1
    else:
        for i in range(len(dirs_name)):
            date = datetime.strptime(dirs_name[i].split('.')[0], "%Y-%m-%d %H:%M:%S")
            if(date>start):
                break
        if((i==0)):
            start_ind = i
        else:
            start_ind = i-1

    date = datetime.strptime(dirs_name[start_ind].split('.')[0], "%Y-%m-%d %H:%M:%S")
    start_sec = (start-date).total_seconds()
    
    ##in this case we plot just one spectrum
    if(stop is None):
        logs = [dirs[start_ind]]
        data, avg_pow, clip, t, bases,flags = get_log_data(
                logs,
                cal_time=cal_time, 
                spect_time=spect_time,
                file_time=file_time, 
                decimation=decimation, 
                win_size=mov_avg_size,
                tails=tails,
                temperature=temperature)
        t_sec = t*60
        freq = np.linspace(1200,1800, 2048, endpoint=False)

        start_t = np.argmin(np.abs(t_sec-start_sec))
        f_i = np.argmin(np.abs(freq-start_freq))
        f_e = np.argmin(np.abs(freq-stop_freq))
        
        if(plot_baseline):
            for i in range(bases.shape[0]):
                plt.plot(freq[f_i:f_e], bases[i,f_i:f_e], label=('base %i'%i))
                plt.title('Baseline')
                plt.xlabel('MHz')
                plt.legend()
                plt.grid()

            aux = data/380*np.median(bases, axis=0)
            plt.plot(freq[f_i:f_e], np.max(aux[200:,f_i:f_e], axis=0), label='max')
            plt.plot(freq[f_i:f_e], np.min(aux[200:,f_i:f_e], axis=0), label='min')
            plt.plot(freq[f_i:f_e], np.median(aux[200:,f_i:f_e], axis=0), label='median')
            plt.plot(freq[f_i:f_e], np.mean(aux[200:,f_i:f_e], axis=0), label='avg')
            plt.legend()
        plt.figure()
        plt.plot(freq[f_i:f_e], data[start_t,f_i:f_e])
        plt.grid()
        plt.xlabel('MHz')
        plt.ylabel(unit)
        return start_ind, start_ind+1, start_sec, -1, -1 
    
    ##search stop file
    stop = datetime.strptime(stop, "%Y/%m/%d/%H:%M:%S:%f")

    date = datetime.strptime(dirs_name[-1].split('.')[0], "%Y-%m-%d %H:%M:%S")
    if(stop>date):
        stop_ind = len(dirs_name)-1
    else:
        for i in range(len(dirs_name)):
            date = datetime.strptime(dirs_name[i].split('.')[0], "%Y-%m-%d %H:%M:%S")
            if(date>stop):
                break
        if(i==0):
            stop_ind = i
        else:
            stop_ind = i-1
    date = datetime.strptime(dirs_name[start_ind].split('.')[0], "%Y-%m-%d %H:%M:%S")
    stop_sec = (stop-date).total_seconds()

    ##handle when the starting and stoping log is the same one
    if(start_ind==stop_ind):
        logs = [dirs[start_ind]]
    else:
        logs = dirs[start_ind:stop_ind+1]
    print(logs)
    ##get data 
    data, avg_pow, clip, t, bases,flags = get_log_data(
            logs,
            cal_time=cal_time,
            spect_time=spect_time,
            file_time=file_time,
            decimation=decimation,
            win_size=mov_avg_size,
            tails=tails,
            temperature=temperature)
    t_sec = t*60
    freq = np.linspace(1200,1800, 2048, endpoint=False)


    start_t = np.argmin(np.abs(t_sec-start_sec))
    stop_t = np.argmin(np.abs(t_sec-stop_sec))
    f_i = np.argmin(np.abs(freq-start_freq))
    if(stop_freq<0):
        plt.plot(t[start_t:stop_t], data[start_t:stop_t, f_i])
        plt.xlabel('min')
        plt.ylabel(unit)
        plt.title('%f MHz channel'%freq[f_i])
        plt.grid()
        return start_ind, stop_ind, start_sec, stop_sec, t[-1]

    f_e = np.argmin(np.abs(freq-stop_freq))
    if(plot_baseline):
        for i in range(bases.shape[0]):
            plt.plot(freq[f_i:f_e], bases[i,f_i:f_e])
            plt.xlabel('MHz')
            plt.grid()
        ##I DONT LIKE THIS ONE!
        aux = data/380*np.median(base, axis=0)
        plt.plot(freq[f_i:f_e], np.max(aux[200:,f_i:f_e], axis=0), label='max')
        plt.plot(freq[f_i:f_e], np.min(aux[200:,f_i:f_e], axis=0), label='min')
        plt.plot(freq[f_i:f_e], np.median(aux[200:,f_i:f_e], axis=0), label='median')
        plt.plot(freq[f_i:f_e], np.mean(aux[200:,f_i:f_e], axis=0), label='avg')
        plt.legend()
    plt.figure()
    if(temperature):
        plt.pcolormesh(t[start_t:stop_t], freq[f_i:f_e] , 
                data[start_t:stop_t,f_i:f_e].T, cmap = 'viridis',
                vmax = 290,vmin =  200,shading='auto' )
    else:
        plt.pcolormesh(t[start_t:stop_t], freq[f_i:f_e] , 
                data[start_t:stop_t,f_i:f_e].T, cmap = 'viridis')
    plt.xlabel('minutes')
    plt.ylabel('MHz')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel(unit)
    #plt.show()
    return start_ind, stop_ind, start_sec, stop_sec, t[-1]
 
if __name__ == '__main__':
    args = parser.parse_args()
    log_folder = os.path.join(args.folder_name, 'logs')
    start_ind, stop_ind, t_start, t_stop, t_total = zoom_plot(folder_name=log_folder,
            start=args.start,
            stop=args.stop,
            start_freq=args.start_freq,
            stop_freq=args.stop_freq,
            cal_time=args.cal_time,
            spect_time=args.spect_time,
            file_time=args.file_time,
            decimation=args.decimation,
            mov_avg_size=args.mov_avg_size,
            tails=args.tails,
            temperature=(not args.power),
            plot_baseline=args.baseline)
    print(t_total)
    if(args.plot_dm):
        misc_folder = os.path.join(args.folder_name, 'misc')
        dirs_name = os.listdir(misc_folder)
        dirs_name.sort()
        #to match the requirement of the function
        dirs_name = [os.path.join(misc_folder, x.split('.npz')[0]) for x in dirs_name]
        dms, mov_avg = get_dm_data(dirs_name[start_ind:stop_ind+1])

        tf = t_total
        fig, axes = plt.subplots(11,1, sharex=True)
        for i in range(11):
            t = np.linspace(0,tf, len(dms[i][0]))
            t_sec = t*60
            start_t = np.argmin(np.abs(t_sec-t_start))
            stop_t = np.argmin(np.abs(t_sec-t_stop))
            axes[i].plot(t[start_t:stop_t],dms[i][0][start_t:stop_t])
            axes[i].plot(t[start_t:stop_t], mov_avg[i][0][start_t:stop_t])
            axes[i].grid()

    plt.show()

