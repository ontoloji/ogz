@echo off
REM Araç Kalifikasyon Takip Sistemi Başlatıcı
REM Windows için batch dosyası

echo ============================================
echo Araç Kalifikasyon Takip Sistemi
echo ============================================
echo.

REM Python kurulu mu kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadı!
    echo Lütfen Python 3.10 veya üzeri yükleyin.
    pause
    exit /b 1
)

echo Python bulundu.
echo.

REM Gerekli paketleri kontrol et
echo Gerekli Python paketleri kontrol ediliyor...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo PyQt6 bulunamadı. Yükleniyor...
    pip install PyQt6
)

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo pandas bulunamadı. Yükleniyor...
    pip install pandas openpyxl
)

echo.
echo Program başlatılıyor...
echo.

REM Programı başlat
python vehicle_qualification_gui.py

REM Hata kontrolü
if errorlevel 1 (
    echo.
    echo HATA: Program çalıştırılamadı!
    echo.
    pause
    exit /b 1
)
