from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

database_connection_string = os.getenv("DATABASE_CONNECTION_STRING")

engine = create_engine(database_connection_string, pool_pre_ping=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

