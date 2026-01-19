from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
import json
import os
from datetime import datetime
from database_legacy import User, SessionLocal, TradeHistory
from security import encrypt_password, decrypt_password
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuración de Seguridad
SECRET_KEY = "tu_llave_secreta_super_segura"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Antigravity SaaS Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado de los procesos de bots por usuario
user_bots = {}

# --- UTILIDADES ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

import hashlib

def verify_password(plain_password, hashed_password):
    # Intentar bcrypt primero (para futuros usuarios)
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except:
        pass
    # Fallback a SHA256 (para el admin actual)
    sha_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return sha_hash == hashed_password

# --- ENDPOINTS DE DASHBOARD ---

@app.post("/api/register")
async def register(request: Request, db=Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email ya registrado")
        
    new_user = User(
        email=email,
        hashed_password=get_password_hash(password)
    )
    db.add(new_user)
    db.commit()
    return {"status": "success", "message": "Usuario creado"}

@app.post("/api/login")
async def login(request: Request, db=Depends(get_db)):
    data = await request.json()
    user = db.query(User).filter(User.email == data.get("email")).first()
    if not user or not verify_password(data.get("password"), user.hashed_password):
        raise HTTPException(401, "Credenciales inválidas")
        
    return {"status": "success", "user_id": user.id, "email": user.email}

@app.post("/api/update-broker")
async def update_broker(request: Request, db=Depends(get_db)):
    data = await request.json()
    user_id = data.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:
        user.broker_email = data.get("broker_email")
        if data.get("broker_password"):
            user.broker_password_enc = encrypt_password(data.get("broker_password"))
        user.trading_amount = data.get("amount", 1.0)
        db.commit()
        return {"status": "success"}
    return {"status": "error"}

@app.get("/status/{user_id}")
async def get_user_status(user_id: int):
    # Por ahora devolvemos un estado simulado para el dashboard
    # En la siguiente fase, conectaremos los procesos reales aquí
    return {
        "balance": 4485.27,
        "current_phase": "Modo Aprendizaje",
        "win_rate": 68.5,
        "ops_count": "12/20",
        "active_asset": "GBPUSD-OTC",
        "confidence": 57.8,
        "logs": [f"[{datetime.now().strftime('%H:%M:%S')}] Iniciado como servicio SaaS..."],
        "recent_trades": []
    }

# Montar los archivos del dashboard
dashboard_path = os.path.join(os.getcwd(), "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/", StaticFiles(directory=dashboard_path, html=True), name="dashboard")

if __name__ == "__main__":
    print("🚀 SaaS API Bridge listo en puerto 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
