from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QPushButton,
                             QLineEdit, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon

class ClipboardWidget(QWidget):
    def __init__(self, clipboard_manager, theme_engine, settings, parent=None):
        super().__init__(parent)
        self.clipboard_manager = clipboard_manager
        self.theme_engine = theme_engine
        self.settings = settings
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.clipboard_manager.clipboard_changed.connect(self.on_clipboard_changed)
        
    def init_ui(self):
        """Initialize the user interface"""
        # Set window flags
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Create main frame
        frame = QFrame()
        frame.setObjectName("clipboardFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(5)
        
        # Add title
        title_label = QLabel("Clipboard History")
        title_label.setObjectName("clipboardTitle")
        frame_layout.addWidget(title_label)
        
        # Add search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search clipboard history...")
        self.search_box.textChanged.connect(self.filter_history)
        frame_layout.addWidget(self.search_box)
        
        # Add clipboard list
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.copy_item)
        frame_layout.addWidget(self.history_list)
        
        # Add control buttons
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(self.clear_button)
        
        frame_layout.addLayout(button_layout)
        
        # Add frame to main layout
        layout.addWidget(frame)
        
        # Set initial size
        self.resize(300, 400)
        
        # Apply theme
        self.apply_theme()
        
        # Load initial history
        self.load_history()
        
    def apply_theme(self):
        """Apply theme to the widget"""
        # Apply base widget style
        self.setStyleSheet(self.theme_engine.get_style_sheet("QWidget"))
        
        # Apply frame style
        frame_style = """
            QFrame#clipboardFrame {
                background-color: %s;
                border: 1px solid %s;
                border-radius: %dpx;
            }
        """ % (
            self.theme_engine.get_color('background'),
            self.theme_engine.get_color('border'),
            self.theme_engine.get_theme()['border_radius']
        )
        
        # Apply title style
        title_style = """
            QLabel#clipboardTitle {
                color: %s;
                font-weight: bold;
                font-size: %dpx;
            }
        """ % (
            self.theme_engine.get_color('accent'),
            self.theme_engine.get_theme()['font_size'] + 2
        )
        
        # Apply list style
        list_style = """
            QListWidget {
                background-color: %s;
                border: 1px solid %s;
                border-radius: %dpx;
                color: %s;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid %s;
            }
            QListWidget::item:selected {
                background-color: %s;
                color: %s;
            }
            QListWidget::item:hover {
                background-color: %s;
            }
        """ % (
            self.theme_engine.get_color('background'),
            self.theme_engine.get_color('border'),
            self.theme_engine.get_theme()['border_radius'],
            self.theme_engine.get_color('text'),
            self.theme_engine.get_color('border'),
            self.theme_engine.get_color('accent'),
            self.theme_engine.get_color('background'),
            self.theme_engine.get_color('accent_secondary')
        )
        
        # Apply search box style
        search_style = self.theme_engine.get_style_sheet("QLineEdit")
        
        # Apply button style
        button_style = self.theme_engine.get_style_sheet("QPushButton")
        
        self.setStyleSheet(frame_style + title_style + list_style + search_style + button_style)
        
    def load_history(self):
        """Load clipboard history into list"""
        self.history_list.clear()
        for item in self.clipboard_manager.get_history():
            self.add_history_item(item)
            
    def add_history_item(self, text):
        """Add an item to the history list"""
        # Truncate text for display
        display_text = text[:100] + "..." if len(text) > 100 else text
        display_text = display_text.replace("\n", " ")
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, text)  # Store full text
        self.history_list.insertItem(0, item)  # Add to top of list
        
    @pyqtSlot(str)
    def on_clipboard_changed(self, text):
        """Handle clipboard content changes"""
        self.add_history_item(text)
        
    def copy_item(self, item):
        """Copy selected item back to clipboard"""
        text = item.data(Qt.UserRole)
        self.clipboard_manager.copy_to_clipboard(text)
        
    def clear_history(self):
        """Clear clipboard history"""
        self.clipboard_manager.clear_history()
        self.history_list.clear()
        
    def filter_history(self, text):
        """Filter history list based on search text"""
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            item.setHidden(text.lower() not in item.data(Qt.UserRole).lower())
            
    def toggle_visibility(self):
        """Toggle widget visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.search_box.setFocus()
            
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging"""
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept() 