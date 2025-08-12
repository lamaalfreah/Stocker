from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, F
from django.core.paginator import Paginator
from datetime import date, timedelta

from .models import Product, Category, Supplier
from .forms import ProductForm, CategoryForm, SupplierForm
from .utils import maybe_send_product_alert

is_staff = user_passes_test(lambda u: u.is_staff)

# ----- Products -----
@login_required
def product_list(request):
    q = request.GET.get('q', '').strip()
    qs = Product.objects.all()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(category__name__icontains=q) |
            Q(suppliers__name__icontains=q)
        ).distinct()
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory/products/list.html', {'page_obj': page_obj, 'q': q})

@login_required
def product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/products/detail.html', {'product': p})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            maybe_send_product_alert(p)
            messages.success(request, 'Product added.')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/products/form.html', {'form': form, 'title': 'Add Product'})

@login_required
def product_update(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            p = form.save()
            maybe_send_product_alert(p)
            messages.success(request, 'Product updated.')
            return redirect('inventory:product_detail', pk=p.pk)
    else:
        form = ProductForm(instance=p)
    return render(request, 'inventory/products/form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@is_staff
def product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        p.delete()
        messages.success(request, 'Product deleted.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/products/confirm_delete.html', {'product': p})

# ----- Categories (staff for write) -----
@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/categories/list.html', {'categories': categories})

@login_required
@is_staff
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/categories/form.html', {'form': form, 'title': 'Add Category'})

@login_required
@is_staff
def category_update(request, pk):
    c = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=c)
    return render(request, 'inventory/categories/form.html', {'form': form, 'title': 'Edit Category'})

@login_required
@is_staff
def category_delete(request, pk):
    c = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        c.delete()
        messages.success(request, 'Category deleted.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/categories/confirm_delete.html', {'category': c})

# ----- Suppliers (staff for write) -----
@login_required
def supplier_list(request):
    q = request.GET.get('q', '').strip()
    qs = Supplier.objects.all().order_by('name')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    page_obj = Paginator(qs, 12).get_page(request.GET.get('page'))
    return render(request, 'inventory/suppliers/list.html', {'suppliers': page_obj, 'q': q})

@login_required
def supplier_detail(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    products = Product.objects.filter(suppliers=s)
    return render(request, 'inventory/suppliers/detail.html', {'supplier': s, 'products': products})

@login_required
@is_staff
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added.')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/suppliers/form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
@is_staff
def supplier_update(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated.')
            return redirect('inventory:supplier_detail', pk=s.pk)
    else:
        form = SupplierForm(instance=s)
    return render(request, 'inventory/suppliers/form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
@is_staff
def supplier_delete(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Supplier deleted.')
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/suppliers/confirm_delete.html', {'supplier': s})

# ----- Stock status -----
@login_required
def stock_status(request):
    low_stock = Product.objects.filter(quantity__lte=F('reorder_level'))
    soon = date.today() + timedelta(days=30)
    near_expiry = Product.objects.filter(expiry_date__isnull=False, expiry_date__lte=soon)
    return render(request, 'inventory/stock/status.html', {
        'low_stock': low_stock,
        'near_expiry': near_expiry,
    })
