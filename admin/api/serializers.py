# api/serializers.py
from rest_framework import serializers
from panel.models import User, Task, UserTask, Channel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Включаем все поля модели

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = '__all__'


class ChannelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'