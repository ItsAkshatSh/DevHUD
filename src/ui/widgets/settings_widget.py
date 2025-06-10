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
    settings_changed = pyqtSignal()  # Signal for settings changes
    
    def __init__(self, settings, theme_engine, keybind_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_engine = theme_engine
        self.keybind_manager = keybind_manager
        self.is_widget_mode = True
        self.drag_position = None
        self.has_unsaved_changes = False
        
        # Initialize UI
        self.init_ui()
        
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
        self.appearance_tab = self.create_appearance_tab()
        self.behavior_tab = self.create_behavior_tab()
        self.github_tab = self.create_github_tab()
        
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self.tab_widget.addTab(self.behavior_tab, "Behavior")
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
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setObjectName("saveButton")
        self.save_button.setEnabled(False) # Initially disabled
        self.save_button.clicked.connect(self.save_settings)
        self.main_layout.addWidget(self.save_button)
        
        # Apply theme
        self.apply_theme()
        
        # Set initial mode
        self.set_widget_mode(True)
        
        # Load settings
        self.load_settings()
        
        # Connect change signals
        self.connect_change_signals()
        
    def connect_change_signals(self):
        """Connect signals for change detection"""
        # Theme changes
        if hasattr(self, 'theme_combo'):
            self.theme_combo.currentTextChanged.connect(self.on_setting_changed)
        if hasattr(self, 'quick_theme_combo'):
            self.quick_theme_combo.currentTextChanged.connect(self.on_setting_changed)
            
        # Opacity changes
        if hasattr(self, 'opacity_slider'):
            self.opacity_slider.valueChanged.connect(self.on_setting_changed)
        if hasattr(self, 'quick_opacity_slider'):
            self.quick_opacity_slider.valueChanged.connect(self.on_setting_changed)
            
        # Behavior changes
        if hasattr(self, 'always_on_top'):
            self.always_on_top.stateChanged.connect(self.on_setting_changed)
        if hasattr(self, 'auto_hide'):
            self.auto_hide.stateChanged.connect(self.on_setting_changed)
            
        # GitHub changes
        if hasattr(self, 'github_username'):
            self.github_username.textChanged.connect(self.on_setting_changed)
        if hasattr(self, 'github_token'):
            self.github_token.textChanged.connect(self.on_setting_changed)
            
    def on_setting_changed(self):
        """Handle any setting change"""
        self.has_unsaved_changes = True
        self.save_button.setEnabled(True)
        
        # Update opacity value label if slider is the source of change
        if self.sender() == self.opacity_slider or self.sender() == self.quick_opacity_slider:
            if hasattr(self, 'opacity_value'):
                self.opacity_value.setText(f"{self.opacity_slider.value()}%")
            if hasattr(self, 'quick_opacity_label'):
                self.quick_opacity_label.setText(f"{self.quick_opacity_slider.value()}%")
        
    def save_settings(self):
        """Save all settings"""
        if not self.has_unsaved_changes:
            return
            
        # Save appearance settings
        self.settings.set('theme', self.theme_combo.currentText())
        self.settings.set('opacity', self.opacity_slider.value() / 100.0)
        
        # Save behavior settings
        self.settings.set('always_on_top', self.always_on_top.isChecked())
        self.settings.set('auto_hide', self.auto_hide.isChecked())
        
        # Save GitHub settings
        self.settings.set('github_username', self.github_username.text())
        self.settings.set('github_token', self.github_token.text())
        
        # Apply theme changes immediately
        self.theme_engine.apply_theme(self.settings.get_theme())
        
        # Disable save button
        self.save_button.setEnabled(False)
        self.has_unsaved_changes = False
        
        # Notify other widgets
        self.settings_changed.emit()
        
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_engine.get_available_themes())
        self.theme_combo.currentTextChanged.connect(self.on_setting_changed)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.settings.get('opacity', 1.0) * 100))
        self.opacity_slider.valueChanged.connect(self.on_setting_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_value = QLabel(f"{self.opacity_slider.value()}%")
        opacity_layout.addWidget(self.opacity_value)
        layout.addLayout(opacity_layout)
        
        layout.addStretch()
        return tab
        
    def create_behavior_tab(self):
        """Create behavior settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Always on top
        self.always_on_top = QCheckBox("Always on top")
        self.always_on_top.setChecked(self.settings.get('always_on_top', False))
        self.always_on_top.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.always_on_top)
        
        # Auto hide
        self.auto_hide = QCheckBox("Auto hide when not focused")
        self.auto_hide.setChecked(self.settings.get('auto_hide', False))
        self.auto_hide.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.auto_hide)
        
        layout.addStretch()
        return tab
        
    def create_github_tab(self):
        """Create GitHub settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # GitHub username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("GitHub Username:"))
        self.github_username = QLineEdit()
        self.github_username.setText(self.settings.get('github_username', ''))
        self.github_username.textChanged.connect(self.on_setting_changed)
        username_layout.addWidget(self.github_username)
        layout.addLayout(username_layout)
        
        # GitHub token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("GitHub Token:"))
        self.github_token = QLineEdit()
        self.github_token.setEchoMode(QLineEdit.Password)
        self.github_token.setText(self.settings.get('github_token', ''))
        self.github_token.textChanged.connect(self.on_setting_changed)
        token_layout.addWidget(self.github_token)
        layout.addLayout(token_layout)
        
        layout.addStretch()
        return tab
        
    def create_quick_settings(self):
        """Create quick settings display for widget mode"""
        self.quick_settings_frame = QFrame()
        self.quick_settings_frame.setObjectName("compactFrame")
        layout = QVBoxLayout(self.quick_settings_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.quick_theme_combo = QComboBox()
        self.quick_theme_combo.addItems(["Dark", "Light", "System"])
        self.quick_theme_combo.currentTextChanged.connect(self.on_setting_changed)
        theme_layout.addWidget(self.quick_theme_combo)
        layout.addLayout(theme_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.quick_opacity_slider = QSlider(Qt.Horizontal)
        self.quick_opacity_slider.setRange(20, 100)
        self.quick_opacity_slider.setValue(int(self.settings.get('opacity', 0.8) * 100))
        self.quick_opacity_slider.valueChanged.connect(self.on_setting_changed)
        opacity_layout.addWidget(self.quick_opacity_slider)
        self.quick_opacity_label = QLabel(f"{self.quick_opacity_slider.value()}%")
        opacity_layout.addWidget(self.quick_opacity_label)
        layout.addLayout(opacity_layout)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)
        
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
        
    def on_theme_changed(self, theme):
        """Handle theme change"""
        self.theme_engine.apply_theme(theme.lower())
        self.apply_theme()  # Reapply theme to this widget
        self.show()  # Ensure widget stays visible
        
    def on_font_size_changed(self, size):
        """Handle font size change"""
        sizes = {
            "Small": 12,
            "Medium": 14,
            "Large": 16
        }
        self.theme_engine.set_font_size(sizes[size])
        
    def on_opacity_changed(self, value):
        """Handle opacity change"""
        self.opacity_value.setText(f"{value}%")
        opacity = value / 100.0
        self.settings.set('opacity', opacity)
        self.theme_engine.set_opacity(opacity)
        
    def on_quick_opacity_changed(self, value):
        """Handle quick opacity change"""
        self.quick_opacity_label.setText(f"{value}%")
        opacity = value / 100.0
        self.settings.set('opacity', opacity)
        self.theme_engine.set_opacity(opacity)
        
    def on_github_username_changed(self, username):
        """Handle GitHub username change"""
        self.settings.set('github_username', username)
        
    def on_github_token_changed(self, token):
        """Handle GitHub token change"""
        self.settings.set('github_token', token)
        
    def load_settings(self):
        """Load all settings"""
        # Load appearance settings
        current_theme = self.settings.get('theme', 'dark').capitalize()
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setCurrentText(current_theme)
        if hasattr(self, 'quick_theme_combo'):
            self.quick_theme_combo.setCurrentText(current_theme)
        
        opacity = int(self.settings.get('opacity', 0.8) * 100)
        if hasattr(self, 'opacity_slider'):
            self.opacity_slider.setValue(opacity)
            self.opacity_value.setText(f"{opacity}%")
        if hasattr(self, 'quick_opacity_slider'):
            self.quick_opacity_slider.setValue(opacity)
            self.quick_opacity_label.setText(f"{opacity}%")
        
        # Load behavior settings
        if hasattr(self, 'always_on_top'):
            self.always_on_top.setChecked(self.settings.get('always_on_top', True))
        if hasattr(self, 'auto_hide'):
            self.auto_hide.setChecked(self.settings.get('auto_hide', False))
        
        # Load GitHub settings
        if hasattr(self, 'github_username'):
            self.github_username.setText(self.settings.get('github_username', ''))
        if hasattr(self, 'github_token'):
            self.github_token.setText(self.settings.get('github_token', ''))
        
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
        if event.buttons() & Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()
            
    def contextMenuEvent(self, event):
        """Show context menu on right click"""
        menu = QMenu(self)
        
        toggle_action = QAction("Toggle Mode", self)
        toggle_action.triggered.connect(self.toggle_mode)
        menu.addAction(toggle_action)
        
        menu.exec_(event.globalPos()) 