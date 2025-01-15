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

    tasks_to_archive.update(status='0')


