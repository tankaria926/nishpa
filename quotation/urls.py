from django.urls import path
from . import views

app_name = 'quotation'

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    path('create/', views.quotation_create, name='quotation_create'),
    path('create/<int:inquiry_id>/', views.quotation_create, name='quotation_create_from_inquiry'),
    path('quotation/<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('quotation/<int:pk>/edit/', views.quotation_edit, name='quotation_edit'),
    path('quotation/<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),
    path('quotation/<int:pk>/send/', views.send_quotation, name='send_quotation'),
    path('quotation/<int:pk>/delete/', views.quotation_delete, name='quotation_delete'),
    path('quotation/<int:pk>/finalize/', views.finalize_quotation, name='finalize_quotation'),
    path('quotation/<int:pk>/versions/', views.quotation_versions, name='quotation_versions'),
    path('quotation/<int:pk>/version/<int:version_id>/', views.quotation_version_detail, name='quotation_version_detail'),
    path('quotation/<int:pk>/status/', views.update_status, name='update_status'),
]
