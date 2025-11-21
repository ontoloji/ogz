"""
Toplu rapor oluşturma modülü
Birden fazla test için otomatik rapor oluşturur
"""

from pathlib import Path
from typing import List, Dict, Union, Optional
import concurrent.futures
from datetime import datetime

from .report_builder import ReportBuilder


class BatchReportProcessor:
    """Toplu rapor işleme sınıfı"""

    def __init__(self, config: Dict = None, language: str = 'tr'):
        """
        Args:
            config: Rapor konfigürasyonu
            language: Dil
        """
        self.config = config
        self.language = language
        self.results = []

    def process_single_file(
        self,
        data_file: Path,
        output_format: str = 'pdf',
        output_dir: Optional[Path] = None
    ) -> Dict:
        """
        Tek bir dosya için rapor oluştur

        Args:
            data_file: Test verisi dosyası
            output_format: Çıktı formatı
            output_dir: Çıktı dizini

        Returns:
            Dict: Sonuç bilgileri
        """
        try:
            print(f"\n{'='*70}")
            print(f"İşleniyor: {data_file.name}")
            print(f"{'='*70}")

            # Report builder
            builder = ReportBuilder(config=self.config, language=self.language)

            # Çıktı yolu
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                ext = 'pdf' if output_format == 'pdf' else 'docx'
                output_path = output_dir / f"{data_file.stem}_report.{ext}"
            else:
                output_path = None

            # Raporu oluştur
            start_time = datetime.now()
            report_path = builder.generate_full_report(
                data_file,
                output_format=output_format,
                output_path=output_path
            )
            duration = (datetime.now() - start_time).total_seconds()

            result = {
                'input_file': str(data_file),
                'output_file': str(report_path),
                'status': 'success',
                'duration': duration,
                'message': f'Rapor başarıyla oluşturuldu ({duration:.1f}s)'
            }

            print(f"✓ BAŞARILI: {report_path}")
            return result

        except Exception as e:
            result = {
                'input_file': str(data_file),
                'output_file': None,
                'status': 'error',
                'duration': 0,
                'message': f'Hata: {str(e)}'
            }
            print(f"✗ HATA: {str(e)}")
            return result

    def process_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        pattern: str = '*.csv',
        output_format: str = 'pdf',
        parallel: bool = True,
        max_workers: int = 4
    ) -> List[Dict]:
        """
        Bir dizindeki tüm dosyaları işle

        Args:
            input_dir: Girdi dizini
            output_dir: Çıktı dizini
            pattern: Dosya deseni (glob pattern)
            output_format: Çıktı formatı
            parallel: Paralel işleme
            max_workers: Maksimum işçi sayısı

        Returns:
            List[Dict]: Sonuç listesi
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        # Dosyaları bul
        files = list(input_dir.glob(pattern))

        if not files:
            print(f"⚠ Hiç dosya bulunamadı: {input_dir / pattern}")
            return []

        print(f"\n{'='*70}")
        print(f"TOPLU RAPOR OLUŞTURMA")
        print(f"{'='*70}")
        print(f"Girdi dizini: {input_dir}")
        print(f"Çıktı dizini: {output_dir}")
        print(f"Dosya sayısı: {len(files)}")
        print(f"Format: {output_format.upper()}")
        print(f"Paralel: {'Evet' if parallel else 'Hayır'}")

        self.results = []
        start_time = datetime.now()

        if parallel and len(files) > 1:
            # Paralel işleme
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self.process_single_file,
                        file,
                        output_format,
                        output_dir
                    ): file for file in files
                }

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    self.results.append(result)
        else:
            # Seri işleme
            for file in files:
                result = self.process_single_file(file, output_format, output_dir)
                self.results.append(result)

        # Özet
        total_duration = (datetime.now() - start_time).total_seconds()
        self._print_summary(total_duration)

        return self.results

    def process_file_list(
        self,
        file_list: List[Union[str, Path]],
        output_dir: Union[str, Path],
        output_format: str = 'pdf',
        parallel: bool = True,
        max_workers: int = 4
    ) -> List[Dict]:
        """
        Dosya listesini işle

        Args:
            file_list: Dosya listesi
            output_dir: Çıktı dizini
            output_format: Çıktı formatı
            parallel: Paralel işleme
            max_workers: Maksimum işçi sayısı

        Returns:
            List[Dict]: Sonuç listesi
        """
        output_dir = Path(output_dir)
        files = [Path(f) for f in file_list]

        print(f"\n{'='*70}")
        print(f"TOPLU RAPOR OLUŞTURMA (Dosya Listesi)")
        print(f"{'='*70}")
        print(f"Dosya sayısı: {len(files)}")
        print(f"Çıktı dizini: {output_dir}")

        self.results = []
        start_time = datetime.now()

        if parallel and len(files) > 1:
            # Paralel işleme
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self.process_single_file,
                        file,
                        output_format,
                        output_dir
                    ): file for file in files
                }

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    self.results.append(result)
        else:
            # Seri işleme
            for file in files:
                result = self.process_single_file(file, output_format, output_dir)
                self.results.append(result)

        # Özet
        total_duration = (datetime.now() - start_time).total_seconds()
        self._print_summary(total_duration)

        return self.results

    def _print_summary(self, total_duration: float):
        """Özet yazdır"""
        print(f"\n{'='*70}")
        print("ÖZET")
        print(f"{'='*70}")

        success_count = sum(1 for r in self.results if r['status'] == 'success')
        error_count = sum(1 for r in self.results if r['status'] == 'error')

        print(f"Toplam dosya: {len(self.results)}")
        print(f"Başarılı: {success_count}")
        print(f"Hatalı: {error_count}")
        print(f"Toplam süre: {total_duration:.1f}s")

        if success_count > 0:
            avg_duration = sum(r['duration'] for r in self.results if r['status'] == 'success') / success_count
            print(f"Ortalama süre: {avg_duration:.1f}s")

        # Hataları listele
        if error_count > 0:
            print(f"\nHatalı dosyalar:")
            for result in self.results:
                if result['status'] == 'error':
                    print(f"  ✗ {Path(result['input_file']).name}: {result['message']}")

        print(f"{'='*70}\n")

    def save_results(self, output_file: Union[str, Path]):
        """
        Sonuçları dosyaya kaydet

        Args:
            output_file: Çıktı dosyası (CSV veya JSON)
        """
        import pandas as pd
        import json

        output_file = Path(output_file)

        if output_file.suffix == '.csv':
            # CSV
            df = pd.DataFrame(self.results)
            df.to_csv(output_file, index=False, encoding='utf-8')
        elif output_file.suffix == '.json':
            # JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {output_file.suffix}")

        print(f"✓ Sonuçlar kaydedildi: {output_file}")


class ComparisonReportGenerator:
    """Karşılaştırmalı rapor oluşturucu"""

    def __init__(self, config: Dict = None, language: str = 'tr'):
        """
        Args:
            config: Rapor konfigürasyonu
            language: Dil
        """
        self.config = config
        self.language = language

    def compare_tests(
        self,
        test_files: List[Union[str, Path]],
        test_names: Optional[List[str]] = None,
        output_path: Union[str, Path] = None,
        output_format: str = 'pdf'
    ) -> Path:
        """
        Birden fazla testi karşılaştır ve rapor oluştur

        Args:
            test_files: Test dosyaları
            test_names: Test isimleri (opsiyonel)
            output_path: Çıktı yolu
            output_format: Çıktı formatı

        Returns:
            Path: Oluşturulan rapor yolu
        """
        from .data_reader import TestDataReader
        from .statistics import StatisticsAnalyzer
        from .chart_generator import ChartGenerator
        from .pdf_generator import PDFGenerator
        from .word_generator import WordGenerator
        from .config import ReportConfig

        print(f"\n{'='*70}")
        print("KARŞILAŞTIRMALI RAPOR")
        print(f"{'='*70}")
        print(f"Test sayısı: {len(test_files)}")

        # Konfigürasyon
        config = ReportConfig(self.config or {})
        config.ensure_dirs()

        # Test verilerini oku
        datasets = {}
        for i, file_path in enumerate(test_files):
            reader = TestDataReader()
            data = reader.read_sort_test(file_path)

            if test_names and i < len(test_names):
                name = test_names[i]
            else:
                name = f"Test {i+1}"

            datasets[name] = data

        # İstatistikler
        stats_analyzer = StatisticsAnalyzer()
        comparison_stats = stats_analyzer.compare_datasets(datasets, 'Speed')

        # Grafikler
        chart_gen = ChartGenerator(config=config.config.get('charts', {}))
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())

        # Karşılaştırma grafiği
        comparison_chart = chart_gen.multi_test_comparison(
            datasets,
            'Speed',
            title='Hız Karşılaştırması',
            save_path=temp_dir / 'speed_comparison.png'
        )

        # Rapor oluştur
        if output_format == 'pdf':
            pdf_config = config.config.get('pdf', {})
            pdf_config['translations'] = config.translations
            pdf_gen = PDFGenerator(config=pdf_config)

            pdf_gen.add_section_title('Test Karşılaştırması')
            pdf_gen.add_statistics_table(comparison_stats.to_dict('index'))
            pdf_gen.add_image(comparison_chart, title='Hız Karşılaştırması')

            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = config.config['REPORTS_DIR'] / f"comparison_{timestamp}.pdf"

            output_path = pdf_gen.build(output_path)

        elif output_format in ['word', 'docx']:
            word_config = config.config.get('word', {})
            word_config['translations'] = config.translations
            word_gen = WordGenerator(config=word_config)

            word_gen.add_section_title('Test Karşılaştırması')
            word_gen.add_statistics_table(comparison_stats.to_dict('index'))
            word_gen.add_image(comparison_chart, title='Hız Karşılaştırması')

            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = config.config['REPORTS_DIR'] / f"comparison_{timestamp}.docx"

            output_path = word_gen.save(output_path)

        print(f"✓ Karşılaştırmalı rapor oluşturuldu: {output_path}")
        return output_path
