from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inquiry.urls')),
    path('inquiries/', include('inquiry_dashboard.urls')),
    path('quotations/', include('quotation.urls')),
    path('proforma-invoices/', include('proforma_invoice.urls')),
    path('purchase-orders/', include('purchase_order.urls')),
    path('grns/', include('grn.urls')),
    path('inventory/', include('inventory.urls')),
]
