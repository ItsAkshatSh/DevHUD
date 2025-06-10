from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QFrame, QPushButton, QTabWidget,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSlot, QPoint
from PyQt5.QtGui import QIcon, QCursor
import psutil

class SystemStatsWidget(QWidget):
    def __init__(self, system_stats, theme_engine, settings, parent=None):
        super().__init__(parent)
        self.system_stats = system_stats
        self.theme_engine = theme_engine
        self.settings = settings
        self.is_widget_mode = True
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.system_stats.stats_updated.connect(self.update_stats)
        
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
        self.title_label = QLabel("System Monitor")
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
        self.tab_widget.setObjectName("statsTabWidget")
        
        # Create tabs
        self.cpu_tab = self.create_cpu_tab()
        self.memory_tab = self.create_memory_tab()
        if self.system_stats.gpu_available:
            self.gpu_tab = self.create_gpu_tab()
        
        self.tab_widget.addTab(self.cpu_tab, "CPU")
        self.tab_widget.addTab(self.memory_tab, "Memory")
        if self.system_stats.gpu_available:
            self.tab_widget.addTab(self.gpu_tab, "GPU")
        
        self.main_layout.addWidget(self.tab_widget)
        
        # Create compact widget view
        self.widget_view = QWidget()
        widget_layout = QVBoxLayout(self.widget_view)
        widget_layout.setContentsMargins(5, 5, 5, 5)
        widget_layout.setSpacing(2)
        
        # Add compact stats displays
        self.cpu_compact = self.create_compact_display("CPU")
        self.memory_compact = self.create_compact_display("RAM")
        if self.system_stats.gpu_available:
            self.gpu_compact = self.create_compact_display("GPU")
        
        widget_layout.addWidget(self.cpu_compact)
        widget_layout.addWidget(self.memory_compact)
        if self.system_stats.gpu_available:
            widget_layout.addWidget(self.gpu_compact)
        
        self.main_layout.addWidget(self.widget_view)
        
        # Apply theme
        self.apply_theme()
        
        # Set initial mode (do this last after all widgets are created)
        self.set_widget_mode(True)
        
    def create_cpu_tab(self):
        """Create CPU statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        self.cpu_bars = []
        cpu_count = psutil.cpu_count()
        
        for i in range(cpu_count):
            bar_layout = QHBoxLayout()
            core_label = QLabel(f"Core {i}")
            core_label.setFixedWidth(50)
            bar = QProgressBar()
            bar.setFixedHeight(8)
            bar.setTextVisible(False)
            
            bar_layout.addWidget(core_label)
            bar_layout.addWidget(bar)
            layout.addLayout(bar_layout)
            
            self.cpu_bars.append(bar)
        
        # Total CPU usage
        total_layout = QHBoxLayout()
        total_label = QLabel("Total")
        total_label.setFixedWidth(50)
        self.cpu_total_bar = QProgressBar()
        self.cpu_total_bar.setFixedHeight(8)
        self.cpu_total_bar.setTextVisible(False)
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.cpu_total_bar)
        layout.addLayout(total_layout)
        
        return tab
        
    def create_memory_tab(self):
        """Create memory statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # RAM section
        ram_group = QFrame()
        ram_group.setObjectName("statsGroup")
        ram_layout = QVBoxLayout(ram_group)
        
        ram_bar_layout = QHBoxLayout()
        ram_label = QLabel("RAM")
        ram_label.setFixedWidth(50)
        self.ram_bar = QProgressBar()
        self.ram_bar.setFixedHeight(8)
        self.ram_bar.setTextVisible(False)
        
        ram_bar_layout.addWidget(ram_label)
        ram_bar_layout.addWidget(self.ram_bar)
        ram_layout.addLayout(ram_bar_layout)
        
        self.ram_details = QLabel()
        ram_layout.addWidget(self.ram_details)
        
        layout.addWidget(ram_group)
        
        # Swap section
        swap_group = QFrame()
        swap_group.setObjectName("statsGroup")
        swap_layout = QVBoxLayout(swap_group)
        
        swap_bar_layout = QHBoxLayout()
        swap_label = QLabel("Swap")
        swap_label.setFixedWidth(50)
        self.swap_bar = QProgressBar()
        self.swap_bar.setFixedHeight(8)
        self.swap_bar.setTextVisible(False)
        
        swap_bar_layout.addWidget(swap_label)
        swap_bar_layout.addWidget(self.swap_bar)
        swap_layout.addLayout(swap_bar_layout)
        
        self.swap_details = QLabel()
        swap_layout.addWidget(self.swap_details)
        
        layout.addWidget(swap_group)
        layout.addStretch()
        
        return tab
        
    def create_gpu_tab(self):
        """Create GPU statistics tab"""
        tab = QWidget()
        self.gpu_layout = QVBoxLayout(tab)
        self.gpu_layout.setContentsMargins(10, 10, 10, 10)
        self.gpu_layout.setSpacing(5)
        
        self.gpu_bars = []
        self.gpu_labels = []
        
        return tab
        
    def create_compact_display(self, title):
        """Create a compact stats display for widget mode"""
        frame = QFrame()
        frame.setObjectName("compactFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        label = QLabel(title)
        label.setFixedWidth(30)
        bar = QProgressBar()
        bar.setFixedHeight(6)
        bar.setTextVisible(False)
        value = QLabel("0%")
        value.setFixedWidth(40)
        
        layout.addWidget(label)
        layout.addWidget(bar)
        layout.addWidget(value)
        
        if title == "CPU":
            self.cpu_compact_bar = bar
            self.cpu_compact_value = value
        elif title == "RAM":
            self.ram_compact_bar = bar
            self.ram_compact_value = value
        elif title == "GPU":
            self.gpu_compact_bar = bar
            self.gpu_compact_value = value
        
        return frame
        
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
            
            QFrame#statsGroup {{
                background: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 2px;
                background: {colors['background']};
            }}
            
            QProgressBar::chunk {{
                background: {colors['accent']};
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
            
            QLabel#headerTitle {{
                color: {colors['accent']};
                font-weight: bold;
            }}
        """)
        
    @pyqtSlot(dict)
    def update_stats(self, stats):
        """Update widget with new stats"""
        # Update CPU stats
        cpu_stats = stats['cpu']
        total_cpu = int(cpu_stats['total_percent'])
        
        if not self.is_widget_mode:
            for i, usage in enumerate(cpu_stats['percent_per_core']):
                self.cpu_bars[i].setValue(int(usage))
            self.cpu_total_bar.setValue(total_cpu)
        
        # Update compact CPU display
        self.cpu_compact_bar.setValue(total_cpu)
        self.cpu_compact_value.setText(f"{total_cpu}%")
        
        # Update memory stats
        memory_stats = stats['memory']
        ram_percent = int(memory_stats['percent'])
        
        if not self.is_widget_mode:
            self.ram_bar.setValue(ram_percent)
            ram_used = memory_stats['used'] / (1024 * 1024 * 1024)
            ram_total = memory_stats['total'] / (1024 * 1024 * 1024)
            self.ram_details.setText(f"{ram_used:.1f}GB / {ram_total:.1f}GB")
            
            swap_percent = int(memory_stats['swap']['percent'])
            self.swap_bar.setValue(swap_percent)
            swap_used = memory_stats['swap']['used'] / (1024 * 1024 * 1024)
            swap_total = memory_stats['swap']['total'] / (1024 * 1024 * 1024)
            self.swap_details.setText(f"{swap_used:.1f}GB / {swap_total:.1f}GB")
        
        # Update compact RAM display
        self.ram_compact_bar.setValue(ram_percent)
        self.ram_compact_value.setText(f"{ram_percent}%")
        
        # Update GPU stats if available
        if stats['gpu'] and self.system_stats.gpu_available:
            if not self.is_widget_mode:
                self._update_gpu_widgets(stats['gpu'])
            
            # Update compact GPU display
            gpu = stats['gpu'][0]  # First GPU
            gpu_percent = int(gpu['load'])
            self.gpu_compact_bar.setValue(gpu_percent)
            self.gpu_compact_value.setText(f"{gpu_percent}%")
            
    def _update_gpu_widgets(self, gpu_stats):
        """Update GPU statistics display"""
        # Create or update GPU widgets
        while len(self.gpu_bars) < len(gpu_stats):
            # Create new GPU widgets
            gpu_layout = QVBoxLayout()
            
            # Usage bar
            usage_layout = QHBoxLayout()
            usage_label = QLabel("Usage")
            usage_label.setFixedWidth(50)
            usage_bar = QProgressBar()
            usage_bar.setFixedHeight(8)
            usage_bar.setTextVisible(False)
            
            usage_layout.addWidget(usage_label)
            usage_layout.addWidget(usage_bar)
            gpu_layout.addLayout(usage_layout)
            
            # Memory bar
            memory_layout = QHBoxLayout()
            memory_label = QLabel("Memory")
            memory_label.setFixedWidth(50)
            memory_bar = QProgressBar()
            memory_bar.setFixedHeight(8)
            memory_bar.setTextVisible(False)
            
            memory_layout.addWidget(memory_label)
            memory_layout.addWidget(memory_bar)
            gpu_layout.addLayout(memory_layout)
            
            # Details label
            details_label = QLabel()
            gpu_layout.addWidget(details_label)
            
            self.gpu_layout.addLayout(gpu_layout)
            self.gpu_bars.append((usage_bar, memory_bar))
            self.gpu_labels.append(details_label)
            
        # Update GPU stats
        for i, gpu in enumerate(gpu_stats):
            usage_bar, memory_bar = self.gpu_bars[i]
            details_label = self.gpu_labels[i]
            
            # Update usage
            usage_bar.setValue(int(gpu['load']))
            
            # Update memory
            memory_percent = (gpu['memory']['used'] / gpu['memory']['total']) * 100
            memory_bar.setValue(int(memory_percent))
            
            # Update details
            memory_used = gpu['memory']['used'] / 1024  # Convert to GB
            memory_total = gpu['memory']['total'] / 1024
            details_label.setText(
                f"{gpu['name']}\n"
                f"Memory: {memory_used:.1f}GB / {memory_total:.1f}GB\n"
                f"Temperature: {gpu['temperature']}°C"
            )
            
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