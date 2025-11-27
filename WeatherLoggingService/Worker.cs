using WeatherLoggingService.Services;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace WeatherLoggingService;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly WeatherDataCollector _dataCollector;
    private readonly int _intervalMinutes;
    private Timer? _timer;

    public Worker(
        ILogger<Worker> logger,
        WeatherDataCollector dataCollector,
        int intervalMinutes)
    {
        _logger = logger;
        _dataCollector = dataCollector;
        _intervalMinutes = intervalMinutes;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Hava Durumu Loglama Servisi başlatıldı.");
        _logger.LogInformation("Log aralığı: {Interval} dakika", _intervalMinutes);
        _logger.LogInformation(_dataCollector.GetProviderSummary());

        // Run immediately on start
        await CollectWeatherDataAsync();

        // Calculate time until next hour
        var now = DateTime.Now;
        var nextHour = now.Date.AddHours(now.Hour + 1);
        var timeUntilNextHour = nextHour - now;

        _logger.LogInformation("İlk zamanlanmış toplama: {NextRun}", nextHour);

        // Wait until next hour, then start hourly timer
        await Task.Delay(timeUntilNextHour, stoppingToken);

        if (!stoppingToken.IsCancellationRequested)
        {
            await CollectWeatherDataAsync();

            // Start hourly timer
            var intervalMs = _intervalMinutes * 60 * 1000;
            _timer = new Timer(
                async _ => await CollectWeatherDataAsync(),
                null,
                intervalMs,
                intervalMs);

            _logger.LogInformation("Saatlik zamanlayıcı başlatıldı.");
        }

        // Keep service running
        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
    }

    private async Task CollectWeatherDataAsync()
    {
        try
        {
            _logger.LogInformation("==========================================");
            _logger.LogInformation("Hava durumu toplama başlıyor: {Time}", DateTime.Now);
            _logger.LogInformation("==========================================");

            await _dataCollector.CollectAndLogWeatherDataAsync();

            _logger.LogInformation("==========================================");
            _logger.LogInformation("Hava durumu toplama tamamlandı: {Time}", DateTime.Now);
            _logger.LogInformation("==========================================");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Hava durumu toplama sırasında hata oluştu");
        }
    }

    public override async Task StopAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Hava Durumu Loglama Servisi durduruluyor...");

        _timer?.Change(Timeout.Infinite, 0);
        _timer?.Dispose();

        await base.StopAsync(stoppingToken);

        _logger.LogInformation("Hava Durumu Loglama Servisi durduruldu.");
    }
}
