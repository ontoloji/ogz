#!/bin/bash
# Wealth Tracker Launcher for macOS/Linux

echo "==================================="
echo "  Wealth Tracker Başlatılıyor..."
echo "==================================="
echo ""

# Python kontrolü
if ! command -v python3 &> /dev/null
then
    echo "HATA: Python3 bulunamadı!"
    echo "Lütfen Python'u yükleyin: https://www.python.org/downloads/"
    exit 1
fi

# Gerekli kütüphaneleri yükle
echo "Gerekli kütüphaneler kontrol ediliyor..."
pip3 install -r requirements.txt > /dev/null 2>&1

# Uygulamayı başlat
echo ""
echo "Uygulama başlatılıyor..."
echo ""
python3 main.py
