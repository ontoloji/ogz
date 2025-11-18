# CAN Bus Test Arayüzü

Kvaser Memorator 2xHS ile CAN hattına mesaj gönderme ve alma işlemlerini gerçekleştiren kullanıcı dostu masaüstü uygulaması.

## Özellikler

### 🚀 Temel Özellikler
- **Çoklu Mesaj Gönderimi**: Eşzamanlı birden fazla CAN mesajı gönderimi
- **Periyodik Gönderim**: Her mesaj için bağımsız gönderim sıklığı ayarı
- **Gelişmiş Filtreleme**: ID ve byte değeri bazlı mesaj filtreleme
- **DBC Entegrasyonu**: DBC dosyası yükleme ve otomatik mesaj decode
- **Gerçek Zamanlı İzleme**: Canlı mesaj görüntüleme ve analiz
- **Log Kaydetme**: CSV/TXT formatında detaylı mesaj kaydı

### 📊 Arayüz Bileşenleri

#### 1. Bağlantı Ayarları
- CAN kanal seçimi (CH0/CH1)
- Baud rate ayarı (125/250/500/1000 kbit/s)
- Bağlantı durumu göstergesi

#### 2. Mesaj Gönderme Paneli
- CAN ID girişi (Hex format)
- DLC ayarı (0-8 byte)
- Data girişi (Hex format, byte-byte)
- Gönderim sıklığı ayarı (ms)
- Gönderim listesi yönetimi
- Aktif/pasif mesaj kontrolü

#### 3. DBC Dosya Yönetimi
- DBC dosyası yükleme
- Mesaj ve sinyal listesi görüntüleme
- Otomatik mesaj decode
- Sinyal fiziksel değer hesaplama

#### 4. Mesaj İzleme
- Gerçek zamanlı mesaj tablosu
- ID bazlı filtreleme
- Byte değeri filtreleme
- Mesaj yönü göstergesi (TX/RX)
- Zaman damgası

#### 5. DBC Decode Görünümü
- Otomatik mesaj decode
- Sinyal değerleri ve birimleri
- Okunabilir format

## Kurulum

### Gereksinimler

1. **Python 3.10+**
   ```bash
   python --version  # 3.10+ olmalı
   ```

2. **Kvaser CANlib SDK** (Windows)
   - [Kvaser CANlib SDK](https://www.kvaser.com/downloads-kvaser/) indir ve kur
   - Windows installer'ı çalıştır
   - Varsayılan ayarlarla kur

3. **Python Paketleri**
   ```bash
   pip install -r requirements.txt
   ```

### Gerekli Paketler
- PyQt6 >= 6.5.0
- cantools >= 39.0.0
- pandas >= 2.0.0
- numpy >= 1.24.0

> **Not**: `canlib` paketi Kvaser CANlib SDK ile birlikte gelir.

## Kullanım

### Program Başlatma

```bash
python can_test_gui.py
```

### Temel İşlemler

#### 1. CAN Bağlantısı

1. **CAN Kanal** seçin (genelde CH0)
2. **Baud Rate** ayarlayın (varsayılan: 500 kbit/s)
3. **Bağlan** butonuna tıklayın
4. Durum göstergesinin **yeşil** olmasını bekleyin

#### 2. Mesaj Gönderme

**Tek Seferlik Gönderim:**
1. CAN ID girin (örn: `0x123`)
2. DLC ayarlayın (örn: `4`)
3. Data byte'larını girin (örn: `01 02 03 04`)
4. **Tek Seferlik Gönder** butonuna tıklayın

**Periyodik Gönderim:**
1. Mesaj bilgilerini girin
2. Gönderim sıklığı ayarlayın (ms, örn: `100`)
3. **Ekle** butonuna tıklayın
4. Listeye eklenen mesajı kontrol edin
5. **Gönderimi Başlat** (F5) butonuna tıklayın

#### 3. DBC Dosyası Yükleme

1. **DBC Yükle...** butonuna tıklayın
2. DBC dosyasını seçin
3. Mesaj listesinin yüklendiğini kontrol edin
4. İstediğiniz mesajı seçip **İzlemeye Ekle** yapabilirsiniz

#### 4. Mesaj Filtreleme

**ID Filtresi:**
1. Filtreleme panelinde ID'leri girin: `0x100, 0x200, 0x300`
2. **Filtre Uygula** butonuna tıklayın
3. Sadece belirlenen ID'ler görüntülenecek

> **Not**: Boş bırakırsanız tüm mesajlar görüntülenir

#### 5. Log Kaydetme

**Manuel Kayıt:**
1. **Export (CSV)** butonuna tıklayın
2. Dosya adı ve konum seçin
3. Mevcut mesajlar export edilir

**Otomatik Loglama:**
1. **Log Kaydet** (F6) butonuna tıklayın
2. Otomatik loglama başlar
3. Tekrar tıklayarak durdurun
4. Log dosyası otomatik kaydedilir

## Kısayol Tuşları

| Tuş | Fonksiyon |
|-----|-----------|
| **F5** | Gönderimi Başlat/Durdur |
| **F6** | Loglama Başlat/Durdur |
| **Ctrl+S** | Log Kaydet (Export) |
| **ESC** | Acil Durdurma |

## Dosya Yapısı

```
ogz/
├── can_test_gui.py          # Ana GUI uygulaması
├── can_message_manager.py   # Mesaj gönderme/alma yöneticisi
├── dbc_manager.py           # DBC dosya yönetimi
├── can_logger.py            # Log kaydetme modülü
├── can_interface.py         # Mevcut CAN interface (SORT için)
├── requirements.txt         # Python bağımlılıkları
├── CAN_TEST_README.md       # Bu dosya
├── can_logs/                # Log dosyaları (otomatik oluşur)
│   ├── CAN_LOG_*.csv
│   └── CAN_LOG_*.txt
└── can_test_settings.json   # Uygulama ayarları (otomatik)
```

## Modül Açıklamaları

### 1. can_message_manager.py

**CANMessage**: Mesaj tanımı
- `can_id`: CAN mesaj ID
- `data`: Mesaj verisi (bytes)
- `dlc`: Data uzunluğu
- `period_ms`: Periyodik gönderim sıklığı
- `enabled`: Aktif/pasif durum

**CANMessageSender**: Gönderici
- `add_message()`: Mesaj ekle
- `remove_message()`: Mesaj sil
- `start_sending()`: Gönderimi başlat
- `stop_sending()`: Gönderimi durdur
- `send_once()`: Tek seferlik gönder

**CANMessageReceiver**: Alıcı
- `set_id_filters()`: ID filtresi ayarla
- `add_byte_filter()`: Byte filtresi ekle
- `start_receiving()`: Almayı başlat
- `get_messages()`: Mesajları al

### 2. dbc_manager.py

**DBCManager**: DBC yöneticisi
- `load_dbc()`: DBC dosyası yükle
- `decode_message()`: Mesaj decode et
- `encode_message()`: Mesaj encode et
- `get_signal_value()`: Sinyal değeri al

### 3. can_logger.py

**CANLogger**: Log yöneticisi
- `start_logging()`: Loglama başlat
- `stop_logging()`: Loglama durdur
- `export_to_csv()`: CSV export
- `export_to_txt()`: TXT export

## Örnek Kullanım Senaryoları

### Senaryo 1: Basit Mesaj Gönderme

```
Amaç: 0x123 ID'li mesaj gönder

1. Bağlantı:
   - Kanal: CH0
   - Baud: 500 kbit/s
   - Bağlan

2. Mesaj:
   - CAN ID: 0x123
   - DLC: 4
   - Data: 01 02 03 04
   - Tek Seferlik Gönder
```

### Senaryo 2: Periyodik Çoklu Mesaj

```
Amaç: 3 farklı mesajı farklı sıklıklarda gönder

1. Mesaj 1:
   - ID: 0x100, Data: AA BB CC DD, Periyot: 100ms
   - Ekle

2. Mesaj 2:
   - ID: 0x200, Data: 11 22 33, Periyot: 50ms
   - Ekle

3. Mesaj 3:
   - ID: 0x300, Data: FF EE, Periyot: 200ms
   - Ekle

4. Gönderimi Başlat (F5)
```

### Senaryo 3: DBC ile Mesaj İzleme

```
Amaç: Motor mesajlarını decode ederek izle

1. DBC Yükle:
   - vehicle.dbc dosyasını yükle

2. Mesaj Seç:
   - "EngineStatus" mesajını seç
   - İzlemeye Ekle

3. Filtre Uygula:
   - Sadece motor mesajları görüntülenir

4. Decode Tab:
   - RPM, Temperature gibi sinyaller okunabilir formatta
```

### Senaryo 4: Test Logu Kaydetme

```
Amaç: 1 saatlik test logu kaydet

1. Filtre Ayarla:
   - İlgilenilen ID'leri gir: 0x100, 0x200, 0x300

2. Loglama Başlat:
   - F6 tuşuna bas
   - Log dosyası otomatik oluşturulur

3. Test Yap:
   - 1 saat test gerçekleştir

4. Loglama Durdur:
   - F6 tuşuna tekrar bas
   - Log otomatik kaydedilir

5. Analiz:
   - can_logs/ klasöründe CSV dosyasını aç
   - Excel veya Python ile analiz et
```

## Log Dosyası Formatları

### CSV Format

```csv
Timestamp,CAN ID,DLC,Data,Direction
2024-11-18 10:23:45.123,0x123,4,01 02 03 04,TX
2024-11-18 10:23:45.156,0x456,3,AA BB CC,RX
```

### TXT Format

```
================================================================================
CAN Bus Mesaj Logu
Toplam Mesaj: 1234
Tarih: 2024-11-18 10:23:45
================================================================================

Zaman           | CAN ID     | DLC | Data                           | Dir
--------------------------------------------------------------------------------
10:23:45.123    | 0x123      | 4   | 01 02 03 04                    | TX
10:23:45.156    | 0x456      | 3   | AA BB CC                       | RX
```

## Sorun Giderme

### CAN Bağlantı Hatası

**Problem**: "CAN bağlantısı başarısız" hatası

**Çözümler**:
1. Kvaser CANlib SDK kurulu mu kontrol edin
2. CAN cihazı USB'ye bağlı mı?
3. Cihaz Driver'ları güncel mi?
4. Başka program CAN kullanıyor mu?
5. Kanal numarası doğru mu? (genelde CH0)

### DBC Yükleme Hatası

**Problem**: "DBC dosyası yüklenemedi" hatası

**Çözümler**:
1. Dosya formatı doğru mu? (.dbc uzantılı)
2. Dosya yolu Türkçe karakter içeriyor mu?
3. cantools paketi yüklü mü?
   ```bash
   pip install cantools
   ```

### Mesaj Görünmüyor

**Problem**: Mesajlar tabloda görünmüyor

**Çözümler**:
1. Filtre aktif mi? (Boş bırakın = tümü)
2. Duraklat modu aktif mi?
3. Bağlantı hala aktif mi?
4. CAN bus'ta gerçekten mesaj var mı?

### Periyodik Gönderim Çalışmıyor

**Problem**: Mesajlar gönderilmiyor

**Çözümler**:
1. "Gönderimi Başlat" butonuna basıldı mı?
2. Mesaj "Aktif" olarak işaretli mi?
3. Periyot 0'dan büyük mü?
4. Bağlantı hala aktif mi?

## Performans İpuçları

### Yüksek Yük Durumları

**Yüksek mesaj hızında (>1000 msg/s):**
- Filtre kullanın, sadece gerekli ID'leri izleyin
- Duraklat modunu kullanın
- Buffer boyutunu azaltın (max 1000 mesaj)

**Uzun süreli loglama:**
- Düzenli aralıklarla log dosyası kaydedin
- Eski mesajları temizleyin
- Disk alanını kontrol edin

### Bellek Yönetimi

**Tablo temizleme:**
- Düzenli olarak "Temizle" butonunu kullanın
- Max 1000 mesaj buffer limiti var
- Eski mesajlar otomatik siliniyor

## Güvenlik Uyarıları

⚠️ **ÖNEMLİ**

1. **Üretim Ortamı**: Kritik CAN bus'larda dikkatli olun
2. **Test Ortamı**: Önce test ortamında deneyin
3. **Yedek**: Orijinal DBC dosyalarını yedekleyin
4. **Acil Durdur**: ESC tuşu ile her zaman durdurun
5. **ID Çakışması**: Mevcut mesajlarla çakışmaya dikkat

## Geliştirme Roadmap

### Mevcut Özellikler ✅
- ✅ Temel CAN bağlantısı
- ✅ Çoklu mesaj gönderimi
- ✅ DBC entegrasyonu
- ✅ Log kaydetme
- ✅ Mesaj filtreleme

### Planlanan Özellikler 🔜
- 🔜 CANoe blf dosya import/export
- 🔜 Grafik görünüm (sinyal trend)
- 🔜 Mesaj şablonları (templates)
- 🔜 Replay modu (kayıtlı mesajları tekrar oynat)
- 🔜 CAN FD desteği
- 🔜 Scriptleme desteği (Python API)

## Lisans

Bu proje özel bir proje olup, tüm hakları saklıdır.

## İletişim

Sorularınız için:
- GitHub Issues
- Email: support@example.com

## Sürüm Geçmişi

### v1.0.0 (2024-11-18)
- İlk sürüm
- Temel CAN gönderme/alma
- DBC entegrasyonu
- Log kaydetme
- PyQt6 GUI

---

**Son Güncelleme**: 2024-11-18
**Yazar**: CAN Bus Test Arayüzü Geliştirme Ekibi
