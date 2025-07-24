from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Get the parent directory where .env file is located
parent_dir = Path(__file__).parent.parent

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ai_agent_platform.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    llamaparse_api_key: str | None = None
    gemini_api_key: str | None = None
    
    class Config:
        env_file = parent_dir / ".env"  # Look for .env in parent directory

settings = Settings()

# Print loaded settings for debugging (remove in production)
print(f"🔗 Database URL: {settings.database_url[:50]}...")
print(f"🤖 OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
print(f"🔑 Secret Key: {'✅ Set' if settings.secret_key else '❌ Missing'}")
print(f"🌍 Environment: {settings.environment}")

# Database setup with SSL and connection pooling
if settings.database_url.startswith("postgresql"):
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        pool_size=5,         # Number of connections to maintain
        max_overflow=10,     # Maximum connections beyond pool_size
        connect_args={
            "sslmode": "require",  # Require SSL connection
            "connect_timeout": 30,  # Connection timeout
            "application_name": "AOM_2025_Backend"
        }
    )
else:
    # Use simpler engine for SQLite (no pooling or connect_args)
    engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Database dependency with connection retry logic"""
    db = SessionLocal()
    try:
        # Test the connection
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        db.close()
        # Retry once with a new connection
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            yield db
        except Exception as retry_e:
            db.close()
            raise retry_e
    finally:
        db.close() 