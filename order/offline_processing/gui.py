import matplotlib 
matplotlib.use('TkAgg')
import tkinter as tk
import tkinter.filedialog as fd
from tkinter import ttk
import os
import subprocess, shlex
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


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
    
        ##misc plots
        fig, axes = plt.subplots(1,3)

        
        for i in range(3):
            axes[i].grid()
        canvas = FigureCanvasTkAgg(fig, master=tab3)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, tab3)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)




        
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
          

        

    def folder_search(self, event):
        path = fd.askdirectory()
        self.path.delete(0, tk.END)
        self.path.insert(0,path)
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


if __name__ == '__main__':
    root = tk.Tk()
    wind = main_app(root)
    #root.resizable(False, False)
    root.mainloop()
