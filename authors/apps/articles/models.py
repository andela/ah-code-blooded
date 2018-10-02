from django.db import models

# Create your models here.
from authors.apps.core.models import BaseModel


class Article(BaseModel):
    """
    Model for an article, extends a basemodel since the created and updated times are required
    """
    slug = models.SlugField(max_length=128, unique=True, db_index=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    body = models.TextField()

    # The author Foreign Key should be bound to a user profile
    author = models.ForeignKey(
        'authentication.User',
        related_name='articles',
        on_delete=models.CASCADE
    )
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        """
        Use the Article title to represent this object
        :return:
        """
        return self.title
