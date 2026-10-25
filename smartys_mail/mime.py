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
