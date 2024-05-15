from django_filters.rest_framework import filterset
from .models import Product


class ProductFilter(filterset.FilterSet):
    title = filterset.CharFilter(lookup_expr='icontains')
    min_price = filterset.NumberFilter(field_name='unit_price', lookup_expr='gte')
    max_price = filterset.NumberFilter(field_name='unit_price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt'],
        }
