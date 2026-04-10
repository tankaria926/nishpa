from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'contact_person')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('po_number', 'vendor__name')
    readonly_fields = ('po_number', 'created_at', 'updated_at')


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'description', 'quantity', 'unit_price', 'get_total')
    search_fields = ('description', 'purchase_order__po_number')
    readonly_fields = ('created_at', 'updated_at')
