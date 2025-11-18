"""
Reminder service - Background service for checking and triggering reminders
"""
from datetime import datetime, timedelta
from typing import Callable, Optional
from threading import Thread, Event
import time
from ..models.database import Database, RemindersModel


class ReminderService:
    """Background service that checks for pending reminders"""

    def __init__(self, db: Database, notification_callback: Callable):
        """
        Initialize reminder service

        Args:
            db: Database instance
            notification_callback: Function to call when a reminder should trigger
        """
        self.db = db
        self.reminders_model = RemindersModel(db)
        self.notification_callback = notification_callback
        self.check_interval = 60  # Check every 60 seconds
        self.running = False
        self.thread: Optional[Thread] = None
        self.stop_event = Event()

    def start(self):
        """Start the reminder service"""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            self.thread = Thread(target=self._run, daemon=True)
            self.thread.start()
            print("✓ Reminder service started")

    def stop(self):
        """Stop the reminder service"""
        if self.running:
            self.running = False
            self.stop_event.set()
            if self.thread:
                self.thread.join(timeout=5)
            print("✓ Reminder service stopped")

    def _run(self):
        """Main loop for checking reminders"""
        while self.running:
            try:
                self._check_reminders()
            except Exception as e:
                print(f"Error in reminder service: {e}")

            # Wait for the interval or until stopped
            self.stop_event.wait(self.check_interval)

    def _check_reminders(self):
        """Check for pending reminders and trigger notifications"""
        current_time = datetime.now()
        pending_reminders = self.reminders_model.get_pending_reminders(current_time)

        for reminder in pending_reminders:
            try:
                # Call notification callback
                self.notification_callback(reminder)

                # Handle recurrence
                if reminder['recurrence_type'] and reminder['recurrence_interval']:
                    self._handle_recurring_reminder(reminder)
                else:
                    # Mark as completed for one-time reminders
                    self.reminders_model.complete_reminder(reminder['id'])

            except Exception as e:
                print(f"Error processing reminder {reminder['id']}: {e}")

    def _handle_recurring_reminder(self, reminder):
        """Handle recurring reminders by creating the next occurrence"""
        recurrence_type = reminder['recurrence_type']
        interval = reminder['recurrence_interval']
        current_time = datetime.fromisoformat(reminder['reminder_time'])

        # Calculate next reminder time
        if recurrence_type == 'daily':
            next_time = current_time + timedelta(days=interval)
        elif recurrence_type == 'weekly':
            next_time = current_time + timedelta(weeks=interval)
        elif recurrence_type == 'monthly':
            # Approximate month as 30 days
            next_time = current_time + timedelta(days=30 * interval)
        elif recurrence_type == 'yearly':
            next_time = current_time + timedelta(days=365 * interval)
        else:
            # Unknown recurrence type, just complete it
            self.reminders_model.complete_reminder(reminder['id'])
            return

        # Update the reminder with the new time
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE reminders
            SET reminder_time = ?,
                last_triggered = CURRENT_TIMESTAMP,
                is_snoozed = 0,
                snooze_until = NULL
            WHERE id = ?
        ''', (next_time, reminder['id']))
        conn.commit()

    def snooze_reminder(self, reminder_id: int, minutes: int):
        """
        Snooze a reminder for specified minutes

        Args:
            reminder_id: ID of the reminder to snooze
            minutes: Number of minutes to snooze
        """
        snooze_until = datetime.now() + timedelta(minutes=minutes)
        self.reminders_model.snooze_reminder(reminder_id, snooze_until)

    def dismiss_reminder(self, reminder_id: int):
        """
        Dismiss a reminder permanently

        Args:
            reminder_id: ID of the reminder to dismiss
        """
        self.reminders_model.complete_reminder(reminder_id)
