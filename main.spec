# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Fran\\Desktop\\Fran\\Programacion\\Universidad\\10mo semestre\\Tesis\\dev\\InstrumentClassifier\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Fran\\Desktop\\Fran\\Programacion\\Universidad\\10mo semestre\\Tesis\\dev\\InstrumentClassifier\\src\\gui\\btn_icons', 'btn_icons/'), ('C:\\Users\\Fran\\Desktop\\Fran\\Programacion\\Universidad\\10mo semestre\\Tesis\\dev\\InstrumentClassifier\\src\\gui\\img', 'img/'), ('C:\\Users\\Fran\\Desktop\\Fran\\Programacion\\Universidad\\10mo semestre\\Tesis\\dev\\InstrumentClassifier\\models', 'models/'), ('C:\\Users\\Fran\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\customtkinter', 'customtkinter/'), ('C:\\Users\\Fran\\Desktop\\Fran\\Programacion\\Universidad\\10mo semestre\\Tesis\\dev\\InstrumentClassifier\\guitar_28109.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow', 'cryptography', 'PyQt5', 'pygame', 'matplotlib', 'pandas','h5py','google','coverage','jedi'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Fran\\Downloads\\guitar_28109.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
