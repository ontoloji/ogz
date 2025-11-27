using System.Text;
using WeatherLoggingService.Models;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace WeatherLoggingService.Services;

public class WeatherLogger
{
    private readonly ILogger<WeatherLogger> _logger;
    private readonly string _logDirectory;

    public WeatherLogger(ILogger<WeatherLogger> logger, string logDirectory)
    {
        _logger = logger;
        _logDirectory = logDirectory;

        // Ensure log directory exists
        if (!Directory.Exists(_logDirectory))
        {
            Directory.CreateDirectory(_logDirectory);
            _logger.LogInformation("Log dizini oluşturuldu: {Directory}", _logDirectory);
        }
    }

    public async Task LogWeatherDataAsync(WeatherData weatherData)
    {
        try
        {
            // Create provider-specific directory
            var providerDir = Path.Combine(_logDirectory, weatherData.ProviderName);
            if (!Directory.Exists(providerDir))
            {
                Directory.CreateDirectory(providerDir);
            }

            // Create location-specific subdirectory
            var locationDir = Path.Combine(providerDir, SanitizeFileName(weatherData.LocationName));
            if (!Directory.Exists(locationDir))
            {
                Directory.CreateDirectory(locationDir);
            }

            // Create daily log file
            var date = weatherData.Timestamp.ToString("yyyy-MM-dd");
            var logFileName = $"weather_{date}.json";
            var logFilePath = Path.Combine(locationDir, logFileName);

            // Append to JSON array
            var logEntry = new
            {
                timestamp = weatherData.Timestamp.ToString("yyyy-MM-dd HH:mm:ss"),
                location = weatherData.LocationName,
                latitude = weatherData.Latitude,
                longitude = weatherData.Longitude,
                provider = weatherData.ProviderName,
                temperature_celsius = weatherData.Temperature,
                rain_mm = weatherData.RainAmount,
                rain_probability_percent = weatherData.RainProbability,
                wind_speed_ms = weatherData.WindSpeed,
                wind_direction_degrees = weatherData.WindDirection,
                wind_direction_text = weatherData.WindDirectionText,
                humidity_percent = weatherData.Humidity,
                pressure_hpa = weatherData.Pressure,
                description = weatherData.Description
            };

            List<object> entries;
            if (File.Exists(logFilePath))
            {
                var existingContent = await File.ReadAllTextAsync(logFilePath);
                entries = JsonConvert.DeserializeObject<List<object>>(existingContent) ?? new List<object>();
            }
            else
            {
                entries = new List<object>();
            }

            entries.Add(logEntry);

            var jsonContent = JsonConvert.SerializeObject(entries, Formatting.Indented);
            await File.WriteAllTextAsync(logFilePath, jsonContent);

            // Also create a CSV log for easier analysis
            await LogToCsvAsync(weatherData, locationDir);

            // Save raw response separately
            if (!string.IsNullOrEmpty(weatherData.RawResponse))
            {
                var rawDir = Path.Combine(locationDir, "raw");
                if (!Directory.Exists(rawDir))
                {
                    Directory.CreateDirectory(rawDir);
                }

                var rawFileName = $"raw_{weatherData.Timestamp:yyyy-MM-dd_HH-mm-ss}.json";
                var rawFilePath = Path.Combine(rawDir, rawFileName);
                await File.WriteAllTextAsync(rawFilePath, weatherData.RawResponse);
            }

            _logger.LogInformation(
                "Hava durumu kaydedildi: {Provider}/{Location} - {File}",
                weatherData.ProviderName,
                weatherData.LocationName,
                logFilePath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Hava durumu kaydedilirken hata: {Location}", weatherData.LocationName);
        }
    }

    private async Task LogToCsvAsync(WeatherData weatherData, string locationDir)
    {
        var date = weatherData.Timestamp.ToString("yyyy-MM-dd");
        var csvFileName = $"weather_{date}.csv";
        var csvFilePath = Path.Combine(locationDir, csvFileName);

        var fileExists = File.Exists(csvFilePath);

        using var writer = new StreamWriter(csvFilePath, append: true, Encoding.UTF8);

        // Write header if new file
        if (!fileExists)
        {
            await writer.WriteLineAsync("Timestamp,Location,Latitude,Longitude,Provider,Temperature(°C),Rain(mm),WindSpeed(m/s),WindDirection,Humidity(%),Pressure(hPa),Description");
        }

        // Write data
        var line = $"{weatherData.Timestamp:yyyy-MM-dd HH:mm:ss}," +
                   $"\"{weatherData.LocationName}\"," +
                   $"{weatherData.Latitude}," +
                   $"{weatherData.Longitude}," +
                   $"{weatherData.ProviderName}," +
                   $"{weatherData.Temperature}," +
                   $"{weatherData.RainAmount ?? 0}," +
                   $"{weatherData.WindSpeed}," +
                   $"{weatherData.WindDirectionText ?? weatherData.WindDirection?.ToString() ?? "N/A"}," +
                   $"{weatherData.Humidity ?? 0}," +
                   $"{weatherData.Pressure ?? 0}," +
                   $"\"{weatherData.Description ?? ""}\"";

        await writer.WriteLineAsync(line);
    }

    private static string SanitizeFileName(string fileName)
    {
        var invalidChars = Path.GetInvalidFileNameChars();
        var sanitized = string.Join("_", fileName.Split(invalidChars, StringSplitOptions.RemoveEmptyEntries));
        return sanitized.Replace(" ", "_");
    }

    public string GetLogSummary()
    {
        if (!Directory.Exists(_logDirectory))
        {
            return "Log dizini bulunamadı.";
        }

        var summary = new StringBuilder();
        summary.AppendLine($"Log Dizini: {_logDirectory}");
        summary.AppendLine();

        var providers = Directory.GetDirectories(_logDirectory);
        foreach (var providerDir in providers)
        {
            var providerName = Path.GetFileName(providerDir);
            summary.AppendLine($"Sağlayıcı: {providerName}");

            var locations = Directory.GetDirectories(providerDir);
            foreach (var locationDir in locations)
            {
                var locationName = Path.GetFileName(locationDir);
                var fileCount = Directory.GetFiles(locationDir, "*.json").Length;
                summary.AppendLine($"  - {locationName}: {fileCount} dosya");
            }

            summary.AppendLine();
        }

        return summary.ToString();
    }
}
