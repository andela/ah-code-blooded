from rest_framework import serializers

from authors.apps.articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    image = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Article

        fields = ['slug', 'title', 'description', 'body', 'author', 'image']
