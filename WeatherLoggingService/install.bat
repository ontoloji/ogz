@echo off
echo ================================================
echo Hava Durumu Loglama Servisi - Kurulum
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

echo [1/5] Servis durumu kontrol ediliyor...
sc query "WeatherLoggingService" >nul 2>&1
if %errorLevel% equ 0 (
    echo Servis zaten yuklu. Once kaldiriliyor...
    sc stop "WeatherLoggingService" >nul 2>&1
    timeout /t 2 /nobreak >nul
    sc delete "WeatherLoggingService" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo [2/5] Kurulum dizini hazirlaniyor...
set "INSTALL_DIR=%ProgramFiles%\WeatherLoggingService"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [3/5] Dosyalar kopyalaniyor...
xcopy /E /I /Y "%~dp0bin\Release\net8.0-windows\win-x64\publish\*" "%INSTALL_DIR%\" >nul

if not exist "%INSTALL_DIR%\WeatherLoggingService.exe" (
    echo HATA: Dosyalar bulunamadi! Once projeyi derleyin:
    echo        dotnet publish -c Release -r win-x64 --self-contained true
    pause
    exit /b 1
)

echo [4/5] Windows servisi olusturuluyor...
sc create "WeatherLoggingService" binpath= "%INSTALL_DIR%\WeatherLoggingService.exe" start= auto DisplayName= "Hava Durumu Loglama Servisi"
sc description "WeatherLoggingService" "Saatlik hava durumu verilerini otomatik olarak toplar ve kaydeder."

echo [5/5] Servis baslatiliyor...
sc start "WeatherLoggingService"

echo.
echo ================================================
echo Kurulum tamamlandi!
echo ================================================
echo.
echo Servis konumu: %INSTALL_DIR%
echo Yapilandirma: %INSTALL_DIR%\appsettings.json
echo.
echo ONEMLI: appsettings.json dosyasini duzenleyip API anahtarinizi girin!
echo.
echo Servis durumunu gormek icin:
echo   services.msc
echo.
pause
