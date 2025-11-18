"""
Main application entry point
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.database import Database
from src.ui.main_window import MainWindow
from src.ui.system_tray import SystemTrayIcon


class PersonalAssistantApp:
    """Main application class"""

    def __init__(self):
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Create application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Kişisel Asistan")
        self.app.setOrganizationName("PersonalAssistant")

        # Initialize database
        self.db = Database()

        # Create main window
        self.main_window = MainWindow(self.db)

        # Create system tray
        self.setup_system_tray()

        # Show main window
        self.main_window.show()

    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = SystemTrayIcon()
        self.tray_icon.show_window_requested.connect(self.show_main_window)
        self.tray_icon.quit_requested.connect(self.quit_application)
        self.tray_icon.quick_note_requested.connect(self.show_quick_note)

    def show_main_window(self):
        """Show and activate main window"""
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()

    def show_quick_note(self):
        """Show quick note dialog"""
        # Switch to notes tab and show add dialog
        self.show_main_window()
        self.main_window.tabs.setCurrentIndex(0)  # Notes tab
        self.main_window.notes_tab.add_note()

    def quit_application(self):
        """Quit the application"""
        # Stop services
        self.main_window.reminder_service.stop()
        if self.main_window.pomodoro_service.is_running:
            self.main_window.pomodoro_service.stop()

        # Close database
        self.db.close()

        # Quit
        self.app.quit()

    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    """Main entry point"""
    print("=" * 50)
    print("Windows 11 Kişisel Asistan Uygulaması")
    print("=" * 50)
    print()

    app = PersonalAssistantApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
