from django.urls import path
from .views import ProfileListView, ProfileGetView

app_name = 'profiles'

urlpatterns = [
    path('', ProfileListView.as_view()),
    path('<str:username>/', ProfileGetView.as_view()),
]
