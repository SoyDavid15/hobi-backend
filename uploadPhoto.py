import os
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from supabase import create_client, Client

# Importaciones de tu proyecto
from database import SessionLocal
from models import Foto

router = APIRouter()

# --- CONFIGURACIÓN DE SUPABASE ---
# Coloca aquí tus credenciales (puedes sacarlas de Project Settings -> API en Supabase)
SUPABASE_URL = "https://lywureazxewyujvjfrcx.supabase.co"  # Ej: "https://xyz.supabase.co"
SUPABASE_KEY = "sb_publishable_eVdP92MbyxJi1h8ZMS78BA_3YG2rCmK"

# Creamos el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nombre del bucket que creaste en Supabase Storage
BUCKET_NAME = "fotos"

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# Dependencia de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1. Validar tipo MIME
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Sube JPEG, PNG, GIF o WebP.",
        )

    # 2. Generar nombre único para la imagen
    _, ext = os.path.splitext(file.filename or ".jpg")
    nombre_unico = f"{uuid.uuid4()}{ext.lower()}"

    # 3. Leer el archivo en memoria
    contenido = await file.read()

    # 4. Subir la imagen física a Supabase Storage
    try:
        # Subimos indicando el content-type para que el navegador sepa que es una imagen
        supabase.storage.from_(BUCKET_NAME).upload(
            path=nombre_unico,
            file=contenido,
            file_options={"content-type": file.content_type}
        )
        # Obtenemos la URL pública que usará tu frontend para mostrarla
        url_publica = supabase.storage.from_(BUCKET_NAME).get_public_url(nombre_unico)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al subir la imagen al Bucket de Supabase: {str(e)}"
        )

    # 5. Registrar los datos (URL, fecha, tamaño) en la tabla PostgreSQL de Supabase
    try:
        foto = Foto(
            nombre=nombre_unico,
            ruta=url_publica,  # Ahora guardamos la URL de internet, no una ruta local
            fecha=datetime.utcnow(),
            tamanio=len(contenido),
        )
        db.add(foto)
        db.commit()
        db.refresh(foto)
        
    except Exception as e:
        # Si la base de datos falla, borramos la imagen del bucket para no dejar archivos huérfanos
        supabase.storage.from_(BUCKET_NAME).remove([nombre_unico])
        raise HTTPException(
            status_code=500, 
            detail=f"Error al registrar en la base de datos: {str(e)}"
        )

    # 6. Responder al frontend con los datos definitivos
    return {
        "mensaje": "Foto subida a Supabase exitosamente",
        "id": foto.id,
        "nombre": foto.nombre,
        "url_imagen": foto.ruta,
        "fecha": foto.fecha.isoformat(),
    }