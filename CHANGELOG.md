# Changelog

Alle nennenswerten Änderungen an der Smartys Himalaya GUI. Format orientiert
an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) und
[Semantic Versioning](https://semver.org/lang/de/).

## [0.4.0] — 2026-10-26

Schwerpunkt: Schreiben und Lesen in fremden Sprachen.

### Neu

- **Oberfläche auf Deutsch und Englisch.** Umschaltbar im Zahnrad unter
  „Sprache der Oberfläche“; die Wahl bleibt gespeichert. Übersetzt wird nur
  die Bedienung — Absender, Betreff, Mailinhalt und Signaturen bleiben
  unangetastet.
- **Rechtschreibprüfung beim Verfassen.** Betreff und Textfeld prüfen mit,
  falsch geschriebene Wörter werden unterstrichen. Im Fenster-Programm wird
  die Prüfung von WebKitGTK ausdrücklich eingeschaltet (braucht
  `hunspell-de` bzw. `hunspell-en`); unter Windows prüft WebView2 von selbst.
  Die Adressfelder sind bewusst ausgenommen.
- **Übersetzer.** In der Nachrichtenansicht gibt es einen Knopf „⇄ Übersetzen“.
  Zwei Wege, beide ohne Zusatzpakete:
  * **ollama** — lokales Sprachmodell, der Text bleibt auf dem Rechner,
  * **LibreTranslate** — selbst betriebener oder fremder Dienst.
  Einzustellen im Zahnrad oben links unter „Übersetzer“.

### Behoben

- Ohne eingerichteten Übersetzer kommt ein verständlicher Hinweis statt einer
  Fehlermeldung aus dem Nichts.
- Sehr lange Nachrichten werden bei 12.000 Zeichen gekürzt, mit Hinweis im
  Ergebnis — statt in eine Zeitüberschreitung zu laufen.

## [0.3.1] — 2026-10-26

Schwerpunkt: Löschen schlug bei manchen Anbietern fehl.

### Behoben

- **„Löschen" scheiterte mit „Destination mailbox does not exist".** himalaya
  verschiebt beim Löschen in den in seiner Konfiguration hinterlegten
  Papierkorb. Heißt der Ordner auf dem Server anders (z. B. `Deleted Items`
  statt `Trash`), blieb die Mail liegen und die Oberfläche zeigte nur den
  rohen Fehlertext.
  Jetzt löst die GUI den Papierkorb selbst auf: zuerst der Alias aus der
  Konfiguration, danach die üblichen Schreibweisen (`Deleted Items`,
  `Papierkorb`, `Trash`, `Gelöschte Elemente`, `Deleted Messages`,
  `INBOX.Trash`, `Deleted`). Findet sich keiner, kommt ein verständlicher
  Hinweis auf `mailbox.alias.trash` statt des Rohfehlers.
- Betrifft Fenster- und Web-Variante gleichermaßen (gemeinsamer Code).

## [0.3.0] — 2026-10-26

Schwerpunkt: Die HTML-Anzeige war zwar da, aber unbrauchbar.

### Behoben

- **HTML-Mails wurden nur als schmaler Streifen angezeigt.** Der Rahmen konnte
  seine Höhe nicht messen (`sandbox` ohne `allow-same-origin` gibt
  `contentDocument` nicht heraus), also blieb er bei den 180 px aus dem
  Stylesheet. Jetzt feste Höhe von 72 % der Fensterhöhe mit eigenem
  Scrollbalken — die automatische Nachmessung war unzuverlässig (3.829 px für
  269 Zeichen Text) und ist wieder entfernt.
- Die Einstellung stand auf `ssh` mit dem eigenen Rechner als Ziel, sodass
  himalaya per SSH auf sich selbst aufgerufen wurde. Jetzt `lokal`.

### Neu

- **Schalter „Bilder aus Mails laden"** in den Einstellungen (Zahnrad neben
  „Konten"). Standard: aus. Der Hinweis darunter erklärt den Grund.
- **HTML-Beispielmail im Demo-Modus.** Ohne sie ließ sich die HTML-Anzeige
  gar nicht prüfen — der Demo-Bestand hatte nur reine Textmails.

---

## [0.2.0] — 2026-10-25

Schwerpunkt: Mails werden so angezeigt, wie sie gedacht sind.

### Neu

- **HTML-Mails werden korrekt dargestellt.** Bisher kam nur der reine
  Text-Teil an — Tabellen, Hervorhebungen, Formatierungen und Links fehlten.
  Jetzt wird die vollständige Nachricht geholt (`--raw`) und der HTML-Teil
  angezeigt, in einem eigenen Rahmen mit eigener Schrift und Zeilenhöhe.
- **Links in Mails sind klickbar** und öffnen im Standardbrowser, nicht im
  Programmfenster.
- **Betreff und Absender lesbar.** Bei vollständig geholten Mails kommen sie
  kodiert an (`=?UTF-8?B?…`); das wird aufgelöst.
- **Fernbetrieb:** Die Oberfläche kann den Dienst eines anderen Rechners
  anzeigen, ohne dort etwas zu installieren. Einstellung über
  `SMARTYS_MAIL_REMOTE`; ohne diese Variable startet wie bisher ein eigener
  Server.

### Sicherheit

- **Skripte in Mails werden entfernt**, bevor sie den Rahmen erreichen —
  zusätzlich zum `sandbox`-Modus, der ohne `allow-scripts` läuft.
- **Externe Bilder sind blockiert.** Ein geladenes Zählpixel verrät dem
  Absender, dass und wann die Mail geöffnet wurde. Das betrifft vor allem
  Newsletter. Eingebettete Bilder werden weiterhin angezeigt.
- Formulare und Passwortfelder aus Mails werden nicht mitgerendert.

### Behoben

- Der Text-Teil einer Mail wurde aus dem HTML erzeugt, wenn ein
  `text/plain`-Teil vorhanden war — Ergebnis waren bis zu 49.000 Zeichen
  statt der tatsächlichen 7.400.
- Die Oberfläche zeigt HTML und Text nie doppelt untereinander.

### Hinweis

Bilder aus Newslettern bleiben durch die Sicherheitsregel leer. Ein
Umschalter „Bilder laden" pro Mail ist vorgesehen, aber noch nicht gebaut.

---

## [0.1.0] — 2026-10-12

Erste veröffentlichte Fassung.

### Neu

- Fenster-Variante (GTK/WebKit, unter Windows Edge WebView2) und
  Web-Oberfläche auf Port 8770 aus einer Codebasis
- Postfachliste mit Absender, Betreff, Zeitangabe in Stufen (heute, gestern,
  Wochentag, Datum), Ordner-Anzeigenamen auf Deutsch
- Mailansicht mit Metadaten, Anhängen und Antworten/Weiterleiten
- Verfassen mit Signaturgruppen
- Konten anlegen mit Anbieter-Erkennung
- Einrichtungsassistent beim ersten Start
- Demo-Modus mit Beispieldaten
- Logo und Fenstersymbol in allen Größen, Eintrag im Anwendungsmenü
