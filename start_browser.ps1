# Gizli Web Tarayıcı Başlatıcı - Windows PowerShell Script
# Kayıt tutmayan gizli tarayıcıyı başlatır

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   🔒 Gizli Web Tarayıcı Başlatılıyor...      " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Gizlilik Özellikleri:" -ForegroundColor Green
Write-Host "  ✓ Geçmiş kaydetmez" -ForegroundColor Gray
Write-Host "  ✓ Çerez kaydetmez" -ForegroundColor Gray
Write-Host "  ✓ Önbellek oluşturmaz" -ForegroundColor Gray
Write-Host "  ✓ İzleme engelleyici aktif" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Python kurulu mu kontrol et
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python bulundu: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "HATA: Python bulunamadı!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python'u yüklemek için:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

# PyQt6 kurulu mu kontrol et
Write-Host ""
Write-Host "Bağımlılıklar kontrol ediliyor..." -ForegroundColor Yellow

$pyqt6Check = python -c "import PyQt6" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "UYARI: PyQt6 bulunamadı!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Bağımlılıklar yükleniyor..." -ForegroundColor Cyan
    pip install PyQt6 PyQt6-WebEngine
    Write-Host ""
}

$webengineCheck = python -c "import PyQt6.QtWebEngineWidgets" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "UYARI: PyQt6-WebEngine bulunamadı!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WebEngine yükleniyor..." -ForegroundColor Cyan
    pip install PyQt6-WebEngine
    Write-Host ""
}

# Tarayıcıyı başlat
Write-Host "Tarayıcı başlatılıyor..." -ForegroundColor Green
Write-Host ""

try {
    python private_browser.py

    if ($LASTEXITCODE -ne 0) {
        throw "Tarayıcı başlatma hatası"
    }

    Write-Host ""
    Write-Host "Tarayıcı kapatıldı. Tüm veriler temizlendi." -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "HATA: Tarayıcı başlatılamadı!" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Çözüm önerileri:" -ForegroundColor Yellow
    Write-Host "1. 'pip install -r requirements.txt' komutunu çalıştırın" -ForegroundColor Gray
    Write-Host "2. Python sürümünüzü kontrol edin (3.9+ gerekli)" -ForegroundColor Gray
    Write-Host "3. BROWSER_README.md dosyasını okuyun" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Hata detayı: $_" -ForegroundColor Red
    Write-Host ""
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

exit 0
