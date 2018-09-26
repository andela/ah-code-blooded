from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

app_name = "authentication"
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user_ru"),
    path('users/', RegistrationAPIView.as_view(), name="user_register"),
    path('users/login/', LoginAPIView.as_view(), name="user_login"),
]
