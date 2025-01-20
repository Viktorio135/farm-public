import ast
from celery import shared_task
from django.utils import timezone
from asgiref.sync import async_to_sync  # Для работы с асинхронными функциями в Celery
from channels.layers import get_channel_layer


from .models import Task, UserTask, User
from .views import get_channel_members_count, send_websocket_notification



def send_websocket_notification_sync(chat_id, message_text):
    """
    Синхронная версия функции отправки сообщения через WebSocket.
    """
    channel_layer = get_channel_layer()
    try:
        print(f"Попытка отправить сообщение в WebSocket: chat_id={chat_id}, text={message_text}")
        async_to_sync(channel_layer.group_send)(
            "notifications",  # Имя группы WebSocket
            {
                "type": "send_notification",  # Метод в Consumer
                "message": {
                    "chat_id": chat_id,
                    "text": message_text,
                },
            },
        )
        print(f"Сообщение отправлено в WebSocket: chat_id={chat_id}, text={message_text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в WebSocket: {e}")



@shared_task
def update_task_status():
    now = timezone.now()
    # Находим задания, у которых end_time прошло, но статус еще активный
    tasks_to_archive = Task.objects.filter(end_time__lte=now, status='1')

    tasks_to_archive.update(status='0')


@shared_task
def send_unsubscribe_reminder(user_task_id):
    # Получаем UserTask по ID
    user_task = UserTask.objects.get(id=user_task_id)
    task = user_task.task

    # Формируем сообщение
    message = (
        f"Напоминание: отпишитесь от канала {task.link}.\n"
        f"Задание: {task.name}\n"
    )

    # Отправляем уведомление через WebSocket
    send_websocket_notification_sync(user_task.user.user_id, message)

    # Обновляем время последнего напоминания
    user_task.last_reminder = timezone.now()
    user_task.save()


@shared_task
def schedule_unsubscribe_reminders():
    now = timezone.now()

    # Получаем задачи, у которых наступила дата напоминания (notification_date)
    tasks_to_remind = Task.objects.filter(reminder_start_time__lte=now)
    print(now)


    for task in tasks_to_remind:
        # Получаем время начала и окончания рассылки (с учетом значений по умолчанию)
        reminder_start_time = task.reminder_start_time
        reminder_end_time = task.reminder_end_time

        # Проверяем, находится ли текущее время в пределах интервала рассылки
        if not (reminder_start_time <= now <= reminder_end_time):
            continue  # Пропускаем задачу, если текущее время вне интервала

        # Получаем все UserTask для этой задачи, которые еще не завершены
        user_tasks = UserTask.objects.filter(task=task, status='approved')

        # Рассчитываем задержку между уведомлениями
        total_users = user_tasks.count()
        if total_users == 0:
            continue

        # Рассчитываем общее время для рассылки (в секундах)
        total_time = (reminder_end_time - reminder_start_time).total_seconds()

        # Задержка между уведомлениями
        delay_between_users = total_time / total_users

        # Планируем уведомления для каждого пользователя с задержкой
        for index, user_task in enumerate(user_tasks):
            delay = index * delay_between_users
            send_unsubscribe_reminder.apply_async(args=[user_task.id], countdown=delay)