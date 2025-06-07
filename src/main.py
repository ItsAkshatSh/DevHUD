import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from core.desktop_integration import DesktopIntegration
from core.window_manager import WindowManager
from core.system_stats import SystemStats
from core.clipboard_manager import ClipboardManager
from core.focus_timer import FocusTimer
from core.keybind_manager import KeybindManager
from core.theme_engine import ThemeEngine
from core.settings import Settings
from core.github_manager import GitHubManager
from ui.main_window import MainWindow

class NerdHUD:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.settings = Settings()
        self.theme_engine = ThemeEngine(self.settings)
        
        self.desktop_integration = DesktopIntegration()
        self.window_manager = WindowManager()
        self.system_stats = SystemStats()
        self.clipboard_manager = ClipboardManager()
        self.focus_timer = FocusTimer()
        self.keybind_manager = KeybindManager()
        self.github_manager = GitHubManager(self.settings)
        
        self.main_window = MainWindow(
            self.desktop_integration,
            self.window_manager,
            self.system_stats,
            self.clipboard_manager,
            self.focus_timer,
            self.keybind_manager,
            self.theme_engine,
            self.settings,
            self.github_manager
        )
        
        # Apply initial theme
        self.theme_engine.apply_theme(self.settings.get_theme())
        
    def run(self):
        """Start the application"""
        self.main_window.show()
        return self.app.exec_()

def main():
    app_dir = os.path.join(os.path.expanduser("~"), ".nerdhud")
    os.makedirs(app_dir, exist_ok=True)
    
    nerdhud = NerdHUD()
    sys.exit(nerdhud.run())

if __name__ == "__main__":
    main() 