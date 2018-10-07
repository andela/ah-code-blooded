import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User


class AuthenticationTestCase(APITestCase):
    """
    Extend this class in order to use the helper functions to login and sign up a user
    """

    def setUp(self):
        self.user = {
            "user": {
                "username": "bev",
                "password": "password",
                "email": "beverly@gmail.com"
            }
        }

    def register(self, user=None):
        if user is None:
            user = self.user
        return self.client.post(reverse("authentication:user-register"), data=user, format="json")

    def login(self, user=None):
        if user is None:
            user = self.user
        return self.client.post(reverse("authentication:user-login"), data=user, format="json")


class AuthenticatedTestCase(AuthenticationTestCase):
    """
    Extend this class in order to perform tests for an authenticated user
    """

    def setUp(self):
        super().setUp()
        """
        Register the user for further authentication
        :return:
        """
        self.register()  # register the user
        self.verify_user() # by default, the user is verified
        self.login()

    def logout(self):
        """
        Unset the HTTP Authorization header whenever you need to use an unauthenticated user
        :return:
        """
        self.client.credentials(HTTP_AUTHORIZATION="")

    def login(self, user=None):
        """
        Login the user to the system and also set the authorization headers
        :param user:
        :return:
        """
        response = super().login(user)  # login the user
        self.client.credentials(HTTP_AUTHORIZATION="Token " + (json.loads(response.content))['user']['token'])
        return response

    def verify_user(self, email=None):
        """
        Verify the user
        :param email:
        :return:
        """
        if email is None:
            email = self.user['user']['email']
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()

    def unverify_user(self, email=None):
        """
        Unverify a user's account in order to perform some tests
        :param email:
        :return:
        """
        if email is None:
            email = self.user['user']['email']
        user = User.objects.get(email=email)
        user.is_verified = False
        user.save()


class RegistrationViewTestCase(AuthenticationTestCase):
    """
    Tests if a user can be registered successfully with username, email and password
    """

    def test_user_can_register(self):
        """"
        Tests if user can register successfully
        """
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(json.loads(res.content)['user']['token'])

    def test_user_cannot_register_twice(self):
        """
        Test a user cannot register twice.
        """

        # registering a new user
        self.register()
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'user with this email already exists.', res.content)


class LoginViewTestCase(AuthenticationTestCase):
    """
    Test for authentication in username and password login
    """

    def test_user_cannot_login_before_registering(self):
        """
        Test user cannot login before registering
        """
        res = self.login()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'A user with this email and password was not found.', res.content)

    def test_user_can_login(self):
        """
        Test user can login successfully
        """
        self.register()
        res = self.login()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(json.loads(res.content)['user']['token'])
