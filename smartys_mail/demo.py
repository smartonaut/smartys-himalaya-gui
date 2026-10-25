# -*- coding: utf-8 -*-
"""Beispieldaten fuer Screenshots und zum Ausprobieren.

Mit SMARTYS_MAIL_DEMO=1 beantwortet der Server alle Anfragen aus diesem Modul
statt aus himalaya. So lässt sich die Oberfläche zeigen, ohne echte Postfächer
zu berühren — und es landen garantiert keine fremden Daten in Screenshots.
"""
import html

KONTEN = [
    {"name": "beispiel-firma", "default": True, "backends": ["imap", "smtp"]},
    {"name": "beispiel-privat", "default": False, "backends": ["imap", "smtp"]},
    {"name": "beispiel-verein", "default": False, "backends": ["imap", "smtp"]},
]

ORDNER = ["Inbox", "Sent Items", "Drafts", "Archive", "Junk Mail", "Deleted Items"]

_MAILS = {
    "Inbox": [
        (101, "Anna Berger", "anna.berger@beispiel-firma.de",
         "Angebot 2026-114: Lieferung Kaffeemaschinen",
         "2026-10-25T09:12:00+01:00",
         "Guten Tag,\n\nanbei unser Angebot über sechs Kaffeemaschinen "
         "inklusive Wartungspaket. Die Lieferzeit beträgt acht Werktage.\n\n"
         "Für Rückfragen stehe ich gern zur Verfügung.\n\nMit freundlichen Grüßen\n"
         "Anna Berger\nBeispiel GmbH"),
        (102, "Marktplatz Nord", "news@marktplatz-nord.example",
         "Ihre Anzeige wurde freigegeben",
         "2026-10-24T17:45:00+01:00",
         "Ihre Anzeige ist jetzt online und für 30 Tage sichtbar.\n\n"
         "Sie können sie jederzeit im Konto bearbeiten oder verlängern."),
        (103, "Thomas Krämer", "t.kraemer@beispiel-firma.de",
         "Re: Termin am Donnerstag",
         "2026-10-24T11:03:00+01:00",
         "Hallo,\n\nDonnerstag 14 Uhr passt mir gut. Ich bringe die Unterlagen mit.\n\n"
         "Bis dahin\nThomas"),
        (104, "Buchhaltung", "buchhaltung@beispiel-firma.de",
         "Rechnung 2026-0847 beglichen",
         "2026-10-23T08:20:00+01:00",
         "Die Rechnung über 1.240,00 € ist am 23.10. bei uns eingegangen.\n"
         "Vorgang abgeschlossen."),
        (105, "Systembenachrichtigung", "no-reply@beispiel-firma.de",
         "Sicherheitshinweis: neue Anmeldung",
         "2026-10-22T21:14:00+01:00",
         "Es wurde eine Anmeldung von einem neuen Gerät festgestellt.\n"
         "Falls Sie das nicht waren, ändern Sie bitte umgehend Ihr Passwort."),
    ],
    "Sent Items": [
        (201, "Anna Berger", "anna.berger@beispiel-firma.de",
         "Re: Angebot 2026-114: Lieferung Kaffeemaschinen",
         "2026-10-25T10:02:00+01:00",
         "Guten Tag Frau Berger,\n\ndas Angebot passt. Bitte senden Sie mir noch "
         "die Wartungsbedingungen zu.\n\nFreundliche Grüße"),
        (202, "Thomas Krämer", "t.kraemer@beispiel-firma.de",
         "Termin am Donnerstag",
         "2026-10-23T16:30:00+01:00",
         "Hallo Thomas,\n\npasst dir Donnerstag um 14 Uhr?\n\nGruß"),
    ],
    "Drafts": [
        (301, "", "",
         "Entwurf: Zusammenfassung Quartal",
         "2026-10-25T08:00:00+01:00",
         "Noch offen: Zahlen vom Steuerberater abwarten."),
    ],
    "Archive": [],
    "Junk Mail": [
        (401, "Gewinnspiel-Zentrale", "gewinn@beispiel.example",
         "Sie haben gewonnen!",
         "2026-10-20T03:11:00+01:00",
         "Glückwunsch, Sie wurden ausgewählt …"),
    ],
    "Deleted Items": [],
}

INHALT = {
    101: "<p>Guten Tag,</p><p>anbei unser Angebot über <b>sechs Kaffeemaschinen</b> "
         "inklusive Wartungspaket. Die Lieferzeit beträgt acht Werktage.</p>"
         "<p>Für Rückfragen stehe ich gern zur Verfügung.</p>"
         "<p>Mit freundlichen Grüßen<br>Anna Berger<br>Beispiel GmbH</p>",
    102: "<p>Ihre Anzeige ist jetzt online und für 30 Tage sichtbar.</p>",
    103: "<p>Hallo,</p><p>Donnerstag 14 Uhr passt mir gut. Ich bringe die Unterlagen mit.</p>"
         "<p>Bis dahin<br>Thomas</p>",
    104: "<p>Die Rechnung über <b>1.240,00 €</b> ist am 23.10. bei uns eingegangen.</p>"
         "<p>Vorgang abgeschlossen.</p>",
    105: "<p>Es wurde eine Anmeldung von einem neuen Gerät festgestellt.</p>",
    201: "<p>Guten Tag Frau Berger,</p><p>das Angebot passt. Bitte senden Sie mir noch "
         "die Wartungsbedingungen zu.</p>",
    202: "<p>Hallo Thomas,</p><p>passt dir Donnerstag um 14 Uhr?</p>",
    301: "<p>Noch offen: Zahlen vom Steuerberater abwarten.</p>",
    401: "<p>Glückwunsch, Sie wurden ausgewählt …</p>",
}


def konten():
    return {"accounts": KONTEN}


def mailboxes(_konto):
    return {"mailboxes": [{"name": n, "id": n, "total": None, "unread": None}
                          for n in ORDNER]}


def liste(_konto, ordner):
    eintraege = []
    for mid, name, adresse, betreff, datum, _ in _MAILS.get(ordner, []):
        eintraege.append({
            "id": str(mid),
            "subject": betreff,
            "from": [{"name": name or None, "email": adresse or None}],
            "date": datum,
            "flags": [] if mid in (101, 103, 105) else ["seen"],
            "size": 1024,
            "has-attachment": None,
        })
    return {"envelopes": eintraege}


def lesen(_konto, mid, _ordner):
    mid = int(mid)
    for ordner, eintraege in _MAILS.items():
        for m in eintraege:
            if m[0] == mid:
                _, name, adresse, betreff, datum, text = m
                return {"subject": betreff,
                        "from": f"{name} <{adresse}>" if name else adresse,
                        "date": datum,
                        "anhaenge": [],
                        "body": text}
    return {"error": "Nachricht nicht gefunden"}


def suche(_konto, begriff):
    begriff = begriff.lower()
    treffer = []
    for eintraege in _MAILS.values():
        for mid, name, adresse, betreff, datum, _ in eintraege:
            if begriff in (betreff or "").lower() or begriff in (name or "").lower():
                treffer.append({"id": str(mid), "subject": betreff,
                                "from": [{"name": name or None, "email": adresse or None}],
                                "date": datum, "flags": []})
    return {"envelopes": treffer}


def signaturen():
    return {
        "gruppen": {
            "beispiel-firma": {"konten": ["beispiel-firma"],
                               "html": "<p><b>Max Mustermann</b><br>Beispiel GmbH</p>"},
            "beispiel-privat": {"konten": ["beispiel-privat"], "html": ""},
            "beispiel-verein": {"konten": ["beispiel-verein"], "html": ""},
        },
        "ausnahmen": {},
    }
