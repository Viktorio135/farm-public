# api/urls.py
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/add/', views.UserAddView.as_view(), name='add_user'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('usertasks/', views.UserTaskView.as_view(), name='usertasks'),
]