from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventory.models import Product, Supplier, Category
from django.db.models import F
from datetime import date, timedelta

def home_view(request):
    return render(request, 'main/home.html')

@login_required
def dashboard(request):
    stats = {
        'products': Product.objects.count(),
        'suppliers': Supplier.objects.count(),
        'categories': Category.objects.count(),
    }
    low_stock = Product.objects.filter(quantity__lte=F('reorder_level'))[:8]
    soon = date.today() + timedelta(days=30)
    near_expiry = Product.objects.filter(expiry_date__isnull=False, expiry_date__lte=soon)[:8]
    return render(request, 'main/dashboard.html', {'stats': stats, 'low_stock': low_stock, 'near_expiry': near_expiry})
