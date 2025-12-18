import pandas as pd
import time

class Analyzer:
    def __init__(self, log_data, activity_timestamps=None, hold_durations=None):
        self.log_data = log_data
        self.df = pd.DataFrame(log_data)
        self.activity_timestamps = activity_timestamps if activity_timestamps else []
        self.hold_durations = hold_durations if hold_durations else []

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
        
        # Mistake Analysis
        backspaces = len(self.df[self.df['key'] == 'Key.backspace'])
        correction_ratio = (backspaces / total_keys * 100) if total_keys > 0 else 0
        
        special_keys = self.df[self.df['key'].astype(str).str.len() > 1]
        mistake_count = len(special_keys)

        # Advanced Fatigue Analysis
        score, fatigue_label, deep_idles = self.calculate_fatigue_score(correction_ratio)

        report = f"""
        --- Session Report ---
        Duration: {duration:.2f} seconds
        Total Keystrokes: {total_keys}
        Speed: {speed:.2f} keys/sec
        
        --- Mistake Analysis ---
        Total Backspaces: {backspaces}
        Correction Ratio: {correction_ratio:.2f}%
        
        --- Fatigue Analysis (v3.0) ---
        Fatigue Score: {score}/100
        Status: {fatigue_label}
        Deep Idles (>10s): {deep_idles}
        ----------------------
        """
        return report

    def calculate_fatigue_score(self, correction_ratio):
        score = 100
        deep_idles = 0
        
        # 1. Idle Penalty
        if len(self.activity_timestamps) > 1:
            for i in range(1, len(self.activity_timestamps)):
                diff = self.activity_timestamps[i] - self.activity_timestamps[i-1]
                if diff > 10:
                    score -= 20 # Deep Idle (Zoned out - Demo Mode >10s)
                    deep_idles += 1
                elif diff > 5:
                    score -= 5 # Minor Distraction

        # 2. Key Hold Penalty (Sluggishness)
        avg_hold = 0
        if self.hold_durations:
            avg_hold = sum(self.hold_durations) / len(self.hold_durations)
            if avg_hold > 0.15: # 150ms
                score -= 10

        # 3. Frustration Penalty (Errors)
        score -= (correction_ratio * 2)

        # Clamp Score
        score = max(0, min(100, int(score)))

        # Label
        if score >= 90:
            label = "Unknown/Energetic (Flow State)"
        elif score >= 60:
            label = "Normal"
        else:
            label = "Fatigued (Need a Break)"
            
        return score, label, deep_idles

    def save_report(self, report_text):
        filename = f"session_report_{int(time.time())}.txt"
        with open(filename, "w") as f:
            f.write(report_text)
        return filename
