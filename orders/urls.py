from rest_framework.routers import DefaultRouter
from orders.views import ProductViewSet, OrderViewSet, OrderDetailViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'order-details', OrderDetailViewSet, basename='order-details')

urlpatterns = router.urls
