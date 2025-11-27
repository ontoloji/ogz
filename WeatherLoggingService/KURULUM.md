# Detaylı Kurulum Rehberi

## Adım Adım Windows Service Kurulumu

### 1. Projeyi Derleyin

Windows bilgisayarınızda komut satırını (Command Prompt veya PowerShell) açın:

```powershell
# Proje klasörüne gidin
cd WeatherLoggingService

# Projeyi derleyin
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

Derleme tamamlandığında dosyalar şurada olacak:
```
bin\Release\net8.0-windows\win-x64\publish\
```

### 2. Dosyaları İstediğiniz Konuma Kopyalayın

Örneğin:
```powershell
# Hedef klasör oluşturun
mkdir C:\Services\WeatherLoggingService

# Dosyaları kopyalayın
xcopy /E /I bin\Release\net8.0-windows\win-x64\publish\* C:\Services\WeatherLoggingService\
```

### 3. Konfigürasyonu Ayarlayın

`C:\Services\WeatherLoggingService\appsettings.json` dosyasını Not Defteri ile açın:

```json
{
  "WeatherService": {
    "LogIntervalMinutes": 60,
    "LogDirectory": "C:\\WeatherLogs",
    "Locations": [
      {
        "Name": "Sakarya Adapazarı",
        "Latitude": 40.7569,
        "Longitude": 30.4030,
        "Enabled": true
      },
      {
        "Name": "Sakarya Kaynarca",
        "Latitude": 40.8833,
        "Longitude": 30.3000,
        "Enabled": true
      }
    ],
    "WeatherProviders": [
      {
        "Name": "OpenWeatherMap",
        "Enabled": true,
        "ApiKey": "BURAYA_GERÇEK_API_ANAHTARINIZI_YAZIN",
        "Url": "https://api.openweathermap.org/data/2.5/weather"
      }
    ]
  }
}
```

**ÖNEMLİ**:
- `ApiKey` alanına https://openweathermap.org/api adresinden aldığınız gerçek API anahtarını yazın
- `LogDirectory` yolunu değiştirebilirsiniz
- Koordinatları https://www.latlong.net/ adresinden bulabilirsiniz

### 4. Önce Konsol Modunda Test Edin

Servisi kurmadan önce çalışıp çalışmadığını test edin:

```powershell
cd C:\Services\WeatherLoggingService
.\WeatherLoggingService.exe
```

Şunları görmeli siniz:
```
[14:30:15 INF] Hava Durumu Loglama Servisi başlatılıyor...
[14:30:15 INF] Servis yapılandırması tamamlandı.
[14:30:15 INF] Log Dizini: C:\WeatherLogs
[14:30:15 INF] Hava durumu sağlayıcısı kaydedildi: OpenWeatherMap
...
```

**CTRL+C** ile durdurun.

Hata alıyorsanız:
- API anahtarınızı kontrol edin
- İnternet bağlantınızı kontrol edin
- `logs\` klasöründeki hata loglarını okuyun

### 5. Windows Service Olarak Kurun

**Yönetici olarak** PowerShell açın (sağ tık -> Yönetici olarak çalıştır):

```powershell
# Servisi oluştur
sc.exe create "WeatherLoggingService" `
  binpath= "C:\Services\WeatherLoggingService\WeatherLoggingService.exe" `
  start= auto `
  DisplayName= "Hava Durumu Loglama Servisi"

# Servis açıklaması ekle
sc.exe description "WeatherLoggingService" "Saatlik hava durumu verilerini otomatik olarak toplar ve kaydeder."

# Servisi başlat
sc.exe start "WeatherLoggingService"

# Durumu kontrol et
sc.exe query "WeatherLoggingService"
```

Başarılı olursa şunu göreceksiniz:
```
STATE              : 4  RUNNING
```

### 6. Windows Hizmetler Penceresinden Yönetim

1. `Win + R` tuşlarına basın
2. `services.msc` yazın ve Enter
3. "Hava Durumu Loglama Servisi" veya "WeatherLoggingService" bulun
4. Sağ tık -> Özellikler:
   - **Başlangıç türü**: Otomatik (Gecikmeli Başlangıç) önerilir
   - **Oturum açma**: Yerel Sistem hesabı
5. "Uygula" ve "Tamam"

### 7. Servisin Çalıştığını Doğrulayın

#### Log Dosyalarını Kontrol Edin

```powershell
# Servis logları
notepad C:\Services\WeatherLoggingService\logs\weather-service-20241127.log

# Hava durumu logları
explorer C:\WeatherLogs
```

`C:\WeatherLogs` klasöründe şu yapıyı görmelisiniz:
```
WeatherLogs\
└── OpenWeatherMap\
    ├── Sakarya_Adapazari\
    │   ├── weather_2024-11-27.json
    │   ├── weather_2024-11-27.csv
    │   └── raw\
    └── Sakarya_Kaynarca\
        ├── weather_2024-11-27.json
        └── weather_2024-11-27.csv
```

#### CSV Dosyasını Excel'de Açın

```powershell
start excel C:\WeatherLogs\OpenWeatherMap\Sakarya_Adapazari\weather_2024-11-27.csv
```

## Yeni Lokasyon Ekleme

1. Servisi durdurun:
```powershell
sc.exe stop "WeatherLoggingService"
```

2. `appsettings.json` dosyasını düzenleyin:
```json
{
  "Locations": [
    {
      "Name": "Sakarya Adapazarı",
      "Latitude": 40.7569,
      "Longitude": 30.4030,
      "Enabled": true
    },
    {
      "Name": "İstanbul Kadıköy",
      "Latitude": 40.9833,
      "Longitude": 29.0333,
      "Enabled": true
    }
  ]
}
```

3. Servisi başlatın:
```powershell
sc.exe start "WeatherLoggingService"
```

## Yeni Hava Durumu Kaynağı Ekleme

### WeatherAPI Ekleme Örneği

1. https://www.weatherapi.com/ adresinden API anahtarı alın

2. Servisi durdurun:
```powershell
sc.exe stop "WeatherLoggingService"
```

3. `appsettings.json` dosyasını düzenleyin:
```json
{
  "WeatherProviders": [
    {
      "Name": "OpenWeatherMap",
      "Enabled": true,
      "ApiKey": "your_openweathermap_key",
      "Url": "https://api.openweathermap.org/data/2.5/weather"
    },
    {
      "Name": "WeatherAPI",
      "Enabled": true,
      "ApiKey": "your_weatherapi_key",
      "Url": "https://api.weatherapi.com/v1/current.json"
    }
  ]
}
```

4. Servisi başlatın:
```powershell
sc.exe start "WeatherLoggingService"
```

Artık her lokasyon için **iki ayrı kaynaktan** veri toplanacak ve ayrı klasörlerde saklanacak.

## Sorun Giderme

### "Erişim engellendi" hatası
PowerShell'i **Yönetici olarak** çalıştırdığınızdan emin olun.

### Servis başlamıyor
```powershell
# Event Viewer'da Windows loglarını kontrol edin
eventvwr.msc

# Veya servis loglarına bakın
notepad C:\Services\WeatherLoggingService\logs\weather-service-*.log
```

### API hatası alıyorum
```powershell
# API anahtarınızı test edin
curl "https://api.openweathermap.org/data/2.5/weather?lat=40.7569&lon=30.4030&appid=YOUR_API_KEY&units=metric"
```

### Veri toplanmıyor
```powershell
# Servisi yeniden başlatın
sc.exe stop "WeatherLoggingService"
sc.exe start "WeatherLoggingService"

# Logları kontrol edin
notepad C:\Services\WeatherLoggingService\logs\weather-service-*.log
```

## Servisi Kaldırma

```powershell
# Servisi durdur
sc.exe stop "WeatherLoggingService"

# Servisi sil
sc.exe delete "WeatherLoggingService"

# Dosyaları sil (opsiyonel)
rmdir /S /Q C:\Services\WeatherLoggingService

# Logları sakla veya sil (opsiyonel)
# rmdir /S /Q C:\WeatherLogs
```

## Otomatik Başlatma Ayarları

### Windows başlangıcında otomatik başlat
Varsayılan olarak zaten aktif. Kontrol etmek için:

```powershell
sc.exe qc "WeatherLoggingService"
```

`START_TYPE` değeri `AUTO_START` olmalı.

### Gecikmeli başlatma
Bilgisayar açılışında sistem stabilleştikten sonra başlaması için:

```powershell
sc.exe config "WeatherLoggingService" start= delayed-auto
```

## Performans ve Kaynak Kullanımı

- **CPU**: Veri toplama sırasında %1-2, boşta %0
- **RAM**: ~50-80 MB
- **Disk**: Her lokasyon için günde ~1-2 MB
- **Network**: Saatte ~10-20 KB per lokasyon per kaynak

## Güncelleme

Yeni versiyon için:

```powershell
# Servisi durdur
sc.exe stop "WeatherLoggingService"

# Yeni dosyaları kopyala
xcopy /E /Y bin\Release\net8.0-windows\win-x64\publish\* C:\Services\WeatherLoggingService\

# appsettings.json'u korumak için yedek aldığınızdan emin olun!

# Servisi başlat
sc.exe start "WeatherLoggingService"
```

## Destek

Sorun yaşarsanız:
1. `logs\` klasöründeki logları kontrol edin
2. Event Viewer (eventvwr.msc) Windows loglarını kontrol edin
3. Issue açın

## Yedekleme Önerileri

```powershell
# Log verilerini düzenli yedekleyin
robocopy C:\WeatherLogs D:\Backups\WeatherLogs /E /MIR /R:3 /W:10

# Konfigürasyonu yedekleyin
copy C:\Services\WeatherLoggingService\appsettings.json D:\Backups\
```

## İleri Düzey Ayarlar

### Log dosyalarını otomatik temizle
30 günden eski logları silmek için Windows Task Scheduler kullanabilirsiniz:

```powershell
# PowerShell scripti oluşturun: cleanup_old_logs.ps1
$LogPath = "C:\WeatherLogs"
$DaysToKeep = 30
Get-ChildItem -Path $LogPath -Recurse -File | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysToKeep)
} | Remove-Item -Force
```

### Email bildirimleri
Hata durumunda email almak için SMTP konfigürasyonu eklenebilir (gelecek özellik).

### Veritabanı entegrasyonu
Logları SQL Server'a kaydetmek için (gelecek özellik).
