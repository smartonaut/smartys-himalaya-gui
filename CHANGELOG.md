# Changelog

Alle nennenswerten Änderungen an der Smartys Himalaya GUI. Format orientiert
an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) und
[Semantic Versioning](https://semver.org/lang/de/).

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
