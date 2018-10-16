from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer
from django.db import models
from authors.apps.articles.models import Article, Tag, ArticleRating, Comment, FavouriteArticle
from authors.apps.authentication.models import User


class TagField(serializers.RelatedField):
    """
    Override the RelatedField serializer field in order to serialize the Tags related to a particular article
    """
    queryset = Tag.objects.all()

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(tag=data, slug=slugify(data))

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
            'max_length':
            "The article title cannot be more than 255 characters"
        })
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'blank': 'The article must have a description',
            'required': "The article must have a description",
        })
    body = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'blank': 'The article must have a body',
            'required': "The article must have a body",
        })

    published = serializers.BooleanField(required=False)
    image = serializers.URLField(required=False, allow_blank=False)
    avg_rating = serializers.SerializerMethodField(
        method_name='get_average_rating')

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    tags = TagField(
        many=True,
        required=False,
        error_messages={'not_a_list': "The tags must be a list of strings"})

    reactions = serializers.SerializerMethodField(read_only=True)

    author = serializers.SerializerMethodField(read_only=True)

    read_time = serializers.SerializerMethodField(read_only=True)

    # tagList = TagField(many=True, required=False)

    class Meta:
        model = Article

        fields = [
            'slug', 'title', 'description', 'body', 'published', 'author',
            'image', 'created_at', 'updated_at', 'tags', 'avg_rating',
            'read_time', 'reactions'
        ]
        read_only_fields = [
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
            'reactions',
            'read_time',
        ]
        read_only_fields = ('slug', 'author', 'reactions')

    def get_author(self, obj):
        serializer = ProfileSerializer(
            instance=Profile.objects.get(user=obj.author))
        return serializer.data

    def get_read_time(self, obj):
        """
        TRT = NoW/275 + [(10/60)*NoI)

        Where;
        TRT = Total Read Time (in seconds)
        NoW = Number of Words (in the article)
        NoI = Number of Images (in the article)
        """
        image = obj.image
        words = obj.body.split()
        readtime = (len(words) / 275.0) * 60
        image_readtime = 10  # Currently we allow a single image (10s)

        if image == "":
            return round(readtime,
                         2)  # Round down the readtime in seconds to 2dp
        return round(readtime + image_readtime, 2)

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
            disliked_by_me = instance.dislikes.all().filter(
                id=user_id).count() == 1

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
    tag = serializers.CharField(
        required=True,
        max_length=28,
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
                    "Rating should be a number between 1 and 5!")
        return {'rating': _rating}


class CommentSerializer(serializers.ModelSerializer):
    """ serialize and deserialize comment model"""
    body = serializers.CharField(max_length=1200)  # remove
    article = ArticleSerializer(read_only=True)
    author = ProfileSerializer(read_only=True)
    likes = serializers.SerializerMethodField(method_name='count_likes')
    dislikes = serializers.SerializerMethodField(method_name='count_dislikes')

    class Meta:
        model = Comment

        fields = "__all__"

    def count_likes(self, instance):
        """Returns the total likes of particlular comment"""
        return instance.likes.count()

    def count_dislikes(self, instance):
        """Returns  the total dislikes of a particular comment."""
        return instance.dislikes.count()


class UpdateCommentSerializer(serializers.Serializer):
    """
    Defines the update comment serializer
    """
    body = serializers.CharField(max_length=200)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ('body', 'created_at')

    def update(instance, data):
        instance.body = data.get('body', instance.body)
        instance.save()
        return instance


class FavouriteSerializer(serializers.ModelSerializer):
    """validate favourite model"""

    article = serializers.SlugField()
    email = serializers.EmailField()

    def get_user_email_and_article(self, data):
        try:
            self.article = Article.objects.get(slug=data['article'])
            self.email = User.objects.get(email=data['email'])
        except Article.DoesNotExist:
            raise NotFound("this slug doesnt match any article")
        except User.DoesNotExist:
            raise NotFound("this email does not exist")
        data['article'] = self.article
        data['email'] = self.email
        return data

    def add_or_remove(self, data):
        data = self.get_user_email_and_article(data)
        query_set = FavouriteArticle.favourite.filter(
            article=self.article, email=self.email)
        if query_set.exists():
            output = query_set.get()
            return output
        return data

    def create(self, data):
        fav = self.add_or_remove(data)
        if isinstance(fav, FavouriteArticle):
            raise serializers.ValidationError("Article already favourited")
        else:
            return FavouriteArticle.favourite.create(**fav)

    def view_favourite(self, data):
        fav = self.add_or_remove(data)

        if isinstance(fav, FavouriteArticle):
            return fav
        else:
            raise serializers.ValidationError("Article not favourited")

    class Meta:
        model = FavouriteArticle
        fields = ['email', 'article']


def update(request, key):
    data = request.data
    data[key] = request.user.email
    return data
