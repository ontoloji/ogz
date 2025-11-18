"""
Pomodoro tab UI component
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QGroupBox, QFormLayout, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ..models.database import Database
from ..services.pomodoro_service import PomodoroService


class PomodoroTab(QWidget):
    """Pomodoro timer tab widget"""

    def __init__(self, db: Database, pomodoro_service: PomodoroService):
        super().__init__()
        self.db = db
        self.pomodoro = pomodoro_service
        self.pomodoro.load_settings()

        # Set callbacks
        self.pomodoro.set_tick_callback(self.on_timer_tick)
        self.pomodoro.set_complete_callback(self.on_session_complete)

        self.setup_ui()
        self.update_ui()

        # Update UI periodically
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(100)  # Update every 100ms for smooth display

    def setup_ui(self):
        """Setup tab UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Timer display
        timer_group = QGroupBox("⏰ Pomodoro Timer")
        timer_layout = QVBoxLayout()

        self.session_type_label = QLabel("Çalışma Oturumu")
        self.session_type_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.session_type_label.setFont(font)
        timer_layout.addWidget(self.session_type_label)

        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_font = QFont()
        timer_font.setPointSize(48)
        timer_font.setBold(True)
        self.timer_label.setFont(timer_font)
        timer_layout.addWidget(self.timer_label)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.start_work_btn = QPushButton("🍅 Çalışma Başlat")
        self.start_work_btn.clicked.connect(self.start_work_session)
        controls_layout.addWidget(self.start_work_btn)

        self.start_break_btn = QPushButton("☕ Kısa Mola")
        self.start_break_btn.clicked.connect(self.start_short_break)
        controls_layout.addWidget(self.start_break_btn)

        self.start_long_break_btn = QPushButton("🎉 Uzun Mola")
        self.start_long_break_btn.clicked.connect(self.start_long_break)
        controls_layout.addWidget(self.start_long_break_btn)

        timer_layout.addLayout(controls_layout)

        # Pause/Resume/Stop buttons
        action_layout = QHBoxLayout()

        self.pause_btn = QPushButton("⏸ Duraklat")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        action_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Durdur")
        self.stop_btn.clicked.connect(self.stop_session)
        self.stop_btn.setEnabled(False)
        action_layout.addWidget(self.stop_btn)

        timer_layout.addLayout(action_layout)

        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)

        # Statistics
        stats_group = QGroupBox("📊 Bugünün İstatistikleri")
        stats_layout = QFormLayout()

        self.stats_total = QLabel("0")
        self.stats_work = QLabel("0")
        self.stats_minutes = QLabel("0")

        stats_layout.addRow("Toplam Oturum:", self.stats_total)
        stats_layout.addRow("Çalışma Oturumları:", self.stats_work)
        stats_layout.addRow("Toplam Dakika:", self.stats_minutes)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Session counter
        counter_label = QLabel()
        counter_label.setText(
            f"Tamamlanan Oturumlar: {self.pomodoro.sessions_completed} / "
            f"{self.pomodoro.sessions_until_long_break}"
        )
        self.counter_label = counter_label
        layout.addWidget(counter_label)

        layout.addStretch()

    def start_work_session(self):
        """Start a work session"""
        if self.pomodoro.start_work_session():
            self.update_button_states(running=True)

    def start_short_break(self):
        """Start a short break"""
        if self.pomodoro.start_break_session(is_long_break=False):
            self.update_button_states(running=True)

    def start_long_break(self):
        """Start a long break"""
        if self.pomodoro.start_break_session(is_long_break=True):
            self.update_button_states(running=True)

    def toggle_pause(self):
        """Toggle pause/resume"""
        if self.pomodoro.is_paused:
            self.pomodoro.resume()
            self.pause_btn.setText("⏸ Duraklat")
        else:
            self.pomodoro.pause()
            self.pause_btn.setText("▶ Devam Et")

    def stop_session(self):
        """Stop current session"""
        self.pomodoro.stop()
        self.update_button_states(running=False)

    def update_button_states(self, running: bool):
        """Update button enabled/disabled states"""
        self.start_work_btn.setEnabled(not running)
        self.start_break_btn.setEnabled(not running)
        self.start_long_break_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        self.stop_btn.setEnabled(running)

        if not running:
            self.pause_btn.setText("⏸ Duraklat")

    def on_timer_tick(self, time_remaining: int, session_type: str):
        """Called every second during timer"""
        pass  # UI updated by periodic timer

    def on_session_complete(self, session_type: str, sessions_completed: int):
        """Called when a session completes"""
        self.update_button_states(running=False)
        self.update_statistics()
        self.counter_label.setText(
            f"Tamamlanan Oturumlar: {sessions_completed} / "
            f"{self.pomodoro.sessions_until_long_break}"
        )

    def update_ui(self):
        """Update UI with current timer state"""
        if self.pomodoro.is_running:
            # Update timer display
            self.timer_label.setText(self.pomodoro.get_time_remaining_formatted())

            # Update session type
            type_names = {
                'work': '🍅 Çalışma Oturumu',
                'short_break': '☕ Kısa Mola',
                'long_break': '🎉 Uzun Mola'
            }
            self.session_type_label.setText(
                type_names.get(self.pomodoro.session_type, 'Oturum')
            )

            # Visual indicator for paused state
            if self.pomodoro.is_paused:
                self.session_type_label.setText(
                    self.session_type_label.text() + " (DURAKLATILDI)"
                )

    def update_statistics(self):
        """Update today's statistics"""
        stats = self.pomodoro.get_today_statistics()
        self.stats_total.setText(str(stats['total_sessions']))
        self.stats_work.setText(str(stats['work_sessions']))
        self.stats_minutes.setText(str(stats['total_minutes']))
