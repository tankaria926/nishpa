from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import InquiryForm
from .models import ProductCategory, Product, Inquiry, InquiryItem


def inquiry_create(request):
    categories = ProductCategory.objects.all()
    form = InquiryForm()
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        if form.is_valid():
            inquiry = form.save()
            for pid, qty in zip(product_ids, quantities):
                try:
                    p = Product.objects.get(pk=int(pid))
                    q = int(qty) if qty else 0
                    if q > 0:
                        InquiryItem.objects.create(inquiry=inquiry, product=p, quantity=q)
                except (Product.DoesNotExist, ValueError):
                    continue
            return redirect('inquiry:thank_you')
    return render(request, 'inquiry/inquiry_form.html', {'form': form, 'categories': categories})


def thank_you(request):
    return render(request, 'inquiry/thank_you.html')


def products_by_category(request):
    cat_id = request.GET.get('category_id')
    data = []
    if cat_id:
        try:
            cat = ProductCategory.objects.get(pk=int(cat_id))
            for p in cat.products.all():
                data.append({'id': p.id, 'name': p.name, 'image_url': p.image_url})
        except ProductCategory.DoesNotExist:
            pass
    return JsonResponse({'products': data})
