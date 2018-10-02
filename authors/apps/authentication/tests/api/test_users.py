from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.api.test_auth import AuthenticatedTestCase


class UserRetrieveUpdateAPIViewTest(AuthenticatedTestCase):
    """
    Test the ability for a user to update their profile and retrieve their profile details
    """

    def setUp(self):
        self.userDetails = {
            "user": {
                "email": "anotheremail@gmail.com",
                "bio": "The quick brown fox jumped over the lazy dogs.",
                "image": "https://images.io/jKLJSDLFKJADUF8ADFASDF.jpg"
            }
        }

    def test_can_retrieve_user_details(self):
        """
        Retrieve user details - the user has to be authenticated
        :return:
        """
        response = self.client.get(reverse("authentication:user-retrieve-update"), data={}, format="json")
        self.assertIsNotNone(response.data['user'])

    def test_can_update_user_details(self):
        """
        Update the user's profile - the user has to be authenticated
        :return:
        """
        response = self.client.put(reverse("authentication:user-retrieve-update"), data=self.userDetails, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['user'])

    def test_cannot_retrieve_unauthenticated_user_details(self):
        """
        Try to retrieve details of a user that is not authenticated. Should not be an authorized operation
        :return:
        """
        self.logout()
        response = self.client.get(reverse("authentication:user-retrieve-update"), data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_unauthenticated_user_details(self):
        """
        Try to update the details of a unauthenticated user
        :return:
        """
        self.logout()
        response = self.client.put(reverse("authentication:user-retrieve-update"), data=self.userDetails, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
