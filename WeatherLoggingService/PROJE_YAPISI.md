# Proje Yapısı

## Dizin Yapısı

```
WeatherLoggingService/
├── Models/
│   └── WeatherData.cs              # Veri modelleri ve konfigürasyon sınıfları
│
├── Services/
│   ├── IWeatherDataProvider.cs     # Hava durumu sağlayıcı arayüzü
│   ├── OpenWeatherMapProvider.cs   # OpenWeatherMap implementasyonu
│   ├── WeatherAPIProvider.cs       # WeatherAPI implementasyonu
│   ├── WeatherLogger.cs            # Log yazma servisi
│   └── WeatherDataCollector.cs     # Ana veri toplama orkestratörü
│
├── Worker.cs                        # Background service worker
├── Program.cs                       # Uygulama giriş noktası ve DI konfigürasyonu
│
├── appsettings.json                 # Ana konfigürasyon dosyası
├── appsettings.production.json      # Üretim konfigürasyonu (örnekler ile)
│
├── WeatherLoggingService.csproj     # .NET proje dosyası
│
├── install.bat                      # Otomatik kurulum scripti
├── uninstall.bat                    # Otomatik kaldırma scripti
│
├── README.md                        # Genel proje dokümantasyonu
├── KURULUM.md                       # Detaylı kurulum rehberi
├── CHANGELOG.md                     # Versiyon geçmişi
├── PROJE_YAPISI.md                 # Bu dosya
│
└── .gitignore                       # Git ignore kuralları
```

## Mimari Tasarım

### Katmanlar

#### 1. **Models** (Veri Katmanı)
- `WeatherData`: Hava durumu verisini temsil eden model
- `Location`: Lokasyon bilgisi
- `WeatherProvider`: Hava durumu kaynağı konfigürasyonu
- `WeatherServiceConfiguration`: Servis konfigürasyonu

#### 2. **Services** (İş Mantığı Katmanı)
- `IWeatherDataProvider`: Sağlayıcı arayüzü (Strategy Pattern)
- `OpenWeatherMapProvider`: OpenWeatherMap implementasyonu
- `WeatherAPIProvider`: WeatherAPI implementasyonu
- `WeatherLogger`: Log dosyası yönetimi
- `WeatherDataCollector`: Veri toplama koordinasyonu

#### 3. **Worker** (Uygulama Katmanı)
- `Worker`: Background service, zamanlama ve yaşam döngüsü yönetimi
- `Program`: DI container ve servis başlatma

## Tasarım Desenleri

### 1. **Strategy Pattern**
```csharp
public interface IWeatherDataProvider
{
    Task<WeatherData?> GetWeatherDataAsync(Location location);
}
```
Her hava durumu kaynağı bu arayüzü implement eder, böylece yeni kaynaklar kolayca eklenebilir.

### 2. **Dependency Injection**
```csharp
services.AddSingleton<WeatherDataCollector>();
services.AddSingleton<WeatherLogger>();
```
Tüm servisler DI container üzerinden yönetilir.

### 3. **Factory Pattern**
```csharp
var httpClient = httpClientFactory.CreateClient();
```
HttpClient örnekleri factory üzerinden oluşturulur.

### 4. **Repository Pattern** (Kısmen)
`WeatherLogger` log dosyalarına erişimi soyutlar.

## Veri Akışı

```
[Timer] → [Worker.CollectWeatherDataAsync()]
           ↓
    [WeatherDataCollector.CollectAndLogWeatherDataAsync()]
           ↓
    [Paralel olarak her lokasyon ve sağlayıcı için]
           ↓
    [IWeatherDataProvider.GetWeatherDataAsync()]
           ↓
    [HTTP Request → API]
           ↓
    [JSON Parse → WeatherData]
           ↓
    [WeatherLogger.LogWeatherDataAsync()]
           ↓
    [Dosyaya Yaz: JSON, CSV, Raw]
```

## Konfigürasyon Sistemi

### appsettings.json Yapısı
```json
{
  "WeatherService": {
    "LogIntervalMinutes": 60,           // Veri toplama aralığı
    "LogDirectory": "C:\\WeatherLogs",  // Log dizini
    "Locations": [...],                  // Lokasyonlar
    "WeatherProviders": [...]            // API sağlayıcıları
  }
}
```

### Konfigürasyon Yükleme
```csharp
var weatherConfig = builder.Configuration
    .GetSection("WeatherService")
    .Get<WeatherServiceConfiguration>();
```

## Log Sistemi

### Hiyerarşi
```
{LogDirectory}/
├── {ProviderName}/              # Örn: OpenWeatherMap
│   ├── {LocationName}/          # Örn: Sakarya_Adapazari
│   │   ├── weather_YYYY-MM-DD.json    # Günlük JSON log
│   │   ├── weather_YYYY-MM-DD.csv     # Günlük CSV log
│   │   └── raw/
│   │       └── raw_YYYY-MM-DD_HH-mm-ss.json  # Ham API yanıtı
```

### Log Formatları

#### JSON Format
```json
[
  {
    "timestamp": "2024-11-27 14:00:00",
    "location": "Sakarya Adapazarı",
    "temperature_celsius": 12.5,
    "rain_mm": 0,
    "wind_speed_ms": 3.2,
    ...
  }
]
```

#### CSV Format
```csv
Timestamp,Location,Temperature(°C),Rain(mm),WindSpeed(m/s),...
2024-11-27 14:00:00,Sakarya Adapazarı,12.5,0,3.2,...
```

## Zamanlama Sistemi

### İlk Çalıştırma
1. Servis başlar
2. Hemen bir veri toplama yapılır
3. Bir sonraki tam saate kadar beklenir

### Döngüsel Çalıştırma
```csharp
var nextHour = now.Date.AddHours(now.Hour + 1);
var timeUntilNextHour = nextHour - now;
await Task.Delay(timeUntilNextHour);

// Sonra saatlik timer başlar
_timer = new Timer(..., intervalMs, intervalMs);
```

## Hata Yönetimi

### Katmanlı Hata Yakalama

1. **Provider Seviyesi**: API isteği başarısız
   ```csharp
   catch (Exception ex)
   {
       _logger.LogError(ex, "API verisi alınamadı");
       return null; // Diğer sağlayıcılar çalışmaya devam eder
   }
   ```

2. **Collector Seviyesi**: Toplama hatası
   ```csharp
   catch (Exception ex)
   {
       _logger.LogError(ex, "Veri toplama hatası");
       // Devam eder, bir sonraki saatte tekrar dener
   }
   ```

3. **Worker Seviyesi**: Zamanlayıcı hatası
   ```csharp
   catch (Exception ex)
   {
       _logger.LogError(ex, "Worker hatası");
       // Servis çalışmaya devam eder
   }
   ```

## Genişletilebilirlik

### Yeni Hava Durumu Kaynağı Ekleme

1. **Yeni Provider Sınıfı Oluştur**:
```csharp
public class MyWeatherProvider : IWeatherDataProvider
{
    public string ProviderName => "MyWeather";

    public async Task<WeatherData?> GetWeatherDataAsync(Location location)
    {
        // API çağrısı ve parsing
    }
}
```

2. **Program.cs'de Kaydet**:
```csharp
if (providerConfig.Name == "MyWeather")
{
    var provider = new MyWeatherProvider(...);
    collector.RegisterProvider(provider);
}
```

3. **appsettings.json'a Ekle**:
```json
{
  "Name": "MyWeather",
  "Enabled": true,
  "ApiKey": "...",
  "Url": "..."
}
```

### Yeni Veri Alanı Ekleme

1. `WeatherData` modeline ekle
2. Provider'larda parse et
3. `WeatherLogger`'da log formatlarına ekle

## Performans Optimizasyonları

### 1. **Asenkron Paralel İşleme**
```csharp
var tasks = new List<Task>();
foreach (var location in locations)
    foreach (var provider in providers)
        tasks.Add(CollectAsync(location, provider));

await Task.WhenAll(tasks);
```

### 2. **HttpClient Reuse**
```csharp
services.AddHttpClient(); // Singleton factory
```

### 3. **Buffered File Writing**
```csharp
using var writer = new StreamWriter(path, append: true);
```

### 4. **Lazy Timer Creation**
```csharp
_timer = new Timer(...); // Sadece gerektiğinde
```

## Güvenlik

### 1. **API Key Güvenliği**
- appsettings.json gitignore'da
- Production'da environment variables kullanılabilir
- User Secrets (.NET) desteklenir

### 2. **Dosya Yolu Güvenliği**
```csharp
private static string SanitizeFileName(string fileName)
{
    var invalidChars = Path.GetInvalidFileNameChars();
    return string.Join("_", fileName.Split(invalidChars));
}
```

### 3. **Hata Mesajlarında Hassas Bilgi**
```csharp
_logger.LogError(ex, "API hatası"); // API key loglanmaz
```

## Test Stratejisi

### Unit Testler (Gelecek)
- Provider testleri (mock HTTP)
- Logger testleri (mock file system)
- Worker testleri (mock timer)

### Integration Testleri (Gelecek)
- Gerçek API çağrıları
- Gerçek dosya yazma
- Service lifecycle testleri

### Manuel Test
```powershell
# Console modda çalıştır
.\WeatherLoggingService.exe

# Log dosyalarını kontrol et
Get-Content C:\WeatherLogs\OpenWeatherMap\*\*.json
```

## Bağımlılıklar

### NuGet Paketleri
- `Microsoft.Extensions.Hosting` - Background service
- `Microsoft.Extensions.Hosting.WindowsServices` - Windows service
- `Newtonsoft.Json` - JSON serialization
- `Serilog.*` - Logging framework

### .NET Kütüphaneleri
- `System.Net.Http` - API calls
- `System.IO` - File operations
- `System.Threading` - Timers

## Deployment

### Self-Contained Deployment
```bash
dotnet publish -c Release -r win-x64 --self-contained true
```

Avantajlar:
- .NET runtime yüklü olması gerekmez
- Version conflicts yok
- Portable

Dezavantajlar:
- Daha büyük dosya boyutu (~70 MB)

### Framework-Dependent Deployment
```bash
dotnet publish -c Release -r win-x64 --self-contained false
```

Avantajlar:
- Küçük dosya boyutu (~1 MB)

Dezavantajlar:
- Hedef sistemde .NET 8 runtime gerekli

## Bakım ve İzleme

### Log Dosyaları
- **Servis logları**: `logs/weather-service-*.log`
- **Windows Event Viewer**: Application logs
- **Hava durumu logları**: `{LogDirectory}/`

### Performans Metrikleri
- CPU kullanımı: Task Manager
- Memory: Performance Monitor
- Disk I/O: Resource Monitor

### Debugging
```csharp
// appsettings.json
"LogLevel": {
  "Default": "Debug"  // Daha detaylı loglar
}
```

## Lisans ve Katkı

Bu proje açık kaynak kodludur. Katkılar memnuniyetle karşılanır.

### Katkı Süreci
1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request açın

## Destek

Sorular için:
- GitHub Issues
- Email
- Dokümantasyon
