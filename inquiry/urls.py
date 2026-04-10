from django.urls import path
from . import views

app_name = 'inquiry'

urlpatterns = [
    path('', views.inquiry_create, name='create'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('api/products/', views.products_by_category, name='api_products'),
]
