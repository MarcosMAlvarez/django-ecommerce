from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Product, Order, OrderDetail
from orders.utils import stock


class TestProductAuthorization(APITestCase):
    """Test calling product url with and without authorization."""
    def test_product_unauthorized(self):
        response = self.client.get(reverse("products-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_authorized(self):
        User.objects.create_user(username="user", password="pass")
        response = self.client.post(reverse("token_obtain_pair"), data={"username": "user", "password": "pass"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        response = self.client.get(reverse("products-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestProduct(APITestCase):
    """Test product urls"""
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        response = self.client.post(reverse("token_obtain_pair"), data={"username": "user", "password": "pass"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        Product.objects.create(name="plate", price=3.0, stock=20)

    def test_get_product(self):
        response = self.client.get("/products/1/")
        self.assertEqual(response.data["name"], "plate")

    def test_get_all_orders(self):
        for _ in range(3):
            Product.objects.create(name="test-product", price=1.0, stock=1)
        response = self.client.get(reverse("products-list"))
        self.assertEqual(len(response.data), 4)

    def test_modify_stock(self):
        response = self.client.put("/products/1/modify-stock/", {"stock": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/products/1/")
        self.assertEqual(response.data["stock"], 10)

    def test_delete_product(self):
        self.client.delete("/products/1/")
        response = self.client.get("/products/1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stock_helper(self):
        Order.objects.create()
        OrderDetail.objects.create(order_id=1, cuantity=5, product_id=1)
        product_instance = Product.objects.first()
        detail_instance = OrderDetail.objects.first()

        stock.restore_stock(product_instance, detail_instance)
        self.assertEqual(Product.objects.first().stock, 25)
