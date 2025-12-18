import pandas as pd
import time

class Analyzer:
    def __init__(self, log_data):
        self.log_data = log_data
        self.df = pd.DataFrame(log_data)

    def analyze(self):
        if self.df.empty:
            return "No data to analyze."
        
        # Calculate session duration
        start_time = self.df['time'].min()
        end_time = self.df['time'].max()
        duration = end_time - start_time
        
        # Calculate Keystrokes per Second
        total_keys = len(self.df)
        speed = total_keys / duration if duration > 0 else 0
        
        # Fatigue Detection (Pause Analysis)
        long_pauses = 0
        pause_threshold = 5.0 # seconds
        timestamps = self.df['time'].tolist()
        
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]
            if diff > pause_threshold:
                long_pauses += 1
        
        fatigue_status = "Low"
        if long_pauses > 5:
            fatigue_status = "High (Taking many breaks)"
        elif long_pauses > 2:
            fatigue_status = "Medium"

        # Fatigue Detection (Pause Analysis)
        long_pauses = 0
        pause_threshold = 5.0 # seconds
        timestamps = self.df['time'].tolist()
        
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]
            if diff > pause_threshold:
                long_pauses += 1
        
        fatigue_status = "Low"
        if long_pauses > 5:
            fatigue_status = "High (Taking many breaks)"
        elif long_pauses > 2:
            fatigue_status = "Medium"

        report = f"""
        --- Session Report ---
        Duration: {duration:.2f} seconds
        Total Keystrokes: {total_keys}
        Speed: {speed:.2f} keys/sec

        Special/Function Keys Used: {mistake_count} (Potential corrections?)

        
        --- Fatigue Analysis ---
        Long Pauses (>5s): {long_pauses}
        Fatigue Level: {fatigue_status}
        ----------------------
        """
        return report

    def save_report(self, report_text):
        filename = f"session_report_{int(time.time())}.txt"
        with open(filename, "w") as f:
            f.write(report_text)
        return filename
