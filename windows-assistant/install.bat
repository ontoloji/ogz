@echo off
echo ========================================
echo Windows Personal Assistant - Kurulum
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python 3.8 veya uzeri yuklediginizden emin olun.
    echo Python'u https://www.python.org/downloads/ adresinden indirebilirsiniz.
    pause
    exit /b 1
)

echo [1/4] Python bulundu
python --version
echo.

REM Create virtual environment
echo [2/4] Sanal ortam olusturuluyor...
if not exist "venv" (
    python -m venv venv
    echo Sanal ortam basariyla olusturuldu.
) else (
    echo Sanal ortam zaten mevcut.
)
echo.

REM Activate virtual environment
echo [3/4] Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo [4/4] Bagimliliklar yukleniyor...
pip install -r requirements.txt
echo.

echo ========================================
echo Kurulum tamamlandi!
echo ========================================
echo.
echo Uygulamayi calistirmak icin:
echo   1. venv\Scripts\activate
echo   2. python src/main.py
echo.
echo veya dogrudan:
echo   run.bat
echo.
pause
