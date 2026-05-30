# Pokédex Knob

Verwandelt den **Guition ESP32-S3 Knob** (rundes 360×360-Touch-Display mit Drehrad
und LED-Ring) in einen sprechenden Pokédex der originalen 151 Pokémon — als
Bastelprojekt für Kinder.

> Privates Hobby-/Fanprojekt. „Pokémon" ist eine Marke von Nintendo / Game Freak /
> The Pokémon Company. Dieses Projekt steht in keiner Verbindung zu diesen und ist
> nicht zum Verkauf bestimmt. Die Pokémon-Bilder werden **beim Flashen auf deinem
> eigenen Rechner** aus dem öffentlichen [PokeAPI](https://pokeapi.co)-Projekt
> geladen und nicht mit diesem Installer verteilt.

---

## Was es kann
- Alle **151 Pokémon** — Drehrad blättert durch
- **Antippen** dreht das Pokémon wie einen Taler → Pokédex-Karte mit Typ, Größe,
  Gewicht, Werten und Beschreibung
- **Sprachausgabe**: Name, Typ und Standard-Attacken werden vorgelesen
- **LED-Ring** in der Typ-Farbe, Pokéball-Startanimation, Vibrations-Feedback

## Was du brauchst
1. **Guition ESP32-S3 Knob 1.8″** (Modell JC3636K718C, rundes 360×360-Display
   mit Drehrad + LED-Ring)
   → **[Hier erhältlich auf AliExpress](https://s.click.aliexpress.com/e/_c41cmOC5)** *(Werbung · Affiliate-Link)*
2. Ein **USB-C-Datenkabel** (kein reines Ladekabel!)
3. Einen **Mac** oder **Windows-PC** mit Internet (für den einmaligen Bild-Download)

---

## Installation

### 1. Herunterladen
Lade das passende Paket von der [**Releases-Seite**](../../releases):
- `pokedex-installer-mac.zip`
- `pokedex-installer-windows.zip`

Entpacke die ZIP.

### 2. Knob anstecken
Per USB-C an den Computer.

### 3. Installer starten
- **Mac:** Doppelklick auf `Pokedex-Installer.command`
  *(Beim ersten Mal evtl. Rechtsklick → „Öffnen", um Gatekeeper zu bestätigen.)*
- **Windows:** Doppelklick auf `Pokedex-Installer.bat`

Der Installer richtet sich beim ersten Lauf selbst ein, lädt die Bilder, baut das
Inhalts-Image und flasht alles. Dauert ein paar Minuten.

### 4. Nur beim allerersten Mal: HID ausschalten
Ein **fabrikneuer** Knob läuft mit Werks-Firmware und meldet sich am USB als
Tastatur/Maus (HID) statt als Flash-Gerät. Der Installer sagt dir dann:

1. Knob einschalten → Werks-Menü erscheint
2. Auf **Settings** tippen
3. **HID** ausschalten
4. Gerät **aus- und wieder einschalten**

Danach erkennt der Installer den Knob automatisch und macht weiter. Bei späteren
Updates entfällt dieser Schritt.

---

## Voraussetzungen
- **Mac:** macOS 12+ und Python 3 (kommt mit den Xcode Command Line Tools — falls
  der Mac danach fragt, einfach installieren lassen)
- **Windows:** Python 3 von [python.org](https://www.python.org/downloads/)
  (beim Setup **„Add python.exe to PATH"** anhaken!)

## Problemlösung
| Problem | Lösung |
|---|---|
| Knob wird nicht gefunden | Anderes USB-Kabel (Datenkabel!), Type-C um 180° gedreht einstecken |
| Bleibt schwarz nach Flash | Gerät aus/an; nochmal Installer ausführen |
| „Python fehlt" | Mac: `xcode-select --install` · Windows: python.org mit PATH-Häkchen |
| Neu anfangen | Cache löschen: Mac `rm -rf ~/.pokedex-installer` · Windows `%USERPROFILE%\.pokedex-installer` löschen |

---

## Credits & Lizenz
- Code in diesem Repo: **MIT** (siehe `LICENSE`)
- Typ-Icons: [duiker101/pokemon-type-svg-icons](https://github.com/duiker101/pokemon-type-svg-icons) (MIT)
- Pokémon-Bilder & -Daten: [PokeAPI](https://pokeapi.co) (zur Laufzeit beim Nutzer geladen)
- Pokémon © Nintendo / Game Freak / The Pokémon Company
