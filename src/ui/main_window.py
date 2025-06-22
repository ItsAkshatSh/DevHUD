from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSystemTrayIcon, QMenu, QApplication)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QMouseEvent
from .widgets.system_stats_widget import SystemStatsWidget
from .widgets.clipboard_widget import ClipboardWidget
from .widgets.focus_timer_widget import FocusTimerWidget
from .widgets.settings_widget import SettingsWidget
from .widgets.github_widget import GitHubWidget
from ui.widgets.spotify_widget import SpotifyWidget

class MainWindow(QMainWindow):
    def __init__(self, desktop_integration, window_manager, system_stats,
                 clipboard_manager, focus_timer, keybind_manager, theme_engine, settings,
                 github_manager):
        super().__init__()
        
        self.desktop_integration = desktop_integration
        self.window_manager = window_manager
        self.system_stats = system_stats
        self.clipboard_manager = clipboard_manager
        self.focus_timer = focus_timer
        self.keybind_manager = keybind_manager
        self.theme_engine = theme_engine
        self.settings = settings
        self.github_manager = github_manager
        
        # Initialize widgets list
        self.widgets = {}
        
        # Apply initial opacity from settings
        opacity = self.settings.get_opacity()
        self.setWindowOpacity(opacity)
        
        self.init_ui()
        
        self.setup_system_tray()
        
        self.setup_keybinds()
        
        self.start_services()
        
        # Initialize Spotify widget
        self.spotify_widget = SpotifyWidget(
            self.desktop_integration,
            self.theme_engine,
            self.settings
        )
        # Get saved position or use default
        x, y = self.settings.get_widget_position('spotify')
        self.spotify_widget.move(x, y)
        self.spotify_widget.show()
        self.spotify_widget.setWindowOpacity(self.settings.get_opacity())
        self.widgets['spotify_widget'] = self.spotify_widget
        
        # Initialize other widgets
        if self.settings.is_enabled('system_stats'):
            self.stats_widget = SystemStatsWidget(
                self.system_stats,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('system_stats')
            self.stats_widget.move(x, y)
            self.stats_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.stats_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.stats_widget.show()
            self.stats_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['stats_widget'] = self.stats_widget
            
        if self.settings.is_enabled('clipboard'):
            self.clipboard_widget = ClipboardWidget(
                self.clipboard_manager,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('clipboard')
            self.clipboard_widget.move(x, y)
            self.clipboard_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.clipboard_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.clipboard_widget.show()
            self.clipboard_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['clipboard_widget'] = self.clipboard_widget
            
        if self.settings.is_enabled('focus_timer'):
            self.timer_widget = FocusTimerWidget(
                self.focus_timer,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('focus_timer')
            self.timer_widget.move(x, y)
            self.timer_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.timer_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.timer_widget.show()
            self.timer_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['timer_widget'] = self.timer_widget
            
        self.settings_widget = SettingsWidget(
            self.settings,
            self.theme_engine,
            self.keybind_manager
        )
        x, y = self.settings.get_widget_position('settings')
        self.settings_widget.move(x, y)
        self.settings_widget.hide()
        self.settings_widget.setWindowOpacity(self.settings.get_opacity())
        self.widgets['settings_widget'] = self.settings_widget
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        
        # GitHub Widget
        if self.settings.is_enabled('github'):
            self.github_widget = GitHubWidget(
                self.github_manager,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('github')
            self.github_widget.move(x, y)
            self.github_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.github_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.github_widget.show()
            self.github_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['github_widget'] = self.github_widget
            
        # Start GitHub monitoring after all widgets are initialized
        self.github_manager.start_monitoring()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_widgets()
        
        self.apply_theme()
        
        self.restore_window_state()
        
    def create_widgets(self):
        """Create and setup widgets"""
        if self.settings.is_enabled('system_stats'):
            self.stats_widget = SystemStatsWidget(
                self.system_stats,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('system_stats')
            self.stats_widget.move(x, y)
            self.stats_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.stats_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.stats_widget.show()
            self.stats_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['stats_widget'] = self.stats_widget
            
        if self.settings.is_enabled('clipboard'):
            self.clipboard_widget = ClipboardWidget(
                self.clipboard_manager,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('clipboard')
            self.clipboard_widget.move(x, y)
            self.clipboard_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.clipboard_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.clipboard_widget.show()
            self.clipboard_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['clipboard_widget'] = self.clipboard_widget
            
        if self.settings.is_enabled('focus_timer'):
            self.timer_widget = FocusTimerWidget(
                self.focus_timer,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('focus_timer')
            self.timer_widget.move(x, y)
            self.timer_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.timer_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.timer_widget.show()
            self.timer_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['timer_widget'] = self.timer_widget
            
        self.settings_widget = SettingsWidget(
            self.settings,
            self.theme_engine,
            self.keybind_manager
        )
        x, y = self.settings.get_widget_position('settings')
        self.settings_widget.move(x, y)
        self.settings_widget.hide()
        self.settings_widget.setWindowOpacity(self.settings.get_opacity())
        self.widgets['settings_widget'] = self.settings_widget
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        
        # GitHub Widget
        if self.settings.is_enabled('github'):
            self.github_widget = GitHubWidget(
                self.github_manager,
                self.theme_engine,
                self.settings
            )
            x, y = self.settings.get_widget_position('github')
            self.github_widget.move(x, y)
            self.github_widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnBottomHint |
                Qt.Tool
            )
            self.github_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.github_widget.show()
            self.github_widget.setWindowOpacity(self.settings.get_opacity())
            self.widgets['github_widget'] = self.github_widget
            
        # Start GitHub monitoring after all widgets are initialized
        self.github_manager.start_monitoring()
        
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("resources/DevHUD.ico"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Add actions
        show_action = tray_menu.addAction("Show All")
        show_action.triggered.connect(self.show_all)
        
        hide_action = tray_menu.addAction("Hide All")
        hide_action.triggered.connect(self.hide_all)
        
        tray_menu.addSeparator()
        
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # Connect double-click signal
        self.tray_icon.activated.connect(self.handle_tray_activation)
        
        self.tray_icon.show()
        
    def handle_tray_activation(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_settings()
            
    def setup_keybinds(self):
        """Setup global hotkeys"""
        # Toggle visibility
        toggle_key = self.settings.get_keybind("toggle_visibility")
        if not toggle_key:
            toggle_key = "ctrl+alt+h"
            self.settings.set_keybind("toggle_visibility", toggle_key)
        self.keybind_manager.register_hotkey(
            "toggle_visibility",
            toggle_key,
            self.toggle_visibility
        )
        
        # Start focus timer
        focus_key = self.settings.get_keybind("focus_timer_start")
        if not focus_key:
            focus_key = "ctrl+alt+t"
            self.settings.set_keybind("focus_timer_start", focus_key)
        self.keybind_manager.register_hotkey(
            "focus_timer_start",
            focus_key,
            self.toggle_focus_timer
        )
        
        # Show clipboard history
        clipboard_key = self.settings.get_keybind("clipboard_history")
        if not clipboard_key:
            clipboard_key = "ctrl+alt+c"
            self.settings.set_keybind("clipboard_history", clipboard_key)
        self.keybind_manager.register_hotkey(
            "clipboard_history",
            clipboard_key,
            self.toggle_clipboard_history
        )
        
        # Start monitoring
        self.keybind_manager.start_monitoring()
        
    def start_services(self):
        """Start background services"""
        if self.settings.is_enabled('system_stats'):
            self.system_stats.start_monitoring()
            
        if self.settings.is_enabled('clipboard'):
            self.clipboard_manager.start_monitoring()
            
    def apply_theme(self):
        """Apply current theme to all widgets"""
        theme = self.settings.get_theme()
        self.theme_engine.apply_theme(theme)
        
        # Set window opacity for all widgets
        opacity = self.settings.get_opacity()
        self.setWindowOpacity(opacity)
        for widget_name, widget in self.widgets.items():
            widget.setWindowOpacity(opacity)
            widget.apply_theme()
                
    def restore_window_state(self):
        """Restore window position and state"""
        # Load widget positions from settings
        for widget in self.widgets.values():
            name = widget.__class__.__name__.lower()
            x, y = self.settings.get_widget_position(name)
            widget.move(x, y)
        
    def save_window_state(self):
        """Save window position and state"""
        # Save widget positions
        for widget in self.widgets.values():
            name = widget.__class__.__name__.lower()
            self.settings.set_widget_position(name, widget.x(), widget.y())
            
    def show_all(self):
        """Show all widgets"""
        for widget in self.widgets.values():
            if widget != self.settings_widget:  # Don't show settings automatically
                widget.show()
                
    def hide_all(self):
        """Hide all widgets"""
        for widget in self.widgets.values():
            widget.hide()
            
    def toggle_visibility(self):
        """Toggle visibility of all widgets"""
        if any(widget.isVisible() for widget in self.widgets.values() if widget != self.settings_widget):
            self.hide_all()
        else:
            self.show_all()
            
    def toggle_focus_timer(self):
        """Toggle focus timer"""
        if hasattr(self, 'timer_widget'):
            self.timer_widget.toggle_timer()
            
    def toggle_clipboard_history(self):
        """Toggle clipboard history widget"""
        if hasattr(self, 'clipboard_widget'):
            self.clipboard_widget.toggle_visibility()
            
    def show_settings(self):
        """Show settings dialog"""
        self.settings_widget.show()
        self.settings_widget.set_widget_mode(False)  # Show in window mode
        self.settings_widget.setWindowOpacity(1.0)  # Full opacity for settings window
        
    def quit_application(self):
        """Clean up and quit the application"""
        # Save window state
        self.save_window_state()
        
        # Stop services
        self.system_stats.stop_monitoring()
        self.clipboard_manager.stop_monitoring()
        self.keybind_manager.stop_monitoring()
        
        # Quit application
        QApplication.quit()
        
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()  # Prevent closing
        self.hide_all()  # Hide instead of close 

    def on_settings_changed(self):
        """Handle settings changed signal"""
        # Apply theme and opacity changes
        self.apply_theme()
        
        # Apply always on top setting
        if self.settings.get('always_on_top', False):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show() # Re-show window to apply flags 