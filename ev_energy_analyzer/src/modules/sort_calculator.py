"""
UITP SORT Test Döngüsü Hesaplama Modülü
UITP (International Association of Public Transport) SORT (Standardised On-Road Test) metodolojisi
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import SORT_CYCLES

class SORTCalculator:
    """UITP SORT test döngüsü hesaplamaları"""

    def __init__(self, dataframe):
        """
        Args:
            dataframe (pd.DataFrame): Test verileri
        """
        self.df = dataframe
        self.results = {}

    def detect_cycles(self):
        """
        Test verisinde SORT döngülerini tespit eder

        Returns:
            list: Tespit edilen döngüler ve indeksleri
        """
        cycles = []

        # Durma noktalarını bul (hız < 1 km/h ve 10 saniyeden fazla)
        stopped = self.df['speed'] < 1

        # Durma periyotlarını grupla
        stop_groups = (stopped != stopped.shift()).cumsum()
        stop_periods = self.df[stopped].groupby(stop_groups)

        # Her durma periyodunu kontrol et
        for group_id, group in stop_periods:
            if len(group) > 10:  # En az 10 saniye durma
                cycles.append({
                    'start_idx': group.index[0],
                    'end_idx': group.index[-1],
                    'type': 'stop'
                })

        return cycles

    def classify_cycle(self, start_idx, end_idx):
        """
        Bir döngüyü SORT tipine göre sınıflandırır

        Args:
            start_idx: Başlangıç indeksi
            end_idx: Bitiş indeksi

        Returns:
            str: SORT döngü tipi (SORT1, SORT2, SORT3 veya Unknown)
        """
        segment = self.df.iloc[start_idx:end_idx + 1]

        if len(segment) == 0:
            return 'Unknown'

        # Segmentin özelliklerini hesapla
        max_speed = segment['speed'].max()
        avg_speed = segment['speed'].mean()
        duration = segment['time'].iloc[-1] - segment['time'].iloc[0]

        if 'cumulative_distance_km' in segment.columns:
            distance = (segment['cumulative_distance_km'].iloc[-1] -
                       segment['cumulative_distance_km'].iloc[0])
        else:
            distance = 0

        # SORT döngü tipini belirle
        best_match = 'Unknown'
        min_error = float('inf')

        for cycle_name, cycle_data in SORT_CYCLES.items():
            # Parametreleri karşılaştır
            speed_error = abs(max_speed - cycle_data['max_speed']) / cycle_data['max_speed']
            avg_speed_error = abs(avg_speed - cycle_data['avg_speed']) / cycle_data['avg_speed']
            duration_error = abs(duration - cycle_data['duration']) / cycle_data['duration']

            # Toplam hata
            total_error = speed_error + avg_speed_error + duration_error

            if total_error < min_error:
                min_error = total_error
                best_match = cycle_name

        # Hata çok yüksekse Unknown döndür
        if min_error > 0.5:  # %50'den fazla sapma
            return 'Unknown'

        return best_match

    def analyze_cycle(self, cycle_type='auto'):
        """
        SORT döngüsüne göre analiz yapar

        Args:
            cycle_type (str): 'SORT1', 'SORT2', 'SORT3' veya 'auto'

        Returns:
            dict: Analiz sonuçları
        """
        if cycle_type == 'auto':
            # Otomatik tespit
            detected = self.detect_cycles()

            if not detected:
                # Döngü bulunamadı, tüm veriyi kullan
                cycle_type = self.classify_cycle(0, len(self.df) - 1)
            else:
                # İlk döngüyü kullan
                first_cycle = detected[0]
                cycle_type = self.classify_cycle(
                    first_cycle['start_idx'],
                    first_cycle['end_idx']
                )

        # Döngü bilgilerini al
        if cycle_type not in SORT_CYCLES:
            cycle_type = 'SORT2'  # Varsayılan

        cycle_info = SORT_CYCLES[cycle_type]

        # Temel metrikler
        total_time = self.df['time'].iloc[-1] - self.df['time'].iloc[0]
        total_distance = self.df['cumulative_distance_km'].iloc[-1]
        total_energy = self.df['cumulative_energy_kwh'].iloc[-1]

        # Hız istatistikleri
        max_speed = self.df['speed'].max()
        avg_speed = self.df['speed'].mean()
        min_speed = self.df['speed'].min()

        # Güç istatistikleri
        if 'power_kw' in self.df.columns:
            max_power = self.df['power_kw'].max()
            avg_power = self.df['power_kw'].mean()
            min_power = self.df['power_kw'].min()
        else:
            max_power = avg_power = min_power = 0

        # Sürüş fazları analizi
        if 'accelerating' in self.df.columns:
            accel_time = self.df['accelerating'].sum() * self.df['dt'].mean()
            decel_time = self.df['decelerating'].sum() * self.df['dt'].mean()
            cruise_time = self.df['cruising'].sum() * self.df['dt'].mean()
            stop_time = self.df['stopped'].sum() * self.df['dt'].mean()
        else:
            accel_time = decel_time = cruise_time = stop_time = 0

        # Regeneratif frenleme
        if 'regen_power' in self.df.columns:
            total_regen_energy = (self.df['regen_power'] * self.df['dt'] / 3600000).sum()
            regen_power_avg = self.df.loc[self.df['regenerating'], 'regen_power'].mean() if self.df['regenerating'].any() else 0
        else:
            total_regen_energy = 0
            regen_power_avg = 0

        # İvme istatistikleri
        if 'acceleration' in self.df.columns:
            max_accel = self.df['acceleration'].max()
            max_decel = self.df['acceleration'].min()
            avg_accel = self.df.loc[self.df['accelerating'], 'acceleration'].mean() if self.df['accelerating'].any() else 0
            avg_decel = self.df.loc[self.df['decelerating'], 'acceleration'].mean() if self.df['decelerating'].any() else 0
        else:
            max_accel = max_decel = avg_accel = avg_decel = 0

        # Enerji tüketimi (kWh/100km)
        energy_per_100km = (total_energy / total_distance * 100) if total_distance > 0 else 0

        # Döngü sayısı (teorik)
        cycle_count = total_distance / cycle_info['distance'] if cycle_info['distance'] > 0 else 1

        # SORT standartlarıyla karşılaştırma
        speed_compliance = (max_speed / cycle_info['max_speed'] * 100) if cycle_info['max_speed'] > 0 else 0
        distance_compliance = (total_distance / cycle_info['distance'] * 100) if cycle_info['distance'] > 0 else 0
        duration_compliance = (total_time / cycle_info['duration'] * 100) if cycle_info['duration'] > 0 else 0

        # Sonuçları kaydet
        self.results = {
            'cycle_type': cycle_type,
            'cycle_name': cycle_info['name'],
            'cycle_description': cycle_info['description'],

            # Temel metrikler
            'total_time': total_time,
            'total_distance': total_distance,
            'total_energy': total_energy,
            'energy_per_100km': energy_per_100km,

            # Hız
            'max_speed': max_speed,
            'avg_speed': avg_speed,
            'min_speed': min_speed,

            # Güç
            'max_power': max_power,
            'avg_power': avg_power,
            'min_power': min_power,

            # Sürüş fazları
            'acceleration_time': accel_time,
            'deceleration_time': decel_time,
            'cruise_time': cruise_time,
            'stop_time': stop_time,

            # İvme
            'max_acceleration': max_accel,
            'max_deceleration': max_decel,
            'avg_acceleration': avg_accel,
            'avg_deceleration': avg_decel,

            # Regeneratif frenleme
            'total_regen_energy': total_regen_energy,
            'avg_regen_power': regen_power_avg,
            'regen_efficiency': (total_regen_energy / total_energy * 100) if total_energy > 0 else 0,

            # SORT uyumluluk
            'cycle_count': cycle_count,
            'speed_compliance': speed_compliance,
            'distance_compliance': distance_compliance,
            'duration_compliance': duration_compliance,

            # SORT standartları
            'sort_max_speed': cycle_info['max_speed'],
            'sort_avg_speed': cycle_info['avg_speed'],
            'sort_distance': cycle_info['distance'],
            'sort_duration': cycle_info['duration']
        }

        return self.results

    def get_summary_report(self):
        """
        Özet rapor döndürür

        Returns:
            str: Formatlanmış rapor metni
        """
        if not self.results:
            return "Henüz analiz yapılmadı. Lütfen önce analyze_cycle() metodunu çağırın."

        r = self.results

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           UITP SORT TEST DÖNGÜSÜ ANALİZ RAPORU              ║
╚══════════════════════════════════════════════════════════════╝

DÖNGÜ BİLGİLERİ:
  Döngü Tipi          : {r['cycle_name']}
  Açıklama            : {r['cycle_description']}
  Döngü Sayısı        : {r['cycle_count']:.1f}

TEMEL METRİKLER:
  Toplam Süre         : {r['total_time']:.1f} saniye ({r['total_time']/60:.1f} dakika)
  Toplam Mesafe       : {r['total_distance']:.2f} km
  Toplam Enerji       : {r['total_energy']:.3f} kWh
  Enerji Tüketimi     : {r['energy_per_100km']:.2f} kWh/100km

HIZ İSTATİSTİKLERİ:
  Maksimum Hız        : {r['max_speed']:.1f} km/h
  Ortalama Hız        : {r['avg_speed']:.1f} km/h
  Minimum Hız         : {r['min_speed']:.1f} km/h

GÜÇ İSTATİSTİKLERİ:
  Maksimum Güç        : {r['max_power']:.1f} kW
  Ortalama Güç        : {r['avg_power']:.1f} kW
  Minimum Güç         : {r['min_power']:.1f} kW

SÜRÜŞ FAZLARI:
  Hızlanma            : {r['acceleration_time']:.1f} s ({r['acceleration_time']/r['total_time']*100:.1f}%)
  Yavaşlama           : {r['deceleration_time']:.1f} s ({r['deceleration_time']/r['total_time']*100:.1f}%)
  Sabit Hız           : {r['cruise_time']:.1f} s ({r['cruise_time']/r['total_time']*100:.1f}%)
  Durma               : {r['stop_time']:.1f} s ({r['stop_time']/r['total_time']*100:.1f}%)

İVME İSTATİSTİKLERİ:
  Maks. Hızlanma      : {r['max_acceleration']:.2f} m/s²
  Maks. Yavaşlama     : {r['max_deceleration']:.2f} m/s²
  Ort. Hızlanma       : {r['avg_acceleration']:.2f} m/s²
  Ort. Yavaşlama      : {r['avg_deceleration']:.2f} m/s²

REGENERATİF FRENLEME:
  Toplam Regen Enerji : {r['total_regen_energy']:.3f} kWh
  Ortalama Regen Güç  : {r['avg_regen_power']:.1f} W
  Regen Verimliliği   : {r['regen_efficiency']:.1f}%

SORT STANDARTLARIYLA KARŞILAŞTIRMA:
  Standart Maks. Hız  : {r['sort_max_speed']:.1f} km/h
  Gerçek Maks. Hız    : {r['max_speed']:.1f} km/h
  Uyumluluk           : {r['speed_compliance']:.1f}%

  Standart Mesafe     : {r['sort_distance']:.2f} km
  Gerçek Mesafe       : {r['total_distance']:.2f} km
  Uyumluluk           : {r['distance_compliance']:.1f}%

  Standart Süre       : {r['sort_duration']:.0f} s
  Gerçek Süre         : {r['total_time']:.0f} s
  Uyumluluk           : {r['duration_compliance']:.1f}%

╚══════════════════════════════════════════════════════════════╝
"""
        return report


def analyze_sort_cycle(dataframe, cycle_type='auto'):
    """
    SORT döngüsü analizi yapar (kolaylık fonksiyonu)

    Args:
        dataframe: Test verileri
        cycle_type: SORT döngü tipi

    Returns:
        dict: Analiz sonuçları
    """
    calculator = SORTCalculator(dataframe)
    results = calculator.analyze_cycle(cycle_type)
    return results, calculator


if __name__ == "__main__":
    print("SORT Calculator Modülü Test")
    print("=" * 60)

    # Test için örnek veri
    print("\nÖrnek SORT döngü bilgileri:")
    for cycle_name, cycle_data in SORT_CYCLES.items():
        print(f"\n{cycle_data['name']}:")
        print(f"  Maksimum Hız     : {cycle_data['max_speed']} km/h")
        print(f"  Ortalama Hız     : {cycle_data['avg_speed']} km/h")
        print(f"  Mesafe           : {cycle_data['distance']} km")
        print(f"  Süre             : {cycle_data['duration']} s")
        print(f"  Açıklama         : {cycle_data['description']}")
