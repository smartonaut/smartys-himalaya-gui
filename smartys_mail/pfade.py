# -*- coding: utf-8 -*-
"""Pfade plattformunabhaengig bestimmen.

himalaya legt seine Konfiguration je Betriebssystem woanders ab. Statt die
Linux-Pfade fest zu verdrahten, fragen wir hier zentral danach — sonst
startet die Windows-Fassung und findet kein einziges Konto.
"""
import os
import shutil
import sys

WINDOWS = sys.platform.startswith("win")


def himalaya_config():
    """Pfad zur himalaya-Konfiguration."""
    eigene = os.environ.get("SMARTYS_MAIL_CONFIG")
    if eigene:
        return os.path.expanduser(eigene)
    if WINDOWS:
        basis = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
        return os.path.join(basis, "himalaya", "config.toml")
    # XDG respektieren, sonst ~/.config
    xdg = os.environ.get("XDG_CONFIG_HOME")
    basis = xdg if xdg else os.path.expanduser("~/.config")
    return os.path.join(basis, "himalaya", "config.toml")


def datenordner():
    """Ordner fuer Zwischendateien (Downloads, Signaturen)."""
    eigene = os.environ.get("SMARTYS_MAIL_DATEN")
    if eigene:
        ordner = os.path.expanduser(eigene)
    elif WINDOWS:
        basis = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        ordner = os.path.join(basis, "smartys-himalaya-gui")
    else:
        xdg = os.environ.get("XDG_CACHE_HOME")
        basis = xdg if xdg else os.path.expanduser("~/.cache")
        ordner = os.path.join(basis, "smartys-himalaya-gui")
    os.makedirs(ordner, exist_ok=True)
    return ordner


def himalaya_binary():
    """himalaya finden: Umgebungsvariable, PATH, dann uebliche Orte."""
    eigene = os.environ.get("SMARTYS_MAIL_HIMALAYA")
    if eigene and os.path.exists(os.path.expanduser(eigene)):
        return os.path.expanduser(eigene)

    name = "himalaya.exe" if WINDOWS else "himalaya"
    gefunden = shutil.which("himalaya")
    if gefunden:
        return gefunden

    kandidaten = []
    if WINDOWS:
        lokal = os.environ.get("LOCALAPPDATA") or ""
        kandidaten = [
            os.path.join(lokal, "Programs", "himalaya", name),
            os.path.join(os.path.expanduser("~"), ".cargo", "bin", name),
            os.path.join(os.path.expanduser("~"), "himalaya", name),
        ]
    else:
        kandidaten = [
            os.path.expanduser("~/.local/bin/himalaya"),
            "/usr/local/bin/himalaya",
            "/usr/bin/himalaya",
        ]
    for pfad in kandidaten:
        if pfad and os.path.exists(pfad):
            return pfad
    return "himalaya"
