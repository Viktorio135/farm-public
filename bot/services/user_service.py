import aiohttp
from config import API_URL

async def get_user(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}users/{user_id}/") as response:
            if response.status == 200:
                return await response.json()
            return None

async def create_user(user_id, username, avatar):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}users/add/", data={"user_id": user_id, "username": username, "avatar": avatar}) as response:
            return response.status == 201