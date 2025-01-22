# api/serializers.py
from rest_framework import serializers
from panel.models import User, Task, UserTask, Groups, Channels

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Включаем все поля модели


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = '__all__'


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'  # Укажите нужные поля

class ChannelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channels
        fields = '__all__'  # Укажите нужные поля

class TaskSerializer(serializers.ModelSerializer):
    # Вложенные сериализаторы для связанных объектов
    groups = GroupsSerializer(many=True, read_only=True)
    channel = ChannelsSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'link', 'required_subscriptions', 'reward',
            'end_time', 'example', 'channel', 'groups',
            'reminder_start_time', 'reminder_end_time'
        ]