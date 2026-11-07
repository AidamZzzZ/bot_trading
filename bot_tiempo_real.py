"""Bot de Trading en tiempo real (Conexion con API Key y WebSocket).

Funciones:
1. Valida las credenciales de la API Key en Binance.
2. Muestra los saldos iniciales (USDT / BTC).
3. Conecta al WebSocket en vivo de BTCUSDT para recibir precios directos y continuos.
4. Prepara el punto de entrada para la logica futura de compra y venta.

Ejecutar:
    .\\venv\\Scripts\\python.exe bot_tiempo_real.py
"""

import asyncio
import json
import signal
import sys
from datetime import datetime, timezone
from decimal import Decimal

import websockets
from cliente_binance import BinanceClient
from config import BINANCE_WS_URL, SIMBOLO, hay_credenciales


def hora_actual_utc() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def al_recibir_precio(precio: Decimal, cliente: BinanceClient | None) -> None:
    """Punto de integracion para la estrategia y las ordenes de compra/venta.

    Aqui es donde mas adelante agregaremos las condiciones para ejecutar:
    - cliente.comprar(...)
    - cliente.vender(...)
    """
    # De momento solo mostramos el precio en vivo
    # (En las proximas fases agregaremos indicadores como RSI, EMA, etc.)
    pass


async def iniciar_stream_tiempo_real(cliente: BinanceClient | None = None) -> None:
    # Usamos el stream de ticker o trade para ver cada movimiento de precio
    stream_url = f"{BINANCE_WS_URL}/{SIMBOLO.lower()}@ticker"
    print(f"\n[+] Conectando al WebSocket de Binance: {stream_url}")
    print("[+] Presiona Ctrl+C en cualquier momento para detener el bot.\n")
    print(f"{'HORA (UTC)':<12} | {'SIMBOLO':<10} | {'PRECIO EN VIVO':<18} | {'VAR 24H (%)':<12}")
    print("-" * 62)

    precio_anterior: Decimal | None = None

    while True:
        try:
            async with websockets.connect(stream_url, ping_interval=20, ping_timeout=20) as ws:
                while True:
                    mensaje = await ws.recv()
                    datos = json.loads(mensaje)

                    # 'c' es el precio de cierre actual (precio en vivo)
                    precio_actual = Decimal(datos["c"])
                    cambio_24h = Decimal(datos["P"])

                    # Indicador visual si subio o bajo respecto al tick previo
                    if precio_anterior is None:
                        direccion = " "
                    elif precio_actual > precio_anterior:
                        direccion = "▲"
                    elif precio_actual < precio_anterior:
                        direccion = "▼"
                    else:
                        direccion = "="

                    precio_anterior = precio_actual

                    print(
                        f"{hora_actual_utc():<12} | "
                        f"{SIMBOLO:<10} | "
                        f"${precio_actual:>12,.2f} {direccion} | "
                        f"{cambio_24h:>+10.2f}%",
                        flush=True,
                    )

                    # Ejecutar hook de logica
                    al_recibir_precio(precio_actual, cliente)

        except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
            print("\n[!] Conexion interrumpida con Binance. Reconectando en 3 segundos...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"\n[!] Error en el stream: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)


def main() -> None:
    print("=" * 62)
    print("      INICIANDO BOT DE TRADING - PRECIO BTC EN VIVO")
    print("=" * 62)

    cliente: BinanceClient | None = None

    if hay_credenciales():
        print("[*] Credenciales API encontradas en .env. Verificando con Binance...")
        cliente = BinanceClient()
        try:
            cuenta = cliente.obtener_cuenta()
            print("    -> Autenticacion API: EXITOSA")
            print(f"    -> Cuenta habilitada para operar: {cuenta.get('canTrade', False)}")

            balances = cliente.obtener_balances()
            usdt = balances.get("USDT", {}).get("free", Decimal("0.0"))
            btc = balances.get("BTC", {}).get("free", Decimal("0.0"))
            print(f"    -> Balance disponible: {usdt} USDT | {btc} BTC")
        except Exception as e:
            print(f"    [AVISO] No se pudo verificar la API Key ({e}).")
            print("    Se continuara con el stream de precios en vivo.")
    else:
        print("[*] Modo sin API Key: Obteniendo precios publicos en vivo.")
        print("    (Para habilitar compras/ventas, configura tus claves en el archivo .env)")

    # Iniciar el bucle de eventos asincrono
    try:
        asyncio.run(iniciar_stream_tiempo_real(cliente))
    except KeyboardInterrupt:
        print("\n\n[+] Bot detenido por el usuario.")


if __name__ == "__main__":
    main()
