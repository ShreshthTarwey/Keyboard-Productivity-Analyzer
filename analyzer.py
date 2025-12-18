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
        
        # Identify non-alphanumeric keys (potential corrections/mistakes logic for demo)
        special_keys = self.df[self.df['key'].astype(str).str.len() > 1]
        mistake_count = len(special_keys)

        report = f"""
        --- Session Report ---
        Duration: {duration:.2f} seconds
        Total Keystrokes: {total_keys}
        Speed: {speed:.2f} keys/sec
        Special/Function Keys Used: {mistake_count} (Potential corrections?)
        ----------------------
        """
        return report
