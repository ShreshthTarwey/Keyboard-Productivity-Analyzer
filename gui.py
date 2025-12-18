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
        self.status_label.pack(pady=20)

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
