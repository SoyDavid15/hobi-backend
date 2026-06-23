from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class Retos(Base):
    __tablename__ = "Retos"
    id = Column(Integer, primary_key=True)
    Musica = Column(String)
    Lectura = Column(String)
    Cine_y_Television = Column(String)
    Videojuegos = Column(String)
    Comida = Column(String)
    Deporte = Column(String)
    Salir = Column(String)
    Arte = Column(String)
    
    

Base.metadata.create_all(engine)
