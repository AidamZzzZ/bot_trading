"""Paso 3 - Comprobar el stream publico de velas (kline) de Binance.

Objetivo de este paso: ver el JSON en crudo que envia Binance y confirmar
que los campos que necesitaremos (apertura, maximo, minimo, cierre, volumen
y estado de la vela) llegan como esperamos. Todavia NO hay logica de trading.

Ejecutar:
    .\\venv\\Scripts\\python.exe paso3_probar_kline.py
"""

import asyncio
import json
from datetime import datetime, timezone

import websockets

# Stream publico: no requiere API key ni firma.
# Formato del nombre: <simbolo_minusculas>@kline_<intervalo>
URL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
MENSAJES = 5


def hora_utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%H:%M:%S")


async def main() -> None:
    async with websockets.connect(URL, open_timeout=10) as ws:
        print(f"Conectado a {URL}\n")

        for n in range(1, MENSAJES + 1):
            payload = json.loads(await asyncio.wait_for(ws.recv(), timeout=15))

            if n == 1:
                print("--- JSON crudo del primer mensaje ---")
                print(json.dumps(payload, indent=2))
                print("\n--- Resumen de los mensajes recibidos ---")

            vela = payload["k"]
            print(
                f"[{n}] {payload['s']} {vela['i']} "
                f"abre={hora_utc(vela['t'])} "
                f"O={vela['o']} H={vela['h']} L={vela['l']} C={vela['c']} "
                f"vol={vela['v']} "
                f"cerrada={vela['x']}"
            )

        print(f"\nFin: {MENSAJES} mensajes recibidos, conexion cerrada.")


if __name__ == "__main__":
    asyncio.run(main())
