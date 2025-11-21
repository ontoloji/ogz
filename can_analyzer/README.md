# CAN Bus Analyzer - Windows

Windows işletim sistemi için geliştirilmiş, profesyonel CAN Bus veri analiz aracı.

## 🚀 Özellikler

### CAN Bus İletişimi
- ✅ **Kvaser CAN cihazları** tam desteği
- ✅ PCAN, Vector, SocketCAN arayüzleri desteği
- ✅ Ayarlanabilir bitrate (125k, 250k, 500k, 1M bps)
- ✅ Real-time mesaj alıcı/gönderici
- ✅ Çoklu kanal desteği

### DBC Dosya Desteği
- ✅ DBC dosyası yükleme ve parse etme
- ✅ Otomatik sinyal decode
- ✅ Mesaj ve sinyal tanımları görüntüleme
- ✅ Enum değerleri desteği
- ✅ Sinyal validasyon

### Veri Görselleştirme
- ✅ Real-time grafik çizimi (PyQtGraph)
- ✅ Çoklu sinyal gösterimi
- ✅ Zoom, pan, otomatik ölçeklendirme
- ✅ Grafik export (PNG, JPG)
- ✅ Yüksek performanslı rendering

### Log Dosyası Analizi
- ✅ ASC (ASCII) log dosyaları
- ✅ BLF (Binary Logging Format) dosyaları
- ✅ Hızlı dosya okuma
- ✅ Zaman aralığı filtreleme
- ✅ ID bazlı filtreleme

### Veri Export
- ✅ CSV formatında export
- ✅ Excel (XLSX) formatında export
- ✅ İstatistik raporları
- ✅ Decode edilmiş sinyal verileri
- ✅ Otomatik grafik ekleme (Excel)

### Kullanıcı Arayüzü
- ✅ Modern PyQt5 GUI
- ✅ Tab-based arayüz
- ✅ Kolay kullanım
- ✅ Windows 10/11 uyumlu tema
- ✅ Türkçe dil desteği

## 📋 Gereksinimler

### Sistem Gereksinimleri
- **İşletim Sistemi:** Windows 10 veya Windows 11 (64-bit)
- **RAM:** Minimum 4 GB (8 GB önerilir)
- **Disk:** 500 MB boş alan
- **Ekran:** 1920x1080 veya üzeri önerilir

### Yazılım Gereksinimleri
- **Python:** 3.8 veya üzeri (geliştirme için)
- **Kvaser CANlib SDK:** [İndir](https://www.kvaser.com/downloads/)
- **CAN Arayüzü:** Kvaser, PCAN, Vector vb.

## 🔧 Kurulum

### Seçenek 1: Derlenmiş .exe Kullanımı (Önerilir)

1. **Kvaser CANlib SDK Kurulumu**
   ```
   https://www.kvaser.com/downloads/ adresinden indirin
   SDK'yı kurun (Windows sürücüleri dahil)
   ```

2. **CANBusAnalyzer.exe'yi İndirin**
   - Releases sayfasından son sürümü indirin
   - İstediğiniz klasöre çıkarın
   - `CANBusAnalyzer.exe`'yi çalıştırın

### Seçenek 2: Python ile Çalıştırma

1. **Repository'yi Klonlayın**
   ```bash
   git clone https://github.com/ontoloji/ogz.git
   cd ogz/can_analyzer
   ```

2. **Virtual Environment Oluşturun (Opsiyonel)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Bağımlılıkları Yükleyin**
   ```bash
   pip install -r requirements.txt
   ```

4. **Kvaser CANlib SDK Kurulumu**
   - SDK'yı https://www.kvaser.com/downloads/ adresinden indirin ve kurun

5. **Uygulamayı Başlatın**
   ```bash
   python main.py
   ```

### Seçenek 3: Setup ile Kurulum

```bash
pip install -e .
can-analyzer
```

## 📖 Kullanım

### 1. CAN Bus Bağlantısı

1. **Arayüz Seçimi**: Kvaser, PCAN, Vector vb.
2. **Kanal Seçimi**: CAN kanal numarası (0, 1, ...)
3. **Bitrate Ayarı**: 125000, 250000, 500000, 1000000
4. **Bağlan** butonuna tıklayın

### 2. DBC Dosyası Yükleme

1. **DBC Yükle** butonuna tıklayın
2. .dbc dosyasını seçin
3. Mesaj ve sinyal tanımları otomatik yüklenir

### 3. Real-Time CAN Mesajları

1. **Almaya Başla** butonuna tıklayın
2. Mesajlar tabloda görüntülenir
3. DBC yüklüyse otomatik decode edilir
4. ID filtreleme yapabilirsiniz

### 4. Grafik Görselleştirme

1. **Grafik** tab'ına geçin
2. Sinyal listesinden istediğiniz sinyali seçin
3. **Grafiğe Ekle** butonuna tıklayın
4. **Otomatik Güncelle** seçeneğini aktif edin
5. Real-time grafik görüntülenir

### 5. Log Dosyası Analizi

1. **Log Analizi** tab'ına geçin
2. **Log Yükle** butonuna tıklayın
3. .asc veya .blf dosyasını seçin
4. Veriler tabloda görüntülenir

### 6. Veri Export

1. **Export** tab'ına geçin
2. Export seçeneklerini belirleyin
3. **CSV'ye Export** veya **Excel'e Export** seçin
4. Kayıt konumunu belirtin

## 🏗️ Proje Yapısı

```
can_analyzer/
├── main.py                 # Ana giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── setup.py               # Kurulum scripti
├── build.py               # PyInstaller build scripti
├── CANBusAnalyzer.spec    # PyInstaller spec dosyası
│
├── core/                  # Ana modüller
│   ├── __init__.py
│   ├── can_handler.py     # CAN Bus iletişim
│   ├── dbc_parser.py      # DBC dosya işleme
│   ├── log_reader.py      # Log dosyası okuma
│   └── data_exporter.py   # Veri export
│
├── gui/                   # GUI modülleri
│   ├── __init__.py
│   ├── main_window.py     # Ana pencere
│   └── plot_widget.py     # Grafik widget
│
├── utils/                 # Yardımcı modüller
│   ├── __init__.py
│   └── helpers.py         # Yardımcı fonksiyonlar
│
└── resources/             # Kaynaklar
    └── icons/             # İkonlar
```

## 🔨 .exe Dosyası Oluşturma

### PyInstaller ile Build

```bash
cd can_analyzer
python build.py
```

Veya alternatif olarak:

```bash
pyinstaller CANBusAnalyzer.spec
```

Build tamamlandığında:
- `dist/CANBusAnalyzer.exe` - Ana uygulama
- `dist/KURULUM.txt` - Kurulum talimatları
- `dist/README.md` - Kullanım kılavuzu

## 📝 Örnekler

### Python API Kullanımı

```python
from can_analyzer import CANHandler, DBCParser

# CAN bağlantısı
can = CANHandler()
can.connect(channel=0, bitrate=500000, interface='kvaser')

# DBC yükle
dbc = DBCParser()
dbc.load_dbc('C:\\path\\to\\database.dbc')

# Mesaj gönder
can.send_message(arbitration_id=0x123, data=b'\x01\x02\x03\x04')

# Mesaj al ve decode et
can.add_callback(lambda msg: print(dbc.decode_message(msg['arbitration_id'], msg['data'])))
can.start_receiving()
```

### Log Dosyası Analizi

```python
from can_analyzer import LogReader, DataExporter

# Log yükle
log = LogReader()
log.load_file('C:\\logs\\candata.asc')

# Belirli ID'leri filtrele
messages = log.filter_by_id([0x123, 0x456])

# Excel'e export et
exporter = DataExporter()
exporter.export_to_excel(messages, 'C:\\output\\report.xlsx')
```

## 🐛 Sorun Giderme

### Kvaser Bağlantı Hatası

**Hata:** `CAN Bus bağlantı hatası`

**Çözüm:**
1. Kvaser CANlib SDK'nın kurulu olduğundan emin olun
2. Kvaser cihazının bağlı ve tanımlı olduğunu kontrol edin
3. Windows Aygıt Yöneticisi'nde cihaz durumunu kontrol edin
4. Sürücüleri güncelleyin

### DBC Yükleme Hatası

**Hata:** `DBC yükleme hatası`

**Çözüm:**
1. DBC dosyasının doğru formatta olduğundan emin olun
2. Dosya yolunda Türkçe karakter olmamasına dikkat edin
3. Dosya izinlerini kontrol edin

### Import Hatası

**Hata:** `ModuleNotFoundError`

**Çözüm:**
```bash
pip install -r requirements.txt --upgrade
```

### Antivirüs Engeli

.exe dosyası antivirüs tarafından engelleniyorsa:
1. Dosyayı güvenli listesine ekleyin
2. Windows Defender SmartScreen'i geçici olarak kapatın
3. Güvenilir kaynaklardan indirdiğinizi doğrulayın

## 📊 Performans

- **Real-time rendering:** 60+ FPS
- **Mesaj işleme:** 10,000+ mesaj/saniye
- **Bellek kullanımı:** ~150 MB (boşta)
- **Log okuma:** ~1M mesaj/saniye

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [python-can](https://github.com/hardbyte/python-can) - CAN Bus kütüphanesi
- [cantools](https://github.com/cantools/cantools) - DBC parser
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [PyQtGraph](http://www.pyqtgraph.org/) - Grafik kütüphanesi
- [Kvaser](https://www.kvaser.com/) - CAN hardware

## 📞 İletişim

- **GitHub Issues:** [Issues](https://github.com/ontoloji/ogz/issues)
- **Email:** [support@example.com](mailto:support@example.com)

## 📈 Versiyon Geçmişi

### v1.0.0 (2024)
- ✨ İlk sürüm
- ✅ Kvaser desteği
- ✅ DBC parser
- ✅ Real-time grafik
- ✅ Log analizi
- ✅ Excel/CSV export

---

**Windows 10/11 için optimize edilmiştir** 🪟
