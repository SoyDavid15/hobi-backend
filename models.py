from sqlalchemy import Column, Integer, String, DateTime, func
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
    
class Foto(Base):
    __tablename__ = "fotos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # 👈 COLUMNA AGREGADA
    nombre = Column(String, index=True)
    ruta = Column(String)
    fecha = Column(DateTime, server_default=func.now()) 
    tamanio = Column(Integer)
    
class UserProgress(Base):
    __tablename__ = "user_progress"
    
    user_id = Column(String, primary_key=True, index=True) # Assuming UUID string from Supabase
    completed_challenges = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    last_completed_date = Column(DateTime, nullable=True)

Base.metadata.create_all(engine)