from rest_framework_nested import routers
from .views import ProductViewSet, CollectionViewSet, ReviewViewSet


router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet)

product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')

product_router.register('reviews', ReviewViewSet, basename='product-reviews')

urlpatterns = router.urls + product_router.urls
