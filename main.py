from fastapi import FastAPI, Depends, HTTPException
from database import engine
from models import Retos
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import hashlib

app = FastAPI()

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

def get_daily_seed() -> float:
    """Genera un número flotante único entre -1.0 y 1.0 basado en la fecha de hoy para PostgreSQL"""
    today_str = str(date.today())
    # Convertimos la fecha en un hash numérico estable
    hash_object = hashlib.md5(today_str.encode())
    hash_hex = hash_object.hexdigest()
    # Transformamos el hash en un valor flotante válido para setseed()
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
