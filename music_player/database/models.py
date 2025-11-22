"""
Müzik Çalar - Veritabanı Modelleri
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


class DatabaseManager:
    """SQLite veritabanı yöneticisi"""

    def __init__(self, db_path: Path):
        """
        Veritabanı yöneticisini başlat

        Args:
            db_path: Veritabanı dosya yolu
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.initialize_database()

    def connect(self):
        """Veritabanına bağlan"""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Dict-like access

    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def initialize_database(self):
        """Veritabanı tablolarını oluştur"""
        self.connect()

        # Playlists tablosu
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tracks tablosu
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,
                duration INTEGER,
                source TEXT,
                source_id TEXT,
                thumbnail_url TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                play_count INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Playlist-Track ilişkisi (many-to-many)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
                UNIQUE(playlist_id, track_id)
            )
        """)

        # Radio stations tablosu
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS radio_stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stream_url TEXT NOT NULL UNIQUE,
                homepage TEXT,
                genre TEXT,
                country TEXT,
                language TEXT,
                bitrate INTEGER,
                is_favorite BOOLEAN DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Equalizer presets
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS eq_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                band_31hz REAL DEFAULT 0,
                band_62hz REAL DEFAULT 0,
                band_125hz REAL DEFAULT 0,
                band_250hz REAL DEFAULT 0,
                band_500hz REAL DEFAULT 0,
                band_1khz REAL DEFAULT 0,
                band_2khz REAL DEFAULT 0,
                band_4khz REAL DEFAULT 0,
                band_8khz REAL DEFAULT 0,
                band_16khz REAL DEFAULT 0,
                is_custom BOOLEAN DEFAULT 0
            )
        """)

        # Play history
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
            )
        """)

        self.connection.commit()
        self._insert_default_eq_presets()

    def _insert_default_eq_presets(self):
        """Varsayılan equalizer preset'lerini ekle"""
        presets = [
            ("Flat", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            ("Pop", [-1, -0.5, 0, 2, 4, 4, 2, 0, -0.5, -1]),
            ("Rock", [4, 3, -2, -3, -1, 1, 3, 4, 4, 4]),
            ("Jazz", [3, 2, 1, 1, -1, -1, 0, 1, 2, 3]),
            ("Classical", [3, 2, -1, -1, 0, 0, -1, -1, 2, 3]),
            ("Bass Boost", [6, 5, 4, 2, 0, -1, -2, -2, -2, -2]),
            ("Treble Boost", [-2, -2, -2, -1, 0, 2, 4, 5, 6, 6]),
            ("Vocal", [-2, -1, 1, 3, 3, 2, 1, -1, -2, -3]),
        ]

        cursor = self.connection.cursor()
        for name, bands in presets:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO eq_presets
                    (name, band_31hz, band_62hz, band_125hz, band_250hz, band_500hz,
                     band_1khz, band_2khz, band_4khz, band_8khz, band_16khz, is_custom)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (name, *bands))
            except sqlite3.IntegrityError:
                pass  # Preset zaten var

        self.connection.commit()

    # === PLAYLIST OPERASYONLARI ===

    def create_playlist(self, name: str, description: str = "") -> int:
        """
        Yeni playlist oluştur

        Args:
            name: Playlist adı
            description: Açıklama

        Returns:
            Oluşturulan playlist ID
        """
        cursor = self.connection.execute(
            "INSERT INTO playlists (name, description) VALUES (?, ?)",
            (name, description)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_playlists(self) -> List[Dict[str, Any]]:
        """Tüm playlist'leri getir"""
        cursor = self.connection.execute(
            "SELECT * FROM playlists ORDER BY updated_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def delete_playlist(self, playlist_id: int):
        """Playlist sil"""
        self.connection.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        self.connection.commit()

    def update_playlist(self, playlist_id: int, name: str = None, description: str = None):
        """Playlist bilgilerini güncelle"""
        if name:
            self.connection.execute(
                "UPDATE playlists SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (name, playlist_id)
            )
        if description is not None:
            self.connection.execute(
                "UPDATE playlists SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (description, playlist_id)
            )
        self.connection.commit()

    # === TRACK OPERASYONLARI ===

    def add_track(self, title: str, artist: str = "", album: str = "",
                  duration: int = 0, source: str = "", source_id: str = "",
                  thumbnail_url: str = "") -> int:
        """
        Yeni şarkı ekle veya mevcut ID'yi döndür

        Returns:
            Track ID
        """
        # Aynı kaynak ve kaynak ID'ye sahip track var mı kontrol et
        cursor = self.connection.execute(
            "SELECT id FROM tracks WHERE source = ? AND source_id = ?",
            (source, source_id)
        )
        existing = cursor.fetchone()

        if existing:
            return existing['id']

        cursor = self.connection.execute("""
            INSERT INTO tracks
            (title, artist, album, duration, source, source_id, thumbnail_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, artist, album, duration, source, source_id, thumbnail_url))

        self.connection.commit()
        return cursor.lastrowid

    def add_track_to_playlist(self, playlist_id: int, track_id: int):
        """Playlist'e şarkı ekle"""
        # Mevcut maksimum pozisyonu bul
        cursor = self.connection.execute(
            "SELECT MAX(position) as max_pos FROM playlist_tracks WHERE playlist_id = ?",
            (playlist_id,)
        )
        result = cursor.fetchone()
        next_position = (result['max_pos'] or 0) + 1

        try:
            self.connection.execute("""
                INSERT INTO playlist_tracks (playlist_id, track_id, position)
                VALUES (?, ?, ?)
            """, (playlist_id, track_id, next_position))
            self.connection.commit()

            # Playlist güncelleme zamanını güncelle
            self.connection.execute(
                "UPDATE playlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (playlist_id,)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass  # Track zaten playlist'de

    def remove_track_from_playlist(self, playlist_id: int, track_id: int):
        """Playlist'ten şarkı çıkar"""
        self.connection.execute(
            "DELETE FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?",
            (playlist_id, track_id)
        )
        self.connection.commit()

    def get_playlist_tracks(self, playlist_id: int) -> List[Dict[str, Any]]:
        """Playlist'teki tüm şarkıları getir"""
        cursor = self.connection.execute("""
            SELECT t.*, pt.position
            FROM tracks t
            JOIN playlist_tracks pt ON t.id = pt.track_id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
        """, (playlist_id,))
        return [dict(row) for row in cursor.fetchall()]

    def set_favorite(self, track_id: int, is_favorite: bool):
        """Şarkıyı favorilere ekle/çıkar"""
        self.connection.execute(
            "UPDATE tracks SET is_favorite = ? WHERE id = ?",
            (1 if is_favorite else 0, track_id)
        )
        self.connection.commit()

    def get_favorites(self) -> List[Dict[str, Any]]:
        """Favori şarkıları getir"""
        cursor = self.connection.execute(
            "SELECT * FROM tracks WHERE is_favorite = 1 ORDER BY added_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    # === RADİO İSTASYONLARI ===

    def add_radio_station(self, name: str, stream_url: str, genre: str = "",
                          country: str = "", **kwargs) -> int:
        """Radyo istasyonu ekle"""
        cursor = self.connection.execute("""
            INSERT OR IGNORE INTO radio_stations
            (name, stream_url, homepage, genre, country, language, bitrate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, stream_url, kwargs.get('homepage', ''), genre, country,
              kwargs.get('language', ''), kwargs.get('bitrate', 0)))
        self.connection.commit()
        return cursor.lastrowid

    def get_radio_stations(self, genre: str = None, country: str = None) -> List[Dict[str, Any]]:
        """Radyo istasyonlarını getir (filtrelenebilir)"""
        query = "SELECT * FROM radio_stations WHERE 1=1"
        params = []

        if genre:
            query += " AND genre = ?"
            params.append(genre)
        if country:
            query += " AND country = ?"
            params.append(country)

        query += " ORDER BY name"

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_favorite_radio_stations(self) -> List[Dict[str, Any]]:
        """Favori radyo istasyonlarını getir"""
        cursor = self.connection.execute(
            "SELECT * FROM radio_stations WHERE is_favorite = 1 ORDER BY name"
        )
        return [dict(row) for row in cursor.fetchall()]

    # === EQUALIZER PRESETS ===

    def get_eq_presets(self) -> List[Dict[str, Any]]:
        """Tüm EQ preset'lerini getir"""
        cursor = self.connection.execute("SELECT * FROM eq_presets ORDER BY is_custom, name")
        return [dict(row) for row in cursor.fetchall()]

    def save_custom_eq_preset(self, name: str, bands: List[float]) -> int:
        """Özel EQ preset kaydet"""
        cursor = self.connection.execute("""
            INSERT OR REPLACE INTO eq_presets
            (name, band_31hz, band_62hz, band_125hz, band_250hz, band_500hz,
             band_1khz, band_2khz, band_4khz, band_8khz, band_16khz, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (name, *bands))
        self.connection.commit()
        return cursor.lastrowid

    # === PLAYİSTORY ===

    def add_to_history(self, track_id: int):
        """Çalma geçmişine ekle ve çalma sayısını artır"""
        self.connection.execute(
            "INSERT INTO play_history (track_id) VALUES (?)",
            (track_id,)
        )
        self.connection.execute(
            "UPDATE tracks SET play_count = play_count + 1 WHERE id = ?",
            (track_id,)
        )
        self.connection.commit()

    def get_recently_played(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Son çalınan şarkıları getir"""
        cursor = self.connection.execute("""
            SELECT t.*, ph.played_at
            FROM tracks t
            JOIN play_history ph ON t.id = ph.track_id
            ORDER BY ph.played_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
