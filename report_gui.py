"""
SORT Test Otomasyon Sistemi - Raporlama GUI Modülü
Test sonuçlarını analiz etme ve Excel raporu oluşturma
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import pyqtgraph as pg
import numpy as np
import pandas as pd

from data_logger import DataLogger
from utils import format_energy, calculate_percentage_difference


class ReportWindow(QMainWindow):
    """Raporlama penceresi"""

    def __init__(self):
        super().__init__()

        self.test_files = []
        self.selected_gidis = []
        self.selected_donus = []

        self.init_ui()
        self.load_test_files()

        self.logger = logging.getLogger(__name__)

    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("SORT Test Raporlama")
        self.setGeometry(150, 150, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Test seçim paneli
        main_layout.addWidget(self.create_selection_panel())

        # Analiz sonuçları
        main_layout.addWidget(self.create_analysis_panel())

        # Grafik karşılaştırma
        main_layout.addWidget(self.create_graph_panel())

        # Alt butonlar
        main_layout.addWidget(self.create_button_panel())

    def create_selection_panel(self) -> QWidget:
        """Test seçim paneli"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Gidiş testleri
        gidis_group = QGroupBox("Gidiş Testleri")
        gidis_layout = QVBoxLayout()
        self.list_gidis = QListWidget()
        self.list_gidis.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        gidis_layout.addWidget(self.list_gidis)
        gidis_group.setLayout(gidis_layout)
        layout.addWidget(gidis_group)

        # Dönüş testleri
        donus_group = QGroupBox("Dönüş Testleri")
        donus_layout = QVBoxLayout()
        self.list_donus = QListWidget()
        self.list_donus.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        donus_layout.addWidget(self.list_donus)
        donus_group.setLayout(donus_layout)
        layout.addWidget(donus_group)

        return widget

    def create_analysis_panel(self) -> QGroupBox:
        """Analiz sonuçları paneli"""
        group = QGroupBox("Analiz Sonuçları")
        layout = QVBoxLayout()

        self.text_analysis = QTextEdit()
        self.text_analysis.setReadOnly(True)
        self.text_analysis.setFont(QFont("Courier New", 10))
        layout.addWidget(self.text_analysis)

        group.setLayout(layout)
        return group

    def create_graph_panel(self) -> QWidget:
        """Grafik karşılaştırma paneli"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Gidiş grafikleri
        gidis_widget = QWidget()
        gidis_layout = QVBoxLayout(gidis_widget)
        gidis_layout.addWidget(QLabel("GİDİŞ"))

        self.plot_gidis_speed = pg.PlotWidget(title="Hız-Mesafe")
        self.plot_gidis_speed.setLabel('left', 'Hız', units='km/h')
        self.plot_gidis_speed.setLabel('bottom', 'Mesafe', units='m')
        self.plot_gidis_speed.showGrid(x=True, y=True)
        gidis_layout.addWidget(self.plot_gidis_speed)

        self.plot_gidis_energy = pg.PlotWidget(title="Enerji-Mesafe")
        self.plot_gidis_energy.setLabel('left', 'Enerji', units='kWh')
        self.plot_gidis_energy.setLabel('bottom', 'Mesafe', units='m')
        self.plot_gidis_energy.showGrid(x=True, y=True)
        gidis_layout.addWidget(self.plot_gidis_energy)

        layout.addWidget(gidis_widget)

        # Dönüş grafikleri
        donus_widget = QWidget()
        donus_layout = QVBoxLayout(donus_widget)
        donus_layout.addWidget(QLabel("DÖNÜŞ"))

        self.plot_donus_speed = pg.PlotWidget(title="Hız-Mesafe")
        self.plot_donus_speed.setLabel('left', 'Hız', units='km/h')
        self.plot_donus_speed.setLabel('bottom', 'Mesafe', units='m')
        self.plot_donus_speed.showGrid(x=True, y=True)
        donus_layout.addWidget(self.plot_donus_speed)

        self.plot_donus_energy = pg.PlotWidget(title="Enerji-Mesafe")
        self.plot_donus_energy.setLabel('left', 'Enerji', units='kWh')
        self.plot_donus_energy.setLabel('bottom', 'Mesafe', units='m')
        self.plot_donus_energy.showGrid(x=True, y=True)
        donus_layout.addWidget(self.plot_donus_energy)

        layout.addWidget(donus_widget)

        return widget

    def create_button_panel(self) -> QWidget:
        """Alt buton paneli"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        layout.addStretch()

        self.btn_analyze = QPushButton("Analiz Et")
        self.btn_analyze.clicked.connect(self.on_analyze_clicked)
        layout.addWidget(self.btn_analyze)

        self.btn_export = QPushButton("Rapor Oluştur (Excel)")
        self.btn_export.clicked.connect(self.on_export_clicked)
        layout.addWidget(self.btn_export)

        self.btn_refresh = QPushButton("Yenile")
        self.btn_refresh.clicked.connect(self.load_test_files)
        layout.addWidget(self.btn_refresh)

        return widget

    def load_test_files(self):
        """Test dosyalarını yükle"""
        self.list_gidis.clear()
        self.list_donus.clear()

        # Data klasöründeki CSV dosyalarını bul
        test_files = DataLogger.get_test_files(directory='data')

        for filepath in test_files:
            filename = filepath.name
            summary = DataLogger.get_test_summary(str(filepath))

            if summary is None:
                continue

            # Liste item oluştur
            energy = summary['total_energy']
            item_text = f"{filename} ({format_energy(energy)})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, str(filepath))

            # Gidiş/Dönüş ayır
            if 'GIDIS' in filename.upper():
                self.list_gidis.addItem(item)
            elif 'DONUS' in filename.upper():
                self.list_donus.addItem(item)

        self.logger.info(f"Toplam {len(test_files)} test dosyası yüklendi")

    def on_analyze_clicked(self):
        """Analiz butonu"""
        try:
            # Seçili testleri al
            gidis_items = self.list_gidis.selectedItems()
            donus_items = self.list_donus.selectedItems()

            if not gidis_items and not donus_items:
                QMessageBox.warning(self, "Uyarı", "En az bir test seçmelisiniz!")
                return

            # Gidiş analizi
            gidis_results = None
            if gidis_items:
                gidis_files = [item.data(Qt.ItemDataRole.UserRole) for item in gidis_items]
                gidis_results = self.analyze_tests(gidis_files, "GİDİŞ")

            # Dönüş analizi
            donus_results = None
            if donus_items:
                donus_files = [item.data(Qt.ItemDataRole.UserRole) for item in donus_items]
                donus_results = self.analyze_tests(donus_files, "DÖNÜŞ")

            # Sonuçları göster
            self.display_analysis_results(gidis_results, donus_results)

            # Grafikleri çiz
            self.plot_comparison(gidis_results, donus_results)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz hatası: {e}")
            self.logger.error(f"Analiz hatası: {e}", exc_info=True)

    def analyze_tests(self, filepaths: List[str], direction: str) -> Dict:
        """
        Testleri analiz et

        SORT standardı: En düşük enerji tüketimine sahip 3 test seçilir
        (aralarındaki fark %2'den az olmalı)
        """
        results = {
            'direction': direction,
            'all_tests': [],
            'selected_tests': [],
            'average_energy': 0.0,
            'dataframes': []
        }

        # Tüm testleri yükle
        for filepath in filepaths:
            summary = DataLogger.get_test_summary(filepath)
            df = DataLogger.load_test_data(filepath)

            if summary and df is not None:
                results['all_tests'].append({
                    'filepath': filepath,
                    'filename': Path(filepath).name,
                    'energy': summary['total_energy'],
                    'summary': summary,
                    'dataframe': df
                })

        # Enerjiye göre sırala (en düşük ilk)
        results['all_tests'].sort(key=lambda x: x['energy'])

        # En düşük enerjili testi seç
        if results['all_tests']:
            min_test = results['all_tests'][0]
            min_energy = min_test['energy']

            # %2 tolerans dahilinde olan testleri seç (maksimum 3 test)
            for test in results['all_tests']:
                diff_percent = calculate_percentage_difference(min_energy, test['energy'])

                if diff_percent <= 2.0 and len(results['selected_tests']) < 3:
                    test['diff_percent'] = diff_percent
                    results['selected_tests'].append(test)
                    results['dataframes'].append(test['dataframe'])

            # Ortalama enerji
            if results['selected_tests']:
                total = sum([t['energy'] for t in results['selected_tests']])
                results['average_energy'] = total / len(results['selected_tests'])

        return results

    def display_analysis_results(self, gidis_results: Dict, donus_results: Dict):
        """Analiz sonuçlarını göster"""
        text = ""

        if gidis_results:
            text += "=" * 60 + "\n"
            text += "GİDİŞ YÖNÜ\n"
            text += "=" * 60 + "\n"
            text += f"Toplam test sayısı: {len(gidis_results['all_tests'])}\n"
            text += f"Seçilen test sayısı: {len(gidis_results['selected_tests'])}\n\n"

            for idx, test in enumerate(gidis_results['selected_tests'], 1):
                text += f"{idx}. {test['filename']}\n"
                text += f"   Enerji: {format_energy(test['energy'])}\n"
                if idx > 1:
                    text += f"   Fark: +{test['diff_percent']:.2f}%\n"
                text += "\n"

            text += f"Ortalama Enerji: {format_energy(gidis_results['average_energy'])}\n"
            text += "\n\n"

        if donus_results:
            text += "=" * 60 + "\n"
            text += "DÖNÜŞ YÖNÜ\n"
            text += "=" * 60 + "\n"
            text += f"Toplam test sayısı: {len(donus_results['all_tests'])}\n"
            text += f"Seçilen test sayısı: {len(donus_results['selected_tests'])}\n\n"

            for idx, test in enumerate(donus_results['selected_tests'], 1):
                text += f"{idx}. {test['filename']}\n"
                text += f"   Enerji: {format_energy(test['energy'])}\n"
                if idx > 1:
                    text += f"   Fark: +{test['diff_percent']:.2f}%\n"
                text += "\n"

            text += f"Ortalama Enerji: {format_energy(donus_results['average_energy'])}\n"

        self.text_analysis.setPlainText(text)

    def plot_comparison(self, gidis_results: Dict, donus_results: Dict):
        """Karşılaştırma grafiklerini çiz"""
        colors = ['g', 'b', 'r', 'y', 'm', 'c']

        # Gidiş grafikleri
        self.plot_gidis_speed.clear()
        self.plot_gidis_energy.clear()

        if gidis_results and gidis_results['selected_tests']:
            for idx, test in enumerate(gidis_results['selected_tests']):
                df = test['dataframe']
                color = colors[idx % len(colors)]

                # Hız-Mesafe
                self.plot_gidis_speed.plot(
                    df['distance_m'].values,
                    df['speed_kmh'].values,
                    pen=color,
                    name=f"Test {idx+1}"
                )

                # Enerji-Mesafe
                self.plot_gidis_energy.plot(
                    df['distance_m'].values,
                    df['energy_kwh'].values,
                    pen=color,
                    name=f"Test {idx+1}"
                )

        # Dönüş grafikleri
        self.plot_donus_speed.clear()
        self.plot_donus_energy.clear()

        if donus_results and donus_results['selected_tests']:
            for idx, test in enumerate(donus_results['selected_tests']):
                df = test['dataframe']
                color = colors[idx % len(colors)]

                # Hız-Mesafe
                self.plot_donus_speed.plot(
                    df['distance_m'].values,
                    df['speed_kmh'].values,
                    pen=color,
                    name=f"Test {idx+1}"
                )

                # Enerji-Mesafe
                self.plot_donus_energy.plot(
                    df['distance_m'].values,
                    df['energy_kwh'].values,
                    pen=color,
                    name=f"Test {idx+1}"
                )

    def on_export_clicked(self):
        """Excel raporu oluştur"""
        try:
            # Seçili testleri al
            gidis_items = self.list_gidis.selectedItems()
            donus_items = self.list_donus.selectedItems()

            if not gidis_items and not donus_items:
                QMessageBox.warning(self, "Uyarı", "En az bir test seçmelisiniz!")
                return

            # Analiz yap
            gidis_results = None
            if gidis_items:
                gidis_files = [item.data(Qt.ItemDataRole.UserRole) for item in gidis_items]
                gidis_results = self.analyze_tests(gidis_files, "GİDİŞ")

            donus_results = None
            if donus_items:
                donus_files = [item.data(Qt.ItemDataRole.UserRole) for item in donus_items]
                donus_results = self.analyze_tests(donus_files, "DÖNÜŞ")

            # Dosya adı sor
            default_name = f"SORT_Rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Raporu Kaydet",
                default_name,
                "Excel Dosyaları (*.xlsx)"
            )

            if not filepath:
                return

            # Excel raporu oluştur
            self.create_excel_report(filepath, gidis_results, donus_results)

            QMessageBox.information(self, "Başarılı", f"Rapor oluşturuldu:\n{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor oluşturma hatası: {e}")
            self.logger.error(f"Rapor hatası: {e}", exc_info=True)

    def create_excel_report(self, filepath: str, gidis_results: Dict, donus_results: Dict):
        """Excel raporu oluştur"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sayfa 1: Özet
            summary_data = []

            if gidis_results:
                summary_data.append(['GİDİŞ YÖNÜ', ''])
                summary_data.append(['Seçilen Test Sayısı', len(gidis_results['selected_tests'])])
                summary_data.append(['Ortalama Enerji (kWh)', gidis_results['average_energy']])
                summary_data.append(['', ''])

                for idx, test in enumerate(gidis_results['selected_tests'], 1):
                    summary_data.append([f"Test {idx}", test['filename']])
                    summary_data.append(['  Enerji (kWh)', test['energy']])
                    if idx > 1:
                        summary_data.append(['  Fark (%)', test['diff_percent']])

                summary_data.append(['', ''])

            if donus_results:
                summary_data.append(['DÖNÜŞ YÖNÜ', ''])
                summary_data.append(['Seçilen Test Sayısı', len(donus_results['selected_tests'])])
                summary_data.append(['Ortalama Enerji (kWh)', donus_results['average_energy']])
                summary_data.append(['', ''])

                for idx, test in enumerate(donus_results['selected_tests'], 1):
                    summary_data.append([f"Test {idx}", test['filename']])
                    summary_data.append(['  Enerji (kWh)', test['energy']])
                    if idx > 1:
                        summary_data.append(['  Fark (%)', test['diff_percent']])

            df_summary = pd.DataFrame(summary_data, columns=['Parametre', 'Değer'])
            df_summary.to_excel(writer, sheet_name='Özet', index=False)

            # Sayfa 2: Gidiş Testleri Detay
            if gidis_results and gidis_results['dataframes']:
                combined_df = pd.concat(gidis_results['dataframes'], ignore_index=True)
                combined_df.to_excel(writer, sheet_name='Gidiş Detay', index=False)

            # Sayfa 3: Dönüş Testleri Detay
            if donus_results and donus_results['dataframes']:
                combined_df = pd.concat(donus_results['dataframes'], ignore_index=True)
                combined_df.to_excel(writer, sheet_name='Dönüş Detay', index=False)

        self.logger.info(f"Excel raporu oluşturuldu: {filepath}")


def main():
    """Ana fonksiyon"""
    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ReportWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
