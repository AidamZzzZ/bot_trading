"""Paso 4 - Parsear la vela y esperar la primera vela CERRADA.

Objetivo: comprobar que `velas.py` convierte bien el JSON de Binance y que
sabemos distinguir una vela en curso (x=false) de una cerrada (x=true).

Se ignoran las actualizaciones de la vela en curso; al llegar la primera
vela cerrada de 5m se muestra limpia y el script termina.

Ejecutar:
    .\\venv\\Scripts\\python.exe paso4_vela_cerrada.py
"""

import asyncio
import json

import websockets

from velas import INTERVALO, desde_kline

SIMBOLO = "btcusdt"
URL = f"wss://stream.binance.com:9443/ws/{SIMBOLO}@kline_{INTERVALO}"
ESPERA_MAXIMA_MS = 60_000  # si Binance no envia nada en 60 s, algo va mal


async def main() -> None:
    async with websockets.connect(URL, open_timeout=10) as ws:
        print(f"Conectado a {URL}")
        print(f"Esperando la primera vela cerrada de {INTERVALO}...\n")

        actualizaciones = 0
        while True:
            payload = json.loads(
                await asyncio.wait_for(ws.recv(), timeout=ESPERA_MAXIMA_MS / 1000)
            )
            vela = desde_kline(payload)

            if vela.cerrada:
                print(f"Actualizaciones ignoradas de la vela en curso: {actualizaciones}\n")
                print("--- Vela cerrada ---")
                print(f"simbolo   : {vela.simbolo}")
                print(f"intervalo : {vela.intervalo}")
                print(f"apertura  : {vela.apertura:%Y-%m-%d %H:%M:%S} UTC")
                print(f"cierre    : {vela.cierre:%Y-%m-%d %H:%M:%S} UTC")
                print(f"open      : {vela.open}")
                print(f"high      : {vela.high}")
                print(f"low       : {vela.low}")
                print(f"close     : {vela.close}")
                print(f"volumen   : {vela.volumen} BTC")
                print(f"cerrada   : {vela.cerrada}")
                return

            actualizaciones += 1
            print(f"  en curso {vela.apertura:%H:%M} -> close={vela.close}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
