from rest_framework import serializers

from authors.apps.articles.models import Article, Tag, ArticleImage


class ArticleImageSerializer(serializers.ModelSerializer):
    """
    Serialize the Article image
    """

    class Meta:
        model = ArticleImage
        fields = ['image']


class ArticleImageField(serializers.RelatedField):
    def get_queryset(self):
        return ArticleImage.objects.all()

    def to_internal_value(self, data):
        image = ArticleImage(image=data)
        return image

    def to_representation(self, value):
        return value.image


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
    published = serializers.BooleanField(required=False)
    images = ArticleImageField(source='articleimage_set', many=True, required=False)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    tags = TagField(many=True, required=False)

    # tagList = TagField(many=True, required=False)

    class Meta:
        model = Article

        fields = [
            'slug',
            'title',
            'description',
            'body',
            'published',
            'author',
            'images',
            'created_at',
            'updated_at',
            'tags'
        ]
        read_only_fields = ('slug', 'author',)

    def create(self, validated_data):
        """
        Creates an article, this method will also be used to handle foreign checks
        and create any relevant models related to this article
        :param validated_data:
        :return:
        """
        tags = validated_data.pop('tags', [])
        images = validated_data.pop('articleimage_set', [])

        article = Article.objects.create(**validated_data)

        for tag in tags:
            article.tags.add(tag)

        for image in images:
            image.article = article
            # avoid having two similar images in the same article
            if not ArticleImage.objects.filter(article__slug=article.slug,
                                               article__articleimage__image=image):
                image.save()

        return article

    def update(self, instance, validated_data):
        """
        Performs an update to the article
        :param instance:
        :param validated_data:
        :return:
        """

        tags = validated_data.pop('tags', [])
        images = validated_data.pop('articleimage_set', [])

        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)

        for image in images:
            image.article = instance
            if not ArticleImage.objects.filter(article__slug=instance.slug,
                                               article__articleimage__image=image):
                image.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class TagSerializer(serializers.ModelSerializer):
    """
    Validate the tag model
    """
    tag = serializers.CharField(required=True,
                                max_length=128)

    class Meta:
        model = Tag
        fields = ['tag']
