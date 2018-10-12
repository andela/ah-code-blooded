from django.contrib import admin

# Register your models here.
from authors.apps.articles.models import Article, Tag, Violation

admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(Violation)
