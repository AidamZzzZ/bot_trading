"""Modelo de velas (kline) de Binance.

Convierte el JSON crudo del stream en un objeto `Vela` con tipos correctos.
Los precios y volumenes llegan como texto ("75776.37000000"), asi que se
guardan como `Decimal` para no perder precision.

Intervalo elegido para el proyecto: 5 minutos.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

INTERVALO = "5m"


@dataclass(frozen=True)
class Vela:
    simbolo: str
    intervalo: str
    apertura: datetime  # inicio de la vela (campo k.t)
    cierre: datetime  # fin de la vela (campo k.T)
    open: Decimal  # k.o
    high: Decimal  # k.h
    low: Decimal  # k.l
    close: Decimal  # k.c
    volumen: Decimal  # k.v (volumen base, en BTC)
    cerrada: bool  # k.x -> True solo cuando la vela ya termino

    def __str__(self) -> str:
        estado = "cerrada" if self.cerrada else "en curso"
        return (
            f"{self.simbolo} {self.intervalo} "
            f"{self.apertura:%H:%M}-{self.cierre:%H:%M:%S} ({estado}) "
            f"O={self.open} H={self.high} L={self.low} C={self.close} "
            f"vol={self.volumen}"
        )


def a_utc(ms: int) -> datetime:
    """Epoch en milisegundos (como lo envia Binance) -> datetime UTC."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def desde_kline(payload: dict[str, Any]) -> Vela:
    """Extrae la vela del mensaje de stream y falla claro si el mensaje no es una kline."""
    if payload.get("e") != "kline":
        raise ValueError(f"Se esperaba un mensaje 'kline', llego: {payload.get('e')!r}")

    k = payload["k"]
    return Vela(
        simbolo=payload["s"],
        intervalo=k["i"],
        apertura=a_utc(k["t"]),
        cierre=a_utc(k["T"]),
        open=Decimal(k["o"]),
        high=Decimal(k["h"]),
        low=Decimal(k["l"]),
        close=Decimal(k["c"]),
        volumen=Decimal(k["v"]),
        cerrada=k["x"],
    )
