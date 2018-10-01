# Create your views here.
from rest_framework import status, viewsets
from rest_framework import mixins
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from authors.apps.articles.models import Article
from authors.apps.articles.renderers import ArticleJSONRenderer
from authors.apps.articles.serializers import ArticleSerializer


class ArticleAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    Define the method to manipulate an article
    """
    lookup_field = 'slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def create(self, request, *args, **kwargs):
        article = request.data.get('article', {})

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        slug = kwargs['slug']

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an article using the article slug
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        slug = kwargs['slug']

        try:
            article = Article.objects.get(slug=slug)
        except Exception:
            raise NotFound("Article does not exist")

        serializer = self.serializer_class(article, context={'request': request})

        return Response(serializer.data)
