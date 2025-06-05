from PyQt5.QtCore import QObject
from keyboard import add_hotkey, remove_hotkey

class KeybindManager(QObject):
    def __init__(self):
        super().__init__()
        self.hotkeys = {}
        self.monitoring = False
        self.default_keybinds = {
            'toggle_visibility': 'ctrl+alt+h',
            'focus_timer_start': 'ctrl+alt+t',
            'clipboard_history': 'ctrl+alt+c'
        }
        
    def register_hotkey(self, action, key_combo, callback):
        """Register a hotkey combination"""
        if not key_combo:
            key_combo = self.default_keybinds.get(action, '')
            
        if not key_combo:
            print(f"Warning: No keybind specified for {action}, using default")
            return
            
        if action in self.hotkeys:
            try:
                remove_hotkey(self.hotkeys[action])
            except:
                pass
                
        try:
            add_hotkey(key_combo, callback)
            self.hotkeys[action] = key_combo
        except Exception as e:
            print(f"Error registering hotkey {key_combo} for {action}: {e}")
            
    def unregister_hotkey(self, name):
        """Unregister a global hotkey"""
        if name in self.hotkeys:
            key_combo, _ = self.hotkeys[name]
            remove_hotkey(key_combo)
            del self.hotkeys[name]
            
    def start_monitoring(self):
        """Start monitoring for hotkeys"""
        self.monitoring = True
        for action, key_combo in self.hotkeys.items():
            add_hotkey(key_combo, self.hotkeys[action])
            
    def stop_monitoring(self):
        """Stop monitoring for hotkeys"""
        self.monitoring = False
        for action, key_combo in self.hotkeys.items():
            try:
                remove_hotkey(key_combo)
            except:
                pass
        self.hotkeys.clear()
            
    def clear_hotkeys(self):
        for name in list(self).hotkeys.keys():
            self.unregister_hotkey(name)
            
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.stop_monitoring()
        except:
            pass
    
    def __contains__(self, name):
        return name in self.hotkeys
    def __getitem__(self, name):
        return self.hotkeys[name] if name in self.hotkeys else None