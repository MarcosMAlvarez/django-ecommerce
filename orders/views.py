from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Product, Order, OrderDetail
from orders.serializers import ProductSerializer, OrderSerializer, OrderDetailSerializer
from orders.utils import stock


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product ViewSet
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['PUT'], url_path='modify-stock')
    def modify_stock(self, request, pk=None):
        """Modify stock of a product."""
        instance = Product.objects.get(pk=pk)
        serializer = self.get_serializer(
            instance,
            data=request.data,
            many=isinstance(request.data, list),
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order ViewSet
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """Delete an order's detail restoring the stock of the product."""
        order_instance = self.get_object()

        details_instances = OrderDetail.objects.filter(order_id=order_instance.id).all()
        for detail_instance in details_instances:
            product_instance = Product.objects.filter(pk=detail_instance.product_id).get()
            stock.restore_stock(product_instance, detail_instance)

        order_instance.delete()
        return Response({"msg": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET"], url_path="get-details")
    def get_details(self, request, pk=None):
        """Modify stock of a product."""
        order_details = OrderDetail.objects.filter(order=pk).all().values()
        return Response(order_details)


class OrderDetailViewSet(viewsets.ModelViewSet):
    """
    OrderDetail ViewSet
    """
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create an order's detail validating that product has stock, and it is not repeated."""
        try:
            Order.objects.filter(pk=request.data["order"]).get()
        except Order.DoesNotExist:
            return Response(
                {"msg": f"Order id {request.data['order']} does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            product_instance = Product.objects.filter(pk=request.data["product"]).get()
        except Product.DoesNotExist:
            return Response({"msg": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        product_stock = product_instance.stock

        order_details = self.queryset.values()
        for detail in order_details:
            if request.data["product"] == detail["product_id"]:
                return Response({"msg": "Product already ordered."}, status=status.HTTP_400_BAD_REQUEST)

        product_stock = product_stock - request.data["cuantity"]
        if product_stock < 0:
            return Response({"msg": "Stock unavailable."}, status=status.HTTP_400_BAD_REQUEST)

        product_serializer = ProductSerializer(product_instance, data={"stock": product_stock}, partial=True)
        if product_serializer.is_valid():
            product_serializer.save()

        order_detail_serializer = self.get_serializer(data=request.data)
        if not order_detail_serializer.is_valid():
            return Response(order_detail_serializer.errors)
        order_detail_serializer.save()
        return Response({"msg": f"{product_instance.name} added."}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Delete an order's detail restoring the stock of the product."""
        detail_instance = self.get_object()

        product_instance = Product.objects.filter(pk=detail_instance.product_id).get()
        stock.restore_stock(product_instance, detail_instance)

        detail_instance.delete()
        return Response({"msg": "OrderDetail deleted"}, status=status.HTTP_204_NO_CONTENT)
