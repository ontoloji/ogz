namespace WeatherLoggingService.Models;

public class WeatherData
{
    public DateTime Timestamp { get; set; }
    public string LocationName { get; set; } = string.Empty;
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public string ProviderName { get; set; } = string.Empty;
    public double Temperature { get; set; } // Celsius
    public double? RainAmount { get; set; } // mm
    public double? RainProbability { get; set; } // %
    public double WindSpeed { get; set; } // m/s
    public double? WindDirection { get; set; } // degrees
    public string? WindDirectionText { get; set; }
    public double? Humidity { get; set; } // %
    public double? Pressure { get; set; } // hPa
    public string? Description { get; set; }
    public string? RawResponse { get; set; }
}

public class Location
{
    public string Name { get; set; } = string.Empty;
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public bool Enabled { get; set; } = true;
}

public class WeatherProvider
{
    public string Name { get; set; } = string.Empty;
    public bool Enabled { get; set; } = true;
    public string ApiKey { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
}

public class WeatherServiceConfiguration
{
    public int LogIntervalMinutes { get; set; } = 60;
    public string LogDirectory { get; set; } = "C:\\WeatherLogs";
    public List<Location> Locations { get; set; } = new();
    public List<WeatherProvider> WeatherProviders { get; set; } = new();
}
