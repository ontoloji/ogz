@echo off
REM Wealth Tracker Launcher for Windows

echo ===================================
echo   Wealth Tracker Baslatiliyor...
echo ===================================
echo.

REM Gerekli paketleri kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python'u yukleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Gerekli kutuphaneleri yukle
echo Gerekli kutuphaneler kontrol ediliyor...
pip install -r requirements.txt >nul 2>&1

REM Uygulamayi baslat
echo.
echo Uygulama baslatiliyor...
echo.
python main.py

pause
