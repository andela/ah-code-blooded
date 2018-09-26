from django.test import TestCase
from rest_framework import status

class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.user = {"username": "bev", "password": "password", "email": "beverly@gmail.com"}

    def register(self, user = self.user):
        return self.client.post("/api/users", data=user, format="json")

    def login(self, user=self.user):
        return self.client.post("/api/users/login", data=user, format="json")

class ViewsTestCase(AuthenticationTestCase):
    """
    Tests if a user can be registered suessfully with username, email and password
    
    """

    def test_user_can_register(self):
        """"
        Tests if user can register successfully
        """

        # registering a new user
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'User registered successfully', res.data)

    def test_user_cannot_register_twice(self):
        """
        Test a user cannot register twice.
        """

        # registering a new user
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'User registered successfully', res.data)

        # registering the same user again
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'User already exists. Please login.', res.data)

    def test_user_cannot_login_before_registering(self):
        """
        Test user cannot login before registering
        """

        # login a user
        res = self.login()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(b'User not found. Please register before you login.', res.data)
        
    def test_user_can_login(self):
        """
        Test user can login suessfully
        """
        res = self.login()
        self.assertEqual(rv.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['user'])
        self.assertIsNotNone(res.data['user']['token'])




         