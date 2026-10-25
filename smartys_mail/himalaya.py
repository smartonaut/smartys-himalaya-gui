# -*- coding: utf-8 -*-
"""Aufruf von himalaya.

Die gesamte Anmeldung — Passwoerter, App-Passwoerter, OAuth2, Token —
erledigt himalaya anhand seiner eigenen Konfiguration. Dieses Modul ruft es
nur auf und reicht Ergebnisse weiter. Es sieht und speichert keine
Zugangsdaten.
"""
import json
import os
import subprocess

# Ueberschreibbar, falls himalaya woanders liegt
HIMALAYA = os.environ.get("SMARTYS_MAIL_HIMALAYA") or os.path.expanduser("~/.local/bin/himalaya")
if not os.path.exists(HIMALAYA):
    HIMALAYA = "himalaya"

_TIMEOUT = 120


def json_aufruf(args, timeout=_TIMEOUT, stdin=None):
    """himalaya mit --json aufrufen und die Antwort als dict zurueckgeben.

    Bei Fehlern kommt {"error": "..."} zurueck — nie eine Ausnahme, damit
    die Oberflaeche immer etwas anzeigen kann.
    """
    try:
        p = subprocess.run([HIMALAYA, "--json"] + list(args),
                           capture_output=True, text=True,
                           timeout=timeout, input=stdin)
        if p.returncode != 0:
            return {"error": (p.stderr or p.stdout or "").strip()[:400]}
        return json.loads(p.stdout or "{}")
    except subprocess.TimeoutExpired:
        return {"error": "Zeitueberschreitung"}
    except json.JSONDecodeError:
        return {"error": "Antwort war kein JSON"}
    except Exception as e:  # noqa: BLE001 — Fehler sollen die UI erreichen
        return {"error": str(e)}


def roh_aufruf(args, timeout=_TIMEOUT, stdin=None):
    """himalaya ohne --json: fuer MIME, Rohmails und Menschenausgaben."""
    try:
        p = subprocess.run([HIMALAYA] + list(args),
                           capture_output=True, text=True,
                           timeout=timeout, input=stdin)
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 1, "", "Zeitueberschreitung"
    except Exception as e:  # noqa: BLE001
        return 1, "", str(e)


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
