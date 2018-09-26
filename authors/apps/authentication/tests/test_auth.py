from django.test import TestCase
from rest_framework import status
<<<<<<< HEAD
<<<<<<< HEAD
from .helpers import register_user, login_user

class ViewsTestCase(TestCase):
    """
    Tests if a user can be registered suessfully with username, email and password
    
    """

    def test_user_can_register(self):
        """"
        Tests if user can register successfully
        """

        # registering a new user
        res = register_user(self)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('User registered successfully', str(res))

    def test_user_cannot_register_twice(self):
        """
        Test a user cannot register twice.
        """

        # registering a new user
        res = register_user(self)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('User registered successfully', str(res))

        # registering the same user again
        res = register_user(self)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User already exists. Please login.', str(res))

    def test_user_cannot_login_before_registering(self):
        """
        Test user cannot login before registering
        """

        # login a user
        rv = login_user(self)
        self.asserEqual(rv.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('User not found. Please register before you login.', str(rv.data))



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

         