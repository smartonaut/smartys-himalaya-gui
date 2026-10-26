# -*- coding: utf-8 -*-
"""HTTP-Server der Oberflaeche.

Bindet ausschliesslich an 127.0.0.1: die Mails bleiben auf dem Rechner.
Der Server spricht nie selbst mit einem Mailserver — das erledigt himalaya.
"""
import json
import mimetypes
import os
import re
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote

from . import demo, himalaya, konten, pfade, signaturen, uebersetzer, verbindung
from .mime import kopf_entpacken, mail_html, mail_text, nachricht_bauen

PORT = int(os.environ.get("SMARTYS_MAIL_PORT", "8770"))
BIND = os.environ.get("SMARTYS_MAIL_BIND", "127.0.0.1")
WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
HIMALAYA_CONFIG = pfade.himalaya_config()
DOWNLOAD_TMP = os.path.join(pfade.datenordner(), "downloads")

# Ordner, in die "Loeschen" verschieben kann. Zuerst der in der
# himalaya-Config hinterlegte Name, danach die ueblichen Schreibweisen.
# Grund: himalaya kennt den echten Papierkorb-Namen eines Servers nicht und
# scheitert sonst mit "Destination mailbox does not exist".
_PAPIERKORB = (
    "Deleted Items", "Papierkorb", "Trash", "Gelöschte Elemente",
    "Deleted Messages", "INBOX.Trash", "Deleted",
)


def alias_papierkorb(konto):
    """mailbox.alias.trash des Kontos aus der himalaya-Config (oder None)."""
    try:
        with open(HIMALAYA_CONFIG, "rb") as f:
            daten = tomllib.load(f)
        konto_daten = daten.get("accounts", {}).get(konto, {})
        return konto_daten.get("mailbox", {}).get("alias", {}).get("trash")
    except Exception:  # noqa: BLE001
        return None
# Beispieldaten statt echter Postfaecher (Screenshots, Ausprobieren)
DEMO = os.environ.get("SMARTYS_MAIL_DEMO") == "1"


def konten_emails():
    """Konto -> Absenderadresse. Liest nur die Adresse, keine Passwoerter."""
    try:
        with open(HIMALAYA_CONFIG, "rb") as f:
            daten = tomllib.load(f)
        return {n: (a.get("email") or "") for n, a in (daten.get("accounts") or {}).items()}
    except Exception:  # noqa: BLE001
        return {}


def konten_je_gruppe():
    ergebnis = {}
    for konto in konten_emails():
        ergebnis.setdefault(signaturen.gruppe_von(konto), []).append(konto)
    return ergebnis


class Handler(BaseHTTPRequestHandler):
    server_version = "SmartysHimalayaGUI"

    def log_message(self, *args):
        pass

    # -------------------------------------------------------------- Ausgabe
    def _sende(self, code, typ, daten):
        roh = daten.encode("utf-8") if isinstance(daten, str) else daten
        self.send_response(code)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(roh)))
        # Nach Code-Aenderungen soll der Browser die neue Oberflaeche laden.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(roh)

    def _json(self, obj):
        self._sende(200, "application/json; charset=utf-8",
                    json.dumps(obj, ensure_ascii=False))

    def _post_daten(self):
        laenge = int(self.headers.get("Content-Length") or 0)
        return json.loads((self.rfile.read(laenge) or b"{}").decode("utf-8"))

    # ----------------------------------------------------------------- POST
    def do_POST(self):
        pfad = urlparse(self.path).path
        try:
            d = self._post_daten()
        except Exception:  # noqa: BLE001
            return self._json({"error": "ungueltige Anfrage"})

        if pfad == "/api/send":
            return self._senden_mail(d)
        if pfad == "/api/flag":
            return self._flag(d)
        if pfad == "/api/delete":
            return self._loeschen(d)
        if pfad == "/api/uebersetzen":
            return self._uebersetzen(d)

        if pfad == "/api/signatur":
            return self._signatur_setzen(d)
        if pfad == "/api/verbindung":
            fehler = verbindung.speichern(d)
            if fehler:
                return self._json({"error": fehler})
            # Sofort pruefen, ob die Einstellung traegt
            probe = himalaya.json_aufruf(["account", "list"], timeout=45)
            return self._json({"ok": True,
                               "erreichbar": "error" not in probe,
                               "meldung": probe.get("error") or "",
                               "konten": len(probe.get("accounts") or [])})

        if pfad == "/api/konto/pruefen":
            return self._konto_pruefen(d)
        if pfad == "/api/konto/anlegen":
            return self._konto_anlegen(d)
        self._sende(404, "text/plain; charset=utf-8", "nicht gefunden")

    def _flag(self, d):
        konto = (d.get("account") or "").strip()
        mid = str(d.get("id") or "").strip()
        box = d.get("mailbox") or "Inbox"
        if not (konto and mid):
            return self._json({"error": "Konto und Mail noetig"})
        # gelesen=true setzt "seen" gezielt (beim Oeffnen einer Mail).
        # Ohne die Angabe wird umgeschaltet (Knopf in der Oberflaeche).
        if d.get("gelesen"):
            antwort = himalaya.json_aufruf(
                ["flag", "add", "-a", konto, "-m", box, "seen", mid])
            if "error" in antwort:
                return self._json(antwort)
            return self._json({"ok": True, "gelesen": True})
        antwort = himalaya.json_aufruf(["flag", "add", "-a", konto, "-m", box, "seen", mid])
        if "error" in antwort:
            antwort = himalaya.json_aufruf(["flag", "remove", "-a", konto, "-m", box, "seen", mid])
            if "error" in antwort:
                return self._json(antwort)
        return self._json({"ok": True})

    def _loeschen(self, d):
        konto = (d.get("account") or "").strip()
        mid = str(d.get("id") or "").strip()
        box = d.get("mailbox") or "Inbox"
        if not (konto and mid):
            return self._json({"error": "Konto und Mail noetig"})

        antwort = himalaya.json_aufruf(
            ["message", "delete", "-a", konto, "-m", box, mid])
        if "error" not in antwort:
            return self._json({"ok": True})

        # himalaya loescht in den in seiner Config hinterlegten Papierkorb.
        # Stimmt der Name nicht mit dem Server ueberein, kommt
        # "Destination mailbox does not exist" — dann selbst verschieben.
        if "Destination mailbox does not exist" not in str(antwort.get("error", "")):
            return self._json(antwort)

        kandidaten = []
        alias = alias_papierkorb(konto)
        if alias:
            kandidaten.append(alias)
        kandidaten += [k for k in _PAPIERKORB if k not in kandidaten]

        for ziel in kandidaten:
            mv = himalaya.json_aufruf(
                ["message", "move", "-a", konto, "-f", box, "-t", ziel, mid])
            if "error" not in mv:
                return self._json({"ok": True, "verschoben_nach": ziel})

        return self._json({
            "error": "Kein Papierkorb-Ordner gefunden. In der "
                     "himalaya-Konfiguration mailbox.alias.trash auf den "
                     "echten Ordnernamen des Servers setzen."})

    def _uebersetzen(self, d):
        ergebnis, fehler = uebersetzer.uebersetzen(
            d.get("text") or "", (d.get("ziel") or "").strip() or None)
        if fehler:
            return self._json({"error": fehler})
        return self._json({"uebersetzt": ergebnis})

    def _signatur_setzen(self, d):
        gruppe = (d.get("gruppe") or "").strip()
        if not gruppe:
            return self._json({"error": "Gruppe fehlt"})
        try:
            signaturen.setzen(gruppe, d.get("html") or "")
        except Exception as e:  # noqa: BLE001
            return self._json({"error": f"Speichern fehlgeschlagen: {e}"})
        return self._json({"ok": True})

    def _konto_pruefen(self, d):
        """Serverdaten zum Adressteil vorschlagen."""
        email = (d.get("email") or "").strip()
        if not email:
            return self._json({"error": "E-Mail fehlt"})
        return self._json(konten.anbieter_erkennen(email))

    def _konto_anlegen(self, d):
        ergebnis = konten.konto_hinzufuegen(
            email=d.get("email"), passwort=d.get("passwort"),
            anzeigename=d.get("anzeigename"), name=d.get("name"),
            imap_host=d.get("imap_host"), imap_port=d.get("imap_port") or 993,
            smtp_host=d.get("smtp_host"), smtp_port=d.get("smtp_port") or 465)
        if "error" in ergebnis:
            return self._json(ergebnis)
        # Verbindung sofort testen, damit der Nutzer nicht im Dunkeln sitzt
        test = himalaya.json_aufruf(
            ["account", "list"], timeout=30)
        namen = [a.get("name") for a in (test.get("accounts") or [])]
        ergebnis["sichtbar"] = ergebnis.get("name") in namen
        return self._json(ergebnis)

    def _senden_mail(self, d):
        konto = (d.get("account") or "").strip()
        an = (d.get("an") or "").strip()
        cc = (d.get("cc") or "").strip()
        betreff = (d.get("betreff") or "").strip()
        html = d.get("html") or ""
        if not (konto and an):
            return self._json({"error": "Konto und Empfaenger noetig"})
        if not html.strip():
            return self._json({"error": "Text fehlt"})
        # Ein leerer Betreff ("Re: ") faellt beim Empfaenger unangenehm auf
        # und landet leichter im Spam.
        if betreff in ("", "Re:", "AW:", "Fwd:", "WG:"):
            return self._json({"error": "Betreff fehlt"})

        absender = konten_emails().get(konto) or konto
        antwort_auf = referenzen = ""
        mid = str(d.get("antwortAuf") or "").strip()
        box = d.get("ordner") or "Inbox"
        if mid:
            _, roh, _ = himalaya.roh_aufruf(
                ["message", "read", "-a", konto, "-m", box, mid], timeout=60)
            treffer = re.search(r"(?mi)^message-id:\s*(\S+)", roh or "")
            if treffer:
                antwort_auf = referenzen = treffer.group(1)

        rohdaten = nachricht_bauen(absender, an, betreff, html, cc=cc,
                                   antwort_auf=antwort_auf, referenzen=referenzen)

        gesendet = himalaya.gesendet_ordner(konto)
        argumente = ["message", "send", "-a", konto]
        if gesendet:
            argumente += ["--save", gesendet]
        code, aus, fehler = himalaya.roh_aufruf(argumente, stdin=rohdaten, timeout=180)
        if code != 0:
            return self._json({"error": (fehler or aus or "Senden fehlgeschlagen").strip()[:300]})
        return self._json({"ok": True, "gespeichertIn": gesendet})

    # ------------------------------------------------------------------ GET
    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        pfad = u.path

        def w(name, vorgabe=""):
            return (q.get(name) or [vorgabe])[0]

        # Logo als Bild ausliefern (Kopfzeile der Oberflaeche, Browser-Tab).
        # Gesucht wird im Paket: assets/icons neben dem Modul.
        if pfad in ("/icon.png", "/favicon.ico"):
            hier = os.path.dirname(os.path.abspath(__file__))
            for name in ("logo_256.png", "logo_128.png", "logo_64.png"):
                datei = os.path.abspath(os.path.join(hier, "..", "assets", "icons", name))
                if os.path.exists(datei):
                    with open(datei, "rb") as f:
                        return self._sende(200, "image/png", f.read())
            return self._sende(404, "text/plain; charset=utf-8", "Kein Logo im Paket")

        # Statische Dateien
        if pfad in ("/", "/index.html", "/app.js", "/i18n.js", "/style.css"):
            datei = os.path.join(WEB, "index.html" if pfad in ("/", "/index.html") else pfad.lstrip("/"))
            if not os.path.exists(datei):
                return self._sende(500, "text/plain; charset=utf-8", "Oberflaeche fehlt")
            typ = mimetypes.guess_type(datei)[0] or "text/plain"
            if typ.startswith("text/") or typ.endswith("javascript"):
                typ += "; charset=utf-8"
            with open(datei, "rb") as f:
                return self._sende(200, typ, f.read())

        if pfad == "/api/verbindung":
            einstellung = verbindung.laden()
            # Kennwort/Token gibt es hier nicht — nur wo himalaya laeuft
            einstellung["himalaya_gefunden"] = os.path.exists(pfade.himalaya_binary()) or \
                os.path.exists(pfade.himalaya_binary() + ".exe")
            return self._json(einstellung)

        if pfad == "/api/accounts":
            if DEMO:
                return self._json(demo.konten())
            return self._json(himalaya.json_aufruf(["account", "list"]))

        if pfad == "/api/signaturen":
            if DEMO:
                return self._json(demo.signaturen())
            daten = signaturen.laden()
            gruppen = {}
            for gruppe, konten in konten_je_gruppe().items():
                gruppen[gruppe] = {"konten": sorted(konten),
                                   "html": (daten.get("gruppen") or {}).get(gruppe, "")}
            return self._json({"gruppen": gruppen,
                               "ausnahmen": daten.get("ausnahmen") or {}})

        if pfad == "/api/mailboxes":
            konto = w("account")
            if not konto:
                return self._json({"error": "account fehlt"})
            if DEMO:
                return self._json(demo.mailboxes(konto))
            return self._json(himalaya.json_aufruf(["mailbox", "list", "-a", konto]))

        if pfad == "/api/list":
            return self._liste(w)

        if pfad == "/api/search":
            konto, such = w("account"), w("q").strip()
            if not (konto and such):
                return self._json({"error": "account/q fehlt"})
            if DEMO:
                return self._json(demo.suche(konto, such))
            sicher = such.replace('"', " ")
            return self._json(himalaya.json_aufruf(
                ["envelope", "search", "-a", konto, f"subject {sicher} or from {sicher}"],
                timeout=120))

        if pfad == "/api/read":
            return self._lesen(w)

        if pfad == "/api/attachment":
            return self._anhang(w)

        self._sende(404, "text/plain; charset=utf-8", "nicht gefunden")

    def _liste(self, w):
        konto = w("account")
        if not konto:
            return self._json({"error": "account fehlt"})
        if DEMO:
            return self._json(demo.liste(konto, w("mailbox", "Inbox")))
        box = w("mailbox", "Inbox")
        seite = w("page", "1")
        ergebnis = {"error": "kein Ordner"}
        for variante in himalaya.ordner_varianten(box):
            ergebnis = himalaya.json_aufruf(
                ["envelope", "list", "-a", konto, "-m", variante, "-s", "60", "-p", seite])
            if "error" not in ergebnis:
                break
        return self._json(ergebnis)

    def _lesen(self, w):
        konto, mid = w("account"), w("id")
        box = w("mailbox", "Inbox")
        if not (konto and mid):
            return self._json({"error": "account/id fehlt"})
        if DEMO:
            return self._json(demo.lesen(konto, mid, box))
        code, roh, fehler = 1, "", ""
        for variante in himalaya.ordner_varianten(box):
            code, roh, fehler = himalaya.roh_aufruf(
                # --raw ist Pflicht: ohne das zeigt himalaya nur den
                # text/plain-Teil, und HTML-Mails kommen als flacher
                # Textblock an (Tabellen, Links, Formatierung verloren).
                ["message", "read", "-a", konto, "-m", variante, mid, "--raw"])
            if code == 0 and roh:
                box = variante
                break
        if code != 0 and not roh:
            return self._json({"error": (fehler or "").strip()[:300]})

        # Bei einer Rohmail (--raw) steht der Kopf als RFC-822, nicht als
        # einfacher Text. Beides abdecken: erst versuchen, den Kopf aus der
        # Mailstruktur zu lesen, sonst wie bisher die erste Leerzeile teilen.
        felder_aus_mime = {}
        try:
            _h, _t = None, None
            import email
            from email import policy
            msg = email.message_from_string(roh, policy=policy.default)
            for feld in ("subject", "from", "to", "date"):
                wert = msg.get(feld)
                if wert:
                    felder_aus_mime[feld] = str(wert)
        except Exception:
            felder_aus_mime = {}

        kopf, _, rumpf = roh.partition("\n\n")
        felder = dict(felder_aus_mime)
        for zeile in kopf.splitlines():
            if ":" in zeile:
                k, v = zeile.split(":", 1)
                felder[k.strip().lower()] = v.strip()

        anhaenge = []
        antwort = himalaya.json_aufruf(
            ["attachment", "list", "-a", konto, "-m", box, mid], timeout=60)
        for x in (antwort.get("attachments") or []):
            anhaenge.append({"name": x.get("filename") or x.get("name") or ""})

        return self._json({"subject": kopf_entpacken(felder.get("subject", "")),
                           "from": kopf_entpacken(felder.get("from", "")),
                           "date": felder.get("date", ""),
                           "anhaenge": anhaenge,
                           # Immer die VOLLE Rohmail uebergeben: rumpf ist
                           # der Text nach dem ersten Leerzeilen-Trenner und
                           # damit kein gueltiges MIME mehr — mail_text()
                           # baut daraus sonst aus dem HTML einen 49k-Text
                           # statt den vorhandenen text/plain-Teil zu nehmen.
                           "body": mail_text(roh),
                           # HTML-Fassung fuer die Anzeige. Fehlt sie,
                           # zeigt die Oberflaeche den Text — nie beides
                           # untereinander, das doppelt den Inhalt.
                           "body_html": mail_html(roh),
                           # Die Oberflaeche entscheidet anhand dieser
                           # Einstellung, ob sie externe Bilder sperrt.
                           "bilder_laden": bool(
                               verbindung.laden().get("bilder_laden"))})

    def _anhang(self, w):
        konto, mid = w("account"), w("id")
        box, index = w("mailbox", "Inbox"), w("index", "0")
        if not (konto and mid):
            return self._json({"error": "account/id fehlt"})
        os.makedirs(DOWNLOAD_TMP, exist_ok=True)
        vorher = set(os.listdir(DOWNLOAD_TMP))
        _, _, fehler = himalaya.roh_aufruf(
            ["attachment", "download", "-a", konto, "-m", box, "-d", DOWNLOAD_TMP, mid, index])
        neu = set(os.listdir(DOWNLOAD_TMP)) - vorher
        if not neu:
            return self._json({"error": (fehler or "Anhang nicht gefunden").strip()[:200]})
        datei = os.path.join(DOWNLOAD_TMP, sorted(neu)[0])
        try:
            rohdaten = open(datei, "rb").read()
            os.remove(datei)
        except Exception as e:  # noqa: BLE001
            return self._json({"error": str(e)})
        name = os.path.basename(datei)
        self.send_response(200)
        self.send_header("Content-Type",
                         mimetypes.guess_type(name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(rohdaten)))
        self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(name)}")
        self.end_headers()
        return self.wfile.write(rohdaten)


def starten(port=None, bind=None):
    os.makedirs(DOWNLOAD_TMP, exist_ok=True)
    p = port or PORT
    b = bind or BIND
    print(f"Smartys Himalaya GUI auf http://{b}:{p}")
    ThreadingHTTPServer((b, p), Handler).serve_forever()
