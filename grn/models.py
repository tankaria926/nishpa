from django.db import models
from django.utils import timezone
from purchase_order.models import PurchaseOrder, PurchaseOrderItem
from decimal import Decimal


class GRN(models.Model):
    """Goods Received Note model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('inspected', 'Inspected'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='grns')
    
    grn_number = models.CharField(max_length=50, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    received_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True, help_text='Receiving notes and remarks')
    quality_check_notes = models.TextField(blank=True, help_text='Quality inspection remarks')
    
    received_by = models.CharField(max_length=200)
    inspected_by = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.grn_number} - PO{self.purchase_order.po_number}'
    
    @property
    def total_items_received(self):
        return sum(item.quantity_received for item in self.items.all())
    
    def get_total_items_received(self):
        return self.total_items_received


class GRNItem(models.Model):
    """Items received in a GRN"""
    CONDITION_CHOICES = [
        ('good', 'Good'),
        ('damaged', 'Damaged'),
        ('partial', 'Partially Damaged'),
        ('shortlisted', 'Short Listed'),
    ]
    
    grn = models.ForeignKey(GRN, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='grn_items')
    
    quantity_received = models.IntegerField(default=0)
    quantity_accepted = models.IntegerField(default=0)
    quantity_rejected = models.IntegerField(default=0)
    
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f'GRN Item: {self.po_item.description} x{self.quantity_received}'
    
    @property
    def quantity_pending_inspection(self):
        return self.quantity_received - (self.quantity_accepted + self.quantity_rejected)
