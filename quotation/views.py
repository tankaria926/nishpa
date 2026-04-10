from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.core.mail import EmailMessage
from datetime import timedelta
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import Quotation, QuotationItem, QuotationVersion, QuotationTemplate
from inquiry.models import Inquiry


def generate_quotation_number():
    """Generate unique quotation number"""
    from datetime import datetime
    latest = Quotation.objects.order_by('id').last()
    year = datetime.now().year
    month = datetime.now().month
    seq = (latest.id if latest else 0) + 1
    return f'QT-{year}{month:02d}-{seq:05d}'


def quotation_list(request):
    """List all quotations with filters"""
    quotations = Quotation.objects.all()
    
    # Filters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        quotations = quotations.filter(status=status_filter)
    
    if search_query:
        quotations = quotations.filter(
            quotation_number__icontains=search_query
        ) | quotations.filter(
            customer_name__icontains=search_query
        ) | quotations.filter(
            customer_email__icontains=search_query
        )
    
    sort_by = request.GET.get('sort_by', '-created_at')
    quotations = quotations.order_by(sort_by)
    
    context = {
        'quotations': quotations,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'status_choices': Quotation.STATUS_CHOICES,
    }
    
    return render(request, 'quotation/quotation_list.html', context)


def quotation_create(request, inquiry_id=None):
    """Create new quotation from inquiry or manually"""
    inquiry = None
    if inquiry_id:
        inquiry = get_object_or_404(Inquiry, pk=inquiry_id)
    
    if request.method == 'POST':
        quotation = Quotation()
        quotation.quotation_number = generate_quotation_number()
        quotation.customer_name = request.POST.get('customer_name')
        quotation.customer_email = request.POST.get('customer_email')
        quotation.customer_phone = request.POST.get('customer_phone', '')
        quotation.customer_company = request.POST.get('customer_company', '')
        quotation.subject = request.POST.get('subject', 'Quotation for Products')
        quotation.description = request.POST.get('description', '')
        quotation.inquiry = inquiry
        quotation.created_by = request.user.username if request.user.is_authenticated else 'Admin'
        quotation.tax_rate = request.POST.get('tax_rate', 0)
        quotation.valid_until = request.POST.get('valid_until', '')
        quotation.notes = request.POST.get('notes', '')
        quotation.terms = request.POST.get('terms', '')
        
        quotation.save()
        
        # Add items from POST data
        items_json = request.POST.get('items_json', '{}')
        try:
            items_data = json.loads(items_json)
            for item in items_data.get('items', []):
                QuotationItem.objects.create(
                    quotation=quotation,
                    description=item.get('description'),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('unit_price', 0),
                    product_id=item.get('product_id') if item.get('product_id') else None,
                )
        except json.JSONDecodeError:
            pass
        
        # Create first version
        create_quotation_version(quotation, 'Initial version', 'System')
        
        messages.success(request, f'Quotation {quotation.quotation_number} created successfully!')
        return redirect('quotation:quotation_detail', pk=quotation.pk)
    
    # Get inquiry items if available
    inquiry_items = []
    if inquiry:
        inquiry_items = inquiry.items.all()
    
    context = {
        'inquiry': inquiry,
        'inquiry_items': inquiry_items,
        'status_choices': Quotation.STATUS_CHOICES,
    }
    
    return render(request, 'quotation/quotation_form.html', context)


def quotation_detail(request, pk):
    """View quotation details"""
    quotation = get_object_or_404(Quotation, pk=pk)
    versions = quotation.versions.all()
    
    context = {
        'quotation': quotation,
        'items': quotation.items.all(),
        'quotation_items': quotation.items.all(),
        'versions': versions,
        'status_choices': Quotation.STATUS_CHOICES,
    }
    
    return render(request, 'quotation/quotation_detail.html', context)


def quotation_edit(request, pk):
    """Edit quotation"""
    quotation = get_object_or_404(Quotation, pk=pk)
    
    if request.method == 'POST':
        old_data = {
            'customer_name': quotation.customer_name,
            'customer_email': quotation.customer_email,
            'amount': quotation.grand_total,
        }
        
        quotation.customer_name = request.POST.get('customer_name')
        quotation.customer_email = request.POST.get('customer_email')
        quotation.customer_phone = request.POST.get('customer_phone', '')
        quotation.customer_company = request.POST.get('customer_company', '')
        quotation.subject = request.POST.get('subject', 'Quotation for Products')
        quotation.description = request.POST.get('description', '')
        quotation.tax_rate = request.POST.get('tax_rate', 0)
        quotation.valid_until = request.POST.get('valid_until', '')
        quotation.notes = request.POST.get('notes', '')
        quotation.terms = request.POST.get('terms', '')
        
        # Handle version increment
        old_version = quotation.version
        quotation.version += 1
        quotation.save()
        
        # Update items
        quotation.items.all().delete()
        items_json = request.POST.get('items_json', '{}')
        try:
            items_data = json.loads(items_json)
            for item in items_data.get('items', []):
                QuotationItem.objects.create(
                    quotation=quotation,
                    description=item.get('description'),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('unit_price', 0),
                    product_id=item.get('product_id') if item.get('product_id') else None,
                )
        except json.JSONDecodeError:
            pass
        
        # Create new version
        new_data = {
            'customer_name': quotation.customer_name,
            'customer_email': quotation.customer_email,
            'amount': quotation.grand_total,
        }
        changes = [k for k in old_data if old_data[k] != new_data.get(k)]
        change_summary = f"Updated: {', '.join(changes)}" if changes else "Item changes"
        
        create_quotation_version(quotation, change_summary, request.user.username if request.user.is_authenticated else 'Admin')
        
        messages.success(request, f'Quotation updated to v{quotation.version}!')
        return redirect('quotation:quotation_detail', pk=quotation.pk)
    
    context = {
        'quotation': quotation,
        'items': quotation.items.all(),
        'status_choices': Quotation.STATUS_CHOICES,
        'editing': True,
    }
    
    return render(request, 'quotation/quotation_form.html', context)


def quotation_detail_view(request, pk):
    """View quotation details for template"""
    quotation = get_object_or_404(Quotation, pk=pk)
    return render(request, 'quotation/quotation_detail.html', {
        'quotation': quotation,
        'quotation_items': quotation.items.all(),
        'status_choices': Quotation.STATUS_CHOICES,
    })


def create_quotation_version(quotation, change_summary, changed_by):
    """Create a version snapshot of the quotation"""
    data = {
        'quotation_number': quotation.quotation_number,
        'customer_name': quotation.customer_name,
        'customer_email': quotation.customer_email,
        'subject': quotation.subject,
        'items': [
            {
                'description': item.description,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'total': str(item.total),
            }
            for item in quotation.items.all()
        ],
        'subtotal': str(quotation.subtotal),
        'discount': str(quotation.discount),
        'tax': str(quotation.tax_amount),
        'grand_total': str(quotation.grand_total),
    }
    
    QuotationVersion.objects.create(
        quotation=quotation,
        version_number=quotation.version,
        data=data,
        change_summary=change_summary,
        changed_by=changed_by,
    )


def quotation_pdf(request, pk):
    """Generate PDF of quotation"""
    quotation = get_object_or_404(Quotation, pk=pk)
    
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
    elements.append(Paragraph('QUOTATION', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Quotation info
    info_data = [
        ['Quotation #:', f"{quotation.quotation_number}"],
        ['Date:', quotation.created_at.strftime('%B %d, %Y')],
        ['Status:', quotation.get_status_display()],
        ['Valid Until:', quotation.valid_until.strftime('%B %d, %Y') if quotation.valid_until else 'N/A'],
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
    <b>{quotation.customer_name}</b><br/>
    {quotation.customer_company}<br/>
    Email: {quotation.customer_email}<br/>
    Phone: {quotation.customer_phone if quotation.customer_phone else 'N/A'}
    """
    elements.append(Paragraph(customer_info, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Items table
    elements.append(Paragraph('ITEMS', heading_style))
    items_data = [['Description', 'Qty', 'Unit Price', 'Total']]
    for item in quotation.items.all():
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
        ['Subtotal:', f"${quotation.subtotal:.2f}"],
        ['Discount:', f"-${quotation.discount_amount:.2f}"],
        ['Tax ({:.2f}%):'.format(quotation.tax_rate), f"${quotation.tax_amount:.2f}"],
        ['TOTAL:', f"${quotation.grand_total:.2f}"],
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
    if quotation.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('NOTES', heading_style))
        elements.append(Paragraph(quotation.notes, normal_style))
    
    if quotation.terms:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph('TERMS & CONDITIONS', heading_style))
        elements.append(Paragraph(quotation.terms, normal_style))
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Quotation_{quotation.quotation_number}.pdf"'
    return response


@require_POST
def send_quotation(request, pk):
    """Send quotation via email"""
    quotation = get_object_or_404(Quotation, pk=pk)
    
    # Generate PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
    
    # Create a simpler inline PDF generation for email
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f62fe'), alignment=TA_CENTER)
    
    elements.append(Paragraph('QUOTATION', title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Quote #{quotation.quotation_number}", styles['Heading2']))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    
    # Prepare email
    subject = f"Quotation {quotation.quotation_number} - {quotation.subject}"
    body = f"""
Dear {quotation.customer_name},

Please find attached the quotation for your inquiry.

Quotation Details:
- Quotation #: {quotation.quotation_number}
- Amount: ${quotation.grand_total:.2f}
- Valid Until: {quotation.valid_until.strftime('%B %d, %Y') if quotation.valid_until else 'N/A'}

{quotation.description or 'Thank you for your interest in our products.'}

Best regards,
Nishpa Sales Team
    """
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email='noreply@nishpa.com',  # Configure in settings
        to=[quotation.customer_email],
    )
    
    email.attach(f'Quotation_{quotation.quotation_number}.pdf', pdf_buffer.getvalue(), 'application/pdf')
    
    try:
        email.send()
        quotation.status = 'sent'
        quotation.save()
        messages.success(request, f'Quotation sent to {quotation.customer_email}!')
    except Exception as e:
        messages.error(request, f'Error sending email: {str(e)}')
    
    return redirect('quotation:quotation_detail', pk=quotation.pk)


def quotation_versions(request, pk):
    """View version history"""
    quotation = get_object_or_404(Quotation, pk=pk)
    versions = quotation.versions.all()
    
    context = {
        'quotation': quotation,
        'versions': versions,
    }
    
    return render(request, 'quotation/quotation_versions.html', context)


def quotation_version_detail(request, pk, version_id):
    """View specific version details"""
    quotation = get_object_or_404(Quotation, pk=pk)
    version = get_object_or_404(QuotationVersion, pk=version_id, quotation=quotation)
    
    context = {
        'quotation': quotation,
        'version': version,
        'version_data': version.data,
    }
    
    return render(request, 'quotation/quotation_version_detail.html', context)


@require_POST
def update_status(request, pk):
    """Update quotation status"""
    quotation = get_object_or_404(Quotation, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Quotation.STATUS_CHOICES):
        quotation.status = new_status
        quotation.save()
        messages.success(request, f'Status updated to {quotation.get_status_display()}')
    
    return redirect('quotation:quotation_detail', pk=quotation.pk)


@require_POST
def quotation_delete(request, pk):
    """Delete a quotation (POST only)"""
    quotation = get_object_or_404(Quotation, pk=pk)
    if quotation.status == 'draft':
        quotation.delete()
        messages.success(request, 'Quotation deleted successfully.')
    else:
        messages.error(request, 'Only draft quotations can be deleted.')
    return redirect('quotation:quotation_list')


def finalize_quotation(request, pk):
    """Finalize a quotation and navigate to proforma invoice creation"""
    quotation = get_object_or_404(Quotation, pk=pk)
    
    # Check if proforma invoice already exists
    if hasattr(quotation, 'proforma_invoice'):
        messages.info(request, 'Proforma invoice already exists for this quotation.')
        from django.urls import reverse
        return redirect('proforma_invoice:proforma_invoice_detail', pk=quotation.proforma_invoice.pk)
    
    # Redirect to proforma invoice creation
    from django.urls import reverse
    return redirect('proforma_invoice:proforma_invoice_create', quotation_id=quotation.pk)
