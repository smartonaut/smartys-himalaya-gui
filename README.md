# Smartys Himalaya GUI

Eine grafische Oberfläche für [himalaya](https://github.com/pimalaya/himalaya) —
den CLI-Mail-Client, der IMAP, SMTP, JMAP, Gmail, Microsoft Graph und Maildir
beherrscht.

## Warum es das gibt

himalaya ist bewusst nur eine Engine: „a simple CLI API that can be used
directly from the terminal, from scripts, from UIs". Eine UI dazu existiert
nicht — das einzige `himalaya-gui` auf GitHub ist ein leeres
eframe-Template von 2023, nach zehn Tagen aufgegeben. Alles andere sind
Textoberflächen für Vim, Emacs oder das Terminal.

Wer viele Postfächer verwaltet, stolpert außerdem über ein Problem, das
Thunderbird und Claws Mail nicht lösen: Sobald unterschiedliche
Anmeldemethoden im Spiel sind — klassische Passwörter, App-Passwörter,
OAuth2 — brauchen diese Clients die Zugangsdaten im Klartext. himalaya holt
sie zur Laufzeit aus seiner Konfiguration. Diese Oberfläche nutzt das: Sie
spricht nie selbst mit einem Mailserver, sondern ruft himalaya auf.

## Funktionen

- **Alle himalaya-Konten** in einer Oberfläche, inklusive OAuth2 und
  App-Passwörtern — ohne dass Zugangsdaten im Client liegen
- **Ordner-Navigation** je Konto (Eingang, Gesendet, Entwürfe, Papierkorb …)
- **Nachrichten lesen**: HTML-Mails werden in lesbaren Text gewandelt,
  quoted-printable dekodiert
- **Anhänge** herunterladen
- **Antworten und Weiterleiten** mit korrektem Threading
  (`In-Reply-To` / `References`)
- **Neue Nachricht** mit formatiertem Text: fett, kursiv, unterstrichen,
  durchgestrichen, Schriftgröße, Schriftart, Schriftfarbe, Textmarker,
  Listen, Links
- **Signaturen pro Gruppe**: alle Konten eines Präfixes (`firma-*`) teilen
  eine Signatur; Ausnahmen pro Konto sind vorgesehen
- **Suche** über Betreff und Absender
- **Löschen**, gelesen/ungelesen umschalten
- **Gesendet-Ordner** wird automatisch erkannt (`Sent`, `Sent Items`,
  `Gesendet` …)
- Läuft als Dienst, startet mit dem Benutzer, lauscht **nur auf 127.0.0.1**

## Installation

Voraussetzungen: Python 3.11+ (wegen `tomllib`) und ein eingerichtetes
himalaya mit mindestens einem Konto.

```bash
git clone https://github.com/smartonaut/smartys-himalaya-gui.git
cd smartys-himalaya-gui
python3 -m smartys_mail
```

Dann <http://127.0.0.1:8770> öffnen.

Abhängigkeiten: keine. Nur die Python-Standardbibliothek.

### Als Dienst einrichten

```bash
mkdir -p ~/.config/systemd/user
cp systemd/smartys-himalaya-gui.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now smartys-himalaya-gui.service
```

## Konfiguration

### himalaya

Konten werden ausschließlich in `~/.config/himalaya/config.toml` gepflegt.
Diese Oberfläche liest daraus nur die Absenderadressen — niemals Passwörter.
Neue Konten erscheinen nach einem Neustart des Dienstes automatisch.

### Signaturen

Liegen in `signaturen.json` neben dem Programm (Pfad über die Umgebungsvariable
`SMARTYS_MAIL_SIG` überschreibbar) und werden über die Oberfläche gepflegt —
Gruppen-Signaturen, Konto-Ausnahmen, mit Vorschau.

```json
{
  "gruppen": {
    "firma": "<p><b>Vorname Nachname</b><br>firma.de</p>"
  },
  "ausnahmen": {}
}
```

Die Gruppe eines Kontos ergibt sich aus dem Teil vor dem ersten Bindestrich:
`firma-buchhaltung` gehört zur Gruppe `firma`.

## Sicherheit

- Der Server bindet ausschließlich an `127.0.0.1` — kein Zugriff aus dem Netz
- Er kennt keine Passwörter: die Anmeldung erledigt himalaya
- HTML aus Mails wird **nicht** gerendert, sondern in Text gewandelt; damit
  sind auch Tracking-Pixel und eingebettete Skripte wirkungslos
- Beim Senden wird der Text als Argument übergeben, nie durch eine Shell
  geleitet

## Grenzen

Ehrlich benannt, damit niemand Überraschungen erlebt:

- **Anhänge senden** ist noch nicht umgesetzt (Empfangen und Herunterladen geht)
- **Entwürfe** werden nicht zwischengespeichert — ein geschlossener Tab
  verwirft den Text
- Kein Adressbuch, kein Kalender (dafür gibt es `cardamum` und `calendula`
  aus derselben Schmiede)
- Kein Push: neue Mails erscheinen beim Neuladen, nicht von selbst

## Lizenz

MIT — siehe [LICENSE](LICENSE).
