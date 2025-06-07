from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
import json
import os

class ThemeEngine:
    def __init__(self, settings):
        self.settings = settings
        self.themes = self._load_themes()
        self.current_theme = self.settings.get_theme()
        
    def _load_themes(self):
        """Load themes from themes directory"""
        themes = {
            'dark': {
                'name': 'Dark Theme',
                'colors': {
                    'background': '#1E1E1E',
                    'foreground': '#FFFFFF',
                    'accent': '#007ACC',
                    'accent_secondary': '#005999',
                    'warning': '#FF0000',
                    'success': '#00FF00',
                    'error': '#FF0000',
                    'text': '#FFFFFF',
                    'text_secondary': '#CCCCCC',
                    'border': '#333333'
                },
                'background_color': '#1E1E1E',
                'text_color': '#FFFFFF',
                'accent_color': '#007ACC',
                'border_color': '#333333',
                'hover_color': '#2D2D2D',
                'font_family': 'Segoe UI',
                'font_size': 12,
                'border_radius': 4,
                'padding': 8,
                'opacity': 0.9
            },
            'light': {
                'name': 'Light Theme',
                'colors': {
                    'background': '#FFFFFF',
                    'foreground': '#000000',
                    'accent': '#0078D4',
                    'accent_secondary': '#005A9E',
                    'warning': '#FF0000',
                    'success': '#00FF00',
                    'error': '#FF0000',
                    'text': '#000000',
                    'text_secondary': '#666666',
                    'border': '#CCCCCC'
                },
                'background_color': '#FFFFFF',
                'text_color': '#000000',
                'accent_color': '#0078D4',
                'border_color': '#CCCCCC',
                'hover_color': '#F0F0F0',
                'font_family': 'Segoe UI',
                'font_size': 12,
                'border_radius': 4,
                'padding': 8,
                'opacity': 0.9
            },
            'cyber': {
                'name': 'Cyber Theme',
                'colors': {
                    'background': '#0A0A0A',
                    'foreground': '#00FF00',
                    'accent': '#FF00FF',
                    'accent_secondary': '#CC00CC',
                    'warning': '#FFFF00',
                    'success': '#00FF00',
                    'error': '#FF0000',
                    'text': '#00FF00',
                    'text_secondary': '#00CC00',
                    'border': '#00FF00'
                },
                'background_color': '#0A0A0A',
                'text_color': '#00FF00',
                'accent_color': '#FF00FF',
                'border_color': '#00FF00',
                'hover_color': '#1A1A1A',
                'font_family': 'Consolas',
                'font_size': 12,
                'border_radius': 0,
                'padding': 8,
                'opacity': 0.9
            }
        }
        return themes
        
    def get_theme(self):
        """Get current theme data"""
        return self.themes.get(self.current_theme, self.themes['dark'])
        
    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.themes.keys())
        
    def apply_theme(self, theme_name):
        """Apply a theme by name"""
        theme_name = theme_name.lower()
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.settings.set_theme(theme_name)
            return True
        return False
        
    def get_theme_css(self):
        """Get CSS styles for current theme"""
        theme = self.get_theme()
        return f"""
            QWidget {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                font-family: {theme['font_family']};
                font-size: {theme['font_size']}px;
                border-radius: {theme['border_radius']}px;
                padding: {theme['padding']}px;
            }}
            
            QPushButton {{
                background-color: {theme['accent_color']};
                color: {theme['background_color']};
                border: 1px solid {theme['border_color']};
                padding: 5px 10px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['hover_color']};
            }}
            
            QLabel {{
                color: {theme['text_color']};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {theme['background_color']};
                border: 1px solid {theme['border_color']};
                color: {theme['text_color']};
                padding: 5px;
            }}
            
            QMenu {{
                background-color: {theme['background_color']};
                border: 1px solid {theme['border_color']};
            }}
            
            QMenu::item {{
                padding: 5px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme['hover_color']};
            }}
            
            QGroupBox {{
                border: 1px solid {theme['border_color']};
                border-radius: {theme['border_radius']}px;
                margin-top: 1em;
                padding-top: 0.5em;
            }}
            
            QGroupBox::title {{
                color: {theme['accent_color']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {theme['border_color']};
                border-radius: {theme['border_radius']}px;
            }}
            
            QTabBar::tab {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                padding: 5px 10px;
                border-top-left-radius: {theme['border_radius']}px;
                border-top-right-radius: {theme['border_radius']}px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme['accent_color']};
                color: {theme['background_color']};
            }}
        """
        
    def get_color(self, color_name):
        """Get a color from the current theme"""
        theme = self.get_theme()
        return theme['colors'].get(color_name)
        
    def get_style_sheet(self, widget_type):
        """Get QSS style sheet for a widget type"""
        theme = self.get_theme()
        colors = theme['colors']
        border_radius = theme['border_radius']
        font_family = theme['font_family']
        font_size = theme['font_size']
        
        base_style = f"""
            {widget_type} {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius}px;
                font-family: {font_family};
                font-size: {font_size}px;
            }}
        """
        
        if widget_type == "QPushButton":
            return base_style + f"""
                QPushButton:hover {{
                    background-color: {colors['accent']};
                    color: {colors['background']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['accent_secondary']};
                }}
            """
        elif widget_type == "QLabel":
            return base_style
        elif widget_type == "QLineEdit":
            return base_style + f"""
                QLineEdit:focus {{
                    border: 2px solid {colors['accent']};
                }}
            """
        elif widget_type == "QProgressBar":
            return f"""
                QProgressBar {{
                    border: 1px solid {colors['border']};
                    border-radius: {border_radius}px;
                    text-align: center;
                    background-color: {colors['background']};
                }}
                QProgressBar::chunk {{
                    background-color: {colors['accent']};
                    border-radius: {border_radius}px;
                }}
            """
            
        return base_style
        
    def create_custom_theme(self, name, colors, opacity=0.9, border_radius=10, font_family="Arial", font_size=12):
        """Create a custom theme"""
        self.themes[name] = {
            'name': name,
            'colors': colors,
            'background_color': colors['background'],
            'text_color': colors['text'],
            'accent_color': colors['accent'],
            'border_color': colors['border'],
            'hover_color': colors['accent_secondary'],
            'opacity': opacity,
            'border_radius': border_radius,
            'font_family': font_family,
            'font_size': font_size,
            'padding': 8
        }
        self.save_themes()
        
    def save_themes(self):
        """Save custom themes to file"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".nerdhud")
            os.makedirs(config_dir, exist_ok=True)
            
            with open(os.path.join(config_dir, "themes.json"), 'w') as f:
                json.dump(self.themes, f, indent=4)
        except Exception as e:
            print(f"Failed to save themes: {e}")
            
    def load_themes(self):
        """Load custom themes from file"""
        try:
            theme_file = os.path.join(os.path.expanduser("~"), ".nerdhud", "themes.json")
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    custom_themes = json.load(f)
                    self.themes.update(custom_themes)
        except Exception as e:
            print(f"Failed to load themes: {e}")
            
    def get_available_themes(self):
        """Get list of available themes"""
        return list(self.themes.keys()) 
    
    