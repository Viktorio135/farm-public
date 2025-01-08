from django.db import models



def confirmation_upload_path(instance, filename):
    return f'confirmations/{filename}'

def examples_upload_path(instance, filename):
    return f'task_examples/{filename}'


class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    bank_details = models.CharField(max_length=255, null=True, blank=True)
    balance = models.FloatField(default=0.0)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

class Task(models.Model):

    STATUS_CHOISE = {
        (1, 'active'),
        (0, 'archive')
    }

    channel_name = models.CharField(max_length=255)
    channel_link = models.CharField(max_length=255)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOISE,
        default=1,  # Опционально: можно указать значение по умолчанию
    )
    required_subscriptions = models.IntegerField(default=1)
    reward = models.FloatField()
    example = models.ImageField(upload_to=examples_upload_path)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.channel_name

class UserTask(models.Model):

    STATUS_CHOISE = {
        'pending': 'Ожидает проверки',
        'approved': 'Выполнено',
        'rejected': 'Отклонено'
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOISE, default='pending')  # pending, approved, rejected
    screenshot = models.ImageField(upload_to=confirmation_upload_path)
    feedback = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.channel_name}"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    type = models.CharField(max_length=20)  # deposit, withdrawal
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} {self.amount}"