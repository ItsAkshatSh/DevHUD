from PyQt5.QtCore import QSettings
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal

class Settings(QObject):
    settings_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join(os.path.expanduser("~"), ".nerdhud", "settings.json")
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                return self._get_default_settings()
        return self._get_default_settings()
        
    def _save_settings(self):
        """Save settings to file"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
            
    def _get_default_settings(self):
        """Get default settings"""
        return {
            'theme': 'dark',
            'opacity': 0.9,
            'github_token': '',
            'github_username': '',
            'enabled_widgets': {
                'system_stats': True,
                'clipboard': True,
                'focus_timer': True,
                'github': True
            },
            'keybinds': {
                'toggle_visibility': 'ctrl+alt+h',
                'focus_timer_start': 'ctrl+alt+t',
                'clipboard_history': 'ctrl+alt+c'
            },
            'widget_positions': {
                'system_stats': [100, 100],
                'clipboard': [100, 200],
                'focus_timer': [100, 300],
                'settings': [100, 400],
                'github': [100, 500]
            }
        }
        
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self._save_settings()
        self.settings_changed.emit()
        
    def get_theme(self):
        """Get current theme"""
        return self.get('theme', 'dark')
        
    def get_opacity(self):
        """Get window opacity"""
        return self.get('opacity', 0.9)
        
    def is_enabled(self, widget_name):
        """Check if a widget is enabled"""
        return self.get('enabled_widgets', {}).get(widget_name, True)
        
    def get_keybind(self, action):
        """Get keybind for an action"""
        keybinds = self.get('keybinds', {})
        if not keybinds:
            keybinds = self._get_default_settings()['keybinds']
            self.set('keybinds', keybinds)
        return keybinds.get(action, '')
        
    def get_widget_position(self, widget_name):
        """Get widget position"""
        positions = self.get('widget_positions', {})
        return positions.get(widget_name, [100, 100])
        
    def set_widget_position(self, widget_name, x, y):
        """Set widget position"""
        if 'widget_positions' not in self.settings:
            self.settings['widget_positions'] = {}
        self.settings['widget_positions'][widget_name] = [x, y]
        self._save_settings()
        self.settings_changed.emit()
        
    def get_setting(self, key, default=None):
        """Get a setting value by key (supports nested keys with dots)"""
        try:
            value = self.settings
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set_setting(self, key, value):
        """Set a setting value by key (supports nested keys with dots)"""
        try:
            keys = key.split('.')
            target = self.settings
            for k in keys[:-1]:
                target = target[k]
            target[keys[-1]] = value
            self._save_settings()
            self.settings_changed.emit()
            return True
        except (KeyError, TypeError):
            return False
            
    def set_theme(self, theme_name):
        """Set current theme"""
        result = self.set('theme', theme_name)
        self.settings_changed.emit()
        return result
        
    def set_opacity(self, opacity):
        """Set window opacity"""
        result = self.set('opacity', max(0.1, min(1.0, opacity)))
        self.settings_changed.emit()
        return result
        
    def set_enabled(self, widget_name, enabled):
        """Enable or disable a widget"""
        if 'enabled_widgets' not in self.settings:
            self.settings['enabled_widgets'] = {}
        self.settings['enabled_widgets'][widget_name] = enabled
        self._save_settings()
        self.settings_changed.emit()
        
    def set_keybind(self, action, key_combination):
        """Set keybind for an action"""
        if 'keybinds' not in self.settings:
            self.settings['keybinds'] = {}
        self.settings['keybinds'][action] = key_combination
        self._save_settings()
        self.settings_changed.emit() 