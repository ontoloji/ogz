# SORT Test Otomasyon Sistemi

Windows ortamında çalışan, elektrikli ve içten yanmalı araçların UITP SORT standardına uygun enerji tüketimi testlerini otomatik olarak gerçekleştiren Python tabanlı test otomasyon yazılımı.

## Özellikler

- **3 Farklı SORT Profili**: SORT 1, 2 ve 3 test profilleri
- **Çoklu Araç Desteği**: Elektrikli araç (CAN), DAF Motor, IBK
- **Otomatik Hız Kontrolü**: PID tabanlı sabit hız kontrolü
- **Gerçek Zamanlı Grafik**: Hız, mesafe ve enerji tüketimi grafikleri
- **Veri Kayıt**: CSV formatında saniye-saniye test verileri
- **Raporlama**: Excel formatında detaylı test raporları
- **Güvenlik**: Acil durdurma, hız limiti kontrolü, bağlantı izleme

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

### Kvaser CAN Mesaj Logger Başlatma
```bash
python kvaser_message_logger.py
```

## Kvaser CAN Mesaj Logger Kullanımı

Kvaser Memorator 2xHS cihazından CAN mesajlarını loglayan bağımsız bir araçtır.

### Özellikler
- **DBC Dosyası Desteği**: DBC dosyası yükleyip mesajları seçebilme
- **Manuel Mesaj Girişi**: DBC olmadan mesaj ID ve byte bilgisi girişi (30 mesaja kadar)
- **Esnek Loglama**: İstediğiniz sıklıkla (1ms - 10s arası) CSV loglama
- **Otomatik Tarihleme**: Log dosyalarına otomatik tarih-saat damgası ekleme
- **Çoklu Mesaj**: Birden fazla mesajı aynı anda loglama
- **Gerçek Zamanlı İzleme**: Gelen mesajları anlık görüntüleme

### Kullanım Adımları

#### 1. CAN Cihazı Bağlantısı
1. Kanal numarasını seçin (genelde 0)
2. Bitrate'i seçin (varsayılan: 500 kbit/s)
3. "Bağlan" butonuna tıklayın

#### 2. Mesaj Ekleme - DBC ile
1. "Gözat..." butonuna tıklayarak DBC dosyası seçin
2. "DBC Yükle" butonuna tıklayın
3. Açılan listeden mesaj seçin
4. "DBC Mesajı Ekle" butonuna tıklayın
5. Tabloda mesajın "Aktif" kutucuğunu işaretleyin

#### 3. Mesaj Ekleme - Manuel
1. Mesaj ID'yi hex (0x123) veya decimal (291) formatında girin
2. Mesaj adı girin (opsiyonel)
3. "Manuel Mesaj Ekle" butonuna tıklayın
4. Tabloda mesajın "Aktif" kutucuğunu işaretleyin
5. Maksimum 30 manuel mesaj ekleyebilirsiniz

#### 4. Loglama Ayarları
1. Log dosyası ismi girin (örn: "test_log")
2. İsterseniz "Klasör Seç" ile kayıt klasörünü değiştirin
3. Loglama sıklığını ayarlayın:
   - 0.001 saniye = 1000 Hz
   - 0.01 saniye = 100 Hz
   - 0.1 saniye = 10 Hz (varsayılan)
   - 1.0 saniye = 1 Hz

#### 5. Loglama Başlatma
1. En az bir mesajın "Aktif" olduğundan emin olun
2. "Loglamayı Başlat" butonuna tıklayın
3. Log dosyası otomatik olarak şu formatta oluşturulur:
   ```
   test_log_20241118_143025.csv
   (isim_YYYYMMDD_HHMMSS.csv)
   ```

#### 6. Loglama Durdurma
1. "Loglamayı Durdur" butonuna tıklayın
2. Dosya otomatik olarak kaydedilip kapatılır

### CSV Dosya Formatı

#### DBC Mesajları için
```csv
Timestamp,Time_ms,Message_Name,Message_ID,Signal1,Signal2,...
2024-11-18 14:30:25.123,1234567,EngineSpeed,0x123,1500,85,...
```

#### Manuel Mesajlar için
```csv
Timestamp,Time_ms,Message_Name,Message_ID,Byte0,Byte1,Byte2,...
2024-11-18 14:30:25.123,1234567,MSG_0x456,0x456,0x12,0x34,0x56,...
```

### İpuçları

- **DBC Mesajları**: Sinyal isimleri ve değerleri otomatik parse edilir
- **Manuel Mesajlar**: Ham byte değerleri hex formatında loglanır
- **Gerçek Zamanlı İzleme**: Tabloda "Son Veri" sütununda gelen mesajları görebilirsiniz
- **Mesaj Yönetimi**: İstemediğiniz mesajları "Aktif" kutucuğunu kaldırarak devre dışı bırakabilirsiniz
- **Çoklu Test**: Farklı mesaj setleri için tablodaki mesajları temizleyip yeni mesajlar ekleyebilirsiniz

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
├── main_gui.py                  # Ana test arayüzü
├── report_gui.py                # Raporlama arayüzü
├── kvaser_message_logger.py     # CAN mesaj logger (bağımsız araç)
├── can_interface.py             # CAN iletişimi
├── arduino_interface.py         # Arduino kontrolü
├── edaq_interface.py            # eDAQ entegrasyonu
├── pid_controller.py            # PID kontrolcü
├── sort_profiles.py             # Test profilleri
├── data_logger.py               # Veri kaydı
├── utils.py                     # Yardımcı fonksiyonlar
├── config.json                  # Yapılandırma
├── requirements.txt             # Python bağımlılıkları
├── README.md                    # Bu dosya
├── arduino_firmware/
│   └── pedal_controller.ino     # Arduino firmware
├── data/                        # Test verileri (CSV)
│   ├── SORT1_GIDIS_*.csv
│   └── SORT1_GIDIS_*.meta.json
└── logs/                        # Log dosyaları
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
