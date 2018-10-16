from django.urls import path

from .views import (
    AllNotificationsAPIView,
    UnreadNotificationsAPIView,
    ReadNotificationsAPIView,
    UnsentNotificationsAPIView, SentNotificationsAPIView)

app_name = "notifications"

urlpatterns = [
    path('all/', AllNotificationsAPIView.as_view(), name="notifications"),
    path('unread/', UnreadNotificationsAPIView.as_view(), name="unread-notifications"),
    path('read/', ReadNotificationsAPIView.as_view(), name="read-notifications"),
    path('read/<int:pk>/', ReadNotificationsAPIView.as_view(), name="read-notification"),
    path('unsent/', UnsentNotificationsAPIView.as_view(), name="unsent-notifications"),
    path('sent/', SentNotificationsAPIView.as_view(), name="sent-notification")
]
