from django.urls import path
from .views import *

app_name = 'panel'


urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('create_task/', CreateTaskVies.as_view(), name='create_task'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('tasks/add/', AddTaskView.as_view(), name='add_task'),
    path('tasks/<int:task_id>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/edit/', EditTaskView.as_view(), name='edit_task'),
    path('tasks/<int:task_id>/complete/', CompleteTaskView.as_view(), name='complete_task'),
    path('tasks/<int:task_id>/delete/', DeleteTaskView.as_view(), name='delete_task'),
    path('tasks/archived_tasks/', ArchivedTasksView.as_view(), name='archived_tasks'),
    path('tasks/check_task/', CheckTaskView.as_view(), name='check_tasks'),
    path('tasks/check_task/<int:task_id>/', CheckTaskDetailView.as_view(), name='check_task'),
    path('users/add/', AddUserView.as_view(), name='add_user'),
    path('usertask/<int:user_task_id>', UserTaskDetailView.as_view(), name='user_task_detail'),
]