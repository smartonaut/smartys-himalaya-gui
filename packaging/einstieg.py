# -*- coding: utf-8 -*-
"""Einstiegspunkt fuer die gepackte Windows-Anwendung.

Startet bewusst die Fenster-Variante: Wer eine .exe doppelklickt, erwartet
ein Fenster, keinen Server im Hintergrund. __main__.py waere die
Web-Variante und wuerde nur still einen Port belegen.
"""
import sys

from smartys_mail.desktop import main

if __name__ == "__main__":
    main()
