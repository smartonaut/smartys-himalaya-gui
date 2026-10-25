#!/bin/sh
# Baut das Debian-Paket. Aufruf: ./packaging/build-deb.sh
set -eu

HIER=$(cd "$(dirname "$0")/.." && pwd)
VERSION=$(sed -n 's/^Version: //p' "$HIER/debian/control")
NAME=smartys-himalaya-gui
BAU=$(mktemp -d)
WURZEL="$BAU/$NAME-$VERSION"

echo "Baue $NAME $VERSION in $WURZEL"
mkdir -p "$WURZEL/DEBIAN" \
         "$WURZEL/usr/lib/python3/dist-packages/smartys_mail" \
         "$WURZEL/usr/bin" \
         "$WURZEL/usr/share/applications" \
         "$WURZEL/usr/share/icons/hicolor/scalable/apps" \
         "$WURZEL/usr/lib/systemd/user"

# Programmdateien (nur das Paket, keine persoenlichen Daten)
cp -r "$HIER/smartys_mail/." "$WURZEL/usr/lib/python3/dist-packages/smartys_mail/"
find "$WURZEL/usr/lib/python3/dist-packages" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

cp "$HIER/debian/control" "$WURZEL/DEBIAN/control"
[ -f "$HIER/debian/postinst" ] && cp "$HIER/debian/postinst" "$WURZEL/DEBIAN/postinst"
[ -f "$HIER/debian/prerm" ] && cp "$HIER/debian/prerm" "$WURZEL/DEBIAN/prerm"
chmod 755 "$WURZEL/DEBIAN"/*inst "$WURZEL/DEBIAN"/prerm 2>/dev/null || true

# Startbefehle: einmal als Fenster, einmal als Web-Dienst
cat > "$WURZEL/usr/bin/smartys-himalaya-gui" <<'EOF'
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages")
from smartys_mail.desktop import main
main()
EOF

cat > "$WURZEL/usr/bin/smartys-himalaya-gui-web" <<'EOF'
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages")
from smartys_mail.__main__ import main
main()
EOF
chmod 755 "$WURZEL/usr/bin/smartys-himalaya-gui" "$WURZEL/usr/bin/smartys-himalaya-gui-web"

# Desktop-Eintrag (Fenster-Variante)
cat > "$WURZEL/usr/share/applications/smartys-himalaya-gui.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Smartys Himalaya GUI
GenericName=E-Mail
Comment=E-Mail ueber himalaya verwalten
Exec=smartys-himalaya-gui
Icon=smartys-himalaya-gui
Terminal=false
Categories=Network;Email;
Keywords=mail;email;imap;himalaya;
StartupWMClass=smartys-himalaya-gui
EOF

# Symbol: schlichte Sprechblase
cat > "$WURZEL/usr/share/icons/hicolor/scalable/apps/smartys-himalaya-gui.svg" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" rx="14" fill="#0b0e14"/>
  <rect x="10" y="17" width="44" height="30" rx="4" fill="none" stroke="#ffc94d" stroke-width="3"/>
  <path d="M11 20 L32 36 L53 20" fill="none" stroke="#ffc94d" stroke-width="3" stroke-linecap="round"/>
  <circle cx="46" cy="45" r="7" fill="#ffc94d"/>
</svg>
EOF

# Systemd-Dienst fuer die Web-Variante
cat > "$WURZEL/usr/lib/systemd/user/smartys-himalaya-gui-web.service" <<'EOF'
[Unit]
Description=Smartys Himalaya GUI (Web-Oberflaeche)
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/smartys-himalaya-gui-web
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

dpkg-deb --root-owner-group --build "$WURZEL" "$HIER/packaging/$NAME"_"$VERSION"_all.deb
echo
echo "Fertig: $HIER/packaging/${NAME}_${VERSION}_all.deb"
dpkg-deb --info "$HIER/packaging/$NAME"_"$VERSION"_all.deb | head -12
rm -rf "$BAU"
