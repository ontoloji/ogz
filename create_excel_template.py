"""
Excel Şablon Oluşturucu

Bu script batarya test maliyeti hesaplaması için örnek bir Excel şablonu oluşturur.
"""

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    from datetime import datetime

    # Workbook oluştur
    wb = openpyxl.Workbook()

    # ==================== 1. MALİYET HESAPLAMA SAYFA ====================
    ws1 = wb.active
    ws1.title = "Maliyet Hesaplama"

    # Başlık
    ws1['A1'] = 'BATARYA TEST MALİYETİ HESAPLAMA ŞABLONU'
    ws1['A1'].font = Font(size=18, bold=True, color='FFFFFF')
    ws1['A1'].fill = PatternFill(start_color='2196F3', end_color='2196F3', fill_type='solid')
    ws1['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws1.merge_cells('A1:F1')
    ws1.row_dimensions[1].height = 30

    # Tarih
    ws1['A2'] = f'Oluşturulma Tarihi: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    ws1.merge_cells('A2:F2')

    # Boşluk
    row = 4

    # GİRDİ PARAMETRELERİ
    ws1[f'A{row}'] = 'GİRDİ PARAMETRELERİ'
    ws1[f'A{row}'].font = Font(size=14, bold=True)
    ws1[f'A{row}'].fill = PatternFill(start_color='4CAF50', end_color='4CAF50', fill_type='solid')
    ws1[f'A{row}'].font = Font(size=14, bold=True, color='FFFFFF')
    ws1.merge_cells(f'A{row}:C{row}')
    row += 1

    # Parametreler
    params = [
        ('Test Tipi:', 'Ömür Döngüsü Testi', ''),
        ('Bölge:', 'Türkiye', ''),
        ('Para Birimi:', 'TRY', ''),
        ('', '', ''),
        ('Test Süresi (saat):', '1000', 'Varsayılan: 1000'),
        ('Güç Tüketimi (kW):', '2.5', 'Varsayılan: 2.5'),
        ('Personel Sayısı:', '1', 'Varsayılan: 1'),
        ('Batarya Sayısı:', '10', ''),
        ('Ekipman Maliyeti (USD):', '150000', 'Varsayılan: 150000'),
        ('', '', ''),
        ('Dış Kaynak Kullanımı:', 'Hayır', 'Evet/Hayır'),
    ]

    for label, value, note in params:
        ws1[f'A{row}'] = label
        ws1[f'B{row}'] = value
        ws1[f'C{row}'] = note
        if label:
            ws1[f'A{row}'].font = Font(bold=True)
            ws1[f'B{row}'].fill = PatternFill(start_color='FFFFCC', end_color='FFFFCC', fill_type='solid')
        row += 1

    # Boşluk
    row += 2

    # MALİYET DAĞILIMI
    ws1[f'A{row}'] = 'MALİYET DAĞILIMI'
    ws1[f'A{row}'].font = Font(size=14, bold=True, color='FFFFFF')
    ws1[f'A{row}'].fill = PatternFill(start_color='FF9800', end_color='FF9800', fill_type='solid')
    ws1.merge_cells(f'A{row}:D{row}')
    row += 1

    # Başlıklar
    headers = ['Maliyet Kalemi', 'Tutar', 'Para Birimi', 'Yüzde (%)']
    for col, header in enumerate(headers, 1):
        cell = ws1.cell(row=row, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='DDDDDD', end_color='DDDDDD', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
    row += 1

    # Maliyet kalemleri (örnek)
    cost_items = [
        ('İşçilik Maliyeti', 625000, 'TRY', 58.5),
        ('Enerji Maliyeti', 10350, 'TRY', 1.0),
        ('Ekipman Amortismanı', 103500, 'TRY', 9.7),
        ('Bakım Maliyeti', 110900, 'TRY', 10.4),
        ('Tesis Maliyeti', 517500, 'TRY', 48.5),
        ('Kalibrasyon Maliyeti', 1725, 'TRY', 0.2),
        ('Sarf Malzemeleri', 6900, 'TRY', 0.6),
    ]

    start_row = row
    for item, cost, currency, pct in cost_items:
        ws1[f'A{row}'] = item
        ws1[f'B{row}'] = cost
        ws1[f'C{row}'] = currency
        ws1[f'D{row}'] = pct
        row += 1

    # Toplam
    ws1[f'A{row}'] = 'TOPLAM MALİYET'
    ws1[f'B{row}'] = 1067875
    ws1[f'C{row}'] = 'TRY'
    ws1[f'D{row}'] = 100.0
    for col in range(1, 5):
        cell = ws1.cell(row=row, column=col)
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill(start_color='4CAF50', end_color='4CAF50', fill_type='solid')
    row += 1

    # Birim başına
    ws1[f'A{row}'] = 'BİRİM BAŞINA MALİYET'
    ws1[f'B{row}'] = 106787.5
    ws1[f'C{row}'] = 'TRY'
    ws1[f'A{row}'].font = Font(bold=True)
    ws1[f'B{row}'].font = Font(bold=True)
    ws1[f'C{row}'].font = Font(bold=True)

    # Sütun genişlikleri
    ws1.column_dimensions['A'].width = 25
    ws1.column_dimensions['B'].width = 15
    ws1.column_dimensions['C'].width = 15
    ws1.column_dimensions['D'].width = 12
    ws1.column_dimensions['E'].width = 20
    ws1.column_dimensions['F'].width = 20

    # ==================== 2. BÖLGESEL KARŞILAŞTIRMA SAYFA ====================
    ws2 = wb.create_sheet("Bölgesel Karşılaştırma")

    # Başlık
    ws2['A1'] = 'BÖLGESEL MALİYET KARŞILAŞTIRMASI'
    ws2['A1'].font = Font(size=18, bold=True, color='FFFFFF')
    ws2['A1'].fill = PatternFill(start_color='2196F3', end_color='2196F3', fill_type='solid')
    ws2['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws2.merge_cells('A1:F1')
    ws2.row_dimensions[1].height = 30

    row = 3
    ws2[f'A{row}'] = 'Test Tipi: Güvenlik Testi'
    ws2[f'A{row}'].font = Font(bold=True)
    row += 1
    ws2[f'A{row}'] = 'Para Birimi: USD'
    ws2[f'A{row}'].font = Font(bold=True)
    row += 2

    # Tablo başlıkları
    headers = ['Bölge', 'Toplam Maliyet', 'İşçilik', 'Enerji', 'Ekipman', 'Tesis']
    for col, header in enumerate(headers, 1):
        cell = ws2.cell(row=row, column=col)
        cell.value = header
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='FF9800', end_color='FF9800', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
    row += 1

    # Örnek veriler
    regions_data = [
        ('Türkiye', 3240, 1200, 14.4, 160, 720),
        ('Avrupa', 8745, 6240, 36, 320, 1920),
        ('Çin', 2082, 720, 9.6, 160, 480),
        ('Hindistan', 1826, 576, 12, 160, 384)
    ]

    for region, total, labor, energy, equipment, facility in regions_data:
        ws2[f'A{row}'] = region
        ws2[f'B{row}'] = total
        ws2[f'C{row}'] = labor
        ws2[f'D{row}'] = energy
        ws2[f'E{row}'] = equipment
        ws2[f'F{row}'] = facility
        row += 1

    # Sütun genişlikleri
    for col in range(1, 7):
        ws2.column_dimensions[get_column_letter(col)].width = 18

    # ==================== 3. SENARYO KARŞILAŞTIRMA SAYFA ====================
    ws3 = wb.create_sheet("Senaryo Karşılaştırma")

    # Başlık
    ws3['A1'] = 'SENARYO KARŞILAŞTIRMASI: KENDİ TEST vs DIŞ KAYNAK'
    ws3['A1'].font = Font(size=16, bold=True, color='FFFFFF')
    ws3['A1'].fill = PatternFill(start_color='2196F3', end_color='2196F3', fill_type='solid')
    ws3['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws3.merge_cells('A1:D1')
    ws3.row_dimensions[1].height = 30

    row = 3

    # Tablo
    headers = ['Maliyet Kalemi', 'Kendi Test', 'Dış Kaynak', 'Fark']
    for col, header in enumerate(headers, 1):
        cell = ws3.cell(row=row, column=col)
        cell.value = header
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4CAF50', end_color='4CAF50', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
    row += 1

    # Örnek veriler
    scenario_data = [
        ('İşçilik', 6240, 8736, 2496),
        ('Enerji', 36, 50.4, 14.4),
        ('Ekipman', 320, 0, -320),
        ('Bakım', 109.59, 0, -109.59),
        ('Tesis', 1920, 576, -1344),
        ('Kalibrasyon', 120, 168, 48),
        ('Sarf Malzeme', 350, 490, 140),
        ('', '', '', ''),
        ('TOPLAM', 9095.59, 10020.4, 924.81)
    ]

    for item, in_house, outsource, diff in scenario_data:
        ws3[f'A{row}'] = item
        ws3[f'B{row}'] = in_house if isinstance(in_house, str) else in_house
        ws3[f'C{row}'] = outsource if isinstance(outsource, str) else outsource
        ws3[f'D{row}'] = diff if isinstance(diff, str) else diff

        if item == 'TOPLAM':
            for col in range(1, 5):
                cell = ws3.cell(row=row, column=col)
                cell.font = Font(bold=True, size=12)
                cell.fill = PatternFill(start_color='FFE0B2', end_color='FFE0B2', fill_type='solid')
        row += 1

    row += 1
    ws3[f'A{row}'] = 'SONUÇ:'
    ws3[f'A{row}'].font = Font(bold=True, size=12, color='FF0000')
    row += 1
    ws3[f'A{row}'] = '✓ Kendi test 924.81 USD daha avantajlı'
    ws3[f'A{row}'].font = Font(bold=True, color='4CAF50')
    ws3.merge_cells(f'A{row}:D{row}')

    # Sütun genişlikleri
    for col in range(1, 5):
        ws3.column_dimensions[get_column_letter(col)].width = 20

    # ==================== 4. MALİYET VERİLERİ SAYFA ====================
    ws4 = wb.create_sheet("Maliyet Verileri")

    # Başlık
    ws4['A1'] = 'BÖLGESEL MALİYET VERİLERİ'
    ws4['A1'].font = Font(size=16, bold=True, color='FFFFFF')
    ws4['A1'].fill = PatternFill(start_color='2196F3', end_color='2196F3', fill_type='solid')
    ws4['A1'].alignment = Alignment(horizontal='center')
    ws4.merge_cells('A1:E1')

    row = 3

    # Türkiye
    ws4[f'A{row}'] = 'TÜRKİYE'
    ws4[f'A{row}'].font = Font(bold=True, size=12)
    ws4[f'A{row}'].fill = PatternFill(start_color='FFCDD2', end_color='FFCDD2', fill_type='solid')
    ws4.merge_cells(f'A{row}:E{row}')
    row += 1

    turkey_data = [
        ('İşçilik (USD/saat)', 25.0),
        ('Enerji (USD/kWh)', 0.12),
        ('Tesis (USD/saat)', 15.0),
        ('Bakım Oranı (%)', 8.0),
        ('Kalibrasyon (USD/yıl)', 5000),
        ('Sarf Malzeme (USD/test)', 200)
    ]

    for param, value in turkey_data:
        ws4[f'A{row}'] = param
        ws4[f'B{row}'] = value
        row += 1

    row += 1

    # Avrupa
    ws4[f'A{row}'] = 'AVRUPA'
    ws4[f'A{row}'].font = Font(bold=True, size=12)
    ws4[f'A{row}'].fill = PatternFill(start_color='C5CAE9', end_color='C5CAE9', fill_type='solid')
    ws4.merge_cells(f'A{row}:E{row}')
    row += 1

    europe_data = [
        ('İşçilik (USD/saat)', 65.0),
        ('Enerji (USD/kWh)', 0.25),
        ('Tesis (USD/saat)', 40.0),
        ('Bakım Oranı (%)', 10.0),
        ('Kalibrasyon (USD/yıl)', 12000),
        ('Sarf Malzeme (USD/test)', 350)
    ]

    for param, value in europe_data:
        ws4[f'A{row}'] = param
        ws4[f'B{row}'] = value
        row += 1

    # Sütun genişlikleri
    ws4.column_dimensions['A'].width = 30
    ws4.column_dimensions['B'].width = 15

    # ==================== 5. FORMÜLLER SAYFA ====================
    ws5 = wb.create_sheet("Formüller")

    # Başlık
    ws5['A1'] = 'MALİYET HESAPLAMA FORMÜLLERİ'
    ws5['A1'].font = Font(size=16, bold=True, color='FFFFFF')
    ws5['A1'].fill = PatternFill(start_color='2196F3', end_color='2196F3', fill_type='solid')
    ws5['A1'].alignment = Alignment(horizontal='center')
    ws5.merge_cells('A1:B1')

    row = 3

    formulas = [
        ('1. İşçilik Maliyeti', 'Test Süresi × Personel Sayısı × Saat Ücreti'),
        ('', ''),
        ('2. Enerji Maliyeti', 'Test Süresi × Güç Tüketimi × Birim Enerji Fiyatı'),
        ('', ''),
        ('3. Ekipman Amortismanı', '(Ekipman Maliyeti / Kullanım Ömrü) × Test Süresi'),
        ('', ''),
        ('4. Bakım Maliyeti', 'Ekipman Maliyeti × Bakım Oranı × (Test Süresi / 8760)'),
        ('', ''),
        ('5. Tesis Maliyeti', 'Saatlik Tesis Maliyeti × Test Süresi'),
        ('', ''),
        ('6. Kalibrasyon', 'Yıllık Kalibrasyon / Yıllık Test Sayısı'),
        ('', ''),
        ('7. Sarf Malzeme', 'Sabit Test Başına Maliyet'),
        ('', ''),
        ('8. TOPLAM MALİYET', '∑(Tüm Maliyet Bileşenleri)'),
        ('', ''),
        ('9. Birim Başına', 'Toplam Maliyet / Batarya Sayısı'),
    ]

    for label, formula in formulas:
        ws5[f'A{row}'] = label
        ws5[f'B{row}'] = formula
        if label and label[0].isdigit():
            ws5[f'A{row}'].font = Font(bold=True, size=11)
            ws5[f'A{row}'].fill = PatternFill(start_color='E3F2FD', end_color='E3F2FD', fill_type='solid')
        row += 1

    # Sütun genişlikleri
    ws5.column_dimensions['A'].width = 25
    ws5.column_dimensions['B'].width = 60

    # Dosyayı kaydet
    filename = 'batarya_test_maliyet_sablonu.xlsx'
    wb.save(filename)

    print(f"✓ Excel şablonu başarıyla oluşturuldu: {filename}")
    print(f"\nŞablon içeriği:")
    print(f"  - Maliyet Hesaplama sayfası")
    print(f"  - Bölgesel Karşılaştırma sayfası")
    print(f"  - Senaryo Karşılaştırma sayfası")
    print(f"  - Maliyet Verileri sayfası")
    print(f"  - Formüller sayfası")
    print(f"\nŞablonu açarak maliyet hesaplamaları yapabilirsiniz.")

except ImportError:
    print("❌ HATA: openpyxl kütüphanesi gerekli!")
    print("Kurulum: pip install openpyxl")
except Exception as e:
    print(f"❌ HATA: {str(e)}")
