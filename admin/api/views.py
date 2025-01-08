from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async


from panel.models import Task, User, Transaction, UserTask
from .serializers import UserSerializer, TaskSerializer, UserTaskSerializer


class UserAddView(APIView):
    async def post(self, request):
        user_id = request.data.get('user_id')
        username = request.data.get('username')

        if not user_id or not username:
            return Response(
                {"error": "user_id and username are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = await User.objects.acreate(user_id=user_id, username=username)
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
            user = await sync_to_async(User.objects.get)(user_id=user_id)
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
        all_tasks = await sync_to_async(list)(Task.objects.all())

        # Получаем задания, которые пользователь уже выполнял
        user_tasks = await sync_to_async(list)(UserTask.objects.filter(user_id=user_id).values_list('task_id', flat=True))

        # Исключаем выполненные задания
        available_tasks = [task for task in all_tasks if task.id not in user_tasks]

        # Сериализуем задания
        serializer = TaskSerializer(available_tasks, many=True)
        return Response(serializer.data)
    

class UserTaskView(APIView):
    async def post(self, request):
        serializer = UserTaskSerializer(data=request.data)
        if await sync_to_async(serializer.is_valid)():
            await sync_to_async(serializer.save)()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)