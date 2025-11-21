@echo off
REM CAN Bus Analyzer - Quick Start Script
REM Uygulamayi calistirmak icin bu dosyayi cift tiklayin

echo ========================================
echo CAN Bus Analyzer v1.0
echo ========================================
echo.

REM Virtual environment kontrolu
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment aktif ediliyor...
    call venv\Scripts\activate.bat
) else (
    echo UYARI: Virtual environment bulunamadi!
    echo Python ortami kullaniliyor...
)

echo.
echo Uygulama baslatiliyor...
echo.

REM Uygulamayi calistir
cd src
python can_analyzer_gui.py

REM Hata kontrolu
if %errorlevel% neq 0 (
    echo.
    echo HATA: Uygulama baslamadi!
    echo.
    echo Olasi cozumler:
    echo 1. Python yuklu oldugundan emin olun: python --version
    echo 2. Bagimliliklari yukleyin: pip install -r requirements.txt
    echo 3. Kvaser CANlib SDK yuklu oldugundan emin olun
    echo.
    pause
    exit /b 1
)

pause
