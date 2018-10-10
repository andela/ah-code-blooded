# Create your views here.
from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from rest_framework import status, viewsets, generics
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from authors.apps.articles.models import Article, Tag
from authors.apps.articles.permissions import IsArticleOwnerOrReadOnly
from authors.apps.articles.serializers import ArticleSerializer, TagSerializer, TagsSerializer
from authors.apps.core.renderers import BaseJSONRenderer


class ArticleAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    Define the method to manipulate an article
    """
    lookup_field = 'slug'
    permission_classes = (IsAuthenticatedOrReadOnly, IsArticleOwnerOrReadOnly,)
    renderer_classes = (BaseJSONRenderer,)
    queryset = Article.objects.all()
    renderer_names = ('article', 'articles')
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


class ArticleTagsAPIView(generics.ListCreateAPIView, generics.DestroyAPIView):
    lookup_field = 'slug'
    serializer_class = TagSerializer
    renderer_classes = (BaseJSONRenderer,)
    queryset = Tag.objects.all()
    permission_classes = [IsArticleOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Create a tag, and use it for a particular article,
        This method ensures there is no duplication of articles
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        slug = kwargs['slug']

        article = Article.objects.filter(slug=slug, author=request.user).first()
        if article is None:
            return Response({'errors': 'Article does not exist'}, status.HTTP_404_NOT_FOUND)

        else:
            tags = request.data.get('tags', [])
            serializer = self.serializer_class(many=True, data=[{'tag': x} for x in tags])
            serializer.is_valid(raise_exception=True)

            for tag in tags:
                t, created = Tag.objects.get_or_create(slug=slugify(tag), tag=tag)
                article.tags.add(t)

            output = TagsSerializer(article)

            return Response(output.data)

    def destroy(self, request, *args, **kwargs):
        slug = kwargs['slug']

        article = Article.objects.filter(slug=slug, author=request.user).first()
        if article is None:
            return Response({'errors': 'Article does not exist'}, status.HTTP_404_NOT_FOUND)
        else:
            tags = request.data.get('tags', [])

            # delete the tags from the article
            for tag in tags:
                t = Tag.objects.get(slug=slugify(tag))
                if t:
                    article.tags.remove(t)

            output = TagsSerializer(article)
            return Response(output.data)

    def list(self, request, *args, **kwargs):
        """
        Get all the tags for a particular article
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        slug = kwargs['slug']

        article = Article.objects.filter(slug=slug, author=request.user).first()
        if article is None:
            return Response({'errors': 'Article does not exist'}, status.HTTP_404_NOT_FOUND)
        else:
            output = TagsSerializer(article)
            return Response(output.data)


class TagsAPIView(generics.ListAPIView):
    """
    API View class to display all the tags
    """
    queryset = Tag.objects.all()
    renderer_classes = (BaseJSONRenderer,)
    renderer_names = ('tag', 'tags')
    serializer_class = TagSerializer
