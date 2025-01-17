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
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.db.models.functions import Coalesce



from admin.queues import response_queue
from .serializers import TaskSerializer
from .models import User, Task, UserTask, Channel, Transaction





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
        user_ids = [int(user) for user in required_subscriptions]
        users = await sync_to_async(list)(User.objects.filter(user_id__in=user_ids))

        # Создаем записи UserTask для каждого пользователя
        user_tasks = [
            UserTask(user=user, task=task, status='missed')
            for user in users
        ]

        # Используем bulk_create для создания всех записей за один запрос
        await sync_to_async(UserTask.objects.bulk_create)(user_tasks)

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


class TaskDetailView(View):
    async def get(self, request, task_id):
        task = await sync_to_async(get_object_or_404)(Task, id=task_id)

        completed_tasks = await sync_to_async(list)(UserTask.objects.filter(task=task, status='approved'))
        pending_tasks = await sync_to_async(list)(UserTask.objects.filter(task=task, status='pending'))
        rejected_tasks = await sync_to_async(list)(UserTask.objects.filter(task=task, status='rejected'))
        missed_tasks = await sync_to_async(list)(UserTask.objects.filter(task=task, status='missed', task__status='0'))

        context = {
            'task': task,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'rejected_tasks': rejected_tasks,
            'missed_tasks': missed_tasks,
        }

        return await sync_to_async(render)(request, 'admin_panel/task_detail.html', context)


class EditTaskView(View):
    async def post(self, request, task_id):
        task = await sync_to_async(get_object_or_404)(Task, id=task_id)

        # Обновляем данные задания
        task.name = request.POST.get('name')
        task.link = request.POST.get('link')
        task.required_subscriptions = int(request.POST.get('required_subscriptions'))
        task.reward = float(request.POST.get('reward'))
        task.end_time = request.POST.get('end_time')

        await sync_to_async(task.save)()
        return redirect('panel:task_detail', task_id=task.id)
    

class CompleteTaskView(View):
    async def get(self, request, task_id):
        task = await sync_to_async(get_object_or_404)(Task, id=task_id)

        # Меняем статус задания на "архив"
        task.status = '0'
        await sync_to_async(task.save)()

        return redirect('panel:task_detail', task_id=task.id)


class DeleteTaskView(View):
    async def get(self, request, task_id):
        task = await sync_to_async(get_object_or_404)(Task, id=task_id)

        # Удаляем задание
        await sync_to_async(task.delete)()
        return redirect('panel:task_list')


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
        user = await sync_to_async(lambda: task.user)()
        task_obj = await sync_to_async(lambda: task.task)()
        await sync_to_async(task.save)()
        if status == 'approved':
            reward = task_obj.reward
            # Получаем пользователя асинхронно
            user.balance = user.balance + reward
            await sync_to_async(user.save)()
            await sync_to_async(Transaction.objects.create)(
                user=user,
                amount=reward,
                type='completed_task',
                comment=f'Успешное выполнение задания {task_obj.id}'
            )

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

    

class UserTaskDetailView(View):
    async def get(self, request, user_task_id):
        task_data = await sync_to_async(get_object_or_404)(UserTask, id=user_task_id)

        context = {
            'task_data': task_data,
        }

        return await sync_to_async(render)(request, 'admin_panel/user_task_detail.html', context)


class ArchivedTasksView(View):
    async def get(self, request):
        # Фильтруем задачи по статусу "архив" (status='0')
        tasks = await sync_to_async(list)(Task.objects.filter(status='0'))

        # Добавляем аннотации для подсчета выполненных, отклоненных и ожидающих задач
        tasks = await sync_to_async(list)(
            Task.objects.filter(status='0').annotate(
                completed_count=Count('usertask', filter=Q(usertask__status='approved')),
                rejected_count=Count('usertask', filter=Q(usertask__status='rejected')),
                pending_count=Count('usertask', filter=Q(usertask__status='pending')),
                missed_count=Count('usertask', filter=Q(usertask__status='missed')),
            )
        )

        context = {
            'tasks': tasks,
        }

        return await sync_to_async(render)(request, 'admin_panel/archived_tasks.html', context)

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
        user_tasks = await sync_to_async(list)(UserTask.objects.filter(user=user).prefetch_related('task'))

        # Разделяем задания на выполненные и текущие
        completed_tasks = [task for task in user_tasks if task.status == 'approved']
        pending_tasks = [task for task in user_tasks if task.status == 'pending']
        rejected_tasks = [task for task in user_tasks if task.status == 'rejected']
        missed_tasks = [task for task in user_tasks if task.status == 'missed' and task.task.status == '0']
        transactions = await sync_to_async(list)(Transaction.objects.filter(user=user).order_by('-timestamp'))
        if (len(completed_tasks) + len(rejected_tasks) + len(missed_tasks)) != 0:
            completion_rate = ((len(completed_tasks) + len(rejected_tasks)) / (len(completed_tasks) + len(rejected_tasks) + len(missed_tasks))) * 100
        else:
            completion_rate = 0

        # Контекст для шаблона
        context = {
            'user': user,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'rejected_tasks': rejected_tasks,
            'missed_tasks': missed_tasks,
            'transactions': transactions,
            'completion_rate': completion_rate,
        }
        return await sync_to_async(render)(request, 'admin_panel/user_detail.html', context)
    

class AddFundsView(View):
    async def post(self, request, user_id):
        user = await sync_to_async(get_object_or_404)(User, user_id=user_id)
        amount = float(request.POST.get('amount'))
        comment = request.POST.get('comment')

        # Начисляем деньги
        user.balance += amount
        await sync_to_async(user.save)()

        # Логируем транзакцию
        await sync_to_async(Transaction.objects.create)(
            user=user,
            amount=amount,
            type='manual_crediting',
            comment=comment,
        )

        # Добавляем сообщение об успехе

        message_text = (
            f"Вам зачислена награда {amount} руб.\n"
            f"Комментарий к начислению: {comment}"
        )
        await send_websocket_notification(user.user_id, message_text)
        return redirect('panel:user_detail', user_id=user.user_id)
    

class ApproveTaskView(View):
    async def get(self, request, user_task_id):
        user_task = await sync_to_async(get_object_or_404)(UserTask, id=user_task_id)

        # Засчитываем задание
        user_task.status = 'approved'
        await sync_to_async(user_task.save)()

        # Начисляем вознаграждение пользователю
        user = user_task.user
        user.balance += user_task.task.reward
        await sync_to_async(user.save)()

        # Логируем транзакцию
        await sync_to_async(Transaction.objects.create)(
            user=user,
            amount=user_task.task.reward,
            type='completed_task',
            comment=f"Ручное зачитывание задания {user_task.task.id}",
        )
        message_text = f"Задание '{user_task.task.name}' засчитано. Начислено {user_task.task.reward} руб."
        # Добавляем сообщение об успехе
        await send_websocket_notification(user_task.user.user_id, message_text)

        return redirect('panel:user_detail', user_id=user.user_id)
    


class ChannelListView(View):
    async def get(self, request):
        channels = await sync_to_async(list)(Channel.objects.all())
        return await sync_to_async(render)(request, 'admin_panel/channels.html', {'channels': channels})
    

class CreateChannelView(View):
    async def get(self, request):
        return await sync_to_async(render)(request, 'admin_panel/create_channel.html')

    async def post(self, request):
        name = request.POST.get('name')
        chat_id = request.POST.get('chat_id')

        # Создаем канал
        await sync_to_async(Channel.objects.create)(name=name, chat_id=chat_id)
        return redirect('panel:channel_list')

class ChannelDetailView(View):
    async def get(self, request, channel_id):
        channel = await sync_to_async(get_object_or_404)(Channel, id=channel_id)
        total_tasks = await sync_to_async(UserTask.objects.filter(task__channels=channel).count)()
        completed_rask = await sync_to_async(UserTask.objects.filter(task__channels=channel).exclude(status='missed').count)()
        if total_tasks != 0:
            percent = (completed_rask / total_tasks) * 100
        else:
            percent = 100
        return await sync_to_async(render)(request, 'admin_panel/channel_detail.html', {'channel': channel, 'percent': percent})

class EditChannelView(View):
    async def post(self, request, channel_id):
        channel = await sync_to_async(get_object_or_404)(Channel, id=channel_id)

        # Обновляем данные канала
        channel.name = request.POST.get('name')
        channel.chat_id = request.POST.get('chat_id')
        await sync_to_async(channel.save)()
        return redirect('panel:channel_detail', channel_id=channel.id)

class DeleteChannelView(View):
    async def get(self, request, channel_id):
        channel = await sync_to_async(get_object_or_404)(Channel, id=channel_id)
        usertask = await sync_to_async(UserTask.objects.filter(task__channels=channel, status='pending').count)()
        if usertask == 0:
            await sync_to_async(channel.delete)()
        return redirect('panel:channel_list')
    

from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce

class UserChannelStatisticsView(View):
    async def get(self, request):
        # Получаем список всех каналов
        channels = await sync_to_async(list)(Channel.objects.all())

        # Получаем данные о всех пользователях и их статистике
        users = await sync_to_async(list)(
            User.objects.annotate(
                total_missed=Count('usertask', filter=Q(usertask__status='missed', usertask__task__status='0')),
                total_tasks=Count('usertask'),
                completion_rate=ExpressionWrapper(
                    Coalesce(100 * Count('usertask', filter=Q(usertask__status='approved')) / Count('usertask'), 0.0),
                    output_field=FloatField()
                )
            )
        )

        # Для каждого пользователя рассчитываем количество реклам, пропущенных подряд
        for user in users:
            # Получаем все задачи пользователя, отсортированные по времени окончания (от новых к старым)
            user_tasks = await sync_to_async(list)(
                UserTask.objects.filter(user=user).select_related('task__channels').order_by('-task__end_time')
            )

            # Счетчик для количества пропущенных подряд
            last_missed_sequence = 0

            # Проходим по всем задачам пользователя
            for user_task in user_tasks:
                # Если задача пропущена (missed), увеличиваем счетчик
                if user_task.status == 'missed' and user_task.task.status == '0':
                    last_missed_sequence += 1
                # Если задача не пропущена (approved, pending и т.д.), останавливаем подсчет
                else:
                    break

            # Сохраняем количество пропущенных подряд
            user.last_missed_sequence = last_missed_sequence

        # Получаем список user_id для каждого канала
        channel_members = {}
        for channel in channels:
            user_ids = await get_channel_members_count(channel.chat_id)
            user_ids = ast.literal_eval(user_ids)  # Преобразуем строку в список
            channel_members[channel.id] = [int(user_id) for user_id in user_ids]  # Преобразуем user_id в числа

        # Подготовка данных для шаблона
        context = {
            'channels': channels,
            'users': users,
            'channel_members': channel_members,
        }

        return await sync_to_async(render)(request, 'admin_panel/user_channel_statistics.html', context)