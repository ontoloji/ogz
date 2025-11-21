"""
Enerji Analiz Modülü
kWh/100km hesaplaması, menzil tahmini, regeneratif frenleme ve sıcaklık etkisi analizi
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import BATTERY_CAPACITIES, TEMPERATURE_RANGES, DEFAULTS

class EnergyAnalyzer:
    """Enerji tüketimi ve verimlilik analizi"""

    def __init__(self, dataframe):
        """
        Args:
            dataframe (pd.DataFrame): Test verileri
        """
        self.df = dataframe
        self.results = {}

    def calculate_consumption(self):
        """
        Enerji tüketimini hesaplar (kWh/100km)

        Returns:
            dict: Tüketim metrikleri
        """
        total_energy = self.df['cumulative_energy_kwh'].iloc[-1]
        total_distance = self.df['cumulative_distance_km'].iloc[-1]

        if total_distance == 0:
            return {
                'total_energy': 0,
                'total_distance': 0,
                'consumption_per_100km': 0,
                'consumption_per_km': 0
            }

        consumption_per_100km = (total_energy / total_distance) * 100
        consumption_per_km = total_energy / total_distance

        # Faz bazında tüketim
        if 'accelerating' in self.df.columns:
            accel_energy = self.df.loc[self.df['accelerating'], 'energy_kwh'].sum()
            cruise_energy = self.df.loc[self.df['cruising'], 'energy_kwh'].sum()
            decel_energy = self.df.loc[self.df['decelerating'], 'energy_kwh'].sum()
            stop_energy = self.df.loc[self.df['stopped'], 'energy_kwh'].sum()

            phases = {
                'acceleration': accel_energy,
                'cruise': cruise_energy,
                'deceleration': decel_energy,
                'stop': stop_energy
            }
        else:
            phases = {}

        return {
            'total_energy': total_energy,
            'total_distance': total_distance,
            'consumption_per_100km': consumption_per_100km,
            'consumption_per_km': consumption_per_km,
            'phase_consumption': phases
        }

    def calculate_range(self, battery_capacities=None):
        """
        Farklı batarya kapasiteleri için menzil tahmini

        Args:
            battery_capacities (list): Batarya kapasiteleri (kWh)

        Returns:
            dict: Menzil tahminleri
        """
        if battery_capacities is None:
            battery_capacities = BATTERY_CAPACITIES

        consumption = self.calculate_consumption()
        consumption_per_km = consumption['consumption_per_km']

        if consumption_per_km == 0:
            return {}

        ranges = {}

        for capacity in battery_capacities:
            # Kullanılabilir kapasite (%80 SOC kullanımı)
            usable_capacity = capacity * 0.8

            # Teorik menzil
            theoretical_range = usable_capacity / consumption_per_km

            # Gerçekçi menzil (%90 verimlilik)
            realistic_range = theoretical_range * 0.9

            # Minimum menzil (zorlu koşullarda %75 verimlilik)
            minimum_range = theoretical_range * 0.75

            ranges[capacity] = {
                'theoretical': theoretical_range,
                'realistic': realistic_range,
                'minimum': minimum_range,
                'usable_capacity': usable_capacity
            }

        return ranges

    def analyze_regenerative_braking(self):
        """
        Regeneratif frenleme verimliliği analizi

        Returns:
            dict: Regeneratif frenleme metrikleri
        """
        if 'regen_power' not in self.df.columns:
            return {
                'available': False,
                'message': 'Regeneratif frenleme verisi bulunamadı'
            }

        # Toplam motor gücü (pozitif = tüketim)
        total_motor_energy = (self.df['motor_power'] * self.df['dt'] / 3600000).sum()

        # Toplam regen gücü (negatif = geri kazanım)
        total_regen_energy = (self.df['regen_power'] * self.df['dt'] / 3600000).sum()

        # Yavaşlama fazlarındaki enerji
        decel_motor_energy = (self.df.loc[self.df['decelerating'], 'motor_power'] *
                             self.df.loc[self.df['decelerating'], 'dt'] / 3600000).sum()

        decel_regen_energy = (self.df.loc[self.df['decelerating'], 'regen_power'] *
                             self.df.loc[self.df['decelerating'], 'dt'] / 3600000).sum()

        # Verimlilik hesapları
        regen_efficiency = (total_regen_energy / total_motor_energy * 100) if total_motor_energy > 0 else 0

        # Potansiyel kazanım (kinetik enerji)
        if 'speed_ms' in self.df.columns and 'acceleration' in self.df.columns:
            # Varsayılan araç kütlesi (kg)
            vehicle_mass = 15000  # 15 ton otobüs

            # Kinetik enerji değişimi
            kinetic_energy = 0.5 * vehicle_mass * (self.df['speed_ms'] ** 2)
            kinetic_loss = -kinetic_energy.diff()  # Negatif = enerji kaybı

            # Yavaşlama fazlarındaki kinetik enerji kaybı
            decel_kinetic_loss = kinetic_loss.loc[self.df['decelerating']].sum() / 3600000  # kWh

            # Teorik geri kazanım potansiyeli
            theoretical_regen_potential = decel_kinetic_loss
        else:
            theoretical_regen_potential = 0

        # Regen performansı
        regen_performance = (total_regen_energy / theoretical_regen_potential * 100) if theoretical_regen_potential > 0 else 0

        # Ortalama regen güçleri
        avg_regen_power = self.df.loc[self.df['regenerating'], 'regen_power'].mean() if self.df['regenerating'].any() else 0
        max_regen_power = self.df['regen_power'].max()

        # Regen olayları
        regen_events = (self.df['regenerating'] != self.df['regenerating'].shift()).sum() // 2

        return {
            'available': True,
            'total_motor_energy': total_motor_energy,
            'total_regen_energy': total_regen_energy,
            'regen_efficiency': regen_efficiency,
            'decel_motor_energy': decel_motor_energy,
            'decel_regen_energy': decel_regen_energy,
            'theoretical_regen_potential': theoretical_regen_potential,
            'regen_performance': regen_performance,
            'avg_regen_power': avg_regen_power,
            'max_regen_power': max_regen_power,
            'regen_events': regen_events,
            'energy_saved': total_regen_energy,
            'cost_saved_percent': regen_efficiency
        }

    def analyze_temperature_effect(self):
        """
        Sıcaklık etkisi analizi

        Returns:
            dict: Sıcaklık analiz sonuçları
        """
        if 'temperature' not in self.df.columns:
            return {
                'available': False,
                'message': 'Sıcaklık verisi bulunamadı'
            }

        # Ortalama sıcaklık
        avg_temp = self.df['temperature'].mean()
        min_temp = self.df['temperature'].min()
        max_temp = self.df['temperature'].max()
        temp_std = self.df['temperature'].std()

        # Sıcaklık aralığını belirle
        temp_range = None
        for range_name, (low, high) in TEMPERATURE_RANGES.items():
            if low <= avg_temp < high:
                temp_range = range_name
                break

        if temp_range is None:
            temp_range = 'Bilinmeyen'

        # Sıcaklık etkisi faktörü (25°C referans)
        reference_temp = 25
        temp_effect_factor = 1.0

        if avg_temp < reference_temp:
            # Soğuk hava: Her 10°C için %5 artış
            temp_diff = reference_temp - avg_temp
            temp_effect_factor = 1.0 + (temp_diff / 10 * 0.05)
        elif avg_temp > reference_temp:
            # Sıcak hava: Her 10°C için %3 artış
            temp_diff = avg_temp - reference_temp
            temp_effect_factor = 1.0 + (temp_diff / 10 * 0.03)

        # Normalize edilmiş enerji tüketimi
        consumption = self.calculate_consumption()
        normalized_consumption = consumption['consumption_per_100km'] / temp_effect_factor

        # Sıcaklık değişimi analizi
        temp_changes = self.df['temperature'].diff().abs()
        temp_stability = 100 - (temp_changes.mean() / avg_temp * 100) if avg_temp > 0 else 0

        return {
            'available': True,
            'avg_temperature': avg_temp,
            'min_temperature': min_temp,
            'max_temperature': max_temp,
            'temperature_std': temp_std,
            'temperature_range': temp_range,
            'temp_effect_factor': temp_effect_factor,
            'actual_consumption': consumption['consumption_per_100km'],
            'normalized_consumption': normalized_consumption,
            'consumption_increase': (temp_effect_factor - 1) * 100,
            'temperature_stability': temp_stability
        }

    def calculate_efficiency(self):
        """
        Genel verimlilik metrikleri

        Returns:
            dict: Verimlilik metrikleri
        """
        # Teorik vs gerçek enerji
        if 'power_kw' in self.df.columns:
            avg_power = self.df['power_kw'].mean()
            peak_power = self.df['power_kw'].max()

            # Yük faktörü
            load_factor = (avg_power / peak_power * 100) if peak_power > 0 else 0
        else:
            avg_power = 0
            peak_power = 0
            load_factor = 0

        # Enerji dağılımı
        consumption = self.calculate_consumption()
        phase_consumption = consumption.get('phase_consumption', {})

        total_phase_energy = sum(phase_consumption.values())

        if total_phase_energy > 0:
            phase_distribution = {
                phase: (energy / total_phase_energy * 100)
                for phase, energy in phase_consumption.items()
            }
        else:
            phase_distribution = {}

        # Regen analizi
        regen_analysis = self.analyze_regenerative_braking()

        # Genel verimlilik skoru (0-100)
        efficiency_score = 0

        # Regen verimliliği (30 puan)
        if regen_analysis.get('available'):
            regen_eff = min(regen_analysis.get('regen_efficiency', 0), 30)
            efficiency_score += regen_eff

        # Yük faktörü (30 puan)
        efficiency_score += min(load_factor * 0.3, 30)

        # Tüketim verimliliği (40 puan - düşük tüketim = yüksek puan)
        # Referans: 100 kWh/100km = 0 puan, 50 kWh/100km = 40 puan
        consumption_score = max(0, 40 - (consumption['consumption_per_100km'] - 50) * 0.4)
        efficiency_score += consumption_score

        return {
            'avg_power': avg_power,
            'peak_power': peak_power,
            'load_factor': load_factor,
            'phase_distribution': phase_distribution,
            'efficiency_score': min(efficiency_score, 100),
            'consumption_per_100km': consumption['consumption_per_100km'],
            'regen_efficiency': regen_analysis.get('regen_efficiency', 0)
        }

    def full_analysis(self):
        """
        Kapsamlı enerji analizi yapar

        Returns:
            dict: Tüm analiz sonuçları
        """
        self.results = {
            'consumption': self.calculate_consumption(),
            'range': self.calculate_range(),
            'regenerative_braking': self.analyze_regenerative_braking(),
            'temperature': self.analyze_temperature_effect(),
            'efficiency': self.calculate_efficiency()
        }

        return self.results

    def get_summary_report(self):
        """
        Özet rapor oluşturur

        Returns:
            str: Formatlanmış rapor
        """
        if not self.results:
            self.full_analysis()

        r = self.results

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              ENERJİ ANALİZİ ÖZET RAPORU                      ║
╚══════════════════════════════════════════════════════════════╝

ENERJİ TÜKETİMİ:
  Toplam Enerji         : {r['consumption']['total_energy']:.3f} kWh
  Toplam Mesafe         : {r['consumption']['total_distance']:.2f} km
  Tüketim (100km)       : {r['consumption']['consumption_per_100km']:.2f} kWh/100km
  Tüketim (km)          : {r['consumption']['consumption_per_km']:.4f} kWh/km

MENZİL TAHMİNLERİ (Örnek Batarya Kapasiteleri):
"""

        # Örnek menzil tahminleri
        sample_capacities = [100, 150, 200, 300]
        for capacity in sample_capacities:
            if capacity in r['range']:
                range_data = r['range'][capacity]
                report += f"""  {capacity} kWh Batarya:
    Teorik Menzil       : {range_data['theoretical']:.1f} km
    Gerçekçi Menzil     : {range_data['realistic']:.1f} km
    Minimum Menzil      : {range_data['minimum']:.1f} km
"""

        # Regeneratif frenleme
        if r['regenerative_braking'].get('available'):
            rb = r['regenerative_braking']
            report += f"""
REGENERATİF FRENLEME:
  Toplam Motor Enerjisi : {rb['total_motor_energy']:.3f} kWh
  Geri Kazanılan Enerji : {rb['total_regen_energy']:.3f} kWh
  Regen Verimliliği     : {rb['regen_efficiency']:.1f}%
  Ort. Regen Gücü       : {rb['avg_regen_power']:.1f} W
  Maks. Regen Gücü      : {rb['max_regen_power']:.1f} W
  Regen Olayları        : {rb['regen_events']:.0f}
  Maliyet Tasarrufu     : %{rb['cost_saved_percent']:.1f}
"""

        # Sıcaklık etkisi
        if r['temperature'].get('available'):
            t = r['temperature']
            report += f"""
SICAKLIK ETKİSİ:
  Ortalama Sıcaklık     : {t['avg_temperature']:.1f}°C
  Sıcaklık Aralığı      : {t['temperature_range']}
  Sıcaklık Etkisi       : x{t['temp_effect_factor']:.2f}
  Normalize Tüketim     : {t['normalized_consumption']:.2f} kWh/100km
  Tüketim Artışı        : +%{t['consumption_increase']:.1f}
"""

        # Verimlilik
        e = r['efficiency']
        report += f"""
VERİMLİLİK:
  Verimlilik Skoru      : {e['efficiency_score']:.1f}/100
  Ortalama Güç          : {e['avg_power']:.1f} kW
  Tepe Güç              : {e['peak_power']:.1f} kW
  Yük Faktörü           : {e['load_factor']:.1f}%
  Regen Verimliliği     : {e['regen_efficiency']:.1f}%
"""

        if e['phase_distribution']:
            report += "\nFAZ DAĞILIMI:\n"
            for phase, percent in e['phase_distribution'].items():
                report += f"  {phase.capitalize():20s}: %{percent:.1f}\n"

        report += "\n╚══════════════════════════════════════════════════════════════╝\n"

        return report


if __name__ == "__main__":
    print("Energy Analyzer Modülü Test")
    print("=" * 60)
    print("\nBatarya kapasiteleri:", BATTERY_CAPACITIES)
    print("\nSıcaklık aralıkları:")
    for name, (low, high) in TEMPERATURE_RANGES.items():
        print(f"  {name}: {low}°C - {high}°C")
