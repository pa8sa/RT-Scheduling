import tkinter as tk
from tkinter import ttk
import globals

def show_gui():
    root = tk.Tk()
    root.title("Scheduling")
    root.geometry("1200x600")
    root.configure(bg='#2d2d2d')
    
    style = ttk.Style()
    style.theme_use('clam')
    
    bg_color = '#2d2d2d'
    fg_color = '#ffffff'
    frame_bg = '#3d3d3d'
    accent_color = '#4a9cff'
    
    style.configure('.', background=bg_color, foreground=fg_color, font=('Helvetica', 10))
    style.configure('TFrame', background=frame_bg)
    style.configure('TLabel', background=frame_bg, foreground=fg_color)
    style.configure('TLabelFrame', background=frame_bg, foreground=accent_color)
    style.configure('TScale', background=bg_color)
    style.configure('Vertical.TScrollbar', background=frame_bg, troughcolor=bg_color)
    style.map('TScale', background=[('active', frame_bg)])

    current_time = tk.IntVar(value=0)
    
    control_frame = ttk.Frame(root, padding=10)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(control_frame, text="Time Unit:", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, padx=10)
    slider = ttk.Scale(control_frame, from_=0, to=len(globals.time_units_data)+1,
                      variable=current_time, orient="horizontal", length=600)
    slider.pack(side=tk.LEFT, padx=10, expand=True)
    time_label = ttk.Label(control_frame, text="0", width=4, font=('Helvetica', 12, 'bold'))
    time_label.pack(side=tk.LEFT, padx=10)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    sub_frames = []
    for i in range(4):
        row = i // 2
        col = i % 2
        frame = ttk.LabelFrame(main_frame, text=f"Subsystem {i+1}", padding=10)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        frame.grid_propagate(False)
        sub_frames.append(frame)
    
    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    def update_display(_=None):
        time_idx = current_time.get()
        time_label.config(text=str(time_idx))
        
        for frame in sub_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        
        if time_idx == len(globals.time_units_data):
            index = 0
            for sub_idx, frame in enumerate(sub_frames):
                ttk.Label(frame, text="End of Simulation", font=('Helvetica', 12, 'bold'), foreground='#ff4a4a').pack(pady=10)
                if index == 0:
                    ttk.Label(frame, text="Sub System 1 - Core 1", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub1_core1.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub1_core1.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub1_core1.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)
                if index == 1:
                    ttk.Label(frame, text="Sub System 1 - Core 2", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub1_core2.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub1_core2.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub1_core2.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)
                if index == 2:
                    ttk.Label(frame, text="Sub System 1 - Core 3", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub1_core3.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub1_core3.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub1_core3.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)
                if index == 3:
                    ttk.Label(frame, text="Sub System 2 - Core 1", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub2_core1.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub2_core1.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub2_core1.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)

                draw_timeline(frame, sub_idx, index)
                index += 1
            return
        
        if time_idx == len(globals.time_units_data) + 1:
            index = 0
            for sub_idx, frame in enumerate(sub_frames):
                ttk.Label(frame, text="End of Simulation", font=('Helvetica', 12, 'bold'), foreground='#ff4a4a').pack(pady=10)
                if index == 0:
                    ttk.Label(frame, text="Sub System 2 - Core 2", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub2_core2.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub2_core2.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub2_core2.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)
                if index == 1:
                    ttk.Label(frame, text="Sub System 3 - Core 1", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub3_core1.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub3_core1.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub3_core1.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)
                if index == 2:
                    ttk.Label(frame, text="Sub System 4 - Core 1", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub4_core1.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub4_core1.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub4_core1.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)
                if index == 3:
                    ttk.Label(frame, text="Sub System 4 - Core 2", font=('Helvetica', 10, 'bold')).pack(pady=2)
                    ttk.Label(frame, text=f"⏳ Waiting Time: {globals.sub4_core2.avg_waiting_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"🔄 Turnaround Time: {globals.sub4_core2.avg_turnaround_time}", font=('Helvetica', 10)).pack(pady=2)
                    ttk.Label(frame, text=f"⚡ Response Time: {globals.sub4_core2.avg_response_time}", font=('Helvetica', 10)).pack(pady=2)

                draw_timeline(frame, sub_idx, index + 4)
                index += 1
            return
        
        data = globals.time_units_data[time_idx]
        
        for sub_idx, frame in enumerate(sub_frames):
            sub_data = data["subsystems"][sub_idx]
            
            res_frame = ttk.Frame(frame)
            res_frame.pack(fill=tk.X, pady=5)
            ttk.Label(res_frame, text=f"R1: {sub_data.get('R1', '-')}", 
                     font=('Helvetica', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(res_frame, text=f"R2: {sub_data.get('R2', '-')}", 
                     font=('Helvetica', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(frame, text=f"⏳ Waiting: {', '.join(sub_data.get('waiting_queue', [])) or 'None'}",
                     font=('Helvetica', 9)).pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=f"✅ Completed: {', '.join(sub_data.get('completed_tasks', [])) or 'None'}",
                     font=('Helvetica', 9)).pack(fill=tk.X, pady=2)
            
            cores_frame = ttk.Frame(frame)
            cores_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            for core_idx, core in enumerate(sub_data.get("cores", [])):
                core_frame = ttk.Frame(cores_frame)
                core_frame.pack(fill=tk.X, pady=3)
                
                ttk.Label(core_frame, text=f"Core {core_idx+1}:", 
                         width=8, anchor='w', font=('Helvetica', 9, 'bold')).pack(side=tk.LEFT)
                ttk.Label(core_frame, text=f"▶ {core.get('running_task', 'idle')}", 
                         width=20, anchor='w', foreground=accent_color).pack(side=tk.LEFT)
                ttk.Label(core_frame, text=f"📂 Ready: {', '.join(core.get('ready_queue', [])) or 'Empty'}",
                         anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)

    def draw_timeline(frame, sub_idx, index):
        canvas_frame = ttk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        num_time_units = len(globals.time_units_data)
        rect_width = 100
        total_width = num_time_units * rect_width
        
        canvas = tk.Canvas(canvas_frame, bg='white', height=80, width=1200, scrollregion=(0, 0, total_width, 80))
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(xscrollcommand=h_scrollbar.set)
        
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        for i in range(num_time_units):
            x = i * rect_width
            canvas.create_line(x, 0, x, 60, fill='black')
            
            if index == 0:
                text = f'{globals.sub1_core1.schedule[i].name if globals.sub1_core1.schedule[i] else 'idle'}'
            elif index == 1:
                text = f'{globals.sub1_core2.schedule[i].name if globals.sub1_core2.schedule[i] else 'idle'}'
            elif index == 2:
                text = f'{globals.sub1_core3.schedule[i].name if globals.sub1_core3.schedule[i] else 'idle'}'
            elif index == 3:
                text = f'{globals.sub2_core1.schedule[i].name if globals.sub2_core1.schedule[i] else 'idle'}'
            elif index == 4:
                text = f'{globals.sub2_core2.schedule[i].name if globals.sub2_core2.schedule[i] else 'idle'}'
            elif index == 5:
                text = f'{globals.sub3_core1.schedule[i].name if globals.sub3_core1.schedule[i] else 'idle'}'
            elif index == 6:
                text = f'{globals.sub4_core1.schedule[i].name if globals.sub4_core1.schedule[i] else 'idle'}'
            elif index == 7:
                text = f'{globals.sub4_core2.schedule[i].name if globals.sub4_core2.schedule[i] else 'idle'}'
            canvas.create_text(x + rect_width / 2, 30, text=text, font=('Helvetica', 8))
            
            canvas.create_text(x + rect_width / 2, 70, text=f'{i}-{i+1}', font=('Helvetica', 8))
        
        canvas.create_rectangle(0, 0, total_width, 60, outline='black')
    
    slider.config(command=update_display)
    update_display()
    root.mainloop()