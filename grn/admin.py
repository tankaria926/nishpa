from django.contrib import admin
from .models import GRN, GRNItem


@admin.register(GRN)
class GRNAdmin(admin.ModelAdmin):
    list_display = ('grn_number', 'purchase_order', 'status', 'received_date', 'created_at')
    list_filter = ('status', 'received_date', 'created_at')
    search_fields = ('grn_number', 'purchase_order__po_number')
    readonly_fields = ('grn_number', 'created_at', 'updated_at')


@admin.register(GRNItem)
class GRNItemAdmin(admin.ModelAdmin):
    list_display = ('grn', 'po_item', 'quantity_received', 'quantity_accepted', 'quantity_rejected', 'condition')
    list_filter = ('condition', 'created_at')
    search_fields = ('grn__grn_number', 'po_item__description')
    readonly_fields = ('created_at', 'updated_at')
