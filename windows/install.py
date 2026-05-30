#!/usr/bin/env python3
"""
Pokedex Knob - Installer (Mac + Windows).

Laeuft INNERHALB des venv, das der Launcher (.command / .bat) anlegt -
dadurch sind esptool, pyserial, pillow und requests direkt importierbar.

Ablauf:
  1. Knob am USB suchen (Espressif-Serial-Port)
  2. 151 Bilder von PokeAPI/GitHub laden (Fan-Mirror), 360x360 JPG
  3. LittleFS-Image bauen (Bilder + mitgelieferte Audios + Icons)
  4. Firmware + Inhalte flashen
"""
import io, os, sys, time, subprocess, shutil, platform
from pathlib import Path

# ---- Ausgaben ----------------------------------------------------------------
WIN = (os.name == "nt")
class C:
    if WIN:  # Windows-Terminal kann ANSI seit Win10, aber sicher ist sicher
        R=G=Y=B=D=X=""
    else:
        R="\033[31m"; G="\033[32m"; Y="\033[33m"; B="\033[34m"; D="\033[2m"; X="\033[0m"
def p(m): print(m, flush=True)
def ok(m): p(f"{C.G}[ok]{C.X} {m}")
def warn(m): p(f"{C.Y}[!]{C.X} {m}")
def err(m): p(f"{C.R}[x] {m}{C.X}")
def step(m): p(f"\n{C.B}> {m}{C.X}")

HERE  = Path(__file__).resolve().parent
FW    = HERE / "firmware"
CT    = HERE / "content"
BIN   = HERE / "bin"
CACHE = Path.home() / ".pokedex-installer"
CACHE.mkdir(exist_ok=True)
PIC_CACHE = CACHE / "pic"

MKLITTLEFS = BIN / ("mklittlefs.exe" if WIN else "mklittlefs")

ESP_VID = 0x303A   # Espressif USB Vendor ID

def dequarantine(path: Path):
    """macOS setzt heruntergeladene Dateien in Quarantaene. Gatekeeper killt
    unsignierte Binaries dann mit SIGKILL. Attribut entfernen, damit das
    mitgelieferte mklittlefs laufen kann."""
    if sys.platform != "darwin":
        return
    subprocess.run(["xattr", "-d", "com.apple.quarantine", str(path)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---- 1) Port suchen ----------------------------------------------------------
def find_port(timeout_s: int = 90) -> str:
    from serial.tools import list_ports
    step("Suche Knob am USB...")
    instructed = False
    t_end = time.time() + timeout_s
    while time.time() < t_end:
        esp = [pi.device for pi in list_ports.comports() if pi.vid == ESP_VID]
        if esp:
            ok(f"Knob gefunden: {esp[0]}")
            return esp[0]
        if not instructed:
            show_hid_instructions()
            instructed = True
        time.sleep(1.5)
    err("Kein Geraet gefunden. Stecker / Kabel / HID-Settings pruefen.")
    sys.exit(1)

def show_hid_instructions():
    p("")
    warn("Noch kein Knob im Flash-Modus erkannt.")
    p(f"{C.D}Falls der Knob brandneu ist (Werks-Firmware), einmalig am Geraet:{C.X}")
    p("   1) Knob einschalten -> Werks-Menue erscheint")
    p("   2) auf 'Settings' tippen")
    p("   3) 'HID' ausschalten")
    p("   4) Geraet aus- und wieder einschalten")
    p(f"{C.D}Dann geht es hier automatisch weiter. (Kabel muss Daten koennen!){C.X}\n")

# ---- 2) Bilder laden ---------------------------------------------------------
PIC_URL = ("https://raw.githubusercontent.com/PokeAPI/sprites/master/"
           "sprites/pokemon/other/official-artwork/{id}.png")
CANVAS = 360; LABEL_RESERVE = 90
ART_BOX = (300, CANVAS - LABEL_RESERVE - 10)
ART_CY  = (CANVAS - LABEL_RESERVE) // 2
BG = (255, 255, 255)

def fetch_images():
    import requests
    from PIL import Image
    step("Lade die 151 Pokemon-Artworks (PokeAPI/GitHub)...")
    PIC_CACHE.mkdir(parents=True, exist_ok=True)
    for pid in range(1, 152):
        out = PIC_CACHE / f"{pid:03d}.jpg"
        if out.exists():
            continue
        for attempt in range(4):
            try:
                r = requests.get(PIC_URL.format(id=pid), timeout=20)
                r.raise_for_status()
                art = Image.open(io.BytesIO(r.content)).convert("RGBA")
                art.thumbnail(ART_BOX, Image.LANCZOS)
                canvas = Image.new("RGB", (CANVAS, CANVAS), BG)
                x = (CANVAS - art.width) // 2
                y = ART_CY - art.height // 2
                canvas.paste(art, (x, y), mask=art.split()[-1])
                canvas.save(out, "JPEG", quality=85, optimize=True)
                break
            except Exception:
                time.sleep(1 + attempt)
        else:
            err(f"Bild #{pid} fehlgeschlagen. Internet pruefen, neu starten.")
            sys.exit(3)
        if pid % 15 == 0:
            p(f"  {pid}/151")
    ok(f"151/151 Bilder bereit (Cache: {PIC_CACHE})")

# ---- 3) LittleFS-Image bauen -------------------------------------------------
def build_littlefs() -> Path:
    step("Baue Inhalts-Image (Bilder + Audio + Icons)...")
    root = CACHE / "lfs_root"
    if root.exists():
        shutil.rmtree(root)
    (root / "audio").mkdir(parents=True)
    (root / "icons").mkdir(parents=True)
    shutil.copytree(PIC_CACHE, root / "pic")
    for sub in ("de", "type", "info"):
        shutil.copytree(CT / "audio" / sub, root / "audio" / sub)
    if (CT / "audio" / "boot.mp3").exists():
        shutil.copy(CT / "audio" / "boot.mp3", root / "audio" / "boot.mp3")
    for f in (CT / "icons").glob("*.bin"):
        shutil.copy(f, root / "icons" / f.name)

    out = CACHE / "littlefs.bin"
    dequarantine(MKLITTLEFS)
    cmd = [str(MKLITTLEFS), "-c", str(root), "-p", "256", "-b", "4096",
           "-s", "0xCE0000", str(out)]
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        err(f"mklittlefs fehlt: {MKLITTLEFS}")
        sys.exit(4)
    ok("Image gebaut.")
    return out

# ---- 4) Flashen --------------------------------------------------------------
def flash(port: str, lfs_bin: Path):
    step("Flashe Firmware + Inhalte aufs Geraet...")
    # esptool als Modul des venv-Python (sys.executable) -> plattformunabhaengig
    args = [sys.executable, "-m", "esptool",
            "--chip", "esp32s3", "--port", port, "--baud", "921600",
            "--before", "default_reset", "--after", "hard_reset",
            "write_flash", "-z",
            "--flash_mode", "keep", "--flash_freq", "keep", "--flash_size", "keep",
            "0x0",      str(FW / "bootloader.bin"),
            "0x8000",   str(FW / "partitions.bin"),
            "0xe000",   str(FW / "boot_app0.bin"),
            "0x10000",  str(FW / "app.bin"),
            "0x310000", str(lfs_bin)]
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        err(f"Flashen fehlgeschlagen ({e.returncode}). Abziehen, neu stecken, nochmal.")
        sys.exit(e.returncode)
    ok("Geflasht. Geraet startet neu.")

# ---- Paket-Pruefung ----------------------------------------------------------
def check_package():
    """Stellt sicher, dass Firmware + Audio dabei sind. Wenn nicht, hat der
    Nutzer vermutlich den Quellcode (Code -> Download ZIP) statt des
    Release-Pakets geladen."""
    needed = [FW / "app.bin", FW / "bootloader.bin", CT / "audio" / "de"]
    if all(x.exists() for x in needed):
        return
    err("Dieses Paket ist unvollstaendig (Firmware/Audio fehlen).")
    p("")
    p(f"{C.Y}Du hast vermutlich den QUELLCODE geladen (gruener 'Code'-Button).{C.X}")
    p("Der lauffaehige Installer ist das Release-Paket:")
    p(f"{C.B}  https://github.com/moorfun-vibe/pokedex-knob/releases/latest{C.X}")
    p("  -> dort 'pokedex-installer-mac.zip' (bzw. -windows.zip) laden,")
    p("     entpacken und DARAUS den Installer starten.")
    p("")
    sys.exit(5)

# ---- main --------------------------------------------------------------------
def main():
    p(f"{C.B}== Pokedex Installer =={C.X}")
    p(f"{C.D}System: {platform.system()} | Cache: {CACHE}{C.X}")
    check_package()
    port    = find_port()
    fetch_images()
    lfs_bin = build_littlefs()
    flash(port, lfs_bin)
    p("")
    ok("Fertig! Dein Pokedex laeuft jetzt. Viel Spass.")
    p(f"{C.D}Drehrad blaettert, Pokemon antippen dreht zur Pokedex-Karte.{C.X}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        p("\nAbgebrochen.")
        sys.exit(130)
