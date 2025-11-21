# CAN Bus Analyzer - Kurulum Kılavuzu

Windows 10/11 için detaylı kurulum talimatları.

## İçindekiler

1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kvaser CANlib SDK Kurulumu](#kvaser-canlib-sdk-kurulumu)
3. [Python Kurulumu](#python-kurulumu)
4. [Proje Kurulumu](#proje-kurulumu)
5. [Test ve Doğrulama](#test-ve-doğrulama)
6. [Sorun Giderme](#sorun-giderme)

---

## Sistem Gereksinimleri

### Minimum Gereksinimler
- **İşletim Sistemi**: Windows 10 64-bit
- **RAM**: 4 GB
- **Disk Alanı**: 500 MB (kurulum + veri için)
- **Python**: 3.9 veya üzeri
- **CAN Interface**: Kvaser USB CAN interface

### Önerilen Gereksinimler
- **İşletim Sistemi**: Windows 11 64-bit
- **RAM**: 8 GB
- **Disk Alanı**: 2 GB
- **Python**: 3.11 veya 3.12
- **CAN Interface**: Kvaser Leaf Light v2 veya üzeri

---

## Kvaser CANlib SDK Kurulumu

### Adım 1: SDK İndirme

1. [Kvaser Downloads](https://www.kvaser.com/downloads-kvaser/) sayfasını açın
2. "Drivers" bölümünden **"CANlib SDK"** seçeneğini bulun
3. Windows için uygun versiyonu indirin:
   - 64-bit Windows için: `canlib_x64_setup.exe`
   - 32-bit Windows için: `canlib_x86_setup.exe`

### Adım 2: SDK Kurulumu

1. İndirilen kurulum dosyasını **yönetici olarak** çalıştırın
2. Kurulum sihirbazını takip edin:
   - **License Agreement**: Kabul edin
   - **Installation Type**: "Complete" seçin
   - **Installation Path**: Varsayılan yolu kullanın
3. "Install" butonuna tıklayın
4. Kurulum tamamlandığında "Finish" tıklayın
5. **Bilgisayarı yeniden başlatın**

### Adım 3: Driver Doğrulama

1. Kvaser cihazınızı USB'ye takın
2. Cihaz Yöneticisi'ni açın (`devmgmt.msc`)
3. "Kvaser Hardware" altında cihazınızı kontrol edin
4. Driver durumu "Bu aygıt düzgün çalışıyor" olmalı

**Alternatif Doğrulama:**
```
Başlat → Kvaser → CANlib SDK → Device Guide
```

---

## Python Kurulumu

### Adım 1: Python İndirme

1. [Python.org](https://www.python.org/downloads/) adresine gidin
2. Python 3.11 veya 3.12 sürümünü indirin
3. İndirilen `.exe` dosyasını çalıştırın

### Adım 2: Python Kurulumu

**ÖNEMLİ**: Kurulum sırasında:
1. ✅ **"Add Python to PATH"** kutucuğunu işaretleyin
2. "Install Now" seçeneğini seçin
3. Kurulum tamamlanana kadar bekleyin
4. "Close" butonuna tıklayın

### Adım 3: Python Doğrulama

Komut İstemi'ni (CMD) açın ve şunu yazın:
```bash
python --version
```

Çıktı şöyle olmalı:
```
Python 3.11.x
```

---

## Proje Kurulumu

### Yöntem 1: Standalone EXE (Kullanıcılar için)

1. `dist` klasöründen `CAN_Bus_Analyzer.exe` dosyasını istediğiniz konuma kopyalayın
2. Çift tıklayarak çalıştırın
3. İlk çalıştırmada Windows Güvenlik uyarısı çıkarsa:
   - "Daha fazla bilgi" → "Yine de çalıştır"

### Yöntem 2: Kaynak Koddan (Geliştiriciler için)

#### Adım 1: Proje Klasörünü Oluşturma

```bash
# İstediğiniz konuma gidin
cd C:\Users\YourName\Projects

# Proje klasörünü oluşturun veya klonlayın
git clone <repository-url>
cd can_bus_analyzer
```

#### Adım 2: Virtual Environment Oluşturma

```bash
# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktif et
venv\Scripts\activate

# Aktif olduğunu doğrula (prompt başında (venv) görünmeli)
```

#### Adım 3: Bağımlılıkları Yükleme

```bash
# Tüm paketleri yükle
pip install -r requirements.txt

# Yüklemenin başarılı olduğunu kontrol et
pip list
```

Beklenen paketler:
- python-can
- cantools
- pandas
- matplotlib
- openpyxl
- numpy
- pyinstaller

#### Adım 4: Uygulamayı Çalıştırma

```bash
# src klasörüne git
cd src

# Uygulamayı başlat
python can_analyzer_gui.py
```

---

## Test ve Doğrulama

### Temel Fonksiyon Testi

1. **Uygulama Başlatma Testi**
   ```bash
   cd src
   python can_analyzer_gui.py
   ```
   Beklenen: GUI penceresi açılmalı

2. **CAN Bağlantı Testi**
   - Kvaser cihazını bağlayın
   - "Kanal: 0", "Bitrate: 500000" seçin
   - "Bağlan" butonuna tıklayın
   - Beklenen: "Bağlı" durumu yeşil renkte

3. **DBC Yükleme Testi**
   - "DBC Yükle" butonuna tıklayın
   - `examples/example.dbc` dosyasını seçin
   - Beklenen: "Yüklü: example.dbc" mesajı

4. **Mesaj Okuma Testi**
   - CAN bus'a bağlı olduğunuzdan emin olun
   - "Mesaj Monitör" sekmesine gidin
   - Beklenen: Gelen mesajlar tabloda görünmeli

### Modül Testleri

Her modülün test fonksiyonunu çalıştırabilirsiniz:

```bash
cd src

# CAN Reader test
python can_reader.py

# DBC Parser test
python dbc_parser.py

# Log Reader test
python log_reader.py

# Data Exporter test
python data_exporter.py

# Plotter test
python plotter.py
```

---

## Sorun Giderme

### 1. "python komutu tanınmıyor" Hatası

**Sebep**: Python PATH'e eklenmemiş

**Çözüm**:
1. Python'u kaldırın
2. Tekrar kurarken "Add Python to PATH" seçeneğini işaretleyin
3. Veya manuel olarak PATH'e ekleyin:
   - Sistem Özellikleri → Gelişmiş → Ortam Değişkenleri
   - Path değişkenine Python yolunu ekleyin

### 2. "ModuleNotFoundError: No module named 'can'" Hatası

**Sebep**: python-can paketi kurulmamış

**Çözüm**:
```bash
pip install python-can
# veya
pip install -r requirements.txt
```

### 3. "CAN Bus'a bağlanılamadı" Hatası

**Olası Sebepler ve Çözümler**:

a) **Kvaser driver kurulu değil**
   - CANlib SDK'yi yükleyin
   - Bilgisayarı yeniden başlatın

b) **Cihaz tanınmıyor**
   - USB bağlantısını kontrol edin
   - Cihaz Yöneticisi'nde kontrol edin
   - Başka bir USB portuna takın

c) **Kanal numarası yanlış**
   - Kanal 0'dan başlayıp sırayla deneyin
   - Kvaser Device Guide'dan kanal bilgisini kontrol edin

d) **Cihaz başka program tarafından kullanılıyor**
   - Diğer CAN araçlarını kapatın
   - Bilgisayarı yeniden başlatın

### 4. "DBC dosyası yüklenemedi" Hatası

**Çözümler**:
- DBC formatının doğru olduğundan emin olun
- Dosya yolunda Türkçe/özel karakter olmamalı
- Dosya izinlerini kontrol edin
- Örnek dosyayı (`examples/example.dbc`) deneyin

### 5. "Import Error: DLL load failed" Hatası

**Sebep**: Visual C++ Redistributable eksik

**Çözüm**:
1. [Microsoft C++ Redistributable](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads) indirin
2. Hem x86 hem x64 versiyonlarını kurun
3. Bilgisayarı yeniden başlatın

### 6. Grafik Görünmüyor

**Çözümler**:
1. DBC dosyasının yüklü olduğundan emin olun
2. Sol panelden en az bir sinyal seçin
3. "Grafik Güncelle" butonuna tıklayın
4. CAN bus'a bağlı olduğundan emin olun
5. Mesajların geldiğini "Mesaj Monitör"den kontrol edin

### 7. EXE Oluşturamıyorum

**Çözümler**:

a) **PyInstaller kurulu değil**
   ```bash
   pip install pyinstaller
   ```

b) **Build scripti çalışmıyor**
   ```bash
   # Yönetici olarak CMD açın
   cd can_bus_analyzer
   build_exe.bat
   ```

c) **Manuel build**
   ```bash
   pyinstaller can_analyzer.spec
   ```

### 8. Yüksek CPU Kullanımı

**Çözümler**:
- `config.json` dosyasında `update_interval_ms` değerini artırın (örn: 200)
- "Grafik Güncelle" öncesi gereksiz sinyalleri kaldırın
- Mesaj filtreleme kullanın

---

## Ek Kaynaklar

### Kvaser Dokümantasyonu
- [CANlib Documentation](https://www.kvaser.com/developer/canlib-sdk/)
- [CANlib API Reference](https://www.kvaser.com/canlib-webhelp/)

### Python-CAN Dokümantasyonu
- [python-can Documentation](https://python-can.readthedocs.io/)
- [python-can Kvaser Interface](https://python-can.readthedocs.io/en/stable/interfaces/kvaser.html)

### DBC Format
- [DBC File Format](https://www.csselectronics.com/pages/can-dbc-file-database-intro)
- [CANtools Documentation](https://cantools.readthedocs.io/)

---

## Destek

Sorunlarınız devam ediyorsa:
1. Log dosyasını (`can_analyzer.log`) kontrol edin
2. Hata mesajını tam olarak kopyalayın
3. Sistem bilgilerinizi not alın:
   - Windows versiyonu
   - Python versiyonu
   - Kvaser cihaz modeli
   - Hata mesajı
4. Issue açın veya destek isteyin

---

**Son Güncelleme**: 2024
**Versiyon**: 1.0.0
