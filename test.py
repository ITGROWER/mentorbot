import asyncpg
import asyncio

async def test_pg():
    conn = await asyncpg.connect("postgresql://user:password@localhost:5432/tgbot")
    print("✅ Connected to PostgreSQL")
    await conn.close()

asyncio.run(test_pg())
