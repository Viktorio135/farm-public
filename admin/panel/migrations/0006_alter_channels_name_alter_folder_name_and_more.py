# Generated by Django 5.1.4 on 2025-01-24 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0005_alter_task_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channels',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='folder',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='chat_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='payout',
            name='date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='end_time',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('0', 'archive'), ('1', 'active')], db_index=True, default=1, max_length=1),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('completed_task', 'выполненное задание'), ('manual_crediting', 'ручное зачисление'), ('disbersement', 'выплата'), ('referral_bonus', 'реферальный бонус')], db_index=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='usertask',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает проверки'), ('approved', 'Выполнено'), ('rejected', 'Отклонено'), ('missed', 'Пропущенные'), ('referral_bonus', 'Реферальный бонус')], db_index=True, default='pending', max_length=20),
        ),
    ]
