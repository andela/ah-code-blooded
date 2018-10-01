from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ResetPasswordAPIView, ComfirmPasswordResetAPIView,
)

app_name = "authentication"
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user-retrieve-update"),
    path('users/', RegistrationAPIView.as_view(), name="user-register"),
    path('users/login/', LoginAPIView.as_view(), name="user-login"),
    path('users/password_reset/', ResetPasswordAPIView.as_view(), name="password_reset"),
    path('users/password_reset/confirm', ComfirmPasswordResetAPIView.as_view(), name="confirm_password_reset"),
]
