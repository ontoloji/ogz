# Hava Durumu Loglama Servisi

Windows tabanlı, arka planda çalışan bir hava durumu veri toplama ve loglama servisidir.

## Özellikler

### ✅ Temel Özellikler
- **Windows Service**: Bilgisayar açık olmasa bile (uyku modundan çıktıktan sonra) otomatik çalışır
- **Saatlik Loglama**: Her saat başı otomatik olarak hava durumu verilerini toplar
- **Çoklu Lokasyon**: İstediğiniz kadar şehir/bölge ekleyebilirsiniz
- **Çoklu Hava Durumu Kaynağı**: Farklı hava durumu API'larından veri toplayabilirsiniz
- **Sınıflandırılmış Loglar**: Her veri kaynağı için ayrı klasörlerde organize edilmiş loglar

### 📊 Loglanan Veriler
- **Sıcaklık** (°C)
- **Yağmur Miktarı** (mm)
- **Yağmur Olasılığı** (%)
- **Rüzgar Hızı** (m/s)
- **Rüzgar Yönü** (derece ve yön)
- **Nem** (%)
- **Basınç** (hPa)
- **Genel Durum** (açıklama)

### 🗂️ Log Yapısı
```
C:\WeatherLogs\
├── OpenWeatherMap\
│   ├── Sakarya_Adapazari\
│   │   ├── weather_2024-11-27.json
│   │   ├── weather_2024-11-27.csv
│   │   └── raw\
│   │       └── raw_2024-11-27_14-00-00.json
│   └── Sakarya_Kaynarca\
│       ├── weather_2024-11-27.json
│       └── weather_2024-11-27.csv
└── WeatherAPI\
    ├── Sakarya_Adapazari\
    └── Sakarya_Kaynarca\
```

## 🚀 Hızlı Başlangıç: GitHub'dan Hazır EXE İndirme

**Kendi bilgisayarınızda .NET SDK kurmak istemiyorsanız:**

1. GitHub'da **Actions** sekmesine gidin
2. **"Build Weather Logging Service"** workflow'unu seçin
3. **"Run workflow"** ile build başlatın (veya en son tamamlanmış build'i bulun)
4. Build tamamlandığında **Artifacts** bölümünden ZIP dosyasını indirin
5. ZIP'i çıkartın, `appsettings.json`'a API anahtarınızı ekleyin
6. `install.bat` ile kurun

**Detaylı bilgi için:** [GITHUB_BUILD.md](GITHUB_BUILD.md) dosyasına bakın.

## Kurulum

### Gereksinimler
- Windows 10/11 veya Windows Server 2016+
- .NET 8.0 Runtime (otomatik dahil edilir)
- Hava durumu API anahtarları

### 1. API Anahtarları
Aşağıdaki hava durumu servislerinden ücretsiz API anahtarı alın:

#### OpenWeatherMap (Önerilen)
1. https://openweathermap.org/api adresine gidin
2. Ücretsiz hesap oluşturun
3. API anahtarınızı kopyalayın

#### WeatherAPI (Opsiyonel)
1. https://www.weatherapi.com/ adresine gidin
2. Ücretsiz hesap oluşturun
3. API anahtarınızı kopyalayın

### 2. Derleme

Windows bilgisayarda PowerShell'de çalıştırın:

```powershell
cd WeatherLoggingService
dotnet publish -c Release -r win-x64 --self-contained true
```

### 3. Konfigürasyon

`appsettings.json` dosyasını düzenleyin:

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
        "ApiKey": "BURAYA_API_ANAHTARINIZI_GIRIN",
        "Url": "https://api.openweathermap.org/data/2.5/weather"
      }
    ]
  }
}
```

### 4. Windows Service Olarak Kurulum

**Yönetici olarak** PowerShell'de:

```powershell
# Servisi oluştur
sc.exe create "WeatherLoggingService" binpath="C:\Path\To\WeatherLoggingService.exe"

# Servisi başlat
sc.exe start "WeatherLoggingService"

# Servis durumunu kontrol et
sc.exe query "WeatherLoggingService"
```

Alternatif olarak, Windows Hizmetler penceresinden (services.msc):
1. Win+R tuşlarına basın, `services.msc` yazın
2. "Weather Logging Service" servisini bulun
3. Sağ tıklayın ve "Özellikler"
4. "Başlangıç Türü" olarak "Otomatik" seçin
5. "Başlat" butonuna tıklayın

## Kullanım

### Yeni Lokasyon Ekleme

`appsettings.json` dosyasındaki `Locations` dizisine ekleyin:

```json
{
  "Name": "İstanbul Kadıköy",
  "Latitude": 40.9833,
  "Longitude": 29.0333,
  "Enabled": true
}
```

Koordinatları bulmak için: https://www.latlong.net/

### Yeni Hava Durumu Kaynağı Ekleme

`appsettings.json` dosyasındaki `WeatherProviders` dizisine ekleyin:

```json
{
  "Name": "WeatherAPI",
  "Enabled": true,
  "ApiKey": "YOUR_API_KEY",
  "Url": "https://api.weatherapi.com/v1/current.json"
}
```

### Logları Görüntüleme

#### JSON Formatı
Detaylı veri analizi için:
```
C:\WeatherLogs\OpenWeatherMap\Sakarya_Adapazari\weather_2024-11-27.json
```

#### CSV Formatı
Excel'de açmak için:
```
C:\WeatherLogs\OpenWeatherMap\Sakarya_Adapazari\weather_2024-11-27.csv
```

#### Ham API Yanıtları
Debugging için:
```
C:\WeatherLogs\OpenWeatherMap\Sakarya_Adapazari\raw\raw_2024-11-27_14-00-00.json
```

### Servis Logları

Servisin kendi logları:
```
WeatherLoggingService\logs\weather-service-20241127.log
```

## Sorun Giderme

### Servis başlamıyor
1. Event Viewer'da hata loglarını kontrol edin
2. API anahtarlarının doğru olduğundan emin olun
3. İnternet bağlantısını kontrol edin

### Veri toplanmıyor
1. `logs\` klasöründeki servis loglarını kontrol edin
2. API quota'nızı kontrol edin (ücretsiz planlarda limit var)
3. Lokasyon koordinatlarının doğru olduğundan emin olun

### Servisi durdurma
```powershell
sc.exe stop "WeatherLoggingService"
```

### Servisi kaldırma
```powershell
sc.exe delete "WeatherLoggingService"
```

## Teknik Detaylar

- **.NET 8.0** ile geliştirilmiştir
- **Serilog** ile loglama
- **HttpClient** ile API iletişimi
- **Microsoft.Extensions.Hosting** ile Windows Service desteği
- Her saat başı otomatik veri toplama
- Asenkron paralel veri toplama (tüm lokasyonlar ve kaynaklar aynı anda)

## Lisans

Bu proje açık kaynak kodludur.

## Destek

Sorularınız için issue açabilirsiniz.
