from key_logger import KeyLogger
import sys

def main():
    print("Welcome to Productivity Analyzer")
    logger = KeyLogger()
    
    try:
        print("Recording... Press Ctrl+C to stop in terminal if needed.")
        logger.start()
    except KeyboardInterrupt:
        print("\nStopping...")

    # Always generate report (whether stopped by ESC or Ctrl+C)
    log_data = logger.get_log()
    print(f"Captured {len(log_data)} keystrokes.")
    
    # Analysis Phase
    from analyzer import Analyzer
    print("Analyzing session...")
    analyzer = Analyzer(log_data)
    print(analyzer.analyze())

if __name__ == "__main__":
    main()
