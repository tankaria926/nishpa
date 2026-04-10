from django.urls import path
from . import views

app_name = 'inquiry_dashboard'

urlpatterns = [
    path('', views.inquiry_list, name='inquiry_list'),
    path('inquiry/<int:inquiry_id>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiry/<int:inquiry_id>/status/', views.update_inquiry_status, name='update_status'),
]
