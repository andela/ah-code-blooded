import json
import random
import string

from django.utils.text import slugify
from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.api.test_auth import AuthenticatedTestCase


class CreateArticlesTestCase(AuthenticatedTestCase):
    """
    Test for the articles implementation
    """

    def setUp(self):
        super().setUp()
        self.article = {
            "article": {
                "title": "How to train your dragon today",
                "description": "Ever wonder how?",
                "body": "You have to believe in you",
                "tags": [
                    "reactjs",
                    "angularjs",
                    "dragons"
                ],
                "image": "https://dummyimage.com/600x400/000/fff"
            }
        }
        self.url = reverse("articles:articles-list")
        self.user2 = {
            "user": {
                "username": "gitaumoses4",
                "email": "gitaumoses40@gmail.com",
                "password": "password"
            }
        }

    def create_article(self, article=None):
        """
        Helper method to create an article
        :return:
        """
        if article is None:
            article = self.article
        return self.client.post(self.url, data=article, format="json")

    def test_verified_user_can_create_article(self):
        """
        Ensure a verified user can create an article
        :return:
        """
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unverified_user_cannot_create_article(self):
        """
        Ensure an unverified user cannot create an article
        :return:
        """
        self.unverify_user()
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_create_article_without_logging_in(self):
        """
        Ensure that a user has to login in order to create an article
        :return:
        """
        self.logout()
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(b"Authentication credentials were not provided.", response.content)

    def test_cannot_create_article_without_title(self):
        """
        Ensure that a user cannot create an article without a title
        :return:
        """
        self.article['article']['title'] = ''
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'The article must have a title', response.content)

    def test_cannot_create_article_without_description(self):
        """
        Ensure that a user cannot create an article without a description
        :return:
        """
        self.article['article']['description'] = ''
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b"The article must have a description", response.content)

    def test_cannot_create_article_without_body(self):
        """
        Ensure the article must have a body, that is not empty
        :return:
        """
        self.article['article']['body'] = ''
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'The article must have a body', response.content)

    def test_title_cannot_be_more_than_255_characters(self):
        """
        Ensure the title must be less than 255 characters
        :return:
        """
        self.article['article']['title'] = ''.join(
            random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(256))
        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'The article title cannot be more than 255 characters', response.content)

    def test_tags_must_be_a_list(self):
        """
        Ensure the list of tags will be passed in as a list of strings
        :return:
        """
        self.article['article']['tags'] = 'AngularJS'

        response = self.create_article()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b"The tags must be a list of strings", response.content)

    def test_slug_made_from_title(self):
        """
        Ensure the slug is made from the title of the article
        :return:
        """
        response = self.create_article()
        self.assertIn(slugify(self.article['article']['title']),
                      json.loads(response.content)['data']['article']['slug'])
