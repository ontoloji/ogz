@echo off
REM Gizli Web Tarayıcı Başlatıcı - Windows Batch Script
REM Kayıt tutmayan gizli tarayıcıyı başlatır

echo.
echo ================================================
echo    🔒 Gizli Web Tarayıcı Başlatılıyor...
echo ================================================
echo.
echo Gizlilik Özellikleri:
echo   ✓ Geçmiş kaydetmez
echo   ✓ Çerez kaydetmez
echo   ✓ Önbellek oluşturmaz
echo   ✓ İzleme engelleyici aktif
echo.
echo ================================================
echo.

REM Python kurulu mu kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadı!
    echo.
    echo Python'u yüklemek için:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM PyQt6 kurulu mu kontrol et
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo UYARI: PyQt6 bulunamadı!
    echo.
    echo Bağımlılıklar yükleniyor...
    pip install PyQt6 PyQt6-WebEngine
    echo.
)

REM Tarayıcıyı başlat
echo Tarayıcı başlatılıyor...
echo.
python private_browser.py

REM Hata durumunda
if errorlevel 1 (
    echo.
    echo ================================================
    echo HATA: Tarayıcı başlatılamadı!
    echo ================================================
    echo.
    echo Çözüm önerileri:
    echo 1. "pip install -r requirements.txt" komutunu çalıştırın
    echo 2. Python sürümünüzü kontrol edin (3.9+ gerekli)
    echo 3. BROWSER_README.md dosyasını okuyun
    echo.
    pause
    exit /b 1
)

exit /b 0
