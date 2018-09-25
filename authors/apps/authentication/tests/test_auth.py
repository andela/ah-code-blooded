from django.test import TestCase
from rest_framework import status

class ViewsTestCase(TestCase):
    """Tests if a user can be registered suessfully with username, email and password"""
    def SetUp(self):
        self.user = {
            "username": "Yahya Hassan",
            "email": "hassan@gmail.com",
            "password": "pass1234"
         }
        self.response = self.client.post(
            'users/', 
            self.user,
            format="json"
         )A

    def test_user_can_register(self):
        """"Tests if user can register successfully"""
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

         