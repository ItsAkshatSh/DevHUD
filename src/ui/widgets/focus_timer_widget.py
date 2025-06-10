from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon

class FocusTimerWidget(QWidget):
    def __init__(self, focus_timer, theme_engine, settings, parent=None):
        super().__init__(parent)
        self.focus_timer = focus_timer
        self.theme_engine = theme_engine
        self.settings = settings
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.focus_timer.time_updated.connect(self.update_time)
        self.focus_timer.timer_completed.connect(self.on_timer_completed)
        self.focus_timer.state_changed.connect(self.on_state_changed)
        
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
        frame.setObjectName("timerFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(5)
        
        # Add title
        title_label = QLabel("Focus Timer")
        title_label.setObjectName("timerTitle")
        frame_layout.addWidget(title_label)
        
        # Add timer display
        self.time_label = QLabel("25:00")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.time_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        frame_layout.addWidget(self.progress_bar)
        
        # Add status label
        self.status_label = QLabel("Ready to start")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.status_label)
        
        # Add control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_button)
        
        frame_layout.addLayout(button_layout)
        
        # Add frame to main layout
        layout.addWidget(frame)
        
        # Set initial size
        self.resize(200, 200)
        
        # Apply theme
        self.apply_theme()
        
    def apply_theme(self):
        """Apply theme to the widget"""
        # Apply base widget style
        self.setStyleSheet(self.theme_engine.get_style_sheet("QWidget"))
        
        # Apply frame style
        frame_style = """
            QFrame#timerFrame {
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
            QLabel#timerTitle {
                color: %s;
                font-weight: bold;
                font-size: %dpx;
            }
        """ % (
            self.theme_engine.get_color('accent'),
            self.theme_engine.get_theme()['font_size'] + 2
        )
        
        # Apply time label style
        time_style = """
            QLabel#timeLabel {
                color: %s;
                font-size: %dpx;
                font-weight: bold;
            }
        """ % (
            self.theme_engine.get_color('text'),
            self.theme_engine.get_theme()['font_size'] + 8
        )
        
        # Apply status label style
        status_style = """
            QLabel#statusLabel {
                color: %s;
                font-size: %dpx;
            }
        """ % (
            self.theme_engine.get_color('text_secondary'),
            self.theme_engine.get_theme()['font_size']
        )
        
        # Apply progress bar style
        progress_style = self.theme_engine.get_style_sheet("QProgressBar")
        
        # Apply button style
        button_style = self.theme_engine.get_style_sheet("QPushButton")
        
        self.setStyleSheet(frame_style + title_style + time_style + status_style + progress_style + button_style)
        
    @pyqtSlot(int)
    def update_time(self, seconds):
        """Update displayed time"""
        self.time_label.setText(self.focus_timer.get_time_string())
        self.progress_bar.setValue(int(self.focus_timer.get_progress()))
        
    @pyqtSlot(str)
    def on_timer_completed(self, timer_type):
        """Handle timer completion"""
        if timer_type == "work":
            self.status_label.setText("Work session completed! Take a break.")
        elif timer_type == "break":
            self.status_label.setText("Break completed! Ready to work?")
        elif timer_type == "long_break":
            self.status_label.setText("Long break completed! Ready for a new session?")
            
    @pyqtSlot(str)
    def on_state_changed(self, state):
        """Handle timer state changes"""
        if state == "started":
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.pause_button.setText("Pause")
            self.status_label.setText("Focus time!")
        elif state == "paused":
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.pause_button.setText("Resume")
            self.status_label.setText("Timer paused")
        elif state == "resumed":
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.pause_button.setText("Pause")
            self.status_label.setText("Focus time!")
        elif state == "stopped":
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.pause_button.setText("Pause")
            self.status_label.setText("Timer stopped")
            
    def start_timer(self):
        """Start the timer"""
        self.focus_timer.start_timer()
        
    def pause_timer(self):
        """Pause or resume the timer"""
        if self.focus_timer.paused:
            self.focus_timer.resume_timer()
        else:
            self.focus_timer.pause_timer()
            
    def reset_timer(self):
        """Reset the timer"""
        self.focus_timer.reset_timer()
        self.status_label.setText("Ready to start")
        
    def toggle_timer(self):
        """Toggle timer start/pause"""
        if not self.focus_timer.running:
            self.start_timer()
        else:
            self.pause_timer()
            
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