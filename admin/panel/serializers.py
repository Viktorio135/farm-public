from rest_framework import serializers
from .models import Task, Groups

class TaskSerializer(serializers.ModelSerializer):
    # Поле groups принимает список идентификаторов групп
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Groups.objects.all(),  # Указываем queryset для валидации
        many=True,  # Разрешаем множественный выбор
        required=True  # Поле обязательно
    )

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
            'channel',
            'groups',
            'reminder_start_time', 
            'reminder_end_time'
        ]
        extra_kwargs = {
            'id': {'required': False, 'allow_null': True},
            'end_time': {'required': False, 'allow_null': True},
            'reminder_start_time': {'required': False, 'allow_null': True},
            'reminder_end_time': {'required': False, 'allow_null': True}
        }

    def to_internal_value(self, data):
        # Преобразуем пустые строки в None для reminder_start_time и reminder_end_time
        if 'reminder_start_time' in data and data['reminder_start_time'] == '':
            data['reminder_start_time'] = None
        if 'reminder_end_time' in data and data['reminder_end_time'] == '':
            data['reminder_end_time'] = None
        if 'end_time' in data and data['end_time'] == '':
            data['end_time'] = None
        return super().to_internal_value(data)
    
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