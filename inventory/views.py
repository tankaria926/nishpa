from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, Warehouse, Stock, StockTransaction, Supplier


def index(request):
    products = Product.objects.count()
    low_stock = Stock.objects.filter(quantity__lt=5).select_related('product')[:10]
    context = {
        'product_count': products,
        'low_stock': low_stock,
    }
    return render(request, 'inventory/index.html', context)


def product_list(request):
    qs = Product.objects.all().order_by('name')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(sku__icontains=q)
    context = {'products': qs, 'query': q}
    return render(request, 'inventory/product_list.html', context)


def product_create(request):
    if request.method == 'POST':
        p = Product()
        p.name = request.POST.get('name')
        p.sku = request.POST.get('sku', '')
        cat_id = request.POST.get('category')
        p.category_id = cat_id if cat_id else None
        p.unit_cost = request.POST.get('unit_cost', 0)
        p.save()
        messages.success(request, 'Product created successfully')
        return redirect('inventory:product_detail', pk=p.pk)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/product_form.html', {'categories': categories, 'suppliers': suppliers})


def product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk)
    stocks = Stock.objects.filter(product=p).select_related('warehouse')
    warehouses = Warehouse.objects.all()
    context = {'product': p, 'stocks': stocks, 'warehouses': warehouses}
    return render(request, 'inventory/product_detail.html', context)


def product_edit(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        p.name = request.POST.get('name', p.name)
        p.sku = request.POST.get('sku', p.sku)
        p.unit_cost = request.POST.get('unit_cost', p.unit_cost)
        p.save()
        messages.success(request, 'Product updated')
        return redirect('inventory:product_detail', pk=p.pk)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/product_form.html', {'product': p, 'categories': categories, 'suppliers': suppliers, 'editing': True})


def adjust_stock(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method != 'POST':
        return redirect('inventory:product_detail', pk=p.pk)

    warehouse_id = request.POST.get('warehouse')
    tx_type = request.POST.get('tx_type')
    qty = int(request.POST.get('quantity', 0) or 0)
    reason = request.POST.get('reason', '')

    if not warehouse_id or qty <= 0 or tx_type not in ['in', 'out']:
        messages.error(request, 'Invalid stock adjustment')
        return redirect('inventory:product_detail', pk=p.pk)

    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    stock, _ = Stock.objects.get_or_create(product=p, warehouse=warehouse)
    change = qty if tx_type == 'in' else -qty
    stock.quantity = max(0, stock.quantity + change)
    stock.save()

    StockTransaction.objects.create(product=p, warehouse=warehouse, change=change, tx_type=tx_type, reason=reason)
    messages.success(request, 'Stock adjusted successfully')
    return redirect('inventory:product_detail', pk=p.pk)
