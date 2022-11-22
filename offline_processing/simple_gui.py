import tkinter as tk
import tkinter.filedialog as fd
from tkinter import ttk
import os
from datetime import datetime
import subprocess, shlex
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from log_reduction import read_10gbe_data, get_baseline
from scipy.signal import savgol_filter, medfilt


CODE_PATH = os.getcwd()
CAL_TIME = 1
SPECT_TIME = 0.01
FILE_TIME = 5
TAILS = 32

class main_app():

    def __init__(self, top):
        top.wm_title('ARTE debug')
        
        tabControl = ttk.Notebook(top)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        
        tabControl.add(tab1, text="General")
        tabControl.add(tab3, text="Misc plots")
        tabControl.add(tab2, text="optional")
        tabControl.pack(expand=1, fill='both')

        frame0 = tk.Frame(tab1)
        frame0.grid(row=0, column=0, pady=5, sticky='n')

        self.btn_folder = tk.Button(frame0, 
                text="open folder")
        self.btn_folder.grid(row=0, column=0, padx=3, sticky='n')
        self.btn_folder.bind('<Button-1>', self.folder_search)
        
        self.path = tk.Entry(frame0)
        self.path.grid(row=0, column=1, padx=3, sticky='n')

        
        ###check how to force the date format
        frame1 = tk.Frame(tab1)
        frame1.grid(row=1, column=0, pady=5, sticky='n')
        lab = tk.Label(frame1, text='Start Time: ')
        lab.grid(row=0, column=0, padx=2, pady=3, sticky='n')
        

        self.tstart = tk.StringVar()
        self.ent_tstart = tk.Entry(frame1, textvariable=self.tstart, width=30)
        self.ent_tstart.grid(row=0, column=1, padx=2, pady=3,sticky='n')
        self.ent_tstart.bind('<Key>', self.time_formating_start)

        
        lab = tk.Label(frame1, text='Stop Time:')
        lab.grid(row=0, column=2, padx=2, pady=3,sticky='n')

        self.tstop = tk.StringVar()
        self.ent_tstop = tk.Entry(frame1,textvariable=self.tstop, width=30)
        self.ent_tstop.grid(row=0, column=3, padx=2, pady=3,sticky='n')
        self.ent_tstop.bind('<Key>', self.time_formating_stop)
        ##
        
        lab = tk.Label(frame1, text='Start Freq: ')
        lab.grid(row=1, column=0, padx=2, pady=3, sticky='n')

        self.ent_fstart = tk.Entry(frame1, width=30)
        self.ent_fstart.grid(row=1, column=1, padx=2, pady=3,sticky='n')
        self.ent_fstart.insert(0, "1200")
        
        lab = tk.Label(frame1, text='Stop Freq: ')
        lab.grid(row=1, column=2, padx=2, pady=3, sticky='n')

        self.ent_fstop = tk.Entry(frame1, width=30)
        self.ent_fstop.grid(row=1, column=3, padx=2, pady=3,sticky='n')
        self.ent_fstop.insert(0, "1800")
        
        ##
        frame2 = tk.Frame(tab1)
        frame2.grid(row=2, column=0, pady=5, sticky='n')
        self.temp = tk.BooleanVar()
        self.temp.set(1)
        check_temp = tk.Checkbutton(frame2, text="temperature", variable=self.temp)
        check_temp.grid(row=0,column=0, sticky='w')
        check_temp.bind('<Button-1>', self.temp_check)
        self.power = tk.BooleanVar()
        check_pow = tk.Checkbutton(frame2, text="Power dB", variable=self.power)
        check_pow.grid(row=0,column=1, sticky='w')
        check_pow.bind('<Button-1>', self.pow_check)
        
        self.base = tk.BooleanVar()
        self.check_base = tk.Checkbutton(frame2, text="Plot baseline", variable=self.base)
        self.check_base.grid(row=1, column=0, sticky='w')
        self.dm = tk.BooleanVar()
        self.check_dm = tk.Checkbutton(frame2, text="Plot dm", variable=self.dm)
        self.check_dm.grid(row=1, column=1, sticky='w')
        
        self.channel_evol = tk.BooleanVar()
        check_evol = tk.Checkbutton(frame2, text="Single channel", variable=self.channel_evol)
        check_evol.grid(row=2, column=0, sticky='w')
        check_evol.bind('<Button-1>', self.evol_check)

        self.spectra = tk.BooleanVar()
        check_spectra = tk.Checkbutton(frame2, text="single spectrun", variable=self.spectra)
        check_spectra.grid(row=2, column=1, sticky='w')
        check_spectra.bind('<Button-1>', self.spectra_check)

        ##### 
        frame3 = tk.Frame(tab1)
        frame3.grid(row=3, column=0, pady=5, sticky='n')
        self.btn_plot = tk.Button(frame3, 
                text="Generate plot")
        self.btn_plot.grid(row=0, column=0, padx=3, sticky='n')
        self.btn_plot.bind('<Button-1>', self.gen_plots)
        self.btn_plot.bind('Return', self.gen_plots)

        ###optional parameters
        frame1 = tk.Frame(tab2)
        frame1.grid(row=1, column=0, pady=5, sticky='n')
        lab = tk.Label(frame1, text='Code path: ')
        lab.grid(row=0, column=0, padx=2, pady=3, sticky='n')

        self.code_path = tk.Entry(frame1)
        self.code_path.grid(row=0, column=1, padx=2, pady=3,sticky='n')
        self.code_path.insert(0, str(CODE_PATH))

        lab = tk.Label(frame1, text='Cal time(s): ')
        lab.grid(row=1, column=0, padx=2, pady=3, sticky='n')
        self.cal_time = tk.Entry(frame1)
        self.cal_time.grid(row=1, column=1, padx=2, pady=3,sticky='n')
        self.cal_time.insert(0, str(CAL_TIME))
        
        lab = tk.Label(frame1, text='integration time: ')
        lab.grid(row=2, column=0, padx=2, pady=3, sticky='n')
        self.spect_time = tk.Entry(frame1)
        self.spect_time.grid(row=2, column=1, padx=2, pady=3,sticky='n')
        self.spect_time.insert(0, str(SPECT_TIME))

        
        lab = tk.Label(frame1, text='file time (min):')
        lab.grid(row=3, column=0, padx=2, pady=3, sticky='n')
        self.file_time = tk.Entry(frame1)
        self.file_time.grid(row=3, column=1, padx=2, pady=3,sticky='n')
        self.file_time.insert(0, str(FILE_TIME))

        ###matploltib plots
        self.matflag = None
        frame_plots = tk.Frame(tab3)
        frame_plots.grid(row=0, column=0, padx=5, sticky='n')
        #frame_plots.pack(side=tk.TOP)

        fig, axes = plt.subplots(3,1, sharex=True)
        self.axes = axes
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=frame_plots)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_plots)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        for i in range(3):
            axes[i].grid()
        axes[0].set_title('temperature')
        axes[1].set_title('Power')
        axes[2].set_title('Linear')

        frame3_0 = tk.Frame(tab3)
        frame3_0.grid(row=1, column=0, pady=5, sticky='n')
        #frame3_0.pack(side=tk.TOP)

        self.btn_folder2 = tk.Button(frame3_0, 
                text="open folder")
        self.btn_folder2.grid(row=0, column=0, padx=3, sticky='n')
        self.btn_folder2.bind('<Button-1>', self.folder_search)
        
        self.path2 = tk.Entry(frame3_0)
        self.path2.grid(row=0, column=1, padx=5, sticky='n')

        frame3_1 = tk.Frame(tab3)
        frame3_1.grid(row=2, column=0, pady=5, sticky='n')
        #frame3_1.pack(side=tk.TOP)
        lab = tk.Label(frame3_1, text='Time:')
        lab.grid(row=0, column=0, padx=5, pady=3, sticky='n')
        
        self.t_matplot = tk.StringVar()
        self.ent_matplot = tk.Entry(frame3_1, textvariable=self.t_matplot, width=30)
        self.ent_matplot.grid(row=0, column=1, padx=2, pady=3,sticky='n')
        self.ent_matplot.bind('<Key>', self.time_formating_matplot)


        self.btn_matplot = tk.Button(frame3_0, 
                text="Generate plot")
        self.btn_matplot.grid(row=0, column=2, padx=40, sticky='n')
        self.btn_matplot.bind('<Button-1>', self.gen_matplot)
        self.btn_matplot.bind('Return', self.gen_matplot)
        
        self.btn_clean = tk.Button(frame3_1, 
                text="Clean plot")
        self.btn_clean.grid(row=0, column=2, padx=40, sticky='n')
        self.btn_clean.bind('<Button-1>', self.clean_matplot)
        self.btn_clean.bind('Return', self.clean_matplot)

        
        
    def gen_plots(self, event):
        folder_name = self.path.get()
        start_t = self.ent_tstart.get()
        stop_t = self.ent_tstop.get()
        start_f = self.ent_fstart.get()
        stop_f = self.ent_fstop.get()
        cal_time = self.cal_time.get()
        file_time = self.file_time.get()
        spect_time = self.spect_time.get()
        power = self.power.get()
        base = self.base.get()
        dm = self.dm.get()
        if(self.spectra.get()):
            stop_t = None
        elif(self.channel_evol.get()):
            stop_f = -1

        code_path = os.path.join(str(self.code_path.get()), "zoom_plot.py" )
        msg = "python3 "+str(code_path)
        msg += " --folder_name "+str(folder_name)
        msg += " --start "+str(start_t)
        if(stop_t is not None):
            msg += " --stop "+str(stop_t)
        msg += " --startf "+str(start_f)
        msg += " --stopf "+str(stop_f)
        msg += " --cal_time "+str(cal_time)
        msg += " --file_time "+str(file_time)
        msg += " --spect_time "+str(spect_time)
        msg += " --tails "+str(TAILS)
        if(power):
            msg += ' --power'
        if(base):
            msg += ' --base'
        if(dm):
            msg += ' --plot_dm'
        print(msg)
        #os.system(msg)
        subprocess.Popen(shlex.split(msg))
        return 1
          

    def gen_matplot(self, event):
        ##now I need to get the damn data... and because its a new requirement I
        ##cant reuse my codes...
        
        folder_name = self.path.get()
        folder_name = os.path.join(folder_name, 'logs')
        start = self.ent_matplot.get()
        cal_time = float(self.cal_time.get())
        file_time = float(self.file_time.get())
        spect_time = float(self.spect_time.get())
        
        dirs_name = os.listdir(folder_name)
        dirs_name.sort()
        dirs = [os.path.join(folder_name, x) for x in dirs_name]
        
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
        
        logs = dirs[start_ind]
        
        sample = read_10gbe_data(logs)
        sample_spect, header = sample.get_complete()
        sample.close_file()

        hot_source = sample_spect[2:int(cal_time/spect_time*3),:]
        hot_pow = np.sum(hot_source, axis=1)
        hot_pow = medfilt(hot_pow, 5)
        thresh = (np.max(hot_pow)+np.min(hot_pow))/2
        index = (hot_pow>thresh)
        flags, baseline = get_baseline(np.median(hot_source[index,:],axis=0))
        
        temp_data = np.zeros(sample_spect.shape)
        temp_data[:,flags] = sample_spect[:, flags]*280./baseline[flags]-90
        
        t_sec = np.arange(temp_data.shape[0])*spect_time
        start_t = np.argmin(np.abs(t_sec-start_sec))

        freq = np.linspace(1200,1800,2048, endpoint=False)
        self.axes[0].plot(freq, temp_data[start_t,:])
        self.axes[1].plot(freq,10*np.log10(sample_spect[start_t,:]))
        self.axes[2].plot(freq,sample_spect[start_t,:], label='data')
        if(self.matflag is None):
            self.axes[2].plot(freq,baseline, label='baseline', color='black')
            self.axes[2].legend()
        self.matflag = 1 
        self.canvas.draw()
        return 1
    
    def clean_matplot(self, event):
        for i in range(3):
            self.axes[i].clear()
            self.axes[i].grid()
        self.canvas.draw()
        self.matflag = None
        return 1
        

    def folder_search(self, event):
        path = fd.askdirectory()
        self.path.delete(0, tk.END)
        self.path.insert(0,path)
        self.path2.delete(0, tk.END)
        self.path2.insert(0,path)
        return 1
    
    def folder_search_matplot(self, event):
        path = fd.askdirectory()
        self.path_2.delete(0, tk.END)
        self.path_2.insert(0,path)
        return 1

    def temp_check(self, event):
        self.power.set(not self.temp)
        self.check_base.configure(state="active")

    def pow_check(self, event):
        self.temp.set(not self.power)
        self.base.set(False)
        self.check_base.configure(state="disable")

    def evol_check(self, event):
        if(not self.channel_evol.get()):
            self.ent_fstop.configure(state='disable')
            self.spectra.set(False)
            self.ent_tstop.configure(state='normal')
        else:
            self.ent_fstop.configure(state='normal')
    
    def spectra_check(self, event):
        if(not self.spectra.get()):
            self.ent_tstop.configure(state='disable')
            self.channel_evol.set(False)
            self.ent_fstop.configure(state='normal')
        else:
            self.ent_tstop.configure(state='normal')
 
         
    def time_formating_start(self, event):
        cur_date = self.tstart.get()
        if((event.keysym !="backspace" ) & (event.keysym in 
            ["0","1","2","3","4","5","6","7","8","9"]) ):
            #check that its a number
            if(len(cur_date) in [4,7,10]):
                self.ent_tstart.insert(tk.END,'/')
            elif(len(cur_date) in [13,16,19]):
                self.ent_tstart.insert(tk.END,':')
       
        
    def time_formating_stop(self, event):
        cur_date = self.tstop.get()
        if((event.keysym !="backspace" ) & (event.keysym in 
            ["0","1","2","3","4","5","6","7","8","9"]) ):
            #check that its a number
            if(len(cur_date) in [4,7,10]):
                self.ent_tstop.insert(tk.END,'/')
            elif(len(cur_date) in [13,16,19]):
                self.ent_tstop.insert(tk.END,':')

    def time_formating_matplot(self, event):
        cur_date = self.t_matplot.get()
        if((event.keysym !="backspace" ) & (event.keysym in 
            ["0","1","2","3","4","5","6","7","8","9"]) ):
            #check that its a number
            if(len(cur_date) in [4,7,10]):
                self.ent_matplot.insert(tk.END,'/')
            elif(len(cur_date) in [13,16,19]):
                self.ent_matplot.insert(tk.END,':')

if __name__ == '__main__':
    root = tk.Tk()
    wind = main_app(root)
    #root.resizable(False, False)
    root.mainloop()
