"""
Veritabanı yönetim modülü - Wealth Tracker
SQLite kullanarak kullanıcı, birikimler ve ayarları saklar
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_path="wealth_tracker.db"):
        """Veritabanı bağlantısını başlat"""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Veritabanı bağlantısı oluştur"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Kullanıcı tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Birikimler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                asset_type TEXT NOT NULL,
                asset_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                purchase_price REAL,
                purchase_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password: str) -> str:
        """Şifreyi hash'le"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, password: str) -> bool:
        """Yeni kullanıcı oluştur"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> Optional[int]:
        """Kullanıcı doğrula ve user_id döndür"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)

        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def add_saving(self, user_id: int, asset_type: str, asset_name: str,
                   quantity: float, purchase_price: float = None,
                   purchase_date: str = None, notes: str = "") -> bool:
        """Yeni birikim ekle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if purchase_date is None:
                purchase_date = datetime.now().strftime("%Y-%m-%d")

            cursor.execute(
                """INSERT INTO savings
                   (user_id, asset_type, asset_name, quantity, purchase_price,
                    purchase_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, asset_type, asset_name, quantity, purchase_price,
                 purchase_date, notes)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Hata: {e}")
            return False

    def get_savings(self, user_id: int) -> List[Dict]:
        """Kullanıcının tüm birikimlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, asset_type, asset_name, quantity, purchase_price,
                      purchase_date, notes, created_at
               FROM savings WHERE user_id = ?
               ORDER BY created_at DESC""",
            (user_id,)
        )

        columns = ['id', 'asset_type', 'asset_name', 'quantity', 'purchase_price',
                   'purchase_date', 'notes', 'created_at']

        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        conn.close()
        return results

    def delete_saving(self, saving_id: int, user_id: int) -> bool:
        """Birikim kaydını sil"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM savings WHERE id = ? AND user_id = ?",
                (saving_id, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Hata: {e}")
            return False

    def update_saving(self, saving_id: int, user_id: int, quantity: float,
                     notes: str = "") -> bool:
        """Birikim miktarını güncelle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE savings SET quantity = ?, notes = ?
                   WHERE id = ? AND user_id = ?""",
                (quantity, notes, saving_id, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Hata: {e}")
            return False
