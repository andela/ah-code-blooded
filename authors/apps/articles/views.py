
# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authors.apps.articles.renderers import ArticleJSONRenderer
from authors.apps.articles.serializers import ArticleSerializer


class ArticleAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def post(self, request, *args, **kwargs):
        article = request.data.get('article', {})

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
