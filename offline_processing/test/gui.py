import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class main_app():
    
    def __init__(self, top):
        top.wm_title('matplotlib test')
        tabControl = ttk.Notebook(top)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)

        tabControl.add(tab1, text="General")
        tabControl.add(tab2, text="optional")
        tabControl.pack(expand=1, fill='both')

        frame = tk.Frame(tab2)
        frame.grid(row=0, column=0, pady=5, sticky='n')
        

        self.btn_folder = tk.Button(frame, 
                text="open folder")
        self.btn_folder.grid(row=0, column=0, padx=3, sticky='n')
        #self.btn_folder.bind('<Button-1>', self.folder_search)
        
        self.path = tk.Entry(frame)
        self.path.grid(row=0, column=1, padx=3, sticky='n')

        
        frame1 = tk.Frame(tab2)
        frame1.grid(row=0, column=1, pady=5) 



        fig, axes = plt.subplots(1,3)
        axes[0].plot(np.sin(np.arange(255)/255*2*np.pi*10))
        axes[0].plot(np.cos(np.arange(255)/255*2*np.pi*10))
        axes[0].grid()
        
        canvas = FigureCanvasTkAgg(fig, master=frame1)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, frame1)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        btn = tk.Button(tab1, text="asd")
        btn.grid(row=0, column=0)
        


if __name__ == '__main__':
    root = tk.Tk()
    wind = main_app(root)
    root.mainloop()



        
