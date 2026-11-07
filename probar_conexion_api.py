"""Script de diagnostico para validar la API Key y Secret de Binance.

Uso:
    .\\venv\\Scripts\\python.exe probar_conexion_api.py
"""

import sys
from config import BINANCE_API_KEY, BINANCE_API_SECRET, SIMBOLO, hay_credenciales
from cliente_binance import BinanceClient


def main() -> None:
    print("=" * 60)
    print("      DIAGNOSTICO DE CONEXION CON BINANCE API")
    print("=" * 60)

    # 1. Comprobacion de presencia de claves en el archivo .env
    if not hay_credenciales():
        print("\n[AVISO] No se encontraron claves en el archivo .env.")
        print("Edita el archivo .env y agrega tus credenciales:")
        print("    BINANCE_API_KEY=tu_clave_aqui")
        print("    BINANCE_API_SECRET=tu_secreto_aqui")
        print("\nSi aun no tienes la API Key, puedes generarla en Binance:")
        print("    Perfil -> Gestion de API -> Crear API\n")
        sys.exit(1)

    print(f"\n[1] Clave detectada: {BINANCE_API_KEY[:6]}...{BINANCE_API_KEY[-4:]}")
    print("[2] Comprobando conexion con Binance...")

    cliente = BinanceClient()

    # 2. Test de ping basico
    if not cliente.ping():
        print("[ERROR] No se pudo hacer ping a api.binance.com. Revisa tu conexion a internet.")
        sys.exit(1)
    print("    -> Ping a Binance: EXITOSO")

    # 3. Test de precio publico
    try:
        precio = cliente.obtener_precio(SIMBOLO)
        print(f"    -> Precio actual de {SIMBOLO} (REST): ${precio:,.2f} USD")
    except Exception as e:
        print(f"    -> Error al consultar precio: {e}")

    # 4. Test de autenticacion con API Key y Secret
    print("\n[3] Probando autenticacion y permisos de la API Key...")
    try:
        cuenta = cliente.obtener_cuenta()
        puede_operar = cuenta.get("canTrade", False)
        tipo_cuenta = cuenta.get("accountType", "SPOT")

        print("    -> Autenticacion: CORRECTA (Claves validas)")
        print(f"    -> Tipo de cuenta: {tipo_cuenta}")
        print(f"    -> Permiso para operar (Trading habilitado): {'SI' if puede_operar else 'NO'}")

        # Mostrar saldos disponibles
        balances = cliente.obtener_balances()
        print("\n--- Balances disponibles en tu cuenta ---")
        if not balances:
            print("    (No hay balances mayores a 0 en la cuenta)")
        else:
            for activo, datos in balances.items():
                print(f"    * {activo:<6}: {datos['free']} (disponible) | {datos['locked']} (bloqueado)")

        print("\n" + "=" * 60)
        print("¡Todo listo! Tu API Key esta correctamente conectada.")
        print("Ya tienes las credenciales listas para comprar y vender.")
        print("=" * 60)

    except RuntimeError as e:
        print(f"\n[ERROR DE AUTENTICACION] {e}")
        print("\nConsejos de resolucion:")
        print("1. Verifica que la API Key y Secret esten bien copiadas (sin espacios).")
        print("2. Asegurate de que la API Key no haya expirado en Binance.")
        print("3. Si tienes restriccion por IP en Binance, comprueba tu direccion IP publica.")


if __name__ == "__main__":
    main()
