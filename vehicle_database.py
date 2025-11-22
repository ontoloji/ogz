"""
Araç Kalifikasyon Veritabanı Modülü
SQLite veritabanı yönetimi ve veri erişim katmanı
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os
import shutil


class VehicleDatabase:
    """Araç kalifikasyon veritabanı yönetim sınıfı"""

    def __init__(self, db_path: str = "vehicle_qualification.db"):
        """
        Veritabanı bağlantısını başlat

        Args:
            db_path: Veritabanı dosya yolu
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Veritabanına bağlan"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Dict-like access
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        """Veritabanı tablolarını oluştur"""

        # Araçlar tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT,
                manufacturer TEXT,
                year INTEGER,
                vehicle_type TEXT,
                image_path TEXT,
                specifications TEXT,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)

        # Günlük girdiler tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                entry_date DATE NOT NULL,
                entry_time TIME DEFAULT (strftime('%H:%M:%S', 'now', 'localtime')),
                test_type TEXT,
                test_result TEXT,
                distance_km REAL,
                duration_hours REAL,
                fuel_consumption REAL,
                energy_consumption REAL,
                status TEXT,
                issues TEXT,
                notes TEXT,
                operator TEXT,
                temperature REAL,
                weather TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles (id) ON DELETE CASCADE
            )
        """)

        # İndeksler oluştur
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vehicle_status
            ON vehicles(status)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_entries_vehicle
            ON daily_entries(vehicle_id, entry_date DESC)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_entries_date
            ON daily_entries(entry_date DESC)
        """)

        self.conn.commit()

    # ============= ARAÇ İŞLEMLERİ =============

    def add_vehicle(self, name: str, model: str = None, manufacturer: str = None,
                   year: int = None, vehicle_type: str = None, image_path: str = None,
                   specifications: Dict = None, notes: str = None) -> int:
        """
        Yeni araç ekle

        Args:
            name: Araç adı
            model: Model
            manufacturer: Üretici
            year: Yıl
            vehicle_type: Araç tipi (Elektrikli, Dizel, vb.)
            image_path: Araç resim yolu
            specifications: Teknik özellikler (dict)
            notes: Notlar

        Returns:
            Eklenen aracın ID'si
        """
        # Resmi kopyala
        saved_image_path = None
        if image_path and os.path.exists(image_path):
            saved_image_path = self._save_vehicle_image(image_path, name)

        # Özellikleri JSON'a dönüştür
        specs_json = json.dumps(specifications) if specifications else None

        self.cursor.execute("""
            INSERT INTO vehicles (name, model, manufacturer, year, vehicle_type,
                                image_path, specifications, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, model, manufacturer, year, vehicle_type,
              saved_image_path, specs_json, notes))

        self.conn.commit()
        return self.cursor.lastrowid

    def update_vehicle(self, vehicle_id: int, **kwargs):
        """
        Araç bilgilerini güncelle

        Args:
            vehicle_id: Araç ID
            **kwargs: Güncellenecek alanlar
        """
        # İzin verilen alanlar
        allowed_fields = ['name', 'model', 'manufacturer', 'year',
                         'vehicle_type', 'image_path', 'specifications',
                         'notes', 'status']

        # Resim güncellemesi varsa
        if 'image_path' in kwargs and kwargs['image_path']:
            if os.path.exists(kwargs['image_path']):
                vehicle = self.get_vehicle(vehicle_id)
                kwargs['image_path'] = self._save_vehicle_image(
                    kwargs['image_path'], vehicle['name']
                )

        # Specifications dict ise JSON'a çevir
        if 'specifications' in kwargs and isinstance(kwargs['specifications'], dict):
            kwargs['specifications'] = json.dumps(kwargs['specifications'])

        # SQL oluştur
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)

        if updates:
            updates.append("updated_date = CURRENT_TIMESTAMP")
            values.append(vehicle_id)

            sql = f"UPDATE vehicles SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(sql, values)
            self.conn.commit()

    def get_vehicle(self, vehicle_id: int) -> Optional[Dict]:
        """
        Araç bilgilerini getir

        Args:
            vehicle_id: Araç ID

        Returns:
            Araç bilgileri dict veya None
        """
        self.cursor.execute("""
            SELECT * FROM vehicles WHERE id = ?
        """, (vehicle_id,))

        row = self.cursor.fetchone()
        if row:
            vehicle = dict(row)
            # JSON'ı dict'e çevir
            if vehicle['specifications']:
                vehicle['specifications'] = json.loads(vehicle['specifications'])
            return vehicle
        return None

    def get_all_vehicles(self, status: str = 'active') -> List[Dict]:
        """
        Tüm araçları getir

        Args:
            status: Araç durumu ('active', 'inactive', 'all')

        Returns:
            Araç listesi
        """
        if status == 'all':
            self.cursor.execute("""
                SELECT * FROM vehicles
                ORDER BY created_date DESC
            """)
        else:
            self.cursor.execute("""
                SELECT * FROM vehicles
                WHERE status = ?
                ORDER BY created_date DESC
            """, (status,))

        vehicles = []
        for row in self.cursor.fetchall():
            vehicle = dict(row)
            if vehicle['specifications']:
                vehicle['specifications'] = json.loads(vehicle['specifications'])
            vehicles.append(vehicle)

        return vehicles

    def delete_vehicle(self, vehicle_id: int):
        """
        Aracı sil (soft delete)

        Args:
            vehicle_id: Araç ID
        """
        self.cursor.execute("""
            UPDATE vehicles SET status = 'deleted' WHERE id = ?
        """, (vehicle_id,))
        self.conn.commit()

    def search_vehicles(self, search_term: str) -> List[Dict]:
        """
        Araçlarda ara

        Args:
            search_term: Arama terimi

        Returns:
            Bulunan araçlar listesi
        """
        search_pattern = f"%{search_term}%"
        self.cursor.execute("""
            SELECT * FROM vehicles
            WHERE status = 'active'
            AND (name LIKE ? OR model LIKE ? OR manufacturer LIKE ?)
            ORDER BY name
        """, (search_pattern, search_pattern, search_pattern))

        vehicles = []
        for row in self.cursor.fetchall():
            vehicle = dict(row)
            if vehicle['specifications']:
                vehicle['specifications'] = json.loads(vehicle['specifications'])
            vehicles.append(vehicle)

        return vehicles

    # ============= GÜNLÜK GİRDİ İŞLEMLERİ =============

    def add_daily_entry(self, vehicle_id: int, entry_date: str = None,
                       test_type: str = None, test_result: str = None,
                       distance_km: float = None, duration_hours: float = None,
                       fuel_consumption: float = None, energy_consumption: float = None,
                       status: str = None, issues: str = None, notes: str = None,
                       operator: str = None, temperature: float = None,
                       weather: str = None) -> int:
        """
        Günlük girdi ekle

        Args:
            vehicle_id: Araç ID
            entry_date: Girdi tarihi (YYYY-MM-DD format, None ise bugün)
            test_type: Test tipi
            test_result: Test sonucu
            distance_km: Mesafe (km)
            duration_hours: Süre (saat)
            fuel_consumption: Yakıt tüketimi
            energy_consumption: Enerji tüketimi
            status: Durum
            issues: Sorunlar
            notes: Notlar
            operator: Operatör
            temperature: Sıcaklık
            weather: Hava durumu

        Returns:
            Eklenen girdinin ID'si
        """
        if entry_date is None:
            entry_date = datetime.now().strftime('%Y-%m-%d')

        self.cursor.execute("""
            INSERT INTO daily_entries (
                vehicle_id, entry_date, test_type, test_result,
                distance_km, duration_hours, fuel_consumption, energy_consumption,
                status, issues, notes, operator, temperature, weather
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vehicle_id, entry_date, test_type, test_result,
              distance_km, duration_hours, fuel_consumption, energy_consumption,
              status, issues, notes, operator, temperature, weather))

        self.conn.commit()
        return self.cursor.lastrowid

    def get_vehicle_entries(self, vehicle_id: int, limit: int = None) -> List[Dict]:
        """
        Araç günlük girdilerini getir

        Args:
            vehicle_id: Araç ID
            limit: Maksimum kayıt sayısı

        Returns:
            Günlük girdiler listesi
        """
        if limit:
            self.cursor.execute("""
                SELECT * FROM daily_entries
                WHERE vehicle_id = ?
                ORDER BY entry_date DESC, entry_time DESC
                LIMIT ?
            """, (vehicle_id, limit))
        else:
            self.cursor.execute("""
                SELECT * FROM daily_entries
                WHERE vehicle_id = ?
                ORDER BY entry_date DESC, entry_time DESC
            """, (vehicle_id,))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_entries_by_date_range(self, vehicle_id: int = None,
                                  start_date: str = None,
                                  end_date: str = None) -> List[Dict]:
        """
        Tarih aralığına göre girdileri getir

        Args:
            vehicle_id: Araç ID (None ise tüm araçlar)
            start_date: Başlangıç tarihi (YYYY-MM-DD)
            end_date: Bitiş tarihi (YYYY-MM-DD)

        Returns:
            Günlük girdiler listesi
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if vehicle_id:
            self.cursor.execute("""
                SELECT * FROM daily_entries
                WHERE vehicle_id = ?
                AND entry_date BETWEEN ? AND ?
                ORDER BY entry_date DESC, entry_time DESC
            """, (vehicle_id, start_date, end_date))
        else:
            self.cursor.execute("""
                SELECT * FROM daily_entries
                WHERE entry_date BETWEEN ? AND ?
                ORDER BY entry_date DESC, entry_time DESC
            """, (start_date, end_date))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_weekly_entries(self, vehicle_id: int = None,
                          week_offset: int = 0) -> List[Dict]:
        """
        Haftalık girdileri getir

        Args:
            vehicle_id: Araç ID (None ise tüm araçlar)
            week_offset: Hafta ofset (0: bu hafta, -1: geçen hafta, vb.)

        Returns:
            Günlük girdiler listesi
        """
        # Haftanın başlangıcı (Pazartesi)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)

        start_date = week_start.strftime('%Y-%m-%d')
        end_date = week_end.strftime('%Y-%m-%d')

        return self.get_entries_by_date_range(vehicle_id, start_date, end_date)

    def update_daily_entry(self, entry_id: int, **kwargs):
        """
        Günlük girdi güncelle

        Args:
            entry_id: Girdi ID
            **kwargs: Güncellenecek alanlar
        """
        allowed_fields = ['entry_date', 'test_type', 'test_result',
                         'distance_km', 'duration_hours', 'fuel_consumption',
                         'energy_consumption', 'status', 'issues', 'notes',
                         'operator', 'temperature', 'weather']

        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)

        if updates:
            values.append(entry_id)
            sql = f"UPDATE daily_entries SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(sql, values)
            self.conn.commit()

    def delete_daily_entry(self, entry_id: int):
        """
        Günlük girdi sil

        Args:
            entry_id: Girdi ID
        """
        self.cursor.execute("""
            DELETE FROM daily_entries WHERE id = ?
        """, (entry_id,))
        self.conn.commit()

    # ============= İSTATİSTİK VE RAPOR =============

    def get_vehicle_statistics(self, vehicle_id: int) -> Dict:
        """
        Araç istatistiklerini getir

        Args:
            vehicle_id: Araç ID

        Returns:
            İstatistikler dict
        """
        self.cursor.execute("""
            SELECT
                COUNT(*) as total_entries,
                SUM(distance_km) as total_distance,
                SUM(duration_hours) as total_duration,
                AVG(distance_km) as avg_distance,
                AVG(fuel_consumption) as avg_fuel,
                AVG(energy_consumption) as avg_energy,
                MIN(entry_date) as first_entry,
                MAX(entry_date) as last_entry
            FROM daily_entries
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        row = self.cursor.fetchone()
        return dict(row) if row else {}

    def get_weekly_summary(self, vehicle_id: int = None,
                          week_offset: int = 0) -> Dict:
        """
        Haftalık özet rapor

        Args:
            vehicle_id: Araç ID (None ise tüm araçlar)
            week_offset: Hafta ofset

        Returns:
            Özet rapor dict
        """
        entries = self.get_weekly_entries(vehicle_id, week_offset)

        if not entries:
            return {
                'total_entries': 0,
                'total_distance': 0,
                'total_duration': 0,
                'total_fuel': 0,
                'total_energy': 0,
                'entries': []
            }

        summary = {
            'total_entries': len(entries),
            'total_distance': sum(e['distance_km'] or 0 for e in entries),
            'total_duration': sum(e['duration_hours'] or 0 for e in entries),
            'total_fuel': sum(e['fuel_consumption'] or 0 for e in entries),
            'total_energy': sum(e['energy_consumption'] or 0 for e in entries),
            'entries': entries
        }

        return summary

    # ============= YARDIMCI FONKSİYONLAR =============

    def _save_vehicle_image(self, source_path: str, vehicle_name: str) -> str:
        """
        Araç resmini kaydet

        Args:
            source_path: Kaynak resim yolu
            vehicle_name: Araç adı

        Returns:
            Kaydedilen resim yolu
        """
        # images klasörü oluştur
        images_dir = os.path.join(os.path.dirname(self.db_path), 'vehicle_images')
        os.makedirs(images_dir, exist_ok=True)

        # Dosya uzantısı
        ext = os.path.splitext(source_path)[1]

        # Yeni dosya adı (timestamp ile)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c for c in vehicle_name if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"{safe_name}_{timestamp}{ext}"

        dest_path = os.path.join(images_dir, filename)

        # Kopyala
        shutil.copy2(source_path, dest_path)

        return dest_path

    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Test
if __name__ == "__main__":
    # Test veritabanı
    db = VehicleDatabase("test_vehicles.db")

    # Test aracı ekle
    vehicle_id = db.add_vehicle(
        name="Test Aracı A1",
        model="Model X",
        manufacturer="Test Motors",
        year=2024,
        vehicle_type="Elektrikli",
        specifications={
            "motor_gucu": "150 kW",
            "batarya": "75 kWh",
            "menzil": "400 km"
        },
        notes="Test aracı"
    )

    print(f"Araç eklendi: ID={vehicle_id}")

    # Günlük girdi ekle
    entry_id = db.add_daily_entry(
        vehicle_id=vehicle_id,
        test_type="SORT 1",
        test_result="Başarılı",
        distance_km=15.5,
        duration_hours=1.2,
        energy_consumption=12.3,
        status="Tamamlandı",
        operator="Test Operatör",
        temperature=22.5,
        notes="Test girdi"
    )

    print(f"Günlük girdi eklendi: ID={entry_id}")

    # Araç bilgilerini getir
    vehicle = db.get_vehicle(vehicle_id)
    print(f"\nAraç Bilgileri: {vehicle['name']}")
    print(f"Model: {vehicle['model']}")
    print(f"Özellikler: {vehicle['specifications']}")

    # Günlük girdileri getir
    entries = db.get_vehicle_entries(vehicle_id)
    print(f"\nGünlük Girdi Sayısı: {len(entries)}")

    # İstatistikler
    stats = db.get_vehicle_statistics(vehicle_id)
    print(f"\nİstatistikler: {stats}")

    db.close()
    print("\nTest başarılı!")
