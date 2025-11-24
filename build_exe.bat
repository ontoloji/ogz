@echo off
REM Internet Radyo Çalar - EXE Build Script
REM PyInstaller ile Windows EXE dosyası oluşturur

echo.
echo ========================================
echo   Internet Radyo Çalar - EXE Builder
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadı!
    echo Lütfen Python 3.8 veya üzeri yükleyin.
    pause
    exit /b 1
)

echo [1/6] PyInstaller kontrolü...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller bulunamadı. Yükleniyor...
    pip install pyinstaller
) else (
    echo PyInstaller kurulu: OK
)

echo.
echo [2/6] Bağımlılıkları kontrol ediliyor...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo PyQt5 yükleniyor...
    pip install PyQt5>=5.15.0
)

python -c "import vlc" >nul 2>&1
if errorlevel 1 (
    echo python-vlc yükleniyor...
    pip install python-vlc>=3.0.0
)

echo Bağımlılıklar: OK
echo.

REM Eski build'leri temizle
echo [3/6] Eski build dosyaları temizleniyor...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo Temizleme tamamlandı.
echo.

REM Kullanıcıya seçenek sun
echo Build tipi seçin:
echo [1] Tek dosya (portable) - InternetRadyoCalar.exe (~80 MB, yavaş başlatma)
echo [2] Klasör (önerilir) - InternetRadyoCalar/ klasörü (~60 MB, hızlı başlatma)
echo [3] Her ikisi
echo.
set /p choice="Seçiminiz (1/2/3): "

if "%choice%"=="1" goto build_onefile
if "%choice%"=="2" goto build_folder
if "%choice%"=="3" goto build_both
echo Geçersiz seçim!
pause
exit /b 1

:build_onefile
echo.
echo [4/6] Tek dosya EXE oluşturuluyor...
pyinstaller --clean internet_radio_player.spec
if errorlevel 1 goto error
echo Tek dosya EXE oluşturuldu: dist\InternetRadyoCalar.exe
goto success

:build_folder
echo.
echo [4/6] Klasör tabanlı EXE oluşturuluyor...
pyinstaller --clean internet_radio_player_folder.spec
if errorlevel 1 goto error
echo Klasör tabanlı EXE oluşturuldu: dist\InternetRadyoCalar\
goto success

:build_both
echo.
echo [4/6] Tek dosya EXE oluşturuluyor...
pyinstaller --clean internet_radio_player.spec
if errorlevel 1 goto error
echo Tek dosya tamamlandı.
echo.
echo [5/6] Klasör tabanlı EXE oluşturululuyor...
pyinstaller --clean internet_radio_player_folder.spec
if errorlevel 1 goto error
echo Her iki build tamamlandı.
goto success

:success
echo.
echo [6/6] README kopyalanıyor...
if exist "dist\RADIO_README.md" (
    echo README zaten mevcut
) else (
    copy RADIO_README.md dist\ >nul 2>&1
)

if exist "dist\InternetRadyoCalar\" (
    copy RADIO_README.md "dist\InternetRadyoCalar\" >nul 2>&1
    copy radio_favorites_example.json "dist\InternetRadyoCalar\" >nul 2>&1
)

echo.
echo ========================================
echo   BUILD BAŞARILI!
echo ========================================
echo.
echo Dosyalar 'dist' klasöründe:
dir /b dist
echo.
echo ÖNEMLI: VLC Media Player kullanıcıların sisteminde kurulu olmalıdır!
echo VLC İndirme: https://www.videolan.org/vlc/
echo.
echo Dağıtım için 'dist' klasöründeki dosyaları paylaşın.
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo   BUILD HATASI!
echo ========================================
echo.
echo Hata oluştu. Lütfen yukarıdaki hata mesajlarını kontrol edin.
echo.
pause
exit /b 1
