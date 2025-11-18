"""
Main window UI for Windows Personal Assistant
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from datetime import datetime
from typing import Optional

from .notes_tab import NotesTab
from .tasks_tab import TasksTab
from .pomodoro_tab import PomodoroTab
from .calendar_tab import CalendarTab
from .settings_tab import SettingsTab
from ..models.database import Database
from ..services.reminder_service import ReminderService
from ..services.notification_service import NotificationService
from ..services.pomodoro_service import PomodoroService
from ..services.outlook_service import OutlookService


class MainWindow(QMainWindow):
    """Main application window"""

    # Signals
    theme_changed = Signal(str)  # Emits theme name

    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        # Initialize services
        self.notification_service = NotificationService(db)
        self.reminder_service = ReminderService(db, self._on_reminder_triggered)
        self.pomodoro_service = PomodoroService(db, self.notification_service)
        self.outlook_service = OutlookService(db)

        # UI state
        self.current_theme = 'light'

        # Setup UI
        self.setWindowTitle("Kişisel Asistan")
        self.setMinimumSize(900, 600)
        self.setup_ui()

        # Start services
        self.reminder_service.start()

        # Setup periodic tasks
        self.setup_timers()

        # Load theme from settings
        self.load_settings()

    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Create tabs
        self.notes_tab = NotesTab(self.db)
        self.tasks_tab = TasksTab(self.db)
        self.pomodoro_tab = PomodoroTab(self.db, self.pomodoro_service)
        self.calendar_tab = CalendarTab(self.db, self.outlook_service)
        self.settings_tab = SettingsTab(self.db, self)

        # Add tabs
        self.tabs.addTab(self.notes_tab, "📝 Notlar")
        self.tabs.addTab(self.tasks_tab, "✅ Görevler")
        self.tabs.addTab(self.pomodoro_tab, "🍅 Pomodoro")
        self.tabs.addTab(self.calendar_tab, "📅 Takvim")
        self.tabs.addTab(self.settings_tab, "⚙️ Ayarlar")

        main_layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Hazır")

    def create_header(self) -> QWidget:
        """Create the header widget"""
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        header_layout = QHBoxLayout(header)

        # Title
        title_label = QLabel("🏠 Kişisel Asistan")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # Spacer
        header_layout.addStretch()

        # Date/Time
        self.datetime_label = QLabel()
        self.update_datetime()
        header_layout.addWidget(self.datetime_label)

        # Quick stats
        self.stats_label = QLabel()
        self.update_stats()
        header_layout.addWidget(self.stats_label)

        return header

    def setup_timers(self):
        """Setup periodic timers"""
        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_datetime)
        self.time_timer.start(1000)

        # Update stats every minute
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(60000)

        # Check calendar events every 30 minutes
        self.calendar_timer = QTimer()
        self.calendar_timer.timeout.connect(self.check_calendar_events)
        self.calendar_timer.start(1800000)  # 30 minutes

    def update_datetime(self):
        """Update the date/time display"""
        now = datetime.now()
        self.datetime_label.setText(
            now.strftime("%d %B %Y, %A - %H:%M:%S")
        )

    def update_stats(self):
        """Update quick statistics"""
        try:
            from ..models.database import RemindersModel, TasksModel

            reminders_model = RemindersModel(self.db)
            tasks_model = TasksModel(self.db)

            # Count pending reminders
            pending_reminders = len(reminders_model.get_pending_reminders())

            # Count pending tasks
            pending_tasks = len(tasks_model.get_tasks(status='pending'))

            self.stats_label.setText(
                f"⏰ {pending_reminders} Hatırlatma | ✅ {pending_tasks} Görev"
            )

        except Exception as e:
            print(f"Error updating stats: {e}")

    def check_calendar_events(self):
        """Check for upcoming calendar events"""
        try:
            count = self.outlook_service.check_events_for_notifications(
                self._on_calendar_event
            )
            if count > 0:
                self.statusBar().showMessage(
                    f"{count} takvim bildirimi gönderildi",
                    5000
                )
        except Exception as e:
            print(f"Error checking calendar events: {e}")

    def _on_reminder_triggered(self, reminder_data: dict):
        """Callback when a reminder is triggered"""
        try:
            self.notification_service.send_reminder_notification(reminder_data)
            self.update_stats()
        except Exception as e:
            print(f"Error handling reminder: {e}")

    def _on_calendar_event(self, event_data: dict):
        """Callback when a calendar event needs notification"""
        try:
            self.notification_service.send_calendar_notification(event_data)
        except Exception as e:
            print(f"Error handling calendar event: {e}")

    def load_settings(self):
        """Load application settings"""
        try:
            from ..models.database import SettingsModel
            settings = SettingsModel(self.db)

            # Load theme
            theme = settings.get_setting('theme', 'light')
            self.apply_theme(theme)

        except Exception as e:
            print(f"Error loading settings: {e}")

    def apply_theme(self, theme_name: str):
        """Apply a theme to the application"""
        self.current_theme = theme_name

        if theme_name == 'dark':
            stylesheet = self.get_dark_theme_stylesheet()
        else:
            stylesheet = self.get_light_theme_stylesheet()

        self.setStyleSheet(stylesheet)
        self.theme_changed.emit(theme_name)

    def get_light_theme_stylesheet(self) -> str:
        """Get light theme stylesheet"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #0078d4;
                font-weight: bold;
            }
            QFrame {
                background-color: white;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateTimeEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0078d4;
            }
        """

    def get_dark_theme_stylesheet(self) -> str:
        """Get dark theme stylesheet"""
        return """
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: #4cc2ff;
                font-weight: bold;
            }
            QFrame {
                background-color: #2d2d2d;
                color: #ffffff;
                border-radius: 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e90ff;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateTimeEdit {
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 5px;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0078d4;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                border-radius: 6px;
            }
        """

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop services
        self.reminder_service.stop()
        if self.pomodoro_service.is_running:
            self.pomodoro_service.stop()

        # Close database
        self.db.close()

        event.accept()
