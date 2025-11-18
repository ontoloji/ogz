# CAN Bus Siber Güvenlik Test Sistemi

**Kvaser Memorator 2xHS ile Otomotiv CAN Bus Güvenlik Testi**

## ⚠️ ÖNEMLİ UYARI

**Bu yazılım SADECE aşağıdaki amaçlar için kullanılmalıdır:**

- ✅ Yetkili penetrasyon testleri
- ✅ Güvenlik araştırmaları
- ✅ Eğitim ve akademik çalışmalar
- ✅ Ürün güvenlik değerlendirmesi
- ✅ Savunma amaçlı testler

**YASAK KULLANIM ALANLARI:**

- ❌ Yetkisiz sistemlere saldırı
- ❌ Üretim ortamındaki araçlara müdahale
- ❌ Kötü niyetli saldırılar
- ❌ Trafikteki araçlara müdahale
- ❌ Yasal izni olmayan testler

**YASAL UYARI:** Yetkisiz kullanım ciddi yasal sonuçlar doğurabilir. Bu yazılımı kullanmadan önce tüm gerekli izinleri aldığınızdan emin olun.

---

## İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Özellikler](#özellikler)
3. [Kurulum](#kurulum)
4. [Hızlı Başlangıç](#hızlı-başlangıç)
5. [Saldırı Türleri](#saldırı-türleri)
6. [Kullanım Kılavuzu](#kullanım-kılavuzu)
7. [Güvenlik En İyi Uygulamaları](#güvenlik-en-iyi-uygulamaları)
8. [Sorun Giderme](#sorun-giderme)
9. [Teknik Detaylar](#teknik-detaylar)

---

## Genel Bakış

CAN Bus Siber Güvenlik Test Sistemi, otomotiv ve endüstriyel sistemlerde kullanılan CAN (Controller Area Network) bus protokolünün güvenlik açıklarını test etmek için geliştirilmiş profesyonel bir araçtır.

### Desteklenen Donanım

- **Kvaser Memorator Pro 2xHS v2**
- **Kvaser Leaf Light v2**
- **Kvaser USBcan Professional**
- Diğer Kvaser CANlib uyumlu cihazlar

### Sistem Gereksinimleri

- **İşletim Sistemi:** Windows 10/11 (64-bit)
- **Python:** 3.10 veya üzeri
- **RAM:** Minimum 4 GB
- **Disk:** 500 MB boş alan
- **Donanım:** USB 2.0/3.0 port

---

## Özellikler

### Saldırı Modları

1. **Fuzzing** - Rastgele CAN mesajları ile güvenlik açığı tespiti
2. **DoS (Denial of Service)** - Bus flooding saldırıları
3. **Spoofing** - Sahte mesaj enjeksiyonu
4. **Replay Attack** - Yakalanan mesajların tekrarı
5. **Diagnostic Attack** - UDS komut enjeksiyonu
6. **Error Frame Injection** - Hata frame saldırıları
7. **Bus Off Attack** - ECU'ları devre dışı bırakma
8. **ID Scan** - Aktif CAN ID'leri keşfi

### GUI Özellikleri

- 🎯 Sezgisel kullanıcı arayüzü
- 📊 Gerçek zamanlı CAN bus monitoring
- 📈 İstatistik ve performans metrikleri
- 💾 Mesaj yakalama ve kaydetme
- 🔧 Esnek parametre konfigürasyonu
- 📝 Detaylı log sistemi
- 💾 CSV export desteği

---

## Kurulum

### 1. Python Kurulumu

```bash
# Python versiyonunu kontrol et
python --version  # 3.10+ olmalı
```

### 2. Kvaser CANlib SDK Kurulumu

1. [Kvaser Downloads](https://www.kvaser.com/downloads-kvaser/) sayfasından **CANlib SDK** indir
2. İndirilen installer'ı çalıştır
3. Varsayılan ayarlarla kurulumu tamamla
4. Bilgisayarı yeniden başlat

### 3. Python Bağımlılıklarını Yükle

```bash
# Proje dizinine git
cd ogz

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 4. Kvaser Cihazını Bağla

1. Kvaser Memorator 2xHS'yi USB ile bilgisayara bağla
2. Windows Device Manager'da cihazın tanındığını kontrol et
3. Kvaser Hardware Configuration Tool ile cihazı test et

### 5. CAN Bus Bağlantısı

1. CAN High (CANH) ve CAN Low (CANL) kablolarını bağla
2. 120Ω terminasyon dirençlerinin yerinde olduğundan emin ol
3. CAN bus güç beslemesini kontrol et

---

## Hızlı Başlangıç

### Programı Başlatma

```bash
python can_security_gui.py
```

### İlk Test

1. **Bağlantı Kurma**
   - Kanal: 0 (varsayılan)
   - Baud Rate: 500000 (500 kbit/s)
   - "Bağlan" butonuna tıkla

2. **ID Scan Testi (Güvenli Başlangıç)**
   - Saldırı Türü: "ID Scan"
   - ID Aralığı: 0x000 - 0x7FF
   - Paket Hızı: 100 pkt/s
   - Süre: 10 saniye
   - "SALDIRIYI BAŞLAT"

3. **Sonuçları İzleme**
   - "CAN Bus Monitor" tabında gelen mesajları izle
   - İstatistikleri kontrol et
   - Log'ları incele

---

## Saldırı Türleri

### 1. Fuzzing

**Amaç:** Rastgele CAN mesajları göndererek ECU'ların beklenmedik girişlere karşı davranışını test etmek.

**Parametreler:**
- ID Aralığı: Test edilecek CAN ID aralığı (örn: 0x100-0x200)
- Paket Hızı: Saniyede gönderilecek paket sayısı
- Süre: Test süresi (saniye)
- Data Uzunluğu: 0-8 byte

**Kullanım Senaryoları:**
- Bilinmeyen ID'lerde güvenlik açığı tespiti
- Buffer overflow testi
- ECU crash tespiti
- Input validation kontrolü

**Örnek Konfigürasyon:**
```json
{
  "attack_type": "fuzzing",
  "id_range_start": "0x100",
  "id_range_end": "0x3FF",
  "packet_rate": 100,
  "duration": 60,
  "data_length": 8
}
```

**Beklenen Sonuçlar:**
- Normal: ECU'lar bilinmeyen mesajları görmezden gelir
- Güvenlik Açığı: ECU crash, reset veya beklenmedik davranış

---

### 2. DoS (Denial of Service)

**Amaç:** CAN bus'ı mesajlarla doldurarak normal iletişimi engellemek.

**Parametreler:**
- Hedef ID: Flood edilecek CAN ID (varsayılan: 0x000)
- Paket Hızı: Maksimum hız (5000+ pkt/s önerilir)
- Süre: Saldırı süresi

**Kullanım Senaryoları:**
- Bus yükü dayanıklılık testi
- Kritik mesaj gecikmesi testi
- ECU timeout davranışı testi

**Örnek Konfigürasyon:**
```json
{
  "attack_type": "dos",
  "target_id": "0x000",
  "packet_rate": 10000,
  "duration": 30
}
```

**Tehlike Seviyesi:** 🔴 YÜKSEK
- CAN bus'ı tamamen kullanılamaz hale gelebilir
- Kritik sistemler çalışmayabilir
- Sadece izole test ortamında kullanın!

---

### 3. Spoofing

**Amaç:** Belirli bir CAN ID'sine sahte veriler göndererek sistemi manipüle etmek.

**Parametreler:**
- Hedef ID: Taklit edilecek CAN ID
- Paket Hızı: Gönderim frekansı
- Süre: Saldırı süresi

**Kullanım Senaryoları:**
- Hız verisini manipüle etme (0x302)
- Motor devri taklit etme
- Sensor verilerini değiştirme
- Kontrol komutları gönderme

**Örnek Konfigürasyon:**
```json
{
  "attack_type": "spoofing",
  "target_id": "0x302",
  "packet_rate": 50,
  "duration": 20
}
```

**Örnek Hedefler:**
- **0x302:** VBOX hız mesajı
- **0x0C0:** Motor devri
- **0x200:** Body control module

**Tehlike Seviyesi:** 🟠 ORTA-YÜKSEK
- Araç davranışını değiştirebilir
- Yanlış bilgi gösterebilir

---

### 4. Replay Attack

**Amaç:** Yakalanan CAN mesajlarını tekrar göndererek yetkisiz işlemler gerçekleştirmek.

**Kullanım Adımları:**

1. **Mesaj Yakalama**
   - "Mesaj Yakalamayı Başlat" butonuna tıkla
   - İstediğin işlemi yap (örn: kilit aç, motor çalıştır)
   - "Yakalamayı Durdur"

2. **Replay Saldırısı**
   - Saldırı Türü: "Replay Attack" seç
   - Paket hızı ve süreyi ayarla
   - "SALDIRIYI BAŞLAT"

**Kullanım Senaryoları:**
- Kilit açma komutunu tekrarlama
- Motor çalıştırma sekansını replay etme
- Pencere/ayna kontrol komutlarını tekrarlama

**Örnek:**
```
# Yakalanan mesajlar:
0x2C0: 01 23 45 67 89 AB CD EF  (Kilit aç komutu)
0x2C1: 00 00 00 00 00 00 00 00  (Onay mesajı)

# Replay:
Bu mesajları tekrar göndererek kilidi açmaya çalış
```

**Tehlike Seviyesi:** 🔴 YÜKSEK
- Gerçek araç fonksiyonlarını aktive edebilir
- Güvenlik mekanizmalarını bypass edebilir

---

### 5. Diagnostic Attack

**Amaç:** UDS (Unified Diagnostic Services) protokolü ile ECU'lara diagnostic komutlar göndermek.

**UDS Servisleri:**

| Servis ID | Fonksiyon | Açıklama |
|-----------|-----------|----------|
| 0x10 | DiagnosticSessionControl | Diagnostic session başlat |
| 0x11 | ECUReset | ECU'yu reset et |
| 0x27 | SecurityAccess | Güvenlik erişimi |
| 0x22 | ReadDataByIdentifier | Veri oku |
| 0x2E | WriteDataByIdentifier | Veri yaz |
| 0x3E | TesterPresent | Session'ı canlı tut |
| 0x85 | ControlDTCSetting | DTC kontrol |

**Kullanım Senaryoları:**
- ECU'ları diagnostic mode'a alma
- Konfigürasyon verilerini okuma/yazma
- Güvenlik erişim mekanizmalarını test etme
- Firmware versiyonlarını okuma

**Örnek Konfigürasyon:**
```json
{
  "attack_type": "diagnostic",
  "target_id": "0x7DF",  // OBD-II broadcast
  "packet_rate": 10,
  "duration": 30
}
```

**Hedef ID'ler:**
- **0x7DF:** OBD-II broadcast
- **0x7E0-0x7E7:** Standart diagnostic
- **0x18DA00F1:** Extended diagnostic

**Tehlike Seviyesi:** 🟠 ORTA
- Sadece okuma yapıldığında düşük risk
- Yazma işlemleri tehlikeli olabilir

---

### 6. Error Frame Injection

**Amaç:** CAN bus'a hata frame'leri enjekte ederek ECU'ların error counter'larını artırmak.

**Not:** Bu saldırı türü özel donanım gerektirir. Standart Kvaser cihazları genellikle error frame gönderemez.

**Çalışma Prensibi:**
1. Mesaj iletimi sırasında hata sinyali gönder
2. Hedef ECU'nun error counter'ını artır
3. 255 hataya ulaştığında ECU bus-off durumuna geçer

**Tehlike Seviyesi:** 🔴 YÜKSEK
- ECU'ları tamamen devre dışı bırakabilir

---

### 7. Bus Off Attack

**Amaç:** Yüksek öncelikli ID'lerle flooding yaparak hedef ECU'nun bus-off durumuna geçmesini sağlamak.

**Çalışma Prensibi:**
1. Düşük ID'lerle (yüksek öncelik) sürekli mesaj gönder
2. Hedef ECU mesaj göndermeye çalıştığında sürekli kaybeder
3. Error counter artışı ile bus-off durumuna geçer

**Örnek Konfigürasyon:**
```json
{
  "attack_type": "bus_off",
  "id_range_start": "0x000",
  "id_range_end": "0x010",
  "packet_rate": 10000,
  "duration": 60
}
```

**Tehlike Seviyesi:** 🔴 YÜKSEK
- Kritik ECU'ları devre dışı bırakabilir

---

### 8. ID Scan

**Amaç:** CAN bus'ta aktif ID'leri keşfetmek ve haritalandırmak.

**Kullanım:**
- Bus üzerindeki tüm aktif ID'leri tespit et
- Hangi ECU'ların hangi ID'leri kullandığını öğren
- Ters mühendislik için temel oluştur

**Örnek Konfigürasyon:**
```json
{
  "attack_type": "id_scan",
  "id_range_start": "0x000",
  "id_range_end": "0x7FF",
  "packet_rate": 100,
  "duration": 82  // 2048 ID / 100 pkt/s ≈ 20s + marj
}
```

**Analiz:**
1. Monitor tabında gelen yanıtları gözlemle
2. Hangi ID'lere yanıt geldiğini not et
3. ID pattern'lerini analiz et:
   - 0x000-0x0FF: Yüksek öncelikli sistem mesajları
   - 0x100-0x1FF: Powertrain
   - 0x200-0x2FF: Body control
   - 0x300-0x3FF: Chassis
   - 0x400-0x7FF: Diğer sistemler

**Tehlike Seviyesi:** 🟢 DÜŞÜK
- Pasif dinleme ile de yapılabilir
- Bus'a minimum etki

---

## Kullanım Kılavuzu

### Ana Pencere

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ CAN BUS SİBER GÜVENLİK TEST SİSTEMİ ⚠️              │
├─────────────────────────────────────────────────────────┤
│ [CAN Bağlantısı]  [İstatistikler]                      │
│                                                         │
│ [Saldırı Kontrolü] [CAN Monitor] [Log]                 │
│                                                         │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### Bağlantı Paneli

1. **Kanal:** Kvaser cihazın kanal numarası (0-7)
2. **Baud Rate:** CAN bus hızı
   - 125000 = 125 kbit/s (Düşük hız)
   - 250000 = 250 kbit/s
   - 500000 = 500 kbit/s (Standart)
   - 1000000 = 1 Mbit/s (Yüksek hız)
3. **Bağlan:** Bağlantıyı başlat/durdur

### Saldırı Kontrolü

1. **Saldırı Türü:** Yukarıda açıklanan 8 türden birini seç
2. **Parametreler:** Saldırıya özel ayarları yap
3. **SALDIRIYI BAŞLAT:** Onaydan sonra saldırıyı başlat
4. **SALDIRIYI DURDUR:** Saldırıyı anında durdur

### CAN Bus Monitor

- Gerçek zamanlı CAN mesajlarını görüntüle
- CSV'ye aktar
- Mesaj filtreleme (gelecek versiyonda)

### Log Paneli

- Detaylı sistem logları
- Hata mesajları
- Saldırı durumu güncellemeleri

---

## Güvenlik En İyi Uygulamaları

### Test Ortamı

✅ **YAPILMASI GEREKENLER:**

1. **İzole Test Ortamı**
   - Kapalı devre test pisti
   - Bench test düzeneği
   - Simülatör ortamı

2. **Yetkilendirme**
   - Yazılı test izni
   - Proje onayı
   - Güvenlik protokol uygulaması

3. **Dokümantasyon**
   - Tüm testleri kaydet
   - Sonuçları dokümante et
   - Risk değerlendirmesi yap

4. **Güvenlik Önlemleri**
   - Araç park freninde
   - Motor kapalı (gerekmedikçe)
   - Güvenli duruş mesafesi

❌ **YAPILMAMASI GEREKENLER:**

1. **Asla yapma:**
   - Trafikteki araçlara test
   - Yetkisiz sistemlere saldırı
   - Üretim ortamında test
   - Güvenlik backupu olmadan kritik test

### Test Prosedürü

```
1. PRE-TEST
   ├─ Risk değerlendirmesi
   ├─ Yetkilendirme kontrolü
   ├─ Ekipman kontrolü
   └─ Backup/Recovery planı

2. TEST
   ├─ Düşük riskli testlerle başla (ID Scan)
   ├─ Sonuçları sürekli izle
   ├─ Beklenmedik davranışta dur
   └─ Tüm adımları kaydet

3. POST-TEST
   ├─ Sistem durumunu kontrol et
   ├─ Normal çalışmaya dön
   ├─ Sonuçları analiz et
   └─ Rapor hazırla
```

### Acil Durum Prosedürü

**Problem:** ECU yanıt vermiyor

1. Saldırıyı durdur
2. CAN bağlantısını kes
3. Sistemi power cycle yap
4. Diagnostic tarama yap
5. Gerekirse fabrika ayarlarına dön

**Problem:** Bus tamamen kilitlendi

1. Tüm test ekipmanlarının bağlantısını kes
2. Ana güç beslemesini kes
3. 30 saniye bekle
4. Sistemi yeniden başlat
5. Minimal konfigürasyonla test et

---

## Sorun Giderme

### Kvaser Bağlantı Sorunları

**Problem:** "CANlib kütüphanesi bulunamadı"

**Çözüm:**
```bash
# 1. Kvaser CANlib SDK kurulu mu kontrol et
# Windows: C:\Program Files (x86)\Kvaser\CANlib\

# 2. Python canlib modülünü yeniden yükle
pip uninstall canlib
pip install canlib

# 3. Python path kontrolü
python -c "import canlib; print(canlib.__file__)"
```

---

**Problem:** "CAN bağlantı hatası"

**Çözüm:**
1. Device Manager'da Kvaser cihazını kontrol et
2. USB kablosunu değiştir
3. Farklı USB porta dene
4. Kvaser Hardware Configuration Tool ile test et
5. Driver'ı güncelle

---

**Problem:** "Timeout" hataları

**Çözüm:**
1. CAN bus terminasyon dirençlerini kontrol et (120Ω x 2)
2. Baud rate ayarını doğrula
3. Bus kablo uzunluğunu kontrol et (<40m @ 500kbit/s)
4. Bus yükünü azalt

---

### Saldırı Sorunları

**Problem:** Saldırı etkisiz

**Çözüm:**
1. Hedef ID'nin doğru olduğunu kontrol et
2. Paket hızını artır
3. Data formatını kontrol et
4. Bus monitoring ile mesajların gittiğini doğrula

---

**Problem:** "Bus off" durumu

**Çözüm:**
```bash
# 1. Saldırıyı durdur
# 2. Bağlantıyı kes
# 3. 5 saniye bekle
# 4. Yeniden bağlan
```

---

## Teknik Detaylar

### CAN Bus Temelleri

**CAN Frame Yapısı:**
```
┌────┬────┬───┬────┬─────────┬────┬────┬───┐
│SOF │ ID │RTR│ DLC│  DATA   │CRC │ACK │EOF│
└────┴────┴───┴────┴─────────┴────┴────┴───┘
```

- **SOF:** Start of Frame (1 bit)
- **ID:** Identifier (11-bit standard, 29-bit extended)
- **RTR:** Remote Transmission Request
- **DLC:** Data Length Code (0-8)
- **DATA:** 0-8 bytes veri
- **CRC:** Cyclic Redundancy Check
- **ACK:** Acknowledgment
- **EOF:** End of Frame

**Arbitration:**
- Düşük ID = Yüksek öncelik
- Örn: 0x000 > 0x7FF
- Collision durumunda düşük ID kazanır

**Baud Rate Hesaplama:**
```
Bit Time = 1 / Baud Rate
500 kbit/s = 2 μs/bit
250 kbit/s = 4 μs/bit
```

**Bus Kapasitesi:**
```
Max throughput @ 500kbit/s:
- 1 frame = 128 bits (worst case)
- Max: ~3900 frames/second
- Pratikte: ~2000-3000 frames/second (bus load %40-60)
```

### Programlama API'si

**Temel Kullanım:**

```python
from can_security_attacks import CANSecurityTester, AttackType, AttackConfig

# Tester oluştur
tester = CANSecurityTester(channel=0, bitrate=500000)

# Bağlan
if tester.connect():
    # Fuzzing saldırısı konfigüre et
    config = AttackConfig(
        attack_type=AttackType.FUZZING,
        id_range_start=0x100,
        id_range_end=0x200,
        packet_rate=100,
        duration=10,
        data_length=8
    )

    # Saldırıyı başlat
    tester.start_attack(config)

    # İstatistikleri al
    stats = tester.get_statistics()
    print(f"Gönderilen: {stats['packets_sent']}")

    # Durdur
    tester.stop_attack()
    tester.disconnect()
```

**Callback Kullanımı:**

```python
def status_callback(status, data):
    print(f"Durum: {status}, Data: {data}")

def message_callback(frame):
    print(f"Mesaj: ID=0x{frame.id:03X}, Data={frame.data.hex()}")

tester.set_status_callback(status_callback)
tester.set_message_callback(message_callback)
```

**Replay Attack:**

```python
# Mesaj yakala
tester.start_capture()
time.sleep(10)  # 10 saniye yakala
messages = tester.stop_capture()

# Replay
config = AttackConfig(
    attack_type=AttackType.REPLAY,
    replay_messages=messages,
    packet_rate=50,
    duration=20
)
tester.start_attack(config)
```

---

## Log Dosyaları

**Log Konumu:** `logs/can_security_YYYYMMDD_HHMMSS.log`

**Log Formatı:**
```
2024-11-18 10:30:45,123 - can_security_attacks - INFO - CAN bağlantısı başarılı
2024-11-18 10:30:50,456 - can_security_attacks - WARNING - Saldırı başlatıldı: fuzzing
2024-11-18 10:31:00,789 - can_security_attacks - INFO - Saldırı durduruldu: 1000 paket gönderildi
```

**Log Seviyeleri:**
- **DEBUG:** Detaylı debug bilgisi
- **INFO:** Normal bilgi mesajları
- **WARNING:** Uyarı mesajları (saldırı başlatma/durdurma)
- **ERROR:** Hata mesajları
- **CRITICAL:** Kritik hatalar

---

## Sık Sorulan Sorular

**S: Hangi araçlarda kullanılabilir?**

C: CAN bus kullanan tüm araçlarda (2008 sonrası çoğu araç). Ancak **sadece yetkili test ortamında** kullanılmalıdır.

---

**S: Yasal mı?**

C: Yetkili güvenlik testleri, araştırma ve eğitim amaçlı kullanım yasaldır. Yetkisiz kullanım yasa dışıdır.

---

**S: Gerçek hasara yol açabilir mi?**

C: Evet, agresif saldırılar ECU'lara zarar verebilir veya araç davranışını etkileyebilir. Bu yüzden **sadece kontrollü ortamlarda** test edin.

---

**S: Kaç tane saldırıyı aynı anda çalıştırabilirim?**

C: Bir seferde sadece bir saldırı. Birden fazla saldırı için birden fazla Kvaser cihazı gerekir.

---

**S: Mock mode ne işe yarar?**

C: Kvaser cihazı olmadan yazılımı test etmek için. Gerçek CAN bus kullanmaz.

---

## Gelecek Özellikler

- [ ] ISO-TP (ISO 15765-2) desteği
- [ ] CAN-FD desteği
- [ ] Otomatik saldırı senaryoları
- [ ] Gelişmiş mesaj filtreleme
- [ ] Real-time grafik analiz
- [ ] Multi-channel saldırıları
- [ ] Saldırı rapor şablonları
- [ ] Database DBC dosya desteği

---

## Lisans ve Sorumluluk Reddi

Bu yazılım eğitim ve araştırma amaçlı geliştirilmiştir. Yazılımın kullanımından doğacak tüm sorumluluk kullanıcıya aittir. Geliştiriciler hiçbir şekilde sorumlu tutulamaz.

**Kullanım öncesi:**
1. Tüm yasal izinleri alın
2. Risk değerlendirmesi yapın
3. Güvenlik protokollerini uygulayın
4. Yetkili personel gözetiminde çalışın

---

## İletişim ve Destek

**Teknik Destek:**
- GitHub Issues: [Proje repository'si]
- E-posta: [Destek e-postası]

**Güvenlik Açığı Bildirimi:**
- Bu yazılımda güvenlik açığı bulduysanız sorumlu açıklama yapın
- security@example.com

---

## Referanslar

1. **CAN Specification**
   - ISO 11898-1:2015 - Road vehicles — Controller area network (CAN)

2. **UDS Protocol**
   - ISO 14229-1:2013 - Unified diagnostic services (UDS)

3. **Automotive Security**
   - SAE J3061 - Cybersecurity Guidebook for Cyber-Physical Vehicle Systems

4. **Kvaser Documentation**
   - CANlib SDK Documentation
   - Kvaser Memorator 2xHS User Guide

5. **Research Papers**
   - "Comprehensive Experimental Analyses of Automotive Attack Surfaces" (USENIX Security 2011)
   - "Adventures in Automotive Networks and Control Units" (DEF CON 21)

---

**Versiyon:** 1.0.0
**Tarih:** 2024-11-18
**Yazar:** CAN Security Research Team

---

*Bu dokümantasyon sürekli güncellenmektedir. En son versiyon için repository'yi kontrol edin.*
