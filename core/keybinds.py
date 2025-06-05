import sys
from PyQt5.QtCore import QObject, pyqtSignal
import json
import os

if sys.platform == "win32":
    from win32con import *
    import win32api
    import win32gui
    import win32con
    import threading
    import time

class KeybindManager(QObject):
    hotkey_triggered = pyqtSignal(str)  # Signal emitted when a hotkey is triggered
    
    def __init__(self):
        super().__init__()
        self.hotkeys = {}
        self.running = False
        self.monitor_thread = None
        self.config_file = os.path.join(os.path.expanduser("~"), ".nerdhud", "hotkeys.json")
        self.load_hotkeys()
        
    def register_hotkey(self, name, key_combination, action):
        """Register a new hotkey"""
        if sys.platform == "win32":
            vk, modifiers = self._parse_key_combination(key_combination)
            if vk:
                try:
                    if win32gui.RegisterHotKey(None, len(self.hotkeys), modifiers, vk):
                        self.hotkeys[name] = {
                            'combination': key_combination,
                            'action': action,
                            'vk': vk,
                            'modifiers': modifiers
                        }
                        self.save_hotkeys()
                        return True
                except Exception as e:
                    print(f"Failed to register hotkey: {e}")
        return False
        
    def unregister_hotkey(self, name):
        """Unregister a hotkey"""
        if name in self.hotkeys and sys.platform == "win32":
            try:
                win32gui.UnregisterHotKey(None, list(self.hotkeys.keys()).index(name))
                del self.hotkeys[name]
                self.save_hotkeys()
                return True
            except Exception as e:
                print(f"Failed to unregister hotkey: {e}")
        return False
        
    def start_monitoring(self):
        """Start monitoring for hotkey triggers"""
        if not self.running and sys.platform == "win32":
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop monitoring for hotkey triggers"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop for hotkey triggers"""
        while self.running:
            try:
                msg = win32gui.GetMessage(None, 0, 0)
                if msg and msg[1][1] == win32con.WM_HOTKEY:
                    # Find the hotkey that was triggered
                    for name, hotkey in self.hotkeys.items():
                        if msg[1][2] == list(self.hotkeys.keys()).index(name):
                            self.hotkey_triggered.emit(name)
                            break
            except Exception as e:
                print(f"Error in hotkey monitoring: {e}")
            time.sleep(0.1)
            
    def _parse_key_combination(self, combination):
        """Parse key combination string into Windows virtual key codes"""
        modifiers = 0
        vk = 0
        
        parts = combination.lower().split('+')
        
        # Parse modifiers
        for part in parts[:-1]:
            part = part.strip()
            if part == 'ctrl':
                modifiers |= win32con.MOD_CONTROL
            elif part == 'alt':
                modifiers |= win32con.MOD_ALT
            elif part == 'shift':
                modifiers |= win32con.MOD_SHIFT
            elif part == 'win':
                modifiers |= win32con.MOD_WIN
                
        # Parse the main key
        key = parts[-1].strip()
        if len(key) == 1:
            # Single character key
            vk = ord(key.upper())
        else:
            # Special key
            key_map = {
                'f1': win32con.VK_F1, 'f2': win32con.VK_F2,
                'f3': win32con.VK_F3, 'f4': win32con.VK_F4,
                'f5': win32con.VK_F5, 'f6': win32con.VK_F6,
                'f7': win32con.VK_F7, 'f8': win32con.VK_F8,
                'f9': win32con.VK_F9, 'f10': win32con.VK_F10,
                'f11': win32con.VK_F11, 'f12': win32con.VK_F12,
                'space': win32con.VK_SPACE,
                'enter': win32con.VK_RETURN,
                'tab': win32con.VK_TAB,
                'esc': win32con.VK_ESCAPE,
                'backspace': win32con.VK_BACK,
                'delete': win32con.VK_DELETE,
                'home': win32con.VK_HOME,
                'end': win32con.VK_END,
                'pageup': win32con.VK_PRIOR,
                'pagedown': win32con.VK_NEXT,
                'insert': win32con.VK_INSERT
            }
            vk = key_map.get(key, 0)
            
        return vk, modifiers
        
    def save_hotkeys(self):
        """Save hotkeys to configuration file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.hotkeys, f, indent=4)
        except Exception as e:
            print(f"Failed to save hotkeys: {e}")
            
    def load_hotkeys(self):
        """Load hotkeys from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.hotkeys = json.load(f)
        except Exception as e:
            print(f"Failed to load hotkeys: {e}")
            
    def get_hotkey_action(self, name):
        """Get the action associated with a hotkey"""
        return self.hotkeys.get(name, {}).get('action')
        
    def get_all_hotkeys(self):
        """Get all registered hotkeys"""
        return {name: hotkey['combination'] for name, hotkey in self.hotkeys.items()} 