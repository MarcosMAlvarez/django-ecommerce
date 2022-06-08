from django.db import models
from django.core.cache import cache
import requests
from decimal import Decimal


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date_time",)

    def get_total(self):
        """Get the total payment of the order."""
        order_details = self.order_details.all()
        total = 0
        for detail in order_details:
            cuantity = detail.cuantity
            price = Product.objects.filter(pk=detail.product_id).get().price
            total += cuantity * price
        return total

    def get_total_usd(self):
        """Get the total payment of the order in dollars using dolarsi's api."""
        response = cache.get_or_set(
            "dolarsi_response",
            requests.get("https://www.dolarsi.com/api/api.php?type=valoresprincipales").json()
        )

        dolar_str = next(dict_["casa"]["compra"] for dict_ in response if dict_["casa"]["nombre"] == "Dolar Blue")
        return self.get_total() / Decimal(dolar_str.replace(',', '.'))

    def __str__(self):
        return f"order number {self.id}"


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_details")
    cuantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"details from order {self.order}"
