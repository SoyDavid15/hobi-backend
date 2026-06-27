import hashlib
from datetime import date, datetime, timezone
from pydantic import BaseModel

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

# Importaciones de tu base de datos y modelos
from database import engine, SessionLocal
import models
from models import Retos, UserProgress

class ChallengeRequest(BaseModel):
    user_id: str

# Importamos el router de las fotos (asegúrate de que el archivo se llame uploadPhoto.py)
from uploadPhoto import router as photo_router

# 1. Crear las tablas (incluyendo "fotos" y "retos" en PostgreSQL)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hobi API",
    description="API para retos diarios y subida de fotos a Supabase"
)

# 2. Incluir el router de fotos (esto añade el endpoint POST /upload-photo automáticamente)
app.include_router(photo_router)

# 3. Dependencia de Base de Datos corregida
def get_db():
    db = SessionLocal()  # <-- Esto evita los problemas de conexión
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------------------------------- #
# Lógica de Retos Diarios
# --------------------------------------------------------------------------- #

def get_daily_seed() -> float:
    """Genera un número flotante único entre -1.0 y 1.0 basado en la fecha de hoy para PostgreSQL"""
    today_str = str(date.today())
    hash_object = hashlib.md5(today_str.encode())
    hash_hex = hash_object.hexdigest()
    seed = int(hash_hex[:8], 16) / 4294967295.0
    return (seed * 2) - 1


@app.get('/retos')
async def read_root(db: Session = Depends(get_db)):
    # 1. Fijar la semilla aleatoria en PostgreSQL para el día de hoy
    seed_value = get_daily_seed()
    db.execute(func.setseed(seed_value))
    
    # 2. Realizar la consulta ordenada por la semilla diaria fija
    reto = db.query(Retos).order_by(func.random()).first()

    if not reto:
        raise HTTPException(status_code=404, detail="No hay retos disponibles")
    
    # 3. Retornar un diccionario estructurado (clave: valor)
    return {
        "Musica": reto.Musica,
        "Lectura": reto.Lectura,
        "Cine_y_Television": reto.Cine_y_Television,
        "Videojuegos": reto.Videojuegos,
        "Comida": reto.Comida,
        "Deporte": reto.Deporte,
        "Salir": reto.Salir,
        "Arte": reto.Arte
    }

# --------------------------------------------------------------------------- #
# Lógica de Progreso de Usuario
# --------------------------------------------------------------------------- #

@app.get('/progreso/{user_id}')
async def get_progreso(user_id: str, db: Session = Depends(get_db)):
    progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
    if not progress:
        return {"completed_challenges": 0, "streak": 0, "last_completed_date": None}
    
    # Validar si la racha sigue vigente
    if progress.last_completed_date:
        today = datetime.now(timezone.utc).date()
        last_date = progress.last_completed_date.date()
        diff_days = (today - last_date).days
        
        if diff_days > 1:
            progress.streak = 0
            db.commit()

    return {
        "completed_challenges": progress.completed_challenges,
        "streak": progress.streak,
        "last_completed_date": progress.last_completed_date.isoformat() if progress.last_completed_date else None
    }

@app.post('/retos/realizado')
async def mark_reto_realizado(req: ChallengeRequest, db: Session = Depends(get_db)):
    progress = db.query(UserProgress).filter(UserProgress.user_id == req.user_id).first()
    today = datetime.now(timezone.utc)
    
    if not progress:
        progress = UserProgress(
            user_id=req.user_id,
            completed_challenges=1,
            streak=1,
            last_completed_date=today
        )
        db.add(progress)
    else:
        if progress.last_completed_date:
            last_date = progress.last_completed_date.date()
            today_date = today.date()
            diff_days = (today_date - last_date).days
            
            if diff_days == 1:
                progress.streak += 1
            elif diff_days > 1:
                progress.streak = 1
            elif diff_days == 0 and progress.streak == 0:
                progress.streak = 1
        else:
            progress.streak = 1
            
        progress.completed_challenges += 1
        progress.last_completed_date = today
    
    db.commit()
    db.refresh(progress)
    return {
        "message": "Progreso actualizado",
        "completed_challenges": progress.completed_challenges,
        "streak": progress.streak
    }