# -*- coding: utf-8 -*-
"""Signaturen je Kontogruppe.

Eine Signatur gilt fuer alle Konten einer Gruppe. Die Gruppe ergibt sich aus
dem Teil vor dem ersten Bindestrich: 'firma-buchhaltung' gehoert zu 'firma'.
Damit pflegt man eine Signatur fuer neun Postfaecher, nicht neun einzeln.

Aufbau der Datei:
    {
      "gruppen":   {"firma": "<p>...</p>"},
      "ausnahmen": {"firma-chef": "<p>abweichend</p>"}
    }
"""
import json
import os

STANDARD_PFAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "signaturen.json")


def pfad():
    return os.environ.get("SMARTYS_MAIL_SIG") or STANDARD_PFAD


def gruppe_von(konto):
    """'firma-buchhaltung' -> 'firma'."""
    return konto.split("-")[0] if "-" in konto else konto


def laden():
    """Signaturdatei lesen; alte Fassung (je Konto) automatisch umziehen."""
    ziel = pfad()
    if not os.path.exists(ziel):
        return {"gruppen": {}, "ausnahmen": {}}
    try:
        daten = json.load(open(ziel, encoding="utf-8"))
    except Exception:  # noqa: BLE001 — kaputte Datei darf den Start nicht verhindern
        return {"gruppen": {}, "ausnahmen": {}}

    if "gruppen" in daten:
        daten.setdefault("ausnahmen", {})
        return daten

    # Fruehere Fassung: Signatur je Konto. Auf Gruppen umziehen, damit
    # bestehende Installationen weiterlaufen.
    gruppen, ausnahmen = {}, {}
    for konto, html in daten.items():
        if not isinstance(html, str) or not html.strip():
            continue
        gruppe = gruppe_von(konto)
        if gruppe not in gruppen:
            gruppen[gruppe] = html
        elif gruppen[gruppe] != html:
            ausnahmen[konto] = html
    neu = {"gruppen": gruppen, "ausnahmen": ausnahmen}
    speichern(neu)
    return neu


def speichern(daten):
    ziel = pfad()
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    with open(ziel, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)


def fuer_konto(konto, daten=None):
    """Signatur eines Kontos: Konto-Ausnahme schlaegt Gruppensignatur."""
    if daten is None:
        daten = laden()
    ausnahme = (daten.get("ausnahmen") or {}).get(konto)
    if ausnahme:
        return ausnahme
    return (daten.get("gruppen") or {}).get(gruppe_von(konto)) or ""


def setzen(gruppe, html):
    daten = laden()
    gruppen = daten.get("gruppen") or {}
    if (html or "").strip():
        gruppen[gruppe] = html
    else:
        gruppen.pop(gruppe, None)
    daten["gruppen"] = gruppen
    speichern(daten)
    return daten
