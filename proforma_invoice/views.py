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

from .models import ProformaInvoice, ProformaInvoiceItem
from quotation.models import Quotation


def generate_invoice_number():
    """Generate unique proforma invoice number"""
    latest = ProformaInvoice.objects.order_by('id').last()
    year = datetime.now().year
    month = datetime.now().month
    seq = (latest.id if latest else 0) + 1
    return f'PI-{year}{month:02d}-{seq:05d}'


def proforma_invoice_list(request):
    """List all proforma invoices with filters"""
    invoices = ProformaInvoice.objects.all()
    
    # Filters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    if search_query:
        invoices = invoices.filter(
            invoice_number__icontains=search_query
        ) | invoices.filter(
            customer_name__icontains=search_query
        ) | invoices.filter(
            customer_email__icontains=search_query
        )
    
    sort_by = request.GET.get('sort_by', '-created_at')
    invoices = invoices.order_by(sort_by)
    
    context = {
        'invoices': invoices,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'status_choices': ProformaInvoice.STATUS_CHOICES,
    }
    
    return render(request, 'proforma_invoice/proforma_invoice_list.html', context)


def proforma_invoice_create(request, quotation_id):
    """Create proforma invoice from quotation"""
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    
    # Check if proforma invoice already exists
    if hasattr(quotation, 'proforma_invoice'):
        messages.info(request, 'Proforma invoice already exists for this quotation.')
        return redirect('proforma_invoice:proforma_invoice_detail', pk=quotation.proforma_invoice.pk)
    
    if request.method == 'POST':
        proforma = ProformaInvoice()
        proforma.invoice_number = generate_invoice_number()
        
        # Copy data from quotation
        proforma.quotation = quotation
        proforma.customer_name = quotation.customer_name
        proforma.customer_email = quotation.customer_email
        proforma.customer_phone = quotation.customer_phone
        proforma.customer_company = quotation.customer_company
        proforma.subject = request.POST.get('subject', f'Proforma Invoice - {quotation.quotation_number}')
        proforma.description = quotation.description
        proforma.discount = quotation.discount
        proforma.discount_type = quotation.discount_type
        proforma.tax_rate = quotation.tax_rate
        proforma.notes = request.POST.get('notes', quotation.notes)
        proforma.terms = request.POST.get('terms', quotation.terms)
        proforma.valid_until = request.POST.get('valid_until', quotation.valid_until)
        proforma.created_by = request.user.username if request.user.is_authenticated else 'Admin'
        
        proforma.save()
        
        # Copy items from quotation
        for item in quotation.items.all():
            ProformaInvoiceItem.objects.create(
                proforma_invoice=proforma,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        
        messages.success(request, f'Proforma Invoice {proforma.invoice_number} created successfully!')
        return redirect('proforma_invoice:proforma_invoice_detail', pk=proforma.pk)
    
    context = {
        'quotation': quotation,
        'quotation_items': quotation.items.all(),
    }
    
    return render(request, 'proforma_invoice/proforma_invoice_create.html', context)


def proforma_invoice_detail(request, pk):
    """View proforma invoice details"""
    proforma = get_object_or_404(ProformaInvoice, pk=pk)
    
    context = {
        'proforma': proforma,
        'invoice': proforma,
        'items': proforma.items.all(),
        'proforma_items': proforma.items.all(),
        'status_choices': ProformaInvoice.STATUS_CHOICES,
    }
    
    return render(request, 'proforma_invoice/proforma_invoice_detail.html', context)


def proforma_invoice_edit(request, pk):
    """Edit proforma invoice"""
    proforma = get_object_or_404(ProformaInvoice, pk=pk)
    
    if request.method == 'POST':
        proforma.subject = request.POST.get('subject', proforma.subject)
        proforma.description = request.POST.get('description', proforma.description)
        proforma.customer_name = request.POST.get('customer_name', proforma.customer_name)
        proforma.customer_email = request.POST.get('customer_email', proforma.customer_email)
        proforma.customer_phone = request.POST.get('customer_phone', proforma.customer_phone)
        proforma.customer_company = request.POST.get('customer_company', proforma.customer_company)
        proforma.discount = request.POST.get('discount', proforma.discount)
        proforma.discount_type = request.POST.get('discount_type', proforma.discount_type)
        proforma.tax_rate = request.POST.get('tax_rate', proforma.tax_rate)
        proforma.notes = request.POST.get('notes', proforma.notes)
        proforma.terms = request.POST.get('terms', proforma.terms)
        proforma.valid_until = request.POST.get('valid_until', proforma.valid_until)
        
        proforma.save()
        
        # Update items
        proforma.items.all().delete()
        items_json = request.POST.get('items_json', '{}')
        try:
            items_data = json.loads(items_json)
            for item in items_data.get('items', []):
                ProformaInvoiceItem.objects.create(
                    proforma_invoice=proforma,
                    description=item.get('description'),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('unit_price', 0),
                )
        except json.JSONDecodeError:
            pass
        
        messages.success(request, 'Proforma invoice updated successfully!')
        return redirect('proforma_invoice:proforma_invoice_detail', pk=proforma.pk)
    
    context = {
        'proforma': proforma,
        'items': proforma.items.all(),
        'status_choices': ProformaInvoice.STATUS_CHOICES,
        'editing': True,
    }
    
    return render(request, 'proforma_invoice/proforma_invoice_form.html', context)


@require_POST
def proforma_invoice_issue(request, pk):
    """Issue proforma invoice"""
    proforma = get_object_or_404(ProformaInvoice, pk=pk)
    
    if proforma.status != 'draft':
        messages.warning(request, 'Only draft proforma invoices can be issued.')
        return redirect('proforma_invoice:proforma_invoice_detail', pk=proforma.pk)
    
    proforma.status = 'issued'
    proforma.issued_at = timezone.now()
    proforma.save()
    
    messages.success(request, f'Proforma Invoice {proforma.invoice_number} issued successfully!')
    return redirect('proforma_invoice:proforma_invoice_detail', pk=proforma.pk)


@require_POST
def proforma_invoice_delete(request, pk):
    """Delete proforma invoice"""
    proforma = get_object_or_404(ProformaInvoice, pk=pk)
    invoice_number = proforma.invoice_number
    
    if proforma.status == 'converted':
        messages.error(request, 'Cannot delete a proforma invoice that has been converted to an invoice.')
        return redirect('proforma_invoice:proforma_invoice_detail', pk=proforma.pk)
    
    proforma.delete()
    messages.success(request, f'Proforma Invoice {invoice_number} deleted successfully!')
    return redirect('proforma_invoice:proforma_invoice_list')


@require_POST
def update_proforma_status(request, pk):
    """Update proforma invoice status"""
    proforma = get_object_or_404(ProformaInvoice, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(ProformaInvoice.STATUS_CHOICES):
        proforma.status = new_status
        proforma.save()
        messages.success(request, f'Proforma invoice status updated to {proforma.get_status_display()}')
    else:
        messages.error(request, 'Invalid status.')
    
    return redirect('proforma_invoice:proforma_invoice_detail', pk=proforma.pk)


def proforma_invoice_pdf(request, pk):
    """Generate PDF of proforma invoice"""
    proforma = get_object_or_404(ProformaInvoice, pk=pk)
    
    # Create BytesIO object
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
    
    # Styles
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
    
    # Title
    elements.append(Paragraph('PROFORMA INVOICE', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice info
    info_data = [
        ['Invoice #:', f"{proforma.invoice_number}"],
        ['Date:', proforma.created_at.strftime('%B %d, %Y')],
        ['Status:', proforma.get_status_display()],
        ['Valid Until:', proforma.valid_until.strftime('%B %d, %Y') if proforma.valid_until else 'N/A'],
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
    
    # Customer info
    elements.append(Paragraph('BILL TO:', heading_style))
    customer_info = f"""
    <b>{proforma.customer_name}</b><br/>
    {proforma.customer_company}<br/>
    Email: {proforma.customer_email}<br/>
    Phone: {proforma.customer_phone if proforma.customer_phone else 'N/A'}
    """
    elements.append(Paragraph(customer_info, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Items table
    elements.append(Paragraph('ITEMS', heading_style))
    items_data = [['Description', 'Qty', 'Unit Price', 'Total']]
    for item in proforma.items.all():
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
    
    # Totals
    totals_data = [
        ['Subtotal:', f"${proforma.subtotal:.2f}"],
        ['Discount:', f"-${proforma.discount_amount:.2f}"],
        ['Tax ({:.2f}%):'.format(proforma.tax_rate), f"${proforma.tax_amount:.2f}"],
        ['TOTAL:', f"${proforma.grand_total:.2f}"],
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
    
    # Notes and terms
    if proforma.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('NOTES', heading_style))
        elements.append(Paragraph(proforma.notes, normal_style))
    
    if proforma.terms:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph('TERMS & CONDITIONS', heading_style))
        elements.append(Paragraph(proforma.terms, normal_style))
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ProformaInvoice_{proforma.invoice_number}.pdf"'
    return response
