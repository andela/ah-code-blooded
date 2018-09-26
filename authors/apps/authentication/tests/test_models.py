from django.test import TestCase

from authors.apps.authentication.models import (
    User, UserManager
)


class UserManagerTest(TestCase):
    """
    This tests the UserManager class, ability to create a user and create a super user.

    """

    def setUp(self):
        """"
        Initializes all our test variables.
        """
        self.userManager = UserManager()

    def test_create_user(self):
        """
        Checks whether the User manager class creates a user with a username, email and password
        :return:
        """
        self.assertIsInstance(
            self.userManager.create_user(username="username", email="username@mail.com", password="password"), User)

    def test_cannot_create_user_without_email(self):
        """
        Ensure that user manager cannot create a user with no email
        :return:
        """
        with self.assertRaises(TypeError):
            self.userManager.create_user(username="username", password="password", email=None)

    def test_create_superuser(self):
        """
        Checks whether the UserManager class creates a super user
        :return:
        """
        user = self.userManager.create_superuser(username="admin", email="admin@admin.com", password="password")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_cannot_create_superuser_without_password(self):
        """
        Ensures the
        :return:
        """
        with self.assertRaises(TypeError):
            self.userManager.create_superuser(username="admin", email="admin@admin.com")
