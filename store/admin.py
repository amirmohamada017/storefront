from django.contrib import admin
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit_price', 'inventory_status', 'collection')
    list_filter = ('collection', 'last_update', InventoryFilter)
    list_editable = ('unit_price',)
    search_fields = ('title',)
    actions = ('clear_inventory',)
    ordering = ('unit_price',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',)
    }

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request, f'{update_count} products were successfully updated.'
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'products_count')
    search_fields = ('title',)

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist') +
               '?collection_id=' + str(collection.id)
               )

        return format_html(
            '<a href="{}">{}</a>',
            url, collection.products_count
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'membership')
    list_editable = ('membership',)
    search_fields = ('first_name', 'last_name')
    list_select_related = ('user',)
    ordering = ('user__first_name', 'user__last_name')
    list_per_page = 10


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ('product',)
    extra = 0
    model = models.OrderItem


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ('customer',)
    inlines = (OrderItemInline,)
    list_display = ('id', 'placed_at', 'customer',)
    list_per_page = 10
