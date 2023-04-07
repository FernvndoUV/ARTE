import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from utils import *
import os, sys, yaml, argparse
import gc

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder_name", dest="folder_name", default=None)
parser.add_argument("-l", "--log_per_img", dest="log_per_img", default=1, type=int)
parser.add_argument("-c", "--cal_time", dest="cal_time", default=1, type=float)
parser.add_argument("-ft", "--file_time", dest="file_time", default=1, type=float)
parser.add_argument("-st", "--spect_time", dest="spect_time", default=1e-2)
parser.add_argument("-d", "--decimation", dest="decimation", default=1, type=int)
parser.add_argument("-w", "--avg_win", dest="mov_avg_size", default=100, type=int)
parser.add_argument("-t", "--tails", dest="tails", default=32, type=int)
parser.add_argument("-i", "--img_folder", dest="img_folder", type=str)
parser.add_argument("-m", "--plot_misc", dest="plot_misc", action="store_true")
parser.add_argument("-pc", "--plot_clip", dest="plot_clip", action="store_true")


def plot_folder(folder_name, log_per_img=1, cal_time=1, file_time=2,spect_time=1e-2,
        plot_misc=True, decimation=1, mov_avg_size=32, tails=32, img_folder="log_img",
                plot_clip=True):
    """
    folder_name:    Folder to plot. It should have the folders logs and misc inside
    log_per_img:    How many logs to plot in one image
    cal_time:       Calibration time in seconds (set by logger.py when generating the log)
    file_time:      Time saved in one file (set by logger.py when generating the log)
    spect_time:     Time between sucessive spectrums (set by logger.py when generating the log)
    plot_misc:      if True, plot the misc data
    decimation:     How much to downsample the image in the time domain.
    mov_avg_size:   Mov average window size used in the total power curve
    tails:          Spectras that we lost at the end of the file 
    img_folder:     Where to store the resulting images
    plot_clip:      if True, plot the clip curves over the total power
    """
    #create the folders if doesnt exist
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
        data, avg_pow, clips, t, bases,flags = get_log_data(sublogs,cal_time, spect_time,
                file_time, decimation, mov_avg_size, tails)
        hr_i= sublogs[0].split('/')[-1].split('.')[0]
        hr_f= sublogs[-1].split('/')[-1].split('.')[0]

        name = os.path.join(img_folder,  hr_i+'_to_'+hr_f)
        print('Making 10Gbe plot')
        fig, axes = plt.subplots(2,1, sharex=True, gridspec_kw={'height_ratios': [0.15,0.85]})
        axes[0].set_title('Average power',fontsize=20)
        axes[0].plot(t,avg_pow,linewidth=1.5)
        axes[0].axis(ymin =  np.mean(avg_pow)-5 , ymax = np.mean(avg_pow)+5 )
        axes[0].vlines([1,2,3,4],  np.mean(avg_pow)-5 ,np.mean(avg_pow)+5 , linestyles='dashed',linewidth= 0.1, colors='grey')
        axes[0].grid()
        axes[0].set_ylabel('Temperature K',fontsize=15)
        axes[0].tick_params(axis= 'y', labelsize=15)


        if(plot_clip):
            colors = ['r', 'blue','black']
            for i in range(2,-1,-1):
                clip = clips[i]
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
                    axes[0].axvspan(t[up], t[down], color=colors[i], alpha=0.5, lw=0)

        graph = axes[1].pcolormesh(t,freq , data[:len(t),::].T, cmap = 'viridis',vmax = 290,vmin =  200,shading='auto' )

        axes[1].vlines([1,2,3,4],freq[0], freq[2047], linestyles='dashed', linewidth= 0.1, colors='grey')
        axes[1].set_xlabel('Minutes',fontsize=15)
        axes[1].set_ylabel('MHz',fontsize=15)
        plt.tick_params(axis='both', labelsize=15)
        cax = fig.add_axes([axes[1].get_position().x1+0.01,axes[1].get_position().y0,0.02,axes[1].get_position().height])
        plt.tick_params(axis='both', labelsize=15)
        plt.colorbar(graph, cax=cax)
        fig.set_size_inches(15,12)
        plt.savefig(name+'_log.png',dpi=1000)
        plt.close()

        if(plot_clip):
            del clip
        del data, avg_pow, bases,flags
        del fig, axes   ##maybe its faster to clean the canvas and keep the figure
        gc.collect()

        if(plot_misc):
            print("Making dedispersors plots")
            submisc = misc_names[i*log_per_img:(i+1)*log_per_img]
            dms, mov_avg = get_dm_data(submisc)

            tf = t[-1]
            fig, axes = plt.subplots(11,1, sharex=True)
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
            gc.collect()


if __name__ == '__main__':
    if( not (len(sys.argv)>1)):
        #no argument, so use the config file to get the parameters
        f = open('configuration.yml', 'r')
        config = yaml.load(f, Loader=yaml.loader.SafeLoader)
        f.close()
        plot_folder(
                folder_name=config['log_info']['read_folder'],
                log_per_img=config['log_info']['log_per_img'],
                cal_time=config['tengbe_log']['calibration_time'],
                file_time=config['tengbe_log']['filetime'],
                spect_time=config['tengbe_log']['log_time']*1e-3,
                plot_misc=config['log_info']['plot_misc'],
                plot_clip=config['log_info']['plot_clip'],
                decimation=config['log_info']['decimation'],
                mov_avg_size=config['log_info']['mov_avg_size'],
                tails=config['log_info']['tails'],
                img_folder=config['log_info']['img_folder']
                )
    else:
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
                img_folder=args.img_folder
                )
            
