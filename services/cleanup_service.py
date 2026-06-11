import asyncio

from core.database import AsyncSessionLocal
from repository.reset_token_repositery import ResetRepositery


async def _cleanup():
    async with AsyncSessionLocal as db:
        repo = ResetRepositery(db)
        await repo.delete_token()


def cleanup_expired_token():
    asyncio.run(_cleanup())
