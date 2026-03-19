import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql://ztn:ztn%40sim@localhost:5432/ztn_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)
# Keep a scoped session only for legacy `Model.query` convenience accessors.
ScopedQuerySession = scoped_session(SessionFactory)
# Use plain sessionmaker for FastAPI request dependencies and background worker helpers.
SessionLocal = SessionFactory

Base = declarative_base()
Base.query = ScopedQuerySession.query_property()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
