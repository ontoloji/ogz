# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File
CAN Bus Analyzer - Windows
"""

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),  # Resources klasörünü dahil et
    ],
    hiddenimports=[
        # python-can interfaces
        'can.interfaces.kvaser',
        'can.interfaces.socketcan',
        'can.interfaces.pcan',
        'can.interfaces.vector',
        'can.interfaces',
        # PyQt5
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        # Diğer
        'pyqtgraph',
        'pandas',
        'numpy',
        'openpyxl',
        'xlsxwriter',
        'cantools',
        'matplotlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CANBusAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI uygulama, console gösterme
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='resources/icons/app_icon.ico',  # İkon dosyası varsa yolu belirt
)
