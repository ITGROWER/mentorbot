import asyncpg
import asyncio
import os
from tgbot.config import create_config

async def test_pg():
    config = create_config()
    dsn = config.postgres.build_dsn()
    conn = await asyncpg.connect(dsn)
    print("✅ Connected to PostgreSQL")
    await conn.close()

asyncio.run(test_pg())
