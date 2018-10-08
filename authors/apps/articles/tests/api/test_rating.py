from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.articles.models import Article, ArticleRating
from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase


class TestArticleRating(BaseArticlesTestCase):

    def setUp(self):
        super().setUp()
        self.register()
        self.articleRating = {
            "rating": {
                "rating": 3
            }
        }
        self.rating_user = {
            "user": {
                "username": "emily",
                "email": "emily@gmail.com",
                "password": "password"
            }
        }


    def test_user_can_rate_available_article(self):
        """
        User who can rate article has to be authenticated
        """
        article = self.create_article()['slug']
        slug = self.create_article()['slug']
        rating = self.articleRating
        self.register_and_login(self.rating_user)
        response = self.client.post(reverse("articles:rate-article", kwargs={'slug': slug}), data=rating, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b"You have successfully rated this article", response.content)

    def test_user_cannot_rate_unavailable_article(self):
        """
        If article does not exist, user cannot rate it
        """
        article = None
        slug = None
        rating = self.articleRating
        self.register_and_login(self.rating_user)
        response = self.client.post(reverse("articles:rate-article", kwargs={'slug': slug}), data=rating, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(b"This article does not exist!", response.content)

    def test_author_cannot_rate_his_articlw(self):
        """
        Writers of articles cannot rate their own articles
        Their articles are rated by other users instead
        """
        article = self.create_article()['slug']
        slug = self.create_article()['slug']
        rating = self.articleRating
        response = self.client.post(reverse("articles:rate-article", kwargs={'slug': slug}), data=rating, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(b"You cannot rate your own article.", response.content)

    