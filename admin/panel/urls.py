from django.urls import path
from .views import TaskListView, UserListView, AddTaskView, AddUserView, UserDetailView, IndexPageView, CreateTaskVies

app_name = 'panel'


urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('create_task/', CreateTaskVies.as_view(), name='create_task'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('tasks/add/', AddTaskView.as_view(), name='add_task'),
    path('users/add/', AddUserView.as_view(), name='add_user'),
]