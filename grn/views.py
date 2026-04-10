from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
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

from .models import GRN, GRNItem
from purchase_order.models import PurchaseOrder, PurchaseOrderItem


def generate_grn_number():
    """Generate unique GRN number"""
    latest = GRN.objects.order_by('id').last()
    year = datetime.now().year
    month = datetime.now().month
    seq = (latest.id if latest else 0) + 1
    return f'GRN-{year}{month:02d}-{seq:05d}'


def grn_list(request):
    """List all GRNs"""
    grns = GRN.objects.all()
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        grns = grns.filter(status=status_filter)
    
    if search_query:
        grns = grns.filter(grn_number__icontains=search_query) | grns.filter(
            purchase_order__po_number__icontains=search_query
        )
    
    context = {
        'grns': grns,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': GRN.STATUS_CHOICES,
    }
    
    return render(request, 'grn/grn_list.html', context)


def grn_create(request, po_id):
    """Create new GRN for a purchase order"""
    po = get_object_or_404(PurchaseOrder, pk=po_id)
    
    if request.method == 'POST':
        grn = GRN()
        grn.grn_number = generate_grn_number()
        grn.purchase_order = po
        grn.received_date = request.POST.get('received_date')
        grn.notes = request.POST.get('notes', '')
        grn.received_by = request.POST.get('received_by', request.user.username if request.user.is_authenticated else 'Admin')
        
        grn.save()
        
        # Add items from POST data
        items_json = request.POST.get('items_json', '{}')
        try:
            items_data = json.loads(items_json)
            for item_data in items_data.get('items', []):
                po_item = get_object_or_404(PurchaseOrderItem, pk=item_data.get('po_item_id'))
                GRNItem.objects.create(
                    grn=grn,
                    po_item=po_item,
                    quantity_received=item_data.get('quantity_received', 0),
                    quantity_accepted=item_data.get('quantity_received', 0),
                    condition=item_data.get('condition', 'good'),
                    batch_number=item_data.get('batch_number', ''),
                    expiry_date=item_data.get('expiry_date') if item_data.get('expiry_date') else None,
                    remarks=item_data.get('remarks', ''),
                )
        except json.JSONDecodeError:
            pass
        
        # Update purchase order status
        if po.status == 'confirmed':
            po.status = 'partial'
        po.save()
        
        messages.success(request, f'GRN {grn.grn_number} created successfully!')
        return redirect('grn:grn_detail', pk=grn.pk)
    
    po_items = po.items.all()
    context = {
        'purchase_order': po,
        'po_items': po_items,
    }
    
    return render(request, 'grn/grn_create.html', context)


def grn_detail(request, pk):
    """View GRN details"""
    grn = get_object_or_404(GRN, pk=pk)
    
    context = {
        'grn': grn,
        'po': grn.purchase_order,
        'items': grn.items.all(),
        'grn_items': grn.items.all(),
        'status_choices': GRN.STATUS_CHOICES,
    }
    
    return render(request, 'grn/grn_detail.html', context)


def grn_edit(request, pk):
    """Edit GRN"""
    grn = get_object_or_404(GRN, pk=pk)
    
    if request.method == 'POST':
        grn.received_date = request.POST.get('received_date', grn.received_date)
        grn.notes = request.POST.get('notes', grn.notes)
        grn.save()
        
        # Update items
        items_json = request.POST.get('items_json', '{}')
        try:
            items_data = json.loads(items_json)
            for item_data in items_data.get('items', []):
                grn_item_id = item_data.get('item_id')
                
                try:
                    grn_item = GRNItem.objects.get(pk=grn_item_id)
                    grn_item.quantity_received = item_data.get('quantity_received', 0)
                    grn_item.quantity_accepted = item_data.get('quantity_accepted', 0)
                    grn_item.quantity_rejected = item_data.get('quantity_rejected', 0)
                    grn_item.condition = item_data.get('condition', 'good')
                    grn_item.batch_number = item_data.get('batch_number', '')
                    grn_item.expiry_date = item_data.get('expiry_date') if item_data.get('expiry_date') else None
                    grn_item.remarks = item_data.get('remarks', '')
                    grn_item.save()
                    
                    # Update PO item received quantity
                    po_item = grn_item.po_item
                    po_item.received_quantity = item_data.get('quantity_accepted', 0)
                    po_item.save()
                except GRNItem.DoesNotExist:
                    pass
        except json.JSONDecodeError:
            pass
        
        messages.success(request, 'GRN updated successfully!')
        return redirect('grn:grn_detail', pk=grn.pk)
    
    context = {
        'grn': grn,
        'po': grn.purchase_order,
        'items': grn.items.all(),
        'status_choices': GRN.STATUS_CHOICES,
        'editing': True,
    }
    
    return render(request, 'grn/grn_form.html', context)


@require_POST
def grn_inspect(request, pk):
    """Mark GRN as inspected"""
    grn = get_object_or_404(GRN, pk=pk)
    
    if grn.status not in ['draft', 'received']:
        messages.warning(request, 'Only draft or received GRNs can be inspected.')
        return redirect('grn:grn_detail', pk=grn.pk)
    
    grn.status = 'inspected'
    grn.quality_check_notes = request.POST.get('quality_check_notes', '')
    grn.inspected_by = request.user.username if request.user.is_authenticated else 'Admin'
    grn.save()
    
    messages.success(request, f'GRN {grn.grn_number} marked as inspected!')
    return redirect('grn:grn_detail', pk=grn.pk)


@require_POST
def grn_accept(request, pk):
    """Accept GRN after inspection"""
    grn = get_object_or_404(GRN, pk=pk)
    
    if grn.status != 'inspected':
        messages.warning(request, 'Only inspected GRNs can be accepted.')
        return redirect('grn:grn_detail', pk=grn.pk)
    
    grn.status = 'accepted'
    grn.save()
    
    # Update PO status if all items received
    po = grn.purchase_order
    total_po_qty = sum(item.quantity for item in po.items.all())
    total_received_qty = sum(item.received_quantity for item in po.items.all())
    
    if total_received_qty >= total_po_qty:
        po.status = 'received'
        po.save()
    
    messages.success(request, f'GRN {grn.grn_number} accepted!')
    return redirect('grn:grn_detail', pk=grn.pk)


@require_POST
def grn_reject(request, pk):
    """Reject GRN"""
    grn = get_object_or_404(GRN, pk=pk)
    
    grn.status = 'rejected'
    grn.save()
    
    messages.success(request, f'GRN {grn.grn_number} rejected!')
    return redirect('grn:grn_detail', pk=grn.pk)


@require_POST
def grn_delete(request, pk):
    """Delete GRN"""
    grn = get_object_or_404(GRN, pk=pk)
    grn_number = grn.grn_number
    
    if grn.status != 'draft':
        messages.error(request, 'Only draft GRNs can be deleted.')
        return redirect('grn:grn_detail', pk=grn.pk)
    
    grn.delete()
    messages.success(request, f'GRN {grn_number} deleted successfully!')
    return redirect('grn:grn_list')


def grn_pdf(request, pk):
    """Generate PDF of GRN"""
    grn = get_object_or_404(GRN, pk=pk)
    
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
    
    elements.append(Paragraph('GOODS RECEIVED NOTE', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    info_data = [
        ['GRN #:', f"{grn.grn_number}"],
        ['Date:', grn.created_at.strftime('%B %d, %Y')],
        ['Status:', grn.get_status_display()],
        ['PO #:', grn.purchase_order.po_number],
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
    <b>{grn.purchase_order.vendor.name}</b><br/>
    Email: {grn.purchase_order.vendor.email}
    """
    elements.append(Paragraph(vendor_info, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph('ITEMS RECEIVED', heading_style))
    items_data = [['Description', 'PO Qty', 'Received', 'Accepted', 'Rejected', 'Condition']]
    for item in grn.items.all():
        items_data.append([
            item.po_item.description,
            str(item.po_item.quantity),
            str(item.quantity_received),
            str(item.quantity_accepted),
            str(item.quantity_rejected),
            item.get_condition_display(),
        ])
    
    items_table = Table(items_data, colWidths=[2*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f62fe')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
    ]))
    elements.append(items_table)
    
    if grn.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('RECEIVING NOTES', heading_style))
        elements.append(Paragraph(grn.notes, normal_style))
    
    if grn.quality_check_notes:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph('QUALITY CHECK NOTES', heading_style))
        elements.append(Paragraph(grn.quality_check_notes, normal_style))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="GRN_{grn.grn_number}.pdf"'
    return response
