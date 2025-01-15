# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .queues import response_queue





class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Принимаем соединение
        await self.accept()
        # Добавляем подключение в группу "notifications"
        await self.channel_layer.group_add("notifications", self.channel_name)
        print("Бот подключился к WebSocket и добавлен в группу 'notifications'")

    async def disconnect(self, close_code):
        # Удаляем подключение из группы "notifications"
        await self.channel_layer.group_discard("notifications", self.channel_name)
        print("Бот отключился от WebSocket и удален из группы 'notifications'")

    async def receive(self, text_data):
        # Обрабатываем входящие сообщения от бота
        try:
            data = json.loads(text_data)
            print(f"Получено сообщение от бота: {data}")

            if 'action' in data and data['action'] == 'channel_members_count':
                # Обрабатываем ответ от бота
                members_count = data.get('members_count')

                # Помещаем ответ в очередь
                await response_queue.put({
                    'action': 'channel_members_count',
                    'members_count': members_count,
                })

        except Exception as e:
            print(f"Ошибка при обработке сообщения от бота: {e}")

    async def send_notification(self, event):
        # Отправляем уведомление боту
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))
        print(f"Уведомление отправлено боту: {message}")

    async def get_channel_members_count(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message 
        }))
        print(f"Уведомление отправлено боту: {message}")

    

