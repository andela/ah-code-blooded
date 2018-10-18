from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authors.apps.articles.views import (
    ArticleAPIView, ArticleTagsAPIView, LikeAPIView, RatingAPIView,
    CommentAPIView, CommentCreateUpdateDestroy, DislikeAPIView,
    ReactionsAPIView, SearchFilterListAPIView, FavouriteArticleApiView,
    LikeComments, DislikeComments)

app_name = "articles"
router = DefaultRouter()
router.register('articles', ArticleAPIView, base_name="articles")

urlpatterns = [
    path('', include(router.urls)),
    path(
        'articles/<slug>/tags/',
        ArticleTagsAPIView.as_view(),
        name="article-tags"),
    path('articles/<str:slug>/like/', LikeAPIView.as_view(), name='like'),
    path(
        'articles/<str:slug>/unlike/',
        DislikeAPIView.as_view(),
        name='dislike'),
    path(
        'articles/<str:slug>/reactions/',
        ReactionsAPIView.as_view(),
        name='reactions'),
    path(
        'articles/<slug>/rate/', RatingAPIView.as_view(), name='rate-article'),
    path(
        'articles/<slug>/comments', CommentAPIView.as_view(), name='comments'),
    path(
        'articles/<slug>/comments/<pk>',
        CommentCreateUpdateDestroy.as_view(),
        name="a-comment"),
    path(
        'articles/search_filter',
        SearchFilterListAPIView.as_view(),
        name='search-filter'),
    path(
        'articles/<str:slug>/unlike/',
        DislikeAPIView.as_view(),
        name='dislike'),
    path(
        'articles/<str:slug>/reactions/',
        ReactionsAPIView.as_view(),
        name='reactions'),
    path(
        'articles/<slug>/rate/', RatingAPIView.as_view(), name='rate-article'),
    path(
        'articles/<slug>/favourite/',
        FavouriteArticleApiView.as_view(),
        name="favourite_article"),
    path(
        'articles/<slug>/comments/<pk>/likes',
        LikeComments.as_view(),
        name="likes"),
    path(
        'articles/<slug>/comments/<pk>/dislikes',
        DislikeComments.as_view(),
        name="dislikes")
]
