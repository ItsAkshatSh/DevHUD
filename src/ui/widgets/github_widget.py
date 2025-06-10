from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTabWidget, QMenu, QAction,
                             QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon

class GitHubWidget(QWidget):
    def __init__(self, github_manager, theme_engine, settings, parent=None):
        super().__init__(parent)
        self.github_manager = github_manager
        self.theme_engine = theme_engine
        self.settings = settings
        self.is_widget_mode = True
        
        # Connect signals
        self.github_manager.prs_updated.connect(self.update_prs_list)
        self.github_manager.repos_updated.connect(self.update_repos_count)
        
        # Set window flags
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize UI
        self.init_ui()
        
        # Set username
        self.username.setText(self.settings.get('github_username', ''))
        
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
        self.title_label = QLabel("GitHub")
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
        self.tab_widget.setObjectName("githubTabWidget")
        
        # Create tabs
        self.prs_tab = self.create_prs_tab()
        self.tab_widget.addTab(self.prs_tab, "Pull Requests")
        
        self.main_layout.addWidget(self.tab_widget)
        
        # Create compact widget view
        self.widget_view = QWidget()
        widget_layout = QVBoxLayout(self.widget_view)
        widget_layout.setContentsMargins(5, 5, 5, 5)
        widget_layout.setSpacing(2)
        
        # Quick status in widget mode
        self.create_quick_status()
        widget_layout.addWidget(self.quick_status_frame)
        
        self.main_layout.addWidget(self.widget_view)
        
        # Apply theme
        self.apply_theme()
        
        # Set initial mode
        self.set_widget_mode(True)
        
    def create_prs_tab(self):
        """Create pull requests tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # PRs list
        self.prs_list = QListWidget()
        self.prs_list.setObjectName("prsList")
        layout.addWidget(self.prs_list)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        new_pr_btn = QPushButton("New PR")
        new_pr_btn.clicked.connect(self.create_new_pr)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_prs)
        
        controls_layout.addWidget(new_pr_btn)
        controls_layout.addWidget(refresh_btn)
        layout.addLayout(controls_layout)
        
        return tab
        
    def create_quick_status(self):
        """Create quick status display for widget mode"""
        self.quick_status_frame = QFrame()
        self.quick_status_frame.setObjectName("compactFrame")
        layout = QVBoxLayout(self.quick_status_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # User info
        user_layout = QHBoxLayout()
        self.user_label = QLabel("User:")
        self.username = QLabel()
        user_layout.addWidget(self.user_label)
        user_layout.addWidget(self.username)
        layout.addLayout(user_layout)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        
        # Repositories count
        repos_layout = QVBoxLayout()
        self.repos_count = QLabel("0")
        self.repos_count.setObjectName("countLabel")
        repos_layout.addWidget(QLabel("Repos"))
        repos_layout.addWidget(self.repos_count)
        
        # PRs count
        prs_layout = QVBoxLayout()
        self.prs_count = QLabel("0")
        self.prs_count.setObjectName("countLabel")
        prs_layout.addWidget(QLabel("PRs"))
        prs_layout.addWidget(self.prs_count)
        
        stats_layout.addLayout(repos_layout)
        stats_layout.addLayout(prs_layout)
        layout.addLayout(stats_layout)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        layout.addWidget(refresh_btn)
        
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
        
    def refresh_all(self):
        """Refresh all GitHub data"""
        self.github_manager.update_prs()
        self.github_manager.update_repos()
        
    def refresh_prs(self):
        """Refresh pull requests list"""
        self.github_manager.update_prs()
        
    def create_new_pr(self):
        """Create new pull request"""
        # TODO: Implement with GitHub manager
        pass
        
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
            
            QListWidget {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
            
            QListWidget::item {{
                padding: 5px;
            }}
            
            QListWidget::item:selected {{
                background: {colors['accent']};
                color: {colors['background']};
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
            
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background: {colors['background']};
                color: {colors['foreground']};
                border: 1px solid {colors['border']}
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
            
            QLabel#countLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {colors['accent']};
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
        
    @pyqtSlot(list)
    def update_prs_list(self, prs):
        """Update PRs list with new data"""
        self.prs_list.clear()
        self.prs_count.setText(str(len(prs)))
        for pr in prs:
            item = QListWidgetItem()
            item.setText(f"#{pr['number']} {pr['title']} ({pr['repo']})")
            item.setToolTip(f"State: {pr['state']}\nCreated: {pr['created_at']}\nUpdated: {pr['updated_at']}")
            self.prs_list.addItem(item)
            
    @pyqtSlot(int)
    def update_repos_count(self, count):
        """Update repository count"""
        self.repos_count.setText(str(count)) 