import aiohttp
from config import API_URL

async def get_tasks(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}tasks/", data={"user_id": user_id}) as response:
            if response.status == 200:
                return await response.json()
            return []
        

async def send_confirmation(image_url, user_id, task_id):
    async with aiohttp.ClientSession() as session:
        # Скачиваем изображение
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                # Отправляем изображение в Django API
                form_data = aiohttp.FormData()
                form_data.add_field('file', image_data, filename='screenshot.png', content_type='image/png')
                form_data.add_field('task_id', str(task_id))
                form_data.add_field('user_id', str(user_id))

                async with session.post(f'{API_URL}usertasks/send_confirmation/', data=form_data) as response:
                    if response.status == 201:
                        return 1
                    else:
                        return 0
            else:
                await 0



async def create_user_task(user_id, task_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}usertasks/", data={"user_id": user_id, "task_id": task_id}) as response:
            return response.status == 201
        

