"""
Notification service - Handles Windows notifications
"""
import platform
from datetime import datetime
from typing import Optional


class NotificationService:
    """Service for sending Windows notifications"""

    def __init__(self, db=None):
        self.db = db
        self.system = platform.system()

        # Try to import Windows-specific notification library
        if self.system == 'Windows':
            try:
                from win10toast import ToastNotifier
                self.toaster = ToastNotifier()
                self.notification_method = 'win10toast'
            except ImportError:
                print("⚠ win10toast not available, notifications may not work on Windows")
                self.toaster = None
                self.notification_method = 'fallback'
        else:
            self.toaster = None
            self.notification_method = 'fallback'

    def send_notification(self, title: str, message: str,
                         duration: int = 10,
                         icon_path: Optional[str] = None,
                         notification_type: str = "reminder",
                         reference_id: Optional[int] = None):
        """
        Send a notification to the user

        Args:
            title: Notification title
            message: Notification message
            duration: How long to show notification (seconds)
            icon_path: Path to icon file
            notification_type: Type of notification (reminder, calendar, task, etc.)
            reference_id: ID of the related item (note, task, etc.)
        """

        # Log to database if available
        if self.db:
            self._log_notification(notification_type, reference_id, title, message)

        # Send platform-specific notification
        if self.notification_method == 'win10toast' and self.toaster:
            try:
                self.toaster.show_toast(
                    title=title,
                    msg=message,
                    duration=duration,
                    icon_path=icon_path,
                    threaded=True
                )
            except Exception as e:
                print(f"Error sending notification: {e}")
                self._fallback_notification(title, message)
        else:
            self._fallback_notification(title, message)

    def _fallback_notification(self, title: str, message: str):
        """Fallback notification method (console output)"""
        print("\n" + "="*50)
        print(f"🔔 NOTIFICATION: {title}")
        print(f"📝 {message}")
        print("="*50 + "\n")

    def _log_notification(self, notification_type: str, reference_id: Optional[int],
                         title: str, message: str):
        """Log notification to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notification_history (notification_type, reference_id, title, message)
                VALUES (?, ?, ?, ?)
            ''', (notification_type, reference_id, title, message))
            conn.commit()
        except Exception as e:
            print(f"Error logging notification: {e}")

    def send_reminder_notification(self, reminder_data: dict):
        """
        Send a notification for a reminder

        Args:
            reminder_data: Dictionary containing reminder information
        """
        title = f"⏰ Hatırlatma: {reminder_data.get('title', 'Başlıksız')}"
        message = reminder_data.get('content', '')

        # Add priority indicator
        priority = reminder_data.get('priority', 2)
        if priority == 4:
            title = "🔴 [ACİL] " + title
        elif priority == 3:
            title = "🟡 [YÜKSEK] " + title

        # Add category
        category = reminder_data.get('category', '')
        if category:
            message = f"[{category}]\n{message}"

        self.send_notification(
            title=title,
            message=message[:200],  # Limit message length
            notification_type="reminder",
            reference_id=reminder_data.get('id')
        )

    def send_calendar_notification(self, event_data: dict):
        """
        Send a notification for a calendar event

        Args:
            event_data: Dictionary containing event information
        """
        title = f"📅 Yaklaşan Toplantı: {event_data.get('subject', 'Başlıksız')}"

        start_time = event_data.get('start_time', '')
        location = event_data.get('location', '')
        attendees = event_data.get('attendees', '')

        message = f"Başlangıç: {start_time}"
        if location:
            message += f"\n📍 Yer: {location}"
        if attendees:
            message += f"\n👥 Katılımcılar: {attendees}"

        self.send_notification(
            title=title,
            message=message[:200],
            notification_type="calendar",
            reference_id=event_data.get('id')
        )

    def send_task_notification(self, task_data: dict):
        """
        Send a notification for a task

        Args:
            task_data: Dictionary containing task information
        """
        title = f"✅ Görev Hatırlatması: {task_data.get('title', 'Başlıksız')}"
        message = task_data.get('description', '')

        due_date = task_data.get('due_date', '')
        if due_date:
            message = f"📅 Termin: {due_date}\n{message}"

        self.send_notification(
            title=title,
            message=message[:200],
            notification_type="task",
            reference_id=task_data.get('id')
        )

    def send_pomodoro_notification(self, session_type: str, message: str):
        """
        Send a notification for Pomodoro timer

        Args:
            session_type: Type of session (work, short_break, long_break)
            message: Notification message
        """
        icons = {
            'work': '🍅',
            'short_break': '☕',
            'long_break': '🎉'
        }

        title = f"{icons.get(session_type, '⏰')} Pomodoro"

        self.send_notification(
            title=title,
            message=message,
            notification_type="pomodoro"
        )


# Singleton instance
_notification_service_instance = None


def get_notification_service(db=None) -> NotificationService:
    """Get singleton instance of notification service"""
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = NotificationService(db)
    return _notification_service_instance
