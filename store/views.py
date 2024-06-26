from django.db.models import Count
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from . import models
from . import serializers
from .permissions import IsAdminUserOrReadOnly, ViewCustomerHistoryPermission
from .filters import ProductFilter
from .pagination import DefaultPagination


class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.prefetch_related('images').all()
    serializer_class = serializers.ProductSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if models.OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response(status=405)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.annotate(
        products_count=Count('product')).all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if models.Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response(status=405)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        return models.Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = models.Cart.objects.prefetch_related('items__product').all()
    serializer_class = serializers.CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.methode == 'PATCH':
            return serializers.UpdateCartItemSerializer
        else:
            return serializers.CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return models.CartItem.objects.filter(
            cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = models.Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = serializers.CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateOrderSerializer
        else:
            return serializers.OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'user_id': self.request.user.id},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return models.Order.objects.all()

        customer_id = models.Customer.objects.only('id').get(user_id=user.id)
        return models.Order.objects.filter(customer_id=customer_id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = serializers.ProductImageSerializer

    def get_queryset(self):
        return models.ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
