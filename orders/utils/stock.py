from orders.models import Product, OrderDetail
from orders.serializers import ProductSerializer


def restore_stock(product_instance: Product, detail_instance: OrderDetail) -> None:
    """Restore stock of a product from an order detail deleted."""
    product_stock = product_instance.stock + detail_instance.cuantity
    product_serializer = ProductSerializer(product_instance, data={'stock': product_stock}, partial=True)
    product_serializer.is_valid(raise_exception=True)
    product_serializer.save()
