#!/bin/sh
# Baut das RPM-Paket (SUSE, Red Hat, Fedora, openSUSE).
# Aufruf: ./packaging/build-rpm.sh
# Setzt rpmbuild voraus (Paket "rpm" bzw. "rpm-build").
set -eu

HIER=$(cd "$(dirname "$0")/.." && pwd)
VERSION=$(sed -n 's/^Version:[[:space:]]*//p' "$HIER/debian/control" | head -1)
NAME=smartys-himalaya-gui

if [ -z "$VERSION" ]; then
    echo "Version nicht in debian/control gefunden" >&2
    exit 1
fi

command -v rpmbuild >/dev/null 2>&1 || {
    echo "rpmbuild fehlt. Installieren: apt install rpm / dnf install rpm-build" >&2
    exit 1
}

TOP=$(mktemp -d)
trap 'rm -rf "$TOP"' EXIT
mkdir -p "$TOP/BUILD" "$TOP/RPMS" "$TOP/SOURCES" "$TOP/SPECS" "$TOP/SRPMS"

# Quellbaum fuer Source0: nur Programm und Anzeigedaten, keine Pakete/Repos
STAGE="$TOP/stage/$NAME-$VERSION"
mkdir -p "$STAGE"
cp -r "$HIER/smartys_mail" "$STAGE/"
cp -r "$HIER/assets" "$STAGE/"
cp "$HIER/README.md" "$HIER/CHANGELOG.md" "$HIER/LICENSE" "$STAGE/" 2>/dev/null || true
find "$STAGE" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name '*.pyc' -delete 2>/dev/null || true

tar czf "$TOP/SOURCES/$NAME-$VERSION.tar.gz" -C "$TOP/stage" "$NAME-$VERSION"
cp "$HIER/packaging/$NAME.rpm.spec" "$TOP/SPECS/"

echo "Baue $NAME $VERSION"
rpmbuild -bb --define "_topdir $TOP" --define "_version $VERSION" \
    "$TOP/SPECS/$NAME.rpm.spec"

RPM=$(find "$TOP/RPMS" -name '*.rpm' | head -1)
[ -n "$RPM" ] || { echo "kein RPM erzeugt" >&2; exit 1; }
cp "$RPM" "$HIER/packaging/"

echo
echo "Fertig: $HIER/packaging/$(basename "$RPM")"
echo "--- Metadaten ---"
# Als normaler Benutzer darf rpm keine Systemdatenbank oeffnen; die Abfrage
# einer Paketdatei klappt aber auch ohne - Fehler trotzdem nicht eskalieren.
rpm -qip "$HIER/packaging/$(basename "$RPM")" 2>/dev/null | head -12 || true
echo "--- Inhalt ---"
rpm -qlp "$HIER/packaging/$(basename "$RPM")" 2>/dev/null | head -20 || true
