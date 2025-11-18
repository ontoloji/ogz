@echo off
echo ========================================
echo Windows Personal Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Lutfen once install.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
echo Uygulama baslatiliyor...
echo.
python src/main.py

REM Deactivate when done
deactivate
