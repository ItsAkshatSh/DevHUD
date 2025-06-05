import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QWindow

class DesktopIntegration:
    def __init__(self):
        self.desktop_widget = None
        self.is_click_through = True
        
    def create_desktop_widget(self, parent=None):
        """Create a widget that will be positioned on the desktop"""
        self.desktop_widget = QWidget(parent)
        self.desktop_widget.setWindowFlags(
            Qt.FramelessWindowHint |  # No window frame
            Qt.WindowStaysOnBottomHint |  
            Qt.Tool 
        )
        self.desktop_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.desktop_widget.setAttribute(Qt.WA_NoSystemBackground)
        self.desktop_widget.setAttribute(Qt.WA_TransparentForMouseEvents, self.is_click_through)
        return self.desktop_widget
        
    def set_click_through(self, enabled):
        """Enable or disable click-through functionality"""
        self.is_click_through = enabled
        if self.desktop_widget:
            self.desktop_widget.setAttribute(Qt.WA_TransparentForMouseEvents, enabled)
            
    def position_widget(self, widget, x, y):
        """Position a widget at specific coordinates on the desktop"""
        if sys.platform == "win32":
            # Windows-specific positioning
            hwnd = widget.winId().__int__()
            import ctypes
            from ctypes import wintypes
            
            # Get the window handle
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # Set window position
            user32.SetWindowPos(
                hwnd,
                -1,  # HWND_TOPMOST
                x, y,
                0, 0,  # width, height (0 means keep current)
                0x0001  # SWP_NOSIZE
            )
        else:
            # Generic positioning for other platforms
            widget.move(x, y)
            
    def handle_resolution_change(self, widget):
        """Handle desktop resolution changes"""
        # Get the screen geometry
        screen = widget.screen()
        if screen:
            geometry = screen.geometry()
            # Adjust widget position if needed
            current_pos = widget.pos()
            if current_pos.x() > geometry.width() or current_pos.y() > geometry.height():
                new_x = min(current_pos.x(), geometry.width() - widget.width())
                new_y = min(current_pos.y(), geometry.height() - widget.height())
                widget.move(new_x, new_y)
                
    def handle_fullscreen_app(self, widget, is_fullscreen):
        """Handle fullscreen application state"""
        if is_fullscreen:
            widget.hide()
        else:
            widget.show()
            
    def get_desktop_geometry(self):
        """Get the desktop geometry"""
        if self.desktop_widget:
            screen = self.desktop_widget.screen()
            if screen:
                return screen.geometry()
        return None 
    
    def get_widget_position(self, widget):
        if widget:
            pos = widget.pos()
            return (pos.x(), pos.y())
        return (0, 0)
    
    def set_widget_position(self, widget, x, y):
        if widget:
            widget.move(QPoint(x, y))
            self.handle_resolution_change(widget)
    
    def get_widget_size(self, widget):
        if widget:
            return ( widget.width(), widget.height())
        return (0, 0)
    
    def set_widget_size(self, widget, width, height):
        if widget:
            widget_resize(width, height)
            self.handle_resolution_change(widget)