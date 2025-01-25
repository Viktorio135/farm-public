from django.urls import path
from .views import *

app_name = 'panel'


urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),



    #tasks

    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('create_task/', CreateTaskView.as_view(), name='create_task'),
    path('tasks/add/', AddTaskView.as_view(), name='add_task'),
    path('tasks/<int:task_id>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/edit/', EditTaskView.as_view(), name='edit_task'),
    path('tasks/<int:task_id>/complete/', CompleteTaskView.as_view(), name='complete_task'),
    path('tasks/<int:task_id>/delete/', DeleteTaskView.as_view(), name='delete_task'),
    path('tasks/archived_tasks/', ArchivedTasksView.as_view(), name='archived_tasks'),
    path('tasks/check_task/', CheckTaskView.as_view(), name='check_tasks'),
    path('tasks/check_task/<int:task_id>/', CheckTaskDetailView.as_view(), name='check_task'),


    #users


    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path("users/approve_task/<int:user_id>/", ApproveTaskView.as_view(), name="approve_task"),
    path('users/statistics/', UserGroupStatisticsView.as_view(), name='users_statistics'),
    path('user/<int:user_id>/add_funds/', AddFundsView.as_view(), name='add_funds'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/delete-user/', DeleteUserView.as_view(), name='delete_user'),
    path('users/add/', AddUserView.as_view(), name='add_user'),
    path('usertask/<int:user_task_id>', UserTaskDetailView.as_view(), name='user_task_detail'),   


    #channels
    path("channels/<int:channel_id>/", ChannelDetailView.as_view(), name="channel_detail"),
    path("channels/create/", CreateChannelView.as_view(), name="create_channel"),
    path("channels/", ChannelListView.as_view(), name="channel_list"),
    path("channels/delete/<int:channel_id>/", DeleteChannelView.as_view(), name="delete_channel"),



    #groups


    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/create/', CreateGroupView.as_view(), name='create_group'),
    path('groups/<int:group_id>/', GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:group_id>/edit/', EditGroupView.as_view(), name='edit_group'),
    path('groups/<int:group_id>/delete/', DeleteGroupView.as_view(), name='delete_group'),


    #folders


    path('folders/', FolderListView.as_view(), name='folder_list'),
    path('folders/create/', FolderCreateView.as_view(), name='folder_create'),
    path('folders/<int:folder_id>/', FolderDetailView.as_view(), name='folder_detail'),
    path('folders/delete/<int:folder_id>/', FolderDeleteView.as_view(), name='folder_delete'),
    path('folders/<int:folder_id>/remove-users/', FolderRemoveUsersView.as_view(), name='folder_remove_users'),


    #payouts

    path('payout/', PayoutView.as_view(), name='payout_list'),
    path('payout/reset/', ResetBalancesView.as_view(), name='payout_reset'),
    path('payout/send_information/', SendPayoutInformation.as_view(), name='send_information'),
    path('payout/export-payouts-to-excel/', ExportPayoutsToExcelView.as_view(), name='export_payouts_to_excel'),


    #referals


    path('referrals/create/', CreateReferralView.as_view(), name='create_referral'),
    path('referrals/', ReferralListView.as_view(), name='referral_list'),
    path('referrals/delete/<int:referral_id>/', DeleteReferralView.as_view(), name='delete_referral'),
]