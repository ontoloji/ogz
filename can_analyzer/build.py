"""
PyInstaller Build Script
Windows için .exe oluşturma scripti
"""
import os
import sys
import shutil
from pathlib import Path
import subprocess


def clean_build_dirs():
    """
    Önceki build dosyalarını temizle.
    """
    print("Önceki build dosyaları temizleniyor...")

    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ {dir_name}/ temizlendi")

    # .spec dosyası varsa sil
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"  ✓ {spec_file.name} silindi")


def create_icon():
    """
    Varsayılan ikon dosyası oluştur (opsiyonel).
    Windows .ico formatı gerekir.
    """
    icon_path = Path("resources/icons/app_icon.ico")

    if not icon_path.exists():
        print("  ⚠ İkon dosyası bulunamadı, varsayılan kullanılacak")
        return None

    return str(icon_path)


def build_exe():
    """
    PyInstaller ile .exe dosyası oluştur.
    """
    print("\nPyInstaller ile .exe oluşturuluyor...")

    # PyInstaller komut parametreleri
    cmd = [
        'pyinstaller',
        '--name=CANBusAnalyzer',  # Uygulama adı
        '--onefile',  # Tek .exe dosyası
        '--windowed',  # Console penceresi gösterme (GUI için)
        '--clean',  # Önbelleği temizle
        # Data dosyaları ekle
        '--add-data=resources;resources',
        # Hidden imports (python-can backend'leri)
        '--hidden-import=can.interfaces.kvaser',
        '--hidden-import=can.interfaces.socketcan',
        '--hidden-import=can.interfaces.pcan',
        '--hidden-import=can.interfaces.vector',
        '--hidden-import=can.interfaces',
        # PyQt5 imports
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        # Diğer
        '--hidden-import=pyqtgraph',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=xlsxwriter',
        '--hidden-import=cantools',
        # Ana script
        'main.py'
    ]

    # İkon varsa ekle
    icon_path = create_icon()
    if icon_path:
        cmd.insert(1, f'--icon={icon_path}')

    # Komutu çalıştır
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ Build başarılı!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Build hatası!")
        print(f"  Hata: {e.stderr}")
        return False


def copy_additional_files():
    """
    Dist klasörüne ek dosyaları kopyala.
    """
    print("\nEk dosyalar kopyalanıyor...")

    dist_path = Path('dist')
    if not dist_path.exists():
        print("  ✗ dist/ klasörü bulunamadı")
        return

    # README kopyala
    readme_src = Path('../README.md')
    if readme_src.exists():
        shutil.copy(readme_src, dist_path / 'README.md')
        print("  ✓ README.md kopyalandı")

    # Örnek DBC dosyası kopyala (varsa)
    examples_dir = dist_path / 'examples'
    examples_dir.mkdir(exist_ok=True)

    print("  ✓ Ek dosyalar hazır")


def create_installer_info():
    """
    Windows installer bilgi dosyası oluştur.
    """
    print("\nBuild bilgileri oluşturuluyor...")

    info_text = """
CAN Bus Analyzer - Windows Kurulum

Kurulum:
1. CANBusAnalyzer.exe dosyasını istediğiniz konuma kopyalayın
2. Kvaser CANlib SDK'yı yükleyin (https://www.kvaser.com/downloads/)
3. CANBusAnalyzer.exe'yi çalıştırın

Gereksinimler:
- Windows 10/11 (64-bit)
- Kvaser CANlib SDK (Kvaser cihazları için)
- CAN arayüzü (Kvaser, PCAN, Vector, vb.)

Kullanım:
1. CAN arayüzünü seçin ve bağlanın
2. DBC dosyası yükleyin (opsiyonel)
3. "Almaya Başla" butonuna tıklayın
4. Verileri görüntüleyin ve analiz edin
5. CSV/Excel formatında export edin

Destek:
- GitHub: https://github.com/ontoloji/ogz
- Log dosyaları: %USERPROFILE%\\Documents\\CANAnalyzer\\logs

Versiyon: 1.0.0
"""

    info_file = Path('dist') / 'KURULUM.txt'
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_text)

    print("  ✓ KURULUM.txt oluşturuldu")


def main():
    """
    Ana build fonksiyonu.
    """
    print("=" * 60)
    print("CAN Bus Analyzer - Windows Build Script")
    print("=" * 60)

    # Dizini değiştir (can_analyzer klasörüne)
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"\nÇalışma dizini: {Path.cwd()}")

    # 1. Temizlik
    clean_build_dirs()

    # 2. Build
    success = build_exe()

    if not success:
        print("\n✗ Build başarısız!")
        sys.exit(1)

    # 3. Ek dosyalar
    copy_additional_files()

    # 4. Kurulum bilgileri
    create_installer_info()

    # Sonuç
    print("\n" + "=" * 60)
    print("✓ Build tamamlandı!")
    print("=" * 60)
    print(f"\nÇıktı dosyaları: {Path('dist').absolute()}")
    print("\nÖnemli:")
    print("  1. Kullanıcıların Kvaser CANlib SDK yüklü olmalı")
    print("  2. .exe dosyası Windows 10/11'de test edilmeli")
    print("  3. Antivirüs programları .exe'yi engelleyebilir")
    print("\nDağıtım:")
    print("  - dist/CANBusAnalyzer.exe")
    print("  - dist/KURULUM.txt")
    print("  - dist/README.md")


if __name__ == "__main__":
    main()
