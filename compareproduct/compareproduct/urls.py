# yourproject/urls.py

from django.contrib import admin
from django.urls import path
from products import views  # Corrected: Changed 'products' to 'scraper'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.scraping, name='home'),
    path('product/<str:encoded_url>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
]