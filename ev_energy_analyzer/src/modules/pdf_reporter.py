"""
PDF Rapor Oluşturma Modülü
Türkçe destekli, şirket logolu, profesyonel görünümlü PDF raporları oluşturur
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                Spacer, Image, PageBreak, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import get_logo_path, get_output_path, format_turkish_number

class PDFReporter:
    """PDF rapor oluşturucu"""

    def __init__(self, output_filename=None):
        """
        Args:
            output_filename (str): Çıktı dosyası adı
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"enerji_raporu_{timestamp}.pdf"

        self.output_path = get_output_path(output_filename)
        self.logo_path = get_logo_path()

        # PDF dökümanı
        self.doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Stil tanımlamaları
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

        # İçerik elemanları
        self.story = []

    def _create_custom_styles(self):
        """Özel stiller oluşturur"""
        # Başlık stili
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Alt başlık stili
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Normal metin stili
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            fontName='Helvetica'
        ))

        # Küçük metin stili
        self.styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica'
        ))

    def add_header(self, title, subtitle=None):
        """
        Rapor başlığı ekler

        Args:
            title (str): Ana başlık
            subtitle (str): Alt başlık
        """
        # Logo varsa ekle
        if self.logo_path:
            try:
                img = Image(self.logo_path, width=4*cm, height=2*cm)
                img.hAlign = 'CENTER'
                self.story.append(img)
                self.story.append(Spacer(1, 0.5*cm))
            except:
                pass  # Logo yüklenemezse devam et

        # Ana başlık
        self.story.append(Paragraph(title, self.styles['CustomTitle']))

        # Alt başlık
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['CustomBody']))

        # Tarih
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.story.append(Paragraph(f"Rapor Tarihi: {date_str}", self.styles['CustomSmall']))
        self.story.append(Spacer(1, 0.5*cm))

        # Çizgi
        self._add_line()

    def _add_line(self):
        """Yatay çizgi ekler"""
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#CCCCCC')),
        ]))
        self.story.append(line_table)
        self.story.append(Spacer(1, 0.3*cm))

    def add_section(self, title):
        """
        Bölüm başlığı ekler

        Args:
            title (str): Bölüm başlığı
        """
        self.story.append(Spacer(1, 0.3*cm))
        self.story.append(Paragraph(title, self.styles['CustomHeading']))
        self.story.append(Spacer(1, 0.2*cm))

    def add_paragraph(self, text):
        """
        Paragraf ekler

        Args:
            text (str): Paragraf metni
        """
        self.story.append(Paragraph(text, self.styles['CustomBody']))

    def add_table(self, data, col_widths=None, header_color='#2E86AB'):
        """
        Tablo ekler

        Args:
            data (list): Tablo verileri
            col_widths (list): Sütun genişlikleri
            header_color (str): Başlık rengi
        """
        if not data:
            return

        # Varsayılan sütun genişlikleri
        if col_widths is None:
            num_cols = len(data[0])
            col_widths = [17*cm / num_cols] * num_cols

        # Tablo oluştur
        table = Table(data, colWidths=col_widths)

        # Tablo stili
        style = TableStyle([
            # Başlık satırı
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Veri satırları
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Çizgiler
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Alternatif satır renkleri
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ])

        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*cm))

    def add_image(self, image_path, width=15*cm, height=8*cm):
        """
        Görsel ekler

        Args:
            image_path (str): Görsel dosyası yolu
            width: Genişlik
            height: Yükseklik
        """
        if not Path(image_path).exists():
            return

        try:
            img = Image(image_path, width=width, height=height)
            img.hAlign = 'CENTER'
            self.story.append(img)
            self.story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            print(f"Görsel eklenemedi: {e}")

    def add_test_info(self, test_info):
        """
        Test bilgilerini ekler

        Args:
            test_info (dict): Test bilgileri
        """
        self.add_section("Test Bilgileri")

        data = [['Parametre', 'Değer']]

        for key, value in test_info.items():
            # Anahtarı formatla
            key_formatted = key.replace('_', ' ').title()
            data.append([key_formatted, str(value)])

        self.add_table(data, col_widths=[8*cm, 9*cm])

    def add_sort_results(self, sort_results):
        """
        SORT analiz sonuçlarını ekler

        Args:
            sort_results (dict): SORT sonuçları
        """
        self.add_section("UITP SORT Test Döngüsü Analizi")

        # Döngü bilgileri
        data = [
            ['Parametre', 'Standart', 'Gerçek', 'Uyumluluk'],
            [
                'Maksimum Hız (km/h)',
                format_turkish_number(sort_results['sort_max_speed'], 1),
                format_turkish_number(sort_results['max_speed'], 1),
                f"%{format_turkish_number(sort_results['speed_compliance'], 1)}"
            ],
            [
                'Mesafe (km)',
                format_turkish_number(sort_results['sort_distance'], 2),
                format_turkish_number(sort_results['total_distance'], 2),
                f"%{format_turkish_number(sort_results['distance_compliance'], 1)}"
            ],
            [
                'Süre (saniye)',
                format_turkish_number(sort_results['sort_duration'], 0),
                format_turkish_number(sort_results['total_time'], 0),
                f"%{format_turkish_number(sort_results['duration_compliance'], 1)}"
            ]
        ]

        self.add_table(data, col_widths=[6*cm, 3.5*cm, 3.5*cm, 4*cm])

        # Temel metrikler
        self.add_paragraph(f"<b>Döngü Tipi:</b> {sort_results['cycle_name']}")
        self.add_paragraph(f"<b>Enerji Tüketimi:</b> {format_turkish_number(sort_results['energy_per_100km'], 2)} kWh/100km")
        self.add_paragraph(f"<b>Ortalama Hız:</b> {format_turkish_number(sort_results['avg_speed'], 1)} km/h")
        self.add_paragraph(f"<b>Ortalama Güç:</b> {format_turkish_number(sort_results['avg_power'], 1)} kW")

    def add_energy_results(self, energy_results):
        """
        Enerji analiz sonuçlarını ekler

        Args:
            energy_results (dict): Enerji sonuçları
        """
        self.add_section("Enerji Tüketimi Analizi")

        cons = energy_results['consumption']

        data = [
            ['Metrik', 'Değer'],
            ['Toplam Enerji', f"{format_turkish_number(cons['total_energy'], 3)} kWh"],
            ['Toplam Mesafe', f"{format_turkish_number(cons['total_distance'], 2)} km"],
            ['Tüketim (100km)', f"{format_turkish_number(cons['consumption_per_100km'], 2)} kWh/100km"],
            ['Tüketim (km)', f"{format_turkish_number(cons['consumption_per_km'], 4)} kWh/km"]
        ]

        self.add_table(data, col_widths=[10*cm, 7*cm])

        # Regeneratif frenleme
        if energy_results['regenerative_braking'].get('available'):
            self.add_section("Regeneratif Frenleme Analizi")

            regen = energy_results['regenerative_braking']

            data = [
                ['Metrik', 'Değer'],
                ['Toplam Motor Enerjisi', f"{format_turkish_number(regen['total_motor_energy'], 3)} kWh"],
                ['Geri Kazanılan Enerji', f"{format_turkish_number(regen['total_regen_energy'], 3)} kWh"],
                ['Regen Verimliliği', f"%{format_turkish_number(regen['regen_efficiency'], 1)}"],
                ['Ortalama Regen Gücü', f"{format_turkish_number(regen['avg_regen_power'], 1)} W"],
                ['Maksimum Regen Gücü', f"{format_turkish_number(regen['max_regen_power'], 1)} W"],
                ['Regen Olayları', f"{int(regen['regen_events'])}"]
            ]

            self.add_table(data, col_widths=[10*cm, 7*cm])

        # Sıcaklık etkisi
        if energy_results['temperature'].get('available'):
            self.add_section("Sıcaklık Etkisi Analizi")

            temp = energy_results['temperature']

            data = [
                ['Metrik', 'Değer'],
                ['Ortalama Sıcaklık', f"{format_turkish_number(temp['avg_temperature'], 1)}°C"],
                ['Sıcaklık Aralığı', temp['temperature_range']],
                ['Sıcaklık Etkisi Faktörü', f"x{format_turkish_number(temp['temp_effect_factor'], 2)}"],
                ['Gerçek Tüketim', f"{format_turkish_number(temp['actual_consumption'], 2)} kWh/100km"],
                ['Normalize Tüketim', f"{format_turkish_number(temp['normalized_consumption'], 2)} kWh/100km"],
                ['Tüketim Artışı', f"%{format_turkish_number(temp['consumption_increase'], 1)}"]
            ]

            self.add_table(data, col_widths=[10*cm, 7*cm])

    def add_range_estimates(self, range_data):
        """
        Menzil tahminlerini ekler

        Args:
            range_data (dict): Menzil verileri
        """
        self.add_section("Menzil Tahminleri")

        data = [['Batarya (kWh)', 'Teorik (km)', 'Gerçekçi (km)', 'Minimum (km)']]

        for capacity, ranges in sorted(range_data.items()):
            data.append([
                str(capacity),
                format_turkish_number(ranges['theoretical'], 1),
                format_turkish_number(ranges['realistic'], 1),
                format_turkish_number(ranges['minimum'], 1)
            ])

        self.add_table(data, col_widths=[4*cm, 4.3*cm, 4.3*cm, 4.4*cm])

    def add_charts(self, chart_paths):
        """
        Grafikleri ekler

        Args:
            chart_paths (dict): Grafik dosya yolları
        """
        self.add_section("Grafikler")

        chart_order = ['speed', 'power', 'energy', 'soc', 'temperature', 'phase', 'range']

        for chart_key in chart_order:
            if chart_key in chart_paths:
                self.add_image(chart_paths[chart_key])

                # Her 2 grafikten sonra sayfa sonu
                if chart_key in ['power', 'soc']:
                    self.story.append(PageBreak())

    def generate(self):
        """
        PDF'yi oluşturur

        Returns:
            str: Oluşturulan dosya yolu
        """
        try:
            self.doc.build(self.story)
            return self.output_path
        except Exception as e:
            print(f"PDF oluşturma hatası: {e}")
            return None


def create_full_report(test_info, sort_results, energy_results, chart_paths, output_filename=None):
    """
    Tam rapor oluşturur (kolaylık fonksiyonu)

    Args:
        test_info (dict): Test bilgileri
        sort_results (dict): SORT sonuçları
        energy_results (dict): Enerji sonuçları
        chart_paths (dict): Grafik yolları
        output_filename (str): Çıktı dosyası

    Returns:
        str: PDF dosya yolu
    """
    reporter = PDFReporter(output_filename)

    # Başlık
    reporter.add_header(
        "Elektrikli Araç Enerji Tüketimi Analiz Raporu",
        "UITP SORT Test Döngüsü"
    )

    # Test bilgileri
    reporter.add_test_info(test_info)

    # SORT sonuçları
    reporter.add_sort_results(sort_results)

    # Sayfa sonu
    reporter.story.append(PageBreak())

    # Enerji sonuçları
    reporter.add_energy_results(energy_results)

    # Menzil tahminleri
    if 'range' in energy_results:
        reporter.add_range_estimates(energy_results['range'])

    # Sayfa sonu
    reporter.story.append(PageBreak())

    # Grafikler
    reporter.add_charts(chart_paths)

    # PDF oluştur
    return reporter.generate()


if __name__ == "__main__":
    print("PDF Reporter Modülü Test")
    print("=" * 60)
    print(f"Çıktı dizini: {Path(__file__).parent.parent.parent / 'output'}")
