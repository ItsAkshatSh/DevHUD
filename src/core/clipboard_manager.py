import pyperclip
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal
from collections import deque

class ClipboardManager(QObject):
    clipboard_changed = pyqtSignal(str)
    
    def __init__(self, max_history=20):
        super().__init__()
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self.running = False
        self.moniter_thread = None
        self.last_content = None
        
    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.moniter_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.moniter_thread.start()
            
    def stop_monitoring(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        while self.running:
            current_content = pyperclip.paste()
            if current_content != self.last_content:
                self.last_content = current_content
                self.history.append(current_content)
                self.clipboard_changed.emit(current_content)
                
            time.sleep(1)
            
    def get_histoyy(self):
        return list(self.history)
    
    def clear_history(self):
        self.history_clear()
        
    def copy_to_clipboard(self, content):
        pyperclip.copy(content)
        
    def search_history(self, query):
        query = query.lower()
        
        return [item for item in self.history if query in item.lower()]
    
    def set_max_history(self, max_items):
        self.max_history = max_items
        self.history = deque(self.history, maxlen=max_items)
        
    def remove_from_history(self, index):
        if 0 <= index < len(self.history):
            items = list(self.history)
            items.pop(index)
            self.history = deque(items, maxlen=self.max_history)
        
        