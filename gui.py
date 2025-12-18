import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from key_logger import KeyLogger
from analyzer import Analyzer

class TrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Activity Tracker")
        self.root.geometry("360x320")
        
        # Theme & Style
        self.style = ttk.Style()
        self.style.theme_use('clam') # Modern clean look
        
        # Colors
        BG_COLOR = "#f5f5f5"
        self.root.configure(bg=BG_COLOR)
        
        # Configure Styles
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, font=("Segoe UI", 10), foreground="#333333")
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50")
        self.style.configure("Status.TLabel", font=("Segoe UI", 12))
        self.style.configure("TLabelframe", background=BG_COLOR, font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabelframe.Label", background=BG_COLOR, foreground="#555555")
        
        # Button Styles
        self.style.configure("Start.TButton", background="#2ecc71", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Start.TButton", background=[('active', '#27ae60')])
        
        self.style.configure("Stop.TButton", background="#e74c3c", foreground="black", font=("Segoe UI", 10, "bold"))
        self.style.map("Stop.TButton", background=[('active', '#c0392b')], foreground=[('active', 'black'), ('disabled', 'gray')])

        self.logger = KeyLogger()
        self.is_running = False

        # Main Layout
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="Activity Tracker", style="Title.TLabel")
        title.pack(pady=(0, 10))

        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Ready", style="Status.TLabel", foreground="gray")
        self.status_label.pack(pady=5)

        # Metrics Card
        self.metrics_frame = ttk.LabelFrame(main_frame, text="Live Session Metrics", padding="15")
        self.metrics_frame.pack(fill=tk.X, pady=15)
        
        # Grid Layout for Metrics
        self.lbl_speed = ttk.Label(self.metrics_frame, text="Speed: 0.00 KPS")
        self.lbl_speed.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.lbl_count = ttk.Label(self.metrics_frame, text="Keys: 0")
        self.lbl_count.grid(row=0, column=1, sticky="e", padx=10, pady=5)
        
        self.lbl_pause = ttk.Label(self.metrics_frame, text="Pause: 0.0s")
        self.lbl_pause.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.lbl_mouse = ttk.Label(self.metrics_frame, text="Mouse: Idle")
        self.lbl_mouse.grid(row=1, column=1, sticky="e", padx=10, pady=5)
        
        # Expand columns
        self.metrics_frame.columnconfigure(0, weight=1)
        self.metrics_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10, fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Tracking", command=self.start_tracking, style="Start.TButton")
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop & Report", command=self.stop_tracking, style="Stop.TButton")
        self.stop_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        self.stop_btn.state(['disabled'])

    def start_tracking(self):
        self.logger = KeyLogger() # Reset logger
        self.logger.start()
        self.is_running = True
        self.status_label.configure(text="Status: Recording...", foreground="#27ae60")
        self.start_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self.update_metrics()

    def update_metrics(self):
        if not self.is_running:
            return
            
        duration, keys, speed, pause, mouse_stat = self.logger.get_stats()
        
        self.lbl_speed.configure(text=f"Speed: {speed:.2f} KPS")
        self.lbl_count.configure(text=f"Keys: {keys}")
        self.lbl_pause.configure(text=f"Pause: {pause:.1f}s")
        self.lbl_mouse.configure(text=f"Mouse: {mouse_stat}")
        
        if mouse_stat == "Active":
            self.lbl_mouse.configure(foreground="#27ae60") # Green
        else:
            self.lbl_mouse.configure(foreground="#95a5a6") # Gray
        
        # Color code pause
        if pause > 5:
            self.lbl_pause.configure(foreground="#e74c3c") # Red
        else:
            self.lbl_pause.configure(foreground="#333333") # Dark

        self.root.after(100, self.update_metrics)

    def stop_tracking(self):
        if not self.is_running:
            return
        
        self.logger.stop()
        self.is_running = False
        self.status_label.configure(text="Status: Stopped", foreground="#e74c3c")
        
        # Analyze
        log_data = self.logger.get_log()
        activity, holds = self.logger.get_advanced_metrics()
        
        analyzer = Analyzer(log_data, activity, holds)
        report = analyzer.analyze()
        
        # Save
        filename = analyzer.save_report(report)
        
        messagebox.showinfo("Report Generated", f"Session saved to:\n{filename}")
        
        # Reset UI
        self.start_btn.state(['!disabled'])
        self.stop_btn.state(['disabled'])

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerGUI(root)
    root.mainloop()
