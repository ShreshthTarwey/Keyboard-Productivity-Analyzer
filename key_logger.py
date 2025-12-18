from pynput import keyboard
import time
import threading

class KeyLogger:
    def __init__(self):
        self.log = []
        self.active = False
        self.start_time = None

    def on_press(self, key):
        try:
            self.log.append({'key': key.char, 'time': time.time()})
        except AttributeError:
            self.log.append({'key': str(key), 'time': time.time()})

    def start(self):
        self.active = True
        self.start_time = time.time()
        print("Logger started... (Press ESC to stop)")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
    
    def get_log(self):
        return self.log
