import json

from notifications.signals import notify
from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.api.test_auth import AuthenticatedTestCase


class BaseNotificationsTestCase(AuthenticatedTestCase):
    DEFAULT_NOTIFICATION_COUNT = 10

    def setUp(self):
        super().setUp()
        self.url = reverse("notifications:notifications")

    def get(self):
        """
        Return a list of notifications and response_code
        :return:
        """
        response = self.client.get(self.url)
        return response.status_code, json.loads(response.content)

    def delete(self):
        """
        Delete a list of notifications and return the response
        :return:
        """
        response = self.client.delete(self.url)
        return response.status_code, json.loads(response.content)

    def sendNotification(self, user=None, verb="sample", description="You have a notification"):
        """
        Helper method to send notification to a particular user
        :param user:
        :param verb:
        :param description:
        :return:
        """
        user = user or self.get_authenticated_user()
        notify.send(user, recipient=user, verb=verb, description=description)

    def sendManyNotifications(self, user=None, count=DEFAULT_NOTIFICATION_COUNT):
        """
        Helper method to send many notifications
        :param user:
        :param count:
        :return:
        """
        for i in range(0, count):
            self.sendNotification(user)


class AllNotificationsTestCase(BaseNotificationsTestCase):

    def setUp(self):
        super().setUp()
        self.sendManyNotifications()

    def test_get_all_notifications(self):
        """
        Test can list all the notifications in the system
        :return:
        """
        response_code, data = self.get()
        self.assertEqual(response_code, status.HTTP_200_OK)
        self.assertEqual(data['data']['count'], self.DEFAULT_NOTIFICATION_COUNT)

    def test_delete_all_notifications(self):
        """
        Test that can delete all the notifications
        :return:
        """
        status_code, data = self.delete()
        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], "success")

        status_code, data = self.get()
        self.assertEqual(data['data']['count'], 0)

    def test_unauthenticated_user_cannot_get_notifications(self):
        """
        Ensure an unauthenticated user cannot get notifications
        :return:
        """
        self.logout()
        status_code, data = self.get()
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_notifications(self):
        """
        Ensure a user that is not authenticated cannot delete notifications
        :return:
        """
        self.logout()
        status_code, data = self.delete()
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)

    def test_another_user_cannot_get_my_notifications(self):
        """
        Ensure a user only gets notifications that belong to them
        :return:
        """
        # login another user
        self.authenticate_another_user()
        status_code, data = self.get()
        self.assertEqual(data['data']['count'], 0)
