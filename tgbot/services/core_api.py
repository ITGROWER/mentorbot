import os, aiohttp

CORE_URL = os.getenv("CORE_URL", "http://localhost:8000")

async def create_mentor(user_id: str, description: str, goal: str | None):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            f"{CORE_URL}/v1/mentors/init",
            json={"user_id": user_id, "description": description, "goal": goal},
            timeout=30,
        )
        resp.raise_for_status()
        return await resp.json()        # {"mentor": {...}}
