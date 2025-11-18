"""
System tray icon and menu
"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for the application"""

    # Signals
    show_window_requested = Signal()
    quit_requested = Signal()
    quick_note_requested = Signal()

    def __init__(self, parent=None):
        # Create a simple icon (in production, use an actual icon file)
        # For now, we'll use a default icon
        super().__init__(parent)

        # Set tooltip
        self.setToolTip("Kişisel Asistan")

        # Create menu
        self.create_menu()

        # Connect signals
        self.activated.connect(self.on_activated)

        # Show icon
        self.show()

    def create_menu(self):
        """Create the context menu"""
        menu = QMenu()

        # Show window action
        show_action = QAction("🏠 Pencereyi Göster", menu)
        show_action.triggered.connect(self.show_window_requested.emit)
        menu.addAction(show_action)

        # Quick note action
        quick_note_action = QAction("📝 Hızlı Not", menu)
        quick_note_action.triggered.connect(self.quick_note_requested.emit)
        menu.addAction(quick_note_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("🚪 Çıkış", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window_requested.emit()

    def show_notification(self, title: str, message: str, duration: int = 5000):
        """Show a notification from system tray"""
        self.showMessage(
            title,
            message,
            QSystemTrayIcon.Information,
            duration
        )
