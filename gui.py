import tkinter as tk
from tkinter import messagebox
from key_logger import KeyLogger
from analyzer import Analyzer

class TrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Activity Tracker")
        self.root.geometry("300x200")

        self.logger = KeyLogger()
        self.is_running = False

        # Status Label
        self.status_label = tk.Label(root, text="Status: Ready", fg="gray", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Metrics Frame
        self.metrics_frame = tk.Frame(root)
        self.metrics_frame.pack(pady=10)
        
        self.lbl_speed = tk.Label(self.metrics_frame, text="Speed: 0.0 KPS", font=("Arial", 10))
        self.lbl_speed.pack()
        
        self.lbl_count = tk.Label(self.metrics_frame, text="Total Keys: 0", font=("Arial", 10))
        self.lbl_count.pack()
        
        self.lbl_pause = tk.Label(self.metrics_frame, text="Pause: 0.0s", font=("Arial", 10))
        self.lbl_pause.pack()

        # Start Button
        self.start_btn = tk.Button(root, text="Start Tracking", command=self.start_tracking, bg="green", fg="white", width=15)
        self.start_btn.pack(pady=5)

        # Stop Button
        self.stop_btn = tk.Button(root, text="Stop & Report", command=self.stop_tracking, bg="red", fg="white", width=15)
        self.stop_btn.pack(pady=5)
        self.stop_btn.config(state=tk.DISABLED)

    def start_tracking(self):
        self.logger = KeyLogger() # Reset logger
        self.logger.start()
        self.is_running = True
        self.status_label.config(text="Status: Recording...", fg="green")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.update_metrics()

    def update_metrics(self):
        if not self.is_running:
            return
            
        duration, keys, speed, pause = self.logger.get_stats()
        
        self.lbl_speed.config(text=f"Speed: {speed:.2f} KPS")
        self.lbl_count.config(text=f"Total Keys: {keys}")
        self.lbl_pause.config(text=f"Pause: {pause:.1f}s")
        
        # Color code pause (visual fatigue warning)
        if pause > 5:
            self.lbl_pause.config(fg="red")
        else:
            self.lbl_pause.config(fg="black")

        self.root.after(100, self.update_metrics)

    def stop_tracking(self):
        if not self.is_running:
            return
        
        self.logger.stop()
        self.is_running = False
        self.status_label.config(text="Status: Stopped", fg="red")
        
        # Analyze
        log_data = self.logger.get_log()
        analyzer = Analyzer(log_data)
        report = analyzer.analyze()
        
        # Save
        filename = analyzer.save_report(report)
        
        messagebox.showinfo("Report Generated", f"Session saved to:\n{filename}")
        
        # Reset UI
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerGUI(root)
    root.mainloop()
