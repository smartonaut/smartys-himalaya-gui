# -*- coding: utf-8 -*-
"""Einstiegspunkt: python3 -m smartys_mail"""
import argparse

from .server import starten


def main():
    p = argparse.ArgumentParser(
        prog="smartys_mail",
        description="Grafische Oberflaeche fuer himalaya (nur lokal erreichbar).")
    p.add_argument("--port", type=int, default=None,
                   help="Port (Standard 8770, auch SMARTYS_MAIL_PORT)")
    p.add_argument("--bind", default=None,
                   help="Adresse (Standard 127.0.0.1). Aus Sicherheitsgruenden "
                        "nicht auf 0.0.0.0 setzen, solange kein Passwortschutz davor steht.")
    args = p.parse_args()
    starten(port=args.port, bind=args.bind)


if __name__ == "__main__":
    main()
