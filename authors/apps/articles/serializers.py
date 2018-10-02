from rest_framework import serializers

from authors.apps.articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Creates articles, updates and validated data for the articles created and retrieved.
    """
    slug = serializers.CharField(required=False)
    title = serializers.CharField(
        required=True,
        max_length=128,
        allow_blank=False,
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    body = serializers.CharField(
        required=True,
        allow_blank=False
    )
    image = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Article

        fields = ['slug', 'title', 'description', 'body', 'author', 'image']
        read_only_fields = ('slug',)

    def create(self, validated_data):
        """
        Creates an article, this method will also be used to handle foreign checks
        and create any relevant models related to this article
        :param validated_data:
        :return:
        """
        article = Article.objects.create(**validated_data)

        return article

    def update(self, instance, validated_data):
        """
        Performs an update to the article
        :param instance:
        :param validated_data:
        :return:
        """
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        return instance
