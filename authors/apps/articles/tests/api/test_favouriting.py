""""Imports modules"""
from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase


class TestFavouriteArticle(BaseArticlesTestCase):
    """"""
    def setUp(self):
        super().setUp()
        self.fav_user = {"user": {
            "username": "brybzz",
            "email": "bry@gmail.com",
            "password": "Bryzzz@123"
        }}

    def test_user_can_favourite_article(self):
        """"registered user can favourite article"""
        slug = self.create_article()['slug']
        self.register_and_login(self.fav_user)
        response = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"message":"Article favourited"}')

    def test_user_cant_favourite_twice(self):
        """registered user cant unfavourite the same article twice"""
        slug = self.create_article()['slug']
        self.register_and_login(self.fav_user)
        response = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        response2 = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.content, b'{"errors":["Article already favourited"]}')

    def test_user_cant_unfavourite_unfavourited_article(self):
        """registered user cant unfavourite the same article twice"""
        slug = self.create_article()['slug']
        self.register_and_login(self.fav_user)
        response = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        response2 = self.client.delete(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        response3 = self.client.delete(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.content, b'{"errors":["Article not favourited"]}')

    def test_user_cant_unfavourite_not_favourited_article(self):
        """registered user cant unfavourite not already favourited article"""
        slug = self.create_article()['slug']
        self.register_and_login(self.fav_user)
        response = self.client.delete(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, b'{"errors":["Article not favourited"]}')

    def test_user_can_unfavourite_article(self):
        """registered user can unfavourite"""
        slug = self.create_article()['slug']
        self.register_and_login(self.fav_user)
        response = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response2 = self.client.delete(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response2.content, b'{"message":"Article removed from favourites"}')

    def test_unregistered_user_cant_favourite_article(self):
        """unregistered user cant favourite an article"""
        slug = self.create_article()['slug']
        self.logout()
        response = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.content, b'{"detail":"Authentication credentials were not provided."}')

    def test_unregistered_user_cant_unfavourite_article(self):
        """unregistered user cant unfavourite an article"""
        slug = self.create_article()['slug']
        self.logout()
        response = self.client.delete(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.content, b'{"detail":"Authentication credentials were not provided."}')

    def test_unregistered_user_cant_favourite_wrong_article(self):
        """a registered user cannot favourite an article with a wrong slug"""
        slug = "jklmno"
        self.register_and_login(self.fav_user)
        response = self.client.post(reverse(
            'articles:favourite_article', kwargs={'slug': slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.content, b'{"detail":"this slug doesnt match any article"}')