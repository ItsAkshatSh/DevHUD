import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class FocusTimer(QObject):
    time_updated = pyqtSignal(int) 
    timer_completed = pyqtSignal(str) 
    state_changed = pyqtSignal(str)  
    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False
        self.timer_thread = None
        self.remaining_seconds = 0
        self.work_duration = 25 * 60 
        self.break_duration = 5 * 60  
        self.long_break_duration = 15 * 60 
        self.pomodoros_until_long_break = 4
        self.current_pomodoro_count = 0
        self.is_break = False
        
    def start_timer(self, duration=None):
        """Start the timer with optional custom duration"""
        if not self.running:
            self.running = True
            self.paused = False
            if duration is not None:
                self.remaining_seconds = duration
            elif self.remaining_seconds == 0:
                self.remaining_seconds = self.work_duration
                
            self.timer_thread = threading.Thread(target=self._timer_loop)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            self.state_changed.emit("started")
            
    def pause_timer(self):
        """Pause the timer"""
        if self.running and not self.paused:
            self.paused = True
            self.state_changed.emit("paused")
            
    def resume_timer(self):
        """Resume the timer"""
        if self.running and self.paused:
            self.paused = False
            self.state_changed.emit("resumed")
            
    def stop_timer(self):
        """Stop the timer"""
        if self.running:
            self.running = False
            self.paused = False
            if self.timer_thread:
                self.timer_thread.join()
            self.state_changed.emit("stopped")
            
    def reset_timer(self):
        """Reset the timer to initial state"""
        self.stop_timer()
        self.remaining_seconds = self.work_duration
        self.is_break = False
        self.current_pomodoro_count = 0
        self.time_updated.emit(self.remaining_seconds)
        
    def _timer_loop(self):
        """Main timer loop"""
        while self.running:
            if not self.paused:
                if self.remaining_seconds > 0:
                    self.remaining_seconds -= 1
                    self.time_updated.emit(self.remaining_seconds)
                else:
                    self._handle_timer_completion()
            time.sleep(1)
            
    def _handle_timer_completion(self):
        """Handle timer completion and switch between work/break periods"""
        if not self.is_break:
            # Work period completed
            self.current_pomodoro_count += 1
            self.is_break = True
            
            if self.current_pomodoro_count % self.pomodoros_until_long_break == 0:
                # Long break
                self.remaining_seconds = self.long_break_duration
                self.timer_completed.emit("long_break")
            else:
                # Regular break
                self.remaining_seconds = self.break_duration
                self.timer_completed.emit("break")
        else:
            # Break completed
            self.is_break = False
            self.remaining_seconds = self.work_duration
            self.timer_completed.emit("work")
            
    def set_work_duration(self, minutes):
        """Set work duration in minutes"""
        self.work_duration = minutes * 60
        if not self.is_break and not self.running:
            self.remaining_seconds = self.work_duration
            
    def set_break_duration(self, minutes):
        """Set break duration in minutes"""
        self.break_duration = minutes * 60
        
    def set_long_break_duration(self, minutes):
        """Set long break duration in minutes"""
        self.long_break_duration = minutes * 60
        
    def set_pomodoros_until_long_break(self, count):
        """Set number of pomodoros until long break"""
        self.pomodoros_until_long_break = count
        
    def get_time_string(self):
        """Get formatted time string (MM:SS)"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_progress(self):
        """Get timer progress as percentage"""
        if self.is_break:
            total = self.long_break_duration if self.current_pomodoro_count % self.pomodoros_until_long_break == 0 else self.break_duration
        else:
            total = self.work_duration
        return ((total - self.remaining_seconds) / total) * 100 