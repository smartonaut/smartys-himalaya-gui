# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-Vorlage fuer die Windows-Fassung.

Baut eine einzelne .exe, die ohne Python-Installation laeuft. Die
Web-Dateien muessen mit hinein, sonst startet das Programm ohne Oberflaeche.
"""
import os

HIER = os.path.abspath(".")
WEB = os.path.join(HIER, "smartys_mail", "web")
ICONS = os.path.join(HIER, "assets", "icons")

a = Analysis(
    ["smartys_mail/__main__.py"],
    pathex=[HIER],
    binaries=[],
    datas=[
        (WEB, "smartys_mail/web"),
        (os.path.join(ICONS, "logo_256.png"), "assets/icons"),
        (os.path.join(ICONS, "smartys-himalaya-gui.ico"), "assets/icons"),
    ],
    hiddenimports=["smartys_mail.desktop"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "PIL"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SmartysHimalayaGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # kein schwarzes Fenster
    disable_windowed_traceback=False,
    icon=os.path.join(ICONS, "smartys-himalaya-gui.ico"),
)
