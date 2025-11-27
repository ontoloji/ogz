using System.Text.Json;
using WeatherLoggingService.Models;
using Microsoft.Extensions.Logging;

namespace WeatherLoggingService.Services;

public class WeatherAPIProvider : IWeatherDataProvider
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<WeatherAPIProvider> _logger;
    private readonly string _apiKey;
    private readonly string _baseUrl;

    public string ProviderName => "WeatherAPI";

    public WeatherAPIProvider(
        HttpClient httpClient,
        ILogger<WeatherAPIProvider> logger,
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
            var url = $"{_baseUrl}?key={_apiKey}&q={location.Latitude},{location.Longitude}&lang=tr";

            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var content = await response.Content.ReadAsStringAsync();
            var json = JsonDocument.Parse(content);
            var root = json.RootElement;

            var current = root.GetProperty("current");

            var weatherData = new WeatherData
            {
                Timestamp = DateTime.Now,
                LocationName = location.Name,
                Latitude = location.Latitude,
                Longitude = location.Longitude,
                ProviderName = ProviderName,
                Temperature = current.GetProperty("temp_c").GetDouble(),
                Humidity = current.GetProperty("humidity").GetDouble(),
                Pressure = current.GetProperty("pressure_mb").GetDouble(),
                WindSpeed = current.GetProperty("wind_kph").GetDouble() / 3.6, // Convert km/h to m/s
                WindDirection = current.GetProperty("wind_degree").GetDouble(),
                WindDirectionText = current.GetProperty("wind_dir").GetString(),
                RainAmount = current.GetProperty("precip_mm").GetDouble(),
                Description = current.GetProperty("condition").GetProperty("text").GetString(),
                RawResponse = content
            };

            _logger.LogInformation(
                "WeatherAPI: {Location} - Sıcaklık: {Temp}°C, Rüzgar: {Wind} m/s, Yağmur: {Rain} mm",
                location.Name,
                weatherData.Temperature,
                weatherData.WindSpeed,
                weatherData.RainAmount ?? 0);

            return weatherData;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WeatherAPI verisi alınırken hata: {Location}", location.Name);
            return null;
        }
    }
}
