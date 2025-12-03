# 📦 Internet Radyo Çalar - EXE Build Kılavuzu

Bu doküman, Internet Radyo Çalar uygulamasını Windows EXE dosyası olarak nasıl derleyeceğinizi açıklar.

## 🎯 Genel Bakış

PyInstaller kullanarak Python uygulamasını bağımsız bir Windows EXE dosyasına dönüştürebilirsiniz. İki farklı build tipi mevcuttur:

### Build Tipleri

| Tip | Dosya | Boyut | Başlatma | Kullanım |
|-----|-------|-------|----------|----------|
| **Tek Dosya** | `InternetRadyoCalar.exe` | ~80 MB | Yavaş | Portable, USB'den çalıştırma |
| **Klasör** | `InternetRadyoCalar/` | ~60 MB | Hızlı | Kurulum, Program Files |

## 🚀 Hızlı Başlangıç

### Otomatik Build (Önerilen)

```batch
# 1. Build scriptini çalıştırın
build_exe.bat

# 2. Build tipini seçin (1, 2, veya 3)
# 3. Bekleyin...
# 4. dist/ klasöründe EXE dosyanız hazır!
```

### Manuel Build

```batch
# Bağımlılıkları yükleyin
pip install pyinstaller PyQt5 python-vlc

# Tek dosya için
pyinstaller --clean internet_radio_player.spec

# Klasör için
pyinstaller --clean internet_radio_player_folder.spec
```

## 📋 Ön Gereksinimler

### Sistem Gereksinimleri
- **Windows 10/11** (64-bit önerilir)
- **Python 3.8 - 3.11** (3.11 önerilir)
- En az **200 MB** boş disk alanı

### Python Paketleri

```bash
pip install pyinstaller
pip install PyQt5>=5.15.0
pip install python-vlc>=3.0.0
```

Veya tek komutla:

```bash
pip install pyinstaller -r radio_requirements.txt
```

## 🔧 Detaylı Build Adımları

### 1. Hazırlık

#### İkon Dosyası (Opsiyonel)

Uygulama ikonu eklemek için:

**Seçenek A - Otomatik Oluşturma:**
```bash
pip install Pillow
python create_icon.py
```

**Seçenek B - Manuel:**
1. `radio_icon.ico` dosyası edinin (256x256 önerilir)
2. Proje klasörüne koyun
3. Spec dosyası otomatik olarak kullanacaktır

**Seçenek C - İkonsuz:**
- İkon olmadan da build yapabilirsiniz
- Varsayılan Python ikonu kullanılır

#### Dosya Kontrolü

Aşağıdaki dosyaların mevcut olduğundan emin olun:
```
✓ internet_radio_player.py
✓ internet_radio_player.spec
✓ internet_radio_player_folder.spec
✓ build_exe.bat
✓ RADIO_README.md
✓ radio_favorites_example.json
✓ ambient_sounds.py
✓ download_sounds.py
✓ AMBIENT_SOUNDS_README.md
✓ sounds/ (klasör)
✓ radio_icon.ico (opsiyonel)
```

### 2. Build Süreci

#### Otomatik Build

```batch
build_exe.bat
```

Script şunları yapar:
1. Python ve bağımlılıkları kontrol eder
2. Eksik paketleri yükler
3. Eski build'leri temizler
4. Seçtiğiniz build tipini oluşturur
5. Gerekli dosyaları kopyalar

#### Manuel Build Komutları

**Tek Dosya Build:**
```batch
# Eski build'leri temizle
rmdir /s /q dist build

# Build
pyinstaller --clean internet_radio_player.spec

# Sonuç: dist\InternetRadyoCalar.exe
```

**Klasör Build:**
```batch
# Eski build'leri temizle
rmdir /s /q dist build

# Build
pyinstaller --clean internet_radio_player_folder.spec

# Sonuç: dist\InternetRadyoCalar\ klasörü
```

### 3. Build Sonrası

Build tamamlandığında `dist/` klasöründe:

**Tek Dosya Build:**
```
dist/
└── InternetRadyoCalar.exe    (~80 MB)
```

**Klasör Build:**
```
dist/
└── InternetRadyoCalar/
    ├── InternetRadyoCalar.exe
    ├── python311.dll
    ├── Qt5Core.dll
    ├── Qt5Gui.dll
    ├── Qt5Widgets.dll
    ├── _internal/           (Tüm bağımlılıklar)
    ├── RADIO_README.md
    ├── AMBIENT_SOUNDS_README.md
    ├── ambient_sounds.py
    ├── download_sounds.py
    ├── radio_favorites_example.json
    └── sounds/              (Ses dosyaları klasörü - boş)
```

## 📦 Dağıtım

### Kullanıcılara Ne Göndermeli?

#### Tek Dosya (Portable)
```
InternetRadyoCalar.exe          # Ana uygulama
RADIO_README.md                 # Radyo kullanım kılavuzu
AMBIENT_SOUNDS_README.md        # Ambient sesler kılavuzu
ambient_sounds.py               # Ses tanımları (gerekli)
download_sounds.py              # Ses indirme scripti
radio_favorites_example.json    # Örnek favoriler
sounds/                         # Ses dosyaları klasörü (kullanıcı dolduracak)
```

**Önemli:** Ambient sesler için kullanıcılar `sounds/` klasörüne kendi ses dosyalarını eklemeli.
`download_sounds.py` scriptini çalıştırarak hangi seslerin gerekli olduğunu görebilirler.

#### Klasör Versiyonu
```
InternetRadyoCalar/            # Tüm klasör
RADIO_README.md                # Kullanım kılavuzu (klasör içinde zaten var)
```

Kullanıcılar klasörü açıp `InternetRadyoCalar.exe`'yi çalıştırır.

### ⚠️ Önemli Kullanıcı Gereksinimleri

**VLC Media Player Zorunludur:**

Kullanıcıların sisteminde VLC kurulu olmalıdır:
- İndirme: https://www.videolan.org/vlc/
- Windows 64-bit veya 32-bit (sistem mimarisine uygun)
- En son sürüm önerilir

### 📤 Paylaşım Yöntemleri

**Yöntem 1 - ZIP Arşivi:**
```batch
# Tek dosya için
powershell Compress-Archive -Path "dist\InternetRadyoCalar.exe", "RADIO_README.md" -DestinationPath "InternetRadyoCalar_Portable.zip"

# Klasör için
powershell Compress-Archive -Path "dist\InternetRadyoCalar\*" -DestinationPath "InternetRadyoCalar.zip"
```

**Yöntem 2 - Installer (İleri Seviye):**
- NSIS (Nullsoft Scriptable Install System)
- Inno Setup
- WiX Toolset

**Yöntem 3 - Doğrudan Paylaşım:**
- Google Drive, Dropbox, OneDrive
- GitHub Releases
- Özel sunucu

## 🐛 Sorun Giderme

### Build Hataları

#### "PyInstaller not found"
```bash
pip install pyinstaller
```

#### "Failed to execute script"
- Python sürümünüzü kontrol edin (3.8-3.11)
- Sanal ortam (venv) kullanmayı deneyin
- `--debug all` parametresi ile detaylı log alın:
  ```batch
  pyinstaller --debug all internet_radio_player.spec
  ```

#### "Module not found" hatası
```bash
# Tüm bağımlılıkları yeniden yükleyin
pip uninstall PyQt5 python-vlc
pip install PyQt5>=5.15.0 python-vlc>=3.0.0
```

#### Build çok uzun sürüyor
- Normal: 2-5 dakika
- UPX (sıkıştırma) devre dışı bırakabilirsiniz:
  Spec dosyasında `upx=False` yapın

### Çalışma Zamanı Hataları

#### "libvlc.dll not found"
**Sorun:** VLC kurulu değil

**Çözüm:**
1. VLC Media Player'ı yükleyin
2. 64-bit Python → 64-bit VLC
3. 32-bit Python → 32-bit VLC

#### "Failed to load platform plugin windows"
**Sorun:** Qt platformu bulunamadı

**Çözüm:**
```batch
# Spec dosyasını düzenleyin, datas kısmına ekleyin:
datas=[
    ('C:\\Python311\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms', 'platforms'),
]
```

#### EXE yavaş başlıyor
**Sorun:** Tek dosya build kullanıyorsunuz

**Çözüm:**
- Klasör build'i kullanın (10-20x daha hızlı)
- Veya antivirüs exclude listesine ekleyin

### Boyut Optimizasyonu

EXE boyutunu küçültmek için:

1. **Gereksiz modülleri hariç tutun:**
   Spec dosyasında `excludes` listesini genişletin

2. **UPX sıkıştırma:**
   - UPX indirin: https://upx.github.io/
   - PATH'e ekleyin
   - Spec dosyasında `upx=True`

3. **Strip debug symbols:**
   ```batch
   pyinstaller --strip internet_radio_player.spec
   ```

## 📊 Build Karşılaştırması

### Boyut Karşılaştırması

| Build Tipi | EXE Boyutu | Toplam Boyut | Sıkıştırılmış (ZIP) |
|-----------|-----------|--------------|-------------------|
| Tek Dosya | 78-82 MB | 78-82 MB | 35-40 MB |
| Klasör | 2 MB | 55-65 MB | 30-35 MB |

### Performans

| Kriter | Tek Dosya | Klasör |
|--------|-----------|--------|
| Başlatma | 10-15 sn | 1-2 sn |
| Bellek | ~150 MB | ~120 MB |
| Disk Yazma | Temp'e açar | Yok |

### Kullanım Senaryoları

**Tek Dosya - İyi:**
- USB'den çalıştırma
- Portable kullanım
- Hızlı dağıtım
- Tek dosya paylaşım

**Klasör - İyi:**
- Kurulum paketi
- Program Files
- Günlük kullanım
- Hızlı başlatma önemli

## 🔒 Güvenlik ve İmza

### Dijital İmza (Opsiyonel)

Windows için kod imzalama:

```batch
# SignTool (Windows SDK gerekli)
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\InternetRadyoCalar.exe
```

Avantajlar:
- Windows SmartScreen uyarısı göstermez
- Kullanıcı güveni artar
- Profesyonel görünüm

### VirusTotal Taraması

Build sonrası tarama:
1. https://www.virustotal.com'a gidin
2. EXE dosyasını yükleyin
3. Sonuçları kontrol edin

**Not:** PyInstaller EXE'ler bazen yanlış pozitif verebilir.

## 📝 Spec Dosyası Özelleştirme

### Özel Dosya Ekleme

```python
datas=[
    ('my_config.json', '.'),
    ('assets/*.png', 'assets'),
],
```

### Gizli Import'lar

```python
hiddenimports=[
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'vlc',
    'custom_module',
],
```

### İkonu Değiştirme

```python
icon='path/to/your/icon.ico'
```

## 🎓 İleri Seviye

### Otomatik Güncelleme

Uygulamaya güncelleme sistemi eklemek için:
- PyUpdater
- Sparkle for Windows
- Squirrel.Windows

### Çoklu Platform Build

```bash
# Windows'ta
pyinstaller internet_radio_player.spec

# Linux'ta
pyinstaller internet_radio_player.spec

# macOS'ta
pyinstaller internet_radio_player.spec
```

Her platform için ayrı build gerekir.

### CI/CD Pipeline

GitHub Actions örneği:

```yaml
name: Build EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r radio_requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller internet_radio_player.spec
      - uses: actions/upload-artifact@v2
        with:
          name: InternetRadyoCalar
          path: dist/
```

## 📚 Kaynaklar

- **PyInstaller Dokümantasyonu:** https://pyinstaller.org/
- **PyQt5 Dokümantasyonu:** https://www.riverbankcomputing.com/software/pyqt/
- **VLC Python Bindings:** https://wiki.videolan.org/Python_bindings
- **UPX Sıkıştırma:** https://upx.github.io/

## 💡 İpuçları

1. **Sanal Ortam Kullanın:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r radio_requirements.txt
   ```

2. **Build Önce Test Edin:**
   ```bash
   python internet_radio_player.py
   ```

3. **Temiz Ortam:**
   Sadece gerekli paketleri yükleyin

4. **Antivirüs:**
   Build sırasında antivirüsü geçici olarak kapatın

5. **Log Tutun:**
   ```batch
   pyinstaller internet_radio_player.spec > build.log 2>&1
   ```

## 🆘 Destek

Sorunlarla karşılaşırsanız:

1. Bu README'yi dikkatlice okuyun
2. Sorun Giderme bölümünü kontrol edin
3. Build log'ları inceleyin
4. PyInstaller GitHub issues'a bakın

## ✅ Kontrol Listesi

Build öncesi:
- [ ] Python 3.8-3.11 kurulu
- [ ] Tüm bağımlılıklar yüklü
- [ ] VLC kurulu (test için)
- [ ] İkon hazır (opsiyonel)
- [ ] Uygulama çalışıyor

Build sonrası:
- [ ] EXE çalışıyor
- [ ] Tüm özellikler çalışıyor
- [ ] Equalizer çalışıyor
- [ ] Favoriler kaydediliyor
- [ ] README dahil edilmiş

Dağıtım öncesi:
- [ ] Temiz sistemde test edildi
- [ ] VLC gereksinimi belirtildi
- [ ] Kullanım kılavuzu hazır
- [ ] Antivirüs taraması yapıldı

---

**Başarılı build'ler! 🎉**
