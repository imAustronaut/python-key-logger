import time
from pynput import keyboard, mouse
from datetime import datetime
import threading
import sys

class InputTracker:
    def __init__(self):
        self.log_file = "savedinput.txt"
        self.running = True
        self.events = []
        self.start_time = datetime.now()
        
        # Initialize counters
        self.key_count = 0
        self.click_count = 0
        self.scroll_count = 0
        self.last_activity = datetime.now()
        
        # Setup listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
    def on_key_press(self, key):
        """Record keyboard presses"""
        try:
            self.events.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] KEY: {key.char}")
            self.key_count += 1
        except AttributeError:
            self.events.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SPECIAL_KEY: {key}")
            self.key_count += 1
        self.last_activity = datetime.now()
        
    def on_click(self, x, y, button, pressed):
        """Record mouse clicks"""
        if pressed:
            self.events.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CLICK: {button} at ({x}, {y})")
            self.click_count += 1
            self.last_activity = datetime.now()
            
    def on_scroll(self, x, y, dx, dy):
        """Record mouse scrolls"""
        direction = "down" if dy < 0 else "up"
        self.events.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCROLL: {direction} at ({x}, {y})")
        self.scroll_count += 1
        self.last_activity = datetime.now()
    
    def check_idle(self):
        """Check for inactivity to auto-stop"""
        while self.running:
            time.sleep(1)
            idle_time = (datetime.now() - self.last_activity).total_seconds()
            if idle_time > 9999999999:  # 9999999999 seconds of inactivity
                print("\nNo activity for 9999999999 seconds. Stopping tracking...")
                self.stop()
    
    def start(self):
        """Start tracking inputs"""
        print("Input tracking started. All keyboard and mouse activity will be recorded.")
        print("Press CTRL+C or wait 30 seconds of inactivity to stop tracking.")
        
        # Write header to log file
        with open(self.log_file, 'w') as f:
            f.write(f"Input Tracking Session - {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
        
        # Start listeners
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        # Start inactivity monitor
        threading.Thread(target=self.check_idle, daemon=True).start()
        
        try:
            while self.running:
                time.sleep(0.1)
                # Periodically save events to file
                if len(self.events) > 0:
                    with open(self.log_file, 'a') as f:
                        for event in self.events:
                            f.write(event + "\n")
                    self.events.clear()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop tracking and save results"""
        self.running = False
        
        # Ensure all remaining events are saved
        if len(self.events) > 0:
            with open(self.log_file, 'a') as f:
                for event in self.events:
                    f.write(event + "\n")
        
        # Write summary to log file
        duration = datetime.now() - self.start_time
        with open(self.log_file, 'a') as f:
            f.write("\n" + "="*50 + "\n")
            f.write(f"Tracking Summary\n")
            f.write(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration.total_seconds():.1f} seconds\n")
            f.write(f"Total Keys Pressed: {self.key_count}\n")
            f.write(f"Total Mouse Clicks: {self.click_count}\n")
            f.write(f"Total Mouse Scrolls: {self.scroll_count}\n")
        
        print("\nTracking stopped. Results saved to 'savedinput.txt'")
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        print(f"Keys pressed: {self.key_count}")
        print(f"Mouse clicks: {self.click_count}")
        print(f"Mouse scrolls: {self.scroll_count}")
        
        # Exit the program
        sys.exit(0)

if __name__ == "__main__":
    tracker = InputTracker()
    tracker.start()
