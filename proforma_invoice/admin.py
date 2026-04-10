from django.contrib import admin
from .models import ProformaInvoice, ProformaInvoiceItem


@admin.register(ProformaInvoice)
class ProformaInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'quotation', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'quotation__quotation_number')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')


@admin.register(ProformaInvoiceItem)
class ProformaInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('proforma_invoice', 'description', 'quantity', 'unit_price', 'get_total')
    search_fields = ('description', 'proforma_invoice__invoice_number')
    readonly_fields = ('created_at', 'updated_at')
