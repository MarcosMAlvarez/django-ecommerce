from django.contrib import admin
from orders.models import Product, Order, OrderDetail

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderDetail)
