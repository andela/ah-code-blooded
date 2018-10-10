from rest_framework import status
from rest_framework.reverse import reverse
from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase
import json


class TestCommentLikeDislike(BaseArticlesTestCase):
    """This class tests for like and dislike of article"""

    def setUp(self):
        super().setUp()
        self.register()
        self.slug = self.create_article()['slug']
        self.comment = {"comment": {"body": "comment on this "}}
        self.thread = {"comment": {"body": "comment on this thread "}}
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': self.slug}),
            data=self.comment,
            format="json")
        self.pk = json.loads(response.content)["id"]
        self.user = {
            "user": {
                "username": "tester001",
                "email": "test@example.com",
                "password": "@secret123"
            }
        }

    # like helpers
    def like_url(self, slug, pk):
        return reverse('articles:likes', kwargs={'slug': slug, "pk": pk})

    def like(self, slug, pk):
        return self.client.put(self.like_url(slug=slug, pk=pk))

    def test_user_can_like_comment(self):
        """Test like a comment"""
        self.register_and_login(self.user)
        response = self.like(self.slug, self.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)