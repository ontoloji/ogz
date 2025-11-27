# Değişiklik Günlüğü

## [1.0.0] - 2024-11-27

### Eklenenler
- ✅ Windows Service olarak çalışma desteği
- ✅ Saatlik otomatik hava durumu veri toplama
- ✅ OpenWeatherMap API entegrasyonu
- ✅ WeatherAPI API entegrasyonu
- ✅ Çoklu lokasyon desteği
  - Sakarya Adapazarı (varsayılan)
  - Sakarya Kaynarca (varsayılan)
  - Diğer şehirler eklenebilir
- ✅ Çoklu hava durumu kaynağı desteği
- ✅ Sınıflandırılmış log sistemi
  - Kaynak bazlı klasörler
  - Lokasyon bazlı alt klasörler
- ✅ Çoklu log formatı
  - JSON (detaylı veri)
  - CSV (Excel uyumlu)
  - Raw API yanıtları
- ✅ Kapsamlı loglama
  - Sıcaklık (°C)
  - Yağmur miktarı (mm)
  - Rüzgar hızı ve yönü (m/s, derece)
  - Nem (%)
  - Basınç (hPa)
  - Hava durumu açıklaması
- ✅ Konfigürasyon dosyası desteği (appsettings.json)
- ✅ Serilog ile gelişmiş loglama
- ✅ Asenkron paralel veri toplama
- ✅ Otomatik klasör oluşturma
- ✅ Hata yönetimi ve logging
- ✅ Kurulum scriptleri (install.bat, uninstall.bat)
- ✅ Türkçe dokümantasyon
  - README.md
  - KURULUM.md
  - Bu CHANGELOG.md

### Teknik Özellikler
- .NET 8.0 Windows
- Self-contained deployment
- Background Service (Worker)
- Dependency Injection
- HttpClient factory pattern
- Configuration binding
- Structured logging

### Gelecek Sürümler İçin Planlar
- [ ] Email bildirimleri (hata durumunda)
- [ ] SMS bildirimleri
- [ ] SQL Server/SQLite veritabanı desteği
- [ ] Web arayüzü (dashboard)
- [ ] Grafik ve raporlama
- [ ] Uyarı sistemi (belirli hava koşullarında)
- [ ] API endpoint (diğer uygulamalar için)
- [ ] Docker desteği
- [ ] Linux desteği
- [ ] Daha fazla hava durumu kaynağı:
  - AccuWeather
  - Weather Underground
  - Dark Sky API
- [ ] Otomatik API key rotation
- [ ] Rate limiting ve quota yönetimi
- [ ] Gelişmiş hata kurtarma
- [ ] Performans metrikleri
- [ ] Unit testler
- [ ] Integration testler

## Versiyon Numaralandırma

Bu proje [Semantic Versioning](https://semver.org/) kullanır:
- MAJOR: Geriye uyumsuz değişiklikler
- MINOR: Geriye uyumlu yeni özellikler
- PATCH: Geriye uyumlu hata düzeltmeleri

## Destek

Sorular ve öneriler için issue açabilirsiniz.
