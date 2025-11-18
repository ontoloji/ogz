# SORT Test Otomasyon Sistemi & CAN Bus Güvenlik Test Platformu

Windows ortamında çalışan, elektrikli ve içten yanmalı araçların UITP SORT standardına uygun enerji tüketimi testlerini otomatik olarak gerçekleştiren Python tabanlı test otomasyon yazılımı.

**YENİ:** CAN Bus Siber Güvenlik Test Sistemi - Kvaser Memorator 2xHS ile otomotiv güvenlik testleri için profesyonel araç.

## Özellikler

- **3 Farklı SORT Profili**: SORT 1, 2 ve 3 test profilleri
- **Çoklu Araç Desteği**: Elektrikli araç (CAN), DAF Motor, IBK
- **Otomatik Hız Kontrolü**: PID tabanlı sabit hız kontrolü
- **Gerçek Zamanlı Grafik**: Hız, mesafe ve enerji tüketimi grafikleri
- **Veri Kayıt**: CSV formatında saniye-saniye test verileri
- **Raporlama**: Excel formatında detaylı test raporları
- **Güvenlik**: Acil durdurma, hız limiti kontrolü, bağlantı izleme

---

## 🔒 CAN Bus Siber Güvenlik Test Sistemi

**⚠️ UYARI: Bu yazılım SADECE yetkili güvenlik testleri, araştırma ve eğitim amaçlı kullanılmalıdır.**

### Özellikler

- **8 Farklı Saldırı Türü**: Fuzzing, DoS, Spoofing, Replay, Diagnostic, Error Frame, Bus Off, ID Scan
- **Kvaser Desteği**: Memorator 2xHS ve diğer Kvaser cihazlar
- **Esnek Konfigürasyon**: Baud rate, ID aralığı, paket hızı ayarlanabilir
- **Gerçek Zamanlı Monitor**: CAN bus mesajlarını canlı izleme
- **Mesaj Yakalama**: Replay attack için mesaj yakalama ve kaydetme
- **Detaylı Loglama**: Tüm işlemler log'lanır
- **GUI Arayüzü**: Kullanıcı dostu PyQt6 arayüzü

### Hızlı Başlangıç (Güvenlik Testi)

```bash
# GUI ile başlat
python can_security_gui.py

# Örnek scriptleri çalıştır
python examples/can_security_example.py
```

### Saldırı Türleri

1. **Fuzzing** - Rastgele CAN mesajları ile güvenlik açığı tespiti
2. **DoS** - Bus flooding saldırıları
3. **Spoofing** - Sahte mesaj enjeksiyonu
4. **Replay** - Yakalanan mesajların tekrarı
5. **Diagnostic** - UDS komut enjeksiyonu
6. **Error Frame** - Hata frame saldırıları
7. **Bus Off** - ECU'ları devre dışı bırakma
8. **ID Scan** - Aktif CAN ID'leri keşfi

### Dokümantasyon

Detaylı kullanım kılavuzu için: **[CAN_SECURITY_GUIDE.md](CAN_SECURITY_GUIDE.md)**

### Dosyalar

- `can_security_attacks.py` - Saldırı modülleri
- `can_security_gui.py` - GUI arayüzü
- `can_security_config.json` - Konfigürasyon ve presetler
- `examples/can_security_example.py` - Örnek kullanım scriptleri
- `CAN_SECURITY_GUIDE.md` - Detaylı dokümantasyon

---

## Sistem Mimarisi

### Ana Modüller

1. **Ana Test Arayüzü** (`main_gui.py`)
   - PyQt6 tabanlı modern arayüz
   - Gerçek zamanlı veri görüntüleme
   - Test kontrolü ve izleme

2. **Raporlama Arayüzü** (`report_gui.py`)
   - Test sonuçlarını analiz
   - SORT standardına göre test seçimi
   - Excel raporu oluşturma

3. **CAN İletişim Modülü** (`can_interface.py`)
   - Kvaser Memorator Pro 2xHS v2 desteği
   - Gaz pedalı kontrolü (TX)
   - VBOX hız okuma (RX)

4. **Arduino Kontrol Modülü** (`arduino_interface.py`)
   - 2 kanallı analog sinyal üretimi
   - DAF Motor: 0.5V - 4.5V
   - IBK: 2.5V - 4.5V

5. **eDAQ Entegrasyon Modülü** (`edaq_interface.py`)
   - HBK eDAQ HTTP REST API
   - XML formatında enerji verisi okuma

6. **PID Kontrol Modülü** (`pid_controller.py`)
   - Sabit hız kontrolü
   - Ayarlanabilir Kp, Ki, Kd parametreleri

7. **Veri Kayıt Modülü** (`data_logger.py`)
   - CSV formatında veri kaydetme
   - Test meta verileri yönetimi

## Donanım Gereksinimleri

### CAN İletişimi (Elektrikli Araç)
- **Cihaz**: Kvaser Memorator Pro 2xHS v2
- **Protokol**: CAN 2.0, 500 kbit/s
- **TX Mesaj ID**: 0xCF00002 (217056130)
- **RX Mesaj ID**: 0x302 (770)

### Arduino (İçten Yanmalı Araçlar)
- **Cihaz**: Arduino Uno
- **Bağlantı**: USB Serial (115200 baud)
- **Çıkış**: 2 kanal PWM + RC Filter
  - Pin 9: DAF Motor (0.5V - 4.5V)
  - Pin 10: IBK (2.5V - 4.5V)
- **RC Filter**: Her kanal için 1kΩ + 100µF

### eDAQ (Enerji Ölçümü)
- **Cihaz**: HBK eDAQ
- **Bağlantı**: HTTP REST API (Ethernet)
- **Veri Formatı**: XML
- **Okuma Periyodu**: 400ms

## Yazılım Kurulumu

### 1. Python Kurulumu
```bash
# Python 3.10 veya üzeri gereklidir
python --version  # 3.10+ olmalı
```

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Kvaser CANlib SDK Kurulumu (CAN için)
1. [Kvaser CANlib SDK](https://www.kvaser.com/downloads-kvaser/) indir
2. Windows installer'ı çalıştır
3. Varsayılan ayarlarla kur

### 4. Arduino Firmware Yükleme (DAF/IBK için)
1. Arduino IDE'yi aç
2. `arduino_firmware/pedal_controller.ino` dosyasını aç
3. Arduino Uno'yu USB ile bağla
4. Tools -> Board -> Arduino Uno seç
5. Tools -> Port -> COMx seç
6. Upload butonuna tıkla

### 5. Yapılandırma
`config.json` dosyasını düzenle:
```json
{
    "can": {
        "channel": 0,
        "bitrate": 500000
    },
    "arduino": {
        "port": "COM3"
    },
    "edaq": {
        "ip": "192.168.1.100",
        "port": 8080
    },
    "pid": {
        "kp": 2.0,
        "ki": 0.5,
        "kd": 0.1
    }
}
```

## Kullanım

### Ana Test Programı Başlatma
```bash
python main_gui.py
```

### Raporlama Programı Başlatma
```bash
python report_gui.py
```

## Test Prosedürü

### 1. Hazırlık
1. Donanım bağlantılarını kontrol edin
2. Araç güvenli bir test ortamında olmalı
3. Enerji ölçüm cihazını sıfırlayın

### 2. Test Konfigürasyonu
1. **Araç Tipi** seçin (Elektrikli/DAF/IBK)
2. **Test Tipi** seçin (SORT 1/2/3)
3. **Hızlanma Gaz Pedalı** yüzdesini girin (önerilen: %50)
4. **Maksimum Hız Limiti** belirleyin
5. **PID Parametrelerini** ayarlayın
6. **Test Bilgileri** girin (araç, sürücü, sıcaklık, vd.)

### 3. Bağlantı
1. "CAN/Arduino Bağlan" butonuna tıklayın
2. Bağlantı başarılı mesajını bekleyin

### 4. Test Başlatma
1. "TEST BAŞLAT" butonuna tıklayın
2. Test otomatik olarak başlar
3. Gerçek zamanlı grafikler ve verileri izleyin

### 5. Frenleme Segmentleri
- Test sırasında frenleme segmentlerinde **sürücü manuel olarak frenlemelidir**
- Sistem gaz pedalını 0'a çeker
- Hedef mesafede (±5m tolerans) durmaya çalışın

### 6. Bekleme Segmentleri
- Sistem otomatik olarak bekler
- Ekranda geri sayım gösterilir

### 7. Test Tamamlanması
- Test bittiğinde otomatik olarak durur
- Veriler CSV formatında kaydedilir
- Test meta verileri JSON formatında saklanır

### 8. Acil Durdurma
- **"ACİL DURDUR"** butonu veya **ESC** tuşu
- Gaz pedalı anında 0'a çekilir
- Test durdurulur ve veri kaydedilir

## SORT Test Profilleri

### SORT 1 (Toplam: 1040m)
- Hız seviyeleri: 20, 30, 40 km/h
- Her hız 2 kez tekrarlanır
- Toplam 18 segment + 6 bekleme

### SORT 2 (Toplam: 920m)
- Hız seviyeleri: 20, 40, 50 km/h
- Toplam 9 segment + 3 bekleme

### SORT 3 (Toplam: 1450m)
- Hız seviyeleri: 30, 50, 60 km/h
- Toplam 9 segment + 3 bekleme

## Raporlama

### Test Analizi
1. Raporlama programını açın
2. Gidiş ve dönüş testlerini seçin
3. "Analiz Et" butonuna tıklayın
4. Sistem otomatik olarak:
   - En düşük enerji tüketimli testi seçer
   - %2 tolerans dahilinde olan 3 testi seçer
   - Ortalama enerji tüketimini hesaplar

### Excel Raporu
1. "Rapor Oluştur (Excel)" butonuna tıklayın
2. Dosya adı ve konum seçin
3. Rapor içeriği:
   - **Sayfa 1**: Özet bilgiler
   - **Sayfa 2**: Gidiş testleri detay (saniye-saniye)
   - **Sayfa 3**: Dönüş testleri detay (saniye-saniye)
   - **Sayfa 4**: Grafikler (opsiyonel)

## Dosya Yapısı

```
project/
├── main_gui.py              # Ana test arayüzü
├── report_gui.py            # Raporlama arayüzü
├── can_interface.py         # CAN iletişimi
├── arduino_interface.py     # Arduino kontrolü
├── edaq_interface.py        # eDAQ entegrasyonu
├── pid_controller.py        # PID kontrolcü
├── sort_profiles.py         # Test profilleri
├── data_logger.py           # Veri kaydı
├── utils.py                 # Yardımcı fonksiyonlar
├── config.json              # Yapılandırma
├── requirements.txt         # Python bağımlılıkları
├── README.md                # Bu dosya
├── arduino_firmware/
│   └── pedal_controller.ino # Arduino firmware
├── data/                    # Test verileri (CSV)
│   ├── SORT1_GIDIS_*.csv
│   └── SORT1_GIDIS_*.meta.json
└── logs/                    # Log dosyaları
    └── sort_test_*.log
```

## PID Parametre Ayarlama

### Başlangıç Değerleri
- **Kp**: 2.0 (Oransal kazanç)
- **Ki**: 0.5 (İntegral kazanç)
- **Kd**: 0.1 (Türev kazanç)

### Ayarlama İpuçları
- **Kp** çok yüksek: Salınım (oscillation)
- **Kp** çok düşük: Yavaş cevap
- **Ki** çok yüksek: Aşma (overshoot)
- **Ki** çok düşük: Kalıcı hata
- **Kd** çok yüksek: Gürültüye hassas
- **Kd** çok düşük: Ani değişimlere yavaş cevap

## Sorun Giderme

### CAN Bağlantı Hatası
1. Kvaser CANlib SDK kurulu mu kontrol edin
2. CAN cihazı bağlı mı?
3. Kanal numarası doğru mu? (genelde 0)
4. Bit rate doğru mu? (500 kbit/s)

### Arduino Bağlantı Hatası
1. Arduino USB kablosu bağlı mı?
2. COM port numarası doğru mu?
3. Firmware yüklü mü?
4. Başka program port'u kullanıyor mu?

### eDAQ Bağlantı Hatası
1. IP adresi doğru mu?
2. eDAQ aynı ağda mı?
3. Firewall engelliyor mu?
4. eDAQ cihazı açık mı?

### Test Sırasında Hız Kontrolü Sorunu
1. PID parametrelerini ayarlayın
2. Gaz pedalı yüzdesini değiştirin
3. Araç tepkisini gözlemleyin
4. Gerekirse manuel test yapın

### Veri Kaydı Hatası
1. `data/` klasörü mevcut mu?
2. Yazma izni var mı?
3. Disk doldu mu?

## Güvenlik Uyarıları

⚠️ **ÖNEMLİ GÜVENLİK BİLGİLERİ**

1. **Test Ortamı**: Kapalı test pisti veya güvenli alan kullanın
2. **Acil Durdurma**: ESC tuşu veya acil durdur butonuna erişim kolay olmalı
3. **Hız Limiti**: Güvenli bir maksimum hız belirleyin
4. **Frenleme**: Manuel frenleme segmentlerinde hazır olun
5. **Donanım Kontrolü**: Test öncesi tüm bağlantıları kontrol edin
6. **Yedekleme**: Önemli ayarları yedekleyin

## Lisans

Bu proje özel bir proje olup, tüm hakları saklıdır.

## Destek

Sorularınız için:
- Email: support@example.com
- Doküman: [Wiki sayfası]

## Sürüm Geçmişi

### v1.0.0 (2024-11-18)
- İlk sürüm
- SORT 1, 2, 3 profil desteği
- CAN, Arduino, eDAQ entegrasyonu
- PID hız kontrolü
- Raporlama modülü
