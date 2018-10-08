from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.authentication.tests.api.test_auth import AuthenticatedTestCase


class TestArticleRating(AuthenticatedTestCase):

    def setUp(self):
        super().setUp()
        self.register()
        self.articleRating = {
            "rating": {
                "rating": 3
            }
        }

    def test_user_can_rate_available_article(self):
        """
        User who can rate article has to be authenticated
        """
        response = self.client.post(reverse("articles:rate-article", kwargs={'slug':'this-is-a-slug'}), data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b"You have successfully rated this article", response.content)

    