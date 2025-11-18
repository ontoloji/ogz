"""
UI components package
"""
from .main_window import MainWindow
from .system_tray import SystemTrayIcon
from .notes_tab import NotesTab
from .tasks_tab import TasksTab
from .pomodoro_tab import PomodoroTab
from .calendar_tab import CalendarTab
from .settings_tab import SettingsTab

__all__ = [
    'MainWindow',
    'SystemTrayIcon',
    'NotesTab',
    'TasksTab',
    'PomodoroTab',
    'CalendarTab',
    'SettingsTab'
]
