from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


from .serializers import TaskSerializer
from .models import User, Task, UserTask


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
        return render(request, 'admin_panel/index.html', context=context)
    
class CreateTaskVies(View):
    async def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/create_task.html')
    
    async def post(self, request, *args, **kwargs):
        data = {
            'channel_name': request.POST.get('channel_name'),
            'channel_link': request.POST.get('channel_link'),
            'required_subscriptions': request.POST.get('required_subscriptions'),
            'reward': request.POST.get('reward'),
            'example': request.FILES.get('example'),
        }

        # Валидация данных с помощью сериализатора
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
            channel_name=serializer.validated_data['channel_name'],
            channel_link=serializer.validated_data['channel_link'],
            required_subscriptions=serializer.validated_data['required_subscriptions'],
            reward=serializer.validated_data['reward'],
            example=serializer.validated_data['example'],
            status=1  # По умолчанию задание активно
        )

        # Перенаправляем на страницу списка заданий
        return redirect('panel:task_list')





@method_decorator(csrf_exempt, name='dispatch')
class TaskListView(View):
    async def get(self, request):
        # Получаем все задания асинхронно
        tasks = await sync_to_async(list)(Task.objects.all())

        # Для каждого задания подсчитываем количество пользователей по статусам
        for task in tasks:
            task.completed_count = await sync_to_async(UserTask.objects.filter(task=task, status='approved').count)()
            task.rejected_count = await sync_to_async(UserTask.objects.filter(task=task, status='rejected').count)()
            task.pending_count = await sync_to_async(UserTask.objects.filter(task=task, status='pending').count)()

        # Подготовка контекста для шаблона
        context = {
            'tasks': tasks,
        }

        # Рендерим шаблон с контекстом
        return await sync_to_async(render)(request, 'admin_panel/tasks.html', context=context)

class UserListView(View):
    async def get(self, request):
        users = await sync_to_async(list)(User.objects.all())
        return render(request, 'admin_panel/users.html', {'users': users})
    
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

        # Контекст для шаблона
        context = {
            'user': user,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'rejected_tasks': rejected_tasks,
        }
        return render(request, 'admin_panel/user_detail.html', context)
    
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