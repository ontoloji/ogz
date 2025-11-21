# Test Report Generator

Test sonuçlarından otomatik olarak profesyonel PDF ve Word raporları oluşturan Python modülü.

## Özellikler

### 📊 Veri İşleme
- **Excel ve CSV desteği**: Farklı formatlarda test verisi okuma
- **Otomatik veri doğrulama**: Sütun kontrolü ve veri tutarlılığı
- **Metadata desteği**: JSON formatında test meta verileri

### 📈 İstatistiksel Analiz
- Temel istatistikler (ortalama, min, max, standart sapma, medyan)
- Güven aralığı hesaplama
- Aykırı değer tespiti
- Korelasyon analizi
- Normallik testleri
- Özel enerji tüketimi hesaplamaları

### 📉 Grafik Oluşturma
- Hız profili grafikleri
- Enerji tüketimi analizi
- Çoklu test karşılaştırması
- İstatistiksel karşılaştırma grafikleri
- Dashboard görünümü
- Otokar kurumsal renk paleti

### 📝 Rapor Formatları
- **PDF**: ReportLab ile profesyonel PDF raporları
- **Word**: python-docx ile düzenlenebilir Word belgeleri
- Otokar logosu ve kurumsal kimlik
- Özelleştirilebilir şablonlar (Türkçe/İngilizce)

### ✅ Gereksinim Kontrolü
- Test gereksinimlerini otomatik kontrol
- Başarı/başarısızlık durumu
- Detaylı karşılaştırma tabloları
- Özelleştirilebilir eşik değerleri

### 🚀 Toplu İşleme
- Dizindeki tüm dosyaları otomatik işleme
- Paralel işleme desteği
- İlerleme takibi
- Hata yönetimi ve loglama

### 🌍 Çoklu Dil
- Türkçe rapor şablonu
- İngilizce rapor şablonu
- Kolay dil ekleme sistemi

## Kurulum

### Gereksinimler
- Python 3.10 veya üzeri

### Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

Gerekli paketler:
- pandas: Veri işleme
- numpy: Sayısal hesaplamalar
- matplotlib: Grafik oluşturma
- seaborn: Gelişmiş grafikler
- reportlab: PDF oluşturma
- python-docx: Word belgesi oluşturma
- Pillow: Görsel işleme
- openpyxl: Excel okuma
- xlsxwriter: Excel yazma
- scipy: İstatistiksel analizler

## Kullanım

### 1. Komut Satırı (CLI)

#### Tek Dosya için Rapor

```bash
# PDF raporu
python report_cli.py single data/test_data.csv -o report.pdf

# Word raporu
python report_cli.py single data/test_data.csv -f word -o report.docx

# İngilizce rapor
python report_cli.py single data/test_data.csv --language en

# Grafik ve gereksinim kontrolü olmadan
python report_cli.py single data/test_data.csv --no-charts --no-requirements
```

#### Toplu Rapor Oluşturma

```bash
# Dizindeki tüm CSV dosyaları için PDF raporu
python report_cli.py batch data/ -o reports/

# Paralel işleme
python report_cli.py batch data/ -o reports/ --parallel --workers 4

# Word formatında
python report_cli.py batch data/ -o reports/ -f word

# Sonuçları kaydet
python report_cli.py batch data/ -o reports/ --save-results results.csv
```

#### Test Karşılaştırma

```bash
# Birden fazla testi karşılaştır
python report_cli.py compare test1.csv test2.csv test3.csv -o comparison.pdf

# İsimlendirilmiş karşılaştırma
python report_cli.py compare test1.csv test2.csv --names "Gidiş" "Dönüş" -o comparison.pdf
```

### 2. Python API

#### Basit Kullanım

```python
from test_report_generator import ReportBuilder

# Rapor oluşturucu
builder = ReportBuilder(language='tr')

# Tek adımda rapor oluştur
report_path = builder.generate_full_report(
    data_file='test_data.csv',
    output_format='pdf',
    output_path='report.pdf'
)
```

#### Adım Adım Kullanım

```python
from test_report_generator import ReportBuilder

# Rapor oluşturucu
builder = ReportBuilder(language='tr')

# 1. Veriyi yükle
builder.load_test_data('test_data.csv')

# 2. Analiz et
builder.analyze_data()

# 3. Grafikleri oluştur
builder.generate_charts()

# 4. Gereksinimleri kontrol et
builder.check_requirements()

# 5. PDF raporu oluştur
pdf_path = builder.generate_pdf_report('report.pdf')

# 6. Word raporu oluştur
word_path = builder.generate_word_report('report.docx')
```

#### Toplu İşleme

```python
from test_report_generator import BatchReportProcessor

# Toplu işleyici
processor = BatchReportProcessor(language='tr')

# Dizindeki tüm dosyaları işle
results = processor.process_directory(
    input_dir='data/',
    output_dir='reports/',
    pattern='*.csv',
    output_format='pdf',
    parallel=True,
    max_workers=4
)

# Sonuçları kaydet
processor.save_results('batch_results.json')
```

#### Test Karşılaştırma

```python
from test_report_generator.batch_processor import ComparisonReportGenerator

# Karşılaştırma oluşturucu
comparator = ComparisonReportGenerator(language='tr')

# Testleri karşılaştır
report_path = comparator.compare_tests(
    test_files=['test1.csv', 'test2.csv', 'test3.csv'],
    test_names=['Gidiş', 'Dönüş', 'Tekrar'],
    output_path='comparison.pdf',
    output_format='pdf'
)
```

### 3. Özel Konfigürasyon

```python
from test_report_generator import ReportBuilder

# Özel konfigürasyon
custom_config = {
    'company_name': 'OTOKAR',
    'language': 'tr',

    # PDF ayarları
    'pdf': {
        'page_size': 'A4',
        'font_size': 10,
        'margin_top': 2.5,
    },

    # Grafik ayarları
    'charts': {
        'width': 12,
        'height': 6,
        'dpi': 150,
        'otokar_colors': {
            'primary': '#003366',
            'secondary': '#FF6600',
        }
    },

    # Test gereksinimleri
    'requirements': {
        'SORT1': {
            'max_energy_consumption': 100,  # kWh/100km
            'max_duration': 3600,  # saniye
            'min_distance': 1000,  # metre
        }
    }
}

builder = ReportBuilder(config=custom_config)
```

## Dosya Yapısı

```
test_report_generator/
├── __init__.py              # Paket başlatıcı
├── config.py                # Konfigürasyon yönetimi
├── data_reader.py           # Veri okuma modülü
├── statistics.py            # İstatistiksel analiz
├── chart_generator.py       # Grafik oluşturma
├── pdf_generator.py         # PDF rapor oluşturma
├── word_generator.py        # Word rapor oluşturma
├── report_builder.py        # Ana rapor oluşturucu
├── batch_processor.py       # Toplu işleme
├── templates/               # Rapor şablonları
│   ├── sort_test_tr.json   # Türkçe şablon
│   └── sort_test_en.json   # İngilizce şablon
└── assets/                  # Görseller (logo vb.)
    └── otokar_logo.png

examples/
├── generate_sample_data.py  # Örnek veri oluşturucu
└── test_data/               # Örnek test verileri

reports/                     # Oluşturulan raporlar
```

## Test Verisi Formatı

### CSV Formatı

Test verisi CSV dosyası şu sütunları içermelidir:

```csv
Time,Speed,Distance,Throttle,Energy
0,0.0,0.0,0.0,0.0
1,5.2,1.4,45.0,12.5
2,10.5,4.3,50.0,28.7
...
```

**Gerekli Sütunlar:**
- `Time`: Zaman (saniye)
- `Speed`: Hız (km/h)
- `Distance`: Mesafe (metre)
- `Throttle`: Gaz pedalı (%)
- `Energy`: Kümülatif enerji (Wh)

### Metadata Formatı (Opsiyonel)

Test verisi ile aynı dizinde `.meta.json` uzantılı dosya:

```json
{
  "test_type": "SORT1",
  "test_date": "2024-11-21",
  "vehicle_type": "Elektrikli Otobüs",
  "vehicle_plate": "34 ABC 123",
  "driver": "Test Sürücüsü",
  "test_engineer": "Test Mühendisi",
  "ambient_temperature": 25.0,
  "humidity": 60.0
}
```

## Örnek Veri Oluşturma

```bash
# Örnek test verileri ve logo oluştur
python examples/generate_sample_data.py
```

Bu komut şunları oluşturur:
- 3 farklı SORT test verisi (SORT1, SORT2, SORT3)
- Her test için metadata dosyası
- Otokar logo placeholder

## Modül Detayları

### DataReader
- CSV ve Excel dosyalarını okur
- Veri doğrulama
- Sütun kontrolü
- Metadata yönetimi

### StatisticsAnalyzer
- Temel istatistikler
- Güven aralığı
- Aykırı değer tespiti
- Korelasyon analizi
- Enerji tüketimi hesaplama

### RequirementChecker
- Gereksinim tanımlama
- Otomatik kontrol
- Başarı/başarısızlık durumu
- Özet rapor

### ChartGenerator
- Hız profili
- Enerji tüketimi
- Karşılaştırma grafikleri
- Dashboard
- Özelleştirilebilir renkler

### PDFGenerator
- ReportLab tabanlı
- Profesyonel tasarım
- Tablo ve grafikler
- Header/footer
- Sayfa numaralandırma

### WordGenerator
- python-docx tabanlı
- Düzenlenebilir format
- Tablolar ve grafikler
- Kurumsal stil

### BatchReportProcessor
- Toplu dosya işleme
- Paralel işleme desteği
- İlerleme takibi
- Hata yönetimi

## Sorun Giderme

### Bağımlılık Hataları

```bash
# Tüm bağımlılıkları yeniden yükle
pip install -r requirements.txt --upgrade
```

### Font Hataları (PDF)

ReportLab varsayılan fontları kullanır. Özel font gerekiyorsa:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('CustomFont', 'font.ttf'))
```

### Bellek Sorunları

Büyük veri setleri için:

```python
# Veriyi parçalara böl
builder.analyze_data(columns=['Speed', 'Energy'])  # Sadece gerekli sütunlar
```

### Paralel İşleme Hataları

```python
# Seri işleme kullan
processor.process_directory(..., parallel=False)
```

## Katkıda Bulunma

Hata bildirimleri ve öneriler için issue açabilirsiniz.

## Lisans

Bu proje Otokar'a aittir. Tüm hakları saklıdır.

## Sürüm Geçmişi

### v1.0.0 (2024-11-21)
- İlk sürüm
- PDF ve Word rapor desteği
- Türkçe ve İngilizce şablonlar
- Toplu işleme özelliği
- Test karşılaştırma
- İstatistiksel analiz
- Otomatik grafik oluşturma
