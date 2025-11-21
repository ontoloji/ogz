# -*- mode: python ; coding: utf-8 -*-
# CAN Bus Analyzer - PyInstaller Spec Dosyası
# Manuel build için: pyinstaller can_analyzer.spec

import sys
import os

block_cipher = None

# Ana dizin
main_dir = os.path.abspath('.')
src_dir = os.path.join(main_dir, 'src')

# Analiz
a = Analysis(
    [os.path.join(src_dir, 'can_analyzer_gui.py')],
    pathex=[src_dir],
    binaries=[],
    datas=[
        (os.path.join(main_dir, 'resources'), 'resources'),
    ],
    hiddenimports=[
        'can',
        'can.interfaces',
        'can.interfaces.kvaser',
        'can.interfaces.vector',
        'can.interfaces.socketcan',
        'cantools',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'pandas',
        'openpyxl',
        'numpy',
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

# PYZ (Python ZIP archive)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CAN_Bus_Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI modu (console gizli)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(main_dir, 'resources', 'icon.ico') if os.path.exists(os.path.join(main_dir, 'resources', 'icon.ico')) else None,
)
