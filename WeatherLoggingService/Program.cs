using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Serilog;
using WeatherLoggingService;
using WeatherLoggingService.Models;
using WeatherLoggingService.Services;

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .WriteTo.Console()
    .WriteTo.File(
        "logs/weather-service-.log",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 30)
    .CreateLogger();

try
{
    Log.Information("Hava Durumu Loglama Servisi başlatılıyor...");

    var builder = Host.CreateApplicationBuilder(args);

    // Load configuration
    builder.Configuration
        .SetBasePath(Directory.GetCurrentDirectory())
        .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

    // Add Serilog
    builder.Services.AddSerilog();

    // Load weather service configuration
    var weatherConfig = builder.Configuration
        .GetSection("WeatherService")
        .Get<WeatherServiceConfiguration>() ?? new WeatherServiceConfiguration();

    builder.Services.AddSingleton(weatherConfig);

    // Register services
    builder.Services.AddHttpClient();

    builder.Services.AddSingleton<WeatherLogger>(sp =>
    {
        var logger = sp.GetRequiredService<ILogger<WeatherLogger>>();
        return new WeatherLogger(logger, weatherConfig.LogDirectory);
    });

    builder.Services.AddSingleton<WeatherDataCollector>(sp =>
    {
        var logger = sp.GetRequiredService<ILogger<WeatherDataCollector>>();
        var weatherLogger = sp.GetRequiredService<WeatherLogger>();
        var collector = new WeatherDataCollector(logger, weatherLogger, weatherConfig);

        // Register enabled providers
        var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();

        foreach (var providerConfig in weatherConfig.WeatherProviders.Where(p => p.Enabled))
        {
            var httpClient = httpClientFactory.CreateClient();

            if (providerConfig.Name == "OpenWeatherMap")
            {
                var providerLogger = sp.GetRequiredService<ILogger<OpenWeatherMapProvider>>();
                var provider = new OpenWeatherMapProvider(
                    httpClient,
                    providerLogger,
                    providerConfig.ApiKey,
                    providerConfig.Url);
                collector.RegisterProvider(provider);
            }
            else if (providerConfig.Name == "WeatherAPI")
            {
                var providerLogger = sp.GetRequiredService<ILogger<WeatherAPIProvider>>();
                var provider = new WeatherAPIProvider(
                    httpClient,
                    providerLogger,
                    providerConfig.ApiKey,
                    providerConfig.Url);
                collector.RegisterProvider(provider);
            }
        }

        return collector;
    });

    // Register worker
    builder.Services.AddSingleton<Worker>(sp =>
    {
        var logger = sp.GetRequiredService<ILogger<Worker>>();
        var collector = sp.GetRequiredService<WeatherDataCollector>();
        return new Worker(logger, collector, weatherConfig.LogIntervalMinutes);
    });

    builder.Services.AddHostedService(sp => sp.GetRequiredService<Worker>());

    // Configure as Windows Service
    builder.Services.AddWindowsService(options =>
    {
        options.ServiceName = "Weather Logging Service";
    });

    var host = builder.Build();

    Log.Information("Servis yapılandırması tamamlandı.");
    Log.Information("Log Dizini: {LogDirectory}", weatherConfig.LogDirectory);
    Log.Information("Log Aralığı: {Interval} dakika", weatherConfig.LogIntervalMinutes);
    Log.Information("Lokasyonlar: {Locations}",
        string.Join(", ", weatherConfig.Locations.Where(l => l.Enabled).Select(l => l.Name)));

    await host.RunAsync();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Servis başlatılamadı");
    return 1;
}
finally
{
    Log.CloseAndFlush();
}

return 0;
