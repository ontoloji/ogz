# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec dosyası - Meeting Translator için dizin versiyonu
Bu versiyon daha hızlı başlar ve daha küçük olur (çoklu dosya)
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
    ],
    hiddenimports=[
        'whisper',
        'torch',
        'torchaudio',
        'torchvision',
        'sounddevice',
        'numpy',
        'deep_translator',
        'tkinter',
        'scipy',
        'scipy.signal',
        'scipy.fft',
        '_sounddevice_data',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
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
    exclude_binaries=True,  # Dizin versiyonu için
    name='MeetingTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MeetingTranslator',
)
