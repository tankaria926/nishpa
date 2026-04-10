from django.db import models
from django.utils import timezone
from quotation.models import Quotation
from decimal import Decimal


class ProformaInvoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('converted', 'Converted to Invoice'),
        ('cancelled', 'Cancelled'),
    ]
    
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, related_name='proforma_invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50, blank=True)
    customer_company = models.CharField(max_length=200, blank=True)
    
    subject = models.CharField(max_length=255, default='Proforma Invoice')
    description = models.TextField(blank=True)
    
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_type = models.CharField(max_length=10, choices=[('fixed', 'Fixed'), ('percent', 'Percentage')], default='fixed')
    
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True, help_text='Additional notes for the proforma invoice')
    terms = models.TextField(blank=True, help_text='Terms and conditions')
    
    valid_until = models.DateField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=200, default='Admin')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.invoice_number} - {self.customer_name}'
    
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
        return self.subtotal_after_discount + self.tax_amount
    
    def get_subtotal(self):
        return self.subtotal
    
    def get_tax_amount(self):
        return self.tax_amount
    
    def get_total(self):
        return self.grand_total


class ProformaInvoiceItem(models.Model):
    proforma_invoice = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE, related_name='items')
    
    description = models.CharField(max_length=500)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f'{self.description} x{self.quantity}'
    
    @property
    def total(self):
        return Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
    
    def get_total(self):
        return self.total
