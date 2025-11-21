@echo off
REM Windows AI Kişisel Asistan Başlatıcı

echo ========================================
echo   AI Kişisel Asistan Başlatılıyor...
echo ========================================
echo.

REM Python kurulu mu kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lütfen Python 3.8 veya üzerini yükleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Gerekli kütüphaneler kurulu mu kontrol et
python -c "import pystray" >nul 2>&1
if errorlevel 1 (
    echo Gerekli kütüphaneler yükleniyor...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo HATA: Kütüphaneler yüklenemedi!
        pause
        exit /b 1
    )
)

REM Uygulamayı başlat
echo.
echo Uygulama başlatıldı!
echo Ctrl+Shift+A ile asistan penceresini açabilirsiniz.
echo.
python main.py

if errorlevel 1 (
    echo.
    echo HATA: Uygulama başlatılamadı!
    pause
)
