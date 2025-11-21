"""
PyInstaller ile .exe derleme script'i
Windows için tek dosya çalıştırılabilir oluşturur
"""
import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """
    PyInstaller kullanarak .exe dosyası oluşturur
    """
    print("=" * 60)
    print("Elektrikli Araç Enerji Analiz Sistemi")
    print(".exe Derleme İşlemi")
    print("=" * 60)
    print()

    # PyInstaller kurulu mu kontrol et
    try:
        import PyInstaller
        print(f"✓ PyInstaller versiyonu: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller bulunamadı!")
        print("Kurulum için: pip install pyinstaller")
        return False

    # Ana dizin
    root_dir = Path(__file__).parent
    main_file = root_dir / "main.py"

    if not main_file.exists():
        print(f"❌ main.py dosyası bulunamadı: {main_file}")
        return False

    print(f"✓ Ana dosya: {main_file}")
    print()

    # PyInstaller komutu
    cmd = [
        "pyinstaller",
        "--name=EVEnergyAnalyzer",
        "--onefile",  # Tek dosya
        "--windowed",  # Konsol penceresi gösterme
        "--clean",  # Önceki build'i temizle

        # İkonlar (varsa)
        # "--icon=assets/icon.ico",

        # Ek veriler
        "--add-data=src;src",

        # Gizli importlar
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=matplotlib",
        "--hidden-import=openpyxl",
        "--hidden-import=reportlab",
        "--hidden-import=tkinter",

        # Optimize et
        "--optimize=2",

        # Ana dosya
        str(main_file)
    ]

    print("PyInstaller komutu:")
    print(" ".join(cmd))
    print()
    print("Derleme başlıyor... (Bu işlem birkaç dakika sürebilir)")
    print()

    try:
        # PyInstaller çalıştır
        result = subprocess.run(cmd, cwd=root_dir, check=True)

        print()
        print("=" * 60)
        print("✅ Derleme başarılı!")
        print("=" * 60)
        print()

        exe_path = root_dir / "dist" / "EVEnergyAnalyzer.exe"

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ .exe dosyası oluşturuldu:")
            print(f"  Yol: {exe_path}")
            print(f"  Boyut: {size_mb:.1f} MB")
            print()
            print("Uygulamayı çalıştırmak için:")
            print(f"  {exe_path}")
        else:
            print("⚠ .exe dosyası oluşturuldu ama konumu belirsiz")
            print("dist/ klasörünü kontrol edin")

        return True

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("❌ Derleme başarısız!")
        print("=" * 60)
        print(f"Hata: {e}")
        return False

def clean_build():
    """
    Build dosyalarını temizler
    """
    import shutil

    root_dir = Path(__file__).parent

    # Temizlenecek klasörler
    clean_dirs = ['build', 'dist', '__pycache__']
    clean_files = ['*.spec']

    print("Eski build dosyaları temizleniyor...")

    for dir_name in clean_dirs:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ {dir_name}/ silindi")

    # .spec dosyalarını sil
    for spec_file in root_dir.glob("*.spec"):
        spec_file.unlink()
        print(f"  ✓ {spec_file.name} silindi")

    print("✓ Temizlik tamamlandı")
    print()

def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="EV Energy Analyzer .exe Builder")
    parser.add_argument("--clean", action="store_true", help="Build dosyalarını temizle")

    args = parser.parse_args()

    if args.clean:
        clean_build()
    else:
        success = build_exe()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
