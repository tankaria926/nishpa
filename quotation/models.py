from django.db import models
from django.utils import timezone
from inquiry.models import Inquiry, Product
import json
from decimal import Decimal


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='quotations', null=True, blank=True)
    quotation_number = models.CharField(max_length=50, unique=True)
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50, blank=True)
    customer_company = models.CharField(max_length=200, blank=True)
    
    subject = models.CharField(max_length=255, default='Quotation for Products')
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.IntegerField(default=1)
    
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_type = models.CharField(max_length=10, choices=[('fixed', 'Fixed'), ('percent', 'Percentage')], default='fixed')
    
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True, help_text='Additional notes for the quotation')
    terms = models.TextField(blank=True, help_text='Terms and conditions')
    
    valid_until = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=200, default='Admin')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.quotation_number} - {self.customer_name}'

    @property
    def quote_number(self):
        return self.quotation_number

    def get_total(self):
        return self.grand_total
    
    @property
    def subtotal(self):
        total = Decimal('0')
        for item in self.items.all():
            try:
                total += Decimal(str(item.total))
            except Exception:
                # fallback to 0 if conversion fails
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


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    
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


class QuotationVersion(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    
    # Store snapshot of quotation data
    data = models.JSONField()  # Snapshot of quotation and items
    
    change_summary = models.CharField(max_length=500, blank=True)
    changed_by = models.CharField(max_length=200)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ('quotation', 'version_number')
    
    def __str__(self):
        return f'{self.quotation.quotation_number} - v{self.version_number}'


class QuotationTemplate(models.Model):
    name = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)
    
    company_name = models.CharField(max_length=200, blank=True)
    company_logo_url = models.URLField(blank=True)
    company_email = models.EmailField(blank=True)
    company_phone = models.CharField(max_length=50, blank=True)
    company_address = models.TextField(blank=True)
    
    terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
