"""
Grafik Oluşturma Modülü
matplotlib kullanarak hız profili, enerji tüketimi ve SOC değişimi grafiklerini oluşturur
"""
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışma
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import CHART_COLORS, get_output_path

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    """Grafik oluşturma sınıfı"""

    def __init__(self, dataframe, title_prefix=""):
        """
        Args:
            dataframe (pd.DataFrame): Test verileri
            title_prefix (str): Grafik başlığı öneki
        """
        self.df = dataframe
        self.title_prefix = title_prefix
        self.colors = CHART_COLORS

    def plot_speed_profile(self, output_path=None, figsize=(12, 6)):
        """
        Hız profili grafiği oluşturur

        Args:
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Zaman ekseni
        time = self.df['time'] / 60  # dakikaya çevir

        # Hız grafiği
        ax.plot(time, self.df['speed'], color=self.colors['primary'],
                linewidth=2, label='Hız')

        # Fazları renklendir
        if 'accelerating' in self.df.columns:
            # Hızlanma fazları
            accel_mask = self.df['accelerating']
            if accel_mask.any():
                ax.fill_between(time, 0, self.df['speed'].max() * 1.1,
                               where=accel_mask, alpha=0.2,
                               color=self.colors['success'], label='Hızlanma')

            # Yavaşlama fazları
            decel_mask = self.df['decelerating']
            if decel_mask.any():
                ax.fill_between(time, 0, self.df['speed'].max() * 1.1,
                               where=decel_mask, alpha=0.2,
                               color=self.colors['warning'], label='Yavaşlama')

        # Eksen ayarları
        ax.set_xlabel('Zaman (dakika)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hız (km/h)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.title_prefix}Hız Profili', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(loc='best')

        # Y ekseni limitleri
        ax.set_ylim(0, self.df['speed'].max() * 1.1)

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('speed_profile.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_power_profile(self, output_path=None, figsize=(12, 6)):
        """
        Güç profili grafiği oluşturur

        Args:
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Zaman ekseni
        time = self.df['time'] / 60

        # Güç grafiği
        if 'power_kw' in self.df.columns:
            power = self.df['power_kw']

            # Pozitif (motor) ve negatif (regen) güçleri ayır
            positive_power = power.clip(lower=0)
            negative_power = power.clip(upper=0)

            # Motor gücü
            ax.fill_between(time, 0, positive_power, color=self.colors['danger'],
                           alpha=0.6, label='Motor Gücü')

            # Regen gücü
            ax.fill_between(time, 0, negative_power, color=self.colors['success'],
                           alpha=0.6, label='Regen Gücü')

            # Sıfır çizgisi
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        # Eksen ayarları
        ax.set_xlabel('Zaman (dakika)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Güç (kW)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.title_prefix}Güç Profili', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(loc='best')

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('power_profile.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_energy_consumption(self, output_path=None, figsize=(12, 6)):
        """
        Enerji tüketimi grafiği oluşturur

        Args:
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Zaman ekseni
        time = self.df['time'] / 60

        # Kümülatif enerji
        if 'cumulative_energy_kwh' in self.df.columns:
            ax.plot(time, self.df['cumulative_energy_kwh'],
                   color=self.colors['primary'], linewidth=2.5,
                   label='Toplam Enerji Tüketimi')

        # Eksen ayarları
        ax.set_xlabel('Zaman (dakika)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Kümülatif Enerji (kWh)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.title_prefix}Enerji Tüketimi', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(loc='best')

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('energy_consumption.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_soc_profile(self, initial_soc=100, battery_capacity=100,
                        output_path=None, figsize=(12, 6)):
        """
        SOC (State of Charge) değişimi grafiği oluşturur

        Args:
            initial_soc (float): Başlangıç SOC (%)
            battery_capacity (float): Batarya kapasitesi (kWh)
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Zaman ekseni
        time = self.df['time'] / 60

        # SOC hesapla
        if 'cumulative_energy_kwh' in self.df.columns:
            energy_consumed = self.df['cumulative_energy_kwh']
            soc = initial_soc - (energy_consumed / battery_capacity * 100)

            # SOC grafiği
            ax.plot(time, soc, color=self.colors['primary'],
                   linewidth=2.5, label='SOC')

            # Kritik seviyeler
            ax.axhline(y=80, color=self.colors['success'], linestyle='--',
                      linewidth=1, alpha=0.5, label='İdeal Maks (80%)')
            ax.axhline(y=20, color=self.colors['danger'], linestyle='--',
                      linewidth=1, alpha=0.5, label='Minimum (20%)')

            # Renkli bölgeler
            ax.fill_between(time, 80, 100, alpha=0.1, color=self.colors['warning'],
                           label='Yüksek SOC')
            ax.fill_between(time, 0, 20, alpha=0.1, color=self.colors['danger'],
                           label='Düşük SOC')

        # Eksen ayarları
        ax.set_xlabel('Zaman (dakika)', fontsize=12, fontweight='bold')
        ax.set_ylabel('SOC (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.title_prefix}Batarya Şarj Durumu (SOC) - {battery_capacity} kWh',
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(loc='best')

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path(f'soc_profile_{battery_capacity}kwh.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_temperature_effect(self, output_path=None, figsize=(12, 6)):
        """
        Sıcaklık ve enerji tüketimi ilişkisi grafiği

        Args:
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu veya None
        """
        if 'temperature' not in self.df.columns:
            return None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # Zaman ekseni
        time = self.df['time'] / 60

        # Sıcaklık grafiği
        ax1.plot(time, self.df['temperature'], color=self.colors['warning'],
                linewidth=2, label='Sıcaklık')
        ax1.set_ylabel('Sıcaklık (°C)', fontsize=12, fontweight='bold')
        ax1.set_title(f'{self.title_prefix}Sıcaklık ve Enerji Tüketimi',
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, color=self.colors['grid'])
        ax1.legend(loc='best')

        # Enerji tüketimi grafiği
        if 'power_kw' in self.df.columns:
            ax2.plot(time, self.df['power_kw'], color=self.colors['primary'],
                    linewidth=2, label='Güç')
            ax2.set_ylabel('Güç (kW)', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Zaman (dakika)', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3, color=self.colors['grid'])
            ax2.legend(loc='best')

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('temperature_effect.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_phase_distribution(self, phase_data, output_path=None, figsize=(10, 6)):
        """
        Sürüş fazları dağılımı pasta grafiği

        Args:
            phase_data (dict): Faz verileri
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Veri hazırlama
        labels = []
        sizes = []
        colors_list = []

        phase_colors = {
            'acceleration': self.colors['success'],
            'cruise': self.colors['info'],
            'deceleration': self.colors['warning'],
            'stop': self.colors['danger']
        }

        phase_labels = {
            'acceleration': 'Hızlanma',
            'cruise': 'Sabit Hız',
            'deceleration': 'Yavaşlama',
            'stop': 'Durma'
        }

        for phase, value in phase_data.items():
            if value > 0:
                labels.append(phase_labels.get(phase, phase))
                sizes.append(value)
                colors_list.append(phase_colors.get(phase, self.colors['primary']))

        # Pasta grafiği
        if sizes:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_list,
                                               autopct='%1.1f%%', startangle=90,
                                               textprops={'fontsize': 11, 'fontweight': 'bold'})

            # Yüzde yazıları beyaz
            for autotext in autotexts:
                autotext.set_color('white')

        ax.set_title(f'{self.title_prefix}Sürüş Fazları Dağılımı',
                    fontsize=14, fontweight='bold')

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('phase_distribution.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_range_comparison(self, range_data, output_path=None, figsize=(12, 6)):
        """
        Farklı batarya kapasiteleri için menzil karşılaştırması

        Args:
            range_data (dict): Menzil verileri
            output_path (str): Çıktı dosyası yolu
            figsize (tuple): Grafik boyutu

        Returns:
            str: Kaydedilen dosya yolu
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Veri hazırlama
        capacities = []
        theoretical = []
        realistic = []
        minimum = []

        for capacity, data in sorted(range_data.items()):
            capacities.append(capacity)
            theoretical.append(data['theoretical'])
            realistic.append(data['realistic'])
            minimum.append(data['minimum'])

        # Bar genişliği
        x = np.arange(len(capacities))
        width = 0.25

        # Çubuk grafikleri
        ax.bar(x - width, theoretical, width, label='Teorik',
              color=self.colors['info'], alpha=0.8)
        ax.bar(x, realistic, width, label='Gerçekçi',
              color=self.colors['success'], alpha=0.8)
        ax.bar(x + width, minimum, width, label='Minimum',
              color=self.colors['warning'], alpha=0.8)

        # Eksen ayarları
        ax.set_xlabel('Batarya Kapasitesi (kWh)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Menzil (km)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.title_prefix}Batarya Kapasitesine Göre Menzil Tahmini',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(capacities)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3, axis='y', color=self.colors['grid'])

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('range_comparison.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def create_all_charts(self, energy_results=None, battery_capacity=100, initial_soc=100):
        """
        Tüm grafikleri oluşturur

        Args:
            energy_results (dict): Enerji analiz sonuçları
            battery_capacity (float): Batarya kapasitesi
            initial_soc (float): Başlangıç SOC

        Returns:
            dict: Oluşturulan grafik dosyalarının yolları
        """
        charts = {}

        # Temel grafikler
        charts['speed'] = self.plot_speed_profile()
        charts['power'] = self.plot_power_profile()
        charts['energy'] = self.plot_energy_consumption()
        charts['soc'] = self.plot_soc_profile(initial_soc, battery_capacity)

        # Sıcaklık grafiği (varsa)
        temp_chart = self.plot_temperature_effect()
        if temp_chart:
            charts['temperature'] = temp_chart

        # Enerji analiz sonuçlarına dayalı grafikler
        if energy_results:
            # Faz dağılımı
            if 'efficiency' in energy_results and 'phase_distribution' in energy_results['efficiency']:
                phase_dist = energy_results['efficiency']['phase_distribution']
                if phase_dist:
                    charts['phase'] = self.plot_phase_distribution(phase_dist)

            # Menzil karşılaştırması
            if 'range' in energy_results:
                charts['range'] = self.plot_range_comparison(energy_results['range'])

        return charts


if __name__ == "__main__":
    print("Chart Generator Modülü Test")
    print("=" * 60)
    print("\nGrafik renkleri:")
    for key, value in CHART_COLORS.items():
        print(f"  {key}: {value}")
