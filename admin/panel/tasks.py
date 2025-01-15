import ast
from celery import shared_task
from django.utils import timezone
from asgiref.sync import async_to_sync  # Для работы с асинхронными функциями в Celery

from .models import Task, UserTask, User
from .views import get_channel_members_count



@shared_task
def update_task_status():
    now = timezone.now()
    # Находим задания, у которых end_time прошло, но статус еще активный
    tasks_to_archive = Task.objects.filter(end_time__lte=now, status='1')


    # Обрабатываем каждую задачу отдельно
    for task in tasks_to_archive:
        # Получаем chat_id канала, связанного с задачей
        channel = task.channels.chat_id

        # Получаем список участников канала (синхронный вызов асинхронной функции)
        members = async_to_sync(get_channel_members_count)(int(channel))

        # Преобразуем строку в список, если это необходимо
        if isinstance(members, str):
            members = ast.literal_eval(members)

        # Обрабатываем каждого участника
        for member in members:
            user_id = int(member)
            user = User.objects.get(user_id=user_id)
            if UserTask.objects.filter(user=user, task=task).exists():
                UserTask.objects.create(
                    user=user,
                    task=task,
                    status='missed',
                )
    tasks_to_archive.update(status='0')


