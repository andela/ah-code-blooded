import random
import string

from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from authors.apps.authentication.models import User
from authors.apps.core.models import TimestampsMixin
from rest_framework.reverse import reverse


class ReactionMixin(models.Model):
    """
    This mixin adds like and dislike functionality to the article model.
    """
    likes = models.ManyToManyField(User, related_name='likes', blank=True)

    dislikes = models.ManyToManyField(
        User, related_name='dislikes', blank=True)

    def like(self, user):
        """
        Adds a like on the article for the user. Before
        liking, it attempts to un-dislike
        in case the user disliked it.
        :param user:
        :return:
        """
        self.un_dislike(user)
        # add like for the user
        self.likes.add(user)

    def un_like(self, user):
        """
        Un-likes the article if the user likes it.
        If they don't like it nothing happens.
        :param user:
        :return:
        """
        self.likes.remove(user)

    def dislike(self, user):
        """
        Adds a dislike on the article for the user.
        Before disliking, it attempts to un-like
        in case the user liked it.
        :param user:
        :return:
        """
        self.un_like(user)
        self.dislikes.add(user)

    def un_dislike(self, user):
        """
        Un-dislikes the article if the user dislikes it.
        If they don't dislike it nothing happens.
        :param user:
        :return:
        """
        self.dislikes.remove(user)

    class Meta:
        abstract = True


class Article(TimestampsMixin, ReactionMixin):
    """
    Model for an article, extends a base model since the created and updated times are required
    """
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    image = models.URLField(default='')

    # The author Foreign Key should be bound to a user profile
    author = models.ForeignKey(
        'authentication.User',
        related_name='articles',
        on_delete=models.CASCADE)
    # a article contains many tags
    tags = models.ManyToManyField(
        'articles.Tag',
        related_name='articles',
    )
    published = models.BooleanField(default=False)

    @staticmethod
    def pre_save(sender, instance, *args, **kwargs):
        # create the slug only when the article is being saved to avoid broken links
        if not instance.id or not instance.published:
            unique = ''.join(
                random.choice(string.ascii_lowercase + string.digits)
                for _ in range(12))
            if instance.slug[:-13] != slugify(instance.title):
                instance.slug = slugify(instance.title)
                instance.slug = instance.slug[:250]
                instance.slug = instance.slug + '-' + unique

    def __str__(self):
        """
        Use the Article title to represent this object
        :return:
        """
        return self.title

    def get_share_article(self, request=None):
        """
        This method shares article through twitter, facebook, email
        linkedin and email.
        """
        article = reverse(
            "articles:articles-detail",
            kwargs={'slug': self.slug},
            request=request)

        article_uri = {
            'Email':
            'mailto:?subject=New Article Alert&body={}'.format(article),
            'Twitter':
            'https://twitter.com/intent/tweet?url={}'.format(article),
            'Facebook':
            'https://www.facebook.com/sharer/sharer.php?u={}'.format(article),
            'LinkedIn':
            'http://www.linkedin.com/shareArticle?mini=true&amp;url={}'.format(
                article),
        }
        return article_uri


class Tag(TimestampsMixin):
    """
    Every article contains a tag

    A tag has a unique slug
    """
    tag = models.CharField(max_length=28)
    slug = models.SlugField(db_index=True, unique=True)

    class Meta:
        unique_together = ['tag', 'slug']
        ordering = ['tag']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tag)
        if not Tag.objects.filter(slug=self.slug).first():
            super().save(*args, **kwargs)

    def __str__(self):
        return self.tag


class ArticleRating(models.Model):
    """
    Ratings that users give Articles
    """
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='articleratings')
    rating = models.IntegerField(default=0)
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE)


# register the pre_save signal
pre_save.connect(
    Article.pre_save,
    Article,
    dispatch_uid="authors.apps.articles.models.Article")


class Comment(TimestampsMixin):
    """
    Represent model for an comment
    """
    # Bound comment to article class
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments')
    # User form to insert comment for the article
    body = models.TextField()
    # Create a recursive relationship so that comment has many-to-one relationship
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='thread')
    author = models.ForeignKey(
        'profiles.Profile',
        related_name='comments',
        blank=True,
        on_delete=models.CASCADE)
    likes = models.ManyToManyField(
        User, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(
        User, related_name='comment_dislikes', blank=True)


pre_save.connect(Article.pre_save, Article, dispatch_uid="authors.apps.articles.models.Article")


class FavouriteArticle(TimestampsMixin):
    """Allow an article to be favourited"""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="favourites")
    email = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    favourite = models.Manager()
