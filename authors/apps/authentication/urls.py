"""imports modules."""
from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

app_name = "authentication"
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user-retrieve-update"),
    path('users/', RegistrationAPIView.as_view(), name="user-register"),
    path('users/login/', LoginAPIView.as_view(), name="user-login"),
]
