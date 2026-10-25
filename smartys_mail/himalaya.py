# -*- coding: utf-8 -*-
"""Aufruf von himalaya.

Die gesamte Anmeldung — Passwoerter, App-Passwoerter, OAuth2, Token —
erledigt himalaya anhand seiner eigenen Konfiguration. Dieses Modul ruft es
nur auf und reicht Ergebnisse weiter. Es sieht und speichert keine
Zugangsdaten.

himalaya muss nicht auf diesem Rechner laufen: Ist in den Einstellungen ein
entfernter Rechner hinterlegt, gehen die Aufrufe per SSH dorthin. Dann bleiben
die Konten und Zugangsdaten an einer Stelle, und der Client braucht nur einen
SSH-Schluessel.
"""
import json
import os
import shlex
import subprocess

from . import pfade, verbindung

_TIMEOUT = 120

# SSH-Fehler sind fuer Endnutzer nicht selbsterklaerend. Uebersetzen, statt
# den rohen stderr durchzureichen.
_FEHLER_DE = {
    "Host key verification failed": "Der SSH-Schluessel des Rechners hat sich "
        "geaendert. Verbindung pruefen, bevor es weitergeht.",
    "Permission denied": "SSH-Anmeldung abgelehnt. Liegt der oeffentliche "
        "Schluessel auf dem Zielrechner?",
    "Connection refused": "Der Zielrechner nimmt keine SSH-Verbindung an. "
        "Laeuft dort ein SSH-Server?",
    "No route to host": "Der Zielrechner ist nicht erreichbar.",
    "Could not resolve hostname": "Der Rechnername ist unbekannt.",
    "Connection timed out": "Zeitueberschreitung beim Verbindungsaufbau.",
}


# OpenSSH schreibt bei jedem Aufruf Hinweise zur Schluesselaushandlung auf
# stderr, auch wenn der Befehl erfolgreich ist. Ohne Filter sieht jeder
# Fehlerfall so aus, als waere die Verbindung kaputt.
_SSH_RAUSCHEN = (
    "post-quantum", "store now", "may need to be upgraded",
    "vulnerable", "WARNING: connection", "** WARNING",
)


def _ohne_ssh_rauschen(text):
    """Nur echte Fehlerzeilen behalten."""
    zeilen = [z for z in (text or "").splitlines()
              if z.strip() and not any(m in z for m in _SSH_RAUSCHEN)]
    return "\n".join(zeilen).strip()


def _lesbar(text):
    """Bekannte Fehler in verstaendliche Saetze uebersetzen."""
    for muster, satz in _FEHLER_DE.items():
        if muster.lower() in (text or "").lower():
            return satz
    return text


def befehlszeile(args, mit_json=False):
    """Die komplette argv-Liste fuer den Aufruf bauen.

    Lokal: [himalaya, --json, ...]
    Per SSH: [ssh, ziel, "himalaya --json ..."] — auf der Gegenseite wird eine
    Shell benutzt, deshalb muss jeder Teil einzeln gequotet werden.
    """
    einstellung = verbindung.laden()
    teile = []
    if mit_json:
        teile.append("--json")
    teile += [str(a) for a in args]

    if einstellung["modus"] == "ssh":
        programm = (einstellung["himalaya_pfad"] or "himalaya").strip()
        # Nicht-interaktive SSH-Sitzungen lesen .profile/.bashrc nicht, dort ist
        # himalaya also oft NICHT im PATH — auch wenn es im Terminal klappt.
        # Deshalb die ueblichen Installationsorte der Reihe nach probieren,
        # statt den Nutzer nach einem Pfad zu fragen, den er nicht kennt.
        if programm in ("himalaya", "", "./himalaya"):
            suche = ("command -v himalaya 2>/dev/null"
                     " || ls ~/.local/bin/himalaya 2>/dev/null"
                     " || ls ~/.cargo/bin/himalaya 2>/dev/null"
                     " || ls /usr/local/bin/himalaya 2>/dev/null"
                     " || echo himalaya")
            # Geschweifte Klammern: sonst bindet die Pipe nur an das letzte
            # Kommando der Kette.
            programm = f'"$( {{ {suche}; }} | head -n1 )"'
        fernbefehl = " ".join([programm] + [shlex.quote(t) for t in teile])
        # accept-new: beim ersten Verbinden wird der Schluessel gespeichert,
        # ein SPAETER geaenderter Schluessel wird weiterhin abgelehnt. Ohne
        # diese Option scheitert der erste Aufruf auf jedem frischen Rechner
        # mit "Host key verification failed" und niemand weiss warum.
        return ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                "-o", "StrictHostKeyChecking=accept-new",
                einstellung["ssh_ziel"], fernbefehl]
    return [pfade.himalaya_binary()] + teile


def json_aufruf(args, timeout=_TIMEOUT, stdin=None):
    """himalaya mit --json aufrufen und die Antwort als dict zurueckgeben.

    Bei Fehlern kommt {"error": "..."} zurueck — nie eine Ausnahme, damit
    die Oberflaeche immer etwas anzeigen kann.
    """
    try:
        p = subprocess.run(befehlszeile(args, mit_json=True),
                           capture_output=True, text=True,
                           timeout=timeout, input=stdin)
        if p.returncode != 0:
            meldung = _ohne_ssh_rauschen(p.stderr or "") or _ohne_ssh_rauschen(p.stdout or "")
            return {"error": _lesbar(meldung[:400] or "himalaya ist fehlgeschlagen")}
        return json.loads(p.stdout or "{}")
    except subprocess.TimeoutExpired:
        return {"error": "Zeitueberschreitung — antwortet der entfernte Rechner?"}
    except json.JSONDecodeError:
        return {"error": "Antwort war kein JSON"}
    except Exception as e:  # noqa: BLE001 — Fehler sollen die UI erreichen
        return {"error": str(e)}


def roh_aufruf(args, timeout=_TIMEOUT, stdin=None):
    """himalaya ohne --json: fuer MIME, Rohmails und Menschenausgaben."""
    try:
        p = subprocess.run(befehlszeile(args),
                           capture_output=True, text=True,
                           timeout=timeout, input=stdin)
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 1, "", "Zeitueberschreitung"
    except Exception as e:  # noqa: BLE001
        return 1, "", str(e)


def datei_holen(fernpfad, timeout=_TIMEOUT):
    """Eine Datei vom himalaya-Rechner lesen — roh, ohne Textumwandlung.

    Wird fuer Anhaenge gebraucht: im SSH-Betrieb liegt die heruntergeladene
    Datei auf dem anderen Rechner, nicht hier.
    """
    einstellung = verbindung.laden()
    if einstellung["modus"] != "ssh":
        try:
            with open(fernpfad, "rb") as f:
                return f.read(), ""
        except OSError as e:
            return None, str(e)
    try:
        p = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                            einstellung["ssh_ziel"], f"cat {shlex.quote(fernpfad)}"],
                           capture_output=True, timeout=timeout)
        if p.returncode != 0:
            return None, (p.stderr or b"").decode("utf-8", "replace")[:300]
        return p.stdout, ""
    except subprocess.TimeoutExpired:
        return None, "Zeitueberschreitung"
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def entferntes_temporaer():
    """Ein temporaeres Verzeichnis auf der himalaya-Seite.

    Im SSH-Betrieb muss himalaya die Anhaenge dort ablegen, wo sie entstehen;
    der Pfad wird nach dem Holen wieder aufgeraeumt.
    """
    if verbindung.laden()["modus"] != "ssh":
        ordner = os.path.join(pfade.datenordner(), "downloads")
        os.makedirs(ordner, exist_ok=True)
        return ordner
    return "/tmp"


def ordner_varianten(name):
    """Schreibweisen des Eingangsordners durchprobieren.

    Provider benennen ihn 'Inbox', 'INBOX' oder 'Posteingang'; himalaya
    vergleicht exakt und antwortet sonst mit 'mailbox not found'.
    """
    varianten = [name]
    for kandidat in ("Inbox", "INBOX", "Posteingang"):
        if kandidat.lower() != (name or "").lower():
            varianten.append(kandidat)
    return varianten


def gesendet_ordner(konto):
    """Namen des Gesendet-Ordners ermitteln (darf None sein).

    Wird vor dem Senden gebraucht: himalaya stellt zuerst zu und speichert
    danach. Ein zweiter Versuch nach einem Speicherfehler wuerde die Mail
    doppelt zustellen.
    """
    antwort = json_aufruf(["mailbox", "list", "-a", konto], timeout=60)
    namen = [m.get("name", "") for m in (antwort.get("mailboxes") or [])]
    for kandidat in ("Sent", "Sent Items", "Gesendet", "Sent Messages",
                     "Gesendet Items", "Gesendet Nachrichten", "Gesendete Objekte"):
        if kandidat in namen:
            return kandidat
    return None
