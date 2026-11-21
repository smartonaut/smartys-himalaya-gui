# Changelog

Alle nennenswerten Änderungen an der Smartys Himalaya GUI. Format orientiert
an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/) und
[Semantic Versioning](https://semver.org/lang/de/).

## [0.5.0] — 2026-11-21

Schwerpunkt: die Kontenleiste. Mit 32 Postfaechern war eine alphabetische Liste
technischer Kontonamen nicht mehr benutzbar.

### Neu

- **Konten sind gruppiert.** Ueberschrift mit Trennlinie je Gruppe, abgeleitet
  aus der Adressdomain — neue Konten landen automatisch richtig, nichts zu
  pflegen: `dekojuwelen.de` → Dekojuwelen, `smartys.tech` und `smarty.tips` →
  Smartys Tech, `sk-ft.de` und `sk-smarty.de` → Job / SK, alles andere → Privat.
- **Anzeigename und Adresse stehen in der Leiste.** Oben der Name, darunter
  klein die Adresse — sie sagt, wer wirklich schreibt.
- **Konten lassen sich umbenennen.** Stift rechts in der Zeile, Enter speichert,
  Escape bricht ab. Geaendert wird nur `display-name` in der `config.toml`
  (mit Sicherung daneben); der Kontoname als Schluessel bleibt unangetastet,
  damit Signatur-Gruppen und Mailbox-Aliase gueltig bleiben.
- Innerhalb einer Gruppe steht das Standardkonto oben, danach alphabetisch nach
  Anzeigename.

### Behoben

- Der Stern fuer das Standardkonto hing zwischen Name und Adresse statt auf der
  Namenszeile.

## [0.4.1] — 2026-11-01

Schwerpunkt: Gelesen-Markierung reparieren.

### Behoben

- **Gelesene Mails sprangen nach einem Kontowechsel zurück auf ungelesen.**
  Die Oberfläche rief `himalaya flag add ... seen <id>` auf — himalaya 2.x
  verlangt das Flag aber als Option (`--flag seen`). Jeder Aufruf scheiterte
  stillschweigend, die Mail blieb serverseitig ungelesen und erschien nach dem
  Neuladen wieder mit Punkt.
- **Der Knopf „Gelesen" konnte nur lesen, nie ungelesen machen.** Er schickte
  keinen Zielzustand, der Server probierte „add", was bei IMAP auf ein bereits
  gesetztes Flag folgenlos bleibt (idempotent) — der „remove"-Zweig war damit
  unerreichbar. Jetzt schickt die Oberfläche den Zielzustand (`gelesen: true`
  oder `false`), und der Server setzt genau diesen.
- **Nur an `\Seen` erkennbar, ob eine Mail gelesen ist.** Die Liste stufte
  jede Mail mit *irgendeinem* Flag als gelesen ein; eine markierte, aber
  ungelesene Nachricht (`\Flagged` ohne `\Seen`) erschien dadurch falsch.

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
