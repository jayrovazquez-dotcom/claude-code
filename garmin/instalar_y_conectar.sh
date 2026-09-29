#!/usr/bin/env bash
# Crea un entorno virtual, instala python-garminconnect y ejecuta el script de conexión.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
./.venv/bin/pip install --quiet --upgrade pip garminconnect
./.venv/bin/python conectar_garmin.py
