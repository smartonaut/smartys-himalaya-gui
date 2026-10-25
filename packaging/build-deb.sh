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

# Symbol: goldener Briefumschlag mit Berg (FLUX-Rendering, alle Groessen)
for groesse in 16 24 32 48 64 128 256; do
    mkdir -p "$WURZEL/usr/share/icons/hicolor/${groesse}x${groesse}/apps"
done
cp "$HIER/assets/icons/logo_64.png"   "$WURZEL/usr/share/icons/hicolor/64x64/apps/smartys-himalaya-gui.png"
cp "$HIER/assets/icons/logo_128.png"  "$WURZEL/usr/share/icons/hicolor/128x128/apps/smartys-himalaya-gui.png"
cp "$HIER/assets/icons/logo_256.png"  "$WURZEL/usr/share/icons/hicolor/256x256/apps/smartys-himalaya-gui.png"
mkdir -p "$WURZEL/usr/share/icons/hicolor/scalable/apps"
cp "$HIER/assets/icons/smartys-himalaya-gui.svg" "$WURZEL/usr/share/icons/hicolor/scalable/apps/"

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
