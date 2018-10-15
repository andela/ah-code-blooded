from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from rest_framework import status, viewsets, generics
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, DestroyAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView

from authors.apps.articles.models import Article, Tag, ArticleRating
from authors.apps.articles.permissions import IsArticleOwnerOrReadOnly
from authors.apps.articles.serializers import ArticleSerializer, TagSerializer, TagsSerializer, RatingSerializer
from authors.apps.core.renderers import BaseJSONRenderer
from authors.apps.articles.permissions import IsArticleOwnerOrReadOnly


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

    @staticmethod
    def retrieve_owner_or_published(slug, user):
        """
        Retrieve the article for a user,
        If the user is logged in:
            1. if the user is the owner, return the article whether it is published or not
            2. If the user is not the owner, return the article only if it is published
        If the user is not logged in:
            1. Return the article only if it is published
        :param slug:
        :param user:
        :return:
        """
        article = Article.objects.filter(slug=slug)
        if user and not isinstance(user, AnonymousUser):
            mine = Article.objects.filter(slug=slug, author=user)
            article = article.filter(published=True)

            article = article.union(mine).first()
        else:
            # ensure the article is published
            article = article.filter(published=True).first()
        return article

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

        article = self.retrieve_owner_or_published(slug, request.user)

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

    def create(self, request, *args, **kwargs):  # NOQA : E731
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
            valid = serializer.is_valid(raise_exception=False)
            if not valid:
                errors = {}
                for i in range(0, len(serializer.errors)):
                    if len(serializer.errors[i]) > 0:
                        errors[tags[i]] = serializer.errors[i]
                return Response(errors, status.HTTP_400_BAD_REQUEST)

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

        article = ArticleAPIView.retrieve_owner_or_published(slug, request.user)

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


class ReactionMixin(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)


class BaseReactionsMixin:
    """
    This mixin contains properties common to all reaction
    views.
    """
    def get_queryset(self):
        return Article.objects.all()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_reactions(self):
        article = self.get_object()
        serializer = ArticleSerializer(article, context={'request': self.request})
        return serializer.data['reactions']


class ReactionsAPIView(BaseReactionsMixin, RetrieveAPIView):
    """
    This view retrieves the reactions of an article.
    """
    def get(self, request, **kwargs):
        return Response({'reactions': self.get_reactions()})


class LikeDislikeMixin(BaseReactionsMixin, CreateAPIView, DestroyAPIView):
    """
    This mixin adds create and destroy API views and permission classes to the
    BaseReactionMixin. These properties are required required by the like
    and dislike views.
    """
    def get_response(self, message):
        return {
            'message': message,
            'reactions': self.get_reactions()
        }


class LikeAPIView(LikeDislikeMixin):
    """
    This view enables liking and un-liking articles.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        Like an article.
        """
        article = self.get_object()
        article.like(request.user)

        return Response(self.get_response('You like this article.'), status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        """
        Un-like an article.
        """
        article = self.get_object()
        article.un_like(request.user)

        return Response(self.get_response('You no longer like this article.'), status=status.HTTP_200_OK)


class DislikeAPIView(LikeDislikeMixin):
    """
    This view enables disliking and un-disliking articles.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        Dislike an article.
        """
        article = self.get_object()
        article.dislike(request.user)

        return Response(self.get_response('You dislike this article.'), status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        """
        Un-dislike an article.
        """
        article = self.get_object()
        article.un_dislike(request.user)

        return Response(self.get_response('You no longer dislike this article.'), status=status.HTTP_200_OK)


class RatingAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ArticleRating.objects.all()
    serializer_class = RatingSerializer
    renderer_classes = (BaseJSONRenderer,)

    def post(self, request, *args, **kwargs):
        """
        Users can post article ratings
        """
        rating = request.data.get('rating', {})

        try:
            article = Article.objects.get(slug=kwargs['slug'])
        except Article.DoesNotExist:
            data = {"errors": "This article does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        if article:
            rated = ArticleRating.objects.filter(article=article, rated_by=request.user).first()
            rating_author = article.author
            rating_user = request.user
            if rating_author == rating_user:
                data = {"errors": "You cannot rate your own article."}
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            if rated:
                data = {"errors": "You have already rated this article."}
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            else:
                serializer = self.serializer_class(data=rating)
                serializer.is_valid(raise_exception=True)
                serializer.save(rated_by=request.user, article=article)

                data = serializer.data
                data['message'] = "You have successfully rated this article"
                return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """users an update the ratings of articles
        """
        serializer_data = request.data.get('rating', {})
        try:
            article = Article.objects.get(slug=kwargs['slug'])
        except Article.DoesNotExist:
            data = {"errors": "This article does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        rating = ArticleRating.objects.filter(article=article, rated_by=request.user).first()

        serializer = self.serializer_class(rating, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(rated_by=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_200_OK)
