from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Ensure the DATABASE_URL always uses the asyncpg dialect.
# Neon/Supabase connection strings use plain 'postgresql://' which
# causes SQLAlchemy to fall back to psycopg2 (not installed).
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

# asyncpg requires 'ssl=require', not 'sslmode=require'
db_url = db_url.replace("sslmode=require", "ssl=require")

# Create async engine
engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
)


# Async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for retrieving async session."""
    async with AsyncSessionLocal() as session:
        yield session
