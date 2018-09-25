from django.test import TestCase
from authors.apps.authentication.models import (
    User, UserManager
)


class UserManagerTest(TestCase):
    """
    This tests the UserManager class, ability to create a user and create a super user.

    """

    def setUp(self):
        self.userManager = UserManager()

    def test_create_user(self):
        """
        Checks whether the User manager class creates a user with a username, email and password
        :return:
        """
        self.assertIsInstance(
            self.userManager.create_user(username="username", email="username@mail.com", password="password"), User)

    def test_cannot_create_user_without_password(self):
        """
        Ensure that user manager cannot create a user with no password
        :return:
        """
        with self.assertRaises(TypeError):
            self.userManager.create_user(username="username", email="username@mail.com")
