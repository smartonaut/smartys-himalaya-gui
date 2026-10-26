# -*- coding: utf-8 -*-
"""Uebersetzung von Mailtexten.

Zwei Wege, beide ohne zusaetzliche Abhaengigkeiten (nur Standardbibliothek):

* **ollama**          — lokales Sprachmodell, z.B. auf dem Heimrechner.
                        Nichts verlaesst das Netz.
* **libretranslate**  — selbst betriebener oder oeffentlicher Uebersetzungs-
                        dienst mit LibreTranslate-Schnittstelle.

Welcher Weg benutzt wird, steht in den Einstellungen (verbindung.json).
Ist nichts eingerichtet, meldet uebersetzen() einen klaren Fehler, statt
still zu scheitern.
"""
import json
import urllib.error
import urllib.request

from . import verbindung

# Sprachkuerzel fuer LibreTranslate. Die Oberflaeche arbeitet mit den
# ausgeschriebenen Namen, weil die im Einstellungsdialog stehen.
KUERZEL = {
    "Deutsch": "de",
    "Englisch": "en",
    "Franzoesisch": "fr",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Polnisch": "pl",
    "Tuerkisch": "tr",
    "Türkisch": "tr",
    "Niederlaendisch": "nl",
    "Niederländisch": "nl",
}

# Sehr lange Mails sprengen jeden Dienst. Der Rest bleibt unuebersetzt, der
# Hinweis dazu steht im Rueckgabetext.
MAX_ZEICHEN = 12000


def _post_json(url, daten, timeout=90):
    """POST mit JSON, gibt das geparste Ergebnis zurueck."""
    anfrage = urllib.request.Request(
        url,
        data=json.dumps(daten).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json"},
    )
    with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
        roh = antwort.read().decode("utf-8", "replace")
    return json.loads(roh)


def _ollama(text, ziel, url, modell):
    # Klare Anweisung: nur die Uebersetzung, keine Erklaerung, keine
    # Anfuehrungszeichen, Gliederung erhalten.
    anweisung = (
        f"Uebersetze den folgenden Text nach {ziel}. "
        "Gib ausschliesslich die Uebersetzung aus, ohne Einleitung, ohne "
        "Anfuehrungszeichen und ohne Kommentar. Behalte Absaetze und "
        "Zeilenumbrueche bei. Wenn der Text bereits in der Zielsprache ist, "
        "gib ihn unveraendert zurueck.\n\n"
        f"Text:\n{text}"
    )
    daten = _post_json(
        url.rstrip("/") + "/api/generate",
        {"model": modell, "prompt": anweisung, "stream": False,
         "options": {"temperature": 0.1}},
    )
    ergebnis = (daten.get("response") or "").strip()
    if not ergebnis:
        raise ValueError("Das Modell hat nichts zurueckgegeben.")
    return ergebnis


def _libretranslate(text, ziel, url):
    kuerzel = KUERZEL.get(ziel)
    if not kuerzel:
        raise ValueError(f"Fuer '{ziel}' ist kein Sprachkuerzel hinterlegt.")
    daten = _post_json(
        url.rstrip("/") + "/translate",
        {"q": text, "source": "auto", "target": kuerzel, "format": "text"},
    )
    ergebnis = (daten.get("translatedText") or "").strip()
    if not ergebnis:
        raise ValueError("Der Dienst hat nichts zurueckgegeben.")
    return ergebnis


def einstellungen():
    """Aktuelle Uebersetzer-Einstellungen."""
    einst = verbindung.laden()
    return {
        "dienst": (einst.get("uebersetzer") or "").strip(),
        "url": (einst.get("uebersetzer_url") or "").strip(),
        "modell": (einst.get("uebersetzer_modell") or "").strip(),
        "ziel": (einst.get("uebersetzer_ziel") or "Deutsch").strip(),
    }


def bereit():
    """Ist ein Uebersetzer eingerichtet?"""
    e = einstellungen()
    return bool(e["dienst"] and e["url"])


def uebersetzen(text, ziel=None):
    """Uebersetzt text. Rueckgabe (ergebnis, fehler) — genau eines ist None."""
    text = (text or "").strip()
    if not text:
        return None, "Es ist kein Text zum Uebersetzen da."

    e = einstellungen()
    ziel = (ziel or e["ziel"] or "Deutsch").strip()
    dienst = e["dienst"]
    url = e["url"]

    if not dienst:
        return None, ("Es ist noch kein Uebersetzer eingerichtet. Zahnrad oben "
                      "links öffnen und unter „Übersetzer“ eintragen, wo er "
                      "läuft.")
    if not url:
        return None, "Für den Übersetzer fehlt die Adresse."

    hinweis = ""
    if len(text) > MAX_ZEICHEN:
        text = text[:MAX_ZEICHEN]
        hinweis = ("\n\n[Hinweis: Der Text war länger als "
                   f"{MAX_ZEICHEN} Zeichen und wurde gekürzt.]")

    try:
        if dienst == "ollama":
            if not e["modell"]:
                return None, "Für ollama fehlt der Modellname."
            ergebnis = _ollama(text, ziel, url, e["modell"])
        elif dienst == "libretranslate":
            ergebnis = _libretranslate(text, ziel, url)
        else:
            return None, f"Unbekannter Übersetzer-Dienst: {dienst}"
    except urllib.error.HTTPError as fehler:
        return None, f"Der Übersetzer antwortete mit HTTP {fehler.code}."
    except urllib.error.URLError as fehler:
        return None, (f"Der Übersetzer ist nicht erreichbar ({fehler.reason}). "
                      "Läuft der Dienst, und stimmt die Adresse?")
    except (ValueError, KeyError, json.JSONDecodeError) as fehler:
        return None, f"Der Übersetzer lieferte keine brauchbare Antwort: {fehler}"
    except Exception as fehler:  # noqa: BLE001 - nie die Oberflaeche abstuerzen
        return None, f"Übersetzen fehlgeschlagen: {fehler}"

    return ergebnis + hinweis, None
