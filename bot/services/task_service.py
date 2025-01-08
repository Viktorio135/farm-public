import aiohttp
from config import API_URL

async def get_tasks(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}tasks/", data={"user_id": user_id}) as response:
            if response.status == 200:
                return await response.json()
            return []

async def create_user_task(user_id, task_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}usertasks/", data={"user_id": user_id, "task_id": task_id}) as response:
            return response.status == 201