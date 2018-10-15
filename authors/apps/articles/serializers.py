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
