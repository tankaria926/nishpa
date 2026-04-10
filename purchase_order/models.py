from django.db import models
from django.utils import timezone
from proforma_invoice.models import ProformaInvoice
from decimal import Decimal


class Vendor(models.Model):
    """Vendor model for purchase orders"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=50, blank=True)
    
    tax_id = models.CharField(max_length=100, blank=True, help_text='GST/Tax ID')
    bank_account = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    
    contact_person = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Vendor'),
        ('confirmed', 'Confirmed'),
        ('partial', 'Partially Received'),
        ('received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    proforma_invoice = models.OneToOneField(ProformaInvoice, on_delete=models.CASCADE, related_name='purchase_order', null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    
    po_number = models.CharField(max_length=50, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    subject = models.CharField(max_length=255, default='Purchase Order')
    description = models.TextField(blank=True)
    
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_type = models.CharField(max_length=10, choices=[('fixed', 'Fixed'), ('percent', 'Percentage')], default='fixed')
    
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    
    required_by = models.DateField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=200, default='Admin')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.po_number} - {self.vendor.name}'
    
    @property
    def subtotal(self):
        total = Decimal('0')
        for item in self.items.all():
            try:
                total += Decimal(str(item.total))
            except Exception:
                total += Decimal('0')
        return total
    
    @property
    def discount_amount(self):
        if self.discount_type == 'percent':
            return (self.subtotal * Decimal(str(self.discount))) / Decimal('100')
        return Decimal(str(self.discount))
    
    @property
    def subtotal_after_discount(self):
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self):
        return (self.subtotal_after_discount * Decimal(str(self.tax_rate))) / Decimal('100')
    
    @property
    def grand_total(self):
        return self.subtotal_after_discount + self.tax_amount + Decimal(str(self.shipping_cost))
    
    def get_subtotal(self):
        return self.subtotal
    
    def get_tax_amount(self):
        return self.tax_amount
    
    def get_total(self):
        return self.grand_total


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    
    description = models.CharField(max_length=500)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    received_quantity = models.IntegerField(default=0, help_text='Quantity received from GRN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f'{self.description} x{self.quantity}'
    
    @property
    def total(self):
        return Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
    
    @property
    def pending_quantity(self):
        return self.quantity - self.received_quantity
    
    def get_total(self):
        return self.total
