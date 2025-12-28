import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql://ztn:ztn%40sim@localhost:5432/ztn_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)

Base = declarative_base()
Base.query = SessionLocal.query_property()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        SessionLocal.remove()
