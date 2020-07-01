from django.urls import path
from .views import *


urlpatterns = [

    path('notification_list', NotificationListAPIView.as_view(), name="notification"),

]

