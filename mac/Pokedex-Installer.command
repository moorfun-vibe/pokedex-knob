#!/bin/bash
# Pokedex Knob Installer - Mac. Doppelklick.
cd "$(dirname "$0")"

PYTHON=""
for c in python3 /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
    command -v "$c" >/dev/null 2>&1 && { PYTHON="$c"; break; }
done
if [ -z "$PYTHON" ]; then
    echo "Python 3 fehlt. Bitte einmal ausfuehren:  xcode-select --install"
    echo "Danach diesen Installer erneut doppelklicken."
    read -p "Enter zum Beenden..."; exit 1
fi

VENV="$HOME/.pokedex-installer/venv"
if [ ! -x "$VENV/bin/python" ]; then
    echo "Richte Tools ein (einmalig, ~20 MB)..."
    "$PYTHON" -m venv "$VENV" || { echo "venv-Fehler"; read -p "Enter..."; exit 1; }
    "$VENV/bin/pip" install --quiet --upgrade pip
    "$VENV/bin/pip" install --quiet esptool pyserial pillow requests || {
        echo "pip-Fehler (Internet?)"; read -p "Enter..."; exit 1; }
fi

clear
"$VENV/bin/python" install.py
ec=$?
echo
read -p "Enter zum Schliessen..."
exit $ec
