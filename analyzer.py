import pandas as pd
import time
import csv
import os

class Analyzer:
    def __init__(self, log_data, activity_timestamps=None, hold_durations=None):
        self.log_data = log_data
        self.df = pd.DataFrame(log_data)
        self.activity_timestamps = activity_timestamps if activity_timestamps else []
        self.hold_durations = hold_durations if hold_durations else []
        self.history_file = "history.csv"

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
        
        # History & Comparison
        self.save_to_history(duration, speed, score, fatigue_label)
        prev_speed, prev_score, trend = self.get_comparison(speed, score)

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
        
        --- History Comparison ---
        Previous Speed: {prev_speed} KPS
        Previous Score: {prev_score}/100
        Trend: {trend}
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
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)
        return filename

    def save_to_history(self, duration, speed, score, status):
        file_exists = os.path.isfile(self.history_file)
        
        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Duration", "Speed", "Score", "Status"])
            
            writer.writerow([int(time.time()), f"{duration:.2f}", f"{speed:.2f}", score, status])

    def get_comparison(self, current_speed, current_score):
        if not os.path.isfile(self.history_file):
            return "N/A", "N/A", "First Session"
            
        try:
            df = pd.read_csv(self.history_file)
            if len(df) < 2: # Only the current one exists
                return "N/A", "N/A", "First Session"
                
            # Get second to last row (previous session)
            prev = df.iloc[-2]
            prev_speed = float(prev["Speed"])
            prev_score = int(prev["Score"])
            
            if current_score > prev_score:
                trend = "Improved 🟢"
            elif current_score < prev_score:
                trend = "Worsened 🔴"
            else:
                trend = "Stable 🟡"
                
            return f"{prev_speed:.2f}", prev_score, trend
        except Exception:
            return "Error", "Error", "Data Corrupt"
