from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Count
from inquiry.models import Inquiry, InquiryItem
from quotation.models import Quotation
from datetime import datetime, timedelta


def inquiry_list(request):
    """Display filterable list of all inquiries"""
    
    # Base queryset
    inquiries = Inquiry.objects.prefetch_related('items__product').all()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date_range', '')
    
    # Apply search filter (across name, email, phone, message)
    if search_query:
        inquiries = inquiries.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
    
    # Apply date range filter
    if date_filter:
        today = datetime.now().date()
        if date_filter == 'today':
            inquiries = inquiries.filter(created_at__date=today)
        elif date_filter == 'week':
            start_date = today - timedelta(days=7)
            inquiries = inquiries.filter(created_at__date__gte=start_date)
        elif date_filter == 'month':
            start_date = today - timedelta(days=30)
            inquiries = inquiries.filter(created_at__date__gte=start_date)
    
    # Sorting
    sort_by = request.GET.get('sort_by', '-created_at')
    inquiries = inquiries.order_by(sort_by)
    
    # Get statistics
    total_inquiries = Inquiry.objects.count()
    status_stats = Inquiry.objects.values('status').annotate(count=Count('id'))
    
    # Count by status
    status_counts = {
        'pending': Inquiry.objects.filter(status='pending').count(),
        'in_progress': Inquiry.objects.filter(status='in_progress').count(),
        'completed': Inquiry.objects.filter(status='completed').count(),
        'cancelled': Inquiry.objects.filter(status='cancelled').count(),
    }
    
    # Pagination
    per_page = int(request.GET.get('per_page', 10))
    page = int(request.GET.get('page', 1))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_inquiries = inquiries[start_idx:end_idx]
    total_results = len(inquiries)
    total_pages = (total_results + per_page - 1) // per_page
    
    # Add item counts to each inquiry
    for inquiry in paginated_inquiries:
        inquiry.item_count = inquiry.items.count()
    
    # Generate page numbers for pagination
    page_numbers = list(range(1, total_pages + 1))
    
    context = {
        'inquiries': paginated_inquiries,
        'total_inquiries': total_results,
        'total_pages': total_pages,
        'page_numbers': page_numbers,
        'current_page': page,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'per_page': per_page,
        'status_counts': status_counts,
        'total': total_inquiries,
        'status_choices': Inquiry.STATUS_CHOICES,
    }
    
    # Handle AJAX requests for filtering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render(request, 'inquiry_dashboard/inquiries_table.html', context).content.decode()
        return JsonResponse({
            'html': html,
            'total': total_results,
            'current_page': page,
            'total_pages': total_pages,
        })
    
    return render(request, 'inquiry_dashboard/inquiry_list.html', context)


def inquiry_detail(request, inquiry_id):
    """Display detailed view of a single inquiry"""
    inquiry = Inquiry.objects.prefetch_related('items__product').get(pk=inquiry_id)
    items = inquiry.items.all()
    quotations = Quotation.objects.filter(inquiry=inquiry).order_by('-created_at')
    
    context = {
        'inquiry': inquiry,
        'items': items,
        'quotations': quotations,
        'status_choices': Inquiry.STATUS_CHOICES,
    }
    
    return render(request, 'inquiry_dashboard/inquiry_detail.html', context)


def update_inquiry_status(request, inquiry_id):
    """AJAX endpoint to update inquiry status"""
    if request.method == 'POST':
        try:
            inquiry = Inquiry.objects.get(pk=inquiry_id)
            new_status = request.POST.get('status')
            
            if new_status in dict(Inquiry.STATUS_CHOICES):
                inquiry.status = new_status
                inquiry.save()
                return JsonResponse({
                    'success': True,
                    'status': new_status,
                    'status_display': inquiry.get_status_display()
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        except Inquiry.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Inquiry not found'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
