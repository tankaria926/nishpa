from django.urls import path
from . import views

app_name = 'grn'

urlpatterns = [
    path('', views.grn_list, name='grn_list'),
    path('create/<int:po_id>/', views.grn_create, name='grn_create'),
    path('grn/<int:pk>/', views.grn_detail, name='grn_detail'),
    path('grn/<int:pk>/edit/', views.grn_edit, name='grn_edit'),
    path('grn/<int:pk>/inspect/', views.grn_inspect, name='grn_inspect'),
    path('grn/<int:pk>/accept/', views.grn_accept, name='grn_accept'),
    path('grn/<int:pk>/reject/', views.grn_reject, name='grn_reject'),
    path('grn/<int:pk>/delete/', views.grn_delete, name='grn_delete'),
    path('grn/<int:pk>/pdf/', views.grn_pdf, name='grn_pdf'),
]
