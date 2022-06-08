from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Product, Order, OrderDetail


class TestOrderDetailAuthorization(APITestCase):
    """Test calling order detail url with and without authorization."""
    def test_detail_unauthorized(self):
        response = self.client.get(reverse("order-details-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_authorized(self):
        User.objects.create_user(username="user", password="pass")
        response = self.client.post(reverse("token_obtain_pair"), data={"username": "user", "password": "pass"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        response = self.client.get(reverse("order-details-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrderDetail(APITestCase):
    """Test order detail urls"""
    def setUp(self):
        User.objects.create_user(username="user", password="pass")
        response = self.client.post(reverse("token_obtain_pair"), data={"username": "user", "password": "pass"})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        Order.objects.create()
        Product.objects.create(name="plate", price=3.0, stock=20)
        OrderDetail.objects.create(order_id=1, cuantity=5, product_id=1)

    def test_get_detail(self):
        response = self.client.get("/order-details/1/")
        self.assertEqual(response.data["id"], 1)

    def test_get_all_details(self):
        for index in range(2, 4):
            Product.objects.create(name="test-product", price=1.0, stock=1)
            OrderDetail.objects.create(order_id=1, cuantity=1, product_id=index)
        response = self.client.get(reverse("order-details-list"))
        self.assertEqual(len(response.data), 3)

    def test_create_detail(self):
        Product.objects.create(name="test-product", price=1.0, stock=10)
        response = self.client.post("/order-details/", data={"order": 1, "cuantity": 3, "product": 2}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/products/2/")
        self.assertEqual(response.data["stock"], 7)

    def test_create_detail_no_product_and_order(self):
        response = self.client.post("/order-details/", data={"order": 2, "cuantity": 3, "product": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"msg": "Order id 2 does not exist."})

        response = self.client.post("/order-details/", data={"order": 1, "cuantity": 3, "product": 2}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"msg": "Product does not exist."})

    def test_create_detail_duplicated_product(self):
        response = self.client.post("/order-details/", data={"order": 1, "cuantity": 3, "product": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"msg": "Product already ordered."})

    def test_create_detail_no_stock(self):
        Product.objects.create(name="test-product", price=1.0, stock=10)
        response = self.client.post("/order-details/", data={"order": 1, "cuantity": 11, "product": 2}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"msg": "Stock unavailable."})

    def test_delete_detail_and_stock_restoration(self):
        self.client.delete("/order-details/1/")
        response = self.client.get("/order-details/1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get("/products/1/")
        self.assertEqual(response.data["stock"], 25)
