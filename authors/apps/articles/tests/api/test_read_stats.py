import json

from django.urls import reverse
from rest_framework import status

from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase
from authors.apps.core.test_helpers import set_test_client, login, logout


class BaseReadStatsTestCase(BaseArticlesTestCase):
    def setUp(self):
        super().setUp()
        set_test_client(self.client)
        self.owner = login(verified=True)
        self.article = self.create_article(published=True)
        self.slug = self.article['slug']
        logout()

    def view_article(self, slug):
        return self.client.get(reverse('articles:articles-detail', kwargs={'slug': slug}))

    def comment_on_article(self, slug, comment="It's awesome."):
        return self.client.post(
            reverse('articles:comments', kwargs={'slug': slug}),
            data={'comment': {'body': comment}},
            format='json'
        )

    def article_stats(self):
        return self.client.get(reverse('articles:stats'))


class ReadStatsTestCase(BaseReadStatsTestCase):
    def setUp(self):
        super().setUp()

    def assertStatsEqual(self, stats, article=None, views=0, comments=0):
        if article is None:
            article = self.article
        stats_list = json.loads(json.dumps(stats))
        data = {
            "slug": article['slug'],
            "title": article['title'],
            "view_count": views,
            "comment_count": comments,
        }
        self.assertIn(data, stats_list)

    def test_initial_stats_are_zero(self):
        # owner logs in
        login(self.owner)
        response = self.article_stats()
        self.assertStatsEqual(response.data, views=0, comments=0)

    def test_owner_view_is_not_added_to_stats(self):
        # owner logs in and views article
        login(self.owner)
        self.view_article(self.slug)
        # owner gets stats
        response = self.article_stats()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertStatsEqual(response.data, views=0)

    def test_views_by_different_users_are_added_to_stats(self):
        # other users view article
        login()
        self.view_article(self.slug)
        login()
        self.view_article(self.slug)
        login()
        self.view_article(self.slug)
        # owner logs in
        login(self.owner)
        response = self.article_stats()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertStatsEqual(response.data, views=3)

    def test_only_one_view_is_added_per_user(self):
        # other users view article
        login()
        self.view_article(self.slug)
        self.view_article(self.slug)
        # owner logs in
        login(self.owner)
        response = self.article_stats()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertStatsEqual(response.data, views=1)

    def test_comments_by_different_users_are_added_to_stats(self):
        # other users comment on article
        login()
        self.comment_on_article(self.slug)
        login()
        self.comment_on_article(self.slug)
        # owner logs in
        login(self.owner)
        response = self.article_stats()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertStatsEqual(response.data, comments=2)

    def test_multiple_comments_by_same_user_are_added_to_stats(self):
        # other users comment on article
        login()
        self.comment_on_article(self.slug)
        self.comment_on_article(self.slug)
        self.comment_on_article(self.slug)
        # owner logs in
        login(self.owner)
        response = self.article_stats()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertStatsEqual(response.data, comments=3)
