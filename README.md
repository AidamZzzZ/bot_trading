# Bot de Trading - Binance BTC

Bot de trading algorítmico conectado a la API de Binance para monitorización de precios en tiempo real mediante WebSockets y gestión de cuenta mediante API Keys autenticadas.

---

## 1. Configuración de API Key

1. Crea o abre el archivo `.env` en la raíz de este proyecto.
2. Añade tus claves de Binance:
   ```env
   BINANCE_API_KEY=tu_api_key_aqui
   BINANCE_API_SECRET=tu_api_secret_aqui
   ```
3. *Nota de seguridad:* El archivo `.env` está incluido en `.gitignore` para proteger tus claves y que nunca se suban a un repositorio público.

---

## 2. Probar la conexión con tu API Key

Para comprobar que tus claves son válidas y ver tus saldos disponibles (USDT / BTC):

```powershell
.\venv\Scripts\python.exe probar_conexion_api.py
```

---

## 3. Iniciar el monitor de precios en vivo

Para conectar el WebSocket directo de Binance y ver los precios tick a tick junto con el estado de tu cuenta:

```powershell
.\venv\Scripts\python.exe bot_tiempo_real.py
```

---

## 4. Próximos pasos
- [ ] Definir la estrategia de entrada y salida (RSI, Medias Móviles, cruces de velas).
- [ ] Implementar los métodos de compra y venta (`POST /api/v3/order`) en `cliente_binance.py`.
- [ ] Probar primero en modo simulación (Paper Trading).
