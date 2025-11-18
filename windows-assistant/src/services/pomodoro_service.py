"""
Pomodoro service - Timer for productivity
"""
from datetime import datetime, timedelta
from typing import Optional, Callable
from threading import Thread, Event
import time


class PomodoroService:
    """Service for managing Pomodoro timer sessions"""

    def __init__(self, db, notification_service):
        self.db = db
        self.notification_service = notification_service

        # Default durations (in minutes)
        self.work_duration = 25
        self.short_break_duration = 5
        self.long_break_duration = 15
        self.sessions_until_long_break = 4

        # State
        self.current_session_id: Optional[int] = None
        self.current_task_id: Optional[int] = None
        self.session_type = "work"  # work, short_break, long_break
        self.sessions_completed = 0
        self.is_running = False
        self.is_paused = False
        self.time_remaining = 0  # in seconds
        self.start_time: Optional[datetime] = None

        # Threading
        self.thread: Optional[Thread] = None
        self.stop_event = Event()

        # Callbacks
        self.tick_callback: Optional[Callable] = None
        self.complete_callback: Optional[Callable] = None

    def load_settings(self):
        """Load Pomodoro settings from database"""
        try:
            from ..models.database import SettingsModel
            settings = SettingsModel(self.db)

            self.work_duration = settings.get_setting('pomodoro_work_duration', 25)
            self.short_break_duration = settings.get_setting('pomodoro_short_break', 5)
            self.long_break_duration = settings.get_setting('pomodoro_long_break', 15)
            self.sessions_until_long_break = settings.get_setting(
                'pomodoro_sessions_until_long_break', 4
            )
        except Exception as e:
            print(f"Error loading Pomodoro settings: {e}")

    def start_work_session(self, task_id: Optional[int] = None):
        """Start a work session"""
        if self.is_running:
            print("⚠ A session is already running")
            return False

        self.session_type = "work"
        self.current_task_id = task_id
        self.time_remaining = self.work_duration * 60
        self._start_timer()
        self._create_session_record()

        self.notification_service.send_pomodoro_notification(
            "work",
            f"Çalışma oturumu başladı! {self.work_duration} dakika odaklan."
        )

        return True

    def start_break_session(self, is_long_break: bool = False):
        """Start a break session"""
        if self.is_running:
            print("⚠ A session is already running")
            return False

        if is_long_break:
            self.session_type = "long_break"
            duration = self.long_break_duration
            message = f"Uzun mola! {duration} dakika dinlen."
        else:
            self.session_type = "short_break"
            duration = self.short_break_duration
            message = f"Kısa mola! {duration} dakika dinlen."

        self.time_remaining = duration * 60
        self._start_timer()

        self.notification_service.send_pomodoro_notification(
            self.session_type,
            message
        )

        return True

    def pause(self):
        """Pause the current session"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            print("⏸ Pomodoro paused")

    def resume(self):
        """Resume the current session"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            print("▶ Pomodoro resumed")

    def stop(self):
        """Stop the current session"""
        if self.is_running:
            self.is_running = False
            self.stop_event.set()
            if self.thread:
                self.thread.join(timeout=2)
            self._complete_session(completed=False)
            print("⏹ Pomodoro stopped")

    def _start_timer(self):
        """Start the timer thread"""
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        self.stop_event.clear()
        self.thread = Thread(target=self._run_timer, daemon=True)
        self.thread.start()

    def _run_timer(self):
        """Main timer loop"""
        while self.is_running and self.time_remaining > 0:
            if not self.is_paused:
                time.sleep(1)
                self.time_remaining -= 1

                # Call tick callback if set
                if self.tick_callback:
                    try:
                        self.tick_callback(self.time_remaining, self.session_type)
                    except Exception as e:
                        print(f"Error in tick callback: {e}")
            else:
                time.sleep(0.1)  # Check pause state more frequently

        # Timer completed
        if self.is_running:  # Not manually stopped
            self._on_timer_complete()

    def _on_timer_complete(self):
        """Called when timer completes naturally"""
        self.is_running = False
        self._complete_session(completed=True)

        # Send completion notification
        if self.session_type == "work":
            self.sessions_completed += 1
            message = f"Çalışma oturumu tamamlandı! 🎉\n"

            # Determine next session type
            if self.sessions_completed % self.sessions_until_long_break == 0:
                message += f"Uzun mola zamanı! ({self.long_break_duration} dakika)"
            else:
                message += f"Kısa mola zamanı! ({self.short_break_duration} dakika)"

            self.notification_service.send_pomodoro_notification("work", message)

        elif self.session_type in ["short_break", "long_break"]:
            self.notification_service.send_pomodoro_notification(
                self.session_type,
                "Mola bitti! Bir sonraki çalışma oturumuna hazır mısın?"
            )

        # Call complete callback if set
        if self.complete_callback:
            try:
                self.complete_callback(self.session_type, self.sessions_completed)
            except Exception as e:
                print(f"Error in complete callback: {e}")

    def _create_session_record(self):
        """Create a database record for the session"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            duration = {
                'work': self.work_duration,
                'short_break': self.short_break_duration,
                'long_break': self.long_break_duration
            }.get(self.session_type, 25)

            cursor.execute('''
                INSERT INTO pomodoro_sessions
                (task_id, start_time, duration_minutes, session_type)
                VALUES (?, ?, ?, ?)
            ''', (self.current_task_id, datetime.now(), duration, self.session_type))

            conn.commit()
            self.current_session_id = cursor.lastrowid

        except Exception as e:
            print(f"Error creating session record: {e}")

    def _complete_session(self, completed: bool):
        """Update session record on completion"""
        if self.current_session_id:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE pomodoro_sessions
                    SET end_time = ?,
                        is_completed = ?
                    WHERE id = ?
                ''', (datetime.now(), 1 if completed else 0, self.current_session_id))

                conn.commit()
                self.current_session_id = None

            except Exception as e:
                print(f"Error completing session record: {e}")

    def get_today_statistics(self) -> dict:
        """Get Pomodoro statistics for today"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            today = datetime.now().date()
            cursor.execute('''
                SELECT
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN session_type = 'work' AND is_completed = 1 THEN 1 ELSE 0 END) as work_sessions,
                    SUM(CASE WHEN is_completed = 1 THEN duration_minutes ELSE 0 END) as total_minutes
                FROM pomodoro_sessions
                WHERE DATE(start_time) = ?
            ''', (today,))

            row = cursor.fetchone()
            return {
                'total_sessions': row[0] or 0,
                'work_sessions': row[1] or 0,
                'total_minutes': row[2] or 0
            }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {'total_sessions': 0, 'work_sessions': 0, 'total_minutes': 0}

    def set_tick_callback(self, callback: Callable):
        """Set callback for timer tick (called every second)"""
        self.tick_callback = callback

    def set_complete_callback(self, callback: Callable):
        """Set callback for session completion"""
        self.complete_callback = callback

    def get_time_remaining_formatted(self) -> str:
        """Get formatted time remaining (MM:SS)"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
