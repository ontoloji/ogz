"""
Ana rapor oluşturucu modülü
Tüm bileşenleri bir araya getirerek tam rapor oluşturur
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import tempfile

from .config import ReportConfig
from .data_reader import DataReader, TestDataReader
from .statistics import StatisticsAnalyzer, RequirementChecker
from .chart_generator import ChartGenerator
from .pdf_generator import PDFGenerator
from .word_generator import WordGenerator


class ReportBuilder:
    """Ana rapor oluşturucu sınıfı"""

    def __init__(self, config: Dict = None, language: str = 'tr'):
        """
        Args:
            config: Özel konfigürasyon
            language: Dil ('tr' veya 'en')
        """
        # Konfigürasyon
        if config is None:
            config = {}
        config['language'] = language
        self.config = ReportConfig(config)
        self.config.ensure_dirs()

        # Modüller
        self.data_reader = TestDataReader()
        self.stats_analyzer = StatisticsAnalyzer(
            decimal_places=self.config.get('statistics.decimal_places', 2)
        )
        self.chart_generator = ChartGenerator(
            config=self.config.get('charts', {})
        )
        self.requirement_checker = RequirementChecker(
            requirements=self.config.get('requirements', {})
        )

        # Veri
        self.test_data = None
        self.test_metadata = None
        self.statistics = {}
        self.charts = {}
        self.requirement_results = []

    def load_test_data(
        self,
        data_file: Union[str, Path],
        metadata_file: Optional[Union[str, Path]] = None
    ):
        """
        Test verisini yükle

        Args:
            data_file: Test verisi dosyası
            metadata_file: Metadata dosyası (opsiyonel)
        """
        print(f"\n{'='*60}")
        print("TEST VERİSİ YÜKLEME")
        print(f"{'='*60}")

        self.test_data = self.data_reader.read_sort_test(data_file)
        if metadata_file:
            self.test_metadata = self.data_reader.read_json(metadata_file)
        else:
            self.test_metadata = self.data_reader.test_metadata

        print(f"✓ Test verisi yüklendi")
        return self

    def analyze_data(self, columns: List[str] = None):
        """
        Veriyi analiz et

        Args:
            columns: Analiz edilecek sütunlar (None ise default)
        """
        print(f"\n{'='*60}")
        print("VERİ ANALİZİ")
        print(f"{'='*60}")

        if self.test_data is None:
            raise ValueError("Önce test verisi yüklenmelidir")

        # Default sütunlar
        if columns is None:
            columns = ['Speed', 'Distance', 'Throttle', 'Energy']
            columns = [c for c in columns if c in self.test_data.columns]

        # İstatistikler
        self.statistics = {}
        for col in columns:
            if col in self.test_data.columns:
                self.statistics[col] = self.stats_analyzer.basic_statistics(
                    self.test_data[col]
                )
                print(f"  ✓ {col} analizi tamamlandı")

        # Enerji tüketimi hesapla
        if 'Energy' in self.test_data.columns and 'Distance' in self.test_data.columns:
            energy_consumption = self.stats_analyzer.calculate_energy_consumption(
                self.test_data['Energy'],
                self.test_data['Distance']
            )
            self.statistics['energy_consumption'] = {
                'value': energy_consumption,
                'unit': 'kWh/100km'
            }
            print(f"  ✓ Enerji tüketimi: {energy_consumption:.2f} kWh/100km")

        print(f"✓ Veri analizi tamamlandı")
        return self

    def generate_charts(self, output_dir: Optional[Path] = None):
        """
        Grafikleri oluştur

        Args:
            output_dir: Grafiklerin kaydedileceği dizin (None ise temp)
        """
        print(f"\n{'='*60}")
        print("GRAFİK OLUŞTURMA")
        print(f"{'='*60}")

        if self.test_data is None:
            raise ValueError("Önce test verisi yüklenmelidir")

        # Temp dizin
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp())
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Test bilgileri
        test_info = self.data_reader.get_test_info()

        # Hız profili
        if 'Speed' in self.test_data.columns:
            self.charts['speed_profile'] = self.chart_generator.speed_profile_plot(
                self.test_data,
                title=f"{self.config.translate('speed')} - {test_info.get('test_type', '')}",
                save_path=output_dir / 'speed_profile.png'
            )

        # Enerji tüketimi
        if 'Energy' in self.test_data.columns:
            self.charts['energy_consumption'] = self.chart_generator.energy_consumption_chart(
                self.test_data,
                title=f"{self.config.translate('energy')} - {test_info.get('test_type', '')}",
                save_path=output_dir / 'energy_consumption.png'
            )

        # Dashboard
        self.charts['dashboard'] = self.chart_generator.create_dashboard(
            self.test_data,
            test_info,
            save_path=output_dir / 'dashboard.png'
        )

        print(f"✓ {len(self.charts)} grafik oluşturuldu")
        return self

    def check_requirements(self, test_type: Optional[str] = None):
        """
        Gereksinimleri kontrol et

        Args:
            test_type: Test tipi (None ise metadata'dan alınır)
        """
        print(f"\n{'='*60}")
        print("GEREKSİNİM KONTROLÜ")
        print(f"{'='*60}")

        if self.test_data is None:
            raise ValueError("Önce test verisi yüklenmelidir")

        # Test tipini belirle
        if test_type is None:
            test_type = self.data_reader.test_type or self.test_metadata.get('test_type')

        if test_type is None:
            print("⚠ Test tipi belirtilmedi, gereksinim kontrolü atlandı")
            return self

        # Gerçekleşen değerler
        actual_values = {
            'max_duration': self.test_data['Time'].max(),
            'min_distance': self.test_data['Distance'].max(),
        }

        # Enerji tüketimi varsa
        if 'energy_consumption' in self.statistics:
            actual_values['max_energy_consumption'] = self.statistics['energy_consumption']['value']

        # Kontrol
        self.requirement_results = self.requirement_checker.check_all_requirements(
            test_type, actual_values
        )

        # Özet
        summary = self.requirement_checker.generate_summary(self.requirement_results)
        print(f"  Toplam: {summary['total_checks']}")
        print(f"  Başarılı: {summary['passed']}")
        print(f"  Başarısız: {summary['failed']}")
        print(f"  Genel Durum: {summary['overall_status']}")

        return self

    def generate_pdf_report(
        self,
        output_path: Union[str, Path],
        include_charts: bool = True,
        include_requirements: bool = True
    ) -> Path:
        """
        PDF raporu oluştur

        Args:
            output_path: Çıktı dosya yolu
            include_charts: Grafikleri dahil et
            include_requirements: Gereksinim kontrolünü dahil et

        Returns:
            Path: Oluşturulan dosya yolu
        """
        print(f"\n{'='*60}")
        print("PDF RAPORU OLUŞTURMA")
        print(f"{'='*60}")

        if self.test_data is None:
            raise ValueError("Önce test verisi yüklenmelidir")

        # PDF generator
        pdf_config = self.config.config.get('pdf', {})
        pdf_config['translations'] = self.config.translations
        pdf_config['company_name'] = self.config.get('company_name', 'OTOKAR')

        pdf_gen = PDFGenerator(config=pdf_config)

        # Test bilgileri
        test_info = self.data_reader.get_test_info()
        test_info.update(self.test_metadata or {})

        # Kapak sayfası
        pdf_gen.create_cover_page(
            title=self.config.translate('report_title'),
            test_info=test_info,
            logo_path=self.config.get('logo_path')
        )

        # Özet
        pdf_gen.add_section_title(self.config.translate('summary'))
        summary_text = (
            f"{self.config.translate('test_type')}: {test_info.get('test_type', 'N/A')}<br/>"
            f"{self.config.translate('duration')}: {self.test_data['Time'].max():.1f} s<br/>"
            f"{self.config.translate('distance')}: {self.test_data['Distance'].max():.1f} m<br/>"
        )
        if 'energy_consumption' in self.statistics:
            ec = self.statistics['energy_consumption']['value']
            summary_text += f"{self.config.translate('energy')}: {ec:.2f} kWh/100km<br/>"

        pdf_gen.add_paragraph(summary_text)

        # İstatistikler
        pdf_gen.add_section_title(self.config.translate('statistics'))
        pdf_gen.add_statistics_table(
            self.statistics,
            title=self.config.translate('test_results')
        )

        # Grafikler
        if include_charts and self.charts:
            pdf_gen.add_page_break()
            pdf_gen.add_section_title(self.config.translate('charts'))
            for chart_name, chart_path in self.charts.items():
                if chart_path and Path(chart_path).exists():
                    pdf_gen.add_image(
                        chart_path,
                        title=chart_name.replace('_', ' ').title()
                    )

        # Gereksinim kontrolü
        if include_requirements and self.requirement_results:
            pdf_gen.add_page_break()
            pdf_gen.add_section_title(self.config.translate('requirements'))
            pdf_gen.add_requirement_check_table(
                self.requirement_results,
                title=self.config.translate('requirements')
            )

        # PDF'i kaydet
        output_path = pdf_gen.build(output_path, test_info)
        return output_path

    def generate_word_report(
        self,
        output_path: Union[str, Path],
        include_charts: bool = True,
        include_requirements: bool = True
    ) -> Path:
        """
        Word raporu oluştur

        Args:
            output_path: Çıktı dosya yolu
            include_charts: Grafikleri dahil et
            include_requirements: Gereksinim kontrolünü dahil et

        Returns:
            Path: Oluşturulan dosya yolu
        """
        print(f"\n{'='*60}")
        print("WORD RAPORU OLUŞTURMA")
        print(f"{'='*60}")

        if self.test_data is None:
            raise ValueError("Önce test verisi yüklenmelidir")

        # Word generator
        word_config = self.config.config.get('word', {})
        word_config['translations'] = self.config.translations
        word_config['company_name'] = self.config.get('company_name', 'OTOKAR')

        word_gen = WordGenerator(config=word_config)

        # Test bilgileri
        test_info = self.data_reader.get_test_info()
        test_info.update(self.test_metadata or {})

        # Kapak sayfası
        word_gen.create_cover_page(
            title=self.config.translate('report_title'),
            test_info=test_info,
            logo_path=self.config.get('logo_path')
        )

        # Özet
        word_gen.add_section_title(self.config.translate('summary'))
        summary_text = (
            f"{self.config.translate('test_type')}: {test_info.get('test_type', 'N/A')}\n"
            f"{self.config.translate('duration')}: {self.test_data['Time'].max():.1f} s\n"
            f"{self.config.translate('distance')}: {self.test_data['Distance'].max():.1f} m"
        )
        if 'energy_consumption' in self.statistics:
            ec = self.statistics['energy_consumption']['value']
            summary_text += f"\n{self.config.translate('energy')}: {ec:.2f} kWh/100km"

        word_gen.add_paragraph(summary_text)

        # İstatistikler
        word_gen.add_section_title(self.config.translate('statistics'))
        word_gen.add_statistics_table(
            self.statistics,
            title=self.config.translate('test_results')
        )

        # Grafikler
        if include_charts and self.charts:
            word_gen.add_page_break()
            word_gen.add_section_title(self.config.translate('charts'))
            for chart_name, chart_path in self.charts.items():
                if chart_path and Path(chart_path).exists():
                    word_gen.add_image(
                        chart_path,
                        title=chart_name.replace('_', ' ').title()
                    )

        # Gereksinim kontrolü
        if include_requirements and self.requirement_results:
            word_gen.add_page_break()
            word_gen.add_section_title(self.config.translate('requirements'))
            word_gen.add_requirement_check_table(
                self.requirement_results,
                title=self.config.translate('requirements')
            )

        # Word'ü kaydet
        output_path = word_gen.save(output_path)
        return output_path

    def generate_full_report(
        self,
        data_file: Union[str, Path],
        output_format: str = 'pdf',
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Path:
        """
        Tam rapor oluştur (tek adımda)

        Args:
            data_file: Test verisi dosyası
            output_format: Çıktı formatı ('pdf' veya 'word')
            output_path: Çıktı dosya yolu (None ise otomatik)
            **kwargs: Diğer parametreler

        Returns:
            Path: Oluşturulan dosya yolu
        """
        # Veriyi yükle
        self.load_test_data(data_file)

        # Analiz et
        self.analyze_data()

        # Grafikleri oluştur
        self.generate_charts()

        # Gereksinimleri kontrol et
        self.check_requirements()

        # Çıktı yolu
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_type = self.data_reader.test_type or 'test'
            ext = 'pdf' if output_format == 'pdf' else 'docx'
            output_path = self.config.config['REPORTS_DIR'] / f"{test_type}_report_{timestamp}.{ext}"

        # Raporu oluştur
        if output_format == 'pdf':
            return self.generate_pdf_report(output_path, **kwargs)
        elif output_format in ['word', 'docx']:
            return self.generate_word_report(output_path, **kwargs)
        else:
            raise ValueError(f"Desteklenmeyen format: {output_format}")
