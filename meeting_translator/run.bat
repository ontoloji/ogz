@echo off
echo ====================================
echo Meeting Translator
echo ====================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Lutfen once "install.bat" dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

echo Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo Uygulama baslatiliyor...
echo.
python main.py

pause
