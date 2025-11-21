"""
Elektrikli Araç Enerji Tüketimi Analiz Sistemi
Ana başlatma dosyası
"""
import sys
from pathlib import Path

# Proje dizinini path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# GUI'yi başlat
if __name__ == "__main__":
    from gui.main_window import main
    main()
