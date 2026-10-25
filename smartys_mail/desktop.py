# -*- coding: utf-8 -*-
"""Desktop-Variante: dieselbe Oberflaeche in einem eigenen Fenster.

Statt eines Browsers wird ein GTK-Fenster mit WebKit geoeffnet. Das Programm
startet den internen Server im Hintergrund und laedt die Seite — nach aussen
verhaelt es sich wie eine normale Anwendung mit eigenem Fenster und Icon.

GTK/WebKit sind auf Debian und Ubuntu ueblicherweise vorhanden; das DEB-Paket
zieht sie als Abhaengigkeit nach. Fehlen sie, bleibt die Web-Variante nutzbar.
"""
import os
import sys
import threading
import time

from . import server


def _warte_auf_server(port, sekunden=10):
    """Kurz warten, bis der interne Server antwortet."""
    import socket
    ende = time.time() + sekunden
    while time.time() < ende:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def starten(port=8771):
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gtk, WebKit2
    except (ImportError, ValueError):
        print("GTK/WebKit fehlen. Installation:", file=sys.stderr)
        print("  sudo apt install python3-gi gir1.2-webkit2-4.1", file=sys.stderr)
        print(f"Alternativ im Browser: http://127.0.0.1:{port}", file=sys.stderr)
        return 2

    threading.Thread(target=server.starten, kwargs={"port": port},
                     daemon=True).start()
    _warte_auf_server(port)

    fenster = Gtk.Window(title="Smartys Himalaya GUI")
    fenster.set_default_size(1280, 820)
    fenster.set_icon_name("internet-mail")

    def schliessen(*_):
        Gtk.main_quit()

    fenster.connect("destroy", schliessen)

    web = WebKit2.WebView()
    einstellungen = web.get_settings()
    # Kein Kontextmenue des Browsers, kein Entwicklerwerkzeug im Alltag
    einstellungen.set_property("enable-developer-extras", False)
    einstellungen.set_property("enable-plugins", False)
    web.load_uri(f"http://127.0.0.1:{port}/")
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
