from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Product, Order, OrderDetail


class TestOrderAuthorization(APITestCase):
    """Test calling order url with and without authorization."""
    def test_order_unauthorized(self):
        response = self.client.get(reverse("orders-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_authorized(self):
        User.objects.create_user(username="user", password="pass")
        response = self.client.post(reverse("token_obtain_pair"), data={"username": "user", "password": "pass"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        response = self.client.get(reverse("orders-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrder(APITestCase):
    """Test order urls"""
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        response = self.client.post(reverse("token_obtain_pair"), data={"username": "user", "password": "pass"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        Order.objects.create()
        Product.objects.create(name="plate", price=3.0, stock=20)
        OrderDetail.objects.create(order_id=1, cuantity=5, product_id=1)

    def test_get_order_and_payment(self):
        response = self.client.get("/orders/1/")
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["get_total"], Decimal(3.0 * 5))

    def test_get_all_orders(self):
        for _ in range(3):
            Order.objects.create()
        response = self.client.get(reverse("orders-list"))
        self.assertEqual(len(response.data), 4)

    def test_get_all_details(self):
        response = self.client.get("/orders/1/get-details/")
        self.assertEqual(response.data[0], {"id": 1, "order_id": 1, "cuantity": 5, "product_id": 1})

    def test_delete_order_and_stock_restoration(self):
        self.client.delete("/orders/1/")

        response = self.client.get("/order-details/1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get("/products/1/")
        self.assertEqual(response.data["stock"], 25)
