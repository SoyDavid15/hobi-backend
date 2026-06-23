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
        return {"Reto:", retos.Musica,
        retos.Lectura,
        retos.Cine_y_Television,
        retos.Videojuegos,
        retos.Comida,
        retos.Deporte,
        retos.Salir,
        retos.Arte}