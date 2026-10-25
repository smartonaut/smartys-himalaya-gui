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
    "ssh_ziel": "",            # z.B. smarty@192.168.1.238
    "himalaya_pfad": "himalaya",  # Pfad auf dem entfernten Rechner
}


def _datei():
    return os.path.join(pfade.datenordner(), "verbindung.json")


def laden():
    """Einstellung lesen; bei fehlender oder kaputter Datei die Standardwerte."""
    daten = dict(STANDARD)
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


def speichern(daten):
    """Einstellung ablegen. Gibt eine Fehlermeldung zurueck oder None."""
    modus = (daten.get("modus") or "lokal").strip()
    if modus not in ("lokal", "ssh"):
        return "Unbekannter Modus"
    ziel = (daten.get("ssh_ziel") or "").strip()
    if modus == "ssh" and not ziel:
        return "Ohne Rechnerangabe (z.B. smarty@192.168.1.238) kein SSH-Betrieb"
    pfad = (daten.get("himalaya_pfad") or "himalaya").strip() or "himalaya"
    neu = {"modus": modus, "ssh_ziel": ziel, "himalaya_pfad": pfad}
    try:
        os.makedirs(os.path.dirname(_datei()), exist_ok=True)
        with open(_datei(), "w", encoding="utf-8") as f:
            json.dump(neu, f, indent=2, ensure_ascii=False)
    except OSError as e:
        return f"Speichern fehlgeschlagen: {e}"
    return None
