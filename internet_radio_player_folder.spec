# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Internet Radio Player (Folder Distribution)
Klasör tabanlı dağıtım - daha hızlı başlatma
"""

block_cipher = None

a = Analysis(
    ['internet_radio_player.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('radio_favorites_example.json', '.'),
        ('RADIO_README.md', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'vlc',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='InternetRadyoCalar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI uygulaması
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='radio_icon.ico' if os.path.exists('radio_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='InternetRadyoCalar',
)
