from rest_framework import status
from rest_framework.reverse import reverse
from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase


class TestArticleComment(BaseArticlesTestCase):
    """This class tests for comment article"""

    def setUp(self):
        super().setUp()
        self.register()
        self.comment = {"comment": {"body": "comment on this "}}
        self.user = {
            "user": {
                "username": "tester001",
                "email": "test@example.com",
                "password": "@secret123"
            }
        }

    def test_create_comment(self):
        """Authenticated user can add comment"""
        self.register_and_login(self.user)
        slug = self.create_article()['slug']
        comment = self.comment
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
