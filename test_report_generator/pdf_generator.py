"""
PDF rapor oluşturma modülü
ReportLab kullanarak profesyonel PDF raporları oluşturur
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import io


class PDFGenerator:
    """PDF rapor oluşturucu sınıfı"""

    def __init__(self, config: Dict = None):
        """
        Args:
            config: PDF konfigürasyonu
        """
        self.config = config or {}
        self.translations = self.config.get('translations', {})
        self.story = []
        self.styles = self._setup_styles()

    def _setup_styles(self) -> Dict:
        """Metin stillerini ayarla"""
        styles = getSampleStyleSheet()

        # Başlık stili
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Alt başlık
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Normal metin
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Küçük başlık
        styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#FF6600'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))

        return styles

    def create_cover_page(
        self,
        title: str,
        test_info: Dict,
        logo_path: Optional[Path] = None
    ):
        """
        Kapak sayfası oluştur

        Args:
            title: Rapor başlığı
            test_info: Test bilgileri
            logo_path: Logo dosya yolu
        """
        # Logo
        if logo_path and Path(logo_path).exists():
            try:
                img = Image(str(logo_path), width=6*cm, height=3*cm)
                img.hAlign = 'CENTER'
                self.story.append(img)
                self.story.append(Spacer(1, 2*cm))
            except:
                pass

        # Başlık
        title_para = Paragraph(title, self.styles['CustomTitle'])
        self.story.append(title_para)
        self.story.append(Spacer(1, 1*cm))

        # Test bilgileri
        test_type = test_info.get('test_type', 'N/A')
        test_date = test_info.get('test_date', datetime.now().strftime('%Y-%m-%d'))
        vehicle = test_info.get('vehicle_type', 'N/A')

        info_data = [
            [self.translate('test_type'), test_type],
            [self.translate('test_date'), test_date],
            [self.translate('vehicle'), vehicle],
        ]

        info_table = Table(info_data, colWidths=[7*cm, 7*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        self.story.append(info_table)
        self.story.append(Spacer(1, 2*cm))

        # Rapor tarihi
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        date_para = Paragraph(
            f"{self.translate('generated_on')}: {report_date}",
            self.styles['CustomBody']
        )
        self.story.append(date_para)

        self.story.append(PageBreak())

    def add_section_title(self, title: str):
        """Bölüm başlığı ekle"""
        title_para = Paragraph(title, self.styles['CustomHeading'])
        self.story.append(title_para)

    def add_subsection_title(self, title: str):
        """Alt bölüm başlığı ekle"""
        title_para = Paragraph(title, self.styles['CustomSubheading'])
        self.story.append(title_para)

    def add_paragraph(self, text: str):
        """Paragraf ekle"""
        para = Paragraph(text, self.styles['CustomBody'])
        self.story.append(para)
        self.story.append(Spacer(1, 0.3*cm))

    def add_statistics_table(
        self,
        stats_data: Dict[str, Dict],
        title: Optional[str] = None
    ):
        """
        İstatistik tablosu ekle

        Args:
            stats_data: İstatistik verileri {metrik: {stat: value}}
            title: Tablo başlığı
        """
        if title:
            self.add_subsection_title(title)

        # Tablo verisini hazırla
        headers = [self.translate('parameter')]
        if stats_data:
            first_key = list(stats_data.keys())[0]
            stat_keys = list(stats_data[first_key].keys())
            headers.extend([self.translate(k) if k in ['mean', 'min', 'max', 'std', 'median']
                           else k.capitalize() for k in stat_keys])

        table_data = [headers]

        for param, stats in stats_data.items():
            row = [param]
            row.extend([f"{v:.2f}" if isinstance(v, (int, float)) else str(v)
                       for v in stats.values()])
            table_data.append(row)

        # Tablo oluştur
        col_widths = [4*cm] + [3*cm] * (len(headers) - 1)
        table = Table(table_data, colWidths=col_widths)

        # Tablo stili
        table.setStyle(TableStyle([
            # Başlık satırı
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Veri satırları
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),

            # Çerçeve
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#003366')),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_comparison_table(
        self,
        comparison_data: List[Dict],
        columns: List[str],
        title: Optional[str] = None
    ):
        """
        Karşılaştırma tablosu ekle

        Args:
            comparison_data: Karşılaştırma verileri
            columns: Sütun isimleri
            title: Tablo başlığı
        """
        if title:
            self.add_subsection_title(title)

        # Başlık satırı
        headers = [self.translate(col) for col in columns]
        table_data = [headers]

        # Veri satırları
        for row_dict in comparison_data:
            row = [str(row_dict.get(col, '-')) for col in columns]
            table_data.append(row)

        # Tablo oluştur
        col_width = 15*cm / len(columns)
        table = Table(table_data, colWidths=[col_width] * len(columns))

        # Tablo stili
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6600')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3E6')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FF6600')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_requirement_check_table(
        self,
        check_results: List[Dict],
        title: Optional[str] = None
    ):
        """
        Gereksinim kontrolü tablosu ekle

        Args:
            check_results: Kontrol sonuçları
            title: Tablo başlığı
        """
        if title:
            self.add_subsection_title(title)

        # Başlık satırı
        headers = [
            self.translate('parameter'),
            self.translate('requirement'),
            self.translate('actual'),
            self.translate('status')
        ]
        table_data = [headers]

        # Veri satırları
        for result in check_results:
            param = result.get('parameter', '-')
            req = result.get('requirement', '-')
            actual = result.get('actual', '-')
            status = result.get('status', 'UNKNOWN')

            # Format
            if isinstance(req, (int, float)):
                req = f"{req:.2f}"
            if isinstance(actual, (int, float)):
                actual = f"{actual:.2f}"

            row = [param, str(req), str(actual), self.translate(status.lower())]
            table_data.append(row)

        # Tablo oluştur
        table = Table(table_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm])

        # Tablo stili - durum sütunu renklendirme
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#003366')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]

        # Durum sütununa göre renklendirme
        for i, result in enumerate(check_results, start=1):
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                style_commands.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#00AA44')))
                style_commands.append(('TEXTCOLOR', (3, i), (3, i), colors.whitesmoke))
            elif status == 'FAIL':
                style_commands.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#DD0000')))
                style_commands.append(('TEXTCOLOR', (3, i), (3, i), colors.whitesmoke))

        table.setStyle(TableStyle(style_commands))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_image(
        self,
        image_path: Path,
        width: float = 15*cm,
        title: Optional[str] = None
    ):
        """
        Görsel ekle

        Args:
            image_path: Görsel dosya yolu
            width: Genişlik
            title: Görsel başlığı
        """
        if title:
            self.add_paragraph(f"<b>{title}</b>")

        try:
            # Aspect ratio'yu koru
            img = Image(str(image_path), width=width)
            self.story.append(img)
            self.story.append(Spacer(1, 0.5*cm))
        except Exception as e:
            self.add_paragraph(f"[Görsel yüklenemedi: {e}]")

    def add_page_break(self):
        """Sayfa sonu ekle"""
        self.story.append(PageBreak())

    def translate(self, key: str) -> str:
        """Metni çevir"""
        return self.translations.get(key, key.replace('_', ' ').title())

    def build(self, output_path: Path, test_info: Dict = None):
        """
        PDF'i oluştur ve kaydet

        Args:
            output_path: Çıktı dosya yolu
            test_info: Test bilgileri (header/footer için)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # PDF belgesi oluştur
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )

        # Header/Footer fonksiyonu
        def add_page_number(canvas_obj, doc_obj):
            canvas_obj.saveState()

            # Footer - sayfa numarası
            page_num = canvas_obj.getPageNumber()
            text = f"{self.translate('page')} {page_num}"
            canvas_obj.setFont('Helvetica', 9)
            canvas_obj.drawCentredString(A4[0] / 2, 1.5*cm, text)

            # Header - şirket adı ve test tipi
            if test_info:
                company = self.config.get('company_name', 'OTOKAR')
                test_type = test_info.get('test_type', '')
                canvas_obj.drawString(2*cm, A4[1] - 1.5*cm, company)
                canvas_obj.drawRightString(A4[0] - 2*cm, A4[1] - 1.5*cm, test_type)

            canvas_obj.restoreState()

        # PDF'i oluştur
        doc.build(self.story, onFirstPage=add_page_number, onLaterPages=add_page_number)
        print(f"✓ PDF raporu oluşturuldu: {output_path}")

        return output_path
