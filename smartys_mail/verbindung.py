# -*- coding: utf-8 -*-
"""Welcher himalaya wird benutzt — lokal oder auf einem anderen Rechner.

Nicht jeder hat seine Postfaecher auf demselben Rechner wie die Oberflaeche.
Zwei Betriebsarten:

* **lokal** — himalaya liegt auf diesem Rechner und kennt die Konten.
* **ssh**   — himalaya laeuft auf einem anderen Rechner (etwa dem Heimserver);
  die Oberflaeche ruft es dort ueber SSH auf. Das ist der empfohlene Weg fuer
  mehrere Geraete: Zugangsdaten bleiben an EINER Stelle, der Client braucht
  nur einen SSH-Schluessel.

Die Einstellung liegt neben den Benutzerdaten, nicht im Programmverzeichnis.
"""
import json
import os

from . import pfade

STANDARD = {
    "modus": "lokal",          # "lokal" oder "ssh"
    "ssh_ziel": "",            # z.B. benutzer@192.168.1.50
    "himalaya_pfad": "himalaya",  # Pfad auf dem entfernten Rechner
    # Externe Bilder in HTML-Mails laden? Standard: nein. Ein Zaehlpixel
    # verraet dem Absender sofort, dass und wann die Mail gelesen wurde.
    "bilder_laden": False,

    # Uebersetzer. "" = aus, "ollama" = lokales Sprachmodell,
    # "libretranslate" = Dienst mit LibreTranslate-Schnittstelle.
    "uebersetzer": "",
    "uebersetzer_url": "",
    "uebersetzer_modell": "",
    "uebersetzer_ziel": "Deutsch",
}


def _datei():
    return os.path.join(pfade.einstellordner(), "verbindung.json")


def _alte_datei():
    """Frueher lag die Einstellung im Cache-Ordner — dort wird sie irgendwann
    geloescht. Zum Umzug einmal nachsehen."""
    return os.path.join(pfade.datenordner(), "verbindung.json")


def laden():
    """Einstellung lesen; bei fehlender oder kaputter Datei die Standardwerte."""
    daten = dict(STANDARD)
    # Liegt die Einstellung noch am alten Ort (Cache), einmal herueberholen.
    if not os.path.exists(_datei()):
        umziehen()
    try:
        with open(_datei(), encoding="utf-8") as f:
            gespeichert = json.load(f)
        if isinstance(gespeichert, dict):
            for schluessel in STANDARD:
                if schluessel in gespeichert:
                    daten[schluessel] = gespeichert[schluessel] or STANDARD[schluessel]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    # Umgebungsvariable schlaegt die Datei (fuer Tests und Dienst-Betrieb)
    env_ssh = os.environ.get("SMARTYS_MAIL_SSH")
    if env_ssh:
        daten["modus"] = "ssh"
        daten["ssh_ziel"] = env_ssh
    env_pfad = os.environ.get("SMARTYS_MAIL_SSH_HIMALAYA")
    if env_pfad:
        daten["himalaya_pfad"] = env_pfad
    return daten


def umziehen():
    """Einstellung aus dem alten Cache-Ort uebernehmen, falls vorhanden."""
    alt = _alte_datei()
    if not os.path.exists(alt) or os.path.exists(_datei()):
        return False
    try:
        with open(alt, encoding="utf-8") as f:
            daten = json.load(f)
        if isinstance(daten, dict) and daten.get("modus"):
            os.makedirs(os.path.dirname(_datei()), exist_ok=True)
            with open(_datei(), "w", encoding="utf-8") as f:
                json.dump(daten, f, indent=2, ensure_ascii=False)
            return True
    except (OSError, json.JSONDecodeError):
        pass
    return False


def speichern(daten):
    """Einstellung ablegen. Gibt eine Fehlermeldung zurueck oder None."""
    modus = (daten.get("modus") or "lokal").strip()
    if modus not in ("lokal", "ssh"):
        return "Unbekannter Modus"
    ziel = (daten.get("ssh_ziel") or "").strip()
    if modus == "ssh" and not ziel:
        return "Ohne Rechnerangabe (z.B. benutzer@192.168.1.50) kein SSH-Betrieb"
    pfad = (daten.get("himalaya_pfad") or "himalaya").strip() or "himalaya"
    dienst = (daten.get("uebersetzer") or "").strip()
    if dienst not in ("", "ollama", "libretranslate"):
        return "Unbekannter Uebersetzer-Dienst"
    neu = {"modus": modus, "ssh_ziel": ziel, "himalaya_pfad": pfad,
           "bilder_laden": bool(daten.get("bilder_laden")),
           "uebersetzer": dienst,
           "uebersetzer_url": (daten.get("uebersetzer_url") or "").strip(),
           "uebersetzer_modell": (daten.get("uebersetzer_modell") or "").strip(),
           "uebersetzer_ziel": (daten.get("uebersetzer_ziel") or "Deutsch").strip()}
    try:
        os.makedirs(os.path.dirname(_datei()), exist_ok=True)
        with open(_datei(), "w", encoding="utf-8") as f:
            json.dump(neu, f, indent=2, ensure_ascii=False)
    except OSError as e:
        return f"Speichern fehlgeschlagen: {e}"
    return None
