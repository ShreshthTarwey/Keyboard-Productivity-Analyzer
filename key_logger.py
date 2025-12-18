from pynput import keyboard
import time
import threading

class KeyLogger:
    def __init__(self):
        self.log = []
        self.active = False
        self.start_time = None
        # Real-time stats
        self.key_count = 0
        self.last_key_time = None

    def on_press(self, key):
        current_time = time.time()
        self.key_count += 1
        self.last_key_time = current_time
        
        try:
            self.log.append({'key': key.char, 'time': current_time})
        except AttributeError:
            self.log.append({'key': str(key), 'time': current_time})

        if key == keyboard.Key.esc:
            return False

    def start(self):
        self.active = True
        self.start_time = time.time()
        self.last_key_time = self.start_time
        self.key_count = 0
        # Non-blocking listener for GUI
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop(self):
        self.active = False
        if hasattr(self, 'listener'):
            self.listener.stop()
    
    def get_log(self):
        return self.log

    def get_stats(self):
        if not self.active or not self.start_time:
            return 0, 0, 0, 0
        
        duration = time.time() - self.start_time
        keys = self.key_count
        speed = keys / duration if duration > 0 else 0
        
        current_pause = 0
        if self.last_key_time:
            current_pause = time.time() - self.last_key_time
            
        return duration, keys, speed, current_pause
