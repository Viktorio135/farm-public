import json
import ast


from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Count, Q


from admin.consumers import response_queue
from .serializers import TaskSerializer
from .models import User, Task, UserTask, Channel


async def get_channel_members_count(channel_id):
    channel_layer = get_channel_layer()

    # Отправляем запрос боту через WebSocket
    await channel_layer.group_send(
        "notifications",  # Группа, к которой подключен бот
        {
            "type": "get_channel_members_count",  # Метод в Consumer
            "message": json.dumps({
                'action': 'get_channel_members_count',
                'channel_id': channel_id,
            }),
        }
    )

    # Ждем ответа от бота
    response = await response_queue.get()
    return response['members_count']




async def send_websocket_notification(chat_id, message_text):
    channel_layer = get_channel_layer()
    try:
        await channel_layer.group_send(
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




class IndexPageView(View):
    async def get(self, request, *args, **kwargs):
        active_tasks = await sync_to_async(Task.objects.filter(status=1).count)()
        archived_tasks = await sync_to_async(Task.objects.filter(status=0).count)()
        total_users = await sync_to_async(User.objects.count)()
        context = {
            'active_tasks': active_tasks,
            'archived_tasks': archived_tasks,
            'total_users': total_users            
        }
        return await sync_to_async(render)(request, 'admin_panel/index.html', context=context)
    
class CreateTaskVies(View):
    async def get(self, request, *args, **kwargs):
        channels = await sync_to_async(list)(Channel.objects.all())
        context = {'channels': channels}
        print(context)
        return await sync_to_async(render)(request, 'admin_panel/create_task.html', context)
    
    async def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('channel_name'),
            'link': request.POST.get('channel_link'),
            'channels': request.POST.get('channels'),
            'reward': request.POST.get('reward'),
            'end_time': request.POST.get('end_time'),
            'example': request.FILES.get('example'),
        }

        channel = await sync_to_async(Channel.objects.get)(id=data['channels'])

        required_subscriptions = await get_channel_members_count(channel.chat_id)
        required_subscriptions = ast.literal_eval(required_subscriptions)
        data['required_subscriptions'] = len(required_subscriptions)

        # Валидация данных с помощью сериализатораxw
        serializer = TaskSerializer(data=data)
        try:
            await sync_to_async(serializer.is_valid)(raise_exception=True)
        except ValidationError as e:
            # Если есть ошибки, возвращаем форму с ошибками
            return await sync_to_async(render)(
                request,
                'admin_panel/create_task.html',
                {'errors': e.detail}
            )

        # Создаем задание асинхронно
        task = await sync_to_async(Task.objects.create)(
            name=serializer.validated_data['name'],
            channels=serializer.validated_data['channels'],
            link=serializer.validated_data['link'],
            required_subscriptions=serializer.validated_data['required_subscriptions'],
            reward=serializer.validated_data['reward'],
            end_time=serializer.validated_data['end_time'],
            example=serializer.validated_data['example'],
            status='1'  # По умолчанию задание активно
        )

        # Перенаправляем на страницу списка заданий
        return redirect('panel:task_list')




@method_decorator(csrf_exempt, name='dispatch')
class TaskListView(View):
    async def get(self, request):
        # Получаем все активные задания с аннотациями для подсчета задач по статусам
        tasks = await sync_to_async(list)(
            Task.objects.filter(status='1').annotate(
                completed_count=Count('usertask', filter=Q(usertask__status='approved')),
                rejected_count=Count('usertask', filter=Q(usertask__status='rejected')),
                pending_count=Count('usertask', filter=Q(usertask__status='pending')),
            )
        )
        for task in tasks:
            print(task.completed_count, task.id)
        

        # Подсчет общего количества активных заданий
        active_tasks_count = await sync_to_async(Task.objects.filter(status='1').count)()

        # Подсчет общего количества архивных заданий
        archived_tasks_count = await sync_to_async(Task.objects.filter(status='0').count)()

        # Подсчет общего количества заданий
        total_tasks_count = await sync_to_async(Task.objects.count)()

        # Подготовка контекста для шаблона
        context = {
            'tasks': tasks,  # Уже отфильтрованы по статусу '1' и содержат счетчики
            'active_tasks_count': active_tasks_count,  # Общее количество активных заданий
            'archived_tasks_count': archived_tasks_count,  # Общее количество архивных заданий
            'total_tasks_count': total_tasks_count,  # Общее количество заданий
        }


        # Рендерим шаблон с контекстом
        return await sync_to_async(render)(request, 'admin_panel/tasks.html', context=context)


class CheckTaskView(View):
    async def get(self, request):
        context = {}

        # Получаем UserTask с подгрузкой user и task
        user_tasks = await sync_to_async(UserTask.objects.select_related('user', 'task').filter)(status='pending')

        # Получаем все каналы
        channels = await sync_to_async(list)(Channel.objects.all())

        # Добавляем данные в контекст
        context['user_tasks'] = user_tasks
        context['channels'] = channels

        # Рендерим шаблон асинхронно
        return await sync_to_async(render)(request, 'admin_panel/check_tasks.html', context=context)
    

class CheckTaskDetailView(View):
    async def get(self, request, task_id):
        context = {}
        task_data = await sync_to_async(get_object_or_404)(UserTask, id=task_id)
        context['task_data'] = task_data
        return await sync_to_async(render)(request, 'admin_panel/review_task.html', context)
    
    async def post(self, request, task_id):
        status = request.POST.get('status')
        feedback = request.POST.get('feedback')

        # Получаем задачу асинхронно
        task = await sync_to_async(get_object_or_404)(UserTask, id=task_id)

        # Обновляем статус и обратную связь
        task.status = status
        task.feedback = feedback
        await sync_to_async(task.save)()
        if status == 'approved':
            # Получаем связанный объект Task асинхронно
            task_obj = await sync_to_async(lambda: task.task)()
            reward = task_obj.reward

            # Получаем пользователя асинхронно
            user = await sync_to_async(lambda: task.user)()
            user.balance = user.balance + reward
            await sync_to_async(user.save)()

            # Отправляем уведомление через WebSocket
            message_text = (
                f"Ваше задание '{task_obj.name}' было проверено.\n"
                f"Статус: Одобрено ✅\n"
                f"Вознаграждение: {reward} руб.\n"
            )
        elif status == 'rejected':
            message_text = (
                f"Ваше задание '{task_obj.name}' было проверено.\n"
                f"Статус: Отклонено ❌\n"
                f"Обратная связь: {feedback}" if feedback != "None" else ""
            )
        if feedback != "None":
            message_text += f"Обратная связь: {feedback}"
        await send_websocket_notification(user.user_id, message_text)


        return redirect('panel:check_tasks')

    


class UserListView(View):
    async def get(self, request):
        users = await sync_to_async(list)(User.objects.all())
        return await sync_to_async(render)(request, 'admin_panel/users.html', {'users': users})
    
@method_decorator(csrf_exempt, name='dispatch')
class AddTaskView(View):
    async def get(self, request):
        return render(request, 'admin_panel/add_task.html')

    async def post(self, request):
        channel_name = request.POST.get('channel_name')
        channel_link = request.POST.get('channel_link')
        reward = request.POST.get('reward')
        await sync_to_async(Task.objects.create)(channel_name=channel_name, channel_link=channel_link, reward=reward)
        return redirect('task_list')

@method_decorator(csrf_exempt, name='dispatch')
class AddUserView(View):
    async def get(self, request):
        return render(request, 'admin_panel/add_user.html')

    async def post(self, request):
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        await sync_to_async(User.objects.create)(user_id=user_id, username=username)
        return redirect('user_list')
    

@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    async def get(self, request, user_id):
        # Получаем пользователя и его задания
        user = await sync_to_async(get_object_or_404)(User, user_id=user_id)
        user_tasks = await sync_to_async(list)(UserTask.objects.filter(user=user))

        # Разделяем задания на выполненные и текущие
        completed_tasks = [task for task in user_tasks if task.status == 'approved']
        pending_tasks = [task for task in user_tasks if task.status == 'pending']
        rejected_tasks = [task for task in user_tasks if task.status == 'rejected']
        missed_tasks = [task for task in user_tasks if task.status == 'missed']

        # Контекст для шаблона
        context = {
            'user': user,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'rejected_tasks': rejected_tasks,
            'missed_tasks': missed_tasks,
        }
        return await sync_to_async(render)(request, 'admin_panel/user_detail.html', context)
    
    # async def post(self, request, user_id):
    #     # Получаем пользователя и его задания
    #     user = await sync_to_async(get_object_or_404)(User, user_id=user_id)
    #     user_tasks = await sync_to_async(list)(UserTask.objects.filter(user=user))

    #     # Разделяем задания на выполненные, текущие и отклоненные
    #     completed_tasks = [task for task in user_tasks if task.status == 'approved']
    #     pending_tasks = [task for task in user_tasks if task.status == 'pending']
    #     rejected_tasks = [task for task in user_tasks if task.status == 'rejected']

    #     # Преобразуем объекты в словари
    #     user_dict = {
    #         "user_id": user.user_id,
    #         "username": user.username,
    #         "balance": user.balance,
    #         "phone_number": user.phone_number,
    #         "last_activity": user.last_activity.isoformat() if user.last_activity else None,
    #     }

    #     def task_to_dict(task):
    #         return {
    #             "task_id": task.task.id,
    #             "channel_name": task.task.channel_name,
    #             "channel_link": task.task.channel_link,
    #             "reward": task.task.reward,
    #             "status": task.status,
    #             "screenshot": task.screenshot,
    #             "feedback": task.feedback,
    #         }

    #     completed_tasks_dict = [task_to_dict(task) for task in completed_tasks]
    #     pending_tasks_dict = [task_to_dict(task) for task in pending_tasks]
    #     rejected_tasks_dict = [task_to_dict(task) for task in rejected_tasks]

    #     # Контекст для JSON-ответа
    #     context = {
    #         "user": user_dict,
    #         "completed_tasks": completed_tasks_dict,
    #         "pending_tasks": pending_tasks_dict,
    #         "rejected_tasks": rejected_tasks_dict,
    #     }

    #     return JsonResponse(context)