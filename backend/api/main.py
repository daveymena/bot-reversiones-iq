"""
Backend API para Trading Bot SaaS
FastAPI server que ejecuta el bot y expone endpoints para la GUI
"""
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import asyncio
import json
from typing import Optional, Dict, List
import os
import sys

# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Importar versión headless del trader (sin PySide6)
from core.trader_headless import HeadlessTrader
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
import config

app = FastAPI(title="Trading Bot API", version="1.0.0")

# CORS para permitir conexiones desde el ejecutable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seguridad básica
security = HTTPBearer()

# Estado global del bot
bot_instance: Optional[LiveTrader] = None
active_connections: List[WebSocket] = []

# Modelos de datos
class BotStatus(BaseModel):
    running: bool
    balance: float
    profit: float
    win_rate: float
    total_trades: int
    active_trades: int

class TradeSignal(BaseModel):
    asset: str
    direction: str
    confidence: float
    entry_price: float
    timestamp: float

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check"""
    return {"status": "online", "service": "Trading Bot API"}

@app.get("/api/status")
async def get_status():
    """Obtener estado actual del bot"""
    if not bot_instance:
        return {"running": False, "message": "Bot no inicializado"}
    
    return {
        "running": bot_instance.running,
        "balance": bot_instance.market_data.get_balance() if bot_instance.market_data else 0,
        "profit": bot_instance.risk_manager.daily_pnl if bot_instance.risk_manager else 0,
        "win_rate": (bot_instance.risk_manager.wins / bot_instance.risk_manager.total_trades * 100) 
                    if bot_instance.risk_manager and bot_instance.risk_manager.total_trades > 0 else 0,
        "total_trades": bot_instance.risk_manager.total_trades if bot_instance.risk_manager else 0,
        "active_trades": len(bot_instance.active_trades) if bot_instance.active_trades else 0
    }

@app.post("/api/start")
async def start_bot():
    """Iniciar el bot"""
    global bot_instance
    
    if bot_instance and bot_instance.running:
        raise HTTPException(status_code=400, detail="Bot ya está corriendo")
    
    try:
        # Crear instancia del bot
        market_data = MarketDataHandler(Config.BROKER_NAME)
        market_data.connect()
        
        bot_instance = LiveTrader(market_data)
        
        # Iniciar en thread separado
        import threading
        bot_thread = threading.Thread(target=bot_instance.run, daemon=True)
        bot_thread.start()
        
        return {"message": "Bot iniciado correctamente", "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando bot: {str(e)}")

@app.post("/api/stop")
async def stop_bot():
    """Detener el bot"""
    global bot_instance
    
    if not bot_instance or not bot_instance.running:
        raise HTTPException(status_code=400, detail="Bot no está corriendo")
    
    bot_instance.stop()
    return {"message": "Bot detenido", "status": "stopped"}

@app.post("/api/pause")
async def pause_bot():
    """Pausar el bot"""
    global bot_instance
    
    if not bot_instance or not bot_instance.running:
        raise HTTPException(status_code=400, detail="Bot no está corriendo")
    
    bot_instance.pause()
    return {"message": "Bot pausado", "status": "paused"}

@app.post("/api/resume")
async def resume_bot():
    """Reanudar el bot"""
    global bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot no inicializado")
    
    bot_instance.resume()
    return {"message": "Bot reanudado", "status": "running"}

# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para actualizaciones en tiempo real
    La GUI se conecta aquí para recibir logs, precios, señales, etc.
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Mantener conexión viva
            await asyncio.sleep(1)
            
            # Enviar estado actual
            if bot_instance:
                status = {
                    "type": "status_update",
                    "data": {
                        "running": bot_instance.running,
                        "balance": bot_instance.market_data.get_balance() if bot_instance.market_data else 0,
                        "profit": bot_instance.risk_manager.daily_pnl if bot_instance.risk_manager else 0,
                    }
                }
                await websocket.send_json(status)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)

async def broadcast_message(message: dict):
    """Enviar mensaje a todos los clientes conectados"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar el servidor"""
    print("🚀 Trading Bot API iniciado")
    print(f"📊 Broker: {Config.BROKER_NAME}")
    print(f"💰 Cuenta: {Config.ACCOUNT_TYPE}")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar el servidor"""
    global bot_instance
    if bot_instance and bot_instance.running:
        bot_instance.stop()
    print("👋 Trading Bot API detenido")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
