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

        if key == keyboard.Key.esc:
            return False

    def start(self):
        self.active = True
        self.start_time = time.time()
        # Non-blocking listener for GUI
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop(self):
        self.active = False
        if hasattr(self, 'listener'):
            self.listener.stop()
    
    def get_log(self):
        return self.log
