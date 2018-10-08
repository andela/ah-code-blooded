from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile


class TestProfile(APITestCase):
    """
    Tests profile creation.
    """

    def setUp(self):
        self.register_url = reverse('authentication:user-register')
        self.get_all_url = reverse('profiles:get-profiles')
        username = 'chomba'
        self.get_profiles_url = reverse('profiles:profiles', kwargs={'username': username})
        self.login_url = reverse('authentication:user-login')

        self.user = {
            'user': {
                'username': 'chariss',
                'email': 'chariss@gmail.com',
                'password': 'chariss12345'
            }
        }
        self.user2 = {
            'user': {
                'username': 'chomba',
                'email': 'chomba@gmail.com',
                'password': 'chomba12345'
            }}

        self.login = {
            'user': {
                'email': 'chomba@gmail.com',
                'password': 'chomba12345'
            }}
        # self.client.post(self.register_url, self.user, format="json")
        self.client.post(self.register_url, self.user2, format="json")

    def test_create_profile(self):
        """
        Tests whether a new profile object is created on registration
        """
        resp = self.client.post(self.register_url, self.user, format="json")
        current_users = User.objects.count()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), current_users)
        self.assertEqual(Profile.objects.count(), current_users)

    def test_get_all_profiles(self):
        response = self.client.post(self.login_url, self.login, format="json")
        token = response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        res = self.client.get(self.get_all_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_profiles_unauthenticated(self):
        res = self.client.get(self.get_all_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_single_profile(self):
        response = self.client.post(self.login_url, self.login, format="json")
        token = response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        res = self.client.get(self.get_profiles_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_single_profile_unauthenticated(self):
        res = self.client.get(self.get_profiles_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_update_profile_bio(self):
        response = self.client.post(self.login_url, self.login, format="json")
        token = response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        res = self.client.put(self.get_profiles_url, data={'bio': 'This is some bio'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
