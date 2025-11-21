#!/usr/bin/env python3
"""
Test Rapor Oluşturucu - Komut Satırı Arayüzü
"""

import argparse
import sys
from pathlib import Path

from test_report_generator import ReportBuilder, BatchReportProcessor


def main():
    parser = argparse.ArgumentParser(
        description='Test sonuçlarından otomatik rapor oluştur',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Tek dosya için PDF raporu
  python report_cli.py single test_data.csv -o report.pdf

  # Tek dosya için Word raporu
  python report_cli.py single test_data.csv -f word -o report.docx

  # Dizindeki tüm dosyalar için rapor (PDF)
  python report_cli.py batch data/ -o reports/

  # Paralel toplu işleme
  python report_cli.py batch data/ -o reports/ --parallel --workers 4

  # İngilizce rapor
  python report_cli.py single test_data.csv --language en

  # Grafik ve gereksinim kontrolü olmadan
  python report_cli.py single test_data.csv --no-charts --no-requirements
        """
    )

    # Alt komutlar
    subparsers = parser.add_subparsers(dest='command', help='Komutlar')

    # Single command
    single_parser = subparsers.add_parser('single', help='Tek dosya için rapor oluştur')
    single_parser.add_argument('input', type=str, help='Test verisi dosyası (CSV)')
    single_parser.add_argument('-o', '--output', type=str, help='Çıktı dosyası')
    single_parser.add_argument('-f', '--format', choices=['pdf', 'word'], default='pdf',
                               help='Çıktı formatı (varsayılan: pdf)')
    single_parser.add_argument('-l', '--language', choices=['tr', 'en'], default='tr',
                               help='Dil (varsayılan: tr)')
    single_parser.add_argument('--no-charts', action='store_true',
                               help='Grafikleri dahil etme')
    single_parser.add_argument('--no-requirements', action='store_true',
                               help='Gereksinim kontrolünü dahil etme')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Toplu rapor oluştur')
    batch_parser.add_argument('input_dir', type=str, help='Girdi dizini')
    batch_parser.add_argument('-o', '--output-dir', type=str, required=True,
                             help='Çıktı dizini')
    batch_parser.add_argument('-p', '--pattern', type=str, default='*.csv',
                             help='Dosya deseni (varsayılan: *.csv)')
    batch_parser.add_argument('-f', '--format', choices=['pdf', 'word'], default='pdf',
                             help='Çıktı formatı (varsayılan: pdf)')
    batch_parser.add_argument('-l', '--language', choices=['tr', 'en'], default='tr',
                             help='Dil (varsayılan: tr)')
    batch_parser.add_argument('--parallel', action='store_true',
                             help='Paralel işleme kullan')
    batch_parser.add_argument('--workers', type=int, default=4,
                             help='Paralel işçi sayısı (varsayılan: 4)')
    batch_parser.add_argument('--save-results', type=str,
                             help='Sonuçları kaydet (CSV veya JSON)')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Testleri karşılaştır')
    compare_parser.add_argument('files', nargs='+', type=str,
                               help='Karşılaştırılacak dosyalar')
    compare_parser.add_argument('-o', '--output', type=str,
                               help='Çıktı dosyası')
    compare_parser.add_argument('-f', '--format', choices=['pdf', 'word'], default='pdf',
                               help='Çıktı formatı (varsayılan: pdf)')
    compare_parser.add_argument('-l', '--language', choices=['tr', 'en'], default='tr',
                               help='Dil (varsayılan: tr)')
    compare_parser.add_argument('--names', nargs='+', type=str,
                               help='Test isimleri')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'single':
            # Tek dosya
            print(f"Rapor oluşturuluyor: {args.input}")

            builder = ReportBuilder(language=args.language)
            output_path = builder.generate_full_report(
                args.input,
                output_format=args.format,
                output_path=args.output,
                include_charts=not args.no_charts,
                include_requirements=not args.no_requirements
            )

            print(f"\n✓ Rapor oluşturuldu: {output_path}")

        elif args.command == 'batch':
            # Toplu işleme
            processor = BatchReportProcessor(language=args.language)
            results = processor.process_directory(
                args.input_dir,
                args.output_dir,
                pattern=args.pattern,
                output_format=args.format,
                parallel=args.parallel,
                max_workers=args.workers
            )

            # Sonuçları kaydet
            if args.save_results:
                processor.save_results(args.save_results)

        elif args.command == 'compare':
            # Karşılaştırma
            from test_report_generator.batch_processor import ComparisonReportGenerator

            comparator = ComparisonReportGenerator(language=args.language)
            output_path = comparator.compare_tests(
                args.files,
                test_names=args.names,
                output_path=args.output,
                output_format=args.format
            )

            print(f"\n✓ Karşılaştırma raporu oluşturuldu: {output_path}")

    except Exception as e:
        print(f"\n✗ HATA: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
