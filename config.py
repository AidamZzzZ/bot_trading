"""Modulo de configuracion para el Bot de Trading.

Carga de forma segura las credenciales de Binance desde el archivo .env
sin obligar a instalar librerias externas.
"""

import os
from pathlib import Path

RUTA_BASE = Path(__file__).resolve().parent
ARCHIVO_ENV = RUTA_BASE / ".env"


def cargar_env(ruta_archivo: Path = ARCHIVO_ENV) -> None:
    """Lee un archivo .env simple y lo carga en os.environ si no esta definido."""
    if not ruta_archivo.exists():
        return

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            # Ignorar lineas vacias y comentarios
            if not linea or linea.startswith("#"):
                continue
            if "=" in linea:
                clave, valor = linea.split("=", 1)
                clave = clave.strip()
                valor = valor.strip().strip("\"'")
                if clave not in os.environ:
                    os.environ[clave] = valor


# Cargar variables al importar el modulo
cargar_env()

# Credenciales de Binance
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "").strip()
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET", "").strip()

# Parametros de trading
SIMBOLO = "BTCUSDT"
BINANCE_REST_URL = "https://api.binance.com"
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"


def hay_credenciales() -> bool:
    """Indica si las claves de API estan configuradas y no son vacias."""
    return bool(BINANCE_API_KEY and BINANCE_API_SECRET)
