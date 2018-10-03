from django.urls import path
from .views import ProfileListView, ProfileGetView

app_name = 'profiles'

urlpatterns = [
    path('profiles/', ProfileListView.as_view()),
    path('profiles/<str:username>/', ProfileGetView.as_view()),
]
