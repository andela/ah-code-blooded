from django.urls import path

from authors.apps.articles.views import ArticleAPIView

app_name = "articles"

urlpatterns = [
    path('articles/', ArticleAPIView.as_view(), name="articles"),
]
