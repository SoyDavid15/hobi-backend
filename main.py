from fastapi import FastAPI, Depends
from database import engine
from models import Retos
from sqlalchemy.orm import Session
from sqlalchemy import func


app = FastAPI()

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

@app.get('/retos')
async def read_root(db: Session = Depends(get_db)):
    retos = db.query(Retos).order_by(func.random()).first()

    if not retos:
        return {"No hay retos"}
    else:
        return {"Reto:", "Musica", retos.Musica,
        "Lectura",retos.Lectura,
        "Cine y Television", retos.Cine_y_Television,
        "Videojuegos", retos.Videojuegos,
        "Comida", retos.Comida,
        "Deporte", retos.Deporte,
        "Salir", retos.Salir,
        "Arte", retos.Arte}