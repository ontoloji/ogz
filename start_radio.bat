@echo off
REM Internet Radyo Çalar Başlatıcı
REM Windows için

echo.
echo ========================================
echo   Internet Radyo Çalar Başlatılıyor
echo ========================================
echo.

REM Python kontrol
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadı!
    echo Lütfen Python 3.8 veya üzeri yükleyin.
    echo İndirme: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM VLC kontrol (opsiyonel uyarı)
if not exist "C:\Program Files\VideoLAN\VLC\vlc.exe" (
    if not exist "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" (
        echo UYARI: VLC Media Player bulunamadı!
        echo Lütfen VLC'yi yükleyin: https://www.videolan.org/vlc/
        echo.
        pause
    )
)

REM Bağımlılıkları kontrol et
echo Bağımlılıklar kontrol ediliyor...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo PyQt5 bulunamadı. Yükleniyor...
    pip install PyQt5>=5.15.0
)

python -c "import vlc" >nul 2>&1
if errorlevel 1 (
    echo python-vlc bulunamadı. Yükleniyor...
    pip install python-vlc>=3.0.0
)

echo.
echo Radyo Çalar başlatılıyor...
echo.

REM Uygulamayı başlat
python internet_radio_player.py

if errorlevel 1 (
    echo.
    echo HATA: Uygulama başlatılamadı!
    echo Lütfen RADIO_README.md dosyasını okuyun.
    pause
)
