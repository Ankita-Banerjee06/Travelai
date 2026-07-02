from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Neon DB requires SSL; add sslmode=require if not already in the URL
database_url = settings.DATABASE_URL
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set! "
        "Add it as a Repository Secret in HF Spaces Settings, e.g.: "
        "postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )
if "sslmode" not in database_url:
    separator = "&" if "?" in database_url else "?"
    database_url = f"{database_url}{separator}sslmode=require"

engine = create_engine(
    database_url,
    pool_pre_ping=True,       # Detect stale connections (important for serverless)
    pool_recycle=300,          # Recycle connections every 5 min to avoid Neon idle timeout
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()