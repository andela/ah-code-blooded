import random
import string

from django.db import models
from django.db.models.signals import pre_save

from django.template.defaultfilters import slugify

from authors.apps.core.models import BaseModel


class Article(BaseModel):
    """
    Model for an article, extends a basemodel since the created and updated times are required
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
        on_delete=models.CASCADE
    )
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
            unique = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
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


class Tag(BaseModel):
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


# register the pre_save signal
pre_save.connect(Article.pre_save, Article, dispatch_uid="authors.apps.articles.models.Article")
