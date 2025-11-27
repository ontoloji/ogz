@echo off
echo ================================================
echo Hava Durumu Loglama Servisi - Kaldirma
echo ================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo HATA: Bu script yonetici yetkisi gerektirir!
    echo Lutfen sag tikla - Yonetici olarak calistir
    pause
    exit /b 1
)

echo [1/3] Servis durduruluyor...
sc stop "WeatherLoggingService" >nul 2>&1
timeout /t 3 /nobreak >nul

echo [2/3] Servis kaldiriliyor...
sc delete "WeatherLoggingService" >nul 2>&1

echo [3/3] Dosyalar siliniyor...
set "INSTALL_DIR=%ProgramFiles%\WeatherLoggingService"
if exist "%INSTALL_DIR%" (
    rmdir /S /Q "%INSTALL_DIR%"
)

echo.
echo ================================================
echo Kaldirma tamamlandi!
echo ================================================
echo.
echo NOT: Log dosyalari korundu (C:\WeatherLogs)
echo Silmek isterseniz: rmdir /S /Q C:\WeatherLogs
echo.
pause
