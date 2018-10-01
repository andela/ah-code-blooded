from rest_framework import serializers

from authors.apps.articles.models import Article, Tag


class TagField(serializers.RelatedField):
    """
    Override the RelatedField serializer field in order to serialize the Tags related to a particular article
    """

    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(
            tag=data,
        )
        return tag

    def to_representation(self, value):
        return value.tag


class ArticleSerializer(serializers.ModelSerializer):
    """
    Creates articles, updates and validated data for the articles created and retrieved.
    """
    slug = serializers.CharField(read_only=True, max_length=255)
    title = serializers.CharField(
        required=True,
        max_length=255,
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

    # tagList = TagField(many=True, required=False)

    class Meta:
        model = Article

        fields = ['slug', 'title', 'description', 'body', 'author', 'image',
                  'created_at', 'updated_at']
        read_only_fields = ('slug', 'author',)

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


class TagSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(required=True,
                                max_length=128)

    class Meta:
        model = Tag

    def create(self, validated_data):
        tag = Tag.objects.create(**validated_data)
        return tag

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        return instance
