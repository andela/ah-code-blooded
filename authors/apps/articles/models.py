import random
import string

from django.db import models

# Create your models here.
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

    def save(self, *args, **kwargs):
        # create the slug only when the article is being saved to avoid broken links
        if not self.id or not self.published:
            unique = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
            if self.slug[:-13] != slugify(self.title):
                self.slug = slugify(self.title)
                self.slug = self.slug[:250]
                self.slug = self.slug + '-' + unique
        super().save(*args, **kwargs)

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
    tag = models.CharField(max_length=128)
    slug = models.SlugField(db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tag)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tag


class ArticleImage(BaseModel):
    """
    Allow an article to have many images
    """
    image = models.URLField(max_length=255, db_index=True)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.image
