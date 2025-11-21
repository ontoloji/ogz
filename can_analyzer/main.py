"""
CAN Bus Analyzer - Ana Giriş Noktası
Windows CAN Bus Veri Analiz Aracı
"""
import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Windows'ta yüksek DPI desteği
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from gui.main_window import MainWindow


def setup_logging():
    """
    Logging yapılandırmasını kur.
    Windows log dosyası: %USERPROFILE%\\Documents\\CANAnalyzer\\logs
    """
    # Log dizinini oluştur
    log_dir = Path.home() / "Documents" / "CANAnalyzer" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"can_analyzer_{Path(__file__).stem}.log"

    # Logging yapılandırması
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("CAN Bus Analyzer başlatıldı")
    logger.info(f"Log dosyası: {log_file}")
    logger.info("=" * 60)

    return logger


def main():
    """
    Ana uygulama fonksiyonu.
    """
    # Logging kur
    logger = setup_logging()

    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        app.setApplicationName("CAN Bus Analyzer")
        app.setOrganizationName("CAN Tools")
        app.setOrganizationDomain("cantools.com")

        # Stil ayarla (Windows modern görünüm)
        app.setStyle("Fusion")

        # Ana pencereyi oluştur ve göster
        window = MainWindow()
        window.show()

        logger.info("Ana pencere gösteriliyor")

        # Uygulama döngüsünü başlat
        exit_code = app.exec_()

        logger.info(f"Uygulama sonlandı (Exit code: {exit_code})")
        return exit_code

    except Exception as e:
        logger.critical(f"Kritik hata: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
