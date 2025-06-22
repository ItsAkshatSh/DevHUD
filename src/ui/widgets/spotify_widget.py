from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer
from utils.spotify_info import get_spotify_song_info, send_spotify_control
from PyQt5.QtGui import QIcon

class SpotifyWidget(QWidget):
    def __init__(self, desktop_integration, theme_engine, settings, parent=None):
        super().__init__(parent)
        self.desktop_integration = desktop_integration
        self.theme_engine = theme_engine
        self.settings = settings
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.apply_theme()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_song_info)
        self.timer.start(1000)
        self.update_song_info()
        self.settings.settings_changed.connect(self.apply_theme)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.spotify_frame = QFrame(self)
        self.spotify_frame.setObjectName("SpotifyFrame")
        frame_layout = QVBoxLayout(self.spotify_frame)
        frame_layout.setContentsMargins(10, 8, 10, 8)
        frame_layout.setSpacing(4)

        # Top: Source label
        self.source_label = QLabel("SPOTIFY")
        self.source_label.setObjectName("SourceLabel")
        frame_layout.addWidget(self.source_label, alignment=Qt.AlignLeft)

        # Song title
        self.song_label = QLabel("No song playing")
        self.song_label.setObjectName("TitleLabel")
        self.song_label.setWordWrap(True)
        frame_layout.addWidget(self.song_label)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(QIcon('resources/media/skip_previous.svg'))
        self.play_btn = QPushButton()
        self.play_btn.setIcon(QIcon('resources/media/play.svg'))
        self.next_btn = QPushButton()
        self.next_btn.setIcon(QIcon('resources/media/skip_next.svg'))
        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(QIcon('resources/media/pause.svg'))
        self.pause_btn.setVisible(False)

        for btn in [self.prev_btn, self.play_btn, self.next_btn, self.pause_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(32, 32)

        self.play_btn.clicked.connect(self.toggle_play_pause)
        self.pause_btn.clicked.connect(self.toggle_play_pause)
        self.prev_btn.clicked.connect(lambda: send_spotify_control('prev'))
        self.next_btn.clicked.connect(lambda: send_spotify_control('next'))
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addStretch(1)
        frame_layout.addLayout(controls_layout)

        main_layout.addWidget(self.spotify_frame)

        self.setFixedSize(320, 80)  # Reduced size since we removed the visualizer

    def apply_theme(self):
        theme = self.theme_engine.get_theme()
        colors = theme['colors']
        font_family = theme['font_family']
        font_size = theme['font_size']
        border_radius = theme['border_radius']

        self.spotify_frame.setStyleSheet(f"""
            QFrame#SpotifyFrame {{
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: {border_radius}px;
            }}
            QLabel#TitleLabel {{
                color: {colors['text']};
                font-weight: bold;
                font-size: {font_size}px;
                font-family: {font_family};
            }}
            QLabel#SourceLabel {{
                color: {colors['accent']};
                font-size: {font_size-4}px;
                font-weight: bold;
                letter-spacing: 1px;
                font-family: {font_family};
            }}
            QPushButton {{
                background: transparent;
                color: {colors['text']};
                font-size: {font_size-2}px;
                border: 1px solid {colors['border']};
                border-radius: {border_radius - 2}px;
                padding: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_secondary']};
                border: 1px solid {colors['accent']};
                border-radius: {border_radius - 2}px;
            }}
        """)

    def update_song_info(self):
        song, artist, is_playing = get_spotify_song_info()
        if song and song.lower() == 'spotify free':
            # Ignore 'Spotify Free' as a song title
            return
        if song and artist:
            self.song_label.setText(f"{song} - {artist}")
            self._last_song = f"{song} - {artist}"
        elif song:
            self.song_label.setText(f"{song}")
            self._last_song = f"{song}"
        elif hasattr(self, '_last_song'):
            # If paused and no song, keep showing last valid song
            self.song_label.setText(self._last_song)
        else:
            self.song_label.setText("No song playing")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            # Save position when widget is moved
            self.settings.set_widget_position('spotify', self.x(), self.y())
            event.accept()

    def toggle_play_pause(self):
        # This toggles between play and pause icons
        send_spotify_control('play_pause')
        if self.play_btn.isVisible():
            self.play_btn.setVisible(False)
            self.pause_btn.setVisible(True)
        else:
            self.play_btn.setVisible(True)
            self.pause_btn.setVisible(False) 