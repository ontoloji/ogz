using WeatherLoggingService.Models;

namespace WeatherLoggingService.Services;

public interface IWeatherDataProvider
{
    string ProviderName { get; }
    Task<WeatherData?> GetWeatherDataAsync(Location location);
}
