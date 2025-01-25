import os
import aiofiles
import aiofiles.os


from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from django.core.files.storage import default_storage



from panel.models import Task, User, UserTask, Groups
from .serializers import UserSerializer, TaskSerializer, UserTaskSerializer, GroupsSerializer


class UserAddView(APIView):
    async def post(self, request):
        user_id = request.data.get('user_id')
        username = request.data.get('username')
        avatar = request.data.get('avatar')

        if not user_id or not username:
            return Response(
                {"error": "user_id and username are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = await User.objects.acreate(user_id=user_id, username=username, avatar=avatar)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    

class UserDetailView(APIView):
    async def get(self, request, user_id):
        try:
            user = await User.objects.aget(user_id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        

class TaskListView(APIView):
    async def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем все задания
        all_tasks = await sync_to_async(list)(Task.objects.filter(status='1'))

        # Получаем задания, которые пользователь уже выполнял
        user_tasks = await sync_to_async(list)(UserTask.objects.filter(user_id=user_id).exclude(status='missed').values_list('task_id', flat=True))

        # Исключаем выполненные задания
        available_tasks = [task for task in all_tasks if task.id not in user_tasks]

        groups = await sync_to_async(list)(Groups.objects.all())
        # Сериализуем задания
        task_serializer = TaskSerializer(available_tasks, many=True)
        group_serializer = GroupsSerializer(groups, many=True)
        tasks_data = await sync_to_async(lambda: task_serializer.data)()
        groups_data = await sync_to_async(lambda: group_serializer.data)()
        response = {
            'tasks': tasks_data,
            'groups': groups_data,
        }
        return Response(response)
    

class SendConfirmationView(APIView):
    async def post(self, request):
        file = request.FILES.get('file')
        task_id = request.POST.get('task_id')
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')

        if file and task_id and user_id and group_id:
            # Сохраняем файл
            dir_path = f'media/screenshots/{str(user_id)}'
            if not await aiofiles.os.path.exists(dir_path):
                await aiofiles.os.makedirs(dir_path, exist_ok=True)
            
            # Асинхронно сохраняем файл
            file_name = f"{dir_path}/{file.name}"
            async with aiofiles.open(file_name, 'wb') as f:
                await f.write(file.read())
            user = await User.objects.aget(user_id=user_id)
            task = await Task.objects.aget(id=task_id, status='1')

            usertask = await UserTask.objects.filter(
                user=user,
                task=task,
                status='missed').afirst()
            
            group = await Groups.objects.aget(id=group_id)

            if usertask:
                # Обновляем существующий UserTask
                usertask.status = 'pending'
                usertask.screenshot = file_name
                usertask.group = group
                await usertask.asave()
            else:
                # Создаем новый UserTask
                await UserTask.objects.acreate(
                    user=user,
                    task=task,
                    status='pending',
                    screenshot=file_name,
                    group=group,
                )
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
    

class UserTaskView(APIView):
    async def post(self, request):
        serializer = UserTaskSerializer(data=request.data)
        if await sync_to_async(serializer.is_valid)():
            await sync_to_async(serializer.save)()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ChannelsListView(APIView):
    async def get(self, request):
        try:
            groups = await sync_to_async(list)(Groups.objects.all())
            serializer = GroupsSerializer(groups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)