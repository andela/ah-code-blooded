from django.test import TestCase
from rest_framework import status
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from .helpers import register_user, login_user
=======
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
>>>>>>> [Chore #160577595] Remove hardcoded URLs

class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.user = {"username": "bev", "password": "password", "email": "beverly@gmail.com"}

<<<<<<< HEAD
    def register(self, user = self.user):
        return self.client.post("/api/users", data=user, format="json")

    def login(self, user=self.user):
        return self.client.post("/api/users/login", data=user, format="json")
=======
    def register(self, user=None):
        if user is None:
            user = self.user
        return self.client.post(reverse("authentication:user_register"), data=user, format="json")

    def login(self, user=None):
        if user is None:
            user = self.user
        return self.client.post(reverse("authentication:user_login"), data=user, format="json")
>>>>>>> [Chore #160577595] Remove hardcoded URLs

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
        self.register()
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



=======
=======
from .helpers import register_user, login_user
>>>>>>> [chore #160577595] testing the auth endpoints

class ViewsTestCase(TestCase):
    """Tests if a user can be registered suessfully with username, email and password"""

    def test_user_can_register(self):
        """"Tests if user can register successfully"""
<<<<<<< HEAD
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_user_can_login(self):
        """Test if registered user can logon suessfully"""
        res = self.client.post(
            'users/login/',
            self.user,
            format="json"
        )
        self.asserEqual(self.res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['user'])
        self.assertIsNotNone(res.data['user']['token'])
>>>>>>> [Chore #160577595] Tests for Resistration and login
=======

        # registering a new user
        res = register_user(self)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('User registered successfully', str(res))

    def test_user_cannot_register_twice(self):
        """Test a user cannot register twice."""

        # registering a new user
        res = register_user(self)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('User registered successfully', str(res))

        # registering the same user again
        res = register_user(self)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User already exists. Please login.', str(res))

    def test_user_cannot_login_before_registering(self):
        """Test user cannot login before registering"""

        # login a user
        rv = login_user(self)
        self.asserEqual(rv.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('User not found. Please register.', str(rv.data))



>>>>>>> [chore #160577595] testing the auth endpoints

         