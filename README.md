# Tayori Mouselook fuer macOS

Private Firestorm-Abwandlung mit Zielverfolgung im echten Mouselook. Kein offizieller Firestorm-Release.
Zielgeraet: Apple M3, vom Nutzer gemeldetes macOS Tahoe 26.7.1. Der Build wird universal fuer arm64 und x86_64 erstellt.
**Vorbereitung: Mac-Build und Laufzeittest stehen noch aus.** Windows-Version wurde gebaut und bei bewegten Zielen vom Nutzer positiv getestet.

## Einrichtung

Den gesamten Inhalt dieses Pakets inklusive `.github` in die Wurzel des oeffentlichen Repositorys `Moonfox79/Tayori-Mouselook-Mac` hochladen. Das ZIP selbst nicht als ZIP ins Repository legen.
Danach unter Actions den Workflow **Tayori Mac bauen** oeffnen und **Run workflow** auswaehlen.
Der Workflow startet ausschliesslich manuell. Keine Releases, keine automatischen Push-Builds, keine Apple-Zugangsdaten oder bezahlten Runner.
Nur bei einem oeffentlichen Repository wird der Job ausgefuehrt. Standard-Runner `macos-15-intel`, Xcode 16.4; offizielle Quellen und Buildvariablen sind auf feste Commits gebunden.

## Download nach erfolgreichem Build

Unter dem abgeschlossenen Actions-Lauf im Bereich Artifacts **Tayori-Mouselook-Mac-Universal** herunterladen.
Enthaelt DMG, Viewer-Quellcode, Buildskripte, Lizenz und Pruefsummen. Das Paket kann nach erfolgreichem Mac-Test komplett weitergegeben werden.
Downloadartefakte werden nach 7 Tagen geloescht. Buildprotokolle nach 3 Tagen.
Bei einem Fehler die Buildprotokolle herunterladen und zur Diagnose bereitstellen.

## Installation und Bedienung

DMG oeffnen und die enthaltene App nach Programme ziehen. Eigene Tayori-Bezeichnung verwenden und vorhandenen offiziellen Viewer behalten.
F9: Zielauswahl, Aktualisierung alle 5 Sekunden, Umkreis 96 m. Avatar anklicken: Mouselook-Verfolgung. F8: stoppen.
Bei Mac-Funktionstasten ggf. Fn/Globus zusammen mit F8/F9 druecken.
Geladene Zielperson in derselben Region erforderlich. Fokusverlust, Teleport oder Verlassen von Mouselook beendet die Verfolgung.

Die App wird mit lokaler Ad-hoc-Signatur erstellt, ohne Apple Developer ID und ohne Apple-Notarisierung. macOS kann sie deshalb blockieren. Keine globale Abschaltung von Gatekeeper vornehmen. Erst die tatsaechliche Meldung auf dem Ziel-Mac pruefen.
Der Build prueft DMG-Integritaet, Universal-Architekturen und die lokale Signatur. Das ersetzt keinen Start- oder Second-Life-Test auf dem M3.

## Quellen und Lizenz

Viewer: https://github.com/FirestormViewer/phoenix-firestorm
Commit: be6bce603845b9dc376a381722ebd9525aba0e64
Buildvariablen: https://github.com/FirestormViewer/fs-build-variables
Commit: c17312d38377c003977cf5b6dcc83c6042eba194

Viewer und Tayori-Viewer-Aenderungen: LGPL-2.1-only, siehe LICENSE_Firestorm.txt. Bestehende Urheber- und Drittanbieterhinweise bleiben erhalten.
Benoetigte Bibliotheken werden ueber das originale autobuild.xml geladen. Keine lizenzierten KDU-/FMOD-Pakete werden hinzugefuegt.
Python-Buildskript und Workflow duerfen mit diesem Projekt benutzt, geaendert und weitergegeben werden.
