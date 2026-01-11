from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./trading_saas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Credenciales de Broker (Encriptadas)
    broker_email = Column(String, nullable=True)
    broker_password_enc = Column(String, nullable=True) # Encriptado con una Master Key
    broker_type = Column(String, default="EXNOVA") # EXNOVA o IQOPTION
    
    # Configuración de Trading del Usuario
    trading_amount = Column(Float, default=1.0)
    max_daily_loss = Column(Float, default=10.0)
    target_profit = Column(Float, default=20.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class TradeHistory(Base):
    __tablename__ = "trade_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    asset = Column(String)
    action = Column(String)
    strategy = Column(String)
    confidence = Column(Float)
    result = Column(String) # win/loss/equal
    profit = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
