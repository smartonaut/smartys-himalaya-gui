# -*- coding: utf-8 -*-
"""Konten einrichten, ohne dass jemand Servernamen kennen muss.

himalaya bringt einen interaktiven Assistenten mit, der im Terminal laeuft.
Fuer eine grafische Oberflaeche ist das unbrauchbar — deshalb schreibt dieses
Modul die Konfiguration selbst.

Bekannte Anbieter werden an der Domain erkannt und mit den richtigen
Serverdaten gefuellt. Alles andere landet in der manuellen Eingabe.
"""
import os
import re
import shutil
import tomllib

from . import pfade

CONFIG = pfade.himalaya_config()

# Gruppen in der Kontenleiste. Aus der Domain abgeleitet, damit beim Anlegen
# eines Kontos nichts gepflegt werden muss. Reihenfolge = Anzeigereihenfolge,
# der Rest landet unter GRUPPE_REST.
GRUPPEN = (
    ("Dekojuwelen", ("dekojuwelen.de",)),
    ("Smartys Tech", ("smartys.tech", "smarty.tips")),
    ("Job / SK", ("sk-ft.de", "sk-smarty.de")),
)
GRUPPE_REST = "Privat"

# host_imap, port_imap, host_smtp, port_smtp, verschluesselung, hinweis
ANBIETER = {
    "gmail.com": ("imap.gmail.com", 993, "smtp.gmail.com", 465, "tls",
                  "Google verlangt ein App-Passwort (16 Zeichen), nicht das "
                  "Kontopasswort. Erstellen unter: "
                  "https://myaccount.google.com/apppasswords — dafür muss die "
                  "Bestätigung in zwei Schritten aktiv sein."),
    "googlemail.com": ("imap.gmail.com", 993, "smtp.gmail.com", 465, "tls",
                       "Google verlangt ein App-Passwort (16 Zeichen)."),
    "gmx.de": ("imap.gmx.net", 993, "mail.gmx.net", 465, "tls",
               "In den GMX-Einstellungen muss IMAP/POP3 freigeschaltet sein."),
    "gmx.net": ("imap.gmx.net", 993, "mail.gmx.net", 465, "tls",
                "In den GMX-Einstellungen muss IMAP/POP3 freigeschaltet sein."),
    "web.de": ("imap.web.de", 993, "smtp.web.de", 587, "starttls",
               "In den WEB.DE-Einstellungen muss IMAP freigeschaltet sein."),
    "t-online.de": ("secureimap.t-online.de", 993, "securesmtp.t-online.de", 465, "tls",
                    "T-Online verlangt ein eigenes E-Mail-Passwort, das im "
                    "Kundencenter gesetzt wird — nicht das Login-Passwort."),
    "outlook.com": ("outlook.office365.com", 993, "smtp.office365.com", 587, "starttls",
                    "Microsoft verlangt meist ein App-Passwort, wenn "
                    "Zwei-Faktor-Anmeldung aktiv ist."),
    "hotmail.com": ("outlook.office365.com", 993, "smtp.office365.com", 587, "starttls",
                    "Microsoft verlangt meist ein App-Passwort."),
    "live.de": ("outlook.office365.com", 993, "smtp.office365.com", 587, "starttls",
                "Microsoft verlangt meist ein App-Passwort."),
    "yahoo.com": ("imap.mail.yahoo.com", 993, "smtp.mail.yahoo.com", 465, "tls",
                  "Yahoo verlangt ein App-Passwort aus den Kontoeinstellungen."),
    "yahoo.de": ("imap.mail.yahoo.com", 993, "smtp.mail.yahoo.com", 465, "tls",
                 "Yahoo verlangt ein App-Passwort."),
    "ionos.de": ("imap.ionos.de", 993, "smtp.ionos.de", 465, "tls", ""),
    "1und1.de": ("imap.ionos.de", 993, "smtp.ionos.de", 465, "tls", ""),
    "freenet.de": ("mx.freenet.de", 993, "mx.freenet.de", 465, "tls", ""),
    "posteo.de": ("posteo.de", 993, "posteo.de", 465, "tls", ""),
    "mailbox.org": ("imap.mailbox.org", 993, "smtp.mailbox.org", 465, "tls", ""),
}


def anbieter_erkennen(email):
    """Serverdaten anhand der Domain raten — None, wenn unbekannt."""
    domain = (email or "").split("@")[-1].lower().strip()
    if domain in ANBIETER:
        i_host, i_port, s_host, s_port, art, hinweis = ANBIETER[domain]
        return {"imap_host": i_host, "imap_port": i_port,
                "smtp_host": s_host, "smtp_port": s_port,
                "verschluesselung": art, "hinweis": hinweis,
                "erkannt": True}
    # Selbst gehostete Domains: haeufig mail.<domain> oder imap.<domain>
    return {"imap_host": f"mail.{domain}", "imap_port": 993,
            "smtp_host": f"mail.{domain}", "smtp_port": 465,
            "verschluesselung": "tls", "hinweis": "",
            "erkannt": False}


def _toml_string(wert):
    """Wert als TOML-Zeichenkette — Anfuehrungszeichen und Backslashes schuetzen."""
    return '"' + str(wert).replace("\\", "\\\\").replace('"', '\\"') + '"'


def konto_block(name, email, anzeigename, passwort, imap_host, imap_port,
                smtp_host, smtp_port, verschluesselung="tls", standard=False):
    """Einen [accounts.NAME]-Block als TOML-Text bauen."""
    imap_schema = "imaps" if int(imap_port) == 993 else "imap"
    smtp_schema = "smtps" if int(smtp_port) == 465 else "smtp"
    zeilen = [
        f"[accounts.{_toml_string(name)}]",
        f"email = {_toml_string(email)}",
        f"display-name = {_toml_string(anzeigename or name)}",
        f"default = {'true' if standard else 'false'}",
        "",
        f"[accounts.{_toml_string(name)}.imap]",
        f"server = {_toml_string(f'{imap_schema}://{imap_host}:{imap_port}')}",
        "",
        f"[accounts.{_toml_string(name)}.imap.sasl.login]",
        f"username = {_toml_string(email)}",
        f"password = {_toml_string(passwort)}",
        "",
        f"[accounts.{_toml_string(name)}.smtp]",
        f"server = {_toml_string(f'{smtp_schema}://{smtp_host}:{smtp_port}')}",
        "",
        f"[accounts.{_toml_string(name)}.smtp.sasl.login]",
        f"username = {_toml_string(email)}",
        f"password = {_toml_string(passwort)}",
        "",
    ]
    # STARTTLS-Anbieter (Port 587) brauchen keinen Sonderfall: himalaya
    # verhandelt TLS bei "smtp://" automatisch, wenn der Port es verlangt.
    return "\n".join(zeilen)


def konten_lesen():
    """Namen der bereits eingerichteten Konten."""
    try:
        with open(CONFIG, "rb") as f:
            return list((tomllib.load(f).get("accounts") or {}).keys())
    except Exception:  # noqa: BLE001
        return []


def name_vorschlag(email):
    """Kontoname aus der Adresse: max@firma.de -> max-firma-de."""
    basis = re.sub(r"[^a-z0-9]+", "-", (email or "").lower()).strip("-")
    return basis or "konto"


def konto_hinzufuegen(email, passwort, anzeigename="", name="",
                      imap_host="", imap_port=993, smtp_host="", smtp_port=465,
                      verschluesselung="tls"):
    """Konto an die himalaya-Konfiguration anhaengen.

    Die Datei wird vorher gesichert. Bei TOML-Fehlern bleibt das Original
    unveraendert — ein kaputter Zustand waere schlimmer als ein Fehlschlag.
    """
    email = (email or "").strip()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return {"error": "Das sieht nicht wie eine E-Mail-Adresse aus."}
    if not (passwort or "").strip():
        return {"error": "Passwort fehlt."}

    bekannt = konten_lesen()
    name = (name or "").strip() or name_vorschlag(email)
    if name in bekannt:
        return {"error": f"Ein Konto namens '{name}' gibt es schon."}

    if not imap_host:
        daten = anbieter_erkennen(email)
        imap_host, imap_port = daten["imap_host"], daten["imap_port"]
        smtp_host, smtp_port = daten["smtp_host"], daten["smtp_port"]
    if not smtp_host:
        smtp_host = imap_host

    block = konto_block(name, email, anzeigename, passwort,
                        imap_host, int(imap_port), smtp_host, int(smtp_port),
                        verschluesselung, standard=not bekannt)

    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    alt = ""
    if os.path.exists(CONFIG):
        with open(CONFIG, encoding="utf-8") as f:
            alt = f.read()
        # Sicherung, damit ein Fehlschlag nichts zerstört
        with open(CONFIG + ".bak", "w", encoding="utf-8") as f:
            f.write(alt)

    neu = alt.rstrip() + "\n\n" + block
    with open(CONFIG, "w", encoding="utf-8") as f:
        f.write(neu)
    try:
        os.chmod(CONFIG, 0o600)
    except Exception:  # noqa: BLE001
        pass

    # Pruefen, ob himalaya die Datei akzeptiert
    try:
        with open(CONFIG, "rb") as f:
            tomllib.load(f)
    except Exception as e:  # noqa: BLE001
        if alt:
            with open(CONFIG, "w", encoding="utf-8") as f:
                f.write(alt)
        return {"error": f"Konfiguration waere ungueltig ({e}) — nichts geaendert."}

    return {"ok": True, "name": name}


# ---------------------------------------------------------------- Gruppen
def gruppe_von(email):
    """Gruppenname zu einer Adresse. Unbekannte Domains landen unter Privat."""
    dom = (email or "").rsplit("@", 1)[-1].lower() if "@" in (email or "") else ""
    for gruppe, endungen in GRUPPEN:
        for e in endungen:
            if dom == e or dom.endswith("." + e):
                return gruppe
    return GRUPPE_REST


def gruppen_reihenfolge():
    return [g for g, _ in GRUPPEN] + [GRUPPE_REST]


def konto_info():
    """Kontoname -> {email, display_name, gruppe}.

    Liest nur Adresse und Anzeigename, keine Zugangsdaten. Grundlage fuer die
    beschriftete Kontenleiste: himalaya selbst liefert in `account list --json`
    weder Adresse noch Anzeigename.
    """
    try:
        with open(CONFIG, "rb") as f:
            daten = tomllib.load(f)
    except Exception:  # noqa: BLE001
        return {}
    info = {}
    for name, eintrag in (daten.get("accounts") or {}).items():
        if not isinstance(eintrag, dict):
            continue
        email = eintrag.get("email") or ""
        info[name] = {
            "email": email,
            "display_name": eintrag.get("display-name") or "",
            "gruppe": gruppe_von(email),
        }
    return info


def anzeigename_setzen(konto, anzeigename):
    """Aendert NUR display-name des Kontos, nicht den Kontonamen.

    Der Kontoname ist der Schluessel in himalaya — Signatur-Gruppen,
    Mailbox-Aliase und die Verknuepfung in signaturen.json haengen daran. Ein
    Umbenennen des Schluessels wuerde sie alle verlieren.
    """
    name = (konto or "").strip()
    wert = (anzeigename or "").strip()
    if not name:
        return {"error": "Konto fehlt"}
    if "\n" in wert or "\r" in wert:
        return {"error": "Der Anzeigename darf keinen Zeilenumbruch enthalten."}
    if len(wert) > 80:
        return {"error": "Der Anzeigename ist zu lang (maximal 80 Zeichen)."}

    try:
        with open(CONFIG, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:  # noqa: BLE001
        return {"error": f"Konfiguration nicht lesbar: {e}"}

    kopf = re.search(r"^\[accounts\." + re.escape(name) + r"\]\s*$", text, re.M)
    if not kopf:
        return {"error": f"Konto {name} steht nicht in der Konfiguration."}
    rest = text[kopf.end():]
    naechste = re.search(r"^\[", rest, re.M)
    ende = kopf.end() + (naechste.start() if naechste else len(rest))
    block = text[kopf.end():ende]

    zeile = "display-name = " + _toml_string(wert)
    if re.search(r"^display-name\s*=.*$", block, re.M):
        block_neu = re.sub(r"^display-name\s*=.*$", lambda _m: zeile, block,
                           count=1, flags=re.M)
    elif block.startswith("\n"):
        block_neu = "\n" + zeile + block
    else:
        block_neu = "\n" + zeile + "\n" + block

    neu = text[:kopf.end()] + block_neu + text[ende:]

    # Probe, bevor geschrieben wird: die Datei muss gueltiges TOML bleiben und
    # den neuen Wert wirklich enthalten.
    try:
        probe = tomllib.loads(neu)
        if (probe.get("accounts", {}).get(name, {}).get("display-name") or "") != wert:
            return {"error": "Der Anzeigename liess sich nicht setzen — nichts geaendert."}
    except Exception as e:  # noqa: BLE001
        return {"error": f"Konfiguration waere ungueltig ({e}) — nichts geaendert."}

    try:
        shutil.copy2(CONFIG, CONFIG + ".bak")
    except Exception:  # noqa: BLE001
        pass
    try:
        with open(CONFIG, "w", encoding="utf-8") as f:
            f.write(neu)
        os.chmod(CONFIG, 0o600)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Schreiben fehlgeschlagen: {e}"}
    return {"ok": True, "name": name, "display_name": wert}
