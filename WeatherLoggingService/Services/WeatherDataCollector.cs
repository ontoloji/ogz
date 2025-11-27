using WeatherLoggingService.Models;
using Microsoft.Extensions.Logging;

namespace WeatherLoggingService.Services;

public class WeatherDataCollector
{
    private readonly ILogger<WeatherDataCollector> _logger;
    private readonly WeatherLogger _weatherLogger;
    private readonly List<IWeatherDataProvider> _providers;
    private readonly WeatherServiceConfiguration _configuration;

    public WeatherDataCollector(
        ILogger<WeatherDataCollector> logger,
        WeatherLogger weatherLogger,
        WeatherServiceConfiguration configuration)
    {
        _logger = logger;
        _weatherLogger = weatherLogger;
        _configuration = configuration;
        _providers = new List<IWeatherDataProvider>();
    }

    public void RegisterProvider(IWeatherDataProvider provider)
    {
        _providers.Add(provider);
        _logger.LogInformation("Hava durumu sağlayıcısı kaydedildi: {Provider}", provider.ProviderName);
    }

    public async Task CollectAndLogWeatherDataAsync()
    {
        _logger.LogInformation("Hava durumu verileri toplanıyor...");

        var tasks = new List<Task>();

        foreach (var location in _configuration.Locations.Where(l => l.Enabled))
        {
            foreach (var provider in _providers)
            {
                tasks.Add(CollectForLocationAndProviderAsync(location, provider));
            }
        }

        await Task.WhenAll(tasks);

        _logger.LogInformation("Hava durumu verileri toplama işlemi tamamlandı.");
    }

    private async Task CollectForLocationAndProviderAsync(Location location, IWeatherDataProvider provider)
    {
        try
        {
            _logger.LogInformation(
                "Veri alınıyor: {Provider} - {Location}",
                provider.ProviderName,
                location.Name);

            var weatherData = await provider.GetWeatherDataAsync(location);

            if (weatherData != null)
            {
                await _weatherLogger.LogWeatherDataAsync(weatherData);
            }
            else
            {
                _logger.LogWarning(
                    "Veri alınamadı: {Provider} - {Location}",
                    provider.ProviderName,
                    location.Name);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex,
                "Veri toplama hatası: {Provider} - {Location}",
                provider.ProviderName,
                location.Name);
        }
    }

    public string GetProviderSummary()
    {
        return $"Kayıtlı Sağlayıcılar: {string.Join(", ", _providers.Select(p => p.ProviderName))}";
    }
}
