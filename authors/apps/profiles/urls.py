from django.urls import path
from .views import ProfileListView

app_name = 'profiles'

urlpatterns = [
    path('profiles/', ProfileListView.as_view()),
]
