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
        
        # Ensure directories exist
        import os
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, "data")
        self.report_dir = os.path.join(self.root_dir, "reports")
        
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
        if not os.path.exists(self.report_dir): os.makedirs(self.report_dir)
        
        self.history_file = os.path.join(self.data_dir, "history.csv")

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

    def generate_charts(self):
        try:
            import matplotlib.pyplot as plt
            
            # Create a simple "Keys over Time" chart
            # Bucket timestamps into 1-second intervals
            if not self.activity_timestamps:
                return None
                
            start_t = self.activity_timestamps[0]
            relative_times = [t - start_t for t in self.activity_timestamps]
            
            plt.figure(figsize=(6, 4))
            plt.hist(relative_times, bins=max(1, int(max(relative_times))), color='skyblue', edgecolor='black')
            plt.title('Work Intensity (Keystrokes & Mouse Events)')
            plt.xlabel('Timeline (Seconds)')
            plt.ylabel('Intensity (Actions/Sec)')
            plt.tight_layout()
            
            chart_filename = f"chart_{int(time.time())}.png"
            plt.savefig(chart_filename)
            plt.close()
            return chart_filename
        except ImportError:
            return None
        except Exception as e:
            print(f"Chart error: {e}")
            return None

    def save_report(self, report_text):
        # Generate Chart
        chart_file = self.generate_charts()
        
        # Define Filename in Reports Directory
        base_name = f"session_report_{int(time.time())}"
        pdf_filename = os.path.join(self.report_dir, f"{base_name}.pdf")
            
        # Generate PDF Report
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Session Productivity Report")
            
            # Content (Split by newlines)
            c.setFont("Helvetica", 10)
            y = height - 80
            for line in report_text.split('\n'):
                c.drawString(50, y, line.strip())
                y -= 15
                
            # Embed Chart
            if chart_file and os.path.exists(chart_file):
                y -= 220 # Space for chart
                c.drawImage(chart_file, 50, y, width=400, height=250)
                os.remove(chart_file) # Cleanup png
                
            c.save()
            return pdf_filename # Return PDF path
            
        except ImportError:
            # Fallback to text if reportlab missing (Saved to Data Dir)
            txt_filename = os.path.join(self.data_dir, f"{base_name}.txt")
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(report_text)
            return txt_filename

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
