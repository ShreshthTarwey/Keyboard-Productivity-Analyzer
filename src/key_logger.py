from pynput import keyboard, mouse
import time
import threading

class KeyLogger:
    def __init__(self, privacy_mode=False):
        self.log = []
        self.active = False
        self.start_time = None
        self.privacy_mode = privacy_mode
        
        # Real-time stats
        self.key_count = 0
        self.backspace_count = 0
        self.last_activity_time = None
        
        # Advanced Fatigue Metrics
        self.hold_durations = []
        self.activity_timestamps = [] # Store ALL user interaction times (Keys + Mouse)
        self.pressed_keys = {} # To track hold duration {key: start_time}

    def on_press(self, key):
        current_time = time.time()
        self.key_count += 1
        
        if key == keyboard.Key.backspace:
            self.backspace_count += 1
            
        self.last_activity_time = current_time
        self.activity_timestamps.append(current_time)
        
        # Start Hold Timer
        if key not in self.pressed_keys:
            self.pressed_keys[key] = current_time
        
        # Log key (Masked if Privacy Mode is ON)
        if self.privacy_mode:
            self.log.append({'key': 'HIDDEN', 'time': current_time})
        else:
            try:
                self.log.append({'key': key.char, 'time': current_time})
            except AttributeError:
                self.log.append({'key': str(key), 'time': current_time})

        if key == keyboard.Key.esc:
            return False

    def on_release(self, key):
        current_time = time.time()
        if key in self.pressed_keys:
            start_time = self.pressed_keys.pop(key)
            duration = current_time - start_time
            self.hold_durations.append(duration)

    def on_move(self, x, y):
        self.record_activity()

    def on_click(self, x, y, button, pressed):
        self.record_activity()

    def on_scroll(self, x, y, dx, dy):
        self.record_activity()

    def record_activity(self):
        if self.active:
            self.last_activity_time = time.time()
            self.activity_timestamps.append(self.last_activity_time)

    def start(self):
        self.active = True
        self.start_time = time.time()
        self.last_activity_time = self.start_time
        self.key_count = 0
        self.backspace_count = 0
        self.activity_timestamps = [self.start_time]
        
        # Keyboard Listener
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.key_listener.start()
        
        # Mouse Listener
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move, 
            on_click=self.on_click, 
            on_scroll=self.on_scroll
        )
        self.mouse_listener.start()

    def stop(self):
        self.active = False
        if hasattr(self, 'key_listener'):
            self.key_listener.stop()
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
    
    def get_log(self):
        return self.log
    
    def get_advanced_metrics(self):
        return self.activity_timestamps, self.hold_durations

    def get_stats(self):
        if not self.active or not self.start_time:
            return 0, 0, 0, 0, "Idle"
        
        duration = time.time() - self.start_time
        keys = self.key_count
        speed = keys / duration if duration > 0 else 0
        
        current_pause = 0
        mouse_status = "Idle"
        
        if self.last_activity_time:
            time_since_activity = time.time() - self.last_activity_time
            current_pause = time_since_activity
            if time_since_activity < 1.0:
                mouse_status = "Active"
            else:
                mouse_status = "Idle"
            
        return duration, keys, speed, current_pause, mouse_status, self.backspace_count
