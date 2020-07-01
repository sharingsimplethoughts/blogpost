from django.urls import path

from .views import *

urlpatterns = [
    path('block/<int:user_id>', UserBlockAPIView.as_view(), name="user-block-api"),
    path('unblock/<int:user_id>', UserUnblockAPIView.as_view(), name="user-unblock-api"),
    path('delete/<int:user_id>', UserDeleteAPIView.as_view(), name="user-delete-api"),
    # path('edit/<int:user_id>', EditMemberAPIView.as_view(), name="admin-user-edit-api"),
    path('delete_faq/<int:faq_id>', FAQDeleteAPIView.as_view(), name="faq_delete"),
    path('block_unblock_post/<int:post_id>', BlockUnblockPostAPIView.as_view(), name="block_post"),
#     notification api
    path('delete_notif/<int:id>', NotificationDeleteAPIView.as_view(), name="notification-delete-api"),
    path('header_data/', AdminHomeHeaderView.as_view(), name='admin-home'),

]
