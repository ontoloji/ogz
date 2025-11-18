"""
SORT Test Otomasyon Sistemi - Veri Kayıt Modülü
Test verilerini CSV formatında kaydetme ve okuma
"""

import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd


class DataLogger:
    """Test verilerini CSV dosyasına kaydet"""

    CSV_HEADER = [
        'timestamp',
        'distance_m',
        'speed_kmh',
        'pedal_pct',
        'energy_kwh',
        'segment',
        'test_status'
    ]

    def __init__(self, filename: Optional[str] = None, directory: str = 'data'):
        """
        Data logger başlat

        Args:
            filename: CSV dosya adı (None ise otomatik oluştur)
            directory: Kayıt klasörü
        """
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_{timestamp}.csv"

        self.filepath = self.directory / filename
        self.file_handle = None
        self.csv_writer = None
        self.is_open = False
        self.row_count = 0

        self.logger = logging.getLogger(__name__)

    def open(self):
        """Dosyayı aç ve header yaz"""
        try:
            self.file_handle = open(self.filepath, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.DictWriter(self.file_handle, fieldnames=self.CSV_HEADER)
            self.csv_writer.writeheader()
            self.is_open = True
            self.row_count = 0
            self.logger.info(f"Veri kaydı başlatıldı: {self.filepath}")
        except Exception as e:
            self.logger.error(f"Dosya açılamadı: {e}")
            raise

    def write(self, data: Dict[str, Any]):
        """
        Veri satırı yaz

        Args:
            data: Veri dictionary (header ile eşleşmeli)
        """
        if not self.is_open:
            self.logger.warning("Dosya açık değil, önce open() çağrılmalı")
            return

        try:
            # Timestamp ekle (eğer yoksa)
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # Eksik alanları doldur
            row = {key: data.get(key, '') for key in self.CSV_HEADER}

            self.csv_writer.writerow(row)
            self.row_count += 1

            # Her 10 satırda bir flush (veri kaybını önle)
            if self.row_count % 10 == 0:
                self.file_handle.flush()

        except Exception as e:
            self.logger.error(f"Veri yazılamadı: {e}")

    def close(self):
        """Dosyayı kapat"""
        if self.is_open and self.file_handle:
            try:
                self.file_handle.flush()
                self.file_handle.close()
                self.is_open = False
                self.logger.info(f"Veri kaydı tamamlandı: {self.filepath} ({self.row_count} satır)")
            except Exception as e:
                self.logger.error(f"Dosya kapatılamadı: {e}")

    def __enter__(self):
        """Context manager desteği"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.close()

    @staticmethod
    def load_test_data(filepath: str) -> pd.DataFrame:
        """
        Test verisini yükle

        Args:
            filepath: CSV dosya yolu

        Returns:
            pandas DataFrame
        """
        try:
            df = pd.read_csv(filepath)
            # Timestamp'i datetime'a çevir
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            logging.error(f"Test verisi yüklenemedi: {e}")
            return None

    @staticmethod
    def get_test_files(directory: str = 'data', pattern: str = '*.csv') -> List[Path]:
        """
        Klasördeki test dosyalarını listele

        Args:
            directory: Arama klasörü
            pattern: Dosya pattern

        Returns:
            Dosya yolu listesi (tarihe göre sıralı)
        """
        directory = Path(directory)
        if not directory.exists():
            return []

        files = list(directory.glob(pattern))
        # Değiştirilme tarihine göre sırala (en yeni en üstte)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return files

    @staticmethod
    def get_test_summary(filepath: str) -> Dict[str, Any]:
        """
        Test dosyasının özetini çıkar

        Args:
            filepath: CSV dosya yolu

        Returns:
            Özet bilgiler
        """
        try:
            df = DataLogger.load_test_data(filepath)
            if df is None or df.empty:
                return None

            summary = {
                'filepath': filepath,
                'filename': Path(filepath).name,
                'total_rows': len(df),
                'total_distance': df['distance_m'].max() if 'distance_m' in df.columns else 0,
                'max_speed': df['speed_kmh'].max() if 'speed_kmh' in df.columns else 0,
                'avg_speed': df['speed_kmh'].mean() if 'speed_kmh' in df.columns else 0,
                'total_energy': df['energy_kwh'].max() if 'energy_kwh' in df.columns else 0,
                'duration': None,
                'start_time': None,
                'end_time': None
            }

            # Zaman bilgileri
            if 'timestamp' in df.columns and len(df) > 0:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                summary['start_time'] = df['timestamp'].iloc[0]
                summary['end_time'] = df['timestamp'].iloc[-1]
                summary['duration'] = (summary['end_time'] - summary['start_time']).total_seconds()

            return summary

        except Exception as e:
            logging.error(f"Test özeti oluşturulamadı: {e}")
            return None

    @staticmethod
    def filter_tests_by_criteria(
        test_files: List[Path],
        min_distance: float = None,
        max_distance: float = None,
        direction: str = None
    ) -> List[Dict[str, Any]]:
        """
        Test dosyalarını kriterlere göre filtrele

        Args:
            test_files: Test dosyaları listesi
            min_distance: Minimum toplam mesafe (m)
            max_distance: Maximum toplam mesafe (m)
            direction: Yön filtresi ('GIDIS' veya 'DONUS')

        Returns:
            Filtrelenmiş test özeti listesi
        """
        filtered = []

        for filepath in test_files:
            # Yön filtresi (dosya adından)
            if direction:
                filename = filepath.name.upper()
                if direction.upper() not in filename:
                    continue

            # Özet al
            summary = DataLogger.get_test_summary(str(filepath))
            if summary is None:
                continue

            # Mesafe filtresi
            if min_distance is not None and summary['total_distance'] < min_distance:
                continue
            if max_distance is not None and summary['total_distance'] > max_distance:
                continue

            filtered.append(summary)

        return filtered


class TestMetadata:
    """Test meta verilerini yönet"""

    def __init__(self, csv_filepath: str):
        """
        Test meta verileri

        Args:
            csv_filepath: İlişkili CSV dosya yolu
        """
        self.csv_filepath = Path(csv_filepath)
        self.metadata_filepath = self.csv_filepath.with_suffix('.meta.json')

        self.metadata = {
            'test_type': '',  # SORT1, SORT2, SORT3
            'direction': '',  # GIDIS, DONUS
            'vehicle': '',
            'driver': '',
            'temperature': '',
            'notes': '',
            'accel_pedal': 0,
            'max_speed_limit': 0,
            'pid_kp': 0.0,
            'pid_ki': 0.0,
            'pid_kd': 0.0,
            'created_at': datetime.now().isoformat()
        }

    def set(self, key: str, value: Any):
        """Meta veri ayarla"""
        self.metadata[key] = value

    def get(self, key: str, default=None) -> Any:
        """Meta veri al"""
        return self.metadata.get(key, default)

    def save(self):
        """Meta verileri kaydet"""
        try:
            import json
            with open(self.metadata_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Meta veri kaydedilemedi: {e}")

    def load(self) -> bool:
        """Meta verileri yükle"""
        try:
            import json
            if self.metadata_filepath.exists():
                with open(self.metadata_filepath, 'r', encoding='utf-8') as f:
                    self.metadata.update(json.load(f))
                return True
        except Exception as e:
            logging.error(f"Meta veri yüklenemedi: {e}")
        return False


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    # Örnek veri kaydetme
    with DataLogger(filename='test_example.csv') as logger:
        for i in range(10):
            logger.write({
                'distance_m': i * 10,
                'speed_kmh': 20 + i,
                'pedal_pct': 50,
                'energy_kwh': i * 0.1,
                'segment': 'ACCEL',
                'test_status': 'RUNNING'
            })

    # Veri yükleme
    df = DataLogger.load_test_data('data/test_example.csv')
    if df is not None:
        print("\nYüklenen veri:")
        print(df)

    # Özet
    summary = DataLogger.get_test_summary('data/test_example.csv')
    if summary:
        print("\nTest özeti:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

    # Dosya listesi
    files = DataLogger.get_test_files()
    print(f"\nBulunan test dosyaları: {len(files)}")
    for f in files[:5]:  # İlk 5 dosya
        print(f"  {f.name}")
