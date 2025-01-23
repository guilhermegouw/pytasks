import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DATABASE_URL = "sqlite:///pytasks.db"

engine = create_engine(DATABASE_URL, echo=False)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
