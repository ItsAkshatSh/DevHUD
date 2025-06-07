from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTabWidget, QMenu, QAction,
                             QLineEdit, QCheckBox, QComboBox, QSpinBox,
                             QFormLayout, QGroupBox, QSlider)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence

class KeybindInputWidget(QPushButton):
    """Widget for capturing keyboard shortcuts"""
    keySequenceChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setAutoDefault(False)
        self.setDefault(False)
        self.setFocusPolicy(Qt.StrongFocus)
        self._key_sequence = ""
        self.update_display()
        
    def keyPressEvent(self, event):
        if self.isChecked():
            modifiers = []
            if event.modifiers() & Qt.ControlModifier:
                modifiers.append("Ctrl")
            if event.modifiers() & Qt.AltModifier:
                modifiers.append("Alt")
            if event.modifiers() & Qt.ShiftModifier:
                modifiers.append("Shift")
            if event.modifiers() & Qt.MetaModifier:
                modifiers.append("Win")
                
            key = QKeySequence(event.key()).toString()
            if key and key not in ["Ctrl", "Alt", "Shift", "Win"]:
                if modifiers:
                    self._key_sequence = "+".join(modifiers + [key])
                else:
                    self._key_sequence = key
                self.update_display()
                self.keySequenceChanged.emit(self._key_sequence)
                self.setChecked(False)
        else:
            super().keyPressEvent(event)
            
    def update_display(self):
        """Update button text with current key sequence"""
        if self._key_sequence:
            self.setText(self._key_sequence)
        else:
            self.setText("Click to set shortcut")
            
    def set_key_sequence(self, sequence):
        """Set the key sequence"""
        self._key_sequence = sequence
        self.update_display()
        
    def get_key_sequence(self):
        """Get the current key sequence"""
        return self._key_sequence
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.setChecked(True)
            self.setText("Press keys...")
            event.accept()
        else:
            super().mousePressEvent(event)

class SettingsWidget(QWidget):
    settings_changed = pyqtSignal(dict)  # Signal when settings are changed
    
    def __init__(self, settings, theme_engine, keybind_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_engine = theme_engine
        self.keybind_manager = keybind_manager
        self.is_widget_mode = True
        
        # Initialize UI
        self.init_ui()
        
        # Connect change signals
        self.connect_change_signals()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(2)
        
        # Create header
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(2, 2, 2, 2)
        
        # Title label
        self.title_label = QLabel("Settings")
        self.title_label.setObjectName("headerTitle")
        header_layout.addWidget(self.title_label)
        
        # Mode toggle button
        self.mode_button = QPushButton()
        self.mode_button.setObjectName("modeButton")
        self.mode_button.setFixedSize(16, 16)
        self.mode_button.clicked.connect(self.toggle_mode)
        header_layout.addWidget(self.mode_button)
        
        self.main_layout.addWidget(self.header)
        
        # Create tab widget for window mode
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("settingsTabWidget")
        
        # Create tabs
        self.general_tab = self.create_general_tab()
        self.appearance_tab = self.create_appearance_tab()
        self.keybinds_tab = self.create_keybinds_tab()
        self.github_tab = self.create_github_tab()
        
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self.tab_widget.addTab(self.keybinds_tab, "Keybinds")
        self.tab_widget.addTab(self.github_tab, "GitHub")
        
        self.main_layout.addWidget(self.tab_widget)
        
        # Create compact widget view
        self.widget_view = QWidget()
        widget_layout = QVBoxLayout(self.widget_view)
        widget_layout.setContentsMargins(5, 5, 5, 5)
        widget_layout.setSpacing(2)
        
        # Quick settings in widget mode
        self.create_quick_settings()
        widget_layout.addWidget(self.quick_settings_frame)
        
        self.main_layout.addWidget(self.widget_view)
        
        # Add save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_settings)
        self.main_layout.addWidget(self.save_button)
        
        # Apply theme
        self.apply_theme()
        
        # Set initial mode
        self.set_widget_mode(True)
        
    def connect_change_signals(self):
        """Connect signals for change detection"""
        # General settings
        self.start_minimized.stateChanged.connect(self.on_setting_changed)
        self.start_with_system.stateChanged.connect(self.on_setting_changed)
        self.stats_interval.valueChanged.connect(self.on_setting_changed)
        
        # Appearance settings
        self.theme_selector.currentTextChanged.connect(self.on_setting_changed)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        self.quick_opacity.valueChanged.connect(self.on_quick_opacity_changed)
        
        # Keybind settings
        self.toggle_key.textChanged.connect(self.on_setting_changed)
        self.focus_key.textChanged.connect(self.on_setting_changed)
        self.clipboard_key.textChanged.connect(self.on_setting_changed)
        
        # GitHub settings
        self.github_token.textChanged.connect(self.on_setting_changed)
        self.github_username.textChanged.connect(self.on_setting_changed)
        
    def on_setting_changed(self):
        """Handle setting changes"""
        self.save_button.setEnabled(True)  # Enable save button when settings change
        
    def on_opacity_changed(self, value):
        """Handle opacity slider changes"""
        self.opacity_label.setText(f"{value}%")
        self.on_setting_changed()
        
    def on_quick_opacity_changed(self, value):
        """Handle quick opacity slider changes"""
        self.quick_opacity_label.setText(f"{value}%")
        self.on_setting_changed()
        
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout()
        
        self.start_minimized = QCheckBox("Start minimized")
        self.start_with_system = QCheckBox("Start with system")
        
        startup_layout.addWidget(self.start_minimized)
        startup_layout.addWidget(self.start_with_system)
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Update interval group
        update_group = QGroupBox("Update Intervals")
        update_layout = QFormLayout()
        
        self.stats_interval = QSpinBox()
        self.stats_interval.setRange(1, 60)
        self.stats_interval.setSuffix(" sec")
        
        update_layout.addRow("Stats update interval:", self.stats_interval)
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)
        
        layout.addStretch()
        return tab
        
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark", "System"])
        
        theme_layout.addRow("Theme:", self.theme_selector)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Opacity group
        opacity_group = QGroupBox("Opacity")
        opacity_layout = QVBoxLayout()
        
        # Create slider with label
        slider_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(90)  # Default to 90%
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        
        self.opacity_label = QLabel("90%")
        self.opacity_label.setMinimumWidth(40)
        self.opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        slider_layout.addWidget(self.opacity_slider)
        slider_layout.addWidget(self.opacity_label)
        
        opacity_layout.addLayout(slider_layout)
        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)
        
        layout.addStretch()
        return tab
        
    def create_keybinds_tab(self):
        """Create keybinds settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Keybinds group
        keybinds_group = QGroupBox("Global Hotkeys")
        keybinds_layout = QFormLayout()
        
        self.toggle_key = QLineEdit()
        self.focus_key = QLineEdit()
        self.clipboard_key = QLineEdit()
        
        keybinds_layout.addRow("Toggle visibility:", self.toggle_key)
        keybinds_layout.addRow("Start focus timer:", self.focus_key)
        keybinds_layout.addRow("Show clipboard:", self.clipboard_key)
        
        keybinds_group.setLayout(keybinds_layout)
        layout.addWidget(keybinds_group)
        
        layout.addStretch()
        return tab
        
    def create_github_tab(self):
        """Create GitHub integration settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # GitHub auth group
        github_group = QGroupBox("GitHub Authentication")
        github_layout = QFormLayout()
        
        self.github_token = QLineEdit()
        self.github_token.setEchoMode(QLineEdit.Password)
        self.github_username = QLineEdit()
        
        github_layout.addRow("Username:", self.github_username)
        github_layout.addRow("Access Token:", self.github_token)
        
        # Add help text
        help_label = QLabel("Token is required to access private repositories and avoid rate limits.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        github_layout.addRow("", help_label)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        layout.addStretch()
        return tab
        
    def create_quick_settings(self):
        """Create quick settings for widget mode"""
        self.quick_settings_frame = QFrame()
        self.quick_settings_frame.setObjectName("compactFrame")
        layout = QVBoxLayout(self.quick_settings_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Quick theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.quick_theme = QPushButton()
        self.quick_theme.setObjectName("themeButton")
        self.quick_theme.clicked.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.quick_theme)
        layout.addLayout(theme_layout)
        
        # Quick opacity control
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacity:")
        self.quick_opacity = QSlider(Qt.Horizontal)
        self.quick_opacity.setRange(20, 100)
        self.quick_opacity.setValue(90)
        self.quick_opacity.setTickPosition(QSlider.TicksBelow)
        self.quick_opacity.setTickInterval(10)
        
        self.quick_opacity_label = QLabel("90%")
        self.quick_opacity_label.setMinimumWidth(40)
        self.quick_opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.quick_opacity)
        opacity_layout.addWidget(self.quick_opacity_label)
        layout.addLayout(opacity_layout)
        
    def set_widget_mode(self, enabled):
        """Switch between widget and window modes"""
        self.is_widget_mode = enabled
        if enabled:
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.Tool
            )
            self.tab_widget.hide()
            self.widget_view.show()
            self.setFixedSize(200, self.sizeHint().height())
        else:
            self.setWindowFlags(
                Qt.Window |
                Qt.CustomizeWindowHint |
                Qt.WindowTitleHint |
                Qt.WindowCloseButtonHint |
                Qt.WindowMinimizeButtonHint
            )
            self.tab_widget.show()
            self.widget_view.hide()
            self.setFixedSize(400, 500)
        
        self.mode_button.setText("□" if enabled else "◈")
        self.show()
        
    def toggle_mode(self):
        """Toggle between widget and window modes"""
        self.set_widget_mode(not self.is_widget_mode)
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.theme_selector.currentText()
        if current_theme == "Light":
            self.theme_selector.setCurrentText("Dark")
        else:
            self.theme_selector.setCurrentText("Light")
        # Don't save immediately, wait for save button
        
    def save_settings(self):
        """Save current settings"""
        settings = {
            'general': {
                'start_minimized': self.start_minimized.isChecked(),
                'start_with_system': self.start_with_system.isChecked(),
                'stats_interval': self.stats_interval.value()
            },
            'appearance': {
                'theme': self.theme_selector.currentText(),
                'opacity': self.opacity_slider.value()
            },
            'keybinds': {
                'toggle_visibility': self.toggle_key.text(),
                'focus_timer': self.focus_key.text(),
                'clipboard': self.clipboard_key.text()
            },
            'github': {
                'token': self.github_token.text(),
                'username': self.github_username.text()
            }
        }
        self.settings_changed.emit(settings)
        self.save_button.setEnabled(False)  # Disable save button after saving
        
    def load_settings(self):
        """Load current settings"""
        # Load general settings
        self.start_minimized.setChecked(self.settings.get('start_minimized', False))
        self.start_with_system.setChecked(self.settings.get('start_with_system', False))
        self.stats_interval.setValue(self.settings.get('stats_interval', 1))
        
        # Load appearance settings
        current_theme = self.settings.get('theme', 'System').capitalize()
        self.theme_selector.setCurrentText(current_theme)
        
        opacity = int(self.settings.get('opacity', 0.9) * 100)  # Convert decimal to percentage
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f"{opacity}%")
        self.quick_opacity.setValue(opacity)
        self.quick_opacity_label.setText(f"{opacity}%")
        
        # Load keybind settings
        self.toggle_key.setText(self.settings.get_keybind('toggle_visibility'))
        self.focus_key.setText(self.settings.get_keybind('focus_timer'))
        self.clipboard_key.setText(self.settings.get_keybind('clipboard'))
        
        # Load GitHub settings
        self.github_token.setText(self.settings.get('github_token', ''))
        self.github_username.setText(self.settings.get('github_username', ''))
        
    def apply_theme(self):
        """Apply theme to the widget"""
        colors = {
            'background': self.theme_engine.get_color('background'),
            'foreground': self.theme_engine.get_color('foreground'),
            'accent': self.theme_engine.get_color('accent'),
            'border': self.theme_engine.get_color('border'),
        }
        
        self.setStyleSheet(f"""
            QWidget {{
                background: {colors['background']};
                color: {colors['foreground']};
                font-size: {self.theme_engine.get_theme()['font_size']}px;
            }}
            
            QFrame#compactFrame {{
                background: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
            
            QGroupBox {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin-top: 0.5em;
                padding-top: 0.5em;
            }}
            
            QGroupBox::title {{
                color: {colors['accent']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }}
            
            QPushButton {{
                background: {colors['accent']};
                color: {colors['background']};
                border: none;
                padding: 5px;
                border-radius: 2px;
            }}
            
            QPushButton:hover {{
                background: {colors['foreground']};
            }}
            
            QPushButton#saveButton {{
                background: {colors['accent']};
                color: {colors['background']};
                font-weight: bold;
                padding: 8px;
                margin-top: 10px;
            }}
            
            QPushButton#saveButton:disabled {{
                background: {colors['border']};
                color: {colors['foreground']};
            }}
            
            QLineEdit, QSpinBox, QComboBox {{
                background: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: 2px;
                padding: 2px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background: {colors['background']};
                color: {colors['foreground']};
                border: 1px solid {colors['border']};
                padding: 5px 10px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background: {colors['accent']};
                color: {colors['background']};
            }}
            
            QPushButton#modeButton {{
                background: transparent;
                border: none;
                color: {colors['accent']};
                font-size: 14px;
            }}
            
            QPushButton#themeButton {{
                background: {colors['accent']};
                color: {colors['background']};
                border-radius: 10px;
                min-width: 20px;
                min-height: 20px;
            }}
            
            QLabel#headerTitle {{
                color: {colors['accent']};
                font-weight: bold;
            }}
        """)
        
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
            
    def contextMenuEvent(self, event):
        """Show context menu on right click"""
        menu = QMenu(self)
        
        toggle_action = QAction("Toggle Mode", self)
        toggle_action.triggered.connect(self.toggle_mode)
        menu.addAction(toggle_action)
        
        menu.exec_(event.globalPos()) 