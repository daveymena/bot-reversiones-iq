from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os

app = FastAPI()

# Permitir CORS para que el frontend pueda consultar la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global del bot
bot_state = {
    "balance": 0,
    "current_phase": "Inicializando...",
    "win_rate": 0,
    "net_profit": 0,
    "ops_count": "0/20",
    "active_asset": "Ninguno",
    "confidence": 0,
    "toxic_assets": [],
    "star_assets": [],
    "recent_trades": [],
    "logs": []
}

@app.get("/status")
async def get_status():
    return bot_state

@app.post("/update")
async def update_status(request: Request):
    global bot_state
    new_data = await request.json()
    bot_state.update(new_data)
    # Limitar logs a los últimos 50
    if len(bot_state["logs"]) > 50:
        bot_state["logs"] = bot_state["logs"][-50:]
    return {"status": "success"}

# Montar los archivos del dashboard
dashboard_path = os.path.join(os.getcwd(), "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/", StaticFiles(directory=dashboard_path, html=True), name="dashboard")

if __name__ == "__main__":
    print("🚀 API Bridge escuchando en http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
