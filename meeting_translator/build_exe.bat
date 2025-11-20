@echo off
echo ====================================
echo Meeting Translator - EXE Builder
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

pyinstaller --clean meeting_translator.spec

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
echo EXE dosyasi olusturuldu:
echo   dist\MeetingTranslator.exe
echo.
echo Bu dosyayi kopyalayarak baska bilgisayarlarda
echo Python yuklemeden kullanabilirsiniz.
echo.
echo ONEMLI NOTLAR:
echo - Ilk calistiginda Whisper modeli indirilecek
echo - Windows Defender uyarisi verebilir (guvenli)
echo - Stereo Mix yine de etkinlestirilmelidir
echo.
pause
