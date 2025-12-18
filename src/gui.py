import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from .key_logger import KeyLogger
from .analyzer import Analyzer
import time

class ToastNotification:
    def __init__(self, root, message, color):
        self.top = tk.Toplevel(root)
        self.top.overrideredirect(True)
        self.top.geometry(f"300x50+{root.winfo_screenwidth()-320}+{root.winfo_screenheight()-100}")
        self.top.configure(bg=color)
        
        tk.Label(self.top, text=message, bg=color, fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10).pack()
        
        # Fade in
        self.top.attributes("-alpha", 0.0)
        self.fade_in()

        # Auto close
        self.top.after(4000, self.fade_out)

    def fade_in(self):
        alpha = self.top.attributes("-alpha")
        if alpha < 0.9:
            alpha += 0.1
            self.top.attributes("-alpha", alpha)
            self.top.after(50, self.fade_in)

    def fade_out(self):
        alpha = self.top.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.1
            self.top.attributes("-alpha", alpha)
            self.top.after(50, self.fade_out)
        else:
            self.top.destroy()

class TrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Activity Tracker")
        self.root.geometry("360x380")
        
        # Theme & Style
        self.style = ttk.Style()
        self.style.theme_use('clam') # Modern clean look
        
        # Colors
        BG_COLOR = "#f5f5f5"
        self.root.configure(bg=BG_COLOR)
        
        # Configure Styles
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, font=("Segoe UI", 10), foreground="#333333")
        self.style.configure("TCheckbutton", background=BG_COLOR, font=("Segoe UI", 10), foreground="#333333")
        self.style.map("TCheckbutton", background=[('active', BG_COLOR)])
        
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
        
        # Smart Alert State
        self.last_alert_time = 0
        self.long_pause_count = 0
        self.last_backspace_count = 0
        self.error_burst_start = 0

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

        # Privacy Toggle
        self.privacy_var = tk.BooleanVar(value=False)
        self.chk_privacy = ttk.Checkbutton(main_frame, text="Privacy Mode (Don't save keys)", variable=self.privacy_var)
        self.chk_privacy.pack(pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10, fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Tracking", command=self.start_tracking, style="Start.TButton")
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop & Report", command=self.stop_tracking, style="Stop.TButton")
        self.stop_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        self.stop_btn.state(['disabled'])

    def start_tracking(self):
        privacy = self.privacy_var.get()
        self.logger = KeyLogger(privacy_mode=privacy) # Reset logger with privacy setting
        self.logger.start()
        self.is_running = True
        
        # Reset Alert State
        self.long_pause_count = 0
        self.last_backspace_count = 0
        self.last_alert_time = time.time()
        
        status_text = "Recording (Privacy Mode)..." if privacy else "Recording..."
        self.status_label.configure(text=status_text, foreground="#27ae60")
        
        self.chk_privacy.state(['disabled']) # Lock toggle while running
        self.start_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self.update_metrics()

    def update_metrics(self):
        if not self.is_running:
            return
            
        duration, keys, speed, pause, mouse_stat, backspaces = self.logger.get_stats()
        
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
            
        # --- Smart Alert Logic ---
        import time
        current_time = time.time()
        
        # 1. Fatigue Check (3 Long Pauses)
        # We need to detect the *start* of a long pause only once
        # Using a simple threshold check may trigger repeatedly.
        # Improvement: In a real app, we'd track state transitions. 
        # For this demo, let's just alert if pause > 15s AND we haven't alerted recently.
        if pause > 15 and (current_time - self.last_alert_time) > 60:
             self.long_pause_count += 1
             if self.long_pause_count >= 3:
                 ToastNotification(self.root, "⚠️ You seem tired. Consider a break.", "#e67e22") # Orange
                 self.last_alert_time = current_time
                 self.long_pause_count = 0 # Reset
        
        # 2. Error Burst Check
        # Check delta in backspaces every update (100ms) is too fast.
        # Let's accumulate. But simple way:
        new_errors = backspaces - self.last_backspace_count
        if new_errors > 3: # 3 backspaces in 100ms is HUMANLY IMPOSSIBLE?? No.
            # Actually update runs every 100ms. 
            # If user holds backspace, they can generate many.
            pass
            
        # Better Error Logic: Check total backspaces in last 10 seconds? 
        # For simplicity in this demo: If total backspaces increases by 5 in a short burst.
        if new_errors > 0:
             # simple burst detection could be complex.
             # Let's just say if you made > 5 mistakes since last check (unlikely in 100ms)
             # Let's check accumulated.
             pass
             
        # Re-think Error Logic for simplicity:
        # If total backspaces > 10 and ratio is high? No realtime.
        # Let's track backspaces per minute window? Too complex for 1 file.
        # Simple Trigger: If you press backspace 5 times in 5 seconds.
        # Let's just use the count directly.
        if backspaces - self.last_backspace_count > 0:
             # User pressed backspace
             pass
        
        # Working Simple Logic:
        # Every 5 seconds, check how many errors occurred.
        import time
        current_time = time.time()
        
        # 1. Fatigue Check (Pause > 15s)
        # We only count a long pause once per occurrence
        if pause > 15:
             # Check if we already alerted for this specific long pause
             # We use a simple timestamp lockout
             if (current_time - self.last_alert_time) > 20: 
                 self.long_pause_count += 1
                 if self.long_pause_count >= 3:
                     ToastNotification(self.root, "⚠️ You seem tired. Consider a break.", "#e67e22") # Orange
                     self.last_alert_time = current_time
                     self.long_pause_count = 0
                 else:
                     # Minor visual cue could go here, but let's wait for 3 strikes
                     pass

        # 2. Error Burst Check
        # Check if Backspace count increased
        diff = backspaces - self.last_backspace_count
        if diff > 0:
            # Add timestamp for every backspace press
            if not hasattr(self, 'backspace_timestamps'):
                self.backspace_timestamps = []
            
            for _ in range(diff):
                self.backspace_timestamps.append(current_time)
            
            self.last_backspace_count = backspaces
            
        # Filter timestamps to keep only last 5 seconds
        if hasattr(self, 'backspace_timestamps'):
            self.backspace_timestamps = [t for t in self.backspace_timestamps if current_time - t < 5.0]
            
            # If > 5 backspaces in last 5 seconds
            if len(self.backspace_timestamps) > 5:
                 if (current_time - self.last_alert_time) > 10: # Anti-spam
                     ToastNotification(self.root, "🛑 High correction rate detected.", "#c0392b") # Red
                     self.last_alert_time = current_time
                     self.backspace_timestamps = [] # Reset

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
        self.chk_privacy.state(['!disabled'])

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerGUI(root)
    root.mainloop()
