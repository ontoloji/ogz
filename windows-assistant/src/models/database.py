"""
Database models and schema for Windows Personal Assistant
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
from pathlib import Path


class Database:
    """Database manager for the application"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data directory
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "assistant.db")

        self.db_path = db_path
        self.conn = None
        self.initialize_database()

    def get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def initialize_database(self):
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT DEFAULT 'general',
                priority INTEGER DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                tags TEXT
            )
        ''')

        # Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                reminder_time TIMESTAMP NOT NULL,
                is_completed INTEGER DEFAULT 0,
                is_snoozed INTEGER DEFAULT 0,
                snooze_until TIMESTAMP,
                recurrence_type TEXT,
                recurrence_interval INTEGER,
                last_triggered TIMESTAMP,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
            )
        ''')

        # Tasks table (To-Do List)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general',
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'pending',
                due_date TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parent_task_id INTEGER,
                estimated_minutes INTEGER,
                actual_minutes INTEGER,
                tags TEXT,
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        ''')

        # Outlook calendar events cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                subject TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                location TEXT,
                attendees TEXT,
                description TEXT,
                organizer TEXT,
                is_all_day INTEGER DEFAULT 0,
                notification_sent INTEGER DEFAULT 0,
                last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Pomodoro sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_minutes INTEGER DEFAULT 25,
                is_completed INTEGER DEFAULT 0,
                session_type TEXT DEFAULT 'work',
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#3498db',
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Notification history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_type TEXT NOT NULL,
                reference_id INTEGER,
                title TEXT NOT NULL,
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                was_clicked INTEGER DEFAULT 0
            )
        ''')

        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_calendar_start_time ON calendar_events(start_time)
        ''')

        # Insert default categories if not exists
        default_categories = [
            ('İş', '#e74c3c'),
            ('Kişisel', '#3498db'),
            ('Alışveriş', '#2ecc71'),
            ('Sağlık', '#9b59b6'),
            ('Eğitim', '#f39c12'),
            ('Genel', '#95a5a6')
        ]

        for cat_name, color in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)
            ''', (cat_name, color))

        # Insert default settings if not exists
        default_settings = {
            'theme': 'light',
            'notification_enabled': 'true',
            'notification_sound': 'true',
            'outlook_sync_enabled': 'false',
            'outlook_sync_interval': '30',
            'start_with_windows': 'false',
            'minimize_to_tray': 'true',
            'pomodoro_work_duration': '25',
            'pomodoro_short_break': '5',
            'pomodoro_long_break': '15',
            'pomodoro_sessions_until_long_break': '4'
        }

        for key, value in default_settings.items():
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))

        conn.commit()
        print(f"✓ Database initialized at: {self.db_path}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


class NotesModel:
    """Model for managing notes"""

    def __init__(self, db: Database):
        self.db = db

    def create_note(self, title: str, content: str = "", category: str = "Genel",
                    priority: int = 2, tags: List[str] = None) -> int:
        """Create a new note"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        tags_str = json.dumps(tags) if tags else None

        cursor.execute('''
            INSERT INTO notes (title, content, category, priority, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, category, priority, tags_str))

        conn.commit()
        return cursor.lastrowid

    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Get a note by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM notes WHERE id = ? AND is_deleted = 0
        ''', (note_id,))

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_notes(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all notes, optionally filtered by category"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if category:
            cursor.execute('''
                SELECT * FROM notes
                WHERE category = ? AND is_deleted = 0
                ORDER BY created_at DESC LIMIT ?
            ''', (category, limit))
        else:
            cursor.execute('''
                SELECT * FROM notes
                WHERE is_deleted = 0
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def update_note(self, note_id: int, **kwargs):
        """Update a note"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['title', 'content', 'category', 'priority', 'tags']
        update_fields = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                update_fields.append(f"{key} = ?")
                if key == 'tags' and isinstance(value, list):
                    values.append(json.dumps(value))
                else:
                    values.append(value)

        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(note_id)

            query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

    def delete_note(self, note_id: int, soft_delete: bool = True):
        """Delete a note (soft or hard)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if soft_delete:
            cursor.execute('UPDATE notes SET is_deleted = 1 WHERE id = ?', (note_id,))
        else:
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))

        conn.commit()

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by title or content"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT * FROM notes
            WHERE (title LIKE ? OR content LIKE ?) AND is_deleted = 0
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern))

        return [dict(row) for row in cursor.fetchall()]


class RemindersModel:
    """Model for managing reminders"""

    def __init__(self, db: Database):
        self.db = db

    def create_reminder(self, note_id: int, reminder_time: datetime,
                       recurrence_type: str = None, recurrence_interval: int = None) -> int:
        """Create a new reminder"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reminders (note_id, reminder_time, recurrence_type, recurrence_interval)
            VALUES (?, ?, ?, ?)
        ''', (note_id, reminder_time, recurrence_type, recurrence_interval))

        conn.commit()
        return cursor.lastrowid

    def get_pending_reminders(self, current_time: datetime = None) -> List[Dict[str, Any]]:
        """Get all pending reminders that should be triggered"""
        if current_time is None:
            current_time = datetime.now()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.*, n.title, n.content, n.category, n.priority
            FROM reminders r
            JOIN notes n ON r.note_id = n.id
            WHERE r.is_completed = 0
                AND r.reminder_time <= ?
                AND (r.is_snoozed = 0 OR r.snooze_until <= ?)
                AND n.is_deleted = 0
            ORDER BY r.reminder_time ASC
        ''', (current_time, current_time))

        return [dict(row) for row in cursor.fetchall()]

    def snooze_reminder(self, reminder_id: int, snooze_until: datetime):
        """Snooze a reminder"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE reminders
            SET is_snoozed = 1, snooze_until = ?
            WHERE id = ?
        ''', (snooze_until, reminder_id))

        conn.commit()

    def complete_reminder(self, reminder_id: int):
        """Mark reminder as completed"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE reminders
            SET is_completed = 1, last_triggered = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (reminder_id,))

        conn.commit()


class TasksModel:
    """Model for managing tasks (To-Do List)"""

    def __init__(self, db: Database):
        self.db = db

    def create_task(self, title: str, description: str = "", category: str = "Genel",
                   priority: int = 2, due_date: datetime = None,
                   parent_task_id: int = None, tags: List[str] = None) -> int:
        """Create a new task"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        tags_str = json.dumps(tags) if tags else None

        cursor.execute('''
            INSERT INTO tasks (title, description, category, priority, due_date, parent_task_id, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, category, priority, due_date, parent_task_id, tags_str))

        conn.commit()
        return cursor.lastrowid

    def get_tasks(self, status: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Get tasks with optional filters"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY priority DESC, due_date ASC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_task_status(self, task_id: int, status: str):
        """Update task status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        completed_at = datetime.now() if status == 'completed' else None

        cursor.execute('''
            UPDATE tasks
            SET status = ?, completed_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, completed_at, task_id))

        conn.commit()


class SettingsModel:
    """Model for managing application settings"""

    def __init__(self, db: Database):
        self.db = db

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()

        if row:
            value = row['value']
            # Try to convert to appropriate type
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            try:
                return int(value)
            except ValueError:
                return value

        return default

    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        value_str = str(value).lower() if isinstance(value, bool) else str(value)

        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value_str))

        conn.commit()

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT key, value FROM settings')
        settings = {}

        for row in cursor.fetchall():
            key = row['key']
            value = row['value']

            # Convert to appropriate type
            if value.lower() in ('true', 'false'):
                settings[key] = value.lower() == 'true'
            else:
                try:
                    settings[key] = int(value)
                except ValueError:
                    settings[key] = value

        return settings
