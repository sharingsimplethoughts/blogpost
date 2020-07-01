from django.urls import path
from .views import *
urlpatterns = [
    path('upload_media', UploadMedia.as_view()),
    path('viewers_list', ViewersListAPIView.as_view()),
    path('send_notification', SendNotification.as_view()),
    path('send_notification_by_topic', SendNotificationByTopic.as_view()),
    path('save_group_member_ids', SaveGroupMemberIds.as_view()),
    path('send_multiple_notification', SendMultipleNotification.as_view())

]

