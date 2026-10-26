# -*- rpm-spec -*-
# RPM-Spec fuer Smartys Himalaya GUI (SUSE, Red Hat, Fedora, openSUSE).
#
# Bewusst KEINE Installation nach %{python3_sitelib}: der Pfad unterscheidet
# sich zwischen den Distributionen (Fedora/RHEL: /usr/lib64/python3.x/...,
# SUSE: /usr/lib/python3/site-packages, Debian: /usr/lib/python3/dist-packages).
# Die Anwendung liegt daher als reine Daten unter %{_datadir}/%{name}, die
# Starter setzen den Pfad selbst. Damit laeuft ein und dasselbe Paket ueberall.

Name:           smartys-himalaya-gui
Version:        0.3.1
Release:        1%{?dist}
Summary:        Grafische Oberflaeche fuer himalaya
License:        MIT
URL:            https://github.com/smartonaut/smartys-himalaya-gui
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3

# WebKitGTK wird nur fuer die Fenster-Variante gebraucht; die Paketnamen
# unterscheiden sich je Distribution.
%if 0%{?suse_version}
Requires:       python3-gobject
Recommends:     typelib-1_0-WebKit2-4_1
Recommends:     himalaya
%endif
%if 0%{?fedora} || 0%{?rhel}
Requires:       python3-gobject
Recommends:     webkit2gtk4.1
Recommends:     himalaya
%endif
%if !0%{?suse_version} && !0%{?fedora} && !0%{?rhel}
Requires:       python3-gobject
%endif

%description
himalaya ist ein Mail-Client fuer das Terminal, der IMAP, SMTP, JMAP, Gmail,
Microsoft Graph und Maildir beherrscht — aber keine Oberflaeche.

Diese Anwendung setzt eine grafische Oberflaeche darauf. Sie kennt keine
eigenen Zugangsdaten: Konten, Passwoerter und Servereinstellungen kommen
ausschliesslich aus der himalaya-Konfiguration.

Zwei Varianten:
  * smartys-himalaya-gui       — eigenes Fenster (Port 8771)
  * smartys-himalaya-gui-web   — nur Browser (Port 8770), als Benutzerdienst

Beide binden ausschliesslich an 127.0.0.1.

%prep
%setup -q

%build
# reines Python-Paket, nichts zu kompilieren
for f in $(find smartys_mail -name '*.py'); do
    python3 -c "import ast,sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())" "$f" \
        || exit 1
done

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -r smartys_mail %{buildroot}%{_datadir}/%{name}/
find %{buildroot} -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

mkdir -p %{buildroot}%{_bindir}

cat > %{buildroot}%{_bindir}/smartys-himalaya-gui <<'LAUNCHER'
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/share/smartys-himalaya-gui")
from smartys_mail.desktop import main
main()
LAUNCHER

cat > %{buildroot}%{_bindir}/smartys-himalaya-gui-web <<'LAUNCHER'
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/share/smartys-himalaya-gui")
from smartys_mail.__main__ import main
main()
LAUNCHER
chmod 755 %{buildroot}%{_bindir}/smartys-himalaya-gui \
          %{buildroot}%{_bindir}/smartys-himalaya-gui-web

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/smartys-himalaya-gui.desktop <<'DESKTOP'
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
DESKTOP

for g in 64 128 256; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${g}x${g}/apps
    install -m 644 assets/icons/logo_${g}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${g}x${g}/apps/smartys-himalaya-gui.png
done
install -d %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 644 assets/icons/smartys-himalaya-gui.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/

install -d %{buildroot}/usr/lib/systemd/user
cat > %{buildroot}/usr/lib/systemd/user/smartys-himalaya-gui-web.service <<'UNIT'
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
UNIT

%post
%{?systemd_user_post:%systemd_user_post smartys-himalaya-gui-web.service}

%postun
%{?systemd_user_postun:%systemd_user_postun smartys-himalaya-gui-web.service}

%files
%doc README.md CHANGELOG.md
%license LICENSE
%{_datadir}/%{name}
%{_bindir}/smartys-himalaya-gui
%{_bindir}/smartys-himalaya-gui-web
%{_datadir}/applications/smartys-himalaya-gui.desktop
%{_datadir}/icons/hicolor/64x64/apps/smartys-himalaya-gui.png
%{_datadir}/icons/hicolor/128x128/apps/smartys-himalaya-gui.png
%{_datadir}/icons/hicolor/256x256/apps/smartys-himalaya-gui.png
%{_datadir}/icons/hicolor/scalable/apps/smartys-himalaya-gui.svg
/usr/lib/systemd/user/smartys-himalaya-gui-web.service

%changelog
* Mon Oct 26 2026 Smarty <smartonaut@users.noreply.github.com> - 0.3.1-1
- Loeschen loest den echten Papierkorb-Ordner selbst auf
- Fenster-Dienst startet wieder den Client statt des Webservers
- Erstes RPM-Paket (SUSE, Red Hat, Fedora)
