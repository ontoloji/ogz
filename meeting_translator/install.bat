@echo off
echo ====================================
echo Meeting Translator Kurulum
echo ====================================
echo.

echo Python versiyonu kontrol ediliyor...
python --version
if %errorlevel% neq 0 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python 3.8+ surumunu yükleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo Sanal ortam olusturuluyor...
python -m venv venv
if %errorlevel% neq 0 (
    echo HATA: Sanal ortam olusturulamadi!
    pause
    exit /b 1
)
echo.

echo Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat
echo.

echo Gerekli kutuphaneler yukleniyor...
echo (Bu islem birkaç dakika surebilir)
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo HATA: Kutuphaneler yuklenemedi!
    pause
    exit /b 1
)
echo.

echo ====================================
echo Kurulum tamamlandi!
echo ====================================
echo.
echo Uygulamayi calistirmak icin:
echo   1. venv\Scripts\activate.bat
echo   2. python main.py
echo.
echo veya dogrudan "run.bat" dosyasini calistirin.
echo.
pause
