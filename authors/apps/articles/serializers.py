from django.utils.text import slugify
from rest_framework import serializers

from authors.apps.articles.models import Article, Tag
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer


class TagField(serializers.RelatedField):
    """
    Override the RelatedField serializer field in order to serialize the Tags related to a particular article
    """
    queryset = Tag.objects.all()

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(
            tag=data, slug=slugify(data)
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
        error_messages={
            'blank': 'The article must have a title',
            'required': "The article must have a title",
            'max_length': "The article title cannot be more than 255 characters"
        }
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'blank': 'The article must have a description',
            'required': "The article must have a description",
        }
    )
    body = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'blank': 'The article must have a body',
            'required': "The article must have a body",
        }
    )

    published = serializers.BooleanField(required=False)
    image = serializers.URLField(required=False, allow_blank=False)
    avg_rating = serializers.SerializerMethodField(method_name='get_average_rating')

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    tags = TagField(many=True, required=False, error_messages={
        'not_a_list': "The tags must be a list of strings"
    })

    author = serializers.SerializerMethodField(read_only=True)

    # tagList = TagField(many=True, required=False)

    class Meta:
        model = Article

        fields = [
            'slug',
            'title',
            'description',
            'body',
            'published',
            'avg_rating',
            'author',
            'image',
            'created_at',
            'updated_at',
            'tags'
        ]
        read_only_fields = ('slug', 'author',)

    def get_author(self, obj):
        serializer = ProfileSerializer(instance=Profile.objects.get(user=obj.author))
        return serializer.data

    def create(self, validated_data):
        """
        Creates an article, this method will also be used to handle foreign checks
        and create any relevant models related to this article
        :param validated_data:
        :return:
        """
        tags = validated_data.pop('tags', [])

        article = Article.objects.create(**validated_data)

        for tag in tags:
            article.tags.add(tag)

        return article

    def update(self, instance, validated_data):
        """
        Performs an update to the article
        :param instance:
        :param validated_data:
        :return:
        """

        tags = validated_data.pop('tags', [])

        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def get_average_rating(self, instance):
        return ArticleRating.objects.filter(article=instance).aggregate(
            average_rating=models.Avg('rating'))['average_rating'] or 0


class TagSerializer(serializers.ModelSerializer):
    """
    Validate the tag model
    """
    tag = serializers.CharField(required=True,
                                max_length=128)

    class Meta:
        model = Tag
        fields = ['tag']


class RatingSerializer(serializers.ModelSerializer):
    """
    Creates ratings for the existing articles and edits ratings for existing articles
    """
    rating = serializers.IntegerField(required=True)

    class Meta:
        fields = ['rating', 'rated_by']
        read_only_fields = ['rated_by']
        model = ArticleRating

    def create(self, validated_data):
        rating = ArticleRating.objects.create(**validated_data)

        return rating

    def validate(self, data):
        """
        Ensures that ratings are not less than or greater than 5
        Ensures that users cannot rate an article more than once
        """
        _rating = data.get('rating')

        if _rating:
            if isinstance(_rating, str):
                raise serializers.ValidationError(
                    "Rating has to be a number!"
                )
            if _rating < 0 or _rating > 5:
                raise serializers.ValidationError(
                    "Rating should be a number between 1 and 5!"
                )
        return {'rating': _rating}
