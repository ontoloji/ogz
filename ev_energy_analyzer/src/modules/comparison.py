"""
Karşılaştırma Modülü
Farklı test tarihlerini ve sonuçlarını karşılaştırır
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import CHART_COLORS, get_output_path, format_turkish_number

class TestComparison:
    """Test karşılaştırma sınıfı"""

    def __init__(self):
        """Test karşılaştırma başlatıcı"""
        self.tests = []
        self.colors = CHART_COLORS

    def add_test(self, name, dataframe, sort_results, energy_results):
        """
        Karşılaştırma için test ekler

        Args:
            name (str): Test adı
            dataframe (pd.DataFrame): Test verileri
            sort_results (dict): SORT sonuçları
            energy_results (dict): Enerji sonuçları
        """
        self.tests.append({
            'name': name,
            'dataframe': dataframe,
            'sort_results': sort_results,
            'energy_results': energy_results
        })

    def compare_consumption(self):
        """
        Enerji tüketimini karşılaştırır

        Returns:
            dict: Karşılaştırma sonuçları
        """
        if len(self.tests) < 2:
            return {'error': 'En az 2 test gerekli'}

        comparison = {
            'tests': [],
            'consumption_per_100km': [],
            'total_energy': [],
            'total_distance': [],
            'avg_speed': [],
            'regen_efficiency': []
        }

        for test in self.tests:
            comparison['tests'].append(test['name'])

            # Enerji tüketimi
            cons = test['energy_results']['consumption']
            comparison['consumption_per_100km'].append(cons['consumption_per_100km'])
            comparison['total_energy'].append(cons['total_energy'])
            comparison['total_distance'].append(cons['total_distance'])

            # Hız
            comparison['avg_speed'].append(test['sort_results']['avg_speed'])

            # Regen
            regen = test['energy_results']['regenerative_braking']
            if regen.get('available'):
                comparison['regen_efficiency'].append(regen['regen_efficiency'])
            else:
                comparison['regen_efficiency'].append(0)

        return comparison

    def compare_performance(self):
        """
        Performans metriklerini karşılaştırır

        Returns:
            dict: Performans karşılaştırması
        """
        if len(self.tests) < 2:
            return {'error': 'En az 2 test gerekli'}

        comparison = {
            'tests': [],
            'max_speed': [],
            'max_power': [],
            'avg_power': [],
            'max_acceleration': [],
            'efficiency_score': []
        }

        for test in self.tests:
            comparison['tests'].append(test['name'])

            # SORT sonuçları
            sort_res = test['sort_results']
            comparison['max_speed'].append(sort_res['max_speed'])
            comparison['max_power'].append(sort_res['max_power'])
            comparison['avg_power'].append(sort_res['avg_power'])
            comparison['max_acceleration'].append(sort_res['max_acceleration'])

            # Verimlilik skoru
            eff = test['energy_results']['efficiency']
            comparison['efficiency_score'].append(eff['efficiency_score'])

        return comparison

    def plot_consumption_comparison(self, output_path=None, figsize=(12, 6)):
        """
        Tüketim karşılaştırma grafiği

        Args:
            output_path (str): Çıktı dosyası
            figsize (tuple): Grafik boyutu

        Returns:
            str: Dosya yolu
        """
        comparison = self.compare_consumption()

        if 'error' in comparison:
            return None

        fig, ax = plt.subplots(figsize=figsize)

        x = np.arange(len(comparison['tests']))
        width = 0.35

        # Çubuk grafikleri
        bars1 = ax.bar(x - width/2, comparison['consumption_per_100km'],
                      width, label='kWh/100km', color=self.colors['primary'],
                      alpha=0.8)

        # İkinci Y ekseni (Regen verimliliği)
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, comparison['regen_efficiency'],
                       width, label='Regen Verim. (%)', color=self.colors['success'],
                       alpha=0.8)

        # Eksen ayarları
        ax.set_xlabel('Testler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Enerji Tüketimi (kWh/100km)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Regen Verimliliği (%)', fontsize=12, fontweight='bold')
        ax.set_title('Test Karşılaştırması - Enerji Tüketimi ve Regen Verimliliği',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(comparison['tests'], rotation=15, ha='right')

        # Değerleri çubukların üzerine yaz
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9)

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

        # Legendler
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

        ax.grid(True, alpha=0.3, axis='y', color=self.colors['grid'])

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('comparison_consumption.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_performance_comparison(self, output_path=None, figsize=(12, 8)):
        """
        Performans karşılaştırma grafiği

        Args:
            output_path (str): Çıktı dosyası
            figsize (tuple): Grafik boyutu

        Returns:
            str: Dosya yolu
        """
        comparison = self.compare_performance()

        if 'error' in comparison:
            return None

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        x = np.arange(len(comparison['tests']))
        width = 0.6

        # Maksimum hız
        ax1.bar(x, comparison['max_speed'], width, color=self.colors['primary'], alpha=0.8)
        ax1.set_ylabel('Maks. Hız (km/h)', fontweight='bold')
        ax1.set_title('Maksimum Hız', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(comparison['tests'], rotation=15, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')

        # Maksimum güç
        ax2.bar(x, comparison['max_power'], width, color=self.colors['danger'], alpha=0.8)
        ax2.set_ylabel('Maks. Güç (kW)', fontweight='bold')
        ax2.set_title('Maksimum Güç', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(comparison['tests'], rotation=15, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')

        # Ortalama güç
        ax3.bar(x, comparison['avg_power'], width, color=self.colors['info'], alpha=0.8)
        ax3.set_ylabel('Ort. Güç (kW)', fontweight='bold')
        ax3.set_title('Ortalama Güç', fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(comparison['tests'], rotation=15, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')

        # Verimlilik skoru
        ax4.bar(x, comparison['efficiency_score'], width, color=self.colors['success'], alpha=0.8)
        ax4.set_ylabel('Verimlilik Skoru', fontweight='bold')
        ax4.set_title('Genel Verimlilik Skoru (0-100)', fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(comparison['tests'], rotation=15, ha='right')
        ax4.set_ylim(0, 100)
        ax4.grid(True, alpha=0.3, axis='y')

        plt.suptitle('Test Karşılaştırması - Performans Metrikleri',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('comparison_performance.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_speed_profiles_comparison(self, output_path=None, figsize=(12, 6)):
        """
        Hız profilleri karşılaştırması

        Args:
            output_path (str): Çıktı dosyası
            figsize (tuple): Grafik boyutu

        Returns:
            str: Dosya yolu
        """
        if len(self.tests) < 2:
            return None

        fig, ax = plt.subplots(figsize=figsize)

        # Renk paleti
        color_palette = [
            self.colors['primary'],
            self.colors['secondary'],
            self.colors['success'],
            self.colors['warning'],
            self.colors['danger'],
            self.colors['info']
        ]

        for i, test in enumerate(self.tests):
            df = test['dataframe']
            time = df['time'] / 60  # dakika
            color = color_palette[i % len(color_palette)]

            ax.plot(time, df['speed'], label=test['name'],
                   color=color, linewidth=2, alpha=0.7)

        # Eksen ayarları
        ax.set_xlabel('Zaman (dakika)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hız (km/h)', fontsize=12, fontweight='bold')
        ax.set_title('Test Karşılaştırması - Hız Profilleri',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(loc='best')

        plt.tight_layout()

        # Kaydet
        if output_path is None:
            output_path = get_output_path('comparison_speed_profiles.png')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_comparison_report(self):
        """
        Karşılaştırma raporu oluşturur

        Returns:
            str: Formatlanmış rapor
        """
        if len(self.tests) < 2:
            return "En az 2 test karşılaştırma için gerekli."

        cons_comp = self.compare_consumption()
        perf_comp = self.compare_performance()

        report = """
╔══════════════════════════════════════════════════════════════╗
║              TEST KARŞILAŞTIRMA RAPORU                       ║
╚══════════════════════════════════════════════════════════════╝

"""

        # Enerji tüketimi karşılaştırması
        report += "ENERJİ TÜKETİMİ KARŞILAŞTIRMASI:\n"
        report += "-" * 60 + "\n\n"

        for i, test_name in enumerate(cons_comp['tests']):
            report += f"{test_name}:\n"
            report += f"  Tüketim (100km)     : {format_turkish_number(cons_comp['consumption_per_100km'][i], 2)} kWh/100km\n"
            report += f"  Toplam Enerji       : {format_turkish_number(cons_comp['total_energy'][i], 3)} kWh\n"
            report += f"  Toplam Mesafe       : {format_turkish_number(cons_comp['total_distance'][i], 2)} km\n"
            report += f"  Ortalama Hız        : {format_turkish_number(cons_comp['avg_speed'][i], 1)} km/h\n"
            report += f"  Regen Verimliliği   : %{format_turkish_number(cons_comp['regen_efficiency'][i], 1)}\n\n"

        # En iyi ve en kötü performans
        min_consumption_idx = np.argmin(cons_comp['consumption_per_100km'])
        max_consumption_idx = np.argmax(cons_comp['consumption_per_100km'])

        report += "ÖZET:\n"
        report += f"  En Verimli Test     : {cons_comp['tests'][min_consumption_idx]} "
        report += f"({format_turkish_number(cons_comp['consumption_per_100km'][min_consumption_idx], 2)} kWh/100km)\n"
        report += f"  En Az Verimli Test  : {cons_comp['tests'][max_consumption_idx]} "
        report += f"({format_turkish_number(cons_comp['consumption_per_100km'][max_consumption_idx], 2)} kWh/100km)\n\n"

        # Performans karşılaştırması
        report += "\n" + "=" * 60 + "\n\n"
        report += "PERFORMANS KARŞILAŞTIRMASI:\n"
        report += "-" * 60 + "\n\n"

        for i, test_name in enumerate(perf_comp['tests']):
            report += f"{test_name}:\n"
            report += f"  Maks. Hız           : {format_turkish_number(perf_comp['max_speed'][i], 1)} km/h\n"
            report += f"  Maks. Güç           : {format_turkish_number(perf_comp['max_power'][i], 1)} kW\n"
            report += f"  Ort. Güç            : {format_turkish_number(perf_comp['avg_power'][i], 1)} kW\n"
            report += f"  Verimlilik Skoru    : {format_turkish_number(perf_comp['efficiency_score'][i], 1)}/100\n\n"

        # En iyi performans
        best_efficiency_idx = np.argmax(perf_comp['efficiency_score'])

        report += "ÖZET:\n"
        report += f"  En Yüksek Verimlilik: {perf_comp['tests'][best_efficiency_idx]} "
        report += f"({format_turkish_number(perf_comp['efficiency_score'][best_efficiency_idx], 1)}/100)\n\n"

        report += "╚══════════════════════════════════════════════════════════════╝\n"

        return report

    def create_all_comparison_charts(self):
        """
        Tüm karşılaştırma grafiklerini oluşturur

        Returns:
            dict: Grafik dosya yolları
        """
        charts = {}

        charts['consumption'] = self.plot_consumption_comparison()
        charts['performance'] = self.plot_performance_comparison()
        charts['speed_profiles'] = self.plot_speed_profiles_comparison()

        return charts


if __name__ == "__main__":
    print("Comparison Modülü Test")
    print("=" * 60)
    print("Test karşılaştırma özellikleri:")
    print("  - Enerji tüketimi karşılaştırması")
    print("  - Performans metrik karşılaştırması")
    print("  - Hız profilleri karşılaştırması")
    print("  - Grafik ve rapor oluşturma")
