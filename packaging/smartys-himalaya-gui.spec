# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-Vorlage fuer die Windows-Fassung.

Baut eine einzelne .exe, die ohne Python-Installation laeuft. Die
Web-Dateien muessen mit hinein, sonst startet das Programm ohne Oberflaeche.

Wichtig: PyInstaller loest relative Pfade gegen das Verzeichnis dieser Datei
auf (packaging/), nicht gegen den Projektordner. Deshalb rechnet SPECPATH
eine Ebene hoch — sonst sucht der Build smartys_mail/ unter packaging/.
"""
import os

PROJEKT = os.path.abspath(os.path.join(SPECPATH, ".."))  # noqa: F821
WEB = os.path.join(PROJEKT, "smartys_mail", "web")
ICONS = os.path.join(PROJEKT, "assets", "icons")

a = Analysis(
    [os.path.join(PROJEKT, "packaging", "einstieg.py")],
    pathex=[PROJEKT],
    binaries=[],
    datas=[
        (WEB, "smartys_mail/web"),
        (os.path.join(ICONS, "logo_256.png"), "assets/icons"),
        (os.path.join(ICONS, "smartys-himalaya-gui.ico"), "assets/icons"),
    ],
    hiddenimports=["smartys_mail.desktop"],
    hookspath=[],
    runtime_hooks=[],
    # Pillow und numpy werden nirgends gebraucht; ohne den Ausschluss
    # waechst die .exe unnoetig.
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
