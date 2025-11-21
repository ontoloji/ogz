"""
Veritabanı Modülü
SQLite kullanarak notları, hatırlatıcıları ve diğer verileri yönetir
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, db_path=None):
        """Veritabanı bağlantısını başlat"""
        if db_path is None:
            # Kullanıcının home dizininde bir klasör oluştur
            app_data = Path.home() / '.ai_assistant'
            app_data.mkdir(exist_ok=True)
            db_path = app_data / 'assistant.db'

        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # Notlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        # Hatırlatıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                remind_time TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                is_completed INTEGER DEFAULT 0
            )
        ''')

        # Sık kullanılan uygulamalar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP
            )
        ''')

        # Komut geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    # ============ NOT İŞLEMLERİ ============

    def add_note(self, content, tags=None):
        """Yeni not ekle"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO notes (content, tags) VALUES (?, ?)',
            (content, tags)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all_notes(self):
        """Tüm notları getir"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notes ORDER BY created_at DESC')
        return cursor.fetchall()

    def search_notes(self, keyword):
        """Notlarda arama yap"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM notes WHERE content LIKE ? OR tags LIKE ? ORDER BY created_at DESC',
            (f'%{keyword}%', f'%{keyword}%')
        )
        return cursor.fetchall()

    def delete_note(self, note_id):
        """Not sil"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()

    # ============ HATIRLATICI İŞLEMLERİ ============

    def add_reminder(self, title, remind_time, description=None):
        """Yeni hatırlatıcı ekle"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO reminders (title, description, remind_time) VALUES (?, ?, ?)',
            (title, description, remind_time)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_active_reminders(self):
        """Aktif hatırlatıcıları getir"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM reminders
            WHERE is_active = 1 AND is_completed = 0
            ORDER BY remind_time ASC
        ''')
        return cursor.fetchall()

    def get_due_reminders(self):
        """Zamanı gelmiş hatırlatıcıları getir"""
        cursor = self.conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT * FROM reminders
            WHERE is_active = 1 AND is_completed = 0 AND remind_time <= ?
            ORDER BY remind_time ASC
        ''', (now,))
        return cursor.fetchall()

    def complete_reminder(self, reminder_id):
        """Hatırlatıcıyı tamamlandı olarak işaretle"""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE reminders SET is_completed = 1 WHERE id = ?',
            (reminder_id,)
        )
        self.conn.commit()

    def delete_reminder(self, reminder_id):
        """Hatırlatıcıyı sil"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        self.conn.commit()

    # ============ UYGULAMA İŞLEMLERİ ============

    def add_favorite_app(self, name, path):
        """Favori uygulama ekle"""
        cursor = self.conn.cursor()
        # Önce var mı kontrol et
        cursor.execute('SELECT id FROM favorite_apps WHERE path = ?', (path,))
        result = cursor.fetchone()

        if result:
            # Varsa usage_count'u artır
            cursor.execute(
                'UPDATE favorite_apps SET usage_count = usage_count + 1, last_used = ? WHERE id = ?',
                (datetime.now(), result[0])
            )
        else:
            # Yoksa yeni ekle
            cursor.execute(
                'INSERT INTO favorite_apps (name, path, usage_count, last_used) VALUES (?, ?, 1, ?)',
                (name, path, datetime.now())
            )

        self.conn.commit()

    def get_favorite_apps(self, limit=10):
        """En çok kullanılan uygulamaları getir"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM favorite_apps
            ORDER BY usage_count DESC, last_used DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def search_favorite_apps(self, keyword):
        """Favori uygulamalarda arama yap"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM favorite_apps WHERE name LIKE ? ORDER BY usage_count DESC',
            (f'%{keyword}%',)
        )
        return cursor.fetchall()

    # ============ KOMUT GEÇMİŞİ ============

    def add_command_history(self, command, response):
        """Komut geçmişine ekle"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO command_history (command, response) VALUES (?, ?)',
            (command, response)
        )
        self.conn.commit()

    def get_command_history(self, limit=50):
        """Komut geçmişini getir"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM command_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            self.conn.close()
