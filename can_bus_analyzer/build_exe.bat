@echo off
REM CAN Bus Analyzer - EXE Build Script
REM Windows için PyInstaller build scripti

echo ========================================
echo CAN Bus Analyzer - EXE Olusturucu
echo ========================================
echo.

REM Virtual environment kontrolu
if not exist "venv" (
    echo Virtual environment bulunamadi!
    echo Once 'python -m venv venv' komutu ile virtual environment olusturun.
    echo Sonra 'venv\Scripts\activate' ile aktif edin.
    echo Son olarak 'pip install -r requirements.txt' ile bagimliliklari yukleyin.
    pause
    exit /b 1
)

REM Onceki build dosyalarini temizle
echo Onceki build dosyalari temizleniyor...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

echo.
echo PyInstaller ile EXE olusturuluyor...
echo.

REM PyInstaller komutu
pyinstaller --name="CAN_Bus_Analyzer" ^
    --onefile ^
    --windowed ^
    --icon=resources\icon.ico ^
    --add-data "resources;resources" ^
    --hidden-import="can.interfaces.kvaser" ^
    --hidden-import="can.interfaces.vector" ^
    --hidden-import="tkinter" ^
    --hidden-import="matplotlib" ^
    --hidden-import="pandas" ^
    --hidden-import="openpyxl" ^
    --hidden-import="cantools" ^
    --collect-all="can" ^
    --collect-all="cantools" ^
    --noconfirm ^
    src\can_analyzer_gui.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BUILD BASARILI!
    echo ========================================
    echo.
    echo EXE dosyasi: dist\CAN_Bus_Analyzer.exe
    echo.
    echo Kullanim:
    echo 1. dist\CAN_Bus_Analyzer.exe dosyasini calistirin
    echo 2. Kvaser CANlib SDK'nin yuklu oldugunu kontrol edin
    echo 3. DBC dosyanizi yukleyin
    echo 4. CAN cihazina baglanin
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD HATASI!
    echo ========================================
    echo.
    echo Hata kodu: %errorlevel%
    echo Lutfen hata mesajlarini kontrol edin.
    echo.
)

pause
