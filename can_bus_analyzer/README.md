# CAN Bus Analyzer

Windows için profesyonel CAN Bus veri analiz ve görselleştirme aracı.

## Özellikler

- **Kvaser Cihaz Desteği**: Windows'ta Kvaser CAN cihazları ile çalışır
- **DBC Dosya Desteği**: DBC dosyaları yükleyerek CAN mesajlarını decode eder
- **Real-time Görselleştirme**: Seçili sinyalleri gerçek zamanlı olarak grafikleştirir
- **Log Dosya Analizi**: ASC ve BLF formatındaki log dosyalarını okur ve analiz eder
- **Veri Export**: Toplanan verileri CSV ve Excel formatında export eder
- **Sinyal Filtreleme**: İstediğiniz CAN ID'leri ve sinyalleri filtreleyebilirsiniz
- **Windows GUI**: Kullanıcı dostu Tkinter arayüzü
- **Standalone EXE**: PyInstaller ile tek dosya halinde çalıştırılabilir

## Sistem Gereksinimleri

- **İşletim Sistemi**: Windows 10/11 (64-bit)
- **Python**: 3.9 veya üzeri (sadece kaynak koddan çalıştırma için)
- **CAN Cihazı**: Kvaser CAN interface (USB, PCIe, vb.)
- **Kvaser CANlib SDK**: [Kvaser Downloads](https://www.kvaser.com/downloads-kvaser/) sayfasından indirin

## Kurulum

### Yöntem 1: Standalone EXE (Önerilen)

1. `dist` klasöründeki `CAN_Bus_Analyzer.exe` dosyasını çalıştırın
2. Kvaser CANlib SDK'nin kurulu olduğundan emin olun
3. Hazırsınız!

### Yöntem 2: Python ile Kaynak Koddan

#### Adım 1: Python ve Git Kurulumu
```bash
# Python 3.9+ kurulu olmalı
python --version

# Repository'yi klonlayın
git clone <repository-url>
cd can_bus_analyzer
```

#### Adım 2: Virtual Environment Oluşturma (Önerilen)
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

#### Adım 3: Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

#### Adım 4: Kvaser CANlib SDK Kurulumu
1. [Kvaser Downloads](https://www.kvaser.com/downloads-kvaser/) sayfasından CANlib SDK'yi indirin
2. Windows için uygun sürümü (32-bit veya 64-bit) yükleyin
3. Kurulum tamamlandıktan sonra bilgisayarınızı yeniden başlatın

#### Adım 5: Uygulamayı Çalıştırma
```bash
cd src
python can_analyzer_gui.py
```

## EXE Oluşturma

Windows'ta standalone EXE dosyası oluşturmak için:

```bash
# Otomatik build scripti (Önerilen)
build_exe.bat

# veya manuel PyInstaller
pyinstaller can_analyzer.spec
```

EXE dosyası `dist` klasöründe oluşturulacaktır.

## Kullanım Kılavuzu

### 1. CAN Bus Bağlantısı

1. **Kvaser cihazınızı** bilgisayara bağlayın
2. Sol panelde **"CAN Bağlantısı"** bölümünden:
   - Kanal numarasını seçin (varsayılan: 0)
   - Bitrate değerini seçin (varsayılan: 500000 = 500Kbps)
   - **"Bağlan"** butonuna tıklayın
3. Bağlantı başarılı olursa durum "Bağlı" olarak yeşil renkte görünür

### 2. DBC Dosyası Yükleme

1. **Dosya → DBC Yükle** menüsünden veya sol paneldeki **"DBC Yükle"** butonundan
2. DBC dosyanızı seçin
3. Başarılı yüklemede, dosya adı gösterilir ve sinyaller listeye eklenir

### 3. Mesaj Monitörü

**"Mesaj Monitör"** sekmesinde:
- Gelen tüm CAN mesajları real-time olarak görüntülenir
- Timestamp, CAN ID, DLC, Data ve Decode bilgileri gösterilir
- **CAN ID Filtre** alanından istediğiniz ID'leri filtreleyebilirsiniz
  - Örnek: `0x123, 0x456` veya `291, 1110`

### 4. Veri Kaydı

1. Sol panelde **"Kaydı Başlat"** butonuna tıklayın
2. Mesajlar otomatik olarak kaydedilir
3. **"Kaydı Durdur"** ile kaydı sonlandırın
4. Kaydedilen mesajları export edebilirsiniz:
   - **Dosya → CSV Export**
   - **Dosya → Excel Export**

### 5. Real-time Grafik

1. Sol paneldeki **"Sinyal Seçimi"** listesinden istediğiniz sinyalleri seçin
   - Çoklu seçim: Ctrl tuşuna basılı tutarak tıklayın
2. **"Grafik Güncelle"** butonuna tıklayın
3. **"Grafik"** sekmesine geçin
4. Seçili sinyaller real-time olarak grafikleştirilir

### 6. Log Dosya Analizi

1. **Dosya → Log Dosyası Aç** menüsünden ASC veya BLF dosyası seçin
2. **"Log Analizi"** sekmesine geçin
3. Dosya istatistiklerini görüntüleyin
4. **Araçlar → İstatistikler** menüsünden detaylı analiz alın

### 7. Veri Export

#### CSV Export
```
Dosya → CSV Export
```
- Timestamp, CAN ID, Data ve (varsa) decode edilmiş sinyaller
- Excel ve diğer araçlarla uyumlu

#### Excel Export
```
Dosya → Excel Export
```
- Düzenli formatlanmış Excel dosyası
- Her sinyal ayrı kolonda
- Otomatik kolon genişlikleri

#### Grafik Kaydetme
```
Araçlar → Grafik Kaydet
```
- PNG veya PDF formatında
- Yüksek çözünürlük (150 DPI)

## Proje Yapısı

```
can_bus_analyzer/
│
├── src/                          # Kaynak kodlar
│   ├── can_reader.py            # CAN bus okuyucu
│   ├── dbc_parser.py            # DBC dosya parser
│   ├── log_reader.py            # Log dosya okuyucu
│   ├── data_exporter.py         # CSV/Excel export
│   ├── plotter.py               # Grafik oluşturma
│   └── can_analyzer_gui.py      # Ana GUI uygulaması
│
├── resources/                    # Kaynaklar (icon, vb.)
├── examples/                     # Örnek DBC ve log dosyaları
├── docs/                         # Dokümantasyon
│
├── requirements.txt              # Python bağımlılıkları
├── build_exe.bat                 # EXE build scripti
├── can_analyzer.spec             # PyInstaller spec
└── README.md                     # Bu dosya
```

## Modül Açıklamaları

### can_reader.py
- Kvaser CAN cihazlarından mesaj okuma
- Thread-safe mesaj kuyruğu
- CAN ID filtreleme
- İstatistik toplama

### dbc_parser.py
- DBC dosya yükleme ve parsing
- CAN mesaj decode/encode
- Sinyal arama ve listeleme
- Mesaj bilgilerini export

### log_reader.py
- ASC ve BLF log dosyalarını okuma
- Zaman bazlı filtreleme
- İstatistik hesaplama
- Pattern arama

### data_exporter.py
- CSV export
- Excel export (openpyxl)
- Analiz raporu oluşturma
- Signal data export

### plotter.py
- Real-time grafik
- Matplotlib/Tkinter entegrasyonu
- Çoklu sinyal gösterimi
- Statik grafik export

### can_analyzer_gui.py
- Tkinter GUI
- Tüm modüllerin entegrasyonu
- Event handling
- Periyodik güncelleme

## Sık Karşılaşılan Sorunlar

### "CAN Bus'a bağlanılamadı" Hatası

**Çözüm:**
1. Kvaser cihazının USB bağlantısını kontrol edin
2. Kvaser CANlib SDK'nin kurulu olduğunu doğrulayın
3. Doğru kanal numarasını seçtiğinizden emin olun
4. Cihaz Yöneticisi'nden Kvaser cihazını kontrol edin

### "DBC dosyası yüklenemedi" Hatası

**Çözüm:**
1. DBC dosyasının geçerli bir formatta olduğunu kontrol edin
2. Dosya yolunda Türkçe karakter olmamalı
3. Dosyanın başka bir program tarafından kullanılmadığından emin olun

### Grafik Görünmüyor

**Çözüm:**
1. Önce DBC dosyası yükleyin
2. Sol panelden sinyal seçin
3. "Grafik Güncelle" butonuna tıklayın
4. CAN Bus'a bağlı olduğunuzdan emin olun

### EXE Oluşturamıyorum

**Çözüm:**
1. Virtual environment aktif olmalı
2. `pip install pyinstaller` komutunu çalıştırın
3. `build_exe.bat` scriptini yönetici olarak çalıştırın

## Teknik Detaylar

### Desteklenen CAN Bitrate'ler
- 125 Kbps
- 250 Kbps
- 500 Kbps (varsayılan)
- 1000 Kbps (1 Mbps)

### Desteklenen Dosya Formatları
- **DBC**: .dbc (Vector DBC format)
- **Log**: .asc (ASC format), .blf (Binary Log Format)
- **Export**: .csv, .xlsx, .png, .pdf

### Windows Uyumluluğu
- Windows 10 (64-bit)
- Windows 11 (64-bit)
- Python 3.9, 3.10, 3.11, 3.12

## Geliştirme

### Test Etme
```bash
# Modül testleri
cd src
python can_reader.py       # CAN reader test
python dbc_parser.py       # DBC parser test
python log_reader.py       # Log reader test
```

### Kod Yapısı
- Modüler tasarım
- Type hinting kullanımı
- Comprehensive error handling
- Detailed logging
- Thread-safe operasyonlar

## Lisans

Bu proje telif hakkı koruması altındadır. Ticari kullanım için izin gereklidir.

## İletişim ve Destek

Sorularınız veya sorunlarınız için:
- Issue açın
- Dokümantasyonu inceleyin
- Log dosyalarını kontrol edin

## Güncellemeler

### v1.0.0 (2024)
- İlk sürüm
- Kvaser desteği
- DBC parsing
- Real-time plotting
- Log file analysis
- CSV/Excel export
- Windows GUI

## Katkıda Bulunanlar

Bu proje, otomotiv test ve doğrulama uygulamaları için geliştirilmiştir.

---

**Not**: Kvaser CANlib SDK kurulumu zorunludur. SDK indirme linki: https://www.kvaser.com/downloads-kvaser/

**Uyarı**: CAN Bus üzerinde veri gönderirken dikkatli olun. Yanlış mesajlar araç güvenliğini etkileyebilir.
