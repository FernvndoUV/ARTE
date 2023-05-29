import tkinter as tk

def btn_handler(event):
    print(event)


top = tk.Tk()

frame0 = tk.Frame(top)
frame0.grid(row=0, column=0, pady=5)

lab = tk.Label(frame0, text='folder name')
lab.grid(row=0, column=0, padx=2)

ent_start = tk.Entry(frame0)
ent_start.grid(row=0, column=1, padx=2)
#ent_start.pack(side=tk.RIGHT)



last_frame = tk.Frame(top)
last_frame.grid(row=1, column=0, pady=5)

btn_plots = tk.Button(
    last_frame,
    text="Generate plots"
        )
btn_plots.grid(row=0, column=0, sticky='n')
btn_plots.bind('<Button-1>', btn_handler)

top.mainloop()
