from django.db import models



def confirmation_upload_path(instance, filename):
    return f'confirmations/{filename}'

def examples_upload_path(instance, filename):
    return f'task_examples/{filename}'


class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.BooleanField(default=False)
    balance = models.FloatField(default=0.0)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class Channel(models.Model):
    name = models.CharField(max_length=200)
    chat_id = models.IntegerField()

    def __str__(self):
        return self.name[:50]+'...'


class Task(models.Model):

    STATUS_CHOISE = {
        ('1', 'active'),
        ('0', 'archive')
    }

    id = models.AutoField(primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOISE,
        default=1,
    )
    required_subscriptions = models.IntegerField(blank=True, null=True)
    reward = models.FloatField()
    channels = models.ForeignKey(Channel, blank=True, on_delete=models.CASCADE)
    example = models.ImageField(upload_to=examples_upload_path)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name

class UserTask(models.Model):

    STATUS_CHOISE = {
        'pending': 'Ожидает проверки',
        'approved': 'Выполнено',
        'rejected': 'Отклонено',
        'missed': 'Пропущенные'
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOISE, default='pending')
    screenshot = models.ImageField(upload_to=confirmation_upload_path, null=True, blank=True)
    feedback = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.name}"

class Payout(models.Model):
    date = models.DateTimeField(auto_now_add=True)  # Дата выплаты
    is_paid = models.BooleanField(default=False)  # Флаг, указывающий, была ли выплата произведена

    def __str__(self):
        return f"{self.user.username} - {self.amount} руб. ({self.payout_date})"

class Transaction(models.Model):

    TYPE_CHOISE = {
        'completed_task': 'выполненное задание',
        'manual_crediting': 'ручное зачисление',
        'disbersement': 'выплата'
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    amount = models.FloatField()
    type = models.CharField(max_length=20, choices=TYPE_CHOISE) 
    comment = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    payout_id = models.ForeignKey(Payout, on_delete=models.CASCADE, related_name='payout', null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.username} - {self.type} {self.amount}"
    


class Folder(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class FolderUser(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_folders')

    class Meta:
        unique_together = ('folder', 'user')

    def __str__(self):
        return f"{self.folder.name} - {self.user.username}"