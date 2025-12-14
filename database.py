import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from environment variable (Render sets this automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    print("🚀 LOADING: Utilisation de la base de données POSTGRESQL (Render)")
    # Render uses postgres:// but SQLAlchemy requires postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Create engine for PostgreSQL
    engine = create_engine(DATABASE_URL)
else:
    print("⚠️ LOADING: Utilisation de la base de données SQLITE (Local)")
    # Fallback: Use SQLite for local development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./industrie_v6.db"
    
    # Create engine for SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
