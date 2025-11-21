"""
Excel dosyalarından test verilerini okuma modülü
Windows Excel dosyaları ile uyumlu
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Parent dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import EXCEL_COLUMNS

class ExcelReader:
    """Excel test verilerini okuma ve işleme sınıfı"""

    def __init__(self, file_path):
        """
        Args:
            file_path (str): Excel dosyasının yolu
        """
        self.file_path = Path(file_path)
        self.data = None
        self.metadata = {}

    def read_file(self, sheet_name=0):
        """
        Excel dosyasını okur

        Args:
            sheet_name: Okunacak sheet (index veya isim)

        Returns:
            bool: Başarılı ise True
        """
        try:
            # Windows Excel dosyalarını okuma
            self.data = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name,
                engine='openpyxl'
            )

            # Sütun isimlerini temizle (boşluk ve özel karakterler)
            self.data.columns = self.data.columns.str.strip()

            return True

        except Exception as e:
            raise Exception(f"Excel dosyası okunamadı: {str(e)}")

    def identify_columns(self):
        """
        Sütunları otomatik olarak tanımlar

        Returns:
            dict: Tanımlanan sütunlar
        """
        identified = {}

        for key, possible_names in EXCEL_COLUMNS.items():
            for col in self.data.columns:
                col_lower = str(col).lower().strip()

                for name in possible_names:
                    name_lower = name.lower().strip()
                    if name_lower in col_lower or col_lower in name_lower:
                        identified[key] = col
                        break

                if key in identified:
                    break

        return identified

    def validate_data(self, column_mapping):
        """
        Veri kalitesini kontrol eder

        Args:
            column_mapping (dict): Sütun eşleştirmeleri

        Returns:
            dict: Validasyon sonuçları
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        # Gerekli sütunların varlığını kontrol et
        required = ['time', 'speed', 'current', 'voltage']
        for req in required:
            if req not in column_mapping:
                results['errors'].append(f"Gerekli sütun bulunamadı: {req}")
                results['valid'] = False

        if not results['valid']:
            return results

        # Veri tiplerini kontrol et
        for key, col in column_mapping.items():
            try:
                # Sayısal veri kontrolü
                pd.to_numeric(self.data[col], errors='coerce')

                # Eksik veri kontrolü
                null_count = self.data[col].isnull().sum()
                if null_count > 0:
                    results['warnings'].append(
                        f"{col} sütununda {null_count} adet eksik veri var"
                    )

                # Negatif değer kontrolü (zaman için)
                if key == 'time':
                    negative_count = (self.data[col] < 0).sum()
                    if negative_count > 0:
                        results['warnings'].append(
                            f"{col} sütununda {negative_count} adet negatif değer var"
                        )

            except Exception as e:
                results['errors'].append(f"{col} sütunu işlenemedi: {str(e)}")
                results['valid'] = False

        return results

    def prepare_data(self, column_mapping):
        """
        Veriyi analiz için hazırlar

        Args:
            column_mapping (dict): Sütun eşleştirmeleri

        Returns:
            pd.DataFrame: Hazırlanmış veri
        """
        # Yeni DataFrame oluştur
        df = pd.DataFrame()

        # Sütunları standart isimlere dönüştür
        for key, col in column_mapping.items():
            df[key] = pd.to_numeric(self.data[col], errors='coerce')

        # Eksik verileri doldurmak için interpolasyon kullan
        df = df.interpolate(method='linear', limit_direction='both')

        # Hala NaN varsa 0 ile doldur
        df = df.fillna(0)

        # Zaman sütununu indeks olarak ayarla (opsiyonel)
        if 'time' in df.columns:
            # Zaman farkını hesapla (delta time)
            df['dt'] = df['time'].diff().fillna(0)

            # Negatif zaman farklarını düzelt
            df.loc[df['dt'] < 0, 'dt'] = 0

        # Güç hesapla (W = V * I)
        if 'voltage' in df.columns and 'current' in df.columns:
            df['power'] = df['voltage'] * df['current']  # Watt
            df['power_kw'] = df['power'] / 1000  # kW

        # Enerji hesapla (Wh = W * t/3600)
        if 'power' in df.columns and 'dt' in df.columns:
            df['energy_wh'] = df['power'] * df['dt'] / 3600
            df['energy_kwh'] = df['energy_wh'] / 1000

            # Kümülatif enerji
            df['cumulative_energy_kwh'] = df['energy_kwh'].cumsum()

        # Mesafe hesapla (m = v * t)
        if 'speed' in df.columns and 'dt' in df.columns:
            # Hızı m/s'ye çevir (km/h -> m/s)
            df['speed_ms'] = df['speed'] / 3.6

            # Mesafe (metre)
            df['distance_m'] = df['speed_ms'] * df['dt']

            # Kümülatif mesafe (km)
            df['cumulative_distance_km'] = df['distance_m'].cumsum() / 1000

        # İvme hesapla (m/s²)
        if 'speed_ms' in df.columns and 'dt' in df.columns:
            df['acceleration'] = df['speed_ms'].diff() / df['dt']
            df['acceleration'] = df['acceleration'].fillna(0)

            # Hızlanma ve yavaşlama fazlarını ayır
            df['accelerating'] = df['acceleration'] > 0.1
            df['decelerating'] = df['acceleration'] < -0.1
            df['cruising'] = (df['acceleration'].abs() <= 0.1) & (df['speed'] > 1)
            df['stopped'] = df['speed'] <= 1

        # Regeneratif frenleme tespiti (negatif güç)
        if 'power' in df.columns:
            df['regenerating'] = df['power'] < -100  # -100W'tan düşük
            df['regen_power'] = df['power'].clip(upper=0).abs()
            df['motor_power'] = df['power'].clip(lower=0)

        # Metadata oluştur
        self.metadata = {
            'total_time': df['time'].max() if 'time' in df.columns else 0,
            'total_distance': df['cumulative_distance_km'].max() if 'cumulative_distance_km' in df.columns else 0,
            'total_energy': df['cumulative_energy_kwh'].max() if 'cumulative_energy_kwh' in df.columns else 0,
            'max_speed': df['speed'].max() if 'speed' in df.columns else 0,
            'avg_speed': df['speed'].mean() if 'speed' in df.columns else 0,
            'max_power': df['power_kw'].max() if 'power_kw' in df.columns else 0,
            'avg_temp': df['temperature'].mean() if 'temperature' in df.columns else None,
            'data_points': len(df)
        }

        return df

    def get_test_info(self):
        """
        Test hakkında özet bilgi döndürür

        Returns:
            dict: Test bilgileri
        """
        return {
            'dosya': self.file_path.name,
            'dosya_yolu': str(self.file_path),
            'veri_sayisi': self.metadata.get('data_points', 0),
            'toplam_sure': f"{self.metadata.get('total_time', 0):.1f} saniye",
            'toplam_mesafe': f"{self.metadata.get('total_distance', 0):.2f} km",
            'toplam_enerji': f"{self.metadata.get('total_energy', 0):.3f} kWh",
            'max_hiz': f"{self.metadata.get('max_speed', 0):.1f} km/h",
            'ortalama_hiz': f"{self.metadata.get('avg_speed', 0):.1f} km/h",
            'max_guc': f"{self.metadata.get('max_power', 0):.1f} kW",
            'ortalama_sicaklik': f"{self.metadata.get('avg_temp', 0):.1f} °C" if self.metadata.get('avg_temp') else "N/A"
        }


def load_excel_data(file_path, sheet_name=0):
    """
    Excel dosyasını yükler ve hazırlar (kolaylık fonksiyonu)

    Args:
        file_path (str): Dosya yolu
        sheet_name: Sheet ismi veya indeksi

    Returns:
        tuple: (DataFrame, metadata dict, info dict)
    """
    reader = ExcelReader(file_path)

    # Dosyayı oku
    reader.read_file(sheet_name)

    # Sütunları tanımla
    columns = reader.identify_columns()

    if not columns:
        raise Exception("Excel dosyasında uygun sütunlar bulunamadı!")

    # Veriyi doğrula
    validation = reader.validate_data(columns)

    if not validation['valid']:
        error_msg = "Veri validasyonu başarısız:\n" + "\n".join(validation['errors'])
        raise Exception(error_msg)

    # Veriyi hazırla
    df = reader.prepare_data(columns)

    return df, reader.metadata, reader.get_test_info(), validation['warnings']


if __name__ == "__main__":
    # Test kodu
    print("Excel Reader Modülü Test")
    print("=" * 50)

    # Test dosyası yoksa uyarı ver
    test_file = Path(__file__).parent.parent.parent / "data" / "ornek_test_verisi.xlsx"

    if not test_file.exists():
        print(f"Test dosyası bulunamadı: {test_file}")
        print("Lütfen önce örnek veri dosyası oluşturun.")
    else:
        try:
            df, metadata, info, warnings = load_excel_data(test_file)

            print("\nTest Bilgileri:")
            for key, value in info.items():
                print(f"  {key}: {value}")

            if warnings:
                print("\nUyarılar:")
                for warning in warnings:
                    print(f"  - {warning}")

            print(f"\nVeri başarıyla yüklendi: {len(df)} satır")
            print("\nİlk 5 satır:")
            print(df.head())

        except Exception as e:
            print(f"Hata: {str(e)}")
