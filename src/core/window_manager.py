from PyQt5.QtWidgets import QWidget, QSystemTrayIcon, QMenu, QApplication
from PyQt5.QtCore import Qt, QPoint, QSettings
from PyQt5.QtGui import QIcon
import json
import os

class WindowManager:
    def __init__(self):
        self.widgets = {}
        self.settings = QSettings("NerdHUD", "WindowPositions")
        self.tray_icon = None
        self.is_minimized = False
        
    def create_widget(self, widget_id, widget_class, parent=None):
        """Create and register a new widget"""
        widget = widget_class(parent)
        self.widgets[widget_id] = widget
        self.load_widget_position(widget_id, widget)
        return widget
        
    def load_widget_position(self, widget_id, widget):
        """Load saved position for a widget"""
        pos = self.settings.value(f"{widget_id}/position")
        if pos:
            widget.move(QPoint(pos.x(), pos.y()))
            
    def save_widget_position(self, widget_id, widget):
        """Save widget position"""
        self.settings.setValue(f"{widget_id}/position", widget.pos())
        
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("resources/icon.png"))  # You'll need to create this icon
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show_all_widgets)
        
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide_all_widgets)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def show_all_widgets(self):
        """Show all registered widgets"""
        for widget in self.widgets.values():
            widget.show()
        self.is_minimized = False
        
    def hide_all_widgets(self):
        """Hide all registered widgets"""
        for widget in self.widgets.values():
            widget.hide()
        self.is_minimized = True
        
    def minimize_to_tray(self):
        """Minimize application to system tray"""
        self.hide_all_widgets()
        if self.tray_icon:
            self.tray_icon.showMessage(
                "NerdHUD",
                "Application minimized to system tray",
                QSystemTrayIcon.Information,
                2000
            )
            
    def quit_application(self):
        """Save positions and quit the application"""
        for widget_id, widget in self.widgets.items():
            self.save_widget_position(widget_id, widget)
        QApplication.quit()
        
    def set_widget_opacity(self, widget_id, opacity):
        """Set widget opacity (0.0 to 1.0)"""
        if widget_id in self.widgets:
            self.widgets[widget_id].setWindowOpacity(opacity)
            
    def set_widget_always_on_top(self, widget_id, always_on_top):
        """Set whether widget should always be on top"""
        if widget_id in self.widgets:
            flags = self.widgets[widget_id].windowFlags()
            if always_on_top:
                flags |= Qt.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowStaysOnTopHint
            self.widgets[widget_id].setWindowFlags(flags)
            self.widgets[widget_id].show()  # Need to show after changing flags 