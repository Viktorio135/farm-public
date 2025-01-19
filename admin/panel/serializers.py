from datetime import timezone
from rest_framework import serializers
from .models import Task, Channel


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',  # Добавляем поле ID
            'name',
            'link',
            'required_subscriptions',
            'reward',
            'end_time',
            'example',
            'channels',
        ]
        extra_kwargs = {
            'id': {'required': False, 'allow_null': True}
        }

    def validate_id(self, value):
        """Проверка уникальности ID только если оно указано."""
        if value is not None:  # Проверяем, только если ID указан
            if Task.objects.filter(id=value).exists():
                raise serializers.ValidationError("Задача с таким ID уже существует.")
        return value

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
