from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import hashlib

# Configuración mínima para el script
DATABASE_URL = "sqlite:///./trading_saas.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    broker_email = Column(String)
    broker_password_enc = Column(String)
    broker_type = Column(String)
    trading_amount = Column(Float)
    max_daily_loss = Column(Float)
    target_profit = Column(Float)

def create_admin():
    db = SessionLocal()
    email = "daveymena16@gmail.com"
    password = "6715320Dvd."
    
    # Usar SHA-256 simple para este script de emergencia para evitar problemas de bcyrpt
    # Solo para asegurar que entras hoy mismo al Dashboard
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    # Limpiar si existe
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()

    admin = User(
        email=email,
        hashed_password=hashed,
        is_active=True,
        trading_amount=1.0,
        max_daily_loss=10.0,
        target_profit=20.0
    )
    db.add(admin)
    db.commit()
    print(f"✅ ¡SaaS EN LÍNEA! Usuario {email} creado con éxito.")
    db.close()

if __name__ == "__main__":
    create_admin()
