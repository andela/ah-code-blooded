from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class AuthenticationTestCase(APITestCase):
    """
    Extend this class in order to use the helper functions to login and sign up a user
    """

    def setUp(self):
        self.user = {"username": "bev", "password": "password", "email": "beverly@gmail.com"}

    def register(self, user=None):
        if user is None:
            user = self.user
        return self.client.post(reverse("user-register"), data=user, format="json")


    def login(self, user=None):
        if user is None:
            user = self.user
        return self.client.post(reverse("user-login"), data=user, format="json")


class AuthenticatedTestCase(AuthenticationTestCase):
    """
    Extend this class in order to perform tests for an authenticated user
    """

    def setUp(self):
        """
        Register the user for further authentication
        :return:
        """
        self.register()  # register the user
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
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + response.data['user']['token'])
        return response


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
        self.assertIn(b'User registered successfully', res.data)

    def test_user_cannot_register_twice(self):
        """
        Test a user cannot register twice.
        """

        # registering a new user
        self.register()
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'User already exists. Please login.', res.data)


class LoginViewTestCase(AuthenticationTestCase):
    """
    Test for authentication in username and password login
    """

    def test_user_cannot_login_before_registering(self):
        """
        Test user cannot login before registering
        """
        res = self.login()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(b'User not found. Please register before you login.', res.data)

    def test_user_can_login(self):
        """
        Test user can login successfully
        """
        res = self.login()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['user'])
        self.assertIsNotNone(res.data['user']['token'])
