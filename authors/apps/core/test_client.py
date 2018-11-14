from django.test import TestCase
from authors.apps.core.client import get_activate_account_link, get_password_reset_link


class TestGenerateLinks(TestCase):

    def test_get_activate_account_link(self):
        self.assertEqual(get_activate_account_link("token", 'uid'), "http://localhost:3000/activate-account?token=token&uid=uid")
    def test_get_password_reset_link(self):
        self.assertEqual(get_password_reset_link('token'), "http://localhost:3000/reset-password?token=token")