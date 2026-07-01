import hashlib
from datetime import date
from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal, engine
import models
from models import Retos
from uploadPhoto import SupabaseStorageService
from challenge_service import ChallengeService

# Inicializar tablas e instancias
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Hobi API Premium", description="Estructura desacoplada y escalable")
storage_service = SupabaseStorageService()

# Dependencia de conexión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_daily_seed() -> float:
    """Genera una semilla determinista basada en la fecha actual."""
    today_str = str(date.today())
    hash_hex = hashlib.md5(today_str.encode()).hexdigest()
    return (int(hash_hex[:8], 16) / 4294967295.0 * 2) - 1


# =========================================================================== #
# ENDPOINT 1: Obtener Retos Diarios
# =========================================================================== #
@app.get('/retos')
async def get_daily_challenges(db: Session = Depends(get_db)):
    """Muestra los retos almacenados usando una semilla aleatoria diaria fija."""
    seed_value = get_daily_seed()
    db.execute(func.setseed(seed_value))
    
    reto = db.query(Retos).order_by(func.random()).first()
    if not reto:
        raise HTTPException(status_code=404, detail="No se encontraron retos en la base de datos.")
    
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


# =========================================================================== #
# ENDPOINT 2: Registrar Reto Realizado (Subida + Progreso sin IA)
# =========================================================================== #
@app.post('/retos/realizado')
async def mark_challenge_as_done(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Recibe la foto del usuario, la almacena en la nube y actualiza sus estadísticas."""
    # 1. Leer archivo
    file_bytes = await file.read()
    
    # 2. Subir a la nube de manera aislada
    try:
        url_publica = await storage_service.upload_file(
            file_bytes=file_bytes,
            original_filename=file.filename,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el almacenamiento en la nube: {str(e)}"
        )
    
    # 3. Procesar las reglas del negocio e insertar en PostgreSQL
    try:
        progress = ChallengeService.process_challenge_completion(
            db=db,
            user_id=user_id,
            filename=file.filename,
            file_size=file.size,
            url_publica=url_publica
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el progreso en la base de datos: {str(e)}"
        )

    # 4. Respuesta limpia y estandarizada
    return {
        "status": "success",
        "message": "Reto completado exitosamente",
        "data": {
            "url_foto": url_publica,
            "streak": progress.streak,
            "completed_challenges": progress.completed_challenges
        }
    }