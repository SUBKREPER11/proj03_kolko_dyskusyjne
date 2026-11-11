from django.test import TestCase
from django.urls import reverse

from .models import User


class SignUpTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'jan',
            'email': 'Jan@Example.com',
            'password1': 'BardzoTrudne123!',
            'password2': 'BardzoTrudne123!',
        })
        self.assertRedirects(response, reverse('boards:board_list'))
        user = User.objects.get(username='jan')
        self.assertEqual(user.email, 'jan@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user('ala', 'ala@example.com', 'x')
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'ala2',
            'email': 'ALA@example.com',
            'password1': 'BardzoTrudne123!',
            'password2': 'BardzoTrudne123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='ala2').exists())


class SettingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('jan', 'jan@example.com', 'BardzoTrudne123!', email_verified=True)

    def test_settings_requires_login(self):
        response = self.client.get(reverse('accounts:settings'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:settings')}")

    def test_update_settings_resets_verification_on_email_change(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:settings'), {
            'email': 'nowy@example.com', 'bio': 'Cześć', 'theme': 'dark',
        })
        self.assertRedirects(response, reverse('accounts:settings'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.theme, 'dark')
        self.assertEqual(self.user.bio, 'Cześć')
        self.assertFalse(self.user.email_verified)

    def test_password_change_keeps_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'BardzoTrudne123!',
            'new_password1': 'InneHaslo456!',
            'new_password2': 'InneHaslo456!',
        })
        self.assertRedirects(response, reverse('accounts:settings'))
        self.assertEqual(self.client.get(reverse('accounts:settings')).status_code, 200)


class LoginLogoutProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('jan', 'jan@example.com', 'BardzoTrudne123!')

    def test_login_and_logout(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'jan', 'password': 'BardzoTrudne123!',
        })
        self.assertRedirects(response, reverse('boards:board_list'))
        self.client.post(reverse('accounts:logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_page(self):
        response = self.client.get(reverse('accounts:profile', kwargs={'username': 'jan'}))
        self.assertContains(response, 'jan')
