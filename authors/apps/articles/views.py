from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from rest_framework import status, viewsets, generics
from rest_framework import mixins
from rest_framework.generics import DestroyAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import (RetrieveUpdateDestroyAPIView,
                                     CreateAPIView, ListAPIView,
                                     ListCreateAPIView, UpdateAPIView)
from rest_framework.views import APIView
from authors.apps.articles.models import Article, Tag, ArticleRating, Comment
from authors.apps.articles.permissions import IsArticleOwnerOrReadOnly
from authors.apps.articles.serializers import (ArticleSerializer,
                                               TagSerializer, RatingSerializer,
                                               FavouriteSerializer, update)
from authors.apps.core.renderers import BaseJSONRenderer

from .pagination import StandardResultsSetPagination
from authors.apps.articles.serializers import (
    CommentSerializer, UpdateCommentSerializer, TagsSerializer)

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from notifications.signals import notify
from authors.apps.ah_notifications.notifications import Verbs


class ArticleAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Define the method to manipulate an article
    """
    lookup_field = 'slug'
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsArticleOwnerOrReadOnly,
    )
    renderer_classes = (BaseJSONRenderer,)
    queryset = Article.objects.all()
    renderer_names = ('article', 'articles')
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsSetPagination

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
            return Response({
                "errors":
                    "Sorry, verify your account first in order to create articles"
            }, status.HTTP_401_UNAUTHORIZED)

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
            return Response({
                'errors': 'Article does not exist'
            }, status.HTTP_404_NOT_FOUND)
        elif not article.author == request.user:
            return Response(
                {
                    "errors": "You are not allowed to modify this article"
                }, status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(
            article, data=request.data.get('article', {}), partial=True)
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
            return Response({
                'errors': 'Article does not exist'
            }, status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            article, context={'request': request})

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

        # paginates a queryset(articles) if required
        page = self.paginate_queryset(articles)

        serializer = self.serializer_class(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

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


class ArticleFilter(filters.FilterSet):
    tag = filters.CharFilter(field_name='tags__tag', lookup_expr='exact')
    username = filters.CharFilter(field_name='author__username', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='exact')

    class Meta:
        model = Article
        fields = ['tag', 'username', 'title']


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

        article = Article.objects.filter(
            slug=slug, author=request.user).first()
        if article is None:
            return Response({
                'errors': 'Article does not exist'
            }, status.HTTP_404_NOT_FOUND)

        else:
            tags = request.data.get('tags', [])
            serializer = self.serializer_class(
                many=True, data=[{
                    'tag': x
                } for x in tags])
            valid = serializer.is_valid(raise_exception=False)
            if not valid:
                errors = {}
                for i in range(0, len(serializer.errors)):
                    if len(serializer.errors[i]) > 0:
                        errors[tags[i]] = serializer.errors[i]
                return Response(errors, status.HTTP_400_BAD_REQUEST)

            for tag in tags:
                t, created = Tag.objects.get_or_create(
                    slug=slugify(tag), tag=tag)
                article.tags.add(t)

            output = TagsSerializer(article)

            return Response(output.data)

    def destroy(self, request, *args, **kwargs):
        slug = kwargs['slug']

        article = Article.objects.filter(
            slug=slug, author=request.user).first()
        if article is None:
            return Response({
                'errors': 'Article does not exist'
            }, status.HTTP_404_NOT_FOUND)
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

        article = ArticleAPIView.retrieve_owner_or_published(
            slug, request.user)

        if article is None:
            return Response({
                'errors': 'Article does not exist'
            }, status.HTTP_404_NOT_FOUND)
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
        serializer = ArticleSerializer(
            article, context={'request': self.request})
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



class ArticleFilter(filters.FilterSet):
    tag = filters.CharFilter(field_name='tags__tag', lookup_expr='exact')
    username = filters.CharFilter(field_name='author__username', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='exact')

    class Meta:
        model = Article
        fields = ['tag', 'username', 'title']


class SearchFilterListAPIView(ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (BaseJSONRenderer,)
    queryset = Article.objects.all()

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    # filter fields are used to filter the articles using the tags, author's username and title
    filterset_class = ArticleFilter
    # search fields search all articles' parameters for the searched character
    search_fields = ('tags__tag', 'author__username', 'title', 'body', 'description')
    # ordering fields are used to render search outputs in a particular order e.g asending or descending order
    ordering_fields = ('author__username', 'title')


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

        return Response(
            self.get_response('You like this article.'),
            status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        """
        Un-like an article.
        """
        article = self.get_object()
        article.un_like(request.user)

        return Response(
            self.get_response('You no longer like this article.'),
            status=status.HTTP_200_OK)


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

        return Response(
            self.get_response('You dislike this article.'),
            status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        """
        Un-dislike an article.
        """
        article = self.get_object()
        article.un_dislike(request.user)

        return Response(
            self.get_response('You no longer dislike this article.'),
            status=status.HTTP_200_OK)


class RatingAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ArticleRating.objects.all()
    serializer_class = RatingSerializer
    renderer_classes = (BaseJSONRenderer,)

    def post(self, request, *args, **kwargs):  # NOQA
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
            rated = ArticleRating.objects.filter(
                article=article, rated_by=request.user).first()
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

                notify.send(rating_user, verb=Verbs.ARTICLE_RATING, recipient=rating_author, 
                    description="{} has rated your article {}/5".format(rating_user, rating))

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

        rating = ArticleRating.objects.filter(
            article=article, rated_by=request.user).first()

        serializer = self.serializer_class(
            rating, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(rated_by=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (BaseJSONRenderer,)
    """This class get commit for specific article and create comment"""

    # filter by slug from url
    lookup_url_kwarg = 'slug'
    lookup_field = 'article__slug'

    def filter_queryset(self, queryset):
        """This method filter and get comment of an article."""
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        return queryset.filter(**filters)

    def create(self, request, *args, **kwargs):
        """This methods creates a comment"""
        slug = self.kwargs['slug']
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({
                'Error': 'Article doesnot exist'
            }, status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(
            data=request.data.get('comment', {}))
        serializer.is_valid(raise_exception=True)

        serializer.save(article=article, author=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentCreateUpdateDestroy(CreateAPIView, RetrieveUpdateDestroyAPIView):
    """This class view creates update and delete comment"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (BaseJSONRenderer,)
    lookup_url_kwarg = "pk"

    def create(self, request, slug=None, pk=None):
        """This method creates child comment(thread-replies on the parent comment)"""
        slug = self.kwargs['slug']

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({
                'Error': 'Article doesnot exist'
            }, status.HTTP_404_NOT_FOUND)

        # Get the parent commet of the thread
        try:
            pk = self.kwargs.get('pk')
            parent = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            message = {"Error": "comment with this ID doesn't exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        # validating, deserializing and  serializing comment-thread.
        serializer = self.serializer_class(
            data=request.data.get('comment', {}))
        serializer.is_valid(raise_exception=True)
        serializer.save(
            article=article, parent=parent, author=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """This method delele comment"""
        slug = self.kwargs['slug']

        try:
            Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({
                'Error': 'Article doesnot exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            message = {"Error": "comment with this ID doesn't exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        super().destroy(self, request, *args, **kwargs)
        return Response({'message': 'The comment has been deleted.'})

    def update(self, request, *args, **kwargs):
        """This method update comment"""
        serializer_class = UpdateCommentSerializer
        slug = self.kwargs['slug']

        try:
            Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({
                'Error': 'Article doesnot exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            message = {"Error": "comment with this ID doesn't exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        updated_comment = serializer_class.update(
            data=request.data.get('comment', {}), instance=comment)
        return Response(
            self.serializer_class(updated_comment).data,
            status=status.HTTP_201_CREATED)




class FavouriteArticleApiView(APIView):
    """
    define method to favourite article
    """

    permission_classes = (IsAuthenticated, )
    serializer_class = FavouriteSerializer

    def post(self, request, slug):
        """
        a registered user can favourite an article
        """
        request.data['email'] = request.user.email
        request.data['article'] = slug
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Article favourited'})

    def delete(self, request, slug):
        """
        a registered user can unfavourite an article
        """
        data = update(request, 'email')
        data['article'] = slug
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        favourite = serializer.view_favourite(data)
        favourite.delete()
        return Response({
            'message': 'Article removed from favourites'
        }, status.HTTP_200_OK)


class LikeComments(UpdateAPIView):
    """This class Handles likes of comment"""

    def update(self, request, *args, **kwargs):  # NOQA
        """This method updates liking of comment"""
        slug = self.kwargs['slug']

        try:
            Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({
                'Error': 'Article doesnot exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            message = {"Error": "comment with this ID doesn't exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        # get the user
        user = request.user
        comment.dislikes.remove(user.id)

        # confirm if user has already liked comment and remove him if
        # clicks it again
        confirm = bool(user in comment.likes.all())
        if confirm is True:
            comment.likes.remove(user.id)
            return Response({'Success, You no longer like this comment'},
                            status.HTTP_200_OK)

        # This add the user to likes lists
        comment.likes.add(user.id)
        message = {"Sucess": "You liked this comment"}
        return Response(message, status.HTTP_200_OK)


class DislikeComments(UpdateAPIView):
    """This class Handles dislikes of comment"""

    def update(self, request, *args, **kwargs):  # NOQA
        """This method updates liking of comment"""
        slug = self.kwargs['slug']

        try:
            Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({
                'Error': 'Article doesnot exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            message = {"Error": "comment with this ID doesn't exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)
        # get the user
        user = request.user
        comment.likes.remove(user.id)

        # confirm if user has already disliked comment and remove him if
        # clicks it again
        confirm = bool(user in comment.dislikes.all())
        if confirm is True:
            comment.dislikes.remove(user.id)
            message = {"Success": "You undislike this comment"}
            return Response(message, status.HTTP_200_OK)

        # This add the user to dislikes lists
        comment.dislikes.add(user.id)
        message = {"success": "You disliked this comment"}
        return Response(message, status.HTTP_200_OK)
