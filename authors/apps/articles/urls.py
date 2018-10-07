from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authors.apps.articles.views import ArticleAPIView

app_name = "articles"
router = DefaultRouter()
router.register('articles', ArticleAPIView, base_name="articles")

urlpatterns = [
    path('', include(router.urls)),
]