from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, poolclass=NullPool)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tu función get_db se mantiene igual
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()