from unittest import TestCase

from authors.apps.articles.models import Article, Tag
from authors.apps.authentication.tests.api.test_auth import AuthenticatedTestCase


class ArticleModelTest(AuthenticatedTestCase):

    def create_article(self):
        return Article.objects.create(title="This is a simple title", description="This is a simple description",
                                      body="This is a simple body", author=self.get_current_user())

    def test_creates_a_slug(self):
        """
        Ensure that the article has a slug
        :return:
        """
        article = self.create_article()
        self.assertIsNotNone(article.slug)

    def test_has_created_time(self):
        """
        Ensure the article has a created time
        :return:
        """
        article = self.create_article()
        self.assertIsNotNone(article.created_at)


class TagModelTest(TestCase):

    def create_tag(self, tag=None):
        return Tag.objects.create(tag=tag or "Django")

    def test_creates_a_slug(self):
        """
        Ensure that a slug is created or every tag
        :return:
        """
        tag = self.create_tag()
        self.assertIsNotNone(tag.slug)

    def test_does_not_duplicate_tags(self):
        """
        Ensure that the tags created are not duplicated
        :return:
        """
        self.create_tag()
        self.create_tag()

        self.assertEqual(len(Tag.objects.filter(tag="Django")), 1)
