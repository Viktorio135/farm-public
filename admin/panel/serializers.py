from datetime import timezone
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'channel_name',
            'channel_link',
            'required_subscriptions',
            'reward',
            'example',
        ]

    def validate_required_subscriptions(self, value):
        """Проверка, что количество выполнений больше 0."""
        if value <= 0:
            raise serializers.ValidationError("Количество выполнений должно быть больше 0.")
        return value

    def validate_reward(self, value):
        """Проверка, что вознаграждение больше 0."""
        if value <= 0:
            raise serializers.ValidationError("Вознаграждение должно быть больше 0.")
        return value
