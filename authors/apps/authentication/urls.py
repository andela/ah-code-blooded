from django.urls import path
from django.conf.urls import url

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    AccountVerificationView,
    UserRetrieveUpdateAPIView
)

app_name = "authentication"

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user-retrieve-update"),
    path('users/', RegistrationAPIView.as_view(), name="user-register"),
    path('users/login/', LoginAPIView.as_view(), name="user-login"),
    path('account/verify/<str:token>/<str:uid>/', AccountVerificationView.as_view(),
         name='activate-account'),
]
