# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Resume AI
Build command: pyinstaller resume-ai.spec
"""

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core', 'core'),
        ('gui', 'gui'),
        ('samples', 'samples'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'requests',
        'fitz',
        'pdfplumber',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ResumeAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resume-ai.ico',
)
