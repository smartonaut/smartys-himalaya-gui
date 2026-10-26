/* -*- coding: utf-8 -*- */
/* Sprachumschaltung Deutsch / Englisch.
 *
 * Deutsch ist die Ausgangssprache und steht als Schluessel in der Tabelle.
 * Fehlt eine Uebersetzung, bleibt der deutsche Text stehen — es kann also
 * nie etwas leer werden.
 *
 * Grundsatz: uebersetzt wird ausschliesslich die Bedienoberflaeche. Absender,
 * Betreff, Mailinhalt und die Signatur des Nutzers werden NICHT angefasst;
 * ui() wird nur auf Bedienelemente angewandt, nie auf Mailinhalte.
 */
var HG_SPRACHE_KEY = 'hg-sprache';

function hgSprache(){
  try { return localStorage.getItem(HG_SPRACHE_KEY) === 'en' ? 'en' : 'de'; }
  catch(e){ return 'de'; }
}
function hgIstEnglisch(){ return hgSprache() === 'en'; }
function hgSpracheSetzen(code){
  try { localStorage.setItem(HG_SPRACHE_KEY, code === 'en' ? 'en' : 'de'); } catch(e){}
  location.reload();
}
function hgDatumLocale(){ return hgIstEnglisch() ? 'en-GB' : 'de-DE'; }

var HG_EN = {
  /* --- Rahmen (index.html) --- */
  'Fehler: ': 'Error: ',
  'Standardkonto': 'Default account',
  'Konten': 'Accounts',
  'Posteingang': 'Inbox',
  '+ Neu': '+ New',
  'Suchen…': 'Search…',
  'Konto wählen': 'Choose an account',
  'Signatur bearbeiten': 'Edit signature',
  'Wo läuft himalaya?': 'Where does himalaya run?',
  'lade…': 'loading…',
  'kopiert': 'copied',
  '(unbekannt)': '(unknown)',
  '(ohne Betreff)': '(no subject)',
  'gestern': 'yesterday',
  ' Uhr': '',
  'Keine Nachrichten': 'No messages',
  'Nichts gefunden': 'Nothing found',
  'Gelöscht.': 'Deleted.',
  'Nachricht löschen?': 'Delete this message?',
  'Erst ein Konto wählen': 'Choose an account first',
  'Adresse (https://…):': 'Address (https://…):',

  /* --- Einstellungen --- */
  'Die Oberfläche kann himalaya auf diesem Rechner benutzen — oder auf einem anderen, auf dem deine Postfächer eingerichtet sind.': 'The interface can use himalaya on this computer — or on another one where your mailboxes are set up.',
  'Im zweiten Fall bleiben die Zugangsdaten dort, und hier wird nur ein SSH-Zugang gebraucht.': 'In the second case the credentials stay there and only an SSH account is needed here.',
  'Auf diesem Rechner': 'On this computer',
  'Auf einem anderen Rechner (SSH)': 'On another computer (SSH)',
  'benutzer@rechner, z.B. benutzer@192.168.1.50': 'user@host, e.g. user@192.168.1.50',
  'Pfad zu himalaya dort (Standard: himalaya)': 'Path to himalaya there (default: himalaya)',
  'Der öffentliche SSH-Schlüssel dieses Rechners muss dort hinterlegt sein — sonst kommt keine Verbindung zustande.': "This computer's public SSH key must be stored there — otherwise no connection can be made.",
  'Bilder aus Mails laden': 'Load images in mails',
  'Aus: fremde Bilder bleiben gesperrt. Ein eingebundenes Zählpixel verrät dem Absender sonst, dass und wann du die Mail geöffnet hast — bei Newslettern passiert genau das.': 'Off: external images stay blocked. Otherwise an embedded tracking pixel tells the sender that and when you opened the mail — which is exactly what newsletters do.',
  'Übersetzer': 'Translator',
  'Damit lässt sich eine Nachricht auf Knopfdruck übersetzen. Ein lokales Sprachmodell (ollama) behält den Text auf dem Rechner; ein LibreTranslate-Dienst schickt ihn an den eingetragenen Server.': 'Translate a message at the touch of a button. A local language model (ollama) keeps the text on this computer; a LibreTranslate service sends it to the server you enter.',
  'Sprache der Oberfläche': 'Interface language',
  'Deutsch': 'German',
  'Englisch': 'English',
  '— aus —': '— off —',
  'ollama (lokales Sprachmodell)': 'ollama (local language model)',
  'Adresse, z.B. http://127.0.0.1:11434': 'Address, e.g. http://127.0.0.1:11434',
  'Modell (nur ollama), z.B. qwen2.5:7b': 'Model (ollama only), e.g. qwen2.5:7b',
  'Speichern und prüfen': 'Save and test',
  'prüfe…': 'checking…',
  'Gespeichert, aber keine Verbindung: ': 'Saved, but no connection: ',

  /* --- Konto einrichten --- */
  'Konto einrichten': 'Set up account',
  'Trag deine E-Mail-Adresse und das Passwort ein — die Servereinstellungen erkennt die App meist selbst. Nichts hiervon verlässt deinen Rechner.': 'Enter your email address and password — the app usually detects the server settings itself. None of this leaves your computer.',
  'E-Mail-Adresse': 'Email address',
  'Passwort': 'Password',
  'Anzeigename (optional)': 'Display name (optional)',
  'Server selbst eintragen': 'Enter server manually',
  'IMAP-Server (z.B. imap.gmx.net)': 'IMAP server (e.g. imap.gmx.net)',
  'IMAP-Port (993)': 'IMAP port (993)',
  'SMTP-Server (z.B. mail.gmx.net)': 'SMTP server (e.g. mail.gmx.net)',
  'SMTP-Port (465)': 'SMTP port (465)',
  'Konto hinzufügen': 'Add account',
  'E-Mail und Passwort sind nötig.': 'Email and password are required.',
  'prüfe Zugangsdaten…': 'checking credentials…',

  /* --- Nachrichtenansicht --- */
  'Antworten': 'Reply',
  'Antworten (A)': 'Reply (A)',
  'Weiterleiten': 'Forward',
  'Weiterleiten (W)': 'Forward (W)',
  'Gelesen': 'Read',
  'Als gelesen oder ungelesen markieren': 'Mark as read or unread',
  'Löschen': 'Delete',
  'In den Papierkorb (Entf)': 'Move to trash (Del)',
  'Übersetzen': 'Translate',
  'Nachricht übersetzen': 'Translate message',
  'Anhänge': 'Attachments',
  'Anhang ': 'Attachment ',
  'Adresse kopieren': 'Copy address',
  ' · Suche': ' · Search',

  /* --- Verfassen --- */
  'Neue Nachricht': 'New message',
  'An (mehrere mit Komma trennen)': 'To (separate addresses with commas)',
  'Cc (optional)': 'Cc (optional)',
  'Betreff': 'Subject',
  'Fett': 'Bold',
  'Kursiv': 'Italic',
  'Unterstrichen': 'Underline',
  'Durchgestrichen': 'Strikethrough',
  'Größe': 'Size',
  'klein': 'small',
  'normal': 'normal',
  'groß': 'large',
  'sehr groß': 'very large',
  'Schrift': 'Font',
  'Schriftfarbe': 'Text colour',
  'Textmarker': 'Highlight',
  'Aufzählung': 'Bulleted list',
  'Nummerierung': 'Numbered list',
  'Formatierung entfernen': 'Remove formatting',
  'Senden': 'Send',
  'sende…': 'sending…',
  'Gesendet.': 'Sent.',
  'Empfänger fehlt': 'Recipient missing',
  '----- Ursprüngliche Nachricht -----': '----- Original message -----',

  /* --- Signaturen --- */
  'Signaturen': 'Signatures',
  'Eine Signatur gilt für alle Konten einer Gruppe — die Gruppen ergeben sich aus dem Namensanfang (dekohuwelen-*, smartystech-* …).': 'One signature applies to all accounts in a group — groups are formed from the name prefix (dekohuwelen-*, smartystech-* …).',
  'Keine Konten gefunden.': 'No accounts found.',
  'Signatur gesetzt': 'Signature set',
  'keine Signatur': 'no signature',
  ' Konto: ': ' account: ',
  ' Konten: ': ' accounts: ',
  'Signatur: ': 'Signature: ',
  'Gilt für: ': 'Applies to: ',
  '. Feld leeren und speichern = keine Signatur für diese Gruppe.': '. Clear the field and save = no signature for this group.',
  'Speichern': 'Save',
  'Vorschau': 'Preview',
  'speichere…': 'saving…',
  'Gespeichert — gilt für alle Konten dieser Gruppe.': 'Saved — applies to all accounts in this group.',

  /* --- Übersetzungskasten --- */
  'Kein Text zum Übersetzen gefunden.': 'No text found to translate.',
  'übersetze…': 'translating…',
  'Der Dienst antwortet nicht.': 'The service is not responding.',
  'Übersetzung': 'Translation',
  'schließen': 'close'
};

/* Nach Laenge absteigend ersetzen: sonst wuerde "Konto" das laengere
   "Konten" zerschneiden. */
var HG_PAARE = Object.keys(HG_EN)
  .map(function(de){ return [de, HG_EN[de]]; })
  .sort(function(a, b){ return b[0].length - a[0].length; });

function t(text){
  if(!hgIstEnglisch()) return text;
  var s = String(text == null ? '' : text);
  return HG_EN[s] !== undefined ? HG_EN[s] : s;
}

function ui(html){
  if(!hgIstEnglisch()) return html;
  var s = String(html == null ? '' : html);
  for(var i = 0; i < HG_PAARE.length; i++){
    var de = HG_PAARE[i][0];
    if(s.indexOf(de) !== -1) s = s.split(de).join(HG_PAARE[i][1]);
  }
  return s;
}

/* Feste Texte aus index.html uebersetzen (die stehen nicht in app.js). */
function hgRahmenUebersetzen(){
  if(!hgIstEnglisch()) return;
  document.documentElement.lang = 'en';
  var kopf = document.querySelectorAll('.kopf .markentext');
  for(var i = 0; i < kopf.length; i++) kopf[i].textContent = t('Konten');
  var liste = document.getElementById('listenkopf');
  if(liste && liste.textContent.trim() === 'Posteingang') liste.textContent = 'Inbox';
  var neu = document.querySelectorAll('.kopf .neu');
  for(var j = 0; j < neu.length; j++){
    if(neu[j].textContent.trim() === '+ Neu') neu[j].textContent = '+ New';
  }
  var suche = document.getElementById('suche');
  if(suche) suche.placeholder = t('Suchen…');
  var titel = document.querySelectorAll('[title]');
  for(var k = 0; k < titel.length; k++){
    var tt = titel[k].getAttribute('title');
    if(HG_EN[tt]) titel[k].setAttribute('title', HG_EN[tt]);
  }
}

document.addEventListener('DOMContentLoaded', hgRahmenUebersetzen);
