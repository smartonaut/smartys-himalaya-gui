# -*- coding: utf-8 -*-
"""Desktop-Variante: dieselbe Oberflaeche in einem eigenen Fenster.

Drei Wege, je nach Betriebssystem und installierten Bibliotheken:

1. pywebview — traegt unter Windows (Edge WebView2) und Linux (GTK/Qt).
   Bevorzugt, weil es sich wie ein eigenes Programm anfuehlt.
2. GTK/WebKit — unter Linux ueblicherweise vorhanden, ohne Zusatzpaket.
3. Standardbrowser — letzter Ausweg, damit die Anwendung nie tot dasteht.

Der Server laeuft in einem Hintergrund-Thread; nach aussen verhaelt sich das
Programm wie eine normale Anwendung mit eigenem Fenster.
"""
import os
import socket
import sys
import threading
import time

from . import pfade, server


def _warte_auf_server(port, sekunden=12):
    """Kurz warten, bis der interne Server antwortet."""
    ende = time.time() + sekunden
    while time.time() < ende:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def _server_starten(port):
    threading.Thread(target=server.starten, kwargs={"port": port},
                     daemon=True).start()
    return _warte_auf_server(port)


def _mit_pywebview(url, titel):
    import webview  # noqa: PLC0415
    webview.create_window(titel, url, width=1280, height=820, min_size=(900, 600))
    webview.start()
    return True


def _mit_gtk(url, titel):
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gtk, WebKit2
    except (ImportError, ValueError):
        return False

    fenster = Gtk.Window(title=titel)
    fenster.set_default_size(1280, 820)
    fenster.set_icon_name("internet-mail")
    fenster.connect("destroy", lambda *_: Gtk.main_quit())

    web = WebKit2.WebView()
    einstellungen = web.get_settings()
    # Kein Kontextmenue des Browsers, kein Entwicklerwerkzeug im Alltag
    einstellungen.set_property("enable-developer-extras", False)
    einstellungen.set_property("enable-plugins", False)
    web.load_uri(url)
    fenster.add(web)
    fenster.show_all()
    # Nach vorn holen: sonst startet das Programm unbemerkt hinter anderen
    # Fenstern und der Nutzer denkt, es sei nicht gestartet.
    fenster.present()
    fenster.set_keep_above(True)
    from gi.repository import GLib
    GLib.timeout_add_seconds(2, lambda: (fenster.set_keep_above(False), False)[1])

    def tastenkürzel(widget, event):
        # F5 aktualisiert, Strg+Q beendet
        from gi.repository import Gdk
        zustand = event.state & Gtk.accelerator_get_default_mod_mask()
        if event.keyval == Gdk.KEY_F5:
            web.reload()
            return True
        if event.keyval in (Gdk.KEY_q, Gdk.KEY_Q) and zustand == Gdk.ModifierType.CONTROL_MASK:
            Gtk.main_quit()
            return True
        return False

    fenster.connect("key-press-event", tastenkürzel)
    Gtk.main()
    return True


def starten(port=8771):
    titel = "Smartys Himalaya GUI"
    url = f"http://127.0.0.1:{port}/"
    if not _server_starten(port):
        print(f"Der interne Server antwortet nicht auf Port {port}.", file=sys.stderr)
        return 1

    # Reihenfolge: pywebview (ueberall), dann GTK (Linux), dann Browser
    try:
        return 0 if _mit_pywebview(url, titel) else 1
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        print(f"pywebview nicht nutzbar ({e}) — versuche GTK.", file=sys.stderr)

    if not pfade.WINDOWS:
        try:
            if _mit_gtk(url, titel):
                return 0
        except Exception as e:  # noqa: BLE001
            print(f"GTK nicht nutzbar ({e}) — oeffne den Browser.", file=sys.stderr)

    import webbrowser
    print(f"Oeffne die Oberflaeche im Browser: {url}")
    webbrowser.open(url)
    # Ohne eigenes Fenster muss der Prozess leben bleiben, sonst ist der
    # Server sofort weg.
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return 0


def main():
    import argparse
    p = argparse.ArgumentParser(prog="smartys-himalaya-gui-desktop",
                                description="Smartys Himalaya GUI als eigenes Fenster")
    p.add_argument("--port", type=int, default=int(os.environ.get("SMARTYS_MAIL_PORT", "8771")))
    args = p.parse_args()
    sys.exit(starten(port=args.port))


if __name__ == "__main__":
    main()
