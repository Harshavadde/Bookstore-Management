from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Book

User = get_user_model()

class BookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bookuser", password="bookpass123")
        self.book = Book.objects.create(title="Test Book", author="Author A", price=9.99, stock=5)

        # Login and get token
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "bookuser", "password": "bookpass123"})
        self.token = response.data["access"]

    def test_list_books(self):
        url = reverse("book-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_book(self):
        url = reverse("book-list-create")
        data = {"title": "New Book", "author": "Author B", "price": "15.00", "stock": 10}
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book(self):
        url = reverse("book-detail", args=[self.book.id])
        data = {"title": "Updated Book", "author": "Author X", "price": "20.00", "stock": 7}
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Book")

    def test_delete_book(self):
        url = reverse("book-detail", args=[self.book.id])
        response = self.client.delete(url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
