from django.db import models

# Create your models here.
from authors.apps.core.models import BaseModel


class Article(BaseModel):
    slug = models.SlugField(max_length=128, unique=True, db_index=True)
    title = models.CharField()
