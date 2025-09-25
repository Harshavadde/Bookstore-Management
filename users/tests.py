from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

    def test_user_list_requires_auth(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_login_and_get_token(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "testuser", "password": "testpass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_admin_can_list_users(self):
        # Login as admin
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "admin", "password": "adminpass123"})
        token = response.data["access"]

        url = reverse("user-list")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
