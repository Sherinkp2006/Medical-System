from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Pharmacy


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='admin',
            password='test-password',
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username='alex',
            password='test-password',
            first_name='Alex',
            last_name='Morgan',
            email='alex@example.com',
        )
        User.objects.create_user(
            username='casey',
            password='test-password',
            email='casey@example.com',
        )
        Pharmacy.objects.create(
            medicine_name='Example medicine',
            manufacturer='Example Labs',
            manufacture_date=date(2025, 1, 1),
            expiry_date=date(2027, 1, 1),
            unit_price=Decimal('12.50'),
            stock_available=Decimal('4'),
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get('/admin-dashboard/')

        self.assertRedirects(response, '/login/?next=/admin-dashboard/')

    def test_regular_user_is_forbidden(self):
        self.client.force_login(self.regular_user)

        response = self.client.get('/admin-dashboard/')

        self.assertEqual(response.status_code, 403)

    def test_staff_can_view_user_and_inventory_details(self):
        self.client.force_login(self.staff_user)

        response = self.client.get('/admin-dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alex@example.com')
        self.assertContains(response, 'Example medicine')
        self.assertContains(response, '₹50.00')

    def test_user_search_matches_names_and_email(self):
        self.client.force_login(self.staff_user)

        response = self.client.get('/admin-dashboard/', {'q': 'Morgan'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alex@example.com')
        self.assertNotContains(response, 'casey@example.com')

    def test_staff_can_delete_another_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(f'/admin-dashboard/users/{self.regular_user.pk}/delete/')

        self.assertRedirects(response, '/admin-dashboard/')
        self.assertFalse(User.objects.filter(pk=self.regular_user.pk).exists())

    def test_staff_cannot_delete_their_own_account(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(f'/admin-dashboard/users/{self.staff_user.pk}/delete/')

        self.assertRedirects(response, '/admin-dashboard/')
        self.assertTrue(User.objects.filter(pk=self.staff_user.pk).exists())

    def test_last_superuser_cannot_be_deleted(self):
        superuser = User.objects.create_superuser(
            username='root',
            password='test-password',
        )
        self.client.force_login(self.staff_user)

        response = self.client.post(f'/admin-dashboard/users/{superuser.pk}/delete/')

        self.assertRedirects(response, '/admin-dashboard/')
        self.assertTrue(User.objects.filter(pk=superuser.pk).exists())

    def test_regular_user_cannot_delete_accounts(self):
        self.client.force_login(self.regular_user)

        response = self.client.post(f'/admin-dashboard/users/{self.staff_user.pk}/delete/')

        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.staff_user.pk).exists())
