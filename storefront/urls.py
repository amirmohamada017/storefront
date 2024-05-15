from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Storefront Administration"
admin.site.site_title = "Storefront Admin Portal"
admin.site.index_title = "Welcome to Storefront"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('playground/', include('playground.urls')),
    path('store/', include('store.urls')),
]
