using System.Text.Json;
using WeatherLoggingService.Models;
using Microsoft.Extensions.Logging;

namespace WeatherLoggingService.Services;

public class OpenWeatherMapProvider : IWeatherDataProvider
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<OpenWeatherMapProvider> _logger;
    private readonly string _apiKey;
    private readonly string _baseUrl;

    public string ProviderName => "OpenWeatherMap";

    public OpenWeatherMapProvider(
        HttpClient httpClient,
        ILogger<OpenWeatherMapProvider> logger,
        string apiKey,
        string baseUrl)
    {
        _httpClient = httpClient;
        _logger = logger;
        _apiKey = apiKey;
        _baseUrl = baseUrl;
    }

    public async Task<WeatherData?> GetWeatherDataAsync(Location location)
    {
        try
        {
            var url = $"{_baseUrl}?lat={location.Latitude}&lon={location.Longitude}&appid={_apiKey}&units=metric&lang=tr";

            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var content = await response.Content.ReadAsStringAsync();
            var json = JsonDocument.Parse(content);
            var root = json.RootElement;

            var weatherData = new WeatherData
            {
                Timestamp = DateTime.Now,
                LocationName = location.Name,
                Latitude = location.Latitude,
                Longitude = location.Longitude,
                ProviderName = ProviderName,
                Temperature = root.GetProperty("main").GetProperty("temp").GetDouble(),
                Humidity = root.GetProperty("main").GetProperty("humidity").GetDouble(),
                Pressure = root.GetProperty("main").GetProperty("pressure").GetDouble(),
                WindSpeed = root.GetProperty("wind").GetProperty("speed").GetDouble(),
                RawResponse = content
            };

            // Wind direction
            if (root.GetProperty("wind").TryGetProperty("deg", out var windDeg))
            {
                weatherData.WindDirection = windDeg.GetDouble();
                weatherData.WindDirectionText = GetWindDirection(windDeg.GetDouble());
            }

            // Rain data
            if (root.TryGetProperty("rain", out var rain))
            {
                if (rain.TryGetProperty("1h", out var rain1h))
                {
                    weatherData.RainAmount = rain1h.GetDouble();
                }
            }

            // Weather description
            if (root.TryGetProperty("weather", out var weather) && weather.GetArrayLength() > 0)
            {
                weatherData.Description = weather[0].GetProperty("description").GetString();
            }

            _logger.LogInformation(
                "OpenWeatherMap: {Location} - Sıcaklık: {Temp}°C, Rüzgar: {Wind} m/s, Yağmur: {Rain} mm",
                location.Name,
                weatherData.Temperature,
                weatherData.WindSpeed,
                weatherData.RainAmount ?? 0);

            return weatherData;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "OpenWeatherMap verisi alınırken hata: {Location}", location.Name);
            return null;
        }
    }

    private static string GetWindDirection(double degrees)
    {
        var directions = new[] { "K", "KD", "D", "GD", "G", "GB", "B", "KB" };
        var index = (int)Math.Round(degrees / 45.0) % 8;
        return directions[index];
    }
}
