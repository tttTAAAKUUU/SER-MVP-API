#!/usr/bin/env python3
"""
Initialize database by creating all tables from SQLAlchemy models
"""
import asyncio
from app.db.database import engine, Base
# Import all models to register them with Base
import app.models.user
import app.models.service
import app.models.booking
import app.models.customer
import app.models.provider
import app.models.rating
import app.models.notification

async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized! Tables created.")

if __name__ == "__main__":
    asyncio.run(init_db())
