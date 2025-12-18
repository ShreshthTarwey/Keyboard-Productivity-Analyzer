from key_logger import KeyLogger
import sys

def main():
    print("Welcome to Productivity Analyzer")
    logger = KeyLogger()
    
    try:
        print("Recording... Press Ctrl+C to stop in terminal if needed, or define exit condition.")
        # logic to start logger
        # For simplicity in this phase, we just instantiate it.
        # functional listener needs to be blocking or in thread.
        logger.start()
    except KeyboardInterrupt:
        print("\nStopping...")
        print(f"Captured {len(logger.get_log())} keystrokes.")

if __name__ == "__main__":
    main()
