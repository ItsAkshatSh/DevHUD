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
        self.monitor_thread = None
        self.last_content = None
        
    def start_monitoring(self):
        """Start monitoring clipboard changes"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop monitoring clipboard changes"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            current_content = pyperclip.paste()
            
            # Only process if content has changed and is not empty
            if current_content and current_content != self.last_content:
                self.last_content = current_content
                self.history.append(current_content)
                self.clipboard_changed.emit(current_content)
                
            time.sleep(0.5) 
            
    def get_history(self):
        """Get clipboard history"""
        return list(self.history)
        
    def clear_history(self):
        """Clear clipboard history"""
        self.history.clear()
        
    def copy_to_clipboard(self, content):
        """Copy content to clipboard"""
        pyperclip.copy(content)
        
    def search_history(self, query):
        """Search clipboard history for matching content"""
        query = query.lower()
        return [item for item in self.history if query in item.lower()]
        
    def set_max_history(self, max_items):
        """Set maximum number of items to keep in history"""
        self.max_history = max_items
        # Create new deque with new maxlen
        self.history = deque(self.history, maxlen=max_items)
        
    def remove_from_history(self, index):
        """Remove item from history at specified index"""
        if 0 <= index < len(self.history):
            # Convert to list, remove item, and create new deque
            items = list(self.history)
            items.pop(index)
            self.history = deque(items, maxlen=self.max_history) 
            
    def get_last_content(self):
        """gert last copied content"""
        return self.last_content if self.last_content else None
    
    def is_running(self):
        return self.running