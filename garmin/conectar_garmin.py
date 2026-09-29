#!/usr/bin/env python3
"""Conecta tu cuenta de Garmin Connect (y tu reloj) usando python-garminconnect.

- La contraseña se pide aquí en la Terminal con getpass (no se muestra ni se guarda).
- Tras el primer inicio de sesión se guardan tokens en ~/.garminconnect,
  así que las siguientes veces no te volverá a pedir la contraseña.
"""

import getpass
import os
import sys
from datetime import date
from pathlib import Path

try:
    from garminconnect import (
        Garmin,
        GarminConnectAuthenticationError,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
    )
except ImportError:
    sys.exit("Falta la librería. Ejecuta primero:  pip install garminconnect")

TOKENSTORE = Path(os.getenv("GARMINTOKENS", "~/.garminconnect")).expanduser()


def pedir_codigo_mfa() -> str:
    return input("Código de verificación (MFA) que te envió Garmin: ").strip()


def iniciar_sesion() -> Garmin:
    # 1) Intentar con tokens guardados de una sesión anterior.
    if TOKENSTORE.exists():
        try:
            api = Garmin()
            api.login(str(TOKENSTORE))
            print("✔ Sesión restaurada con los tokens guardados.")
            return api
        except Exception:
            print("Los tokens guardados ya no sirven; hay que iniciar sesión de nuevo.")

    # 2) Pedir credenciales en la Terminal.
    email = input("Correo de tu cuenta Garmin Connect: ").strip()
    password = getpass.getpass("Contraseña (no se mostrará al escribir): ")

    TOKENSTORE.mkdir(mode=0o700, parents=True, exist_ok=True)
    api = Garmin(email=email, password=password, prompt_mfa=pedir_codigo_mfa)
    api.login(str(TOKENSTORE))
    for f in TOKENSTORE.iterdir():
        f.chmod(0o600)
    print(f"✔ Sesión iniciada. Tokens guardados en {TOKENSTORE}")
    return api


def main() -> None:
    try:
        api = iniciar_sesion()
    except GarminConnectAuthenticationError as e:
        sys.exit(f"✘ Error de autenticación (¿correo/contraseña o código MFA?): {e}")
    except GarminConnectTooManyRequestsError:
        sys.exit("✘ Garmin está limitando los intentos. Espera un rato y vuelve a probar.")
    except GarminConnectConnectionError as e:
        sys.exit(f"✘ No se pudo conectar con Garmin Connect: {e}")

    print(f"\nHola, {api.get_full_name()} 👋\n")

    print("⌚ Dispositivos vinculados a tu cuenta:")
    for d in api.get_devices() or []:
        nombre = d.get("displayName") or d.get("productDisplayName") or "¿?"
        print(f"   - {nombre}  (id {d.get('deviceId')})")

    hoy = date.today().isoformat()
    stats = api.get_stats(hoy) or {}
    print(f"\n📊 Hoy ({hoy}):")
    print(f"   Pasos:            {stats.get('totalSteps')}")
    print(f"   Calorías:         {stats.get('totalKilocalories')}")
    print(f"   FC en reposo:     {stats.get('restingHeartRate')}")

    print("\n🏃 Últimas 5 actividades:")
    for a in api.get_activities(0, 5) or []:
        km = (a.get("distance") or 0) / 1000
        print(f"   - {a.get('startTimeLocal')}  {a.get('activityName')}  ({km:.2f} km)")

    print("\n✅ Conexión funcionando.")


if __name__ == "__main__":
    main()
