from django.urls import path
from . import views

app_name = 'proforma_invoice'

urlpatterns = [
    path('', views.proforma_invoice_list, name='proforma_invoice_list'),
    path('create/<int:quotation_id>/', views.proforma_invoice_create, name='proforma_invoice_create'),
    path('invoice/<int:pk>/', views.proforma_invoice_detail, name='proforma_invoice_detail'),
    path('invoice/<int:pk>/edit/', views.proforma_invoice_edit, name='proforma_invoice_edit'),
    path('invoice/<int:pk>/pdf/', views.proforma_invoice_pdf, name='proforma_invoice_pdf'),
    path('invoice/<int:pk>/issue/', views.proforma_invoice_issue, name='proforma_invoice_issue'),
    path('invoice/<int:pk>/delete/', views.proforma_invoice_delete, name='proforma_invoice_delete'),
    path('invoice/<int:pk>/status/', views.update_proforma_status, name='update_proforma_status'),
]
