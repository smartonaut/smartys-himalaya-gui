# -*- coding: utf-8 -*-
"""MIME-Nachrichten bauen und Mail-Texte lesbar machen."""
import html as htmllib
import quopri
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

# himalaya stellt jedem Teil eine Kopfzeile voran:
#   [1] text/html (16.22 KiB)
#       Content-Type: text/html; charset=UTF-8
#       Content-Transfer-Encoding: quoted-printable
_TEILKOPF = re.compile(r"(?m)^\[\d+\]\s+[\w./+-]+[^\n]*\n(?:\s+Content-[^\n]*\n)*\s*\n?")
_TAGAUF = re.compile(r"(?s)<[^>]+>")
_HTML_VERDACHT = re.compile(r"(?i)<(html|body|div|p|table|br)\b")


def mail_text(roh):
    """Rohmail-Ausgabe von himalaya in lesbaren Text wandeln."""
    if not roh:
        return ""
    # Echte Rohmail (himalaya --raw): den text/plain-Teil nehmen, sonst aus
    # dem HTML eine Textfassung bauen.
    html_teil, text_teil = _echtes_mime(roh)
    if text_teil or html_teil:
        if text_teil and text_teil.strip():
            text = text_teil
        else:
            text = html_zu_text(html_teil or "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+\n", "\n", text)
        return re.sub(r"\n{3,}", "\n\n", text).strip()
    text = _TEILKOPF.sub("", roh)
    try:
        text = quopri.decodestring(text.encode("utf-8", "replace")).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 — kaputte Kodierung darf nicht stoeren
        pass
    if _HTML_VERDACHT.search(text):
        text = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", text)
        text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</h[1-6]>", "\n", text)
        text = _TAGAUF.sub("", text)
        text = htmllib.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def kopf_entpacken(wert):
    """MIME-kodierte Kopfzeile lesbar machen.

    Mit --raw kommen Betreff und Absender kodiert an:
    "=?UTF-8?B?TmljaHQgdmVycGFzc2Vu?=" statt "Nicht verpassen". Das ist
    RFC 2047 und wird hier aufgeloest.
    """
    if not wert:
        return ""
    try:
        from email.header import decode_header, make_header
        return str(make_header(decode_header(wert)))
    except Exception:
        return wert


def _echtes_mime(roh):
    """Mail ueber das email-Modul zerlegen, wenn es eine echte Rohmail ist.

    himalaya liefert mit --raw die vollstaendige Nachricht. Das ist die
    einzige Variante, die den HTML-Teil enthaelt: ohne --raw zeigt
    `message read` nur text/plain, und eine HTML-Mail kommt als flacher
    Textblock an.
    Liefert (html, text) oder (None, None), wenn es kein MIME ist.
    """
    if not roh or ":" not in roh[:200]:
        return None, None
    try:
        import email
        from email import policy
        msg = email.message_from_string(roh, policy=policy.default)
    except Exception:
        return None, None

    html_teil, text_teil = None, None
    if msg.is_multipart():
        for teil in msg.walk():
            art = (teil.get_content_type() or "").lower()
            if teil.get_content_maintype() == "multipart":
                continue
            if "attachment" in (teil.get("Content-Disposition") or "").lower():
                continue
            if art == "text/html" and html_teil is None:
                try:
                    html_teil = teil.get_content()
                except Exception:
                    continue
            elif art == "text/plain" and text_teil is None:
                try:
                    text_teil = teil.get_content()
                except Exception:
                    continue
    else:
        art = (msg.get_content_type() or "").lower()
        try:
            inhalt = msg.get_content()
        except Exception:
            inhalt = None
        if art == "text/html":
            html_teil = inhalt
        elif art == "text/plain":
            text_teil = inhalt
    return html_teil, text_teil


def mail_html(roh):
    """Den HTML-Teil einer Rohmail herausgeben, oder "" wenn es keiner ist.

    mail_text() entfernt alle Tags — richtig fuer eine Textvorschau, aber
    eine HTML-Mail verliert damit Tabellen, Hervorhebungen und Bilder und
    sieht aus wie ein unformatierter Textblock. Die Oberflaeche braucht
    beides: Text als Rueckfall, HTML fuer die Anzeige.
    """
    if not roh:
        return ""
    # Echte Rohmail (himalaya --raw): ueber das email-Modul zerlegen
    html_teil, _text = _echtes_mime(roh)
    if html_teil:
        return _entschaerfen(html_teil)
    # Mehrere Teile: den nehmen, der als text/html ausgewiesen ist
    teile = re.split(r"(?m)^\[(\d+)\]\s+([\w./+-]+)", roh)
    if len(teile) >= 3:
        for i in range(1, len(teile) - 1, 3):
            typ = teile[i + 1].lower()
            if typ != "text/html":
                continue
            rumpf = teile[i + 2]
            # Kopfzeilen des Teils abschneiden. Der split() laesst den Rest
            # der Kopfzeile stehen — "(0.5 KiB)", "Content-Type: ..." — und
            # der Rumpf beginnt erst nach der ersten Leerzeile.
            rumpf = rumpf.split("\n\n", 1)[-1] if "\n\n" in rumpf else rumpf
            rumpf = re.sub(r"(?m)^\s+Content-[^\n]*\n", "", rumpf)
            rumpf = re.sub(r"(?m)^\s+Content-[^\n]*$", "", rumpf)
            # MIME-Trennzeichen am Ende entfernen
            rumpf = re.sub(r"(?m)^--[-=\w]+(--)?\s*$", "", rumpf)
            rumpf = rumpf.strip()
            try:
                rumpf = quopri.decodestring(
                    rumpf.encode("utf-8", "replace")).decode("utf-8", "replace")
            except Exception:
                pass
            if _HTML_VERDACHT.search(rumpf):
                return _entschaerfen(rumpf)
        return ""

    # Einteilige Mail: nur wenn der Inhalt nach HTML aussieht
    text = _TEILKOPF.sub("", roh)
    try:
        text = quopri.decodestring(
            text.encode("utf-8", "replace")).decode("utf-8", "replace")
    except Exception:
        pass
    if _HTML_VERDACHT.search(text):
        return _entschaerfen(text)
    return ""


def _entschaerfen(markup):
    """Aktive Inhalte entfernen — die Oberflaeche zeigt das in einem
    sandboxed iframe, aber Skripte und Einbetter sollen gar nicht erst
    mitkommen. Bilder bleiben als Verweis erhalten, werden aber nicht
    automatisch nachgeladen (sonst verraet die Mail das Lesen an den
    Absender)."""
    t = re.sub(r"(?is)<script\b.*?</script>", "", markup)
    t = re.sub(r"(?is)<iframe\b.*?</iframe>", "", t)
    t = re.sub(r"(?is)<object\b.*?</object>", "", t)
    t = re.sub(r"(?is)<embed\b[^>]*>", "", t)
    t = re.sub(r"(?is)<link\b[^>]*>", "", t)
    t = re.sub(r"(?is)<meta\b[^>]*>", "", t)
    t = re.sub(r'''(?i)\son\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)''', "", t)
    t = re.sub(r"(?is)<base\b[^>]*>", "", t)
    # Formulare und Passwortfelder gehoeren nicht in eine gelesene Mail
    t = re.sub(r"(?is)<form\b.*?</form>", "", t)
    return t.strip()


def html_zu_text(markup):
    """HTML in reine Textfassung — fuer den text/plain-Teil beim Senden."""
    t = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", markup or "")
    t = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</tr>|</h[1-6]>", "\n", t)
    t = _TAGAUF.sub("", t)
    return re.sub(r"\n{3,}", "\n\n", htmllib.unescape(t)).strip()


def nachricht_bauen(absender, empfaenger, betreff, html_teil, cc="",
                    antwort_auf="", referenzen=""):
    """multipart/alternative bauen: Leser ohne HTML sehen die Textfassung.

    antwort_auf/referenzen sorgen dafuer, dass die Mail im Thread des
    Empfaengers landet statt als neue Unterhaltung.
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = absender
    msg["To"] = empfaenger
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = betreff
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    if antwort_auf:
        msg["In-Reply-To"] = antwort_auf
        msg["References"] = referenzen or antwort_auf
    msg.attach(MIMEText(html_zu_text(html_teil) or " ", "plain", "utf-8"))
    msg.attach(MIMEText(html_teil or " ", "html", "utf-8"))
    return msg.as_string()
