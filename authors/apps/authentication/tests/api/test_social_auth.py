"""
Test for the social authentication with Google
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

access_token = '''
EAAJrz4Wyof4BALP69kKhbavn0orNiZACWttkmT
xdYeapBJR487dpLnIWaBmKaGnYJxyRI09OdRF8krBOL6isVZBZC1rZCo6
acc9sZBymZBX0ZB83WmWOPj6vzRrPtTdqZBxceZCnFjPtaoJjJCbHeuXsH
4LzeKHfe5MMR2dpz0qe2M3maZBznrxsNRQWl37qxCvlCelZCiVEDoZCTtn
wDdV0zZC84tsqQIDPQN9CiitF2K6jvRgZDZD
'''


class SocialAuthTest(APITestCase):
    """
    Base Test Class for the Social Authentication
    """
    def test_provider_in_payload(self):
        """
        Test that the OAuth provider is included in request
        """
        payload = {
            "provider": "",
            "access_token": access_token
        }
        res = self.client.post(
            reverse("authentication:social"),
            payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_token_in_payload(self):
        """
        Test that the OAuth access_token is provided
        """
        payload = {
            "provider": "facebook",
            "access_token": ""
        }
        res = self.client.post(
            reverse("authentication:social"),
            payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_token_is_valid(self):
        """
        When access_token is included in payload, check for validity
        """
        payload = {
            "provider": "facebook",
            "access_token": access_token + "FAKETOKEN"
        }
        res = self.client.post(
            reverse("authentication:social"),
            payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
