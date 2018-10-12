from django.utils.text import slugify
from rest_framework import serializers

<<<<<<< HEAD
=======
from authors.apps.articles.models import Article, Tag, Violation
>>>>>>> [Feature #160577626] Add report serializer
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer
from django.db import models

from authors.apps.articles.models import Article, Tag, ArticleRating


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

    reactions = serializers.SerializerMethodField(read_only=True)

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
            'tags',
            'reactions'
        ]
        read_only_fields = ('slug', 'author', 'reactions')

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

    def get_reactions(self, instance):
        request = self.context.get('request')

        liked_by_me = False
        disliked_by_me = False

        if request is not None and request.user.is_authenticated:
            user_id = request.user.id
            liked_by_me = instance.likes.all().filter(id=user_id).count() == 1
            disliked_by_me = instance.dislikes.all().filter(id=user_id).count() == 1

        return {
            'likes': {
                'count': instance.likes.count(),
                'me': liked_by_me
            },
            'dislikes': {
                'count': instance.dislikes.count(),
                'me': disliked_by_me
            }
        }


class TagsSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    tags = TagField(many=True)

    class Meta:
        model = Article
        fields = ['article', 'tags']

    def get_article(self, instance):
        return instance.slug


class TagSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(required=True, max_length=28,
                                allow_blank=False,
                                allow_null=False,
                                error_messages={
                                    "blank": "Please specify a tag",
                                    "required": "Please specify a tag",
                                    "max_length": "Tag cannot be more than 28 characters"
                                })
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = ['tag', 'slug']



class RatingSerializer(serializers.ModelSerializer):
    """
    Creates ratings for the existing articles and edits ratings for existing articles
    """
    rating = serializers.IntegerField(required=True)

    class Meta:
<<<<<<< HEAD
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
            if _rating < 0 or _rating > 5:
                raise serializers.ValidationError(
                    "Rating should be a number between 1 and 5!"
                )
        return {'rating': _rating}
=======
        model = Tag
        fields = ['tag']


class ReporterSerializer(serializers.ModelSerializer):
    """
    Validate the tag model
    """
    violation_type = serializers.ChoiceField(choices=Violation.VIOLATION_TYPES_CHOICES)
    description = serializers.CharField()
    article = serializers.CharField(write_only=True)
    reportee = serializers.SerializerMethodField()
    reporter = serializers.SerializerMethodField()

    class Meta:
        model = Violation
        fields = ['violation_type', 'article', 'description', 'reporter', 'reportee']

    def get_reporter(self, obj):
        return obj.reporter.email

    def get_reportee(self, obj):
        return obj.article.author.email

    def create(self, validated_data):
        slug = validated_data.pop('article')

        article = Article.objects.get(slug=slug)

        validated_data['article'] = article

        return Violation.objects.create(**validated_data)

    def violation_types(self):
        return {x[0]: x[1] for x in Violation.VIOLATION_TYPES_CHOICES}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['article'] = instance.article.slug
        data['violation_type'] = {
            'value': data['violation_type'],
            'display': self.violation_types()[data['violation_type']]
        }
        return data
>>>>>>> [Feature #160577626] Add report serializer
