from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from books.models import Book
from .models import Order

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="orderpass123")
        self.book1 = Book.objects.create(title="Book One", author="A", price=10.00, stock=10)
        self.book2 = Book.objects.create(title="Book Two", author="B", price=20.00, stock=5)

        # Login and get token
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "orderuser", "password": "orderpass123"})
        self.token = response.data["access"]

    def test_create_order(self):
        url = reverse("order-list-create")
        data = {
            "user": self.user.id,
            "items": [
                {"book": self.book1.id, "quantity": 2},
                {"book": self.book2.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Bearer {self.token}", format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().items.count(), 2)

    def test_list_orders(self):
        # First create an order
        self.test_create_order()

        url = reverse("order-list-create")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_order_detail(self):
        # Create order
        self.test_create_order()
        order = Order.objects.first()

        url = reverse("order-detail", args=[order.id])
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], order.id)
