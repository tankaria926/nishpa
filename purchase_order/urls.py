from django.urls import path
from . import views

app_name = 'purchase_order'

urlpatterns = [
    # Vendor URLs
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/create/', views.vendor_create, name='vendor_create'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    
    # Purchase Order URLs
    path('', views.purchase_order_list, name='purchase_order_list'),
    path('create/', views.purchase_order_create, name='purchase_order_create'),
    path('create/<int:proforma_id>/', views.purchase_order_create, name='purchase_order_create_from_proforma'),
    path('po/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('po/<int:pk>/edit/', views.purchase_order_edit, name='purchase_order_edit'),
    path('po/<int:pk>/send/', views.purchase_order_send, name='purchase_order_send'),
    path('po/<int:pk>/confirm/', views.purchase_order_confirm, name='purchase_order_confirm'),
    path('po/<int:pk>/cancel/', views.purchase_order_cancel, name='purchase_order_cancel'),
    path('po/<int:pk>/delete/', views.purchase_order_delete, name='purchase_order_delete'),
    path('po/<int:pk>/pdf/', views.purchase_order_pdf, name='purchase_order_pdf'),
]
