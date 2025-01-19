from django.urls import path
from .views import *

app_name = 'panel'


urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('create_task/', CreateTaskView.as_view(), name='create_task'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path("users/approve_task/<int:user_id>/", ApproveTaskView.as_view(), name="approve_task"),
    path('users/statistics/', UserChannelStatisticsView.as_view(), name='users_statistics'),
    path('user/<int:user_id>/add_funds/', AddFundsView.as_view(), name='add_funds'),
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
    path('channels/', ChannelListView.as_view(), name='channel_list'),
    path('channels/create/', CreateChannelView.as_view(), name='create_channel'),
    path('channels/<int:channel_id>/', ChannelDetailView.as_view(), name='channel_detail'),
    path('channels/<int:channel_id>/edit/', EditChannelView.as_view(), name='edit_channel'),
    path('channels/<int:channel_id>/delete/', DeleteChannelView.as_view(), name='delete_channel'),
    path('folders/', FolderListView.as_view(), name='folder_list'),
    path('folders/create/', FolderCreateView.as_view(), name='folder_create'),
    path('folders/<int:folder_id>/', FolderDetailView.as_view(), name='folder_detail'),
    path('folders/delete/<int:folder_id>/', FolderDeleteView.as_view(), name='folder_delete'),
    path('folders/<int:folder_id>/remove-users/', FolderRemoveUsersView.as_view(), name='folder_remove_users'),
    path('payout/', PayoutView.as_view(), name='payout_list'),
    path('payout/reset/', ResetBalancesView.as_view(), name='payout_reset'),
]