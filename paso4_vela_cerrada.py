import asyncio
import json
import websockets
from velas import INTERVALO, desde_kline

SIMBOLO = "btcusdt"
URL = f"wss://stream.binance.com:9443/ws/{SIMBOLO}@kline_{INTERVALO}"
ESPERA_MAXIMA_MS = 60_000  # si Binance no envia nada en 60 s, algo va mal

async def main() -> None:
    # --- 1. ENTORNO DEMO: Creamos nuestro saldo ficticio ---
    saldo_usdt = 1000.0  # Empezamos con 1000 dólares de prueba
    saldo_btc = 0.0      # Empezamos con 0 Bitcoin

    async with websockets.connect(URL, open_timeout=10) as ws:
        print(f"Conectado a {URL}")
        print(f"💰 Saldo inicial: {saldo_usdt} USDT | {saldo_btc} BTC")
        print(f"Esperando la primera vela cerrada de {INTERVALO}...\n")

        actualizaciones = 0
        while True:
            payload = json.loads(
                await asyncio.wait_for(ws.recv(), timeout=ESPERA_MAXIMA_MS / 1000)
            )
            vela = desde_kline(payload)

            # --- 2. LÓGICA CUANDO LA VELA SE CIERRA ---
            if vela.cerrada:
                precio_cierre = float(vela.close) # Guardamos el precio como número
                print("\n--- Vela cerrada ---")
                print(f"Precio actual de BTC: {precio_cierre} USDT")

                # Aquí es donde en el futuro Gemini tomará la decisión.
                # Por ahora, programamos una regla de prueba: 
                # Si tenemos 100 USDT, compramos. Si no tenemos USDT pero sí BTC, vendemos todo.
                
                if saldo_usdt >= 100.0:
                    print("🟢 [ACCIÓN SIMULADA] El bot aprieta el botón de COMPRAR (100 USDT)...")
                    btc_comprado = 100.0 / precio_cierre
                    saldo_usdt -= 100.0
                    saldo_btc += btc_comprado
                    print(f"✅ Compra exitosa a {precio_cierre}")
                
                elif saldo_btc > 0:
                    print("🔴 [ACCIÓN SIMULADA] El bot aprieta el botón de VENDER (Todo el BTC)...")
                    usdt_obtenidos = saldo_btc * precio_cierre
                    saldo_usdt += usdt_obtenidos
                    saldo_btc = 0.0
                    print(f"✅ Venta exitosa a {precio_cierre}")

                # 3. Mostramos la billetera actualizada
                print(f"💰 NUEVO SALDO DEMO -> USDT: {saldo_usdt:.2f} | BTC: {saldo_btc:.5f}\n")
                
                # ¡OJO! Eliminamos el 'return' que tenías antes para que el bot 
                # no se apague y siga operando con las siguientes velas.

            actualizaciones += 1
            print(f"  en curso {vela.apertura:%H:%M} -> close={vela.close}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
