from config import *
import matplotlib 
matplotlib.use('TkAgg')
import tkinter as tk
from tkinter import ttk
import os, time, sys
import subprocess, shlex
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2T
from calan_python3 import calan_python3 
from matplotlib.animation import FuncAnimation
import multiprocessing
import read_sensors_v3
#sys.path.append('../../codes')
#import utils

class tab_class():
    def __init__(self, tab):
        self.tab = tab

class main_app():
    def __init__(self, top, roach_ip, server_ip, python2_interpreter):
        #connect to the roach
        self.roach = calan_python3(server_ip, roach_ip, python2_interpreter)
        self.tn = read_sensors_v3.roach_connect(roach_ip, debug=DEBUG)   ##telnet connection
        time.sleep(1)
        ##
        tabControl = ttk.Notebook(top)
        tabs = []
        for i in range(TAB_NUMBER):
            tab = ttk.Frame(tabControl)
            tabs.append(tab)
            tabControl.add(tab, text=TAB_NAMES[i])
        tabControl.pack(expand=1, fill='both')
        #tabControl.bind("<<NotebookTabChanged>>", self.tab_selected)
        self.antenna_spectrum(tabs[0])
        self.beam_spectrum(tabs[1])
        self.adc_inputs(tabs[2])
        self.temperature_tab(tabs[3])
        
        self.temp_proc = multiprocessing.Process(target=self.get_temperature)
        self.temp_proc.start()

    def tab_selected(self, event):
        """
        Handle the update of the opened tab and halt the other tab animations
        """
        sel_tab = event.widget.select()
        tab_text = event.widget.tab(sel_tab, 'text')
        print(tab_text)
        if(tab_text==TAB_NAMES[0]):
            if('self.beam_tab.anim' in locals()):
                self.beam_tab.anim.pause()

            if('self.adc_tab.anim' in locals()):
                self.adc_tab.anim.pause()
            ###
            if('self.spect_tab.anim' in locals()):
                self.spect_tab.anim.resume()
            else:
                self.spect_tab.anim = FuncAnimation(self.spect_tab.fig, self.antenna_animation,
                                                    interval=50, blit=True)
        elif(tab_text == TAB_NAMES[1]):
            self.spect_tab.anim.pause()
            if('self.adc_tab.anim' in locals()):
                self.adc_tab.anim.pause()
            
            if('self.beam_tab.anim' in locals()):
                self.beam_tab.anim.resume()
            else:
                self.beam_tab.anim = FuncAnimation(self.beam_tab.fig, self.beam_animation,
                                                    interval=50, blit=True)
        elif(tab_text == TAB_NAMES[2]):
            self.spect_tab.anim.pause()
            if('self.beam_tab.anim' in locals()):
                self.beam_tab.anim.pause()

            if('self.adc_tab.anim' in locals()):
                self.adc_tab.anim.resume()
            else:
                self.adc_tab.anim =  FuncAnimation(self.beam_tab.fig, self.adc_animation,
                                                    interval=50, blit=True)
        else:
            if('self.beam_tab.anim' in locals()):
                self.beam_tab.anim.pause()

            if('self.adc_tab.anim' in locals()):
                self.adc_tab.anim.pause()

            if('self.spect_tab.anim' in locals()):
                self.spect_tab.anim.pause()

    def antenna_spectrum(self, tab):
        y_lim = (0,100)
        self.spect_tab = tab_class(tab)
        self.spect_tab.freq = np.linspace(1200,1800,2048,endpoint=False)
        self.spect_tab.fig, self.spect_tab.axes = plt.subplots(2,2)
        self.spect_tab.data = []

        canvas = FigureCanvasTkAgg(self.spect_tab.fig, tab)
        for i in range(2):
            for j in range(2):
                self.spect_tab.axes[i,j].set_ylim(y_lim)
                self.spect_tab.axes[i,j].set_xlim(1200,1800)
                self.spect_tab.axes[i,j].set_title('Antenna %i' %(i+j))
                self.spect_tab.axes[i,j].grid()
                line, = self.spect_tab.axes[i,j].plot([],[])
                self.spect_tab.data.append(line)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.spect_tab.canvas = canvas
        return 0

    def beam_spectrum(self, tab):
        y_lim = (0,100)
        self.beam_tab = tab_class(tab)
        self.beam_tab.freq = np.linspace(1200,1800,2048,endpoint=False)
        self.beam_tab.fig, self.beam_tab.axes = plt.subplots(1)
        self.beam_tab.data = []
        canvas = FigureCanvasTkAgg(self.beam_tab.fig, tab)
        self.beam_tab.axes.set_ylim(y_lim)
        self.beam_tab.axes.set_xlim(1200,1800)
        self.beam_tab.axes.set_title('Beam')
        self.beam_tab.axes.grid()
        line, = self.beam_tab.axes.plot([],[])
        self.beam_tab.data.append(line)
    
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.beam_tab.canvas = canvas
        return 0
    
    def adc_inputs(self, tab):
        y_lim = (-130,130)
        self.adc_tab = tab_class(tab)
        self.adc_tab.x = np.arange(ADC_SAMPLES)  ##check!
        self.adc_tab.fig, self.adc_tab.axes = plt.subplots(2,2)
        self.adc_tab.data = []

        canvas = FigureCanvasTkAgg(self.adc_tab.fig, tab)
        for i in range(2):
            for j in range(2):
                self.adc_tab.axes[i,j].set_ylim(y_lim)
                self.adc_tab.axes[i,j].set_xlim(0,self.adc_tab.x[-1])
                self.adc_tab.axes[i,j].set_title('Antenna %i' %(i+j))
                self.adc_tab.axes[i,j].grid()
                line, = self.adc_tab.axes[i,j].plot([],[])
                self.adc_tab.data.append(line)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.adc_tab.canvas = canvas
        return 0

    def temperature_tab(self, tab):
        """
        """
        self.temp_tab = tab_class(tab)
        
        ###roach_sensors
        self.temp_tab.text = []
        self.temp_tab.vars = []
        sensors_names = [
            'ambient temperature', 'ppc temperature', 'fpga temperature', 'inlet temperature',
            'outlet temperature', '1V', '1.5V', '1.8V', '2.5V', '3.3V', '5V', '12V',
            '3.3V (2)', '5V (2)', '3.3V current', '2.5V current', '3.3V current',
            '2.5V current', '1.8V current', '1.5V current', '1V current', '5V current',
            '12V current']
        for i in range(len(sensors_names)//2):
            name = sensors_names[2*i]
            text = tk.Label(self.temp_tab.tab, text=name+' :')
            text.grid(row=i, column=0, padx=2, pady=3, sticky='n')
            var = tk.StringVar(value='0.1')
            self.temp_tab.vars.append(var)
            #label = tk.Label(self.temp_tab.tab, textvariable=self.temp_tab.vars[-1], background='white', width=20)
            label = tk.Label(self.temp_tab.tab, text="0.1", background='white', width=20)
            label.grid(row=i, column=1, padx=2, pady=3, sticky='n')
            self.temp_tab.text.append(label)

            name = sensors_names[2*i+1]
            text = tk.Label(self.temp_tab.tab, text=name+' :')
            text.grid(row=i, column=2, padx=10, pady=3, sticky='n')
            var = tk.StringVar(value='0.1')
            self.temp_tab.vars.append(var)
            #label = tk.Label(self.temp_tab.tab, textvariable=self.temp_tab.vars[-1], background='white',width=20)
            label = tk.Label(self.temp_tab.tab, text="0.1", background='white',width=20)
            label.grid(row=i, column=3, padx=2, pady=3, sticky='n')
            self.temp_tab.text.append(label)

        


    ### 
    ### antennas animation functions
    ###
    def antenna_animation(self,i):
        dat = self.get_roach_antennas()
        for i in range(4):
            spec = 10*np.log10(dat[i,:]+1)
            self.spect_tab.data[i].set_data(self.spect_tab.freq, spec)
            #data = self.spect_tab.data
        return self.spect_tab.data

    def get_roach_antennas(self, dwidth=32, dtype=">I"):
        ###
        ### 
        ###
        brams = ['antenna_0','antenna_1', 'antenna_2', 'antenna_3']
        antenas = np.zeros([4, 2048])
        for i in range(len(brams)):
            antenas[i,:] =  self.roach.read_data(brams[i], awidth=11,dwidth=dwidth,dtype=dtype)
        return antenas
    
    ###
    ### beam animation functions
    ###
    
    def beam_animation(self, i):
        beam = self.roach.read_data('beam', awidth=11, dwidth=32, dtype='>I')
        beam = 10.*np.log10(beam+1)
        self.beam_tab.data[0].set_data(self.beam_tab.freq, beam)
        return self.beam_tab.data
    
    ###
    ### ADC inputs animation functions
    ###
    
    def adc_animation(self,i):
        ##CHECK the names!!!
        dat = self.get_adc_samples()
        for i in range(4):
            self.adc_tab.data[i].set_data(self.adc_tab.x, dat)
            #data = self.spect_tab.data
        return self.adc_tab.data
          

    def get_adc_samples(self):
        snaps = ['adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3']
        samples = self.roach.read_snapshots(snaps, ADC_SAMPLES, dtype='>i1')
        return samples
        
    ###
    ### Temperature monitor
    ###
    def get_temperature(self):
        start = time.time()
        try:
            while(1):
                val = time.time()-start
                #print(val)
                if(val> SENSOR_TIMESTEP):
                    sensor_vals = read_sensors_v3.read_all_sensors('qwe',self.tn)
                    print("update sensors")
                    for vr in self.temp_tab.vars:
                        print(vr.get())

                    for i,var in zip(range(len(sensor_vals)),sensor_vals):
                        print(i)
                        #self.temp_tab.vars[i].set(str(var))
                        self.temp_tab.text[i].configure(text=str(var))
                    start = time.time()
        finally:
            print('Killing sensor read process')
            self.tn.close()


                    
                        
                




if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('ARTE status')
    #note = ttk.Notebook(root)
    wind = main_app(root, ROACH_IP, SERVER_ADDR, PYTHON2_ENV)
    def closing():
        root.destroy()
        wind.roach.close()
        wind.temp_proc.kill()
    #root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", closing)
    root.mainloop()



