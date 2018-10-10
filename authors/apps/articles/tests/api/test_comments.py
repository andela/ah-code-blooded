from rest_framework import status
from rest_framework.reverse import reverse
from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase
import json


class TestArticleComment(BaseArticlesTestCase):
    """This class tests for comment article"""

    def setUp(self):
        super().setUp()
        self.register()
        self.comment = {"comment": {"body": "comment on this "}}
        self.thread = {"comment": {"body": "comment on this thread "}}
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

    def test_get_comment_related_article(self):
        """Test get comment related to article"""
        self.register_and_login(self.user)
        slug = self.create_article()['slug']
        comment = self.comment
        response = self.client.get(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_unavailable_article(self):
        """Test commenting on non-existing-comment"""
        self.register_and_login(self.user)
        slug = None
        comment = self.comment
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_thread_comment_related_article(self):
        """Test thread comment related to article"""
        self.register_and_login(self.user)
        slug = self.create_article()["slug"]
        comment = self.comment
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        pk = json.loads(response.content)["id"]
        response = self.client.post(
            reverse("articles:a-comment", kwargs={
                'slug': slug,
                'pk': pk
            }),
            data=self.thread,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_thread_comment_unavailable_article(self):
        """Test thread-commenting on non-existing-comment"""
        self.register_and_login(self.user)
        slug = None
        comment = self.comment
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        pk = json.loads(response.content)
        response = self.client.post(
            reverse("articles:a-comment", kwargs={
                'slug': slug,
                'pk': pk
            }),
            data=self.thread,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment(self):
        """Test update comment related to article"""
        self.register_and_login(self.user)
        slug = self.create_article()["slug"]
        comment = self.comment
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        pk = json.loads(response.content)["id"]
        response = self.client.put(
            reverse("articles:a-comment", kwargs={
                'slug': slug,
                'pk': pk
            }),
            data=self.thread,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_comment(self):
        """Test delete comment related to article"""
        self.register_and_login(self.user)
        slug = self.create_article()["slug"]
        comment = self.comment
        response = self.client.post(
            reverse("articles:comments", kwargs={'slug': slug}),
            data=comment,
            format="json")
        pk = json.loads(response.content)["id"]
        response = self.client.delete(
            reverse("articles:a-comment", kwargs={
                'slug': slug,
                'pk': pk
            }),
            data=self.thread,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)