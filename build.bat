@echo off
chcp 65001 >nul
title StreamScribe Build Script v2.1

echo.
echo ========================================
echo 🚀 StreamScribe Build Script v2.1
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    echo Lütfen Python'u yükleyin ve PATH'e ekleyin.
    echo.
    pause
    exit /b 1
)

:: Check if PyInstaller is available
echo 🔍 PyInstaller kontrol ediliyor...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller bulunamadı!
    echo Yükleniyor...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller yüklenemedi!
        pause
        exit /b 1
    )
)

:: Check if required packages are available
echo 🔍 Gerekli paketler kontrol ediliyor...
python -c "import yt_dlp, customtkinter, requests, PIL" >nul 2>&1
if errorlevel 1 (
    echo ❌ Bazı paketler eksik!
    echo Yükleniyor...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Paketler yüklenemedi!
        pause
        exit /b 1
    )
)

:: Clean previous build artifacts
echo.
echo 🧹 Önceki build dosyaları temizleniyor...
if exist build (
    echo   - build/ klasörü siliniyor...
    rmdir /s /q build 2>nul
)
if exist __pycache__ (
    echo   - __pycache__ klasörleri siliniyor...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
)

:: Check if Streamscribe.spec exists
if not exist "Streamscribe.spec" (
    echo ❌ Streamscribe.spec dosyası bulunamadı!
    pause
    exit /b 1
)

:: Check if logo folder exists
if not exist "logo\favicon.ico" (
    echo ⚠️  logo/favicon.ico bulunamadı!
    echo Icon olmadan build devam edecek...
)

:: Start build process
echo.
echo 🏗️  Build başlatılıyor...
echo    - Spec dosyası: Streamscribe.spec
echo    - Icon: logo/favicon.ico
echo    - Çıktı: dist/ klasörü
echo.

:: Run PyInstaller
echo 📦 PyInstaller çalıştırılıyor...
pyinstaller Streamscribe.spec

if errorlevel 1 (
    echo.
    echo ❌ Build başarısız!
    echo Hata detayları yukarıda görülebilir.
    echo.
    pause
    exit /b 1
)

:: Check if build was successful
if not exist "dist\Streamscribe_v2.1_Standalone.exe" (
    echo.
    echo ❌ Executable oluşturulamadı!
    echo Build süreci tamamlandı ama çıktı dosyası bulunamadı.
    echo.
    pause
    exit /b 1
)

:: Get file size
for %%A in ("dist\Streamscribe_v2.1_Standalone.exe") do set size=%%~zA
set /a size_mb=%size%/1048576

echo.
echo ✅ Build başarılı!
echo.
echo 📊 Build Sonuçları:
echo    - Executable: dist\Streamscribe_v2.1_Standalone.exe
echo    - Boyut: %size_mb% MB
echo    - Durum: Standalone (Python gerektirmez)
echo.

:: Test the executable
echo 🧪 Executable test ediliyor...
echo    - Versiyon kontrolü...
dist\Streamscribe_v2.1_Standalone.exe --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Executable test edilemedi (normal olabilir)
) else (
    echo ✅ Executable test başarılı!
)

:: Show final instructions
echo.
echo 🎉 Build tamamlandı!
echo.
echo 📁 Çıktı dosyaları:
echo    - dist\Streamscribe_v2.1_Standalone.exe (Ana uygulama)
echo    - dist\ klasörü (Tüm gerekli dosyalar)
echo.
echo 💡 Kullanım:
echo    1. dist\ klasörünü USB'ye kopyalayın
echo    2. Başka bilgisayarlarda çalıştırın
echo    3. Python kurulumu gerekmez
echo.
echo 🗑️  Temizlik:
echo    - build/ klasörü silinebilir
echo    - __pycache__ klasörleri silinebilir
echo    - dist/ klasörü korunmalı
echo.

:: Automatically clean build artifacts
echo.
echo 🧹 Build dosyaları otomatik temizleniyor...
if exist build rmdir /s /q build 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
echo ✅ Temizlik tamamlandı!

echo.
echo 🎬 StreamScribe v2.1 build işlemi tamamlandı!
echo.
pause