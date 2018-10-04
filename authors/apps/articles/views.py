# Create your views here.
from django.contrib.auth.models import AnonymousUser
from rest_framework import status, viewsets
from rest_framework import mixins
from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView

from authors.apps.articles.models import Article, ArticleRating
from authors.apps.articles.permissions import IsArticleOwnerOrReadOnly
from authors.apps.articles.renderers import ArticleJSONRenderer, RatingJSONRenderer
from authors.apps.articles.serializers import ArticleSerializer, RatingSerializer


class ArticleAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    Define the method to manipulate an article
    """
    lookup_field = 'slug'
    permission_classes = (IsAuthenticatedOrReadOnly, IsArticleOwnerOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates an article.
        Set the author as the current logged in user
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        article = request.data.get('article', {})

        # prevent an unauthorized user to create an account
        if not request.user.is_verified:
            return Response({"errors": "Sorry, verify your account first in order to create articles"},
                            status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Check whether the article exists and returns a custom message,

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        slug = kwargs['slug']

        article = Article.objects.filter(slug=slug).first()
        if article is None:
            return Response({'errors': 'Article does not exist'}, status.HTTP_404_NOT_FOUND)
        elif not article.author == request.user:
            return Response({"errors": "You are not allowed to modify this article"}, status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(article, data=request.data.get('article', {}), partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save(author=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an article using the article slug
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        slug = kwargs['slug']

        article = Article.objects.filter(slug=slug)
        if request.user and not isinstance(request.user, AnonymousUser):
            mine = Article.objects.filter(slug=slug, author=request.user)
            article = article.filter(published=True)

            article = article.union(mine).first()
        else:
            # ensure the article is published
            article = article.filter(published=True).first()

        if article is None:
            return Response({'errors': 'Article does not exist'}, status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(article, context={'request': request})

        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Only list the articles that have been published
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        articles = Article.objects.filter(published=True)
        # if the user is logged in, display both published and unpublished articles
        if request.user and not isinstance(request.user, AnonymousUser):
            mine = Article.objects.filter(author=request.user)

            articles = articles.union(mine)

        serializer = self.serializer_class(articles, context={'request': request},
                                           many=True)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Return a custom message when the article has been deleted
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        super().destroy(self, request, *args, **kwargs)

        return Response({'message': 'The article has been deleted.'})

class RatingAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ArticleRating.objects.all()
    serializer_class = RatingSerializer
    renderer_classes = (RatingJSONRenderer,)

    def post(self, request, *args, **kwargs):
        """
        Users can post article ratings
        """
        rating = request.data.get('rating', {})

        article = Article.objects.get(slug=kwargs['slug'])
        if article:
            rated = ArticleRating.objects.filter(article=article, rated_by=request.user).first()
            if rated:
                data = {"message": "You have already rated this article."}
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            else:
                serializer = self.serializer_class(data=rating)
                serializer.is_valid(raise_exception=True)
                serializer.save(rated_by=request.user, article=article)

                data = serializer.data
                data['message'] = "You have successfully rated this article"
                return Response(data, status=status.HTTP_201_CREATED)
                

        data = {"message": "This article does not exist."}
        return Response(data, status=status.HTTP_404_NOT_FOUND)


            


        
        


