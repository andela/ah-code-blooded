import json

from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.articles.tests.api.test_articles import BaseArticlesTestCase


class TagCreationTestCase(BaseArticlesTestCase):

    def setUp(self):
        super().setUp()
        self.tags = {
            "tags": [
                "Andela",
                "Cohort 30",
                "MacBook Pro 2016"
            ]
        }
        # create an article
        self.article = self.create_article()

    def generate_url(self, slug):
        """
        Generate tagging url for an article
        :param slug:
        :return:
        """
        return reverse("articles:article-tags", kwargs={'slug': slug or self.article['slug']})

    def tag_article(self, slug=None, tags=None):
        """
        Helper method to tag an article
        :param slug:
        :param tags:
        :return:
        """
        return self.client.post(self.generate_url(slug or self.article['slug']), tags or self.tags, format="json")

    def un_tag_article(self, slug=None, tags=None):
        """
        Helper method to remove tags from an article
        :param slug:
        :param tags:
        :return:
        """
        return self.client.delete(self.generate_url(slug or self.article['slug']), tags or self.tags, format="json")

    def list_tags(self, slug=None):
        """
        Helper method to get the tags for a particular article
        :param slug:
        :return:
        """
        return self.client.get(self.generate_url(slug or self.article['slug']))

    def test_user_can_tag_article(self):
        """
        Make sure a user can add tags to their own article
        :return:
        """
        response = self.tag_article()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        slug = json.loads(response.content)['data']['article']
        tags = json.loads(response.content)['data']['tags']
        for tag in self.tags['tags']:
            self.assertIn(tag, tags)
        self.assertEqual(slug, self.article['slug'])

    def test_unauthenticated_user_cannot_tag_article(self):
        """
        Ensure an unauthenticated user cannot tag an article
        :return:
        """
        self.logout()
        response = self.tag_article()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_another_only_owner_can_tag_article(self):
        """
        Ensure only the owner of the article can add tags to it
        :return:
        """
        self.register_and_login(self.user2)
        response = self.tag_article()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tags_cannot_be_duplicated(self):
        """
        Ensure the tags are not duplicated when they are created
        :return:
        """
        self.tag_article()
        response = self.tag_article()
        tags = json.loads(response.content)['data']['tags']
        for tag in self.tags['tags']:
            # ensure each tag appears only once
            self.assertEqual(tags.count(tag), 1)