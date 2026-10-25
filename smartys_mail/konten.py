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
import tomllib

CONFIG = os.path.expanduser("~/.config/himalaya/config.toml")

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
