"""
Grafik oluşturma modülü
Matplotlib ve Seaborn kullanarak test verileri için grafikler oluşturur
"""

import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışması için
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import io


class ChartGenerator:
    """Grafik oluşturucu sınıfı"""

    def __init__(self, config: Dict = None):
        """
        Args:
            config: Grafik ayarları
        """
        self.config = config or {}
        self.setup_style()

    def setup_style(self):
        """Grafik stilini ayarla"""
        # Stil
        style = self.config.get('style', 'seaborn-v0_8-darkgrid')
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')

        # Renk paleti
        palette = self.config.get('color_palette', 'Set2')
        sns.set_palette(palette)

        # Font boyutları
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9

        # Türkçe karakter desteği
        plt.rcParams['font.family'] = 'DejaVu Sans'

    def get_otokar_colors(self) -> Dict[str, str]:
        """Otokar kurumsal renklerini döndür"""
        return self.config.get('otokar_colors', {
            'primary': '#003366',
            'secondary': '#FF6600',
            'success': '#00AA44',
            'danger': '#DD0000',
            'warning': '#FFAA00',
            'info': '#0088CC',
        })

    def time_series_plot(
        self,
        df: pd.DataFrame,
        time_column: str,
        value_columns: List[str],
        title: str = 'Zaman Serisi Grafiği',
        xlabel: str = 'Zaman (s)',
        ylabel: str = 'Değer',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Zaman serisi grafiği oluştur

        Args:
            df: DataFrame
            time_column: Zaman sütunu
            value_columns: Değer sütunları
            title: Grafik başlığı
            xlabel: X ekseni etiketi
            ylabel: Y ekseni etiketi
            save_path: Kayıt yolu (None ise BytesIO döner)

        Returns:
            Path veya BytesIO: Grafik dosyası
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        colors = self.get_otokar_colors()
        color_list = list(colors.values())

        for i, col in enumerate(value_columns):
            if col in df.columns:
                color = color_list[i % len(color_list)]
                ax.plot(df[time_column], df[col], label=col, linewidth=2, color=color)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def speed_profile_plot(
        self,
        df: pd.DataFrame,
        time_column: str = 'Time',
        speed_column: str = 'Speed',
        target_speed_column: Optional[str] = None,
        title: str = 'Hız Profili',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Hız profili grafiği

        Args:
            df: DataFrame
            time_column: Zaman sütunu
            speed_column: Hız sütunu
            target_speed_column: Hedef hız sütunu (varsa)
            title: Başlık
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        colors = self.get_otokar_colors()

        # Gerçek hız
        ax.plot(df[time_column], df[speed_column],
                label='Gerçek Hız', linewidth=2, color=colors['primary'])

        # Hedef hız (varsa)
        if target_speed_column and target_speed_column in df.columns:
            ax.plot(df[time_column], df[target_speed_column],
                    label='Hedef Hız', linewidth=2, linestyle='--',
                    color=colors['secondary'], alpha=0.7)

        ax.set_xlabel('Zaman (s)')
        ax.set_ylabel('Hız (km/h)')
        ax.set_title(title, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def multi_test_comparison(
        self,
        datasets: Dict[str, pd.DataFrame],
        column: str,
        title: str = 'Test Karşılaştırması',
        ylabel: str = 'Değer',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Birden fazla testi karşılaştır

        Args:
            datasets: {test_adı: DataFrame} dictionary
            column: Karşılaştırılacak sütun
            title: Başlık
            ylabel: Y ekseni etiketi
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        colors = self.get_otokar_colors()
        color_list = list(colors.values())

        for i, (name, df) in enumerate(datasets.items()):
            if column in df.columns and 'Time' in df.columns:
                color = color_list[i % len(color_list)]
                ax.plot(df['Time'], df[column], label=name, linewidth=2, color=color)

        ax.set_xlabel('Zaman (s)')
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def bar_chart(
        self,
        data: Dict[str, float],
        title: str = 'Çubuk Grafik',
        xlabel: str = 'Kategori',
        ylabel: str = 'Değer',
        color_key: str = 'primary',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Çubuk grafiği

        Args:
            data: {kategori: değer} dictionary
            title: Başlık
            xlabel: X ekseni etiketi
            ylabel: Y ekseni etiketi
            color_key: Renk anahtarı
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = self.get_otokar_colors()

        categories = list(data.keys())
        values = list(data.values())

        bars = ax.bar(categories, values, color=colors.get(color_key, colors['primary']))

        # Değerleri çubukların üstüne yaz
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom')

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)

        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def statistics_comparison_chart(
        self,
        stats_df: pd.DataFrame,
        title: str = 'İstatistik Karşılaştırması',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        İstatistik karşılaştırma grafiği

        Args:
            stats_df: İstatistik DataFrame (satırlar: testler, sütunlar: metrikler)
            title: Başlık
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        colors = self.get_otokar_colors()
        color_list = list(colors.values())

        metrics = ['mean', 'std', 'min', 'max']
        titles = ['Ortalama', 'Standart Sapma', 'Minimum', 'Maksimum']

        for idx, (metric, subtitle) in enumerate(zip(metrics, titles)):
            ax = axes[idx // 2, idx % 2]

            if metric in stats_df.columns:
                bars = ax.bar(stats_df.index, stats_df[metric],
                             color=color_list[idx % len(color_list)])

                # Değerleri yaz
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}',
                           ha='center', va='bottom', fontsize=9)

                ax.set_title(subtitle, fontweight='bold')
                ax.set_ylabel('Değer')
                ax.grid(True, axis='y', alpha=0.3)
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def box_plot(
        self,
        datasets: Dict[str, pd.Series],
        title: str = 'Kutu Grafiği',
        ylabel: str = 'Değer',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Kutu grafiği (box plot)

        Args:
            datasets: {isim: Series} dictionary
            title: Başlık
            ylabel: Y ekseni etiketi
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = self.get_otokar_colors()

        data_list = [series.values for series in datasets.values()]
        labels = list(datasets.keys())

        bp = ax.boxplot(data_list, labels=labels, patch_artist=True)

        # Renklendirme
        for patch in bp['boxes']:
            patch.set_facecolor(colors['primary'])
            patch.set_alpha(0.7)

        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)

        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def energy_consumption_chart(
        self,
        df: pd.DataFrame,
        time_column: str = 'Time',
        energy_column: str = 'Energy',
        title: str = 'Enerji Tüketimi',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Enerji tüketimi grafiği

        Args:
            df: DataFrame
            time_column: Zaman sütunu
            energy_column: Enerji sütunu
            title: Başlık
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        colors = self.get_otokar_colors()

        # Kümülatif enerji
        ax1.plot(df[time_column], df[energy_column],
                linewidth=2, color=colors['primary'])
        ax1.set_xlabel('Zaman (s)')
        ax1.set_ylabel('Kümülatif Enerji (Wh)')
        ax1.set_title('Kümülatif Enerji Tüketimi', fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Anlık güç (türev)
        if len(df) > 1:
            power = df[energy_column].diff() / df[time_column].diff() * 3600  # W
            ax2.plot(df[time_column], power,
                    linewidth=1.5, color=colors['secondary'], alpha=0.8)
            ax2.set_xlabel('Zaman (s)')
            ax2.set_ylabel('Anlık Güç (W)')
            ax2.set_title('Anlık Güç Tüketimi', fontweight='bold')
            ax2.grid(True, alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def pie_chart(
        self,
        data: Dict[str, float],
        title: str = 'Pasta Grafiği',
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Pasta grafiği

        Args:
            data: {kategori: değer} dictionary
            title: Başlık
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        colors_dict = self.get_otokar_colors()
        colors = list(colors_dict.values())

        labels = list(data.keys())
        sizes = list(data.values())

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )

        # Metin stilini düzenle
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(title, fontweight='bold')

        plt.tight_layout()

        return self._save_or_return(fig, save_path)

    def create_dashboard(
        self,
        df: pd.DataFrame,
        test_info: Dict,
        save_path: Optional[Path] = None
    ) -> Union[Path, io.BytesIO]:
        """
        Kapsamlı dashboard oluştur

        Args:
            df: Test verisi DataFrame
            test_info: Test bilgileri
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        colors = self.get_otokar_colors()

        # 1. Hız profili
        ax1 = fig.add_subplot(gs[0, :])
        if 'Speed' in df.columns:
            ax1.plot(df['Time'], df['Speed'], linewidth=2, color=colors['primary'])
            ax1.set_ylabel('Hız (km/h)')
            ax1.set_title('Hız Profili', fontweight='bold')
            ax1.grid(True, alpha=0.3)

        # 2. Mesafe
        ax2 = fig.add_subplot(gs[1, 0])
        if 'Distance' in df.columns:
            ax2.plot(df['Time'], df['Distance'], linewidth=2, color=colors['info'])
            ax2.set_xlabel('Zaman (s)')
            ax2.set_ylabel('Mesafe (m)')
            ax2.set_title('Mesafe', fontweight='bold')
            ax2.grid(True, alpha=0.3)

        # 3. Enerji
        ax3 = fig.add_subplot(gs[1, 1])
        if 'Energy' in df.columns:
            ax3.plot(df['Time'], df['Energy'], linewidth=2, color=colors['secondary'])
            ax3.set_xlabel('Zaman (s)')
            ax3.set_ylabel('Enerji (Wh)')
            ax3.set_title('Kümülatif Enerji', fontweight='bold')
            ax3.grid(True, alpha=0.3)

        # 4. Gaz pedalı
        ax4 = fig.add_subplot(gs[2, 0])
        if 'Throttle' in df.columns:
            ax4.plot(df['Time'], df['Throttle'], linewidth=1.5, color=colors['success'])
            ax4.set_xlabel('Zaman (s)')
            ax4.set_ylabel('Gaz Pedalı (%)')
            ax4.set_title('Gaz Pedalı', fontweight='bold')
            ax4.grid(True, alpha=0.3)

        # 5. Özet istatistikler (metin)
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis('off')

        summary_text = f"""
        TEST BİLGİLERİ
        {'='*30}
        Test Tipi: {test_info.get('test_type', 'N/A')}
        Süre: {test_info.get('duration', 0):.1f} s
        Mesafe: {test_info.get('total_distance', 0):.1f} m

        Ort. Hız: {df['Speed'].mean():.1f} km/h
        Max Hız: {df['Speed'].max():.1f} km/h

        Toplam Enerji: {df['Energy'].iloc[-1]:.1f} Wh
        """

        ax5.text(0.1, 0.9, summary_text, transform=ax5.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        fig.suptitle(f'Test Dashboard - {test_info.get("test_type", "Unknown")}',
                    fontsize=16, fontweight='bold')

        return self._save_or_return(fig, save_path)

    def _save_or_return(self, fig, save_path: Optional[Path]) -> Union[Path, io.BytesIO]:
        """
        Grafiği kaydet veya BytesIO olarak döndür

        Args:
            fig: Matplotlib figure
            save_path: Kayıt yolu

        Returns:
            Path veya BytesIO
        """
        dpi = self.config.get('dpi', 150)

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            print(f"✓ Grafik kaydedildi: {save_path}")
            return save_path
        else:
            # BytesIO'ya kaydet
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            return buf
