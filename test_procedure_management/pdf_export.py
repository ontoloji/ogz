"""
PDF Export Module - Generate PDF reports for test procedures and results
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


class PDFExporter:
    """PDF export utility for test procedures and results"""

    def __init__(self, filename, title="Test Report"):
        """Initialize PDF exporter"""
        self.filename = filename
        self.title = title
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        self.styles = getSampleStyleSheet()
        self.story = []

        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        ))

    def add_title(self, title):
        """Add title to document"""
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 12))

    def add_heading(self, text):
        """Add heading"""
        self.story.append(Paragraph(text, self.styles['CustomHeading']))

    def add_paragraph(self, text):
        """Add paragraph"""
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 6))

    def add_spacer(self, height=12):
        """Add vertical space"""
        self.story.append(Spacer(1, height))

    def add_table(self, data, col_widths=None, header=True):
        """Add table to document"""
        table = Table(data, colWidths=col_widths)

        # Style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])

        if not header:
            style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])

        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 12))

    def add_page_break(self):
        """Add page break"""
        self.story.append(PageBreak())

    def build(self):
        """Build and save PDF"""
        self.doc.build(self.story)


def export_procedure_pdf(procedure, language='en', filename=None):
    """Export test procedure to PDF"""

    if filename is None:
        filename = f"procedure_{procedure.procedure_code}_{datetime.now().strftime('%Y%m%d')}.pdf"

    # Get localized data
    title = procedure.title_tr if language == 'tr' else procedure.title_en
    purpose = procedure.purpose_tr if language == 'tr' else procedure.purpose_en
    steps = procedure.steps_tr if language == 'tr' else procedure.steps_en
    criteria = procedure.acceptance_criteria_tr if language == 'tr' else procedure.acceptance_criteria_en

    # Labels
    labels = {
        'tr': {
            'procedure': 'Test Prosedürü',
            'code': 'Kod',
            'level': 'Seviye',
            'category': 'Kategori',
            'purpose': 'Amaç',
            'steps': 'Adımlar',
            'step': 'Adım',
            'description': 'Açıklama',
            'expected': 'Beklenen Sonuç',
            'criteria': 'Kabul Kriterleri',
            'equipment': 'Gerekli Ekipman',
            'regulations': 'ECE Regülasyonları',
            'duration': 'Tahmini Süre',
            'minutes': 'dakika',
            'generated': 'Oluşturulma Tarihi'
        },
        'en': {
            'procedure': 'Test Procedure',
            'code': 'Code',
            'level': 'Level',
            'category': 'Category',
            'purpose': 'Purpose',
            'steps': 'Steps',
            'step': 'Step',
            'description': 'Description',
            'expected': 'Expected Result',
            'criteria': 'Acceptance Criteria',
            'equipment': 'Required Equipment',
            'regulations': 'ECE Regulations',
            'duration': 'Estimated Duration',
            'minutes': 'minutes',
            'generated': 'Generated On'
        }
    }

    label = labels.get(language, labels['en'])

    # Create PDF
    pdf = PDFExporter(filename, title=title)

    # Title
    pdf.add_title(f"{label['procedure']}: {procedure.procedure_code}")

    # Header info
    pdf.add_heading(title)

    # Basic info table
    basic_info = [
        [label['code'], procedure.procedure_code],
        [label['level'], procedure.level],
        [label['category'], procedure.category],
        [label['duration'], f"{procedure.estimated_duration} {label['minutes']}" if procedure.estimated_duration else 'N/A'],
    ]

    pdf.add_table(basic_info, col_widths=[100, 300], header=False)
    pdf.add_spacer(20)

    # Purpose
    pdf.add_heading(label['purpose'])
    pdf.add_paragraph(purpose)
    pdf.add_spacer(20)

    # Steps
    pdf.add_heading(label['steps'])

    steps_data = [[label['step'], label['description'], label['expected']]]
    for step in steps:
        steps_data.append([
            str(step['step']),
            step['description'],
            step.get('expected', '')
        ])

    pdf.add_table(steps_data, col_widths=[40, 250, 150])
    pdf.add_spacer(20)

    # Acceptance Criteria
    pdf.add_heading(label['criteria'])
    pdf.add_paragraph(criteria)
    pdf.add_spacer(20)

    # Required Equipment
    if procedure.required_equipment:
        pdf.add_heading(label['equipment'])
        for equipment in procedure.required_equipment:
            pdf.add_paragraph(f"• {equipment}")
        pdf.add_spacer(20)

    # ECE Regulations
    if procedure.ece_regulations:
        pdf.add_heading(label['regulations'])
        for regulation in procedure.ece_regulations:
            pdf.add_paragraph(f"• {regulation}")
        pdf.add_spacer(20)

    # Footer
    pdf.add_spacer(30)
    pdf.add_paragraph(f"{label['generated']}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Build PDF
    pdf.build()

    return filename


def export_result_pdf(result, language='en', filename=None):
    """Export test result to PDF"""

    if filename is None:
        filename = f"result_{result.procedure.procedure_code}_{result.id}_{datetime.now().strftime('%Y%m%d')}.pdf"

    # Get localized data
    procedure_title = result.procedure.title_tr if language == 'tr' else result.procedure.title_en

    # Labels
    labels = {
        'tr': {
            'report': 'Test Sonucu Raporu',
            'procedure': 'Test Prosedürü',
            'code': 'Kod',
            'date': 'Test Tarihi',
            'operator': 'Operatör',
            'status': 'Durum',
            'duration': 'Süre',
            'minutes': 'dakika',
            'temperature': 'Sıcaklık',
            'humidity': 'Nem',
            'steps': 'Adım Sonuçları',
            'step': 'Adım',
            'result': 'Sonuç',
            'notes': 'Notlar',
            'observations': 'Gözlemler',
            'measurements': 'Ölçümler',
            'generated': 'Oluşturulma Tarihi'
        },
        'en': {
            'report': 'Test Result Report',
            'procedure': 'Test Procedure',
            'code': 'Code',
            'date': 'Test Date',
            'operator': 'Operator',
            'status': 'Status',
            'duration': 'Duration',
            'minutes': 'minutes',
            'temperature': 'Temperature',
            'humidity': 'Humidity',
            'steps': 'Step Results',
            'step': 'Step',
            'result': 'Result',
            'notes': 'Notes',
            'observations': 'Observations',
            'measurements': 'Measurements',
            'generated': 'Generated On'
        }
    }

    label = labels.get(language, labels['en'])

    # Create PDF
    pdf = PDFExporter(filename, title=procedure_title)

    # Title
    pdf.add_title(label['report'])

    # Procedure info
    pdf.add_heading(f"{label['procedure']}: {result.procedure.procedure_code}")
    pdf.add_paragraph(procedure_title)
    pdf.add_spacer(20)

    # Test info table
    test_info = [
        [label['date'], result.test_date.strftime('%Y-%m-%d %H:%M') if result.test_date else 'N/A'],
        [label['operator'], result.operator],
        [label['status'], result.status],
        [label['duration'], f"{result.actual_duration} {label['minutes']}" if result.actual_duration else 'N/A'],
        [label['temperature'], f"{result.temperature}°C" if result.temperature else 'N/A'],
        [label['humidity'], f"{result.humidity}%" if result.humidity else 'N/A'],
    ]

    pdf.add_table(test_info, col_widths=[100, 300], header=False)
    pdf.add_spacer(20)

    # Step results
    if result.step_results:
        pdf.add_heading(label['steps'])

        step_data = [[label['step'], label['result'], label['notes']]]
        for step in result.step_results:
            step_data.append([
                str(step['step']),
                step['status'],
                step.get('notes', '')
            ])

        pdf.add_table(step_data, col_widths=[40, 80, 320])
        pdf.add_spacer(20)

    # Notes
    if result.notes:
        pdf.add_heading(label['notes'])
        pdf.add_paragraph(result.notes)
        pdf.add_spacer(20)

    # Observations
    if result.observations:
        pdf.add_heading(label['observations'])
        pdf.add_paragraph(result.observations)
        pdf.add_spacer(20)

    # Measurements
    if result.measurements:
        pdf.add_heading(label['measurements'])
        measurements_data = [[k, str(v)] for k, v in result.measurements.items()]
        pdf.add_table([['Parameter', 'Value']] + measurements_data, col_widths=[200, 200])
        pdf.add_spacer(20)

    # Footer
    pdf.add_spacer(30)
    pdf.add_paragraph(f"{label['generated']}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Build PDF
    pdf.build()

    return filename
