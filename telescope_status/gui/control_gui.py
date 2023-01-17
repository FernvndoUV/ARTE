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
#sys.path.append('../../codes')
#import utils


class tab_class():
    def __init__(self, tab):
        self.tab = tab

class main_app():
    def __init__(self, top, roach_ip, server_ip, python2_interpreter):
        #connect to the roach
        self.roach = calan_python3(server_ip, roach_ip, python2_interpreter)
        time.sleep(1)
        ##
        tabControl = ttk.Notebook(top)
        tabs = []
        for i in range(TAB_NUMBER):
            tab = ttk.Frame(tabControl)
            tabs.append(tab)
            tabControl.add(tab, text=TAB_NAMES[i])
        tabControl.pack(expand=1, fill='both')
        self.antenna_spectrum(tabs[0])


    def antenna_spectrum(self, tab):
        ###
        ### Real time update?
        ###
        self.spect_tab = tab_class(tab)
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

        self.anim = FuncAnimation(self.spect_tab.fig, self.antenna_animation,
                                  interval=50, blit=True)
        #plt.show()
        return 0


    
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


    def animate(i):
        dat = utils.get_antenas(fpga)
        for i in range(4):
            spec = 10*np.log10(dat[i,:]+1)
            data[i].set_data(freq, spec)
        return data



if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('ARTE status')
    #note = ttk.Notebook(root)
    wind = main_app(root, ROACH_IP, SERVER_ADDR, PYTHON2_ENV)
    def closing():
        root.destroy()
        wind.roach.close()
    #root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", closing)
    root.mainloop()



