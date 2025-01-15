# api/urls.py
from django.urls import path, include
from . import views

app_name = 'api'

urlpatterns = [
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/add/', views.UserAddView.as_view(), name='add_user'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path("usertasks/send_confirmation/", views.SendConfirmationView.as_view(), name='send_confirmation'),
    path('usertasks/', views.UserTaskView.as_view(), name='usertasks'),
    path('channels/get/', views.ChannelsListView.as_view(), name='get_channels'),
]