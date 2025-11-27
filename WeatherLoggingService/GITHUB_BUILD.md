# GitHub Actions ile Otomatik Windows EXE Build

GitHub Actions kullanarak otomatik olarak Windows EXE dosyası oluşturabilir ve indirebilirsiniz. Kendi bilgisayarınızda .NET SDK kurmaya gerek yoktur!

## 🚀 Hızlı Başlangıç

### 1. Otomatik Build Tetikleme

Build işlemi otomatik olarak şu durumlarda çalışır:
- ✅ `WeatherLoggingService/` klasöründe değişiklik yapıp push ettiğinizde
- ✅ Pull request oluşturduğunuzda
- ✅ Manuel olarak tetiklediğinizde

### 2. Manuel Build Çalıştırma

GitHub'da projenize gidin:

1. **Actions** sekmesine tıklayın
2. Sol taraftan **"Build Weather Logging Service"** workflow'unu seçin
3. Sağ tarafta **"Run workflow"** butonuna tıklayın
4. Branch seçin (örn: `claude/weather-logging-service-...`)
5. **"Run workflow"** yeşil butonu ile başlatın

### 3. Build Durumunu İzleme

1. **Actions** sekmesinde çalışan workflow'u görürsünüz
2. Tıklayarak detayları görebilirsiniz
3. Her adımı canlı olarak izleyebilirsiniz
4. Build ~5-10 dakika sürer

### 4. EXE Dosyasını İndirme

Build tamamlandığında:

1. **Actions** sekmesine gidin
2. Tamamlanan workflow'a tıklayın
3. Sayfanın altında **"Artifacts"** bölümünü bulun
4. İki seçeneğiniz var:
   - **WeatherLoggingService-win-x64-standalone.zip** (~70MB)
     - .NET runtime içerir, hiçbir şey kurmanıza gerek yok
     - **ÖNERİLEN**
   - **WeatherLoggingService-win-x64-framework.zip** (~1MB)
     - .NET 8.0 Runtime gerektirir
     - Daha küçük dosya boyutu

5. ZIP dosyasını indirin ve çıkartın

## 📦 İndirdikten Sonra

### Adım 1: ZIP'i Çıkartın

```powershell
# Windows Explorer'da sağ tık -> Extract All
# VEYA PowerShell ile:
Expand-Archive -Path WeatherLoggingService-win-x64-standalone.zip -DestinationPath C:\WeatherService
```

### Adım 2: API Anahtarını Ekleyin

`appsettings.json` dosyasını Not Defteri ile açın:

```json
{
  "WeatherService": {
    "WeatherProviders": [
      {
        "Name": "OpenWeatherMap",
        "ApiKey": "BURAYA_API_ANAHTARINIZI_YAPISTIRINNN"
      }
    ]
  }
}
```

### Adım 3: Servisi Kurun

**Yönetici olarak** `install.bat` dosyasına çift tıklayın.

VEYA PowerShell'de:

```powershell
# Yönetici olarak PowerShell açın
cd C:\WeatherService
.\install.bat
```

### Adım 4: Çalıştığını Doğrulayın

```powershell
# Servis durumunu kontrol et
sc.exe query "WeatherLoggingService"

# Log dosyalarını kontrol et
explorer C:\WeatherLogs
```

## 🏷️ Release (Sürüm) Oluşturma

Belirli bir versiyonu paylaşmak için GitHub Release oluşturabilirsiniz:

### Adım 1: Tag Oluşturun

```bash
# Local'de tag oluştur
git tag -a v1.0.0 -m "İlk stabil sürüm"

# Tag'i GitHub'a push et
git push origin v1.0.0
```

### Adım 2: Otomatik Release

Tag'i push ettiğinizde GitHub Actions otomatik olarak:
- ✅ Projeyi build eder
- ✅ EXE dosyalarını oluşturur
- ✅ GitHub Release sayfasında yayınlar
- ✅ İndirme linkleri oluşturur

### Adım 3: Release'i İndirin

1. GitHub'da projenizin **Releases** sekmesine gidin
2. En son versiyonu bulun (örn: v1.0.0)
3. **Assets** bölümünden ZIP dosyasını indirin

## 🔧 Workflow Detayları

### Build Çıktıları

Her build iki farklı paket oluşturur:

#### 1. Self-Contained (Standalone)
```
WeatherLoggingService-win-x64-standalone.zip
├── WeatherLoggingService.exe       # Ana program (~70MB)
├── appsettings.json                # Konfigürasyon
├── install.bat                     # Kurulum scripti
├── uninstall.bat                   # Kaldırma scripti
├── README.md                       # Dokümantasyon
├── KURULUM.md                      # Kurulum rehberi
└── VERSION.txt                     # Build bilgileri
```

**Avantajlar:**
- .NET kurulu olması gerekmez
- Tek tıkla çalışır
- Taşınabilir

**Dezavantajlar:**
- Büyük dosya boyutu (~70MB)

#### 2. Framework-Dependent
```
WeatherLoggingService-win-x64-framework.zip
├── WeatherLoggingService.exe       # Ana program (~1MB)
├── appsettings.json
├── install.bat
└── ...
```

**Avantajlar:**
- Küçük dosya boyutu (~1MB)

**Dezavantajlar:**
- .NET 8.0 Runtime gerektirir
- Kullanıcı önce .NET yüklemeli

### VERSION.txt İçeriği

Her build'de otomatik oluşturulur:

```
Weather Logging Service
Version: 2024.11.27.1430
Commit: e4bab9b
Build Date: 2024-11-27 14:30:15
Branch: claude/weather-logging-service-01BC3PKgWyr5RjkcTqND2XD7
```

## 📊 GitHub Actions Workflow Adımları

1. **Checkout**: Kodu indir
2. **Setup .NET**: .NET 8.0 SDK kur
3. **Restore**: NuGet paketlerini indir
4. **Build**: Projeyi derle
5. **Publish (Self-Contained)**: Standalone EXE oluştur
6. **Publish (Framework-Dependent)**: Framework-dependent EXE oluştur
7. **Copy Files**: Kurulum scriptlerini kopyala
8. **Create Version**: Versiyon dosyası oluştur
9. **Create ZIP**: Paketleri ziple
10. **Upload Artifacts**: GitHub'a yükle

## 🎯 Kullanım Senaryoları

### Senaryo 1: Hızlı Test
```bash
# Kod değiştir
git add .
git commit -m "Fix: Hata düzeltildi"
git push

# Actions'da build'i bekle (5-10 dk)
# Artifact'i indir
# Test et
```

### Senaryo 2: Stabil Sürüm Paylaşma
```bash
# Tag oluştur
git tag -a v1.0.0 -m "Stable release"
git push origin v1.0.0

# GitHub Releases'da otomatik oluşur
# Link paylaş
```

### Senaryo 3: Farklı Konfigürasyonlar
```bash
# Dev branch'de geliştir
git checkout -b dev/new-feature
# Kod yaz...
git push

# Build otomatik çalışır
# Artifact'i indir ve test et

# Sonra main'e merge et
```

## 🛠️ Sorun Giderme

### Build Başarısız Oluyor

1. **Actions** sekmesinde hatalı workflow'a tıklayın
2. Kırmızı X olan adımı açın
3. Hata mesajını okuyun

Yaygın hatalar:
- **Syntax Error**: `.csproj` veya kaynak kodda hata
- **Restore Failed**: NuGet paket sorunu
- **Publish Failed**: Konfigürasyon hatası

### Artifact Görünmüyor

Build tamamlanmış mı kontrol edin:
- ✅ Yeşil check = başarılı
- ❌ Kırmızı X = başarısız
- 🟡 Sarı nokta = devam ediyor

### EXE Çalışmıyor

1. **Self-contained** versiyonu indirdiniz mi?
2. `appsettings.json` dosyası var mı?
3. API anahtarı eklenmiş mi?
4. Yönetici yetkisi ile mi çalıştırıyorsunuz?

### .NET Runtime Hatası

Framework-dependent versiyonu kullanıyorsanız:

```powershell
# .NET 8.0 Runtime'ı yükleyin
# https://dotnet.microsoft.com/download/dotnet/8.0

# Veya self-contained versiyonu kullanın
```

## 📝 Workflow Özelleştirme

`.github/workflows/build-weather-service.yml` dosyasını düzenleyebilirsiniz:

### Farklı .NET Versiyonu
```yaml
- name: Setup .NET
  uses: actions/setup-dotnet@v4
  with:
    dotnet-version: '9.0.x'  # .NET 9 kullan
```

### Farklı OS Build
```yaml
jobs:
  build-windows:
    runs-on: windows-latest  # windows-2022, windows-2019

  build-linux:
    runs-on: ubuntu-latest
    # Linux build adımları...
```

### Artifact Saklama Süresi
```yaml
- name: Upload Artifact
  uses: actions/upload-artifact@v4
  with:
    retention-days: 90  # 90 gün sakla (varsayılan 30)
```

## 🔐 GitHub Secrets

API anahtarlarını workflow'da kullanmak için:

1. GitHub'da **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** tıklayın
3. İsim: `OPENWEATHER_API_KEY`
4. Değer: API anahtarınız
5. Workflow'da kullanın:

```yaml
- name: Replace API Key
  run: |
    (Get-Content appsettings.json) -replace 'YOUR_API_KEY', '${{ secrets.OPENWEATHER_API_KEY }}' | Set-Content appsettings.json
```

**UYARI**: Production builds için bu önerilir, yoksa herkes ZIP'te API anahtarını görebilir!

## 📈 Build Geçmişi

Tüm build'leri görme:
1. **Actions** sekmesi
2. Sol taraftan workflow seçin
3. Tüm çalıştırmalar listelenir
4. Her birini tıklayarak artifacts'a erişebilirsiniz

## 💡 İpuçları

### Hızlı Build
```yaml
# Sadece değişen dosyalar için build
on:
  push:
    paths:
      - 'WeatherLoggingService/**/*.cs'  # Sadece C# dosyaları
```

### Build Bildirimleri
GitHub Settings → Notifications → Actions'da email bildirimlerini açın.

### Badge Ekleme
README.md dosyasına build durumu badge'i:

```markdown
![Build Status](https://github.com/ontoloji/ogz/actions/workflows/build-weather-service.yml/badge.svg)
```

### Paralel Build
```yaml
strategy:
  matrix:
    runtime: [win-x64, win-x86, win-arm64]
# Her platform için ayrı build
```

## 🎓 Öğrenme Kaynakları

- [GitHub Actions Dokümantasyonu](https://docs.github.com/en/actions)
- [.NET Build Actions](https://github.com/actions/setup-dotnet)
- [Artifact Upload/Download](https://github.com/actions/upload-artifact)

## ✅ Özet Checklist

Build almak için:
- [ ] Kodu GitHub'a push et
- [ ] Actions sekmesinde build'i başlat veya bekle
- [ ] Build tamamlandığında Artifacts bölümünden indir
- [ ] ZIP'i çıkart
- [ ] `appsettings.json`'a API anahtarını ekle
- [ ] `install.bat` ile kur
- [ ] Test et

Release için:
- [ ] Git tag oluştur (`v1.0.0`)
- [ ] Tag'i push et
- [ ] GitHub Releases'da otomatik oluşur
- [ ] Release linkini paylaş

Artık GitHub üzerinden otomatik Windows EXE build'leri alabilirsiniz! 🎉
