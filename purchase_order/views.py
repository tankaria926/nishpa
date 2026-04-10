from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import PurchaseOrder, PurchaseOrderItem, Vendor
from proforma_invoice.models import ProformaInvoice


def generate_po_number():
    """Generate unique purchase order number"""
    latest = PurchaseOrder.objects.order_by('id').last()
    year = datetime.now().year
    month = datetime.now().month
    seq = (latest.id if latest else 0) + 1
    return f'PO-{year}{month:02d}-{seq:05d}'


def vendor_list(request):
    """List all vendors"""
    vendors = Vendor.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        vendors = vendors.filter(name__icontains=search_query) | vendors.filter(email__icontains=search_query)
    
    context = {
        'vendors': vendors,
        'search_query': search_query,
    }
    
    return render(request, 'purchase_order/vendor_list.html', context)


def vendor_create(request):
    """Create new vendor"""
    if request.method == 'POST':
        vendor = Vendor()
        vendor.name = request.POST.get('name')
        vendor.email = request.POST.get('email')
        vendor.phone = request.POST.get('phone', '')
        vendor.address = request.POST.get('address', '')
        vendor.city = request.POST.get('city', '')
        vendor.state = request.POST.get('state', '')
        vendor.country = request.POST.get('country', '')
        vendor.postal_code = request.POST.get('postal_code', '')
        vendor.tax_id = request.POST.get('tax_id', '')
        vendor.bank_account = request.POST.get('bank_account', '')
        vendor.bank_name = request.POST.get('bank_name', '')
        vendor.contact_person = request.POST.get('contact_person', '')
        
        vendor.save()
        
        messages.success(request, f'Vendor {vendor.name} created successfully!')
        return redirect('purchase_order:vendor_list')
    
    return render(request, 'purchase_order/vendor_form.html')


def vendor_detail(request, pk):
    """View vendor details"""
    vendor = get_object_or_404(Vendor, pk=pk)
    purchase_orders = vendor.purchase_orders.all()
    
    context = {
        'vendor': vendor,
        'purchase_orders': purchase_orders,
    }
    
    return render(request, 'purchase_order/vendor_detail.html', context)


def vendor_edit(request, pk):
    """Edit vendor"""
    vendor = get_object_or_404(Vendor, pk=pk)
    
    if request.method == 'POST':
        vendor.name = request.POST.get('name', vendor.name)
        vendor.email = request.POST.get('email', vendor.email)
        vendor.phone = request.POST.get('phone', vendor.phone)
        vendor.address = request.POST.get('address', vendor.address)
        vendor.city = request.POST.get('city', vendor.city)
        vendor.state = request.POST.get('state', vendor.state)
        vendor.country = request.POST.get('country', vendor.country)
        vendor.postal_code = request.POST.get('postal_code', vendor.postal_code)
        vendor.tax_id = request.POST.get('tax_id', vendor.tax_id)
        vendor.bank_account = request.POST.get('bank_account', vendor.bank_account)
        vendor.bank_name = request.POST.get('bank_name', vendor.bank_name)
        vendor.contact_person = request.POST.get('contact_person', vendor.contact_person)
        vendor.is_active = request.POST.get('is_active') == 'on'
        
        vendor.save()
        
        messages.success(request, 'Vendor updated successfully!')
        return redirect('purchase_order:vendor_detail', pk=vendor.pk)
    
    context = {
        'vendor': vendor,
        'editing': True,
    }
    
    return render(request, 'purchase_order/vendor_form.html', context)


def purchase_order_list(request):
    """List all purchase orders"""
    orders = PurchaseOrder.objects.all()
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(po_number__icontains=search_query) | orders.filter(vendor__name__icontains=search_query)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
    }
    
    return render(request, 'purchase_order/purchase_order_list.html', context)


def purchase_order_create(request, proforma_id=None):
    """Create new purchase order from proforma invoice"""
    proforma = None
    if proforma_id:
        proforma = get_object_or_404(ProformaInvoice, pk=proforma_id)
    
    if request.method == 'POST':
        po = PurchaseOrder()
        po.po_number = generate_po_number()
        po.vendor_id = request.POST.get('vendor_id')
        po.proforma_invoice = proforma
        po.subject = request.POST.get('subject', 'Purchase Order')
        po.description = request.POST.get('description', '')
        po.discount = request.POST.get('discount', 0)
        po.discount_type = request.POST.get('discount_type', 'fixed')
        po.tax_rate = request.POST.get('tax_rate', 0)
        po.shipping_cost = request.POST.get('shipping_cost', 0)
        po.notes = request.POST.get('notes', '')
        po.terms = request.POST.get('terms', '')
        po.required_by = request.POST.get('required_by', '')
        po.created_by = request.user.username if request.user.is_authenticated else 'Admin'
        
        po.save()
        
        # Add items from POST data or from proforma invoice
        if proforma:
            for item in proforma.items.all():
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
        else:
            items_json = request.POST.get('items_json', '{}')
            try:
                items_data = json.loads(items_json)
                for item in items_data.get('items', []):
                    PurchaseOrderItem.objects.create(
                        purchase_order=po,
                        description=item.get('description'),
                        quantity=item.get('quantity', 1),
                        unit_price=item.get('unit_price', 0),
                    )
            except json.JSONDecodeError:
                pass
        
        messages.success(request, f'Purchase Order {po.po_number} created successfully!')
        return redirect('purchase_order:purchase_order_detail', pk=po.pk)
    
    vendors = Vendor.objects.filter(is_active=True)
    context = {
        'proforma': proforma,
        'proforma_items': proforma.items.all() if proforma else [],
        'vendors': vendors,
    }
    
    return render(request, 'purchase_order/purchase_order_create.html', context)


def purchase_order_detail(request, pk):
    """View purchase order details"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    context = {
        'purchase_order': po,
        'po': po,
        'items': po.items.all(),
        'po_items': po.items.all(),
        'status_choices': PurchaseOrder.STATUS_CHOICES,
    }
    
    return render(request, 'purchase_order/purchase_order_detail.html', context)


def purchase_order_edit(request, pk):
    """Edit purchase order"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        po.subject = request.POST.get('subject', po.subject)
        po.description = request.POST.get('description', po.description)
        po.discount = request.POST.get('discount', po.discount)
        po.discount_type = request.POST.get('discount_type', po.discount_type)
        po.tax_rate = request.POST.get('tax_rate', po.tax_rate)
        po.shipping_cost = request.POST.get('shipping_cost', po.shipping_cost)
        po.notes = request.POST.get('notes', po.notes)
        po.terms = request.POST.get('terms', po.terms)
        po.required_by = request.POST.get('required_by', po.required_by)
        
        po.save()
        
        # Update items
        po.items.all().delete()
        items_json = request.POST.get('items_json', '{}')
        try:
            items_data = json.loads(items_json)
            for item in items_data.get('items', []):
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    description=item.get('description'),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('unit_price', 0),
                )
        except json.JSONDecodeError:
            pass
        
        messages.success(request, 'Purchase order updated successfully!')
        return redirect('purchase_order:purchase_order_detail', pk=po.pk)
    
    vendors = Vendor.objects.filter(is_active=True)
    context = {
        'purchase_order': po,
        'po': po,
        'items': po.items.all(),
        'vendors': vendors,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
        'editing': True,
    }
    
    return render(request, 'purchase_order/purchase_order_form.html', context)


@require_POST
def purchase_order_send(request, pk):
    """Send purchase order to vendor"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if po.status != 'draft':
        messages.warning(request, 'Only draft purchase orders can be sent.')
        return redirect('purchase_order:purchase_order_detail', pk=po.pk)
    
    po.status = 'sent'
    po.sent_at = timezone.now()
    po.save()
    
    messages.success(request, f'Purchase Order {po.po_number} sent to {po.vendor.name}!')
    return redirect('purchase_order:purchase_order_detail', pk=po.pk)


@require_POST
def purchase_order_confirm(request, pk):
    """Confirm purchase order"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if po.status not in ['sent', 'draft']:
        messages.warning(request, 'Only draft or sent purchase orders can be confirmed.')
        return redirect('purchase_order:purchase_order_detail', pk=po.pk)
    
    po.status = 'confirmed'
    po.confirmed_at = timezone.now()
    po.save()
    
    messages.success(request, f'Purchase Order {po.po_number} confirmed!')
    return redirect('purchase_order:purchase_order_detail', pk=po.pk)


@require_POST
def purchase_order_cancel(request, pk):
    """Cancel purchase order"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if po.status in ['received', 'cancelled']:
        messages.error(request, 'Cannot cancel this purchase order.')
        return redirect('purchase_order:purchase_order_detail', pk=po.pk)
    
    po.status = 'cancelled'
    po.save()
    
    messages.success(request, f'Purchase Order {po.po_number} cancelled!')
    return redirect('purchase_order:purchase_order_detail', pk=po.pk)


@require_POST
def purchase_order_delete(request, pk):
    """Delete purchase order"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    po_number = po.po_number
    
    if po.status != 'draft':
        messages.error(request, 'Only draft purchase orders can be deleted.')
        return redirect('purchase_order:purchase_order_detail', pk=po.pk)
    
    po.delete()
    messages.success(request, f'Purchase Order {po_number} deleted successfully!')
    return redirect('purchase_order:purchase_order_list')


def purchase_order_pdf(request, pk):
    """Generate PDF of purchase order"""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0f62fe'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f62fe'),
        spaceAfter=12,
        marginTop=12,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    
    elements.append(Paragraph('PURCHASE ORDER', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    info_data = [
        ['PO #:', f"{po.po_number}"],
        ['Date:', po.created_at.strftime('%B %d, %Y')],
        ['Status:', po.get_status_display()],
        ['Required By:', po.required_by.strftime('%B %d, %Y') if po.required_by else 'N/A'],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(Paragraph('VENDOR:', heading_style))
    vendor_info = f"""
    <b>{po.vendor.name}</b><br/>
    Email: {po.vendor.email}<br/>
    Phone: {po.vendor.phone if po.vendor.phone else 'N/A'}<br/>
    Address: {po.vendor.address if po.vendor.address else 'N/A'}
    """
    elements.append(Paragraph(vendor_info, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph('ITEMS', heading_style))
    items_data = [['Description', 'Qty', 'Unit Price', 'Total']]
    for item in po.items.all():
        items_data.append([
            item.description,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total:.2f}",
        ])
    
    items_table = Table(items_data, colWidths=[2.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f62fe')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    totals_data = [
        ['Subtotal:', f"${po.subtotal:.2f}"],
        ['Discount:', f"-${po.discount_amount:.2f}"],
        ['Tax ({:.2f}%):'.format(po.tax_rate), f"${po.tax_amount:.2f}"],
        ['Shipping:', f"${po.shipping_cost:.2f}"],
        ['TOTAL:', f"${po.grand_total:.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[4.2*inch, 1.3*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (0, -1), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#0f62fe')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
    ]))
    elements.append(totals_table)
    
    if po.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('NOTES', heading_style))
        elements.append(Paragraph(po.notes, normal_style))
    
    if po.terms:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph('TERMS & CONDITIONS', heading_style))
        elements.append(Paragraph(po.terms, normal_style))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PurchaseOrder_{po.po_number}.pdf"'
    return response
