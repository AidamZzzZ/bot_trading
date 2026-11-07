"""Cliente REST para interactuar con la API de Binance.

Permite:
1. Probar conectividad publica (ping y hora).
2. Consultar balances de la cuenta autenticada con API Key y Secret (HMAC-SHA256).
3. Base para ejecutar ordenes de compra/venta cuando se agreguen mas adelante.
"""

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal
from typing import Any

from config import BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_REST_URL


class BinanceClient:
    def __init__(
        self,
        api_key: str = BINANCE_API_KEY,
        api_secret: str = BINANCE_API_SECRET,
        base_url: str = BINANCE_REST_URL,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

    def _firmar(self, query_string: str) -> str:
        """Genera la firma HMAC SHA256 requerida por Binance para endpoints privados."""
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _solicitud(
        self,
        metodo: str,
        endpoint: str,
        parametros: dict[str, Any] | None = None,
        autenticado: bool = False,
    ) -> dict[str, Any]:
        """Realiza una peticion HTTP a la API de Binance."""
        if parametros is None:
            parametros = {}

        headers = {
            "User-Agent": "BotTrading/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        if autenticado:
            if not self.api_key or not self.api_secret:
                raise ValueError(
                    "Falta configurar BINANCE_API_KEY o BINANCE_API_SECRET en el archivo .env"
                )
            headers["X-MBX-APIKEY"] = self.api_key
            # Binance requiere el timestamp en milisegundos
            parametros["timestamp"] = int(time.time() * 1000)
            parametros["recvWindow"] = 5000

            query_str = urllib.parse.urlencode(parametros)
            signature = self._firmar(query_str)
            query_str = f"{query_str}&signature={signature}"
        else:
            query_str = urllib.parse.urlencode(parametros) if parametros else ""

        url = f"{self.base_url}{endpoint}"
        if query_str and metodo == "GET":
            url = f"{url}?{query_str}"
            data = None
        elif query_str:
            data = query_str.encode("utf-8")
        else:
            data = None

        req = urllib.request.Request(url, data=data, headers=headers, method=metodo)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                cuerpo = resp.read().decode("utf-8")
                return json.loads(cuerpo)
        except urllib.error.HTTPError as e:
            cuerpo_error = e.read().decode("utf-8")
            try:
                detalle = json.loads(cuerpo_error)
                mensaje = f"Error HTTP {e.code} de Binance: [{detalle.get('code')}] {detalle.get('msg')}"
            except Exception:
                mensaje = f"Error HTTP {e.code}: {cuerpo_error}"
            raise RuntimeError(mensaje) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Error de red al conectar con Binance: {e.reason}") from e

    def ping(self) -> bool:
        """Comprueba conectividad basica con los servidores de Binance."""
        try:
            self._solicitud("GET", "/api/v3/ping")
            return True
        except Exception:
            return False

    def obtener_precio(self, symbol: str = "BTCUSDT") -> Decimal:
        """Obtiene el precio actual puntual mediante REST."""
        res = self._solicitud("GET", "/api/v3/ticker/price", {"symbol": symbol.upper()})
        return Decimal(res["price"])

    def obtener_cuenta(self) -> dict[str, Any]:
        """Obtiene el estado completo de la cuenta (requiere API Key valida)."""
        return self._solicitud("GET", "/api/v3/account", autenticado=True)

    def obtener_balances(self) -> dict[str, dict[str, Decimal]]:
        """Devuelve los saldos de criptos y monedas con balance mayor a cero."""
        cuenta = self.obtener_cuenta()
        balances = {}
        for item in cuenta.get("balances", []):
            libre = Decimal(item["free"])
            bloqueado = Decimal(item["locked"])
            total = libre + bloqueado
            if total > 0:
                balances[item["asset"]] = {
                    "free": libre,
                    "locked": bloqueado,
                    "total": total,
                }
        return balances
