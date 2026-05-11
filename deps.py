from database import AsyncSessionLocal, engine

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session