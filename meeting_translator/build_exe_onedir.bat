@echo off
echo ====================================
echo Meeting Translator - EXE Builder
echo (Dizin Versiyonu - Daha kucuk)
echo ====================================
echo.

REM Sanal ortam kontrolü
if not exist "venv\Scripts\activate.bat" (
    echo Sanal ortam bulunamadi. Once install.bat dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

echo Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat
echo.

echo PyInstaller kontrol ediliyor...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller yukleniyor...
    pip install pyinstaller
    echo.
)

echo Eski build dosyalari temizleniyor...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo.

echo ====================================
echo EXE dosyasi olusturuluyor...
echo (Bu islem 5-10 dakika surebilir)
echo ====================================
echo.

pyinstaller --clean meeting_translator_onedir.spec

if %errorlevel% neq 0 (
    echo.
    echo HATA: EXE olusturulamadi!
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================
echo Basarili!
echo ====================================
echo.
echo EXE klasoru olusturuldu:
echo   dist\MeetingTranslator\
echo.
echo Bu klasoru kopyalayarak baska bilgisayarlarda
echo Python yuklemeden kullanabilirsiniz.
echo.
echo Calistirmak icin:
echo   dist\MeetingTranslator\MeetingTranslator.exe
echo.
echo ONEMLI NOTLAR:
echo - Ilk calistiginda Whisper modeli indirilecek
echo - Windows Defender uyarisi verebilir (guvenli)
echo - Stereo Mix yine de etkinlestirilmelidir
echo - Dizin versiyonu daha hizli baslar
echo.
pause
