@echo off
REM Elektrikli Araç Enerji Analiz Sistemi Başlatıcı
REM Windows için

echo ================================================
echo   Elektrikli Araç Enerji Analiz Sistemi
echo ================================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo.
    echo Python 3.8 veya uzeri kurmaniz gerekmektedir.
    echo Indirmek icin: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python bulundu:
python --version
echo.

REM Gerekli kütüphaneleri kontrol et
echo Kutuphaneler kontrol ediliyor...
python -c "import pandas, numpy, matplotlib, openpyxl, reportlab" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [UYARI] Bazi kutuphaneler eksik!
    echo Kurmak ister misiniz? (E/H)
    set /p install="Secim: "

    if /i "%install%"=="E" (
        echo.
        echo Kutuphaneler kuruluyor...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo.
            echo [HATA] Kutuphaneler kurulamadi!
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Lutfen once kutuphaneleri kurun:
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo Kutuphaneler hazir!
echo.

REM Uygulamayı başlat
echo Uygulama baslatiliyor...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [HATA] Uygulama baslatma hatasi!
    echo.
    pause
)
